#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calcul des zéros non triviaux de ζ(s) sur la droite critique Re(s) = 1/2
────────────────────────────────────────────────────────────────────────────
Méthode   : Fonction Z de Hardy  +  affinage Illinois (bisection améliorée)
Précision : mpmath (50 décimales par défaut)
Auteur : hprzeta
────────────────────────────────────────────────────────────────────────────

THÉORIE RAPIDE
══════════════
• ζ(s) = Σ 1/nˢ  (définie pour Re(s) > 1, puis prolongement analytique)
• Les zéros NON TRIVIAUX sont dans la bande critique  0 < Re(s) < 1
• Hypothèse de Riemann : tous ont Re(s) = 1/2  (la "droite critique")
• Fonction Z de Hardy :  Z(t) = exp(iθ(t)) · ζ(1/2 + it)  ∈ ℝ
  → Z(t) est réelle, donc on peut chercher ses changements de signe
  → Chaque changement de signe ↔ un zéro de ζ sur la droite critique
• θ(t) = Im[ln Γ(1/4 + it/2)] − (t/2)·ln π   (phase de Riemann)
"""

# ── Bibliothèques standard ──────────────────────────────────────────────────
import math
import time
from datetime import datetime
from pathlib import Path
from typing import List

# ── Bibliothèques scientifiques ─────────────────────────────────────────────
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from mpmath import mp, zeta, loggamma, findroot


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 1 — SAISIE INTERACTIVE (s'exécute au lancement)
# ═══════════════════════════════════════════════════════════════════════════

def saisir_parametres() -> tuple:
    """
    Demande à l'utilisateur les paramètres de calcul via la console Spyder.
    Retourne (T_MAX, STEP, HORODATAGE).
    """
    print()
    print("=" * 60)
    print("   CALCUL DES ZÉROS NON TRIVIAUX DE ζ(s)")
    print("=" * 60)
    print()
    print("  Formule de Riemann–von Mangoldt :")
    print("  N(T) ≈ T/(2π) · ln(T/2πe)  zéros jusqu'à t = T")
    print()
    print("  Exemples de référence :")
    print("    T =   100  →  ~  29 zéros")
    print("    T =   500  →  ~ 182 zéros")
    print("    T =  1000  →  ~ 396 zéros")
    print("    T = 10000  →  ~4516 zéros")
    print()

    # ── Saisie de T_MAX ────────────────────────────────────────────────────
    while True:
        try:
            T_MAX = float(input("  Entrez T_MAX (valeur minimale : 20) : "))
            if T_MAX < 20:
                print("  ⚠️  T_MAX doit être ≥ 20. Le premier zéro est à t ≈ 14.13.")
            else:
                break
        except ValueError:
            print("  ⚠️  Entrez un nombre valide (ex : 500).")

    # ── Saisie du pas (optionnel) ──────────────────────────────────────────
    print()
    print("  Pas de balayage (STEP) :")
    print("    0.1   → rapide  (peut rater des zéros proches)")
    print("    0.05  → équilibré  ← recommandé")
    print("    0.01  → lent mais fiable")
    choix_step = input("  Entrez le pas [Entrée = 0.05] : ").strip()
    STEP = float(choix_step) if choix_step else 0.05

    # ── Estimation théorique ───────────────────────────────────────────────
    n_attendus = int(T_MAX / (2 * math.pi) * math.log(T_MAX / (2 * math.pi * math.e)))

    print()
    print("  ┌─ Résumé des paramètres ──────────────────────────┐")
    print(f"  │  T_MAX    = {T_MAX:<10.1f}                          │")
    print(f"  │  STEP     = {STEP:<10.4f}                          │")
    print(f"  │  Zéros attendus ≈ {n_attendus:<6d}                       │")
    print(f"  │  Précision  = {mp.dps} décimales (mpmath)          │")
    print("  └──────────────────────────────────────────────────┘")
    print()

    # ── Horodatage capturé UNE FOIS ici ───────────────────────────────────
    # Explication : datetime.now() capture l'instant présent.
    # strftime("%Y%m%d_%H%M%S") le formate en chaîne sans espaces ni /:
    #   %Y = année 4 chiffres, %m = mois, %d = jour
    #   %H = heure (0-23), %M = minutes, %S = secondes
    # Exemple : 20260419_143217
    HORODATAGE = datetime.now().strftime("%Y%m%d_%H%M%S")

    return T_MAX, STEP, HORODATAGE


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 2 — FONCTIONS MATHÉMATIQUES
# ═══════════════════════════════════════════════════════════════════════════

def theta(t: float) -> float:
    """
    Fonction theta de Riemann.

    Définition :
        θ(t) = Im[ ln Γ(1/4 + it/2) ] − (t/2)·ln(π)

    Rôle : c'est la "phase" de ζ(1/2+it).
    En multipliant ζ par exp(iθ), on annule la partie imaginaire
    et on obtient une fonction RÉELLE Z(t).

    Γ = fonction Gamma (généralisation de la factorielle aux réels)
    Im = partie imaginaire d'un nombre complexe
    """
    return float(
        mp.im(loggamma(mp.mpf("0.25") + mp.mpc(0, t) / 2))
        - (t / 2) * mp.log(mp.pi)
    )


def Z(t: float) -> float:
    """
    Fonction Z de Hardy (aussi appelée fonction Z de Riemann).

    Définition :
        Z(t) = exp(iθ(t)) · ζ(1/2 + it)

    Propriétés fondamentales :
        1. Z(t) ∈ ℝ  pour tout t ∈ ℝ   ← réelle !
        2. Z(t) = 0  ⟺  ζ(1/2+it) = 0  ← mêmes zéros que ζ

    Grâce à la propriété 1, on peut détecter les zéros par changement
    de signe : si Z(a) > 0 et Z(b) < 0, il y a un zéro entre a et b.
    C'est le Théorème des Valeurs Intermédiaires (TVI).

    CORRECTION DU BUG ORIGINAL :
        ❌  zeta(0.5+1j*t) * mp.exp(1j*theta(t)).real
            → .real s'applique seulement à exp(), pas au produit entier
            → résultat complexe → comparaison < 0 impossible → erreur !

        ✅  (mp.exp(iθ) · ζ(1/2+it)).real
            → .real s'applique au produit ENTIER → float → OK
    """
    valeur_complexe = mp.exp(mp.mpc(0, theta(t))) * zeta(mp.mpc("0.5", t))
    return float(valeur_complexe.real)  # float Python standard


def affiner_zero(t_gauche: float, t_droite: float, tol: float = 1e-20) -> float:
    """
    Localise précisément un zéro de Z(t) dans l'intervalle [t_gauche, t_droite].

    Méthode Illinois (variante de la bisection) :
        - Robuste : converge toujours si Z change de signe dans l'intervalle
        - Rapide  : convergence super-linéaire (mieux que la bisection pure)
        - On travaille sur Z(t) réelle, pas sur ζ complexe directement

    Paramètres :
        t_gauche, t_droite : bornes de l'intervalle (changement de signe détecté)
        tol                : tolérance souhaitée (1e-20 ≈ 20 décimales exactes)
    """
    try:
        t0 = findroot(
            lambda t: Z(float(t)),    # Z retourne un float → pas de bug de type
            (t_gauche, t_droite),     # intervalle d'encadrement
            solver="illinois",        # méthode robuste pour zéros simples
            tol=tol,
            maxsteps=150
        )
        return float(t0)
    except Exception as e:
        print(f"\n  ⚠️  Affinage échoué sur [{t_gauche:.4f}, {t_droite:.4f}] : {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 3 — ALGORITHME PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def calculer_zeros(T_MAX: float, STEP: float) -> List[float]:
    """
    Balayage de la droite critique pour trouver les zéros de ζ(1/2+it).

    Algorithme en 2 passes :
    ┌─────────────────────────────────────────────────────────────────┐
    │  PASSE 1 – DÉTECTION                                           │
    │  On évalue Z(t) à intervalles réguliers (pas = STEP).         │
    │  Si Z(t−step) · Z(t) < 0 → changement de signe → zéro !      │
    │                                                                 │
    │  PASSE 2 – AFFINAGE                                            │
    │  On localise le zéro précisément par la méthode Illinois.      │
    │  On vérifie : |ζ(1/2 + it₀)| < 1e-10                         │
    └─────────────────────────────────────────────────────────────────┘

    Risque : si deux zéros sont dans le même intervalle STEP,
    on n'en détectera qu'un. Réduire STEP diminue ce risque.
    """
    T_MIN = 10.0   # On commence à 10 (le 1er zéro est à t ≈ 14.13)
    zeros = []

    t      = T_MIN
    Z_prev = Z(t)          # Premier point de référence — c'est un float !
    n_steps = int((T_MAX - T_MIN) / STEP)

    print(f"  Balayage de t={T_MIN} à t={T_MAX} avec pas={STEP}")
    print(f"  Soit {n_steps} évaluations de Z(t) ...\n")

    for _ in tqdm(range(n_steps), desc="  Recherche", unit="pas", ncols=70):

        t      += STEP
        Z_curr  = Z(t)     # Z() retourne un float → comparaison < 0 fonctionne ✅

        # ── Détection : changement de signe ? ─────────────────────────────
        # Z_prev * Z_curr < 0  signifie : l'un est positif, l'autre négatif
        # → la courbe a croisé l'axe des x entre les deux points
        # → il y a forcément un zéro dans cet intervalle (TVI)
        if Z_prev * Z_curr < 0:

            # ── Affinage précis ───────────────────────────────────────────
            t_zero = affiner_zero(t - STEP, t)

            if t_zero is not None:
                # Vérification : est-ce vraiment un zéro de ζ ?
                residu = abs(zeta(mp.mpc("0.5", t_zero)))

                if float(residu) < 1e-10:
                    zeros.append(t_zero)
                    tqdm.write(
                        f"  ✅  Zéro #{len(zeros):5d} : "
                        f"t = {t_zero:.15f}   |ζ| = {float(residu):.2e}"
                    )
                else:
                    tqdm.write(
                        f"  ❌  Faux positif : t = {t_zero:.6f}   |ζ| = {float(residu):.2e}"
                    )

        Z_prev = Z_curr

    return zeros


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 4 — SAUVEGARDE
# ═══════════════════════════════════════════════════════════════════════════

def sauvegarder(zeros: List[float], T_MAX: float, HORODATAGE: str) -> pd.DataFrame:
    """
    Sauvegarde les zéros dans un fichier CSV.

    Nom du fichier : zeros_zeta_T<T_MAX>_<AAAAMMJJ>_<HHMMSS>.csv
    Exemple        : zeros_zeta_T500_20260419_143217.csv

    Avantages de ce format :
      • Tri alphabétique = tri chronologique dans l'explorateur de fichiers
      • Plusieurs calculs avec T_MAX différents ne s'écrasent pas
      • Plusieurs lancements du même jour ne s'écrasent pas
    """
    # Construction du nom — f-string = formatage de chaîne Python
    # {T_MAX:.0f} = T_MAX sans décimale  (ex: 500.0 → "500")
    # {HORODATAGE} = la chaîne capturée au démarrage (ex: "20260419_143217")
    nom_fichier = f"zeros_zeta_T{T_MAX:.0f}_{HORODATAGE}.csv"

    df = pd.DataFrame({
        "n":                  range(1, len(zeros) + 1),
        "partie_imaginaire":  zeros,
        "T_MAX":              T_MAX,
        "methode":            "Hardy-Z + Illinois",
        "precision_dps":      mp.dps,
        "calcule_le":         HORODATAGE,
    })

    chemin = Path(nom_fichier)
    df.to_csv(chemin, index=False)
    print(f"\n  💾  {len(zeros)} zéros sauvegardés → {chemin.resolve()}")
    return df


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 5 — VISUALISATION
# ═══════════════════════════════════════════════════════════════════════════

def visualiser(zeros: List[float], T_MAX: float, HORODATAGE: str):
    """
    Génère deux graphiques et les sauvegarde.

    Graphique 1 — Distribution des espacements entre zéros consécutifs
        Contexte mathématique : la conjecture de Montgomery (1973) prédit
        que cette distribution suit celle des valeurs propres de matrices
        aléatoires unitaires (GUE = Gaussian Unitary Ensemble).
        C'est une connexion profonde avec la physique quantique !

    Graphique 2 — Zéros sur la droite critique
        Visualise directement l'Hypothèse de Riemann :
        tous les points devraient être sur la ligne Re(s) = 1/2.
    """
    if len(zeros) < 2:
        print("  ⚠️  Moins de 2 zéros — pas de graphique.")
        return

    ecarts = np.diff(zeros)  # Différences entre zéros consécutifs
    nom_png = f"zeros_zeta_T{T_MAX:.0f}_{HORODATAGE}.png"

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        f"Zéros de ζ(1/2+it) — {len(zeros)} zéros  [T_MAX={T_MAX:.0f}]",
        fontsize=14, fontweight="bold"
    )

    # ── Graphique 1 : distribution des espacements ─────────────────────────
    axes[0].hist(ecarts, bins=40, edgecolor="black", alpha=0.75, color="steelblue")
    axes[0].axvline(
        np.mean(ecarts), color="red", linestyle="--", linewidth=1.5,
        label=f"Moyenne = {np.mean(ecarts):.4f}"
    )
    axes[0].set_xlabel("Écart Δt entre zéros consécutifs")
    axes[0].set_ylabel("Fréquence")
    axes[0].set_title(
        "Distribution des espacements\n"
        "(→ corrélation de paires de Montgomery / GUE)"
    )
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # ── Graphique 2 : zéros sur la droite critique ─────────────────────────
    axes[1].scatter(
        [0.5] * len(zeros), zeros,
        s=8, color="darkblue", alpha=0.5
    )
    axes[1].axvline(
        0.5, color="red", linestyle="--", linewidth=1.5,
        label="Re(s) = 1/2  (droite critique)"
    )
    axes[1].set_xlabel("Re(s)")
    axes[1].set_ylabel("Im(s) = t")
    axes[1].set_title(
        "Zéros sur la droite critique\n"
        "Hypothèse de Riemann : ils sont TOUS ici"
    )
    axes[1].set_xlim(0.0, 1.0)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(nom_png, dpi=150)
    print(f"  📈  Graphique sauvegardé → {Path(nom_png).resolve()}")
    plt.show()


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 6 — VÉRIFICATION
# ═══════════════════════════════════════════════════════════════════════════

def verifier_premiers_zeros(zeros: List[float]):
    """
    Compare les premiers zéros calculés avec les valeurs de référence
    (issues de la base LMFDB / tables de Riemann).

    Les 10 premiers zéros sont connus avec une précision de plusieurs
    centaines de décimales. Un bon calcul devrait donner un écart < 1e-6.
    """
    # Valeurs de référence (parties imaginaires des 10 premiers zéros)
    references = [
        14.134725141734693,
        21.022039638771555,
        25.010857580145688,
        30.424876125859513,
        32.935061587739189,
        37.586178158825671,
        40.918719012147495,
        43.327073280914999,
        48.005150881167159,
        49.773832477672302,
    ]

    n_check = min(len(zeros), len(references))
    if n_check == 0:
        print("  ⚠️  Aucun zéro à vérifier.")
        return

    print(f"\n  Vérification des {n_check} premiers zéros :")
    print(f"  {'#':>4}  {'Calculé':>20}  {'Référence':>20}  {'Écart':>12}")
    print("  " + "─" * 62)

    for i in range(n_check):
        ecart = abs(zeros[i] - references[i])
        statut = "✅" if ecart < 1e-8 else ("⚠️ " if ecart < 1e-4 else "❌")
        print(
            f"  {i+1:>4}  {zeros[i]:>20.15f}  "
            f"{references[i]:>20.15f}  {ecart:>12.2e}  {statut}"
        )


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 7 — POINT D'ENTRÉE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def main():
    # ── Configuration de la précision mpmath ──────────────────────────────
    mp.dps = 50   # 50 décimales (double précision standard = ~15 décimales)

    debut = time.time()

    # ── 1. Saisie interactive ──────────────────────────────────────────────
    T_MAX, STEP, HORODATAGE = saisir_parametres()

    # ── 2. Calcul des zéros ────────────────────────────────────────────────
    zeros = calculer_zeros(T_MAX, STEP)

    duree = time.time() - debut

    # ── 3. Rapport de synthèse ────────────────────────────────────────────
    print()
    print("=" * 60)
    print(f"  RÉSULTATS  —  {len(zeros)} zéros trouvés")
    print("=" * 60)
    print(f"  T_MAX     = {T_MAX:.1f}")
    print(f"  Durée     = {duree/60:.1f} min  ({duree:.0f} secondes)")
    if zeros:
        print(f"  1er zéro  : t = {zeros[0]:.10f}")
        print(f"  Dernier   : t = {zeros[-1]:.10f}")
        n_attendus = int(T_MAX / (2*math.pi) * math.log(T_MAX / (2*math.pi*math.e)))
        print(f"  Attendus  ≈ {n_attendus}  (formule Riemann–von Mangoldt)")
        print(f"  Taux      = {len(zeros)/T_MAX:.3f} zéros par unité t")

    # ── 4. Vérification ────────────────────────────────────────────────────
    verifier_premiers_zeros(zeros)

    # ── 5. Sauvegarde CSV ──────────────────────────────────────────────────
    if zeros:
        sauvegarder(zeros, T_MAX, HORODATAGE)

    # ── 6. Graphiques ──────────────────────────────────────────────────────
    if zeros:
        visualiser(zeros, T_MAX, HORODATAGE)

    print()
    print("=" * 60)
    print("  Calcul terminé.")
    print("=" * 60)


if __name__ == "__main__":
    main()
