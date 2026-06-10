#!/usr/bin/env bash
# zeta_turbo_off.sh — Restauration système après run Riemann_Lab
# Relance les services arrêtés par zeta_turbo_on.sh, restaure les réglages.
# Usage : sudo ./scripts/zeta_turbo_off.sh
# Auteur : hprzeta — MAJ 2026-06-10

set -euo pipefail

# ─── Constantes ───────────────────────────────────────────────────────────────
PROJET_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${PROJET_DIR}/logs"
STATE_FILE="/tmp/zeta_turbo_state.txt"

# ─── Fonctions ────────────────────────────────────────────────────────────────
log() { echo "[$(date +%H:%M:%S)] $*"; }

ram_libre_mb() {
    awk '/MemAvailable/ {printf "%.0f", $2/1024}' /proc/meminfo
}

# ─── Vérification droits ──────────────────────────────────────────────────────
if [ "$(id -u)" -ne 0 ]; then
    echo "❌  Ce script requiert sudo. Relancer : sudo $0"
    exit 1
fi

log "═══════════════════════════════════════════════════════════════"
log "   ZETA TURBO OFF — Restauration système Riemann_Lab"
log "═══════════════════════════════════════════════════════════════"

RAM_AVANT=$(ram_libre_mb)

# ─── Charger l'état sauvegardé ────────────────────────────────────────────────
if [ ! -f "$STATE_FILE" ]; then
    log "⚠️  Fichier d'état introuvable : ${STATE_FILE}"
    log "    Restauration avec valeurs par défaut."
    GOV_AVANT="powersave"
    SWAP_AVANT=60
    ANIM_AVANT="true"
    SERVICES_ARRETES=()
else
    source "$STATE_FILE"
    GOV_AVANT="${GOV_AVANT:-powersave}"
    SWAP_AVANT="${SWAP_AVANT:-60}"
    ANIM_AVANT="${ANIM_AVANT:-true}"
    # Convertir la chaîne en tableau
    read -ra SERVICES_ARRETES <<< "${SERVICES_ARRETES:-}"
fi

log "Restauration : gov=${GOV_AVANT} | swappiness=${SWAP_AVANT} | animations=${ANIM_AVANT}"
log "Services à relancer : ${#SERVICES_ARRETES[@]}"

# ─── TÂCHE 1 : Relancer les services ──────────────────────────────────────────
log ""
log "── Relancement des services ─────────────────────────────────────"
for svc in "${SERVICES_ARRETES[@]}"; do
    systemctl start "$svc" 2>/dev/null \
        && log "  ✅  ${svc} relancé" \
        || log "  ⚠️  ${svc} — échec relancement (service peut-être masqué)"
done

# ─── TÂCHE 2 : Restaurer le gouverneur CPU ────────────────────────────────────
log ""
log "── Gouverneur CPU ───────────────────────────────────────────────"
if [ -d /sys/devices/system/cpu/cpu0/cpufreq ]; then
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo "${GOV_AVANT}" > "$cpu" 2>/dev/null || true
    done
    GOV_APRES=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo "inconnu")
    log "  CPU governor : performance → ${GOV_APRES} ✅"
fi

# ─── TÂCHE 3 : Restaurer swappiness ───────────────────────────────────────────
log ""
log "── Swappiness ───────────────────────────────────────────────────"
sysctl -w vm.swappiness="${SWAP_AVANT}" > /dev/null 2>&1
log "  swappiness : 10 → ${SWAP_AVANT} ✅"

# ─── TÂCHE 4 : Restaurer animations GNOME ────────────────────────────────────
log ""
log "── Animations GNOME ─────────────────────────────────────────────"
sudo -u "$SUDO_USER" DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u $SUDO_USER)/bus" \
    gsettings set org.gnome.desktop.interface enable-animations "${ANIM_AVANT}" 2>/dev/null \
    && log "  Animations GNOME → ${ANIM_AVANT} ✅" \
    || log "  ⚠️  Impossible de restaurer les animations GNOME"

# ─── Nettoyage ────────────────────────────────────────────────────────────────
rm -f "$STATE_FILE"

# ─── Résumé ───────────────────────────────────────────────────────────────────
sleep 1
RAM_APRES=$(ram_libre_mb)

log ""
log "═══════════════════════════════════════════════════════════════"
log "   RÉSUMÉ RESTAURATION"
log "═══════════════════════════════════════════════════════════════"
log "  Services relancés  : ${#SERVICES_ARRETES[@]}"
log "  RAM libre avant    : ${RAM_AVANT} MB"
log "  RAM libre après    : ${RAM_APRES} MB"
log "  CPU governor       : performance → ${GOV_AVANT}"
log "  swappiness         : 10 → ${SWAP_AVANT}"
log "═══════════════════════════════════════════════════════════════"
log "  ✅  Système restauré — état normal"
log "═══════════════════════════════════════════════════════════════"
