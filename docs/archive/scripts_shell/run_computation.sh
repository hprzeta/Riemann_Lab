#!/bin/bash

# ============================================================================
# Script de lancement complet pour le projet Zêta
# AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
# DATE : 2026
# ============================================================================


cd ~/projet_zeta
source zeta_env/bin/activate
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
python -m src.main
