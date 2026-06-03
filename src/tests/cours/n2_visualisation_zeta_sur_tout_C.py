"""
Module niveau-2 : visualisation de ζ ( s ) sur tout C 
Connexion avec  ζ ( s )  
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""
from mpmath import mp, mpc, zeta, re, im, fabs, log, pi
import numpy as np
import matplotlib.pyplot as plt
import warnings

mp.dps = 15

# Valeurs remarquables du prolongement
print("Valeurs de ζ(s) par prolongement analytique :")
print(f"{'s':<12} | {'Re(ζ(s))':>14} | {'Im(ζ(s))':>14} | Note")
print("-" * 65)
points = [
    (mpc(2,   0),   "ζ(2) = π²/6"),
    (mpc(0,   0),   "ζ(0) = -1/2"),
    (mpc(-1,  0),   "ζ(-1) = -1/12"),
    (mpc(-2,  0),   "ζ(-2) = 0 (zéro trivial)"),
    (mpc(-3,  0),   "ζ(-3) = 1/120"),
    (mpc(0.5, 14.1347), "premier zéro non trivial"),
]
for s, note in points:
    try:
        val = zeta(s)
        print(f"s={s!r:<10} | {float(re(val)):>+14.6f} | {float(im(val)):>+14.6f} | {note}")
    except Exception:
        print(f"s={s!r:<10} | {'(pôle)':>14} | {'':>14} | {note}")

# Carte du module |ζ(s)| dans la bande critique
sigma = np.linspace(-1, 3, 400)
t     = np.linspace(0.5, 40, 400)
S, T  = np.meshgrid(sigma, t)

module = np.zeros_like(S)
for i in range(len(t)):
    for j in range(len(sigma)):
        try:
            val = zeta(mpc(S[i,j], T[i,j]))
            module[i,j] = min(float(fabs(val)), 5)
        except Exception:
            module[i,j] = 5

fig, ax = plt.subplots(figsize=(10, 7))
cf = ax.contourf(S, T, module, levels=40, cmap='hot_r')
plt.colorbar(cf, ax=ax, label='|ζ(s)| (écrêté à 5)')

# Droite critique
ax.axvline(0.5, color='cyan', linewidth=2, linestyle='--', label='Droite critique Re(s)=1/2')
# Bord de convergence de la série
ax.axvline(1.0, color='lime', linewidth=2, linestyle='--', label='Re(s)=1 (bord série)')

# Zéros connus
zeros_t = [14.1347, 21.0220, 25.0109, 30.4249, 32.9351]
for t_zero in zeros_t:
    ax.plot(0.5, t_zero, 'b*', markersize=12)
ax.plot([], [], 'b*', markersize=12, label='Zéros non triviaux')

ax.set_xlabel('Re(s) = σ', fontsize=12)
ax.set_ylabel('Im(s) = t', fontsize=12)
ax.set_title('Module |ζ(s)| dans la bande 0 < Re(s) < 1\nProlongement analytique au-delà de Re(s) > 1', fontsize=11)
ax.legend(loc='upper right', fontsize=9)
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig("niveau2_zeta_bande_critique.png", dpi=150)
plt.show()
print("Graphique sauvegardé : niveau2_zeta_bande_critique.png")