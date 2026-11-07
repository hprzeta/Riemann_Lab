# -*- coding: utf-8 -*-
"""
Test d'équivalence du scan par blocs (option B, 07/11/2026) : _scan_arb_par_blocs contre l'appel unique scan_arb.

Lancement :  PYTHONPATH=src zeta_env/bin/python -I tests_v17/test_scan_par_blocs.py

Vérifie, sur de VRAIS calculs (scan_arb.so) en réduisant la taille de bloc pour forcer plusieurs blocs :
  - même nombre de brackets ;
  - chaque bracket de l'appel unique a son vis-à-vis dans la version par blocs (écart <= 2 ulp sur a et b) ;
  - mêmes signes fa/fb ;
  - brackets en ordre croissant, sans doublon ;
  - un segment court (1 seul bloc) renvoie exactement le même résultat que l'appel unique.
"""
import math
import sys
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "src" / "calculs" / "optimisation"))
import compute_zeros_v17 as v17                       # contient _scan_arb_par_blocs
from scan_arb_wrapper import scan_arb                 # appel unique de référence


class TestScanParBlocs(unittest.TestCase):

    def _compare(self, t_a, t_b, step, pas_bloc):
        v17.PAS_MIN_PAR_BLOC = pas_bloc               # force des blocs courts pour exercer le découpage
        try:
            unique = scan_arb(t_a, t_b, step=step, max_brackets=400_000)
            blocs = v17._scan_arb_par_blocs(t_a, t_b, step, 400_000, 0)
        finally:
            v17.PAS_MIN_PAR_BLOC = 1_000_000          # restaure la valeur de production
        return unique, blocs

    def test_equivalence_plusieurs_blocs(self):
        # 100000 → 100060 au pas 1e-4 : 600 000 pas, blocs de 50 000 pas → 12 blocs
        unique, blocs = self._compare(100000.0, 100060.0, 1e-4, 50_000)
        self.assertGreater(len(unique), 50)           # le segment contient bien des zéros
        self.assertEqual(len(unique), len(blocs), "nombre de brackets différent")
        for (a1, b1, fa1, fb1), (a2, b2, fa2, fb2) in zip(unique, blocs):
            tol = 2 * math.ulp(a1)                    # tolérance : 2 ulp (arrondi de t_min + k·step)
            self.assertAlmostEqual(a1, a2, delta=tol)
            self.assertAlmostEqual(b1, b2, delta=tol)
            self.assertEqual(fa1 > 0, fa2 > 0)        # mêmes signes de Z aux bornes
            self.assertEqual(fb1 > 0, fb2 > 0)
        a_liste = [a for a, _, _, _ in blocs]
        self.assertEqual(a_liste, sorted(a_liste))    # ordre croissant
        self.assertEqual(len(a_liste), len(set(round(a, 6) for a in a_liste)), "doublon aux frontières de blocs")

    def test_segment_court_identique(self):
        # segment court : un seul bloc → résultat strictement identique à l'appel unique
        unique, blocs = self._compare(1000.0, 1010.0, 0.002, 1_000_000)
        self.assertEqual(unique, blocs)

    def test_segment_vide(self):
        self.assertEqual(v17._scan_arb_par_blocs(500.0, 500.0, 0.01, 1000, 0), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
