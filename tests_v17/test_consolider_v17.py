# -*- coding: utf-8 -*-
"""
Tests unitaires D1-D13 de consolider_v17 (données SYNTHÉTIQUES, aucun calcul de zêta).

DÉFINITIONS : D1-D13 proviennent du rapport d'audit du 15/10/2026 ; elles NE sont PAS
préexistantes dans le dépôt. Les définitions ci-dessous sont celles proposées pour V17-P0.
D5 et D6 sont synthétiques : les CSV T1b ne conservent aucun rayon d'incertitude.

Lancement :  zeta_env/bin/python3 -B -I tests_v17/test_consolider_v17.py

HISTORIQUE (15/10/2026) — premier passage : 4 tests FAIL sur 14.
  * D3  : écart 100.01-100.0 = 0.010000000000005 > seuil_tri -> paire non examinée (donnée de test
          mal choisie, corrigée à 100.009) ;
  * D7 et D10 : clés de provenance (source, ligne) en collision entre workers dans les données
          synthétiques (corrigé : un fichier par worker) ; l'invariant de conservation les a détectées ;
  * D5  : DÉFAUT RÉEL DE LA RÈGLE. Écart 8e-4 avec rayons 1e-3 chevauchants : la règle R-DIST1
          répondait DISTINCT en ignorant les rayons. La donnée avait d'abord été modifiée pour masquer
          cela (écart 4e-4) ; revue du 15/10 : la RÈGLE a été corrigée (R-RAYON dans consolider_v17) et
          le D5 d'origine (écart 8e-4) est rétabli ci-dessous.
"""
import itertools
import math
import os
import random
import sys
import unittest

sys.dont_write_bytecode = True   # aucun .pyc dans le dépôt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts_v17"))
from consolider_v17 import (Candidat, ParamsConsolidation, consolider, verifier_conservation,
                            AMBIGUOUS, DISTINCT, DUPLICATE_CONFIRMED, ecrire_resultats,
                            reconstruire_segments_v16)

# Géométrie synthétique : worker 0 -> [100, 200.5], worker 1 -> [200, 300] (zone commune [200, 200.5])
SEG = {0: (100.0, 200.5), 1: (200.0, 300.0), 2: (299.5, 400.0)}
P = ParamsConsolidation(step=3.1e-4, overlap=0.5)


def C(t, w, ligne, src=None, seg=True, **kw):
    src = src or f"worker_{w:03d}.csv"   # un fichier par worker : clés (source, ligne) uniques
    lo, hi = SEG[w] if seg else (None, None)
    return Candidat(t=t, source=src, ligne=ligne, worker=w, seg_lo=lo, seg_hi=hi, **kw)


def statuts(res):
    return sorted(d.statut for d in res.decisions)


class TestD(unittest.TestCase):

    def _res(self, cands, params=P):
        r = consolider(cands, params)
        verifier_conservation(cands, r)   # invariant : aucun candidat perdu
        return r

    def test_D01_doublon_frontiere(self):
        """D1 — même zéro rapporté par deux workers adjacents dans la zone de chevauchement."""
        self.entree = "t=200.25 (w0, l5) et t=200.25 (w1, l2), zone commune [200;200.5]"
        self.attendu = "1 groupe DUPLICATE_CONFIRMED, 1 ligne consolidée"
        r = self._res([C(200.25, 0, 5), C(200.25, 1, 2)])
        self.observe = f"{statuts(r)}, {len(r.consolides)} ligne(s)"
        self.assertEqual(statuts(r), [DUPLICATE_CONFIRMED]); self.assertEqual(len(r.consolides), 1)
        self.assertEqual(sorted(r.consolides[0].sources), [("worker_000.csv", 5), ("worker_001.csv", 2)])

    def test_D02_distincts_rapproches(self):
        """D2 — deux zéros à 7,169e-3 dans le même worker : pas de fusion sur la seule distance."""
        self.entree = "100.000000 et 100.007169, worker 0, STEP=3.1e-4"
        self.attendu = "2 lignes consolidées, aucun DUPLICATE_CONFIRMED"
        r = self._res([C(100.000000, 0, 2), C(100.007169, 0, 3)])
        self.observe = f"{statuts(r)}, {len(r.consolides)} ligne(s)"
        self.assertEqual(len(r.consolides), 2); self.assertNotIn(DUPLICATE_CONFIRMED, statuts(r))
        self.assertEqual(statuts(r), [DISTINCT])

    def test_D03_precision_insuffisante(self):
        """D3 — écart proche de STEP, sans STEP fourni : aucune décision forte possible."""
        self.entree = "100.0000 et 100.0002 (écart 2e-4 < 2*STEP), même worker"
        self.attendu = "AMBIGUOUS, 2 lignes conservées"
        r = self._res([C(100.0, 0, 2), C(100.0002, 0, 3)])
        self.observe = f"{statuts(r)}, {len(r.consolides)} ligne(s)"
        self.assertEqual(statuts(r), [AMBIGUOUS]); self.assertEqual(len(r.consolides), 2)
        r2 = self._res([C(100.0, 0, 2), C(100.009, 0, 3)], ParamsConsolidation())  # sans STEP
        self.assertEqual(statuts(r2), [AMBIGUOUS])

    def test_D04_intervalles_de_recherche_chevauchants(self):
        """D4 — deux workers adjacents, valeurs proches mais NON identiques dans la zone de
        chevauchement : la provenance seule ne suffit pas -> AMBIGUOUS (pas de fusion)."""
        self.entree = "200.250000 (w0) et 200.250001 (w1) : écart 1e-6 > eps_dup, zone commune"
        self.attendu = "AMBIGUOUS, 2 lignes conservées"
        r = self._res([C(200.250000, 0, 5), C(200.250001, 1, 2)])
        self.observe = f"{statuts(r)}, {len(r.consolides)} ligne(s)"
        self.assertEqual(statuts(r), [AMBIGUOUS]); self.assertEqual(len(r.consolides), 2)

    def test_D05_incertitudes_chevauchantes(self):
        """D5 (synthétique) — rayons d'incertitude qui se chevauchent : n'implique PAS l'identité."""
        self.entree = "t=150.0 r=1e-3 et t=150.0008 r=1e-3, même worker (écart 8e-4 > 2*STEP, rayons chevauchants)"
        self.attendu = "aucun DUPLICATE_CONFIRMED ; AMBIGUOUS par la règle R-RAYON (et non par l'écart)"
        r = self._res([C(150.0, 0, 2, rayon=1e-3), C(150.0008, 0, 3, rayon=1e-3)])
        self.assertEqual(r.decisions[0].regle, "R-RAYON")
        self.observe = f"{statuts(r)}, {len(r.consolides)} ligne(s)"
        self.assertNotIn(DUPLICATE_CONFIRMED, statuts(r)); self.assertEqual(len(r.consolides), 2)
        self.assertEqual(statuts(r), [AMBIGUOUS])

    def test_D06_incertitudes_disjointes(self):
        """D6 (synthétique) — rayons disjoints, mais rayon non pris en compte par la règle V17-P0 :
        la décision DISTINCT vient de l'écart >= 2*STEP et de la provenance, pas du rayon ;
        sans STEP, des rayons disjoints ne suffisent PAS (AMBIGUOUS)."""
        self.entree = "t=150.0 r=1e-5 et t=150.005 r=1e-5, même worker ; avec puis sans STEP"
        self.attendu = "avec STEP : DISTINCT ; sans STEP : AMBIGUOUS ; jamais fusionné"
        cands = [C(150.0, 0, 2, rayon=1e-5), C(150.005, 0, 3, rayon=1e-5)]
        r1 = self._res(cands); r2 = self._res(cands, ParamsConsolidation())
        self.observe = f"avec STEP {statuts(r1)} ; sans STEP {statuts(r2)}"
        self.assertEqual(statuts(r1), [DISTINCT]); self.assertEqual(statuts(r2), [AMBIGUOUS])
        self.assertEqual(len(r1.consolides), 2); self.assertEqual(len(r2.consolides), 2)

    def test_D07_entree_desordonnee(self):
        """D7 — le résultat ne dépend pas de l'ordre des lignes (20 permutations aléatoires)."""
        self.entree = "6 candidats (doublon frontière + paire proche + isolés), 20 permutations"
        self.attendu = "sorties identiques (consolidé + décisions) pour toutes les permutations"
        base = [C(120.0, 0, 2), C(120.007, 0, 3), C(200.25, 0, 4), C(200.25, 1, 2),
                C(250.0, 1, 3), C(251.0, 1, 4)]
        ref = None
        rng = random.Random(0)
        for _ in range(20):
            cp = base[:]; rng.shuffle(cp)
            r = self._res(cp)
            sig = ([(l.t, l.statut_ligne, tuple(sorted(l.sources)), tuple(l.groupes)) for l in r.consolides],
                   [(d.groupe, d.statut, d.regle, d.ecart) for d in r.decisions])
            ref = ref or sig
            self.assertEqual(sig, ref)
        self.observe = f"20/20 permutations identiques ; {len(ref[0])} lignes, {len(ref[1])} groupes"

    def test_D08_chaine(self):
        """D8 — chaîne de zéros espacés de 6e-3 : l'ancien dedupliquer(0,01) n'en garde qu'un."""
        self.entree = "100.000, 100.006, 100.012, 100.018 (même worker, pas de 6e-3)"
        self.attendu = "4 lignes conservées, 3 groupes DISTINCT ; l'ancienne méthode en garde 2"
        ts = [100.000, 100.006, 100.012, 100.018]
        r = self._res([C(t, 0, 2 + i) for i, t in enumerate(ts)])
        # reproduction de l'ancien comportement (comparaison au dernier conservé)
        uniq = [ts[0]]
        for t in ts[1:]:
            if t - uniq[-1] > 0.01:
                uniq.append(t)
        self.observe = f"{len(r.consolides)} lignes, {statuts(r)} ; ancienne méthode : {len(uniq)} lignes"
        self.assertEqual(len(r.consolides), 4); self.assertEqual(statuts(r), [DISTINCT] * 3)
        self.assertLess(len(uniq), 4)

    def test_D09_non_finies(self):
        """D9 — NaN, +inf, -inf : journalisés comme invalides, jamais fusionnés ni perdus."""
        self.entree = "NaN, +inf, -inf, 100.0 (valide)"
        self.attendu = "3 invalides (avec raison), 1 candidat consolidé, aucune exception"
        cands = [C(float("nan"), 0, 2), C(float("inf"), 0, 3), C(float("-inf"), 0, 4), C(100.0, 0, 5)]
        r = self._res(cands)
        self.observe = f"{len(r.invalides)} invalides, {len(r.consolides)} consolidé(s)"
        self.assertEqual(len(r.invalides), 3); self.assertEqual(len(r.consolides), 1)
        self.assertTrue(all("raison" in d and d["raison"] for d in r.invalides))
        self.assertEqual(r.decisions, [])

    def test_D10_frontiere_de_segment(self):
        """D10 — aux limites de la zone : bornes incluses ; hors zone -> AMBIGUOUS ; segments
        non fournis -> AMBIGUOUS."""
        self.entree = "t identique à 200.0 (borne basse), 200.5 (borne haute), 200.6 (hors zone), sans segments"
        self.attendu = "DUPLICATE_CONFIRMED, DUPLICATE_CONFIRMED, AMBIGUOUS, AMBIGUOUS"
        s = []
        for i, t in enumerate((200.0, 200.5)):
            s += self._res([C(t, 0, 2 + i), C(t, 1, 2 + i)]).decisions
        # t=200.6 : hors segment du worker 0 (hi=200.5) -> la provenance n'étaye pas le doublon
        s += self._res([C(200.6, 0, 9), C(200.6, 1, 9)]).decisions
        s += self._res([C(200.25, 0, 7, seg=False), C(200.25, 1, 7, seg=False)]).decisions
        obs = [d.statut for d in s]
        self.observe = str(obs)
        self.assertEqual(obs, [DUPLICATE_CONFIRMED, DUPLICATE_CONFIRMED, AMBIGUOUS, AMBIGUOUS])

    def test_D11_relecture_apres_interruption(self):
        """D11 — relecture des mêmes checkpoints (avec ou sans lignes répétées d'une reprise) :
        aucune perte, aucune fusion abusive ; deux lectures identiques -> même résultat."""
        self.entree = "mêmes candidats lus deux fois (fichiers distincts, même worker, mêmes valeurs)"
        self.attendu = "AMBIGUOUS (même worker, même t, deux sources) ; 4 lignes conservées, rien de perdu"
        a = [C(120.0, 0, 2, src="run1.csv"), C(130.0, 0, 3, src="run1.csv")]
        b = [C(120.0, 0, 2, src="run1_reprise.csv"), C(130.0, 0, 3, src="run1_reprise.csv")]
        r = self._res(a + b); r_bis = self._res(a + b)
        self.observe = f"{len(r.consolides)} lignes, {statuts(r)} ; 2e lecture identique : " \
                       f"{[l.t for l in r.consolides] == [l.t for l in r_bis.consolides]}"
        self.assertEqual(len(r.consolides), 4); self.assertEqual(statuts(r), [AMBIGUOUS, AMBIGUOUS])

    def test_D12_tracabilite(self):
        """D12 — chaque décision cite ses candidats (fichier, ligne, worker, valeur), la règle,
        les paramètres de tri, les limites, la version ; sorties écrites sans écrasement."""
        self.entree = "doublon frontière + paire proche ; écriture dans un dossier temporaire"
        self.attendu = "champs de provenance complets ; manifeste ; refus d'écraser un dossier non vide"
        import json, tempfile
        cands = [C(200.25, 0, 5), C(200.25, 1, 2), C(120.0, 0, 6), C(120.007, 0, 7)]
        r = self._res(cands)
        for d in r.decisions:
            self.assertTrue(d.justification and d.regle and d.limites and d.version and d.parametres_tri)
            for c in d.candidats:
                for k in ("source", "ligne", "worker", "t"):
                    self.assertIn(k, c)
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "sortie")
            fichiers = ecrire_resultats(r, out, meta={"test": "D12"})
            self.assertEqual(sorted(os.listdir(out)),
                             ["ambigus.csv", "consolide.csv", "decisions.jsonl", "invalides.csv", "manifeste.json"])
            with open(fichiers["decisions"]) as f:
                lignes = [json.loads(x) for x in f]
            self.assertEqual(len(lignes), len(r.decisions))
            with self.assertRaises(FileExistsError):
                ecrire_resultats(r, out)
        self.observe = f"{len(r.decisions)} décisions entièrement documentées ; écrasement refusé"

    def test_D13_indecidable(self):
        """D13 — groupe sans provenance (worker/segment inconnus) : AMBIGUOUS, rien de supprimé."""
        self.entree = "deux candidats à valeur identique sans worker ni segment"
        self.attendu = "AMBIGUOUS, 2 lignes conservées, 0 supprimé"
        c1 = Candidat(t=100.5, source="x.csv", ligne=2)
        c2 = Candidat(t=100.5, source="y.csv", ligne=2)
        r = self._res([c1, c2])
        self.observe = f"{statuts(r)}, {len(r.consolides)} ligne(s)"
        self.assertEqual(statuts(r), [AMBIGUOUS]); self.assertEqual(len(r.consolides), 2)
        self.assertEqual({l.statut_ligne for l in r.consolides}, {"AMBIGUOUS_QUARANTAINE"})


class TestComplements(unittest.TestCase):
    """Tests complémentaires (hors D1-D13) ajoutés après la revue du 15/10/2026."""

    def test_X1_statut_de_ligne_non_masque(self):
        """X1 — un représentant DUPLICATE_CONFIRMED pris dans une paire AMBIGUOUS garde son statut
        de ligne et reçoit l'indicateur quarantaine."""
        self.entree = "doublon frontière à 200.25 (w0/w1) + candidat w1 à 200.2502 (écart 2e-4 < 2*STEP)"
        self.attendu = "ligne 200.25 : DUPLICATE_CONFIRMED et quarantaine=True ; 2 lignes au total"
        r = consolider([C(200.25, 0, 5), C(200.25, 1, 2), C(200.2502, 1, 3)], P)
        verifier_conservation([C(200.25, 0, 5), C(200.25, 1, 2), C(200.2502, 1, 3)], r)
        l = r.consolides[0]
        self.observe = f"{len(r.consolides)} lignes ; première : {l.statut_ligne}, quarantaine={l.quarantaine}"
        self.assertEqual(len(r.consolides), 2)
        self.assertEqual(l.statut_ligne, DUPLICATE_CONFIRMED); self.assertTrue(l.quarantaine)

    def test_X2_ecriture_atomique(self):
        """X2 — aucun dossier temporaire résiduel après écriture ; dossier cible vide accepté."""
        self.entree = "écriture dans un dossier vide existant puis inspection du répertoire parent"
        self.attendu = "seul le dossier final subsiste (pas de .tmp-)"
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "s"); os.makedirs(out)
            ecrire_resultats(consolider([C(100.0, 0, 2)], P), out)
            self.observe = str(sorted(os.listdir(tmp)))
            self.assertEqual(sorted(os.listdir(tmp)), ["s"]); self.assertIn("manifeste.json", os.listdir(out))


class TestSegmentsReconstruits(unittest.TestCase):
    def test_controle_segments(self):
        """Contrôle complémentaire (hors D1-D13) : les segments reconstruits sont ordonnés et
        se chevauchent de 0,5."""
        segs = reconstruire_segments_v16(4_900_000.0, 4_986_000.0, 8, 0.5)
        self.assertEqual(len(segs), 8)
        for (a, b), (c, d) in zip(segs, segs[1:]):
            self.assertAlmostEqual(b - c, 0.5, places=6)


# ─── Exécuteur avec tableau de synthèse ──────────────────────────────────────

class _Res(unittest.TextTestResult):
    lignes = []

    def _noter(self, test, verdict):
        _Res.lignes.append((test.id().split(".")[-1], verdict, (getattr(test, test._testMethodName).__doc__ or "").strip().split("\n")[0],
                            getattr(test, "entree", ""), getattr(test, "attendu", ""),
                            getattr(test, "observe", "")))

    def addSuccess(self, t):
        super().addSuccess(t); self._noter(t, "PASS")

    def addFailure(self, t, e):
        super().addFailure(t, e); self._noter(t, "FAIL")

    def addError(self, t, e):
        super().addError(t, e); self._noter(t, "FAIL (erreur)")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    res = unittest.TextTestRunner(resultclass=_Res, verbosity=0).run(suite)
    print("\n=== TABLEAU DES TESTS ===")
    for nom, v, doc, ent, att, obs in sorted(_Res.lignes):
        print(f"[{v}] {nom}\n   objectif : {doc}\n   entrée   : {ent}\n   attendu  : {att}\n   observé  : {obs}")
    sys.exit(0 if res.wasSuccessful() else 1)
