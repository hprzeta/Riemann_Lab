#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_zeros_v15.py — Phase C v15 : Phase 2 adaptative (SEUIL_1NEWTON=20k)
═════════════════════════════════════════════════════════════════════════════
v15 (2026-07-04) : optimisation Phase 2 Illinois dans illinois_arb.c.

Diagnostic v14 T=100k (7.7 min, 299 z/s) :
  Illinois Phase 2 domine (~98% du temps) — 2 Newton Z_arb systématiques.
  Pour t > ~50k : early-exit au k=0 déjà → 1 seul Z_arb effectif.
  Pour t ∈ [20k, 50k] : early-exit rare → 2 Z_arb toujours exécutés.

Optimisation v15 :
  SEUIL_1NEWTON = 20 000 dans illinois_arb.c Phase 2.
  t ≥ 20 000 : 1 Newton Z_arb (biais_RS ≈ 6.4e-7 → erreur ~4e-13 < tol=1e-12).
  t < 20 000 : 2 Newton Z_arb inchangé (biais_RS trop grand pour 1 Newton).
  N(20k)/N(100k) ≈ 12.8% des zéros gardent 2 Newton.
  Gain estimé : ×1.77 sur Illinois → T=100k 7.7 → ~4.3 min.

Invariants conservés depuis v14 :
  Cache log_n/isqrt_n : illinois_arb.c + scan_arb.c (inchangé)
  Phase 1 : Illinois Z_rs C → |b-a| < 1e-6 (inchangé)
  T_SEUIL_PETIT_T : 65.0 (inchangé)
  TOL_ARB : 1e-12 (inchangé)
  STEP    : adaptatif κ·gap_moyen(T)·N(T)^(-1/3)/2 (inchangé)
  Workers : 8 (inchangé)

Auteur : hprzeta — Projet Hypothèse de Riemann — Phase C
Date   : 2026-07-04
"""

import os
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

    Recherche binaire pour trouver T_i tels que N(T_i) = N(T_MIN) + i × (N(T_MAX)-N(T_MIN))/W.
    Cibles relatives à N(T_MIN) — indispensable dès que T_MIN ≠ 0 (sous-segment d'un run
    distribué ou rescan ciblé) : sans cela, les cibles i×N(T_MAX)/W restent presque toutes
    inférieures à N(T_MIN), la recherche binaire s'effondre vers T_MIN pour tous les workers
    sauf le dernier, qui se retrouve à traiter tout l'intervalle seul (bug constaté le
    17/06/2026 sur les rescans test_scan_fix_worker6/7 — 7 workers sur 8 inactifs).
    Overlap fixe 0.5 — couvre les brackets sur les bords de segment.
    """
    N_min   = _n_zeros_expected(T_MIN)
    N_total = _n_zeros_expected(T_MAX) - N_min
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
        n_cible = N_min + i * N_total // N_WORKERS
        t_next  = _t_pour_n(n_cible, T_MIN, T_MAX)
        segments.append((t_prev, min(t_next + OVERLAP, T_MAX)))
        t_prev  = t_next
    segments.append((t_prev, T_MAX))
    return segments


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — WORKER MULTIPROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

TOL_ARB  = 1e-12  # tolérance illinois_refine_arb — abaissée de 1e-9 à 1e-12
                  # (double précision ~1e-15 → 1e-12 fiable ; 1e-9 trop proche du
                  # seuil LMFDB et causait 16/20 au lieu de 20/20)
MAX_ITER = 50     # max itérations Illinois (convergence rapide avec Arb)

def worker_v15(args: tuple) -> Tuple[list, dict, dict]:
    """Worker v15 — détection scan_arb.c + affinage illinois_refine_arb.

    Charge illinois_arb.so APRÈS le fork() → pas de corruption mémoire partagée.
    Détection : scan_arb C (Z_double RS + C0+C1, step=0.010) pour t ≥ 20
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
    lib.arb_set_debug_log.restype   = None
    lib.arb_set_debug_log.argtypes  = [ctypes.c_char_p]
    lib.arb_close_debug_log.restype  = None
    lib.arb_close_debug_log.argtypes = []

    # Activation des logs brackets si ZETA_DEBUG_BRACKETS=<répertoire>
    _dbg_dir = os.environ.get("ZETA_DEBUG_BRACKETS", "")
    if _dbg_dir:
        os.makedirs(_dbg_dir, exist_ok=True)
        _scan_log = os.path.join(_dbg_dir, f"scan_w{worker_id}.log")
        _arb_log  = os.path.join(_dbg_dir, f"arb_w{worker_id}.log")
        if SCAN_ARB_DISPONIBLE:
            from scan_arb_wrapper import scan_enable_debug_log
            scan_enable_debug_log(_scan_log)
        lib.arb_set_debug_log(_arb_log.encode())

    # v13 : seuil abaissé de 200 → 65.
    #
    # Pourquoi 65 et pas 20 ?
    #   scan_arb (Z_double) a N_RS=2 termes pour t ∈ [25, 57) et N_RS=3 pour t ∈ [57, 101).
    #   À N_RS=2, l'erreur RS peut atteindre ~0.03 → le bracket [a,b] peut être décalé
    #   de 0.01-0.05 par rapport au vrai zéro. illinois_refine_arb reçoit alors des
    #   fa/fb de mauvais signe et converge vers une valeur décalée (écart constaté : ~3e-9).
    #   Filtrer les brackets spurieux (re-évaluer fa/fb et sauter si même signe) efface
    #   aussi les vrais zéros dont scan_arb a placé le bracket au mauvais endroit.
    #   → seule solution correcte : garder arb_hardy_z+mpmath pour t < 65 (N_RS ≤ 2).
    #
    # Pourquoi pas 100 ?
    #   (100-14)/0.01 = 8 600 évals mpmath → ~47s sur PC2 (6.4 → 14 z/s, sous critère 20 z/s).
    #   (65-14)/0.01 = 5 100 évals mpmath → ~27s sur PC2 (6.4 → 24 z/s ✅).
    #
    # À t=65 (N_RS=3), les tests v13 montrent tous les zéros LMFDB ≥ t=65 conformes (< 1e-9).
    T_SEUIL_PETIT_T = 65.0

    zeros_segment = []
    stats         = {"arb_C": 0, "mpmath_fallback": 0, "mpmath_petit_t": 0}
    _log_palier   = 0

    # ── Petits t ∈ [14, 65] : détection arb_hardy_z + affinage mp.fp.siegelz ──
    # ~5 100 évaluations au lieu de ~18 600 (économie ×3.6 vs v12 sur PC2).
    # Détection : arb_hardy_z (Arb/FLINT, signes garantis pour tout t ≥ 14).
    # Affinage  : mp.fp.findroot + mp.fp.siegelz (float64 natif, sans overhead mpf).
    # Pour t < 65 (N_RS ≤ 3 termes), float64 amplement suffisant pour tol=1e-12.
    if t_start < T_SEUIL_PETIT_T:
        t_fin_pt = min(T_SEUIL_PETIT_T, t_end)
        with chrono("mpmath_petit_t"):
            t_arr_pt = np.arange(t_start, t_fin_pt, step, dtype=np.float64)
            if len(t_arr_pt) >= 2:
                Zv_pt = np.array([arb_hardy_z(float(t)) for t in t_arr_pt])
                for j in np.where(np.diff(np.sign(Zv_pt)))[0]:
                    try:
                        z = float(mpmath.fp.findroot(
                            mpmath.fp.siegelz,
                            (float(t_arr_pt[j]), float(t_arr_pt[j+1])),
                            solver="illinois", tol=1e-12, maxsteps=80,
                        ))
                        zeros_segment.append(z)
                        stats["mpmath_petit_t"] += 1
                    except Exception:
                        pass
        # Continuer avec scan_arb pour la partie [20, t_end]
        t_start_main = t_fin_pt
    else:
        t_start_main = t_start

    # ── Détection : scan_arb C ou Z_vect_correct numpy (fallback) ────────────
    # max_brackets dynamique : N(t_end) - N(t_start) × 2 — évite le dépassement
    # silencieux du buffer (bug constaté run debug 26/06/2026 : chaque worker plafonnait
    # à 100 000 brackets alors que T=500k en demande ~102 302 par worker → 16 107 manquants)
    def _n_zeros_approx(T: float) -> float:
        if T <= 14: return 0.0
        return (T / (2 * math.pi)) * math.log(T / (2 * math.pi * math.e))
    _max_brackets = max(150_000,
                        int((_n_zeros_approx(t_end) - _n_zeros_approx(max(t_start, 14.1))) * 2))

    if SCAN_ARB_DISPONIBLE:
        with chrono("detection"):
            brackets = scan_arb(t_start_main, t_end, step=step, max_brackets=_max_brackets) if t_start_main < t_end else []
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

    # ── Affinage : illinois_refine_arb (Arb) pour tout t ≥ T_SEUIL_PETIT_T ──
    # Pas de seuil t=300 : Arb est valide sans biais RS pour tout t ≥ 14.
    # À t ≥ 65 : N_RS ≥ 3, erreur Z_double < 0.006 → signes fa/fb fiables.
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

    if _dbg_dir:
        if SCAN_ARB_DISPONIBLE:
            from scan_arb_wrapper import scan_disable_debug_log
            scan_disable_debug_log()
        lib.arb_close_debug_log()

    return zeros_segment, stats, snapshot()


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — ORCHESTRATEUR PARALLÈLE
# ═══════════════════════════════════════════════════════════════════════════════

def calculer_zeros_v15(
    T_MIN     : float,
    T_MAX     : float,
    N_WORKERS : int,
    STEP      : float,
    TOL       : float = 1e-9,
) -> Tuple[List[float], dict, dict, list]:
    """Lance N_WORKERS processus sur [T_MIN, T_MAX], fusionne et déduplique.

    Retourne (zeros, stats, profil_workers, segments) — segments exposé pour
    permettre le rescan ciblé par déficit en aval.
    """
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
        resultats = pool.map(worker_v15, args_list)

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
    return zeros, stats_total, profil_workers, segments


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 3b — RESCAN CIBLÉ PAR DÉFICIT
# ═══════════════════════════════════════════════════════════════════════════════

def rescan_segments_deficit(
    zeros         : List[float],
    segments      : List[Tuple[float, float]],
    T_MAX         : float,
    step_original : float,
) -> Tuple[List[float], List[dict]]:
    """Rescan ciblé des segments workers en déficit avec STEP/2.

    Après le run principal, compare pour chaque segment le nombre de zéros
    trouvés au nombre attendu par N(T). Tout segment en déficit est re-scanné
    avec STEP/2 — ce décalage de phase peut capturer les zéros manqués lors
    du premier passage (cause confirmée 26/06/2026 : les manquants sont des
    ratés du scan Z_double, pas des rejets illinois).

    Le pipeline de rescan est identique à worker_v14 (même illinois_arb.so,
    même TOL_ARB) — seul le STEP change.
    Fonctionne sur PC1 uniquement (pas de distribution PC2).

    Retourne (zeros_bruts_rescan, rapport) où zeros_bruts_rescan est la liste
    brute des zéros trouvés dans les segments rescannés — la déduplication se
    fait en aval dans main() via dedupliquer(zeros + zeros_bruts_rescan).
    """
    step_rescan  = step_original / 2.0
    zeros_rescan = []  # bruts — déduplication en aval
    rapport      = []

    # Bornes non chevauchantes : start de chaque segment + T_MAX final.
    # Segment i couvre [checkpoints[i], checkpoints[i+1]) pour le comptage ;
    # le rescan utilise les bornes originales (avec overlap) pour ne pas rater
    # les brackets de frontière.
    checkpoints = [s[0] for s in segments] + [T_MAX]

    print()
    print("=" * 65)
    print("  RESCAN CIBLÉ — vérification déficits par segment")
    print(f"  STEP original = {step_original:.6f}  →  STEP rescan = {step_rescan:.6f}")
    print("=" * 65)

    # Première passe : identifier les segments en déficit
    infos = []  # (i, seg_a, seg_b, t_lo, t_hi, deficit)
    for i, (seg_a, seg_b) in enumerate(segments):
        t_lo       = checkpoints[i]
        t_hi       = checkpoints[i + 1]
        n_trouves  = sum(1 for z in zeros if t_lo <= z < t_hi)
        n_attendus = _n_zeros_expected(t_hi) - _n_zeros_expected(t_lo)
        deficit    = n_attendus - n_trouves
        sym        = "✅" if deficit <= 0 else f"⚠  déficit {deficit:+d}"
        print(f"  Seg {i:>2}  [{t_lo:>10.1f}, {t_hi:>10.1f}]  "
              f"{n_trouves:>7}/{n_attendus:<7}  {sym}")
        infos.append((i, seg_a, seg_b, t_lo, t_hi, deficit))

    segments_a_rescanner = [(i, seg_a, seg_b, t_lo, t_hi, d)
                            for i, seg_a, seg_b, t_lo, t_hi, d in infos if d > 0]

    if not segments_a_rescanner:
        print(f"\n  Aucun déficit détecté — rescan inutile.")
        print("=" * 65)
        return [], []

    print(f"\n  {len(segments_a_rescanner)} segment(s) en déficit → "
          f"rescan parallèle STEP={step_rescan:.6f} ...", flush=True)
    debut_rescan = time.time()

    # Rescan parallèle : un worker par segment en déficit (Pool)
    # worker_id 100+i pour distinguer dans les logs des workers principaux
    args_rescan = [
        (seg_a, seg_b, step_rescan, SO_PATH, TOL_ARB, 100 + i)
        for i, seg_a, seg_b, t_lo, t_hi, d in segments_a_rescanner
    ]
    with multiprocessing.Pool(processes=len(args_rescan)) as pool:
        resultats_rescan = pool.map(worker_v15, args_rescan)

    duree_rescan = time.time() - debut_rescan
    print(f"  Rescan terminé en {duree_rescan:.1f}s")

    for (i, seg_a, seg_b, t_lo, t_hi, d), (zs, _, _) in zip(
            segments_a_rescanner, resultats_rescan):
        zeros_rescan.extend(zs)
        print(f"  Seg {i:>2}  [{t_lo:>10.1f}, {t_hi:>10.1f}]  "
              f"→ {len(zs)} zéros rescannés")
        rapport.append({
            "segment": i, "t_lo": t_lo, "t_hi": t_hi,
            "deficit": d, "recuperes": len(zs),
            "rescanne": True, "duree_s": duree_rescan,
        })

    # Compléter le rapport pour les segments non rescannés
    rescannés_ids = {i for i, *_ in segments_a_rescanner}
    for i, seg_a, seg_b, t_lo, t_hi, d in infos:
        if i not in rescannés_ids:
            rapport.append({
                "segment": i, "t_lo": t_lo, "t_hi": t_hi,
                "deficit": d, "recuperes": 0, "rescanne": False,
            })
    rapport.sort(key=lambda r: r["segment"])

    total_brut = len(zeros_rescan)
    print(f"\n  Segments rescannés : {len(segments_a_rescanner)}  —  "
          f"{total_brut} zéros bruts (avant déduplication)")
    print("=" * 65)
    return zeros_rescan, rapport


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
        f"Zéros de ζ(½+it) — v14 — {len(zeros)} zéros [T_MAX={T_MAX:.0f}]",
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
    nom_png = f"zeros_v15_T{T_MAX:.0f}_{horodatage}.png"
    plt.savefig(str(dossier / nom_png), dpi=150)
    plt.close()
    print(f"  Graphique → {nom_png}")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — SAUVEGARDE CSV + LOG
# ═══════════════════════════════════════════════════════════════════════════════

def sauvegarder_csv(zeros, stats, T_MAX, STEP, N_WORKERS,
                    horodatage, dossier) -> Path:
    nom        = f"zeros_v15_T{T_MAX:.0f}_{horodatage}.csv"
    chemin_csv = dossier / nom
    df = pd.DataFrame({
        "n":                 range(1, len(zeros) + 1),
        "partie_imaginaire": zeros,
        "T_MAX":             T_MAX,
        "version":           "v15",
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
               resultats_turing, chemin_csv, rapport_rescan=None):
    """Journal d'exécution v14."""
    lignes = []
    sep    = "=" * 65

    def L(t=""): lignes.append(t)

    L(sep)
    L("  JOURNAL D'EXÉCUTION — compute_zeros_v15.py  (Phase C)")
    L("  Projet : Hypothèse de Riemann — hprzeta")
    L(sep); L()

    L("  [1] HORODATAGE")
    L(f"      Début  : {horodatage}")
    L(f"      Fin    : {datetime.now().strftime('%Y%m%d_%H%M%S')}")
    L(f"      Durée  : {duree_s/60:.2f} min  ({duree_s:.1f} s)")
    L()

    L("  [2] PARAMÈTRES v14")
    L(f"      T_MIN              = {T_MIN}")
    L(f"      T_MAX              = {T_MAX}")
    L(f"      STEP               = {STEP}")
    L(f"      TOL_ARB            = {tol:.0e}  (double, illinois_refine_arb)")
    L(f"      N_WORKERS          = {N_WORKERS}")
    L(f"      T_SEUIL_PETIT_T    = 65.0  (abaissé de 200 — v13 ; N_RS=2 fiable dès t=65)")
    L(f"      illinois_arb.so    : {SO_PATH}")
    scan_str = "scan_arb C (Z_double RS C0+C1)" if SCAN_ARB_DISPONIBLE else "Z_vect_correct numpy (fallback)"
    L(f"      Détection          : {scan_str} pour t ≥ 20")
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

    L("  [7] RESCAN CIBLÉ PAR DÉFICIT")
    if rapport_rescan is None:
        L("      (non exécuté)")
    else:
        n_rescannés = sum(1 for r in rapport_rescan if r["rescanne"])
        n_récupérés = sum(r["recuperes"] for r in rapport_rescan if r["rescanne"])
        L(f"      Segments rescannés : {n_rescannés}/{len(rapport_rescan)}")
        L(f"      Zéros bruts récupérés (avant dédup) : {n_récupérés}")
        for r in rapport_rescan:
            if r["rescanne"]:
                duree_r = r.get("duree_s", 0)
                L(f"      Seg {r['segment']:>2}  [{r['t_lo']:>10.1f}, {r['t_hi']:>10.1f}]"
                  f"  déficit={r['deficit']:+d}  récupérés={r['recuperes']}  {duree_r:.1f}s")
    L()

    L("  [8] FICHIERS GÉNÉRÉS")
    L(f"      CSV → {chemin_csv}")
    L(f"      LOG → {chemin_log}")
    L()

    import platform
    L("  [9] ENVIRONNEMENT")
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
    """STEP réellement adaptatif — recalibré le 17/06/2026 après échec Turing à T=500000.

    L'ancien STEP fixe (0.010, gap-safe à T=100000 seulement) a manqué 6 zéros sur le
    run distribué T=500000 (818408/818414, cf. claude-traitement-journalier/
    Process_Distribution_PC1_PC2_20260617.md). Cause : si deux zéros tombent dans le
    même pas STEP, Z(a) et Z(b) ont le MÊME signe (deux changements de signe
    s'annulent) → la paire disparaît sans laisser de trace visible dans les données.

    Constat empirique (mesuré sur les 818408 zéros du run T=500000) :
        écart minimal SURVIVANT avec STEP=0.010 :
            0.019   à T≈ 66678   (marge ×1.9)
            0.01281 à T≈453540   (marge ×1.28 — quasi-échec)
    L'écart minimal global décroît avec le NOMBRE TOTAL de zéros échantillonnés N(T),
    pas seulement avec l'écart moyen (répulsion de niveaux GUE : la densité de paires
    proches s'annule en ~r³ près de 0 ⇒ écart minimal attendu sur N tirages ~ N^(-1/3)).
    Un STEP fixe, ou même proportionnel au seul écart moyen, échoue donc TOUJOURS à T
    suffisamment grand.

    Modèle retenu (ordre de grandeur, pas un théorème) :
        min_gap(T) ≈ κ · gap_moyen(T) · N(T)^(-1/3)
        STEP(T)    = min_gap(T) / MARGE_SECURITE

    κ ≈ 1.357 calibré sur le seul point fiable (T=100000, run Turing COMPLET).
    MARGE_SECURITE = 3.0 (restaurée le 02/08/2026 — avait été abaissée à 2.0 juste
    avant le run T=5M du 27-29/06/2026 (commit a0e6e41), qui a donné 96 zéros
    manquants, avec rescan STEP/2 récupérant seulement +1 zéro net. Cette baisse
    2.0 annulait sans le documenter le correctif du 23/06 (commit 7914fa3), déjà
    posé après que le run T=500000 distribué eut donné 8 manquants avec marge=2.0.
    """
    KAPPA = 1.357
    MARGE_SECURITE = 3.0
    T = max(float(T_MAX), 100.0)  # garde-fou : log/N indéfinis sous 2πe
    gap_moyen = 2 * math.pi / math.log(T / (2 * math.pi * math.e))
    N_T = (T / (2 * math.pi)) * math.log(T / (2 * math.pi * math.e))
    return KAPPA * gap_moyen * N_T ** (-1 / 3) / MARGE_SECURITE


def saisir_parametres():
    print()
    print("=" * 65)
    print("   CALCUL DES ZÉROS NON TRIVIAUX — v14 (Phase C / Arb)")
    print("=" * 65)
    print()
    scan_statut = "✓ scan_arb.so actif (Z_double C)" if SCAN_ARB_DISPONIBLE else "⚠ fallback Z_vect_correct"
    print(f"  Détection  : {scan_statut} [t ≥ 20]")
    print(f"  Affinage   : illinois_refine_arb (Arb/FLINT, tout t)")
    print(f"  Validation : Turing-Backlund")
    print(f"  .so : {SO_PATH}")
    print(f"  Backend Arb : {info_backend()}")
    print(f"  Seuil petit-t : 65.0  (abaissé de 200 — N_RS=2 fiable dès t=65, 24 z/s sur PC2)")
    print()
    print(f"  Estimations (8 workers) :")
    print("    T =   1 000  →  ~  649 zéros  →  ~  < 5 sec")
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
    dossier    = Path("calculs") / f"v15_T{T_MAX:.0f}_{horodatage}"
    dossier.mkdir(parents=True, exist_ok=True)
    return T_MAX, N_WORKERS, STEP, horodatage, dossier


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 8 — POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    debut_global = time.time()

    # Mode CLI non-interactif pour la distribution : --t-min T --t-max T [--horodatage TS]
    import argparse
    _p = argparse.ArgumentParser(add_help=False)
    _p.add_argument("--t-min",      type=float, default=None)
    _p.add_argument("--t-max",      type=float, default=None)
    _p.add_argument("--horodatage", type=str,   default=None)
    _cli, _ = _p.parse_known_args()

    if _cli.t_min is not None and _cli.t_max is not None:
        T_MIN      = _cli.t_min
        T_MAX      = _cli.t_max
        N_WORKERS  = 8
        STEP       = _step_adaptatif(T_MAX)
        horodatage = _cli.horodatage or datetime.now().strftime("%Y%m%d_%H%M%S")
        dossier    = Path("calculs") / f"v15_T{T_MIN:.0f}_{T_MAX:.0f}_{horodatage}"
        dossier.mkdir(parents=True, exist_ok=True)
        print(f"\n  [Mode distribué] [{T_MIN:.1f}, {T_MAX:.1f}] — "
              f"{N_WORKERS} workers — STEP={STEP}")
    else:
        T_MIN = 14.0
        T_MAX, N_WORKERS, STEP, horodatage, dossier = saisir_parametres()

    print(f"\n  Lancement — {N_WORKERS} workers, STEP={STEP}, "
          f"T_SEUIL_PETIT_T=20, illinois_refine_arb pour tout t...\n")
    zeros, stats, profil_workers, segments = calculer_zeros_v15(
        T_MIN, T_MAX, N_WORKERS, STEP, TOL_ARB
    )
    duree_run_principal = time.time() - debut_global

    print()
    print("=" * 65)
    print("  RÉSULTATS v15 — run principal")
    print("=" * 65)
    print(f"  Zéros trouvés     : {len(zeros)}")
    print(f"  Attendus (Weyl)   : {N_attendu(T_MAX):.0f}")
    print(f"  Durée run         : {duree_run_principal/60:.1f} min  ({duree_run_principal:.1f} s)")
    vitesse = len(zeros) / duree_run_principal if duree_run_principal > 0 else 0
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

    # ── Rescan ciblé des segments en déficit (PC1 uniquement) ───────────────
    # Ne s'exécute que si le mode distribué n'est pas actif (T_MIN == 14.0),
    # car les segments distribués (PC2) ne sont pas disponibles localement.
    rapport_rescan = None
    if _cli.t_min is None:  # mode interactif (run complet local)
        zeros_bruts_rescan, rapport_rescan = rescan_segments_deficit(
            zeros, segments, T_MAX, STEP
        )
        if zeros_bruts_rescan:
            n_avant = len(zeros)
            zeros   = dedupliquer(zeros + zeros_bruts_rescan, tolerance=0.01)
            n_net   = len(zeros) - n_avant
            print(f"\n  Après fusion rescan : {len(zeros)} zéros  "
                  f"(+{n_net} nets après déduplication)")

    duree = time.time() - debut_global  # durée totale incluant le rescan

    # ── Vérification finale sur la liste complète ────────────────────────────
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

    nom_log    = f"execution_v15_T{T_MAX:.0f}_{horodatage}.log"
    chemin_log = dossier / nom_log
    ecrire_log(
        chemin_log, horodatage, T_MIN, T_MAX, STEP, N_WORKERS,
        TOL_ARB, duree, zeros, stats, resultats_lmfdb, resultats_turing,
        chemin_csv, rapport_rescan=rapport_rescan,
    )

    print()
    print("=" * 65)
    print(f"  v15 terminée — fichiers dans : {dossier}")
    if resultats_turing["complet"]:
        print("  Validation Turing : ✅ COMPLET (aucun zéro manqué)")
    else:
        manq = resultats_turing["manquants_total"]
        print(f"  Validation Turing : ❌ {manq} zéros manquants")
        if rapport_rescan is not None:
            n_rescannés = sum(1 for r in rapport_rescan if r["rescanne"])
            print(f"  Rescan ciblé      : {n_rescannés} segments rescannés")
    print("=" * 65)


if __name__ == "__main__":
    main()
