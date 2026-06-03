"""
Module niveau-5 : calcul des fonctions L et vérification
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

from mpmath import mp, mpc, zeta, re, im, fabs, log, pi, exp
import numpy as np
import matplotlib.pyplot as plt

mp.dps = 15

# Caractère de Dirichlet χ mod 4 (le seul non trivial mod 4)
# χ(1)=1, χ(3)=-1, χ(0)=χ(2)=0
def chi4(n):
    n = n % 4
    if n == 1: return 1
    if n == 3: return -1
    return 0

def L_dirichlet(s, chi, N=5000):
    """Calcul de L(s,χ) = Σ χ(n)/nˢ par troncature."""
    s = mpc(s)
    total = mpc(0)
    for n in range(1, N+1):
        c = chi(n)
        if c != 0:
            total += mpc(c) / mpc(n)**s
    return total

# Comparaison ζ(s) et L(s, χ₄)
print("Valeurs de ζ(s) et L(s, χ₄) = Σ(-1)ⁿ/(2n+1)ˢ pour s réel :\n")
print(f"{'s':>6} | {'ζ(s)':>14} | {'L(s,χ₄)':>14} | Note")
print("-" * 58)
for s_val, note in [(1, 'pôle pour ζ'), (2, 'π²/6'), (3, ''), (4, 'π⁴/90')]:
    z = zeta(s_val) if s_val > 1 else float('inf')
    l = float(re(L_dirichlet(s_val, chi4)))
    print(f"{s_val:>6} | {float(z) if z != float('inf') else 'pôle':>14} | {l:>14.8f} | {note}")

# L(1, χ₄) = π/4 (formule de Leibniz)
print(f"\nL(1, χ₄) = 1 - 1/3 + 1/5 - 1/7 + ... = π/4 ≈ {float(pi)/4:.8f}")
L1_num = float(re(L_dirichlet(1, chi4)))
print(f"L(1, χ₄) numérique = {L1_num:.8f}")

# Module |L(1/2 + it, χ₄)| sur la droite critique
t_vals = np.linspace(1, 50, 500)
L_crit = [float(fabs(L_dirichlet(mpc(0.5, t), chi4, N=2000))) for t in t_vals]
Z_crit = [float(fabs(zeta(mpc(0.5, t)))) for t in t_vals]

fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(t_vals, Z_crit, 'b-', linewidth=1.5, alpha=0.8, label='|ζ(1/2+it)|')
ax.plot(t_vals, L_crit, 'r-', linewidth=1.5, alpha=0.8, label='|L(1/2+it, χ₄)|')
ax.axhline(0, color='k', linewidth=0.5)
ax.set_xlabel('t')
ax.set_ylabel('Module')
ax.set_title('|ζ(1/2+it)| et |L(1/2+it, χ₄)| sur la droite critique\n'
             'Les zéros des fonctions L généralisées obéissent à GRH (conjecturée)')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("niveau5_fonctions_L.png", dpi=150)
plt.show()
print("Graphique sauvegardé : niveau5_fonctions_L.png")