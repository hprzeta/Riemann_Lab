#!/usr/bin/env python3
"""
zeta_run_watch.py — Détecte AUTOMATIQUEMENT qu'un run de zéros tourne sur PC1 (quel que soit
celui qui le lance : toi ou Claude Code), l'enregistre, et à la fin génère le rapport
(graphiques + commentaires, MD + PDF) et met à jour Monitoring-Runs.md.

Détection : un processus dont la ligne de commande contient le motif --pattern (défaut « compute_zeros »).
Début du run  = heure de démarrage du plus ancien processus détecté.
Fin du run    = plus aucun processus pendant --confirm sondages consécutifs.
CSV des zéros : celui donné par `zeta-run-hint NOM CSV` (avant le run) ; sinon le CSV le plus récemment
modifié sous ~/projet_zeta/calculs pendant le run.

Rôle : FILET DE SÉCURITÉ pour les runs lancés SANS le lanceur (zeta_mon_run.py) : il ne fait que le rapport
(pas de fenêtres). Si un run est déjà suivi par le lanceur (runs/.actif), il ne fait rien.
Limite : sondage toutes les 2 s → un run de moins de ~2 s peut être manqué (utiliser zeta-mon-exec).

Usage (PC1) — via l'alias :  zeta-mon-on      (lance aussi le logger 1 s)
  ou :  nice -n 19 python zeta_run_watch.py [--pattern compute_zeros] [--poll 5] [--confirm 3]
Lecture seule sur le run : ne le touche pas, ne lance aucune fenêtre.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zeta_mon_common import ACTIF, ROOT, RUNS, csv_du_run, lire_hint   # noqa: E402

EXCLUS = {"bash", "sh", "zsh", "dash", "vim", "vi", "nano", "less", "more", "cat", "tail", "head", "grep",
          "rg", "git", "pgrep", "pkill", "ssh", "tmux", "screen", "sudo", "watch", "tee", "timeout", "claude", "node"}


def log(*a):
    print(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), *a, flush=True)


def processus(motif):
    """[(pid, ligne de commande)] des processus de calcul (hors outils, éditeurs, shells, ce script)."""
    rx, moi, res = re.compile(motif), os.getpid(), []
    for d in os.listdir("/proc"):
        if not d.isdigit() or int(d) == moi:
            continue
        try:
            argv = [a.decode(errors="replace") for a in open("/proc/%s/cmdline" % d, "rb").read().split(b"\0") if a]
        except OSError:
            continue
        if not argv or os.path.basename(argv[0]) in EXCLUS:
            continue
        ligne = " ".join(argv)
        if any(x in ligne for x in ("zeta_run_watch", "zeta_log_metrics", "zeta_run_report", "zeta_plot_", "zeta_mon_run", "zeta_gue_hist")):
            continue
        if rx.search(ligne):
            res.append((int(d), ligne))
    return res


def debut_proc(pid):
    """Heure de démarrage d'un processus (champ 22 de /proc/PID/stat + btime)."""
    try:
        ticks = int(open("/proc/%d/stat" % pid).read().rsplit(")", 1)[1].split()[19])
        btime = next(int(l.split()[1]) for l in open("/proc/stat") if l.startswith("btime"))
        return dt.datetime.fromtimestamp(btime + ticks / os.sysconf("SC_CLK_TCK"))
    except Exception:
        return dt.datetime.now()


def nom_depuis(ligne):
    for tok in ligne.split():
        if tok.endswith(".py"):
            return Path(tok).stem
    return Path(ligne.split()[0]).name


def demarrer(procs):
    t0 = min(debut_proc(p) for p, _ in procs)
    hint = lire_hint()
    nom = hint.get("nom") or nom_depuis(procs[0][1])
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", nom).strip("-")
    rid = t0.strftime("%Y%m%d_%H%M%S") + "_" + slug
    d = RUNS / "auto" / rid
    (d / "figures").mkdir(parents=True, exist_ok=True)
    meta = dict(id=rid, nom=nom, type="auto", t0=t0.isoformat(timespec="seconds"), t1=dt.datetime.now().isoformat(timespec="seconds"),
                statut="en cours", cmd=procs[0][1], csv=hint.get("csv"), pids=[p for p, _ in procs])
    (d / "meta.json").write_text(json.dumps(meta, indent=1))
    ACTIF.write_text("auto/" + rid)
    log("RUN DÉTECTÉ (sans lanceur) :", rid, "| pids", meta["pids"])
    try:
        import zeta_run_report as rr
        rr.maj_index()
    except Exception:
        log("index non mis à jour :", traceback.format_exc(limit=1))
    return "auto/" + rid


def terminer(rid, dernier_vu):
    d = RUNS / rid
    meta = json.loads((d / "meta.json").read_text())
    t0 = dt.datetime.fromisoformat(meta["t0"])
    t1 = dernier_vu
    meta["t1"] = t1.isoformat(timespec="seconds")
    meta["csv"] = meta.get("csv") or csv_du_run(meta, t0, t1)
    (d / "meta.json").write_text(json.dumps(meta, indent=1))
    log("RUN TERMINÉ :", rid, "| csv :", meta["csv"], "| génération du rapport…")
    try:
        import zeta_run_report as rr
        md, pdf_ok = rr.rapport(d, "fr")
        log("rapport :", d / md, "(PDF %s)" % ("oui" if pdf_ok else "non"))
    except Exception:
        (d / "erreur.txt").write_text(traceback.format_exc())
        log("ERREUR rapport — voir", d / "erreur.txt")
    ACTIF.unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", default="compute_zeros", help="regex cherchée dans la ligne de commande")
    ap.add_argument("--poll", type=float, default=2.0)
    ap.add_argument("--confirm", type=int, default=3, help="sondages vides consécutifs = run terminé")
    a = ap.parse_args()
    RUNS.mkdir(parents=True, exist_ok=True)
    actif = None
    if ACTIF.exists():                                                 # reprise après redémarrage du watcher
        try:
            m = json.loads((RUNS / ACTIF.read_text().strip() / "meta.json").read_text())
            actif = None if m.get("lanceur") else ACTIF.read_text().strip()
        except Exception:
            actif = None
    vide, vu = 0, dt.datetime.now()
    log("watcher actif | motif =", a.pattern, "| racine =", ROOT, "| run repris :", actif)
    while True:
        try:
            if actif is None and ACTIF.exists():              # run suivi par le lanceur (zeta-mon-exec/start) :
                time.sleep(a.poll)                            # il gère tout, le watcher reste en retrait
                continue
            procs = processus(a.pattern)
            if procs:
                vide, vu = 0, dt.datetime.now()
                if actif is None:
                    actif = demarrer(procs)
            elif actif is not None:
                vide += 1
                if vide >= a.confirm:
                    terminer(actif, vu)
                    actif, vide = None, 0
        except Exception:
            log("erreur :", traceback.format_exc(limit=2))
        time.sleep(a.poll)


if __name__ == "__main__":
    main()

# zeta_run_watch.py · hprzeta · MAJ 2026-10-17 · 158 lignes
