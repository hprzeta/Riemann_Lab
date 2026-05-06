"""
Module niveau-2 : vvisualisation du prolongement 
Connexion avec  ζ ( s )  
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""
from mpmath import mp, mpc, fabs
import numpy as np
import matplotlib.pyplot as plt

mp.dps = 15

# Comparaison : somme partielle vs fonction prolongée 1/(1-z)
def serie_geometrique(z, N=50):
    s = mpc(0)
    zn = mpc(1)
    for n in range(N):
        s += zn
        zn *= z
        if fabs(zn) > 1e10:  # divergence
            return None
    return s

x = np.linspace(-2, 2, 400)
y = np.linspace(-2, 2, 400)
X, Y = np.meshgrid(x, y)
Z_exact = 1.0 / (1.0 - (X + 1j*Y))
module_exact = np.abs(Z_exact)
module_exact = np.clip(module_exact, 0, 10)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Prolongement analytique 1/(1-z)
ax1 = axes[0]
cf1 = ax1.contourf(X, Y, module_exact, levels=30, cmap='viridis')
plt.colorbar(cf1, ax=ax1, label='|1/(1-z)|')
circle = plt.Circle((0,0), 1, color='red', fill=False, linewidth=2, label='|z|=1 (bord de convergence)')
ax1.add_patch(circle)
ax1.plot(1, 0, 'r*', markersize=15, label='Pôle en z=1')
ax1.set_xlim(-2, 2)
ax1.set_ylim(-2, 2)
ax1.set_aspect('equal')
ax1.set_title('Prolongement analytique de Σzⁿ\nFonction 1/(1−z) sur C\\{1}')
ax1.set_xlabel('Re(z)')
ax1.set_ylabel('Im(z)')
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.2)

# Domaine de convergence de la série
ax2 = axes[1]
module_serie = np.where(X**2 + Y**2 < 1, module_exact, np.nan)
cf2 = ax2.contourf(X, Y, module_serie, levels=30, cmap='viridis')
plt.colorbar(cf2, ax=ax2, label='|Σzⁿ| (série tronquée)')
circle2 = plt.Circle((0,0), 1, color='red', fill=False, linewidth=2)
ax2.add_patch(circle2)
ax2.set_xlim(-2, 2)
ax2.set_ylim(-2, 2)
ax2.set_aspect('equal')
ax2.set_title('Série Σzⁿ — converge seulement\npour |z| < 1 (disque rouge)')
ax2.set_xlabel('Re(z)')
ax2.set_ylabel('Im(z)')
ax2.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig("niveau2_prolongement.png", dpi=150)
plt.show()
print("Graphique sauvegardé : niveau2_prolongement.png")