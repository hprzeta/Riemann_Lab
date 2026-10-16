#!/bin/bash
# zeta_turbo_on.sh — Active le « turbo » Zêta de la SESSION. IDEMPOTENT.
# Auteur : hprzeta — Projet Riemann_Lab — réécrit le 2026-10-16 (ancienne version : .bak-20261016)
#
# Cycle de vie (voir CLAUDE.md « SCRIPTS TURBO ») :
#   début de session (hook SessionStart) -> zeta_turbo_on.sh              (CPU + swappiness)
#   gros run (zeta_run.sh)               -> zeta_turbo_on.sh --services   (+ arrêt des services)
#   fin de run                           -> zeta_turbo_off.sh --services  (services seuls ; le turbo CPU RESTE)
#   « bye bye »                          -> zeta_turbo_off.sh             (restaure l'état INITIAL réel)
#
# Ce que fait le script :
#   * sauvegarde l'état INITIAL réel (gouverneur + EPP de CHAQUE CPU, swappiness) AVANT toute
#     modification, dans /run/zeta_turbo/state (root:adm 0640) ; un 2e appel NE réécrit JAMAIS cette
#     sauvegarde (il ré-affirme seulement l'état turbo, utile si power-profiles-daemon l'a défait) ;
#   * gouverneur CPU -> performance, vm.swappiness -> 10 ;
#   * avec --services : arrête les services non essentiels et les consigne dans l'état ;
#   * RELIT l'état réel après application : "TURBO: ACTIF (vérifié)" n'est affiché que s'il l'est.
#   * Le boost matériel (intel_pstate/no_turbo) n'est PAS modifié : il est seulement rapporté.
#
# Codes de sortie : 0 ok (vérifié) · 2 droits root absents · 3 état invalide / erreur d'état ·
#                   4 application partielle ou non vérifiée · 6 interface CPU absente · 64 usage
# Après un arrêt brutal : l'état reste dans /run (tmpfs) -> zeta_turbo_off.sh restaure correctement.
# Après un redémarrage : /run est vidé ET le système revient à ses valeurs par défaut : rien à restaurer.
# Aucune restauration automatique n'est faite après un crash (ce n'est pas implémenté).
#
# Tests : ZETA_TURBO_SYSROOT et ZETA_TURBO_STATE_DIR (arbre factice) ne sont honorés QUE hors root.
set -u
umask 077

# ── Mode d'exécution : root réel, ou test hors root sur un arbre factice ─────────────────────────
if [ "$(id -u)" -eq 0 ]; then
    PATH=/usr/sbin:/usr/bin:/sbin:/bin; export PATH
    unset ZETA_TURBO_SYSROOT ZETA_TURBO_STATE_DIR      # jamais honorés en root
    SYSROOT=""; STATE_DIR="/run/zeta_turbo"; MODE_TEST=0
elif [ -n "${ZETA_TURBO_SYSROOT:-}" ] && [ -n "${ZETA_TURBO_STATE_DIR:-}" ]; then
    SYSROOT="$ZETA_TURBO_SYSROOT"; STATE_DIR="$ZETA_TURBO_STATE_DIR"; MODE_TEST=1
else
    echo "ERREUR : droits root requis (lancer via sudo)." >&2
    echo "TURBO: NON ACTIF (droits root absents)"
    exit 2
fi

AVEC_SERVICES=0
for arg in "$@"; do
    case "$arg" in
        --services) AVEC_SERVICES=1 ;;
        -h|--help)  sed -n '2,30p' "$0"; exit 0 ;;
        *) echo "Usage : zeta_turbo_on.sh [--services]" >&2; exit 64 ;;
    esac
done

CPU_ROOT="$SYSROOT/sys/devices/system/cpu"
SWAP_FILE="$SYSROOT/proc/sys/vm/swappiness"
NOTURBO_FILE="$CPU_ROOT/intel_pstate/no_turbo"
SWAP_CIBLE=10
SERVICES=(cups avahi-daemon bluetooth ModemManager NetworkManager-wait-online snapd
          packagekit apt-daily apt-daily-upgrade fwupd whoopsie kerneloops)

# ── Dossier d'état : propriétaire root, pas de lien symbolique, verrou ───────────────────────────
if [ "$MODE_TEST" -eq 0 ]; then
    if [ -L "$STATE_DIR" ] || { [ -e "$STATE_DIR" ] && [ ! -d "$STATE_DIR" ]; }; then
        echo "ERREUR : $STATE_DIR n'est pas un dossier sûr." >&2; echo "TURBO: NON ACTIF (dossier d'état douteux)"; exit 3
    fi
    GRP=root; getent group adm >/dev/null 2>&1 && GRP=adm
    install -d -m 0750 -o root -g "$GRP" "$STATE_DIR" || { echo "TURBO: NON ACTIF (dossier d'état)"; exit 3; }
    [ "$(stat -c %u "$STATE_DIR")" = "0" ] || { echo "ERREUR : $STATE_DIR n'appartient pas à root." >&2; echo "TURBO: NON ACTIF (dossier d'état douteux)"; exit 3; }
else
    GRP=""; mkdir -p "$STATE_DIR"
fi
STATE="$STATE_DIR/state"
exec 9>"$STATE_DIR/lock"
flock -w 10 9 || { echo "ERREUR : verrou occupé depuis plus de 10 s." >&2; echo "TURBO: NON ACTIF (verrou)"; exit 3; }

# ── Fonctions ───────────────────────────────────────────────────────────────────────────────────
cpu_dirs() { local d; for d in "$CPU_ROOT"/cpu[0-9]*/cpufreq; do [ -f "$d/scaling_governor" ] && echo "$d"; done; return 0; }
cpu_id()   { local p="${1%/cpufreq}"; echo "${p##*/cpu}"; }
lire()     { [ -r "$1" ] && tr -d '\n' < "$1" || echo "-"; }

state_get() { sed -n "s/^$1=//p" "$STATE" 2>/dev/null | tail -1; }
state_valid() {
    [ -f "$STATE" ] || return 1
    # Seules des lignes « clé=valeur » strictes (ou commentaires/vides) sont acceptées.
    if grep -q -v -E '^(#.*|[a-z0-9_]+=[A-Za-z0-9_.,:+-]*|)$' "$STATE"; then return 1; fi
    [ "$(state_get version)" = "1" ] || return 1
    [ "$(state_get active)" = "1" ] || return 1
    state_get swap_initial | grep -q -E '^[0-9]+$' || return 1
    grep -q -E '^cpu_gov_[0-9]+=[a-z_]+$' "$STATE" || return 1
    return 0
}
state_perms() { chmod 0640 "$1"; [ "$MODE_TEST" -eq 1 ] || chgrp "$GRP" "$1"; }
state_set() {   # remplace/ajoute une clé de façon atomique (tmp + mv)
    local k="$1" v="$2" tmp="$STATE_DIR/.state.$$"
    { grep -v -E "^$k=" "$STATE" 2>/dev/null; printf '%s=%s\n' "$k" "$v"; } > "$tmp" \
        && state_perms "$tmp" && mv -f "$tmp" "$STATE"
}

# ── Interface CPU ───────────────────────────────────────────────────────────────────────────────
if [ -z "$(cpu_dirs)" ]; then
    echo "ERREUR : aucune interface cpufreq (scaling_governor) trouvée — rien modifié." >&2
    echo "TURBO: NON ACTIF (interface CPU absente)"
    exit 6
fi
while IFS= read -r d; do
    if [ -r "$d/scaling_available_governors" ] && ! grep -q -w performance "$d/scaling_available_governors"; then
        echo "ERREUR : le gouverneur « performance » n'est pas disponible sur cpu$(cpu_id "$d") — rien modifié." >&2
        echo "TURBO: NON ACTIF (gouverneur performance indisponible)"
        exit 6
    fi
done < <(cpu_dirs)

# ── État : réutiliser l'état INITIAL existant, ou le créer AVANT toute modification ─────────────
if [ -e "$STATE" ]; then
    if ! state_valid; then
        echo "ERREUR : état sauvegardé INVALIDE ($STATE) — rien modifié, fichier conservé." >&2
        echo "  Inspecter le fichier, ou : sudo zeta_turbo_off.sh --force-defaults" >&2
        echo "TURBO: NON ACTIF (état invalide)"
        exit 3
    fi
    echo "  = Turbo déjà géré : état INITIAL conservé (enregistré le $(state_get started_at)) — ré-affirmation."
else
    DEJA=1
    while IFS= read -r d; do [ "$(lire "$d/scaling_governor")" = "performance" ] || DEJA=0; done < <(cpu_dirs)
    TMP="$STATE_DIR/.state.$$"
    {
        echo "# zeta_turbo — état INITIAL avant activation (ne pas éditer)"
        echo "version=1"
        echo "active=1"
        echo "started_at=$(date +%Y%m%dT%H%M%S)"
        echo "started_by=$(printf '%s' "${SUDO_USER:-inconnu}" | tr -cd 'A-Za-z0-9_.-')"
        echo "turbo_deja_actif=$DEJA"
        echo "swap_initial=$(lire "$SWAP_FILE")"
        while IFS= read -r d; do
            id="$(cpu_id "$d")"
            echo "cpu_gov_$id=$(lire "$d/scaling_governor")"
            echo "cpu_epp_$id=$(lire "$d/energy_performance_preference")"
        done < <(cpu_dirs)
        echo "services="
    } > "$TMP" && state_perms "$TMP" && mv -f "$TMP" "$STATE" || { echo "TURBO: NON ACTIF (écriture de l'état impossible)"; exit 3; }
    state_valid || { echo "ERREUR : l'état qui vient d'être écrit est invalide." >&2; echo "TURBO: NON ACTIF (état)"; exit 3; }
    [ "$DEJA" = "1" ] && echo "  ! Le gouverneur était déjà « performance » : état initial enregistré tel quel (sera restauré tel quel)."
    echo "  + État initial enregistré : $STATE"
fi

# ── Application ─────────────────────────────────────────────────────────────────────────────────
ECHECS=()
while IFS= read -r d; do
    id="$(cpu_id "$d")"
    if [ "$(lire "$d/scaling_governor")" != "performance" ]; then
        echo performance > "$d/scaling_governor" 2>/dev/null || ECHECS+=("cpu$id : écriture du gouverneur refusée")
    fi
done < <(cpu_dirs)

if [ "$(lire "$SWAP_FILE")" != "$SWAP_CIBLE" ]; then
    echo "$SWAP_CIBLE" > "$SWAP_FILE" 2>/dev/null || ECHECS+=("swappiness : écriture refusée")
fi

if [ "$AVEC_SERVICES" -eq 1 ]; then
    LISTE="$(state_get services)"
    for svc in "${SERVICES[@]}"; do
        if systemctl is-active --quiet "$svc" 2>/dev/null; then
            if systemctl stop "$svc" 2>/dev/null; then
                case ",$LISTE," in *",$svc,"*) ;; *) LISTE="${LISTE:+$LISTE,}$svc" ;; esac
                state_set services "$LISTE" || ECHECS+=("état : enregistrement de $svc impossible")
            else
                ECHECS+=("service $svc : arrêt refusé")
            fi
        fi
    done
fi

# ── Vérification sur l'ÉTAT RÉEL ────────────────────────────────────────────────────────────────
NB=0; NOK=0
while IFS= read -r d; do
    NB=$((NB+1)); [ "$(lire "$d/scaling_governor")" = "performance" ] && NOK=$((NOK+1)) || ECHECS+=("cpu$(cpu_id "$d") : gouverneur = $(lire "$d/scaling_governor") (attendu performance)")
done < <(cpu_dirs)
[ "$(lire "$SWAP_FILE")" = "$SWAP_CIBLE" ] || ECHECS+=("swappiness = $(lire "$SWAP_FILE") (attendu $SWAP_CIBLE)")
if [ "$AVEC_SERVICES" -eq 1 ]; then
    IFS=',' read -r -a ARRET <<< "$(state_get services)"
    for svc in "${ARRET[@]:-}"; do
        [ -z "$svc" ] && continue
        ! systemctl is-active --quiet "$svc" 2>/dev/null || ECHECS+=("service $svc encore actif")
    done
fi
NT="$(lire "$NOTURBO_FILE")"
case "$NT" in
    0) BOOST="boost matériel actif (no_turbo=0, non modifié)" ;;
    1) BOOST="ATTENTION boost matériel DÉSACTIVÉ (no_turbo=1) — non modifié par ce script" ;;
    *) BOOST="boost matériel : interface no_turbo absente (non modifié)" ;;
esac

echo "  Gouverneur performance : $NOK/$NB CPU · swappiness $(lire "$SWAP_FILE") · $BOOST"
if [ "${#ECHECS[@]}" -eq 0 ]; then
    echo "TURBO: ACTIF (vérifié : performance $NOK/$NB CPU, swappiness $(lire "$SWAP_FILE"))"
    exit 0
fi
for e in "${ECHECS[@]}"; do echo "  ✗ $e" >&2; done
echo "TURBO: PARTIEL (${#ECHECS[@]} anomalie(s) ; l'état initial est conservé, zeta_turbo_off.sh restaurera)"
exit 4
