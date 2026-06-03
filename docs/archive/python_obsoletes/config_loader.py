#!/usr/bin/env python3
"""
Chargement de la configuration depuis un fichier YAML.
AUTEUR : hprzeta
"""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

DEFAULTS = {
    # Précision
    "dps": 30,
    # Plage de recherche
    "t_min": 14.0,
    "t_max": 1000.0,
    "step": 0.1,
    # Affinage
    "tol": 1e-12,
    "epsilon": 1e-9,
    # Nombre max de zéros
    "n_zeros": 1000,
    # Sorties
    "csv_output": "csv/zeros_computed.csv",
    "log_dir": "logs",
    "log_level": "INFO",
}


def load_config(config_path: str | Path) -> dict:
    """
    Charge la configuration depuis un fichier YAML.
    Les valeurs manquantes sont complétées par DEFAULTS.
    Retourne un dict prêt à l'emploi.
    """
    path = Path(config_path).expanduser().resolve()

    if not path.exists():
        logger.warning(f"Config introuvable : {path} — utilisation des valeurs par défaut")
        return dict(DEFAULTS)

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Fusion : defaults + fichier (le fichier prime)
    config = {**DEFAULTS, **data}
    logger.info(f"Configuration chargée depuis {path}")
    return config
