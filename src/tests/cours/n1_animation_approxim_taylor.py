"""
Module niveau-1 : visualisation  approximation de Taylor
Connexion avec  ζ ( s )  : convergence de Taylor
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""
from mpmath import mp, mpf, mpc, exp, cos, sin, pi, factorial
import matplotlib.pyplot as plt
import numpy as np

mp.dps = 15

theta = pi / 3   # θ = 60°
valeur_exacte = exp(mpc(0, float(theta)))

print(f"θ = π/3 ≈ {float(theta):.4f} rad")
print(f"\nApproximation de exp(iθ) par troncature de Taylor :")
print(f"{'Ordre N':<10} | {'Re(approx)':>12} | {'Im(approx)':>12} | {'Erreur':>12}")
print("-" * 52)

for N in [1, 2, 3, 5, 8, 12]:
    approx = mpc(0)
    for k in range(N + 1):
        approx += mpc(0, float(theta))**k / factorial(k)
    err = abs(approx - valeur_exacte)
    print(f"{N:<10} | {float(approx.real):>+12.6f} | {float(approx.imag):>+12.6f} | {float(err):>12.2e}")

print(f"\nValeur exacte  : Re = {float(valeur_exacte.real):+.6f}, Im = {float(valeur_exacte.imag):+.6f}")
print(f"cos(π/3) = 0.5, sin(π/3) = √3/2 ≈ {float(sin(pi/3)):.6f} ✓")

# Visualisation de la convergence des approximations
theta_vals = np.linspace(0, 2 * np.pi, 500)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax1 = axes[0]
ax1.plot(np.cos(theta_vals), np.sin(theta_vals), 'b-', linewidth=2, label='Cercle unité exact')
colors = ['orange', 'green', 'red', 'purple']
for i, N in enumerate([2, 4, 6, 20]):
    re_approx, im_approx = [], []
    for th in theta_vals:
        approx = mpc(0)
        for k in range(N + 1):
            approx += mpc(0, th)**k / factorial(k)
        re_approx.append(float(approx.real))
        im_approx.append(float(approx.imag))
    ax1.plot(re_approx, im_approx, '--', color=colors[i], linewidth=1.2,
             label=f'Taylor ordre {N}')
ax1.set_xlim(-1.5, 1.5)
ax1.set_ylim(-1.5, 1.5)
ax1.set_aspect('equal')
ax1.set_xlabel('Re')
ax1.set_ylabel('Im')
ax1.set_title('Convergence de Taylor vers exp(iθ)')
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

ax2 = axes[1]
for N, color in zip([2, 4, 8, 20], colors):
    errs = []
    for th in theta_vals:
        approx = mpc(0)
        for k in range(N + 1):
            approx += mpc(0, th)**k / factorial(k)
        exact = exp(mpc(0, th))
        errs.append(float(abs(approx - exact)))
    ax2.semilogy(theta_vals, errs, color=color, label=f'Ordre {N}')
ax2.set_xlabel('θ (rad)')
ax2.set_ylabel('Erreur |approx - exact|')
ax2.set_title('Erreur de troncature selon l\'ordre')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("niveau1_taylor_euler.png", dpi=150)
plt.show()
print("\nGraphique sauvegardé : niveau1_taylor_euler.png")