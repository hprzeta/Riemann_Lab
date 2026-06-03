"""
Module niveau-1 : visualisation   exploration de ζ(s)
Connexion avec  ζ ( s )  : limite et vitesse de convergence
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""
from mpmath import mp, mpf, zeta, pi, log
import matplotlib.pyplot as plt
import numpy as np

mp.dps = 15

# Valeurs remarquables de ζ(s)
print("Valeurs de ζ(s) pour s réel :")
print(f"{'s':<6} | {'ζ(s) calculé':>16} | {'ζ(s) exact':>20}")
print("-" * 48)
valeurs = [
    (2,  f"π²/6 = {float(pi**2/6):.8f}"),
    (3,  f"≈ {float(zeta(3)):.8f} (Apéry)"),
    (4,  f"π⁴/90 = {float(pi**4/90):.8f}"),
    (6,  f"π⁶/945 = {float(pi**6/945):.8f}"),
]
for s, exact in valeurs:
    print(f"{s:<6} | {float(zeta(s)):>16.8f} | {exact}")

# Graphique : ζ(s) pour s réel > 1
s_vals = np.linspace(1.05, 6, 300)
z_vals = [float(zeta(s)) for s in s_vals]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax1 = axes[0]
ax1.plot(s_vals, z_vals, 'b-', linewidth=2)
ax1.axhline(1, color='gray', linestyle=':', alpha=0.7, label='Limite = 1 quand s→∞')
ax1.axvline(1, color='r', linestyle='--', alpha=0.5, label='Pôle en s=1')
for s, label in [(2, 'ζ(2)=π²/6'), (3, 'ζ(3)≈1.202'), (4, 'ζ(4)=π⁴/90')]:
    ax1.plot(s, float(zeta(s)), 'ro', markersize=7)
    ax1.annotate(f'  {label}', (s, float(zeta(s))), fontsize=8)
ax1.set_xlabel('s')
ax1.set_ylabel('ζ(s)')
ax1.set_title('$\\zeta(s)$ pour $s$ réel $> 1$')
ax1.set_ylim(0, 12)
ax1.legend()
ax1.grid(True, alpha=0.3)

# Convergence des sommes partielles selon s
ax2 = axes[1]
for s, color, ls in [(1.5, 'blue', '-'), (2, 'red', '--'), (3, 'green', ':')]:
    partials = []
    S = mpf(0)
    for n in range(1, 101):
        S += mpf(1) / mpf(n)**s
        partials.append(float(S))
    exact = float(zeta(s))
    ax2.plot(range(1, 101), partials, color=color, linestyle=ls,
             label=f's={s}  →  ζ(s)≈{exact:.4f}')
ax2.set_xlabel('n (termes inclus)')
ax2.set_ylabel('Somme partielle $S_n$')
ax2.set_title('Vitesse de convergence de ζ(s) selon s')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("niveau1_zeta_exploration.png", dpi=150)
plt.show()
print("\nGraphique sauvegardé : niveau1_zeta_exploration.png")