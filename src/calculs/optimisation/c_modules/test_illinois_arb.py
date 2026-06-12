#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_illinois_arb.py — validation de illinois_refine_arb sur les 20 premiers zéros
═══════════════════════════════════════════════════════════════════════════════════
Compare les zéros calculés par illinois_refine_arb (Arb/FLINT) aux valeurs LMFDB.
Tolérance : < 1e-8 (suffisant pour double précision, objectif : < 1e-9).

Benchmark : illinois_refine_arb vs mpmath.findroot (dps=35) sur les mêmes brackets.
"""

import sys
import os
import time
import ctypes
import math

import mpmath
mpmath.mp.dps = 35

# ── Chemin du .so ──────────────────────────────────────────────────────────────
SO_PATH = os.path.join(os.path.dirname(__file__), "illinois_arb.so")
if not os.path.exists(SO_PATH):
    print(f"ERREUR : illinois_arb.so introuvable à {SO_PATH}")
    sys.exit(1)

lib = ctypes.CDLL(SO_PATH)
lib.illinois_refine_arb.restype  = ctypes.c_double
lib.illinois_refine_arb.argtypes = [
    ctypes.c_double,  # a
    ctypes.c_double,  # b
    ctypes.c_double,  # fa = Z(a)
    ctypes.c_double,  # fb = Z(b)
    ctypes.c_double,  # tol
    ctypes.c_int,     # max_iter
]

# ── Références LMFDB — 20 premiers zéros non-triviaux ─────────────────────────
LMFDB_20 = [
    14.134725141734693,
    21.022039638771555,
    25.010857580145688,
    30.424876125859513,
    32.935061587739189,
    37.586178158825671,
    40.918719012147495,
    43.327073280914999,
    48.005150881167159,
    49.773832477672302,
    52.970321477714461,
    56.446247697063394,
    59.347044003113821,
    60.831778524609809,
    65.112544048081659,
    67.079810529494173,
    69.546401711173979,
    72.067157674481907,
    75.704690699083933,
    77.144840068874805,
]

TOL_ARRY = 1e-9   # tolérance affinage illinois_refine_arb
MAX_ITER = 50     # itérations max

# ── Construction des brackets (a, b, fa, fb) via mpmath.siegelz ───────────────
# Chaque bracket encadre un zéro connu : [γ - δ, γ + δ] avec δ suffisamment
# petit pour garantir exactement 1 changement de signe dans l'intervalle.
DELTA = 0.3

def construire_bracket(gamma: float):
    """Retourne (a, b, fa, fb) tel que Z(a)·Z(b) < 0 autour de γ."""
    a  = gamma - DELTA
    b  = gamma + DELTA
    fa = float(mpmath.siegelz(a))
    fb = float(mpmath.siegelz(b))
    if fa * fb >= 0:
        # Si pas de changement de signe, affiner δ
        for delta in [0.1, 0.05, 0.02, 0.01, 0.005]:
            a  = gamma - delta
            b  = gamma + delta
            fa = float(mpmath.siegelz(a))
            fb = float(mpmath.siegelz(b))
            if fa * fb < 0:
                break
    return a, b, fa, fb


print("=" * 72)
print("  test_illinois_arb.py — validation illinois_refine_arb")
print("  Tolérance : 1e-9  |  Références : LMFDB (20 premiers zéros)")
print("=" * 72)
print()

# ── Construction des brackets (mesure du temps de préparation) ────────────────
brackets = []
for gamma in LMFDB_20:
    brackets.append(construire_bracket(gamma))

# ── Test 1 : précision illinois_refine_arb ────────────────────────────────────
print("Test 1 : précision illinois_refine_arb")
print(f"  {'n':>3}  {'γ LMFDB':>22}  {'γ calculé':>22}  {'erreur':>12}  {'statut'}")
print(f"  {'-'*3}  {'-'*22}  {'-'*22}  {'-'*12}  {'-'*6}")

n_ok = 0
t_total_arb = 0.0
for i, (gamma_ref, (a, b, fa, fb)) in enumerate(zip(LMFDB_20, brackets)):
    t0   = time.perf_counter()
    zero = lib.illinois_refine_arb(a, b, fa, fb, TOL_ARRY, MAX_ITER)
    t_total_arb += time.perf_counter() - t0
    err  = abs(zero - gamma_ref)
    ok   = err < 1e-8
    if ok:
        n_ok += 1
    print(f"  {i+1:>3}  {gamma_ref:>22.15f}  {zero:>22.15f}  {err:>12.2e}  {'OK' if ok else 'ECHEC'}")

print()
print(f"  Résultat : {n_ok}/20 OK  |  Temps total : {t_total_arb*1e3:.2f} ms"
      f"  |  {t_total_arb/20*1e3:.3f} ms/zéro")
print()

# ── Test 2 : benchmark vs mpmath.findroot ────────────────────────────────────
print("Test 2 : benchmark illinois_refine_arb vs mpmath.findroot (dps=35)")
print()

# Benchmark illinois_refine_arb (déjà mesuré ci-dessus)
ms_arb = t_total_arb / 20 * 1e3

# Benchmark mpmath.findroot (Illinois, dps=35)
z_fn = mpmath.siegelz
t0_mp = time.perf_counter()
for a, b, fa, fb in brackets:
    mpmath.findroot(z_fn, (a, b), solver="illinois", tol=1e-12, maxsteps=80)
ms_mp = (time.perf_counter() - t0_mp) / 20 * 1e3

ratio = ms_mp / ms_arb if ms_arb > 0 else float("inf")

print(f"  illinois_refine_arb  : {ms_arb:.4f} ms/zéro")
print(f"  mpmath.findroot      : {ms_mp:.4f} ms/zéro")
print(f"  Gain mesuré          : ×{ratio:.1f}")
print()

# ── Synthèse ──────────────────────────────────────────────────────────────────
print("=" * 72)
if n_ok == 20:
    print(f"  VALIDATION OK — 20/20 zéros < 1e-8  |  gain ×{ratio:.1f} vs mpmath")
else:
    print(f"  VALIDATION PARTIELLE — {n_ok}/20 OK")
print("=" * 72)

sys.exit(0 if n_ok == 20 else 1)
