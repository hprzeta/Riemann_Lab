#!/bin/bash
# ============================================================================
# Script de Sauvegarde tous les paquets Python (global + env) du projet Zêta
# AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
# DATE : 2026
# ============================================================================

cd ~/projet_zeta

# 1. Paquets globaux (hors env)
deactivate 2>/dev/null
pip list --format=freeze > requirements_zeta_global.txt 2>/dev/null

# 2. Paquets de l'environnement zeta_env
source zeta_env/bin/activate
pip freeze > requirements_zeta_ia.txt

# 3. Paquets système (apt)
dpkg -l | grep -E "python|pip" | awk '{print $2}' > requirements_zeta_system.txt

echo "✅ Fichiers générés :"
ls -la requirements_zeta_*.txt
