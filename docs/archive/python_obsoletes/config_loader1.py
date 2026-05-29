"""
Gestionnaire de configuration centralisé
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

import yaml
from pathlib import Path
from loguru import logger

def load_config(config_path: str) -> dict:
    """Charge la configuration YAML avec valeurs par défaut"""
    config_file = Path(config_path).expanduser()
    
    default_config = {
        "T_max": 1000.0,
        "step": 0.1,
        "tol": 1e-12,
        "precision": 50,
        "lmfdb_check": True,
        "save_csv": True,
        "save_plots": True,
        "monitoring_interval": 30
    }
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            user_config = yaml.safe_load(f)
            default_config.update(user_config)
            logger.info(f"Configuration chargée depuis {config_file}")
    else:
        logger.warning(f"Fichier {config_file} non trouvé, utilisation des valeurs par défaut")
    
    return default_config
