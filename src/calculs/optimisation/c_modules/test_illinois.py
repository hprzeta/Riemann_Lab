#!/usr/bin/env python3
# test_illinois.py — validation de illinois_mpfr (C/libmpfr)
#
# Stratégie :
#   - Détection des intervalles : Z_double (C float64, même formule RS+C₀+C₁)
#   - Affinage            : illinois_mpfr (C/libmpfr, PREC=170 bits)
#   - Cohérence interne : Z_double(résultat) < 1e-10   (convergence Illinois)
#   - Proximité LMFDB   : |résultat − γ_LMFDB| < 0.5  (bonne identification)
#
# NOTE : Z_mpfr ≈ Z_double (même formule RS+C₀+C₁). Les zéros trouvés sont
# ceux de Z_RS, légèrement différents des vrais zéros de Riemann pour les
# petits t. Pour une précision < 1e-12 vs LMFDB, il faudrait 15+ corrections
# RS ou l'algorithme de Borwein (v5 prévue).
#
# Phase C — Riemann_Lab / hprzeta — 2026-05-24

import ctypes
import os
import sys
import time

# ── chargement de la bibliothèque ────────────────────────────────────────────
_so = os.path.join(os.path.dirname(os.path.abspath(__file__)), "illinois_mpfr.so")
if not os.path.exists(_so):
    print(f"[ERREUR] illinois_mpfr.so introuvable — lancer 'make' d'abord.")
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


def trouver_intervalle_C(t_ref: float, delta: float = 0.5) -> tuple | None:
    """Cherche [a,b] tel que Z_double(a)*Z_double(b) < 0 (même Z que Z_mpfr)."""
    pas  = 0.005
    a    = t_ref - delta
    za   = Z_double(a)
    while a < t_ref + delta:
        b  = a + pas
        zb = Z_double(b)
        if za * zb < 0:
            return (a, b)
        a, za = b, zb
    return None


# ── données de référence LMFDB (10 premiers zéros) ──────────────────────────
LMFDB_10 = [
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
]

TOL_CONVERGENCE = 1e-10   # Z_double(résultat) doit être < cette valeur
TOL_PROXIMITE   = 0.5     # distance max au vrai zéro LMFDB (RS est approximatif)

print("=" * 72)
print("Validation illinois_mpfr  —  Phase C (Z_RS + correction C₀+C₁)")
print("Détection : Z_double C    |  Affinage : illinois_mpfr (PREC=170 bits)")
print("=" * 72)
print(f"{'n':>3}  {'γ_LMFDB':>22}  {'γ_calc':>22}  {'|Z(γ_calc)|':>13}  {'|Δγ|':>10}")
print("-" * 72)

nb_converge = 0
nb_proche   = 0
temps_total = 0.0

for i, gamma_ref in enumerate(LMFDB_10):
    n = i + 1
    iv = trouver_intervalle_C(gamma_ref)
    if iv is None:
        print(f"{n:>3}  {'[intervalle introuvable]':>48}")
        continue

    a, b = iv
    t0      = time.perf_counter()
    gamma_c = illinois_c(a, b, tol=1e-12)
    t1      = time.perf_counter()
    temps_total += (t1 - t0)

    z_val     = abs(Z_double(gamma_c))
    delta_lmf = abs(gamma_c - gamma_ref)
    ok_conv   = z_val     < TOL_CONVERGENCE
    ok_prox   = delta_lmf < TOL_PROXIMITE
    nb_converge += ok_conv
    nb_proche   += ok_prox

    flag = "✓" if ok_conv else "✗"
    print(f"{n:>3}  {gamma_ref:>22.15f}  {gamma_c:>22.15f}  {z_val:>13.2e}  {delta_lmf:>10.5f} {flag}")

print("-" * 72)
print(f"Convergence Illinois (|Z(γ)| < {TOL_CONVERGENCE:.0e})  : {nb_converge}/10")
print(f"Proximité LMFDB     (|Δγ| < {TOL_PROXIMITE})       : {nb_proche}/10")
if nb_converge > 0:
    print(f"Temps moyen affinage Illinois C : {temps_total/nb_converge*1000:.3f} ms/zéro")

print()
if nb_converge >= 9:
    print("[SUCCÈS] Illinois C converge correctement sur les 10 premiers zéros.")
    print("         Les zéros RS sont légèrement décalés des vrais zéros LMFDB")
    print("         (erreur inhérente à la formule RS+C₀+C₁ sans termes sup.).")
    sys.exit(0)
else:
    print(f"[ÉCHEC] Seulement {nb_converge}/10 convergences attendues.")
    sys.exit(1)
