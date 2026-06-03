"""
Module niveau-3 : visualisation de produit eulérien et convergence
Connexion avec  ζ ( s )  
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

from mpmath import mp, mpf, zeta, pi, log
from sympy import primerange
import matplotlib.pyplot as plt
import numpy as np

mp.dps = 15

# Convergence du produit eulérien vers ζ(2)
primes = list(primerange(2, 500))
produit = mpf(1)
produits = []
for p in primes:
    produit *= mpf(1) / (1 - mpf(1)/p**2)
    produits.append(float(produit))

exacte = float(pi**2 / 6)
print(f"Produit eulérien (500 premiers) : {produits[-1]:.8f}")
print(f"ζ(2) = π²/6                     : {exacte:.8f}")
print(f"Erreur                          : {abs(produits[-1] - exacte):.2e}")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Convergence du produit eulérien
ax1 = axes[0]
ax1.plot(range(1, len(primes)+1), produits, 'b-', linewidth=1.5,
         label='Produit eulérien ∏ 1/(1−p⁻²)')
ax1.axhline(exacte, color='r', linestyle='--',
            label=f'ζ(2) = π²/6 ≈ {exacte:.5f}')
ax1.set_xlabel('Nombre de premiers inclus')
ax1.set_ylabel('Valeur du produit partiel')
ax1.set_title('Convergence du produit eulérien vers ζ(2)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Abscisse de convergence — taux de décroissance de 1/n^s
ax2 = axes[1]
n_vals = np.arange(1, 201)
for s, color in [(1.1, 'red'), (1.5, 'orange'), (2.0, 'green'), (3.0, 'blue')]:
    terms = [float(mpf(1)/n**s) for n in n_vals]
    ax2.semilogy(n_vals, terms, color=color, linewidth=1.5, label=f's = {s}')
ax2.set_xlabel('n')
ax2.set_ylabel('|1/nˢ| (échelle log)')
ax2.set_title('Décroissance des termes 1/nˢ\nplus s est grand, plus la convergence est rapide')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("niveau3_dirichlet.png", dpi=150)
plt.show()
print("Graphique sauvegardé : niveau3_dirichlet.png")