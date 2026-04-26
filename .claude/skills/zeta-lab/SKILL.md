---
name: zeta-lab
description: >
  Laboratoire zêta de Riemann — exploration numérique, symbolique et graphique
  de ζ(s) et de l'Hypothèse de Riemann. Se déclenche sur : "calcule les zéros",
  "trace zeta", "vérifie cette formule", "fonction Z de Hardy", "espacement des
  zéros", "PRNG zêta", "hypothèse de Riemann", "zêta de Riemann", "HR", "ζ(",
  "Z(t)", "θ(t)", "Riemann-Siegel", "LMFDB", "nombres premiers".
version: 0.1.0
---

# Zeta-Lab — Laboratoire Riemann

## Contexte du projet

Chercheur : hprzeta — GitHub : https://github.com/hprzeta/Riemann_Lab
Dossier local : /home/riemann/projet_zeta
Niveau actuel : débutant → intermédiaire (progression vers expert)
Objectif final : exploration HR, calcul des zéros, PRNG cryptographique, tentative de résolution.

## Règles de réponse

- Toujours en français
- Adapter le niveau : expliquer les concepts depuis la base, puis monter en complexité
- Toujours proposer du code Python exécutable et testé
- Vérifier les résultats numériques contre LMFDB quand possible
- Signaler explicitement si un résultat pourrait être un faux positif ou une erreur

## Stack technique

- Python 3.12 dans /home/riemann/projet_zeta/zeta_env/
- Activer : `source ~/projet_zeta/zeta_env/bin/activate`
- Bibliothèques : mpmath (50 dps), sympy, numpy, scipy, matplotlib, plotly, loguru

## Workflow standard

### Pour un calcul de zéros
1. Utiliser `compute_zeros_v2.py` (méthode Z de Hardy + Illinois)
2. Valider contre LMFDB (10 premiers zéros)
3. Sauvegarder CSV + PNG dans `/mnt/data/exports/`
4. Logger dans `/mnt/data/logs/`

### Pour une vérification de formule
1. Tester numériquement avec mpmath (50 décimales)
2. Comparer à une référence connue (LMFDB, Odlyzko, tables)
3. Si cohérent → vérification symbolique avec sympy
4. Documenter dans le wiki

### Pour une visualisation
1. Matplotlib pour graphiques 2D statiques
2. Plotly pour graphiques 3D interactifs
3. Sauvegarder dans `/mnt/data/exports/figures/` (fallback : `images/exports/`)

## Formules de référence

Voir references/formules_zeta.md

## Bibliothèques clés et usage

Voir references/bibliotheques.md

## Historique des résultats

- Étape 1 ✅ : 10 142 zéros calculés jusqu'à T=10 000 (21h, mpmath 50 dps, Illinois)
- Validation : 10/10 premiers zéros conformes LMFDB (écart < 1e-14)
- PRNG zêta : prototype dans src/tests/PRNG_ZETA.py
