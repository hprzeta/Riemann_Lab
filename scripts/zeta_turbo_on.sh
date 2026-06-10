#!/usr/bin/env bash
# zeta_turbo_on.sh — Optimisation système avant run Riemann_Lab
# Arrête les services non essentiels, passe le CPU en performance, désactive
# les animations GNOME. Lance zeta_turbo_off.sh pour restaurer.
# Usage : sudo ./scripts/zeta_turbo_on.sh
# Auteur : hprzeta — MAJ 2026-06-10

set -euo pipefail

# ─── Constantes ───────────────────────────────────────────────────────────────
PROJET_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${PROJET_DIR}/logs"
LOG_FILE="${LOG_DIR}/zeta_turbo_$(date +%Y%m%d_%H%M%S).log"
STATE_FILE="/tmp/zeta_turbo_state.txt"

# Services à arrêter (ne jamais toucher au réseau ni à nvidia-persistenced)
SERVICES_A_ARRETER=(
    bluetooth.service
    cups.service
    cups-browsed.service
    avahi-daemon.service
    colord.service
    fwupd.service
    iio-sensor-proxy.service
    ModemManager.service
    snap.canonical-livepatch.canonical-livepatchd.service
    unattended-upgrades.service
    gnome-remote-desktop.service
    ollama.service
)

# ─── Fonctions ────────────────────────────────────────────────────────────────
log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG_FILE"; }

ram_libre_mb() {
    awk '/MemAvailable/ {printf "%.0f", $2/1024}' /proc/meminfo
}

ram_process_mb() {
    local pid=$1
    [ -f "/proc/${pid}/status" ] && awk '/VmRSS/ {printf "%.1f", $2/1024}' "/proc/${pid}/status" || echo "0"
}

gouverneur_actuel() {
    cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo "inconnu"
}

# ─── Vérification droits ──────────────────────────────────────────────────────
if [ "$(id -u)" -ne 0 ]; then
    echo "❌  Ce script requiert sudo. Relancer : sudo $0"
    exit 1
fi

mkdir -p "$LOG_DIR"
log "═══════════════════════════════════════════════════════════════"
log "   ZETA TURBO ON — Optimisation système Riemann_Lab"
log "═══════════════════════════════════════════════════════════════"

# ─── État AVANT ───────────────────────────────────────────────────────────────
RAM_AVANT=$(ram_libre_mb)
GOV_AVANT=$(gouverneur_actuel)
SWAP_AVANT=$(cat /proc/sys/vm/swappiness)
log "AVANT : RAM libre = ${RAM_AVANT} MB | CPU gov = ${GOV_AVANT} | swappiness = ${SWAP_AVANT}"

# Sauvegarder l'état pour la restauration
echo "GOV_AVANT=${GOV_AVANT}" > "$STATE_FILE"
echo "SWAP_AVANT=${SWAP_AVANT}" >> "$STATE_FILE"

# ─── TÂCHE 1 : Arrêt des services ─────────────────────────────────────────────
log ""
log "── Services non essentiels ──────────────────────────────────────"
printf "%-55s %-10s %-10s %s\n" "Service" "RAM avant" "RAM après" "Action" | tee -a "$LOG_FILE"
printf "%-55s %-10s %-10s %s\n" "───────────────────────────────────────────────────" "─────────" "─────────" "──────" | tee -a "$LOG_FILE"

SERVICES_ARRETES=()
RAM_LIBEREE_TOTAL=0

for svc in "${SERVICES_A_ARRETER[@]}"; do
    # Vérifier si le service est actif
    if systemctl is-active --quiet "$svc" 2>/dev/null; then
        pid=$(systemctl show "$svc" -p MainPID 2>/dev/null | cut -d= -f2)
        ram_avant=$(ram_process_mb "$pid")

        systemctl stop "$svc" 2>/dev/null && ACTION="arrêté ✅" || ACTION="échec ⚠️"

        SERVICES_ARRETES+=("$svc")
        RAM_LIBEREE_TOTAL=$(echo "$RAM_LIBEREE_TOTAL + ${ram_avant:-0}" | bc)
        printf "%-55s %-10s %-10s %s\n" "$svc" "${ram_avant} MB" "0 MB" "$ACTION" | tee -a "$LOG_FILE"
        log "  → ${svc} : ${ram_avant} MB libérés"
    else
        printf "%-55s %-10s %-10s %s\n" "$svc" "—" "—" "déjà inactif" | tee -a "$LOG_FILE"
    fi
done

# Sauvegarder la liste des services effectivement arrêtés
echo "SERVICES_ARRETES=${SERVICES_ARRETES[*]}" >> "$STATE_FILE"

# ─── TÂCHE 2 : Gouverneur CPU → performance ────────────────────────────────────
log ""
log "── Gouverneur CPU ───────────────────────────────────────────────"
if [ -d /sys/devices/system/cpu/cpu0/cpufreq ]; then
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo "performance" > "$cpu" 2>/dev/null || true
    done
    GOV_APRES=$(gouverneur_actuel)
    log "  CPU governor : ${GOV_AVANT} → ${GOV_APRES} ✅  (${NPROC:-$(nproc)} cœurs)"
else
    log "  ⚠️  cpufreq non disponible — gouverneur inchangé"
fi

# ─── TÂCHE 3 : Swappiness → 10 ────────────────────────────────────────────────
log ""
log "── Swappiness ───────────────────────────────────────────────────"
sysctl -w vm.swappiness=10 >> "$LOG_FILE" 2>&1
SWAP_APRES=$(cat /proc/sys/vm/swappiness)
log "  swappiness : ${SWAP_AVANT} → ${SWAP_APRES} ✅"

# ─── TÂCHE 4 : Animations GNOME ───────────────────────────────────────────────
log ""
log "── Animations GNOME ─────────────────────────────────────────────"
ANIM_AVANT=$(sudo -u "$SUDO_USER" DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u $SUDO_USER)/bus" \
    gsettings get org.gnome.desktop.interface enable-animations 2>/dev/null || echo "inconnu")
echo "ANIM_AVANT=${ANIM_AVANT}" >> "$STATE_FILE"

sudo -u "$SUDO_USER" DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u $SUDO_USER)/bus" \
    gsettings set org.gnome.desktop.interface enable-animations false 2>/dev/null \
    && log "  Animations GNOME : ${ANIM_AVANT} → false ✅" \
    || log "  ⚠️  Impossible de modifier les animations GNOME"

# ─── Résumé APRÈS ─────────────────────────────────────────────────────────────
sleep 1
RAM_APRES=$(ram_libre_mb)
RAM_GAIN=$((RAM_APRES - RAM_AVANT))

log ""
log "═══════════════════════════════════════════════════════════════"
log "   RÉSUMÉ OPTIMISATION"
log "═══════════════════════════════════════════════════════════════"
log "  Services arrêtés   : ${#SERVICES_ARRETES[@]}"
log "  RAM libérée (proc) : ~${RAM_LIBEREE_TOTAL} MB"
log "  RAM libre avant    : ${RAM_AVANT} MB"
log "  RAM libre après    : ${RAM_APRES} MB"
log "  Gain RAM réel      : +${RAM_GAIN} MB"
log "  CPU governor       : ${GOV_AVANT} → $(gouverneur_actuel)"
log "  swappiness         : ${SWAP_AVANT} → ${SWAP_APRES}"
log "  Log                : ${LOG_FILE}"
log "═══════════════════════════════════════════════════════════════"
log "  ✅  Système optimisé — prêt pour le run Riemann_Lab"
log "  ℹ️  Pour restaurer : sudo ./scripts/zeta_turbo_off.sh"
log "═══════════════════════════════════════════════════════════════"
