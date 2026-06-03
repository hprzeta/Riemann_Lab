#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_v4_1_T300.py — Point d'arrêt N°2 : run T=300, comparaison vs v5 validé

Référence v5 (commit b8018c0, run 2026-05-29) :
    Zéros     : 138
    Turing    : COMPLET (0 manquant)
    LMFDB     : 19/20 à < 10⁻¹⁰
    Illinois_C pur : 100%
    Vitesse   : ~1 z/s (goulot mpmath.siegelz séquentiel)

Objectif v4.1 :
    Mêmes résultats de validation + vitesse > 5 z/s (cible 15-20 z/s)

Auteur : hprzeta — 2026-05-31
"""

import sys
import time
from pathlib import Path

# Configuration des chemins
_OPT_DIR   = Path(__file__).parent
_C_MOD_DIR = _OPT_DIR / "c_modules"
sys.path.insert(0, str(_OPT_DIR))
sys.path.insert(0, str(_C_MOD_DIR))

from compute_zeros_v4_1 import (
    scanner_parallele,
    pas_adaptatif,
    N_attendu_local,
    verifier_lmfdb,
)
from turing_validation import valider_turing

# ── Paramètres du run ───────────────────────────────────────────────────────
T_MIN = 14.0
T_MAX = 300.0
pas   = pas_adaptatif(T_MAX)         # STEP = min(2π/(5·ln(T/2π)), 0.10) = 0.10
TOL   = 1e-12
N_WORKERS = 4

# Référence v5 pour comparaison
REF_V5 = {
    "zeros"     : 138,
    "turing"    : True,
    "lmfdb_ok"  : 19,
    "lmfdb_tot" : 20,
}


def main():
    print()
    print("=" * 65)
    print("  POINT D'ARRÊT N°2 — Run T=300 comparaison v4.1 vs v5")
    print("=" * 65)
    print(f"  T_MAX          = {T_MAX}")
    print(f"  Pas balayage   = {pas:.4f}")
    print(f"  N attendus     ≈ {N_attendu_local(T_MAX)}")
    print(f"  Workers        = {N_WORKERS}")
    print()
    print("  Référence v5 (run validé b8018c0) :")
    print(f"    Zéros     : {REF_V5['zeros']}")
    print(f"    Turing    : COMPLET")
    print(f"    LMFDB     : {REF_V5['lmfdb_ok']}/{REF_V5['lmfdb_tot']}")
    print()

    # ── Run v4.1 ──────────────────────────────────────────────────────────────
    debut = time.time()
    zeros, stats = scanner_parallele(T_MIN, T_MAX, pas, TOL, N_WORKERS)
    duree = time.time() - debut

    vitesse = len(zeros) / duree if duree > 0 else 0

    # ── Résultats bruts ────────────────────────────────────────────────────────
    print()
    print("=" * 65)
    print("  RÉSULTATS v4.1 — T=300")
    print("=" * 65)
    print(f"  Zéros trouvés   : {len(zeros)}")
    print(f"  Attendus (Weyl) : {N_attendu_local(T_MAX)}")
    print(f"  Durée           : {duree:.1f}s")
    print(f"  Vitesse         : {vitesse:.1f} z/s")
    print()
    print("  Méthodes d'affinage :")
    total = sum(v for k, v in stats.items() if k != "echecs")
    for methode, nb in sorted(stats.items()):
        pct = nb / total * 100 if total > 0 else 0
        print(f"    {methode:<24} : {nb:>5}  ({pct:.1f}%)")
    if zeros:
        print(f"\n  t₁  = {zeros[0]:.12f}")
        print(f"  t_n = {zeros[-1]:.12f}")

    # ── Validation LMFDB ──────────────────────────────────────────────────────
    resultats_lmfdb = verifier_lmfdb(zeros, n_check=20)

    # ── Validation Turing ─────────────────────────────────────────────────────
    resultats_turing = valider_turing(zeros, dps=30)

    # ── Comparaison v4.1 vs v5 ────────────────────────────────────────────────
    lmfdb_s   = resultats_lmfdb.get("score", "0/0").split("/")
    lmfdb_ok  = int(lmfdb_s[0]) if len(lmfdb_s) == 2 else 0
    lmfdb_tot = int(lmfdb_s[1]) if len(lmfdb_s) == 2 else 0
    turing_ok = resultats_turing.get("complet", False)

    nb_pur  = stats.get("Illinois_C", 0)
    pct_pur = nb_pur / total * 100 if total > 0 else 0

    print()
    print("=" * 65)
    print("  COMPARAISON v4.1 vs v5 (référence b8018c0)")
    print("=" * 65)
    print(f"  {'Critère':<28} {'v5 (ref)':>10}  {'v4.1':>10}  {'OK?':>6}")
    print("  " + "─" * 59)

    # Nombre de zéros
    zeros_ok = abs(len(zeros) - REF_V5["zeros"]) <= 2   # tolérance ±2
    print(f"  {'Zéros trouvés':<28} {REF_V5['zeros']:>10}  {len(zeros):>10}  "
          + ("✅" if zeros_ok else "⚠️ "))

    # Turing
    print(f"  {'Turing COMPLET':<28} {'✅':>10}  "
          + (f"{'✅':>10}" if turing_ok else f"{'❌':>10}")
          + f"  {'✅' if turing_ok else '❌'}")

    # LMFDB
    lmfdb_ref_ok = lmfdb_ok >= REF_V5["lmfdb_ok"]
    print(f"  {'LMFDB à < 10⁻¹⁰':<28} {REF_V5['lmfdb_ok']:>4}/{REF_V5['lmfdb_tot']:<5}  "
          + f"{lmfdb_ok:>4}/{lmfdb_tot:<5}  "
          + ("✅" if lmfdb_ref_ok else "⚠️ "))

    # Illinois_C pur
    pur_ok = pct_pur > 90.0
    print(f"  {'Illinois_C pur (%)':<28} {'~87-100':>10}  {pct_pur:>9.1f}%  "
          + ("✅" if pur_ok else "⚠️ "))

    # Vitesse
    print(f"  {'Vitesse (z/s)':<28} {'~1':>10}  {vitesse:>9.1f}  "
          + ("✅" if vitesse > 5.0 else "⚠️ (< 5 z/s)"))

    print()
    succes = zeros_ok and turing_ok and lmfdb_ref_ok
    if succes:
        print("  ✅ VALIDATION v4.1 RÉUSSIE — résultats conformes à v5")
    else:
        print("  ⚠️  VALIDATION v4.1 PARTIELLE — vérifier les critères ⚠️")

    print()
    print("  STOP — Attente du feu vert avant tout run plus long.")
    print("=" * 65)


if __name__ == "__main__":
    main()
