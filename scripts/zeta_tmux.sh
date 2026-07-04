#!/bin/bash

# Bascule WireGuard automatique maison/déplacement (avec message d'état)
bash "$(dirname "$0")/wg_auto.sh"

SESSION="zeta-cluster"
tmux kill-session -t $SESSION 2>/dev/null
tmux new-session -d -s $SESSION -x 220 -y 50
tmux split-window -h -t $SESSION
tmux select-pane -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.2
tmux select-pane -t $SESSION:0.0 -P 'bg=yellow,fg=black'
tmux send-keys -t $SESSION:0.0 "ssh -i ~/.ssh/id_acer -o IdentitiesOnly=yes hprzeta@192.168.1.52" Enter
sleep 1
tmux select-pane -t $SESSION:0.1 -P 'bg=cyan,fg=black'
tmux send-keys -t $SESSION:0.1 "ssh -i ~/.ssh/id_acer -o IdentitiesOnly=yes hprzeta@192.168.1.22" Enter
sleep 1
tmux select-pane -t $SESSION:0.2 -P 'bg=black,fg=green'
tmux send-keys -t $SESSION:0.2 "ssh -i ~/.ssh/id_acer -o IdentitiesOnly=yes hprzeta@192.168.1.54" Enter
sleep 1
tmux select-pane -t $SESSION:0.3 -P 'bg=magenta,fg=white'
tmux send-keys -t $SESSION:0.3 "cd ~/projet_zeta && source zeta_env/bin/activate" Enter
tmux send-keys -t $SESSION:0.4 "cd ~/projet_zeta && source zeta_env/bin/activate && python3 scripts/zeta_monitor.py" Enter
tmux attach-session -t $SESSION
