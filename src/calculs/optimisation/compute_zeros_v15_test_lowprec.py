#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_zeros_v15_test_lowprec.py — VALIDATION EXPÉRIMENTALE, PAS UN SCRIPT DE PRODUCTION
═════════════════════════════════════════════════════════════════════════════
Copie quasi à l'identique de compute_zeros_v15.py (production, NON MODIFIÉ),
avec un diff minimal et explicitement marqué "### LOWPREC ###" ci-dessous :

  - SO_PATH pointe vers illinois_arb_lowprec.so (nouveau fichier, ne remplace
    pas illinois_arb.so) au lieu de illinois_arb.so
  - Le worker appelle illinois_refine_arb_lowprec (acb_dirichlet_hardy_z à
    précision FIXE 64 bits, sans la boucle d'escalade arb_fpwrap 64->8192
    bits) au lieu de illinois_refine_arb (arb_fpwrap flags=0)
  - Dossier de sortie distinct (calculs/v15_LOWPREC_TEST_...) pour ne jamais
    se mélanger avec des sorties de run réel en production

Objectif : valider sur un run réel (pas seulement 300 brackets synthétiques)
que le gain mesuré (×5.75 à prec=64 bits, résultat identique bit-à-bit à la
production sur les 300 brackets) tient à l'échelle — Turing-Backlund + LMFDB.

Precision retenue : 64 bits (décision hprzeta 08/08/2026, cf. Handoff.md —
coïncide avec WP_INITIAL de arb_fpwrap, marge de sécurité vs les 40 bits
théoriquement nécessaires pour tol=1e-12).

illinois_arb.c et compute_zeros_v15.py de PRODUCTION NE SONT PAS MODIFIÉS.

Auteur : hprzeta — Projet Hypothèse de Riemann — Phase C (expérimental)
Date   : 2026-08-08
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

### LOWPREC ### — .so de test, PAS illinois_arb.so de production
SO_PATH = Path(__file__).parent / "c_modules" / "illinois_arb_lowprec.so"
### LOWPREC ### — précision fixe retenue (décision hprzeta 08/08/2026)
PREC_BITS_LOWPREC = 64

if not SO_PATH.exists():
    raise FileNotFoundError(
        f"illinois_arb_lowprec.so introuvable : {SO_PATH}\n"
        f"Ce script est un test expérimental — recompiler depuis "
        f"c_modules/illinois_arb_lowprec.c si besoin."
    )


def _n_zeros_expected(T: float) -> int:
    """N(T) — formule de Riemann-von Mangoldt (le 'e' dans 2πe est OBLIGATOIRE)."""
    if T < 14.0:
        return 0
    return int(T / (2 * math.pi) * math.log(T / (2 * math.pi * math.e)))


def _partitionner_adaptatif(
    T_MIN: float, T_MAX: float, N_WORKERS: int
) -> list:
    """Segments équitables par inversion de N(T) — identique à la production."""
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

TOL_ARB  = 1e-12
MAX_ITER = 50

def worker_v15(args: tuple) -> Tuple[list, dict, dict]:
    """Worker v15 — IDENTIQUE à la production sauf l'appel Illinois (### LOWPREC ###)."""
    t_start, t_end, step, so_path, tol, worker_id = args
    debut = time.time()

    lib = ctypes.CDLL(str(so_path))
    ### LOWPREC ### — illinois_refine_arb_lowprec (7 args : + prec_bits) au lieu
    ### de illinois_refine_arb (6 args) de la production
    lib.illinois_refine_arb_lowprec.restype  = ctypes.c_double
    lib.illinois_refine_arb_lowprec.argtypes = [
        ctypes.c_double,  # a
        ctypes.c_double,  # b
        ctypes.c_double,  # fa
        ctypes.c_double,  # fb
        ctypes.c_double,  # tol
        ctypes.c_int,     # max_iter
        ctypes.c_int,     # prec_bits — nouveau vs production
    ]
    lib.arb_set_debug_log.restype   = None
    lib.arb_set_debug_log.argtypes  = [ctypes.c_char_p]
    lib.arb_close_debug_log.restype  = None
    lib.arb_close_debug_log.argtypes = []

    _dbg_dir = os.environ.get("ZETA_DEBUG_BRACKETS", "")
    if _dbg_dir:
        os.makedirs(_dbg_dir, exist_ok=True)
        _scan_log = os.path.join(_dbg_dir, f"scan_w{worker_id}.log")
        _arb_log  = os.path.join(_dbg_dir, f"arb_w{worker_id}.log")
        if SCAN_ARB_DISPONIBLE:
            from scan_arb_wrapper import scan_enable_debug_log
            scan_enable_debug_log(_scan_log)
        lib.arb_set_debug_log(_arb_log.encode())

    T_SEUIL_PETIT_T = 65.0

    zeros_segment = []
    stats         = {"arb_C": 0, "mpmath_fallback": 0, "mpmath_petit_t": 0}
    _log_palier   = 0

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
        t_start_main = t_fin_pt
    else:
        t_start_main = t_start

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

    for a, b, fa, fb in brackets:
        try:
            with chrono("arb_C"):
                ### LOWPREC ### — appel avec prec_bits en 7e argument
                zero = lib.illinois_refine_arb_lowprec(
                    a, b, float(fa), float(fb),
                    TOL_ARB, MAX_ITER, PREC_BITS_LOWPREC,
                )

            if a - 1e-10 <= zero <= b + 1e-10:
                zeros_segment.append(zero)
                stats["arb_C"] += 1
            else:
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
#  SECTION 5 — SAUVEGARDE CSV
# ═══════════════════════════════════════════════════════════════════════════════

def sauvegarder_csv(zeros, stats, T_MAX, STEP, N_WORKERS,
                    horodatage, dossier) -> Path:
    ### LOWPREC ### — préfixe distinct pour ne jamais confondre avec un run production
    nom        = f"zeros_v15_LOWPREC_TEST_T{T_MAX:.0f}_{horodatage}.csv"
    chemin_csv = dossier / nom
    df = pd.DataFrame({
        "n":                 range(1, len(zeros) + 1),
        "partie_imaginaire": zeros,
        "T_MAX":             T_MAX,
        "version":           "v15_lowprec_test",
        "methode_affinage":  f"arb_C_lowprec_{PREC_BITS_LOWPREC}bits",
        "step":              STEP,
        "n_workers":         N_WORKERS,
        "calcule_le":        horodatage,
    })
    df.to_csv(str(chemin_csv), index=False)
    print(f"  {len(zeros)} zéros → {chemin_csv}")
    return chemin_csv


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — STEP adaptatif (identique production)
# ═══════════════════════════════════════════════════════════════════════════════

def _step_adaptatif(T_MAX: float) -> float:
    """STEP adaptatif — identique à compute_zeros_v15.py (production), voir
    ce fichier pour la justification complète (KAPPA, MARGE_SECURITE)."""
    KAPPA = 1.357
    MARGE_SECURITE = 10.0
    T = max(float(T_MAX), 100.0)
    gap_moyen = 2 * math.pi / math.log(T / (2 * math.pi * math.e))
    N_T = (T / (2 * math.pi)) * math.log(T / (2 * math.pi * math.e))
    return KAPPA * gap_moyen * N_T ** (-1 / 3) / MARGE_SECURITE


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 7 — POINT D'ENTRÉE (mode CLI uniquement — pas de saisie interactive
#  pour ce script de test, on force T_MAX en argument)
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    debut_global = time.time()

    import argparse
    _p = argparse.ArgumentParser(description="TEST EXPÉRIMENTAL lowprec — pas la production")
    _p.add_argument("--t-max", type=float, required=True)
    _p.add_argument("--n-workers", type=int, default=8)
    _cli = _p.parse_args()

    T_MIN     = 14.0
    T_MAX     = _cli.t_max
    N_WORKERS = _cli.n_workers
    STEP      = _step_adaptatif(T_MAX)
    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    dossier    = Path("calculs") / f"v15_LOWPREC_TEST_T{T_MAX:.0f}_{horodatage}"
    dossier.mkdir(parents=True, exist_ok=True)

    print()
    print("=" * 65)
    print("   TEST EXPÉRIMENTAL — illinois_refine_arb_lowprec")
    print(f"   Précision fixe : {PREC_BITS_LOWPREC} bits (acb_dirichlet_hardy_z direct)")
    print("   PAS UN RUN DE PRODUCTION — illinois_arb.so non utilisé")
    print("=" * 65)
    print(f"  T_MAX={T_MAX:.0f}  N_WORKERS={N_WORKERS}  STEP={STEP}")
    print(f"  .so : {SO_PATH}")
    print()

    zeros, stats, profil_workers, segments = calculer_zeros_v15(
        T_MIN, T_MAX, N_WORKERS, STEP, TOL_ARB
    )
    duree_run = time.time() - debut_global

    print()
    print("=" * 65)
    print("  RÉSULTATS — TEST LOWPREC (64 bits)")
    print("=" * 65)
    print(f"  Zéros trouvés     : {len(zeros)}")
    print(f"  Attendus (Weyl)   : {N_attendu(T_MAX):.0f}")
    print(f"  Durée run         : {duree_run/60:.2f} min  ({duree_run:.1f} s)")
    vitesse = len(zeros) / duree_run if duree_run > 0 else 0
    print(f"  Vitesse           : {vitesse:.2f} zéros/s")
    print()
    print("  Répartition des méthodes d'affinage :")
    total = sum(stats.values())
    for methode, nb in sorted(stats.items()):
        pct = nb / total * 100 if total > 0 else 0
        print(f"    {methode:<24} : {nb:>6}  ({pct:.1f}%)")
    print("=" * 65)

    resultats_lmfdb  = verifier_lmfdb(zeros, n_check=20)

    with chrono("turing"):
        resultats_turing = valider_turing(zeros, dps=30)

    chemin_csv = sauvegarder_csv(zeros, stats, T_MAX, STEP, N_WORKERS, horodatage, dossier)

    print()
    print("=" * 65)
    print(f"  TEST LOWPREC terminé — fichiers dans : {dossier}")
    if resultats_turing["complet"]:
        print("  Validation Turing : ✅ COMPLET (aucun zéro manqué)")
    else:
        manq = resultats_turing["manquants_total"]
        print(f"  Validation Turing : ❌ {manq} zéros manquants")
    print(f"  Score LMFDB : {resultats_lmfdb.get('score','N/A')}")
    print("=" * 65)


if __name__ == "__main__":
    main()
