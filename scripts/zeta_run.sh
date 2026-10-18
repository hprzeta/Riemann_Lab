#!/bin/bash
# zeta_run.sh — Workflow complet : turbo (CPU + services) → run → services restaurés
# Cycle de vie turbo (2026-10-16) : le turbo CPU est activé au début de SESSION (hook) et RESTE actif
# entre les runs ; il n'est restauré qu'au « bye bye » (zeta_session_turbo.sh end). Ce script ne
# désactive donc PLUS le turbo CPU : il arrête les services pendant le run (--services), puis les
# redémarre (off --services). Un turbo partiel/non actif est signalé, sans interrompre le run.
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

# Toujours se placer à la racine du dépôt : compute_zeros_v16.py écrit dans le chemin RELATIF calculs/
# (sinon un run lancé depuis ~ écrit dans ~/calculs/ et le monitoring ne trouve pas le CSV)
cd "$PROJET_DIR"

echo "=== zeta_run.sh — T_MAX=${T_MAX} ==="
echo "  Log → ${LOG_FILE}"

# Activer l'environnement virtuel
source "${PROJET_DIR}/zeta_env/bin/activate"
export PYTHONPATH="${PYTHONPATH}:${PROJET_DIR}/src"

# Copie durcie (root:root, non modifiable) de préférence si elle existe (voir CLAUDE.md « Droits »).
turbo_bin() {
    local d="/usr/local/sbin/zeta_turbo_$1"
    if [ -x "$d" ] && [ "$(stat -c %u "$d")" = "0" ] && [ -z "$(find "$d" -perm /022)" ]; then echo "$d"
    else echo "${SCRIPT_DIR}/zeta_turbo_$1.sh"; fi
}

# Turbo on (idempotent : n'écrase jamais l'état initial sauvegardé) + arrêt des services pendant le run
sudo "$(turbo_bin on)" --services \
    || echo "  ⚠️  Turbo NON (entièrement) actif — le run continue sans garantie de performance (voir ci-dessus)"

echo ""
echo "  Lancement du calcul en arrière-plan (extinction/veille inhibées)..."
# Monitoring (2026-10-17) : si monitoring/scripts/zeta_mon_run.py existe, la commande est enveloppée
# (suivi, rapport MD+PDF). Type : ZETA_MON_TYPE=test (fenêtres ON) | prod (défaut, fenêtres OFF).
CMD_CALCUL="printf '${T_MAX}\nO\n' | python ${SRC_DIR}/compute_zeros_v16.py"
MON_RUN="${PROJET_DIR}/monitoring/scripts/zeta_mon_run.py"
if [ -f "$MON_RUN" ]; then
    MON_PREFIXE=(python "$MON_RUN" exec --nom "T${T_MAX}" --type "${ZETA_MON_TYPE:-prod}" \
                 --csv "${PROJET_DIR}/calculs/" --)
else
    MON_PREFIXE=()
fi
systemd-inhibit --what=shutdown:sleep:idle --who="zeta_run.sh" \
    --why="Run T=${T_MAX} en cours" --mode=block \
    nohup "${MON_PREFIXE[@]}" bash -c "${CMD_CALCUL}" \
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
# Services redémarrés ; le turbo CPU est MAINTENU jusqu'au « bye bye » (état initial conservé)
sudo "$(turbo_bin off)" --services \
    || echo "  ⚠️  Services non (tous) redémarrés — état conservé ; relancer : sudo scripts/zeta_turbo_off.sh --services"

if [ $RET -eq 0 ]; then
    echo "  ✅  Run T=${T_MAX} terminé avec succès"
else
    echo "  ❌  Run T=${T_MAX} terminé avec erreur (code ${RET})"
fi

rm -f "$PID_FILE"
echo "=== Fin zeta_run.sh ==="
