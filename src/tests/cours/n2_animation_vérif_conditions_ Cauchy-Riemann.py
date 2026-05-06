"""
Module niveau-2 : vérification des conditions de Cauchy-Riemann  
Connexion avec  ζ ( s )  
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

from mpmath import mp, mpc, re, im, diff
import numpy as np
import matplotlib.pyplot as plt

mp.dps = 15

def f(z):
    return z**2

# Vérification numérique des conditions C-R en z = 1 + 2i
z0 = mpc(1, 2)
h = 1e-7

# Dérivées partielles de u = Re(f) et v = Im(f)
du_dx = float(re(f(z0 + h) - f(z0)) / h)
du_dy = float(re(f(z0 + mpc(0,h)) - f(z0)) / h)
dv_dx = float(im(f(z0 + h) - f(z0)) / h)
dv_dy = float(im(f(z0 + mpc(0,h)) - f(z0)) / h)

print("Conditions de Cauchy-Riemann pour f(z) = z² en z = 1+2i")
print(f"  du/dx = {du_dx:.6f}   dv/dy = {dv_dy:.6f}   → égaux : {abs(du_dx - dv_dy) < 1e-5}")
print(f"  du/dy = {du_dy:.6f}  -dv/dx = {-dv_dx:.6f}   → égaux : {abs(du_dy + dv_dx) < 1e-5}")

# Visualisation du module |f(z)| sur C
x = np.linspace(-2, 2, 300)
y = np.linspace(-2, 2, 300)
X, Y = np.meshgrid(x, y)
Z = (X + 1j*Y)**2
module = np.abs(Z)

plt.figure(figsize=(7, 6))
plt.contourf(X, Y, module, levels=30, cmap='plasma')
plt.colorbar(label='|f(z)| = |z²|')
plt.xlabel('Re(z)')
plt.ylabel('Im(z)')
plt.title('Module de f(z) = z² — fonction holomorphe\n(les lignes de niveau sont des cercles)')
plt.tight_layout()
plt.savefig("niveau2_holomorphie.png", dpi=150)
plt.show()
print("Graphique sauvegardé : niveau2_holomorphie.png")