"""
zeta_temp_monitor.py
=====================
Dashboard temps réel de la température CPU du cluster Zeta (PC1-PC4).

Modernisation de docs/archive/python_obsoletes/cpu_temp_monitor.py (mono-PC1,
archivé le 29/05/2026 dans un nettoyage groupé, jamais cassé ni remplacé) :
ajout de l'interrogation SSH de PC2/PC3/PC4, en réutilisant leur alias
~/.ssh/config (zeta-calc-second, zeta-backup, zeta-secure).

Usage :
    source ~/projet_zeta/zeta_env/bin/activate
    python scripts/zeta_temp_monitor.py

Dépendances (PC1 uniquement — les autres machines n'ont besoin de rien de
particulier, seulement `sensors` déjà installé) :
    psutil, matplotlib (déjà dans zeta_env)

AUTEUR : hprzeta — Riemann_Lab
DATE : 2026-08-18
"""

import re
import time
import threading
import subprocess
import psutil
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

matplotlib.rcParams['toolbar'] = 'None'

# ── Paramètres ──────────────────────────────────────────────────────────────
MAX_POINTS       = 300      # 5 min à 1 pt/s (PC1) — les distants ont moins de points
INTERVAL_MS      = 1000     # rafraîchissement du plot
SAMPLE_LOCAL_S   = 1.0      # fréquence d'échantillonnage PC1
SAMPLE_REMOTE_S  = 5.0      # fréquence SSH — pas 1s, coût réseau + latence
SSH_TIMEOUT_S    = 3        # ConnectTimeout — une machine down ne doit pas geler les autres

TEMP_WARN = 75              # °C — seuil indicatif (varie par matériel, cf. légende)
TEMP_CRIT = 90

# ── Cluster — réutilise les alias ~/.ssh/config (zeta_cluster key) ──────────
# ("libellé", host_ssh ou None pour PC1 local, "linux"/"openbsd")
MACHINES = [
    ("PC1 zeta-lab",         None,               "local"),
    ("PC2 zeta-calc-second", "zeta-calc-second", "linux"),
    ("PC3 zeta-backup",      "zeta-backup",      "linux"),
    ("PC4 zeta-secure",      "zeta-secure",      "openbsd"),
]

COLORS = {
    "PC1 zeta-lab":         "#00d4ff",
    "PC2 zeta-calc-second": "#39ff14",
    "PC3 zeta-backup":      "#ff6b35",
    "PC4 zeta-secure":      "#c77dff",
}

BG, PANEL, TEXT, GRID, DANGER = "#0a0e1a", "#111827", "#e2e8f0", "#1e293b", "#ff2d55"

RE_TEMP_LINUX   = re.compile(r"[+-]?(\d+\.\d+)\s*°C")
RE_TEMP_OPENBSD = re.compile(r"cpu\d*\.temp\d*=(\d+\.\d+)\s*degC", re.IGNORECASE)


# ── Lecture température PC1 (local — inchangé de cpu_temp_monitor.py) ───────
def get_temp_local():
    try:
        temps = psutil.sensors_temperatures()
        for key in ("coretemp", "acpitz", "k10temp", "cpu_thermal", "zenpower"):
            if key in temps:
                vals = [e.current for e in temps[key] if e.current and e.current > 0]
                if vals:
                    return sum(vals) / len(vals)
    except Exception:
        pass
    try:
        out = subprocess.check_output(["sensors"], text=True, stderr=subprocess.DEVNULL)
        vals = [float(m) for m in RE_TEMP_LINUX.findall(out)]
        if vals:
            return sum(vals) / len(vals)
    except Exception:
        pass
    try:
        import glob
        vals = []
        for p in glob.glob("/sys/class/thermal/thermal_zone*/temp"):
            with open(p) as f:
                vals.append(int(f.read().strip()) / 1000.0)
        if vals:
            return max(vals)
    except Exception:
        pass
    return None


# ── Lecture température distante — Linux (PC2/PC3) via `sensors` ───────────
def get_temp_ssh_linux(host):
    try:
        out = subprocess.check_output(
            ["ssh", "-o", f"ConnectTimeout={SSH_TIMEOUT_S}", "-o", "BatchMode=yes",
             host, "sensors 2>/dev/null"],
            text=True, stderr=subprocess.DEVNULL, timeout=SSH_TIMEOUT_S + 2,
        )
        vals = [float(m) for m in RE_TEMP_LINUX.findall(out)]
        return sum(vals) / len(vals) if vals else None
    except Exception:
        return None


# ── Lecture température distante — OpenBSD (PC4) via sysctl hw.sensors ─────
def get_temp_ssh_openbsd(host):
    try:
        out = subprocess.check_output(
            ["ssh", "-o", f"ConnectTimeout={SSH_TIMEOUT_S}", "-o", "BatchMode=yes",
             host, "sysctl hw.sensors 2>/dev/null"],
            text=True, stderr=subprocess.DEVNULL, timeout=SSH_TIMEOUT_S + 2,
        )
        vals = [float(m) for m in RE_TEMP_OPENBSD.findall(out)]
        return sum(vals) / len(vals) if vals else None
    except Exception:
        return None


def read_temp(host, kind):
    if kind == "local":
        return get_temp_local()
    if kind == "openbsd":
        return get_temp_ssh_openbsd(host)
    return get_temp_ssh_linux(host)


# ── Données partagées ────────────────────────────────────────────────────────
start_time = time.time()
lock       = threading.Lock()
history    = {label: {"t": deque(maxlen=MAX_POINTS), "temp": deque(maxlen=MAX_POINTS)}
              for label, _, _ in MACHINES}
status     = {label: {"temp": None, "last_ok": None} for label, _, _ in MACHINES}


def collect(label, host, kind):
    interval = SAMPLE_LOCAL_S if kind == "local" else SAMPLE_REMOTE_S
    while True:
        t = time.time() - start_time
        temp = read_temp(host, kind)
        with lock:
            if temp is not None:
                history[label]["t"].append(t)
                history[label]["temp"].append(temp)
                status[label]["temp"] = temp
                status[label]["last_ok"] = t
            # si temp est None : machine injoignable, on ne casse rien,
            # on retentera au prochain cycle (cf. incident PC3 du 18/08).
        time.sleep(interval)


for label, host, kind in MACHINES:
    threading.Thread(target=collect, args=(label, host, kind), daemon=True).start()

psutil.cpu_percent(interval=None)  # chauffe l'appel local (non utilisé ailleurs)

# ── Dashboard — 2 panneaux : courbes multi-machines + statut cluster ────────
fig = plt.figure(figsize=(13, 7), facecolor=BG)
fig.canvas.manager.set_window_title("⚛  Zeta Cluster — Températures CPU")

ax_temp   = fig.add_axes([0.08, 0.38, 0.88, 0.52])
ax_status = fig.add_axes([0.08, 0.06, 0.88, 0.22])

for ax in (ax_temp, ax_status):
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)

fig.text(0.5, 0.95, "⚛  Cluster Zeta — Températures CPU (PC1-PC4)",
          ha="center", fontsize=13, fontweight="bold", color="#00d4ff",
          fontfamily="monospace")

ax_temp.axhline(TEMP_WARN, color="#ff6b35", lw=1, ls="--", alpha=0.6,
                 label=f"Avert. {TEMP_WARN}°C (indicatif)")
ax_temp.axhline(TEMP_CRIT, color=DANGER, lw=1, ls="--", alpha=0.6,
                 label=f"Critique {TEMP_CRIT}°C (indicatif)")
ax_temp.set_ylabel("°C", color=TEXT)
ax_temp.set_xlabel("Temps (s)", color=TEXT)
ax_temp.tick_params(colors=TEXT, labelsize=8)
ax_temp.grid(True, color=GRID, lw=0.5)
ax_temp.set_ylim(20, 110)

lines = {}
for label, _, _ in MACHINES:
    lines[label], = ax_temp.plot([], [], lw=1.8, color=COLORS[label], label=label)
ax_temp.legend(loc="upper left", fontsize=7.5, facecolor=PANEL, labelcolor=TEXT, ncol=2)

ax_status.axis("off")
status_text = ax_status.text(
    0.0, 0.5, "", ha="left", va="center", fontsize=10.5,
    color=TEXT, fontfamily="monospace", transform=ax_status.transAxes,
)


def fmt_status(label):
    s = status[label]
    if s["temp"] is None:
        return f"  {label:<22} —        INJOIGNABLE"
    age = time.time() - start_time - s["last_ok"]
    tag = "OK" if s["temp"] < TEMP_WARN else ("WARN" if s["temp"] < TEMP_CRIT else "CRIT")
    stale = "  (⚠ dernière lecture ancienne)" if age > (SAMPLE_REMOTE_S * 3) else ""
    return f"  {label:<22} {s['temp']:5.1f}°C  {tag:<4}{stale}"


def update(frame):
    with lock:
        for label, _, _ in MACHINES:
            t_arr = list(history[label]["t"])
            temp_arr = list(history[label]["temp"])
            lines[label].set_data(t_arr, temp_arr)
        lines_text = "\n".join(fmt_status(label) for label, _, _ in MACHINES)

    all_t = [t for label, _, _ in MACHINES for t in history[label]["t"]]
    if all_t:
        ax_temp.set_xlim(max(0, max(all_t) - MAX_POINTS * SAMPLE_LOCAL_S), max(all_t) + 1)

    status_text.set_text(lines_text)


ani = animation.FuncAnimation(fig, update, interval=INTERVAL_MS, cache_frame_data=False)
plt.show()
