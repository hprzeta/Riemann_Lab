"""
Exercice 3 — Vitesse de convergence de ζ(s)
Pour s = 1.1, s = 1.5 et s = 2 :
  - trace l'erreur relative |S_n - ζ(s)| / ζ(s) en fonction de n
  - montre que plus s s'approche de 1, plus la convergence est lente
"""

from mpmath import mp, mpf, zeta
import matplotlib.pyplot as plt
import numpy as np

mp.dps = 25  # précision suffisante pour que ζ(s) exact soit fiable

N_MAX  = 500   # nombre de termes
VALEURS_S = [
    (mpf("1.1"), "blue",  "-",  "s = 1,1  (très lent)"),
    (mpf("1.5"), "orange","--", "s = 1,5  (lent)"),
    (mpf("2"),   "green", ":",  "s = 2    (rapide)"),
]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# ── Graphique gauche : sommes partielles ──────────────────────────────────────
ax1 = axes[0]
for s, color, ls, label in VALEURS_S:
    exact = float(zeta(s))
    partials = []
    S = mpf(0)
    for n in range(1, N_MAX + 1):
        S += mpf(1) / mpf(n) ** s
        partials.append(float(S))
    ns = list(range(1, N_MAX + 1))
    ax1.plot(ns, partials, color=color, linestyle=ls, linewidth=1.8, label=label)
    ax1.axhline(exact, color=color, linestyle=":", alpha=0.4, linewidth=1)

ax1.set_xlabel("n  (nombre de termes)")
ax1.set_ylabel("Somme partielle $S_n$")
ax1.set_title("Sommes partielles de $\\zeta(s)$")
ax1.legend()
ax1.grid(True, alpha=0.3)

# ── Graphique droit : erreur relative (échelle log) ───────────────────────────
ax2 = axes[1]
for s, color, ls, label in VALEURS_S:
    exact = float(zeta(s))
    errors = []
    S = mpf(0)
    for n in range(1, N_MAX + 1):
        S += mpf(1) / mpf(n) ** s
        err = abs(float(S) - exact) / exact
        errors.append(err if err > 0 else 1e-30)   # éviter log(0)
    ns = list(range(1, N_MAX + 1))
    ax2.semilogy(ns, errors, color=color, linestyle=ls, linewidth=1.8, label=label)

ax2.set_xlabel("n  (nombre de termes)")
ax2.set_ylabel("Erreur relative  $|S_n - \\zeta(s)| / \\zeta(s)$")
ax2.set_title("Vitesse de convergence  (échelle logarithmique)")
ax2.legend()
ax2.grid(True, alpha=0.3, which="both")

plt.suptitle(
    "Convergence de la série $\\sum_{n=1}^{N} n^{-s}$ vers $\\zeta(s)$",
    fontsize=13, y=1.01
)
plt.tight_layout()
output_path = "exercice3_convergence_zeta.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight")
plt.show()
print(f"\nGraphique sauvegardé : {output_path}")

# ── Résumé numérique ──────────────────────────────────────────────────────────
print("\nErreur relative après N termes :")
print(f"{'s':<6} | {'ζ(s) exact':>14} | {'err n=50':>12} | {'err n=200':>12} | {'err n=500':>12}")
print("-" * 66)
for s, *_ in VALEURS_S:
    exact = float(zeta(s))
    S = mpf(0)
    checkpoints = {50: None, 200: None, 500: None}
    for n in range(1, N_MAX + 1):
        S += mpf(1) / mpf(n) ** s
        if n in checkpoints:
            checkpoints[n] = abs(float(S) - exact) / exact
    print(
        f"{float(s):<6.1f} | {exact:>14.8f} | "
        f"{checkpoints[50]:>12.2e} | {checkpoints[200]:>12.2e} | {checkpoints[500]:>12.2e}"
    )
