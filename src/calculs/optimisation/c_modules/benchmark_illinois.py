#!/usr/bin/env python3
# benchmark_illinois.py — illinois_mpfr C vs mpmath sur 100 zéros à t ∈ [500, 1100]
#
# Conditions du benchmark :
#   - Plage t ∈ [500, 1100] → N = ⌊√(t/2π)⌋ ≈ 8–13 → Z_double cohérent avec mpmath
#   - Intervalles [a,b] détectés par Z_double (change de signe) → Illinois C garanti
#   - Méthode A : illinois_mpfr(a, b, tol=1e-12)  — C/libmpfr, 170 bits
#   - Méthode B : mpmath.findroot(mpmath.siegelz, mid, tol=1e-12)  — Python/mpmath, 35 dps
#   - Les deux méthodes cherchent des zéros légèrement différents (RS vs exacte) mais
#     la mesure de vitesse (ms/zéro) est valide et directement comparable.
#
# Phase C — Riemann_Lab / hprzeta — 2026-05-24

import ctypes
import os
import sys
import time
import math

import mpmath
mpmath.mp.dps = 35  # cohérent avec test_illinois.py

# ── chargement de la bibliothèque ────────────────────────────────────────────
_so = os.path.join(os.path.dirname(os.path.abspath(__file__)), "illinois_mpfr.so")
if not os.path.exists(_so):
    print("[ERREUR] illinois_mpfr.so introuvable — lancer 'make' d'abord.")
    sys.exit(1)

_lib = ctypes.CDLL(_so)
_lib.illinois_mpfr.restype  = ctypes.c_double
_lib.illinois_mpfr.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]
_lib.Z_double.restype       = ctypes.c_double
_lib.Z_double.argtypes      = [ctypes.c_double]

def Z_double(t: float) -> float:
    return _lib.Z_double(float(t))

def illinois_c(a: float, b: float, tol: float = 1e-12) -> float:
    return _lib.illinois_mpfr(float(a), float(b), float(tol))


# ── collecte des 100 intervalles à t ∈ [500, 1100] ──────────────────────────
# Détection par Z_double (cohérent avec Illinois C pour ce régime de t)
N_CIBLE = 100
T_DEBUT = 500.0
PAS     = 0.05      # finesse du balayage (espacement moyen ~1.5 pour t~800)
TOL     = 1e-12

print("Collecte des intervalles...")
intervalles = []
t  = T_DEBUT
za = Z_double(t)
while len(intervalles) < N_CIBLE:
    b  = t + PAS
    zb = Z_double(b)
    if za * zb < 0:
        intervalles.append((t, b))
    t, za = b, zb

print(f"{len(intervalles)} intervalles collectés — t ∈ [{intervalles[0][0]:.1f}, {intervalles[-1][1]:.1f}]")
print()

# ── benchmark méthode A : illinois_mpfr C ────────────────────────────────────
print("Méthode A — illinois_mpfr C (libmpfr, 170 bits)...")
resultats_C  = []
temps_C_list = []

for a, b in intervalles:
    t0 = time.perf_counter()
    gamma = illinois_c(a, b, TOL)
    t1 = time.perf_counter()
    resultats_C.append(gamma)
    temps_C_list.append(t1 - t0)

temps_C_moy = sum(temps_C_list) / len(temps_C_list) * 1000   # ms
temps_C_tot = sum(temps_C_list) * 1000

# ── benchmark méthode B : mpmath.findroot ───────────────────────────────────
print("Méthode B — mpmath.findroot(mpmath.siegelz, ...) — Python, 35 dps...")
resultats_mp  = []
temps_mp_list = []

for a, b in intervalles:
    mid = (a + b) / 2.0
    t0  = time.perf_counter()
    gamma = float(mpmath.findroot(mpmath.siegelz, mid, tol=TOL))
    t1  = time.perf_counter()
    resultats_mp.append(gamma)
    temps_mp_list.append(t1 - t0)

temps_mp_moy = sum(temps_mp_list) / len(temps_mp_list) * 1000   # ms
temps_mp_tot = sum(temps_mp_list) * 1000

# ── calcul des écarts entre les deux méthodes ────────────────────────────────
# Les deux méthodes cherchent des zéros légèrement différents (RS vs exacte) ;
# l'écart mesure la différence entre les zéros RS et les vrais zéros de Riemann.
ecarts = [abs(resultats_C[i] - resultats_mp[i]) for i in range(N_CIBLE)]
ecart_moy = sum(ecarts) / N_CIBLE
ecart_max = max(ecarts)

# ── affichage des résultats ──────────────────────────────────────────────────
print()
print("=" * 60)
print("BENCHMARK illinois_mpfr C vs mpmath — Phase C")
print("=" * 60)
print(f"  Nombre de zéros     : {N_CIBLE}")
print(f"  Plage t             : [{intervalles[0][0]:.1f}, {intervalles[-1][1]:.1f}]")
print(f"  N = ⌊√(t/2π)⌋      : {int(math.sqrt(intervalles[0][0]/(2*math.pi)))}–"
      f"{int(math.sqrt(intervalles[-1][1]/(2*math.pi)))}")
print(f"  Tolérance           : {TOL:.0e}")
print()
print(f"  Illinois C (libmpfr 170 bits) :")
print(f"    Temps moyen       : {temps_C_moy:.4f} ms/zéro")
print(f"    Temps total       : {temps_C_tot:.1f} ms")
print()
print(f"  mpmath.findroot (Python, 35 dps) :")
print(f"    Temps moyen       : {temps_mp_moy:.4f} ms/zéro")
print(f"    Temps total       : {temps_mp_tot:.1f} ms")
print()
gain = temps_mp_moy / temps_C_moy
print(f"  ── Rapport de vitesse ──────────────────")
print(f"  Gain Illinois C     : ×{gain:.2f}  (mpmath / C)")
if gain >= 5:
    print(f"  → Objectif ×5–10 {'ATTEINT ✓' if gain <= 10 else 'DÉPASSÉ ✓'}")
elif gain >= 2:
    print(f"  → Objectif ×5–10 partiellement atteint")
else:
    print(f"  → Gain inférieur à ×2 — vérifier la configuration")
print()
print(f"  ── Cohérence des résultats ──────────────")
print(f"  |γ_C − γ_mpmath| moyen : {ecart_moy:.3e}  (biais RS)")
print(f"  |γ_C − γ_mpmath| max   : {ecart_max:.3e}")
print(f"  (écart = différence entre zéros RS et vrais zéros — attendu ~1e-3 pour N=8–10)")
print("=" * 60)
