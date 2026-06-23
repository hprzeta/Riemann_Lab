#!/bin/bash
# zeta_distribute_run.sh — Lance la distribution PC1+PC2
# Usage : zeta-distribute 500000
# ou     zeta-distribute 500000 --no-dashboard

set -e
cd ~/projet_zeta
source zeta_env/bin/activate

T_MAX=${1:-500000}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG="logs/distribute_T${T_MAX}_nohup_${TIMESTAMP}.log"

echo "=== ZETA DISTRIBUTE — T_MAX=$T_MAX ==="
echo "Log : $LOG"

# Turbo ON (sudoers NOPASSWD configuré depuis le 12/06/2026 — non interactif)
sudo scripts/zeta_turbo_on.sh

# Lancer dashboard tmux (sauf si --no-dashboard)
if [[ "$2" != "--no-dashboard" ]]; then
  tmux kill-session -t zeta-progress 2>/dev/null || true
  tmux new-session -d -s zeta-progress \
    "source zeta_env/bin/activate && python scripts/zeta_run_progress.py"
  echo "Dashboard : tmux attach -t zeta-progress"
fi

# Lancer le run en arrière-plan
# "O\n" auto-répondu à la confirmation interactive de zeta_distribute.py
nohup bash -c 'printf "O\n" | python scripts/zeta_distribute.py '"$T_MAX"'' \
  > "$LOG" 2>&1 &
PID=$!
echo $PID > /tmp/zeta_distribute.pid
echo "PID: $PID — run lancé"
echo "Résultat : tail -f $LOG"
