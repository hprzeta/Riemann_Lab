#!/usr/bin/env python3
"""
Fonctions de base pour la fonction zêta de Riemann
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

from mpmath import zeta, mp,zetazero

# Précision par défaut
mp.dps = 30

def zeta_valeur(s, precision=30):
    """  
    Calcule la fonction zêta de Riemann ζ(s) avec une précision donnée.

    Paramètres
    ----------
    s : complex ou float
        Le point où évaluer la fonction zêta.
        Peut être un nombre réel (ex: 2.0) ou complexe (ex: 0.5 + 14j).
    precision : int, optionnel (défaut=30)
        Nombre de décimales pour le calcul (via mpmath.mp.dps).
        Plus la précision est élevée, plus le calcul est lent.

    Retourne
    -------
    mpmath.mpf ou mpc
        La valeur de ζ(s) à la précision demandée.
        Si s est réel, retourne un flottant multiprécision (mpf).
        Si s est complexe, retourne un complexe multiprécision (mpc).

    Notes
    -----
    Cette fonction modifie globalement mpmath.mp.dps pour la durée du calcul.
    Si une précision plus faible était définie auparavant, elle sera écrasée.
    Pour une utilisation intensive, il est recommandé de sauvegarder et restaurer
    la précision originale (non fait ici pour simplifier l'exemple).

    Exemples
    --------
    >>> zeta_valeur(2)
    mpf('1.644934066848226436472415166646')

    >>> zeta_valeur(0.5 + 14j, precision=50)
    mpc(real='1.6302581668434337428933519038366894001715470747867e-5',
        imag='-1.035502386950401254451202360128080777272067607025e-7')    
    """
    mp.dps = precision
    return zeta(s)

def calculer_premiers_zeros(n=10, precision=50):
    """
    Calcule les n premiers zéros non triviaux de la fonction zêta.

    Paramètres:
    -----------
    n (int): Le nombre de zéros à calculer.
    precision (int): La précision en décimales.

    Retourne:
    ---------
    list: Une liste des n premiers zéros sous forme de nombres complexes(mpc).
    
    
    Exemples:
    ---------
    print(calculer_premiers_zeros(n=1))
    mpc(real='0.5', imag='14.1347251417346937904572519835625')    
    """
    
    # Sauvegarde de l'ancienne précision et définition de la nouvelle
    ancienne_precision = mp.dps
    mp.dps = precision

    # Calcul des zéros
    zeros = []
    
    for i in range(1, n + 1):
        zero = zetazero(i)
        zeros.append(zero)

    # Restauration de la précision
    mp.dps = ancienne_precision

    return zeros


# Exemple d'exécution si le fichier est lancé directement
if __name__ == "__main__":
    
    print(f" ζ(2) = {zeta_valeur(2)} ")
    
    premiers_zeros = calculer_premiers_zeros(n=2)
    for i, zero in enumerate(premiers_zeros):
        print(f"Zéro n°{i+1}: {zero}")