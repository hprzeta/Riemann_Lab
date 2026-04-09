#!/usr/bin/env python3
from mpmath import zeta, mp

# Précision élevée pour les calculs scientifiques
mp.dps = 50

def calculer_zeta(s):
    """Calcule la fonction zêta de Riemann pour un nombre s"""
    return zeta(s)

# Test sur différents points
valeurs_test = [2, 3, 4, 0.5, 1.5, complex(0.5, 14.1347)]

for s in valeurs_test:
    resultat = calculer_zeta(s)
    print(f"ζ({s}) = {resultat}")
