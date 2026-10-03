#!/bin/bash
# =============================================================================
# zeta_rag.sh — Menu BrainVault : SSD vault_rag + RAG (Objectif 2)
# Projet Zeta / Riemann Lab — PC1 (riemann@zeta-lab)
# Version : 1.0 — 03/10/2026
#
# Usage   : zeta-rag            (menu interactif)
#           zeta-rag etat       (une option puis sortie : etat | monter |
#                                demonter | question | surveillance |
#                                ingestion | sauvegarde)
#
# Principes (leçons du projet) :
#   - Le SSD est identifié par UUID + étiquette, JAMAIS par /dev/sdX
#     (le nom change à chaque branchement USB).
#   - AUCUNE écriture si le SSD n'est pas monté ET reconnu (leçon 05/07 :
#     écriture silencieuse sur le disque système).
#   - Démontage propre avant débranchement (SMART : 129 coupures brutales).
#   - Sauvegarde sans --delete (un vault démonté = dossier vide ; --delete
#     viderait la sauvegarde).
#   - sudo uniquement pour monter / démonter / SMART. Ne pas lancer avec sudo.
# =============================================================================

# shellcheck disable=SC2059,SC2034,SC1090
set -uo pipefail
trap ':' INT      # Ctrl+C arrête le programme lancé, pas le menu

# ─── Couleurs (même palette que zeta_backup_toshiba.sh) ──────────────────────
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'
BLU='\033[0;34m'; CYN='\033[0;36m'; NC='\033[0m'

# ─── Identité du SSD (ne change qu'en cas de reformatage) ────────────────────
LBL="vault_rag"
UUID="9476fad5-8512-4e0d-8cd4-50c9acae01c2"
VAULT="${VAULT_RAG:-/mnt/vault_rag}"

# ─── Chemins ─────────────────────────────────────────────────────────────────
PROJ="$HOME/projet_zeta"
VENV="$PROJ/zeta_env/bin/activate"
EXPORTS="/mnt/data/exports"
WIKI="$PROJ/Riemann_Lab.wiki"
MENU_LOG="$PROJ/logs/zeta_rag_menu.log"

# ─── Référence SMART du 03/10/2026 (Micron 1100 256 Go) ──────────────────────
# On surveille la TENDANCE : une valeur qui monte est plus parlante qu'une
# valeur absolue. Format : "ID:valeur_de_reference:libellé".
SMART_BASE_DATE="03/10/2026"
SMART_BASE_LIFE=89            # Percent_Lifetime_Remain (valeur normalisée)
SMART_SPECS=(
  "5:97:Blocs NAND realloues"
  "187:59950:Reported_Uncorrect"
  "198:2:Offline_Uncorrectable"
  "199:2:Erreurs CRC (cable/boitier)"
  "174:129:Coupures brutales"
)

DEV=""          # rempli par verifier_identite (ex. /dev/sdc1)
SMART_OUT=""    # sortie smartctl mise en cache

# ─── Affichage ───────────────────────────────────────────────────────────────
ok()   { printf "${GRN}  [OK]${NC} %s\n" "$*"; }
warn() { printf "${YLW}  [!] ${NC} %s\n" "$*"; }
err()  { printf "${RED}  [X] ${NC} %s\n" "$*"; }
info() { printf "${CYN}  ->  ${NC}%s\n" "$*"; }

confirm() {            # confirm "question" -> 0 si o/O/y/Y
  local r
  printf "  %s [o/N] " "$1"
  read -r r || return 1
  [[ "$r" =~ ^[oOyY]$ ]]
}

journal() {            # journal "action" : trace dans projet_zeta/logs
  mkdir -p "$(dirname "$MENU_LOG")" 2>/dev/null || return 0
  printf "%s | %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$MENU_LOG" 2>/dev/null || true
}

# ─── Détection / gardes ──────────────────────────────────────────────────────
dev_ssd() {            # device de la partition (par UUID), vide si absent
  local p="/dev/disk/by-uuid/$UUID"
  [ -e "$p" ] && readlink -f "$p"
  return 0
}

verifier_identite() {  # 0 = le SSD est branché ET porte la bonne étiquette
  DEV="$(dev_ssd)"
  if [ -z "$DEV" ]; then
    err "SSD vault_rag absent (UUID $UUID introuvable). Branche-le puis reessaie."
    return 1
  fi
  local lbl
  lbl="$(lsblk -no LABEL "$DEV" 2>/dev/null | head -1)"
  if [ "$lbl" != "$LBL" ]; then
    err "$DEV porte l'etiquette '$lbl' au lieu de '$LBL'. Arret par securite."
    return 1
  fi
  local lp="/dev/disk/by-label/$LBL"
  if [ -e "$lp" ] && [ "$(readlink -f "$lp")" != "$DEV" ]; then
    warn "Un AUTRE disque porte aussi l'etiquette $LBL ($(readlink -f "$lp")). On ne touche que $DEV (UUID verifie)."
  fi
  return 0
}

parent_dev() {         # /dev/sdX du disque portant la partition $DEV, vide sinon
  local k
  k="$(lsblk -no PKNAME "$DEV" 2>/dev/null | head -1)"
  [ -n "$k" ] && printf '/dev/%s\n' "$k"
  return 0
}

is_mounted()  { mountpoint -q "$VAULT"; }
mounted_src() { findmnt -no SOURCE "$VAULT" 2>/dev/null | head -1; }
is_rw()       { findmnt -no OPTIONS "$VAULT" 2>/dev/null | tr ',' '\n' | grep -qx rw; }

garde_monte() {        # SSD reconnu + monte sur $VAULT (lecture au moins)
  verifier_identite || return 1
  if ! is_mounted; then
    err "$VAULT n'est PAS monte (dossier vide du disque systeme). Utilise l'option 2."
    return 1
  fi
  if [ "$(mounted_src)" != "$DEV" ]; then
    err "$VAULT est monte depuis $(mounted_src), pas depuis le SSD $DEV. Arret."
    return 1
  fi
  return 0
}

garde_ecriture() {     # garde_monte + lecture-écriture
  garde_monte || return 1
  if ! is_rw; then
    err "$VAULT est monte en LECTURE SEULE. Option 2 pour passer en lecture-ecriture."
    return 1
  fi
  return 0
}

exiger_rsync() {
  command -v rsync > /dev/null 2>&1 && return 0
  err "rsync est introuvable (sudo apt install rsync). Rien n'a ete fait."
  return 1
}

lancer_python() {      # lancer_python script.py [args...] dans zeta_env
  if [ ! -f "$VENV" ]; then
    err "Environnement introuvable : $VENV"
    return 1
  fi
  ( cd "$PROJ" && source "$VENV" && python "$@" )
}

# ─── SMART ───────────────────────────────────────────────────────────────────
smart_raw() { printf '%s\n' "$SMART_OUT" | awk -v id="$1" '$1==id{print $10; exit}'; }
smart_val() { printf '%s\n' "$SMART_OUT" | awk -v id="$1" '$1==id{print $4; exit}'; }

smart_resume() {
  local par
  par="$(parent_dev)"
  if [ -z "$par" ]; then
    warn "Disque parent introuvable pour $DEV."
    return 1
  fi
  info "SMART de $par (mot de passe sudo requis)"
  SMART_OUT="$(sudo smartctl -H -A -d sat "$par" 2>&1)"
  printf '%s\n' "$SMART_OUT" | grep -q "overall-health" || \
    SMART_OUT="$(sudo smartctl -H -A "$par" 2>&1)"
  if ! printf '%s\n' "$SMART_OUT" | grep -q "overall-health"; then
    warn "smartctl n'a rien renvoye d'exploitable."
    return 1
  fi

  local sante life
  sante="$(printf '%s\n' "$SMART_OUT" | awk -F: '/overall-health/{gsub(/^ +/,"",$2); print $2}')"
  if [ "$sante" = "PASSED" ]; then ok "Sante globale : $sante"; else err "Sante globale : $sante"; fi

  life="$(smart_val 202)"
  if [[ "$life" =~ ^[0-9]+$ ]]; then
    if [ "$life" -lt "$SMART_BASE_LIFE" ]; then
      warn "Vie restante : ${life}% (reference ${SMART_BASE_LIFE}% au $SMART_BASE_DATE)"
    else
      ok "Vie restante : ${life}% (reference ${SMART_BASE_LIFE}% au $SMART_BASE_DATE)"
    fi
  fi

  printf "  %-34s %10s %10s\n" "Compteur (ref. $SMART_BASE_DATE)" "reference" "maintenant"
  local spec id base label now
  for spec in "${SMART_SPECS[@]}"; do
    IFS=: read -r id base label <<< "$spec"
    now="$(smart_raw "$id")"
    if [[ "$now" =~ ^[0-9]+$ ]]; then
      if [ "$now" -gt "$base" ]; then
        printf "${RED}  %-34s %10s %10s  (+%d)${NC}\n" "$label" "$base" "$now" $((now - base))
      else
        printf "${GRN}  %-34s %10s %10s${NC}\n" "$label" "$base" "$now"
      fi
    else
      printf "  %-34s %10s %10s\n" "$label" "$base" "n/a"
    fi
  done
  info "Rouge = le compteur a augmente depuis la reference : a surveiller."
}

# ─── Option 1 : état ─────────────────────────────────────────────────────────
opt_etat() {
  echo
  info "Etat du SSD vault_rag"
  verifier_identite || return
  local par
  par="$(parent_dev)"
  [ -n "$par" ] && lsblk -dno MODEL,SIZE,TRAN "$par" 2>/dev/null | sed 's/^/       /'
  ok "Detecte : $DEV (UUID et etiquette corrects)"
  local w
  w="$(findmnt -no TARGET -S "$DEV" 2>/dev/null | head -1)"
  if [ -z "$w" ]; then
    warn "Branche mais NON monte. Option 2 pour le monter."
    return
  fi
  if [ "$w" != "$VAULT" ]; then
    warn "Monte ailleurs : $w (attendu : $VAULT). Option 2 pour corriger."
    return
  fi
  if is_rw; then ok "Monte sur $VAULT (lecture-ecriture)"; else warn "Monte sur $VAULT en LECTURE SEULE"; fi
  echo
  lancer_python scripts/rag_monitor.py
  echo
  if confirm "Afficher aussi le SMART (sudo) ?"; then smart_resume; fi
}

# ─── Option 2 : monter ───────────────────────────────────────────────────────
opt_monter() {
  echo
  verifier_identite || return
  if is_mounted; then
    if [ "$(mounted_src)" != "$DEV" ]; then
      err "$VAULT est deja occupe par $(mounted_src), ce n'est pas le SSD. Rien fait."
      return
    fi
    if is_rw; then ok "Deja monte en lecture-ecriture."; return; fi
    info "Monte en lecture seule : passage en lecture-ecriture"
    if sudo mount -o remount,rw "$VAULT"; then ok "Remonte en lecture-ecriture."; journal "monter: remount rw $DEV"; fi
    return
  fi
  local ailleurs
  ailleurs="$(findmnt -no TARGET -S "$DEV" 2>/dev/null | head -1)"
  if [ -n "$ailleurs" ]; then
    warn "Le SSD est monte ailleurs : $ailleurs"
    confirm "Le demonter d'abord ?" || { warn "Annule."; return; }
    sudo umount "$ailleurs" || { err "Demontage impossible."; return; }
  fi
  info "Montage de $DEV sur $VAULT"
  if sudo mount -o defaults,noatime "UUID=$UUID" "$VAULT"; then
    if garde_ecriture; then
      ok "Monte (lecture-ecriture)."
      df -h "$VAULT" | sed 's/^/       /'
      journal "monter: $DEV -> $VAULT"
    fi
  else
    err "Echec du montage."
  fi
}

# ─── Option 3 : démonter proprement ──────────────────────────────────────────
opt_demonter() {
  echo
  verifier_identite || return
  if ! is_mounted; then
    warn "Le vault n'est pas monte."
  else
    if [ "$(mounted_src)" != "$DEV" ]; then
      err "$VAULT n'est pas le SSD ($(mounted_src)). Rien fait."
      return
    fi
    if sudo fuser -m "$VAULT" > /dev/null 2>&1; then
      err "Des processus utilisent encore le vault :"
      sudo fuser -vm "$VAULT" 2>&1 | sed 's/^/       /'
      info "Ferme-les (ollama, rag_query, shell dans $VAULT...) puis recommence."
      return
    fi
    info "Synchronisation puis demontage..."
    sync
    if sudo umount "$VAULT"; then
      ok "Demonte proprement."
      journal "demonter: $DEV"
    else
      err "Demontage impossible (occupe ?)."
      return
    fi
  fi
  local par
  par="$(parent_dev)"
  if command -v udisksctl > /dev/null 2>&1 && [ -n "$par" ]; then
    if confirm "Arreter le disque USB $par (mise hors tension) ?"; then
      udisksctl power-off -b "$par" && ok "Disque arrete : tu peux le debrancher."
    else
      ok "Demonte : tu peux le debrancher."
    fi
  else
    ok "Demonte : tu peux le debrancher."
  fi
}

# ─── Option 4 : poser une question ───────────────────────────────────────────
opt_question() {
  echo
  garde_ecriture || return        # ChromaDB (SQLite) a besoin d'ecrire
  local q k
  printf "  Question : "; read -r q || return
  [ -n "$q" ] || { warn "Question vide."; return; }
  printf "  Nombre de passages K [8] : "; read -r k || return
  k="${k:-8}"; [[ "$k" =~ ^[0-9]+$ ]] || k=8
  info "mathstral a froid : ~1m30 de chargement. Ctrl+C pour interrompre."
  journal "question: K=$k"
  lancer_python scripts/rag_query.py "$q" --k "$k" --log
}

# ─── Option 5 : surveillance ─────────────────────────────────────────────────
opt_surveillance() {
  echo
  garde_monte || return
  echo "    1) Photo instantanee"
  echo "    2) En continu (toutes les 10 s, Ctrl+C pour revenir)"
  echo "    3) Photo + latence d'une requete (retrieval seul)"
  echo "    4) Session tmux 3 vues GPU/RAM/ollama (monitor_rag.sh)"
  printf "  Choix [1-4] : "
  local c; read -r c || return
  case "$c" in
    1) lancer_python scripts/rag_monitor.py ;;
    2) lancer_python scripts/rag_monitor.py --watch 10 ;;
    3) lancer_python scripts/rag_monitor.py --test-query ;;
    4) if [ -x "$PROJ/scripts/monitor_rag.sh" ]; then "$PROJ/scripts/monitor_rag.sh"; else warn "scripts/monitor_rag.sh introuvable."; fi ;;
    *) warn "Choix invalide." ;;
  esac
}

# ─── Option 6 : ingestion ────────────────────────────────────────────────────
opt_ingestion() {
  echo
  garde_ecriture || return
  exiger_rsync || return
  if ! grep -q -- '--reset' "$PROJ/scripts/rag_ingest_corpus.py" 2> /dev/null; then
    err "rag_ingest_corpus.py n'a pas l'option --reset (version non corrigee). Installe la version corrigee d'abord."
    return
  fi
  local ram wiki
  ram="$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
  wiki="$(git -C "$WIKI" log -1 --format='%cd (%s)' --date=short 2> /dev/null || echo 'inconnu')"
  echo "  Ce que va faire l'ingestion :"
  echo "    1. copie de securite du vault dans $EXPORTS/vault_backup_<date>"
  echo "    2. SUPPRESSION de la collection riemann_lab_corpus (838 chunks actuels)"
  echo "    3. relecture du wiki + code + prompts ARCHIVE, re-decoupage, re-vectorisation (~5 min)"
  echo
  info "Dernier commit du wiki local : $wiki"
  info "Le corpus ingere refletera ce que contient le wiki/code LOCAL maintenant."
  if [[ "$ram" =~ ^[0-9]+$ ]] && [ "$ram" -lt 2000 ]; then
    warn "RAM disponible : ${ram} Mo (< 2000). Ferme VS Code / Firefox avant."
  fi
  printf "  Tape INGERER pour confirmer : "
  local c; read -r c || return
  [ "$c" = "INGERER" ] || { warn "Annule."; return; }

  local snap
  snap="$EXPORTS/vault_backup_$(date +%Y%m%d_%H%M%S)"
  info "Copie de securite -> $snap"
  if ! { mkdir -p "$snap" && rsync -a --exclude lost+found "$VAULT"/ "$snap"/; }; then
    err "Copie de securite echouee : ingestion annulee."
    return
  fi
  ok "Copie de securite faite."
  journal "ingestion: snapshot $snap puis --reset"
  lancer_python scripts/rag_ingest_corpus.py --reset
  echo
  lancer_python scripts/rag_monitor.py
}

# ─── Option 7 : sauvegarde du vault ──────────────────────────────────────────
opt_sauvegarde() {
  echo
  garde_monte || return
  exiger_rsync || return
  local dest n sim
  dest="$EXPORTS/vault_backup_$(date +%Y%m%d)"
  info "Destination : $dest (sans --delete : rien n'est supprime)"
  mkdir -p "$dest" || { err "Impossible de creer $dest"; return; }
  if ! sim="$(rsync -a --dry-run --itemize-changes --exclude lost+found "$VAULT"/ "$dest"/ 2>&1)"; then
    err "La simulation rsync a echoue :"
    printf '%s\n' "$sim" | tail -5 | sed 's/^/       /'
    return
  fi
  n="$(printf '%s\n' "$sim" | grep -c '^[<>c]')"
  info "Simulation : $n fichier(s) a copier ou mettre a jour."
  if [ "$n" -eq 0 ]; then ok "Deja a jour."; return; fi
  confirm "Lancer la sauvegarde ?" || { warn "Annule."; return; }
  if rsync -a --exclude lost+found "$VAULT"/ "$dest"/; then
    ok "Sauvegarde terminee : $(du -sh "$dest" | cut -f1) dans $dest"
    journal "sauvegarde: $dest"
  else
    err "rsync a signale une erreur."
  fi
}

# ─── Menu ────────────────────────────────────────────────────────────────────
statut_ligne() {
  local d
  d="$(dev_ssd)"
  if [ -z "$d" ]; then
    printf "  SSD : ${RED}absent${NC}\n"
  elif ! is_mounted || [ "$(mounted_src)" != "$d" ]; then
    printf "  SSD : ${YLW}branche, non monte${NC} (%s)\n" "$d"
  elif is_rw; then
    printf "  SSD : ${GRN}monte, lecture-ecriture${NC} (%s)\n" "$d"
  else
    printf "  SSD : ${YLW}monte, LECTURE SEULE${NC} (%s)\n" "$d"
  fi
}

menu() {
  local c
  while true; do
    echo
    printf "${CYN}==================================================================${NC}\n"
    printf "${CYN}   ZETA-RAG - BrainVault (SSD vault_rag) - PC1${NC}\n"
    printf "${CYN}==================================================================${NC}\n"
    statut_ligne
    echo "------------------------------------------------------------------"
    echo "  1) Etat            monte ? bon disque ? espace, collections, SMART"
    echo "  2) Monter          monte le SSD sur $VAULT (verifie UUID)"
    echo "  3) Demonter        sync + demontage propre, avant de debrancher"
    echo "  4) Poser question  retrieval + mathstral (rag_query.py)"
    echo "  5) Surveillance    photo / continu / latence / tmux"
    echo "  6) Ingestion       copie de securite + remise a zero + re-ingestion"
    echo "  7) Sauvegarde      copie du vault vers $EXPORTS (sans --delete)"
    echo "  0) Quitter"
    echo "------------------------------------------------------------------"
    printf "  Ton choix [0-7] : "
    read -r c || { echo; break; }
    case "$c" in
      1) opt_etat ;;
      2) opt_monter ;;
      3) opt_demonter ;;
      4) opt_question ;;
      5) opt_surveillance ;;
      6) opt_ingestion ;;
      7) opt_sauvegarde ;;
      0) echo "  A bientot."; break ;;
      *) warn "Choix invalide." ;;
    esac
  done
}

main() {
  if [ "$(id -u)" -eq 0 ]; then
    err "Ne lance pas ce menu avec sudo : il demande sudo lui-meme quand c'est utile."
    exit 1
  fi
  case "${1:-}" in
    "")           menu ;;
    etat)         opt_etat ;;
    monter)       opt_monter ;;
    demonter)     opt_demonter ;;
    question)     opt_question ;;
    surveillance) opt_surveillance ;;
    ingestion)    opt_ingestion ;;
    sauvegarde)   opt_sauvegarde ;;
    *)            err "Option inconnue : $1 (etat|monter|demonter|question|surveillance|ingestion|sauvegarde)"; exit 1 ;;
  esac
}

# Ne lance main que si le script est execute (pas s'il est "source" pour test)
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
