#!/usr/bin/env python3
"""
Module de vérification des zéros contre la base LMFDB.
API publique : https://www.lmfdb.org/api/zeros/zeta/
AUTEUR : hprzeta
"""

import logging
import time
import csv
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

LMFDB_API = "https://www.lmfdb.org/api/zeros/zeta/"
TOLERANCE = 1e-6  # tolérance pour correspondance t


def fetch_lmfdb_zeros(t_min: float, t_max: float) -> list[float]:
    """
    Interroge l'API LMFDB pour récupérer les zéros dans [t_min, t_max].
    Retourne une liste de valeurs t.
    """
    params = {
        "t": f"{t_min}-{t_max}",
        "_format": "json",
        "_fields": "t",
        "_limit": 2000,
    }
    try:
        resp = requests.get(LMFDB_API, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        zeros = [float(entry["t"]) for entry in data.get("data", [])]
        logger.info(f"LMFDB : {len(zeros)} zéros récupérés dans [{t_min:.1f}, {t_max:.1f}]")
        return zeros
    except requests.RequestException as e:
        logger.warning(f"LMFDB inaccessible : {e} — comparaison ignorée")
        return []


def match_zero(t_computed: float, lmfdb_zeros: list[float], tol: float = TOLERANCE) -> float | None:
    """
    Cherche le zéro LMFDB le plus proche de t_computed.
    Retourne t_lmfdb si |t_computed - t_lmfdb| < tol, sinon None.
    """
    if not lmfdb_zeros:
        return None
    closest = min(lmfdb_zeros, key=lambda t: abs(t - t_computed))
    if abs(closest - t_computed) < tol:
        return closest
    return None


def compare_with_lmfdb(zeros: list[dict]) -> dict:
    """
    Compare les zéros calculés avec la base LMFDB.

    Retourne un dict :
    {
        "matched": [...],       # zéros présents dans LMFDB
        "unmatched": [...],     # zéros non trouvés dans LMFDB
        "missing": [...],       # zéros LMFDB non trouvés par le calcul
        "stats": { ... }
    }
    """
    if not zeros:
        logger.warning("Aucun zéro à comparer")
        return {"matched": [], "unmatched": [], "missing": [], "stats": {}}

    t_values = [z["t"] for z in zeros]
    t_min = min(t_values) - 1.0
    t_max = max(t_values) + 1.0

    # Récupération LMFDB (par tranches pour éviter timeout)
    lmfdb_zeros = []
    chunk = 200.0
    t = t_min
    while t < t_max:
        lmfdb_zeros += fetch_lmfdb_zeros(t, min(t + chunk, t_max))
        t += chunk
        time.sleep(0.3)  # respecter l'API

    lmfdb_set = set(lmfdb_zeros)

    matched   = []
    unmatched = []

    for z in zeros:
        ref = match_zero(z["t"], lmfdb_zeros)
        entry = {**z, "lmfdb_t": ref, "delta": abs(z["t"] - ref) if ref else None}
        if ref is not None:
            matched.append(entry)
        else:
            unmatched.append(entry)

    # Zéros LMFDB manqués par notre calcul
    computed_set = set(round(z["t"], 4) for z in zeros)
    missing = [t for t in lmfdb_zeros if round(t, 4) not in computed_set]

    stats = {
        "computed_total": len(zeros),
        "lmfdb_total": len(lmfdb_zeros),
        "matched": len(matched),
        "unmatched": len(unmatched),
        "missing": len(missing),
        "match_rate": len(matched) / len(zeros) * 100 if zeros else 0,
    }

    logger.info(
        f"Comparaison LMFDB : {stats['matched']}/{stats['computed_total']} "
        f"correspondances ({stats['match_rate']:.1f}%)"
    )

    return {
        "matched": matched,
        "unmatched": unmatched,
        "missing": missing,
        "stats": stats,
    }
