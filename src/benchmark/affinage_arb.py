"""
Benchmark : arb_fpwrap_cdouble_hardy_z (Arb/FLINT 3) vs mpmath.siegelz
Mesure le speedup de Z(t) sur 200 valeurs t ∈ [100, 10000].
Utilisé pour évaluer si Arb peut accélérer l'affinage Illinois de compute_zeros_v4_1.py.

Auteur : hprzeta — Riemann_Lab_C
"""

import ctypes
import os
import time
import math
import datetime

import mpmath
import numpy as np

# ─── Paramètres du benchmark ────────────────────────────────────────────────
N_POINTS = 200         # nombre de valeurs t à tester
T_MIN = 100.0
T_MAX = 10000.0
DPS_MPMATH = 35        # précision utilisée dans compute_zeros_v4_1.py
N_ZEROS_TOTAL = 10142  # zéros prévus pour le run complet (référence extrapolation)
N_APPELS_PAR_ZERO = 6  # estimation moyenne d'appels Z(t) par zéro (Illinois)

# ─── Chargement de la libflint bundlée avec python-flint ─────────────────────
_LIBFLINT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../zeta_env/lib/python3.12/site-packages/python_flint.libs/libflint-24205715.so.21.0.0"
)
_LIBFLINT_PATH = os.path.realpath(_LIBFLINT_PATH)

class _CDoubleComplex(ctypes.Structure):
    """Représentation ctypes de complex double C (ABI x86-64 System V)."""
    _fields_ = [("real", ctypes.c_double), ("imag", ctypes.c_double)]

def _load_arb_hardy_z():
    """Charge arb_fpwrap_cdouble_hardy_z depuis libflint et retourne le callable."""
    lib = ctypes.CDLL(_LIBFLINT_PATH)
    fn = lib.arb_fpwrap_cdouble_hardy_z
    fn.restype = ctypes.c_int
    fn.argtypes = [ctypes.POINTER(_CDoubleComplex), _CDoubleComplex, ctypes.c_int]
    return fn

_arb_hardy_z_fn = _load_arb_hardy_z()
_res_buf = _CDoubleComplex(0.0, 0.0)  # buffer réutilisable, évite l'allocation par appel

def arb_hardy_z(t: float) -> float:
    """Z(t) via Arb/FLINT arb_fpwrap_cdouble_hardy_z — précision ~15 dps (double)."""
    t_in = _CDoubleComplex(t, 0.0)
    _arb_hardy_z_fn(ctypes.byref(_res_buf), t_in, 0)
    return _res_buf.real

# ─── Fonctions de mesure ─────────────────────────────────────────────────────

def mesurer_mpmath(valeurs_t: list[float]) -> tuple[list[float], list[float]]:
    """Mesure mpmath.siegelz à dps=35 sur chaque valeur de t."""
    mpmath.mp.dps = DPS_MPMATH
    temps_ms = []
    valeurs_z = []
    for t in valeurs_t:
        debut = time.perf_counter()
        z = float(mpmath.siegelz(t))
        fin = time.perf_counter()
        temps_ms.append((fin - debut) * 1000.0)
        valeurs_z.append(z)
    return temps_ms, valeurs_z

def mesurer_arb(valeurs_t: list[float]) -> tuple[list[float], list[float]]:
    """Mesure arb_fpwrap_cdouble_hardy_z sur chaque valeur de t."""
    temps_ms = []
    valeurs_z = []
    for t in valeurs_t:
        debut = time.perf_counter()
        z = arb_hardy_z(t)
        fin = time.perf_counter()
        temps_ms.append((fin - debut) * 1000.0)
        valeurs_z.append(z)
    return temps_ms, valeurs_z

# ─── Statistiques par tranche ────────────────────────────────────────────────

_TRANCHES = {
    "[100,1000]":    (100.0,  1000.0),
    "(1000,5000]":  (1000.0, 5000.0),
    "(5000,10000]": (5000.0, 10000.0),
}

def stats_tranche(label: str, t_arr, tms_mp, tms_arb):
    """Retourne un dict de stats pour une tranche de valeurs t."""
    t_lo, t_hi = _TRANCHES[label]
    mask = np.array([t_lo <= t <= t_hi for t in t_arr], dtype=bool)
    if mask.sum() == 0:
        return None
    mp_sel = np.array(tms_mp)[mask]
    arb_sel = np.array(tms_arb)[mask]
    speedup = np.mean(mp_sel) / np.mean(arb_sel) if np.mean(arb_sel) > 0 else 0.0
    return {
        "n": int(mask.sum()),
        "mp_mean_ms": float(np.mean(mp_sel)),
        "arb_mean_ms": float(np.mean(arb_sel)),
        "speedup": speedup,
    }

# ─── Extrapolation T_total ────────────────────────────────────────────────────

def extrapoler_t_total(temps_moyen_ms: float) -> str:
    """Convertit temps/appel moyen en durée totale estimée pour 10142 zéros."""
    t_total_s = temps_moyen_ms / 1000.0 * N_APPELS_PAR_ZERO * N_ZEROS_TOTAL
    heures = t_total_s / 3600.0
    if heures >= 1.0:
        return f"~{heures:.1f}h"
    return f"~{t_total_s/60:.0f}min"

# ─── Programme principal ─────────────────────────────────────────────────────

def main():
    # Génération des 200 points — espacement log pour couvrir [100, 10000]
    valeurs_t = list(np.logspace(math.log10(T_MIN), math.log10(T_MAX), N_POINTS))

    print(f"=== Benchmark Arb/FLINT vs mpmath — {N_POINTS} points t ∈ [{T_MIN:.0f}, {T_MAX:.0f}] ===")
    print(f"Précision mpmath : dps={DPS_MPMATH}   |   Arb : double (~15 dps)")
    print()

    # Passe de chauffe (évite la latence de premier appel)
    print("Chauffe mpmath...")
    mpmath.mp.dps = DPS_MPMATH
    _ = float(mpmath.siegelz(100.0))
    print("Chauffe Arb...")
    _ = arb_hardy_z(100.0)

    print(f"Mesure mpmath sur {N_POINTS} points...")
    tms_mp, vals_mp = mesurer_mpmath(valeurs_t)

    print(f"Mesure Arb sur {N_POINTS} points...")
    tms_arb, vals_arb = mesurer_arb(valeurs_t)

    # ─── Calcul des métriques globales ───────────────────────────────────────
    mp_mean = float(np.mean(tms_mp))
    arb_mean = float(np.mean(tms_arb))
    speedup_global = mp_mean / arb_mean if arb_mean > 0 else 0.0

    erreurs = [abs(vm - va) for vm, va in zip(vals_mp, vals_arb)]
    erreur_max = max(erreurs)
    erreur_moy = sum(erreurs) / len(erreurs)

    # ─── Extrapolations ──────────────────────────────────────────────────────
    t_tot_mp = extrapoler_t_total(mp_mean)
    t_tot_arb = extrapoler_t_total(arb_mean)

    # ─── Statistiques par tranche ────────────────────────────────────────────
    tranches_labels = ["[100,1000]", "(1000,5000]", "(5000,10000]"]
    tranches_stats = {}
    for label in tranches_labels:
        st = stats_tranche(label, valeurs_t, tms_mp, tms_arb)
        if st:
            tranches_stats[label] = st

    # ─── Affichage tableau récapitulatif ─────────────────────────────────────
    print()
    print("┌─────────────────────────────────────────────────────────────────────────────┐")
    print("│            RÉSUMÉ — Arb/FLINT vs mpmath.siegelz                            │")
    print("├──────────┬───────────┬──────────────────┬──────────┬─────────────────────────┤")
    print("│ Méthode  │ t moyen   │ temps/appel (ms) │ speedup  │ T_total estimé          │")
    print("├──────────┼───────────┼──────────────────┼──────────┼─────────────────────────┤")
    t_moy = float(np.mean(valeurs_t))
    print(f"│ mpmath   │ {t_moy:9.1f} │ {mp_mean:16.4f} │ 1.00×    │ {t_tot_mp:<23s} │")
    print(f"│ Arb      │ {t_moy:9.1f} │ {arb_mean:16.4f} │ {speedup_global:6.2f}×   │ {t_tot_arb:<23s} │")
    print("└──────────┴───────────┴──────────────────┴──────────┴─────────────────────────┘")
    print()

    print("Speedup par tranche :")
    print(f"  {'Tranche':<15} {'n':>4} {'mpmath ms':>12} {'Arb ms':>10} {'speedup':>10}")
    print(f"  {'-'*15} {'-'*4} {'-'*12} {'-'*10} {'-'*10}")
    for label, st in tranches_stats.items():
        print(f"  {label:<15} {st['n']:>4} {st['mp_mean_ms']:>12.4f} {st['arb_mean_ms']:>10.4f} {st['speedup']:>9.2f}×")
    print()

    print(f"Erreur max  |Z_mpmath - Z_arb| : {erreur_max:.3e}  (machine eps = 2.2e-16)")
    print(f"Erreur moy  |Z_mpmath - Z_arb| : {erreur_moy:.3e}")
    print()

    # ─── Sauvegarde dans logs/ ───────────────────────────────────────────────
    horodatage = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"benchmark_arb_vs_mpmath_{horodatage}.log")

    with open(log_path, "w") as f:
        f.write(f"# Benchmark Arb/FLINT vs mpmath — {horodatage}\n")
        f.write(f"# N_POINTS={N_POINTS}, T_MIN={T_MIN}, T_MAX={T_MAX}, DPS_MPMATH={DPS_MPMATH}\n")
        f.write(f"# mpmath_mean_ms={mp_mean:.6f}, arb_mean_ms={arb_mean:.6f}\n")
        f.write(f"# speedup_global={speedup_global:.4f}\n")
        f.write(f"# erreur_max={erreur_max:.3e}, erreur_moy={erreur_moy:.3e}\n")
        f.write(f"# t_total_mpmath={t_tot_mp}, t_total_arb={t_tot_arb}\n")
        f.write("# t | tms_mp | tms_arb | Z_mpmath | Z_arb | erreur\n")
        for i, t in enumerate(valeurs_t):
            f.write(f"{t:.6f}\t{tms_mp[i]:.6f}\t{tms_arb[i]:.6f}\t"
                    f"{vals_mp[i]:.15e}\t{vals_arb[i]:.15e}\t{erreurs[i]:.3e}\n")

    print(f"Résultats sauvegardés : {log_path}")

if __name__ == "__main__":
    main()
