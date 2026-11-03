#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
localiser_manques.py — Localise (puis retrouve) les zéros manquants d'un jeu de zéros de ζ.

Pourquoi : pour un jeu à grande hauteur (ex. V13 à T = 5·10⁶, 97 manquants sur 10⁷ zéros),
la validation de Turing dit COMBIEN de zéros manquent, pas OÙ. Recalculer tout coûte ≈ 30 h ;
localiser chaque manque par dichotomie sur N_exact puis l'affiner coûte ≈ 35 min à 2,5 h.

Principe (dichotomie sur le déficit) :
    Les zéros du CSV, triés, sont t_0 < t_1 < ... < t_{m-1}. On pose p_k = milieu de ]t_k ; t_{k+1}[
    (p_{-1} = t_0 − ε ; p_{m-1} = t_{m-1} + ε), et le déficit
        d(k) = N_exact(p_k) − (k + 1)        (zéros vrais ≤ p_k, moins zéros du CSV ≤ p_k)
    d(-1) = 0 ; d est constant tant qu'il ne manque rien. Si d(lo) ≠ d(hi), il manque (ou il y a
    en trop) d(hi) − d(lo) zéros dans ]p_lo ; p_hi[. On coupe en deux jusqu'à hi = lo + 1 : la
    fenêtre ]p_lo ; p_hi[ ne contient qu'un seul zéro du CSV (t_{lo+1}) et les manquants.
    Coût : ≈ log2(m) évaluations de N_exact par manque, au lieu de m.

Étape 2 (--affiner) : dans chaque fenêtre, balayage de Z(t) (Arb, repli mpmath) à pas fin, bissection
    sur chaque changement de signe, retrait des zéros déjà dans le CSV. Un manque non retrouvé est
    signalé INCOMPLET (jamais passé sous silence). Le CSV d'origine n'est JAMAIS modifié.

Statut des affirmations :
    - N_exact = round(θ/π + 1 + S) : formule de Backlund (prouvée) ; S(T) est calculée numériquement
      (précision dps) -> VÉRIFIÉ NUMÉRIQUEMENT, pas démontré, pour chaque T évalué.
    - Limite : si un zéro du CSV est en trop (doublon, faux positif), d peut décroître ; la dichotomie
      détecte alors d(hi) ≠ d(lo) mais ne distingue pas manque/surplus (le signe de l'écart est reporté).

Usage :
    python scripts_v17/localiser_manques.py zeros.csv [--workers 4] [--chunks 64]
                                            [--affiner] [--sortie dossier] [--dps 35]

Auteur : hprzeta — Projet Hypothèse de Riemann · 2026-11-03
"""

import os
import sys
import math
import time
import argparse
from pathlib import Path
from multiprocessing import Pool          # multiprocessing (fork-safe) — pas de joblib avec mpmath

import numpy as np
import pandas as pd

# ── Accès aux modules de calcul (turing_validation, arb_wrapper)
RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "src" / "calculs" / "optimisation"))

EPS_BORD = 1e-4          # décalage hors du premier/dernier zéro (même valeur que EPS_CONTROLE)
_T = None                # tableau des zéros, partagé par les workers (hérité par fork)
_DPS = 35                # précision de N_exact, fixée dans main() avant la création du Pool


def lire_zeros(chemin: str) -> np.ndarray:
    """Lit la colonne partie_imaginaire en lecture EXACTE (aller-retour float), triée."""
    df = pd.read_csv(chemin, usecols=["partie_imaginaire"], float_precision="round_trip")
    t = np.sort(df["partie_imaginaire"].to_numpy(dtype=np.float64))   # tri croissant
    return t


def point_controle(k: int) -> float:
    """p_k : milieu de ]t_k ; t_{k+1}[ ; bords : t_0 − ε (k = −1) et t_{m−1} + ε (k = m−1)."""
    m = len(_T)
    if k < 0:
        return float(_T[0]) - EPS_BORD                     # avant le premier zéro
    if k >= m - 1:
        return float(_T[-1]) + EPS_BORD                    # après le dernier zéro
    return 0.5 * (float(_T[k]) + float(_T[k + 1]))         # milieu de l'intervalle


def deficit(k: int) -> int:
    """d(k) = N_exact(p_k) − (k + 1) ; d(−1) = 0 par convention (N(t_0 − ε) = 0)."""
    if k < 0:
        return 0
    from turing_validation import N_exact                   # import tardif (mpmath lourd)
    return int(N_exact(point_controle(k), dps=_DPS)) - (k + 1)


def _deficit_pour_pool(k: int):
    """Enveloppe picklable pour Pool.map : (k, d(k))."""
    return k, deficit(k)


def bissecter(args):
    """Cherche toutes les fenêtres à écart de déficit dans ]lo ; hi] (d(lo), d(hi) connus).

    Retourne la liste de (lo, hi, d_lo, d_hi) avec hi = lo + 1, et le nombre d'évaluations faites.
    """
    lo, hi, d_lo, d_hi = args
    trouvees, n_eval = [], 0
    pile = [(lo, hi, d_lo, d_hi)]                           # pile explicite (pas de récursion profonde)
    while pile:
        a, b, da, db = pile.pop()
        if da == db:                                        # aucun écart : rien à chercher ici
            continue
        if b - a == 1:                                      # fenêtre minimale : un seul zéro du CSV
            trouvees.append((a, b, da, db))
            continue
        c = (a + b) // 2                                    # milieu (indices)
        dc = deficit(c)                                     # une évaluation de N_exact
        n_eval += 1
        pile.append((c, b, dc, db))                         # moitié droite
        pile.append((a, c, da, dc))                         # moitié gauche
    return trouvees, n_eval


def localiser(t: np.ndarray, workers: int, chunks: int, log=print):
    """Étape 1 : renvoie la liste triée des fenêtres (a, b, nb) avec nb = d(hi) − d(lo)."""
    global _T
    _T = t
    m = len(t)
    bornes = sorted(set(int(x) for x in np.linspace(-1, m - 1, chunks + 1)))   # indices de découpe
    t0 = time.time()
    with Pool(workers) as pool:
        d_bornes = dict(pool.map(_deficit_pour_pool, bornes))                  # d aux bornes (parallèle)
        log(f"  [bornes] {len(bornes)} évaluations — {time.time() - t0:.0f} s — "
            f"déficit total d(m−1) = {d_bornes[bornes[-1]]}")
        taches = [(bornes[i], bornes[i + 1], d_bornes[bornes[i]], d_bornes[bornes[i + 1]])
                  for i in range(len(bornes) - 1) if d_bornes[bornes[i]] != d_bornes[bornes[i + 1]]]
        log(f"  [découpe] {len(taches)} tranches contiennent un écart sur {len(bornes) - 1}")
        fenetres, n_eval = [], len(bornes)
        for trouvees, ne in pool.imap_unordered(bissecter, taches):            # bissection parallèle
            fenetres += trouvees
            n_eval += ne
            log(f"  [bissection] {len(fenetres)} fenêtres, {n_eval} évaluations — {time.time() - t0:.0f} s")
    fenetres.sort()
    # nb de zéros en écart dans la fenêtre = d(hi) − d(lo) (négatif => surplus dans le CSV)
    return [(point_controle(a), point_controle(b), db - da) for a, b, da, db in fenetres], n_eval


def _z(t: float) -> float:
    """Z(t) via Arb (double) avec repli mpmath — même chaîne que la production."""
    from arb_wrapper import arb_hardy_z
    return float(arb_hardy_z(t))


def zeros_dans_fenetre(a: float, b: float, nb_pas: int) -> list:
    """Racines de Z(t) dans [a ; b] : balayage à nb_pas pas, puis bissection (60 itérations)."""
    ts = np.linspace(a, b, nb_pas + 1)                      # grille fine de la fenêtre
    zs = [_z(float(x)) for x in ts]                         # Z aux nœuds
    racines = []
    for i in range(nb_pas):
        if zs[i] == 0.0 or zs[i] * zs[i + 1] < 0:           # changement de signe => une racine
            lo, hi, zlo = float(ts[i]), float(ts[i + 1]), zs[i]
            for _ in range(60):                             # bissection : ~1e-18 relatif, plancher float64
                mil = 0.5 * (lo + hi)
                zm = _z(mil)
                if zlo * zm <= 0:
                    hi = mil
                else:
                    lo, zlo = mil, zm
            racines.append(0.5 * (lo + hi))
    return racines


def affiner(fenetres, t: np.ndarray, log=print):
    """Étape 2 : retrouve les zéros absents du CSV dans chaque fenêtre."""
    lignes = []
    for (a, b, nb) in fenetres:
        connus = t[(t > a) & (t < b)]                       # zéros du CSV dans la fenêtre
        attendu = len(connus) + nb                          # nombre vrai de zéros dans la fenêtre
        trouves = []
        for facteur in (400, 1600, 6400):                   # on raffine la grille si le compte ne colle pas
            trouves = zeros_dans_fenetre(a, b, facteur)
            if len(trouves) == attendu:
                break
        nouveaux = [r for r in trouves if not np.any(np.abs(connus - r) < 1e-6)]   # absents du CSV
        statut = "OK" if (len(trouves) == attendu and len(nouveaux) == nb) else "INCOMPLET"
        log(f"  fenêtre [{a:.6f} ; {b:.6f}] attendu {attendu}, trouvés {len(trouves)}, "
            f"nouveaux {len(nouveaux)} -> {statut}")
        for r in nouveaux:
            lignes.append({"partie_imaginaire": r, "fenetre_a": a, "fenetre_b": b, "statut": statut})
        if statut == "INCOMPLET" and not nouveaux:          # rien retrouvé : on garde une trace explicite
            lignes.append({"partie_imaginaire": float("nan"), "fenetre_a": a, "fenetre_b": b, "statut": statut})
    return pd.DataFrame(lignes, columns=["partie_imaginaire", "fenetre_a", "fenetre_b", "statut"])


def main():
    global _DPS
    sys.stdout.reconfigure(line_buffering=True)   # log visible en direct même redirigé vers un fichier
    ap = argparse.ArgumentParser(description="Localise par dichotomie les zéros manquants d'un CSV")
    ap.add_argument("csv", help="CSV avec colonne partie_imaginaire")
    ap.add_argument("--workers", type=int, default=4, help="processus (défaut 4)")
    ap.add_argument("--chunks", type=int, default=64, help="tranches initiales (défaut 64)")
    ap.add_argument("--dps", type=int, default=35, help="précision de N_exact (défaut 35)")
    ap.add_argument("--affiner", action="store_true", help="retrouver aussi les zéros (étape 2)")
    ap.add_argument("--sortie", default=None, help="dossier de sortie (défaut : à côté du CSV)")
    a = ap.parse_args()
    _DPS = a.dps

    t = lire_zeros(a.csv)
    print(f"  {len(t)} zéros lus (t_max = {t[-1]:.6f})")
    t0 = time.time()
    fenetres, n_eval = localiser(t, a.workers, a.chunks)
    print(f"  => {len(fenetres)} fenêtres, {sum(f[2] for f in fenetres)} zéros en écart "
          f"(net), {n_eval} évaluations de N_exact, {time.time() - t0:.0f} s")
    sortie = Path(a.sortie) if a.sortie else Path(a.csv).resolve().parent
    sortie.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(fenetres, columns=["fenetre_a", "fenetre_b", "ecart"]).to_csv(
        sortie / "manques_fenetres.csv", index=False, float_format="%.12f")
    print(f"  fenêtres -> {sortie / 'manques_fenetres.csv'}")
    if a.affiner:
        df = affiner(fenetres, t)
        df.to_csv(sortie / "manques_complement.csv", index=False, float_format="%.12f")
        n_inc = int((df["statut"] == "INCOMPLET").sum())
        print(f"  complément -> {sortie / 'manques_complement.csv'} "
              f"({len(df)} lignes, {n_inc} INCOMPLET)")


if __name__ == "__main__":
    main()
