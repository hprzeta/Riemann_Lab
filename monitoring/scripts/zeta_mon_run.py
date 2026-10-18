#!/usr/bin/env python3
"""
zeta_mon_run.py — Lanceur de monitoring d'un run (le point d'entrée recommandé, pour toi ET pour Claude Code).

  exec   : enveloppe une commande : démarre le suivi, lance la commande, récupère son CODE RETOUR, clôt le run.
  start  : démarre le suivi (run lancé à côté, ex. setsid nohup) ; option --pid PID pour clore à sa fin.
  stop   : clôt le run suivi (--code N = code retour du run).
  fenetres / fermer : ouvre / ferme les 3 fenêtres de graphiques (sans run).

Au démarrage : dossier  runs/<type>/<AAAAMMJJ_HHMMSS_nom>/  (type = test | prod), meta.json, fiche de session
(commande, git, turbo, CPU…), puis un SUPERVISEUR (priorité minimale) qui :
  - toutes les 5 s : écrit etat.json + etat.csv (zéros, t courant, z/s, T°/fréquence/load PC1) ;
  - si fenêtres : ouvre zeta_plot_live (zéros), zeta_plot_metrics (machines), zeta_gue_hist --live (GUE),
    en petites fenêtres rangées (jamais plein écran) ;
  - à la fin : génère rapport.md + rapport.pdf (figures, observations, fiche de session) et met à jour Monitoring-Runs.md.
Fenêtres : « auto » = oui pour un run de test, non pour un run de production (CPU saturé → risque de gel).

Exemples (PC1) :
  zeta-mon-exec --nom "T-test-5000" --type test --csv ~/projet_zeta/calculs/x/ -- ./scripts/zeta_run.sh 5000
  zeta-mon-start --nom V17-T5M --type prod ;  ... ;  zeta-mon-stop --code 0
"""
import argparse
import datetime as dt
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zeta_mon_common import (ACTIF, CALCULS, DATA, FENETRES, LOGS, ROOT, RUNS, csv_du_run, layout, lignes_workers,   # noqa: E402
                             lire_hint)

SCR = Path(__file__).resolve().parent


def maintenant():
    return dt.datetime.now().isoformat(timespec="seconds")


def lire(p):
    try:
        return Path(p).read_text().strip()
    except Exception:
        return None


def turbo_etat():
    """État du turbo CPU : intel_pstate/no_turbo (0 = turbo actif) ou cpufreq/boost (1 = actif).
    [hypothèse : suppose que zeta_turbo_on.sh agit par ce mécanisme ; non vérifié]"""
    v = lire("/sys/devices/system/cpu/intel_pstate/no_turbo")
    if v in ("0", "1"):
        return "actif (intel_pstate)" if v == "0" else "inactif (intel_pstate)"
    v = lire("/sys/devices/system/cpu/cpufreq/boost")
    if v in ("0", "1"):
        return "actif (boost)" if v == "1" else "inactif (boost)"
    return "inconnu"


def git(*a):
    try:
        r = subprocess.run(["git", "-C", str(Path.home() / "projet_zeta"), *a], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def collecter():
    """Fiche de session : état de la machine et du code au démarrage du run."""
    d = {"hote": socket.gethostname(), "noyau": platform.release(), "cpu_logiques": os.cpu_count(),
         "python": sys.version.split()[0], "turbo": turbo_etat(),
         "gouverneur": lire("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"),
         "charge_1min": round(os.getloadavg()[0], 2)}
    try:
        d["cpu"] = next(l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name"))
        mem = {l.split(":")[0]: int(l.split()[1]) for l in open("/proc/meminfo")}
        d["ram_totale_Go"] = round(mem["MemTotal"] / 1048576, 1)
        d["ram_dispo_Go"] = round(mem["MemAvailable"] / 1048576, 1)
    except Exception:
        pass
    try:
        d["disque_libre_Go"] = round(shutil.disk_usage(CALCULS if CALCULS.is_dir() else Path.home()).free / 1e9, 1)
    except Exception:
        pass
    try:
        from importlib.metadata import version
        d["paquets"] = {m: version(m) for m in ("numpy", "pandas", "matplotlib", "mpmath") if _a_version(m)}
    except Exception:
        pass
    d["git"] = {"commit": git("rev-parse", "--short", "HEAD"), "branche": git("rev-parse", "--abbrev-ref", "HEAD"),
                "fichiers_modifies": len((git("status", "--porcelain") or "").splitlines())}
    return d


def _a_version(m):
    from importlib.metadata import PackageNotFoundError, version
    try:
        version(m)
        return True
    except PackageNotFoundError:
        return False


def charger(d):
    return json.loads((Path(d) / "meta.json").read_text())


def sauver(d, meta):
    (Path(d) / "meta.json").write_text(json.dumps(meta, indent=1, default=str))


def vivant(pid):
    """Processus en vie (un zombie — terminé mais non « attendu » par son parent — compte comme mort)."""
    try:
        etat = open("/proc/%d/stat" % int(pid)).read().rsplit(")", 1)[1].split()[0]
        return etat != "Z"
    except (OSError, ValueError, TypeError, IndexError):
        return False


# ----------------------------------------------------------------------------- fenêtres
def ouvrir_fenetres(csv, apres=None):
    """Ouvre les 3 fenêtres (priorité minimale, jamais plein écran) ; retourne la liste des PID."""
    lay = layout()
    env = {k: v for k, v in os.environ.items() if k != "MPLBACKEND"}
    if os.environ.get("XDG_SESSION_TYPE") == "wayland":
        print("NB : session Wayland — la position des fenêtres peut être ignorée (Super + flèches pour les ranger).")
    cible = csv or str(CALCULS)
    ap = ["--apres", apres] if apres else []
    cmds = {
        "live": [sys.executable, str(SCR / "zeta_plot_live.py"), cible, "--colonne", "partie_imaginaire",
                 "--refresh", "2", "--geometrie", lay["live"]] + ap,
        "gue": [sys.executable, str(SCR / "zeta_gue_hist.py"), cible, "--colonne", "partie_imaginaire", "--live",
                "--refresh", "30", "--geometrie", lay["gue"]] + ap,
        "metrics": [sys.executable, str(SCR / "zeta_plot_metrics.py"), "--minutes", "15", "--refresh", "2",
                    "--geometrie", lay["metrics"]]}
    LOGS.mkdir(parents=True, exist_ok=True)
    pids = []
    for nom, cmd in cmds.items():
        with open(LOGS / ("fenetre_%s.log" % nom), "w") as lg:
            p = subprocess.Popen(cmd, env=env, stdout=lg, stderr=lg, start_new_session=True,
                                 preexec_fn=lambda: os.nice(19))
        pids.append(p.pid)
    FENETRES.write_text(json.dumps(pids))
    return pids


def fermer_fenetres():
    n = 0
    try:
        for pid in json.loads(FENETRES.read_text()):
            if vivant(pid):
                os.kill(pid, 15)
                n += 1
        FENETRES.unlink()
    except Exception:
        pass
    return n


# ----------------------------------------------------------------------------- démarrage / arrêt
def demarrer(nom, type_, csv=None, fenetres="auto", pid=None, cmd=""):
    RUNS.mkdir(parents=True, exist_ok=True)
    if ACTIF.exists():
        rel = ACTIF.read_text().strip()
        sup = lire(RUNS / rel / "superviseur.pid")
        if sup and vivant(sup):
            sys.exit("Un run est déjà suivi : %s  (le clore : zeta-mon-stop)" % rel)
        print("ancien suivi abandonné :", rel)
    hint = lire_hint()
    nom = nom or hint.get("nom") or "run"
    csv = csv or hint.get("csv")
    t0 = dt.datetime.now()
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", nom).strip("-")
    rid = t0.strftime("%Y%m%d_%H%M%S") + "_" + slug
    d = RUNS / type_ / rid
    (d / "figures").mkdir(parents=True)
    fen = fenetres == "oui" or (fenetres == "auto" and type_ == "test")
    meta = dict(id=rid, nom=nom, type=type_, t0=t0.isoformat(timespec="seconds"), t1=t0.isoformat(timespec="seconds"),
                statut="en cours", lanceur=True, cmd=cmd, csv=csv, fenetres=fen, session=collecter())
    sauver(d, meta)
    ACTIF.write_text("%s/%s" % (type_, rid))
    argv = [sys.executable, str(Path(__file__)), "_superviseur", str(d)] + (["--pid", str(pid)] if pid else [])
    with open(d / "superviseur.log", "w") as lg:
        p = subprocess.Popen(argv, stdout=lg, stderr=lg, start_new_session=True, preexec_fn=lambda: os.nice(19))
    (d / "superviseur.pid").write_text(str(p.pid))
    print("Suivi démarré : %s   [type %s, fenêtres %s]" % (d, type_, "oui" if fen else "non"))
    return d


def arreter(code=None, attendre=False, delai=600):
    if not ACTIF.exists():
        sys.exit("aucun run suivi")
    rel = ACTIF.read_text().strip()
    d = RUNS / rel
    (d / ".fin").write_text(json.dumps({"rc": code, "t": maintenant()}))
    print("Fin demandée pour", rel, "(code retour :", code, ") — génération du rapport…")
    if attendre:                                   # attend la fin du superviseur (indépendant de runs/.actif)
        t = time.time()
        sup = lire(d / "superviseur.pid")
        while sup and vivant(sup) and time.time() - t < delai:
            time.sleep(1)
        print("rapport :", d / "rapport.md" if (d / "rapport.md").exists() else "(pas encore / voir superviseur.log)")
    return d


# ----------------------------------------------------------------------------- superviseur
def derniere_mesure_pc1():
    """(temp °C, MHz, load) de PC1 d'après la fin du CSV machines du jour."""
    f = DATA / ("cluster_metrics_%s.csv" % dt.date.today().strftime("%Y%m%d"))
    try:
        with open(f, "rb") as fh:
            fh.seek(0, 2)
            fh.seek(max(0, fh.tell() - 2500))
            lignes = fh.read().decode(errors="replace").splitlines()[1:]
        for l in reversed(lignes):
            c = l.split(",")
            if len(c) == 9 and c[1] == "PC1" and c[8] == "1":
                return [float(x) if x else None for x in (c[3], c[7], c[4])]
    except Exception:
        pass
    return [None, None, None]


def superviseur(d, pid=None):
    os.environ["MPLBACKEND"] = "Agg"          # ce processus ne dessine rien ; les fenêtres sont des processus séparés
    import zeta_plot_live as zl
    d = Path(d)
    meta = charger(d)
    t0 = dt.datetime.fromisoformat(meta["t0"])
    print(maintenant(), "superviseur", meta["id"], "| pid suivi :", pid, flush=True)
    if meta.get("fenetres"):
        try:
            apres = meta["t0"] if not (meta.get("csv") and Path(os.path.expanduser(meta["csv"])).is_file()) else None
            meta["fenetres_pids"] = ouvrir_fenetres(meta.get("csv"), apres)
            sauver(d, meta)
            print(maintenant(), "fenêtres ouvertes :", meta["fenetres_pids"], flush=True)
        except Exception:
            print(traceback.format_exc(), flush=True)
    hist = d / "etat.csv"
    hist.write_text("horodatage,zeros,t_max,zps,temp_pc1,freq_pc1,load_pc1\n")
    lecteur, csvp, n_prev, t_prev, debut = None, None, 0, time.time(), time.time()
    nw_prev, cache_w = None, {}          # débit : total des zéros de TOUS les workers (None = pas de fichiers de worker)
    prochain = 0
    while True:
        if (d / ".fin").exists() or (pid and not vivant(pid)) or time.time() - debut > 12 * 3600:
            break
        if time.time() >= prochain:
            prochain = time.time() + 5
            try:
                if csvp is None or not os.path.exists(csvp):
                    csvp, lecteur = csv_du_run(meta, t0), None
                if csvp:
                    premier = lecteur is None
                    if premier:
                        lecteur = zl.LecteurZeros(csvp)
                    t = lecteur.maj()
                    n = len(t)
                    tm = time.time()
                    res_w = lignes_workers(csvp, cache_w)
                    nw, tmax_w = res_w if res_w is not None else (None, None)
                    if nw is not None:                      # run multi-workers : débit = croissance du total des workers
                        zps = float("nan") if nw_prev is None else max(nw - nw_prev, 0) / max(tm - t_prev, 1e-6)
                        nw_prev = nw
                        n = max(n, nw)                      # compteur « zéros » : au moins le total des workers
                    else:
                        zps = float("nan") if premier else (n - n_prev) / max(tm - t_prev, 1e-6)   # 1er passage : pas de débit
                    n_prev, t_prev = n, tm
                    tmax = float(t[-1]) if len(t) else None
                    if tmax_w is not None:                  # t_max = le plus grand parmi tous les workers
                        tmax = tmax_w if tmax is None else max(tmax, tmax_w)
                    T, F, L = derniere_mesure_pc1()
                    etat = dict(horodatage=maintenant(), csv=os.path.basename(csvp), zeros=n, t_max=tmax,
                                zps=round(zps, 1) if zps == zps else None, temp_pc1=T, freq_pc1=F, load_pc1=L, turbo=turbo_etat())
                    (d / "etat.json").write_text(json.dumps(etat))
                    etat["zps"] = None if zps != zps else etat["zps"]
                    (d / "etat.json").write_text(json.dumps(etat))
                    with open(hist, "a") as fh:
                        fh.write("%s,%d,%s,%s,%s,%s,%s\n" % (etat["horodatage"], n, "" if tmax is None else "%.3f" % tmax,
                                                             "" if zps != zps else "%.1f" % zps, *["" if x is None else x for x in (T, F, L)]))
            except Exception as e:
                print(maintenant(), "état ignoré :", e, flush=True)
        time.sleep(1)
    # ---- fin du run
    rc = None
    try:
        rc = json.loads((d / ".fin").read_text()).get("rc")
    except Exception:
        pass
    meta = charger(d)
    meta.update(t1=maintenant(), rc=rc, session_fin=dict(turbo=turbo_etat(), charge_1min=round(os.getloadavg()[0], 2)))
    sauver(d, meta)
    print(maintenant(), "RUN TERMINÉ | code retour :", rc, "| rapport…", flush=True)
    try:
        import zeta_run_report as rr
        md, pdf_ok = rr.rapport(d, "fr")
        print(maintenant(), "rapport :", d / md, "(PDF %s)" % ("oui" if pdf_ok else "non"), flush=True)
    except Exception:
        (d / "erreur.txt").write_text(traceback.format_exc())
        print(maintenant(), "ERREUR rapport — voir erreur.txt", flush=True)
    if lire(ACTIF) == "%s/%s" % (meta.get("type"), meta["id"]):      # ne pas effacer le marqueur d'un autre run
        ACTIF.unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    for nom in ("exec", "start"):
        p = sp.add_parser(nom)
        p.add_argument("--nom", default=None)
        p.add_argument("--type", default="test", choices=["test", "prod"])
        p.add_argument("--csv", default=None, help="CSV (ou dossier) des zéros de ce run")
        p.add_argument("--fenetres", default="auto", choices=["auto", "oui", "non"])
        if nom == "start":
            p.add_argument("--pid", type=int, default=None, help="PID du run : clôture automatique à sa fin")
        else:
            p.add_argument("commande", nargs=argparse.REMAINDER)
    p = sp.add_parser("stop")
    p.add_argument("--code", type=int, default=None)
    p.add_argument("--attendre", action="store_true")
    p = sp.add_parser("fenetres")
    p.add_argument("--csv", default=None)
    sp.add_parser("fermer")
    p = sp.add_parser("_superviseur")
    p.add_argument("dossier")
    p.add_argument("--pid", type=int, default=None)
    a = ap.parse_args()

    if a.cmd == "_superviseur":
        superviseur(a.dossier, a.pid)
    elif a.cmd == "start":
        demarrer(a.nom, a.type, a.csv, a.fenetres, a.pid)
    elif a.cmd == "exec":
        cmd = [c for c in a.commande if c != "--"] if a.commande and a.commande[0] == "--" else a.commande
        if not cmd:
            sys.exit("usage : exec --nom N --type test|prod [--csv X] -- commande ...")
        demarrer(a.nom, a.type, a.csv, a.fenetres, None, " ".join(cmd))
        try:
            rc = subprocess.call(cmd)
        except KeyboardInterrupt:
            rc = 130
        arreter(rc, attendre=True)
        sys.exit(rc)
    elif a.cmd == "stop":
        arreter(a.code, a.attendre)
    elif a.cmd == "fenetres":
        print("fenêtres :", ouvrir_fenetres(a.csv))
    elif a.cmd == "fermer":
        print(fermer_fenetres(), "fenêtre(s) fermée(s)")


if __name__ == "__main__":
    main()

# zeta_mon_run.py · hprzeta · MAJ 2026-10-17 · 351 lignes
