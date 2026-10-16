#!/bin/bash
# zeta_session_turbo.sh — Enveloppe SANS privilège du cycle de vie du turbo Zêta (début / fin de session).
# Auteur : hprzeta — Projet Riemann_Lab — créé le 2026-10-16
#
# Usage : zeta_session_turbo.sh start | end | status
#   start   appelé par le hook SessionStart (.claude/settings.local.json) : active le turbo (CPU + swappiness).
#           N'échoue JAMAIS (code 0) pour ne pas bloquer l'ouverture de session ; affiche UNE ligne claire
#           « Turbo Zêta : ACTIF (vérifié…) » ou « Turbo Zêta : NON ACTIF — cause ».
#   end     appelé en PREMIÈRE étape garantie du « bye bye » : restaure l'état initial réel, vérifie, rapporte.
#           Code de sortie = celui de zeta_turbo_off.sh (≠ 0 si la restauration est incomplète).
#   status  état réel (lecture seule).
# Les actions privilégiées passent par « sudo -n » sur les DEUX scripts déjà autorisés (NOPASSWD) ;
# aucune règle sudoers supplémentaire. Si des copies durcies existent (/usr/local/sbin/zeta_turbo_on|off,
# propriétaire root, non modifiables), elles sont utilisées de préférence (voir CLAUDE.md, durcissement).
# Journal : logs/turbo_session.log (ignoré par git). Tests : ZETA_SUDO, ZETA_TURBO_BIN_DIR, ZETA_TURBO_LOG.
set -u
BIN_DIR="${ZETA_TURBO_BIN_DIR:-$(cd "$(dirname "$(readlink -f "$0")")" && pwd)}"
LOG="${ZETA_TURBO_LOG:-$BIN_DIR/../logs/turbo_session.log}"
SUDO="${ZETA_SUDO:-sudo -n}"
MODE="${1:-}"

choisir() {   # $1 = on|off ; préfère la copie durcie root:root non modifiable par d'autres
    local dur="/usr/local/sbin/zeta_turbo_$1"
    if [ -x "$dur" ] && [ "$(stat -c %u "$dur" 2>/dev/null)" = "0" ] && [ -z "$(find "$dur" -perm /022 2>/dev/null)" ]; then
        echo "$dur"
    else
        echo "$BIN_DIR/zeta_turbo_$1.sh"
    fi
}
journal() { mkdir -p "$(dirname "$LOG")" 2>/dev/null; printf '[%s] %s\n' "$(date +%Y-%m-%dT%H:%M:%S)" "$*" >> "$LOG" 2>/dev/null; }

lancer() {    # $1 = on|off ; reste = arguments. Remplit OUT et RC.
    local s; s="$(choisir "$1")"; shift
    # shellcheck disable=SC2086
    OUT="$($SUDO "$s" "$@" 2>&1)"; RC=$?
    journal "$(basename "$s") $* -> rc=$RC"
    [ -n "$OUT" ] && printf '%s\n' "$OUT" | sed 's/^/    /' >> "$LOG" 2>/dev/null
}
resume() { printf '%s\n' "$OUT" | grep '^TURBO:' | tail -1; }
cause_privilege() {
    case "$OUT" in
        *"mot de passe"*|*"password"*|*"sudo:"*) echo "privilèges : sudo sans mot de passe indisponible pour $(choisir on) — lancer « sudo $(choisir on) » dans un terminal, ou voir CLAUDE.md (SCRIPTS TURBO)" ;;
        *) local der; der="$(printf '%s\n' "$OUT" | tail -1)"; echo "${der:-aucune sortie} (code $RC)" ;;
    esac
}

case "$MODE" in
    start)
        lancer on
        if [ "$RC" -eq 0 ] && [ -n "$(resume)" ]; then
            echo "Turbo Zêta : $(resume | sed 's/^TURBO: //') — restauré automatiquement au « bye bye » (zeta_session_turbo.sh end)."
        else
            echo "Turbo Zêta : NON ACTIF — $(cause_privilege) (détails : logs/turbo_session.log)"
        fi
        exit 0 ;;
    end)
        lancer off
        if [ "$RC" -eq 0 ] && [ -n "$(resume)" ]; then
            echo "Turbo Zêta : $(resume | sed 's/^TURBO: //')"; exit 0
        fi
        echo "Turbo Zêta : ERREUR À LA RESTAURATION — $( [ -n "$(resume)" ] && resume | sed 's/^TURBO: //' || cause_privilege ) (rc=$RC ; détails : logs/turbo_session.log ; état conservé)"
        exit "${RC:-1}" ;;
    status)
        exec "$BIN_DIR/zeta_turbo_status.sh" ;;
    *)
        echo "Usage : zeta_session_turbo.sh start | end | status" >&2; exit 64 ;;
esac
