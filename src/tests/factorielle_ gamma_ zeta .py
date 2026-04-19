#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test : Factorielle, Gamma, Digamma et lien avec ζ(s)
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""


import mpmath

mpmath.mp.dps = 50

print("=" * 60)
print("🔗 LIEN CRUCIAL : FACTORIELLE ↔ GAMMA ↔ ZÊTA")
print("=" * 60)

# ═══════════════════════════════════════════════════════════
# PARTIE 1 : FACTORIELLE vs GAMMA
# ═══════════════════════════════════════════════════════════
print("\n📦 PARTIE 1 : Factorielle et Gamma réels")
print("-" * 40)

print("5! =", mpmath.factorial(5))
print("Γ(6) =", mpmath.gamma(6))
print("Γ(6) - 5! =", mpmath.gamma(6) - mpmath.factorial(5))

print("\n📌 Relation fondamentale : Γ(n+1) = n!")

# ═══════════════════════════════════════════════════════════
# PARTIE 2 : GAMMA COMPLEXE
# ═══════════════════════════════════════════════════════════
print("\n📦 PARTIE 2 : Gamma complexe")
print("-" * 40)

s = 0.5 + 14.1347j
print(f"s = {s}")
print(f"Γ(s) = {mpmath.gamma(s)}")
print("→ Nombre complexe !")

# ═══════════════════════════════════════════════════════════
# PARTIE 3 : LOG-GAMMA
# ═══════════════════════════════════════════════════════════
print("\n📦 PARTIE 3 : Log-Gamma")
print("-" * 40)

print(f"Log|Γ({s})| = {mpmath.loggamma(s)}")

# ═══════════════════════════════════════════════════════════
# PARTIE 4 : DIGAMMA (via polygamma)
# ═══════════════════════════════════════════════════════════
print("\n📦 PARTIE 4 : Digamma ψ(z) = Γ'(z)/Γ(z)")
print("-" * 40)

print(f"ψ(1) = {mpmath.polygamma(0, 1)}")      # = -γ
print(f"ψ(0.5) = {mpmath.polygamma(0, 0.5)}")  # ψ(0.5)
print(f"ψ(2) = {mpmath.polygamma(0, 2)}")      # ψ(2) = 1 - γ

print(f"\nγ = -ψ(1) = {-mpmath.polygamma(0, 1)}")

# ═══════════════════════════════════════════════════════════
# PARTIE 5 : LIEN AVEC ZÊTA(s)  ✅ CORRIGÉ
# ═══════════════════════════════════════════════════════════
print("\n📦 PARTIE 5 : Lien avec la fonction Zêta")
print("-" * 40)

s_reel = 2

# Fonction xi complétée
xi = (0.5 * s_reel * (s_reel - 1) * mpmath.pi**(-s_reel/2) * 
       mpmath.gamma(s_reel/2) * mpmath.zeta(s_reel))

# Symétrie ξ(s) = ξ(1-s)
xi_sym = (0.5 * (1-s_reel) * (-s_reel) * mpmath.pi**(-(1-s_reel)/2) * 
           mpmath.gamma((1-s_reel)/2) * mpmath.zeta(1-s_reel))

print(f"ξ(2) = {xi}")
print(f"ξ(-1) = {xi_sym}")

# ✅ CORRECTION : float() pour le formatage
diff_val = abs(xi - xi_sym)
print(f"|ξ(2) - ξ(-1)| = {float(diff_val):.2e}")

# ═══════════════════════════════════════════════════════════
# PARTIE 6 : Constantes
# ═══════════════════════════════════════════════════════════
print("\n📦 PARTIE 6 : Récapitulatif")
print("-" * 40)

print(f"π = {mpmath.pi}")
print(f"γ = {mpmath.euler}")
print(f"e = {mpmath.e}")

print("\n" + "=" * 60)
print("✅ TEST TERMINÉ AVEC SUCCÈS")
print("=" * 60)