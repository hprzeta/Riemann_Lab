#!/usr/bin/env python3
# -*- coding: utf-8 -*-v#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calcul haute précision des zéros non triviaux de ζ(s) sur la droite critique
Méthode : Riemann-Siegel via mpmath + affinage Newton
Monitoring : loguru + tqdm + memory_profiler
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

import sys
import time
import yaml
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import psutil

# Bibliothèques scientifiques
from mpmath import mp, zeta, diff, findroot
from tqdm import tqdm
from loguru import logger
import pandas as pd
import matplotlib.pyplot as plt

# Configuration des logs
logger.remove()
logger.add(
    "/mnt/data/logs/zeros_zeta.log",
    rotation="100 MB",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}",
    level="DEBUG"
)
logger.add(sys.stderr, level="INFO")

# Configuration de la précision
mp.dps = 50  # 50 décimales (haute précision)
mp.pretty = True

def load_config(config_path: str = "~/projet_zeta/config/zeros_config.yaml") -> dict:
    """Charge la configuration YAML"""
    config_file = Path(config_path).expanduser()
    if config_file.exists():
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Configuration par défaut
        default_config = {
            "T_max": 1000.0,           # Recherche jusqu'à t = 1000
            "step": 0.1,               # Pas initial de recherche
            "tol": 1e-12,              # Tolérance Newton
            "max_iter": 50,            # Max itérations Newton
            "expected_zeros": 1000,    # Nombre attendu (théorique ~ T/(2π) log(T/(2πe)))
            "lmfdb_check": True,       # Vérifier avec LMFDB
            "save_csv": True,
            "save_plots": True
        }
        # Créer le répertoire config s'il n'existe pas
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            yaml.dump(default_config, f)
        logger.info(f"Configuration par défaut créée dans {config_file}")
        return default_config

def Z_function(t: float) -> float:
    """
    Fonction Z de Riemann (version réelle sur la droite critique)
    Z(t) = exp(i θ(t)) * ζ(0.5 + i t)
    où θ(t) = Im(log Γ(1/4 + i t/2)) - (t/2) log π
    """
    return zeta(0.5 + 1j * t) * mp.exp(1j * theta(t)).real

def theta(t: float) -> float:
    """Fonction theta de Riemann (phase)"""
    from mpmath import loggamma, pi
    return mp.im(loggamma(0.25 + 0.5j * t)) - 0.5 * t * mp.log(pi)

def find_zero_bracket(t_left: float, t_right: float, tol: float = 1e-12) -> float:
    """
    Trouve le zéro dans l'intervalle [t_left, t_right] par Newton-Raphson
    en utilisant Z(t) et Z'(t) (dérivée numérique)
    """
    def Z_real(t):
        return float(zeta(0.5 + 1j * t).real)
    
    try:
        # Utilisation de findroot de mpmath
        zero = findroot(lambda t: zeta(0.5 + 1j * t), (t_left + t_right)/2, 
                        solver='newton', tol=tol, maxsteps=50)
        return float(zero)
    except Exception as e:
        logger.warning(f"Newton a échoué sur [{t_left}, {t_right}] : {e}")
        # Fallback : bissection sur Z(t)
        from mpmath import findroot as bisect_root
        try:
            zero = findroot(lambda t: zeta(0.5 + 1j * t).real, 
                           (t_left, t_right), solver='bisect', tol=tol)
            return float(zero)
        except:
            return None

def monitor_resources():
    """Capture les métriques système pour le log"""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    return {
        "cpu": cpu_percent,
        "ram_used_gb": mem.used / 1e9,
        "ram_percent": mem.percent
    }

def compute_zeros(T_max: float, step: float, tol: float) -> List[float]:
    """
    Algorithme principal : détection + affinage
    Retourne la liste des parties imaginaires des zéros
    """
    zeros = []
    t = 10.0  # On commence après les premiers zéros (le premier est ~14.13)
    
    # Valeur initiale de Z(t)
    Z_prev = Z_function(t)
    
    # Barre de progression
    n_steps = int((T_max - t) / step)
    pbar = tqdm(total=n_steps, desc="Recherche des zéros", unit="step")
    
    while t < T_max:
        t += step
        Z_curr = Z_function(t)
        
        # Détection de changement de signe
        if Z_prev * Z_curr < 0:
            logger.debug(f"Changement de signe détecté entre {t-step:.2f} et {t:.2f}")
            
            # Affinage
            zero = find_zero_bracket(t-step, t, tol)
            if zero is not None:
                # Vérification finale
                zeta_value = zeta(0.5 + 1j * zero)
                if abs(zeta_value) < 1e-10:
                    zeros.append(zero)
                    logger.info(f"✅ Zéro trouvé : t = {zero:.10f} | ζ = {abs(zeta_value):.2e}")
                    
                    # Sauvegarde périodique (tous les 100 zéros)
                    if len(zeros) % 100 == 0:
                        save_intermediate_results(zeros)
                        log_resources()
                else:
                    logger.warning(f"⚠️ Faux positif : t={zero:.6f} | ζ={abs(zeta_value):.2e}")
        
        Z_prev = Z_curr
        pbar.update(1)
        
        # Monitoring périodique
        if int(t) % 50 == 0 and t > 0:
            log_resources()
    
    pbar.close()
    return zeros

def save_intermediate_results(zeros: List[float]):
    """Sauvegarde temporaire en CSV"""
    df = pd.DataFrame({
        "n": range(1, len(zeros) + 1),
        "imaginary_part": zeros,
        "computed_at": datetime.now().isoformat()
    })
    csv_path = Path("/mnt/data/exports/csv/zeros_intermediaire.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    logger.info(f"Sauvegarde intermédiaire : {len(zeros)} zéros dans {csv_path}")

def log_resources():
    """Enregistre les métriques dans le log"""
    metrics = monitor_resources()
    logger.info(f"📊 CPU: {metrics['cpu']:.1f}% | RAM: {metrics['ram_used_gb']:.1f}/{metrics['ram_percent']:.0f}%")

def compare_with_lmfdb(zeros: List[float]) -> pd.DataFrame:
    """
    Compare les zéros calculés avec la base LMFDB (via fichier local ou API)
    Retourne un DataFrame avec les écarts
    """
    # Fichier de référence LMFDB (à télécharger une fois)
    lmfdb_file = Path("/mnt/data/datasets/references/lmfdb_zeros_first_1000.csv")
    
    if not lmfdb_file.exists():
        logger.warning("Fichier LMFDB non trouvé. Téléchargement...")
        import urllib.request
        lmfdb_file.parent.mkdir(parents=True, exist_ok=True)
        url = "https://raw.githubusercontent.com/Deskuma/riemann-hypothesis-ai/main/data/zeros1000.csv"
        try:
            urllib.request.urlretrieve(url, lmfdb_file)
            logger.info(f"Fichier LMFDB téléchargé : {lmfdb_file}")
        except:
            logger.error("Impossible de télécharger LMFDB. Vérification ignorée.")
            return pd.DataFrame()
    
    lmfdb_df = pd.read_csv(lmfdb_file)
    lmfdb_zeros = lmfdb_df.iloc[:len(zeros), 0].values  # Première colonne = parties imaginaires
    
    # Comparaison
    min_len = min(len(zeros), len(lmfdb_zeros))
    comparison = pd.DataFrame({
        "n": range(1, min_len + 1),
        "zero_calcule": zeros[:min_len],
        "zero_lmfdb": lmfdb_zeros[:min_len],
        "ecart_absolu": np.abs(np.array(zeros[:min_len]) - lmfdb_zeros[:min_len]),
        "ecart_relatif": np.abs(np.array(zeros[:min_len]) - lmfdb_zeros[:min_len]) / lmfdb_zeros[:min_len] * 100
    })
    
    logger.info(f"📊 Comparaison LMFDB : écart moyen = {comparison['ecart_absolu'].mean():.2e}")
    return comparison

def plot_zeros(zeros: List[float], comparison: pd.DataFrame = None):
    """Génère les visualisations"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Graphique 1 : Distribution des écarts entre zéros consécutifs
    gaps = np.diff(zeros)
    axes[0].hist(gaps, bins=50, edgecolor='black', alpha=0.7)
    axes[0].set_xlabel("Écart entre zéros consécutifs Δt")
    axes[0].set_ylabel("Fréquence")
    axes[0].set_title(f"Distribution des écarts – {len(zeros)} zéros")
    axes[0].axvline(np.mean(gaps), color='r', linestyle='--', label=f"Moyenne = {np.mean(gaps):.4f}")
    axes[0].legend()
    
    # Graphique 2 : Évolution des écarts (montgomery pair correlation)
    axes[1].plot(range(2, len(zeros)), gaps[1:], 'b.', alpha=0.5, markersize=2)
    axes[1].set_xlabel("Rang du zéro n")
    axes[1].set_ylabel("Écart Δt")
    axes[1].set_title("Écarts consécutifs en fonction du rang")
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Sauvegarde
    plot_path = Path("/mnt/data/exports/figures/zeros_distribution.png")
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(plot_path, dpi=150)
    logger.info(f"📈 Graphique sauvegardé : {plot_path}")
    plt.show()

def main():
    """Fonction principale orchestrant tout le workflow"""
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("🚀 DÉBUT DU CALCUL DES ZÉROS NON TRIVIAUX DE ζ(s)")
    logger.info("=" * 60)
    
    # 1. Chargement config
    config = load_config()
    T_max = config["T_max"]
    step = config["step"]
    tol = config["tol"]
    
    logger.info(f"Paramètres : T_max={T_max}, step={step}, tol={tol}")
    log_resources()
    
    # 2. Calcul des zéros
    zeros = compute_zeros(T_max, step, tol)
    
    # 3. Sauvegarde finale
    df_zeros = pd.DataFrame({
        "n": range(1, len(zeros) + 1),
        "imaginary_part": zeros,
        "algorithm": "Riemann-Siegel + Newton",
        "precision_dps": mp.dps
    })
    csv_final = Path("/mnt/data/exports/csv/zeros_zeta_final.csv")
    df_zeros.to_csv(csv_final, index=False)
    logger.info(f"💾 Sauvegarde finale : {len(zeros)} zéros dans {csv_final}")
    
    # 4. Vérification LMFDB (si demandé)
    comparison = None
    if config["lmfdb_check"]:
        comparison = compare_with_lmfdb(zeros)
        if not comparison.empty:
            comp_path = Path("/mnt/data/exports/csv/comparaison_lmfdb.csv")
            comparison.to_csv(comp_path, index=False)
            logger.info(f"📊 Comparaison sauvegardée : {comp_path}")
    
    # 5. Graphiques
    if config["save_plots"]:
        plot_zeros(zeros, comparison)
    
    # 6. Rapport final
    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"✅ CALCUL TERMINÉ")
    logger.info(f"📌 {len(zeros)} zéros trouvés sur [10, {T_max}]")
    logger.info(f"⏱️ Temps écoulé : {elapsed/60:.2f} minutes")
    logger.info(f"🎯 Taux : {len(zeros)/T_max:.2f} zéros par unité t")
    
    # Estimation théorique de Riemann-von Mangoldt
    theoretical = T_max/(2*np.pi) * np.log(T_max/(2*np.pi*np.e))
    logger.info(f"📐 Estimation théorique : ~{theoretical:.0f} zéros")
    logger.info("=" * 60)
    
    log_resources()

if __name__ == "__main__":
    main()
"""
Created on Sat Apr 18 17:06:36 2026

@author: riemann
"""

