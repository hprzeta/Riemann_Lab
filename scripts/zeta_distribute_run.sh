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
# python -u (01/11/2026) : sortie non tamponnée, sinon le log reste vide vers un fichier (marqueur de démarrage invisible, tail -f muet)
nohup bash -c 'printf "O\n" | python -u scripts/zeta_distribute.py '"$T_MAX"'' \
  > "$LOG" 2>&1 &
PID=$!
echo $PID > /tmp/zeta_distribute.pid

# Vérification du démarrage RÉEL (01/11/2026) : ne plus afficher « run lancé » sans preuve.
# Succès  : le script a franchi le test PC2 et la confirmation, et affiche « Lancement parallèle ».
# Échec   : le processus est mort (EOFError, PC2 injoignable, argument invalide…) -> on le dit, avec la fin du log.
# Incertain : processus encore actif mais marqueur absent après le délai -> avertissement, pas de faux « lancé ».
verifier_demarrage() {            # $1 = PID, $2 = fichier log, $3 = délai max en secondes (défaut 90)
  local pid="$1" log="$2" delai="${3:-90}" i
  for ((i = 0; i < delai; i++)); do
    if grep -q "Lancement parallèle" "$log" 2>/dev/null; then return 0; fi   # démarrage confirmé
    if ! kill -0 "$pid" 2>/dev/null; then return 1; fi                       # processus mort avant le démarrage
    sleep 1
  done
  return 2                                                                     # actif mais non confirmé
}
set +e
verifier_demarrage "$PID" "$LOG" "${ZETA_DISTRIBUTE_ATTENTE:-90}"
ETAT=$?
set -e
case $ETAT in
  0) echo "PID: $PID — run LANCÉ (démarrage confirmé dans le log)"
     echo "Résultat : tail -f $LOG" ;;
  2) echo "PID: $PID — ATTENTION : processus actif mais démarrage NON confirmé après ${ZETA_DISTRIBUTE_ATTENTE:-90} s."
     echo "Vérifier : tail -f $LOG" ;;
  *) wait "$PID" 2>/dev/null && RC=0 || RC=$?
     rm -f /tmp/zeta_distribute.pid
     echo "ÉCHEC : le run s'est arrêté avant de démarrer (code $RC). Fin du log ($LOG) :"
     tail -n 15 "$LOG" | sed 's/^/  | /'
     exit 1 ;;
esac
