#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DÉMONSTRATION COMPLÈTE DU PROJET ZÊTA
=====================================
Ce script illustre l'utilisation de tous les outils scientifiques installés
dans l'environnement virtuel pour explorer la fonction zêta de Riemann.

OUTILS UTILISÉS :
-----------------
🔴 PRIORITÉ HAUTE :
- mpmath      : Calcul haute précision (50 décimales) et fonction zêta
- numpy       : Calculs vectoriels et manipulation de données
- matplotlib  : Visualisations 2D statiques
- plotly      : Visualisations 3D interactives (bande critique)

🟡 PRIORITÉ MOYENNE :
- pandas      : Sauvegarde des résultats en CSV
- loguru      : Logging structuré (fichier + console)
- joblib      : (Optionnel) Parallélisation (désactivée car incompatible mpmath)

🟢 OPTIONNEL :
- scipy       : (Non utilisé ici) Pour intégrations avancées
- sympy       : (Non utilisé ici) Pour calcul symbolique
- seaborn     : (Non utilisé ici) Pour statistiques visuelles

AUTEUR : Projet Zêta - Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

import os
import sys
import time
from pathlib import Path

# ============================================================================
# 1. LOGGING avec loguru (🟡 Priorité Moyenne)
# ============================================================================
# loguru : Logging structuré plus simple que logging standard
# - Rotation automatique des fichiers logs
# - Format personnalisable
# - Sortie simultanée fichier + console
from loguru import logger

logger.remove()  # Enlever le handler par défaut
logger.add(
    "/mnt/data/logs/demo_zeta.log",
    rotation="10 MB",           # Nouveau fichier tous les 10 Mo
    level="INFO",               # Niveau INFO (DEBUG, INFO, WARNING, ERROR)
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
logger.add(sys.stdout, level="INFO")  # Affichage console

logger.info("=== Démarrage de la démonstration du projet Zêta ===")

# ============================================================================
# 2. CALCUL HAUTE PRÉCISION avec mpmath (🔴 Priorité Haute)
# ============================================================================
# mpmath : Bibliothèque de calcul en précision arbitraire
# - Permet des calculs avec 50, 100, 1000+ décimales
# - Implémentation native de la fonction zêta de Riemann
# - Gère les nombres complexes et réels
from mpmath import mp, zeta

# Configurer la précision (50 décimales)
mp.dps = 50  # decimal places (précision)
logger.info(f"Précision mpmath configurée à {mp.dps} décimales")

# ============================================================================
# 3. IMPORT DES AUTRES BIBLIOTHÈQUES
# ============================================================================
# numpy (🔴 Priorité Haute) : Calculs vectoriels et matrices
import numpy as np

# matplotlib (🔴 Priorité Haute) : Visualisations 2D
import matplotlib.pyplot as plt

# pandas (🟡 Priorité Moyenne) : Manipulation et sauvegarde de données
import pandas as pd

# ============================================================================
# 4. FONCTIONS
# ============================================================================

def lire_nombres_depuis_fichier(fichier_path):
    """
    Lit un fichier texte contenant des nombres (un par ligne ou séparés)
    
    Utilisation : pandas n'est pas utilisé ici car le fichier est simple
    Format supporté : nombres réels (2, 3.5) ou complexes (0.5+14j)
    """
    logger.info(f"Lecture du fichier : {fichier_path}")
    
    if not os.path.exists(fichier_path):
        logger.warning(f"Fichier {fichier_path} inexistant. Utilisation de valeurs par défaut.")
        # Valeurs par défaut : points sur la droite critique (Re=0.5) et réels
        return [0.5 + 14j, 0.5 + 21j, 0.5 + 25j, 2, 3, 4, 0.5, 1.5, 2.5, 3.5]
    
    with open(fichier_path, 'r') as f:
        contenu = f.read()
    
    nombres = []
    for token in contenu.replace(',', ' ').split():
        try:
            # Essayer de lire comme complexe (format: "0.5+14j" ou "0.5+14i")
            if 'j' in token or 'i' in token:
                token = token.replace('i', 'j')
                nombres.append(complex(token))
            else:
                nombres.append(float(token))
        except ValueError:
            logger.warning(f"Impossible de parser '{token}', ignoré")
    
    logger.info(f"Lu {len(nombres)} nombres : {nombres}")
    return nombres


def calculer_zeta(s):
    """
    Calcule ζ(s) avec gestion des erreurs et logging de performance
    
    OUTIL : mpmath.zeta() (🔴 Priorité Haute)
    - Calcule la fonction zêta de Riemann
    - Accepte les nombres réels et complexes
    - Retourne un résultat avec la précision configurée (50 décimales)
    """
    start = time.time()
    try:
        # Appel à la fonction zêta de mpmath
        resultat = zeta(s)
        temps = time.time() - start
        
        # Log de performance (niveau DEBUG uniquement)
        logger.debug(f"ζ({s}) = {resultat} (calculé en {temps:.6f}s)")
        
        return {
            's': s,
            'zeta_s': resultat,
            'temps_calcul': temps,
            'reussite': True
        }
    except Exception as e:
        logger.error(f"Erreur pour ζ({s}) : {e}")
        return {
            's': s,
            'zeta_s': None,
            'temps_calcul': time.time() - start,
            'reussite': False,
            'erreur': str(e)
        }


def traitement_serie(nombres):
    """
    Traitement séquentiel des calculs
    
    NOTE : La parallélisation (joblib) n'est pas utilisée car mpmath
    utilise des types (mpf, mpc) non sérialisables par pickle.
    Pour ce projet, le traitement séquentiel est suffisant.
    """
    logger.info("=== Traitement SÉQUENTIEL ===")
    resultats = []
    debut_total = time.time()
    
    for i, s in enumerate(nombres):
        logger.debug(f"Calcul {i+1}/{len(nombres)} : ζ({s})")
        resultats.append(calculer_zeta(s))
    
    temps_total = time.time() - debut_total
    logger.info(f"Traitement séquentiel terminé en {temps_total:.4f}s")
    return resultats, temps_total


def sauvegarder_resultats_csv(resultats, output_path):
    """
    Sauvegarde les résultats en CSV avec pandas (🟡 Priorité Moyenne)
    
    OUTIL : pandas.DataFrame (🟡 Priorité Moyenne)
    - Crée un tableau structuré
    - Exporte facilement en CSV, JSON, Excel, etc.
    - Gère les types complexes (convertion en string)
    """
    # Créer le dossier si nécessaire
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Création d'un DataFrame pandas
    df = pd.DataFrame(resultats)
    
    # Conversion des nombres complexes en string pour CSV
    df['s'] = df['s'].apply(lambda x: str(x))
    df['zeta_s'] = df['zeta_s'].apply(lambda x: str(x) if x is not None else "NaN")
    
    # Sauvegarde en CSV
    df.to_csv(output_path, index=False)
    logger.info(f"Résultats sauvegardés dans {output_path}")
    return df


def generer_visualisations(df, output_dir="/mnt/data/exports/figures"):
    """
    Génère des graphiques avec matplotlib et plotly
    
    OUTILS :
    - matplotlib (🔴 Priorité Haute) : Graphiques 2D statiques
    - plotly (🔴 Priorité Haute) : Graphiques 3D interactifs (HTML)
    """
    # Créer le dossier de sortie
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Dossier de sortie des figures : {output_dir}")
    
    # Filtrer les résultats valides
    df_valid = df[df['reussite'] == True].copy()
    
    if len(df_valid) == 0:
        logger.warning("Aucun résultat valide pour la visualisation")
        return
    
    # Extraire les parties réelles et imaginaires des complexes
    def extraire_parties(s_str):
        try:
            s = complex(s_str.replace('i', 'j'))
            return s.real, s.imag
        except:
            return None, None
    
    df_valid['real'] = df_valid['s'].apply(lambda x: extraire_parties(x)[0])
    df_valid['imag'] = df_valid['s'].apply(lambda x: extraire_parties(x)[1])
    
    # ========== Graphique 1 : matplotlib (2D) - Module pour les réels purs ==========
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))
    
    # Graphique 1 : Module de ζ(s) pour les réels purs
    reels_valides = df_valid[df_valid['imag'] == 0]
    for _, row in reels_valides.iterrows():
        try:
            val = abs(complex(str(row['zeta_s']).replace('i', 'j')))
            ax1.scatter(row['real'], val, color='blue', s=50)
        except:
            pass
    
    ax1.set_xlabel('s (partie réelle)')
    ax1.set_ylabel('|ζ(s)|')
    ax1.set_title('Module de ζ(s) pour s réel')
    ax1.grid(True)
    
    # ========== Graphique 2 : Temps de calcul par point avec couleurs ==========
    # Créer une liste de couleurs : rouge pour les complexes, bleu pour les réels
    couleurs = []
    indices_complexes = []
    for i, (_, row) in enumerate(df_valid.iterrows()):
        if row['imag'] is not None and row['imag'] != 0:
            couleurs.append('red')      # Nombre complexe (partie imaginaire de ζ(s) ≠ 0)
            indices_complexes.append(i)
        else:
            couleurs.append('royalblue')   # Nombre réel (partie imaginaire de ζ(s) = 0)
    
    # Créer le graphique à barres avec les couleurs
    bars = ax2.bar(range(len(df_valid)), df_valid['temps_calcul'], color=couleurs)
    
    # Ajouter une légende personnalisée
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='red', label='Nombres complexes (partie imaginaire de ζ(s)  ≠ 0)'),
        Patch(facecolor='royalblue', label='Nombres réels (partie imaginaire de ζ(s)  = 0)')
    ]
    ax2.legend(handles=legend_elements, loc='upper right', ncol=1, framealpha=0.9)
    
    ax2.set_xlabel('Indice du calcul de chaque ζ(s)')
    ax2.set_ylabel('Temps (s)')
    ax2.set_title('Performance des calculs des ζ(s) (rouge = complexes)')
    ax2.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Optionnel : ajouter les valeurs sur les barres (pour les complexes)
    for i in indices_complexes:
        hauteur = df_valid.iloc[i]['temps_calcul']
        ax2.text(i, hauteur + 0.0001, f'{hauteur:.4f}s', 
                 ha='center', va='bottom', fontsize=8, color='red')
    
    plt.tight_layout()
    # Valeurs progressives à tester :

    # Décalage marge Version 1 : un peu plus à gauche
    #plt.subplots_adjust(left=0.07, right=0.93, wspace=0.25)
    # Décalage marge Version 2 : encore plus à gauche
    plt.subplots_adjust(left=0.05, right=0.95, wspace=0.2)
     # Décalage marge Version 3 : très agressive
     #plt.subplots_adjust(left=0.03, right=0.97, wspace=0.15)
    
    # Sauvegarde du graphique matplotlib
    png_path = os.path.join(output_dir, "visualisation_matplotlib.png")
    plt.savefig(png_path, dpi=300, bbox_inches='tight')  # bbox_inches='tight' coupe les blancs
    logger.info(f"✅ Graphique matplotlib sauvegardé : {png_path}")
    plt.show()
    
    # ========== Graphique 2 : plotly (interactif) ==========
    logger.info("=" * 50)
    logger.info("Génération du graphique plotly...")
    
    try:
        import plotly.graph_objects as go
        logger.info("✅ plotly.graph_objects importé avec succès")
        
        # Préparer les données pour la bande critique (Re(s)=1/2)
        imaginaires = []
        modules = []
        
        for _, row in df_valid.iterrows():
            if row['imag'] is not None and row['imag'] > 0:
                imaginaires.append(row['imag'])
                try:
                    zeta_str = str(row['zeta_s']).replace('i', 'j')
                    val = abs(complex(zeta_str))
                    modules.append(val)
                except Exception as e:
                    logger.warning(f"Erreur de conversion pour {row['s']}: {e}")
                    modules.append(0)
        
        logger.info(f"Données plotly : {len(imaginaires)} points trouvés (partie imaginaire > 0)")
        
        if len(imaginaires) >= 1:
            fig_plotly = go.Figure()
            fig_plotly.add_trace(go.Scatter(
                x=imaginaires,
                y=modules,
                mode='markers+lines',
                name='|ζ(0.5 + it)|',
                marker=dict(size=10, color='red')
            ))
            fig_plotly.update_layout(
                title='Module de ζ(s) sur la droite critique Re(s)=1/2',
                xaxis_title='Partie imaginaire t',
                yaxis_title='|ζ(0.5 + it)|',
                template='plotly_dark'
            )
            
            # Sauvegarde du fichier HTML
            html_path = os.path.join(output_dir, "visualisation_plotly.html")
            fig_plotly.write_html(html_path)
            
            if os.path.exists(html_path):
                file_size = os.path.getsize(html_path)
                logger.info(f"✅✅✅ Graphique plotly sauvegardé avec succès !")
                logger.info(f"   📁 Chemin : {html_path}")
                logger.info(f"   📊 Taille : {file_size} octets")
            else:
                logger.error(f"❌ Échec : le fichier {html_path} n'a pas été créé")
        else:
            logger.warning(f"⚠️ Pas assez de données pour plotly : {len(imaginaires)} points")
            
    except ImportError as e:
        logger.error(f"❌ Erreur d'import plotly : {e}")
        logger.info("   Solution: pip install plotly --upgrade")
    except Exception as e:
        logger.error(f"❌ Erreur inattendue avec plotly : {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info("=" * 50)
    return fig

def main():
    """
    Fonction principale orchestrant toute la démonstration
    
    DÉROULEMENT :
    1. Création des dossiers nécessaires
    2. Lecture des nombres depuis /mnt/data
    3. Calcul de ζ(s) pour chaque nombre
    4. Sauvegarde des résultats en CSV
    5. Génération des graphiques
    6. Affichage du rapport final
    """
    start_time = time.time()
    
    # Création automatique des dossiers
    os.makedirs("/mnt/data/datasets/calculs", exist_ok=True)
    os.makedirs("/mnt/data/exports/csv", exist_ok=True)
    os.makedirs("/mnt/data/exports/figures", exist_ok=True)
    os.makedirs("/mnt/data/logs", exist_ok=True)
    
    logger.info("Dossiers créés/vérifiés avec succès")
    
    # 1. Lecture des données
    fichier_input = "/mnt/data/datasets/calculs/nombres_a_tester.txt"
    nombres = lire_nombres_depuis_fichier(fichier_input)
    
    # 2. Créer le fichier d'exemple s'il n'existe pas
    if not os.path.exists(fichier_input):
        with open(fichier_input, 'w') as f:
            f.write("0.5+14j\n0.5+21j\n0.5+25j\n2\n3\n4\n0.5\n1.5\n2.5\n3.5")
        logger.info(f"Fichier d'exemple créé : {fichier_input}")
        nombres = lire_nombres_depuis_fichier(fichier_input)
    
    # 3. Traitement séquentiel
    resultats_seq, temps_seq = traitement_serie(nombres)
    
    # 4. Sauvegarde des résultats avec pandas
    df_seq = sauvegarder_resultats_csv(
        resultats_seq, 
        "/mnt/data/exports/csv/resultats_zeta.csv"
    )
    
    # 5. Visualisation
    generer_visualisations(df_seq)
    
    # 6. Rapport final
    total_time = time.time() - start_time
    
    logger.info("=" * 60)
    logger.info("=== RAPPORT FINAL ===")
    logger.info(f"Nombre de calculs effectués : {len(nombres)}")
    logger.info(f"Temps séquentiel : {temps_seq:.4f}s")
    logger.info(f"Temps total d'exécution : {total_time:.4f}s")
    logger.info("=" * 60)
    
    # Affichage des résultats dans la console
    print("\n" + "=" * 60)
    print("RÉSULTATS DES CALCULS")
    print("=" * 60)
    for r in resultats_seq:
        if r['reussite']:
            # mpmath retourne des résultats avec la précision configurée
            print(f"ζ({r['s']}) = {r['zeta_s']}")
        else:
            print(f"ζ({r['s']}) = ERREUR : {r.get('erreur', 'Inconnue')}")
    print("=" * 60)
    
    return resultats_seq


# ============================================================================
# 5. POINT D'ENTRÉE
# ============================================================================
if __name__ == "__main__":
    main()
