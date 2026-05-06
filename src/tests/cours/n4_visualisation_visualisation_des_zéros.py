"""
Module niveau-4 : visualisation des zéros
Connexion avec  ζ ( s )  
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

from mpmath import mp, mpc, zeta, re, im, fabs
import numpy as np
import matplotlib.pyplot as plt

mp.dps = 15

# Premiers zéros connus
zeros_t = [14.134725141734693, 21.022039638771555, 25.010857580145688,
           30.424876125859513, 32.935061587739189, 37.586178158825671,
           40.918719012147495, 43.327073280914999, 48.005150881167159,
           49.773832477672302]

print("Vérification des zéros non triviaux de ζ(s) :")
print(f"{'n':<4} | {'t_n':>18} | {'|ζ(1/2+it_n)|':>16}")
print("-" * 44)
for n, t in enumerate(zeros_t, 1):
    s = mpc(0.5, t)
    val = fabs(zeta(s))
    print(f"{n:<4} | {t:>18.12f} | {float(val):>16.2e}")

# Carte des zéros dans la bande critique
fig, axes = plt.subplots(1, 2, figsize=(13, 7))

# Gauche : plan complexe avec zéros
ax1 = axes[0]
t_dense = np.linspace(0.1, 52, 1000)
sigma_vals = [0.5] * len(t_dense)
module_crit = []
for t in t_dense:
    module_crit.append(min(float(fabs(zeta(mpc(0.5, t)))), 3))

ax1.plot(module_crit, t_dense, 'b-', linewidth=1, alpha=0.7)
ax1.axvline(0, color='k', linewidth=0.5)
for t_z in zeros_t:
    ax1.plot(0, t_z, 'r*', markersize=14)
    ax1.annotate(f'  t={t_z:.4f}', (0, t_z), fontsize=8, va='center')
ax1.set_xlabel('|ζ(1/2 + it)|')
ax1.set_ylabel('t = Im(s)')
ax1.set_title('|ζ(1/2 + it)| — les zéros sont les\npoints rouges où la courbe touche 0')
ax1.set_xlim(-0.2, 3)
ax1.grid(True, alpha=0.3)

# Droite : module sur différentes verticales
ax2 = axes[1]
t_plot = np.linspace(1, 52, 800)
for sigma, color, label in [(0.5,'blue','Re(s)=1/2 (critique)'),
                             (0.7,'orange','Re(s)=0.7'),
                             (0.9,'green','Re(s)=0.9')]:
    mods = [min(float(fabs(zeta(mpc(sigma, t)))), 4) for t in t_plot]
    ax2.plot(t_plot, mods, color=color, linewidth=1.5, label=label)
for t_z in zeros_t:
    ax2.axvline(t_z, color='gray', linewidth=0.5, linestyle=':', alpha=0.5)
ax2.set_xlabel('t = Im(s)')
ax2.set_ylabel('|ζ(σ + it)|')
ax2.set_title('|ζ(s)| sur différentes droites verticales\nSeule Re(s)=1/2 atteint 0')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("niveau4_zeros.png", dpi=150)
plt.show()
print("Graphique sauvegardé : niveau4_zeros.png")