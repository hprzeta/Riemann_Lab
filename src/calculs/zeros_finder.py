"""
Module de recherche des zéros non triviaux de ζ(s)
Contient l'algorithme principal et les fonctions auxiliaires
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

from mpmath import mp, zeta, findroot
import numpy as np
from tqdm import tqdm
from loguru import logger

from ..monitoring.resources import log_resources
from ..utils.file_io import save_intermediate_results

def Z_function(t: float) -> float:
    """Fonction Z de Riemann (réelle sur la droite critique)"""
    return float(zeta(0.5 + 1j * t).real)

def find_zero_bracket(t_left: float, t_right: float, tol: float = 1e-12) -> float:
    """Affinage par Newton-Raphson"""
    try:
        zero = findroot(lambda t: zeta(0.5 + 1j * t), 
                       (t_left + t_right)/2, 
                       solver='newton', tol=tol, maxsteps=50)
        return float(zero)
    except:
        return None

def compute_zeros(T_max: float, step: float, tol: float) -> list:
    """Algorithme principal de détection + affinage"""
    zeros = []
    t = 10.0
    Z_prev = Z_function(t)
    
    n_steps = int((T_max - t) / step)
    for _ in tqdm(range(n_steps), desc="Recherche des zéros"):
        t += step
        Z_curr = Z_function(t)
        
        if Z_prev * Z_curr < 0:
            zero = find_zero_bracket(t-step, t, tol)
            if zero and abs(zeta(0.5 + 1j * zero)) < 1e-10:
                zeros.append(zero)
                logger.info(f"✅ Zéro trouvé : t = {zero:.10f}")
                
                if len(zeros) % 100 == 0:
                    save_intermediate_results(zeros)
                    log_resources()
        
        Z_prev = Z_curr
    
    return zeros

def compute_zeros_pipeline(config: dict) -> list:
    """Pipeline complet avec logging et monitoring"""
    logger.info("Démarrage du calcul des zéros")
    mp.dps = config.get("precision", 50)
    
    zeros = compute_zeros(
        T_max=config["T_max"],
        step=config["step"],
        tol=config["tol"]
    )
    
    logger.info(f"Calcul terminé : {len(zeros)} zéros trouvés")
    return zeros
