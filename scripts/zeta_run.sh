#!/bin/bash
# zeta_run.sh — Workflow complet : turbo_on → run → turbo_off
# Usage : zeta_run.sh <T_MAX>
# Auteur : hprzeta — Projet Riemann_Lab
# MAJ : 2026-06-10

set -e

if [ -z "$1" ]; then
    echo "Usage : zeta_run.sh <T_MAX>"
    echo "Exemple : zeta_run.sh 10000"
    exit 1
fi

T_MAX="$1"
PROJET_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"
SCRIPT_DIR="${PROJET_DIR}/scripts"
SRC_DIR="${PROJET_DIR}/src/calculs/optimisation"
LOG_DIR="${PROJET_DIR}/logs"
HORODATAGE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/run_T${T_MAX}_${HORODATAGE}.log"
PID_FILE="${LOG_DIR}/run_T${T_MAX}.pid"

mkdir -p "$LOG_DIR"

echo "=== zeta_run.sh — T_MAX=${T_MAX} ==="
echo "  Log → ${LOG_FILE}"

# Activer l'environnement virtuel
source "${PROJET_DIR}/zeta_env/bin/activate"
export PYTHONPATH="${PYTHONPATH}:${PROJET_DIR}/src"

# Turbo on
sudo "${SCRIPT_DIR}/zeta_turbo_on.sh"

echo ""
echo "  Lancement du calcul en arrière-plan..."
nohup bash -c "printf '${T_MAX}\nO\n' | python ${SRC_DIR}/compute_zeros_v4_1.py" \
    > "${LOG_FILE}" 2>&1 &
PID=$!
echo "$PID" > "$PID_FILE"
echo "  ✅  PID=${PID} — run lancé"
echo "  Suivre : tail -f ${LOG_FILE}"
echo ""
echo "  Attente de fin..."
wait "$PID"
RET=$?

echo ""
# Turbo off
sudo "${SCRIPT_DIR}/zeta_turbo_off.sh"

if [ $RET -eq 0 ]; then
    echo "  ✅  Run T=${T_MAX} terminé avec succès"
else
    echo "  ❌  Run T=${T_MAX} terminé avec erreur (code ${RET})"
fi

rm -f "$PID_FILE"
echo "=== Fin zeta_run.sh ==="
