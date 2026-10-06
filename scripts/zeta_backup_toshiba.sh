#!/bin/bash
# =============================================================================
# zeta_backup_toshiba.sh — Clone incrémental PC1 -> Toshiba (version allégée)
# Projet Zêta / Riemann Lab — riemann@zeta-lab
# Version : 2.2 — 26/09/2026
#   - v2.0 : Chemins corrigés Toshiba-PC1-root/home/data, montage auto,
#            rsync incrémental (--delete) + correction fstab UUID sur le clone
#   - v2.1 : Exclusion permanente du travail SAP (Documents/SAP + SAP_import)
#            du clone — validé par dry-run le 26/09/2026 (0 fichier SAP touché)
#   - v2.2 : Dry-run automatique (root/home/data) avec résumé des suppressions
#            AVANT toute confirmation — applique la leçon apprise du projet
#            ("rsync --delete nécessite un dry-run avant, le clone peut
#            contenir des fichiers plus récents que PC1") à chaque lancement,
#            sans dépendre d'une vérification manuelle préalable.
# Usage : sudo bash zeta_backup_toshiba.sh
# =============================================================================

set -uo pipefail

# ─── Couleurs ────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'
BLU='\033[0;34m'; CYN='\033[0;36m'; NC='\033[0m'

# ─── Labels du clone Toshiba (identification STABLE, jamais par sdX) ──────────
LBL_ROOT="Toshiba-PC1-root"
LBL_HOME="Toshiba-PC1-home"
LBL_DATA="Toshiba-PC1-data"
LBL_EFI="TSB-PC1-EFI"

# ─── Points de montage réels (auto-montés par GNOME sous /media/riemann) ──────
MNT_ROOT="/media/riemann/$LBL_ROOT"
MNT_HOME="/media/riemann/$LBL_HOME"
MNT_DATA="/media/riemann/$LBL_DATA"

# ─── Sources PC1 (local) ──────────────────────────────────────────────────────
SRC_ROOT="/"
SRC_HOME="/home"
SRC_DATA="/mnt/data"

# ─── Exclusions permanentes ────────────────────────────────────────────────────
# Travail SAP (mission NTT DATA/North Atlantic) : jamais cloné sur le Toshiba.
# Motif large 'SAP*' pour couvrir Documents/SAP/ ET l'ancien Documents/SAP_import/
# (chemin relatif à la racine du transfert /home/ -> préfixe riemann/ obligatoire)
EXCLUDE_SAP="riemann/Documents/SAP*/"

DATE=$(date +%Y%m%d_%H%M%S)
LOG="/home/riemann/zeta_clone_${DATE}.log"
DRYRUN_DIR="/tmp/zeta_dryrun_${DATE}"

# ─── Helpers ──────────────────────────────────────────────────────────────────
banner(){ echo -e "\n${BLU}════════════════════════════════════════════════════════${NC}"; \
          echo -e "${BLU}  $1${NC}"; \
          echo -e "${BLU}════════════════════════════════════════════════════════${NC}\n"; }
ok(){   echo -e "${GRN}✅ $1${NC}"; }
warn(){ echo -e "${YLW}⚠️  $1${NC}"; }
err(){  echo -e "${RED}❌ $1${NC}"; }
info(){ echo -e "${CYN}ℹ️  $1${NC}"; }

confirm(){
    echo -e "${YLW}⚠️  $1${NC}"
    read -rp "   Taper exactement 'oui' pour continuer : " rep
    [[ "$rep" == "oui" ]] || { warn "Annulé."; return 1; }
}

# Trouve /dev/sdXN à partir d'un label (source de vérité)
dev_from_label(){ blkid -L "$1" 2>/dev/null; }

# Monte une partition par label si pas déjà montée ; renvoie le point de montage
ensure_mounted(){
    local label="$1" mnt="$2" dev
    dev=$(dev_from_label "$label")
    [[ -z "$dev" ]] && { err "Partition '$label' introuvable (Toshiba branché ?)"; return 1; }
    if mountpoint -q "$mnt"; then
        info "$label déjà monté sur $mnt"
    else
        mkdir -p "$mnt"
        mount "$dev" "$mnt" || { err "Échec montage $dev -> $mnt"; return 1; }
        ok "$label monté ($dev -> $mnt)"
    fi
}

# ─── Dry-run + résumé automatique avant toute action réelle ──────────────────
# $1=nom court (root/home/data) $2=src $3=dst $4...=options d'exclusion rsync
dryrun_report(){
    local name="$1" src="$2" dst="$3"; shift 3
    local logf="$DRYRUN_DIR/dryrun_${name}.log"
    mkdir -p "$DRYRUN_DIR"

    info "Dry-run $name : $src → $dst ..."
    rsync -aAXHx --delete --dry-run --itemize-changes "$@" "$src" "$dst" > "$logf" 2>&1

    local total del
    total=$(wc -l < "$logf")
    del=$(grep -c '^\*deleting' "$logf")

    echo "  ${name} : ${total} changement(s) prévu(s), dont ${del} suppression(s) côté clone"
    if [[ "$del" -gt 0 ]]; then
        echo "    Répartition des suppressions (top niveau) :"
        grep '^\*deleting' "$logf" | awk '{print $2}' | cut -d/ -f1-2 | sort | uniq -c | sort -rn | head -8 \
            | sed 's/^/      /'
    fi
    # Variables globales pour le total consolidé
    DRYRUN_TOTAL=$(( DRYRUN_TOTAL + total ))
    DRYRUN_DEL=$(( DRYRUN_DEL + del ))
}

# ─── Option 1 : Clone incrémental PC1 -> Toshiba ─────────────────────────────
do_clone(){
    banner "CLONE INCRÉMENTAL PC1 → Toshiba"

    info "Vérification présence du Toshiba…"
    for l in "$LBL_ROOT" "$LBL_HOME" "$LBL_DATA"; do
        dev_from_label "$l" >/dev/null || { err "Label '$l' absent. Branche le Toshiba puis relance."; return 1; }
    done
    ok "Toshiba détecté (3 partitions présentes)"

    # Montage des 3 partitions (nécessaire aussi pour le dry-run)
    ensure_mounted "$LBL_ROOT" "$MNT_ROOT" || return 1
    ensure_mounted "$LBL_HOME" "$MNT_HOME" || return 1
    ensure_mounted "$LBL_DATA" "$MNT_DATA" || return 1

    banner "Dry-run automatique (aucune modification à ce stade)"
    DRYRUN_TOTAL=0; DRYRUN_DEL=0
    dryrun_report "root" "$SRC_ROOT" "$MNT_ROOT/" --exclude='/lost+found' --exclude='/swapfile'
    dryrun_report "home" "$SRC_HOME/" "$MNT_HOME/" --exclude='lost+found' --exclude="$EXCLUDE_SAP"
    dryrun_report "data" "$SRC_DATA/" "$MNT_DATA/" --exclude='lost+found'

    echo
    echo "  TOTAL : ${DRYRUN_TOTAL} changement(s), dont ${DRYRUN_DEL} suppression(s) côté clone"
    info "Détail complet dans : $DRYRUN_DIR/dryrun_{root,home,data}.log"

    echo
    warn "Cette opération synchronise (avec SUPPRESSION des fichiers en trop côté clone) :"
    echo "     $SRC_ROOT  → $MNT_ROOT"
    echo "     $SRC_HOME  → $MNT_HOME  (exclusion permanente : $EXCLUDE_SAP)"
    echo "     $SRC_DATA  → $MNT_DATA"
    confirm "Résumé ci-dessus vérifié. Lancer le VRAI clonage (suppressions incluses) ?" || return 1

    local RSO="-aAXHx --delete --info=progress2"

    banner "1/3 — Racine  /  →  $LBL_ROOT"
    # -x : reste sur un seul système de fichiers (n'entre pas dans /home, /mnt/data, /proc…)
    rsync $RSO \
        --exclude='/lost+found' \
        --exclude='/swapfile' \
        "$SRC_ROOT" "$MNT_ROOT/" 2>&1 | tee -a "$LOG"
    ok "Racine synchronisée"

    banner "2/3 — Home  /home  →  $LBL_HOME"
    rsync $RSO --exclude='lost+found' --exclude="$EXCLUDE_SAP" "$SRC_HOME/" "$MNT_HOME/" 2>&1 | tee -a "$LOG"
    ok "Home synchronisé (SAP exclu)"

    banner "3/3 — Data  /mnt/data  →  $LBL_DATA"
    rsync $RSO --exclude='lost+found' "$SRC_DATA/" "$MNT_DATA/" 2>&1 | tee -a "$LOG"
    ok "Data synchronisé"

    fix_fstab
    ok "Clone terminé — log : $LOG"
    echo
    warn "RAPPEL bootabilité : le clone Toshiba est déjà bootable (clone existant)."
    info "Si tu changes de noyau, pense à mettre à jour GRUB/initramfs via chroot"
    info "  (session dédiée — non fait ici pour rester en mode 'refresh' sûr)."
}

# ─── Correction fstab du clone (UUID sda -> UUID Toshiba) ────────────────────
fix_fstab(){
    banner "Correction fstab du clone"
    local fstab="$MNT_ROOT/etc/fstab"
    [[ -f "$fstab" ]] || { warn "Pas de fstab sur le clone ($fstab) — étape ignorée"; return 0; }

    # UUID source (Seagate PC1) et cible (Toshiba) lus dynamiquement
    local U_SRC_ROOT U_SRC_HOME U_SRC_DATA U_SRC_EFI
    local U_DST_ROOT U_DST_HOME U_DST_DATA U_DST_EFI
    U_SRC_ROOT=$(blkid -o value -s UUID "$(dev_from_label 'Seagate-PC1-root')")
    U_DST_ROOT=$(blkid -o value -s UUID "$(dev_from_label "$LBL_ROOT")")
    U_SRC_HOME=$(blkid -o value -s UUID "$(dev_from_label 'Seagate-PC1-home')")
    U_DST_HOME=$(blkid -o value -s UUID "$(dev_from_label "$LBL_HOME")")
    U_SRC_DATA=$(blkid -o value -s UUID "$(dev_from_label 'Seagate-PC1-data')")
    U_DST_DATA=$(blkid -o value -s UUID "$(dev_from_label "$LBL_DATA")")
    U_SRC_EFI=$(blkid -o value -s UUID "$(dev_from_label 'SG-PC1-EFI')")
    U_DST_EFI=$(blkid -o value -s UUID "$(dev_from_label "$LBL_EFI")")

    cp "$fstab" "$fstab.bak-$DATE"     # cp, PAS tee (retour d'expérience : tee échoue en silence)
    local tmp="/tmp/fstab_clone_$DATE"
    cp "$fstab" "$tmp"

    [[ -n "$U_SRC_ROOT" && -n "$U_DST_ROOT" ]] && sed -i "s/$U_SRC_ROOT/$U_DST_ROOT/g" "$tmp"
    [[ -n "$U_SRC_HOME" && -n "$U_DST_HOME" ]] && sed -i "s/$U_SRC_HOME/$U_DST_HOME/g" "$tmp"
    [[ -n "$U_SRC_DATA" && -n "$U_DST_DATA" ]] && sed -i "s/$U_SRC_DATA/$U_DST_DATA/g" "$tmp"
    if [[ -n "$U_SRC_EFI" && -n "$U_DST_EFI" ]]; then
        sed -i "s/$U_SRC_EFI/$U_DST_EFI/g" "$tmp"
    else
        warn "UUID EFI source/cible introuvable (label 'SG-PC1-EFI' absent ?) — /boot/efi du fstab clone NON corrigé"
        warn "Vérifie manuellement /boot/efi dans $fstab avant de tester le boot."
    fi

    cp "$tmp" "$fstab"
    ok "fstab corrigé (sauvegarde : $fstab.bak-$DATE)"
    echo "----- fstab du clone (après correction) -----"
    grep -vE '^\s*#' "$fstab" | grep -vE '^\s*$'
    echo "---------------------------------------------"
}

# ─── Option 2 : SMART Toshiba ────────────────────────────────────────────────
do_smart(){
    banner "Contrôle SMART Toshiba"
    local dev; dev=$(dev_from_label "$LBL_DATA")
    [[ -z "$dev" ]] && { err "Toshiba non détecté"; return 1; }
    local disk="/dev/$(lsblk -no PKNAME "$dev")"
    command -v smartctl >/dev/null || { err "smartmontools absent : sudo apt install smartmontools"; return 1; }
    smartctl -H "$disk"
    smartctl -A "$disk" | grep -Ei 'Reallocated|Pending|Uncorrect|Power_On|Temperature' || true
}

# ─── Option 3 : Vérifier montage ─────────────────────────────────────────────
do_check(){
    banner "État de montage du Toshiba"
    lsblk -o NAME,SIZE,LABEL,MOUNTPOINT "$(lsblk -no PKNAME "$(dev_from_label "$LBL_DATA")" | sed 's,^,/dev/,')" 2>/dev/null \
      || lsblk -o NAME,SIZE,LABEL,MOUNTPOINT
}

# ─── Option 4 : État des sauvegardes ─────────────────────────────────────────
do_status(){
    banner "Tailles / espace du clone"
    for m in "$MNT_ROOT" "$MNT_HOME" "$MNT_DATA"; do
        if mountpoint -q "$m"; then df -h "$m" | tail -1 | awk -v M="$m" '{printf "  %-40s %s util / %s (%s)\n", M, $3, $2, $5}'; fi
    done
}

# ─── Option 5 : Démonter proprement ──────────────────────────────────────────
do_umount(){
    banner "Démontage propre du Toshiba"
    for m in "$MNT_ROOT" "$MNT_HOME" "$MNT_DATA"; do
        if mountpoint -q "$m"; then
            umount "$m" && ok "Démonté : $m" || err "Échec umount $m (fichier/onglet ouvert ?)"
        fi
    done
    info "Tu peux éjecter le disque via ⏏ dans Fichiers."
}

# ─── Menu ─────────────────────────────────────────────────────────────────────
main_menu(){
    banner "ZÊTA — Clone PC1 → Toshiba (allégé)  v2.2"
    echo "  1) Clone incrémental PC1 → Toshiba  (dry-run auto + / , /home [SAP exclu] , /mnt/data)"
    echo "  2) Contrôle SMART Toshiba"
    echo "  3) Vérifier le montage"
    echo "  4) État des sauvegardes (espace)"
    echo "  5) Démonter proprement"
    echo "  0) Quitter"
    echo
    read -rp "  Choix : " c
    case "$c" in
        1) do_clone ;;
        2) do_smart ;;
        3) do_check ;;
        4) do_status ;;
        5) do_umount ;;
        0) echo "Bye."; exit 0 ;;
        *) warn "Choix invalide"; sleep 1 ;;
    esac
    echo; read -rp "  Entrée pour revenir au menu…" _; main_menu
}

# ─── Garde root ───────────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    err "À lancer avec sudo :  sudo bash ~/projet_zeta/scripts/zeta_backup_toshiba.sh"
    exit 1
fi

main_menu
