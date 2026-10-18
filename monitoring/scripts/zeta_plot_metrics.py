#!/usr/bin/env python3
"""
zeta_plot_metrics.py — Graphique de l'historique des 5 machines (lit les CSV de zeta_log_metrics.py).
Lecture seule, léger. Mode direct : se rafraîchit ; mode image : --sortie PNG.

4 graphiques empilés sur le même axe du temps (jamais deux échelles sur un même graphique) :
  1. Température CPU (°C)   2. Fréquence CPU (MHz)   3. Charge (load 1 min)   4. RAM (%)
Une couleur FIXE par machine (PC1 bleu, PC2 orange, PC3 vert-eau, PC4 jaune, PC5 magenta).

Usage (PC1) — via l'alias :  zeta-metrics [minutes] [refresh_s]
  ou :  nice -n 19 python zeta_plot_metrics.py --minutes 15 --refresh 2
        python zeta_plot_metrics.py --debut 2026-10-16T10:00:00 --fin 2026-10-16T11:00:00 --sortie m.png
"""
import argparse
import datetime
import glob
import io
import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D

from zeta_mon_common import DATA, compacter, placer, titrer

# Palette catégorielle (étapes « sombre »), validée sur fond #1a1a19 (skill dataviz).
COULEURS = {"PC1": "#3987e5", "PC2": "#d95926", "PC3": "#199e70", "PC4": "#c98500", "PC5": "#d55181"}
NOMS = {"PC1": "zeta-lab", "PC2": "zeta-calc-second", "PC3": "zeta-backup",
        "PC4": "zeta-secure", "PC5": "zeta-monitor"}
SURFACE, TEXTE, TEXTE2, GRILLE = "#1a1a19", "#f0efec", "#c3c2b7", "#383835"
AVERT, CRITIQUE = "#fab219", "#d03b3b"       # couleurs de statut (réservées aux seuils)
PANNEAUX = [("temp_c", "Température CPU (°C)"), ("freq_mhz", "Fréquence CPU (MHz)"),
            ("load1", "Charge (load, 1 min)"), ("ram_pct", "RAM utilisée (%)")]
MAX_PTS = 8000        # au-delà, le tracé est sous-échantillonné (les stats gardent tout)


def _lire_fin(fichier, nbytes):
    """Lit seulement la fin d'un CSV (≈ nbytes octets) : rapide même pour une journée entière."""
    with open(fichier, "rb") as fh:
        entete = fh.readline().decode()
        taille = os.fstat(fh.fileno()).st_size
        if taille - len(entete) <= nbytes:
            fh.seek(0)
            return pd.read_csv(io.StringIO(fh.read().decode(errors="replace")), on_bad_lines="skip")
        fh.seek(taille - nbytes)
        fh.readline()                                   # saute la ligne coupée
        corps = fh.read().decode(errors="replace")
    return pd.read_csv(io.StringIO(entete + corps), on_bad_lines="skip")


def lire(dossier=None, minutes=None, t0=None, t1=None):
    """Lit les CSV journaliers. Fenêtre : [t0, t1] si donnés, sinon les `minutes` dernières
    (mode direct : lecture de la fin des fichiers seulement)."""
    dossier = str(dossier or DATA)
    fichiers = sorted(glob.glob(os.path.join(dossier, "cluster_metrics_*.csv")))
    if t0 is not None:
        d0, d1 = t0.strftime("%Y%m%d"), (t1 or datetime.datetime.now()).strftime("%Y%m%d")
        fichiers = [f for f in fichiers if d0 <= os.path.basename(f)[16:24] <= d1]
        if not fichiers:
            return None
        df = pd.concat([pd.read_csv(f, on_bad_lines="skip") for f in fichiers], ignore_index=True)
    else:
        t0 = datetime.datetime.now() - datetime.timedelta(minutes=minutes or 60)
        nbytes = int((minutes or 60) * 60 * 5 * 110 * 1.3) + 4096      # 5 machines/s, ~110 o/ligne max
        parts = []
        for f in reversed(fichiers[-2:]):                               # aujourd'hui, puis hier si besoin
            d = _lire_fin(f, nbytes)
            parts.insert(0, d)
            if len(d) and pd.to_datetime(d["horodatage"].iloc[0], errors="coerce") <= t0:
                break
        if not parts:
            return None
        df = pd.concat(parts, ignore_index=True)
    df["horodatage"] = pd.to_datetime(df["horodatage"], errors="coerce")
    df = df.dropna(subset=["horodatage"]).sort_values("horodatage")
    df = df[df["horodatage"] >= t0]
    if t1 is not None:
        df = df[df["horodatage"] <= t1]
    return df


def creer_figure(figsize=(14, 10)):
    fig, axes = plt.subplots(4, 1, figsize=figsize, sharex=True, constrained_layout=True)
    fig.patch.set_facecolor(SURFACE)
    fig.get_layout_engine().set(rect=(0, 0, 1, 0.91))
    return fig, axes


def dessiner(fig, axes, df, titre):
    for ax in axes:
        ax.clear()
        ax.set_facecolor(SURFACE)
        ax.grid(True, color=GRILLE, lw=0.6, alpha=0.8)
        ax.tick_params(colors=TEXTE2, labelsize=9)
        for s in ax.spines.values():
            s.set_color(GRILLE)
    if df is None or df.empty:
        axes[0].text(0.5, 0.5, "aucune mesure : lancer  zeta-mon-on", transform=axes[0].transAxes,
                     ha="center", color=TEXTE)
        return
    presentes = []
    for pc, couleur in COULEURS.items():
        d = df[df["machine"] == pc]
        if d.empty:
            continue
        pas = max(1, len(d) // MAX_PTS)
        d = d.iloc[::pas]
        for ax, (col, _) in zip(axes, PANNEAUX):
            # Une mesure ratée (ok=0) interrompt la ligne au lieu de tracer un faux zéro.
            y = pd.to_numeric(d[col], errors="coerce").where(d["ok"] == 1)
            if y.notna().any():
                ax.plot(d["horodatage"], y, color=couleur, lw=1.4)
                if pc not in presentes:
                    presentes.append(pc)
    for ax, (_, t) in zip(axes, PANNEAUX):
        ax.set_title(t, loc="left", color=TEXTE, fontsize=11)
    axes[0].set_ylim(20, 100)
    for seuil, couleur, texte in ((75, AVERT, "75 °C avertissement"), (90, CRITIQUE, "90 °C critique")):
        axes[0].axhline(seuil, color=couleur, lw=1, ls="--")
        axes[0].text(0.995, seuil, texte, transform=axes[0].get_yaxis_transform(),
                     ha="right", va="bottom", color=TEXTE2, fontsize=8)
    axes[3].set_ylim(0, 100)
    loc = mdates.AutoDateLocator(minticks=4, maxticks=8)
    axes[3].xaxis.set_major_locator(loc)
    axes[3].xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
    axes[3].set_xlabel("heure locale", color=TEXTE2)
    if fig.legends:
        fig.legends[0].remove()
    if presentes:
        fig.legend([Line2D([0], [0], color=COULEURS[p], lw=2.5) for p in presentes],
                   ["%s %s" % (p, NOMS[p]) for p in presentes], loc="upper center",
                   bbox_to_anchor=(0.5, 0.955), ncol=len(presentes), frameon=False,
                   labelcolor=TEXTE, fontsize=10)
    fig.suptitle(titre, color=TEXTE, y=0.995, fontsize=12)


def figure_metrics(df, titre, figsize=(14, 10)):
    fig, axes = creer_figure(figsize)
    dessiner(fig, axes, df, titre)
    return fig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dossier", default=str(DATA))
    ap.add_argument("--minutes", type=int, default=60)
    ap.add_argument("--refresh", type=float, default=2.0, help="secondes (1 = très fluide)")
    ap.add_argument("--geometrie", default=None, help="fenêtre : LARGEURxHAUTEUR+X+Y (ex. 900x1000+990+35)")
    ap.add_argument("--debut", default=None, help="ISO, ex. 2026-10-16T10:00:00")
    ap.add_argument("--fin", default=None)
    ap.add_argument("--sortie", default=None, help="enregistre une image PNG, sans fenêtre")
    a = ap.parse_args()
    t0 = datetime.datetime.fromisoformat(a.debut) if a.debut else None
    t1 = datetime.datetime.fromisoformat(a.fin) if a.fin else None
    if a.geometrie:
        compacter(a.geometrie)
    fig, axes = creer_figure()
    titrer(fig, "Zêta — Machines du cluster en direct (température, fréquence, load, RAM)")
    if a.geometrie:
        placer(fig, a.geometrie)

    def maj(_=None):
        df = lire(a.dossier, a.minutes, t0, t1)
        titre = ("Cluster Zêta — {} → {}".format(a.debut, a.fin or "…") if t0 else
                 "Cluster Zêta — {} dernières minutes — MAJ {}".format(
                     a.minutes, datetime.datetime.now().strftime("%H:%M:%S")))
        dessiner(fig, axes, df, titre)

    maj()
    if a.sortie:
        fig.savefig(a.sortie, dpi=110, facecolor=SURFACE)
        print("enregistré :", a.sortie)
        return
    _anim = FuncAnimation(fig, maj, interval=int(a.refresh * 1000), cache_frame_data=False)
    plt.show()


if __name__ == "__main__":
    main()

# zeta_plot_metrics.py · hprzeta · MAJ 2026-10-17 · 182 lignes
