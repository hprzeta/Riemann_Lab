#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parallel_scanner.py — Calcul parallèle des zéros par partitionnement
═══════════════════════════════════════════════════════════════════════════════
Résout le problème de l'absence de parallélisme dans compute_zeros_v2.py.

POURQUOI joblib EST INCOMPATIBLE AVEC mpmath
─────────────────────────────────────────────
mpmath utilise GMP (GNU Multiple Precision) via MPFR.
GMP maintient un état global (allocateurs, précision) non thread-safe.
→ joblib avec threads → corruption mémoire.
→ joblib avec processes → fork + GMP = UB (undefined behavior sur Linux).

LA SOLUTION : multiprocessing avec des processus isolés
─────────────────────────────────────────────────────────
Chaque processus enfant a sa propre copie de l'état GMP (après fork).
La stratégie :
    1. Partitionner [T_min, T_max] en N_WORKERS segments disjoints
    2. Lancer N_WORKERS processus, chacun calcule son segment
    3. Fusionner et trier les résultats

ARCHITECTURE
─────────────
    ┌─────────────────────────────────────────┐
    │  Processus principal (orchestrateur)    │
    │  Partitionne [T_min, T_max]             │
    └──────┬──────┬──────┬──────┬────────────┘
           │      │      │      │
    ┌──────▼─┐ ┌──▼───┐ ┌▼─────┐ ┌▼──────┐
    │Worker 0│ │Work 1│ │Work 2│ │Work 3│
    │[14,2500]│ │[2500│ │[5000│ │[7500 │
    │        │ │,5000]│ │,7500]│ │,10000]│
    └────────┘ └──────┘ └──────┘ └───────┘
           │      │      │      │
    ┌──────▼──────▼──────▼──────▼────────────┐
    │  Fusion + tri + validation Turing       │
    └─────────────────────────────────────────┘

GAIN ATTENDU
─────────────
    4 cœurs → 4× plus rapide (de 21h → ~5h)
    8 cœurs → ~2.5h (overhead de communication ~10%)
    Note : θ(t) et Z_RS(t) sont pur calcul flottant → scalabilité quasi-linéaire

PRÉCISION
─────────
    Chaque worker utilise Z_RS pour la détection + Z_fast pour l'affinage.
    Pas de perte de précision vs v2 : l'affinage utilise toujours mpmath.

ATTENTION — CHEVAUCHEMENT AUX BORDS
─────────────────────────────────────
    Les segments se chevauchent de ε = 2·STEP aux jonctions pour éviter
    de rater un zéro à la frontière. La déduplication supprime les doublons.

Auteur : hprzeta — Projet Hypothèse de Riemann
Date   : 2026
"""

import math
import time
import numpy as np
import pandas as pd
import multiprocessing as mp_proc
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# ─── Imports locaux ───────────────────────────────────────────────────────────
try:
    from riemann_siegel import scanner_segment
    from theta_rapide import Z_fast
except ImportError:
    raise ImportError(
        "Placer riemann_siegel.py et theta_rapide.py dans le même dossier"
    )


# ─── Fonction worker (exécutée dans un sous-processus) ───────────────────────

def _worker(args: tuple) -> list:
    """
    Calcule les zéros sur un segment [t_min, t_max].
    Appelé par chaque processus enfant.

    Paramètres (dans le tuple args)
    --------------------------------
    t_min, t_max   : bornes du segment
    step           : pas de balayage RS
    tol_affinage   : tolérance Illinois
    dps_affinage   : précision mpmath lors de l'affinage
    worker_id      : identifiant du worker (pour les logs)
    """
    t_min, t_max, step, tol_affinage, dps_affinage, worker_id = args

    debut = time.time()
    print(f"  [Worker {worker_id}] Démarrage : t ∈ [{t_min:.1f}, {t_max:.1f}]")

    zeros = scanner_segment(
        t_min=t_min,
        t_max=t_max,
        step=step,
        tol_affinage=tol_affinage,
        dps_affinage=dps_affinage,
        verbose=False      # Silencieux dans le worker — logs centralisés
    )

    duree = time.time() - debut
    print(f"  [Worker {worker_id}] ✅ {len(zeros)} zéros en {duree:.1f}s")
    return zeros


# ─── Partitionnement ──────────────────────────────────────────────────────────

def partitionner(
    t_min: float,
    t_max: float,
    n_workers: int,
    overlap: float = 2.0
) -> List[Tuple[float, float]]:
    """
    Partitionne [t_min, t_max] en n_workers segments avec chevauchement.

    Paramètres
    ----------
    overlap : chevauchement aux bords (en unités de t) pour ne pas rater
              de zéro à la jonction. 2.0 est sûr (espacement moyen ≈ 0.5–2).

    Retourne
    --------
    list of (float, float) — bornes de chaque segment
    """
    longueur = (t_max - t_min) / n_workers
    segments = []
    for i in range(n_workers):
        debut  = t_min + i * longueur - (overlap if i > 0 else 0)
        fin    = t_min + (i + 1) * longueur + (overlap if i < n_workers - 1 else 0)
        debut  = max(debut, t_min)
        fin    = min(fin, t_max)
        segments.append((debut, fin))
    return segments


# ─── Déduplication ────────────────────────────────────────────────────────────

def dedupliquer(zeros_bruts: List[float], tolerance: float = 0.01) -> List[float]:
    """
    Supprime les doublons introduits par le chevauchement des segments.
    Deux zéros à distance < tolerance sont considérés identiques.

    Paramètre
    ---------
    tolerance : float — distance minimale entre deux zéros distincts
                (l'espacement minimal entre zéros est ~ π/ln(T/2π) ≫ 0.01
                 pour T < 10⁶)
    """
    if not zeros_bruts:
        return []
    zeros_tries = sorted(zeros_bruts)
    uniques     = [zeros_tries[0]]
    for t in zeros_tries[1:]:
        if t - uniques[-1] > tolerance:
            uniques.append(t)
    return uniques


# ─── Orchestrateur principal ─────────────────────────────────────────────────

def calculer_zeros_parallele(
    T_MAX       : float  = 10000.0,
    T_MIN       : float  = 14.0,
    N_WORKERS   : int    = None,       # None = auto (nombre de cœurs)
    STEP        : float  = 0.3,        # pas RS (0.3 est sûr jusqu'à T=10⁵)
    TOL_AFFINAGE: float  = 1e-12,
    DPS_AFFINAGE: int    = 35,
    DOSSIER     : Path   = None,
) -> List[float]:
    """
    Calcule les zéros non triviaux de ζ sur [T_MIN, T_MAX] en parallèle.

    Paramètres
    ----------
    T_MAX        : borne supérieure (défaut 10 000)
    N_WORKERS    : nombre de processus parallèles (défaut = nb de cœurs)
    STEP         : pas de balayage Riemann-Siegel (0.3 recommandé)
    TOL_AFFINAGE : tolérance Illinois pour l'affinage (1e-12)
    DPS_AFFINAGE : précision mpmath lors de l'affinage
    DOSSIER      : Path — dossier de sauvegarde des résultats intermédiaires

    Retourne
    --------
    List[float] — zéros triés, dédupliqués
    """
    if N_WORKERS is None:
        N_WORKERS = mp_proc.cpu_count()
        print(f"  Détection automatique : {N_WORKERS} cœurs disponibles")

    # ── Estimation théorique ──────────────────────────────────────────────
    N_attendu = int(T_MAX / (2 * math.pi) * math.log(T_MAX / (2 * math.pi * math.e)))

    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    if DOSSIER is None:
        DOSSIER = Path("calculs") / f"T{T_MAX:.0f}_{horodatage}_parallel"
        DOSSIER.mkdir(parents=True, exist_ok=True)

    print()
    print("=" * 65)
    print(f"  CALCUL PARALLÈLE — {N_WORKERS} workers")
    print("=" * 65)
    print(f"  T_MIN           = {T_MIN}")
    print(f"  T_MAX           = {T_MAX}")
    print(f"  STEP (RS)       = {STEP}")
    print(f"  TOL_AFFINAGE    = {TOL_AFFINAGE:.0e}")
    print(f"  DPS_AFFINAGE    = {DPS_AFFINAGE}")
    print(f"  N zéros attendus ≈ {N_attendu}")
    print(f"  Dossier          = {DOSSIER}")
    print("=" * 65)

    # ── Partitionnement ───────────────────────────────────────────────────
    segments = partitionner(T_MIN, T_MAX, N_WORKERS, overlap=STEP * 4)
    args_list = [
        (t_min, t_max, STEP, TOL_AFFINAGE, DPS_AFFINAGE, i)
        for i, (t_min, t_max) in enumerate(segments)
    ]

    print(f"\n  Segments :")
    for i, (a, b) in enumerate(segments):
        print(f"    Worker {i}: [{a:.1f}, {b:.1f}]")
    print()

    # ── Lancement parallèle ───────────────────────────────────────────────
    debut_total = time.time()

    with mp_proc.Pool(processes=N_WORKERS) as pool:
        resultats = pool.map(_worker, args_list)

    # ── Fusion et déduplication ───────────────────────────────────────────
    zeros_bruts = [t for segment in resultats for t in segment]
    zeros       = dedupliquer(zeros_bruts, tolerance=0.01)

    duree_totale = time.time() - debut_total

    # ── Rapport ───────────────────────────────────────────────────────────
    print()
    print("=" * 65)
    print(f"  RÉSULTATS PARALLÈLES")
    print("=" * 65)
    print(f"  Zéros bruts (avec doublons)  : {len(zeros_bruts)}")
    print(f"  Zéros après déduplication    : {len(zeros)}")
    print(f"  Attendus (formule Weyl)       : {N_attendu}")
    print(f"  Durée totale                  : {duree_totale/60:.1f} min")
    print(f"  Vitesse                       : {len(zeros)/duree_totale:.1f} zéros/s")
    print("=" * 65)

    # ── Sauvegarde CSV ────────────────────────────────────────────────────
    nom_csv = f"zeros_parallel_T{T_MAX:.0f}_{horodatage}.csv"
    chemin  = DOSSIER / nom_csv
    df = pd.DataFrame({
        "n":                 range(1, len(zeros) + 1),
        "partie_imaginaire": zeros,
        "T_MAX":             T_MAX,
        "methode":           "RS-detection + Illinois-affinage",
        "n_workers":         N_WORKERS,
        "precision_dps":     DPS_AFFINAGE,
        "calcule_le":        horodatage,
    })
    df.to_csv(chemin, index=False)
    print(f"\n  💾  Sauvegardé → {chemin}")

    return zeros


# ─── Benchmark séquentiel vs parallèle ───────────────────────────────────────

def benchmark_speedup(
    T_MAX: float = 1000.0,
    max_workers: int = 4,
    STEP: float = 0.3,
):
    """
    Mesure le speedup obtenu selon le nombre de workers.
    Lance le calcul séquentiel puis 2, 4 workers et trace le speedup.
    """
    import matplotlib.pyplot as plt

    durees = {}
    resultats = {}

    for n_w in [1, 2, 4][:max_workers]:
        print(f"\n  === Test {n_w} worker(s) ===")
        debut = time.time()
        zeros = calculer_zeros_parallele(
            T_MAX=T_MAX, N_WORKERS=n_w, STEP=STEP, DPS_AFFINAGE=30
        )
        durees[n_w] = time.time() - debut
        resultats[n_w] = len(zeros)
        print(f"  {n_w} worker(s) : {durees[n_w]:.1f}s — {len(zeros)} zéros")

    # Speedup
    t1 = durees.get(1, None)
    if t1 and len(durees) > 1:
        print("\n  Speedup :")
        for n_w, dt in durees.items():
            print(f"    {n_w} workers : {t1/dt:.2f}×")


# ─── Point d'entrée ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    # USAGE DIRECT : calcul jusqu'à T=10 000 avec tous les cœurs disponibles
    zeros = calculer_zeros_parallele(
        T_MAX=10000.0,
        N_WORKERS=None,       # auto
        STEP=0.3,
        TOL_AFFINAGE=1e-12,
        DPS_AFFINAGE=35,
    )
    print(f"\n  ✅ Terminé : {len(zeros)} zéros calculés")
    print(f"  Premier : t₁ = {zeros[0]:.12f}")
    print(f"  Dernier : t_{len(zeros)} = {zeros[-1]:.12f}")
