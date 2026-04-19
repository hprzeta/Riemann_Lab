#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère les graphiques de distribution
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

def plot_zeros_distribution(zeros: list, comparison=None):
    """Génère les graphiques de distribution"""
    import matplotlib.pyplot as plt
    import numpy as np
    from loguru import logger
    
    if len(zeros) < 2:
        logger.warning("Pas assez de zéros pour générer les graphiques")
        return
    
    gaps = np.diff(zeros)
    plt.figure(figsize=(10, 6))
    plt.hist(gaps, bins=50, edgecolor='black')
    plt.xlabel("Écart entre zéros consécutifs Δt")
    plt.ylabel("Fréquence")
    plt.title(f"Distribution des écarts – {len(zeros)} zéros")
    plt.savefig("/mnt/data/exports/figures/zeros_distribution.png", dpi=150)
    plt.show()
