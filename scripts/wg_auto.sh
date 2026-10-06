#!/bin/bash
# wg_auto.sh — monte/démonte wg0 selon la localisation de PC1
# 🏠 Maison (PC4 joignable direct LAN) → wg0 DOWN | 🧳 Déplacement → wg0 UP
# Auteur : hprzeta — Projet Riemann_Lab
# Usage : wg_auto.sh [--quiet]

LOG="$HOME/projet_zeta/logs/wg_auto.log"
# Adresses du cluster : fichier LOCAL hors git (jamais d'IP en dur dans le dépôt)
HOTES="$HOME/.config/zeta/cluster_hosts.env"
if [ ! -r "$HOTES" ]; then                   # absent : on ne touche PAS au tunnel
    echo "$(date '+%F %T') | wg_auto | fichier d'adresses absent : $HOTES" >> "$LOG"
    exit 1
fi
. "$HOTES"                                   # définit ZETA_PC4 et ZETA_BASTION
PC4_LAN="$ZETA_PC4"

notifier() {  # $1 = titre, $2 = message, $3 = icône
    echo "$1 — $2"
    echo "$(date '+%F %T') | $1 | $2" >> "$LOG"
    command -v notify-send > /dev/null && \
        DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u riemann)/bus \
        notify-send -i "$3" "$1" "$2" 2>/dev/null
}

# Ping en forçant l'interface physique (jamais wg0, sinon test faussé)
IFACE=$(ip route | awk '/default/ {print $5; exit}' | grep -v wg0)
[ -z "$IFACE" ] && IFACE=$(ip -o link | awk -F': ' '!/lo|wg/ {print $2; exit}')

# IPv6 globale disponible ? (exclut fe80:: lien-local)
# Sans elle, l'endpoint DuckDNS (IPv6 seul) est injoignable par construction —
# ce n'est pas une panne du tunnel, inutile de tenter/réparer/notifier.
a_ipv6_globale() {
    ip -6 addr show scope global 2>/dev/null | grep -q inet6
}

if ping -c 1 -W 1 -I "$IFACE" "$PC4_LAN" > /dev/null 2>&1; then
    # ═══ MAISON ═══
    if sudo wg show wg0 > /dev/null 2>&1; then
        sudo wg-quick down wg0
        notifier "🏠 MAISON — WireGuard DÉSACTIVÉ" "LAN direct (PC4 joignable). Cluster accessible en 192.168.1.x" "network-wired"
    else
        [ "$1" != "--quiet" ] && notifier "🏠 MAISON — WireGuard déjà désactivé" "LAN direct, rien à faire" "network-wired"
    fi
else
    # ═══ DÉPLACEMENT ═══
    if ! a_ipv6_globale; then
        # Pas d'IPv6 globale (VPN tiers actif, opérateur, etc.) : on attend le
        # prochain event réseau en silence — pas de wg-quick, pas de notify-send.
        echo "$(date '+%F %T') | (silencieux) pas d'IPv6 globale — cycle ignoré" >> "$LOG"
        exit 0
    fi

    if ! sudo wg show wg0 > /dev/null 2>&1; then
        sudo wg-quick up wg0
        sleep 2
        if ping -c 1 -W 3 "$ZETA_BASTION" > /dev/null 2>&1; then
            notifier "🧳 DÉPLACEMENT — WireGuard ACTIVÉ" "Tunnel OK, cluster accessible via le bastion" "network-vpn"
        else
            notifier "⚠️ DÉPLACEMENT — WireGuard activé mais tunnel NE RÉPOND PAS" "Vérifier connexion internet / endpoint DuckDNS" "dialog-warning"
        fi
    else
        # wg0 existe — mais est-il VIVANT ? On teste le handshake, pas juste la présence.
        if ping -c 1 -W 3 "$ZETA_BASTION" > /dev/null 2>&1; then
            [ "$1" != "--quiet" ] && notifier "🧳 DÉPLACEMENT — WireGuard OK" "Tunnel vivant (le bastion répond)" "network-vpn"
        else
            notifier "🧳 DÉPLACEMENT — tunnel MORT, réparation" "wg0 présent sans handshake — relance" "dialog-warning"
            sudo wg-quick down wg0 2>/dev/null
            sudo wg-quick up wg0
            sleep 2
            if ping -c 1 -W 3 "$ZETA_BASTION" > /dev/null 2>&1; then
                notifier "🧳 DÉPLACEMENT — WireGuard RÉPARÉ" "Tunnel rétabli, cluster via le bastion" "network-vpn"
            else
                notifier "⚠️ DÉPLACEMENT — échec réparation" "Vérifier internet / endpoint DuckDNS" "dialog-warning"
            fi
        fi
    fi
fi

exit 0
