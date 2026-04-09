#!/usr/bin/env python3
"""Fonctions de base pour la fonction zêta de Riemann"""
from mpmath import zeta, mp

# Précision par défaut
mp.dps = 30

def zeta_valeur(s, precision=30):
    """Calcule ζ(s) avec une précision donnée"""
    mp.dps = precision
    return zeta(s)

def calculer_premiers_zeros(n=10, precision=50):
    """Calcule les n premiers zéros non triviaux"""
    mp.dps = precision
    zeros = []
    # Implémentation à compléter
    return zeros
