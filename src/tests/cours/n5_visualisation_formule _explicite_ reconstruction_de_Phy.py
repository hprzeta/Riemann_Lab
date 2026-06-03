"""
Module niveau-5 : formule explicite et reconstruction de ψ(x)
Auteur : hprzeta
"""
from mpmath import mp, mpf, mpc, log, sqrt, exp, pi, zeta, re, im, fabs, power
from sympy import primerange, factorint
import numpy as np
import matplotlib.pyplot as plt

mp.dps = 20

# ψ(x) exact — fonction de Tchebyshev
def psi_exact(x):
    """ψ(x) = Σ_{p^k ≤ x} log(p)"""
    s = mpf(0)
    for p in primerange(2, int(x)+1):
        pk = p
        while pk <= x:
            s += log(p)
            pk *= p
    return float(s)

# ψ(x) approché par formule explicite (N premiers zéros)
zeros_t = [14.134725141734693, 21.022039638771555, 25.010857580145688,
           30.424876125859513, 32.935061587739189, 37.586178158825671,
           40.918719012147495, 43.327073280914999, 48.005150881167159,
           49.773832477672302]

def psi_explicite(x, zeros_t):
    """Approximation de ψ(x) via la formule explicite de Riemann."""
    x = mpf(x)
    S = x  # terme principal
    for t in zeros_t:
        rho = mpc(0.5, t)
        S -= re(power(x, rho) / rho)
        rho_conj = mpc(0.5, -t)
        S -= re(power(x, rho_conj) / rho_conj)
    S -= log(2*pi)  # correction constante approx.
    return float(S)

# Comparaison
print("Reconstruction de ψ(x) par formule explicite :\n")
print(f"{'x':>8} | {'ψ exact':>12} | {'ψ explicite':>12} | {'Erreur %':>10}")
print("-" * 50)
for x in [10, 20, 50, 100, 200]:
    p_ex  = psi_exact(x)
    p_app = psi_explicite(x, zeros_t)
    err   = abs(p_ex - p_app) / p_ex * 100 if p_ex > 0 else 0
    print(f"{x:>8} | {p_ex:>12.4f} | {p_app:>12.4f} | {err:>9.2f}%")

# Graphique
x_vals = np.linspace(2, 150, 600)
psi_ex_vals   = [psi_exact(x) for x in x_vals]
psi_app_vals  = [psi_explicite(x, zeros_t) for x in x_vals]
psi_lisse     = [float(x) for x in x_vals]  # terme principal seul

fig, axes = plt.subplots(2, 1, figsize=(12, 9))

ax1 = axes[0]
ax1.plot(x_vals, psi_ex_vals,  'k-',  linewidth=1.5, label='ψ(x) exact')
ax1.plot(x_vals, psi_app_vals, 'r--', linewidth=1.5, label=f'ψ(x) formule explicite ({len(zeros_t)} zéros)')
ax1.plot(x_vals, psi_lisse,    'b:',  linewidth=1.5, alpha=0.7, label='ψ(x) ≈ x (terme principal)')
for p in primerange(2, 151):
    ax1.axvline(p, color='gray', linewidth=0.3, alpha=0.4)
ax1.set_xlabel('x')
ax1.set_ylabel('ψ(x)')
ax1.set_title('Formule explicite de Riemann — reconstruction de ψ(x)\nChaque zéro de ζ ajoute une oscillation')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

ax2 = axes[1]
erreur = [a - e for a, e in zip(psi_app_vals, psi_ex_vals)]
ax2.plot(x_vals, erreur, 'purple', linewidth=1.2)
ax2.axhline(0, color='k', linewidth=0.8)
ax2.set_xlabel('x')
ax2.set_ylabel('ψ_explicite(x) − ψ_exact(x)')
ax2.set_title('Erreur de troncature — due aux zéros non inclus dans la somme')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("niveau5_formule_explicite.png", dpi=150)
plt.show()
print("Graphique sauvegardé : niveau5_formule_explicite.png")