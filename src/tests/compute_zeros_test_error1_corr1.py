#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calcul des zéros de ζ(s) - Version corrigée pour débutants
Auteur : hprzeta
"""

import sys
import time
import numpy as np
from pathlib import Path
from typing import List
import pandas as pd
import matplotlib.pyplot as plt

from mpmath import mp, zeta, loggamma, findroot
from tqdm import tqdm

# ── Précision ──────────────────────────────────────────────────────────────
mp.dps = 50   # 50 décimales (bien plus que la double précision standard)

# ── Paramètres ─────────────────────────────────────────────────────────────
T_MIN  = 10.0     # Le 1er zéro est à t ≈ 14.13, on commence à 10
T_MAX  = 200.0    # Limite de recherche (augmente progressivement !)
STEP   = 0.05     # Pas de balayage (plus petit = moins de zéros manqués)
TOL    = 1e-20    # Tolérance de Newton (profite de la haute précision)

# ═══════════════════════════════════════════════════════════════════════════
#  FONCTIONS MATHÉMATIQUES
# ═══════════════════════════════════════════════════════════════════════════

def theta(t):
    """
    Fonction theta de Riemann.
    
    θ(t) = Im[ ln Γ(1/4 + it/2) ] - (t/2)·ln(π)
    
    Rôle : c'est la "phase" de ζ(1/2+it). Elle sert à "déplier"
    la fonction zêta complexe en une fonction réelle Z(t).
    """
    return float(
        mp.im(loggamma(mp.mpf('0.25') + mp.mpc(0, t) / 2))
        - (t / 2) * mp.log(mp.pi)
    )


def Z(t):
    """
    Fonction Z de Hardy (ou fonction Z de Riemann).
    
    Z(t) = exp(iθ(t)) · ζ(1/2 + it)
    
    PROPRIÉTÉS CLÉS :
    - Z(t) est RÉELLE pour tout t réel  ← permet chercher changements de signe
    - Z(t) = 0  ⟺  ζ(1/2 + it) = 0    ← même zéros que ζ !
    
    CORRECTION DU BUG : les parenthèses englobent TOUT le produit
    avant d'extraire la partie réelle.
    """
    # ✅ CORRECT : on prend .real du produit ENTIER
    valeur_complexe = mp.exp(mp.mpc(0, theta(t))) * zeta(mp.mpc('0.5', t))
    return float(valeur_complexe.real)

    # ❌ INCORRECT (ton code original) :
    # return zeta(0.5 + 1j*t) * mp.exp(1j*theta(t)).real
    # → .real s'applique seulement à exp(...), pas au produit !


def affiner_zero(t_gauche, t_droite, tol=TOL):
    """
    Affine un zéro détecté dans [t_gauche, t_droite].
    
    On utilise Z(t) (réelle) et non ζ directement,
    car Newton marche mieux sur des fonctions réelles.
    
    Méthode :
    1. Bisection (robuste mais lente) pour s'approcher
    2. Newton-Raphson (rapide) pour la précision finale
    """
    try:
        # findroot avec 'illinois' = méthode bisection améliorée
        # On lui donne DEUX points d'encadrement (t_gauche, t_droite)
        t0 = findroot(
            lambda t: Z(float(t)),        # fonction réelle
            (t_gauche, t_droite),          # intervalle d'encadrement
            solver='illinois',             # robuste pour les zéros simples
            tol=tol,
            maxsteps=100
        )
        return float(t0)
    except Exception as e:
        print(f"  ⚠️ Affinage échoué sur [{t_gauche:.3f}, {t_droite:.3f}] : {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  ALGORITHME PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def calculer_zeros(t_min=T_MIN, t_max=T_MAX, step=STEP):
    """
    Balayage de la droite critique pour trouver les zéros de ζ.
    
    Algorithme en 2 passes :
    PASSE 1 — Détection : on cherche les changements de signe de Z(t)
              Un changement de signe → zéro dans l'intervalle (TVI)
              
    PASSE 2 — Affinage : on localise précisément avec Newton/Illinois
    
    THÉORÈME DE VALEURS INTERMÉDIAIRES (TVI) :
    Si Z(a) > 0 et Z(b) < 0 (ou inverse), et Z continue,
    alors ∃ c ∈ ]a,b[ tel que Z(c) = 0.
    """
    zeros   = []
    t       = t_min
    Z_prev  = Z(t)           # Z(t) est un FLOAT — plus de bug de type !
    
    n_steps = int((t_max - t_min) / step)
    
    print(f"\n🔍 Balayage de t={t_min} à t={t_max}, pas={step}")
    print(f"   Soit {n_steps} évaluations de Z(t)...\n")
    
    for _ in tqdm(range(n_steps), desc="Recherche", unit="pas"):
        t      += step
        Z_curr  = Z(t)        # float, la comparaison < 0 marche !
        
        # ── Détection du changement de signe ──────────────────────────────
        # Z_prev * Z_curr < 0  signifie : l'un est positif, l'autre négatif
        # → la fonction a changé de signe → il y a un zéro entre les deux !
        if Z_prev * Z_curr < 0:   # ← comparaison sur des FLOATS ✅
            
            # ── Affinage précis ───────────────────────────────────────────
            t_zero = affiner_zero(t - step, t)
            
            if t_zero is not None:
                # Vérification : est-ce vraiment un zéro ?
                residu = abs(zeta(mp.mpc('0.5', t_zero)))
                
                if residu < 1e-10:
                    zeros.append(t_zero)
                    print(f"\n  ✅ Zéro #{len(zeros):4d} : t = {t_zero:.15f}  |ζ| = {float(residu):.2e}")
                else:
                    print(f"\n  ❌ Faux positif : t={t_zero:.6f}, |ζ|={float(residu):.2e}")
        
        Z_prev = Z_curr
    
    return zeros


# ═══════════════════════════════════════════════════════════════════════════
#  SAUVEGARDE ET VISUALISATION
# ═══════════════════════════════════════════════════════════════════════════

def sauvegarder(zeros: List[float], nom="zeros_zeta.csv"):
    """Sauvegarde les zéros dans un CSV"""
    df = pd.DataFrame({
        "n":               range(1, len(zeros) + 1),
        "partie_imaginaire": zeros,
        "methode":         "Hardy-Z + Illinois",
        "precision_dps":   mp.dps,
    })
    chemin = Path(nom)
    df.to_csv(chemin, index=False)
    print(f"\n💾 {len(zeros)} zéros sauvegardés dans {chemin.resolve()}")
    return df


def visualiser(zeros: List[float]):
    """
    Deux graphiques :
    1. Distribution des espaces entre zéros consécutifs
    2. Les zéros sur la droite critique (re=1/2)
    """
    if len(zeros) < 2:
        print("Pas assez de zéros pour visualiser.")
        return
    
    ecarts = np.diff(zeros)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"Zéros de ζ(1/2+it) — {len(zeros)} zéros trouvés", fontsize=14)
    
    # ── Graphique 1 : distribution des écarts ─────────────────────────────
    # La conjecture de Montgomery prédit que cette distribution suit
    # celle des valeurs propres de matrices aléatoires unitaires (GUE)
    axes[0].hist(ecarts, bins=40, edgecolor='black', alpha=0.75, color='steelblue')
    axes[0].axvline(np.mean(ecarts), color='red', linestyle='--',
                    label=f"Moyenne = {np.mean(ecarts):.4f}")
    axes[0].set_xlabel("Écart entre zéros consécutifs Δt")
    axes[0].set_ylabel("Fréquence")
    axes[0].set_title("Distribution des espacements\n(→ corrélation de paires de Montgomery)")
    axes[0].legend()
    
    # ── Graphique 2 : zéros sur la droite critique ────────────────────────
    axes[1].scatter([0.5] * len(zeros), zeros, s=10, color='darkblue', alpha=0.6)
    axes[1].set_xlabel("Re(s) = 1/2  (droite critique)")
    axes[1].set_ylabel("Im(s) = t")
    axes[1].set_title("Zéros sur la droite critique\nHypothèse de Riemann : tous ici !")
    axes[1].set_xlim(0, 1)
    axes[1].axvline(0.5, color='red', linestyle='--', linewidth=1, label="Re(s) = 1/2")
    axes[1].legend()
    
    plt.tight_layout()
    plt.savefig("zeros_zeta.png", dpi=150)
    plt.show()
    print("📈 Graphique sauvegardé : zeros_zeta.png")


# ═══════════════════════════════════════════════════════════════════════════
#  POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════

def main():
    debut = time.time()
    print("=" * 60)
    print("  CALCUL DES ZÉROS NON TRIVIAUX DE ζ(s)")
    print(f"  Précision : {mp.dps} décimales")
    print("=" * 60)
    
    # Calcul
    zeros = calculer_zeros()
    
    # Résultats
    print("\n" + "=" * 60)
    print(f"✅ {len(zeros)} zéros trouvés en {(time.time()-debut)/60:.1f} min")
    
    # Vérification des 5 premiers (valeurs connues)
    connus = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062]
    print("\n📐 Vérification (5 premiers zéros connus) :")
    for i, (calc, ref) in enumerate(zip(zeros[:5], connus)):
        print(f"   #{i+1}: calculé={calc:.6f}  référence={ref:.6f}  "
              f"écart={abs(calc-ref):.2e}")
    
    # Sauvegarde + visualisation
    sauvegarder(zeros)
    visualiser(zeros)


if __name__ == "__main__":
    main()
