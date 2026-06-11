#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_zeros_v6.py — scan_arb.c (Z_double C) + STEP=0.010 + N(T) bissection
══════════════════════════════════════════════════════════════════════════════════
v6 (basée sur v4.1) — Run T=100 000 : 138 069 zéros, 0 manquant, Turing COMPLET ✅
Date : 11 juin 2026 — bottleneck : illinois_C 83 %, prochaine étape : v7 N_termes adaptatif

Corrige 5 erreurs architecturales de v4 :

  P1 — Détection : mpmath.siegelz → Z_batch() (RS numpy vectorisé)
       Cause v4 : confusion entre Z_mpfr interne .so (imprécis petit t)
       et la détection de signe. Z_batch est correct partout (même N=1).

  P2 — Parallélisme abandonné → réintégré (worker_v4_1 + Pool)
       Cause v4 : croyance que ctypes + multiprocessing était incompatible.
       Correct : charger le .so APRÈS fork(), dans chaque worker.

  P3 — Z_double du .so chargé inutilement → supprimé
       Cause v4 : pré-check Z_double scalaire (lent, source de confusion).
       Seul illinois_mpfr() est appelé depuis le .so.

  P4 — Fallback mpmath non borné → borné à t < T_SEUIL_ILLINOIS_C = 300
       Cause v4 : vérification |mpmath.siegelz(γ)| < 1e-8 partout
       → fallback déclenché à t=9000 sans raison mathématique.
       Règle : t < 300 ↔ N < 7 termes RS → Illinois C imprécis (légitime).
               t ≥ 300 ↔ N ≥ 7 termes RS → Illinois C fiable → gain ×39.

  P5 — Dégradation silencieuse si .so absent → FileNotFoundError immédiat

Performances attendues (4 workers) :
  t < 300  →   87 zéros  → mpmath        (< 1% du temps total)
  t ≥ 300  → 10 055 zéros → Illinois C   (99% du temps → ×39)
  Vitesse estimée : 15–20 z/s vs 1.0 z/s en v4, vs 3.59 z/s en v3

Auteur : hprzeta — Projet Hypothèse de Riemann — Phase C
Date   : 2026-05-24
"""

import sys
import math
import time
import ctypes
import multiprocessing
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # sans affichage (serveur / non interactif)
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

import mpmath
mpmath.mp.dps = 35   # affinage fallback uniquement

from riemann_siegel_batch import Z_batch, Z_vect_correct
from parallel_scanner      import partitionner, dedupliquer
from turing_validation     import valider_turing, N_attendu
from arb_wrapper           import arb_hardy_z, info_backend, ARB_DISPONIBLE

# Instrumentation 3+1 phases (detection / illinois_C / mpmath_petit_t / turing)
from chrono_phases         import chrono, snapshot, agreger, rapport

# scan_arb — détection C pure (Z_double RS double + C0+C1)
# Import au niveau module : scan_arb_wrapper charge scan_arb.so au 1er appel.
# Dans chaque worker (après fork), le 1er appel à scan_arb() charge le .so
# dans l'espace mémoire du worker — pas de conflit GMP/mpfr.
try:
    from scan_arb_wrapper import scan_arb
    SCAN_ARB_DISPONIBLE = True
except (ImportError, FileNotFoundError) as _e:
    SCAN_ARB_DISPONIBLE = False
    print(f"  ⚠️  scan_arb.so absent → fallback Z_vect_correct ({_e})")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — CHEMIN .so ET SEUIL
# ═══════════════════════════════════════════════════════════════════════════════

SO_PATH = Path(__file__).parent / "c_modules" / "illinois_mpfr.so"

if not SO_PATH.exists():
    raise FileNotFoundError(
        f"illinois_mpfr.so introuvable : {SO_PATH}\n"
        f"Compiler avec : cd c_modules && make"
    )

# Seuil mathématiquement justifié :
# N = floor(sqrt(t/2π)) ≥ 7  ↔  t ≥ 300
# En dessous, Z_mpfr interne (RS) a une erreur ~1e-3 → Illinois C imprécis.
T_SEUIL_ILLINOIS_C = 300.0


def _n_zeros_expected(T: float) -> int:
    """N(T) — formule de Riemann-von Mangoldt.
    N(T) ≈ T/(2π) · ln(T/2πe)  — le 'e' dans 2πe est OBLIGATOIRE.
    """
    if T < 14.0:
        return 0
    return int(T / (2 * math.pi) * math.log(T / (2 * math.pi * math.e)))


def _partitionner_adaptatif(
    T_MIN: float, T_MAX: float, N_WORKERS: int
) -> list:
    """Segments équitables par inversion de N(T) — chaque worker reçoit N(T_MAX)/W zéros.

    Recherche binaire pour trouver T_i tels que N(T_i) = i × N(T_MAX)/W.
    Plus précis que la méthode 1/√t pour les grands T où la densité croît.
    Overlap fixe 0.5 — couvre les brackets sur les bords de segment.
    Les doublons sont éliminés par dedupliquer(tolerance=0.01).
    """
    N_total = _n_zeros_expected(T_MAX)
    if N_total == 0 or N_WORKERS <= 1:
        return [(T_MIN, T_MAX)]

    # Trouver T tel que N(T) = cible par bissection
    def _t_pour_n(n_cible: int, t_lo: float, t_hi: float) -> float:
        for _ in range(60):  # 60 itérations → précision ~1e-12 sur t_hi
            t_mid = (t_lo + t_hi) / 2.0
            if _n_zeros_expected(t_mid) < n_cible:
                t_lo = t_mid
            else:
                t_hi = t_mid
        return (t_lo + t_hi) / 2.0

    segments = []
    OVERLAP  = 0.5  # assure que les brackets sur les bords sont capturés
    t_prev   = T_MIN
    for i in range(1, N_WORKERS):
        n_cible = i * N_total // N_WORKERS
        t_next  = _t_pour_n(n_cible, T_MIN, T_MAX)
        segments.append((t_prev, min(t_next + OVERLAP, T_MAX)))
        t_prev  = t_next
    segments.append((t_prev, T_MAX))
    return segments


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — WORKER MULTIPROCESSING (chargement .so après fork)
# ═══════════════════════════════════════════════════════════════════════════════

def worker_v4_1(args: tuple) -> Tuple[list, dict, dict]:
    """Worker multiprocessing v4.1 — détection scan_arb.c + affinage illinois_refine.

    Charge illinois_mpfr.so ET scan_arb.so APRÈS le fork() → pas de corruption GMP.
    Détection : scan_arb C (Z_double RS double + C0+C1, step=0.010)
    Affinage  : illinois_refine C (libmpfr 170 bits) pour t ≥ 300
                arb_hardy_z + mpmath.findroot pour t < 300

    Paramètres
    ----------
    args : (t_start, t_end, step, so_path, tol, worker_id)
    """
    t_start, t_end, step, so_path, tol, worker_id = args
    debut = time.time()

    # Chargement illinois_mpfr.so après fork — chaque worker a son propre espace mémoire
    lib = ctypes.CDLL(str(so_path))
    lib.illinois_refine.restype  = ctypes.c_double
    lib.illinois_refine.argtypes = [
        ctypes.c_double,  # a
        ctypes.c_double,  # b
        ctypes.c_double,  # fa = Z(a) précalculé par scan_arb
        ctypes.c_double,  # fb = Z(b) précalculé par scan_arb
        ctypes.c_int,     # prec_bits (170)
        ctypes.c_double,  # tol
        ctypes.c_int,     # max_iter (100)
    ]

    import mpmath as _mp
    _mp.mp.dps = 35

    zeros_segment = []
    stats         = {"illinois_C": 0, "mpmath_petit_t": 0, "mpmath_fallback": 0}
    _log_palier   = 0

    # ── Détection : scan_arb C (1 appel) ou Z_vect_correct numpy (fallback) ──────
    if SCAN_ARB_DISPONIBLE:
        with chrono("detection"):
            brackets = scan_arb(t_start, t_end, step=step)
    else:
        # Fallback Z_vect_correct — blocs de TAILLE_BLOC pour éviter l'OOM
        TAILLE_BLOC = 5000
        brackets    = []
        t_courant   = t_start
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

    # ── Affinage : illinois_refine ou arb+mpmath selon seuil t=300 ───────────────
    for a, b, fa, fb in brackets:
        t_mid = (a + b) / 2.0
        try:
            if t_mid >= T_SEUIL_ILLINOIS_C:
                # Illinois C Option B — fa/fb depuis scan_arb, pas de recalcul C
                with chrono("illinois_C"):
                    zero = lib.illinois_refine(a, b, fa, fb, 170, tol, 100)
                if a - 1e-10 <= zero <= b + 1e-10:
                    zeros_segment.append(zero)
                    stats["illinois_C"] += 1
                else:
                    # Résultat hors intervalle → fallback Arb bracketed
                    with chrono("mpmath_fallback"):
                        zero = float(_mp.findroot(
                            arb_hardy_z, (a, b),
                            solver="illinois", tol=1e-12, maxsteps=80,
                        ))
                    zeros_segment.append(zero)
                    stats["mpmath_fallback"] += 1
            else:
                # t < 300 — N < 7 termes RS, illinois_refine imprécis → Arb bracketed
                with chrono("mpmath_petit_t"):
                    zero = float(_mp.findroot(
                        arb_hardy_z, (a, b),
                        solver="illinois", tol=tol, maxsteps=80,
                    ))
                zeros_segment.append(zero)
                stats["mpmath_petit_t"] += 1
        except Exception:
            pass  # Turing-Backlund détectera les zéros manquants

        # Log de progression toutes les 1000 zéros
        n = len(zeros_segment)
        if n // 1000 > _log_palier // 1000 and n > 0:
            elapsed = time.time() - debut
            print(f"  [Worker {worker_id}] zéro #{(n // 1000) * 1000}"
                  f" à t={zeros_segment[-1]:.2f} — {elapsed:.1f}s", flush=True)
            _log_palier = n

    duree = time.time() - debut
    print(f"  [Worker {worker_id}] {len(zeros_segment)} zéros en {duree:.1f}s  "
          f"| C:{stats['illinois_C']} mp_pt:{stats['mpmath_petit_t']} "
          f"fallback:{stats['mpmath_fallback']}")
    return zeros_segment, stats, snapshot()


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — ORCHESTRATEUR PARALLÈLE
# ═══════════════════════════════════════════════════════════════════════════════

def calculer_zeros_v4_1(
    T_MIN     : float,
    T_MAX     : float,
    N_WORKERS : int,
    STEP      : float,
    TOL       : float = 1e-12,
) -> Tuple[List[float], dict, dict]:
    """Lance N_WORKERS processus sur [T_MIN, T_MAX], fusionne et déduplique.

    Retourne (zeros, stats_aggregées, profil_phases_workers).
    """
    # Segmentation N(T) — chaque worker reçoit N(T_MAX)/N_WORKERS zéros
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
        resultats = pool.map(worker_v4_1, args_list)

    # Fusion des listes, des statistiques et des profils
    zeros_bruts = []
    stats_total = {"illinois_C": 0, "mpmath_petit_t": 0, "mpmath_fallback": 0}
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
#  SECTION 4 — VÉRIFICATION LMFDB (20 références)
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
        ok    = ecart < 1e-10
        sym   = "✅" if ok else ("⚠️ " if ecart < 1e-6 else "❌")
        print(f"  {i+1:>4}  {zeros[i]:>20.14f}  {LMFDB_REFERENCES[i]:>20.14f}"
              f"  {ecart:>12.2e}  {sym}")
        details.append({"n": i+1, "calcule": zeros[i],
                        "lmfdb": LMFDB_REFERENCES[i], "ecart": ecart, "ok": ok})

    n_ok = sum(1 for d in details if d["ok"])
    print(f"\n  Score LMFDB : {n_ok}/{n} zéros à < 10⁻¹⁰")
    return {"score": f"{n_ok}/{n}", "details": details}


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 — VISUALISATION (Z_batch — pas mpmath.siegelz)
# ═══════════════════════════════════════════════════════════════════════════════

def visualiser(zeros: List[float], T_MAX: float, horodatage: str, dossier: Path):
    """3 graphiques : Z(t) via Z_batch, espacements GUE, droite critique."""
    if len(zeros) < 3:
        return

    ecarts = np.diff(zeros)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(
        f"Zéros de ζ(½+it) — v4.1 — {len(zeros)} zéros [T_MAX={T_MAX:.0f}]",
        fontsize=13, fontweight="bold"
    )

    # Z(t) via Z_batch — vectorisé, pas de boucle mpmath
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

    # Espacements normalisés vs GUE
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

    # Droite critique
    ax = axes[2]
    ax.scatter([0.5] * len(zeros), zeros, s=3, color='darkblue', alpha=0.4)
    ax.axvline(0.5, color='r', linestyle='--', linewidth=1.5, label='Re(s) = ½')
    ax.set_xlabel("Re(s)"); ax.set_ylabel("Im(s) = t")
    ax.set_title("Droite critique — Hypothèse de Riemann")
    ax.set_xlim(0, 1); ax.legend(); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    nom_png = f"zeros_v4_1_T{T_MAX:.0f}_{horodatage}.png"
    plt.savefig(str(dossier / nom_png), dpi=150)
    plt.close()
    print(f"  Graphique → {nom_png}")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — SAUVEGARDE CSV + LOG
# ═══════════════════════════════════════════════════════════════════════════════

def sauvegarder_csv(zeros, stats, T_MAX, STEP, N_WORKERS,
                    horodatage, dossier) -> Path:
    nom        = f"zeros_v4_1_T{T_MAX:.0f}_{horodatage}.csv"
    chemin_csv = dossier / nom
    df = pd.DataFrame({
        "n":                 range(1, len(zeros) + 1),
        "partie_imaginaire": zeros,
        "T_MAX":             T_MAX,
        "version":           "v4.1",
        "methode_affinage":  "illinois_C_seuil300_mpmath_fallback",
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
    """Journal d'exécution v4.1."""
    lignes = []
    sep    = "=" * 65

    def L(t=""): lignes.append(t)

    L(sep)
    L("  JOURNAL D'EXÉCUTION — compute_zeros_v4_1.py  (Phase C)")
    L("  Projet : Hypothèse de Riemann — hprzeta")
    L(sep); L()

    L("  [1] HORODATAGE")
    L(f"      Début  : {horodatage}")
    L(f"      Fin    : {datetime.now().strftime('%Y%m%d_%H%M%S')}")
    L(f"      Durée  : {duree_s/60:.2f} min  ({duree_s:.1f} s)")
    L()

    L("  [2] PARAMÈTRES v4.1")
    L(f"      T_MIN              = {T_MIN}")
    L(f"      T_MAX              = {T_MAX}")
    L(f"      STEP               = {STEP}")
    L(f"      TOL_AFFINAGE       = {tol:.0e}")
    L(f"      N_WORKERS          = {N_WORKERS}")
    L(f"      T_SEUIL_ILLINOIS_C = {T_SEUIL_ILLINOIS_C}  (N≥7 termes RS)")
    L(f"      illinois_mpfr.so   : {SO_PATH}")
    scan_str = "scan_arb C (Z_double RS C0+C1)" if SCAN_ARB_DISPONIBLE else "Z_vect_correct numpy (fallback)"
    L(f"      Détection          : {scan_str}")
    L(f"      Affinage t≥300     : illinois_refine C Option B — fa/fb depuis scan_arb")
    L(f"      Affinage t<300     : arb_hardy_z + mpmath.findroot (N<7 termes — légitime)")
    L(f"      Fallback           : arb_hardy_z + mpmath.findroot (hors intervalle)")
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
    L(f"      Score : {resultats_lmfdb.get('score','N/A')} à < 10⁻¹⁰")
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
    print("   CALCUL DES ZÉROS NON TRIVIAUX — v4.1 (Phase C)")
    print("=" * 65)
    print()
    scan_statut = "✓ scan_arb.so actif (Z_double C)" if SCAN_ARB_DISPONIBLE else "⚠ fallback Z_vect_correct"
    print(f"  Détection  : {scan_statut}")
    print(f"  Affinage   : Illinois C/Arb/mpmath")
    print(f"  Validation : Turing-Backlund")
    print(f"  .so : {SO_PATH}")
    print(f"  Z(t) fallback : {info_backend()}")
    print()
    print(f"  Estimation du temps ({min(8, multiprocessing.cpu_count())} workers) :")
    print("    T =   1 000  →  ~  396 zéros  →  ~  25 sec")
    print("    T =  10 000  →  ~ 4516 zéros  →  ~ 2.5 min")
    print("    T = 100 000  →  ~49k  zéros  →  ~  35 min")
    print()

    while True:
        try:
            T_MAX = float(input("  Entrez T_MAX (≥ 20) : "))
            if T_MAX >= 20:
                break
            print("  T_MAX doit être ≥ 20.")
        except ValueError:
            print("  Nombre invalide.")

    N_WORKERS = min(8, multiprocessing.cpu_count())
    STEP      = _step_adaptatif(T_MAX)
    print(f"\n  ── Configuration ──────────────────────────────")
    print(f"     T_MAX              = {T_MAX:.0f}")
    print(f"     N_WORKERS          = {N_WORKERS}")
    print(f"     STEP               = {STEP}")
    print(f"     T_SEUIL_ILLINOIS_C = {T_SEUIL_ILLINOIS_C}")
    print(f"     N zéros attendus   ≈ {N_attendu(T_MAX):.0f}")

    if input("\n  Lancer le calcul ? [O/n] : ").strip().lower() in ("n", "non"):
        sys.exit(0)

    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    dossier    = Path("calculs") / f"v4_1_T{T_MAX:.0f}_{horodatage}"
    dossier.mkdir(parents=True, exist_ok=True)
    return T_MAX, N_WORKERS, STEP, horodatage, dossier


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 8 — POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    debut_global = time.time()
    T_MIN = 14.0
    TOL   = 1e-12

    T_MAX, N_WORKERS, STEP, horodatage, dossier = saisir_parametres()

    # ── Calcul parallèle ─────────────────────────────────────────────────────
    print(f"\n  Lancement — {N_WORKERS} workers, STEP={STEP}, "
          f"Illinois C pour t ≥ {T_SEUIL_ILLINOIS_C:.0f}...\n")
    zeros, stats, profil_workers = calculer_zeros_v4_1(T_MIN, T_MAX, N_WORKERS, STEP, TOL)
    duree = time.time() - debut_global

    # ── Rapport ──────────────────────────────────────────────────────────────
    print()
    print("=" * 65)
    print("  RÉSULTATS v4.1")
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

    # ── Vérification LMFDB ───────────────────────────────────────────────────
    resultats_lmfdb  = verifier_lmfdb(zeros, n_check=20)

    # ── Validation Turing ────────────────────────────────────────────────────
    with chrono("turing"):
        resultats_turing = valider_turing(zeros, dps=30)

    # ── Profil des phases (localisation du goulot) ───────────────────────────
    # NB : phases workers (detection/illinois_C/mpmath_*) cumulées sur N_WORKERS ;
    #      phase 'turing' = process parent seul. Colonnes 'temps_cumul' et
    #      'ms/appel' sont les indicateurs fiables ; '% mur×W' est indicatif.
    profil_total = agreger([profil_workers, snapshot()])
    print()
    print(rapport(profil_total, duree_run=duree, n_workers=N_WORKERS))

    # ── Sauvegarde ───────────────────────────────────────────────────────────
    chemin_csv = sauvegarder_csv(
        zeros, stats, T_MAX, STEP, N_WORKERS, horodatage, dossier
    )
    visualiser(zeros, T_MAX, horodatage, dossier)

    nom_log    = f"execution_v4_1_T{T_MAX:.0f}_{horodatage}.log"
    chemin_log = dossier / nom_log
    ecrire_log(
        chemin_log, horodatage, T_MIN, T_MAX, STEP, N_WORKERS,
        TOL, duree, zeros, stats, resultats_lmfdb, resultats_turing, chemin_csv
    )

    # ── Conclusion ───────────────────────────────────────────────────────────
    print()
    print("=" * 65)
    print(f"  v4.1 terminée — fichiers dans : {dossier}")
    if resultats_turing["complet"]:
        print("  Validation Turing : COMPLET (aucun zéro manqué)")
    else:
        manq = resultats_turing["manquants_total"]
        print(f"  Validation Turing : {manq} zéros manquants — réduire STEP")
    print("=" * 65)


if __name__ == "__main__":
    main()
