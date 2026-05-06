"""
Module niveau-1 : visualisation  convergence de ζ(2)
Connexion avec  ζ ( s ) : convergence
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

from mpmath import mp, mpf, pi, zeta
import matplotlib.pyplot as plt

mp.dps = 15

n_max = 200
S = mpf(0)
partials = []
for n in range(1, n_max + 1):
    S += mpf(1) / n**2
    partials.append(float(S))

exacte = float(pi**2 / 6)
print(f"Σ 1/n² (n=1 à {n_max}) : {partials[-1]:.8f}")
print(f"Valeur exacte π²/6    : {exacte:.8f}")
print(f"Erreur résiduelle     : {abs(partials[-1] - exacte):.2e}")

plt.figure(figsize=(9, 4))
plt.plot(range(1, n_max + 1), partials, 'b-', linewidth=1.5, label='Somme partielle $S_n$')
plt.axhline(exacte, color='r', linestyle='--',
            label=f'$\\zeta(2) = \\pi^2/6 \\approx {exacte:.4f}$')
plt.xlabel('n (nombre de termes)')
plt.ylabel('$S_n$')
plt.title('Convergence de $\\zeta(2) = \\sum_{{n=1}}^{{\\infty}} \\frac{{1}}{{n^2}} = \\frac{{\\pi^2}}{{6}}$')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("niveau1_zeta2_convergence.png", dpi=150)
plt.show()
print("\nGraphique sauvegardé : niveau1_zeta2_convergence.png")