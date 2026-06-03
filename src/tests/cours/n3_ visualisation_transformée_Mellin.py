
"""
Module niveau-3 : transformée de Mellin et vérification
Connexion avec  ζ ( s )  
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

from mpmath import mp, mpc, gamma, zeta, pi, quad, exp, log, re, im, fabs
import numpy as np
import matplotlib.pyplot as plt

mp.dps = 20

# Vérification numérique de Γ(s)·ζ(s) = ∫₀^∞ t^(s-1)/(e^t-1) dt
print("Vérification de Γ(s)·ζ(s) = ∫₀^∞ t^(s-1)/(e^t−1) dt\n")
print(f"{'s':<6} | {'Γ(s)·ζ(s)':>16} | {'Intégrale Mellin':>16} | {'Erreur':>12}")
print("-" * 60)

for s_val in [2, 3, 4, 1.5, 2.5]:
    s = mpc(s_val)
    produit = gamma(s) * zeta(s)
    integrale = quad(lambda t: t**(s-1) / (exp(t) - 1), [0, mp.inf])
    err = fabs(produit - integrale)
    print(f"{s_val:<6} | {float(re(produit)):>16.10f} | {float(re(integrale)):>16.10f} | {float(err):>12.2e}")

# Symétrie ξ(s) = ξ(1-s)
print("\nVérification de ξ(s) = ξ(1−s) sur la droite critique\n")
print(f"{'t (Im(s))':>12} | {'|ξ(1/2+it)|':>16} | {'|ξ(1/2-it+1)|':>16} | {'Erreur':>12}")
print("-" * 62)

def xi(s):
    return 0.5 * s * (s-1) * pi**(-s/2) * gamma(s/2) * zeta(s)

for t_val in [5, 10, 14.1347, 20]:
    s = mpc(0.5, t_val)
    xi_s   = xi(s)
    xi_1ms = xi(1 - s)
    err = fabs(xi_s - xi_1ms)
    print(f"{t_val:>12} | {float(fabs(xi_s)):>16.10f} | {float(fabs(xi_1ms)):>16.10f} | {float(err):>12.2e}")

# Graphique : |ξ(1/2 + it)| en fonction de t
t_vals = np.linspace(1, 50, 500)
xi_vals = []
for t in t_vals:
    try:
        xi_vals.append(float(fabs(xi(mpc(0.5, t)))))
    except Exception:
        xi_vals.append(float('nan'))

plt.figure(figsize=(10, 4))
plt.plot(t_vals, xi_vals, 'b-', linewidth=1.5)
plt.axhline(0, color='k', linewidth=0.5)
zeros_t = [14.1347, 21.0220, 25.0109, 30.4249, 32.9351, 37.5862, 40.9187, 43.3271]
for t_z in zeros_t:
    plt.axvline(t_z, color='r', linewidth=1, linestyle='--', alpha=0.6)
plt.plot([], [], 'r--', alpha=0.6, label='Zéros de ζ (et de ξ)')
plt.xlabel('t = Im(s),   s = 1/2 + it')
plt.ylabel('|ξ(1/2 + it)|')
plt.title('Fonction ξ complétée sur la droite critique\nξ(s) = ξ(1−s)  —  les zéros de ξ coïncident avec les zéros non triviaux de ζ')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("niveau3_xi.png", dpi=150)
plt.show()
print("Graphique sauvegardé : niveau3_xi.png")