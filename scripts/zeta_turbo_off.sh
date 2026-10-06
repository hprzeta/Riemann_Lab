#!/bin/bash
# zeta_turbo_off.sh — Restaure le système après un run de calcul zeta
# Remet le CPU en powersave, restaure le swappiness, redémarre les services
# Doit être exécuté avec sudo
# Auteur : hprzeta — Projet Riemann_Lab
# MAJ : 2026-06-10

STATE_FILE="/tmp/zeta_turbo_state.txt"

echo "=== zeta_turbo_off.sh — Restauration système post-calcul ==="

# CPU governor → powersave (économie d'énergie)
if command -v cpupower &>/dev/null; then
    cpupower frequency-set -g powersave 2>/dev/null || cpupower frequency-set -g ondemand
    echo "  ✅  CPU governor → powersave"
elif ls /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor &>/dev/null; then
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo powersave > "$cpu" 2>/dev/null || echo ondemand > "$cpu" 2>/dev/null || true
    done
    echo "  ✅  CPU governor → powersave (via sysfs)"
fi

# Restaurer swappiness depuis l'état sauvegardé
if [ -f "$STATE_FILE" ]; then
    SWAPPINESS_AVANT=$(grep "^swappiness_avant=" "$STATE_FILE" | cut -d= -f2)
    if [ -n "$SWAPPINESS_AVANT" ]; then
        sysctl -w vm.swappiness="$SWAPPINESS_AVANT" > /dev/null
        echo "  ✅  swappiness restauré → $SWAPPINESS_AVANT"
    else
        sysctl -w vm.swappiness=60 > /dev/null
        echo "  ✅  swappiness restauré → 60 (défaut)"
    fi
else
    sysctl -w vm.swappiness=60 > /dev/null
    echo "  ✅  swappiness restauré → 60 (défaut, pas d'état sauvegardé)"
fi

# Redémarrer les services arrêtés
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

echo "  Redémarrage des services essentiels..."
for svc in "${SERVICES[@]}"; do
    if [ -f "$STATE_FILE" ] && grep -q "stopped_${svc}=1" "$STATE_FILE"; then
        systemctl start "$svc" 2>/dev/null && echo "    - $svc redémarré" || true
    fi
done

# Nettoyer l'état sauvegardé
rm -f "$STATE_FILE"
echo "  ✅  État temporaire supprimé"
echo "=== Système restauré ==="
