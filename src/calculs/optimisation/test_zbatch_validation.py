#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_zbatch_validation.py — Point d'arrêt N°1 (v2) : Z_vect_correct vs mpmath.siegelz
════════════════════════════════════════════════════════════════════════════════════════
Valide Z_vect_correct (correction du bug N_max fixe de Z_batch) avant utilisation.

Bug corrigé : Z_batch utilisait N_max = ⌊√(t_max/2π)⌋ + 1 FIXE pour tout le batch.
              Z_vect_correct utilise N(t_k) = ⌊√(t_k/2π)⌋ par ligne (masque booléen).

Pour chaque plage de t, ce script vérifie :
  1. Écart numérique |Z_vect_correct(t) − mpmath.siegelz(t)| : doit être ~10⁻³ (erreur RS C0+C1 normale)
  2. Accord sur les changements de signe : objectif 100% (sinon des zéros seraient ratés)

Auteur : hprzeta — 2026-05-31
"""

import sys
import math
import time
import numpy as np
from pathlib import Path

# Ajout du dossier optimisation au chemin Python
_OPT_DIR = Path(__file__).parent
sys.path.insert(0, str(_OPT_DIR))

import mpmath
mpmath.mp.dps = 15              # dps de détection (idem v5)

from theta_rapide import theta_exact

# ── Reproduction locale de Z_vect_correct (sans dépendance à compute_zeros_v4_1) ───

_TWO_PI  = 2.0 * math.pi
_LOG_2PI = math.log(_TWO_PI)
_PI_8    = math.pi / 8.0


def _theta_vect(ts):
    """θ(t) vectorisé — Stirling pour t≥20, mpmath exact pour t<20."""
    ts_cpu = np.asarray(ts, dtype=np.float64)
    thetas = np.empty_like(ts_cpu)
    mask   = ts_cpu >= 20.0
    t_f    = ts_cpu[mask]
    if t_f.size > 0:
        t2 = t_f*t_f; t3 = t2*t_f; t5 = t3*t2
        thetas[mask] = (
            (t_f/2.0)*(np.log(t_f) - _LOG_2PI) - t_f/2.0 - _PI_8
            + 1.0/(48.0*t_f) + 7.0/(5760.0*t3) - 31.0/(80640.0*t5)
        )
    for i in np.where(~mask)[0]:
        thetas[i] = theta_exact(float(ts_cpu[i]))
    return thetas


def _psi_rs(u):
    """Ψ(u) = cos(π(u²/2 + 3/8)) / cos(πu)."""
    d = math.cos(math.pi * u)
    return 0.0 if abs(d) < 1e-10 else math.cos(math.pi*(u*u/2.0+0.375))/d


def Z_vect_correct(ts):
    """
    Z(t) vectorisé avec N(t) correct par ligne — la correction du bug de Z_batch.

    mask[k, n] = (n ≤ N(t_k)) annule les termes n > N(t_k) qui biaisaient Z_batch.
    """
    ts      = np.asarray(ts, dtype=np.float64)
    thetas  = _theta_vect(ts)
    taus    = np.sqrt(ts / _TWO_PI)
    Ns      = np.floor(taus).astype(int)
    N_max   = int(np.max(Ns)) + 1
    ns      = np.arange(1, N_max+1, dtype=np.float64)
    log_ns  = np.log(ns)
    inv_sqn = 1.0 / np.sqrt(ns)

    # Masque par ligne : corrige le bug de Z_batch (N_max fixe pour tout le batch)
    mask   = (np.arange(1, N_max+1)[None, :] <= Ns[:, None])
    phases = thetas[:, None] - ts[:, None] * log_ns[None, :]
    Z_out  = 2.0 * np.dot(np.cos(phases) * mask, inv_sqn)

    # Reste C0+C1
    h = 1e-7
    for k in range(len(ts)):
        tau  = float(taus[k]); N = int(Ns[k])
        u    = 2.0*(tau - N) - 1.0
        C0   = _psi_rs(u)
        dpsi = (_psi_rs(u+h) - _psi_rs(u-h)) / (2.0*h)
        C1   = dpsi*(u*u/2.0 - 0.375) / (math.pi*tau)
        Z_out[k] += (-1)**(N-1) * (tau**(-0.5)) * (C0 + C1)

    return Z_out


# ── Plages à tester ────────────────────────────────────────────────────────────
PLAGES = [
    ("t ∈ [14, 100]",       14.0,    100.0,  0.10),
    ("t ∈ [300, 400]",     300.0,    400.0,  0.10),
    ("t ∈ [3000, 3100]",  3000.0,   3100.0,  0.10),
    ("t ∈ [9900, 10000]", 9900.0,  10000.0,  0.10),
]

# ── En-tête ────────────────────────────────────────────────────────────────────
print()
print("=" * 72)
print("  VALIDATION Z_vect_correct vs mpmath.siegelz — Point d'arrêt N°1 (v2)")
print("  Correction : masque N(t) par ligne (bug N_max fixe de Z_batch corrigé)")
print("=" * 72)

resultats = []

for label, t_min, t_max, step in PLAGES:

    ts = np.arange(t_min, t_max + step * 0.5, step, dtype=np.float64)
    n  = len(ts)
    print(f"\n  ── {label}  (step={step}, {n} points) ──────────────────────────")

    # Z_vect_correct
    t0       = time.perf_counter()
    Z_corr   = Z_vect_correct(ts)
    dt_corr  = time.perf_counter() - t0

    # mpmath.siegelz (référence)
    print(f"     mpmath.siegelz ({n} appels à dps=15)... ", end="", flush=True)
    t0        = time.perf_counter()
    Z_mpmath  = np.array([float(mpmath.siegelz(float(t))) for t in ts])
    dt_mpmath = time.perf_counter() - t0
    print(f"OK ({dt_mpmath:.1f}s)")

    # Écarts numériques
    ecarts      = np.abs(Z_corr - Z_mpmath)
    ecart_max   = float(np.max(ecarts))
    ecart_moyen = float(np.mean(ecarts))

    # Changements de signe
    signes_c  = np.sign(Z_corr)
    signes_m  = np.sign(Z_mpmath)
    cs_corr   = set(i for i in range(n-1) if signes_c[i] * signes_c[i+1] < 0)
    cs_mpmath = set(i for i in range(n-1) if signes_m[i] * signes_m[i+1] < 0)
    communs   = cs_corr & cs_mpmath
    desaccords = cs_corr ^ cs_mpmath
    n_desac   = len(desaccords)
    gain      = dt_mpmath / dt_corr if dt_corr > 0 else float("inf")

    print(f"     Écart max   |Z_vect_correct − siegelz|  = {ecart_max:.3e}")
    print(f"     Écart moyen |Z_vect_correct − siegelz|  = {ecart_moyen:.3e}")
    print(f"     Changements de signe Z_vect_correct      = {len(cs_corr)}")
    print(f"     Changements de signe mpmath              = {len(cs_mpmath)}")
    print(f"     En accord                                = {len(communs)}")
    if n_desac == 0:
        print(f"     Désaccords                              = 0  ✅ accord parfait")
    else:
        print(f"     Désaccords                              = {n_desac}  ⚠️ DIVERGENCES")
        for idx in sorted(desaccords)[:5]:
            src = "corr_seul" if idx in cs_corr else "mpmath_seul"
            print(f"       t={float(ts[idx]):.4f} → {src}  "
                  f"Z_corr={Z_corr[idx]:+.4e}  siegelz={Z_mpmath[idx]:+.4e}")
    print(f"     Temps Z_vect_correct : {dt_corr*1000:.1f}ms  |  "
          f"Temps siegelz : {dt_mpmath:.1f}s  |  Gain : ×{gain:.0f}")

    resultats.append({
        "label": label, "n_pts": n,
        "ecart_max": ecart_max, "ecart_moy": ecart_moyen,
        "n_cs_corr": len(cs_corr), "n_cs_mpmath": len(cs_mpmath),
        "desaccords": n_desac, "gain": gain,
    })

# ── Tableau récapitulatif ──────────────────────────────────────────────────────
print()
print("=" * 76)
print("  RÉCAPITULATIF")
print("=" * 76)
print(f"  {'Plage':<25} {'Ecart_max':>12} {'Ecart_moy':>12} "
      f"{'CS_corr':>8} {'CS_mpm':>7} {'Desac':>6} {'Gain':>8}")
print("  " + "─" * 74)
for r in resultats:
    sym = "✅" if r["desaccords"] == 0 else "⚠️ "
    print(f"  {r['label']:<25} {r['ecart_max']:>12.3e} {r['ecart_moy']:>12.3e} "
          f"{r['n_cs_corr']:>8d} {r['n_cs_mpmath']:>7d} {r['desaccords']:>4d} {sym} "
          f"{r['gain']:>6.0f}×")

n_total_desac = sum(r["desaccords"] for r in resultats)
print()
print("=" * 76)
if n_total_desac == 0:
    print("  ✅ VALIDATION RÉUSSIE : Z_vect_correct et mpmath.siegelz en accord parfait")
    print("     sur tous les changements de signe — prêt pour la détection en production.")
else:
    print(f"  ⚠️  {n_total_desac} désaccord(s) restant(s) — analyse requise.")
print()
print("  STOP — Attente du feu vert ('OK continue') avant le run T=300 (Point N°2).")
print("=" * 76)
