#!/bin/bash

# ============================================================================
# Script de monitoring complet pour le projet Zêta
# monitor.sh - Surveillance htop + iostat + mémoire
# À lancer dans un terminal séparé pendant compute_zeros.py
# AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
# DATE : 2026
# ============================================================================


LOGS_DIR="/mnt/data/logs/monitoring"
mkdir -p "$LOGS_DIR"

DATE=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOGS_DIR/monitor_$DATE.log"

echo "Démarrage monitoring à $(date)" | tee -a "$LOG_FILE"

# Lancement de htop en mode batch toutes les 10 secondes
while true; do
    echo "=== $(date) ===" >> "$LOG_FILE"
    
    # CPU et mémoire avec htop (mode batch)
    echo "--- htop snapshot ---" >> "$LOG_FILE"
    htop -C -d 10 --no-color --delay=1 -C 2>/dev/null | head -20 >> "$LOG_FILE"
    
    # Disque
    echo "--- iostat ---" >> "$LOG_FILE"
    iostat -x 1 2 | tail -10 >> "$LOG_FILE"
    
    # Températures (si lm-sensors installé)
    if command -v sensors &> /dev/null; then
        echo "--- sensors ---" >> "$LOG_FILE"
        sensors -u | grep -E "temp[0-9]+_input|Core" >> "$LOG_FILE"
    fi
    
    # GPU (NVIDIA)
    if command -v nvidia-smi &> /dev/null; then
        echo "--- nvidia-smi ---" >> "$LOG_FILE"
        nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu --format=csv,noheader >> "$LOG_FILE"
    fi
    
    echo "" >> "$LOG_FILE"
    sleep 30
done
