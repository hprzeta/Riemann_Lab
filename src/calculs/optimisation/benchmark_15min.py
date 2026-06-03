#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
benchmark_15min.py — Comparaison de performance sur 15 minutes
═══════════════════════════════════════════════════════════════════════════════
Compare 3 modes de calcul sur un même segment [14, T_MAX/N_WORKERS] :
    - cpu       : Z(t) scalaire point par point (v3 sans batch)
    - batch_cpu : Z(t) vectorisé numpy (batch CPU)
    - batch_gpu : Z(t) vectorisé CuPy  (batch GPU, fallback CPU si absent)

USAGE
──────
    # Terminal 1 — mode CPU seul
    python benchmark_15min.py --mode cpu

    # Terminal 2 — mode batch CPU
    python benchmark_15min.py --mode batch_cpu

    # Terminal 3 — mode batch GPU
    python benchmark_15min.py --mode batch_gpu

    # Options supplémentaires
    python benchmark_15min.py --mode batch_cpu --tmax 2500 --duree 15

    # Lancement automatique des 3 modes en séquence (1 terminal)
    python benchmark_15min.py --mode all

PARAMÈTRES PAR DÉFAUT
──────────────────────
    T_MAX  = 2500   (≈ T=10000 / 4 workers)
    DUREE  = 15 min
    STEP   = 0.1
    T_MIN  = 14.0

RÉSULTATS
──────────
    Affichage en temps réel des zéros trouvés + vitesse courante.
    Sauvegarde CSV dans calculs/benchmark_YYYYMMDD_HHMMSS/
    Rapport de comparaison final si --mode all.

Auteur : hprzeta — Projet Hypothèse de Riemann
Date   : 2026
"""

import argparse
import math
import time
import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

# ─── Configuration par défaut ─────────────────────────────────────────────────
T_MIN_DEFAULT  = 14.0
T_MAX_DEFAULT  = 2500.0   # T=10000 / 4 workers
DUREE_DEFAULT  = 15       # minutes
STEP_DEFAULT   = 0.1
DPS_AFFINAGE   = 35
TOL_AFFINAGE   = 1e-12

# ─── Parsing des arguments ────────────────────────────────────────────────────
parser = argparse.ArgumentParser(
    description="Benchmark 15 min — Zéros de Riemann-Siegel"
)
parser.add_argument(
    "--mode",
    choices=["cpu", "batch_cpu", "batch_gpu", "all"],
    default="batch_cpu",
    help="Mode de calcul : cpu | batch_cpu | batch_gpu | all"
)
parser.add_argument("--tmax",  type=float, default=T_MAX_DEFAULT,
                    help=f"T_MAX du segment (défaut: {T_MAX_DEFAULT})")
parser.add_argument("--tmin",  type=float, default=T_MIN_DEFAULT,
                    help=f"T_MIN (défaut: {T_MIN_DEFAULT})")
parser.add_argument("--duree", type=int,   default=DUREE_DEFAULT,
                    help=f"Durée en minutes (défaut: {DUREE_DEFAULT})")
parser.add_argument("--step",  type=float, default=STEP_DEFAULT,
                    help=f"Pas de balayage (défaut: {STEP_DEFAULT})")
args = parser.parse_args()


# ─── Imports des modules de calcul ────────────────────────────────────────────
try:
    from theta_rapide import theta_asymptotique, theta_exact, Z_fast
except ImportError:
    print("❌  theta_rapide.py introuvable — lancer depuis optimisation/")
    sys.exit(1)

# ─── Dossier de résultats ─────────────────────────────────────────────────────
horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
DOSSIER    = Path("calculs") / f"benchmark_{horodatage}"
DOSSIER.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  MODE CPU — Z(t) scalaire point par point (v3 sans batch)
# ═══════════════════════════════════════════════════════════════════════════════

def Z_scalaire(t: float) -> float:
    """Z(t) via formule RS scalaire — même implémentation que v3 sans batch."""
    tau    = math.sqrt(t / (2 * math.pi))
    N      = int(tau)
    if t >= 20.0:
        th = (t/2)*math.log(t/(2*math.pi)) - t/2 - math.pi/8 + 1/(48*t)
    else:
        th = theta_exact(t)

    ns      = np.arange(1, N + 1, dtype=np.float64)
    phases  = th - t * np.log(ns)
    somme   = float(np.sum(np.cos(phases) / np.sqrt(ns)))

    # Reste RS
    u     = 2*(tau - N) - 1
    denom = math.cos(math.pi * u)
    psi   = math.cos(math.pi*(u*u/2 + 0.375)) / denom if abs(denom) > 1e-10 else 0.0
    reste = ((-1)**(N-1)) * (tau**(-0.5)) * psi

    return 2 * somme + reste


def run_cpu(t_min, t_max, step, duree_s, verbose=True):
    """Scanner CPU scalaire — s'arrête après duree_s secondes."""
    from mpmath import mp, findroot

    mp.dps  = DPS_AFFINAGE
    zeros   = []
    t       = t_min
    Zp      = Z_scalaire(t)
    debut   = time.time()
    n_eval  = 0

    while t + step <= t_max:
        if time.time() - debut >= duree_s:
            break

        t_next = t + step
        Zn     = Z_scalaire(t_next)
        n_eval += 1

        if Zp * Zn < 0:
            try:
                t0 = findroot(
                    lambda x: Z_fast(float(x), dps=DPS_AFFINAGE),
                    (t, t_next), solver="illinois",
                    tol=TOL_AFFINAGE, maxsteps=80
                )
                zeros.append(float(t0))
                elapsed = time.time() - debut
                if verbose:
                    vit = len(zeros) / elapsed
                    print(f"  [CPU]       #{len(zeros):4d}  t={float(t0):.6f}"
                          f"  {vit:.2f} z/s  {elapsed/60:.1f}min")
            except Exception:
                pass

        Zp = Zn
        t  = t_next

    elapsed = time.time() - debut
    return zeros, elapsed, n_eval


# ═══════════════════════════════════════════════════════════════════════════════
#  MODE BATCH CPU/GPU — Z(t) vectorisé
# ═══════════════════════════════════════════════════════════════════════════════

def run_batch(t_min, t_max, step, duree_s, forcer_cpu=False, verbose=True):
    """Scanner batch CPU ou GPU — s'arrête après duree_s secondes."""
    from mpmath import mp, findroot

    # Importer le module batch
    try:
        import riemann_siegel_batch as rsb
    except ImportError:
        print("❌  riemann_siegel_batch.py introuvable")
        sys.exit(1)

    # Forcer CPU si demandé
    if forcer_cpu:
        rsb._GPU_DISPONIBLE = False
        label = "BATCH_CPU"
    else:
        label = "BATCH_GPU" if rsb._GPU_DISPONIBLE else "BATCH_CPU"

    mp.dps   = DPS_AFFINAGE
    zeros    = []
    t_grid   = np.arange(t_min, t_max + step, step, dtype=np.float64)
    n_total  = len(t_grid)
    bloc     = 5000 if not rsb._GPU_DISPONIBLE else 50000
    debut    = time.time()
    n_eval   = 0

    for i0 in range(0, n_total - 1, bloc):
        if time.time() - debut >= duree_s:
            break

        i1      = min(i0 + bloc + 1, n_total)
        ts_b    = t_grid[i0:i1]
        Z_b     = rsb.Z_batch(ts_b, avec_reste=True)
        n_eval += len(ts_b)

        signes   = np.sign(Z_b)
        passages = np.where(np.diff(signes) != 0)[0]

        for idx in passages:
            if time.time() - debut >= duree_s:
                break
            t_a, t_b_val = float(ts_b[idx]), float(ts_b[idx+1])
            try:
                t0 = findroot(
                    lambda x: Z_fast(float(x), dps=DPS_AFFINAGE),
                    (t_a, t_b_val), solver="illinois",
                    tol=TOL_AFFINAGE, maxsteps=80
                )
                zeros.append(float(t0))
                elapsed = time.time() - debut
                if verbose:
                    vit = len(zeros) / elapsed
                    print(f"  [{label:<9}] #{len(zeros):4d}  t={float(t0):.6f}"
                          f"  {vit:.2f} z/s  {elapsed/60:.1f}min")
            except Exception:
                pass

    elapsed = time.time() - debut
    return zeros, elapsed, n_eval


# ═══════════════════════════════════════════════════════════════════════════════
#  RAPPORT FINAL
# ═══════════════════════════════════════════════════════════════════════════════

def afficher_rapport(resultats: list):
    """Affiche le tableau comparatif des 3 modes."""
    print()
    print("═" * 65)
    print("  RAPPORT COMPARATIF — 15 minutes")
    print("═" * 65)
    print(f"  Segment : [{args.tmin:.0f}, {args.tmax:.0f}]"
          f"  STEP={args.step}  DPS={DPS_AFFINAGE}")
    print("─" * 65)
    print(f"  {'Mode':<12}  {'Zéros':<8}  {'Vitesse':<12}"
          f"  {'Évals':<10}  {'Durée'}")
    print("─" * 65)

    meilleur = max(resultats, key=lambda r: r["zeros"])
    for r in resultats:
        star = " ★" if r == meilleur else ""
        print(f"  {r['mode']:<12}  {r['zeros']:<8d}  "
              f"{r['vitesse']:<8.2f} z/s  "
              f"{r['n_eval']:<10d}  "
              f"{r['duree']/60:.1f} min{star}")

    print("─" * 65)
    if len(resultats) > 1:
        ref = next((r for r in resultats if r["mode"] == "CPU"), resultats[0])
        for r in resultats:
            if r != ref and ref["vitesse"] > 0:
                gain = r["vitesse"] / ref["vitesse"]
                print(f"  Gain {r['mode']} vs {ref['mode']} : ×{gain:.1f}")
    print("═" * 65)

    # Sauvegarde CSV
    df  = pd.DataFrame(resultats)
    csv = DOSSIER / f"comparaison_modes_{horodatage}.csv"
    df.to_csv(csv, index=False)
    print(f"\n  💾  Résultats → {csv}")


def sauvegarder_zeros(zeros, mode_label):
    """Sauvegarde les zéros trouvés dans un CSV."""
    if not zeros:
        return
    df  = pd.DataFrame({"n": range(1, len(zeros)+1),
                         "partie_imaginaire": zeros,
                         "mode": mode_label})
    csv = DOSSIER / f"zeros_{mode_label}_{horodatage}.csv"
    df.to_csv(csv, index=False)
    print(f"  📄  {len(zeros)} zéros ({mode_label}) → {csv}")


# ═══════════════════════════════════════════════════════════════════════════════
#  POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def lancer_mode(mode_name: str, duree_s: float) -> dict:
    """Lance un mode et retourne le résultat."""
    print()
    print(f"{'─'*65}")
    print(f"  DÉMARRAGE mode {mode_name.upper()}"
          f"  — segment [{args.tmin:.0f}, {args.tmax:.0f}]"
          f"  — {int(duree_s//60)} min")
    print(f"{'─'*65}")

    debut = time.time()

    if mode_name == "cpu":
        zeros, elapsed, n_eval = run_cpu(
            args.tmin, args.tmax, args.step, duree_s
        )
    elif mode_name == "batch_cpu":
        zeros, elapsed, n_eval = run_batch(
            args.tmin, args.tmax, args.step, duree_s, forcer_cpu=True
        )
    elif mode_name == "batch_gpu":
        zeros, elapsed, n_eval = run_batch(
            args.tmin, args.tmax, args.step, duree_s, forcer_cpu=False
        )
    else:
        zeros, elapsed, n_eval = [], 0, 0

    vitesse = len(zeros) / elapsed if elapsed > 0 else 0
    sauvegarder_zeros(zeros, mode_name)

    print(f"\n  ✅  {mode_name.upper()} terminé — "
          f"{len(zeros)} zéros en {elapsed/60:.1f} min "
          f"({vitesse:.2f} z/s)")

    return {
        "mode"   : mode_name.upper(),
        "zeros"  : len(zeros),
        "vitesse": round(vitesse, 3),
        "n_eval" : n_eval,
        "duree"  : round(elapsed, 1),
        "tmax_atteint": zeros[-1] if zeros else 0,
    }


def main():
    duree_s = args.duree * 60

    print()
    print("═" * 65)
    print("  BENCHMARK 15 MIN — Zéros de ζ(½+it)")
    print("═" * 65)
    print(f"  Mode     : {args.mode.upper()}")
    print(f"  Segment  : [{args.tmin:.0f}, {args.tmax:.0f}]")
    print(f"  Durée    : {args.duree} min")
    print(f"  STEP     : {args.step}")
    print(f"  Dossier  : {DOSSIER}")
    print("═" * 65)

    if args.mode == "all":
        # Lancer les 3 modes en séquence
        resultats = []
        for mode in ["cpu", "batch_cpu", "batch_gpu"]:
            r = lancer_mode(mode, duree_s)
            resultats.append(r)
        afficher_rapport(resultats)

    else:
        # Lancer un seul mode
        r = lancer_mode(args.mode, duree_s)
        print()
        print(f"  Mode          : {r['mode']}")
        print(f"  Zéros trouvés : {r['zeros']}")
        print(f"  Vitesse       : {r['vitesse']} z/s")
        print(f"  Évaluations   : {r['n_eval']}")
        print(f"  Durée réelle  : {r['duree']/60:.2f} min")


if __name__ == "__main__":
    main()
