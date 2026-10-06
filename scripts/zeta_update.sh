#!/usr/bin/env bash
#===============================================================================
# zeta_update.sh — Mise à jour orchestrée des systèmes du cluster Zêta
# Lancé depuis PC1 (zeta-lab). Met à jour PC1..PC4 via SSH, selon l'OS.
# Auteur : hprzeta · MAJ : 2026-09-19 (v2 : --no-calc-guard + garde plus precis)
#
# Principe de sûreté ("ne rien casser") :
#   - Mode CHECK par défaut : n'installe RIEN, liste seulement ce qui est dispo.
#   - Conserve les fichiers de conf modifiés (confold/confdef) sur apt.
#   - Ne redémarre JAMAIS une machine : signale seulement si reboot requis.
#   - Refuse de mettre à jour une machine où un calcul compute_zeros tourne.
#   - PC3 (Ubuntu 16.04 EOL) : check uniquement, apply refusé sauf --force-eol.
#   - PC4 (OpenBSD, bastion) : syspatch + pkg_add -u UNIQUEMENT (jamais sysupgrade),
#     traité en dernier, via ssh -t (doas demande le mot de passe).
#===============================================================================
set -u

# --- Profils machines : key | libellé | hôte SSH (local=PC1) | famille | eol ---
# familles : deb (apt) · obsd (OpenBSD).  PC4 volontairement en dernier (bastion).
MACHINES=(
  "PC1|zeta-lab (Ubuntu 24.04)|local|deb|0"
  "PC2|zeta-calc-second (Debian 12)|zeta-calc-second|deb|0"
  "PC3|zeta-backup (Ubuntu 16.04 - EOL)|zeta-backup|deb|1"
  "PC4|zeta-secure (OpenBSD 7.9 - bastion)|zeta-secure|obsd|0"
  "PC5|zeta-monitor (Debian 12)|zeta-monitor|deb|0"
)

MODE="check"          # check | apply
ONLY=""               # ex: "PC2" ou "PC2 PC4"
FULL=0                # apt dist-upgrade au lieu de upgrade
FORCE_EOL=0           # autoriser l'apply sur PC3
CALC_GUARD=1          # 0 = ne pas bloquer si un calcul compute_zeros tourne
ARGC=$#               # nb d'arguments recus (0 => menu interactif)
LOGDIR="/mnt/data/logs"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$LOGDIR/zeta_update_${TS}.log"

usage() {
  cat <<EOF
Usage : $0 [--check|--apply] [--only "PC2 PC4"] [--full] [--force-eol]

  --check       (defaut) liste les MaJ disponibles, n'installe rien
  --apply       applique reellement les MaJ (demande confirmation)
  --only LIST   ne traite que ces machines (PC1 PC2 PC3 PC4)
  --full        apt : dist-upgrade (peut ajouter/retirer des paquets)
  --force-eol   autorise l'apply sur PC3 (Ubuntu 16.04 EOL) - a eviter
  --no-calc-guard  n'annule pas la MaJ meme si un calcul compute_zeros tourne
  -h|--help     cette aide

Exemples :
  $0 --check                  # etat de tout le cluster, sans rien toucher
  $0 --apply --only "PC2"     # mettre a jour uniquement PC2
  $0 --apply --only "PC1 PC2" # PC1 + PC2
EOF
}

# ------------------------------- Menu interactif ------------------------------
# S'affiche si le script est lance SANS argument. Configure MODE / ONLY / FULL.
choisir_machine() {
  # renvoie via la variable globale ONLY
  echo
  echo "  Quelle machine ?"
  echo "    1) PC1  - zeta-lab (Ubuntu 24.04, orchestrateur)"
  echo "    2) PC2  - zeta-calc-second (Debian 12)"
  echo "    3) PC3  - zeta-backup (Ubuntu 16.04 EOL)"
  echo "    4) PC4  - zeta-secure (OpenBSD 7.9, bastion)"
  echo "    5) TOUTES"
  printf "  Choix [1-5] : "
  read -r m
  case "$m" in
    1) ONLY="PC1" ;;
    2) ONLY="PC2" ;;
    3) ONLY="PC3" ;;
    4) ONLY="PC4" ;;
    5) ONLY="" ;;
    *) echo "  Choix invalide."; return 1 ;;
  esac
  return 0
}

menu() {
  while true; do
    echo
    echo "=================================================================="
    echo "   ZETA-UPDATE - mise a jour du cluster (menu)"
    echo "=================================================================="
    echo "  1) Verifier (check) - liste les MaJ, N'INSTALLE RIEN"
    echo "       -> equivaut a : zeta-update --check --only \"...\""
    echo
    echo "  2) Mettre a jour (apply, prudent) - upgrade sans casser les deps"
    echo "       -> equivaut a : zeta-update --apply --only \"...\""
    echo
    echo "  3) Mettre a jour COMPLET (apply --full) - inclut noyau/nvlles deps"
    echo "       -> equivaut a : zeta-update --apply --full --only \"...\""
    echo
    echo "  4) Aide detaillee (toutes les options)"
    echo "  0) Quitter"
    echo "------------------------------------------------------------------"
    echo "  Rappel : PC4 = bastion (syspatch), PC3 = EOL (check seul)."
    printf "  Ton choix [0-4] : "
    read -r c
    case "$c" in
      1) MODE="check"; choisir_machine && return 0 ;;
      2) MODE="apply"; FULL=0; choisir_machine && return 0 ;;
      3) MODE="apply"; FULL=1; choisir_machine && return 0 ;;
      4) echo; usage; echo; printf "  (Entree pour revenir au menu) "; read -r _ ;;
      0) echo "  Annule."; exit 0 ;;
      *) echo "  Choix invalide." ;;
    esac
  done
}
while [ $# -gt 0 ]; do
  case "$1" in
    --check)     MODE="check" ;;
    --apply)     MODE="apply" ;;
    --only)      ONLY="${2:-}"; shift ;;
    --full)      FULL=1 ;;
    --force-eol) FORCE_EOL=1 ;;
    --no-calc-guard) CALC_GUARD=0 ;;
    -h|--help)   usage; exit 0 ;;
    *) echo "Option inconnue : $1"; usage; exit 1 ;;
  esac
  shift
done

# Aucun argument -> menu interactif (configure MODE / ONLY / FULL)
[ "$ARGC" -eq 0 ] && menu

# --------------------------------- Journal ------------------------------------
mkdir -p "$LOGDIR" 2>/dev/null || LOG="/tmp/zeta_update_${TS}.log"
log(){ printf '%s\n' "$*" | tee -a "$LOG"; }
hr(){  log "--------------------------------------------------------------------"; }

# --------------------------------- Helpers ------------------------------------
# run_and_log HOST TTY CMD  -> execute, tee dans le log, renvoie le rc de CMD.
# TTY=1 : alloue un pseudo-terminal (sudo/doas peut demander le mot de passe).
run_and_log(){
  local host="$1" tty="$2" cmd="$3"
  if [ "$host" = "local" ]; then
    bash -c "$cmd" 2>&1 | tee -a "$LOG"
  elif [ "$tty" = "1" ]; then
    ssh -t "$host" "$cmd" 2>&1 | tee -a "$LOG"
  else
    ssh "$host" "$cmd" 2>&1 | tee -a "$LOG"
  fi
  return "${PIPESTATUS[0]}"
}
# run_plain HOST CMD -> lecture simple, pas de tee, renvoie le rc (pour les tests).
run_plain(){
  local host="$1"; shift
  if [ "$host" = "local" ]; then bash -c "$*"; else ssh "$host" "$*"; fi
}

declare -a SUMMARY   # lignes "PC|version|updates|action|reboot"

# ----------------------------- Famille Debian/Ubuntu --------------------------
do_deb(){   # $1=key $2=host $3=eol
  local key="$1" host="$2" eol="$3"
  local ver upd="?" action="-" reboot="non" rc=0

  ver="$(run_plain "$host" 'if command -v lsb_release >/dev/null 2>&1; then lsb_release -ds; else . /etc/os-release; printf "%s" "$PRETTY_NAME"; fi' 2>/dev/null | tr -d '"')"
  [ -z "$ver" ] && ver="inconnu"

  # --- Cas machine en fin de support (PC3) ---
  if [ "$eol" = "1" ]; then
    log "[$key] $ver - /!\\ FIN DE SUPPORT (Ubuntu 16.04)."
    log "[$key] Plus aucune MaJ de securite publiee ; depots -> old-releases.ubuntu.com."
    log "[$key] Depots configures actuellement :"
    run_plain "$host" "grep -hE '^[[:space:]]*deb ' /etc/apt/sources.list /etc/apt/sources.list.d/*.list 2>/dev/null | awk '{print \$2}' | sort -u" 2>/dev/null | tee -a "$LOG"
    if [ "$MODE" = "apply" ] && [ "$FORCE_EOL" != "1" ]; then
      log "[$key] APPLY refuse (node backup/monitor Python 3.5 sensible). --force-eol pour forcer."
      SUMMARY+=("$key|$ver|EOL|ignore (EOL)|-"); return 0
    fi
    if [ "$MODE" = "check" ]; then
      SUMMARY+=("$key|$ver|EOL|check (info)|-"); return 0
    fi
    log "[$key] --force-eol : tentative de MaJ malgre l'EOL (a vos risques)."
  fi

  # --- Rafraichir l'index (sudo -> tty) ---
  run_and_log "$host" 1 "sudo apt-get update"

  # --- Lister ce qui est disponible ---
  upd="$(run_plain "$host" 'apt list --upgradable 2>/dev/null | grep -vE "^(Listing|En train)" | grep "/" | wc -l')"
  log "[$key] $upd paquet(s) a mettre a jour :"
  run_plain "$host" 'apt list --upgradable 2>/dev/null | grep -vE "^(Listing|En train)" | grep "/"' 2>/dev/null | tee -a "$LOG"

  if [ "$MODE" = "apply" ]; then
    # Garde : un vrai run Python compute_zeros tourne-t-il ? (desarmable via --no-calc-guard)
    if [ "$CALC_GUARD" = "1" ] && run_plain "$host" "pgrep -f 'python[0-9]*.*compute_zeros' >/dev/null 2>&1"; then
      log "[$key] /!\\ compute_zeros (python) semble tourner - MaJ ignoree. --no-calc-guard pour forcer."
      SUMMARY+=("$key|$ver|$upd|ignore (calcul)|-"); return 0
    fi
    local up_cmd="upgrade"; [ "$FULL" = "1" ] && up_cmd="dist-upgrade"
    run_and_log "$host" 1 "sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::=--force-confold -o Dpkg::Options::=--force-confdef $up_cmd"
    rc=$?
    run_and_log "$host" 1 "sudo apt-get -y autoremove"
    [ "$rc" -eq 0 ] && action="mis a jour" || action="ERREUR (rc=$rc)"
  else
    action="check"
  fi

  run_plain "$host" 'test -f /var/run/reboot-required' && reboot="OUI"
  SUMMARY+=("$key|$ver|$upd|$action|$reboot")
}

# -------------------------------- Famille OpenBSD -----------------------------
do_obsd(){  # $1=key $2=host
  local key="$1" host="$2" ver action="-" reboot="non" upd="-" rc1=0 rc2=0
  ver="$(run_plain "$host" 'uname -sr' 2>/dev/null)"
  log "[$key] $ver - bastion VPN (traite en dernier, prudence)."

  # doas requis -> toujours -t (mot de passe interactif)
  log "[$key] syspatch disponibles :"
  run_and_log "$host" 1 "doas /usr/sbin/syspatch -c"
  log "[$key] Paquets a mettre a jour (dry-run) :"
  run_and_log "$host" 1 "doas /usr/sbin/pkg_add -u -n"

  if [ "$MODE" = "apply" ]; then
    log "[$key] Application des patches de securite (syspatch)..."
    run_and_log "$host" 1 "doas /usr/sbin/syspatch"; rc1=$?
    log "[$key] Application des MaJ de paquets (pkg_add -u)..."
    run_and_log "$host" 1 "doas /usr/sbin/pkg_add -u"; rc2=$?
    if [ "$rc1" -le 1 ] && [ "$rc2" -le 1 ]; then action="mis a jour"; else action="ERREUR (sp=$rc1 pkg=$rc2)"; fi
    log "[$key] /!\\ Si un patch NOYAU a ete applique -> reboot requis."
    log "[$key]     NE PAS rebooter le bastion a distance (perte d'acces WireGuard)."
    reboot="verifier sortie syspatch"
  else
    action="check"
  fi
  # sysupgrade volontairement JAMAIS lance ici.
  SUMMARY+=("$key|$ver|$upd|$action|$reboot")
}

# ---------------------------------- Confirmation ------------------------------
log "=== zeta_update.sh - $(date '+%F %T') - mode=$MODE full=$FULL ==="
[ -n "$ONLY" ] && log "Machines ciblees : $ONLY"
if [ "$MODE" = "apply" ]; then
  log ""
  log "########## STOP - MODE APPLY : des paquets vont etre INSTALLES ##########"
  printf 'Confirmer ? (tape OUI en majuscules) : '
  read -r ans
  [ "$ans" = "OUI" ] || { log "Annule."; exit 0; }
fi
hr

# ---------------------------------- Boucle ------------------------------------
for entry in "${MACHINES[@]}"; do
  IFS='|' read -r key label host fam eol <<< "$entry"
  if [ -n "$ONLY" ]; then
    case " $ONLY " in *" $key "*) : ;; *) continue ;; esac
  fi
  log ""
  log ">>> $key - $label"
  case "$fam" in
    deb)  do_deb  "$key" "$host" "$eol" ;;
    obsd) do_obsd "$key" "$host" ;;
  esac
  hr
done

# -------------------------------- Recapitulatif -------------------------------
log ""
log "========================= RECAPITULATIF ========================="
printf '%-5s | %-28s | %-9s | %-20s | %s\n' "PC" "Version" "MaJ disp." "Action" "Reboot" | tee -a "$LOG"
for row in "${SUMMARY[@]}"; do
  IFS='|' read -r k v u a r <<< "$row"
  printf '%-5s | %-28s | %-9s | %-20s | %s\n' "$k" "$v" "$u" "$a" "$r" | tee -a "$LOG"
done
log ""
log "Log complet : $LOG"
