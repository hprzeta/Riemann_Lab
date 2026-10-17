#!/usr/bin/env python3
"""
zeta_log_metrics.py — Enregistre toutes les N secondes les mesures des 5 machines
du cluster (température CPU, fréquence, charge, RAM) dans un CSV.
Lecture seule sur les machines distantes (commandes sysctl / cat / awk, rien n'est modifié).

Pourquoi : voir l'évolution PENDANT un run (ex. la fréquence PC1 qui passe de 3,5 à 3,0 GHz)
et la comparer à la température. Le graphique est fait par zeta_plot_metrics.py.

Usage (PC1) — via les alias :  zeta-mon-on  /  zeta-mon-off
  ou :  python zeta_log_metrics.py --test      # 1 mesure affichée, rien d'écrit
CSV : ~/projet_zeta/monitoring/data/cluster_metrics_AAAAMMJJ.csv (une ligne / machine / seconde).
SSH multiplexé (ControlMaster) pour tenir 1 s sans surcharger ; si PC1 sature : --intervalle 2.

Hypothèses à vérifier avec --test (adapter NOEUDS si besoin) :
  - alias SSH : zeta-calc-second, zeta-backup, zeta-secure, zeta-monitor (PC5, alias supposé)
  - PC4 = OpenBSD (sysctl) ; PC4 n'a pas de mesure de RAM (colonne vide)
"""
import argparse
import csv
import datetime
import math
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

from zeta_mon_common import DATA

# (nom, hôte, alias ssh ou None si local, système)
NOEUDS = [
    ("PC1", "zeta-lab", None, "linux"),
    ("PC2", "zeta-calc-second", "zeta-calc-second", "linux"),
    ("PC3", "zeta-backup", "zeta-backup", "linux"),
    ("PC4", "zeta-secure", "zeta-secure", "openbsd"),
    ("PC5", "zeta-monitor", "zeta-monitor", "linux"),
]

NAN = float("nan")

# Sortie attendue : "<température m°C> <load1> <RAM totale Mo> <RAM utilisée Mo> <fréq kHz>"
CMD_LINUX = (
    r'''t=""; for d in /sys/class/hwmon/hwmon*; do n=$(cat "$d/name" 2>/dev/null); '''
    r'''case "$n" in coretemp|k10temp|k8temp|cpu_thermal) '''
    r'''v=$(cat "$d"/temp*_input 2>/dev/null | sort -n | tail -1); [ -n "$v" ] && t=$v;; esac; done; '''
    r'''[ -z "$t" ] && t=$(cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null | sort -n | tail -1); '''
    r'''l=$(cut -d" " -f1 /proc/loadavg); '''
    r'''m=$(awk '/^MemTotal/{t=$2} /^MemAvailable/{a=$2} END{if(t>0 && a>0) printf "%d %d", t/1024, (t-a)/1024}' /proc/meminfo); '''
    r'''f=$(cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq 2>/dev/null | sort -n | tail -1); '''
    r'''echo "${t:-nan} ${l:-nan} ${m:-nan nan} ${f:-nan}"'''
)

CMD_OPENBSD = (
    r'''t=$(sysctl -n hw.sensors.cpu0.temp0 2>/dev/null | awk '{printf "%d", $1*1000}'); '''
    r'''[ -z "$t" ] && t=$(sysctl hw.sensors 2>/dev/null | grep -i temp | head -1 '''
    r'''| sed 's/.*=\([0-9.]*\) degC.*/\1/' | awk '{printf "%d", $1*1000}'); '''
    r'''l=$(sysctl -n vm.loadavg | awk '{print $1}'); '''
    r'''f=$(sysctl -n hw.cpuspeed 2>/dev/null | awk '{print $1*1000}'); '''
    r'''echo "${t:-nan} ${l:-nan} nan nan ${f:-nan}"'''
)

ENTETE = ["horodatage", "machine", "hote", "temp_c", "load1", "ram_pct", "ram_mo", "freq_mhz", "ok"]


def _f(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else NAN
    except (TypeError, ValueError):
        return NAN


def parser(sortie):
    """'45000 1.2 7800 1300 3000000' -> (temp °C, load1, RAM %, RAM Mo, fréq MHz)."""
    p = sortie.split()
    if len(p) != 5:
        raise ValueError("sortie inattendue : %r" % sortie[:60])
    t, load, mt, mu, f = (_f(x) for x in p)
    temp = t / 1000.0
    if not (0 < temp < 120):          # filtre les valeurs aberrantes ET les nan
        temp = NAN
    ram_pct = 100.0 * mu / mt if (mt > 0 and not math.isnan(mu)) else NAN
    return temp, load, ram_pct, mu, f / 1000.0


def mesurer(noeud):
    nom, hote, alias, systeme = noeud
    cmd = CMD_OPENBSD if systeme == "openbsd" else CMD_LINUX
    argv = (["sh", "-c", cmd] if alias is None else
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=4",
             # connexion SSH partagée (évite 1 handshake par seconde) :
             "-o", "ControlMaster=auto", "-o", "ControlPersist=120",
             "-o", "ControlPath=~/.ssh/zeta_cm_%C", alias, cmd])
    base = dict(machine=nom, hote=hote, temp_c=NAN, load1=NAN, ram_pct=NAN,
                ram_mo=NAN, freq_mhz=NAN, ok=0, err="")
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=12)
        if r.returncode != 0:
            raise RuntimeError((r.stderr or "code %d" % r.returncode).strip()[:80])
        temp, load, ram_pct, ram_mo, freq = parser(r.stdout)
        base.update(temp_c=temp, load1=load, ram_pct=ram_pct, ram_mo=ram_mo,
                    freq_mhz=freq, ok=1)
    except Exception as e:            # machine éteinte, ssh absent, timeout...
        base["err"] = str(e)[:80]
    return base


def _arrondi(v, n):
    return "" if (v is None or math.isnan(v)) else round(v, n)


def ligne_csv(horo, m):
    return [horo, m["machine"], m["hote"], _arrondi(m["temp_c"], 1), _arrondi(m["load1"], 2),
            _arrondi(m["ram_pct"], 1), _arrondi(m["ram_mo"], 0), _arrondi(m["freq_mhz"], 0), m["ok"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--intervalle", type=float, default=1.0, help="secondes entre mesures (défaut 1)")
    ap.add_argument("--dossier", default=str(DATA))
    ap.add_argument("--test", action="store_true", help="une mesure affichée, rien d'écrit")
    args = ap.parse_args()

    def cycle():
        with ThreadPoolExecutor(len(NOEUDS)) as ex:
            return list(ex.map(mesurer, NOEUDS))

    if args.test:
        print("{:<5}{:<18}{:>8}{:>8}{:>8}{:>10}  {}".format(
            "PC", "hôte", "°C", "load", "RAM %", "MHz", "état"))
        for m in cycle():
            print("{:<5}{:<18}{:>8}{:>8}{:>8}{:>10}  {}".format(
                m["machine"], m["hote"], _arrondi(m["temp_c"], 1), _arrondi(m["load1"], 2),
                _arrondi(m["ram_pct"], 1), _arrondi(m["freq_mhz"], 0),
                "OK" if m["ok"] else "ÉCHEC : " + m["err"]))
        return

    os.makedirs(args.dossier, exist_ok=True)
    print("Enregistrement toutes les %.0f s dans %s (Ctrl+C pour arrêter)" % (args.intervalle, args.dossier))
    try:
        while True:
            debut = time.time()
            res = cycle()
            horo = datetime.datetime.now().isoformat(timespec="seconds")
            fichier = os.path.join(args.dossier, "cluster_metrics_%s.csv" % datetime.date.today().strftime("%Y%m%d"))
            nouveau = not os.path.exists(fichier)
            with open(fichier, "a", newline="") as fh:
                w = csv.writer(fh)
                if nouveau:
                    w.writerow(ENTETE)
                for m in res:
                    w.writerow(ligne_csv(horo, m))
            time.sleep(max(0.2, args.intervalle - (time.time() - debut)))
    except KeyboardInterrupt:
        print("arrêt demandé")


if __name__ == "__main__":
    main()

# zeta_log_metrics.py · hprzeta · MAJ 2026-10-17 · 161 lignes
