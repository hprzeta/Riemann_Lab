#!/bin/bash
echo "=== SURVEILLANCE DU CALCUL ==="
echo "Heure : $(date)"
echo ""
echo "=== CPU ==="
top -bn1 | head -10
echo ""
echo "=== GPU ==="
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv
echo ""
echo "=== RAM ==="
free -h
echo -"=== Disque==="
df -h | grep -E "sda[0-9]"


