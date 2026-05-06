"""
Module niveau-4 : densité et répartition des zéros
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""


from mpmath import mp, mpc, siegeltheta, zeta, exp, re, im, fabs, pi
import numpy as np
import matplotlib.pyplot as plt

mp.dps = 15

def Z(t):
    """Fonction Z de Hardy : Z(t) = e^(iθ(t)) · ζ(1/2 + it), réelle."""
    theta = siegeltheta(t)
    z = exp(mpc(0, float(theta))) * zeta(mpc(0.5, t))
    return float(re(z))

# Vérification aux zéros connus
zeros_t = [14.134725141734693, 21.022039638771555, 25.010857580145688,
           30.424876125859513, 32.935061587739189]
print("Vérification Z(t) aux zéros :")
print(f"{'t':>18} | {'Z(t)':>14} | {'θ(t)':>14}")
print("-" * 52)
for t in zeros_t:
    zt  = Z(t)
    tht = float(siegeltheta(t))
    print(f"{t:>18.8f} | {zt:>14.2e} | {tht:>14.6f}")

# Tracé de Z(t)
t_vals = np.linspace(1, 50, 2000)
Z_vals = [Z(t) for t in t_vals]

fig, axes = plt.subplots(2, 1, figsize=(12, 8))

ax1 = axes[0]
ax1.plot(t_vals, Z_vals, 'b-', linewidth=1.2, label='Z(t)')
ax1.axhline(0, color='k', linewidth=0.8)
for t_z in zeros_t + [37.5862, 40.9187, 43.3271, 48.0052, 49.7738]:
    ax1.axvline(t_z, color='r', linewidth=1, linestyle='--', alpha=0.5)
ax1.fill_between(t_vals, Z_vals, 0,
                 where=[z > 0 for z in Z_vals], alpha=0.15, color='blue')
ax1.fill_between(t_vals, Z_vals, 0,
                 where=[z < 0 for z in Z_vals], alpha=0.15, color='red')
ax1.plot([], [], 'r--', alpha=0.5, label='Zéros (changements de signe)')
ax1.set_ylabel('Z(t)')
ax1.set_title('Fonction Z de Hardy — Z(t) = e^(iθ(t))·ζ(1/2+it)\nFonction réelle, ses zéros = zéros non triviaux de ζ')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xlim(1, 50)

# θ(t) — fonction de Siegel
theta_vals = [float(siegeltheta(t)) for t in t_vals]
ax2 = axes[1]
ax2.plot(t_vals, theta_vals, 'g-', linewidth=1.5, label='θ(t) = arg(Γ(1/4+it/2)) − (t/2)log π')
ax2.axhline(0, color='k', linewidth=0.5)
ax2.set_xlabel('t')
ax2.set_ylabel('θ(t) (radians)')
ax2.set_title('Fonction de Siegel θ(t) — phase de Z(t)\nCroît approximativement comme (t/2)log(t/2π)')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xlim(1, 50)

plt.tight_layout()
plt.savefig("niveau4_hardy_Z.png", dpi=150)
plt.show()
print("Graphique sauvegardé : niveau4_hardy_Z.png")