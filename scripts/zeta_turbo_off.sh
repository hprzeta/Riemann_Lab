#!/bin/bash
# zeta_turbo_off.sh — Restaure l'état INITIAL réel enregistré par zeta_turbo_on.sh. IDEMPOTENT.
# Auteur : hprzeta — Projet Riemann_Lab — réécrit le 2026-10-16 (ancienne version : .bak-20261016)
#
# Modes :
#   (sans argument)   restauration COMPLÈTE : gouverneur + EPP de chaque CPU, swappiness, services
#                     arrêtés ; l'état n'est supprimé qu'APRÈS vérification de chaque élément.
#                     Tous les éléments sont tentés même si l'un échoue.
#   --services        redémarre SEULEMENT les services arrêtés par « on --services » ; le turbo CPU
#                     et l'état initial restent en place (fin d'un run, session toujours ouverte).
#   --force-defaults  secours si l'état est manquant/invalide : gouverneur « performance » -> « powersave »
#                     (CPU concernés seulement) ; ne touche NI à l'EPP, NI au swappiness, NI aux services ;
#                     un état invalide est mis de côté (state.invalid-<horodatage>), jamais supprimé.
#
# Ce script ne restaure JAMAIS « powersave » par hypothèse : il remet ce qui a été enregistré
# (si le gouverneur initial était déjà « performance », il reste « performance »).
#
# Codes de sortie : 0 ok (vérifié) ou rien à restaurer · 2 droits root absents · 3 état manquant
#                   (turbo apparemment actif) ou invalide · 5 restauration incomplète (état conservé) · 64 usage
# Voir zeta_turbo_on.sh pour le comportement après crash / redémarrage.
set -u
umask 077

if [ "$(id -u)" -eq 0 ]; then
    PATH=/usr/sbin:/usr/bin:/sbin:/bin; export PATH
    unset ZETA_TURBO_SYSROOT ZETA_TURBO_STATE_DIR
    SYSROOT=""; STATE_DIR="/run/zeta_turbo"; MODE_TEST=0
elif [ -n "${ZETA_TURBO_SYSROOT:-}" ] && [ -n "${ZETA_TURBO_STATE_DIR:-}" ]; then
    SYSROOT="$ZETA_TURBO_SYSROOT"; STATE_DIR="$ZETA_TURBO_STATE_DIR"; MODE_TEST=1
else
    echo "ERREUR : droits root requis (lancer via sudo)." >&2
    echo "TURBO: NON RESTAURÉ (droits root absents)"
    exit 2
fi

SEUL_SERVICES=0; FORCE=0
for arg in "$@"; do
    case "$arg" in
        --services)       SEUL_SERVICES=1 ;;
        --force-defaults) FORCE=1 ;;
        -h|--help)        sed -n '2,24p' "$0"; exit 0 ;;
        *) echo "Usage : zeta_turbo_off.sh [--services | --force-defaults]" >&2; exit 64 ;;
    esac
done
[ "$SEUL_SERVICES" -eq 1 ] && [ "$FORCE" -eq 1 ] && { echo "Usage : --services et --force-defaults sont exclusifs" >&2; exit 64; }

CPU_ROOT="$SYSROOT/sys/devices/system/cpu"
SWAP_FILE="$SYSROOT/proc/sys/vm/swappiness"

if [ "$MODE_TEST" -eq 0 ]; then
    if [ -L "$STATE_DIR" ] || { [ -e "$STATE_DIR" ] && [ ! -d "$STATE_DIR" ]; }; then
        echo "ERREUR : $STATE_DIR n'est pas un dossier sûr." >&2; echo "TURBO: NON RESTAURÉ (dossier d'état douteux)"; exit 3
    fi
    # Rien à verrouiller ni à créer si le dossier n'existe pas : aucun état n'a jamais été écrit.
    [ -d "$STATE_DIR" ] || { echo "  = Aucun état turbo (jamais activé depuis le démarrage) : rien à restaurer."; echo "TURBO: RIEN À RESTAURER"; exit 0; }
    [ "$(stat -c %u "$STATE_DIR")" = "0" ] || { echo "ERREUR : $STATE_DIR n'appartient pas à root." >&2; echo "TURBO: NON RESTAURÉ (dossier d'état douteux)"; exit 3; }
else
    mkdir -p "$STATE_DIR"
fi
STATE="$STATE_DIR/state"
exec 9>"$STATE_DIR/lock"
flock -w 10 9 || { echo "ERREUR : verrou occupé depuis plus de 10 s." >&2; echo "TURBO: NON RESTAURÉ (verrou)"; exit 3; }

cpu_dirs() { local d; for d in "$CPU_ROOT"/cpu[0-9]*/cpufreq; do [ -f "$d/scaling_governor" ] && echo "$d"; done; return 0; }
cpu_id()   { local p="${1%/cpufreq}"; echo "${p##*/cpu}"; }
lire()     { [ -r "$1" ] && tr -d '\n' < "$1" || echo "-"; }
state_get() { sed -n "s/^$1=//p" "$STATE" 2>/dev/null | tail -1; }
state_valid() {
    [ -f "$STATE" ] || return 1
    if grep -q -v -E '^(#.*|[a-z0-9_]+=[A-Za-z0-9_.,:+-]*|)$' "$STATE"; then return 1; fi
    [ "$(state_get version)" = "1" ] || return 1
    [ "$(state_get active)" = "1" ] || return 1
    state_get swap_initial | grep -q -E '^[0-9]+$' || return 1
    grep -q -E '^cpu_gov_[0-9]+=[a-z_]+$' "$STATE" || return 1
    return 0
}
state_perms() { chmod 0640 "$1"; [ "$MODE_TEST" -eq 1 ] || { local g=root; getent group adm >/dev/null 2>&1 && g=adm; chgrp "$g" "$1"; }; }
state_set() {
    local k="$1" v="$2" tmp="$STATE_DIR/.state.$$"
    { grep -v -E "^$k=" "$STATE" 2>/dev/null; printf '%s=%s\n' "$k" "$v"; } > "$tmp" \
        && state_perms "$tmp" && mv -f "$tmp" "$STATE"
}
turbo_semble_actif() { local d; while IFS= read -r d; do [ "$(lire "$d/scaling_governor")" = "performance" ] && return 0; done < <(cpu_dirs); return 1; }

# ── --force-defaults : secours explicite ────────────────────────────────────────────────────────
if [ "$FORCE" -eq 1 ]; then
    if [ -e "$STATE" ] && ! state_valid; then
        AIDE="$STATE_DIR/state.invalid-$(date +%Y%m%dT%H%M%S)"
        mv -f "$STATE" "$AIDE" && echo "  ! État invalide mis de côté : $AIDE"
    elif [ -e "$STATE" ]; then
        echo "  ! État valide présent : utiliser « zeta_turbo_off.sh » (sans option) pour restaurer l'état initial réel." >&2
        echo "TURBO: NON RESTAURÉ (état valide : --force-defaults refusé)"; exit 64
    fi
    ECHECS=(); N=0
    while IFS= read -r d; do
        if [ "$(lire "$d/scaling_governor")" = "performance" ]; then
            if [ -r "$d/scaling_available_governors" ] && ! grep -q -w powersave "$d/scaling_available_governors"; then
                ECHECS+=("cpu$(cpu_id "$d") : « powersave » indisponible"); continue
            fi
            echo powersave > "$d/scaling_governor" 2>/dev/null && [ "$(lire "$d/scaling_governor")" = "powersave" ] \
                && N=$((N+1)) || ECHECS+=("cpu$(cpu_id "$d") : retour à powersave impossible")
        fi
    done < <(cpu_dirs)
    echo "  Gouverneur remis à « powersave » sur $N CPU (EPP, swappiness et services NON touchés)."
    if [ "${#ECHECS[@]}" -eq 0 ]; then echo "TURBO: RESTAURÉ PAR DÉFAUT (powersave sur $N CPU ; swappiness/EPP/services non touchés)"; exit 0; fi
    for e in "${ECHECS[@]}"; do echo "  ✗ $e" >&2; done
    echo "TURBO: RESTAURATION PAR DÉFAUT INCOMPLÈTE"; exit 5
fi

# ── État manquant ou invalide ───────────────────────────────────────────────────────────────────
if [ ! -e "$STATE" ]; then
    if turbo_semble_actif; then
        echo "ERREUR : gouverneur « performance » présent mais AUCUN état sauvegardé : l'état initial est inconnu." >&2
        echo "  Rien modifié. Secours : sudo zeta_turbo_off.sh --force-defaults (remet powersave seulement)." >&2
        echo "TURBO: NON RESTAURÉ (état manquant alors que performance est actif)"
        exit 3
    fi
    echo "  = Aucun état turbo et gouverneur déjà ≠ performance : rien à restaurer."
    echo "TURBO: RIEN À RESTAURER"
    exit 0
fi
if ! state_valid; then
    echo "ERREUR : état sauvegardé INVALIDE ($STATE) — rien modifié, fichier conservé." >&2
    echo "  Secours : sudo zeta_turbo_off.sh --force-defaults" >&2
    echo "TURBO: NON RESTAURÉ (état invalide)"
    exit 3
fi

ECHECS=()

restaurer_services() {
    local liste svc
    IFS=',' read -r -a liste <<< "$(state_get services)"
    local restants=""
    for svc in "${liste[@]:-}"; do
        [ -z "$svc" ] && continue
        # Défense en profondeur (script exécuté en root) : nom de service strict, jamais pris pour une option.
        if ! printf '%s' "$svc" | grep -q -E '^[A-Za-z0-9][A-Za-z0-9_.:@+-]*$'; then
            ECHECS+=("service « $svc » : nom invalide dans l'état (ignoré, NON exécuté)"); continue
        fi
        if systemctl start -- "$svc" 2>/dev/null && systemctl is-active --quiet "$svc" 2>/dev/null; then
            echo "    - $svc redémarré"
        else
            ECHECS+=("service $svc : redémarrage non vérifié"); restants="${restants:+$restants,}$svc"
        fi
    done
    state_set services "$restants" || ECHECS+=("état : mise à jour de la liste des services impossible")
}

# ── --services : services seuls, le turbo CPU reste ─────────────────────────────────────────────
if [ "$SEUL_SERVICES" -eq 1 ]; then
    restaurer_services
    if [ "${#ECHECS[@]}" -eq 0 ]; then echo "TURBO: SERVICES RESTAURÉS (turbo CPU maintenu)"; exit 0; fi
    for e in "${ECHECS[@]}"; do echo "  ✗ $e" >&2; done
    echo "TURBO: SERVICES NON RESTAURÉS (état conservé)"; exit 5
fi

# ── Restauration complète : TOUT est tenté, puis vérifié ───────────────────────────────────────
NB=0
while IFS= read -r d; do
    id="$(cpu_id "$d")"; gov0="$(state_get "cpu_gov_$id")"; epp0="$(state_get "cpu_epp_$id")"
    if [ -z "$gov0" ]; then ECHECS+=("cpu$id : absent de l'état initial (non restauré)"); continue; fi
    NB=$((NB+1))
    if [ "$(lire "$d/scaling_governor")" != "$gov0" ]; then
        echo "$gov0" > "$d/scaling_governor" 2>/dev/null || ECHECS+=("cpu$id : écriture du gouverneur refusée")
    fi
    if [ "$epp0" != "-" ] && [ -f "$d/energy_performance_preference" ] && [ "$(lire "$d/energy_performance_preference")" != "$epp0" ]; then
        echo "$epp0" > "$d/energy_performance_preference" 2>/dev/null || ECHECS+=("cpu$id : écriture de l'EPP refusée")
    fi
    [ "$(lire "$d/scaling_governor")" = "$gov0" ] || ECHECS+=("cpu$id : gouverneur = $(lire "$d/scaling_governor") (attendu $gov0)")
    if [ "$epp0" != "-" ] && [ -f "$d/energy_performance_preference" ]; then
        [ "$(lire "$d/energy_performance_preference")" = "$epp0" ] || ECHECS+=("cpu$id : EPP = $(lire "$d/energy_performance_preference") (attendu $epp0)")
    fi
done < <(cpu_dirs)
# CPU présents dans l'état mais plus visibles (hors ligne) : signalés, pas ignorés en silence.
for cle in $(grep -o -E '^cpu_gov_[0-9]+' "$STATE"); do
    id="${cle#cpu_gov_}"; [ -f "$CPU_ROOT/cpu$id/cpufreq/scaling_governor" ] || ECHECS+=("cpu$id : interface absente (CPU hors ligne ?) — non vérifié")
done

SWAP0="$(state_get swap_initial)"
[ "$(lire "$SWAP_FILE")" = "$SWAP0" ] || echo "$SWAP0" > "$SWAP_FILE" 2>/dev/null || ECHECS+=("swappiness : écriture refusée")
[ "$(lire "$SWAP_FILE")" = "$SWAP0" ] || ECHECS+=("swappiness = $(lire "$SWAP_FILE") (attendu $SWAP0)")

restaurer_services

GOV_RES="$(state_get cpu_gov_0)"
if [ "${#ECHECS[@]}" -eq 0 ]; then
    rm -f "$STATE" && echo "  État supprimé après vérification complète."
    echo "TURBO: RESTAURÉ (vérifié : $NB CPU à leur gouverneur initial${GOV_RES:+ (cpu0=$GOV_RES)}, swappiness $SWAP0)"
    exit 0
fi
for e in "${ECHECS[@]}"; do echo "  ✗ $e" >&2; done
echo "TURBO: RESTAURATION INCOMPLÈTE (${#ECHECS[@]} anomalie(s) ; état CONSERVÉ pour une nouvelle tentative)"
exit 5
