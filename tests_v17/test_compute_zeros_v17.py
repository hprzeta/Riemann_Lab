# -*- coding: utf-8 -*-
"""
Tests ciblés de compute_zeros_v17.py (revue du 16/10/2026) : D1, D2, D6.

Petits calculs réels (T <= 400) : le détecteur et l'affinage de v16 sont utilisés tels quels ;
seules les ÉCRITURES (E/S) sont forcées en échec par des doublures (unittest.mock), sans
disque plein réel.

Lancement :  zeta_env/bin/python3 -B -I tests_v17/test_compute_zeros_v17.py

  D1-a  collision de sortie : consolidation_v17/ déjà occupé -> _2, _3 ; l'existant est inchangé
  D1-b  consolider() qui échoue -> ConsolidationError, jamais de repli sur dedupliquer()
  D1-c  écriture des sorties de consolidation qui échoue -> ConsolidationError
  D2-a  checkpoint périodique en échec d'E/S -> worker poursuivi, échec journalisé et compté,
        résultats identiques à un run sans checkpoint, fichier final lisible par le lecteur v16
  D2-b  l'état courant ≠ l'ancien partiel est signalé (progress) ; l'ancien partiel est intact
  D2-c  une incohérence logique (provenance ≠ zéros) n'est PAS avalée comme une erreur d'E/S
  D2-d  écriture finale en échec -> RuntimeError explicite, rien de déclaré sauvegardé,
        dernier partiel conservé
  D2-e  _ecrire_atomique : échec -> ancien contenu intact, aucun .tmp résiduel, erreur relevée
  D6    provenance alignée sur les zéros (une méthode par ligne) dans les CSV worker
"""
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src" / "calculs" / "optimisation"))   # -I : pas de sys.path implicite
sys.path.insert(0, str(RACINE / "scripts_v17"))

import compute_zeros_v17 as m                      # noqa: E402
from consolider_v17 import lire_checkpoints_v16    # noqa: E402

T_PETIT = 400.0          # petit intervalle réel (quelques secondes)


def _sha_dossier(d: Path) -> dict:
    """Empreinte de tout le contenu d'un dossier (nom -> sha256)."""
    return {str(p.relative_to(d)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(d.rglob("*")) if p.is_file()}


def _worker(ck, **_):
    """Lance UN worker réel dans le processus courant."""
    step = m._step_adaptatif(T_PETIT)
    return m.worker_v17((14.0, T_PETIT, step, m.SO_PATH, m.TOL_ARB, 0, ck))


class TestD2(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ck = Path(self._tmp.name)
        self._intervalle = m.INTERVALLE_CKPT_S
        m.INTERVALLE_CKPT_S = 0.0            # un checkpoint à CHAQUE bracket
        self.reel = m._csv_worker

    def tearDown(self):
        m.INTERVALLE_CKPT_S = self._intervalle
        self._tmp.cleanup()

    def test_D2a_checkpoint_en_echec_non_fatal(self):
        base = _worker(None)[0]               # référence sans aucun checkpoint

        def faux(chemin, *a, **k):
            if str(chemin).endswith(".partial.csv"):
                raise OSError(28, "disque plein simulé")
            return self.reel(chemin, *a, **k)
        with mock.patch.object(m, "_csv_worker", side_effect=faux):
            zeros, stats, _, prov = _worker(self.ck)
        self.assertEqual(zeros, base, "le calcul poursuivi doit donner les mêmes zéros")
        self.assertGreater(stats["checkpoints_echoues"], 0)
        lignes = [json.loads(l) for l in (self.ck / "echecs_worker_000.jsonl").read_text().splitlines()]
        self.assertTrue(lignes and all(l["phase"] == "checkpoint" for l in lignes))
        self.assertEqual(sorted(p.name for p in self.ck.glob("*.tmp")), [])
        prog = json.loads((self.ck / "progress_worker_000.json").read_text())
        self.assertEqual(prog["phase"], "termine")
        self.assertEqual(prog["checkpoints_echoues"], stats["checkpoints_echoues"])
        cands, ctl = lire_checkpoints_v16(str(self.ck), None)
        self.assertEqual(len(cands), len(base), "CSV final lisible par le lecteur v16")

    def test_D2b_etat_courant_distinct_de_l_ancien_partiel(self):
        zeros, prov = [20.0, 30.0], [("arb_C", 64, 19.9, 20.1, 1.0, -1.0)] * 2
        etat, stats = {"derniere_reussite": None, "echecs": 0}, {"checkpoints_echoues": 0}
        etat = m._checkpoint_periodique(self.ck, 0, 14.0, 100.0, zeros, prov, 2, 10, 30.0, etat, stats)
        partiel = self.ck / "worker_000.partial.csv"
        avant = partiel.read_bytes()
        self.assertTrue(json.loads((self.ck / "progress_worker_000.json").read_text())["checkpoint_ok"])
        zeros2, prov2 = zeros + [40.0], prov + prov[:1]
        with mock.patch.object(m, "_csv_worker", side_effect=OSError(5, "E/S simulée")):
            etat = m._checkpoint_periodique(self.ck, 0, 14.0, 100.0, zeros2, prov2, 3, 10, 40.0, etat, stats)
        prog = json.loads((self.ck / "progress_worker_000.json").read_text())
        self.assertFalse(prog["checkpoint_ok"])
        self.assertEqual(prog["zeros"], 3)                 # état courant
        self.assertEqual(prog["partiel_zeros"], 2)         # ce que contient réellement le partiel
        self.assertEqual(prog["partiel_brackets_faits"], 2)
        self.assertEqual(partiel.read_bytes(), avant, "l'ancien partiel doit rester intact")
        self.assertEqual((etat["echecs"], stats["checkpoints_echoues"]), (1, 1))

    def test_D2c_incoherence_logique_non_avalee(self):
        etat, stats = {"derniere_reussite": None, "echecs": 0}, {"checkpoints_echoues": 0}
        with self.assertRaises(AssertionError):
            m._checkpoint_periodique(self.ck, 0, 14.0, 100.0, [20.0, 30.0],
                                     [("arb_C", 64, 19.9, 20.1, 1.0, -1.0)], 1, 5, 20.0, etat, stats)
        self.assertEqual(stats["checkpoints_echoues"], 0, "ce n'est pas une erreur d'E/S")

    def test_D2d_ecriture_finale_en_echec(self):
        def faux(chemin, *a, **k):
            if not str(chemin).endswith(".partial.csv"):
                raise OSError(28, "écriture finale impossible (simulée)")
            return self.reel(chemin, *a, **k)
        with mock.patch.object(m, "_csv_worker", side_effect=faux):
            with self.assertRaises(RuntimeError) as cm:
                _worker(self.ck)
        self.assertIn("NON sauvegardé", str(cm.exception))
        self.assertFalse((self.ck / "worker_000.csv").exists(), "aucun fichier final déclaré sauvegardé")
        self.assertTrue((self.ck / "worker_000.partial.csv").exists(), "dernier partiel conservé")
        prog = json.loads((self.ck / "progress_worker_000.json").read_text())
        self.assertEqual(prog["phase"], "echec_ecriture_finale")
        phases = [json.loads(l)["phase"] for l in (self.ck / "echecs_worker_000.jsonl").read_text().splitlines()]
        self.assertIn("ecriture_finale", phases)

    def test_D2e_ecriture_atomique_echec(self):
        cible = self.ck / "x.csv"
        cible.write_text("ancien")

        def ecrire(tmp):
            Path(tmp).write_text("à moitié")
            raise OSError(28, "plein simulé")
        with self.assertRaises(OSError):
            m._ecrire_atomique(cible, ecrire)
        self.assertEqual(cible.read_text(), "ancien")
        self.assertEqual(sorted(p.name for p in self.ck.glob("*.tmp")), [])

    def test_D6_provenance_alignee(self):
        zeros, _, _, prov = _worker(self.ck)
        self.assertEqual(len(prov["prov"]), len(zeros))
        import pandas as pd
        # round_trip : le lecteur rapide par défaut de pandas n'est pas exact au dernier bit
        # (écart observé ≤ 6e-14) ; le texte du CSV est, lui, identique à repr(float).
        df = pd.read_csv(self.ck / "worker_000.csv", float_precision="round_trip")
        self.assertEqual(len(df), len(zeros))
        self.assertTrue(df.methode.notna().all())
        self.assertTrue((df.partie_imaginaire.to_numpy() == zeros).all())


class TestD1(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dossier = Path(self._tmp.name) / "run"

    def tearDown(self):
        self._tmp.cleanup()

    def _calculer(self):
        return m.calculer_zeros_v17(14.0, 300.0, 8, m._step_adaptatif(300.0), m.TOL_ARB, self.dossier)

    def test_D1a_collision_preserve_l_existant(self):
        z1 = self._calculer()[0]
        d1 = self.dossier / "consolidation_v17"
        sha1 = _sha_dossier(d1)
        self.assertTrue(sha1)
        z2 = self._calculer()[0]                      # même dossier => même horodatage rejoué
        d2 = self.dossier / "consolidation_v17_2"
        self.assertTrue(d2.is_dir(), "la 2e sortie doit aller dans consolidation_v17_2")
        self.assertEqual(_sha_dossier(d1), sha1, "l'existant doit être préservé octet pour octet")
        man = json.loads((d2 / "manifeste.json").read_text())
        self.assertTrue(man["meta"]["collision_evitee"])
        self.assertEqual(man["meta"]["dossier_sortie"], "consolidation_v17_2")
        self.assertEqual(z1, z2)
        self._calculer()
        self.assertTrue((self.dossier / "consolidation_v17_3").is_dir(), "choix déterministe : _3")
        self.assertEqual(sorted(p.name for p in self.dossier.glob("consolidation_v17*.tmp-*")), [])

    def test_D1b_consolider_en_echec_pas_de_repli(self):
        appels = []
        with mock.patch.object(m, "consolider", side_effect=AssertionError("conservation violée simulée")), \
             mock.patch.object(m, "dedupliquer", side_effect=lambda *a, **k: appels.append(1)):
            with self.assertRaises(m.ConsolidationError) as cm:
                self._calculer()
        self.assertIn("NON VALIDE", str(cm.exception))
        self.assertIn("aucun repli sur dedupliquer", str(cm.exception))
        self.assertEqual(appels, [], "dedupliquer() ne doit JAMAIS être appelée")
        self.assertFalse((self.dossier / "consolidation_v17").exists())
        self.assertTrue(list((self.dossier / "checkpoints").glob("worker_00?.csv")), "CSV worker intacts")

    def test_D1c_ecriture_consolidation_en_echec(self):
        with mock.patch.object(m, "ecrire_resultats", side_effect=OSError(28, "plein simulé")):
            with self.assertRaises(m.ConsolidationError) as cm:
                self._calculer()
        self.assertIn("NON VALIDE", str(cm.exception))
        self.assertIsInstance(cm.exception.__cause__, OSError)


if __name__ == "__main__":
    unittest.main(verbosity=2)
