# Formules de référence — Fonction zêta de Riemann

## Définitions fondamentales

### Série de Dirichlet (Re(s) > 1)
ζ(s) = Σ_{n=1}^∞ 1/n^s = 1 + 1/2^s + 1/3^s + ...

### Produit d'Euler (Re(s) > 1)
ζ(s) = Π_p (1 - p^{-s})^{-1}   [produit sur tous les premiers p]

### Prolongement analytique
ζ(s) est définie sur ℂ \ {1}, avec un pôle simple en s=1

### Équation fonctionnelle
ζ(s) = 2^s · π^{s-1} · sin(πs/2) · Γ(1-s) · ζ(1-s)

### Fonction xi (symétrique)
ξ(s) = ½ s(s-1) π^{-s/2} Γ(s/2) ζ(s)
ξ(s) = ξ(1-s)   ← symétrie clé

## Fonction Z de Hardy (calcul des zéros)

Z(t) = e^{iθ(t)} · ζ(½ + it)   ← réelle pour t réel

### Fonction θ(t)
θ(t) = Im[ln Γ(¼ + it/2)] - (t/2)·ln(π)

Propriété clé : Z(t) = 0 ⟺ ζ(½ + it) = 0
→ Détecter les zéros de Z(t) suffit pour trouver les zéros de ζ sur la droite critique

## Hypothèse de Riemann

Tous les zéros non triviaux de ζ(s) vérifient Re(s) = 1/2

Zéros triviaux : s = -2, -4, -6, ... (négatifs pairs)
Zéros non triviaux : dans la bande 0 < Re(s) < 1

## Formule de Riemann-von Mangoldt

N(T) = nombre de zéros avec 0 < Im(s) < T
N(T) ≈ (T/2π) · ln(T/2πe) + O(ln T)

## 10 premiers zéros (référence LMFDB)

| n  | γ_n (partie imaginaire)     |
|----|----------------------------|
| 1  | 14.134725141734693...       |
| 2  | 21.022039638771555...       |
| 3  | 25.010857580145688...       |
| 4  | 30.424876125859513...       |
| 5  | 32.935061587739189...       |
| 6  | 37.586178158825671...       |
| 7  | 40.918719012147495...       |
| 8  | 43.327073280914999...       |
| 9  | 48.005150881167159...       |
| 10 | 49.773832477672286...       |

## Formule de Riemann-Siegel (approximation rapide)

Z(t) ≈ 2 · Σ_{n=1}^{N} cos(θ(t) - t·ln(n)) / √n   où N = floor(√(t/2π))

## Conjecture de Montgomery (espacements)

Les espacements normalisés Δγ_n = (γ_{n+1} - γ_n) · ln(γ_n/2π) / 2π
suivent la distribution GUE (Gaussian Unitary Ensemble) :
p(s) = (π/2) s · e^{-πs²/4}   ← corrélation avec matrices aléatoires

## Lien avec les nombres premiers

π(x) = li(x) - Σ_ρ li(x^ρ) + ...   [formule explicite de Riemann]
où la somme porte sur les zéros non triviaux ρ

La HR ⟹ |π(x) - li(x)| = O(√x · ln x)   [meilleure borne sur l'erreur]
