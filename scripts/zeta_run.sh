#!/usr/bin/env bash
# zeta_run.sh — Workflow complet run Riemann_Lab avec optimisation système
# Usage : ./scripts/zeta_run.sh [T_MAX]
# Exemple : ./scripts/zeta_run.sh 100000
# Si T_MAX non fourni, le script demande la valeur (mode interactif).
# Auteur : hprzeta — MAJ 2026-06-10

set -euo pipefail

PROJET_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${PROJET_DIR}/logs"
SCRIPT_DIR="${PROJET_DIR}/scripts"
COMPUTE="${PROJET_DIR}/src/calculs/optimisation/compute_zeros_v4_1.py"

# ─── T_MAX ─────────────────────────────────────────────────────────────────────
if [ -n "${1:-}" ]; then
    T_MAX="$1"
else
    read -rp "  Entrez T_MAX pour le run : " T_MAX
fi

if ! [[ "$T_MAX" =~ ^[0-9]+(\.[0-9]+)?$ ]] || (( $(echo "$T_MAX < 20" | bc -l) )); then
    echo "❌  T_MAX invalide (minimum 20). Abandon."
    exit 1
fi

echo "═══════════════════════════════════════════════════════════════"
echo "   ZETA-RUN — T_MAX=${T_MAX}"
echo "═══════════════════════════════════════════════════════════════"

# ─── ÉTAPE 1 : Optimisation système ────────────────────────────────────────────
echo ""
echo "── Étape 1/3 : Optimisation système (sudo requis) ───────────────"
sudo "${SCRIPT_DIR}/zeta_turbo_on.sh"

# ─── ÉTAPE 2 : Lancement du run ────────────────────────────────────────────────
echo ""
echo "── Étape 2/3 : Lancement du run ────────────────────────────────"
source "${PROJET_DIR}/zeta_env/bin/activate"
export PYTHONPATH="${PYTHONPATH:-}:${PROJET_DIR}/src"

HORODATAGE=$(date +%Y%m%d_%H%M%S)
LOG_RUN="${LOG_DIR}/run_T${T_MAX%.*}_${HORODATAGE}.log"
PID_FILE="${LOG_DIR}/run_T${T_MAX%.*}.pid"

mkdir -p "$LOG_DIR"

# Lancer le run en arrière-plan (nohup pour résistance aux déconnexions)
printf "%s\nO\n" "$T_MAX" | nohup python "$COMPUTE" > "$LOG_RUN" 2>&1 &
PY_PID=$!
echo "$PY_PID" > "$PID_FILE"

echo "  PID    : ${PY_PID}"
echo "  Log    : ${LOG_RUN}"
echo "  PID file : ${PID_FILE}"
echo "  Attente de la fin du run..."

# Attendre la fin du processus Python
wait "$PY_PID"
EXIT_CODE=$?

# ─── ÉTAPE 3 : Restauration système ────────────────────────────────────────────
echo ""
echo "── Étape 3/3 : Restauration système ─────────────────────────────"
sudo "${SCRIPT_DIR}/zeta_turbo_off.sh"

# ─── Résultat ──────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════"
if [ "$EXIT_CODE" -eq 0 ]; then
    echo "   ✅  Run terminé avec succès"
    echo "   Log : ${LOG_RUN}"
    # Afficher les dernières lignes du log (résumé)
    echo ""
    tail -30 "$LOG_RUN"
else
    echo "   ❌  Run terminé avec code d'erreur : ${EXIT_CODE}"
    echo "   Log : ${LOG_RUN}"
    tail -20 "$LOG_RUN"
fi
echo "═══════════════════════════════════════════════════════════════"
