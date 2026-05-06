"""
Module niveau-4 : formule de Riemann-Siegel et recherche de zéros
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

from mpmath import mp, mpc, mpf, siegeltheta, zeta, exp, re, sqrt, floor, cos, log, pi, fabs
import numpy as np
import matplotlib.pyplot as plt

mp.dps = 20

def Z_hardy(t):
    """Z(t) exact via mpmath."""
    theta = siegeltheta(t)
    z = exp(mpc(0, float(theta))) * zeta(mpc(0.5, t))
    return float(re(z))

def Z_riemann_siegel(t):
    """Approximation de Z(t) par la formule de Riemann-Siegel."""
    t = mpf(t)
    N = int(floor(sqrt(t / (2*pi))))
    theta = siegeltheta(t)
    S = mpf(0)
    for n in range(1, N+1):
        S += cos(theta - t*log(n)) / sqrt(n)
    return float(2 * S)

# Comparaison exact vs approximation
print("Comparaison Z(t) exact vs formule de Riemann-Siegel :\n")
print(f"{'t':>10} | {'Z exact':>14} | {'Z R-S':>14} | {'Erreur':>12}")
print("-" * 56)
for t in [10, 14.1347, 20, 25.011, 30, 40, 50]:
    z_ex = Z_hardy(t)
    z_rs = Z_riemann_siegel(t)
    print(f"{t:>10.4f} | {z_ex:>+14.8f} | {z_rs:>+14.8f} | {abs(z_ex-z_rs):>12.2e}")

# Recherche des zéros par bissection
def trouver_zero(Z_func, a, b, tol=1e-10):
    """Bissection pour trouver un zéro de Z entre a et b."""
    Za, Zb = Z_func(a), Z_func(b)
    if Za * Zb > 0:
        return None
    for _ in range(60):
        m = (a + b) / 2
        Zm = Z_func(m)
        if abs(Zm) < tol or (b-a) < tol:
            return m
        if Za * Zm < 0:
            b, Zb = m, Zm
        else:
            a, Za = m, Zm
    return (a+b)/2

# Grille de recherche
print("\nRecherche des zéros par changements de signe de Z(t) :\n")
t_grid = np.linspace(1, 55, 5000)
Z_grid = [Z_hardy(t) for t in t_grid]

zeros_trouves = []
for k in range(len(t_grid)-1):
    if Z_grid[k] * Z_grid[k+1] < 0:
        t0 = trouver_zero(Z_hardy, t_grid[k], t_grid[k+1])
        if t0 is not None:
            zeros_trouves.append(t0)

zeros_ref = [14.134725141734693, 21.022039638771555, 25.010857580145688,
             30.424876125859513, 32.935061587739189, 37.586178158825671,
             40.918719012147495, 43.327073280914999, 48.005150881167159,
             49.773832477672302]

print(f"{'n':>4} | {'Zéro trouvé':>20} | {'Référence':>20} | {'Erreur':>12}")
print("-" * 64)
for n, (t_calc, t_ref) in enumerate(zip(zeros_trouves, zeros_ref), 1):
    print(f"{n:>4} | {t_calc:>20.12f} | {t_ref:>20.12f} | {abs(t_calc-t_ref):>12.2e}")

# Graphique : Z(t) avec zéros détectés
fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(t_grid, Z_grid, 'b-', linewidth=1, label='Z(t)')
ax.axhline(0, color='k', linewidth=0.8)
for t_z in zeros_trouves:
    ax.plot(t_z, 0, 'r*', markersize=12, zorder=5)
ax.plot([], [], 'r*', markersize=12, label=f'{len(zeros_trouves)} zéros détectés par bissection')
ax.fill_between(t_grid, Z_grid, 0,
                where=[z>0 for z in Z_grid], alpha=0.1, color='blue')
ax.fill_between(t_grid, Z_grid, 0,
                where=[z<0 for z in Z_grid], alpha=0.1, color='red')
ax.set_xlabel('t')
ax.set_ylabel('Z(t)')
ax.set_title('Fonction Z de Hardy — détection des zéros par bissection\n'
             'Chaque changement de signe = un zéro de ζ(1/2+it)')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim(1, 55)
plt.tight_layout()
plt.savefig("niveau4_riemann_siegel.png", dpi=150)
plt.show()
print(f"\nGraphique sauvegardé : niveau4_riemann_siegel.png")