# -*- coding: utf-8 -*-
# =============================================================================
# chrono_phases.py — instrumentation 3 phases pour compute_zeros_v4_1.py
# Projet : Hypothèse de Riemann — Riemann_Lab (Phase C)
# Auteur : hprzeta
# Mise à jour : 2026-06-02
# =============================================================================
"""
Profileur léger pour localiser le goulot du pipeline v4.1.

Accumule le temps mur passé dans les zones réelles de compute_zeros_v4_1 :
    - detection         : balayage Z_batch (RS numpy float64 vectorisé)
    - illinois_C         : appel du noyau C/libmpfr SEUL (.so via ctypes, t≥300)
    - mpmath_petit_t     : affinage mpmath.findroot siegelz (t<300)
    - mpmath_fallback    : repli mpmath si résultat C hors intervalle (rare)
    - turing             : validation Turing-Backlund (process parent)

Compatible multiprocessing : chaque worker accumule LOCALEMENT (dict post-fork),
renvoie snapshot() avec son résultat, puis le parent agrège via agreger().
Sans dépendance externe (stdlib uniquement).

Usage minimal :
    from chrono_phases import chrono, snapshot, agreger, rapport

    # dans le worker, autour de chaque zone :
    with chrono("illinois_C"):
        gamma_c = illinois_c(a, b, tol=1e-12)
    # ... return (zeros_locaux, snapshot())

    # dans le parent, après pool.map :
    snaps  = [snap for (_zs, snap) in resultats]
    profil = agreger(snaps)
    print(rapport(profil, duree_run=duree_totale_s, n_workers=4))
"""
import time
from contextlib import contextmanager
from collections import defaultdict

# Compteurs locaux au process courant (un dict propre par worker après fork).
_acc = defaultdict(lambda: {"t": 0.0, "n": 0})


@contextmanager
def chrono(phase: str):
    """Mesure le temps mur d'un bloc et l'attribue à `phase`."""
    t0 = time.perf_counter()
    try:
        yield
    finally:
        dt = time.perf_counter() - t0
        _acc[phase]["t"] += dt
        _acc[phase]["n"] += 1


def snapshot() -> dict:
    """Copie des compteurs du process courant (à retourner par le worker)."""
    return {k: dict(v) for k, v in _acc.items()}


def reset() -> None:
    """Remet à zéro les compteurs du process courant."""
    _acc.clear()


def agreger(snapshots: list) -> dict:
    """Fusionne les snapshots de tous les workers (somme t et n par phase)."""
    total = defaultdict(lambda: {"t": 0.0, "n": 0})
    for snap in snapshots:
        for phase, v in snap.items():
            total[phase]["t"] += v["t"]
            total[phase]["n"] += v["n"]
    return {k: dict(v) for k, v in total.items()}


def rapport(total: dict, duree_run: float, n_workers: int = 4) -> str:
    """Bilan texte aligné, trié par temps cumulé décroissant.

    `% mur×W` = fraction du temps mur disponible (duree_run * n_workers)
    consommée par la phase ; identifie la zone qui mérite l'optimisation.
    """
    lignes = ["  [PROFIL PHASES] (temps CUMULÉ sur les workers)"]
    lignes.append(
        f"      {'phase':<22}{'temps_cumul':>12}{'appels':>9}"
        f"{'ms/appel':>11}{'% mur×W':>10}"
    )
    mur_x_workers = (duree_run * n_workers) if duree_run else 1.0
    for phase, v in sorted(total.items(), key=lambda kv: -kv[1]["t"]):
        t, n = v["t"], v["n"]
        ms = (t / n * 1000) if n else 0.0
        pct = (t / mur_x_workers * 100) if mur_x_workers else 0.0
        lignes.append(
            f"      {phase:<22}{t:>10.2f}s{n:>9}{ms:>10.2f}{pct:>9.1f}%"
        )
    return "\n".join(lignes)


# =============================================================================
# Auteur : hprzeta — Riemann_Lab Phase C — Mise à jour : 2026-06-02
# =============================================================================
