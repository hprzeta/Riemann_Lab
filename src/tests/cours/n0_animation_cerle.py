#!/usr/bin/env python3
"""
Module niveau-0 : visualisation de e^(iθ) sur le cercle unité
Connexion avec Z(t) de Hardy
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""
from mpmath import mp, exp, pi,  mpc
import matplotlib.pyplot as plt
import numpy as np

mp.dps = 15

# --- Calcul de e^(iθ) pour quelques angles ---
angles = [0, pi/6, pi/4, pi/3, pi/2, pi, 3*pi/2, 2*pi]
print("θ (rad)  | cos θ   | sin θ   | e^(iθ)")
print("-" * 55)
for theta in angles:
    z = exp(mpc(0, float(theta)))   # mpmath pur — évite la conversion via 1j Python
    zr, zi = float(z.real), float(z.imag)
    print(f"{float(theta):.4f}   | {zr:+.4f} | {zi:+.4f} | {zr:+.4f} + {zi:+.4f}i")

# --- Animation : cercle unité ---
theta_vals = np.linspace(0, 2 * np.pi, 500)
x = np.cos(theta_vals)
y = np.sin(theta_vals)

fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.plot(x, y, 'b-', linewidth=2, label='Cercle unité |z|=1')
ax.axhline(0, color='k', linewidth=0.5)
ax.axvline(0, color='k', linewidth=0.5)

# Points remarquables
points = [(1, 0, 'θ=0'), (0, 1, 'θ=π/2'), (-1, 0, 'θ=π'), (0, -1, 'θ=3π/2')]
for px, py, label in points:
    ax.plot(px, py, 'ro', markersize=8)
    ax.annotate(f'  {label}\n  e^(iθ)={px}+{py}i', (px, py), fontsize=9)

ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_aspect('equal')
ax.set_xlabel('Re(z)')
ax.set_ylabel('Im(z)')
ax.set_title("$e^{i\\theta} = \\cos\\theta + i\\sin\\theta$\nLe cercle unité — brique de base de Z(t)")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("niveau0_cercle_unite.png", dpi=150)
plt.show()
print("\nGraphique sauvegardé : niveau0_cercle_unite.png")