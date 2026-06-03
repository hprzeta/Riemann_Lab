#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calcul haute précision des zéros non triviaux de ζ(s) sur la droite critique
────────────────────────────────────────────────────────────────────────────
Méthode   : Vraie fonction Z de Hardy  +  affinage Illinois (bisection améliorée)
Précision : mpmath (50 décimales par défaut)
Auteur    : hprzeta — Exploration de l'Hypothèse de Riemann
Date      : 2026
────────────────────────────────────────────────────────────────────────────

THÉORIE RAPIDE
══════════════
• ζ(s) = Σ 1/nˢ  (définie pour Re(s) > 1, puis prolongement analytique)
• Les zéros NON TRIVIAUX sont dans la bande critique  0 < Re(s) < 1
• Hypothèse de Riemann : tous ont Re(s) = 1/2  (la "droite critique")
• Fonction Z de Hardy :  Z(t) = exp(iθ(t)) · ζ(1/2 + it)  ∈ ℝ
  → Z(t) est réelle, donc on peut chercher ses changements de signe
  → Chaque changement de signe ↔ un zéro de ζ sur la droite critique
• θ(t) = Im[ln Γ(1/4 + it/2)] − (t/2)·ln π   (phase de Riemann-Siegel)

POURQUOI Z(t) ET PAS Re(ζ) ?
══════════════════════════════
❌  Re(ζ(½+it)) — partie réelle brute, oscille sans structure claire,
    génère de faux changements de signe → Newton diverge → overflow GMP

✅  Z(t) = Re(e^(iθ) · ζ(½+it)) — la multiplication par e^(iθ) "annule
    la rotation" du nombre complexe ζ. Z(t) est réellement stable,
    Illinois converge proprement, pas d'overflow.

ORGANISATION DES FICHIERS
══════════════════════════
Chaque lancement crée un dossier dédié :
    calculs/
    └── T{T_MAX}_{AAAAMMJJ_HHMMSS}/
        ├── zeros_zeta_T{T_MAX}_{AAAAMMJJ_HHMMSS}.csv       ← résultats finaux
        ├── zeros_zeta_T{T_MAX}_{AAAAMMJJ_HHMMSS}.log       ← journal complet
        ├── zeros_zeta_T{T_MAX}_{AAAAMMJJ_HHMMSS}.png       ← graphiques
        └── zeros_intermediaire_T{T_MAX}_{AAAAMMJJ_HHMMSS}.csv  ← sauvegardes
"""

# ── Bibliothèques standard ──────────────────────────────────────────────────
import sys
import math
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# ── Bibliothèques scientifiques ─────────────────────────────────────────────
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from mpmath import mp, zeta, loggamma, findroot
from loguru import logger
import psutil


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 1 — SAISIE INTERACTIVE
# ═══════════════════════════════════════════════════════════════════════════

def saisir_parametres() -> Tuple[float, float, str, Path]:
    """
    Demande les paramètres de calcul via la console.
    Retourne (T_MAX, STEP, HORODATAGE, DOSSIER).

    Crée automatiquement le dossier de sortie :
        calculs/T{T_MAX}_{AAAAMMJJ_HHMMSS}/
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
            print("  ⚠️  Entrez un nombre valide (ex : 1000).")

    # ── Saisie du pas ──────────────────────────────────────────────────────
    print()
    print("  Pas de balayage (STEP) :")
    print("    0.1   → rapide  (peut rater des zéros très proches)")
    print("    0.05  → équilibré  ← recommandé")
    print("    0.01  → lent mais fiable")
    choix_step = input("  Entrez le pas [Entrée = 0.05] : ").strip()
    STEP = float(choix_step) if choix_step else 0.05

    # ── Estimation théorique ───────────────────────────────────────────────
    n_attendus = int(T_MAX / (2 * math.pi) * math.log(T_MAX / (2 * math.pi * math.e)))

    # ── Horodatage capturé UNE FOIS ───────────────────────────────────────
    HORODATAGE = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── Création du dossier de sortie ─────────────────────────────────────
    # Structure : calculs/T{T_MAX}_{HORODATAGE}/
    # Exemple   : calculs/T1000_20260425_143217/
    nom_dossier = f"T{T_MAX:.0f}_{HORODATAGE}"
    DOSSIER = Path("calculs") / nom_dossier
    DOSSIER.mkdir(parents=True, exist_ok=True)

    print()
    print("  ┌─ Résumé des paramètres ──────────────────────────┐")
    print(f"  │  T_MAX          = {T_MAX:<10.1f}                    │")
    print(f"  │  STEP           = {STEP:<10.4f}                    │")
    print(f"  │  Zéros attendus ≈ {n_attendus:<6d}                       │")
    print(f"  │  Précision      = {mp.dps} décimales (mpmath)      │")
    print(f"  │  Dossier        = {str(DOSSIER):<36s}  │")
    print("  └──────────────────────────────────────────────────┘")
    print()

    return T_MAX, STEP, HORODATAGE, DOSSIER


def configurer_logger(T_MAX: float, HORODATAGE: str, DOSSIER: Path):
    """
    Configure le logger APRÈS la saisie, pour écrire dans le bon dossier.
    Le fichier log est nommé : zeros_zeta_T{T_MAX}_{HORODATAGE}.log
    """
    logger.remove()  # Supprime le handler par défaut

    chemin_log = DOSSIER / f"zeros_zeta_T{T_MAX:.0f}_{HORODATAGE}.log"

    logger.add(
        str(chemin_log),
        rotation="100 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="DEBUG"
    )
    logger.add(sys.stderr, level="INFO")

    logger.info(f"📁 Dossier de sortie : {DOSSIER.resolve()}")
    logger.info(f"📄 Fichier log       : {chemin_log.name}")


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 2 — FONCTIONS MATHÉMATIQUES
# ═══════════════════════════════════════════════════════════════════════════

def theta(t: float) -> float:
    """
    Fonction thêta de Riemann-Siegel — la "phase" de ζ(½+it).

    Définition :
        θ(t) = Im[ ln Γ(¼ + it/2) ] − (t/2)·ln(π)

    Rôle :
        En multipliant ζ(½+it) par exp(iθ(t)), on annule la partie
        imaginaire et on obtient une fonction RÉELLE Z(t).
    """
    return float(
        mp.im(loggamma(mp.mpf("0.25") + mp.mpc(0, t) / 2))
        - (t / 2) * mp.log(mp.pi)
    )


def Z(t: float) -> float:
    """
    Vraie fonction Z de Hardy (aussi appelée fonction Z de Riemann).

    Définition :
        Z(t) = exp(iθ(t)) · ζ(½ + it)

    Propriétés fondamentales :
        1. Z(t) ∈ ℝ  pour tout t ∈ ℝ   ← réelle !
        2. Z(t) = 0  ⟺  ζ(½+it) = 0   ← mêmes zéros que ζ
    """
    valeur_complexe = mp.exp(mp.mpc(0, theta(t))) * zeta(mp.mpc("0.5", t))
    return float(valeur_complexe.real)


def affiner_zero(t_gauche: float, t_droite: float, tol: float = 1e-20) -> float:
    """
    Localise précisément un zéro de Z(t) dans l'intervalle [t_gauche, t_droite].
    Méthode Illinois (variante de la bisection).
    """
    try:
        t0 = findroot(
            lambda t: Z(float(t)),
            (t_gauche, t_droite),
            solver="illinois",
            tol=tol,
            maxsteps=150
        )
        return float(t0)
    except Exception as e:
        logger.debug(f"Affinage échoué [{t_gauche:.4f}, {t_droite:.4f}] : {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 3 — MONITORING SYSTÈME
# ═══════════════════════════════════════════════════════════════════════════

def log_resources():
    """Enregistre CPU et RAM via psutil."""
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    logger.info(
        f"📊 CPU: {cpu:.1f}% | "
        f"RAM: {mem.used/1e9:.1f} GB ({mem.percent:.0f}%)"
    )


def save_intermediate(zeros: List[float], T_MAX: float, horodatage: str, dossier: Path):
    """
    Sauvegarde intermédiaire CSV tous les 100 zéros dans le dossier du lancement.
    Nom : calculs/T{T_MAX}_{HORODATAGE}/zeros_intermediaire_T{T_MAX}_{HORODATAGE}.csv
    """
    df = pd.DataFrame({
        "n":                 range(1, len(zeros) + 1),
        "partie_imaginaire": zeros,
        "sauvegarde_le":     datetime.now().isoformat()
    })
    chemin = dossier / f"zeros_intermediaire_T{T_MAX:.0f}_{horodatage}.csv"
    df.to_csv(chemin, index=False)
    logger.info(f"💾 Sauvegarde intermédiaire : {len(zeros)} zéros → {chemin.name}")


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 4 — ALGORITHME PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def calculer_zeros(T_MAX: float, STEP: float, horodatage: str, dossier: Path) -> List[float]:
    """
    Balayage de la droite critique pour trouver les zéros de ζ(½+it).

    Algorithme en 2 passes :
    ┌─────────────────────────────────────────────────────────────────┐
    │  PASSE 1 – DÉTECTION                                           │
    │  On évalue Z(t) à intervalles réguliers (pas = STEP).         │
    │  Si Z(t−STEP) · Z(t) < 0 → changement de signe → zéro !      │
    │                                                                 │
    │  PASSE 2 – AFFINAGE                                            │
    │  On localise le zéro précisément par la méthode Illinois.      │
    │  On vérifie : |ζ(½ + it₀)| < 1e-10 pour rejeter les faux pos. │
    └─────────────────────────────────────────────────────────────────┘
    """
    T_MIN  = 10.0
    zeros  = []

    t      = T_MIN
    Z_prev = Z(t)
    n_steps = int((T_MAX - T_MIN) / STEP)

    print(f"\n  Balayage de t={T_MIN} à t={T_MAX} avec pas={STEP}")
    print(f"  Soit {n_steps} évaluations de Z(t) ...\n")

    log_resources()

    for _ in tqdm(range(n_steps), desc="  Recherche", unit="pas", ncols=70):

        t += STEP
        Z_curr = Z(t)

        if Z_prev * Z_curr < 0:
            t_zero = affiner_zero(t - STEP, t)

            if t_zero is not None:
                residu = float(abs(zeta(mp.mpc("0.5", t_zero))))

                if residu < 1e-10:
                    zeros.append(t_zero)
                    tqdm.write(
                        f"  ✅  Zéro #{len(zeros):5d} : "
                        f"t = {t_zero:.15f}   |ζ| = {residu:.2e}"
                    )
                    logger.info(
                        f"✅ Zéro #{len(zeros)} : t = {t_zero:.10f} | |ζ| = {residu:.2e}"
                    )

                    if len(zeros) % 100 == 0:
                        save_intermediate(zeros, T_MAX, horodatage, dossier)
                        log_resources()

                else:
                    tqdm.write(
                        f"  ⚠️   Faux positif : t = {t_zero:.6f}   |ζ| = {residu:.2e}"
                    )
                    logger.warning(
                        f"⚠️ Faux positif : t={t_zero:.6f} | |ζ|={residu:.2e}"
                    )

        Z_prev = Z_curr

        if int(t) % 100 == 0 and abs(t - round(t)) < STEP:
            log_resources()

    return zeros


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 5 — VÉRIFICATION LMFDB
# ═══════════════════════════════════════════════════════════════════════════

def verifier_premiers_zeros(zeros: List[float]):
    """Compare les premiers zéros calculés avec les valeurs de référence LMFDB."""
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

    print(f"\n  Vérification des {n_check} premiers zéros vs LMFDB :")
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
#  SECTION 6 — SAUVEGARDE CSV
# ═══════════════════════════════════════════════════════════════════════════

def sauvegarder(zeros: List[float], T_MAX: float, horodatage: str, dossier: Path) -> pd.DataFrame:
    """
    Sauvegarde finale des zéros en CSV dans le dossier du lancement.
    Nom : zeros_zeta_T{T_MAX}_{HORODATAGE}.csv
    """
    nom_fichier = f"zeros_zeta_T{T_MAX:.0f}_{horodatage}.csv"
    chemin = dossier / nom_fichier

    df = pd.DataFrame({
        "n":                 range(1, len(zeros) + 1),
        "partie_imaginaire": zeros,
        "T_MAX":             T_MAX,
        "methode":           "Hardy-Z + Illinois",
        "precision_dps":     mp.dps,
        "calcule_le":        horodatage,
    })

    df.to_csv(chemin, index=False)
    print(f"\n  💾  {len(zeros)} zéros sauvegardés → {chemin.resolve()}")
    logger.info(f"💾 Sauvegarde finale : {len(zeros)} zéros → {chemin.name}")
    return df


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 7 — VISUALISATION
# ═══════════════════════════════════════════════════════════════════════════

def visualiser(zeros: List[float], T_MAX: float, horodatage: str, dossier: Path):
    """
    Génère deux graphiques et les sauvegarde dans le dossier du lancement.
    Nom : zeros_zeta_T{T_MAX}_{HORODATAGE}.png
    """
    if len(zeros) < 2:
        print("  ⚠️  Moins de 2 zéros — pas de graphique.")
        return

    ecarts  = np.diff(zeros)
    nom_png = f"zeros_zeta_T{T_MAX:.0f}_{horodatage}.png"
    chemin  = dossier / nom_png

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        f"Zéros de ζ(½+it) — {len(zeros)} zéros  [T_MAX={T_MAX:.0f}]",
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
    axes[1].scatter([0.5] * len(zeros), zeros, s=8, color="darkblue", alpha=0.5)
    axes[1].axvline(
        0.5, color="red", linestyle="--", linewidth=1.5,
        label="Re(s) = ½  (droite critique)"
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
    plt.savefig(str(chemin), dpi=150)
    print(f"  📈  Graphique sauvegardé → {chemin.resolve()}")
    logger.info(f"📈 Graphique : {chemin.name}")
    plt.show()


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 8 — POINT D'ENTRÉE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """
    Orchestration complète :
        1. Configuration mpmath (50 décimales)
        2. Saisie interactive + création du dossier calculs/T{xxx}_{date}/
        3. Configuration du logger dans ce dossier
        4. Calcul des zéros (Z de Hardy + Illinois)
        5. Vérification vs LMFDB
        6. Sauvegarde CSV dans le dossier
        7. Visualisation PNG dans le dossier
        8. Rapport final
    """
    # ── Configuration précision mpmath ────────────────────────────────────
    mp.dps    = 50
    mp.pretty = True

    debut = time.time()

    # ── 1. Saisie interactive + création dossier ──────────────────────────
    T_MAX, STEP, HORODATAGE, DOSSIER = saisir_parametres()

    # ── 2. Logger dans le dossier du lancement ────────────────────────────
    configurer_logger(T_MAX, HORODATAGE, DOSSIER)

    logger.info("=" * 60)
    logger.info("🚀 DÉBUT DU CALCUL DES ZÉROS NON TRIVIAUX DE ζ(s)")
    logger.info("=" * 60)
    logger.info(f"Paramètres : T_MAX={T_MAX}, STEP={STEP}")

    # ── 3. Calcul des zéros ────────────────────────────────────────────────
    zeros = calculer_zeros(T_MAX, STEP, HORODATAGE, DOSSIER)

    duree = time.time() - debut

    # ── 4. Rapport de synthèse ────────────────────────────────────────────
    print()
    print("=" * 60)
    print(f"  RÉSULTATS  —  {len(zeros)} zéros trouvés")
    print("=" * 60)
    print(f"  T_MAX     = {T_MAX:.1f}")
    print(f"  Durée     = {duree/60:.1f} min  ({duree:.0f} secondes)")
    print(f"  Dossier   = {DOSSIER.resolve()}")
    if zeros:
        print(f"  1er zéro  : t = {zeros[0]:.10f}")
        print(f"  Dernier   : t = {zeros[-1]:.10f}")
        n_attendus = int(T_MAX / (2*math.pi) * math.log(T_MAX / (2*math.pi*math.e)))
        print(f"  Attendus  ≈ {n_attendus}  (formule Riemann–von Mangoldt)")
        print(f"  Taux      = {len(zeros)/T_MAX:.3f} zéros par unité t")

    logger.info(f"✅ CALCUL TERMINÉ — {len(zeros)} zéros en {duree/60:.1f} min")

    # ── 5. Vérification LMFDB ─────────────────────────────────────────────
    verifier_premiers_zeros(zeros)

    # ── 6. Sauvegarde CSV ──────────────────────────────────────────────────
    if zeros:
        sauvegarder(zeros, T_MAX, HORODATAGE, DOSSIER)

    # ── 7. Graphiques ──────────────────────────────────────────────────────
    if zeros:
        visualiser(zeros, T_MAX, HORODATAGE, DOSSIER)

    print()
    print("=" * 60)
    print(f"  Tous les fichiers sont dans : {DOSSIER.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
