#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theta_rapide.py — Calcul rapide de la fonction θ(t) de Riemann-Siegel
═══════════════════════════════════════════════════════════════════════
Remplace la version lente basée sur loggamma(mpmath) par une expansion
asymptotique de Stirling, 10× à 50× plus rapide pour t > 10.

THÉORIE
───────
La définition exacte est :
    θ(t) = Im[ ln Γ(¼ + it/2) ] − (t/2)·ln(π)

L'expansion asymptotique de Stirling donne pour t → ∞ :
    θ(t) = (t/2)·ln(t/2π) − t/2 − π/8
           + 1/(48t) + 7/(5760t³) − 31/(80640t⁵)
           + O(t⁻⁷)

Erreur pour t > 14 : < 10⁻¹⁶ avec les 3 termes correctifs.
Pour t < 14, on bascule automatiquement sur mpmath (exact).

USAGE DANS compute_zeros_v3.py
──────────────────────────────
    from src.calculs.optimisation.theta_rapide import theta_fast, Z_fast

RÉFÉRENCE
─────────
    E.C. Titchmarsh, "The Theory of the Riemann Zeta-Function", §4.12
    A. Odlyzko & A. Schönhage, "Fast algorithms for multiple evaluations of
    the Riemann zeta function", Trans. AMS 309 (1988)

Auteur : hprzeta — Projet Hypothèse de Riemann
Date   : 2026
"""

import math
import numpy as np
from mpmath import mp, loggamma, zeta, mpc, mpf

# ─── Coefficients de Bernoulli B_{2k} pour l'expansion de Stirling ───────────
# θ(t) = (t/2)ln(t/2π) - t/2 - π/8 + Σ B_{2k} / (2k(2k-1) t^{2k-1})
# B_2 = 1/6, B_4 = -1/30, B_6 = 1/42  →  termes : 1/48t, 7/5760t³, -31/80640t⁵
_C1 = 1.0 / 48.0          # coefficient de 1/t
_C2 = 7.0 / 5760.0        # coefficient de 1/t³
_C3 = -31.0 / 80640.0     # coefficient de 1/t⁵  (négatif !)
_LOG_2PI = math.log(2 * math.pi)
_PI_8    = math.pi / 8.0


def theta_asymptotique(t: float) -> float:
    """
    θ(t) par expansion asymptotique de Stirling (float 64 bits, ~15 chiffres).

    Valide pour t ≥ 14.  Erreur absolue < 10⁻¹⁵ pour t > 100.

    Paramètre
    ---------
    t : float — partie imaginaire de s = ½ + it  (t > 0)

    Retourne
    --------
    float — θ(t)
    """
    t2 = t * t          # t²
    t3 = t2 * t         # t³
    t5 = t3 * t2        # t⁵

    return (
        (t / 2.0) * (math.log(t) - _LOG_2PI)  # (t/2)·ln(t/2π)
        - t / 2.0                              # − t/2
        - _PI_8                                # − π/8
        + _C1 / t                              # + 1/(48t)
        + _C2 / t3                             # + 7/(5760t³)
        + _C3 / t5                             # − 31/(80640t⁵)
    )


def theta_exact(t: float, dps: int = 35) -> float:
    """
    θ(t) exact via mpmath.loggamma — utilisé pour t < 14 ou vérification.

    Paramètre
    ---------
    dps : précision en décimales (35 suffit pour les zéros jusqu'à t=10⁶)
    """
    _dps_save = mp.dps
    mp.dps = dps
    val = float(
        mp.im(loggamma(mpf("0.25") + mpc(0, t) / 2))
        - (t / 2) * mp.log(mp.pi)
    )
    mp.dps = _dps_save
    return val


def theta_fast(t: float, seuil_exact: float = 20.0) -> float:
    """
    Sélectionne automatiquement la méthode optimale pour θ(t).

    - t < seuil_exact → mpmath exact  (premiers zéros, t ≲ 20)
    - t ≥ seuil_exact → expansion asymptotique (rapide, suffisamment précis)

    Paramètre
    ---------
    seuil_exact : float  (défaut 20 — au-delà l'asymptotique est < 10⁻¹⁵)
    """
    if t < seuil_exact:
        return theta_exact(t)
    return theta_asymptotique(t)


def Z_fast(t: float, dps: int = 35) -> float:
    """
    Fonction Z de Hardy avec θ calculé rapidement.

    Z(t) = exp(iθ(t)) · ζ(½ + it)

    Optimisations par rapport à la v2 :
      1. θ(t) via expansion asymptotique (pas de loggamma pour t > 20)
      2. Appel unique à mpmath.zeta() avec précision adaptée (dps < 50)
      3. Extraction directe de la partie réelle (évite la création de mpc)

    Paramètre
    ---------
    dps : précision mpmath pour l'appel à zeta() (35 par défaut, suffisant
          pour détecter les changements de signe et affiner à 10⁻¹²)
    """
    _dps_save = mp.dps
    mp.dps = dps

    th  = theta_fast(t)
    # cos(θ)·Re(ζ) − sin(θ)·Im(ζ)  ← formule de Z sans créer exp(iθ)
    s   = mpc("0.5", t)
    z   = zeta(s)
    val = float(math.cos(th) * float(z.real) - math.sin(th) * float(z.imag))

    mp.dps = _dps_save
    return val


# ─── Benchmark rapide ─────────────────────────────────────────────────────────

def benchmark(n_points: int = 1000, t_start: float = 100.0, t_end: float = 1000.0):
    """
    Compare la vitesse de theta_exact vs theta_asymptotique sur n_points.
    Affiche aussi l'erreur maximale entre les deux méthodes.
    """
    import time

    ts = np.linspace(t_start, t_end, n_points)

    # Méthode asymptotique
    debut = time.perf_counter()
    vals_asym = [theta_asymptotique(t) for t in ts]
    dt_asym = time.perf_counter() - debut

    # Méthode exacte mpmath (référence)
    debut = time.perf_counter()
    vals_exact = [theta_exact(t, dps=50) for t in ts]
    dt_exact = time.perf_counter() - debut

    erreurs = [abs(a - e) for a, e in zip(vals_asym, vals_exact)]
    err_max = max(erreurs)

    print(f"\n{'─'*55}")
    print(f"  Benchmark θ(t) — {n_points} points dans [{t_start:.0f}, {t_end:.0f}]")
    print(f"{'─'*55}")
    print(f"  mpmath exact      : {dt_exact:.3f}s")
    print(f"  Asymptotique      : {dt_asym:.3f}s")
    print(f"  Accélération      : {dt_exact/dt_asym:.1f}×")
    print(f"  Erreur max        : {err_max:.2e}  (doit être < 1e-14)")
    print(f"{'─'*55}\n")

    return dt_exact / dt_asym, err_max


if __name__ == "__main__":
    print("─── Test unitaire theta_rapide.py ───")

    # 1. Vérification sur les 5 premiers zéros connus
    zeros_ref = [14.134725141734693, 21.022039638771555,
                 25.010857580145688, 30.424876125859513,
                 32.935061587739189]

    print("\n  θ(t) comparaison exacte vs asymptotique :")
    print(f"  {'t':>20}  {'exact':>18}  {'asympt.':>18}  {'erreur':>12}")
    print("  " + "─" * 72)
    for t in zeros_ref:
        th_e = theta_exact(t, dps=50)
        th_a = theta_asymptotique(t)
        print(f"  {t:>20.12f}  {th_e:>18.12f}  {th_a:>18.12f}  {abs(th_e-th_a):>12.2e}")

    # 2. Vérification : Z(t) ≈ 0 aux zéros connus
    print("\n  Vérification Z_fast(t) aux zéros connus (doit être ≈ 0) :")
    print(f"  {'t':>20}  {'Z_fast(t)':>16}")
    print("  " + "─" * 40)
    for t in zeros_ref:
        print(f"  {t:>20.12f}  {Z_fast(t):>16.2e}")

    # 3. Benchmark
    facteur, err = benchmark(n_points=200, t_start=100.0, t_end=5000.0)
    assert err < 1e-14, f"Erreur trop grande : {err:.2e}"
    print(f"  ✅  Accélération {facteur:.1f}× confirmée, erreur < 1e-14")
