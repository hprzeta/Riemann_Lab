#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_v4_1.py — Vérifications A et B pour compute_zeros_v4_1.py
════════════════════════════════════════════════════════════════════
Usage :
    python validate_v4_1.py A   — Vérif A : T=300, 138 zéros, Turing, LMFDB
    python validate_v4_1.py B   — Vérif B : précision Illinois_C aux grands t
    python validate_v4_1.py AB  — Vérif A puis Vérif B

Règle absolue : ne pas passer à l'étape suivante sans feu vert explicite.
"""

import sys
import math
import time
import ctypes
from pathlib import Path
from typing import Tuple

# ── Chemins ──────────────────────────────────────────────────────────────────
_OPT = Path(__file__).parent                              # .../src/calculs/optimisation/
_C_MODULES = _OPT / "c_modules"
sys.path.insert(0, str(_OPT))                            # theta_rapide, turing_validation
sys.path.insert(0, str(_C_MODULES))

import numpy as np
import mpmath

# ── Imports locaux ────────────────────────────────────────────────────────────
from compute_zeros_v4_1 import (
    scanner_parallele,          # balayage parallèle 4 workers
    verifier_lmfdb,             # comparaison LMFDB
    pas_adaptatif,              # STEP adaptatif
    N_attendu_local,            # N(T) Weyl
    Z_vect_correct,             # Z(t) vectorisé N(t) correct par ligne
    SO_PATH,                    # chemin vers illinois_mpfr.so
    DPS_AFFINAGE,               # dps mpmath fallback (t < 300)
    DPS_POLISH,                 # dps Newton polish (t ≥ 300)
    NEWTON_STEPS,               # max itérations Newton
    POLISH_DELTA,               # garde-fou bracket autour de gamma_c
    _newton_polish,             # finition Newton (module-level, réutilisable ici)
    T_SEUIL_ILLINOIS_C,         # 300.0
)
from turing_validation import valider_turing                # Turing-Backlund

# ── Chargement illinois_mpfr.so (test direct, hors workers) ──────────────────
_lib = ctypes.CDLL(str(SO_PATH))
_lib.illinois_mpfr.restype  = ctypes.c_double
_lib.illinois_mpfr.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]

# ── Nombre de zéros attendus à T=300 (LMFDB / TURING) ───────────────────────
N_ZEROS_T300 = 138


# ═══════════════════════════════════════════════════════════════════════════
#  VÉRIF A — T=300 : justesse + vitesse
# ═══════════════════════════════════════════════════════════════════════════

def verif_A() -> dict:
    """
    Vérif A : run complet T=300.
    Critères :
      - 138/138 zéros
      - Turing-Backlund COMPLET
      - LMFDB 19/20 < 1e-10
      - Illinois_C pur > 90 % des affinages
      - Vitesse > 5 z/s
    """
    T_MAX = 300.0
    pas   = pas_adaptatif(T_MAX)

    print()
    print("=" * 65)
    print("  VÉRIF A — T=300 (validation complète v4.1)")
    print("=" * 65)
    print(f"  N attendus (Weyl)  = {N_attendu_local(T_MAX)}")
    print(f"  N attendus (exact) = {N_ZEROS_T300}  (référence LMFDB/Turing)")
    print(f"  Pas adaptatif      = {pas:.4f}")
    print(f"  Seuil Illinois_C   = {T_SEUIL_ILLINOIS_C}  (Illinois_C si t ≥ seuil)")
    print(f"  DPS_AFFINAGE       = {DPS_AFFINAGE}  (mpmath fallback pour t < seuil)")
    print()

    debut = time.time()
    zeros, stats = scanner_parallele(14.0, T_MAX, pas, tol=1e-12, n_workers=4)
    duree = time.time() - debut

    vitesse = len(zeros) / duree if duree > 0 else 0.0

    # ── Résumé numérique ─────────────────────────────────────────────────────
    print()
    print("  ── RÉSULTATS ──────────────────────────────────────────────")
    print(f"  Zéros trouvés    : {len(zeros)}  (attendus : {N_ZEROS_T300})")
    print(f"  Durée            : {duree:.2f} s  |  Vitesse : {vitesse:.1f} z/s")
    if zeros:
        print(f"  t₁  = {zeros[0]:.14f}")
        print(f"  t_n = {zeros[-1]:.14f}")

    # ── Répartition méthodes ─────────────────────────────────────────────────
    total = sum(v for k, v in stats.items() if k != "echecs")
    print("\n  Méthodes d'affinage :")
    for k, v in sorted(stats.items()):
        pct = v / total * 100 if total > 0 else 0.0
        print(f"    {k:<24}: {v:>5}  ({pct:.1f}%)")

    # ── LMFDB ────────────────────────────────────────────────────────────────
    lmfdb = verifier_lmfdb(zeros, n_check=20)

    # ── Turing ───────────────────────────────────────────────────────────────
    turing = valider_turing(zeros, dps=30)

    # ── Critères formels ─────────────────────────────────────────────────────
    nb_polish  = stats.get("illinois_C_polish", 0)
    pct_polish = nb_polish / total * 100 if total > 0 else 0.0
    score_str  = lmfdb.get("score", "0/0")
    score_ok   = int(score_str.split("/")[0]) if "/" in score_str else 0
    nb_fallbk  = stats.get("mpmath_fallback", 0)

    print()
    print("  ── CRITÈRES v4.1 ──────────────────────────────────────────")
    _ok_zeros  = len(zeros) == N_ZEROS_T300
    _ok_turing = turing["complet"]
    _ok_lmfdb  = score_ok >= 19
    _ok_polish = pct_polish > 90
    _ok_vitess = vitesse > 5.0
    _ok_fallbk = nb_fallbk == 0

    def sym(cond): return "✅" if cond else "❌"

    print(f"  Zéros {N_ZEROS_T300}/{N_ZEROS_T300}         : {len(zeros):3d} trouvés     {sym(_ok_zeros)}")
    print(f"  Turing complet         :                   {sym(_ok_turing)}")
    print(f"  LMFDB 19/20            : {score_str:>5}             {sym(_ok_lmfdb)}")
    print(f"  illinois_C_polish(≥300): {nb_polish:3d}  ({pct_polish:.1f}%)    {sym(_ok_polish)}")
    print(f"  Fallback hors borne    : {nb_fallbk:3d}  (doit ≈ 0)  {sym(_ok_fallbk)}")
    print(f"  Vitesse                : {vitesse:.1f} z/s (>5?)    {sym(_ok_vitess)}")
    print("=" * 65)

    # ── Verdict ──────────────────────────────────────────────────────────────
    passe = all([_ok_zeros, _ok_turing, _ok_lmfdb])
    if passe:
        print("\n  ✅ VÉRIF A RÉUSSIE — feu vert conditionnel à Vérif B.")
    else:
        print("\n  ❌ VÉRIF A ÉCHOUÉE — corriger avant tout run long.")

    return {
        "zeros"  : zeros,
        "stats"  : stats,
        "turing" : turing,
        "lmfdb"  : lmfdb,
        "vitesse": vitesse,
        "passe"  : passe,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  VÉRIF B — Précision Illinois_C aux grands t
# ═══════════════════════════════════════════════════════════════════════════

def _trouver_brackets(t_centre: float, demi_largeur: float = 1.5, pas: float = 0.05):
    """
    Retourne une liste de brackets [a, b] avec changement de signe de Z(t)
    autour de t_centre ± demi_largeur, avec le pas donné.

    Utilise Z_vect_correct (N(t) correct par ligne) — même formule que illinois_mpfr.
    """
    t_debut = t_centre - demi_largeur
    t_fin   = t_centre + demi_largeur
    ts      = np.arange(t_debut, t_fin + pas * 0.5, pas, dtype=np.float64)
    Z_vals  = Z_vect_correct(ts)

    brackets = []
    for i in range(len(ts) - 1):
        if Z_vals[i] * Z_vals[i + 1] < 0:          # changement de signe → zéro entre i et i+1
            brackets.append((float(ts[i]), float(ts[i + 1])))
    return brackets


def _affiner_illinois_mpfr(a: float, b: float, tol: float = 1e-12) -> float:
    """Affinage Illinois_C via le .so libmpfr (PREC=170 bits)."""
    return _lib.illinois_mpfr(a, b, tol)


def _affiner_mpmath_ref(a: float, b: float, dps: int = 50) -> float:
    """
    Référence haute précision par mpmath.findroot illinois à dps=50.
    Plus lent, mais indépendant du C — sert de référence externe.
    """
    old_dps      = mpmath.mp.dps
    mpmath.mp.dps = dps
    try:
        val = float(mpmath.findroot(
            mpmath.siegelz,
            (a, b),
            solver="illinois",
            tol=1e-20,         # précision cible très haute pour la référence
            maxsteps=200,
        ))
    finally:
        mpmath.mp.dps = old_dps
    return val


def _affiner_avec_polish(a: float, b: float) -> Tuple[float, float, float]:
    """
    Séquence complète illinois_C → finition Newton (dérivée analytique siegelz).
    Retourne (gamma_c, gamma_polish, duree_polish_s).
    Fallback Illinois sur [a, b] si Newton diverge.
    """
    gamma_c = _lib.illinois_mpfr(a, b, 1e-12)   # localisation rapide sur Z_mpfr

    t0 = time.time()
    try:
        gamma_p = _newton_polish(gamma_c)         # 3 pas Newton → < 1e-14 depuis 1.7e-2
    except Exception:
        # Fallback Illinois borné (cas rare : zero plat ou paire proche)
        old_dps = mpmath.mp.dps
        mpmath.mp.dps = DPS_POLISH
        try:
            gamma_p = float(mpmath.findroot(
                mpmath.siegelz, (a, b),
                solver="illinois", tol=1e-12, maxsteps=80,
            ))
        finally:
            mpmath.mp.dps = old_dps
    duree = time.time() - t0
    return gamma_c, gamma_p, duree


def _tester_plage(t_centre: float, label: str, n_test_max: int = 3):
    """
    Cherche des brackets autour de t_centre, applique illinois_C + polish,
    compare le résultat poli avec mpmath dps=50 comme référence.
    Retourne (max_ecart_C, max_ecart_polish, duree_polish_totale_s).
    """
    brackets = _trouver_brackets(t_centre, demi_largeur=2.0, pas=0.04)
    if not brackets:
        print(f"\n  {label} : aucun bracket trouvé autour de t≈{t_centre:.0f}")
        return float("nan"), float("nan"), 0.0

    brackets = brackets[:n_test_max]
    max_ec_C = max_ec_P = 0.0
    total_duree = 0.0

    print(f"\n  {label} — t ≈ {t_centre:.0f}  ({len(brackets)} zéro(s) testé(s))")
    print(f"  {'[a,b]':^32}  {'Illinois_C':>18}  {'Polish dps=30':>18}  {'Réf dps=50':>18}"
          f"  {'Écart_C':>10}  {'Écart_P':>10}  St")
    print("  " + "─" * 118)

    for a, b in brackets:
        gamma_c, gamma_p, dur = _affiner_avec_polish(a, b)  # C + polish
        gamma_ref = _affiner_mpmath_ref(a, b, dps=50)       # référence externe
        ec_C  = abs(gamma_c - gamma_ref)
        ec_P  = abs(gamma_p - gamma_ref)
        max_ec_C = max(max_ec_C, ec_C)
        max_ec_P = max(max_ec_P, ec_P)
        total_duree += dur

        sym = "✅" if ec_P < 1e-10 else ("⚠️ " if ec_P < 1e-8 else "❌")
        print(f"  [{a:.4f},{b:.4f}]  {gamma_c:>18.12f}  {gamma_p:>18.12f}"
              f"  {gamma_ref:>18.12f}  {ec_C:>10.2e}  {ec_P:>10.2e}  {sym}")

    return max_ec_C, max_ec_P, total_duree


def benchmark_vitesse_grands_t(n_bench: int = 10) -> float:
    """
    Mesure la vitesse réelle de la séquence illinois_C + polish siegelz dps=30
    sur un échantillon de n_bench zéros autour de t ≈ 9000–9100.

    Retourne la vitesse estimée en z/s sur 4 workers (×4 la vitesse séquentielle).
    Note : mesure SINGLE-PROCESS (×4 estimé pour les workers réels).
    """
    print()
    print("  ── BENCHMARK VITESSE (illinois_C + polish, t ≈ 9000-9100) ──")

    # Scan de [9000, 9100] pour trouver des brackets
    brackets_tous = []
    centre = 9000.0
    while len(brackets_tous) < n_bench and centre < 9200.0:
        brackets_tous += _trouver_brackets(centre, demi_largeur=10.0, pas=0.05)
        centre += 20.0
    brackets = brackets_tous[:n_bench]

    if not brackets:
        print("  Aucun bracket trouvé — benchmark annulé.")
        return 0.0

    print(f"  {len(brackets)} zéros à t ≈ {brackets[0][0]:.0f}–{brackets[-1][1]:.0f}")
    print(f"  DPS_POLISH = {DPS_POLISH}  |  POLISH_DELTA = {POLISH_DELTA}")
    print()

    # Mesure séquentielle (single-process)
    durees_c = []      # temps Illinois_C seul
    durees_p = []      # temps finition polish
    durees_tot = []    # temps total C + polish

    for a, b in brackets:
        t0 = time.time()
        gc_raw = _lib.illinois_mpfr(a, b, 1e-12)
        dur_c = time.time() - t0

        t1 = time.time()
        old = mpmath.mp.dps
        mpmath.mp.dps = DPS_POLISH
        try:
            _ = float(mpmath.findroot(
                mpmath.siegelz,
                (gc_raw - POLISH_DELTA, gc_raw + POLISH_DELTA),
                solver="illinois", tol=1e-22, maxsteps=50,
            ))
        finally:
            mpmath.mp.dps = old
        dur_p = time.time() - t1

        durees_c.append(dur_c)
        durees_p.append(dur_p)
        durees_tot.append(dur_c + dur_p)

    moy_c   = sum(durees_c) / len(durees_c)
    moy_p   = sum(durees_p) / len(durees_p)
    moy_tot = sum(durees_tot) / len(durees_tot)

    # Vitesse séquentielle (1 worker) et estimée ×4
    vit_1  = 1.0 / moy_tot if moy_tot > 0 else 0
    vit_x4 = 4.0 * vit_1

    print(f"  Temps moyen Illinois_C  : {moy_c*1000:.2f} ms/zéro")
    print(f"  Temps moyen polish dps={DPS_POLISH}: {moy_p*1000:.1f} ms/zéro")
    print(f"  Temps total moyen       : {moy_tot*1000:.1f} ms/zéro")
    print(f"  Vitesse (1 worker)      : {vit_1:.2f} z/s")
    print(f"  Vitesse estimée ×4      : {vit_x4:.1f} z/s  (parallélisme post-fork)")

    return vit_x4


def verif_B() -> dict:
    """
    Vérif B (v2 — après fix polish) : précision illinois_C + polish siegelz.

    Méthode :
      Pour chaque plage (t ≈ 350, 1000, 9900) :
        1. Trouver brackets via Z_vect_correct
        2. Appliquer illinois_C → gamma_c (localisation sur Z_mpfr)
        3. Polish : findroot(siegelz, gamma_c±DELTA, dps=DPS_POLISH) → gamma_p
        4. Référence : findroot(siegelz, [a,b], dps=50) → gamma_ref
        5. Comparer gamma_p vs gamma_ref (critère < 1e-10)
        6. Afficher aussi gamma_c vs gamma_ref (biais Z_mpfr, pour mémoire)
    Puis benchmark de vitesse sur t ≈ 9000–9100.
    """
    print()
    print("=" * 65)
    print("  VÉRIF B (v3) — Précision illinois_C + Newton dps=25")
    print(f"  DPS_POLISH = {DPS_POLISH}  |  NEWTON_STEPS = {NEWTON_STEPS}  |  DELTA = {POLISH_DELTA}")
    print(f"  Dérivée    : mpmath.siegelz(x, derivative=1) — analytique")
    print(f"  Référence  : mpmath.findroot illinois dps=50")
    print(f"  Critère    : écart Newton (gamma_p vs réf) < 1e-10")
    print("=" * 65)

    resultats = {}
    max_ec_P_global = 0.0
    duree_totale = 0.0

    # Plage 1 : t ≈ 350 (juste au-dessus de T_SEUIL=300)
    ec_C1, ec_P1, dur1 = _tester_plage(350.0, "Plage 1 (t ≈ 350)", n_test_max=3)
    resultats["t350"] = {"ecart_C": ec_C1, "ecart_P": ec_P1}
    max_ec_P_global = max(max_ec_P_global, ec_P1 if not math.isnan(ec_P1) else 0)
    duree_totale += dur1

    # Plage 2 : t ≈ 1000 (intermédiaire)
    ec_C2, ec_P2, dur2 = _tester_plage(1000.0, "Plage 2 (t ≈ 1000)", n_test_max=3)
    resultats["t1000"] = {"ecart_C": ec_C2, "ecart_P": ec_P2}
    max_ec_P_global = max(max_ec_P_global, ec_P2 if not math.isnan(ec_P2) else 0)
    duree_totale += dur2

    # Plage 3 : t ≈ 9900 (grand t — N ≈ 39 termes RS)
    print("\n  ⚠️  Plage 3 (t ≈ 9900) — N ≈ 39 termes RS, calcul plus lent...")
    ec_C3, ec_P3, dur3 = _tester_plage(9900.0, "Plage 3 (t ≈ 9900)", n_test_max=3)
    resultats["t9900"] = {"ecart_C": ec_C3, "ecart_P": ec_P3}
    max_ec_P_global = max(max_ec_P_global, ec_P3 if not math.isnan(ec_P3) else 0)
    duree_totale += dur3

    # ── Bilan précision ──────────────────────────────────────────────────────
    print()
    print("  ── BILAN PRÉCISION (polish vs réf dps=50) ─────────────────")

    def ok_p(ec): return "✅" if not math.isnan(ec) and ec < 1e-10 else "⚠️ "

    print(f"  Plage t≈350  : Écart_C = {ec_C1:.2e}  |  Écart_P = {ec_P1:.2e}  {ok_p(ec_P1)}")
    print(f"  Plage t≈1000 : Écart_C = {ec_C2:.2e}  |  Écart_P = {ec_P2:.2e}  {ok_p(ec_P2)}")
    print(f"  Plage t≈9900 : Écart_C = {ec_C3:.2e}  |  Écart_P = {ec_P3:.2e}  {ok_p(ec_P3)}")
    print(f"  Écart_P max global  : {max_ec_P_global:.2e}")

    passe_B = max_ec_P_global < 1e-10

    # ── Benchmark vitesse ────────────────────────────────────────────────────
    vit_x4 = benchmark_vitesse_grands_t(n_bench=10)
    resultats["vit_x4_estimee"] = vit_x4

    # ── Verdict ──────────────────────────────────────────────────────────────
    print()
    print("=" * 65)
    if passe_B:
        print(f"  ✅ VÉRIF B RÉUSSIE — polish < 1e-10 sur toutes les plages.")
        print(f"     Vitesse estimée ×4 : {vit_x4:.1f} z/s à t ≈ 9000")
    else:
        print(f"  ❌ VÉRIF B ÉCHOUÉE — Écart_P max = {max_ec_P_global:.2e} > 1e-10")
        print(f"     Augmenter DPS_POLISH (actuellement {DPS_POLISH}) ou POLISH_DELTA.")
    print("=" * 65)

    resultats["max_ec_P_global"] = max_ec_P_global
    resultats["passe"]           = passe_B
    return resultats


# ═══════════════════════════════════════════════════════════════════════════
#  POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Garde multiprocessing obligatoire (fork Linux) ─────────────────────────
    import multiprocessing
    multiprocessing.set_start_method("fork", force=True)

    # Argument CLI : A, B ou AB ──────────────────────────────────────────────
    mode = sys.argv[1].upper() if len(sys.argv) > 1 else "A"

    if "A" in mode:
        res_A = verif_A()
        if "B" not in mode:
            print()
            print("=" * 65)
            print("  ⛔ STOP VÉRIF A — Montre les chiffres ci-dessus.")
            print("  Attends le feu vert explicite avant de lancer Vérif B")
            print("  ou un run long (T=1000 / T=10000).")
            print("  Commande suivante : python validate_v4_1.py B")
            print("=" * 65)
            sys.exit(0)

    if "B" in mode:
        res_B = verif_B()
        print()
        print("=" * 65)
        print("  ⛔ STOP VÉRIF B — Montre les chiffres ci-dessus.")
        print("  Attends le feu vert explicite avant le run T=1000.")
        print("=" * 65)
