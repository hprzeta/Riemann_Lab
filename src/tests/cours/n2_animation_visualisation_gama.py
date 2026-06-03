"""
Module niveau-3 : visualisation de Γ ( s )  gamma
Connexion avec  ζ ( s )  
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""
from mpmath import mp, gamma, sqrt, pi, factorial, fabs
import numpy as np
import matplotlib.pyplot as plt

mp.dps = 15

# Valeurs remarquables
print("Valeurs de Γ(s) :")
print(f"{'s':<8} | {'Γ(s)':>16} | {'Référence':>20}")
print("-" * 50)
for s, ref in [(1,'0!=1'), (2,'1!=1'), (3,'2!=2'), (4,'3!=6'), (5,'4!=24'),
               (0.5, '√π'), (1.5, '√π/2'), (2.5, '3√π/4')]:
    print(f"{s:<8} | {float(gamma(s)):>16.8f} | {ref}")

# Graphique réel
s_pos = np.linspace(0.1, 5, 500)
g_pos = [float(gamma(s)) for s in s_pos]

s_neg1 = np.linspace(-3.95, -3.05, 200)
s_neg2 = np.linspace(-2.95, -2.05, 200)
s_neg3 = np.linspace(-1.95, -1.05, 200)
s_neg4 = np.linspace(-0.95, -0.05, 200)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(s_pos, g_pos, 'b-', linewidth=2, label='Γ(s) pour s > 0')
for s_seg in [s_neg1, s_neg2, s_neg3, s_neg4]:
    g_seg = [float(gamma(s)) for s in s_seg]
    ax.plot(s_seg, g_seg, 'b-', linewidth=2)

ax.axhline(0, color='k', linewidth=0.5)
for n in [0, -1, -2, -3]:
    ax.axvline(n, color='r', linewidth=1, linestyle='--', alpha=0.5)
ax.plot([], [], 'r--', alpha=0.5, label='Pôles de Γ en 0, -1, -2, ...')

# Points n! = Γ(n+1)
for n in range(1, 5):
    ax.plot(n+1, float(gamma(n+1)), 'go', markersize=8)
    ax.annotate(f'  {n}!={int(factorial(n))}', (n+1, float(gamma(n+1))), fontsize=9)
ax.plot([], [], 'go', markersize=8, label='Γ(n+1) = n!')
ax.plot(0.5, float(gamma(0.5)), 'r^', markersize=10, label=f'Γ(1/2) = √π ≈ {float(sqrt(pi)):.4f}')

ax.set_xlim(-4, 5.5)
ax.set_ylim(-10, 25)
ax.set_xlabel('s')
ax.set_ylabel('Γ(s)')
ax.set_title('Fonction Gamma — généralisation de la factorielle\nPôles simples en s = 0, −1, −2, ...')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("niveau3_gamma.png", dpi=150)
plt.show()
print("Graphique sauvegardé : niveau3_gamma.png")