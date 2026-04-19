#!/usr/bin/env python3
"""
Point d'entrée principal du projet Zêta
Orchestre tous les modules : calculs, IA, visualisation, monitoring
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

import sys
from pathlib import Path

# Ajouter src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from calculs.zeros_finder import compute_zeros_pipeline
from calculs.verification import compare_with_lmfdb
from visualisation.plots import plot_zeros_distribution
from monitoring.logger_config import setup_logger
from utils.config_loader import load_config

def main():
    # Configuration
    config = load_config("~/projet_zeta/config/zeros_config.yaml")
    logger = setup_logger(config)
    
    logger.info("🚀 Lancement du pipeline complet")
    
    # Étape 1 : Calcul des zéros
    zeros = compute_zeros_pipeline(config)
    
    # Étape 2 : Vérification
    comparison = compare_with_lmfdb(zeros)
    
    # Étape 3 : Visualisation
    plot_zeros_distribution(zeros, comparison)
    
    logger.info("✅ Pipeline terminé")

if __name__ == "__main__":
    main()
