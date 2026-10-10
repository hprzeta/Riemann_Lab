#!/bin/bash
# =============================================================================
# zeta_backup_toshiba.sh — Clone incrémental PC1 -> Toshiba (version allégée)
# Projet Zêta / Riemann Lab — riemann@zeta-lab
# Version : 2.3 — 10/10/2026
#   - v2.0 : Chemins corrigés Toshiba-PC1-root/home/data, montage auto,
#            rsync incrémental (--delete) + correction fstab UUID sur le clone
#   - v2.1 : Exclusion permanente du travail SAP (Documents/SAP + SAP_import)
#            du clone — validé par dry-run le 26/09/2026 (0 fichier SAP touché)
#   - v2.2 : Dry-run automatique (root/home/data) avec résumé des suppressions
#            AVANT toute confirmation — applique la leçon apprise du projet
#            ("rsync --delete nécessite un dry-run avant, le clone peut
#            contenir des fichiers plus récents que PC1") à chaque lancement,
#            sans dépendre d'une vérification manuelle préalable.
#   - v2.3 : Boot du clone fiabilisé. Le rsync de "/" recopie /boot/grub/grub.cfg
#            de PC1 (UUID de sda1) vers le clone -> le noyau lancé depuis le
#            Toshiba montait / sur sda1. Ajout de fix_grub() (update-grub en
#            chroot + vérification des UUID, démontage garanti par trap EXIT),
#            option 6 (vérifier la bootabilité, lecture seule), option 7
#            (réparer le boot sans rsync), avertissement si /usr/local/bin/
#            zeta-boot-id est absent de PC1 (étiquette de disque de boot).
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
    # Sans zeta-boot-id sur PC1, le clone n'aurait pas d'étiquette de disque de boot
    if [[ ! -x /usr/local/bin/zeta-boot-id ]]; then
        warn "/usr/local/bin/zeta-boot-id ABSENT de PC1 : le clone n'aura pas d'étiquette de boot."
        warn "Annule (réponds autre chose que 'oui'), installe-le, puis relance."
    fi
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

    fix_fstab                                    # UUID de fstab : sda -> Toshiba
    fix_grub || { err "Réparation GRUB échouée : le clone n'est PAS bootable"; return 1; }
    ok "Clone terminé — log : $LOG"
    verify_boot                                  # résumé des contrôles (option 6)
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

# ─── Démontage garanti des montages du chroot (idempotent, ordre inverse) ─────
CHROOT_MOUNTS=()    # points de montage réellement montés par fix_grub (ordre de montage)
cleanup_chroot(){
    local i m rc=0 left=()
    # Parcours en ordre inverse : run, sys, proc, dev/pts, dev, boot/efi
    for (( i=${#CHROOT_MOUNTS[@]}-1; i>=0; i-- )); do
        m="${CHROOT_MOUNTS[$i]}"
        if mountpoint -q "$m"; then
            umount "$m" 2>/dev/null || { err "Échec démontage $m"; left+=("$m"); rc=1; }
        fi
    done
    # On ne garde que ce qui n'a pas pu être démonté (remis dans l'ordre de montage)
    CHROOT_MOUNTS=()
    for (( i=${#left[@]}-1; i>=0; i-- )); do CHROOT_MOUNTS+=("${left[$i]}"); done
    return $rc
}
# Filet de sécurité : même en cas d'erreur/sortie, rien ne reste sous $MNT_ROOT
trap cleanup_chroot EXIT

# Monte et enregistre la cible (dernier argument) pour le démontage
_cm(){ mount "$@" || { err "Échec : mount $*"; return 1; }; CHROOT_MOUNTS+=("${@: -1}"); }

# ─── Réparation GRUB du clone (update-grub en chroot + vérification UUID) ────
fix_grub(){
    banner "Réparation GRUB du clone (update-grub en chroot)"
    local dev_root dev_efi U_SRC U_DST cfg efi_cfg n_src n_dst rc=0
    dev_root=$(dev_from_label "$LBL_ROOT"); dev_efi=$(dev_from_label "$LBL_EFI")
    [[ -n "$dev_root" && -n "$dev_efi" ]] || { err "Partition root/EFI du clone introuvable"; return 1; }
    mountpoint -q "$MNT_ROOT" || { err "Root du clone non monté ($MNT_ROOT)"; return 1; }
    # UUID lus dynamiquement (comme fix_fstab) : source = Seagate, cible = Toshiba
    U_SRC=$(blkid -o value -s UUID "$(dev_from_label 'Seagate-PC1-root')")
    U_DST=$(blkid -o value -s UUID "$dev_root")
    [[ -n "$U_SRC" && -n "$U_DST" ]] || { err "UUID root source/cible introuvable"; return 1; }
    cfg="$MNT_ROOT/boot/grub/grub.cfg"; efi_cfg="$MNT_ROOT/boot/efi/EFI/ubuntu/grub.cfg"

    # Ctrl-C : démonter proprement avant de sortir
    trap 'cleanup_chroot; exit 130' INT TERM

    # Montages : EFI du clone puis bind dev, dev/pts, proc, sys, run
    if ! mountpoint -q "$MNT_ROOT/boot/efi"; then
        _cm "$dev_efi" "$MNT_ROOT/boot/efi" || rc=1
    fi
    if [[ $rc -eq 0 ]]; then
        _cm --bind /dev     "$MNT_ROOT/dev"     && \
        _cm --bind /dev/pts "$MNT_ROOT/dev/pts" && \
        _cm --bind /proc    "$MNT_ROOT/proc"    && \
        _cm --bind /sys     "$MNT_ROOT/sys"     && \
        _cm --bind /run     "$MNT_ROOT/run"     || rc=1
    fi
    # Régénération de grub.cfg DANS le clone (les UUID deviennent ceux du Toshiba)
    if [[ $rc -eq 0 ]]; then
        chroot "$MNT_ROOT" update-grub 2>&1 | tee -a "$LOG" || rc=1
    fi

    # Vérifications (EFI encore montée à ce stade)
    if [[ $rc -eq 0 ]]; then
        if [[ -f "$cfg" ]]; then
            n_src=$(grep -c "$U_SRC" "$cfg" || true); n_dst=$(grep -c "$U_DST" "$cfg" || true)
        else n_src=1; n_dst=0; fi
        echo "  grub.cfg clone : UUID Seagate=${n_src:-0} (attendu 0) · UUID Toshiba=${n_dst:-0} (attendu >0)"
        if [[ "${n_src:-0}" -ne 0 || "${n_dst:-0}" -eq 0 ]]; then
            err "grub.cfg du clone incorrect (UUID Seagate présent ou UUID Toshiba absent)"; rc=1
        fi
        if ! grep -q "$U_DST" "$efi_cfg" 2>/dev/null; then
            err "EFI/ubuntu/grub.cfg du clone ne contient pas l'UUID du clone"; rc=1
        fi
    fi

    # Démontage immédiat + contrôle qu'aucun montage ne reste sous $MNT_ROOT
    cleanup_chroot || rc=1
    trap - INT TERM
    if findmnt -rn -o TARGET | grep -q "^$MNT_ROOT/"; then
        err "Des montages restent sous $MNT_ROOT (risque pour le prochain rsync --delete)"; rc=1
    fi
    [[ $rc -eq 0 ]] && ok "GRUB du clone réparé et vérifié" || err "fix_grub : ÉCHEC"
    return $rc
}

# ─── Option 6 : vérifier la bootabilité du clone (LECTURE SEULE) ─────────────
VB_FAILS=0
_chk(){ if [[ "$2" -eq 0 ]]; then ok "$1"; else err "ÉCHEC : $1"; VB_FAILS=$((VB_FAILS+1)); fi; }

verify_boot(){
    banner "Bootabilité du clone Toshiba (lecture seule)"
    VB_FAILS=0
    local dev_root dev_efi U_SRC U_DST n_src n_dst pair lbl_s lbl_d us ud rc tmp_efi
    local cfg="$MNT_ROOT/boot/grub/grub.cfg" fstab="$MNT_ROOT/etc/fstab"
    mountpoint -q "$MNT_ROOT" || ensure_mounted "$LBL_ROOT" "$MNT_ROOT" || return 1
    dev_root=$(dev_from_label "$LBL_ROOT"); dev_efi=$(dev_from_label "$LBL_EFI")
    U_SRC=$(blkid -o value -s UUID "$(dev_from_label 'Seagate-PC1-root')")
    U_DST=$(blkid -o value -s UUID "$dev_root")

    # 1) grub.cfg du clone : 0 UUID Seagate, >0 UUID Toshiba
    n_src=$(grep -c "$U_SRC" "$cfg" 2>/dev/null || true); n_dst=$(grep -c "$U_DST" "$cfg" 2>/dev/null || true)
    [[ "${n_src:-0}" -eq 0 && "${n_dst:-0}" -gt 0 ]]; _chk "grub.cfg root (Seagate=${n_src:-0}, Toshiba=${n_dst:-0})" $?

    # 2) EFI/ubuntu/grub.cfg du clone (montage temporaire en lecture seule)
    tmp_efi=$(mktemp -d /tmp/zeta_efi_XXXXXX); rc=1
    if mount -o ro "$dev_efi" "$tmp_efi" 2>/dev/null; then
        grep -q "$U_DST" "$tmp_efi/EFI/ubuntu/grub.cfg" 2>/dev/null; rc=$?
        umount "$tmp_efi"
    fi
    rmdir "$tmp_efi" 2>/dev/null
    _chk "EFI grub.cfg pointe vers l'UUID du clone" $rc

    # 3) fstab : aucun UUID Seagate (root/home/data/EFI) et UUID root Toshiba présent
    rc=0
    for pair in "Seagate-PC1-root:$LBL_ROOT" "Seagate-PC1-home:$LBL_HOME" "Seagate-PC1-data:$LBL_DATA" "SG-PC1-EFI:$LBL_EFI"; do
        lbl_s=${pair%%:*}; lbl_d=${pair##*:}
        us=$(blkid -o value -s UUID "$(dev_from_label "$lbl_s")"); ud=$(blkid -o value -s UUID "$(dev_from_label "$lbl_d")")
        [[ -n "$us" ]] && grep -q "$us" "$fstab" 2>/dev/null && rc=1
        [[ -n "$ud" ]] && ! grep -q "$ud" "$fstab" 2>/dev/null && rc=1
    done
    _chk "fstab : UUID Toshiba partout, aucun UUID Seagate" $rc

    # 4) resume : absent / none = OK ; sinon l'UUID doit être sur le même disque que le clone
    local rf="$MNT_ROOT/etc/initramfs-tools/conf.d/resume" line ruuid rdev
    rc=0
    if [[ -f "$rf" ]]; then
        line=$(grep -E '^RESUME=' "$rf" | tail -1)
        if [[ -n "$line" && "$line" != "RESUME=none" ]]; then
            ruuid=$(echo "$line" | sed -n 's/^RESUME=UUID=//p'); rdev=""
            [[ -n "$ruuid" ]] && rdev=$(blkid -U "$ruuid" 2>/dev/null)
            if [[ -z "$rdev" ]]; then
                rc=1; warn "resume : RESUME=UUID=${ruuid:-?} absent de tous les disques (le boot attendrait une partition inexistante)"
            elif [[ "$(lsblk -no PKNAME "$rdev")" != "$(lsblk -no PKNAME "$dev_root")" ]]; then
                rc=1; warn "resume : l'UUID ${ruuid} est sur un autre disque que le clone ($rdev)"
            fi
            [[ $rc -ne 0 ]] && warn "ALERTE seulement : aucune correction automatique, éditer $rf à la main puis update-initramfs en chroot"
        fi
    fi
    _chk "initramfs resume (absent ou sur le disque du clone)" $rc

    # 5) étiquette de boot sur le clone
    [[ -x "$MNT_ROOT/usr/local/bin/zeta-boot-id" ]];              _chk "zeta-boot-id présent sur le clone" $?
    [[ -f "$MNT_ROOT/etc/xdg/autostart/zeta-boot-id.desktop" ]];  _chk "autostart zeta-boot-id présent" $?
    grep -q 'zeta-boot-id' "$MNT_ROOT/etc/bash.bashrc" 2>/dev/null; _chk "ligne zeta-boot-id dans bash.bashrc" $?

    echo
    [[ $VB_FAILS -eq 0 ]] && ok "Clone bootable (contrôles statiques OK — le test réel reste le reboot)" \
                          || err "$VB_FAILS contrôle(s) en échec"
    return $(( VB_FAILS > 0 ))
}

# ─── Option 7 : réparer le boot du clone seulement (sans rsync) ──────────────
do_repair_boot(){
    banner "Réparation du boot du clone (fstab + GRUB, sans rsync)"
    confirm "Écriture sur le Toshiba : fstab corrigé + update-grub en chroot. Continuer ?" || return 1
    ensure_mounted "$LBL_ROOT" "$MNT_ROOT" || return 1
    fix_fstab
    fix_grub || return 1
    verify_boot
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
    banner "ZÊTA — Clone PC1 → Toshiba (allégé)  v2.3"
    echo "  1) Clone incrémental PC1 → Toshiba  (dry-run auto + / , /home [SAP exclu] , /mnt/data)"
    echo "  2) Contrôle SMART Toshiba"
    echo "  3) Vérifier le montage"
    echo "  4) État des sauvegardes (espace)"
    echo "  5) Démonter proprement"
    echo "  6) Vérifier la bootabilité du clone (lecture seule)"
    echo "  7) Réparer le boot du clone seulement (fstab + GRUB, sans rsync)"
    echo "  0) Quitter"
    echo
    read -rp "  Choix : " c
    case "$c" in
        1) do_clone ;;
        2) do_smart ;;
        3) do_check ;;
        4) do_status ;;
        5) do_umount ;;
        6) verify_boot ;;
        7) do_repair_boot ;;
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
