#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
benchmark_methodes.py — Benchmark illinois_refine_bench sur 500 zéros T=100k v7
═══════════════════════════════════════════════════════════════════════════════
Mesures :
  - ms/appel moyen (appel C illinois_refine_bench 64→80 bits)
  - itérations phase1 + phase2 séparément (miroir Python de l'algorithme C)
  - ms/appel aux paliers t = 1k, 10k, 50k, 77k
  - distribution itérations (min/max/moy)

Source des zéros : CSV T=100k v7 (calculs/v4_1_T100000_20260611_142434/)
Méthode         : NE recalcule PAS les zéros — charge les brackets, mesure l'affinage
Chargement .so  : POST-FORK (multiprocessing.Pool), identique à compute_zeros_v7.py

Auteur : hprzeta — Projet Riemann_Lab
Date   : 2026-06-12
"""

import ctypes
import csv
import math
import multiprocessing
import time
from pathlib import Path

import numpy as np
from riemann_siegel_batch import Z_vect_correct   # Z(t) RS numpy — rapide, correct

# ── Constantes v8 (identiques à compute_zeros_v7/v8) ──────────────────────────
ITER_SWITCH = 8    # itérations phase1 (64 bits)
MAX_ITER    = 50   # maximum total
PREC_FAST   = 64   # bits phase1 — 1 limbe SIMD
PREC_FULL   = 80   # bits phase2 — optimal mesuré benchmark 11 juin
TOL_FULL    = 1e-12

# ── Chemins ────────────────────────────────────────────────────────────────────
_BASE       = Path(__file__).parent
SO_PATH     = _BASE / "c_modules/illinois_mpfr.so"
CSV_T100K   = Path(
    "/home/riemann/projet_zeta/calculs"
    "/v4_1_T100000_20260611_142434"
    "/zeros_v4_1_T100000_20260611_142434.csv"
)

N_BENCH = 500   # zéros à mesurer

# Paliers t (ms/appel par zone)
PALIERS = [1_000, 10_000, 50_000, 77_000]
DEMI_FENETRE = 4_000   # ±4000 autour de chaque palier


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — Chargement CSV + reconstruction brackets
# ══════════════════════════════════════════════════════════════════════════════

def charger_zeros_csv(path: Path, n: int = N_BENCH) -> list:
    """Charge n zéros répartis uniformément (par index) dans [1000, 100000].

    Filtre t >= 300 (seuil Illinois C — en dessous mpmath est utilisé en prod).
    """
    tous = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            t = float(row["partie_imaginaire"])
            if 1_000 <= t <= 100_000:   # plage souhaitée
                tous.append(t)

    # Échantillonnage uniforme par index — couvre toute la plage [1000, 100000]
    pas = max(1, len(tous) // n)
    return tous[::pas][:n]


def reconstruire_bracket(t0: float):
    """Trouve un bracket [a,b] tel que Z(a)·Z(b) < 0 autour du zéro t0.

    Utilise Z_vect_correct (numpy float64) — ×100 plus rapide que mp.siegelz.
    Essaie des largeurs croissantes ; STEP=0.01 suffit presque toujours.
    Retourne (a, b, fa, fb) ou None si aucun signe change trouvé.
    """
    for delta in [0.005, 0.010, 0.015, 0.020]:
        a  = t0 - delta
        b  = t0 + delta
        fa = float(Z_vect_correct(np.array([a]))[0])
        fb = float(Z_vect_correct(np.array([b]))[0])
        if fa * fb < 0.0:
            return a, b, fa, fb
    return None   # ne devrait pas arriver sur des vrais zéros


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — Comptage itérations (miroir Python de l'algorithme C)
# ══════════════════════════════════════════════════════════════════════════════

def _Z_scalaire(t: float) -> float:
    """Z(t) scalaire via Z_vect_correct — wrapper pour le comptage d'itérations."""
    return float(Z_vect_correct(np.array([t]))[0])


def _compter_iters_python(a: float, b: float, fa: float, fb: float) -> tuple:
    """Miroir Python de illinois_refine_bench pour compter phase1/phase2.

    Utilise Z_vect_correct (float64) — ×100 plus rapide que mp.siegelz.
    La convergence Illinois dépend du signe de Z et de |b-a|, pas de la
    précision numérique — les comptes sont représentatifs de l'algorithme C.

    Retourne (iter_phase1, iter_phase2).
    """
    iter1 = 0
    iter2 = 0

    for i in range(MAX_ITER):
        if abs(fb - fa) < 1e-300:
            break
        # Sécante : c = b − Z(b)·(b−a) / (Z(b)−Z(a))
        c  = b - fb * (b - a) / (fb - fa)
        fc = _Z_scalaire(c)

        # Mise à jour Illinois
        if fc * fb < 0.0:
            a, fa = b, fb
        else:
            fa *= 0.5   # correction Illinois — halve fa pour éviter la stagnation

        b, fb = c, fc

        if i < ITER_SWITCH:
            iter1 += 1
        else:
            iter2 += 1
            if abs(b - a) < TOL_FULL:
                break

    return iter1, iter2


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — Worker post-fork (timing C)
# ══════════════════════════════════════════════════════════════════════════════

def _worker_timing(args):
    """Charge illinois_mpfr.so APRÈS fork, mesure ms/appel pour chaque bracket.

    Retourne liste de (t0, ms_appel_C).
    Chargement post-fork — identique au pattern compute_zeros_v7.py.
    """
    brackets, so_path = args

    # Chargement post-fork obligatoire (libmpfr non safe si partagé avant fork)
    lib = ctypes.CDLL(str(so_path))
    lib.illinois_refine_bench.restype  = ctypes.c_double
    lib.illinois_refine_bench.argtypes = [
        ctypes.c_double,  # a
        ctypes.c_double,  # b
        ctypes.c_double,  # fa
        ctypes.c_double,  # fb
        ctypes.c_double,  # t_mid
        ctypes.c_int,     # iter_switch
        ctypes.c_int,     # max_iter
        ctypes.c_int,     # prec_fast_bits
        ctypes.c_int,     # prec_full_bits
    ]

    resultats = []
    for t0, a, b, fa, fb in brackets:
        t_mid = (a + b) / 2.0

        debut = time.perf_counter()
        lib.illinois_refine_bench(
            a, b, fa, fb, t_mid,
            ITER_SWITCH, MAX_ITER, PREC_FAST, PREC_FULL,
        )
        ms = (time.perf_counter() - debut) * 1_000.0   # secondes → ms

        resultats.append((t0, ms))

    return resultats


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — Affichage résultats
# ══════════════════════════════════════════════════════════════════════════════

def afficher_resultats(timing: list, iters: list):
    """Fusionne timing C et comptes d'itérations Python, affiche le rapport."""

    ms_arr    = np.array([r[1] for r in timing])
    iter1_arr = np.array([r[1] for r in iters])
    iter2_arr = np.array([r[2] for r in iters])
    total_arr = iter1_arr + iter2_arr

    sep = "─" * 62

    print()
    print("═" * 62)
    print("  BENCHMARK illinois_refine_bench(64→80 bits) — 500 zéros")
    print("  Source : CSV T=100k v7 · 2026-06-12")
    print("═" * 62)

    print(f"\n{sep}")
    print("  TEMPS (appel C)")
    print(sep)
    print(f"  ms/appel moyen  : {ms_arr.mean():.4f} ms")
    print(f"  ms/appel médiane: {np.median(ms_arr):.4f} ms")
    print(f"  écart-type      : {ms_arr.std():.4f} ms")
    print(f"  min / max       : {ms_arr.min():.4f} / {ms_arr.max():.4f} ms")

    print(f"\n{sep}")
    print("  ITÉRATIONS (miroir Python)")
    print(sep)
    print(f"  Phase 1 (64 bits) : moy={iter1_arr.mean():.1f}  "
          f"min={iter1_arr.min()}  max={iter1_arr.max()}")
    print(f"  Phase 2 (80 bits) : moy={iter2_arr.mean():.1f}  "
          f"min={iter2_arr.min()}  max={iter2_arr.max()}")
    print(f"  Total             : moy={total_arr.mean():.1f}  "
          f"min={total_arr.min()}  max={total_arr.max()}")

    print(f"\n{sep}")
    print("  MS/APPEL PAR PALIER t")
    print(sep)
    print(f"  {'t':>8}  {'N':>4}  {'moy ms':>8}  {'méd ms':>8}  {'iter moy':>9}")
    print(f"  {'─'*8}  {'─'*4}  {'─'*8}  {'─'*8}  {'─'*9}")

    t_arr = np.array([r[0] for r in timing])

    for palier in PALIERS:
        masque  = np.abs(t_arr - palier) <= DEMI_FENETRE
        indices = np.where(masque)[0]

        if len(indices) == 0:
            print(f"  {palier:>8}  {'—':>4}")
            continue

        ms_p    = ms_arr[masque]
        it1_p   = iter1_arr[masque]
        it2_p   = iter2_arr[masque]

        print(f"  {palier:>8}  {len(indices):>4}  "
              f"{ms_p.mean():>8.4f}  {np.median(ms_p):>8.4f}  "
              f"{(it1_p + it2_p).mean():>9.1f}")

    print(f"\n{sep}")
    print("  DISTRIBUTION ITÉRATIONS TOTALES")
    print(sep)
    for v in sorted(set(total_arr)):
        n  = int((total_arr == v).sum())
        pct = 100.0 * n / len(total_arr)
        bar = "█" * int(pct / 2)
        print(f"  iter={int(v):>3} : {n:>4} zéros ({pct:>5.1f}%)  {bar}")

    print()
    print("═" * 62)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    multiprocessing.set_start_method("fork", force=True)   # requis pour ctypes post-fork

    print(f"[1/4] Chargement CSV T=100k v7...")
    zeros = charger_zeros_csv(CSV_T100K, N_BENCH)
    print(f"      {len(zeros)} zéros — t ∈ [{zeros[0]:.1f}, {zeros[-1]:.1f}]")

    print(f"[2/4] Reconstruction des brackets (mpmath.siegelz, dps=35)...")
    brackets = []
    for t0 in zeros:
        res = reconstruire_bracket(t0)
        if res is not None:
            a, b, fa, fb = res
            brackets.append((t0, a, b, fa, fb))
    print(f"      {len(brackets)} brackets valides / {len(zeros)}")

    print(f"[3/4] Timing C post-fork ({len(brackets)} appels illinois_refine_bench)...")
    with multiprocessing.Pool(1) as pool:
        timing = pool.map(_worker_timing, [(brackets, SO_PATH)])[0]

    print(f"[4/4] Comptage itérations Python ({len(brackets)} appels)...")
    iters = []
    for t0, a, b, fa, fb in brackets:
        i1, i2 = _compter_iters_python(a, b, fa, fb)
        iters.append((t0, i1, i2))

    afficher_resultats(timing, iters)
