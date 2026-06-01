#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_zeros_v4_1.py — Phase C v4.1 : Z_vect_correct vectorisé + 4 workers + findroot illinois
════════════════════════════════════════════════════════════════════════════════════════════
Problème identifié dans v5 :
    Détection séquentielle mpmath.siegelz → ~23ms/pas à t=3000, ~52ms/pas à t=9950
    → ~1 z/s en pratique (goulot : chaque pas = 1 appel Python bloquant)

Bug identifié dans Z_batch (riemann_siegel_batch.py) :
    Z_batch utilisait N_max = ⌊√(t_max/2π)⌋ + 1 FIXE pour tous les points du batch.
    Or la formule RS requiert N(t) = ⌊√(t/2π)⌋ propre à chaque t.
    Les termes n > N(t) ne font pas partie de la somme RS et introduisent une erreur
    ~2·Σ_{n>N(t)} 1/√n pouvant dépasser 3 — impossible de détecter les bons signes.
    → Z_batch NON utilisable pour la détection. Remplacé par Z_vect_correct.

Solution v4.1 (illinois_C post-fork — session 1 juin 2026) :
    1. Z_vect_correct     : masque booléen mask[k,n] = (n ≤ N(t_k)) par ligne
                            → chaque ligne n'accumule que ses N(t_k) termes exacts
                            → gain ×4000-×9000 vs mpmath.siegelz mesuré
    2. Parallélisme       : 4 workers multiprocessing traitent 4 chunks en même temps
                            → gain supplémentaire ×4 sur CPU i7 4 cœurs (vrai fork)
    3. illinois_mpfr.so   : chargé APRÈS fork dans chaque worker (ctypes.CDLL local)
                            → pas de partage d'état GMP entre parent et fils
                            → illinois C/libmpfr PREC=170 pour t ≥ 300 (gain ×39)
    4. Seuil T_SEUIL=300  : en-dessous (N < 7 termes RS), Illinois C interne imprécis
                            → mpmath.findroot illinois dps=15 (légitime, < 1% du temps)

Formules mathématiques de référence :
    Z(t) = e^{iθ(t)} · ζ(1/2+it)  — réelle, changements de signe ↔ zéros sur droite critique
    Z(t) ≈ 2·Σ_{n=1}^{N} cos(θ(t)−t·ln n)/√n + R(t)    N=⌊√(t/2π)⌋
    N(T) ≈ T/(2π)·ln(T/(2πe))                            formule exacte Backlund
    STEP = min(2π/(5·ln(T/2π)), 0.10)                    5 points par espacement moyen

⚠️ Ne pas modifier compute_zeros_v4.py ni compute_zeros_v5.py (références validées).

Auteur : hprzeta — Projet Hypothèse de Riemann — Phase C v4.1
Date   : 2026-05-31
"""

import sys
import math
import time
import os
import multiprocessing
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")                   # pas de fenêtre graphique (mode production)
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict

import mpmath
mpmath.mp.dps = 35                      # précision globale (validation, visualisation)


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — CHEMINS ET IMPORTS LOCAUX
# ═══════════════════════════════════════════════════════════════════════════════

_SRC_DIR   = Path(__file__).parent                  # .../src/calculs/optimisation/
_C_MODULES = _SRC_DIR / "c_modules"                 # dossier des binaires C

# Ajout des dossiers au chemin Python pour les imports locaux
sys.path.insert(0, str(_C_MODULES))                 # modules C optionnels
sys.path.insert(0, str(_SRC_DIR))                   # theta_rapide.py, turing_validation.py

# Imports locaux
from turing_validation import valider_turing        # validation Turing-Backlund
from theta_rapide import theta_exact                # θ(t) exact via mpmath (t < 20)

# Chemin vers le binaire Illinois C (libmpfr PREC=170 bits)
SO_PATH = _SRC_DIR / "c_modules" / "illinois_mpfr.so"
if not SO_PATH.exists():
    raise FileNotFoundError(
        f"illinois_mpfr.so introuvable : {SO_PATH}\n"
        f"Compiler : cd src/calculs/optimisation/c_modules && make"
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — Z(t) VECTORISÉ CORRECT (remplace Z_batch de riemann_siegel_batch)
# ═══════════════════════════════════════════════════════════════════════════════

_TWO_PI  = 2.0 * math.pi
_LOG_2PI = math.log(_TWO_PI)
_PI_8    = math.pi / 8.0


def _theta_vect(ts: np.ndarray) -> np.ndarray:
    """
    θ(t) vectorisé — même formule que theta_vect() dans riemann_siegel_batch,
    mais recalculée ici pour ne pas importer riemann_siegel_batch (qui a Z_batch bugué).

    θ(t) = (t/2)·ln(t/2π) − t/2 − π/8 + 1/(48t) + 7/(5760t³) − 31/(80640t⁵)
    Valide pour t ≥ 20 (Stirling). Pour t < 20 : mpmath.loggamma exact.
    """
    ts_cpu  = np.asarray(ts, dtype=np.float64)
    thetas  = np.empty_like(ts_cpu)
    mask    = ts_cpu >= 20.0                            # True = Stirling suffisant
    t_f     = ts_cpu[mask]                              # sous-tableau t ≥ 20
    if t_f.size > 0:
        t2 = t_f * t_f; t3 = t2 * t_f; t5 = t3 * t2  # puissances réutilisées
        thetas[mask] = (
            (t_f / 2.0) * (np.log(t_f) - _LOG_2PI)    # (t/2)·ln(t/2π)
            - t_f / 2.0                                 # − t/2
            - _PI_8                                     # − π/8
            + 1.0 / (48.0 * t_f)                       # + 1/(48t)
            + 7.0 / (5760.0 * t3)                      # + 7/(5760t³)
            - 31.0 / (80640.0 * t5)                    # − 31/(80640t⁵)
        )
    for i in np.where(~mask)[0]:                        # t < 20 : exact via mpmath
        thetas[i] = theta_exact(float(ts_cpu[i]))
    return thetas


def _psi_rs(u: float) -> float:
    """Ψ(u) = cos(π(u²/2 + 3/8)) / cos(πu) — terme de reste C0 de Riemann-Siegel."""
    denom = math.cos(math.pi * u)
    if abs(denom) < 1e-10:                              # évite la division par zéro
        return 0.0
    return math.cos(math.pi * (u * u / 2.0 + 0.375)) / denom


def Z_vect_correct(ts: np.ndarray) -> np.ndarray:
    """
    Z(t) vectorisé avec N(t) = ⌊√(t/2π)⌋ correct par ligne.

    Z(t_k) = 2·Σ_{n=1}^{N(t_k)} cos(θ(t_k) − t_k·ln n)/√n  +  R(t_k)

    Différence vs Z_batch (bugué) :
      Z_batch utilisait N_max identique pour toutes les lignes → erreur ~1/√n
      pour n > N(t_k). Ici, mask[k,n] = (n ≤ N(t_k)) annule ces termes exacts.

    Performances mesurées (même machine) :
      vs mpmath.siegelz séquentiel : ×4771 à t≈350, ×9083 à t≈3050, ×9873 à t≈9950
      vs Z_batch bugué            : précision correcte, vitesse similaire (numpy)
    """
    ts      = np.asarray(ts, dtype=np.float64)
    thetas  = _theta_vect(ts)
    taus    = np.sqrt(ts / _TWO_PI)                     # τ(t) = √(t/2π) pour chaque t
    Ns      = np.floor(taus).astype(int)                # N(t) = ⌊τ(t)⌋ pour chaque t
    N_max   = int(np.max(Ns)) + 1                       # dimension de la matrice

    ns      = np.arange(1, N_max + 1, dtype=np.float64)
    log_ns  = np.log(ns)                                # ln(n) précalculé
    inv_sqn = 1.0 / np.sqrt(ns)                         # 1/√n précalculé

    # Masque par ligne : mask[k, n] = True ssi n ≤ N(t_k)
    # Clé de la correction : chaque ligne n'accumule QUE ses N(t_k) termes légitimes
    mask   = (np.arange(1, N_max + 1)[None, :] <= Ns[:, None])

    # Matrice des phases : phases[k, n] = θ(t_k) − t_k·ln(n)
    phases = thetas[:, None] - ts[:, None] * log_ns[None, :]

    # Somme RS masquée : 2·Σ_{n=1}^{N(t_k)} cos(phases[k,n]) / √n
    # np.dot est efficace (BLAS) ; mask met à 0 les termes hors borne
    Z_out  = 2.0 * np.dot(np.cos(phases) * mask, inv_sqn)

    # Terme de reste C0+C1 (scalaire, une itération par point)
    h = 1e-7
    for k in range(len(ts)):
        tau  = float(taus[k])
        N    = int(Ns[k])
        u    = 2.0 * (tau - N) - 1.0                   # argument de ψ(u)
        C0   = _psi_rs(u)
        dpsi = (_psi_rs(u + h) - _psi_rs(u - h)) / (2.0 * h)   # dérivée numérique
        C1   = dpsi * (u * u / 2.0 - 0.375) / (math.pi * tau)  # correction d'ordre 1
        signe = (-1) ** (N - 1)
        Z_out[k] += signe * (tau ** (-0.5)) * (C0 + C1)

    return Z_out


T_SEUIL_ILLINOIS_C = 300.0      # en-dessous : RS peut être dégénéré, fallback toléré
N_WORKERS          = 4           # processus parallèles (= nb cœurs i7)
T_MIN_GLOBAL       = 14.0        # premier zéro non trivial à t ≈ 14.134

# HYPOTHÈSE à valider sur les grands t (Vérif B obligatoire) :
# à t≈9900, dps=15 → précision absolue ~10^4 × 10^{-15} = 10^{-11}, limite de tol=1e-12
# Si écart > 1e-10 à grand t → remonter à 20 puis 25 et re-tester
DPS_AFFINAGE       = 15          # précision pour mpmath.findroot illinois (workers)


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — FONCTIONS MATHÉMATIQUES DE BASE
# ═══════════════════════════════════════════════════════════════════════════════

def pas_adaptatif(T_MAX: float) -> float:
    """
    STEP = min( 2π / (5·ln(T/2π)), 0.10 )

    Objectif : au moins 5 échantillons par espacement moyen entre zéros.
    Espacement moyen : 2π/ln(T/2π).
    Cap 0.10 : actif pour tout T < 1.8×10⁶ (plage de travail actuelle).
    """
    denom = 5.0 * math.log(T_MAX / (2.0 * math.pi))    # 5·ln(T/2π)
    return min((2.0 * math.pi) / denom, 0.10)           # plafonné à 0.10


def N_attendu_local(T: float) -> int:
    """
    N(T) ≈ T/(2π)·ln(T/(2πe)) = T/(2π)·[ln(T/2π) − 1]

    IMPORTANT : diviseur 2πe et non 2π (le 'e' réduit de ~1 le logarithme).
    Erreur sans 'e' : sous-estimation de ~64% à T=100 000.
    """
    if T <= 2.0 * math.pi:                              # T trop petit, 0 zéros attendus
        return 0
    x = T / (2.0 * math.pi)                            # T/2π
    return int(x * (math.log(x) - 1.0))                # T/(2π) · [ln(T/2π) − 1]


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — WORKER MULTIPROCESSING (fonction top-level, picklable par nom)
# ═══════════════════════════════════════════════════════════════════════════════

def _worker_chunk(args: tuple) -> Tuple[List[float], Dict[str, int]]:
    """
    Worker exécuté dans un processus fils (fork sur Linux).

    Reçoit : (t_a, t_b, pas, tol, so_path) — bornes, paramètres et chemin du .so.
    Retourne : (liste_de_zeros, compteur_methodes).

    Étape 1 — Charger illinois_mpfr.so APRÈS fork :
        Évite tout partage d'état ctypes/GMP entre le parent et les fils.
        Chaque processus fils a sa propre instance de la bibliothèque.

    Étape 2 — Détection vectorisée (Z_vect_correct) :
        ts = [t_a, t_a+pas, …, t_b]   tableau numpy float64
        Z_vals = Z_vect_correct(ts)    matriciel numpy, N(t) correct par ligne
        → repère les i tels que Z_vals[i]·Z_vals[i+1] < 0

    Étape 3 — Affinage avec seuil T_SEUIL_ILLINOIS_C = 300 :
        t_mid ≥ 300  → lib.illinois_mpfr(a, b, tol) — C/libmpfr PREC=170 bits (×39)
        t_mid <  300 → mpmath.findroot illinois dps=DPS_AFFINAGE — N < 7 termes, légitime
    """
    t_a, t_b, pas, tol, so_path = args                # déballage des paramètres

    # Charger le .so APRÈS fork — chaque fils a sa propre copie, zéro partage GMP
    import ctypes as _ctypes
    _lib = _ctypes.CDLL(so_path)
    _lib.illinois_mpfr.restype  = _ctypes.c_double
    _lib.illinois_mpfr.argtypes = [_ctypes.c_double, _ctypes.c_double, _ctypes.c_double]

    # Vecteur de points couvrant [t_a, t_b] (pas*0.5 → inclusion de t_b malgré arrondis)
    ts = np.arange(t_a, t_b + pas * 0.5, pas, dtype=np.float64)

    # Détection vectorisée — N(t) correct par ligne, ×4000-×9000 vs mpmath séquentiel
    Z_vals = Z_vect_correct(ts)

    zeros_chunk = []
    stats_chunk = {
        "illinois_C"      : 0,   # illinois_mpfr C pour t ≥ 300 (majorité des zéros)
        "mpmath_petit_t"  : 0,   # mpmath pour t < 300 (N < 7 termes, légitimement lent)
        "mpmath_fallback" : 0,   # mpmath si illinois_C hors bornes (rare, ≈ 0)
        "echecs"          : 0,   # exceptions non rattrapées
    }

    for i in range(len(ts) - 1):
        if Z_vals[i] * Z_vals[i + 1] < 0:             # changement de signe → zéro entre les deux
            a, b  = float(ts[i]), float(ts[i + 1])
            t_mid = (a + b) / 2.0
            try:
                if t_mid >= T_SEUIL_ILLINOIS_C:
                    # Illinois C : N ≥ 7 termes RS → précis, gain ×39 vs mpmath dps=35
                    zero = _lib.illinois_mpfr(a, b, tol)
                    if a - 1e-10 <= zero <= b + 1e-10:  # sanity check bornes
                        zeros_chunk.append(zero)
                        stats_chunk["illinois_C"] += 1
                    else:
                        # Résultat hors bornes : fallback mpmath (rare — Turing détectera)
                        zero = float(mpmath.findroot(mpmath.siegelz, t_mid))
                        zeros_chunk.append(zero)
                        stats_chunk["mpmath_fallback"] += 1
                else:
                    # t < 300 : N < 7 termes RS → illinois_C interne imprécis → mpmath requis
                    old_dps      = mpmath.mp.dps
                    mpmath.mp.dps = DPS_AFFINAGE        # dps=15 : suffisant pour tol=1e-12
                    try:
                        zero = float(mpmath.findroot(
                            mpmath.siegelz,             # Z(t) de Hardy, vrais zéros garantis
                            (a, b),                     # intervalle avec changement de signe
                            solver="illinois",          # fausse position modifiée
                            tol=tol,                    # tolérance 1e-12
                            maxsteps=80,
                        ))
                        zeros_chunk.append(zero)
                        stats_chunk["mpmath_petit_t"] += 1
                    finally:
                        mpmath.mp.dps = old_dps         # restauration après l'appel

            except Exception:
                stats_chunk["echecs"] += 1              # compte sans crasher le worker

    return zeros_chunk, stats_chunk


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — SCANNER PARALLÈLE (4 WORKERS)
# ═══════════════════════════════════════════════════════════════════════════════

def scanner_parallele(
    T_MIN     : float,
    T_MAX     : float,
    pas       : float,
    tol       : float = 1e-12,
    n_workers : int   = N_WORKERS,
) -> Tuple[List[float], Dict[str, int]]:
    """
    Balayage parallèle de [T_MIN, T_MAX] sur n_workers processus.

    Architecture :
    ┌─────────────────────────────────────────────────────────────┐
    │  [T_MIN ────────────── T_MAX]                               │
    │     ↓ découpe en 4 chunks                                   │
    │  Worker 0 : [T_MIN, T_MIN+L+pas]    Z_batch + illinois_c   │
    │  Worker 1 : [T_MIN+L, T_MIN+2L+pas] Z_batch + illinois_c   │
    │  Worker 2 : [T_MIN+2L, T_MIN+3L+pas]Z_batch + illinois_c   │
    │  Worker 3 : [T_MIN+3L, T_MAX]       Z_batch + illinois_c   │
    │     ↓ merge + tri + déduplication                           │
    │  zeros_finaux (triés, sans duplicats de frontière)          │
    └─────────────────────────────────────────────────────────────┘

    Le chevauchement de +pas aux frontières garantit qu'aucun zéro
    à la jonction de deux chunks n'est manqué.
    """
    # ── Découpe en chunks avec chevauchement d'un pas aux frontières ─────────
    largeur = (T_MAX - T_MIN) / n_workers               # taille d'un chunk sans overlap
    chunks  = []
    so_str  = str(SO_PATH)                              # string pour sécurité pickle
    for i in range(n_workers):
        t_a = T_MIN + i * largeur
        # Extension +pas : le dernier point de ce chunk = premier point du suivant
        # → aucun changement de signe ne tombe dans le vide entre deux chunks
        t_b = min(T_MIN + (i + 1) * largeur + pas, T_MAX)
        chunks.append((t_a, t_b, pas, tol, so_str))    # so_str passé à chaque worker

    print(f"\n  Balayage v4.1 parallèle ({n_workers} workers)")
    print(f"  Plage : [{T_MIN:.1f}, {T_MAX:.1f}]   pas = {pas:.4f}")
    for i, (t_a, t_b, _, _, _) in enumerate(chunks):
        print(f"    Worker {i} : [{t_a:>10.2f}, {t_b:>10.2f}]")
    print()

    # ── Exécution parallèle ─────────────────────────────────────────────────
    debut = time.time()
    with multiprocessing.Pool(processes=n_workers) as pool:
        # pool.map bloque jusqu'à ce que tous les workers terminent
        resultats = pool.map(_worker_chunk, chunks)
    duree_total = time.time() - debut

    # ── Fusion des résultats des 4 workers ──────────────────────────────────
    tous_zeros     = []
    stats_globales = {
        "illinois_C"      : 0,   # C/libmpfr pour t ≥ 300
        "mpmath_petit_t"  : 0,   # mpmath pour t < 300 (légitime)
        "mpmath_fallback" : 0,   # mpmath si illinois_C hors bornes (rare)
        "echecs"          : 0,   # exceptions
    }

    for zeros_chunk, stats_chunk in resultats:
        tous_zeros.extend(zeros_chunk)                  # concaténation des listes
        for methode, nb in stats_chunk.items():
            stats_globales[methode] = stats_globales.get(methode, 0) + nb

    # ── Tri et déduplication ─────────────────────────────────────────────────
    tous_zeros.sort()                                   # tri croissant des parties imaginaires

    # Suppression des quasi-doublons (artefact de chevauchement aux frontières)
    # Deux zéros "réels" ne peuvent pas être à moins de pas*0.5 l'un de l'autre
    zeros_finaux = []
    for z in tous_zeros:
        if not zeros_finaux or abs(z - zeros_finaux[-1]) > pas * 0.5:
            zeros_finaux.append(z)                      # conserve uniquement si assez distant

    vitesse = len(zeros_finaux) / duree_total if duree_total > 0 else 0
    print(f"  Terminé en {duree_total:.1f}s  —  {len(zeros_finaux)} zéros  —  {vitesse:.1f} z/s")

    return zeros_finaux, stats_globales


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 7 — VÉRIFICATION LMFDB (20 premiers zéros)
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
    """Compare les premiers zéros calculés aux références LMFDB."""
    n = min(len(zeros), n_check, len(LMFDB_REFERENCES))
    if n == 0:
        return {"score": "0/0", "details": []}

    print(f"\n  Vérification LMFDB ({n} premiers zéros) :")
    print(f"  {'#':>4}  {'Calculé':>20}  {'LMFDB':>20}  {'Écart':>12}")
    print("  " + "─" * 62)

    details = []
    for i in range(n):
        ecart = abs(zeros[i] - LMFDB_REFERENCES[i])    # écart absolu
        ok    = ecart < 1e-10                           # seuil de validation LMFDB
        sym   = "✅" if ok else ("⚠️ " if ecart < 1e-6 else "❌")
        print(f"  {i+1:>4}  {zeros[i]:>20.14f}  {LMFDB_REFERENCES[i]:>20.14f}"
              f"  {ecart:>12.2e}  {sym}")
        details.append({"n": i+1, "calcule": zeros[i],
                        "lmfdb": LMFDB_REFERENCES[i], "ecart": ecart, "ok": ok})

    n_ok = sum(1 for d in details if d["ok"])
    print(f"\n  Score LMFDB : {n_ok}/{n} zéros à < 10⁻¹⁰")
    return {"score": f"{n_ok}/{n}", "details": details}


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 8 — SAUVEGARDE CSV + LOG D'EXÉCUTION
# ═══════════════════════════════════════════════════════════════════════════════

def sauvegarder_csv(
    zeros      : List[float],
    stats      : dict,
    T_MAX      : float,
    pas        : float,
    horodatage : str,
    dossier    : Path,
) -> Path:
    """Sauvegarde horodatée — jamais d'écrasement d'un run validé."""
    nom_csv    = f"zeros_v4_1_T{T_MAX:.0f}_{horodatage}.csv"
    chemin_csv = dossier / nom_csv
    df = pd.DataFrame({
        "n"                 : range(1, len(zeros) + 1),
        "partie_imaginaire" : zeros,
        "T_MAX"             : T_MAX,
        "version"           : "v4.1",
        "methode_detection" : "Z_batch_vectorise",
        "methode_affinage"  : "mpmath_findroot_illinois",
        "pas_balayage"      : pas,
        "calcule_le"        : horodatage,
    })
    df.to_csv(str(chemin_csv), index=False)
    print(f"\n  {len(zeros)} zéros sauvegardés → {chemin_csv}")
    return chemin_csv


def ecrire_log(
    chemin_log        : Path,
    horodatage        : str,
    T_MIN             : float,
    T_MAX             : float,
    pas               : float,
    tol               : float,
    duree_s           : float,
    zeros             : List[float],
    stats             : dict,
    resultats_lmfdb   : dict,
    resultats_turing  : dict,
    chemin_csv        : Path,
    n_workers         : int,
) -> None:
    """Journal complet d'exécution."""
    import platform
    lignes = []
    sep    = "=" * 65

    def L(texte=""):
        lignes.append(texte)

    L(sep)
    L("  JOURNAL D'EXÉCUTION — compute_zeros_v4_1.py  (Phase C v4.1)")
    L("  Projet : Hypothèse de Riemann — hprzeta")
    L(sep); L()

    L("  [1] HORODATAGE")
    L(f"      Début            : {horodatage}")
    L(f"      Fin              : {datetime.now().strftime('%Y%m%d_%H%M%S')}")
    L(f"      Durée totale     : {duree_s/60:.2f} min  ({duree_s:.1f} s)"); L()

    L("  [2] PARAMÈTRES v4.1")
    L(f"      T_MIN            = {T_MIN}")
    L(f"      T_MAX            = {T_MAX}")
    L(f"      Pas balayage     = {pas:.4f}")
    L(f"      TOL_AFFINAGE     = {tol:.0e}")
    L(f"      mpmath.mp.dps    = {mpmath.mp.dps}  (global ; dps fallback = DPS_AFFINAGE={DPS_AFFINAGE})")
    L(f"      Workers          = {n_workers}")
    L(f"      T_SEUIL_C        = {T_SEUIL_ILLINOIS_C}  (illinois_C si t ≥ seuil)")
    L(f"      illinois_mpfr.so = {SO_PATH}")
    L(f"      Détection        = Z_vect_correct vectorisé (numpy, N(t) correct par ligne)")
    L(f"      Affinage t≥300   = illinois_mpfr C/libmpfr PREC=170 bits (×39 vs mpmath)")
    L(f"      Affinage t<300   = mpmath.findroot illinois dps={DPS_AFFINAGE} (N<7 termes)"); L()

    L("  [3] RÉSULTATS NUMÉRIQUES")
    L(f"      Zéros trouvés    = {len(zeros)}")
    L(f"      N attendus       = {N_attendu_local(T_MAX)}")
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
    L(f"      Python           = {sys.version.split()[0]}")
    L(f"      OS               = {platform.system()} {platform.release()}")
    L(f"      mpmath           = {mpmath.__version__}")
    L(f"      numpy            = {np.__version__}")
    L(f"      CPU cores        = {multiprocessing.cpu_count()}")
    L()
    L(sep)
    L(f"  Fin du journal — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    L(sep)

    chemin_log.write_text("\n".join(lignes), encoding="utf-8")
    print(f"  Journal → {chemin_log}")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 9 — VISUALISATION
# ═══════════════════════════════════════════════════════════════════════════════

def visualiser(
    zeros      : List[float],
    T_MAX      : float,
    horodatage : str,
    dossier    : Path,
) -> None:
    """3 graphiques : Z(t) sur [14,60], espacements GUE, droite critique."""
    if len(zeros) < 3:
        return

    ecarts = np.diff(zeros)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(
        f"Zéros de ζ(½+it) — v4.1 Z_batch — {len(zeros)} zéros [T_MAX={T_MAX:.0f}]",
        fontsize=13, fontweight="bold"
    )

    # Graphique 1 : Z(t) avec marqueurs des zéros (plage visible [14, 60])
    t_plot = np.linspace(14, min(60, T_MAX), 600)
    Z_vals = [float(mpmath.siegelz(t)) for t in t_plot]    # précis pour affichage
    ax = axes[0]
    ax.plot(t_plot, Z_vals, 'b-', linewidth=0.8)
    ax.axhline(0, color='k', linewidth=0.5)
    for t0 in zeros:
        if t0 <= 60:
            ax.axvline(t0, color='r', linewidth=0.5, alpha=0.4)
    ax.set_xlabel("t"); ax.set_ylabel("Z(t)")
    ax.set_title("Fonction Z de Hardy [14, 60]")
    ax.grid(True, alpha=0.3)

    # Graphique 2 : espacement normalisé vs distribution GUE (conjecture de Montgomery)
    t_mid   = np.array(zeros[:-1])
    delta_n = ecarts * np.log(t_mid / (2 * math.pi)) / (2 * math.pi)
    ax = axes[1]
    ax.hist(delta_n, bins=50, density=True, edgecolor='black',
            alpha=0.75, color='steelblue')
    s_vals = np.linspace(0, 4, 200)
    gue    = (math.pi / 2) * s_vals * np.exp(-math.pi * s_vals**2 / 4)
    ax.plot(s_vals, gue, 'r-', linewidth=2, label='GUE (Wigner-Dyson)')
    ax.set_xlabel("δₙ normalisé"); ax.set_ylabel("Densité")
    ax.set_title("Espacements vs GUE (conjecture de Montgomery)")
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

    # Graphique 3 : droite critique Re(s) = 1/2
    ax = axes[2]
    ax.scatter([0.5] * len(zeros), zeros, s=3, color='darkblue', alpha=0.4)
    ax.axvline(0.5, color='r', linestyle='--', linewidth=1.5, label='Re(s) = ½')
    ax.set_xlabel("Re(s)"); ax.set_ylabel("Im(s) = t")
    ax.set_title("Droite critique — Hypothèse de Riemann")
    ax.set_xlim(0, 1); ax.legend(); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    nom_png = f"zeros_v4_1_T{T_MAX:.0f}_{horodatage}.png"
    plt.savefig(str(dossier / nom_png), dpi=150)    # obligatoire
    plt.close()                                      # jamais plt.show() (bloquant)
    print(f"  Graphique → {nom_png}")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 10 — INTERFACE UTILISATEUR
# ═══════════════════════════════════════════════════════════════════════════════

def saisir_parametres():
    """Interaction console : saisie de T_MAX, affichage config, confirmation."""
    print()
    print("=" * 65)
    print("   CALCUL DES ZÉROS — v4.1 (Z_batch vectorisé + 4 workers)")
    print("=" * 65)
    print()
    print("  Détection : Z_vect_correct (numpy)         — gain ×4000-×9000 vs mpmath séquentiel")
    print("  Affinage  : illinois_mpfr.so post-fork     — C/libmpfr PREC=170 bits (×39 vs mpmath)")
    print("  Fallback  : mpmath illinois dps=15         — t < 300 uniquement (N < 7 termes RS)")
    print("  Parallèle : 4 workers multiprocessing     — .so chargé APRÈS fork, GMP isolé")
    print()
    print("  Estimations (à valider avec Turing) :")
    print("    T =   300  → ~138 zéros  →  < 15s")
    print("    T =   650  → ~170 zéros  →  ~30s")
    print("    T = 1 000  → ~396 zéros  →  ~1 min")
    print("    T = 10 000 → ~10142 zéros →  ~5-10 min")
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
    print(f"\n  ── Configuration v4.1 ──────────────────────────────────────")
    print(f"     T_MAX              = {T_MAX:.0f}")
    print(f"     Pas balayage       = {pas:.4f}")
    print(f"     N zéros attendus   ≈ {N_attendu_local(T_MAX)}")
    print(f"     Workers            = {N_WORKERS}")
    print(f"     Seuil Illinois_C   = {T_SEUIL_ILLINOIS_C}")

    confirm = input("\n  Lancer le calcul ? [O/n] : ").strip().lower()
    if confirm in ("n", "non"):
        sys.exit(0)

    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    dossier    = Path("calculs") / f"v4_1_T{T_MAX:.0f}_{horodatage}"
    dossier.mkdir(parents=True, exist_ok=True)

    return T_MAX, pas, horodatage, dossier


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 11 — POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Point d'entrée principal."""
    debut_global = time.time()

    T_MAX, pas, horodatage, dossier = saisir_parametres()
    TOL   = 1e-12
    T_MIN = T_MIN_GLOBAL

    # Lancement du balayage parallèle
    zeros, stats = scanner_parallele(T_MIN, T_MAX, pas, TOL, N_WORKERS)
    duree = time.time() - debut_global

    # ── Résumé terminal ──────────────────────────────────────────────────────
    print()
    print("=" * 65)
    print("  RÉSULTATS v4.1")
    print("=" * 65)
    print(f"  Zéros trouvés    : {len(zeros)}")
    print(f"  Attendus (Weyl)  : {N_attendu_local(T_MAX)}")
    print(f"  Durée            : {duree/60:.2f} min  ({duree:.1f} s)")
    vitesse = len(zeros) / duree if duree > 0 else 0
    print(f"  Vitesse          : {vitesse:.2f} zéros/s")
    print()
    print("  Répartition des méthodes d'affinage :")
    total = sum(v for k, v in stats.items() if k != "echecs")
    for methode, nb in sorted(stats.items()):
        pct = nb / total * 100 if total > 0 else 0
        print(f"    {methode:<24} : {nb:>5}  ({pct:.1f}%)")
    if zeros:
        print(f"\n  t₁  = {zeros[0]:.12f}")
        print(f"  t_n = {zeros[-1]:.12f}")
    print("=" * 65)

    # ── Validation et sauvegarde ─────────────────────────────────────────────
    resultats_lmfdb  = verifier_lmfdb(zeros, n_check=20)
    resultats_turing = valider_turing(zeros, dps=30)
    chemin_csv       = sauvegarder_csv(zeros, stats, T_MAX, pas, horodatage, dossier)
    visualiser(zeros, T_MAX, horodatage, dossier)

    nom_log    = f"execution_v4_1_T{T_MAX:.0f}_{horodatage}.log"
    chemin_log = dossier / nom_log
    ecrire_log(
        chemin_log=chemin_log, horodatage=horodatage,
        T_MIN=T_MIN, T_MAX=T_MAX, pas=pas, tol=TOL,
        duree_s=duree, zeros=zeros, stats=stats,
        resultats_lmfdb=resultats_lmfdb, resultats_turing=resultats_turing,
        chemin_csv=chemin_csv, n_workers=N_WORKERS,
    )

    # ── Critères de succès ───────────────────────────────────────────────────
    print()
    print("=" * 65)
    print(f"  v4.1 terminée — fichiers dans : {dossier}")
    if resultats_turing["complet"]:
        print("  Validation Turing : ✅ COMPLET (0 zéro manqué)")
    else:
        manq = resultats_turing["manquants_total"]
        print(f"  Validation Turing : ❌ {manq} zéros MANQUANTS — réduire le pas")

    total_c   = sum(v for k, v in stats.items() if k != "echecs")
    nb_illc   = stats.get("illinois_C", 0)             # Illinois C/libmpfr (t ≥ 300)
    nb_mpt    = stats.get("mpmath_petit_t", 0)         # mpmath (t < 300, légitime)
    nb_fallbk = stats.get("mpmath_fallback", 0)        # fallback non borné (doit être 0)
    pct_illc  = nb_illc / total_c * 100 if total_c > 0 else 0
    lmfdb_s   = resultats_lmfdb.get("score", "0/0").split("/")
    score_l   = int(lmfdb_s[0]) if len(lmfdb_s) == 2 else 0
    vitesse_f = len(zeros) / duree if duree > 0 else 0

    print()
    print("  Critères v4.1 (illinois_C + fallback) :")
    print(f"    illinois_C (t≥300): {nb_illc:5d}  ({pct_illc:.1f}%)  (cible > 90%)"
          + (" ✅" if pct_illc > 90 else " ⚠️ "))
    print(f"    mpmath_petit_t    : {nb_mpt:5d}  (t < 300, légitime)")
    print(f"    mpmath_fallback   : {nb_fallbk:5d}  (doit être ≈ 0)"
          + (" ✅" if nb_fallbk == 0 else " ⚠️ "))
    print(f"    Turing complet    : {'✅' if resultats_turing['complet'] else '❌'}")
    print(f"    LMFDB 19/20       : {resultats_lmfdb.get('score','?')}"
          + (" ✅" if score_l >= 19 else " ⚠️ "))
    print(f"    Vitesse           : {vitesse_f:.1f} z/s  (cible > 5.0)"
          + (" ✅" if vitesse_f > 5.0 else " ⚠️ "))
    print("=" * 65)


if __name__ == "__main__":
    main()
