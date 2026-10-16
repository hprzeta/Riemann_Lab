#!/bin/bash
# zeta_turbo_status.sh — État RÉEL du turbo Zêta (LECTURE SEULE, aucun sudo, ne modifie rien).
# Auteur : hprzeta — Projet Riemann_Lab — créé le 2026-10-16
#
# Affiche : gouverneur/EPP par CPU, boost matériel (no_turbo), swappiness, profil power-profiles-daemon,
# et l'état sauvegardé par zeta_turbo_on.sh (/run/zeta_turbo/state, lisible par le groupe adm).
# Dernière ligne : TURBO_STATUS=ACTIF | INACTIF | DERIVE | INVALIDE | ILLISIBLE
#   ACTIF     état présent ET tous les CPU en performance
#   INACTIF   pas d'état et aucun CPU en performance
#   DERIVE    état présent mais un CPU n'est plus en performance (power-profiles-daemon ?) -> relancer zeta_turbo_on.sh
#   INVALIDE  état présent mais illisible/incohérent ; ILLISIBLE : droits insuffisants pour le lire
# Codes de sortie : 0 ACTIF · 1 INACTIF · 2 DERIVE · 3 INVALIDE/ILLISIBLE
# Tests : ZETA_TURBO_SYSROOT / ZETA_TURBO_STATE_DIR (arbre factice).
set -u
SYSROOT="${ZETA_TURBO_SYSROOT:-}"
STATE_DIR="${ZETA_TURBO_STATE_DIR:-/run/zeta_turbo}"
STATE="$STATE_DIR/state"
CPU_ROOT="$SYSROOT/sys/devices/system/cpu"
lire() { [ -r "$1" ] && tr -d '\n' < "$1" || echo "-"; }

NB=0; NPERF=0; GOVS=""
for d in "$CPU_ROOT"/cpu[0-9]*/cpufreq; do
    [ -f "$d/scaling_governor" ] || continue
    NB=$((NB+1)); g="$(lire "$d/scaling_governor")"
    [ "$g" = "performance" ] && NPERF=$((NPERF+1))
    case " $GOVS " in *" $g "*) ;; *) GOVS="${GOVS:+$GOVS }$g" ;; esac
    id="${d%/cpufreq}"; id="${id##*/cpu}"
    printf '  cpu%-3s gouverneur=%-12s epp=%s\n' "$id" "$g" "$(lire "$d/energy_performance_preference")"
done
echo "  Gouverneurs présents : ${GOVS:-aucun} · performance sur $NPERF/$NB CPU"
NT="$(lire "$CPU_ROOT/intel_pstate/no_turbo")"
echo "  Boost matériel (no_turbo) : $NT  (0 = actif, 1 = désactivé, - = interface absente)"
echo "  vm.swappiness : $(lire "$SYSROOT/proc/sys/vm/swappiness")"
if command -v powerprofilesctl >/dev/null 2>&1 && [ -z "$SYSROOT" ]; then
    echo "  power-profiles-daemon : profil $(powerprofilesctl get 2>/dev/null || echo '?') (peut réécrire le gouverneur)"
fi

if [ ! -e "$STATE" ]; then
    echo "  État sauvegardé : aucun"
    if [ "$NPERF" -gt 0 ]; then
        echo "  ⚠ performance actif SANS état sauvegardé (activé hors des scripts Zêta ?)"
    fi
    echo "TURBO_STATUS=INACTIF"; [ "$NPERF" -gt 0 ] && exit 3 || exit 1
fi
if [ ! -r "$STATE" ]; then
    echo "  État sauvegardé : présent mais ILLISIBLE (droits ; groupe adm requis)"; echo "TURBO_STATUS=ILLISIBLE"; exit 3
fi
if grep -q -v -E '^(#.*|[a-z0-9_]+=[A-Za-z0-9_.,:+-]*|)$' "$STATE" || ! grep -q -E '^version=1$' "$STATE" || ! grep -q -E '^cpu_gov_[0-9]+=' "$STATE"; then
    echo "  État sauvegardé : INVALIDE"; echo "TURBO_STATUS=INVALIDE"; exit 3
fi
echo "  État sauvegardé : depuis $(sed -n 's/^started_at=//p' "$STATE") · services arrêtés : $(sed -n 's/^services=//p' "$STATE" | sed 's/^$/aucun/')"
if [ "$NB" -gt 0 ] && [ "$NPERF" -eq "$NB" ]; then echo "TURBO_STATUS=ACTIF"; exit 0; fi
echo "  ⚠ dérive : l'état existe mais $((NB-NPERF)) CPU ne sont plus en performance -> relancer zeta_turbo_on.sh (ré-affirmation, état initial conservé)"
echo "TURBO_STATUS=DERIVE"; exit 2
