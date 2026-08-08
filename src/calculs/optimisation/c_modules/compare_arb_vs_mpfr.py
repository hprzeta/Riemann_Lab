#!/usr/bin/env python3
# compare_arb_vs_mpfr.py — comparaison directe illinois_refine_arb (Arb/FLINT)
# vs illinois_refine (MPFR pur, PREC=170 bits) sur les mêmes 300 brackets
# (brackets.json généré par gen_brackets.py, 150 zone A t~[500,5000] 2-Newton,
# 150 zone B t~[50000,150000] 1-Newton). Objectif : chiffrer si le coût
# "ball arithmetic" d'Arb (mag_*, arb_dot... vu au perf record précédent,
# ~91% du temps) est un vrai surcoût vs MPFR pur sans tracking d'erreur.

import ctypes
import json
import os
import time

C_MODULES = os.path.dirname(os.path.abspath(__file__))
BRACKETS_PATH = os.path.join(C_MODULES, "brackets.json")

# ── chargement des deux .so ──────────────────────────────────────────────
lib_arb = ctypes.CDLL(os.path.join(C_MODULES, "illinois_arb.so"))
lib_arb.illinois_refine_arb.restype = ctypes.c_double
lib_arb.illinois_refine_arb.argtypes = [
    ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double,
    ctypes.c_double, ctypes.c_int,
]

lib_mpfr = ctypes.CDLL(os.path.join(C_MODULES, "illinois_mpfr.so"))
lib_mpfr.illinois_refine.restype = ctypes.c_double
lib_mpfr.illinois_refine.argtypes = [
    ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double,
    ctypes.c_int, ctypes.c_double, ctypes.c_int,
]

with open(BRACKETS_PATH) as f:
    data = json.load(f)

zone_a = data["zone_a_2newton"]   # t ~ [500, 5000]
zone_b = data["zone_b_1newton"]   # t ~ [50000, 150000]
brackets = zone_a + zone_b

TOL = 1e-12

# ── benchmark illinois_refine_arb (Arb/FLINT) ────────────────────────────
res_arb = []
t0 = time.perf_counter()
for a, b, fa, fb in brackets:
    res_arb.append(lib_arb.illinois_refine_arb(a, b, fa, fb, TOL, 50))
t_arb = time.perf_counter() - t0

# ── benchmark illinois_refine (MPFR pur, 170 bits) ────────────────────────
res_mpfr = []
t0 = time.perf_counter()
for a, b, fa, fb in brackets:
    res_mpfr.append(lib_mpfr.illinois_refine(a, b, fa, fb, 170, TOL, 100))
t_mpfr = time.perf_counter() - t0

n = len(brackets)
ms_arb = t_arb / n * 1000
ms_mpfr = t_mpfr / n * 1000

# ── écarts arb vs mpfr (cohérence des deux méthodes entre elles) ──────────
ecarts = [abs(res_arb[i] - res_mpfr[i]) for i in range(n)]
ecart_moy = sum(ecarts) / n
ecart_max = max(ecarts)

# séparé par zone
ecarts_a = ecarts[:len(zone_a)]
ecarts_b = ecarts[len(zone_a):]

print("=" * 70)
print("COMPARAISON illinois_refine_arb (Arb/FLINT) vs illinois_refine (MPFR pur)")
print("=" * 70)
print(f"  {n} brackets ({len(zone_a)} zone A t~[500,5000] 2-Newton, "
      f"{len(zone_b)} zone B t~[50000,150000] 1-Newton)")
print()
print(f"  illinois_refine_arb (Arb/FLINT)  : {ms_arb:.4f} ms/appel  (total {t_arb:.2f}s)")
print(f"  illinois_refine (MPFR pur 170b)  : {ms_mpfr:.4f} ms/appel  (total {t_mpfr:.2f}s)")
print()
ratio = ms_mpfr / ms_arb if ms_arb > 0 else float("inf")
if ratio >= 1:
    print(f"  -> Arb est {ratio:.2f}x PLUS RAPIDE que MPFR pur")
else:
    print(f"  -> MPFR pur est {1/ratio:.2f}x PLUS RAPIDE que Arb")
print()
print(f"  Écart |arb - mpfr| moyen : {ecart_moy:.3e}")
print(f"  Écart |arb - mpfr| max   : {ecart_max:.3e}")
print(f"  Écart zone A (2-Newton)  : moy={sum(ecarts_a)/len(ecarts_a):.3e}  max={max(ecarts_a):.3e}")
print(f"  Écart zone B (1-Newton)  : moy={sum(ecarts_b)/len(ecarts_b):.3e}  max={max(ecarts_b):.3e}")
print("=" * 70)

# ── validation absolue sur un sous-échantillon vs mpmath dps=35 (lent) ────
print()
print("Validation absolue sur 10+10 échantillons vs mpmath.findroot(dps=35)...")
import mpmath
mpmath.mp.dps = 35

sample_idx = list(range(0, len(zone_a), max(1, len(zone_a)//10)))[:10] + \
             [len(zone_a) + i for i in list(range(0, len(zone_b), max(1, len(zone_b)//10)))[:10]]

err_arb_ref, err_mpfr_ref = [], []
for i in sample_idx:
    a, b, fa, fb = brackets[i]
    ref = float(mpmath.findroot(mpmath.siegelz, (a, b), solver="illinois", tol=1e-12, maxsteps=80))
    err_arb_ref.append(abs(res_arb[i] - ref))
    err_mpfr_ref.append(abs(res_mpfr[i] - ref))

print(f"  Erreur vs référence mpmath dps=35 (moy sur {len(sample_idx)} échantillons) :")
print(f"    illinois_refine_arb  : {sum(err_arb_ref)/len(err_arb_ref):.3e}  (max {max(err_arb_ref):.3e})")
print(f"    illinois_refine mpfr : {sum(err_mpfr_ref)/len(err_mpfr_ref):.3e}  (max {max(err_mpfr_ref):.3e})")
print("=" * 70)
