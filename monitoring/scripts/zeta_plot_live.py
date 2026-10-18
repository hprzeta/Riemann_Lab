#!/usr/bin/env python3
"""
zeta_plot_live.py — Suivi graphique en direct d'un run de zéros de zêta.

Deux graphiques sur un seul écran (rafraîchis toutes les 2 s, lecture incrémentale du CSV) :
  HAUT : colonnes = nombre de zéros calculés par tranche de t, bleu / gris en alternance,
         + courbe attendue (théorie : densité ln(t/2π)/2π, Riemann–von Mangoldt).
         Une colonne plus basse que la courbe = zéros manquants ou run en cours.
  BAS  : détail de chaque zéro : x = t, y = espacement normalisé avec le zéro suivant
         (1.0 = espacement moyen). Points rouges = écart brut < 0.01.

Usage (PC1) — via l'alias :  zeta-live [csv|dossier]
  ou :  nice -n 19 python zeta_plot_live.py <csv|dossier> --colonne partie_imaginaire
La fonction dessiner() est aussi utilisée par zeta_run_report.py (rapports de run).
Lecture seule : ne modifie jamais les fichiers du run.
"""
import argparse
import glob
import io
import math
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation

from zeta_mon_common import compacter, placer, titrer

BLEU, GRIS, ROUGE = "#3b78c4", "#9a9a9a", "#d62728"
NOMS_T = ("partie_imaginaire", "gamma", "t", "zero", "zero_t", "imag", "im")


def trouver_csv(chemin, apres=None):
    """Si on donne un dossier : prend le CSV modifié le plus récemment (et après `apres`, epoch, si donné)."""
    chemin = os.path.expanduser(str(chemin))
    if os.path.isdir(chemin):
        fichiers = glob.glob(os.path.join(chemin, "**", "*.csv"), recursive=True)
        if apres is not None:
            fichiers = [f for f in fichiers if os.path.getmtime(f) >= apres]
        return max(fichiers, key=os.path.getmtime) if fichiers else None
    return chemin


def _df(src):
    """Lit un CSV (chemin ou StringIO) ; détecte l'absence d'en-tête."""
    df = pd.read_csv(src, comment="#", on_bad_lines="skip")
    try:                      # 1re colonne numérique => pas d'en-tête
        float(str(df.columns[0]))
        if hasattr(src, "seek"):
            src.seek(0)
        df = pd.read_csv(src, comment="#", header=None, on_bad_lines="skip")
    except ValueError:
        pass
    return df


def _choisir(df, colonne=None):
    """Colonne de t : explicite (nom ou numéro) > noms connus > 1re colonne non entière et non constante."""
    col = None
    if colonne is not None:
        col = df.columns[int(colonne)] if str(colonne).isdigit() else colonne
    if col is None:
        col = next((c for c in df.columns if str(c).lower() in NOMS_T), None)
    if col is None:           # écarte l'index n et des colonnes constantes comme step
        for c in df.columns:
            x = pd.to_numeric(df[c], errors="coerce").dropna().to_numpy(float)
            if len(x) > 1 and x.std() > 0 and not np.array_equal(x, np.round(x)):
                col = c
                break
    if col is None:
        raise ValueError("colonne t introuvable : utiliser --colonne")
    return col


def lire_zeros(chemin, colonne=None):
    """Lit les zéros (valeurs de t) déjà écrits. Tolère un CSV en cours d'écriture."""
    df = _df(chemin)
    col = _choisir(df, colonne)
    return np.sort(pd.to_numeric(df[col], errors="coerce").dropna().to_numpy(float))


class LecteurZeros:
    """Lecture INCRÉMENTALE d'un CSV qui grossit : ne relit que les octets ajoutés depuis le dernier appel
    (rafraîchissement fluide même avec des millions de zéros). Ne lit que des lignes complètes."""

    def __init__(self, chemin, colonne=None):
        self.chemin, self.colonne = chemin, colonne
        self.t, self.pos, self.idx, self.trie = np.empty(0), 0, None, True

    def _octets(self):
        with open(self.chemin, "rb") as f:
            f.seek(self.pos)
            data = f.read()
        fin = data.rfind(b"\n") + 1            # jusqu'à la dernière ligne COMPLÈTE
        self.pos += fin
        return data[:fin].decode(errors="replace")

    def maj(self):
        """Retourne le tableau trié des zéros lus jusqu'ici."""
        if os.path.getsize(self.chemin) < self.pos:       # fichier recréé / tronqué
            self.__init__(self.chemin, self.colonne)
        pos0 = self.pos
        texte = self._octets()
        if not texte:
            return self.t
        if self.idx is None:                              # 1er passage : détecte la colonne
            try:
                df = _df(io.StringIO(texte))
                col = _choisir(df, self.colonne)
            except Exception:
                self.pos = pos0                           # en-tête seul pour l'instant : on réessaiera
                raise
            self.idx = df.columns.get_loc(col)
            new = pd.to_numeric(df[col], errors="coerce").dropna().to_numpy(float)
        else:
            d = pd.read_csv(io.StringIO(texte), header=None, usecols=[self.idx], comment="#",
                            on_bad_lines="skip")
            new = pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna().to_numpy(float)
        if len(new):
            if len(self.t) and new.min() < self.t[-1] or (len(new) > 1 and (np.diff(new) < 0).any()):
                self.trie = False
            self.t = np.concatenate([self.t, new])
        if not self.trie:
            self.t, self.trie = np.sort(self.t), True
        return self.t


def tranche_auto(t):
    """Largeur de tranche « ronde » (1, 2, 5 × 10^k) donnant ~40 colonnes."""
    brut = max(float(t[-1] - t[0]), 1.0) / 40
    p = 10 ** math.floor(math.log10(brut))
    return next(m * p for m in (1, 2, 5, 10) if m * p >= brut)


def dessiner(ax1, ax2, t, w=2000.0, max_points=30_000):
    """Trace les deux panneaux pour le tableau de zéros t (trié)."""
    k0, k1 = int(t[0] // w), int(t[-1] // w)
    bords = np.arange(k0, k1 + 2) * w
    comptes, _ = np.histogram(t, bins=bords)
    centres = bords[:-1] + w / 2
    couleurs = [BLEU if (k0 + i) % 2 == 0 else GRIS for i in range(len(comptes))]

    ax1.clear()
    ax1.bar(centres, comptes, width=w * 0.98, color=couleurs)
    attendu = np.log(np.maximum(centres, 10) / (2 * np.pi)) / (2 * np.pi) * w
    ax1.plot(centres, attendu, "k--", lw=1, label="attendu (Riemann–von Mangoldt)")
    ax1.set_title("Zéros calculés par tranche de t — {} zéros — t ∈ [{:.0f} ; {:.0f}]"
                  .format(len(t), t[0], t[-1]))
    ax1.set_xlabel("t")
    ax1.set_ylabel("nb de zéros / tranche")
    ax1.legend(loc="lower right")

    # Panneau bas : calculé seulement sur les points affichés (rapide même avec des millions de zéros)
    pas = max(1, (len(t) - 1) // max_points)
    idx = np.arange(0, len(t) - 1, pas)
    brut = t[idx + 1] - t[idx]
    tm = t[idx] + brut / 2
    norm = brut * np.log(np.maximum(tm, 10) / (2 * np.pi)) / (2 * np.pi)
    col_pts = np.where(((tm // w).astype(int) % 2) == 0, BLEU, GRIS)
    col_pts = np.where(brut < 0.01, ROUGE, col_pts)
    ax2.clear()
    ax2.scatter(tm, norm, s=2, c=col_pts)
    ax2.axhline(1.0, color="k", lw=0.8, ls="--")
    ax2.set_title("Détail par zéro : espacement normalisé (rouge = écart brut < 0.01)")
    ax2.set_xlabel("t")
    ax2.set_ylabel("espacement normalisé")
    ax2.set_ylim(0, max(3, min(5, np.nanmax(norm) * 1.05)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chemin", help="CSV du run, ou dossier du run")
    ap.add_argument("--tranche", type=float, default=2000.0, help="largeur d'une colonne en t")
    ap.add_argument("--colonne", default=None, help="nom ou numéro (0,1,2...) de la colonne t")
    ap.add_argument("--refresh", type=float, default=2.0, help="secondes (défaut 2 ; 1 = très fluide)")
    ap.add_argument("--geometrie", default=None, help="fenêtre : LARGEURxHAUTEUR+X+Y (ex. 900x500+75+35)")
    ap.add_argument("--apres", default=None, help="ISO : ignorer les CSV modifiés avant (début du run)")
    ap.add_argument("--max-points", type=int, default=30_000, help="sous-échantillonnage du nuage du bas")
    args = ap.parse_args()

    # Fenêtre normale (redimensionnable). Plein écran : touche « f » (déconseillé pendant un run).
    apres = __import__("datetime").datetime.fromisoformat(args.apres).timestamp() if args.apres else None
    if args.geometrie:
        compacter(args.geometrie)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), constrained_layout=True)
    titrer(fig, "Zêta — Zéros calculés en direct (tranches de t, espacements)")
    if args.geometrie:
        placer(fig, args.geometrie)

    etat = {"csv": None, "lecteur": None}

    def maj(_=None):
        csv = trouver_csv(args.chemin, apres)
        if not csv or not os.path.exists(csv):
            return
        try:
            if csv != etat["csv"]:                    # nouveau fichier : repartir de zéro
                etat["csv"], etat["lecteur"] = csv, LecteurZeros(csv, args.colonne)
            t = etat["lecteur"].maj()
        except Exception as e:                        # fichier en cours d'écriture
            print("lecture ignorée :", e)
            return
        if len(t) < 3:
            return
        dessiner(ax1, ax2, t, args.tranche, args.max_points)
        fig.suptitle(os.path.basename(csv) + " — MAJ " + pd.Timestamp.now().strftime("%H:%M:%S"))

    maj()
    _anim = FuncAnimation(fig, maj, interval=int(args.refresh * 1000), cache_frame_data=False)
    plt.show()


if __name__ == "__main__":
    main()

# zeta_plot_live.py · hprzeta · MAJ 2026-10-17 · 216 lignes
