"""
Module niveau-5 : statistiques GUE vs zéros de ζ
Auteur : hprzeta
"""

from mpmath import mp, mpf, pi, log
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt

mp.dps = 15

# Zéros de ζ — table de Odlyzko (premiers 1000 zéros approx. via mpmath)
from mpmath import zetazero
mp.dps = 15

print("Calcul des 200 premiers zéros de ζ...")
N_zeros = 200
zeros = [float(zetazero(n).imag) for n in range(1, N_zeros+1)]
print(f"  t_1 = {zeros[0]:.6f}")
print(f"  t_{N_zeros} = {zeros[-1]:.6f}")

# Normalisation par la densité locale
def densite_locale(t):
    return float(log(t / (2*pi)) / (2*pi))

zeros_norm = [t * densite_locale(t) for t in zeros]
espacements = [zeros_norm[n+1] - zeros_norm[n] for n in range(len(zeros_norm)-1)]

# Distribution de Wigner-Dyson (GUE)
s = np.linspace(0, 4, 500)
wigner = (32/np.pi**2) * s**2 * np.exp(-4*s**2/np.pi)

# Distribution de Poisson (processus indépendant — ce que ce N'EST PAS)
poisson = np.exp(-s)

fig, axes = plt.subplots(1, 2, figsize=(13, 6))

# Histogramme des espacements vs loi de Wigner
ax1 = axes[0]
ax1.hist(espacements, bins=40, density=True, alpha=0.6, color='steelblue',
         label=f'Espacements des {N_zeros} premiers zéros de ζ')
ax1.plot(s, wigner, 'r-', linewidth=2.5, label='Loi de Wigner-Dyson (GUE)')
ax1.plot(s, poisson, 'g--', linewidth=2, label='Loi de Poisson (indépendant)')
ax1.set_xlabel('Espacement normalisé δ')
ax1.set_ylabel('Densité de probabilité')
ax1.set_title('Distribution des espacements entre zéros de ζ\nvs loi GUE — conjecture de Montgomery')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, 4)

# Statistiques des espacements
ax2 = axes[1]
ax2.plot(range(1, len(espacements)+1), espacements, 'b.', markersize=3, alpha=0.5)
ax2.axhline(np.mean(espacements), color='r', linewidth=2,
            label=f'Moyenne = {np.mean(espacements):.4f} (théorique ≈ 1)')
ax2.axhline(1.0, color='g', linewidth=1.5, linestyle='--', label='Valeur théorique = 1')
ax2.set_xlabel('Indice n')
ax2.set_ylabel('Espacement normalisé δₙ')
ax2.set_title('Espacements consécutifs entre les zéros normalisés\n(répulsion de niveaux visible)')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("niveau5_gue_montgomery.png", dpi=150)
plt.show()
print("Graphique sauvegardé : niveau5_gue_montgomery.png")

# Statistiques de base
print(f"\nStatistiques des {len(espacements)} espacements normalisés :")
print(f"  Moyenne   : {np.mean(espacements):.6f}  (théorique : 1.000)")
print(f"  Variance  : {np.var(espacements):.6f}")
print(f"  Min/Max   : {min(espacements):.6f} / {max(espacements):.6f}")
print(f"  Nb δ < 0.1 : {sum(1 for d in espacements if d < 0.1)} (répulsion de niveaux)")