# -*- coding: utf-8 -*-
"""
rejeu_t1b.py — Rejeu de la consolidation V17 sur les données BRUTES de T1b (lecture seule).

Aucun zéro n'est recalculé. Lit calculs/v16_T4900000_4986000_T1b/checkpoints/worker_*.csv,
vérifie les chiffres historiques, applique consolider() (2 variantes) et compare à l'ancienne
dedupliquer(0.01). Écrit dans un NOUVEAU dossier (refus d'écraser).

Usage : zeta_env/bin/python3 -I scripts_v17/rejeu_t1b.py <dossier_sortie>
"""
import hashlib
import importlib.util
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True      # aucun .pyc écrit (l'import de parallel_scanner reste en lecture seule)
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from consolider_v17 import (ParamsConsolidation, consolider, ecrire_resultats, lire_checkpoints_v16,
                            reconstruire_segments_v16, sha256_fichier, AMBIGUOUS, DISTINCT,
                            DUPLICATE_CONFIRMED)

RACINE = os.path.abspath(os.path.join(ICI, ".."))
DOSSIER_T1B = os.path.join(RACINE, "calculs", "v16_T4900000_4986000_T1b")
CKPT = os.path.join(DOSSIER_T1B, "checkpoints")
LOG = os.path.join(DOSSIER_T1B, "execution_v16_T4986000_T1b.log")
CSV_FINAL = os.path.join(DOSSIER_T1B, "zeros_v16_T4986000_T1b.csv")
OVERLAP_V16 = 0.5      # lu dans compute_zeros_v16._partitionner_adaptatif (OVERLAP = 0.5)
ECARTS_RAPPORTES = [3.028e-3, 7.169e-3, 7.241e-3, 7.787e-3]


def shas():
    fich = sorted(os.path.join(CKPT, f) for f in os.listdir(CKPT)) + [CSV_FINAL, LOG]
    return {os.path.relpath(f, RACINE): sha256_fichier(f) for f in fich}


def params_log():
    txt = open(LOG, encoding="utf-8").read()
    def grab(nom):
        m = re.search(nom + r"\s*=\s*([0-9.eE+-]+)", txt)
        return float(m.group(1)) if m else None
    return {"T_MIN": grab("T_MIN"), "T_MAX": grab("T_MAX"), "STEP": grab("STEP"),
            "N_WORKERS": int(grab("N_WORKERS")), "TOL_ARB": grab("TOL_ARB")}


def ancienne_dedup(valeurs):
    """Ancienne dedupliquer(0.01) — chargée depuis parallel_scanner si possible (code non modifié)."""
    try:
        sys.path.insert(0, os.path.join(RACINE, "src", "calculs", "optimisation"))
        spec = importlib.util.spec_from_file_location("ps_hist", os.path.join(
            RACINE, "src", "calculs", "optimisation", "parallel_scanner.py"))
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        return mod.dedupliquer(list(valeurs), tolerance=0.01), "parallel_scanner.dedupliquer (import réel)"
    except Exception as e:      # signalé, jamais silencieux
        z = sorted(valeurs); u = [z[0]]
        for t in z[1:]:
            if t - u[-1] > 0.01:
                u.append(t)
        return u, f"COPIE de l'algorithme (import impossible : {type(e).__name__}: {e})"


def main(sortie):
    # garde de chemin : la sortie DOIT être sous resultats_v17/ (jamais dans calculs/, src/, etc.)
    autorise = os.path.join(RACINE, "resultats_v17") + os.sep
    if not os.path.abspath(sortie).startswith(autorise):
        sys.exit(f"Sortie refusée (hors resultats_v17/) : {sortie}")
    if os.path.exists(sortie) and os.listdir(sortie):
        sys.exit(f"Dossier de sortie non vide : {sortie}")
    os.makedirs(sortie, exist_ok=True)
    sha_avant = shas()
    pl = params_log()
    segs = reconstruire_segments_v16(pl["T_MIN"], pl["T_MAX"], pl["N_WORKERS"], OVERLAP_V16)
    cands, controle = lire_checkpoints_v16(CKPT, segs, run_id="T1b_20261015")
    rapport = {"params_log": pl, "overlap_code_v16": OVERLAP_V16, "segments_reconstruits": segs,
               "controle_segments": controle, "sha_avant": sha_avant}

    # --- chiffres historiques recalculés sur les données présentes
    vals = [c.t for c in cands if math.isfinite(c.t)]
    par_worker = {w: v["lignes"] for w, v in controle["workers"].items()}
    ancien, mode_ancien = ancienne_dedup(vals)
    z = sorted(vals)
    # valeurs apparaissant plusieurs fois (écart exactement 0)
    exact = [(a, b) for a, b in zip(z, z[1:]) if b - a == 0.0]
    n_csv_final = sum(1 for _ in open(CSV_FINAL)) - 1
    rapport["historique"] = {"lignes_brutes": len(cands), "par_worker": par_worker,
                              "apres_ancienne_dedup": len(ancien), "mode_ancienne_dedup": mode_ancien,
                              "lignes_csv_final": n_csv_final, "paires_ecart_exactement_0": len(exact)}

    # --- cohérence des zones de chevauchement entre workers adjacents
    zones = []
    for w in range(pl["N_WORKERS"] - 1):
        lo, hi = segs[w + 1][0], segs[w][1]
        a = sorted(c.t for c in cands if c.worker == w and lo <= c.t <= hi)
        b = sorted(c.t for c in cands if c.worker == w + 1 and lo <= c.t <= hi)
        zones.append({"frontiere": f"{w}/{w+1}", "zone": [lo, hi], "n_w_bas": len(a), "n_w_haut": len(b),
                      "valeurs_w_bas": a, "valeurs_w_haut": b, "identiques": a == b})
    rapport["zones_chevauchement"] = zones

    # --- consolidation : A (stricte, sans STEP) et B (avec règle STEP lue dans le log)
    variantes = {"A_stricte_sans_STEP": ParamsConsolidation(overlap=OVERLAP_V16),
                 "B_avec_STEP_du_log": ParamsConsolidation(overlap=OVERLAP_V16, step=pl["STEP"])}
    rapport["variantes"] = {}
    for nom, p in variantes.items():
        res = consolider(cands, p)
        sorties = ecrire_resultats(res, os.path.join(sortie, nom), meta={
            "entree_sha256": {k: v for k, v in sha_avant.items() if "checkpoints" in k},
            "params_log": pl, "segments": "reconstruits (non stockés dans les CSV)"})
        compte = {s: sum(1 for d in res.decisions if d.statut == s)
                  for s in (DUPLICATE_CONFIRMED, DISTINCT, AMBIGUOUS)}
        tab = [{"groupe": d.groupe, "type": d.type_groupe, "statut": d.statut, "regle": d.regle,
                "ecart": d.ecart, "candidats": [(os.path.basename(c["source"]), c["ligne"], c["worker"], c["t"])
                                                 for c in d.candidats], "justification": d.justification}
               for d in res.decisions]
        # candidats conservés par l'ancienne méthode ?
        set_ancien = set(ancien)
        retires_par_ancienne = [t for t in vals if t not in set_ancien]
        consolides_t = {l.t for l in res.consolides}
        rapport["variantes"][nom] = {
            "lignes_lues": res.n_entree, "invalides": len(res.invalides),
            "groupes": len(res.decisions), "decisions": compte,
            "candidats_consolides": len(res.consolides),
            "statut_lignes": {s: sum(1 for l in res.consolides if l.statut_ligne == s)
                              for s in sorted({l.statut_ligne for l in res.consolides})},
            "table_decisions": tab, "sorties": {k: os.path.relpath(v, RACINE) for k, v in sorties.items()},
            "sha256_sorties": {k: sha256_fichier(v) for k, v in sorties.items()},
            "ecarts_ancienne_vs_nouvelle": {
                "ancienne": len(ancien), "nouvelle": len(res.consolides),
                "diff": len(res.consolides) - len(ancien)}}
    # vérifier écarts rapportés contre les décisions de paires proches
    paires = [d for d in rapport["variantes"]["B_avec_STEP_du_log"]["table_decisions"]
              if d["type"] == "paire_proche"]
    rapport["paires_proches_observees"] = [(d["ecart"], d["statut"]) for d in paires]
    rapport["ecarts_rapportes"] = ECARTS_RAPPORTES

    # --- présence des données brutes V13 (listage uniquement, aucun calcul)
    cal = os.path.join(RACINE, "calculs")
    v13 = sorted(d for d in os.listdir(cal) if d.startswith("v13_T5000000"))
    rapport["v13_presence"] = {d: sorted(os.listdir(os.path.join(cal, d)))[:20] for d in v13}

    rapport["sha_apres"] = shas()
    rapport["donnees_brutes_inchangees"] = (sha_avant == rapport["sha_apres"])
    with open(os.path.join(sortie, "rapport_rejeu.json"), "w") as f:
        json.dump(rapport, f, indent=1, ensure_ascii=False, default=str)
    return rapport


if __name__ == "__main__":
    r = main(sys.argv[1])
    print(json.dumps({k: v for k, v in r.items() if k not in ("sha_avant", "sha_apres",
          "zones_chevauchement", "segments_reconstruits")}, indent=1, ensure_ascii=False, default=str)[:12000])
    print("zones :", [(z["frontiere"], z["n_w_bas"], z["n_w_haut"], z["identiques"]) for z in r["zones_chevauchement"]])
    print("DONNEES BRUTES INCHANGEES :", r["donnees_brutes_inchangees"])
