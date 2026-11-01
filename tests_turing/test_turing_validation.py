# -*- coding: utf-8 -*-
"""
Tests de `N_exact` (turing_validation.py) contre une référence indépendante : les zéros LMFDB
et `mpmath.nzeros`. Aucun calcul de zéros de production ; quelques secondes.

Lancement :  zeta_env/bin/python3 -B -I tests_turing/test_turing_validation.py

HISTORIQUE (01/11/2026) — DÉFAUT RÉEL de `N_exact` :
  l'ancienne formule  ⌊θ(T)/π⌋ + 1 + round(S(T))  est fausse de -1 dès que la partie fractionnaire de
  θ(T)/π dépasse 0,5 (θ/π + 1 + S est un entier, donc round(S) retire 1 dans ce cas).
  Constaté : 10 milieux de zéros sur 19 faux, et T = 2774,67 ; 10933,33 (fraction 0,813 ; 0,823).
  Conséquence : des « SURPLUS +1/+2 » factices dans le journal, et un test aveugle à un zéro manquant
  aux points concernés. Formule correcte :  N(T) = round(θ(T)/π + 1 + S(T)).
  Chaque T de ces tests est choisi ENTRE deux zéros (jamais sur un zéro : N(T) y est discontinue).
"""
import contextlib
import io
import os
import sys
import unittest

sys.dont_write_bytecode = True   # aucun .pyc dans le dépôt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "calculs", "optimisation"))

import mpmath                                  # référence indépendante (nzeros, siegeltheta)
from turing_validation import N_exact, valider_turing    # fonctions testées

# 20 premiers zéros (LMFDB) : le n-ième milieu (γ_n + γ_{n+1})/2 a exactement n zéros en dessous
LMFDB_20 = [14.134725141734693, 21.022039638771555, 25.010857580145688, 30.424876125859513,
            32.935061587739189, 37.586178158825671, 40.918719012147495, 43.327073280914999,
            48.005150881167159, 49.773832477672302, 52.970321477714464, 56.446247697063392,
            59.347044003113822, 60.831778524609810, 65.112544048081659, 67.079810529494168,
            69.546401711173985, 72.067157674481905, 75.704690699083926, 77.144840068874799]

# Hautes hauteurs : T posé 1e-4 AU-DESSUS d'un zéro de la liste du run distribué T=20000 du 01/11/2026
# (zéros n° 2249, 5622, 11245 ; écarts au zéro voisin ≥ 0,43) ; compte attendu = mpmath.nzeros
HAUTES = [(2774.6701, 2249), (6021.0786, 5622), (10933.3262, 11245)]


def frac_theta(T, dps=30):
    """Partie fractionnaire de θ(T)/π (θ de Riemann–Siegel, mpmath)."""
    mpmath.mp.dps = dps
    x = mpmath.siegeltheta(mpmath.mpf(T)) / mpmath.pi
    return float(x - mpmath.floor(x))


class TestNExact(unittest.TestCase):

    def test_milieux_des_20_premiers_zeros(self):
        """N_exact(milieu entre γ_n et γ_{n+1}) = n, pour n = 1..19 (les deux côtés de frac(θ/π) = 0,5)."""
        fracs = []
        for n in range(1, 20):
            T = (LMFDB_20[n - 1] + LMFDB_20[n]) / 2.0
            fracs.append(frac_theta(T))
            with self.subTest(n=n, T=round(T, 4), frac=round(fracs[-1], 3)):
                self.assertEqual(N_exact(T, dps=30), n)
        # le jeu de test doit exercer les deux cas (sinon il ne protège pas du défaut)
        self.assertTrue(any(f > 0.5 for f in fracs) and any(f < 0.5 for f in fracs))

    def test_hautes_hauteurs_contre_mpmath_nzeros(self):
        """N_exact = mpmath.nzeros = compte attendu, avec frac(θ/π) à 0,81 ; 0,35 ; 0,82."""
        fracs = []
        for T, attendu in HAUTES:
            fracs.append(frac_theta(T))
            mpmath.mp.dps = 30
            with self.subTest(T=T, frac=round(fracs[-1], 3)):
                self.assertEqual(int(mpmath.nzeros(T)), attendu)     # la référence elle-même
                self.assertEqual(N_exact(T, dps=30), attendu)
        self.assertTrue(any(f > 0.5 for f in fracs) and any(f < 0.5 for f in fracs))


def valider_sans_bruit(zeros, **kw):
    """valider_turing affiche un tableau : on le capture, on ne garde que le dictionnaire retourné."""
    with contextlib.redirect_stdout(io.StringIO()):
        return valider_turing(zeros, dps=30, **kw)


class TestValiderTuring(unittest.TestCase):
    """valider_turing évalue à T + EPS_CONTROLE (ajouté le 01/11/2026) : N(T) est discontinue en un zéro."""

    def test_liste_exacte_aucun_ecart(self):
        r = valider_sans_bruit(LMFDB_20)
        self.assertTrue(r["complet"])
        self.assertEqual([v["delta"] for v in r["verifications"]], [0] * len(r["verifications"]))

    def test_zeros_stockes_sous_la_vraie_position_pas_de_faux_surplus(self):
        """Zéros décalés de -1e-9 (erreur de position typique) : aucun surplus avec le décalage de contrôle ;
        sans lui (eps_controle = 0, ancien comportement) les points posés sur un zéro donnent un surplus factice."""
        sous = [z - 1e-9 for z in LMFDB_20]
        r = valider_sans_bruit(sous)
        self.assertEqual([v["delta"] for v in r["verifications"]], [0] * len(r["verifications"]))
        r0 = valider_sans_bruit(sous, eps_controle=0.0)
        self.assertTrue(any(v["delta"] < 0 for v in r0["verifications"]))        # l'artefact existe bien sans le décalage

    def test_zero_manquant_detecte_a_chaque_point_concerne(self):
        """On retire le 4e zéro (30,42…) : chaque point de contrôle situé après lui doit afficher un manque de 1,
        quelle que soit la partie fractionnaire de θ/π (l'ancienne formule en masquait certains)."""
        liste = LMFDB_20[:3] + LMFDB_20[4:]
        r = valider_sans_bruit(liste)
        self.assertFalse(r["complet"])
        apres = [v for v in r["verifications"] if v["T"] > LMFDB_20[3]]
        self.assertTrue(len(apres) >= 3)
        for v in apres:
            with self.subTest(T=round(v["T"], 3), frac=round(frac_theta(v["T_eval"]), 3)):
                self.assertEqual(v["delta"], 1)
        self.assertEqual(r["manquants_total"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
