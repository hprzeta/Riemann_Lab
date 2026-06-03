"""
Module niveau-1 : visualisation de suite 
Connexion avec  ζ ( s ) 
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""
from mpmath import mp, mpf
import matplotlib.pyplot as plt

mp.dps = 15

n_vals = list(range(1, 51))
u1 = [float(mpf(1)/n)    for n in n_vals]   # 1/n
u2 = [float(mpf(1)/n**2) for n in n_vals]   # 1/n²

print(f"{'n':<6} | {'1/n':>10} | {'1/n²':>10}")
print("-" * 32)
for n in [1, 2, 5, 10, 20, 50]:
    print(f"{n:<6} | {float(mpf(1)/n):>10.6f} | {float(mpf(1)/n**2):>10.6f}")

plt.figure(figsize=(9, 4))
plt.plot(n_vals, u1, 'b-o', markersize=4, label='$u_n = 1/n$')
plt.plot(n_vals, u2, 'r-o', markersize=4, label='$u_n = 1/n^2$')
plt.axhline(0, color='k', linewidth=0.8, linestyle='--', label='Limite = 0')
plt.xlabel('n')
plt.ylabel('$u_n$')
plt.title('Convergence des suites $1/n$ et $1/n^2$ vers 0')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("niveau1_suites.png", dpi=150)
plt.show()