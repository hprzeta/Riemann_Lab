# -*- coding: utf-8 -*-
"""
consolider_v17.py — Consolidation NON DESTRUCTIVE des candidats-zéros (V17, phase P0).

Remplace, à titre expérimental et SANS la modifier, la logique de `dedupliquer()` de
`parallel_scanner.py` (fusion par simple seuil de distance, sans provenance).

Principes :
  * la proximité numérique n'est jamais une preuve d'identité : un seuil sert uniquement
    à désigner les candidats À EXAMINER (tri préalable) ;
  * chaque groupe étudié reçoit EXACTEMENT un statut parmi
    DUPLICATE_CONFIRMED / DISTINCT / AMBIGUOUS ;
  * aucun candidat ne disparaît sans décision traçable (invariant vérifié par
    `verifier_conservation`) ;
  * en cas de doute -> AMBIGUOUS (candidats conservés séparément, mis en quarantaine) ;
  * l'absence de rayon d'incertitude n'est JAMAIS remplacée par une incertitude estimée.

Statuts de validation du projet : ce module ne certifie rien (aucune arithmétique
d'intervalles) ; il documente des décisions de bookkeeping sur des listes de candidats.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Sequence, Tuple

VERSION_ALGO = "consolider_v17/0.1-P0"

DUPLICATE_CONFIRMED = "DUPLICATE_CONFIRMED"
DISTINCT = "DISTINCT"
AMBIGUOUS = "AMBIGUOUS"
STATUTS = (DUPLICATE_CONFIRMED, DISTINCT, AMBIGUOUS)


# ═══════════════════════════════════════════════════════════════════════════
#  Modèle de données
# ═══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Candidat:
    """Un zéro candidat avec toute la provenance disponible (None = non fourni)."""
    t: float                              # valeur estimée du zéro (partie imaginaire)
    source: str                           # fichier source (chemin)
    ligne: int                            # numéro de ligne dans le fichier (1 = en-tête)
    worker: Optional[int] = None          # worker d'origine
    seg_lo: Optional[float] = None        # borne basse du segment de recherche du worker
    seg_hi: Optional[float] = None        # borne haute du segment (inclut le chevauchement)
    methode: Optional[str] = None         # méthode de détection/affinage
    prec_bits: Optional[int] = None       # précision numérique utilisée
    residu: Optional[float] = None        # résidu |Z(t)| ou valeur de contrôle
    rayon: Optional[float] = None         # rayon d'erreur (UNIQUEMENT s'il vient du calcul)
    bracket: Optional[Tuple[float, float]] = None  # encadrement de recherche
    run_id: Optional[str] = None          # identifiant d'exécution / checkpoint
    brut: Optional[str] = None            # texte brut de la valeur lue (traçabilité)

    def cle(self) -> Tuple[str, int]:
        """Clé de provenance unique (fichier, ligne)."""
        return (self.source, self.ligne)


@dataclass
class ParamsConsolidation:
    """Paramètres de travail — des valeurs À EXAMINER, pas des constantes mathématiques."""
    seuil_tri: float = 0.01        # sélection des paires à examiner (n'autorise AUCUNE fusion)
    eps_dup: float = 1e-9          # écart max pour qualifier deux valeurs de « quasi identiques »
                                   # (~1 ulp de float64 à t≈5e6 : 2^-30 ≈ 9,3e-10)
    step: Optional[float] = None   # pas du scan de détection (si connu) ; None => jamais DISTINCT
    facteur_step: float = 2.0      # écart minimal (en multiples de STEP) pour exclure un même bracket
    overlap: Optional[float] = None  # largeur nominale du chevauchement entre segments
    tol_seg: float = 1e-6          # tolérance sur la cohérence des bornes de segments reconstruites


@dataclass
class Decision:
    groupe: str
    type_groupe: str                # 'doublon_exact' | 'paire_proche'
    candidats: List[dict]
    ecart: float
    intervalles: str                # description des incertitudes/encadrements disponibles
    statut: str
    justification: str
    regle: str
    parametres_tri: dict
    limites: str
    version: str = VERSION_ALGO


@dataclass
class LigneConsolidee:
    t: float
    statut_ligne: str               # UNIQUE | DUPLICATE_CONFIRMED | DISTINCT | AMBIGUOUS_QUARANTAINE
    quarantaine: bool               # vrai si la ligne appartient à au moins un groupe AMBIGUOUS
    groupes: List[str]
    sources: List[Tuple[str, int]]  # toutes les provenances représentées par cette ligne
    workers: List[Optional[int]]


@dataclass
class Resultat:
    consolides: List[LigneConsolidee]
    decisions: List[Decision]
    invalides: List[dict]
    params: ParamsConsolidation
    n_entree: int = 0


# ═══════════════════════════════════════════════════════════════════════════
#  Outils internes
# ═══════════════════════════════════════════════════════════════════════════

def _fini(x) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(x)


def _cle_tri(c: Candidat):
    """Ordre déterministe, indépendant de l'ordre d'entrée (t, worker, source, ligne)."""
    return (c.t, -1 if c.worker is None else c.worker, c.source, c.ligne)


def _desc(c: Candidat) -> dict:
    return {"t": repr(c.t), "source": c.source, "ligne": c.ligne, "worker": c.worker,
            "segment": [c.seg_lo, c.seg_hi], "bracket": c.bracket, "rayon": c.rayon,
            "residu": c.residu, "methode": c.methode, "prec_bits": c.prec_bits,
            "run_id": c.run_id}


def _zone_commune(a: Candidat, b: Candidat, p: ParamsConsolidation):
    """Zone de chevauchement entre deux workers ADJACENTS (a < b).
    Retourne (ok, message). Exige des bornes de segment connues et cohérentes."""
    if a.worker is None or b.worker is None:
        return False, "worker inconnu"
    if b.worker != a.worker + 1:
        return False, "workers non adjacents"
    if a.seg_hi is None or b.seg_lo is None:
        return False, "bornes de segment non fournies"
    lo, hi = b.seg_lo, a.seg_hi
    if not hi > lo:
        return False, "les segments ne se chevauchent pas"
    if p.overlap is not None and abs((hi - lo) - p.overlap) > p.tol_seg:
        return False, f"largeur de zone {hi - lo!r} incohérente avec overlap nominal {p.overlap!r}"
    tol = max(p.eps_dup, 0.0)
    for c in (a, b):
        if not (lo - tol <= c.t <= hi + tol):
            return False, f"candidat worker {c.worker} hors de la zone [{lo!r}, {hi!r}]"
    return True, f"zone commune [{lo!r}, {hi!r}] (largeur {hi - lo!r})"


def _paire_dans_zone_commune(x: Candidat, y: Candidat, p: ParamsConsolidation) -> bool:
    """Vrai si x et y sont de workers adjacents et tous deux dans leur zone commune."""
    if x.worker is None or y.worker is None or x.worker == y.worker:
        return False
    a, b = (x, y) if x.worker < y.worker else (y, x)
    return _zone_commune(a, b, p)[0]


# ═══════════════════════════════════════════════════════════════════════════
#  Règles de décision
# ═══════════════════════════════════════════════════════════════════════════

def _decider_cluster(membres: List[Candidat], p: ParamsConsolidation):
    """Cluster de valeurs quasi identiques (écart <= eps_dup). Règle R-DUP1."""
    ecart = membres[-1].t - membres[0].t
    base = (f"{len(membres)} candidats à écart max {ecart!r} <= eps_dup={p.eps_dup!r} ")
    lim = ("Aucun rayon d'incertitude ni encadrement conservé : l'identité repose sur la "
           "provenance (workers adjacents, zone de chevauchement) et sur la concordance "
           "numérique ; eps_dup est une valeur de travail.")
    if len(membres) != 2:
        return AMBIGUOUS, "R-DUP1", base + "taille de cluster != 2 : cas non prévu par la règle", lim
    a, b = membres
    if a.worker is None or b.worker is None:
        return AMBIGUOUS, "R-DUP1", base + "worker inconnu pour au moins un candidat", lim
    if a.worker == b.worker:
        return (AMBIGUOUS, "R-DUP1", base + f"les deux candidats viennent du MÊME worker {a.worker} : "
                "origine de la répétition non élucidée (ré-évaluation ? double détection ?)", lim)
    lo, hi = (a, b) if a.worker < b.worker else (b, a)
    ok, msg = _zone_commune(lo, hi, p)
    if not ok:
        return AMBIGUOUS, "R-DUP1", base + "provenance non concluante : " + msg, lim
    return (DUPLICATE_CONFIRMED, "R-DUP1",
            base + f"workers adjacents {lo.worker}/{hi.worker}, chacun dans la {msg} ; "
            f"écart {ecart!r} : même zéro rapporté deux fois par le chevauchement", lim)


def _decider_paire(x: dict, y: dict, p: ParamsConsolidation):
    """Paire d'items proches (écart > eps_dup mais <= seuil_tri). Règles R-DIST1/2, sinon AMBIGUOUS.
    x, y : {'t', 'membres': [Candidat], 'cluster_ambigu': bool}"""
    gap = y["t"] - x["t"]
    lim = ("DISTINCT repose sur la structure du scan (un zéro par bracket, pas STEP), NON sur des "
           "données stockées : aucun bracket ni rayon conservé dans les CSV historiques. "
           "Ne vaut ni certification ni preuve d'unicité.")
    if x["cluster_ambigu"] or y["cluster_ambigu"]:
        return AMBIGUOUS, "R-PAIRE0", "un des candidats appartient à un cluster AMBIGUOUS", lim
    # R-RAYON : des rayons d'incertitude FOURNIS qui se chevauchent interdisent de conclure
    # (jamais de rayon inventé : un rayon absent compte pour 0 ; sans aucun rayon la règle est muette).
    rayons = [m.rayon for m in x["membres"] + y["membres"] if m.rayon is not None]
    if rayons:
        rx = max([m.rayon for m in x["membres"] if m.rayon is not None] or [0.0])
        ry = max([m.rayon for m in y["membres"] if m.rayon is not None] or [0.0])
        if gap <= rx + ry:
            return (AMBIGUOUS, "R-RAYON",
                    f"écart {gap!r} <= somme des rayons fournis ({rx!r} + {ry!r}) : intervalles d'incertitude "
                    "chevauchants, ni identité ni distinction ne peuvent être conclues", lim)
    if p.step is None:
        return (AMBIGUOUS, "R-PAIRE0",
                f"écart {gap!r} > eps_dup mais aucun STEP fourni : rien n'établit que les deux "
                "candidats viennent de brackets différents", lim)
    if any(m.worker is None for m in x["membres"] + y["membres"]):
        return AMBIGUOUS, "R-PAIRE0", "worker inconnu pour au moins un candidat", lim
    if gap < p.facteur_step * p.step:
        return (AMBIGUOUS, "R-PAIRE0",
                f"écart {gap!r} < {p.facteur_step}*STEP = {p.facteur_step * p.step!r} : "
                "deux racines pourraient relever d'un même bracket", lim)
    for mx in x["membres"]:
        for my in y["membres"]:
            if _paire_dans_zone_commune(mx, my, p):
                return (AMBIGUOUS, "R-PAIRE0",
                        f"écart {gap!r} >= {p.facteur_step}*STEP mais les deux candidats sont de workers "
                        f"adjacents {mx.worker}/{my.worker} dans leur zone de chevauchement : "
                        "incohérence inter-workers possible (zéro vu par un seul worker ?)", lim)
    ws_x = {m.worker for m in x["membres"]}
    ws_y = {m.worker for m in y["membres"]}
    if len(ws_x | ws_y) == 1:
        return (DISTINCT, "R-DIST1",
                f"même worker {next(iter(ws_x))} ; écart {gap!r} >= {p.facteur_step}*STEP = "
                f"{p.facteur_step * p.step!r} (= {gap / p.step:.2f} pas) : deux brackets distincts "
                "du même scan (par construction : un affinage par changement de signe)", lim)
    return (DISTINCT, "R-DIST2",
            f"workers {sorted(ws_x)}/{sorted(ws_y)} hors zone commune ; écart {gap!r} >= "
            f"{p.facteur_step}*STEP", lim)


# ═══════════════════════════════════════════════════════════════════════════
#  Consolidation
# ═══════════════════════════════════════════════════════════════════════════

def consolider(candidats: Sequence[Candidat],
               params: Optional[ParamsConsolidation] = None) -> Resultat:
    """Consolide une liste de candidats SANS en perdre aucun (voir verifier_conservation)."""
    p = params or ParamsConsolidation()
    candidats = list(candidats)

    # 1. Valeurs non finies : écartées de la consolidation, mais journalisées (jamais silencieuses)
    valides, invalides = [], []
    for c in candidats:
        if not _fini(c.t):
            invalides.append({"source": c.source, "ligne": c.ligne, "worker": c.worker,
                              "valeur": repr(c.t), "brut": c.brut,
                              "raison": "valeur non finie ou non numérique (NaN/inf)"})
        else:
            valides.append(c)
    valides.sort(key=_cle_tri)
    invalides.sort(key=lambda d: (d["source"], d["ligne"]))

    # 2. Clusters de valeurs quasi identiques (liaison complète : t - premier <= eps_dup)
    clusters: List[List[Candidat]] = []
    for c in valides:
        if clusters and c.t - clusters[-1][0].t <= p.eps_dup:
            clusters[-1].append(c)
        else:
            clusters.append([c])

    decisions: List[Decision] = []
    compteur = [0]

    def nouveau_id():
        compteur[0] += 1
        return f"G{compteur[0]:06d}"

    tri = {"seuil_tri": p.seuil_tri, "eps_dup": p.eps_dup, "step": p.step,
           "facteur_step": p.facteur_step, "overlap": p.overlap, "tol_seg": p.tol_seg}
    items: List[dict] = []
    for cl in clusters:
        if len(cl) == 1:
            items.append({"t": cl[0].t, "membres": cl, "cluster_ambigu": False,
                          "statut": "UNIQUE", "groupes": [], "quarantaine": False})
            continue
        statut, regle, just, lim = _decider_cluster(cl, p)
        gid = nouveau_id()
        decisions.append(Decision(
            groupe=gid, type_groupe="doublon_exact", candidats=[_desc(c) for c in cl],
            ecart=cl[-1].t - cl[0].t,
            intervalles="rayons/encadrements non fournis par les données d'origine",
            statut=statut, justification=just, regle=regle, parametres_tri=tri, limites=lim))
        if statut == DUPLICATE_CONFIRMED:
            # un seul représentant : le plus petit t du cluster (à égalité, le worker le plus bas) ;
            # toutes les provenances du cluster restent listées dans `sources`
            items.append({"t": cl[0].t, "membres": cl, "cluster_ambigu": False,
                          "statut": DUPLICATE_CONFIRMED, "groupes": [gid], "quarantaine": False})
        else:
            for c in cl:   # AMBIGUOUS : chaque candidat est conservé séparément
                items.append({"t": c.t, "membres": [c], "cluster_ambigu": True,
                              "statut": "AMBIGUOUS_QUARANTAINE", "groupes": [gid], "quarantaine": True})

    # 3. Paires proches successives (tri préalable à seuil_tri ; aucune fusion à ce stade)
    for i in range(len(items) - 1):
        x, y = items[i], items[i + 1]
        gap = y["t"] - x["t"]
        if gap > p.seuil_tri or (x["cluster_ambigu"] and y["cluster_ambigu"]
                                 and x["groupes"] == y["groupes"]):
            continue    # hors tri, ou deux membres d'un même cluster ambigu (déjà décidés)
        statut, regle, just, lim = _decider_paire(x, y, p)
        gid = nouveau_id()
        decisions.append(Decision(
            groupe=gid, type_groupe="paire_proche",
            candidats=[_desc(m) for m in x["membres"] + y["membres"]], ecart=gap,
            intervalles="rayons/encadrements non fournis par les données d'origine",
            statut=statut, justification=just, regle=regle, parametres_tri=tri, limites=lim))
        for it in (x, y):
            it["groupes"].append(gid)
            if statut == AMBIGUOUS:
                it["quarantaine"] = True          # indicateur séparé : n'écrase pas DUPLICATE_CONFIRMED
                if it["statut"] in ("UNIQUE", DISTINCT):
                    it["statut"] = "AMBIGUOUS_QUARANTAINE"
            elif it["statut"] == "UNIQUE":
                it["statut"] = DISTINCT

    consolides = [LigneConsolidee(
        t=it["t"], statut_ligne=it["statut"], quarantaine=it["quarantaine"], groupes=list(it["groupes"]),
        sources=[m.cle() for m in it["membres"]], workers=[m.worker for m in it["membres"]])
        for it in items]
    res = Resultat(consolides=consolides, decisions=decisions, invalides=invalides,
                   params=p, n_entree=len(candidats))
    verifier_conservation(candidats, res)
    return res


def verifier_conservation(candidats: Sequence[Candidat], res: Resultat) -> None:
    """Invariant : chaque candidat d'entrée est soit dans `invalides`, soit représenté par
    exactement une ligne consolidée. Lève AssertionError sinon (jamais de perte silencieuse)."""
    vus: Dict[Tuple[str, int], int] = {}
    for l in res.consolides:
        for k in l.sources:
            vus[k] = vus.get(k, 0) + 1
    inval = {(d["source"], d["ligne"]) for d in res.invalides}
    for c in candidats:
        k = c.cle()
        if k in inval:
            assert k not in vus, f"{k} à la fois invalide et consolidé"
        else:
            assert vus.get(k, 0) == 1, f"candidat {k} représenté {vus.get(k, 0)} fois (attendu 1)"
    assert len(vus) + len(inval) == len({c.cle() for c in candidats}), "provenance incohérente"
    for d in res.decisions:
        assert d.statut in STATUTS, f"statut illégal {d.statut}"


# ═══════════════════════════════════════════════════════════════════════════
#  Adaptateur du format historique V16 (lecture seule)
# ═══════════════════════════════════════════════════════════════════════════

def sha256_fichier(chemin: str) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def _n_zeros_expected(T: float) -> int:
    """COPIE de compute_zeros_v16._n_zeros_expected (Weyl tronquée) — pour reconstruire les segments."""
    if T < 14.0:
        return 0
    return int(T / (2 * math.pi) * math.log(T / (2 * math.pi * math.e)))


def reconstruire_segments_v16(t_min: float, t_max: float, n_workers: int,
                              overlap: float = 0.5) -> List[Tuple[float, float]]:
    """COPIE fonctionnelle de compute_zeros_v16._partitionner_adaptatif (lecture du code,
    l.96-130). Les bornes de segments NE sont PAS stockées dans les CSV historiques : elles sont
    RECONSTRUITES ici (donc DÉDUITES) puis contrôlées contre les données par l'appelant."""
    N_min = _n_zeros_expected(t_min)
    N_total = _n_zeros_expected(t_max) - N_min
    if N_total == 0 or n_workers <= 1:
        return [(t_min, t_max)]

    def t_pour_n(n_cible, lo, hi):
        for _ in range(60):
            mid = (lo + hi) / 2.0
            if _n_zeros_expected(mid) < n_cible:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2.0

    segs, t_prev = [], t_min
    for i in range(1, n_workers):
        t_next = t_pour_n(N_min + i * N_total // n_workers, t_min, t_max)
        segs.append((t_prev, min(t_next + overlap, t_max)))
        t_prev = t_next
    segs.append((t_prev, t_max))
    return segs


def lire_checkpoints_v16(dossier_ckpt: str, segments: Optional[List[Tuple[float, float]]],
                         run_id: Optional[str] = None):
    """Lit `worker_NNN.csv` (colonnes n, partie_imaginaire) SANS rien modifier.
    Retourne (candidats, controle) ; `controle` consigne la cohérence données/segments.
    Si les données d'un worker sortent de son segment reconstruit, ses bornes sont retirées
    (=> aucun DUPLICATE_CONFIRMED possible pour lui)."""
    fichiers = sorted(f for f in os.listdir(dossier_ckpt) if re.fullmatch(r"worker_\d{3}\.csv", f))
    cands: List[Candidat] = []
    controle = {"fichiers": fichiers, "workers": {}}
    for f in fichiers:
        w = int(f[7:10])
        chemin = os.path.join(dossier_ckpt, f)
        lignes = []
        with open(chemin, newline="") as fh:
            lecteur = csv.reader(fh)
            entete = next(lecteur)
            for num, row in enumerate(lecteur, start=2):
                brut = row[1] if len(row) > 1 else ""
                try:
                    t = float(brut)
                except ValueError:
                    t = float("nan")
                lignes.append((num, t, brut))
        seg = segments[w] if segments and w < len(segments) else (None, None)
        finis = [t for _, t, _ in lignes if math.isfinite(t)]
        ok = True
        if seg[0] is not None and finis:
            ok = (min(finis) >= seg[0] - 1e-6) and (max(finis) <= seg[1] + 1e-6)
        controle["workers"][w] = {"entete": entete, "lignes": len(lignes), "segment_reconstruit": seg,
                                  "t_min": min(finis) if finis else None,
                                  "t_max": max(finis) if finis else None,
                                  "coherent_avec_segment": ok}
        lo, hi = (seg if ok else (None, None))
        for num, t, brut in lignes:
            cands.append(Candidat(t=t, source=chemin, ligne=num, worker=w, seg_lo=lo, seg_hi=hi,
                                  methode=None, prec_bits=None, residu=None, rayon=None,
                                  bracket=None, run_id=run_id, brut=brut))
    return cands, controle


# ═══════════════════════════════════════════════════════════════════════════
#  Écriture des sorties (jamais d'écrasement)
# ═══════════════════════════════════════════════════════════════════════════

def ecrire_resultats(res: Resultat, dossier: str, meta: Optional[dict] = None) -> Dict[str, str]:
    """Écrit consolide.csv, decisions.jsonl, ambigus.csv, invalides.csv, manifeste.json.
    Refuse d'écrire dans un dossier existant non vide."""
    if os.path.exists(dossier) and os.listdir(dossier):
        raise FileExistsError(f"dossier de sortie non vide : {dossier}")
    # écriture ATOMIQUE : tout est écrit dans un dossier temporaire voisin, puis renommé en une
    # opération ; un arrêt en cours ne laisse pas de dossier partiel qui bloquerait la relance.
    final = dossier.rstrip(os.sep)
    dossier = f"{final}.tmp-{os.getpid()}"
    os.makedirs(dossier)
    sorties = {}
    p = os.path.join(dossier, "consolide.csv")
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "statut_ligne", "quarantaine", "groupes", "workers", "sources"])
        for l in res.consolides:
            w.writerow([repr(l.t), l.statut_ligne, int(l.quarantaine), "|".join(l.groupes),
                        "|".join("" if x is None else str(x) for x in l.workers),
                        "|".join(f"{os.path.basename(s)}:{n}" for s, n in l.sources)])
    sorties["consolide"] = p
    p = os.path.join(dossier, "decisions.jsonl")
    with open(p, "w") as f:
        for d in res.decisions:
            f.write(json.dumps(asdict(d), ensure_ascii=False, sort_keys=True) + "\n")
    sorties["decisions"] = p
    p = os.path.join(dossier, "ambigus.csv")
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["groupe", "type_groupe", "ecart", "t", "source", "ligne", "worker", "justification"])
        for d in res.decisions:
            if d.statut == AMBIGUOUS:
                for c in d.candidats:
                    w.writerow([d.groupe, d.type_groupe, repr(d.ecart), c["t"],
                                os.path.basename(c["source"]), c["ligne"], c["worker"], d.justification])
    sorties["ambigus"] = p
    p = os.path.join(dossier, "invalides.csv")
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "ligne", "worker", "valeur", "brut", "raison"])
        for d in res.invalides:
            w.writerow([os.path.basename(d["source"]), d["ligne"], d["worker"], d["valeur"],
                        d["brut"], d["raison"]])
    sorties["invalides"] = p
    p = os.path.join(dossier, "manifeste.json")
    with open(p, "w") as f:
        json.dump({"version_algo": VERSION_ALGO, "params": asdict(res.params),
                   "n_entree": res.n_entree, "n_consolides": len(res.consolides),
                   "n_groupes": len(res.decisions), "n_invalides": len(res.invalides),
                   "meta": meta or {}}, f, indent=2, ensure_ascii=False, sort_keys=True)
    sorties["manifeste"] = p
    if os.path.isdir(final):          # dossier cible existant mais vide : on le remplace
        os.rmdir(final)
    os.rename(dossier, final)
    return {k: os.path.join(final, os.path.basename(v)) for k, v in sorties.items()}
