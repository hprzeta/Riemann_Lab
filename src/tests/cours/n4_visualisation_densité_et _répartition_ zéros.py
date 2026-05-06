"""
Module niveau-4 : densité et répartition des zéros
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

from mpmath import mp, mpf, pi, log, exp
import numpy as np
import matplotlib.pyplot as plt

mp.dps = 15

# Formule de Weyl pour N(T)
def N_weyl(T):
    T = mpf(T)
    return T/(2*pi) * log(T/(2*pi*exp(1))) + mpf('7')/8

print("Densité des zéros — formule de Weyl N(T) :")
print(f"{'T':>8} | {'N(T) Weyl':>14} | {'N(T) exact':>12}")
print("-" * 42)
# Valeurs exactes connues
exacts = {10: 0, 20: 2, 30: 4, 40: 8, 50: 10,
          100: 29, 200: 70, 500: 214, 1000: 449}
for T, n_exact in sorted(exacts.items()):
    n_weyl = float(N_weyl(T))
    print(f"{T:>8} | {n_weyl:>14.2f} | {n_exact:>12}")

# Graphique : N(T) weyl vs escalier réel
zeros_t = [14.1347, 21.0220, 25.0109, 30.4249, 32.9351,
           37.5862, 40.9187, 43.3271, 48.0052, 49.7738]

T_vals = np.linspace(1, 52, 500)
weyl_vals = [float(N_weyl(T)) for T in T_vals]

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(T_vals, weyl_vals, 'b-', linewidth=2, label='Formule de Weyl N(T)')

# Fonction escalier réelle
step_T = [0] + [t for t in sorted(zeros_t) for _ in range(2)] + [52]
step_N = [0] + [n for n in range(1, len(zeros_t)+1) for _ in range(2)]
ax.step(sorted(zeros_t + [0, 52]), list(range(len(zeros_t)+1)) + [len(zeros_t)],
        'r-', where='post', linewidth=2, label='N(T) réel (10 premiers zéros)')

for t_z in zeros_t:
    ax.axvline(t_z, color='gray', linewidth=0.7, linestyle=':', alpha=0.6)

ax.set_xlabel('T')
ax.set_ylabel('Nombre de zéros N(T) avec Im(ρ) < T')
ax.set_title('Densité des zéros de ζ(s) sur la droite critique\nFormule de Weyl vs comptage réel')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("niveau4_densite_zeros.png", dpi=150)
plt.show()
print("Graphique sauvegardé : niveau4_densite_zeros.png")