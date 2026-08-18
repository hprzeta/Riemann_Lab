#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zeta_run_progress.py — Dashboard live d'un run distribué zeta_distribute.py
══════════════════════════════════════════════════════════════════════════
Affiche en temps réel (curses) :
  - répartition cible PC1/PC2 (bâtonnet empilé, proportion de N(T_MAX))
  - progression réelle (zéros trouvés / zéros assignés) par machine
  - CPU / RAM / Disque de chaque machine (PC1 local, PC2 via SSH)
  - détail par worker (touche 'd' pour afficher/masquer)

Usage :
    python scripts/zeta_run_progress.py

Touches : q = quitter · d = afficher/masquer le détail par worker
Auteur : hprzeta — Projet Hypothèse de Riemann
"""

import curses
import os
import re
import subprocess
import threading
import time
import glob
from pathlib import Path
from datetime import datetime

PROJET_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = PROJET_DIR / "logs"

PC2_HOST = "192.168.1.52"
PC2_USER = "hprzeta"
PC2_KEY = "~/.ssh/id_acer"
REFRESH = 4  # secondes entre deux sondes CPU/RAM/disque

# ── Commande distante : CPU (delta /proc/stat), RAM (/proc/meminfo), disque (statvfs)
CMD_STATS = ("python3 -c \""
    "import os,time;"
    "s1=open('/proc/stat').readline().split();"
    "time.sleep(0.4);"
    "s2=open('/proc/stat').readline().split();"
    "d=[int(b)-int(a) for a,b in zip(s1[1:],s2[1:])];"
    "idle=d[3];total=sum(d);"
    "cpu=round(100*(1-idle/total),1) if total else 0;"
    "m=open('/proc/meminfo').read();"
    "mt=int([l for l in m.split(chr(10)) if 'MemTotal' in l][0].split()[1]);"
    "ma=int([l for l in m.split(chr(10)) if 'MemAvailable' in l][0].split()[1]);"
    "mu=round(100*(mt-ma)/mt,1);"
    "sv=os.statvfs('/');"
    "dpct=round(100*(1-sv.f_bavail/sv.f_blocks),1) if sv.f_blocks else 0;"
    "print('{0}|{1}|{2}'.format(cpu,mu,dpct));"
    "\"")

LOG_RE = re.compile(r"\[Worker (\d+)\] z[ée]ro #(\d+) à t=([\d.]+) — ([\d.]+)s")


def ssh_or_local(host, cmd):
    if host == "localhost":
        proc = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=8)
    else:
        key = os.path.expanduser(PC2_KEY)
        args = ["ssh", "-o", "ConnectTimeout=6", "-o", "BatchMode=yes",
                "-o", "IdentitiesOnly=yes", "-i", key, f"{PC2_USER}@{host}", cmd]
        proc = subprocess.run(args, capture_output=True, text=True, timeout=10)
    return proc.stdout.strip(), proc.returncode


def tail_lines(path, n=3000, chunk=16384):
    """Lit les ~n dernières lignes d'un fichier sans le charger entièrement (logs en croissance continue)."""
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            data = b""
            while size > 0 and data.count(b"\n") <= n:
                step = min(chunk, size)
                size -= step
                f.seek(size)
                data = f.read(step) + data
            return [l.decode("utf-8", "ignore") for l in data.splitlines()[-n:]]
    except FileNotFoundError:
        return []


def latest_file(pattern):
    files = glob.glob(str(LOG_DIR / pattern))
    return max(files, key=os.path.getmtime) if files else None


def parse_master_log(path):
    """Extrait T_MAX, N(T_MAX) total et la répartition cible PC1/PC2 (N≈...) du log maître."""
    if not path:
        return None
    text = Path(path).read_text(errors="ignore")
    n_total = re.search(r"N\(T_MAX\)\s*≈\s*(\d+)", text)
    segs = re.findall(r"N≈(\d+)", text)
    if len(segs) < 2 or not n_total:
        return None
    return {"n_total": int(n_total.group(1)), "pc1_n": int(segs[0]), "pc2_n": int(segs[1])}


def parse_solo_header(path):
    """Extrait T_MAX et N total du log d'un run solo (zeta_run.sh, PAS zeta_distribute.py) —
    reconnaît le bloc « Configuration » imprimé par saisir_parametres() dans
    compute_zeros_vNN.py (mode interactif, PC1 seul, aucun split PC2)."""
    if not path:
        return None
    text = Path(path).read_text(errors="ignore")
    n_total = re.search(r"N zéros\s*≈\s*(\d+)", text)
    t_max = re.search(r"^\s*T_MAX\s*=\s*(\d+)", text, re.MULTILINE)
    if not n_total:
        return None
    return {"n_total": int(n_total.group(1)), "t_max": int(t_max.group(1)) if t_max else None}


SEG_RE = re.compile(r"Worker (\d+)\s*:\s*\[([\d.]+),\s*([\d.]+)\]")


def parse_segments(path):
    """Bornes [a, b] par worker, telles qu'imprimées au lancement (identique pour
    un run solo ou un sous-run distribué — même code de segmentation)."""
    if not path:
        return {}
    try:
        text = Path(path).read_text(errors="ignore")
    except FileNotFoundError:
        return {}
    return {int(w): (float(a), float(b)) for w, a, b in SEG_RE.findall(text)}


def eta_sqrt_weighted(segments, workers, elapsed_now):
    """ETA pondérée par le coût réel par zéro (~√t, nombre de termes Riemann-Siegel
    croissant avec t) au lieu d'une simple règle de trois sur le débit moyen.

    Le run se termine quand le PIRE worker (le plus avancé en t, donc le plus
    lent par zéro à partir de maintenant) termine son segment — le temps restant
    de chaque worker est extrapolé via l'intégrale fermée du coût cumulé :
        coût(a→b) ∝ ∫[a,b] √t dt = (2/3)(b^1.5 − a^1.5)
    Retourne None si aucun worker n'a assez de données (démarrage), auquel cas
    l'appelant doit retomber sur l'ETA linéaire classique.
    """
    worst_total = None
    for w, (a, b) in segments.items():
        if w not in workers or b <= a:
            continue
        _, t_now, elapsed = workers[w]
        if elapsed <= 0 or t_now <= a:
            continue
        done_area = t_now ** 1.5 - a ** 1.5
        remain_area = max(b ** 1.5 - t_now ** 1.5, 0.0)
        if done_area <= 0:
            continue
        total_w = elapsed + elapsed * remain_area / done_area
        if worst_total is None or total_w > worst_total:
            worst_total = total_w
    if worst_total is None:
        return None
    return max(worst_total - elapsed_now, 0.0)


_worker_cache = {}


def parse_worker_progress(path):
    """Dernier état connu (count, t, elapsed) par worker.

    Mis en cache par fichier : un worker avec un petit segment (ex. bande de
    calibration sur PC2) sort vite de la fenêtre `tail_lines` une fois les
    autres workers actifs ; sans cache son dernier compte serait perdu et le
    total sous-estimé.
    """
    cache = _worker_cache.setdefault(path, {})
    for line in tail_lines(path):
        m = LOG_RE.search(line)
        if m:
            w, count, t, elapsed = m.groups()
            w, count = int(w), int(count)
            prev = cache.get(w)
            if prev is None or count >= prev[0]:
                cache[w] = (count, float(t), float(elapsed))
    return cache


state = {"pc1": {"cpu": None, "ram": None, "disk": None, "status": "init"},
         "pc2": {"cpu": None, "ram": None, "disk": None, "status": "init"}}
lock = threading.Lock()


def poll(name, host):
    while True:
        try:
            out, rc = ssh_or_local(host, CMD_STATS)
            cpu, ram, disk = (float(x) for x in out.split("|"))
            with lock:
                state[name].update(cpu=cpu, ram=ram, disk=disk, status="ok")
        except Exception as e:
            with lock:
                state[name].update(status="err:" + str(e)[:30])
        time.sleep(REFRESH)


PAIR = {}


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1); PAIR["pc1"] = 1
    curses.init_pair(2, curses.COLOR_YELLOW, -1); PAIR["pc2"] = 2
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN); PAIR["ok"] = 3
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW); PAIR["warn"] = 4
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_RED); PAIR["crit"] = 5
    curses.init_pair(6, curses.COLOR_WHITE, -1); PAIR["fg"] = 6
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE); PAIR["bg"] = 7


def bar(stdscr, y, x, pct, width, color_pair, label=""):
    pct = 0 if pct is None else max(0, min(100, pct))
    filled = int(width * pct / 100)
    stdscr.addstr(y, x, "[", curses.color_pair(PAIR["fg"]))
    stdscr.addstr(y, x + 1, "█" * filled, curses.color_pair(color_pair))
    stdscr.addstr(y, x + 1 + filled, "░" * (width - filled), curses.color_pair(PAIR["bg"]))
    stdscr.addstr(y, x + 1 + width, f"] {pct:5.1f}% {label}", curses.color_pair(PAIR["fg"]))


def load_pct_color(pct):
    if pct is None:
        return PAIR["fg"]
    return PAIR["ok"] if pct < 60 else (PAIR["warn"] if pct < 85 else PAIR["crit"])


def draw(stdscr):
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)
    show_detail = False
    while True:
        # ── Détection du mode : run distribué (zeta_distribute.py, PC1+PC2) vs
        # run solo (zeta_run.sh, PC1 seul sur la totalité de T_MAX). On compare
        # les mtimes des 2 familles de logs — celle la plus récemment modifiée
        # est forcément le run actif ; l'autre est un résidu d'un run antérieur
        # (potentiellement vieux de plusieurs jours) qu'il ne faut pas confondre
        # avec des données live (piège corrigé le 17/08 : le dashboard affichait
        # sinon la progression figée d'un ancien run v15 distribué du 04/08).
        distribute_master_path = latest_file("distribute_T*_*.log")
        solo_path = latest_file("run_T*_*.log")
        solo_mtime = os.path.getmtime(solo_path) if solo_path else -1
        dist_mtime = os.path.getmtime(distribute_master_path) if distribute_master_path else -1
        solo_mode = solo_path is not None and solo_mtime > dist_mtime

        if solo_mode:
            solo_hdr = parse_solo_header(solo_path)
            master = {"n_total": solo_hdr["n_total"], "pc1_n": solo_hdr["n_total"], "pc2_n": 0} if solo_hdr else None
            pc1_log = solo_path
            pc2_log = None
        else:
            master = parse_master_log(distribute_master_path)
            pc1_log = latest_file("distribute_pc1_*.log")
            pc2_log = latest_file("distribute_pc2_*.log")

        w1 = parse_worker_progress(pc1_log) if pc1_log else {}
        w2 = parse_worker_progress(pc2_log) if pc2_log else {}
        seg1 = parse_segments(pc1_log) if pc1_log else {}
        seg2 = parse_segments(pc2_log) if pc2_log else {}
        done1 = sum(c for c, _, _ in w1.values())
        done2 = sum(c for c, _, _ in w2.values())
        el1 = max((e for _, _, e in w1.values()), default=0)
        el2 = max((e for _, _, e in w2.values()), default=0)

        stdscr.erase()
        h, w = stdscr.getmaxyx()
        title = ("  ζ  ZETA RUN PROGRESS — PC1 SOLO (v16)  ζ  " if solo_mode
                  else "  ζ  ZETA RUN PROGRESS — PC1/PC2  ζ  ")
        stdscr.addstr(0, max(0, (w - len(title)) // 2), title, curses.color_pair(PAIR["pc1"]) | curses.A_BOLD)
        stdscr.addstr(1, 2, f"Refresh:{REFRESH}s | {datetime.now().strftime('%H:%M:%S')} | q=quitter d=détail workers", curses.color_pair(PAIR["fg"]))
        stdscr.addstr(2, 0, "─" * w, curses.color_pair(PAIR["fg"]))
        row = 3

        if master and solo_mode:
            n_total = n1 = master["n_total"]
            n2 = None
            stdscr.addstr(row, 2, f"Run SOLO PC1 (N(T_MAX)≈{n_total}) — PC2 non utilisé (v16 indisponible sur PC2) :",
                          curses.color_pair(PAIR["fg"]) | curses.A_BOLD)
            row += 1
            width = min(60, w - 14)
            stdscr.addstr(row, 4, "[", curses.color_pair(PAIR["fg"]))
            stdscr.addstr(row, 5, "█" * width, curses.color_pair(PAIR["pc1"]))
            stdscr.addstr(row, 5 + width, "]", curses.color_pair(PAIR["fg"]))
            row += 1
            stdscr.addstr(row, 4, f"PC1 100.0% (N≈{n1}) — totalité de T_MAX", curses.color_pair(PAIR["pc1"]) | curses.A_BOLD)
            row += 2
        elif master:
            n_total, n1, n2 = master["n_total"], master["pc1_n"], master["pc2_n"]
            stdscr.addstr(row, 2, f"Répartition cible (N(T_MAX)≈{n_total}) :", curses.color_pair(PAIR["fg"]) | curses.A_BOLD)
            row += 1
            width = min(60, w - 14)
            f1 = int(width * n1 / n_total)
            stdscr.addstr(row, 4, "[", curses.color_pair(PAIR["fg"]))
            stdscr.addstr(row, 5, "█" * f1, curses.color_pair(PAIR["pc1"]))
            stdscr.addstr(row, 5 + f1, "█" * (width - f1), curses.color_pair(PAIR["pc2"]))
            stdscr.addstr(row, 5 + width, "]", curses.color_pair(PAIR["fg"]))
            row += 1
            stdscr.addstr(row, 4, f"PC1 {100*n1/n_total:4.1f}% (N≈{n1})", curses.color_pair(PAIR["pc1"]) | curses.A_BOLD)
            stdscr.addstr(row, 30, f"PC2 {100*n2/n_total:4.1f}% (N≈{n2})", curses.color_pair(PAIR["pc2"]) | curses.A_BOLD)
            row += 2
        else:
            stdscr.addstr(row, 2, "Aucun run détecté (logs/distribute_T*.log et run_T*.log absents).", curses.color_pair(PAIR["warn"]))
            row += 2
            n1 = n2 = None

        for label, name, done, n_assigned, elapsed, host in (
            ("PC1 (zeta-lab, local)", "pc1", done1, n1, el1, "localhost"),
            ("PC2 (zeta-calc-second, SSH)", "pc2", done2, n2, el2, PC2_HOST),
        ):
            if solo_mode and name == "pc2":
                stdscr.addstr(row, 2, label, curses.color_pair(PAIR["fg"]) | curses.A_DIM)
                row += 1
                stdscr.addstr(row, 4, "non utilisé pour ce run (solo PC1, v16 pas dispo sur PC2)",
                              curses.color_pair(PAIR["fg"]) | curses.A_DIM)
                row += 2
                continue
            s = state[name]
            cp = curses.color_pair(PAIR[name]) | curses.A_BOLD
            stdscr.addstr(row, 2, label, cp)
            row += 1
            if n_assigned:
                pct = 100 * done / n_assigned
                segs = seg1 if name == "pc1" else seg2
                workers_dict = w1 if name == "pc1" else w2
                n_reporting = len(set(segs.keys()) & set(workers_dict.keys()))
                n_segs = len(segs)
                eta_w = eta_sqrt_weighted(segs, workers_dict, elapsed)
                if eta_w is not None and n_segs and n_reporting == n_segs:
                    # Tous les workers ont au moins 1 point de mesure : le "pire
                    # worker" (max sur tous) est une estimation fiable.
                    eta_label = f"ETA(√t) {eta_w/60:.1f} min"
                elif eta_w is not None:
                    # Certains workers n'ont encore rien loggé (phase de scan
                    # initiale, cf. comportement documenté v15 T=5M) — le max
                    # ne porte que sur les workers déjà démarrés, donc sous-estime
                    # potentiellement le vrai pire cas.
                    eta_label = f"ETA(√t, {n_reporting}/{n_segs} workers démarrés) ≥{eta_w/60:.1f} min"
                else:
                    eta_lin = (elapsed / done * (n_assigned - done)) if done > 0 else 0
                    eta_label = f"ETA(lin, optimiste) {eta_lin/60:.1f} min"
                bar(stdscr, row, 4, pct, 30, PAIR[name], f"zéros {done}/{n_assigned} · {eta_label}")
            else:
                stdscr.addstr(row, 4, "en attente de données...", curses.color_pair(PAIR["fg"]))
            row += 1
            stdscr.addstr(row, 4, "CPU ", curses.color_pair(PAIR["fg"]) | curses.A_BOLD)
            bar(stdscr, row, 8, s["cpu"], 22, load_pct_color(s["cpu"]))
            row += 1
            stdscr.addstr(row, 4, "RAM ", curses.color_pair(PAIR["fg"]) | curses.A_BOLD)
            bar(stdscr, row, 8, s["ram"], 22, load_pct_color(s["ram"]))
            row += 1
            stdscr.addstr(row, 4, "DSK ", curses.color_pair(PAIR["fg"]) | curses.A_BOLD)
            bar(stdscr, row, 8, s["disk"], 22, load_pct_color(s["disk"]))
            row += 1
            if s["status"] != "ok":
                stdscr.addstr(row, 4, f"⚠ {s['status']}", curses.color_pair(PAIR["crit"]))
                row += 1
            row += 1
            if row >= h - 3:
                break

        if show_detail and row < h - 3:
            stdscr.addstr(row, 2, "Détail workers (count @ t — elapsed)", curses.color_pair(PAIR["fg"]) | curses.A_BOLD)
            row += 1
            for name, workers, cp in (("PC1", w1, PAIR["pc1"]), ("PC2", w2, PAIR["pc2"])):
                if row >= h - 1:
                    break
                line = f"{name}: " + "  ".join(f"W{k}:#{v[0]}@t={v[1]:.0f}" for k, v in sorted(workers.items()))
                stdscr.addstr(row, 2, line[:w - 4], curses.color_pair(cp))
                row += 1

        footer = " zeta_run_progress.py · hprzeta · q=quitter d=détail "
        try:
            stdscr.addstr(h - 1, max(0, (w - len(footer)) // 2), footer, curses.color_pair(PAIR["fg"]))
        except curses.error:
            pass
        stdscr.refresh()

        ch = stdscr.getch()
        if ch in (ord("q"), ord("Q")):
            break
        if ch in (ord("d"), ord("D")):
            show_detail = not show_detail
        time.sleep(1)


def main():
    threading.Thread(target=poll, args=("pc1", "localhost"), daemon=True).start()
    threading.Thread(target=poll, args=("pc2", PC2_HOST), daemon=True).start()
    curses.wrapper(draw)


if __name__ == "__main__":
    main()
