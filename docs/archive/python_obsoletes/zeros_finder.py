#!/usr/bin/env python3
"""
Module de calcul des zéros non triviaux de ζ(s)
Méthode : fonction Z de Hardy + affinage Newton-Raphson (Illinois)
AUTEUR : hprzeta
"""

import csv
import logging
from pathlib import Path
from datetime import datetime

import mpmath

logger = logging.getLogger(__name__)


def setup_mpmath(dps: int) -> None:
    """Configure la précision mpmath."""
    mpmath.mp.dps = dps
    logger.info(f"Précision mpmath : {dps} décimales")


def Z(t):
    """Fonction Z de Hardy : Z(t) = e^{iθ(t)} ζ(1/2 + it), réelle sur ℝ."""
    return mpmath.siegelz(t)


def find_sign_changes(t_min: float, t_max: float, step: float) -> list:
    """
    Recherche grossière des changements de signe de Z(t).
    Retourne les intervalles [t_a, t_b] contenant un zéro.
    """
    intervals = []
    t = t_min
    z_prev = Z(t)
    count = 0

    while t < t_max:
        t_next = t + step
        z_curr = Z(t_next)
        if z_prev * z_curr < 0:
            intervals.append((t, t_next))
        z_prev = z_curr
        t = t_next
        count += 1
        if count % 500 == 0:
            logger.debug(f"Scan : t={t:.1f}, intervalles trouvés={len(intervals)}")

    logger.info(f"Recherche grossière terminée : {len(intervals)} intervalles trouvés")
    return intervals


def refine_zero_illinois(t_a: float, t_b: float, tol: float = 1e-12) -> float | None:
    """
    Affinage par méthode Illinois (variante de regula falsi).
    Retourne t* tel que Z(t*) ≈ 0, ou None si non convergé.
    """
    fa, fb = Z(t_a), Z(t_b)
    if fa * fb > 0:
        return None

    for _ in range(100):
        t_c = t_b - fb * (t_b - t_a) / (fb - fa)
        fc = Z(t_c)

        if abs(fc) < tol:
            return float(t_c)

        if fc * fb < 0:
            t_a, fa = t_b, fb
            fb = fb / 2  # correction Illinois
        else:
            t_b, fb = t_c, fc
            fa = fa / 2

        t_b = t_c
        fb = fc

        if abs(t_b - t_a) < tol:
            return float((t_a + t_b) / 2)

    return None


def verify_zero(t: float, epsilon: float = 1e-9) -> bool:
    """Vérifie que |ζ(1/2 + it)| < epsilon."""
    s = mpmath.mpc("0.5", str(t))
    val = abs(mpmath.zeta(s))
    return float(val) < epsilon


def save_zeros_csv(zeros: list, output_path: Path) -> None:
    """Sauvegarde les zéros en CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "t", "zeta_abs", "verified"])
        for i, entry in enumerate(zeros, 1):
            writer.writerow([
                i,
                f"{entry['t']:.12f}",
                f"{entry['zeta_abs']:.2e}",
                entry["verified"]
            ])
    logger.info(f"Zéros sauvegardés → {output_path} ({len(zeros)} entrées)")


def compute_zeros_pipeline(config: dict) -> list:
    """
    Pipeline complet de calcul des zéros.
    Retourne la liste des zéros validés.
    """
    # Paramètres depuis config
    dps       = config.get("dps", 30)
    t_min     = config.get("t_min", 14.0)
    t_max     = config.get("t_max", 1000.0)
    step      = config.get("step", 0.1)
    tol       = config.get("tol", 1e-12)
    epsilon   = config.get("epsilon", 1e-9)
    n_max     = config.get("n_zeros", 1000)
    csv_out   = Path(config.get("csv_output", "csv/zeros_computed.csv"))

    setup_mpmath(dps)
    logger.info(f"Pipeline : t ∈ [{t_min}, {t_max}], step={step}, dps={dps}")

    # Étape 1 : recherche grossière
    intervals = find_sign_changes(t_min, t_max, step)

    # Étape 2 : affinage + vérification
    zeros = []
    for t_a, t_b in intervals:
        if len(zeros) >= n_max:
            break
        t_star = refine_zero_illinois(t_a, t_b, tol)
        if t_star is None:
            continue

        s = mpmath.mpc("0.5", str(t_star))
        zeta_abs = float(abs(mpmath.zeta(s)))
        verified = zeta_abs < epsilon

        zeros.append({
            "t": t_star,
            "zeta_abs": zeta_abs,
            "verified": verified
        })

        if len(zeros) % 100 == 0:
            logger.info(f"Zéros trouvés : {len(zeros)}")

    valid = [z for z in zeros if z["verified"]]
    logger.info(f"Zéros validés : {len(valid)} / {len(zeros)}")

    # Étape 3 : sauvegarde
    save_zeros_csv(valid, csv_out)

    return valid
