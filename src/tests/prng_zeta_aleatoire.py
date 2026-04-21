# -*- coding: utf-8 -*-
"""
Calcul des zéros de Riemann et générateur PRNG basé sur leurs espacements

Auteur : hprzeta
Date : 2026
"""

from mpmath import *
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import pandas as pd

# ✅ CRÉATION DU DOSSIER OUTPUT
output_dir = Path('output')
output_dir.mkdir(parents=True, exist_ok=True)

# Calcul des 20 premiers zéros
mp.dps = 30  # Précision
zeros = [zetazero(n) for n in range(1, 21)]
imags = [float(im(z)) for z in zeros]  # Parties imaginaires

# ==================== VISUALISATION ====================
plt.figure(figsize=(10, 6))
plt.plot(range(1, 21), imags, 'bo-', label='Parties imaginaires')
plt.xlabel('Numéro du zéro')
plt.ylabel('γ_n = Im(ρ_n)')
plt.title('Premiers 20 zéros non triviaux de ζ(s)')
plt.grid(True, alpha=0.3)
plt.legend()

# ✅ SAUVEGARDE D'ABORD
plt.savefig(output_dir / 'zeros_riemann.png', dpi=150, bbox_inches='tight')
print(f"💾 Graphique sauvegardé : {output_dir / 'zeros_riemann.png'}")

# ✅ AFFICHAGE ENSUITE (sans plt.close() avant !)
plt.show()  # ← BLOQUE l'exécution jusqu'à fermeture de la fenêtre

# ✅ FERMETURE APRÈS AFFICHAGE
plt.close()
# =====================================================

# PRNG : espacements normalisés -> bits
def prng_riemann(seed=42, length=100):
    """
    Générateur pseudo-aléatoire basé sur les espacements des zéros.
    """
    np.random.seed(seed)
    bits = []
    for i in range(length):
        n = (i // 2) % 20 + 1
        if i % 2 == 1:
            espacement = (imags[(n % 20)] - imags[(n-1) % 20]) / np.log(imags[(n % 20)])
        else:
            espacement = 1.0 / np.log(imags[n % 20])
        bit = 1 if espacement > 1 else 0
        bits.append(bit)
    return bits

# Exemple d'utilisation
bits = prng_riemann(length=50)
print("Premiers 50 bits:", ''.join(map(str, bits)))
print("Suite décimale approx:", int(''.join(map(str, bits[:32])), 2) / 2**32)

# Sauvegarde en CSV pour analyse
df = pd.DataFrame({'zero_num': range(1,21), 'imag': imags})
df.to_csv(output_dir / 'riemann_zeros.csv', index=False)
print(f"✅ Données sauvegardées dans {output_dir.absolute()}/")