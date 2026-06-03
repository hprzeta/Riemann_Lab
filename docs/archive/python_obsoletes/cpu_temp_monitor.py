"""
cpu_temp_monitor.py
===================
Dashboard temps réel de la température CPU pendant le calcul des zéros de Zeta.

Usage :
    # Dans un terminal :
    python cpu_temp_monitor.py & (en arriere plan)

    # Pendant que dans un AUTRE terminal tu lances :
    python compute_zero_test.py 

Dépendances :
    pip install psutil matplotlib

Sous Linux, installe aussi lm-sensors :
    sudo apt install lm-sensors
    sudo sensors-detect  (à faire une seule fois)
    
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

import time
import threading
import subprocess
import psutil
import matplotlib
matplotlib.use('TkAgg')   # Fenêtre indépendante du terminal
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
from collections import deque
from datetime import datetime

matplotlib.rcParams['toolbar'] = 'None'

# ── Paramètres ──────────────────────────────────────────────────────────────
MAX_POINTS      = 300       # Nombre de points gardés en mémoire (= 5 min à 1 Hz)
INTERVAL_MS     = 1000      # Rafraîchissement du plot (ms)
SAMPLE_RATE_S   = 1.0       # Fréquence d'échantillonnage (secondes)

TEMP_WARN       = 75        # °C : seuil avertissement (orange)
TEMP_CRIT       = 90        # °C : seuil critique (rouge)

# Palette "laboratoire quantique"
BG      = "#0a0e1a"
PANEL   = "#111827"
ACCENT  = "#00d4ff"
WARM    = "#ff6b35"
DANGER  = "#ff2d55"
GREEN   = "#39ff14"
TEXT    = "#e2e8f0"
GRID    = "#1e293b"

# ── Données partagées (thread-safe via deque) ────────────────────────────────
temps_history   = deque(maxlen=MAX_POINTS)
cpu_history     = deque(maxlen=MAX_POINTS)
time_history    = deque(maxlen=MAX_POINTS)   # secondes écoulées
zero_events     = []   # (t_sec, temp) à chaque nouveau zéro détecté (optionnel)

start_time      = time.time()
lock            = threading.Lock()

# Initialisation psutil CPU (le premier appel retourne toujours 0, on le "chauffe")
psutil.cpu_percent(interval=1.0)


# ── Lecture température ──────────────────────────────────────────────────────
def get_cpu_temp():
    """Lit la température CPU via psutil (méthode principale) ou sensors."""
    # Méthode 1 : psutil (fonctionne sur la plupart des Linux modernes)
    try:
        temps = psutil.sensors_temperatures()
        # On cherche dans l'ordre : coretemp, acpitz, k10temp, cpu_thermal
        for key in ("coretemp", "acpitz", "k10temp", "cpu_thermal", "zenpower"):
            if key in temps:
                entries = temps[key]
                # Moyenne des cores disponibles
                vals = [e.current for e in entries if e.current and e.current > 0]
                if vals:
                    return sum(vals) / len(vals)
    except Exception:
        pass

    # Méthode 2 : commande sensors (fallback)
    try:
        out = subprocess.check_output(["sensors"], text=True, stderr=subprocess.DEVNULL)
        for line in out.splitlines():
            if "Core 0" in line or "CPU Temperature" in line or "Tdie" in line:
                part = line.split(":")[1].strip().split()[0]
                return float(part.replace("+", "").replace("°C", ""))
    except Exception:
        pass

    # Méthode 3 : lecture directe dans /sys
    import glob
    paths = glob.glob("/sys/class/thermal/thermal_zone*/temp")
    vals = []
    for p in paths:
        try:
            with open(p) as f:
                vals.append(int(f.read().strip()) / 1000.0)
        except Exception:
            pass
    if vals:
        return max(vals)   # on prend la zone la plus chaude

    return None


# ── Thread de collecte ───────────────────────────────────────────────────────
def collect_data():
    while True:
        t   = time.time() - start_time
        temp = get_cpu_temp()
        cpu  = psutil.cpu_percent(interval=0.5)

        if temp is not None:
            with lock:
                temps_history.append(temp)
                cpu_history.append(cpu)
                time_history.append(t)

        time.sleep(SAMPLE_RATE_S)


collector = threading.Thread(target=collect_data, daemon=True)
collector.start()


# ── Mise en page du dashboard ────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 8), facecolor=BG)
fig.canvas.manager.set_window_title("⚛  CPU Monitor — Zéros de Zeta")

gs = gridspec.GridSpec(
    2, 3,
    figure=fig,
    left=0.07, right=0.97,
    top=0.88,  bottom=0.10,
    hspace=0.45, wspace=0.35
)

ax_temp  = fig.add_subplot(gs[0, :2])   # Courbe température (grande)
ax_cpu   = fig.add_subplot(gs[1, :2])   # Courbe CPU %
ax_hist  = fig.add_subplot(gs[0, 2])    # Histogramme températures
ax_gauge = fig.add_subplot(gs[1, 2])    # Jauge / camembert instantané

for ax in (ax_temp, ax_cpu, ax_hist, ax_gauge):
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)

# Titre principal
fig.text(
    0.5, 0.95,
    "⚛  CPU Thermal Monitor — Calcul des Zéros de Zeta",
    ha="center", va="center",
    fontsize=14, fontweight="bold",
    color=ACCENT, fontfamily="monospace"
)

# Affichage température courante (coin haut droit)
temp_display = fig.text(
    0.97, 0.95, "-- °C",
    ha="right", va="center",
    fontsize=22, fontweight="bold",
    color=GREEN, fontfamily="monospace"
)

# ── Courbe température ───────────────────────────────────────────────────────
line_temp, = ax_temp.plot([], [], color=ACCENT, lw=2, label="Temp CPU (°C)")
fill_temp  = ax_temp.fill_between([], [], alpha=0.15, color=ACCENT)

ax_temp.axhline(TEMP_WARN, color=WARM,   lw=1, ls="--", alpha=0.7, label=f"Avert. {TEMP_WARN}°C")
ax_temp.axhline(TEMP_CRIT, color=DANGER, lw=1, ls="--", alpha=0.7, label=f"Critique {TEMP_CRIT}°C")

ax_temp.set_title("Température CPU (°C)", color=TEXT, fontsize=10, pad=6)
ax_temp.set_ylabel("°C", color=TEXT, fontsize=9)
ax_temp.set_xlabel("Temps (s)", color=TEXT, fontsize=9)
ax_temp.tick_params(colors=TEXT, labelsize=8)
ax_temp.yaxis.label.set_color(TEXT)
ax_temp.legend(loc="upper left", fontsize=7, facecolor=PANEL, labelcolor=TEXT)
ax_temp.grid(True, color=GRID, lw=0.5)
ax_temp.set_ylim(20, 110)

# ── Courbe CPU % ─────────────────────────────────────────────────────────────
line_cpu, = ax_cpu.plot([], [], color=WARM, lw=2, label="CPU usage (%)")
fill_cpu  = ax_cpu.fill_between([], [], alpha=0.12, color=WARM)

ax_cpu.set_title("Utilisation CPU (%)", color=TEXT, fontsize=10, pad=6)
ax_cpu.set_ylabel("%", color=TEXT, fontsize=9)
ax_cpu.set_xlabel("Temps (s)", color=TEXT, fontsize=9)
ax_cpu.tick_params(colors=TEXT, labelsize=8)
ax_cpu.legend(loc="upper left", fontsize=7, facecolor=PANEL, labelcolor=TEXT)
ax_cpu.grid(True, color=GRID, lw=0.5)
ax_cpu.set_ylim(0, 105)

# ── Histogramme températures ─────────────────────────────────────────────────
ax_hist.set_title("Distribution températures", color=TEXT, fontsize=9, pad=6)
ax_hist.set_xlabel("°C", color=TEXT, fontsize=8)
ax_hist.set_ylabel("Fréquence", color=TEXT, fontsize=8)
ax_hist.tick_params(colors=TEXT, labelsize=7)
ax_hist.grid(True, color=GRID, lw=0.5, axis='y')

# ── Jauge circulaire ──────────────────────────────────────────────────────────
ax_gauge.set_title("Charge CPU instantanée", color=TEXT, fontsize=9, pad=6)
ax_gauge.set_aspect('equal')
ax_gauge.axis('off')

wedge_bg  = plt.matplotlib.patches.Wedge(
    (0.5, 0.60), 0.38, 0, 360,
    width=0.12, transform=ax_gauge.transAxes,
    facecolor=GRID
)
wedge_val = plt.matplotlib.patches.Wedge(
    (0.5, 0.60), 0.38, 90, 90,
    width=0.12, transform=ax_gauge.transAxes,
    facecolor=ACCENT
)
ax_gauge.add_patch(wedge_bg)
ax_gauge.add_patch(wedge_val)

gauge_text = ax_gauge.text(
    0.5, 0.58, "0%",
    ha='center', va='center',
    fontsize=20, fontweight='bold',
    color=ACCENT, fontfamily='monospace',
    transform=ax_gauge.transAxes
)
gauge_label = ax_gauge.text(
    0.5, 0.35, "CPU Usage",
    ha='center', va='center',
    fontsize=8, color=TEXT,
    transform=ax_gauge.transAxes
)

# Statistiques texte (bien en bas, séparé du camembert)
stats_text = ax_gauge.text(
    0.5, 0.12,
    "Min: --  Max: --  Moy: --",
    ha="center", va="center",
    fontsize=7.5, color=TEXT, fontfamily="monospace",
    transform=ax_gauge.transAxes
)


# Références aux fills (pour pouvoir les supprimer proprement à chaque frame)
fill_ref     = [None]
fill_cpu_ref = [None]


# ── Fonction d'animation ──────────────────────────────────────────────────────
def update(frame):
    with lock:
        if len(temps_history) < 2:
            return

        t_arr    = list(time_history)
        temp_arr = list(temps_history)
        cpu_arr  = list(cpu_history)

    # — Courbe température —
    line_temp.set_data(t_arr, temp_arr)
    ax_temp.set_xlim(max(0, t_arr[-1] - MAX_POINTS), t_arr[-1] + 1)

    # Remplissage : on supprime l'ancienne PolyCollection proprement
    if fill_ref[0] is not None:
        fill_ref[0].remove()
    fill_ref[0] = ax_temp.fill_between(t_arr, temp_arr, 20, alpha=0.12, color=ACCENT)

    # Couleur de la ligne selon température
    cur_temp = temp_arr[-1]
    if cur_temp >= TEMP_CRIT:
        line_temp.set_color(DANGER)
    elif cur_temp >= TEMP_WARN:
        line_temp.set_color(WARM)
    else:
        line_temp.set_color(ACCENT)

    # Affichage température courante
    temp_color = DANGER if cur_temp >= TEMP_CRIT else (WARM if cur_temp >= TEMP_WARN else GREEN)
    temp_display.set_text(f"{cur_temp:.1f} °C")
    temp_display.set_color(temp_color)

    # — Courbe CPU —
    t_cpu = t_arr[-len(cpu_arr):]
    line_cpu.set_data(t_cpu, cpu_arr)
    ax_cpu.set_xlim(ax_temp.get_xlim())
    if fill_cpu_ref[0] is not None:
        fill_cpu_ref[0].remove()
    fill_cpu_ref[0] = ax_cpu.fill_between(t_cpu, cpu_arr, 0, alpha=0.12, color=WARM)

    # — Histogramme —
    ax_hist.cla()
    ax_hist.set_facecolor(PANEL)
    ax_hist.set_title("Distribution températures", color=TEXT, fontsize=9, pad=6)
    ax_hist.set_xlabel("°C", color=TEXT, fontsize=8)
    ax_hist.set_ylabel("Fréquence", color=TEXT, fontsize=8)
    ax_hist.tick_params(colors=TEXT, labelsize=7)
    ax_hist.grid(True, color=GRID, lw=0.5, axis='y')

    n, bins, patches = ax_hist.hist(
        temp_arr, bins=20, color=ACCENT, alpha=0.75, edgecolor=BG
    )
    # Colorier les barres selon la température
    for patch, left in zip(patches, bins[:-1]):
        if left >= TEMP_CRIT:
            patch.set_facecolor(DANGER)
        elif left >= TEMP_WARN:
            patch.set_facecolor(WARM)
        else:
            patch.set_facecolor(ACCENT)

    ax_hist.axvline(cur_temp, color=GREEN, lw=1.5, ls="-", label=f"Actuel: {cur_temp:.1f}°C")
    ax_hist.legend(fontsize=7, facecolor=PANEL, labelcolor=TEXT)
    for spine in ax_hist.spines.values():
        spine.set_edgecolor(GRID)

    # — Jauge circulaire —
    cur_cpu = cpu_arr[-1]
    # Angle : 90° (haut) → sens antihoraire pour remplissage
    end_angle = 90 - (cur_cpu / 100) * 360
    wedge_val.set_theta1(end_angle)
    wedge_val.set_theta2(90)
    gauge_color = DANGER if cur_cpu > 80 else (WARM if cur_cpu > 50 else ACCENT)
    wedge_val.set_facecolor(gauge_color)
    gauge_text.set_text(f"{cur_cpu:.0f}%")
    gauge_text.set_color(gauge_color)

    # — Stats —
    mn, mx, mv = min(temp_arr), max(temp_arr), sum(temp_arr)/len(temp_arr)
    stats_text.set_text(f"Min: {mn:.1f}°  Max: {mx:.1f}°  Moy: {mv:.1f}°")


ani = animation.FuncAnimation(
    fig, update, interval=INTERVAL_MS, cache_frame_data=False
)

plt.show()
