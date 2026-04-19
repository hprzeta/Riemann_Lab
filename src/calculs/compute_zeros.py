#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calcul haute précision des zéros non triviaux de ζ(s) sur la droite critique
Version corrigée - gestion des types mpc et mpf
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

import sys
import time
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Bibliothèques scientifiques
from mpmath import mp, zeta, findroot
from tqdm import tqdm
from loguru import logger
import pandas as pd
import matplotlib.pyplot as plt
import psutil

# Configuration des logs
logger.remove()
logger.add(
    "/mnt/data/logs/zeros_zeta.log",
    rotation="100 MB",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="DEBUG"
)
logger.add(sys.stderr, level="INFO")

# Configuration de la précision
mp.dps = 50
mp.pretty = True


def Z_function(t: float) -> float:
    """Retourne la partie réelle de ζ(0.5 + i*t)"""
    s = 0.5 + 1j * t
    zeta_val = zeta(s)
    return float(zeta_val.real)


def find_zero_bracket(t_left: float, t_right: float, tol: float = 1e-12) -> Optional[float]:
    """Trouve le zéro par Newton-Raphson"""
    try:
        def zeta_on_critical(t):
            return zeta(0.5 + 1j * t)
        
        t_mid = (t_left + t_right) / 2
        zero = findroot(zeta_on_critical, t_mid, solver='newton', tol=tol, maxsteps=50)
        return float(zero)
        
    except Exception as e:
        logger.debug(f"Newton échoué sur [{t_left}, {t_right}] : {e}")
        
        try:
            def zeta_real(t):
                return float(zeta(0.5 + 1j * t).real)
            
            zero = findroot(zeta_real, (t_left, t_right), solver='bisect', tol=tol)
            return float(zero)
        except:
            return None


def monitor_resources() -> dict:
    """Capture les métriques système"""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    return {
        "cpu": cpu_percent,
        "ram_used_gb": mem.used / 1e9,
        "ram_percent": mem.percent
    }


def log_resources():
    """Enregistre les métriques"""
    metrics = monitor_resources()
    logger.info(f"📊 CPU: {metrics['cpu']:.1f}% | RAM: {metrics['ram_used_gb']:.1f} GB ({metrics['ram_percent']:.0f}%)")


def save_intermediate_results(zeros: List[float]):
    """Sauvegarde temporaire"""
    df = pd.DataFrame({
        "n": range(1, len(zeros) + 1),
        "imaginary_part": zeros,
        "computed_at": datetime.now().isoformat()
    })
    csv_path = Path("/mnt/data/exports/csv/zeros_intermediaire.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    logger.info(f"💾 Sauvegarde intermédiaire : {len(zeros)} zéros")


def compute_zeros(T_max: float, step: float, tol: float) -> List[float]:
    """Algorithme principal"""
    zeros = []
    t = 10.0
    
    try:
        Z_prev = Z_function(t)
    except Exception as e:
        logger.error(f"Erreur au premier calcul Z({t}) : {e}")
        return zeros
    
    n_steps = int((T_max - t) / step)
    pbar = tqdm(total=n_steps, desc="Recherche des zéros")
    
    while t < T_max:
        t += step
        
        try:
            Z_curr = Z_function(t)
        except Exception as e:
            logger.warning(f"Erreur calcul Z({t:.2f}) : {e}")
            Z_curr = Z_prev
        
        if Z_prev * Z_curr < 0:
            logger.debug(f"Changement de signe entre {t-step:.2f} et {t:.2f}")
            
            zero = find_zero_bracket(t-step, t, tol)
            if zero is not None:
                zeta_value = zeta(0.5 + 1j * zero)
                zeta_abs = float(abs(zeta_value))  # ← CORRECTION ICI
                
                if zeta_abs < 1e-9:
                    zeros.append(zero)
                    logger.info(f"✅ Zéro #{len(zeros)} : t = {zero:.10f} | |ζ| = {zeta_abs:.2e}")
                    
                    if len(zeros) % 100 == 0:
                        save_intermediate_results(zeros)
                        log_resources()
                else:
                    logger.warning(f"⚠️ Faux positif : t={zero:.6f} | |ζ|={zeta_abs:.2e}")
        
        Z_prev = Z_curr
        pbar.update(1)
        
        if int(t) % 100 == 0 and t > 0:
            log_resources()
    
    pbar.close()
    return zeros


def plot_zeros(zeros: List[float]):
    """Génère les visualisations"""
    if len(zeros) < 2:
        logger.warning("Pas assez de zéros pour générer les graphiques")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    gaps = np.diff(zeros)
    axes[0].hist(gaps, bins=50, edgecolor='black', alpha=0.7)
    axes[0].set_xlabel("Écart entre zéros consécutifs Δt")
    axes[0].set_ylabel("Fréquence")
    axes[0].set_title(f"Distribution des écarts – {len(zeros)} zéros")
    axes[0].axvline(np.mean(gaps), color='r', linestyle='--', label=f"Moyenne = {np.mean(gaps):.4f}")
    axes[0].legend()
    
    axes[1].plot(range(2, len(zeros)), gaps[1:], 'b.', alpha=0.5, markersize=2)
    axes[1].set_xlabel("Rang du zéro n")
    axes[1].set_ylabel("Écart Δt")
    axes[1].set_title("Écarts consécutifs en fonction du rang")
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    plot_path = Path("/mnt/data/exports/figures/zeros_distribution.png")
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(plot_path, dpi=150)
    logger.info(f"📈 Graphique sauvegardé : {plot_path}")
    plt.show()


def main():
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("🚀 DÉBUT DU CALCUL DES ZÉROS NON TRIVIAUX DE ζ(s)")
    logger.info("=" * 60)
    
    T_max = 1000.0
    step = 0.1
    tol = 1e-12
    
    logger.info(f"Paramètres : T_max={T_max}, step={step}, tol={tol}")
    log_resources()
    
    zeros = compute_zeros(T_max, step, tol)
    
    if not zeros:
        logger.error("Aucun zéro trouvé !")
        return
    
    # Sauvegarde finale
    df_zeros = pd.DataFrame({
        "n": range(1, len(zeros) + 1),
        "imaginary_part": zeros,
        "algorithm": "Riemann-Siegel + Newton",
        "precision_dps": mp.dps
    })
    csv_final = Path("/mnt/data/exports/csv/zeros_zeta_final.csv")
    csv_final.parent.mkdir(parents=True, exist_ok=True)
    df_zeros.to_csv(csv_final, index=False)
    logger.info(f"💾 Sauvegarde finale : {len(zeros)} zéros dans {csv_final}")
    
    plot_zeros(zeros)
    
    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"✅ CALCUL TERMINÉ")
    logger.info(f"📌 {len(zeros)} zéros trouvés sur [10, {T_max}]")
    logger.info(f"⏱️ Temps écoulé : {elapsed/60:.2f} minutes")
    logger.info(f"🎯 5 premiers zéros : {zeros[:5]}")
    log_resources()
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
