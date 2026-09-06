#!/bin/bash

# Bascule WireGuard automatique maison/déplacement (avec message d'état)
bash "$(dirname "$0")/wg_auto.sh"

# ─── Détection maison / déplacement (tunnel déjà positionné par wg_auto.sh) ───
if ping -c1 -W2 10.10.0.1 >/dev/null 2>&1; then
    echo "🧳 DÉPLACEMENT — accès cluster via bastion 10.10.0.1"
    SSH_PC2="$SSH_PC2"
    SSH_PC3="$SSH_PC3"
    SSH_PC4="$SSH_PC4"
else
    echo "🏠 MAISON — accès cluster direct en 192.168.1.x"
    SSH_PC2="ssh -i ~/.ssh/zeta_cluster -o IdentitiesOnly=yes hprzeta@192.168.1.52"
    SSH_PC3="ssh -i ~/.ssh/zeta_cluster -o IdentitiesOnly=yes hprzeta@192.168.1.22"
    SSH_PC4="ssh -i ~/.ssh/zeta_cluster -o IdentitiesOnly=yes hprzeta@192.168.1.54"
fi

SESSION="zeta-cluster"
tmux kill-session -t $SESSION 2>/dev/null
tmux new-session -d -s $SESSION -x 220 -y 50
tmux split-window -h -t $SESSION
tmux select-pane -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.2
tmux select-pane -t $SESSION:0.0 -P 'bg=yellow,fg=black'
tmux send-keys -t $SESSION:0.0 "ssh -i ~/.ssh/zeta_cluster -o IdentitiesOnly=yes -J hprzeta@10.10.0.1 hprzeta@192.168.1.52" Enter
sleep 1
tmux select-pane -t $SESSION:0.1 -P 'bg=cyan,fg=black'
tmux send-keys -t $SESSION:0.1 "ssh -i ~/.ssh/zeta_cluster -o IdentitiesOnly=yes -J hprzeta@10.10.0.1 hprzeta@192.168.1.22" Enter
sleep 1
tmux select-pane -t $SESSION:0.2 -P 'bg=black,fg=green'
tmux send-keys -t $SESSION:0.2 "ssh -i ~/.ssh/zeta_cluster -o IdentitiesOnly=yes hprzeta@10.10.0.1" Enter
sleep 1
tmux select-pane -t $SESSION:0.3 -P 'bg=magenta,fg=white'
tmux send-keys -t $SESSION:0.3 "cd ~/projet_zeta && source zeta_env/bin/activate" Enter
tmux send-keys -t $SESSION:0.4 "cd ~/projet_zeta && source zeta_env/bin/activate && python3 scripts/zeta_monitor.py" Enter
tmux attach-session -t $SESSION
