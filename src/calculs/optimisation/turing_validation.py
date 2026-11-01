#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
turing_validation.py — Validation rigoureuse par le critère de Turing-Backlund
═══════════════════════════════════════════════════════════════════════════════
Implémente la méthode de comptage N(T) pour prouver qu'aucun zéro n'a été
omis lors du calcul. C'est le test de complétude manquant dans la v2.

THÉORIE — FORMULE DE RIEMANN–VON MANGOLDT (exacte)
════════════════════════════════════════════════════
Le nombre de zéros non triviaux ρ = β + iγ avec 0 < γ ≤ T est :

    N(T) = θ(T)/π + 1 + S(T)

où :
    θ(T) = Im[ ln Γ(¼ + iT/2) ] − (T/2)·ln π      (phase de Riemann-Siegel)
    S(T) = (1/π) · arg ζ(½ + iT)                   (variation de l'argument)

La valeur θ(T)/π + 1 donne le nombre "attendu" (entier le plus proche).
S(T) est une correction entière bornée : |S(T)| ≤ C·log T / log log T.

EN PRATIQUE — MÉTHODE DE BACKLUND (1914)
─────────────────────────────────────────
S(T) = (1/π) · [arg ζ(σ + iT)]_{σ=+∞}^{σ=1/2}

On calcule la variation de l'argument de ζ en suivant le chemin
horizontal de σ=∞ à σ=½ le long de Im(s) = T.

Pour σ → ∞ : ζ(σ+iT) → 1, donc arg = 0.
Pour σ = ½ : on obtient arg ζ(½+iT) par intégration numérique.

Algorithme :
    1. Calculer θ(T)/π + 1  (formule de Riemann-von Mangoldt, partie fractionnaire CONSERVÉE)
    2. Calculer S(T) = arg ζ(½+iT) / π
    3. N(T) = round( θ(T)/π + 1 + S(T) )   [corrigé le 01/11/2026 : l'ancienne version tronquait θ/π]
    4. Comparer avec le nombre de zéros calculés : si égal → COMPLET ✅

CRITÈRE DE TURING (1953)
─────────────────────────
Turing a montré que si les zéros calculés vérifient :
    ∀ T_k ∈ liste, Z(T_k−ε)·Z(T_k+ε) < 0  (vrai changement de signe)
    et N(T_max) = #{t_n ≤ T_max}
alors aucun zéro n'a été omis dans [0, T_max].

RÉFÉRENCE
─────────
    A.M. Turing, "Some calculations of the Riemann zeta-function" (1953)
    R. Backlund, "Sur les zéros de la fonction ζ(s)" (1914)
    J.B. Rosser & L. Schoenfeld, "Approximate formulas for some functions
    of prime numbers" (1962)

Auteur : hprzeta — Projet Hypothèse de Riemann
Date   : 2026
"""

import math
import numpy as np
from mpmath import mp, mpc, mpf, zeta, loggamma, arg, re, im, pi, log

# ─── Importer theta depuis le module optimisation ─────────────────────────────
try:
    from theta_rapide import theta_fast
except ImportError:
    # Fallback si theta_rapide.py n'est pas dans le même dossier
    def theta_fast(t: float) -> float:
        mp.dps = 35
        return float(
            mp.im(loggamma(mpf("0.25") + mpc(0, t) / 2))
            - (t / 2) * mp.log(mp.pi)
        )


# ─── 1. Comptage théorique N_attendu(T) ──────────────────────────────────────

def N_attendu(T: float) -> float:
    """
    Estimation continue de N(T) par la formule de Riemann-von Mangoldt :

        N(T) ≈ θ(T)/π + 1

    Remarque : cette formule donne un réel, pas un entier.
    La valeur exacte est ⌊θ(T)/π + 1⌋ + S(T) avec S(T) entier.

    Paramètre
    ---------
    T : float — borne supérieure

    Retourne
    --------
    float — estimation continue (prendre floor() pour l'entier)
    """
    return theta_fast(T) / math.pi + 1.0


def N_entier_attendu(T: float) -> int:
    """
    Nombre de zéros attendus dans la bande 0 < Im(ρ) ≤ T.
    Formule exacte : ⌊θ(T)/π⌋ + 1 (sans la correction S(T)).
    """
    return math.floor(theta_fast(T) / math.pi) + 1


def N_asymptotique(T: float) -> int:
    """
    Estimation rapide de N(T) via la formule de Weyl (premier terme) :

        N(T) ≈ (T/2π)·ln(T/2πe)

    Moins précis que N_entier_attendu, mais O(1) sans mpmath.
    Utile pour estimer le nombre de zéros avant de lancer le calcul.
    """
    if T < 14.0:
        return 0
    return int(T / (2 * math.pi) * math.log(T / (2 * math.pi * math.e)))


# ─── 2. Calcul de S(T) — correction par variation de l'argument ──────────────

def S_T(T: float, n_sigma: int = 50, dps: int = 35) -> float:
    """
    S(T) = (1/π) · arg ζ(½ + iT)

    Méthode : variation de l'argument de ζ le long de Im(s) = T
    de Re(s) = σ_max → Re(s) = ½, par pas discrets.

    La variation est calculée en sommant les incréments d'argument :
        ΔArg = Im( ln ζ(σ_k + iT) − ln ζ(σ_{k−1} + iT) )

    Paramètres
    ----------
    T       : float — valeur de t
    n_sigma : int   — nombre de points σ entre ½ et σ_max (défaut 50)
    dps     : int   — précision mpmath

    Retourne
    --------
    float — S(T) (typiquement |S(T)| < 3 pour T < 10⁶)
    """
    _dps_save = mp.dps
    mp.dps = dps

    sigma_max  = 3.0          # ζ(3+iT) ≈ 1, arg ≈ 0
    sigmas     = np.linspace(sigma_max, 0.5, n_sigma + 1)

    variation  = 0.0
    arg_prev   = 0.0          # arg ζ(σ_max + iT) ≈ 0

    for sigma in sigmas[1:]:
        s       = mpc(sigma, T)
        z       = zeta(s)
        # arg courant — on suit la variation continue (évite les sauts de 2π)
        arg_cur = float(mp.atan2(im(z), re(z)))

        # Correction de branche : on choisit la valeur la plus proche
        d = arg_cur - arg_prev
        if d > math.pi:
            arg_cur -= 2 * math.pi
        elif d < -math.pi:
            arg_cur += 2 * math.pi

        variation += arg_cur - arg_prev
        arg_prev   = arg_cur

    mp.dps = _dps_save
    return variation / math.pi


# ─── 3. N(T) exact ────────────────────────────────────────────────────────────

def N_exact(T: float, dps: int = 35) -> int:
    """
    Calcule N(T) exact = round( θ(T)/π + 1 + S(T) ).

    C'est le nombre vrai de zéros non triviaux de ζ avec 0 < Im(ρ) ≤ T.

    CORRECTION du 01/11/2026 : l'ancienne formule ⌊θ(T)/π⌋ + 1 + round(S(T)) était FAUSSE de -1
    dès que la partie fractionnaire de θ(T)/π dépasse 0,5 (θ/π + 1 + S est un entier, donc
    round(S) retire 1 dans ce cas). Constaté sur 10 milieux de zéros sur 19 et à T = 2774,67 ;
    10933,33. Voir tests_turing/test_turing_validation.py.

    ATTENTION : N(T) est discontinue en chaque zéro. Évaluer N_exact(T) pour T = la valeur
    stockée d'un zéro donne N ou N-1 selon que cette valeur est au-dessus ou au-dessous du vrai zéro.

    Paramètres
    ----------
    T   : float — borne
    dps : int   — précision mpmath pour θ(T) et S(T)

    Retourne
    --------
    int — N(T)
    """
    _dps_save = mp.dps
    mp.dps = dps
    try:
        theta_sur_pi = mp.siegeltheta(mp.mpf(T)) / mp.pi      # θ(T)/π en haute précision, partie fractionnaire conservée
        S            = S_T(T, dps=dps)                        # S(T) = arg ζ(½+iT)/π
        return int(mp.nint(theta_sur_pi + 1 + S))             # θ/π + 1 + S est un entier : on arrondit la SOMME
    finally:
        mp.dps = _dps_save


# ─── 4. Validation de Turing ─────────────────────────────────────────────────

# Décalage des points de contrôle (ajouté le 01/11/2026).
# Les points de contrôle sont des zéros DE LA LISTE ; or N(T) est discontinue en chaque zéro : évaluée
# exactement sur la valeur stockée d'un zéro, elle vaut N ou N-1 selon que cette valeur est au-dessus ou
# au-dessous du vrai zéro (erreur de position de l'ordre de 1e-12 à 1e-9) -> « SURPLUS +1 » factices.
# On évalue donc à T + EPS_CONTROLE, dans l'intervalle ouvert qui suit le zéro de contrôle.
# 1e-4 : très supérieur aux erreurs de position (≤ 6e-9 mesuré, 1,7e-6 pour la V16 d'avant le second pas de
# Newton) et très inférieur au plus petit écart observé entre deux zéros (0,0147 jusqu'à t = 1e5).
EPS_CONTROLE = 1e-4


def valider_turing(zeros_calcules: list, dps: int = 35, eps_controle: float = EPS_CONTROLE) -> dict:
    """
    Vérifie que le calcul est complet par le critère de Turing-Backlund.

    Pour chaque point de contrôle T (un zéro de la liste), évalué à T_eval = T + eps_controle :
        n_calcules(T_eval) = #{t_n ≤ T_eval dans la liste}
        N_exact(T_eval)    = nombre vrai de zéros
        → Complet si n_calcules == N_exact

    Paramètres
    ----------
    zeros_calcules : list of float — les t_n calculés, triés
    dps            : précision mpmath
    eps_controle   : décalage au-dessus du zéro de contrôle (0 = ancien comportement, instable : N(T)
                     est discontinue en un zéro)

    Retourne
    --------
    dict avec :
        "complet"        : bool — True si aucun zéro manquant
        "verifications"  : list de dict par point de contrôle
        "manquants_total": int — nombre total de zéros manquants
    """
    if not zeros_calcules:
        return {"complet": False, "verifications": [], "manquants_total": -1}

    zeros = sorted(zeros_calcules)
    T_max = zeros[-1]

    # Points de contrôle : 10%, 25%, 50%, 75%, 100% de T_max
    T_checks = [
        zeros[max(0, len(zeros) // 10 - 1)],
        zeros[max(0, len(zeros) // 4 - 1)],
        zeros[max(0, len(zeros) // 2 - 1)],
        zeros[max(0, 3 * len(zeros) // 4 - 1)],
        T_max
    ]
    # Ajouter quelques T ronds si disponibles
    T_checks = sorted(set(T_checks))

    print(f"\n{'─'*70}")
    print(f"  VALIDATION TURING-BACKLUND")
    print(f"  {len(zeros)} zéros calculés, T_max = {T_max:.2f}")
    print(f"{'─'*70}")
    print(f"  {'T':>10}  {'Calculés':>10}  {'Attendus':>10}  {'Manquants':>10}  Statut")
    print(f"  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*10}")

    verifications   = []
    complet         = True

    for T in T_checks:
        T_eval    = T + eps_controle                       # juste AU-DESSUS du zéro de contrôle (voir EPS_CONTROLE)
        n_calc    = sum(1 for t in zeros if t <= T_eval)
        n_attendu = N_exact(T_eval, dps=dps)
        delta     = n_attendu - n_calc   # positif = manque, négatif = surplus

        if delta == 0:
            statut = "✅ OK"
            ok     = True
        elif delta > 0:
            # Vrais zéros manqués — le calcul est incomplet
            statut = f"❌ MANQUE {delta}"
            ok     = False
            complet = False
        else:
            # Plus de zéros que prévu. Depuis les corrections du 01/11/2026 (N_exact et évaluation à T + EPS),
            # un surplus n'est plus un artefact : c'est un DOUBLON RÉEL probable (même zéro compté deux fois,
            # p. ex. fusion de segments) ou un décalage de la liste : à examiner. Il n'est pas compté comme manque.
            # Historique : ces surplus étaient attribués à tort au « chevauchement des workers ».
            statut = f"⚠️  SURPLUS +{abs(delta)}"
            ok     = True   # un surplus n'est PAS un zéro manqué

        print(f"  {T:>10.2f}  {n_calc:>10d}  {n_attendu:>10d}  {delta:>+10d}  {statut}")

        verifications.append({
            "T": T, "T_eval": T_eval, "calcules": n_calc, "attendus": n_attendu,
            "delta": delta, "ok": ok, "statut": statut
        })

    # Déficit net = delta au dernier checkpoint (T_max).
    # NE PAS sommer les deltas intermédiaires : ils sont cumulatifs et
    # compteraient les mêmes zéros manquants plusieurs fois (bug historique).
    manquants_total = verifications[-1]["delta"] if verifications else 0

    print(f"{'─'*70}")
    if complet:
        print(f"  ✅  COMPLET — aucun zéro manquant dans [0, {T_max:.2f}]")
        if any(v["delta"] < 0 for v in verifications):
            n_surplus = sum(abs(v["delta"]) for v in verifications if v["delta"] < 0)
            print(f"  ℹ️   Surplus total : {n_surplus} zéro(s) supplémentaires")
            print(f"       (à examiner : doublon réel probable ; depuis le 01/11/2026 ce n'est plus un artefact de N(T))")
    else:
        print(f"  ❌  INCOMPLET — {manquants_total} zéro(s) manquant(s)")
        print(f"       → Relancer avec STEP plus petit")
    print(f"{'─'*70}\n")

    return {
        "complet":         complet,
        "verifications":   verifications,
        "manquants_total": manquants_total
    }


# ─── 5. Rapport CSV des vérifications ─────────────────────────────────────────

def exporter_rapport(resultats: dict, chemin: str = "validation_turing.csv"):
    """Exporte le rapport de validation en CSV."""
    import pandas as pd
    df = pd.DataFrame(resultats["verifications"])
    df.to_csv(chemin, index=False)
    print(f"  📄 Rapport exporté : {chemin}")


# ─── Point d'entrée ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("─── Test turing_validation.py ───\n")

    # 1. Tests unitaires sur N(T)
    test_cases = [
        (100,   29),
        (500,   182),
        (1000,  396),
        (10000, 10142),   # notre résultat v2
    ]
    print("  Formule de Riemann-von Mangoldt N(T) :")
    print(f"  {'T':>8}  {'N_asympt':>10}  {'N_entier':>10}  {'N_ref':>8}")
    print("  " + "─" * 44)
    for T, n_ref in test_cases:
        n_as = N_asymptotique(T)
        n_en = N_entier_attendu(T)
        print(f"  {T:>8.0f}  {n_as:>10d}  {n_en:>10d}  {n_ref:>8d}")

    # 2. Test S(T) sur quelques valeurs connues
    print("\n  S(T) pour quelques valeurs (doit être proche de 0 ou ±1) :")
    for T in [100.0, 500.0, 1000.0]:
        s = S_T(T, dps=30)
        print(f"    S({T:.0f}) = {s:.4f}")

    # 3. Simulation : on charge les zéros du CSV si disponible
    import os
    csv_path = "zeros_zeta_T10000_20260424_205325.csv"
    if os.path.exists(csv_path):
        import pandas as pd
        df     = pd.read_csv(csv_path)
        zeros  = df["partie_imaginaire"].tolist()
        print(f"\n  Chargé : {len(zeros)} zéros depuis {csv_path}")
        resultats = valider_turing(zeros, dps=30)
    else:
        # Test avec les 10 premiers zéros connus
        zeros_test = [
            14.134725141734693, 21.022039638771555, 25.010857580145688,
            30.424876125859513, 32.935061587739189, 37.586178158825671,
            40.918719012147495, 43.327073280914999, 48.005150881167159,
            49.773832477672302
        ]
        print(f"\n  Test avec {len(zeros_test)} premiers zéros de référence LMFDB")
        resultats = valider_turing(zeros_test, dps=30)

    print("  Résultat final :", "COMPLET ✅" if resultats["complet"] else "INCOMPLET ❌")
