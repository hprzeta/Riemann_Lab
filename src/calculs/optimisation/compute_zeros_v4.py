#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_zeros_v4.py — Phase C : Illinois C/libmpfr + mpmath.siegelz
══════════════════════════════════════════════════════════════════════
Différences v3 → v4 :

    v3  Détection  : Z_fast (Riemann-Siegel approx., N=⌊√(t/2π)⌋ termes)
    v4  Détection  : mpmath.siegelz  → vrais zéros de Riemann GARANTIS

    v3  Affinage   : mpmath.findroot (Illinois Python, 35 dps)
    v4  Affinage   : illinois_mpfr C (libmpfr 170 bits) si Z_double cohérent,
                     sinon mpmath.findroot (fallback — voir analyse Phase C)

    v3  Exécution  : parallèle multiprocessing
    v4  Exécution  : séquentiel (parallèle prévu v5 — ctypes + multiprocessing)

Gain mesuré Phase C :
    Affinage Illinois C vs mpmath : ×39 sur t ∈ [500, 638]
    Coût : détection mpmath.siegelz plus lente que Z_fast (RS)

Limite fondamentale connue :
    Pour t < 300 (N < 7), Z_mpfr (RS) est décalé de ~1e-3 à 1e-2 par rapport
    aux vrais zéros → illinois C seul ne converge pas → fallback mpmath.
    Illinois C pur est pertinent à partir de t ≈ 500.

Auteur : hprzeta — Projet Hypothèse de Riemann — Phase C
Date   : 2026-05-24
"""

import sys
import math
import time
import ctypes
import os
import multiprocessing
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
from tqdm import tqdm

import mpmath
mpmath.mp.dps = 35   # détection et fallback (35 dps > 12 dps cibles d'affinage)

from turing_validation import valider_turing, N_attendu


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — CHARGEMENT DE illinois_mpfr.so
# ═══════════════════════════════════════════════════════════════════════════════

_SO_PATH = Path(__file__).parent / "c_modules" / "illinois_mpfr.so"

def _charger_lib() -> ctypes.CDLL | None:
    """Charge illinois_mpfr.so. Retourne None si absent (fallback seul)."""
    if not _SO_PATH.exists():
        print(f"[AVERTISSEMENT] {_SO_PATH} introuvable — affinage en mpmath seul.")
        return None
    lib = ctypes.CDLL(str(_SO_PATH))
    lib.illinois_mpfr.restype  = ctypes.c_double
    lib.illinois_mpfr.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]
    lib.Z_double.restype       = ctypes.c_double
    lib.Z_double.argtypes      = [ctypes.c_double]
    return lib

_LIB = _charger_lib()


def Z_double(t: float) -> float:
    """Z(t) formule Riemann-Siegel en C (float64). None si .so absent."""
    if _LIB is None:
        return float(mpmath.siegelz(t))
    return _LIB.Z_double(float(t))


def illinois_c(a: float, b: float, tol: float = 1e-12) -> float:
    """Appel direct à illinois_mpfr C. Précondition : Z_double(a)*Z_double(b) < 0."""
    return _LIB.illinois_mpfr(float(a), float(b), float(tol))


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — DÉTECTION ET AFFINAGE (Option B hybride)
# ═══════════════════════════════════════════════════════════════════════════════

def trouver_intervalle_mpmath(t: float, b: float) -> bool:
    """True si mpmath.siegelz change de signe entre t et b."""
    return float(mpmath.siegelz(t)) * float(mpmath.siegelz(b)) < 0


def affiner_zero(a: float, b: float, tol: float = 1e-12) -> Tuple[float, str]:
    """Affinage hybride d'un zéro dans [a, b] (changement de signe mpmath garanti).

    Étapes :
      1. Vérifie si Z_double change de signe dans [a, b] (cohérence Illinois C)
      2. Si oui : illinois_mpfr C pré-affine → vérification mpmath.siegelz
         Si le résultat C n'est pas un vrai zéro → affinage mpmath depuis γ_C
      3. Si non : mpmath.findroot direct depuis le milieu

    Retourne (gamma, méthode_utilisée).
    """
    t_mid = (a + b) / 2.0

    if _LIB is not None and Z_double(a) * Z_double(b) < 0:
        # Illinois C disponible et cohérent dans cet intervalle
        gamma_c = illinois_c(a, b, tol)
        if abs(float(mpmath.siegelz(gamma_c))) < 1e-8:
            return gamma_c, "illinois_C"
        # RS imprécis : affinage complémentaire depuis le résultat C
        gamma = float(mpmath.findroot(mpmath.siegelz, gamma_c))
        return gamma, "illinois_C→mpmath"

    # Fallback : Z_double incohérent ou .so absent
    gamma = float(mpmath.findroot(mpmath.siegelz, t_mid))
    return gamma, "mpmath"


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — SCANNER PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def pas_adaptatif(T_MAX: float) -> float:
    """Pas de balayage = espacement_moyen / 5, plafonné à 0.05.

    Espacement moyen des zéros ≈ 2π / ln(T/2π) (formule de Weyl).
    Divisé par 5 pour ne jamais rater une paire de zéros proches.
    Plafonné à 0.05 (< espacement min observé pour T < 10^6).
    """
    espacement = 2 * math.pi / math.log(T_MAX / (2 * math.pi))
    return min(round(espacement / 5, 3), 0.05)


def scanner_zeros(
    T_MIN      : float,
    T_MAX      : float,
    pas        : float,
    tol        : float = 1e-12,
    barre      : bool  = True,
    dps_detect : int   = 15,   # précision détection : assez pour le signe, ×2 plus rapide
) -> Tuple[List[float], dict]:
    """Balayage séquentiel [T_MIN, T_MAX] avec mpmath.siegelz + affinage hybride.

    Précision adaptative :
      - Détection (changement de signe) : dps_detect (défaut 15) — rapide
      - Affinage (illinois_C ou findroot) : mpmath.mp.dps global (35) — précis

    Retourne (zeros, statistiques).
    """
    zeros    = []
    stats    = {"illinois_C": 0, "illinois_C→mpmath": 0, "mpmath": 0, "echecs": 0}
    t        = T_MIN
    n_pas    = int((T_MAX - T_MIN) / pas) + 1

    # évaluation initiale à précision réduite (détection de signe seulement)
    with mpmath.workdps(dps_detect):
        za = float(mpmath.siegelz(t))

    iterateur = tqdm(range(n_pas), desc="Balayage", unit="pas", disable=not barre)
    for _ in iterateur:
        b = t + pas

        with mpmath.workdps(dps_detect):
            zb = float(mpmath.siegelz(b))

        if za * zb < 0:
            # changement de signe détecté → affinage à pleine précision
            try:
                gamma, methode = affiner_zero(t, b, tol)
                zeros.append(gamma)
                stats[methode] = stats.get(methode, 0) + 1
                if barre:
                    iterateur.set_postfix(
                        zeros=len(zeros),
                        methode=methode,
                        t=f"{gamma:.2f}"
                    )
            except Exception:
                stats["echecs"] += 1

        t, za = b, zb
        if t >= T_MAX:
            break

    return zeros, stats


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — VÉRIFICATION LMFDB
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
    """Comparaison avec les valeurs LMFDB de référence."""
    n       = min(len(zeros), n_check, len(LMFDB_REFERENCES))
    details = []
    if n == 0:
        return {"score": "0/0", "details": []}

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
#  SECTION 5 — VISUALISATION
# ═══════════════════════════════════════════════════════════════════════════════

def visualiser(zeros: List[float], T_MAX: float, horodatage: str, dossier: Path):
    """3 graphiques identiques à v3 : Z(t), espacements GUE, droite critique."""
    if len(zeros) < 3:
        return

    ecarts = np.diff(zeros)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(
        f"Zéros de ζ(½+it) — v4 — {len(zeros)} zéros [T_MAX={T_MAX:.0f}]",
        fontsize=13, fontweight="bold"
    )

    # ── Z(t) avec zéros marqués ──────────────────────────────────────────────
    t_plot  = np.linspace(14, min(60, T_MAX), 600)
    Z_vals  = [float(mpmath.siegelz(t)) for t in t_plot]
    ax = axes[0]
    ax.plot(t_plot, Z_vals, 'b-', linewidth=0.8, label='Z(t)')
    ax.axhline(0, color='k', linewidth=0.5)
    for t0 in zeros:
        if t0 <= 60:
            ax.axvline(t0, color='r', linewidth=0.5, alpha=0.4)
    ax.set_xlabel("t"); ax.set_ylabel("Z(t)")
    ax.set_title("Fonction Z de Hardy [14, 60]")
    ax.grid(True, alpha=0.3)

    # ── Espacements normalisés vs GUE ────────────────────────────────────────
    t_mid   = zeros[:-1]
    delta_n = ecarts * np.log(np.array(t_mid) / (2 * math.pi)) / (2 * math.pi)
    ax = axes[1]
    ax.hist(delta_n, bins=50, density=True, edgecolor='black',
            alpha=0.75, color='steelblue', label='Espacements normalisés')
    s_vals = np.linspace(0, 4, 200)
    gue    = (math.pi / 2) * s_vals * np.exp(-math.pi * s_vals**2 / 4)
    ax.plot(s_vals, gue, 'r-', linewidth=2, label='GUE (Wigner-Dyson)')
    ax.set_xlabel("δₙ normalisé"); ax.set_ylabel("Densité")
    ax.set_title("Espacements vs GUE (conjecture de Montgomery)")
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

    # ── Droite critique ──────────────────────────────────────────────────────
    ax = axes[2]
    ax.scatter([0.5] * len(zeros), zeros, s=3, color='darkblue', alpha=0.4)
    ax.axvline(0.5, color='r', linestyle='--', linewidth=1.5, label='Re(s) = ½')
    ax.set_xlabel("Re(s)"); ax.set_ylabel("Im(s) = t")
    ax.set_title("Droite critique — Hypothèse de Riemann")
    ax.set_xlim(0, 1); ax.legend(); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    nom_png = f"zeros_v4_T{T_MAX:.0f}_{horodatage}.png"
    plt.savefig(str(dossier / nom_png), dpi=150)
    plt.close()
    print(f"  Graphique sauvegardé → {nom_png}")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — SAUVEGARDE CSV + LOG
# ═══════════════════════════════════════════════════════════════════════════════

def sauvegarder_csv(zeros: List[float], stats: dict, T_MAX: float,
                    pas: float, horodatage: str, dossier: Path) -> Path:
    """Sauvegarde CSV avec métadonnées de méthode par zéro."""
    nom_csv    = f"zeros_v4_T{T_MAX:.0f}_{horodatage}.csv"
    chemin_csv = dossier / nom_csv
    df = pd.DataFrame({
        "n":                 range(1, len(zeros) + 1),
        "partie_imaginaire": zeros,
        "T_MAX":             T_MAX,
        "version":           "v4",
        "methode_affinage":  "illinois_mpfr_C_hybride",
        "pas_balayage":      pas,
        "calcule_le":        horodatage,
    })
    df.to_csv(str(chemin_csv), index=False)
    print(f"  {len(zeros)} zéros → {chemin_csv}")
    return chemin_csv


def ecrire_log(
    chemin_log      : Path,
    horodatage      : str,
    T_MIN           : float,
    T_MAX           : float,
    pas             : float,
    tol             : float,
    dps_detect      : int,
    duree_s         : float,
    zeros           : List[float],
    stats           : dict,
    resultats_lmfdb : dict,
    resultats_turing: dict,
    chemin_csv      : Path,
):
    """Journal d'exécution v4 — même format que v3."""
    lignes = []
    sep    = "=" * 65

    def L(texte=""):
        lignes.append(texte)

    L(sep)
    L("  JOURNAL D'EXÉCUTION — compute_zeros_v4.py  (Phase C)")
    L("  Projet : Hypothèse de Riemann — hprzeta")
    L(sep); L()

    L("  [1] HORODATAGE")
    L(f"      Début            : {horodatage}")
    L(f"      Fin              : {datetime.now().strftime('%Y%m%d_%H%M%S')}")
    L(f"      Durée            : {duree_s/60:.2f} min  ({duree_s:.1f} s)")
    L()

    L("  [2] PARAMÈTRES v4")
    L(f"      T_MIN            = {T_MIN}")
    L(f"      T_MAX            = {T_MAX}")
    L(f"      Pas balayage     = {pas}")
    L(f"      TOL_AFFINAGE     = {tol:.0e}")
    L(f"      mpmath.mp.dps    = {mpmath.mp.dps}")
    L(f"      illinois_mpfr.so = {'chargé' if _LIB else 'ABSENT — fallback seul'}")
    L(f"      dps_detect       = {dps_detect}  (détection signe — réduit pour vitesse)")
    L(f"      Détection        = mpmath.siegelz (vrais zéros garantis)")
    L(f"      Affinage         = Illinois C hybride (C si cohérent, sinon mpmath)")
    L(f"      Parallélisme     = séquentiel (v5 prévu)")
    L()

    L("  [3] RÉSULTATS NUMÉRIQUES")
    L(f"      Zéros trouvés    = {len(zeros)}")
    L(f"      N attendus (Weyl)= {int(T_MAX/(2*math.pi)*math.log(T_MAX/(2*math.pi*math.e)))}")
    vitesse = len(zeros) / duree_s if duree_s > 0 else 0
    L(f"      Vitesse moyenne  = {vitesse:.2f} zéros/s")
    if zeros:
        ecarts = [zeros[i+1]-zeros[i] for i in range(len(zeros)-1)]
        L(f"      t₁  (1er zéro)  = {zeros[0]:.14f}")
        L(f"      t_n (dernier)   = {zeros[-1]:.14f}")
        if ecarts:
            L(f"      Espacement min  = {min(ecarts):.6f}")
            L(f"      Espacement max  = {max(ecarts):.6f}")
            L(f"      Espacement moy  = {sum(ecarts)/len(ecarts):.6f}")
    L()

    L("  [4] RÉPARTITION DES MÉTHODES D'AFFINAGE")
    total = sum(v for k, v in stats.items() if k != "echecs")
    for methode, nb in sorted(stats.items()):
        pct = nb / total * 100 if total > 0 else 0
        L(f"      {methode:<22} : {nb:>5}  ({pct:.1f}%)")
    L()

    L("  [5] VÉRIFICATION LMFDB")
    L(f"      Score            = {resultats_lmfdb.get('score','N/A')} à < 10⁻¹⁰")
    for item in resultats_lmfdb.get("details", []):
        sym = "✅" if item["ok"] else "⚠️ "
        L(f"      #{item['n']:>3}  écart={item['ecart']:.2e}  {sym}")
    L()

    L("  [6] VALIDATION TURING-BACKLUND")
    complet = resultats_turing.get("complet", False)
    L(f"      Statut           = {'✅ COMPLET' if complet else '❌ INCOMPLET'}")
    L(f"      Zéros manquants  = {resultats_turing.get('manquants_total','N/A')}")
    for v in resultats_turing.get("verifications", []):
        L(f"      T={v['T']:>8.2f}  calc={v['calcules']:>6d}  attendus={v['attendus']:>6d}"
          f"  delta={v['delta']:>+5d}  {v.get('statut','')}")
    L()

    L("  [7] FICHIERS GÉNÉRÉS")
    L(f"      CSV → {chemin_csv}")
    L(f"      LOG → {chemin_log}")
    L()

    L("  [8] ENVIRONNEMENT")
    import platform
    L(f"      Python           = {sys.version.split()[0]}")
    L(f"      OS               = {platform.system()} {platform.release()}")
    L(f"      mpmath           = {mpmath.__version__}")
    L(f"      CPU cores        = {multiprocessing.cpu_count()}")
    L()
    L(sep)
    L(f"  Fin du journal — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    L(sep)

    chemin_log.write_text("\n".join(lignes), encoding="utf-8")
    print(f"  Journal → {chemin_log}")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 7 — INTERFACE UTILISATEUR
# ═══════════════════════════════════════════════════════════════════════════════

def saisir_parametres():
    """Interface interactive avec estimation du temps v4."""
    print()
    print("=" * 65)
    print("   CALCUL DES ZÉROS NON TRIVIAUX — v4 (Phase C : Illinois C)")
    print("=" * 65)
    print()
    print("  Méthode : mpmath.siegelz (détection) + Illinois C hybride (affinage)")
    print("  Validation : Turing-Backlund (aucun zéro manqué garanti)")
    print("  Exécution : séquentielle (Illinois C ×39 vs mpmath)")
    print()
    print("  Estimation du temps de calcul :")
    print("    T =   100  →  ~  29 zéros  →  rapide")
    print("    T = 1 000  →  ~ 396 zéros  →  quelques minutes")
    print("    T = 5 000  →  ~2400 zéros  →  ~30 min (détection mpmath lente)")
    print()

    while True:
        try:
            T_MAX = float(input("  Entrez T_MAX (≥ 20) : "))
            if T_MAX >= 20:
                break
            print("  T_MAX doit être ≥ 20.")
        except ValueError:
            print("  Nombre invalide.")

    pas = pas_adaptatif(T_MAX)
    print(f"\n  ── Configuration ──────────────────────────────")
    print(f"     T_MAX             = {T_MAX:.0f}")
    print(f"     Pas balayage      = {pas}")
    print(f"     N zéros attendus  ≈ {N_attendu(T_MAX):.0f}")
    print(f"     illinois_mpfr.so  = {'✓ chargé' if _LIB else '✗ absent (mpmath seul)'}")

    confirm = input("\n  Lancer le calcul ? [O/n] : ").strip().lower()
    if confirm in ("n", "non"):
        sys.exit(0)

    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    dossier    = Path("calculs") / f"v4_T{T_MAX:.0f}_{horodatage}"
    dossier.mkdir(parents=True, exist_ok=True)

    return T_MAX, pas, horodatage, dossier


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 8 — POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    debut_global = time.time()

    # ── 1. Paramètres ────────────────────────────────────────────────────────
    T_MIN = 14.0
    T_MAX, pas, horodatage, dossier = saisir_parametres()
    TOL   = 1e-12

    # ── 2. Calcul séquentiel ─────────────────────────────────────────────────
    DPS_DETECT = 15   # détection du signe (réduit pour vitesse, suffisant)
    print(f"\n  Lancement du balayage séquentiel (dps_detect={DPS_DETECT})...")
    zeros, stats = scanner_zeros(T_MIN, T_MAX, pas, TOL, barre=True,
                                 dps_detect=DPS_DETECT)
    duree = time.time() - debut_global

    # ── 3. Rapport de synthèse ───────────────────────────────────────────────
    print()
    print("=" * 65)
    print("  RÉSULTATS v4")
    print("=" * 65)
    print(f"  Zéros trouvés    : {len(zeros)}")
    print(f"  Attendus (Weyl)  : {N_attendu(T_MAX):.0f}")
    print(f"  Durée            : {duree/60:.1f} min  ({duree:.1f} s)")
    vitesse = len(zeros) / duree if duree > 0 else 0
    print(f"  Vitesse          : {vitesse:.2f} zéros/s")
    print()
    print("  Répartition des méthodes :")
    total = sum(v for k, v in stats.items() if k != "echecs")
    for methode, nb in sorted(stats.items()):
        pct = nb / total * 100 if total > 0 else 0
        print(f"    {methode:<24} : {nb:>5}  ({pct:.1f}%)")
    if zeros:
        print(f"\n  t₁  = {zeros[0]:.12f}")
        print(f"  t_n = {zeros[-1]:.12f}")
    print("=" * 65)

    # ── 4. Vérification LMFDB ────────────────────────────────────────────────
    resultats_lmfdb = verifier_lmfdb(zeros, n_check=20)

    # ── 5. Validation Turing ─────────────────────────────────────────────────
    resultats_turing = valider_turing(zeros, dps=30)

    # ── 6. Sauvegarde CSV ────────────────────────────────────────────────────
    chemin_csv = sauvegarder_csv(zeros, stats, T_MAX, pas, horodatage, dossier)

    # ── 7. Visualisation ─────────────────────────────────────────────────────
    visualiser(zeros, T_MAX, horodatage, dossier)

    # ── 8. Journal d'exécution ───────────────────────────────────────────────
    nom_log    = f"execution_v4_T{T_MAX:.0f}_{horodatage}.log"
    chemin_log = dossier / nom_log
    ecrire_log(
        chemin_log      = chemin_log,
        horodatage      = horodatage,
        T_MIN           = T_MIN,
        T_MAX           = T_MAX,
        pas             = pas,
        tol             = TOL,
        dps_detect      = DPS_DETECT,
        duree_s         = duree,
        zeros           = zeros,
        stats           = stats,
        resultats_lmfdb = resultats_lmfdb,
        resultats_turing= resultats_turing,
        chemin_csv      = chemin_csv,
    )

    # ── 9. Conclusion ─────────────────────────────────────────────────────────
    print()
    print("=" * 65)
    print(f"  v4 terminée — fichiers dans : {dossier}")
    if resultats_turing["complet"]:
        print("  Validation Turing : COMPLET (aucun zéro manqué)")
    else:
        manq = resultats_turing["manquants_total"]
        print(f"  Validation Turing : {manq} zéros manquants — réduire le pas")
    print("=" * 65)


if __name__ == "__main__":
    main()
