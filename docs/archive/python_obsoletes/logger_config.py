#!/usr/bin/env python3
"""
Configuration du logger pour le projet Zêta.
AUTEUR : hprzeta
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(config: dict) -> logging.Logger:
    """
    Configure et retourne le logger principal du projet.
    Sortie : console + fichier logs/zeta_YYYYMMDD.log
    """
    log_dir  = Path(config.get("log_dir", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    log_level = getattr(logging, config.get("log_level", "INFO").upper(), logging.INFO)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file  = log_dir / f"zeta_{timestamp}.log"

    # Format
    fmt = logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler console
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    console.setFormatter(fmt)

    # Handler fichier
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # toujours tout dans le fichier
    file_handler.setFormatter(fmt)

    # Logger racine du projet
    logger = logging.getLogger("zeta")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)
    logger.addHandler(file_handler)
    logger.propagate = False

    logger.info(f"Logger initialisé — fichier : {log_file}")
    return logger
