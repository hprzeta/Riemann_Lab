"""
────────────────────────────────────────────────────────────────────────────
Méthode   : Riemann-Siegel from-scratch — Version pédagogique
Auteur    : hprzeta — Exploration de l'Hypothèse de Riemann
Date      : 2026
────────────────────────────────────────────────────────────────────────────

"""
import mpmath as mp
import numpy as np

def theta_riemann_siegel(t):
    """
    Phase θ(t) = Im[ln Γ(1/4 + it/2)] - (t/2)ln(π)
    """
    return mp.im(mp.loggamma(mp.mpf('0.25') + mp.mpc(0, t)/2)) - (t/2)*mp.log(mp.pi)

def Z_riemann_siegel(t, N=None):
    """
    Fonction Z de Hardy via formule de Riemann-Siegel
    
    Z(t) = 2 * Σ_{n=1}^{N} cos(θ(t) - t*ln(n)) / √n + R(t)
    
    où N = floor(√(t/2π)) et R(t) = termes de correction
    """
    if N is None:
        N = int(mp.sqrt(t / (2*mp.pi)))
    
    theta = theta_riemann_siegel(t)
    
    # Somme principale
    somme = mp.mpf('0')
    for n in range(1, N+1):
        somme += mp.cos(theta - t*mp.log(n)) / mp.sqrt(n)
    
    # Termes de correction R(t) — simplifiés ici
    # (À compléter avec les termes de la série asymptotique)
    R = correction_riemann_siegel(t, N)
    
    return 2 * somme + R

def correction_riemann_siegel(t, N):
    """
    Termes de correction de la formule de Riemann-Siegel
    (Développement asymptotique)
    """
    # Premier terme de correction
    p = mp.sqrt(t/(2*mp.pi)) - N
    C0 = mp.mpf('-1') / (mp.sqrt(2) * mp.pi)  # Simplifié
    
    # ... (à développer selon la précision souhaitée)
    return C0  # Placeholder
