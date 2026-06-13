#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_zeros_v12.py — Phase C v12 : Illinois C pur via arb_fpwrap_cdouble_hardy_z
═══════════════════════════════════════════════════════════════════════════════════
v12 (2026-06-12) : remplacement de brent_refine_adaptive (libmpfr, ~42 ms/appel)
  par illinois_refine_arb (Arb/FLINT, ~0.038 ms/appel) — gain théorique ×1100.

Décisions v12 :
  Méthode affinage  : illinois_refine_arb (Arb/FLINT double, tol=1e-9)
  Seuil t=300       : SUPPRIMÉ — Arb calcule Z(t) exact pour tout t ≥ 14
  Détection         : scan_arb C (Z_double RS double + C0+C1, step=0.010)
  Workers           : 8 (forcé, identique v10)
  STEP              : 0.010 (gap-safe, identique v10)

Pourquoi v12 est plus simple que v10 :
  v10 avait 2 chemins d'affinage (brent_C pour t ≥ 300, mpmath pour t < 300)
  + 1 fallback (hors intervalle). Le biais RS de Z_rs_mpfr_ntermes imposait ce seuil.
  v12 a 1 seul chemin : illinois_refine_arb(a, b, fa, fb, tol, max_iter).
  Arb (avec garanties d'erreur) n'a pas de biais RS → valide pour tout t.

Auteur : hprzeta — Projet Hypothèse de Riemann — Phase C
Date   : 2026-06-12
"""

import sys
import math
import time
import ctypes
import multiprocessing
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

import mpmath
mpmath.mp.dps = 35

from riemann_siegel_batch import Z_batch, Z_vect_correct
from parallel_scanner      import partitionner, dedupliquer
from turing_validation     import valider_turing, N_attendu
from arb_wrapper           import arb_hardy_z, info_backend, ARB_DISPONIBLE

from chrono_phases         import chrono, snapshot, agreger, rapport

try:
    from scan_arb_wrapper import scan_arb
    SCAN_ARB_DISPONIBLE = True
except (ImportError, FileNotFoundError) as _e:
    SCAN_ARB_DISPONIBLE = False
    print(f"  scan_arb.so absent → fallback Z_vect_correct ({_e})")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — CHEMIN .so
# ═══════════════════════════════════════════════════════════════════════════════

SO_PATH = Path(__file__).parent / "c_modules" / "illinois_arb.so"

if not SO_PATH.exists():
    raise FileNotFoundError(
        f"illinois_arb.so introuvable : {SO_PATH}\n"
        f"Compiler avec :\n"
        f"  cd c_modules && make illinois_arb.so"
    )


def _n_zeros_expected(T: float) -> int:
    """N(T) — formule de Riemann-von Mangoldt (le 'e' dans 2πe est OBLIGATOIRE)."""
    if T < 14.0:
        return 0
    return int(T / (2 * math.pi) * math.log(T / (2 * math.pi * math.e)))


def _partitionner_adaptatif(
    T_MIN: float, T_MAX: float, N_WORKERS: int
) -> list:
    """Segments équitables par inversion de N(T) — chaque worker reçoit N/W zéros.

    Recherche binaire pour trouver T_i tels que N(T_i) = i × N(T_MAX)/W.
    Overlap fixe 0.5 — couvre les brackets sur les bords de segment.
    """
    N_total = _n_zeros_expected(T_MAX)
    if N_total == 0 or N_WORKERS <= 1:
        return [(T_MIN, T_MAX)]

    def _t_pour_n(n_cible: int, t_lo: float, t_hi: float) -> float:
        for _ in range(60):
            t_mid = (t_lo + t_hi) / 2.0
            if _n_zeros_expected(t_mid) < n_cible:
                t_lo = t_mid
            else:
                t_hi = t_mid
        return (t_lo + t_hi) / 2.0

    segments = []
    OVERLAP  = 0.5
    t_prev   = T_MIN
    for i in range(1, N_WORKERS):
        n_cible = i * N_total // N_WORKERS
        t_next  = _t_pour_n(n_cible, T_MIN, T_MAX)
        segments.append((t_prev, min(t_next + OVERLAP, T_MAX)))
        t_prev  = t_next
    segments.append((t_prev, T_MAX))
    return segments


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — WORKER MULTIPROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

TOL_ARB  = 1e-9   # tolérance illinois_refine_arb (double précision max utile)
MAX_ITER = 50     # max itérations Illinois (convergence rapide avec Arb)

def worker_v12(args: tuple) -> Tuple[list, dict, dict]:
    """Worker v12 — détection scan_arb.c + affinage illinois_refine_arb.

    Charge illinois_arb.so APRÈS le fork() → pas de corruption mémoire partagée.
    Détection : scan_arb C (Z_double RS + C0+C1, step=0.010)
    Affinage  : illinois_refine_arb (Arb/FLINT double) pour tout t ≥ 14

    Paramètres : (t_start, t_end, step, so_path, tol, worker_id)
    """
    t_start, t_end, step, so_path, tol, worker_id = args
    debut = time.time()

    # Chargement illinois_arb.so après fork — espace mémoire isolé
    lib = ctypes.CDLL(str(so_path))
    lib.illinois_refine_arb.restype  = ctypes.c_double
    lib.illinois_refine_arb.argtypes = [
        ctypes.c_double,  # a
        ctypes.c_double,  # b
        ctypes.c_double,  # fa = Z(a) fourni par scan_arb
        ctypes.c_double,  # fb = Z(b) fourni par scan_arb
        ctypes.c_double,  # tol (1e-9)
        ctypes.c_int,     # max_iter (50)
    ]

    # Seuil petits t : scan_arb (Z_double) a N_RS=1–3 termes → peu précis
    # En dessous de ce seuil, arb_hardy_z (Python) est utilisé pour la détection.
    T_SEUIL_PETIT_T = 200.0

    zeros_segment = []
    stats         = {"arb_C": 0, "mpmath_fallback": 0, "mpmath_petit_t": 0}
    _log_palier   = 0

    # ── Petits t : détection + affinage via arb_hardy_z + mpmath ─────────────
    # Évite les brackets spurieux de scan_arb (Z_double à N_RS faible).
    if t_start < T_SEUIL_PETIT_T:
        t_fin_pt = min(T_SEUIL_PETIT_T, t_end)
        with chrono("mpmath_petit_t"):
            t_arr_pt = np.arange(t_start, t_fin_pt, step, dtype=np.float64)
            if len(t_arr_pt) >= 2:
                Zv_pt = np.array([arb_hardy_z(float(t)) for t in t_arr_pt])
                for j in np.where(np.diff(np.sign(Zv_pt)))[0]:
                    try:
                        z = float(mpmath.findroot(
                            arb_hardy_z,
                            (float(t_arr_pt[j]), float(t_arr_pt[j+1])),
                            solver="illinois", tol=1e-12, maxsteps=80,
                        ))
                        zeros_segment.append(z)
                        stats["mpmath_petit_t"] += 1
                    except Exception:
                        pass
        # Continuer avec scan_arb pour la partie [T_SEUIL_PETIT_T, t_end]
        t_start_main = t_fin_pt
    else:
        t_start_main = t_start

    # ── Détection : scan_arb C ou Z_vect_correct numpy (fallback) ────────────
    if SCAN_ARB_DISPONIBLE:
        with chrono("detection"):
            brackets = scan_arb(t_start_main, t_end, step=step) if t_start_main < t_end else []
    else:
        TAILLE_BLOC = 5000
        brackets    = []
        t_courant   = t_start_main
        with chrono("detection"):
            while t_courant < t_end:
                t_fin = min(t_courant + TAILLE_BLOC * step, t_end)
                t_arr = np.arange(t_courant, t_fin, step, dtype=np.float64)
                if len(t_arr) < 2:
                    break
                Zv = Z_vect_correct(t_arr)
                for j in np.where(np.diff(np.sign(Zv)))[0]:
                    brackets.append((float(t_arr[j]), float(t_arr[j+1]),
                                     float(Zv[j]),   float(Zv[j+1])))
                t_courant = float(t_arr[-1]) + step

    # ── Affinage : illinois_refine_arb (Arb) pour tout t ────────────────────
    # Pas de seuil t=300 : Arb est valide sans biais RS pour tout t ≥ 14.
    for a, b, fa, fb in brackets:
        try:
            with chrono("arb_C"):
                zero = lib.illinois_refine_arb(a, b, float(fa), float(fb),
                                               TOL_ARB, MAX_ITER)

            if a - 1e-10 <= zero <= b + 1e-10:
                zeros_segment.append(zero)
                stats["arb_C"] += 1
            else:
                # Résultat hors intervalle → fallback mpmath (rare)
                with chrono("mpmath_fallback"):
                    zero = float(mpmath.findroot(
                        arb_hardy_z, (a, b),
                        solver="illinois", tol=1e-12, maxsteps=80,
                    ))
                zeros_segment.append(zero)
                stats["mpmath_fallback"] += 1
        except Exception:
            pass

        n = len(zeros_segment)
        if n // 1000 > _log_palier // 1000 and n > 0:
            elapsed = time.time() - debut
            print(f"  [Worker {worker_id}] zéro #{(n // 1000) * 1000}"
                  f" à t={zeros_segment[-1]:.2f} — {elapsed:.1f}s", flush=True)
            _log_palier = n

    duree = time.time() - debut
    print(f"  [Worker {worker_id}] {len(zeros_segment)} zéros en {duree:.1f}s  "
          f"| arb_C:{stats['arb_C']} fallback:{stats['mpmath_fallback']}")
    return zeros_segment, stats, snapshot()


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — ORCHESTRATEUR PARALLÈLE
# ═══════════════════════════════════════════════════════════════════════════════

def calculer_zeros_v12(
    T_MIN     : float,
    T_MAX     : float,
    N_WORKERS : int,
    STEP      : float,
    TOL       : float = 1e-9,
) -> Tuple[List[float], dict, dict]:
    """Lance N_WORKERS processus sur [T_MIN, T_MAX], fusionne et déduplique."""
    segments  = _partitionner_adaptatif(T_MIN, T_MAX, N_WORKERS)
    args_list = [
        (t_min, t_max, STEP, SO_PATH, TOL, i)
        for i, (t_min, t_max) in enumerate(segments)
    ]

    print(f"\n  {N_WORKERS} workers — segments :")
    for i, (a, b) in enumerate(segments):
        print(f"    Worker {i} : [{a:.1f}, {b:.1f}]")
    print()

    with multiprocessing.Pool(processes=N_WORKERS) as pool:
        resultats = pool.map(worker_v12, args_list)

    zeros_bruts = []
    stats_total = {"arb_C": 0, "mpmath_fallback": 0}
    snaps       = []
    for segment_zeros, segment_stats, segment_snap in resultats:
        zeros_bruts.extend(segment_zeros)
        for k, v in segment_stats.items():
            stats_total[k] = stats_total.get(k, 0) + v
        snaps.append(segment_snap)

    profil_workers = agreger(snaps)
    zeros = dedupliquer(zeros_bruts, tolerance=0.01)
    return zeros, stats_total, profil_workers


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — VÉRIFICATION LMFDB
# ═══════════════════════════════════════════════════════════════════════════════

LMFDB_REFERENCES = [
    14.134725141734693, 21.022039638771555, 25.010857580145688,
    30.424876125859513, 32.935061587739189, 37.586178158825671,
    40.918719012147495, 43.327073280914999, 48.005150881167159,
    49.773832477672302, 52.970321477714460, 56.446247697063246,
    59.347044002602353, 60.831778524609882, 65.112544048081607,
    67.079810529494173, 69.546401711173978, 72.067157674481890,
    75.704690699083934, 77.144840069680455,
]


def verifier_lmfdb(zeros: List[float], n_check: int = 20) -> dict:
    """Comparaison avec les valeurs LMFDB de référence."""
    n       = min(len(zeros), n_check, len(LMFDB_REFERENCES))
    details = []
    if n == 0:
        return {"score": "0/0", "details": []}

    print(f"\n  Vérification LMFDB ({n} premiers zéros) :")
    print(f"  {'#':>4}  {'Calculé':>20}  {'LMFDB':>20}  {'Écart':>12}")
    print("  " + "─" * 62)
    for i in range(n):
        ecart = abs(zeros[i] - LMFDB_REFERENCES[i])
        ok    = ecart < 1e-9
        sym   = "✅" if ok else ("⚠️ " if ecart < 1e-6 else "❌")
        print(f"  {i+1:>4}  {zeros[i]:>20.14f}  {LMFDB_REFERENCES[i]:>20.14f}"
              f"  {ecart:>12.2e}  {sym}")
        details.append({"n": i+1, "calcule": zeros[i],
                        "lmfdb": LMFDB_REFERENCES[i], "ecart": ecart, "ok": ok})

    n_ok = sum(1 for d in details if d["ok"])
    print(f"\n  Score LMFDB : {n_ok}/{n} zéros à < 10⁻⁹")
    return {"score": f"{n_ok}/{n}", "details": details}


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 — VISUALISATION
# ═══════════════════════════════════════════════════════════════════════════════

def visualiser(zeros: List[float], T_MAX: float, horodatage: str, dossier: Path):
    """3 graphiques : Z(t) via Z_batch, espacements GUE, droite critique."""
    if len(zeros) < 3:
        return

    ecarts = np.diff(zeros)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(
        f"Zéros de ζ(½+it) — v12 — {len(zeros)} zéros [T_MAX={T_MAX:.0f}]",
        fontsize=13, fontweight="bold"
    )

    t_plot  = np.linspace(14, min(60, T_MAX), 600)
    Z_vals  = Z_batch(t_plot)
    ax = axes[0]
    ax.plot(t_plot, Z_vals, 'b-', linewidth=0.8, label='Z(t)')
    ax.axhline(0, color='k', linewidth=0.5)
    for t0 in zeros:
        if t0 <= 60:
            ax.axvline(t0, color='r', linewidth=0.5, alpha=0.4)
    ax.set_xlabel("t"); ax.set_ylabel("Z(t)")
    ax.set_title("Fonction Z de Hardy [14, 60]")
    ax.grid(True, alpha=0.3)

    t_mid   = zeros[:-1]
    delta_n = ecarts * np.log(np.array(t_mid) / (2 * math.pi)) / (2 * math.pi)
    ax = axes[1]
    ax.hist(delta_n, bins=50, density=True, edgecolor='black',
            alpha=0.75, color='steelblue', label='Espacements normalisés')
    s_vals = np.linspace(0, 4, 200)
    gue    = (math.pi / 2) * s_vals * np.exp(-math.pi * s_vals**2 / 4)
    ax.plot(s_vals, gue, 'r-', linewidth=2, label='GUE (Wigner-Dyson)')
    ax.set_xlabel("δₙ normalisé"); ax.set_ylabel("Densité")
    ax.set_title("Espacements vs GUE (conjecture de Montgomery)")
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

    ax = axes[2]
    ax.scatter([0.5] * len(zeros), zeros, s=3, color='darkblue', alpha=0.4)
    ax.axvline(0.5, color='r', linestyle='--', linewidth=1.5, label='Re(s) = ½')
    ax.set_xlabel("Re(s)"); ax.set_ylabel("Im(s) = t")
    ax.set_title("Droite critique — Hypothèse de Riemann")
    ax.set_xlim(0, 1); ax.legend(); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    nom_png = f"zeros_v12_T{T_MAX:.0f}_{horodatage}.png"
    plt.savefig(str(dossier / nom_png), dpi=150)
    plt.close()
    print(f"  Graphique → {nom_png}")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — SAUVEGARDE CSV + LOG
# ═══════════════════════════════════════════════════════════════════════════════

def sauvegarder_csv(zeros, stats, T_MAX, STEP, N_WORKERS,
                    horodatage, dossier) -> Path:
    nom        = f"zeros_v12_T{T_MAX:.0f}_{horodatage}.csv"
    chemin_csv = dossier / nom
    df = pd.DataFrame({
        "n":                 range(1, len(zeros) + 1),
        "partie_imaginaire": zeros,
        "T_MAX":             T_MAX,
        "version":           "v12",
        "methode_affinage":  "arb_C_pur",
        "step":              STEP,
        "n_workers":         N_WORKERS,
        "calcule_le":        horodatage,
    })
    df.to_csv(str(chemin_csv), index=False)
    print(f"  {len(zeros)} zéros → {chemin_csv}")
    return chemin_csv


def ecrire_log(chemin_log, horodatage, T_MIN, T_MAX, STEP, N_WORKERS,
               tol, duree_s, zeros, stats, resultats_lmfdb,
               resultats_turing, chemin_csv):
    """Journal d'exécution v12."""
    lignes = []
    sep    = "=" * 65

    def L(t=""): lignes.append(t)

    L(sep)
    L("  JOURNAL D'EXÉCUTION — compute_zeros_v12.py  (Phase C)")
    L("  Projet : Hypothèse de Riemann — hprzeta")
    L(sep); L()

    L("  [1] HORODATAGE")
    L(f"      Début  : {horodatage}")
    L(f"      Fin    : {datetime.now().strftime('%Y%m%d_%H%M%S')}")
    L(f"      Durée  : {duree_s/60:.2f} min  ({duree_s:.1f} s)")
    L()

    L("  [2] PARAMÈTRES v12")
    L(f"      T_MIN              = {T_MIN}")
    L(f"      T_MAX              = {T_MAX}")
    L(f"      STEP               = {STEP}")
    L(f"      TOL_ARB            = {tol:.0e}  (double, illinois_refine_arb)")
    L(f"      N_WORKERS          = {N_WORKERS}")
    L(f"      illinois_arb.so    : {SO_PATH}")
    scan_str = "scan_arb C (Z_double RS C0+C1)" if SCAN_ARB_DISPONIBLE else "Z_vect_correct numpy (fallback)"
    L(f"      Détection          : {scan_str}")
    L(f"      Affinage           : illinois_refine_arb (Arb/FLINT) — tout t ≥ 14")
    L(f"      Seuil t=300        : SUPPRIMÉ (Arb sans biais RS)")
    L(f"      Fallback           : mpmath.findroot (résultat hors intervalle seulement)")
    L(f"      Backend Arb        : {info_backend()}")
    L()

    L("  [3] RÉSULTATS NUMÉRIQUES")
    L(f"      Zéros trouvés      = {len(zeros)}")
    L(f"      N attendus (Weyl)  = {int(T_MAX/(2*math.pi)*math.log(T_MAX/(2*math.pi*math.e)))}")
    vitesse = len(zeros) / duree_s if duree_s > 0 else 0
    L(f"      Vitesse moyenne    = {vitesse:.2f} zéros/s")
    if zeros:
        ecarts = [zeros[i+1]-zeros[i] for i in range(len(zeros)-1)]
        L(f"      t₁  (1er zéro)    = {zeros[0]:.14f}")
        L(f"      t_n (dernier)     = {zeros[-1]:.14f}")
        if ecarts:
            L(f"      Espacement min    = {min(ecarts):.6f}")
            L(f"      Espacement max    = {max(ecarts):.6f}")
            L(f"      Espacement moy    = {sum(ecarts)/len(ecarts):.6f}")
    L()

    L("  [4] RÉPARTITION DES MÉTHODES D'AFFINAGE")
    total = sum(stats.values())
    for methode, nb in sorted(stats.items()):
        pct = nb / total * 100 if total > 0 else 0
        L(f"      {methode:<22} : {nb:>6}  ({pct:.1f}%)")
    L()

    L("  [5] VÉRIFICATION LMFDB")
    L(f"      Score : {resultats_lmfdb.get('score','N/A')} à < 10⁻⁹")
    for item in resultats_lmfdb.get("details", []):
        sym = "✅" if item["ok"] else "⚠️ "
        L(f"      #{item['n']:>3}  écart={item['ecart']:.2e}  {sym}")
    L()

    L("  [6] VALIDATION TURING-BACKLUND")
    complet = resultats_turing.get("complet", False)
    L(f"      Statut : {'✅ COMPLET' if complet else '❌ INCOMPLET'}")
    L(f"      Zéros manquants : {resultats_turing.get('manquants_total','N/A')}")
    for v in resultats_turing.get("verifications", []):
        L(f"      T={v['T']:>8.2f}  calc={v['calcules']:>6d}  attendus={v['attendus']:>6d}"
          f"  delta={v['delta']:>+5d}  {v.get('statut','')}")
    L()

    L("  [7] FICHIERS GÉNÉRÉS")
    L(f"      CSV → {chemin_csv}")
    L(f"      LOG → {chemin_log}")
    L()

    import platform
    L("  [8] ENVIRONNEMENT")
    L(f"      Python           = {sys.version.split()[0]}")
    L(f"      OS               = {platform.system()} {platform.release()}")
    L(f"      mpmath           = {mpmath.__version__}")
    L(f"      CPU cores        = {multiprocessing.cpu_count()}")
    L()
    L(sep)
    L(f"  Fin du journal — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    L(sep)

    chemin_log.write_text("\n".join(lignes), encoding="utf-8")
    print(f"  Journal → {chemin_log}")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 7 — INTERFACE UTILISATEUR
# ═══════════════════════════════════════════════════════════════════════════════

def _step_adaptatif(T_MAX: float) -> float:
    """STEP fixe 0.010 — gap-safe mesuré (gap min = 0.019 à t=66678 sur T=100k)."""
    return 0.010


def saisir_parametres():
    print()
    print("=" * 65)
    print("   CALCUL DES ZÉROS NON TRIVIAUX — v12 (Phase C / Arb)")
    print("=" * 65)
    print()
    scan_statut = "✓ scan_arb.so actif (Z_double C)" if SCAN_ARB_DISPONIBLE else "⚠ fallback Z_vect_correct"
    print(f"  Détection  : {scan_statut}")
    print(f"  Affinage   : illinois_refine_arb (Arb/FLINT, tout t)")
    print(f"  Validation : Turing-Backlund")
    print(f"  .so : {SO_PATH}")
    print(f"  Backend Arb : {info_backend()}")
    print()
    print(f"  Estimations (8 workers, gain théorique ×1100 vs mpfr) :")
    print("    T =   1 000  →  ~  396 zéros  →  ~  < 5 sec")
    print("    T =  10 000  →  ~ 4516 zéros  →  ~  < 1 min")
    print("    T = 100 000  →  ~49k  zéros  →  ~  < 5 min")
    print()

    while True:
        try:
            T_MAX = float(input("  Entrez T_MAX (≥ 20) : "))
            if T_MAX >= 20:
                break
            print("  T_MAX doit être ≥ 20.")
        except ValueError:
            print("  Nombre invalide.")

    N_WORKERS = 8
    STEP      = _step_adaptatif(T_MAX)
    print(f"\n  ── Configuration ──────────────────────────────")
    print(f"     T_MAX     = {T_MAX:.0f}")
    print(f"     N_WORKERS = {N_WORKERS}")
    print(f"     STEP      = {STEP}")
    print(f"     TOL_ARB   = {TOL_ARB:.0e}")
    print(f"     N zéros   ≈ {N_attendu(T_MAX):.0f}")

    if input("\n  Lancer le calcul ? [O/n] : ").strip().lower() in ("n", "non"):
        sys.exit(0)

    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    dossier    = Path("calculs") / f"v12_T{T_MAX:.0f}_{horodatage}"
    dossier.mkdir(parents=True, exist_ok=True)
    return T_MAX, N_WORKERS, STEP, horodatage, dossier


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 8 — POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    debut_global = time.time()
    T_MIN = 14.0

    T_MAX, N_WORKERS, STEP, horodatage, dossier = saisir_parametres()

    print(f"\n  Lancement — {N_WORKERS} workers, STEP={STEP}, "
          f"illinois_refine_arb pour tout t...\n")
    zeros, stats, profil_workers = calculer_zeros_v12(
        T_MIN, T_MAX, N_WORKERS, STEP, TOL_ARB
    )
    duree = time.time() - debut_global

    print()
    print("=" * 65)
    print("  RÉSULTATS v12")
    print("=" * 65)
    print(f"  Zéros trouvés     : {len(zeros)}")
    print(f"  Attendus (Weyl)   : {N_attendu(T_MAX):.0f}")
    print(f"  Durée             : {duree/60:.1f} min  ({duree:.1f} s)")
    vitesse = len(zeros) / duree if duree > 0 else 0
    print(f"  Vitesse           : {vitesse:.2f} zéros/s")
    print()
    print("  Répartition des méthodes d'affinage :")
    total = sum(stats.values())
    for methode, nb in sorted(stats.items()):
        pct = nb / total * 100 if total > 0 else 0
        print(f"    {methode:<24} : {nb:>6}  ({pct:.1f}%)")
    if zeros:
        print(f"\n  t₁  = {zeros[0]:.12f}")
        print(f"  t_n = {zeros[-1]:.12f}")
    print("=" * 65)

    resultats_lmfdb  = verifier_lmfdb(zeros, n_check=20)

    with chrono("turing"):
        resultats_turing = valider_turing(zeros, dps=30)

    profil_total = agreger([profil_workers, snapshot()])
    print()
    print(rapport(profil_total, duree_run=duree, n_workers=N_WORKERS))

    chemin_csv = sauvegarder_csv(
        zeros, stats, T_MAX, STEP, N_WORKERS, horodatage, dossier
    )
    visualiser(zeros, T_MAX, horodatage, dossier)

    nom_log    = f"execution_v12_T{T_MAX:.0f}_{horodatage}.log"
    chemin_log = dossier / nom_log
    ecrire_log(
        chemin_log, horodatage, T_MIN, T_MAX, STEP, N_WORKERS,
        TOL_ARB, duree, zeros, stats, resultats_lmfdb, resultats_turing, chemin_csv
    )

    print()
    print("=" * 65)
    print(f"  v12 terminée — fichiers dans : {dossier}")
    if resultats_turing["complet"]:
        print("  Validation Turing : COMPLET (aucun zéro manqué)")
    else:
        manq = resultats_turing["manquants_total"]
        print(f"  Validation Turing : {manq} zéros manquants — réduire STEP")
    print("=" * 65)


if __name__ == "__main__":
    main()
