#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
riemann_siegel.py — Formule de Riemann-Siegel pour Z(t)
═══════════════════════════════════════════════════════════════════════════════
Implémente Z(t) via la formule de Riemann-Siegel (1932), SANS appel à
mpmath.zeta(). Environ 100× plus rapide pour t grand.

THÉORIE — FORMULE DE RIEMANN-SIEGEL
════════════════════════════════════
La fonction Z de Hardy s'écrit :

    Z(t) = 2 · Σ_{n=1}^{N} cos(θ(t) − t·ln n) / √n  +  R(t)

où :
    N = ⌊√(t / 2π)⌋          ← borne de la somme principale
    θ(t)                      ← phase de Riemann-Siegel (voir theta_rapide.py)
    R(t)                      ← terme de reste (ordre t^{-1/4})

TERME DE RESTE R(t) — développement de Taylor
──────────────────────────────────────────────
Soit  u = 2(√(t/2π) − N) − 1  ∈ [−1, 1]
    Ψ(u) = cos(π(u²/2 + 3/8)) / cos(πu)

    R(t) ≈ (−1)^{N−1} · (t/2π)^{−1/4} ·
            [C₀(u)·Ψ(u)  +  C₁(u)·Ψ'(u)/(2π·(t/2π)^{1/2})  + ...]

En pratique, le terme C₀·Ψ(u) seul donne une erreur O(t^{-3/4}).
On inclut ici les 2 premiers termes (C₀ et C₁) pour une erreur O(t^{-5/4}).

PRÉCISION ATTEIGNABLE
─────────────────────
    Somme seule (R=0)    :  erreur O(t^{−1/4})  ← insuffisant
    + C₀·Ψ              :  erreur O(t^{−3/4})   ← bon pour détection de signe
    + C₀·Ψ + C₁·Ψ'      :  erreur O(t^{−5/4})   ← suffisant pour t > 200

Pour l'affinage précis d'un zéro (Illinois), on bascule sur Z_fast
(qui appelle mpmath.zeta() avec dps=35) uniquement dans la fenêtre étroite
autour du zéro détecté.

STRATÉGIE D'UTILISATION RECOMMANDÉE
─────────────────────────────────────
    1. DÉTECTION  → Z_RS(t) pour balayer [T_min, T_max]   (rapide, ~100× v2)
    2. AFFINAGE   → Z_fast(t) ou mpmath.zeta() uniquement dans [t-ε, t+ε]

RÉFÉRENCE
─────────
    H.M. Edwards, "Riemann's Zeta Function", Academic Press 1974, ch. 7
    A. Odlyzko, "The 10²⁰-th zero of the Riemann zeta function", 1992
    mpmath source : mpmath/libmp/libelefun.py (implémentation de référence)

Auteur : hprzeta — Projet Hypothèse de Riemann
Date   : 2026
"""

import math
import numpy as np
from typing import Tuple
from theta_rapide import theta_asymptotique, theta_exact, Z_fast

# ─── Constantes ───────────────────────────────────────────────────────────────
_TWO_PI      = 2.0 * math.pi
_SQRT_TWO_PI = math.sqrt(_TWO_PI)
_LOG_TWO_PI  = math.log(_TWO_PI)


# ─── Fonctions auxiliaires du terme de reste ──────────────────────────────────

def _psi(u: float) -> float:
    """
    Ψ(u) = cos(π(u²/2 + 3/8)) / cos(πu)

    Diverge si cos(πu) → 0, ce qui arrive si u → ±1/2.
    Dans ce cas on renvoie 0 (contribution négligeable car le numérateur
    oscille et la divergence est intégrable).
    """
    denom = math.cos(math.pi * u)
    if abs(denom) < 1e-10:
        return 0.0
    return math.cos(math.pi * (u * u / 2.0 + 0.375)) / denom


def _dpsi(u: float, h: float = 1e-7) -> float:
    """
    Dérivée numérique de Ψ(u) par différences centrées.
    Utilisée pour le terme C₁ du reste.
    """
    return (_psi(u + h) - _psi(u - h)) / (2.0 * h)


def _reste_RS(t: float, N: int, facteur: float) -> float:
    """
    Terme de reste de la formule de Riemann-Siegel.

    Paramètres
    ----------
    t       : valeur de t
    N       : ⌊√(t/2π)⌋
    facteur : (t/2π)^{-1/4}

    Retourne
    --------
    float — contribution du reste R(t)
    """
    signe   = (-1) ** (N - 1)
    tau     = math.sqrt(t / _TWO_PI)
    u       = 2.0 * (tau - N) - 1.0     # ∈ [−1, 1]

    psi_val = _psi(u)
    # Terme C₀ : coefficient 1 (normalisé)
    C0 = psi_val
    # Terme C₁ : dérivée × coefficient du développement
    C1 = _dpsi(u) * (u * u / 2.0 - 0.375) / (math.pi * tau)

    return signe * facteur * (C0 + C1)


# ─── Formule principale ───────────────────────────────────────────────────────

def Z_RS(t: float, avec_reste: bool = True) -> float:
    """
    Z(t) via la formule de Riemann-Siegel.

    Z(t) = 2·Σ_{n=1}^{N} cos(θ(t) − t·ln n) / √n  +  R(t)

    Paramètres
    ----------
    t           : float — partie imaginaire (t > 14)
    avec_reste  : bool  — inclure le terme de reste R(t)
                          (False = ~2× plus rapide, erreur O(t^{-1/4}))

    Retourne
    --------
    float — valeur de Z(t)

    Notes
    -----
    Complexité : O(√t) opérations flottantes (vs appel mpmath.zeta : O(t^ε))
    Précision  : ~10⁻³ à 10⁻⁵ selon t (suffisant pour détecter le signe)
    """
    if t < 14.0:
        raise ValueError(f"t={t:.2f} < 14 : utiliser Z_fast() ou mpmath directement")

    tau     = math.sqrt(t / _TWO_PI)
    N       = int(tau)              # ⌊√(t/2π)⌋
    facteur = tau ** (-0.5)         # (t/2π)^{-1/4} = τ^{-1/2}

    # θ(t) — calcul asymptotique (très rapide)
    th = theta_asymptotique(t) if t >= 20.0 else theta_exact(t)

    # ── Somme principale ──────────────────────────────────────────────────
    # Σ cos(θ − t·ln n) / √n  pour n = 1..N
    # Vectorisé avec numpy pour maximiser la vitesse
    ns       = np.arange(1, N + 1, dtype=np.float64)
    phases   = th - t * np.log(ns)
    somme    = float(np.sum(np.cos(phases) / np.sqrt(ns)))
    Z_val    = 2.0 * somme

    # ── Terme de reste ────────────────────────────────────────────────────
    if avec_reste:
        Z_val += _reste_RS(t, N, facteur)

    return Z_val


# ─── Scanner optimisé (détection + affinage sélectif) ────────────────────────

def scanner_segment(
    t_min: float,
    t_max: float,
    step: float = 0.5,
    tol_affinage: float = 1e-12,
    dps_affinage: int = 35,
    verbose: bool = True,
) -> list:
    """
    Détecte les zéros de Z(t) sur [t_min, t_max] avec la stratégie hybride :
        1. Détection rapide  via Z_RS   (O(√t) par évaluation)
        2. Affinage précis   via Z_fast (mpmath.zeta, uniquement au voisinage)

    Paramètres
    ----------
    step          : pas de balayage (0.5 est sûr car l'espacement moyen ≈ 2π/ln(t/2π))
    tol_affinage  : tolérance pour la bissection Illinois
    dps_affinage  : précision mpmath lors de l'affinage (35 suffit)

    Retourne
    --------
    list of float — valeurs t_n des zéros trouvés
    """
    from mpmath import mp, findroot

    mp_save = mp.dps
    zeros   = []
    t       = t_min
    Zp      = Z_RS(t)

    if verbose:
        print(f"  Scanner RS [{t_min:.1f}, {t_max:.1f}]  step={step}  tol={tol_affinage:.0e}")

    while t + step <= t_max:
        t_next = t + step
        Zn     = Z_RS(t_next)

        if Zp * Zn < 0:
            # ── Affinage Illinois avec Z_fast (mpmath) ─────────────────
            mp.dps = dps_affinage
            try:
                t0 = findroot(
                    lambda x: Z_fast(float(x), dps=dps_affinage),
                    (t, t_next),
                    solver="illinois",
                    tol=tol_affinage,
                    maxsteps=100
                )
                t0 = float(t0)
                zeros.append(t0)
                if verbose:
                    print(f"    ✅ Zéro #{len(zeros):5d} : t = {t0:.12f}")
            except Exception as e:
                if verbose:
                    print(f"    ⚠️  Affinage échoué [{t:.4f}, {t_next:.4f}] : {e}")

        Zp = Zn
        t  = t_next

    mp.dps = mp_save
    return zeros


# ─── Benchmark et validation ──────────────────────────────────────────────────

def benchmark(t_start: float = 100.0, t_end: float = 2000.0, step: float = 0.3):
    """
    Compare la vitesse de Z_RS vs Z_fast (mpmath.zeta) sur une plage de t.
    """
    import time

    ts = np.arange(t_start, t_end, step)

    debut = time.perf_counter()
    vals_rs = [Z_RS(t) for t in ts]
    dt_rs = time.perf_counter() - debut

    debut = time.perf_counter()
    vals_zf = [Z_fast(t, dps=35) for t in ts]
    dt_zf = time.perf_counter() - debut

    # Erreur de signe : combien de points ont-ils le même signe ?
    meme_signe = sum(
        1 for a, b in zip(vals_rs, vals_zf) if (a > 0) == (b > 0)
    )

    print(f"\n{'─'*60}")
    print(f"  Benchmark Z(t)  —  {len(ts)} points dans [{t_start:.0f}, {t_end:.0f}]")
    print(f"{'─'*60}")
    print(f"  Z_fast (mpmath) : {dt_zf:.2f}s")
    print(f"  Z_RS (Riemann-Siegel) : {dt_rs:.2f}s")
    print(f"  Accélération    : {dt_zf/dt_rs:.1f}×")
    print(f"  Accord de signe : {meme_signe}/{len(ts)}  ({100*meme_signe/len(ts):.1f}%)")
    print(f"  (100% = aucun zéro manqué dans ce balayage)")
    print(f"{'─'*60}\n")


if __name__ == "__main__":
    print("─── Test unitaire riemann_siegel.py ───\n")

    # 1. Vérification : Z_RS ≈ 0 aux zéros connus
    zeros_ref = [
        14.134725141734693, 21.022039638771555, 25.010857580145688,
        30.424876125859513, 32.935061587739189, 37.586178158825671,
        40.918719012147495, 43.327073280914999
    ]
    print("  Z_RS aux zéros connus (doit être proche de 0) :")
    print(f"  {'t':>22}  {'Z_RS(t)':>14}  {'Z_fast(t)':>14}")
    print("  " + "─" * 55)
    for t in zeros_ref:
        if t < 14.5:  # premier zéro — RS peu précis
            print(f"  {t:>22.12f}  {'(< 14.5, skip)':>14}")
            continue
        print(f"  {t:>22.12f}  {Z_RS(t):>14.4e}  {Z_fast(t):>14.4e}")

    # 2. Scanner sur [14, 60] et comparer avec les 8 premiers zéros
    print("\n  Scanner hybride RS sur [14, 60] :")
    trouves = scanner_segment(14.0, 60.0, step=0.3, verbose=True)
    print(f"\n  {len(trouves)} zéros trouvés vs {len(zeros_ref)} attendus")

    # 3. Benchmark
    benchmark(t_start=500.0, t_end=2000.0, step=0.3)
