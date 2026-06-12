#!/bin/bash
# zeta_turbo_on.sh — Optimise le système pour un run de calcul zeta
# Arrête les services non essentiels, passe le CPU en performance, réduit swap
# Doit être exécuté avec sudo
# Auteur : hprzeta — Projet Riemann_Lab
# MAJ : 2026-06-10

set -e
STATE_FILE="/tmp/zeta_turbo_state.txt"

echo "=== zeta_turbo_on.sh — Optimisation système pour calcul zeta ==="

# Sauvegarder l'état initial pour restauration propre
echo "# État sauvegardé par zeta_turbo_on.sh — $(date)" > "$STATE_FILE"
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null >> "$STATE_FILE" \
    && echo "governor_saved=1" >> "$STATE_FILE" || echo "governor_saved=0" >> "$STATE_FILE"
cat /proc/sys/vm/swappiness >> "$STATE_FILE" 2>/dev/null || echo "60" >> "$STATE_FILE"

# CPU governor → performance (fréquence max, +15–30 % calcul)
if command -v cpupower &>/dev/null; then
    cpupower frequency-set -g performance
    echo "  ✅  CPU governor → performance"
elif ls /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor &>/dev/null; then
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo performance > "$cpu"
    done
    echo "  ✅  CPU governor → performance (via sysfs)"
else
    echo "  ⚠️   cpupower absent — governor non modifié"
fi

# Swappiness → 10 (évite le swap des workers Python sous charge)
SWAPPINESS_AVANT=$(cat /proc/sys/vm/swappiness)
sysctl -w vm.swappiness=10 > /dev/null
echo "  ✅  swappiness : $SWAPPINESS_AVANT → 10"
echo "swappiness_avant=$SWAPPINESS_AVANT" >> "$STATE_FILE"

# Arrêter services non essentiels (libère ~143 MB RAM)
SERVICES=(
    "cups"
    "avahi-daemon"
    "bluetooth"
    "ModemManager"
    "NetworkManager-wait-online"
    "snapd"
    "packagekit"
    "apt-daily"
    "apt-daily-upgrade"
    "fwupd"
    "whoopsie"
    "kerneloops"
)

echo "  Arrêt des services non essentiels..."
STOPPED=0
for svc in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$svc" 2>/dev/null; then
        systemctl stop "$svc" 2>/dev/null && echo "    - $svc arrêté" && STOPPED=$((STOPPED+1)) || true
        echo "stopped_$svc=1" >> "$STATE_FILE"
    fi
done
echo "  ✅  $STOPPED services arrêtés"

echo ""
echo "  État sauvegardé : $STATE_FILE"
echo "  Lancer zeta_turbo_off.sh après le run pour restaurer."
echo "=== Système optimisé pour le calcul ==="
