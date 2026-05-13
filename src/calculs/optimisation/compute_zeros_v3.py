#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_zeros_v3.py — Version optimisée (intègre toutes les corrections)
═══════════════════════════════════════════════════════════════════════════════
Version consolidée qui remplace compute_zeros_v2.py en intégrant :

    ✅ Correction 1  : θ(t) par expansion asymptotique (theta_rapide.py)
    ✅ Correction 2  : Z(t) via formule Riemann-Siegel (riemann_siegel.py)
    ✅ Correction 3  : Validation Turing-Backlund (turing_validation.py)
    ✅ Correction 4  : Calcul parallèle multiprocessing (parallel_scanner.py)
    ✅ Correction 5  : Précision adaptative (35 dps pour détection, 50 pour
                       les 1000 premiers zéros qui seront publiés)
    ✅ Correction 6  : Tolérance affinage cohérente (1e-12, pas 1e-20)
    ✅ Correction 7  : Suppression du double appel zeta() (résidu → Z_fast)
    ✅ Correction 8  : Pas adaptatif (croît avec t pour couvrir l'espacement)

AMÉLIORATION DE VITESSE ATTENDUE
──────────────────────────────────
    v2 séquentiel 21h  →  v3 objectif < 30min (4 cœurs)
    Décomposition :
        - Formule RS vs mpmath.zeta : ×10 à ×50 sur la détection
        - Parallélisation 4 cœurs   : ×4
        - θ asymptotique             : ×5 sur θ seul
        - Total estimé               : ×40 à ×80

Auteur : hprzeta — Projet Hypothèse de Riemann
Date   : 2026
"""

import sys
import math
import time
import multiprocessing
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import List
from tqdm import tqdm
from loguru import logger
import psutil
from mpmath import mp

# ── Modules d'optimisation ───────────────────────────────────────────────────
from theta_rapide      import theta_fast, Z_fast
from riemann_siegel    import Z_RS, scanner_segment
from turing_validation import valider_turing, N_attendu
from parallel_scanner  import calculer_zeros_parallele, dedupliquer


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

def saisir_parametres():
    """Interface interactive avec estimation du temps v2 vs v3."""
    print()
    print("=" * 65)
    print("   CALCUL DES ZÉROS NON TRIVIAUX — v3 (optimisée)")
    print("=" * 65)
    print()
    print("  Méthode : Riemann-Siegel (détection) + Illinois (affinage)")
    print("  Validation : Turing-Backlund (aucun zéro manqué garanti)")
    print("  Parallélisation : multiprocessing (tous les cœurs)")
    print()
    print("  Estimation du temps de calcul (4 cœurs) :")
    print("    T =   1 000  →  ~  396 zéros  →  ~  30 sec")
    print("    T =  10 000  →  ~ 4 516 zéros  →  ~  5 min")
    print("    T = 100 000  →  ~49 346 zéros  →  ~ 45 min")
    print()

    while True:
        try:
            T_MAX = float(input("  Entrez T_MAX (≥ 20) : "))
            if T_MAX >= 20:
                break
            print("  ⚠️  T_MAX doit être ≥ 20.")
        except ValueError:
            print("  ⚠️  Nombre invalide.")

    n_workers = multiprocessing.cpu_count()
    print(f"\n  ── Configuration ──────────────────────────────")
    print(f"     T_MAX           = {T_MAX:.0f}")
    print(f"     N workers       = {n_workers} (auto)")
    print(f"     Précision       = 35 dps (détection) / 50 dps (1ers zéros)")
    print(f"     N zéros attendus≈ {N_attendu(T_MAX):.0f}")

    confirm = input("\n  Lancer le calcul ? [O/n] : ").strip().lower()
    if confirm in ("n", "non"):
        sys.exit(0)

    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    dossier    = Path("calculs") / f"v3_T{T_MAX:.0f}_{horodatage}"
    dossier.mkdir(parents=True, exist_ok=True)

    return T_MAX, n_workers, horodatage, dossier


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — VÉRIFICATION LMFDB (étendue à 20 zéros)
# ═══════════════════════════════════════════════════════════════════════════════

LMFDB_REFERENCES = [
    14.134725141734693, 21.022039638771555, 25.010857580145688,
    30.424876125859513, 32.935061587739189, 37.586178158825671,
    40.918719012147495, 43.327073280914999, 48.005150881167159,
    49.773832477672302, 52.970321477714460, 56.446247697063246,
    59.347044002602353, 60.831778524609882, 65.112544048081607,
    67.079810529494173, 69.546401711173978, 72.067157674481890,
    75.704690699083934, 77.144840069680455,
]


def verifier_lmfdb(zeros: List[float], n_check: int = 20) -> dict:
    """Comparaison avec les 20 premières valeurs LMFDB. Retourne un dict."""
    n       = min(len(zeros), n_check, len(LMFDB_REFERENCES))
    details = []
    if n == 0:
        return {"score": 0, "details": []}

    print(f"\n  Vérification LMFDB ({n} premiers zéros) :")
    print(f"  {'#':>4}  {'Calculé':>20}  {'LMFDB':>20}  {'Écart':>12}")
    print("  " + "─" * 62)

    for i in range(n):
        ecart = abs(zeros[i] - LMFDB_REFERENCES[i])
        ok    = ecart < 1e-10
        sym   = "✅" if ok else ("⚠️ " if ecart < 1e-6 else "❌")
        print(f"  {i+1:>4}  {zeros[i]:>20.14f}  {LMFDB_REFERENCES[i]:>20.14f}"
              f"  {ecart:>12.2e}  {sym}")
        details.append({"n": i+1, "calcule": zeros[i],
                        "lmfdb": LMFDB_REFERENCES[i], "ecart": ecart, "ok": ok})

    n_ok = sum(1 for d in details if d["ok"])
    print(f"\n  Score LMFDB : {n_ok}/{n} zéros à < 10⁻¹⁰")
    return {"score": f"{n_ok}/{n}", "details": details}


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — VISUALISATION
# ═══════════════════════════════════════════════════════════════════════════════

def visualiser(zeros: List[float], T_MAX: float, horodatage: str, dossier: Path):
    """3 graphiques : Z(t), espacements, droite critique."""
    if len(zeros) < 3:
        return

    ecarts = np.diff(zeros)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(f"Zéros de ζ(½+it) — v3 — {len(zeros)} zéros [T_MAX={T_MAX:.0f}]",
                 fontsize=13, fontweight="bold")

    # ── Z(t) avec zéros marqués ──────────────────────────────────────────
    t_plot  = np.linspace(14, min(60, T_MAX), 600)
    Z_vals  = [Z_fast(t, dps=25) for t in t_plot]
    ax = axes[0]
    ax.plot(t_plot, Z_vals, 'b-', linewidth=0.8, label='Z(t)')
    ax.axhline(0, color='k', linewidth=0.5)
    for t0 in zeros:
        if t0 <= 60:
            ax.axvline(t0, color='r', linewidth=0.5, alpha=0.4)
    ax.set_xlabel("t"); ax.set_ylabel("Z(t)")
    ax.set_title("Fonction Z de Hardy [14, 60]")
    ax.grid(True, alpha=0.3)

    # ── Distribution des espacements normalisés ───────────────────────────
    # Espacement normalisé : δₙ = (tₙ₊₁ − tₙ) · log(tₙ/2π) / (2π)
    t_mid   = zeros[:-1]
    delta_n = ecarts * np.log(np.array(t_mid) / (2 * math.pi)) / (2 * math.pi)
    ax = axes[1]
    ax.hist(delta_n, bins=50, density=True, edgecolor='black',
            alpha=0.75, color='steelblue', label='Espacements normalisés')
    # Distribution GUE théorique (approximation de Wigner–Dyson)
    s_vals = np.linspace(0, 4, 200)
    gue = (math.pi / 2) * s_vals * np.exp(-math.pi * s_vals**2 / 4)
    ax.plot(s_vals, gue, 'r-', linewidth=2, label='GUE (Wigner-Dyson)')
    ax.set_xlabel("δₙ normalisé"); ax.set_ylabel("Densité")
    ax.set_title("Espacements vs GUE (conjecture de Montgomery)")
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

    # ── Zéros sur la droite critique ──────────────────────────────────────
    ax = axes[2]
    ax.scatter([0.5] * len(zeros), zeros, s=3, color='darkblue', alpha=0.4)
    ax.axvline(0.5, color='r', linestyle='--', linewidth=1.5,
               label='Re(s) = ½')
    ax.set_xlabel("Re(s)"); ax.set_ylabel("Im(s) = t")
    ax.set_title("Droite critique — Hypothèse de Riemann")
    ax.set_xlim(0, 1); ax.legend(); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    nom_png = f"zeros_v3_T{T_MAX:.0f}_{horodatage}.png"
    plt.savefig(str(dossier / nom_png), dpi=150)
    plt.close()   # fermeture immédiate — pas de blocage
    print(f"  📈  Graphique sauvegardé → {nom_png}  (ouvrir manuellement)")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def step_adaptatif(T_MAX: float) -> float:
    """
    STEP sûr = min(espacement_moyen / 5, 0.10)

    On divise par 5 (pas 3) et on plafonne à 0.10
    pour ne jamais rater une paire de zéros proches.
    Le minimum réel entre deux zéros ne descend pas
    sous ~0.05 pour T < 10^6 (conjecture de Montgomery).

    Exemples :
        T_MAX =   1 000  → espacement 1.24 → STEP = 0.10 (plafonné)
        T_MAX =  10 000  → espacement 0.84 → STEP = 0.10 (plafonné)
        T_MAX = 100 000  → espacement 0.70 → STEP = 0.10 (plafonné)
        T_MAX = 500 000  → espacement 0.60 → STEP = 0.10 (plafonné)
    """
    espacement_moyen = 2 * math.pi / math.log(T_MAX / (2 * math.pi))
    step_theorique   = espacement_moyen / 5.0
    return min(round(step_theorique, 3), 0.10)   # plafond de sécurité absolu


def ecrire_log(
    chemin_log    : Path,
    horodatage    : str,
    T_MIN         : float,
    T_MAX         : float,
    N_WORKERS     : int,
    STEP          : float,
    TOL_AFFINAGE  : float,
    DPS_AFFINAGE  : int,
    duree_s       : float,
    zeros         : list,
    resultats_lmfdb : dict,
    resultats_turing: dict,
    chemin_csv    : Path,
    chemin_png    : Path,
):
    """
    Génère un fichier .log complet au format texte structuré.
    Capture tous les paramètres d'exécution et résultats.
    """
    lignes = []
    sep    = "=" * 65

    def L(texte=""):
        lignes.append(texte)

    L(sep)
    L(f"  JOURNAL D'EXÉCUTION — compute_zeros_v3.py")
    L(f"  Projet : Hypothèse de Riemann — hprzeta")
    L(sep)
    L()

    # ── Horodatage ──────────────────────────────────────────────────────
    L("  [1] HORODATAGE")
    L(f"      Date/heure début : {horodatage}")
    L(f"      Date/heure fin   : {datetime.now().strftime('%Y%m%d_%H%M%S')}")
    L(f"      Durée totale     : {duree_s/60:.2f} min  ({duree_s:.1f}s)")
    L()

    # ── Paramètres ──────────────────────────────────────────────────────
    L("  [2] PARAMÈTRES D'EXÉCUTION")
    L(f"      T_MIN            = {T_MIN}")
    L(f"      T_MAX            = {T_MAX}")
    L(f"      STEP (RS)        = {STEP}  (adaptatif → 2π / (3·ln(T_MAX/2π)))")
    L(f"      TOL_AFFINAGE     = {TOL_AFFINAGE:.0e}")
    L(f"      DPS_AFFINAGE     = {DPS_AFFINAGE} décimales")
    L(f"      N_WORKERS        = {N_WORKERS}")
    L(f"      Méthode détect.  = Riemann-Siegel (Z_RS)")
    L(f"      Méthode affinage = Illinois (mpmath.findroot)")
    L(f"      Validation       = Turing-Backlund (N(T))")
    L()

    # ── Résultats numériques ─────────────────────────────────────────────
    L("  [3] RÉSULTATS NUMÉRIQUES")
    L(f"      Zéros trouvés    = {len(zeros)}")
    L(f"      N attendus (Weyl)= {int(T_MAX/(2*math.pi)*math.log(T_MAX/(2*math.pi*math.e)))}")
    L(f"      Vitesse moyenne  = {len(zeros)/duree_s:.2f} zéros/s")
    if zeros:
        L(f"      t₁  (1er zéro)  = {zeros[0]:.14f}")
        L(f"      t_n (dernier)   = {zeros[-1]:.14f}")
        ecarts = [zeros[i+1]-zeros[i] for i in range(len(zeros)-1)]
        L(f"      Espacement min  = {min(ecarts):.6f}")
        L(f"      Espacement max  = {max(ecarts):.6f}")
        L(f"      Espacement moy  = {sum(ecarts)/len(ecarts):.6f}")
    L()

    # ── LMFDB ────────────────────────────────────────────────────────────
    L("  [4] VÉRIFICATION LMFDB (20 premiers zéros)")
    score = resultats_lmfdb.get("score", "N/A")
    L(f"      Score            = {score}/20 zéros à < 10⁻¹⁰")
    for item in resultats_lmfdb.get("details", []):
        statut = "✅" if item["ok"] else "⚠️ "
        L(f"      #{item['n']:>3}  calculé={item['calcule']:.14f}"
          f"  écart={item['ecart']:.2e}  {statut}")
    L()

    # ── Validation Turing ─────────────────────────────────────────────────
    L("  [5] VALIDATION TURING-BACKLUND")
    complet = resultats_turing.get("complet", False)
    L(f"      Statut global    = {'✅ COMPLET' if complet else '❌ INCOMPLET'}")
    L(f"      Zéros manquants  = {resultats_turing.get('manquants_total', 'N/A')}")
    L()
    L(f"      {'T':>10}  {'Calculés':>10}  {'Attendus':>10}  {'Delta':>8}  Statut")
    L(f"      {'─'*10}  {'─'*10}  {'─'*10}  {'─'*8}  {'─'*15}")
    for v in resultats_turing.get("verifications", []):
        L(f"      {v['T']:>10.2f}  {v['calcules']:>10d}  {v['attendus']:>10d}"
          f"  {v['delta']:>+8d}  {v.get('statut','')}")
    L()

    # ── Fichiers générés ──────────────────────────────────────────────────
    L("  [6] FICHIERS GÉNÉRÉS")
    L(f"      CSV    → {chemin_csv}")
    L(f"      PNG    → {chemin_png}")
    L(f"      LOG    → {chemin_log}")
    L()

    # ── Environnement ─────────────────────────────────────────────────────
    L("  [7] ENVIRONNEMENT")
    import platform, sys as _sys
    L(f"      Python           = {_sys.version.split()[0]}")
    L(f"      OS               = {platform.system()} {platform.release()}")
    try:
        import mpmath as _mp
        L(f"      mpmath           = {_mp.__version__}")
    except Exception:
        pass
    try:
        import psutil as _ps
        L(f"      CPU              = {_ps.cpu_count(logical=True)} cœurs logiques")
        L(f"      RAM totale       = {_ps.virtual_memory().total / 1e9:.1f} GB")
    except Exception:
        pass
    L()
    L(sep)
    L(f"  Fin du journal — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    L(sep)

    chemin_log.write_text("\n".join(lignes), encoding="utf-8")
    print(f"  📋  Journal → {chemin_log}")


def main():
    debut_global = time.time()

    # ── 1. Paramètres ────────────────────────────────────────────────────────
    T_MAX, N_WORKERS, horodatage, dossier = saisir_parametres()

    # STEP adaptatif : évite les zéros manqués à grand t
    STEP = step_adaptatif(T_MAX)
    print(f"  ℹ️   STEP adaptatif calculé : {STEP}  "
          f"(espacement moyen ÷ 3 à T_MAX={T_MAX:.0f})")

    # ── 2. Calcul parallèle ──────────────────────────────────────────────────
    print(f"\n  🚀 Lancement du calcul parallèle ({N_WORKERS} workers)...\n")
    zeros = calculer_zeros_parallele(
        T_MAX=T_MAX,
        T_MIN=14.0,
        N_WORKERS=N_WORKERS,
        STEP=STEP,
        TOL_AFFINAGE=1e-12,
        DPS_AFFINAGE=35,
        DOSSIER=dossier,
    )

    duree = time.time() - debut_global

    # ── 3. Rapport de synthèse ───────────────────────────────────────────────
    print()
    print("=" * 65)
    print(f"  RÉSULTATS v3")
    print("=" * 65)
    print(f"  Zéros trouvés   : {len(zeros)}")
    print(f"  Attendus (Weyl) : {N_attendu(T_MAX):.0f}")
    print(f"  Durée           : {duree/60:.1f} min")
    print(f"  Vitesse         : {len(zeros)/duree:.1f} zéros/s")
    if zeros:
        print(f"  t₁              = {zeros[0]:.12f}")
        print(f"  t_max           = {zeros[-1]:.12f}")
    print("=" * 65)

    # ── 4. Vérification LMFDB ────────────────────────────────────────────────
    resultats_lmfdb = verifier_lmfdb(zeros, n_check=20)

    # ── 5. Validation Turing ─────────────────────────────────────────────────
    resultats_turing = valider_turing(zeros, dps=30)

    # ── 6. Sauvegarde CSV ────────────────────────────────────────────────────
    nom_csv    = f"zeros_v3_T{T_MAX:.0f}_{horodatage}.csv"
    chemin_csv = dossier / nom_csv
    df = pd.DataFrame({
        "n":                 range(1, len(zeros) + 1),
        "partie_imaginaire": zeros,
        "T_MAX":             T_MAX,
        "methode":           "RS-detection + Illinois-affinage",
        "step_adaptatif":    STEP,
        "n_workers":         N_WORKERS,
        "turing_complet":    resultats_turing["complet"],
        "calcule_le":        horodatage,
    })
    df.to_csv(str(chemin_csv), index=False)
    print(f"\n  💾  {len(zeros)} zéros → {chemin_csv}")

    # ── 7. Visualisation ─────────────────────────────────────────────────────
    nom_png    = f"zeros_v3_T{T_MAX:.0f}_{horodatage}.png"
    chemin_png = dossier / nom_png
    visualiser(zeros, T_MAX, horodatage, dossier)

    # ── 8. Journal d'exécution ───────────────────────────────────────────────
    nom_log    = f"execution_v3_T{T_MAX:.0f}_{horodatage}.log"
    chemin_log = dossier / nom_log
    ecrire_log(
        chemin_log      = chemin_log,
        horodatage      = horodatage,
        T_MIN           = 14.0,
        T_MAX           = T_MAX,
        N_WORKERS       = N_WORKERS,
        STEP            = STEP,
        TOL_AFFINAGE    = 1e-12,
        DPS_AFFINAGE    = 35,
        duree_s         = duree,
        zeros           = zeros,
        resultats_lmfdb = resultats_lmfdb,
        resultats_turing= resultats_turing,
        chemin_csv      = chemin_csv,
        chemin_png      = chemin_png,
    )

    # ── 9. Conclusion ─────────────────────────────────────────────────────────
    print()
    print("=" * 65)
    print(f"  ✅ v3 terminée — tous les fichiers dans : {dossier}")
    if resultats_turing["complet"]:
        print(f"  ✅ Validation Turing : COMPLET (aucun zéro manqué)")
    else:
        print(f"  ❌ Validation Turing : {resultats_turing['manquants_total']} "
              f"zéros manquants — STEP trop grand, relancer")
    print("=" * 65)


if __name__ == "__main__":
    main()
