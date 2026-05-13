#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
riemann_siegel_batch.py — Z(t) vectorisé CPU (numpy) ou GPU (CuPy)
═══════════════════════════════════════════════════════════════════════════════
VERSION GPU/CPU avec détection automatique.

STRATÉGIE
──────────
    1. Si CuPy installé ET GPU CUDA disponible → mode GPU (×8 à ×12)
    2. Sinon → mode CPU numpy (×7 à ×15 vs scalaire)
    Le code est IDENTIQUE dans les deux modes — seul le backend change.

POURQUOI LA GTX 960M AIDE
──────────────────────────
    CPU i7 4 cœurs : 32 opérations flottantes simultanées (AVX2)
    GPU GTX 960M   : 640 cœurs CUDA = 640 opérations simultanées
    Gain réel      : ×8 à ×12 (overhead copie CPU↔GPU)

MÉMOIRE GPU (GTX 960M = 4 GB VRAM)
────────────────────────────────────
    Matrice phases : M × N × 8 bytes
    Blocs recommandés :
        T = 10 000  (N=39)  → bloc M=500 000 → 156 MB ✅
        T = 100 000 (N=126) → bloc M=200 000 → 201 MB ✅
        T = 500 000 (N=281) → bloc M=100 000 → 225 MB ✅

Auteur : hprzeta — Projet Hypothèse de Riemann
Date   : 2026
"""

import math
import time
import numpy as np
from typing import List

# ─── Section 1 — Détection GPU et choix du backend ───────────────────────────

_GPU_DISPONIBLE = False
_GPU_NOM        = "aucun"
xp              = np

try:
    import cupy as cp
    n_devices = cp.cuda.runtime.getDeviceCount()
    if n_devices > 0:
        props    = cp.cuda.runtime.getDeviceProperties(0)
        _GPU_NOM = props["name"].decode()
        _GPU_DISPONIBLE = True
        xp       = cp
        print(f"  ✅  GPU détectée : {_GPU_NOM}")
        print(f"       Backend      : CuPy (mode GPU)")
    else:
        print("  ⚠️   CuPy installé mais aucune GPU CUDA détectée → mode CPU")
except ImportError:
    print("  ℹ️   CuPy absent → mode CPU numpy"
          " (installer : pip install cupy-cuda11x)")
except Exception as e:
    print(f"  ⚠️   CuPy erreur ({e}) → mode CPU numpy")


def mode_actif() -> str:
    if _GPU_DISPONIBLE:
        return f"GPU ({_GPU_NOM}, CuPy)"
    return "CPU (numpy, AVX2)"


# ─── Imports locaux ───────────────────────────────────────────────────────────
try:
    from theta_rapide import theta_asymptotique, theta_exact, Z_fast
except ImportError:
    raise ImportError("Placer theta_rapide.py dans le même dossier")


# ─── Terme de reste RS (intégré — pas besoin de riemann_siegel.py) ────────────

def _psi(u: float) -> float:
    """Ψ(u) = cos(π(u²/2 + 3/8)) / cos(πu)"""
    denom = math.cos(math.pi * u)
    if abs(denom) < 1e-10:
        return 0.0
    return math.cos(math.pi * (u * u / 2.0 + 0.375)) / denom


def _reste_RS(t: float, N: int, facteur: float) -> float:
    """Terme de reste de la formule de Riemann-Siegel."""
    signe = (-1) ** (N - 1)
    tau   = math.sqrt(t / _TWO_PI)
    u     = 2.0 * (tau - N) - 1.0
    h     = 1e-7
    dpsi  = (_psi(u + h) - _psi(u - h)) / (2.0 * h)
    C0    = _psi(u)
    C1    = dpsi * (u * u / 2.0 - 0.375) / (math.pi * tau)
    return signe * facteur * (C0 + C1)

_TWO_PI = 2.0 * math.pi


# ─── Section 2 — θ(t) vectorisé (toujours CPU) ───────────────────────────────

def theta_vect(ts: np.ndarray, seuil: float = 20.0) -> np.ndarray:
    """
    Calcule θ(t) pour un tableau numpy — toujours sur CPU (rapide).
    """
    LOG_2PI = math.log(_TWO_PI)
    PI_8    = math.pi / 8.0
    ts_cpu  = np.asarray(ts, dtype=np.float64)
    thetas  = np.empty_like(ts_cpu)

    mask_fast = ts_cpu >= seuil
    t_f = ts_cpu[mask_fast]
    if t_f.size > 0:
        t2 = t_f * t_f; t3 = t2 * t_f; t5 = t3 * t2
        thetas[mask_fast] = (
            (t_f / 2.0) * (np.log(t_f) - LOG_2PI)
            - t_f / 2.0 - PI_8
            + 1.0 / (48.0 * t_f)
            + 7.0 / (5760.0 * t3)
            - 31.0 / (80640.0 * t5)
        )
    for i in np.where(~mask_fast)[0]:
        thetas[i] = theta_exact(float(ts_cpu[i]))

    return thetas


# ─── Section 3 — Calcul d'un bloc GPU ────────────────────────────────────────

def _bloc_gpu(ts_cpu, thetas_cpu, log_ns, inv_sqn):
    """Calcul matriciel sur GPU via CuPy — fallback CPU si erreur runtime."""
    global _GPU_DISPONIBLE
    try:
        ts_g     = cp.asarray(ts_cpu,     dtype=cp.float64)
        thetas_g = cp.asarray(thetas_cpu, dtype=cp.float64)
        log_ns_g = cp.asarray(log_ns,     dtype=cp.float64)
        inv_sqn_g= cp.asarray(inv_sqn,    dtype=cp.float64)
        phases   = thetas_g[:, None] - ts_g[:, None] * log_ns_g[None, :]
        Z_g      = 2.0 * cp.dot(cp.cos(phases), inv_sqn_g)
        return cp.asnumpy(Z_g)
    except Exception as e:
        print(f"\n  ⚠️   GPU erreur runtime : {e}")
        print(f"       → Bascule automatique sur CPU numpy")
        print(f"       → Fix : sudo apt-get install cuda-nvrtc-11-2")
        _GPU_DISPONIBLE = False
        return _bloc_cpu(ts_cpu, thetas_cpu, log_ns, inv_sqn)


def _bloc_cpu(ts_cpu, thetas_cpu, log_ns, inv_sqn):
    """Calcul matriciel sur CPU via numpy."""
    phases = thetas_cpu[:, None] - ts_cpu[:, None] * log_ns[None, :]
    return 2.0 * np.dot(np.cos(phases), inv_sqn)


# ─── Section 4 — Z_batch principal ───────────────────────────────────────────

def Z_batch(
    ts          : np.ndarray,
    avec_reste  : bool = True,
    bloc_interne: int  = None,
) -> np.ndarray:
    """
    Calcule Z(t) pour tous les points ts — GPU si disponible, sinon CPU.

    Z(t_k) = 2·Σ_{n=1}^{N} cos(θ(t_k) − t_k·ln n) / √n  +  R(t_k)

    Paramètres
    ----------
    ts           : points t (tous > 14)
    avec_reste   : inclure le terme de reste RS
    bloc_interne : taille du sous-bloc (None = auto selon VRAM/RAM)
    """
    M     = len(ts)
    Z_out = np.zeros(M, dtype=np.float64)

    tau_max  = math.sqrt(float(np.max(ts)) / _TWO_PI)
    N_max    = int(tau_max) + 1
    ns       = np.arange(1, N_max + 1, dtype=np.float64)
    log_ns   = np.log(ns)
    inv_sqn  = 1.0 / np.sqrt(ns)
    thetas   = theta_vect(ts)

    # Taille de bloc automatique
    if bloc_interne is None:
        if _GPU_DISPONIBLE:
            # Limite à 1.5 GB par bloc sur VRAM
            bloc_interne = min(500_000, int(1_500_000_000 / (N_max * 8)))
            bloc_interne = max(bloc_interne, 1_000)
        else:
            bloc_interne = 2_000

    calc = _bloc_gpu if _GPU_DISPONIBLE else _bloc_cpu

    for i0 in range(0, M, bloc_interne):
        i1       = min(i0 + bloc_interne, M)
        ts_b     = ts[i0:i1]
        thetas_b = thetas[i0:i1]

        Z_out[i0:i1] = calc(ts_b, thetas_b, log_ns, inv_sqn)

        if avec_reste:
            for j, t in enumerate(ts_b):
                tau = math.sqrt(t / _TWO_PI)
                N   = int(tau)
                Z_out[i0 + j] += _reste_RS(t, N, tau ** (-0.5))

    return Z_out


# ─── Section 5 — Scanner hybride détection + affinage ────────────────────────

def scanner_batch(
    t_min        : float,
    t_max        : float,
    step         : float = 0.1,
    tol_affinage : float = 1e-12,
    dps_affinage : int   = 35,
    bloc         : int   = None,
    verbose      : bool  = True,
) -> List[float]:
    """
    Détecte les zéros sur [t_min, t_max].

    Étape 1 : Z_batch (GPU/CPU) pour détecter les changements de signe.
    Étape 2 : Illinois mpmath (CPU) pour affiner chaque zéro à tol_affinage.
    """
    from mpmath import mp, findroot

    mp_save = mp.dps
    zeros   = []
    t_grid  = np.arange(t_min, t_max + step, step, dtype=np.float64)
    n_total = len(t_grid)

    if bloc is None:
        bloc = 100_000 if _GPU_DISPONIBLE else 5_000

    if verbose:
        print(f"  Scanner [{t_min:.1f}, {t_max:.1f}]"
              f"  step={step}  {n_total} pts  mode={mode_actif()}"
              f"  bloc={bloc}")

    for i0 in range(0, n_total - 1, bloc):
        i1      = min(i0 + bloc + 1, n_total)
        ts_b    = t_grid[i0:i1]
        Z_b     = Z_batch(ts_b, avec_reste=True)

        signes   = np.sign(Z_b)
        passages = np.where(np.diff(signes) != 0)[0]

        for idx in passages:
            t_a, t_b = float(ts_b[idx]), float(ts_b[idx + 1])
            mp.dps = dps_affinage
            try:
                t0 = findroot(
                    lambda x: Z_fast(float(x), dps=dps_affinage),
                    (t_a, t_b),
                    solver="illinois",
                    tol=tol_affinage,
                    maxsteps=80,
                )
                zeros.append(float(t0))
                if verbose:
                    print(f"    ✅ Zéro #{len(zeros):5d} : t = {float(t0):.12f}")
            except Exception as e:
                if verbose:
                    print(f"    ⚠️  [{t_a:.4f}, {t_b:.4f}] : {e}")

    mp.dps = mp_save
    if verbose:
        print(f"  → {len(zeros)} zéros trouvés")
    return zeros


# ─── Section 6 — Benchmark CPU vs GPU ────────────────────────────────────────

def benchmark(
    t_start: float = 200.0,
    t_end  : float = 3000.0,
    step   : float = 0.1,
):
    """Compare scalaire vs CPU batch vs GPU batch."""
    # Z_RS scalaire defini localement pour eviter la dependance a riemann_siegel.py
    def Z_RS(t):
        tau = math.sqrt(t / _TWO_PI); N = int(tau)
        th  = theta_asymptotique(t) if t >= 20.0 else theta_exact(t)
        ns  = np.arange(1, N+1, dtype=np.float64)
        Z   = 2.0*float(np.sum(np.cos(th - t*np.log(ns))/np.sqrt(ns)))
        u   = 2*(tau-N)-1; d = math.cos(math.pi*u)
        psi = math.cos(math.pi*(u*u/2+0.375))/d if abs(d)>1e-10 else 0.0
        return Z + (-1)**(N-1)*(tau**-0.5)*psi

    ts = np.arange(t_start, t_end, step, dtype=np.float64)
    n  = len(ts)
    print(f"\n{'─'*65}")
    print(f"  Benchmark — {n} points [{t_start:.0f}, {t_end:.0f}]"
          f"  mode={mode_actif()}")
    print(f"{'─'*65}")

    # Scalaire (2000 pts extrapolés)
    n_sc  = min(n, 2000)
    debut = time.perf_counter()
    Z_sc  = np.array([Z_RS(t) for t in ts[:n_sc]])
    dt_sc = (time.perf_counter() - debut) * n / n_sc
    print(f"  Z_RS scalaire    : {dt_sc:.1f}s (extrapolé sur {n} pts)")

    # CPU batch forcé
    global _GPU_DISPONIBLE
    gpu_bak = _GPU_DISPONIBLE; _GPU_DISPONIBLE = False
    debut   = time.perf_counter()
    Z_cpu   = Z_batch(ts)
    dt_cpu  = time.perf_counter() - debut
    _GPU_DISPONIBLE = gpu_bak
    print(f"  Z_batch CPU      : {dt_cpu:.2f}s  ({n/dt_cpu:.0f} pts/s)"
          f"  ×{dt_sc/dt_cpu:.1f} vs scalaire")

    # GPU batch (si dispo)
    if _GPU_DISPONIBLE:
        debut  = time.perf_counter()
        Z_gpu  = Z_batch(ts)
        dt_gpu = time.perf_counter() - debut
        acc    = int(np.sum(np.sign(Z_gpu) == np.sign(Z_cpu)))
        print(f"  Z_batch GPU      : {dt_gpu:.2f}s  ({n/dt_gpu:.0f} pts/s)"
              f"  ×{dt_sc/dt_gpu:.1f} vs scalaire"
              f"  ×{dt_cpu/dt_gpu:.1f} vs CPU")
        print(f"  Accord GPU/CPU   : {acc}/{n} ({100*acc/n:.2f}%)")
    else:
        print(f"  GPU              : non disponible (CuPy absent)")

    acc2 = int(np.sum(np.sign(Z_cpu[:n_sc]) == np.sign(Z_sc)))
    print(f"  Accord CPU/scal  : {acc2}/{n_sc} ({100*acc2/n_sc:.2f}%)")
    print(f"{'─'*65}\n")


# ─── Section 7 — Point d'entrée ──────────────────────────────────────────────

if __name__ == "__main__":
    print("─── Test riemann_siegel_batch.py ───")
    print(f"    Mode actif : {mode_actif()}\n")

    # Vérification aux zéros LMFDB
    zeros_ref = [
        14.134725141734693, 21.022039638771555, 25.010857580145688,
        30.424876125859513, 32.935061587739189, 37.586178158825671,
    ]
    ts_ref = np.array(zeros_ref)
    Z_b    = Z_batch(ts_ref)
    print("  Z_batch aux zéros LMFDB (doit être ≈ 0) :")
    print(f"  {'t':>22}  {'Z_batch':>14}")
    print("  " + "─" * 40)
    for t, z in zip(zeros_ref, Z_b):
        print(f"  {t:>22.12f}  {z:>14.4e}")

    # Benchmark
    benchmark(t_start=200.0, t_end=3000.0, step=0.1)

    # Scanner test
    print("  Scanner batch sur [14, 100] :")
    trouves = scanner_batch(14.0, 100.0, step=0.1, verbose=True)
    print(f"\n  {len(trouves)} zéros dans [14, 100]  (attendus : 29)")
