#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
benchmark_v8.py — Benchmark Option A (W=8 workers) + Option B (prec phase 2)
══════════════════════════════════════════════════════════════════════════════
Deux mesures indépendantes :

  Benchmark 1 — prec_fast / prec_full (séquentiel, ~2 min)
    - Génère ~500 brackets via scan_arb sur [1000, 3000]
    - Pour chaque (prec_fast, prec_full) : ms/appel moyen, précision finale
    - Configurations : (64,116) ref · (48,116) · (32,116) · (64,96) · (64,80)

  Benchmark 2 — W=4 vs W=8 workers (parallèle, ~5 min)
    - T=5000, STEP=0.010
    - W=4 (référence) puis W=8 — comparer z/s et durée totale
    - Important : CPU = i7-7500U dual-core HT → 4 threads logiques
      W=8 > nproc → surcharge probable

Usage :
  source ~/projet_zeta/zeta_env/bin/activate
  cd ~/projet_zeta/src/calculs/optimisation
  python benchmark_v8.py

Auteur : hprzeta — Phase C v8 — 11 juin 2026
"""

import sys
import math
import time
import ctypes
import multiprocessing
import numpy as np
from pathlib import Path

# ── Chemin .so ────────────────────────────────────────────────────────────────
SO_PATH = Path(__file__).parent / "c_modules" / "illinois_mpfr.so"
if not SO_PATH.exists():
    sys.exit(f"ERREUR : {SO_PATH} introuvable. Compiler avec : cd c_modules && make")

# ── Imports projet ────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from scan_arb_wrapper import scan_arb
from arb_wrapper      import arb_hardy_z
import mpmath
mpmath.mp.dps = 35

T_SEUIL = 300.0
ITER_SWITCH = 8
MAX_ITER    = 50
TOL         = 1e-12
STEP        = 0.010

# ── Chargement ctypes ─────────────────────────────────────────────────────────
def _charger_lib():
    lib = ctypes.CDLL(str(SO_PATH))
    # illinois_refine_adaptive — chemin de production
    lib.illinois_refine_adaptive.restype  = ctypes.c_double
    lib.illinois_refine_adaptive.argtypes = [
        ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double,
        ctypes.c_double, ctypes.c_int, ctypes.c_int,
    ]
    # illinois_refine_bench — chemin benchmark (prec paramétré)
    lib.illinois_refine_bench.restype  = ctypes.c_double
    lib.illinois_refine_bench.argtypes = [
        ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double,
        ctypes.c_double, ctypes.c_int, ctypes.c_int,
        ctypes.c_int,    # prec_fast_bits
        ctypes.c_int,    # prec_full_bits
    ]
    return lib


# ══════════════════════════════════════════════════════════════════════════════
#  BENCHMARK 1 — prec_fast / prec_full (séquentiel)
# ══════════════════════════════════════════════════════════════════════════════

def _brackets_bench(t_start, t_end):
    """Génère des brackets via scan_arb et filtre t ≥ T_SEUIL."""
    raw = scan_arb(t_start, t_end, step=STEP)
    return [(a, b, fa, fb) for a, b, fa, fb in raw if (a + b) / 2.0 >= T_SEUIL]


def benchmark_prec(brackets, configs, n_max=500):
    """Mesure ms/appel et précision pour chaque (prec_fast, prec_full).

    Retourne une liste de dicts avec les résultats.
    """
    lib = _charger_lib()
    resultats = []
    sample = brackets[:n_max]

    for prec_fast, prec_full in configs:
        label = f"prec_fast={prec_fast:3d} / prec_full={prec_full:3d}"
        limbes_fast = math.ceil(prec_fast / 64)
        limbes_full = math.ceil(prec_full / 64)

        t0 = time.perf_counter()
        zeros = []
        for a, b, fa, fb in sample:
            t_mid = (a + b) / 2.0
            z = lib.illinois_refine_bench(
                a, b, float(fa), float(fb), t_mid,
                ITER_SWITCH, MAX_ITER,
                prec_fast, prec_full,
            )
            zeros.append(z)
        duree = time.perf_counter() - t0

        ms_appel = duree / len(sample) * 1000.0 if sample else 0

        # précision sur les 20 premiers zéros via mpmath.siegelz
        residus = []
        for z in zeros[:20]:
            try:
                r = abs(float(mpmath.siegelz(z)))
                residus.append(r)
            except Exception:
                pass
        residu_max = max(residus) if residus else float("nan")
        residu_med = sorted(residus)[len(residus)//2] if residus else float("nan")

        resultats.append({
            "label":       label,
            "prec_fast":   prec_fast,
            "prec_full":   prec_full,
            "limbes_fast": limbes_fast,
            "limbes_full": limbes_full,
            "ms_appel":    ms_appel,
            "residu_max":  residu_max,
            "residu_med":  residu_med,
            "n":           len(sample),
        })

        print(f"  {label}  ({limbes_fast}+{limbes_full} limbes)"
              f"  → {ms_appel:.3f} ms/appel  |Z_max|={residu_max:.1e}")

    return resultats


# ══════════════════════════════════════════════════════════════════════════════
#  BENCHMARK 2 — W=4 vs W=8 workers
# ══════════════════════════════════════════════════════════════════════════════

def _worker_bench(args):
    """Worker minimal : scan + affinage adaptive, retourne (n_zeros, duree_s)."""
    t_start, t_end, so_path, worker_id = args
    lib = ctypes.CDLL(str(so_path))
    lib.illinois_refine_adaptive.restype  = ctypes.c_double
    lib.illinois_refine_adaptive.argtypes = [
        ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double,
        ctypes.c_double, ctypes.c_int, ctypes.c_int,
    ]

    import mpmath as _mp
    _mp.mp.dps = 35

    t0 = time.time()
    brackets = scan_arb(t_start, t_end, step=STEP)

    zeros = []
    for a, b, fa, fb in brackets:
        t_mid = (a + b) / 2.0
        try:
            if t_mid >= T_SEUIL:
                z = lib.illinois_refine_adaptive(
                    a, b, float(fa), float(fb), t_mid, ITER_SWITCH, MAX_ITER
                )
                if a - 1e-10 <= z <= b + 1e-10:
                    zeros.append(z)
            else:
                z = float(_mp.findroot(arb_hardy_z, (a, b),
                                        solver="illinois", tol=TOL, maxsteps=80))
                zeros.append(z)
        except Exception:
            pass

    duree = time.time() - t0
    return len(zeros), duree


def _partitionner(t_min, t_max, n_workers):
    """Partition uniforme en [t_min, t_max] en n_workers segments."""
    largeur = (t_max - t_min) / n_workers
    return [(t_min + i * largeur, t_min + (i + 1) * largeur, SO_PATH, i)
            for i in range(n_workers)]


def benchmark_workers(t_max, configs_w):
    """Lance le calcul sur [14, t_max] avec différents N_WORKERS.

    Retourne liste de dicts {n_workers, duree, z_s, n_zeros}.
    """
    T_MIN = 14.0
    resultats = []

    for n_workers in configs_w:
        print(f"\n  ── W={n_workers} workers ────────────────────────────")
        args_list = _partitionner(T_MIN, t_max, n_workers)
        t0 = time.time()
        with multiprocessing.Pool(processes=n_workers) as pool:
            res = pool.map(_worker_bench, args_list)
        duree_totale = time.time() - t0

        n_zeros_total = sum(r[0] for r in res)
        z_s = n_zeros_total / duree_totale if duree_totale > 0 else 0

        print(f"  W={n_workers} : {n_zeros_total} zéros en {duree_totale:.1f}s"
              f"  ({z_s:.1f} z/s)")
        resultats.append({
            "n_workers": n_workers,
            "duree_s":   duree_totale,
            "z_s":       z_s,
            "n_zeros":   n_zeros_total,
        })

    return resultats


# ══════════════════════════════════════════════════════════════════════════════
#  RAPPORT FINAL
# ══════════════════════════════════════════════════════════════════════════════

def afficher_rapport(res_prec, res_workers, t_max_w):
    sep = "═" * 70
    print()
    print(sep)
    print("  RAPPORT BENCHMARK v8 — Phase C / Riemann_Lab")
    print(sep)
    print(f"  Machine    : Intel i7-7500U — {multiprocessing.cpu_count()} CPUs logiques (dual-core HT)")
    print(f"  Date       : {time.strftime('%Y-%m-%d %H:%M')}")
    print()

    # Benchmark 1 — prec
    if res_prec:
        ref = next((r for r in res_prec if r["prec_fast"] == 64 and r["prec_full"] == 116), None)
        print("  ┌─ Benchmark 1 : prec_fast / prec_full")
        print(f"  │  Brackets : {res_prec[0]['n']} appels sur t ∈ [1000, 3000]")
        print("  │")
        print(f"  │  {'Config':33s}  {'Limbes':8s}  {'ms/appel':10s}  "
              f"{'Gain':8s}  {'|Z|_max':10s}")
        print("  │  " + "─" * 65)
        for r in res_prec:
            gain = (ref["ms_appel"] / r["ms_appel"]) if ref and r["ms_appel"] > 0 else float("nan")
            gain_str = f"×{gain:.2f}" if not math.isnan(gain) else "—"
            print(f"  │  {r['label']:33s}  "
                  f"{r['limbes_fast']}+{r['limbes_full']} limbes  "
                  f"{r['ms_appel']:8.3f} ms  "
                  f"{gain_str:8s}  "
                  f"{r['residu_max']:.1e}")
        print("  └")

    # Benchmark 2 — workers
    if res_workers:
        ref_w = next((r for r in res_workers if r["n_workers"] == 4), None)
        print()
        print(f"  ┌─ Benchmark 2 : W=4 vs W=8 (T={t_max_w:.0f})")
        print(f"  │  Rappel : nproc={multiprocessing.cpu_count()} "
              f"→ W>nproc déclenche du context-switching")
        print("  │")
        print(f"  │  {'W':4s}  {'Durée':10s}  {'z/s':10s}  {'Gain vs W=4':12s}  {'Zéros':8s}")
        print("  │  " + "─" * 50)
        for r in res_workers:
            gain = (r["z_s"] / ref_w["z_s"]) if ref_w and ref_w["z_s"] > 0 else float("nan")
            gain_str = f"×{gain:.2f}" if not math.isnan(gain) else "—"
            print(f"  │  W={r['n_workers']:<2d}  "
                  f"{r['duree_s']/60:6.2f} min  "
                  f"{r['z_s']:8.1f} z/s  "
                  f"{gain_str:12s}  "
                  f"{r['n_zeros']:6d}")
        print("  └")

    print()
    print("  Recommandation v8 :")
    if res_prec and res_workers:
        best_prec = min(res_prec, key=lambda r: r["ms_appel"])
        best_w = max(res_workers, key=lambda r: r["z_s"])
        print(f"    prec optimale  : fast={best_prec['prec_fast']} / full={best_prec['prec_full']}"
              f"  ({best_prec['ms_appel']:.3f} ms/appel)")
        print(f"    W optimal      : {best_w['n_workers']} workers ({best_w['z_s']:.1f} z/s)")
    print()
    print(sep)


# ══════════════════════════════════════════════════════════════════════════════
#  POINT D'ENTRÉE
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print()
    print("=" * 70)
    print("  BENCHMARK v8 — Option A (W=8) + Option B (prec phase 2)")
    print("=" * 70)
    print(f"  CPUs logiques : {multiprocessing.cpu_count()}")
    print(f"  .so : {SO_PATH}")
    print()

    # ── Benchmark 1 : prec ────────────────────────────────────────────────
    T_BENCH_PREC = (1000.0, 3000.0)
    CONFIGS_PREC = [
        (64, 116),   # référence v7
        (48, 116),   # 1 limbe phase 1 (légèrement plus bas)
        (32, 116),   # 1 limbe phase 1 (minimum significatif)
        (64,  96),   # phase 2 : 2 limbes 96 bits au lieu de 116
        (64,  80),   # phase 2 : 2 limbes 80 bits (minimum sûr ?)
    ]

    print("  ── Benchmark 1 : prec_fast / prec_full ─────────────────────────")
    print(f"  Génération brackets sur t ∈ [{T_BENCH_PREC[0]:.0f}, {T_BENCH_PREC[1]:.0f}]...")
    brackets = _brackets_bench(T_BENCH_PREC[0], T_BENCH_PREC[1])
    print(f"  {len(brackets)} brackets générés — affinage sur {min(500, len(brackets))} premiers")
    print()
    res_prec = benchmark_prec(brackets, CONFIGS_PREC, n_max=500)

    # ── Benchmark 2 : workers ─────────────────────────────────────────────
    T_MAX_W = 5000.0
    CONFIGS_W = [4, 8]

    print()
    print("  ── Benchmark 2 : W=4 vs W=8 ────────────────────────────────────")
    print(f"  T_MAX = {T_MAX_W:.0f}, STEP = {STEP}")
    res_workers = benchmark_workers(T_MAX_W, CONFIGS_W)

    # ── Rapport ───────────────────────────────────────────────────────────
    afficher_rapport(res_prec, res_workers, T_MAX_W)


if __name__ == "__main__":
    main()
