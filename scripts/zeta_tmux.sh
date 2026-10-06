#!/bin/bash

# Bascule WireGuard automatique maison/déplacement (avec message d'état)
bash "$(dirname "$0")/wg_auto.sh"

# Adresses du cluster : fichier LOCAL hors git (jamais d'IP en dur dans le dépôt)
HOTES="$HOME/.config/zeta/cluster_hosts.env"
[ -r "$HOTES" ] || { echo "Fichier d'adresses absent : $HOTES"; exit 1; }
. "$HOTES"                                  # définit ZETA_PC2..PC5 et ZETA_BASTION

# ─── Détection maison / déplacement (tunnel déjà positionné par wg_auto.sh) ───
if ping -c1 -W2 ${ZETA_BASTION} >/dev/null 2>&1; then
    echo "🧳 DÉPLACEMENT — accès cluster via bastion ${ZETA_BASTION}"
    SSH_PC2="ssh -i ~/.ssh/zeta_cluster -o IdentitiesOnly=yes -J hprzeta@${ZETA_BASTION} hprzeta@${ZETA_PC2}"
    SSH_PC3="ssh -i ~/.ssh/zeta_cluster -o IdentitiesOnly=yes -J hprzeta@${ZETA_BASTION} hprzeta@${ZETA_PC3}"
    SSH_PC4="ssh -i ~/.ssh/zeta_cluster -o IdentitiesOnly=yes hprzeta@${ZETA_BASTION}"
    SSH_PC5="ssh -t -i ~/.ssh/zeta_cluster -o IdentitiesOnly=yes -J hprzeta@${ZETA_BASTION} hprzeta@${ZETA_PC5}"
else
    echo "🏠 MAISON — accès cluster direct en LAN"
    SSH_PC2="ssh -i ~/.ssh/zeta_cluster -o IdentitiesOnly=yes hprzeta@${ZETA_PC2}"
    SSH_PC3="ssh -i ~/.ssh/zeta_cluster -o IdentitiesOnly=yes hprzeta@${ZETA_PC3}"
    SSH_PC4="ssh -i ~/.ssh/zeta_cluster -o IdentitiesOnly=yes hprzeta@${ZETA_PC4}"
    SSH_PC5="ssh -t -i ~/.ssh/zeta_cluster -o IdentitiesOnly=yes hprzeta@${ZETA_PC5}"
fi

SESSION="zeta-cluster"
tmux kill-session -t $SESSION 2>/dev/null
tmux new-session -d -s $SESSION -x 220 -y 50
tmux split-window -h -t $SESSION
tmux select-pane -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.2
tmux select-pane -t $SESSION:0.0 -P 'bg=#16261b,fg=#5cb86a'
tmux send-keys -t $SESSION:0.0 "$SSH_PC2" Enter
sleep 1
tmux select-pane -t $SESSION:0.1 -P 'bg=#142130,fg=#4f95dc'
tmux send-keys -t $SESSION:0.1 "$SSH_PC3" Enter
sleep 1
tmux select-pane -t $SESSION:0.2 -P 'bg=#251628,fg=#b06fce'
tmux send-keys -t $SESSION:0.2 "$SSH_PC4" Enter
sleep 1
tmux select-pane -t $SESSION:0.3 -P 'bg=#2a2410,fg=#e0a83c'
tmux send-keys -t $SESSION:0.3 "cd ~/projet_zeta && source zeta_env/bin/activate" Enter
tmux send-keys -t $SESSION:0.4 "cd ~/projet_zeta && source zeta_env/bin/activate && python3 scripts/zeta_monitor.py" Enter

# ─── Window dédiée PC5 (htop en haut / shell libre en bas) ───
tmux new-window -d -t $SESSION -n "PC5"
tmux split-window -v -t $SESSION:PC5
tmux select-pane -t $SESSION:PC5.0 -P 'bg=#2b1a11,fg=#e2743c'
tmux send-keys -t $SESSION:PC5.0 "$SSH_PC5 htop" Enter
sleep 1
tmux select-pane -t $SESSION:PC5.1 -P 'bg=#2b1a11,fg=#e2743c'
tmux send-keys -t $SESSION:PC5.1 "$SSH_PC5" Enter
sleep 1

tmux attach-session -t $SESSION
