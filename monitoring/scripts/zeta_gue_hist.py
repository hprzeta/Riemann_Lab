#!/usr/bin/env python3
"""
zeta_gue_hist.py — Histogramme des espacements normalisés des zéros de zêta,
comparé aux lois théoriques. Lecture seule, aucun calcul lourd.

Théorie :
  - s = (γ_{n+1} - γ_n) · ln(γ/2π) / 2π  => espacement moyen = 1.
  - Conjecture de Montgomery–Odlyzko (heuristique, très bien vérifiée numériquement, NON démontrée) :
    les espacements suivent la loi GUE.
  - Approximation de Wigner (surmise) GUE : p(s) = (32/π²) s² exp(-4 s²/π)
  - Contre-exemple : zéros « au hasard » (Poisson) p(s) = exp(-s) : pas de répulsion.

Usage (PC1) — via l'alias :  zeta-gue [csv|dossier]
  ou :  python zeta_gue_hist.py <csv|dossier> --colonne partie_imaginaire [--sortie hist.png]
"""
import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation

from zeta_mon_common import compacter, placer, titrer
from zeta_plot_live import LecteurZeros, lire_zeros, trouver_csv


def gue_surmise(s):
    return 32.0 / np.pi ** 2 * s ** 2 * np.exp(-4.0 * s ** 2 / np.pi)


def espacements(t):
    brut = np.diff(t)
    tm = t[:-1] + brut / 2
    return brut, brut * np.log(tm / (2 * np.pi)) / (2 * np.pi)


def dessiner_gue(ax1, ax2, t, bins=60):
    """Trace les 2 panneaux sur ax1, ax2 et retourne les stats. Normalisation sur TOUS les espacements
    (pas density=True, qui gonflerait le zoom)."""
    brut, s = espacements(t)
    ax1.clear()
    ax2.clear()
    larg1 = 3.0 / bins
    ax1.hist(s, bins=bins, range=(0, 3), weights=np.full(len(s), 1.0 / (len(s) * larg1)),
             color="#3b78c4", alpha=0.8, label="zéros calculés")
    x = np.linspace(0, 3, 400)
    ax1.plot(x, gue_surmise(x), "k-", lw=2, label="GUE (Wigner surmise)")
    ax1.plot(x, np.exp(-x), "r--", lw=1.5, label="Poisson (hasard pur)")
    ax1.set_xlabel("espacement normalisé s")
    ax1.set_ylabel("densité p(s)")
    ax1.set_title("{} zéros — t ∈ [{:.0f} ; {:.0f}]".format(len(t), t[0], t[-1]))
    ax1.legend()
    larg = 0.5 / 40
    ax2.hist(s, bins=40, range=(0, 0.5), weights=np.full(len(s), 1.0 / (len(s) * larg)),
             color="#3b78c4", alpha=0.8)
    xs = np.linspace(0.001, 0.5, 300)
    ax2.plot(xs, gue_surmise(xs), "k-", lw=2, label="GUE : p(s) ∝ s²")
    ax2.plot(xs, np.exp(-xs), "r--", lw=1.5, label="Poisson : p(0) = 1")
    ax2.set_yscale("log")
    ax2.set_xlabel("espacement normalisé s (zoom 0 – 0,5)")
    ax2.set_title("Répulsion des zéros : peu de petits écarts")
    ax2.legend()
    return dict(n=len(t), t0=float(t[0]), t1=float(t[-1]), moyenne=float(s.mean()),
                variance=float(s.var()), part_s01=float((s < 0.1).mean()), min_brut=float(brut.min()))


def figure_gue(t, bins=60):
    """Retourne (figure, stats)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
    return fig, dessiner_gue(ax1, ax2, t, bins)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chemin", help="CSV des zéros (ou dossier : CSV le plus récent)")
    ap.add_argument("--colonne", default=None, help="nom ou numéro de la colonne t")
    ap.add_argument("--bins", type=int, default=60)
    ap.add_argument("--sortie", default=None, help="enregistre en PNG au lieu d'ouvrir une fenêtre")
    ap.add_argument("--live", action="store_true", help="fenêtre rafraîchie pendant le run (lecture incrémentale)")
    ap.add_argument("--refresh", type=float, default=30.0, help="secondes en mode --live (défaut 30)")
    ap.add_argument("--min-zeros", type=int, default=3000, help="en --live : attendre ce nombre de zéros")
    ap.add_argument("--geometrie", default=None, help="fenêtre : LARGEURxHAUTEUR+X+Y")
    ap.add_argument("--apres", default=None, help="ISO : ignorer les CSV modifiés avant (début du run)")
    args = ap.parse_args()

    if args.live:
        apres = __import__("datetime").datetime.fromisoformat(args.apres).timestamp() if args.apres else None
        if args.geometrie:
            compacter(args.geometrie)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
        titrer(fig, "Zêta — Statistique GUE en direct (espacements normalisés)")
        if args.geometrie:
            placer(fig, args.geometrie)
        etat = {"csv": None, "lecteur": None}

        def maj(_=None):
            csv = trouver_csv(args.chemin, apres)
            if not csv or not os.path.exists(csv):
                return
            try:
                if csv != etat["csv"]:
                    etat["csv"], etat["lecteur"] = csv, LecteurZeros(csv, args.colonne)
                t = etat["lecteur"].maj()
            except Exception as e:
                print("lecture ignorée :", e)
                return
            if len(t) < args.min_zeros:
                ax1.clear()
                ax1.set_title("GUE : en attente de {} zéros ({} lus)".format(args.min_zeros, len(t)))
                return
            dessiner_gue(ax1, ax2, t, args.bins)
            fig.suptitle(os.path.basename(csv) + " — MAJ " + pd.Timestamp.now().strftime("%H:%M:%S"))

        maj()
        _anim = FuncAnimation(fig, maj, interval=int(args.refresh * 1000), cache_frame_data=False)
        plt.show()
        return

    t = lire_zeros(trouver_csv(args.chemin), args.colonne)
    fig, st = figure_gue(t, args.bins)
    print("zéros                :", st["n"])
    print("moyenne de s         : {:.4f}  (attendu ~1)".format(st["moyenne"]))
    print("variance de s        : {:.4f}  (GUE ≈ 0.18, Poisson = 1)".format(st["variance"]))
    print("part de s < 0.1      : {:.3%}  (GUE surmise ≈ 0.11 %, Poisson ≈ 9.5 %)".format(st["part_s01"]))
    print("plus petit écart brut: {:.6f}".format(st["min_brut"]))
    if args.sortie:
        fig.savefig(args.sortie, dpi=120)
        print("enregistré :", args.sortie)
    else:
        plt.show()


if __name__ == "__main__":
    main()

# zeta_gue_hist.py · hprzeta · MAJ 2026-10-17 · 136 lignes
