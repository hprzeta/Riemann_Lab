
"""
Module niveau-3 : vérification de l'équation fonctionnelle
Connexion avec  ζ ( s )  
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

from mpmath import mp, mpc, zeta, gamma, pi, sin, fabs, re, im
import numpy as np
import matplotlib.pyplot as plt

mp.dps = 20

def zeta_fonctionnelle(s):
    """ζ(s) calculé via l'équation fonctionnelle à partir de ζ(1-s)."""
    return 2**s * pi**(s-1) * sin(pi*s/2) * gamma(1-s) * zeta(1-s)

# Vérification numérique
print("Vérification de l'équation fonctionnelle ζ(s) = 2ˢπˢ⁻¹sin(πs/2)Γ(1−s)ζ(1−s)\n")
print(f"{'s':<16} | {'ζ(s) direct':>16} | {'ζ(s) fonct.':>16} | {'Erreur':>12}")
print("-" * 68)

points = [
    mpc(-1,  0),
    mpc(-2,  0),
    mpc(-3,  0),
    mpc(0.5, 14.1347),
    mpc(0.3, 10),
    mpc(0.1, 20),
]
for s in points:
    try:
        z_direct = zeta(s)
        z_fonct  = zeta_fonctionnelle(s)
        err = fabs(z_direct - z_fonct)
        print(f"s={float(re(s)):+.1f}{float(im(s)):+.4f}i | "
              f"{float(re(z_direct)):>+16.8f} | "
              f"{float(re(z_fonct)):>+16.8f} | "
              f"{float(err):>12.2e}")
    except Exception as e:
        print(f"s={s}  →  {e}")

# Carte des zéros triviaux et non triviaux
sigma = np.linspace(-5, 2, 300)
t     = np.linspace(0, 50, 400)
S, T  = np.meshgrid(sigma, t)

module = np.zeros_like(S)
for i in range(len(t)):
    for j in range(len(sigma)):
        try:
            val = zeta(mpc(float(S[i,j]), float(T[i,j])))
            module[i,j] = min(float(fabs(val)), 4)
        except Exception:
            module[i,j] = 4

fig, ax = plt.subplots(figsize=(11, 8))
cf = ax.contourf(S, T, module, levels=40, cmap='hot_r')
plt.colorbar(cf, ax=ax, label='|ζ(s)|')

ax.axvline(0.5, color='cyan', linewidth=2.5, linestyle='--', label='Droite critique Re(s)=1/2')
ax.axvline(1.0, color='lime', linewidth=2, linestyle='--', label='Bord série Re(s)=1')
ax.axvline(0.0, color='yellow', linewidth=1.5, linestyle=':', alpha=0.8)

# Zéros non triviaux
zeros_nt = [14.1347, 21.0220, 25.0109, 30.4249, 32.9351, 37.5862, 40.9187, 43.3271, 48.0052]
for t_z in zeros_nt:
    ax.plot(0.5, t_z, 'b*', markersize=12)
ax.plot([], [], 'b*', markersize=12, label='Zéros non triviaux')

# Zéros triviaux (t=0, représentés sur l'axe réel)
for n in [2, 4]:
    ax.plot(-n, 0, 'w^', markersize=10)
ax.plot([], [], 'w^', markersize=10, label='Zéros triviaux s=−2,−4,...')

ax.set_xlabel('Re(s) = σ', fontsize=12)
ax.set_ylabel('Im(s) = t', fontsize=12)
ax.set_title('|ζ(s)| — structure globale via équation fonctionnelle\n'
             'Symétrie ζ(s) ↔ ζ(1−s) autour de Re(s) = 1/2', fontsize=11)
ax.legend(loc='upper right', fontsize=9)
ax.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig("niveau3_eq_fonctionnelle.png", dpi=150)
plt.show()
print("Graphique sauvegardé : niveau3_eq_fonctionnelle.png")