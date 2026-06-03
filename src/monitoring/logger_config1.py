"""
Configuration centralisée des logs
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

import sys
from loguru import logger
from pathlib import Path

def setup_logger(config: dict = None) -> logger:
    """Configure loguru pour tout le projet"""
    logger.remove()  # Enlever handler par défaut
    
    # Log dans fichier
    log_path = Path("/mnt/data/logs/projet_zeta.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_path,
        rotation="100 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}",
        level="DEBUG"
    )
    
    # Log dans console (niveau INFO uniquement)
    logger.add(sys.stderr, level="INFO")
    
    logger.info("Logger initialisé")
    return logger
