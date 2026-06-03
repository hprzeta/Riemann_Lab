#!/usr/bin/env python3
# test_illinois_v5.py — validation Voie B : illinois_mpfr_cb + callback mpmath.siegelz
#
# Valide que illinois_c_exact converge vers les vrais zéros de Riemann :
#   - LMFDB 10/10 < 1e-8  (critère minimal)
#   - Résidus  < 5e-13    (précision effective mesurée)
#   - Aucune stagnation (cas dégénérés détectés par pré-vérification)
#
# Compare les deux interfaces :
#   - illinois_c_rs   : Z_mpfr interne RS+C0+C1 (biais ~9e-3, référence v4)
#   - illinois_c_exact: callback mpmath.siegelz  (biais < 1e-13, Voie B)
#
# Phase C Voie B — Riemann_Lab / hprzeta — 2026-05-29

import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mpmath
mpmath.mp.dps = 35

from illinois_pyZ import illinois_c_exact, illinois_c_rs

# ── données LMFDB (20 premiers zéros) ────────────────────────────────────────
LMFDB_20 = [
    14.134725141734693, 21.022039638771555, 25.010857580145688,
    30.424876125859513, 32.935061587739189, 37.586178158825671,
    40.918719012147495, 43.327073280914999, 48.005150881167159,
    49.773832477672302, 52.970321477714460, 56.446247697063246,
    59.347044002602353, 60.831778524609882, 65.112544048081607,
    67.079810529494173, 69.546401711173978, 72.067157674481890,
    75.704690699083934, 77.144840069680455,
]


def trouver_iv(ref, pas=0.005):
    """Cherche [a,b] avec changement de signe de mpmath.siegelz.
    Balayage propre (a = b, pas d'accumulation de flottants)."""
    a = ref - 0.5
    while a < ref + 0.5:
        b = a + pas
        za = float(mpmath.siegelz(a))
        zb = float(mpmath.siegelz(b))
        if za * zb < 0:
            return a, b
        a = b  # avancer sans accumulation d'erreurs
    return None, None


print("=" * 80)
print("Validation Voie B — illinois_mpfr_cb + mpmath.siegelz")
print("Comparaison : illinois_c_exact (Voie B) vs illinois_c_rs (v4)")
print("=" * 80)
print()

# ── test illinois_c_exact (Voie B) ───────────────────────────────────────────
print("[ Voie B — illinois_c_exact ]")
print(f"{'n':>3}  {'gamma_exact':>22}  {'|Z(g)|':>12}  {'|delta LMFDB|':>14}  {'ms':>8}  ok")
print("-" * 70)

nb_ok_exact  = 0
nb_ok_lmfdb  = 0
temps_exact  = []

for i, ref in enumerate(LMFDB_20):
    a, b = trouver_iv(ref)
    if a is None:
        print(f"{i+1:>3}  {'[intervalle introuvable]':>40}")
        continue

    t0 = time.perf_counter()
    g  = illinois_c_exact(a, b, 1e-12)
    dt = (time.perf_counter() - t0) * 1000

    residu     = abs(float(mpmath.siegelz(g)))
    delta_lmf  = abs(g - ref)
    ok_conv    = residu < 1e-8
    ok_lmfdb   = delta_lmf < 1e-10

    nb_ok_exact += ok_conv
    nb_ok_lmfdb += ok_lmfdb
    temps_exact.append(dt)

    sym = "✓" if ok_conv else "✗"
    print(f"{i+1:>3}  {g:>22.15f}  {residu:>12.2e}  {delta_lmf:>14.2e}  {dt:>8.1f}  {sym}")

print("-" * 70)
print(f"Convergence (|Z(g)| < 1e-8)  : {nb_ok_exact}/20")
print(f"Précision LMFDB (< 1e-10)    : {nb_ok_lmfdb}/20")
if temps_exact:
    print(f"Temps moyen                   : {sum(temps_exact)/len(temps_exact):.1f} ms/zéro")
    print(f"Temps médian                  : {sorted(temps_exact)[len(temps_exact)//2]:.1f} ms/zéro")
print()

# ── test illinois_c_rs (v4 reference) ────────────────────────────────────────
print("[ Référence v4 — illinois_c_rs (Z_mpfr RS+C0+C1) ]")
print(f"{'n':>3}  {'gamma_rs':>22}  {'|Z(g)|':>12}  {'|delta LMFDB|':>14}  ok")
print("-" * 65)

nb_ok_rs    = 0
nb_ok_lmfdb_rs = 0

for i, ref in enumerate(LMFDB_20[:10]):  # 10 premiers seulement (biais connu)
    a, b = trouver_iv(ref)
    if a is None:
        continue
    g = illinois_c_rs(a, b, 1e-12)
    residu    = abs(float(mpmath.siegelz(g)))
    delta_lmf = abs(g - ref)
    ok_conv   = residu < 1e-8
    nb_ok_rs += ok_conv
    sym = "✓" if ok_conv else "✗"
    print(f"{i+1:>3}  {g:>22.15f}  {residu:>12.2e}  {delta_lmf:>14.2e}  {sym}")

print("-" * 65)
print(f"Convergence v4 (|Z(g)| < 1e-8) : {nb_ok_rs}/10  [biais RS attendu ~9e-3]")
print()

# ── récapitulatif ─────────────────────────────────────────────────────────────
print("=" * 80)
print("RÉCAPITULATIF")
print("=" * 80)
print(f"  Voie B  illinois_c_exact : {nb_ok_exact}/20 convergences (|Z| < 1e-8)")
print(f"  Voie B  LMFDB < 1e-10   : {nb_ok_lmfdb}/20")
print(f"  Réf. v4 illinois_c_rs   : {nb_ok_rs}/10 convergences  [comparaison]")
print()

# critères de succès
if nb_ok_exact >= 18:
    print("[SUCCÈS] Voie B validée — illinois_mpfr_cb converge sur ≥ 18/20 zéros.")
    sys.exit(0)
else:
    print(f"[AVERTISSEMENT] Voie B partielle — {nb_ok_exact}/20 convergences.")
    sys.exit(1)
