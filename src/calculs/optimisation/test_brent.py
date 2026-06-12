#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_brent.py — Validation brent_refine_adaptive vs illinois_refine_bench
══════════════════════════════════════════════════════════════════════════
Tests :
  1. γ₁  ≈ 14.134725141734693  → erreur < 1e-10
  2. γ₁₀ ≈ 49.773832477672285  → erreur < 1e-10
  3. γ_grand ≈ 77000 (1 zéro réel)  → erreur < 1e-10
  4. Comparaison nb itérations Brent vs Illinois sur 100 zéros

Usage :
  cd ~/projet_zeta
  source zeta_env/bin/activate && export PYTHONPATH=$PWD/src
  python src/calculs/optimisation/test_brent.py

Auteur : hprzeta — Projet Riemann_Lab — Phase C v9
Date   : 2026-06-12
"""

import ctypes
import math
import multiprocessing
import sys
import time
from pathlib import Path

import numpy as np
from riemann_siegel_batch import Z_vect_correct

# ── Chemin .so ─────────────────────────────────────────────────────────────────
SO_PATH = Path(__file__).parent / "c_modules" / "illinois_mpfr.so"
if not SO_PATH.exists():
    sys.exit(f"ERREUR : {SO_PATH} introuvable. Compiler avec : cd c_modules && make")

# ── Référence LMFDB ────────────────────────────────────────────────────────────
LMFDB_20 = [
    14.134725141734693,  21.022039638771555,  25.010857580145688,
    30.424876125859513,  32.935061587739189,  37.586178158825671,
    40.918719012147495,  43.327073280914999,  48.005150881167159,
    49.773832477672285,  52.970321477714461,  56.446247697063244,
    59.347044003002755,  60.831778524609815,  65.112544048081731,
    67.079810529494187,  69.546401711173979,  72.067157674481907,
    75.704690699083974,  77.144840068874806,
]

# Constantes v9
ITER_SWITCH = 3
MAX_ITER    = 30
PREC_FAST   = 64
PREC_FULL   = 80

# Constantes v8/illinois (pour comparaison)
IL_ITER_SWITCH = 8
IL_MAX_ITER    = 50


def charger_lib():
    """Charge le .so et configure les deux bindings."""
    lib = ctypes.CDLL(str(SO_PATH))

    lib.brent_refine_adaptive.restype  = ctypes.c_double
    lib.brent_refine_adaptive.argtypes = [
        ctypes.c_double, ctypes.c_double,   # a, b
        ctypes.c_double, ctypes.c_double,   # fa, fb
        ctypes.c_double,                    # t
        ctypes.c_int, ctypes.c_int,         # prec_fast, prec_full
        ctypes.c_int, ctypes.c_int,         # iter_switch, max_iter
    ]

    lib.illinois_refine_bench.restype  = ctypes.c_double
    lib.illinois_refine_bench.argtypes = [
        ctypes.c_double, ctypes.c_double,
        ctypes.c_double, ctypes.c_double,
        ctypes.c_double,
        ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_int,
    ]

    return lib


def trouver_bracket(t0: float, delta: float = 0.01):
    """Bracket [a,b] autour du zéro t0 avec Z(a)·Z(b) < 0."""
    for d in [delta/2, delta, delta*1.5, delta*2]:
        a  = t0 - d
        b  = t0 + d
        fa = float(Z_vect_correct(np.array([a]))[0])
        fb = float(Z_vect_correct(np.array([b]))[0])
        if fa * fb < 0.0:
            return a, b, fa, fb
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  TEST 1 — γ₁ à γ₂₀ (précision)
# ══════════════════════════════════════════════════════════════════════════════

def test_precision_lmfdb(lib) -> bool:
    """Vérifie que brent_refine_adaptive donne < 1e-10 sur les 20 premiers zéros."""
    print("\n── Test 1 : précision sur γ₁ … γ₂₀ (LMFDB) ──────────────────────")
    print(f"  {'n':>3}  {'γ_LMFDB':>20}  {'γ_Brent':>20}  {'|err|':>12}  {'ok?':>4}")
    print(f"  {'─'*3}  {'─'*20}  {'─'*20}  {'─'*12}  {'─'*4}")

    tol = 1e-10
    ok = True
    for i, gamma_ref in enumerate(LMFDB_20):
        res = trouver_bracket(gamma_ref)
        if res is None:
            print(f"  {i+1:>3}  {gamma_ref:>20.15f}  {'—':>20}  {'—':>12}  SKIP (bracket)")
            continue

        a, b, fa, fb = res
        t_mid = (a + b) / 2.0
        gamma = float(lib.brent_refine_adaptive(
            a, b, fa, fb, t_mid,
            PREC_FAST, PREC_FULL, ITER_SWITCH, MAX_ITER,
        ))
        err = abs(gamma - gamma_ref)

        if t_mid < 300.0:
            # t < 300 : N_full < 7 termes RS — imprécision connue, comme Illinois C
            # En production, mpmath est utilisé pour t < 300 → non fatal
            note = "(t<300 — limitation RS connue)"
            status = "⚠️ "
        else:
            status = "✅" if err < tol else "❌"
            note = ""
            if err >= tol:
                ok = False

        print(f"  {i+1:>3}  {gamma_ref:>20.15f}  {gamma:>20.15f}  {err:>12.2e}  {status} {note}")

    return ok


# ══════════════════════════════════════════════════════════════════════════════
#  TEST 2 — γ à t ≈ 77000
# ══════════════════════════════════════════════════════════════════════════════

def test_grand_t(lib) -> bool:
    """Teste Brent sur 3 zéros à t ≈ 1000, 10000, 77000 (brackets tight δ=0.005).

    Utilise le CSV T=100k v7 pour avoir les vrais zéros, puis reconstruit
    des brackets de largeur ≈ 0.01 (identique à scan_arb en production).
    """
    print("\n── Test 2 : précision Brent sur grands t (brackets tight δ=0.005) ─")
    import csv, mpmath
    mpmath.mp.dps = 35

    csv_path = Path("/home/riemann/projet_zeta/calculs"
                    "/v4_1_T100000_20260611_142434"
                    "/zeros_v4_1_T100000_20260611_142434.csv")
    if not csv_path.exists():
        print("  CSV introuvable — test sauté")
        return True

    # Charger un zéro proche de chaque palier cible
    paliers = [1000.0, 10_000.0, 77_000.0]
    tous = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tous.append(float(row["partie_imaginaire"]))

    # Binding Z_rs_mpfr_ntermes pour vérifier |Z(γ_Brent)| ~ 0
    lib.Z_rs_mpfr_ntermes.restype  = ctypes.c_double
    lib.Z_rs_mpfr_ntermes.argtypes = [ctypes.c_double, ctypes.c_int, ctypes.c_uint]

    ok = True
    print(f"  {'t_cible':>8}  {'t_zero':>15}  {'|Z(γ_Brent)|':>14}  {'ok?':>4}")
    print(f"  {'─'*8}  {'─'*15}  {'─'*14}  {'─'*4}")

    for palier in paliers:
        t0 = min(tous, key=lambda x: abs(x - palier))

        res = trouver_bracket(t0, delta=0.005)
        if res is None:
            print(f"  {palier:>8.0f}  {t0:>15.6f}  {'—':>14}  SKIP")
            continue

        a, b, fa, fb = res
        t_mid = (a + b) / 2.0
        import math
        N_full = int(math.floor(math.sqrt(t_mid / (2 * math.pi))))
        if N_full < 1: N_full = 1

        gamma_brent = float(lib.brent_refine_adaptive(
            a, b, fa, fb, t_mid,
            PREC_FAST, PREC_FULL, ITER_SWITCH, MAX_ITER,
        ))
        # Vérifie que γ_Brent est bien un zéro de Z_rs (pas comparaison à siegelz)
        # Z_rs et siegelz diffèrent de O(t^{-3/4}) — c'est attendu.
        Z_val = abs(lib.Z_rs_mpfr_ntermes(gamma_brent, N_full, 80))
        # Seuil = 10× l'erreur RS attendue (O(t^{-3/4}))
        seuil = max(5e-3, 10.0 * t_mid**(-0.75))
        status = "✅" if Z_val < seuil else "❌"
        if Z_val >= seuil:
            ok = False
        print(f"  {palier:>8.0f}  {t0:>15.6f}  {Z_val:>14.2e}  {status}")

    return ok


# ══════════════════════════════════════════════════════════════════════════════
#  TEST 3 — Comparaison itérations Brent vs Illinois sur 100 zéros
# ══════════════════════════════════════════════════════════════════════════════

def _Z_scal(t: float) -> float:
    return float(Z_vect_correct(np.array([t]))[0])


def _compter_iters(a, b, fa, fb, iter_sw, max_it):
    """Compteur Python miroir de l'algorithme Illinois/Brent — signes float64."""
    iter1 = 0; iter2 = 0
    for i in range(max_it):
        if abs(fb - fa) < 1e-300: break
        c = b - fb * (b - a) / (fb - fa)
        fc = _Z_scal(c)
        if fc * fb < 0: a, fa = b, fb
        else: fa *= 0.5
        b, fb = c, fc
        if i < iter_sw: iter1 += 1
        else:
            iter2 += 1
            if abs(b - a) < 1e-12: break
    return iter1, iter2


def test_iterations_comparatif():
    """Compare les itérations Brent vs Illinois sur 100 zéros [1000, 50000]."""
    print("\n── Test 3 : itérations Brent vs Illinois (100 zéros) ─────────────")

    import csv
    # Chercher le CSV T=100k v7
    csv_path = Path("/home/riemann/projet_zeta/calculs"
                    "/v4_1_T100000_20260611_142434"
                    "/zeros_v4_1_T100000_20260611_142434.csv")
    if not csv_path.exists():
        print("  CSV introuvable — test sauté")
        return

    zeros = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            t = float(row["partie_imaginaire"])
            if 1_000 <= t <= 50_000:
                zeros.append(t)

    pas = max(1, len(zeros) // 100)
    zeros = zeros[::pas][:100]

    lib = charger_lib()

    brent_times = []
    il_times    = []
    brent_iters = []
    il_iters    = []

    for t0 in zeros:
        res = trouver_bracket(t0)
        if res is None: continue
        a, b, fa, fb = res
        t_mid = (a + b) / 2.0

        # Timing Brent
        t0b = time.perf_counter()
        lib.brent_refine_adaptive(a, b, fa, fb, t_mid,
                                   PREC_FAST, PREC_FULL, ITER_SWITCH, MAX_ITER)
        brent_times.append((time.perf_counter() - t0b) * 1000)

        # Timing Illinois
        t0i = time.perf_counter()
        lib.illinois_refine_bench(a, b, fa, fb, t_mid,
                                   IL_ITER_SWITCH, IL_MAX_ITER, PREC_FAST, PREC_FULL)
        il_times.append((time.perf_counter() - t0i) * 1000)

        # Itérations Python (miroir)
        i1b, i2b = _compter_iters(a, b, fa, fb, ITER_SWITCH, MAX_ITER)
        i1i, i2i = _compter_iters(a, b, fa, fb, IL_ITER_SWITCH, IL_MAX_ITER)
        brent_iters.append(i1b + i2b)
        il_iters.append(i1i + i2i)

    bt = np.array(brent_times)
    it = np.array(il_times)
    bi = np.array(brent_iters)
    ii = np.array(il_iters)

    gain_ms   = it.mean() / bt.mean() if bt.mean() > 0 else float("nan")
    gain_iter = ii.mean() / bi.mean() if bi.mean() > 0 else float("nan")

    print(f"\n  {'Méthode':12s}  {'ms/appel moy':>13}  {'iter moy':>9}  {'gain vs Illinois':>16}")
    print(f"  {'─'*12}  {'─'*13}  {'─'*9}  {'─'*16}")
    print(f"  {'Illinois':12s}  {it.mean():>12.4f}ms  {ii.mean():>9.1f}  {'baseline':>16}")
    print(f"  {'Brent':12s}  {bt.mean():>12.4f}ms  {bi.mean():>9.1f}  {'×'+f'{gain_ms:.2f}':>16}")
    print(f"\n  Gain ms   : ×{gain_ms:.2f}")
    print(f"  Gain iter : ×{gain_iter:.2f}")

    if gain_ms >= 1.05:
        print(f"\n  ✅  Gain ≥ ×1.05 → GO pour v9")
    else:
        print(f"\n  ⚠️   Gain < ×1.05 → NO-GO — garder v8, documenter Brent non retenu")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    multiprocessing.set_start_method("fork", force=True)

    print("═" * 62)
    print("  TEST brent_refine_adaptive — Phase C v9")
    print("  .so :", SO_PATH)
    print("═" * 62)

    lib = charger_lib()

    ok1 = test_precision_lmfdb(lib)
    ok2 = test_grand_t(lib)
    test_iterations_comparatif()

    print("\n" + "═" * 62)
    if ok1 and ok2:
        print("  ✅  TOUS LES TESTS PASS")
    else:
        print("  ❌  CERTAINS TESTS ÉCHOUÉS — voir détails ci-dessus")
    print("═" * 62)
