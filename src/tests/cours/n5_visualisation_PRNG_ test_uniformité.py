"""
Module niveau-5 : PRNG ζ et test d'uniformité
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

from mpmath import mp, zetazero, frac, log, pi
import numpy as np
from scipy.stats import kstest, uniform
import matplotlib.pyplot as plt

mp.dps = 20

# Génération de la suite pseudo-aléatoire via les zéros de ζ
print("Calcul des 500 premiers zéros de ζ pour le PRNG...")
N = 500
zeros_im = [float(zetazero(n).imag) for n in range(1, N+1)]

# Parties fractionnaires de t_n * log(2) — test de Weyl
seq_log2  = [float(frac(t * log(2)))  for t in zeros_im]
# Parties fractionnaires de t_n / (2π) — espacement normalisé
seq_2pi   = [float(frac(t / (2*pi))) for t in zeros_im]

# Test de Kolmogorov-Smirnov contre la loi uniforme [0,1]
ks_log2, p_log2 = kstest(seq_log2, 'uniform')
ks_2pi,  p_2pi  = kstest(seq_2pi,  'uniform')

print(f"\nTest KS d'uniformité sur {N} valeurs :")
print(f"  {{t_n·log2}}  : statistique KS = {ks_log2:.4f}, p-valeur = {p_log2:.4f}")
print(f"  {{t_n/2π}}   : statistique KS = {ks_2pi:.4f},  p-valeur = {p_2pi:.4f}")
print(f"  (p > 0.05 = pas de raison de rejeter l'uniformité)")

fig, axes = plt.subplots(2, 2, figsize=(13, 10))

# Histogramme {t_n · log 2}
ax1 = axes[0][0]
ax1.hist(seq_log2, bins=25, density=True, alpha=0.7, color='steelblue')
ax1.axhline(1, color='r', linewidth=2, linestyle='--', label='Uniforme [0,1]')
ax1.set_title(f'Distribution de {{t_n·log 2}}\nKS={ks_log2:.4f}, p={p_log2:.3f}')
ax1.set_xlabel('Partie fractionnaire')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Diagramme de dispersion (t_n, t_{n+1}) pour détecter corrélations
ax2 = axes[0][1]
ax2.scatter(seq_log2[:-1], seq_log2[1:], s=3, alpha=0.4, color='steelblue')
ax2.set_title('Diagramme de retard : (uₙ, uₙ₊₁)\n(absence de structure = bonne aléatoire)')
ax2.set_xlabel('uₙ')
ax2.set_ylabel('uₙ₊₁')
ax2.grid(True, alpha=0.3)

# Autocorrélation
ax3 = axes[1][0]
corr = np.correlate(seq_log2 - np.mean(seq_log2),
                    seq_log2 - np.mean(seq_log2), mode='full')
corr = corr[len(corr)//2:] / corr[len(corr)//2]
ax3.plot(range(50), corr[:50], 'b-o', markersize=4)
ax3.axhline(0, color='k', linewidth=0.8)
ax3.axhline(1.96/np.sqrt(N), color='r', linestyle='--', alpha=0.7, label='±1.96/√N (intervalle 95%)')
ax3.axhline(-1.96/np.sqrt(N), color='r', linestyle='--', alpha=0.7)
ax3.set_title('Autocorrélation de {t_n·log 2}\n(doit rester dans les bandes rouges)')
ax3.set_xlabel('Décalage k')
ax3.set_ylabel('Autocorrélation')
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3)

# Évolution de la p-valeur KS en fonction de N
ax4 = axes[1][1]
ns = range(50, N, 10)
p_vals = [kstest(seq_log2[:n], 'uniform')[1] for n in ns]
ax4.plot(ns, p_vals, 'g-', linewidth=1.5)
ax4.axhline(0.05, color='r', linestyle='--', label='Seuil p=0.05')
ax4.set_xlabel('Nombre de zéros utilisés (N)')
ax4.set_ylabel('p-valeur KS')
ax4.set_title('Robustesse du test KS selon N\n(p > 0.05 = uniformité non rejetée)')
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.set_ylim(0, 1)

plt.tight_layout()
plt.savefig("niveau5_prng_zeta.png", dpi=150)
plt.show()
print("Graphique sauvegardé : niveau5_prng_zeta.png")