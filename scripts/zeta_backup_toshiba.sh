#!/bin/bash
# =============================================================================
# zeta_backup_toshiba.sh — Clone incrémental PC1 -> Toshiba (version allégée)
# Projet Zêta / Riemann Lab — riemann@zeta-lab
# Version : 2.4 — 10/10/2026
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
#   - v2.4 : Garde-fou de SENS : toute écriture sur le Toshiba (options 1 et 7,
#            fix_fstab, fix_grub en mode clonage) exige la racine Seagate-PC1-root
#            (require_root_label). Restauration INVERSE Toshiba -> disque de travail :
#            option 8 (dry-run auto, rsync --delete, fstab/GRUB inversés, grub-install +
#            efibootmgr si EFI vide), option 9 (disque neuf : GPT + mkfs par labels),
#            option 10 (restauration d'un chemin précis, sans --delete), --dry-run et
#            --only CHEMIN. SAP : jamais recopié ; une ANCIENNE copie pré-exclusion
#            existe sur le Toshiba (constat 10/10/2026), hors restauration.
#            Variables de TEST : ZETA_TEST_ROOT_LABEL, ZETA_TEST_LABEL_PREFIX.
# Usage : sudo bash zeta_backup_toshiba.sh [--dry-run] [--only CHEMIN]
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

# Mode simulation global (option --dry-run) : s'arrête APRÈS le dry-run rsync, n'écrit rien
DRYRUN_ONLY=0

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

# ─── Garde-fou sur le SENS du clonage (v2.4) ──────────────────────────────────
# Label de la racine du disque de travail (Seagate) : seul point de départ autorisé
# pour toute opération qui ÉCRIT sur le Toshiba (clone, réparation du boot).
LBL_SG_ROOT="Seagate-PC1-root"

# Label de la racine en cours d'exécution.
# ZETA_TEST_ROOT_LABEL : variable de TEST uniquement, simule un label sans toucher
# aux disques (utilisée pour valider les garde-fous, voir étape C du cahier des charges).
current_root_label(){
    if [[ -n "${ZETA_TEST_ROOT_LABEL:-}" ]]; then
        echo "$ZETA_TEST_ROOT_LABEL"
    else
        lsblk -no LABEL "$(findmnt -no SOURCE /)" 2>/dev/null | head -1
    fi
}

# A1 : refuse (code 1, AUCUNE écriture) si la racine en cours n'a pas le label attendu
require_root_label(){
    local want="${1:-$LBL_SG_ROOT}" cur
    cur=$(current_root_label)
    if [[ "$cur" != "$want" ]]; then
        err "Sens inverse interdit : lance ce script depuis le Seagate"
        err "  racine en cours : '${cur:-inconnue}' — attendu : '$want'"
        return 1
    fi
}

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
    require_root_label "$LBL_SG_ROOT" || return 1   # A2 : jamais Toshiba -> Seagate par cette voie

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
    if [[ $DRYRUN_ONLY -eq 1 ]]; then
        ok "Mode simulation (--dry-run) : arrêt ici, aucune écriture effectuée"; return 0
    fi

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

# ─── Sens de l'opération : variables source/cible (v2.4) ─────────────────────
# fix_fstab / fix_grub / verify_boot servent aux DEUX sens ; _dir_vars fixe qui est
# la source, qui est la cible, et où la racine de la cible est montée.
D_MODE=""; D_MNT=""; D_BOOT_PREFIX=""
D_SRC_ROOT=""; D_SRC_HOME=""; D_SRC_DATA=""; D_SRC_EFI=""
D_DST_ROOT=""; D_DST_HOME=""; D_DST_DATA=""; D_DST_EFI=""
_dir_vars(){
    case "${1:-clone}" in
        clone)      # sens normal : Seagate -> Toshiba
            D_MODE=clone; D_MNT="$MNT_ROOT"; D_BOOT_PREFIX="Toshiba"
            D_SRC_ROOT="$LBL_TGT_ROOT"; D_SRC_HOME="$LBL_TGT_HOME"; D_SRC_DATA="$LBL_TGT_DATA"; D_SRC_EFI="$LBL_TGT_EFI"
            D_DST_ROOT="$LBL_ROOT";     D_DST_HOME="$LBL_HOME";     D_DST_DATA="$LBL_DATA";     D_DST_EFI="$LBL_EFI" ;;
        restore)    # sens inverse : Toshiba -> disque de travail
            D_MODE=restore; D_MNT="$RT_ROOT"; D_BOOT_PREFIX="Seagate"
            D_SRC_ROOT="$LBL_ROOT";     D_SRC_HOME="$LBL_HOME";     D_SRC_DATA="$LBL_DATA";     D_SRC_EFI="$LBL_EFI"
            D_DST_ROOT="$LBL_TGT_ROOT"; D_DST_HOME="$LBL_TGT_HOME"; D_DST_DATA="$LBL_TGT_DATA"; D_DST_EFI="$LBL_TGT_EFI" ;;
        *) err "Mode inconnu : $1"; return 1 ;;
    esac
    [[ -n "$D_MNT" ]] || { err "Racine de la cible non montée/inconnue"; return 1; }
}

# Garde commun aux opérations qui ÉCRIVENT sur la cible (selon le sens)
_require_direction(){
    if [[ "$D_MODE" == "clone" ]]; then
        require_root_label "$LBL_SG_ROOT" || return 1          # A2 : depuis le Seagate uniquement
    else
        local run_dev tgt_dev
        run_dev=$(findmnt -no SOURCE /); tgt_dev=$(findmnt -no SOURCE "$D_MNT" 2>/dev/null | head -1)
        # B1 : la cible n'est jamais le système en cours d'exécution
        if [[ -z "$tgt_dev" || "$tgt_dev" == "$run_dev" || "$(current_root_label)" == "$D_DST_ROOT" ]]; then
            err "Restauration refusée : la cible est le système en cours (ou n'est pas montée)"; return 1
        fi
    fi
}

# ─── Correction fstab de la cible (UUID source -> UUID cible) ────────────────
fix_fstab(){
    _dir_vars "${1:-clone}" || return 1
    banner "Correction fstab de la cible ($D_MODE)"
    _require_direction || return 1
    local fstab="$D_MNT/etc/fstab" pair us ud U_SRC_EFI U_DST_EFI
    [[ -f "$fstab" ]] || { warn "Pas de fstab sur la cible ($fstab) — étape ignorée"; return 0; }

    cp "$fstab" "$fstab.bak-$DATE"     # cp, PAS tee (retour d'expérience : tee échoue en silence)
    local tmp="/tmp/fstab_clone_$DATE"
    cp "$fstab" "$tmp"

    # UUID source et cible lus dynamiquement, par label (jamais par sdX)
    for pair in "$D_SRC_ROOT:$D_DST_ROOT" "$D_SRC_HOME:$D_DST_HOME" "$D_SRC_DATA:$D_DST_DATA"; do
        us=$(blkid -o value -s UUID "$(dev_from_label "${pair%%:*}")")
        ud=$(blkid -o value -s UUID "$(dev_from_label "${pair##*:}")")
        [[ -n "$us" && -n "$ud" ]] && sed -i "s/$us/$ud/g" "$tmp"
    done
    U_SRC_EFI=$(blkid -o value -s UUID "$(dev_from_label "$D_SRC_EFI")")
    U_DST_EFI=$(blkid -o value -s UUID "$(dev_from_label "$D_DST_EFI")")
    if [[ -n "$U_SRC_EFI" && -n "$U_DST_EFI" ]]; then
        sed -i "s/$U_SRC_EFI/$U_DST_EFI/g" "$tmp"
    else
        warn "UUID EFI source/cible introuvable (label '$D_SRC_EFI' ou '$D_DST_EFI' absent ?) — /boot/efi du fstab NON corrigé"
        warn "Vérifie manuellement /boot/efi dans $fstab avant de tester le boot."
    fi

    cp "$tmp" "$fstab"
    ok "fstab corrigé (sauvegarde : $fstab.bak-$DATE)"
    echo "----- fstab de la cible (après correction) -----"
    grep -vE '^\s*#' "$fstab" | grep -vE '^\s*$'
    echo "------------------------------------------------"
}

# ─── Démontage garanti des montages du chroot (idempotent, ordre inverse) ─────
CHROOT_MOUNTS=()    # montages enregistrés par _cm (ordre de montage) — chroot ET restauration
# $1 = indice de départ (défaut 0 = tout) : ne démonte que les montages enregistrés
# à partir de cet indice, pour que fix_grub ne démonte pas les montages de la restauration.
cleanup_chroot(){
    local from="${1:-0}" i m rc=0 left=() keep=()
    (( from > 0 )) && keep=("${CHROOT_MOUNTS[@]:0:from}")
    # Parcours en ordre inverse : run, sys, proc, dev/pts, dev, boot/efi
    for (( i=${#CHROOT_MOUNTS[@]}-1; i>=from; i-- )); do
        m="${CHROOT_MOUNTS[$i]}"
        if mountpoint -q "$m"; then
            umount "$m" 2>/dev/null || { err "Échec démontage $m"; left+=("$m"); rc=1; }
        fi
    done
    # On garde ce qui précède l'indice + ce qui n'a pas pu être démonté (ordre de montage)
    CHROOT_MOUNTS=("${keep[@]}")
    for (( i=${#left[@]}-1; i>=0; i-- )); do CHROOT_MOUNTS+=("${left[$i]}"); done
    return $rc
}
# Filet de sécurité : même en cas d'erreur/sortie, rien ne reste sous la cible
trap cleanup_chroot EXIT

# Monte et enregistre la cible (dernier argument) pour le démontage
_cm(){ mount "$@" || { err "Échec : mount $*"; return 1; }; CHROOT_MOUNTS+=("${@: -1}"); }

# Sens inverse : EFI de la cible vide (disque neuf/remplacé) ou périmée -> grub-install + NVRAM.
# $1 = racine de la cible (montée, chroot prêt) · $2 = UUID racine cible · $3 = /dev de l'EFI cible
_grub_install_efi(){
    local root="$1" udst="$2" dev_efi="$3" efi="$1/boot/efi" need=0 disk part loader
    [[ -f "$efi/EFI/ubuntu/grubx64.efi" || -f "$efi/EFI/ubuntu/shimx64.efi" ]] || need=1
    grep -q "$udst" "$efi/EFI/ubuntu/grub.cfg" 2>/dev/null || need=1
    if [[ $need -eq 0 ]]; then
        info "EFI de la cible déjà équipée (GRUB présent, UUID à jour) : grub-install inutile"; return 0
    fi
    warn "EFI de la cible vide ou périmée : grub-install --target=x86_64-efi --bootloader-id=ubuntu"
    # efivars : le bind (non récursif) de /sys ne l'emporte pas ; nécessaire pour écrire en NVRAM
    if [[ -d /sys/firmware/efi/efivars && -d "$root/sys/firmware/efi/efivars" ]]; then
        mountpoint -q "$root/sys/firmware/efi/efivars" || \
            _cm --bind /sys/firmware/efi/efivars "$root/sys/firmware/efi/efivars" || return 1
    else
        warn "Session non-UEFI ou efivars absent : l'entrée NVRAM ne pourra pas être créée (reste : EFI/ubuntu sur la partition)"
    fi
    chroot "$root" grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=ubuntu 2>&1 | tee -a "$LOG"
    [[ ${PIPESTATUS[0]} -eq 0 ]] || { err "grub-install a échoué"; return 1; }

    if [[ -d /sys/firmware/efi/efivars ]] && command -v efibootmgr >/dev/null; then
        if ! efibootmgr 2>/dev/null | grep -qi 'ubuntu'; then
            disk="/dev/$(lsblk -no PKNAME "$dev_efi")"; part=$(cat "/sys/class/block/$(basename "$dev_efi")/partition")
            loader='\EFI\ubuntu\shimx64.efi'; [[ -f "$efi/EFI/ubuntu/shimx64.efi" ]] || loader='\EFI\ubuntu\grubx64.efi'
            warn "Aucune entrée 'ubuntu' en NVRAM : création (efibootmgr -c, disque $disk partition $part)"
            efibootmgr -c -d "$disk" -p "$part" -L ubuntu -l "$loader" 2>&1 | tee -a "$LOG"
        fi
        info "Entrées NVRAM (à contrôler) :"; efibootmgr 2>/dev/null | grep -iE 'BootOrder|ubuntu' | sed 's/^/     /'
    fi
}

# ─── Réparation GRUB de la cible (update-grub en chroot + vérification UUID) ──
fix_grub(){
    _dir_vars "${1:-clone}" || return 1
    banner "Réparation GRUB de la cible ($D_MODE) (update-grub en chroot)"
    _require_direction || return 1
    local dev_root dev_efi U_SRC U_DST cfg efi_cfg n_src n_dst rc=0 base=${#CHROOT_MOUNTS[@]}
    dev_root=$(dev_from_label "$D_DST_ROOT"); dev_efi=$(dev_from_label "$D_DST_EFI")
    [[ -n "$dev_root" && -n "$dev_efi" ]] || { err "Partition root/EFI de la cible introuvable"; return 1; }
    mountpoint -q "$D_MNT" || { err "Root de la cible non monté ($D_MNT)"; return 1; }
    # UUID lus dynamiquement (comme fix_fstab)
    U_SRC=$(blkid -o value -s UUID "$(dev_from_label "$D_SRC_ROOT")")
    U_DST=$(blkid -o value -s UUID "$dev_root")
    [[ -n "$U_SRC" && -n "$U_DST" ]] || { err "UUID root source/cible introuvable"; return 1; }
    cfg="$D_MNT/boot/grub/grub.cfg"; efi_cfg="$D_MNT/boot/efi/EFI/ubuntu/grub.cfg"

    # Ctrl-C : démonter proprement (uniquement NOS montages) avant de sortir
    trap "cleanup_chroot $base; exit 130" INT TERM

    # Montages : EFI de la cible puis bind dev, dev/pts, proc, sys, run
    if ! mountpoint -q "$D_MNT/boot/efi"; then
        _cm "$dev_efi" "$D_MNT/boot/efi" || rc=1
    fi
    if [[ $rc -eq 0 ]]; then
        _cm --bind /dev     "$D_MNT/dev"     && \
        _cm --bind /dev/pts "$D_MNT/dev/pts" && \
        _cm --bind /proc    "$D_MNT/proc"    && \
        _cm --bind /sys     "$D_MNT/sys"     && \
        _cm --bind /run     "$D_MNT/run"     || rc=1
    fi
    # Régénération de grub.cfg DANS la cible (les UUID deviennent ceux de la cible)
    if [[ $rc -eq 0 ]]; then
        chroot "$D_MNT" update-grub 2>&1 | tee -a "$LOG"
        [[ ${PIPESTATUS[0]} -eq 0 ]] || rc=1
    fi
    # Sens inverse : installer GRUB sur l'EFI si elle est vide/périmée (+ NVRAM)
    if [[ $rc -eq 0 && "$D_MODE" == "restore" ]]; then
        _grub_install_efi "$D_MNT" "$U_DST" "$dev_efi" || rc=1
    fi

    # Vérifications (EFI encore montée à ce stade)
    if [[ $rc -eq 0 ]]; then
        if [[ -f "$cfg" ]]; then
            n_src=$(grep -c "$U_SRC" "$cfg" || true); n_dst=$(grep -c "$U_DST" "$cfg" || true)
        else n_src=1; n_dst=0; fi
        echo "  grub.cfg cible : UUID source=${n_src:-0} (attendu 0) · UUID cible=${n_dst:-0} (attendu >0)"
        if [[ "${n_src:-0}" -ne 0 || "${n_dst:-0}" -eq 0 ]]; then
            err "grub.cfg de la cible incorrect (UUID source présent ou UUID cible absent)"; rc=1
        fi
        if ! grep -q "$U_DST" "$efi_cfg" 2>/dev/null; then
            err "EFI/ubuntu/grub.cfg de la cible ne contient pas l'UUID de la cible"; rc=1
        fi
    fi

    # Démontage immédiat de NOS montages + contrôle qu'aucun ne reste sous la cible
    cleanup_chroot "$base" || rc=1
    trap - INT TERM
    if findmnt -rn -o TARGET | grep -q "^$D_MNT/"; then
        err "Des montages restent sous $D_MNT (risque pour le prochain rsync --delete)"; rc=1
    fi
    [[ $rc -eq 0 ]] && ok "GRUB de la cible réparé et vérifié" || err "fix_grub : ÉCHEC"
    return $rc
}

# ─── Option 6 : vérifier la bootabilité de la cible (LECTURE SEULE) ──────────
VB_FAILS=0
_chk(){ if [[ "$2" -eq 0 ]]; then ok "$1"; else err "ÉCHEC : $1"; VB_FAILS=$((VB_FAILS+1)); fi; }

verify_boot(){
    _dir_vars "${1:-clone}" || return 1
    banner "Bootabilité de la cible ($D_MODE) (lecture seule)"
    VB_FAILS=0
    local dev_root dev_efi U_SRC U_DST n_src n_dst pair lbl_s lbl_d us ud rc tmp_efi lbl_boot
    local cfg="$D_MNT/boot/grub/grub.cfg" fstab="$D_MNT/etc/fstab"
    mountpoint -q "$D_MNT" || { [[ "$D_MODE" == "clone" ]] && ensure_mounted "$D_DST_ROOT" "$D_MNT"; } || { err "Racine de la cible non montée ($D_MNT)"; return 1; }
    dev_root=$(dev_from_label "$D_DST_ROOT"); dev_efi=$(dev_from_label "$D_DST_EFI")
    U_SRC=$(blkid -o value -s UUID "$(dev_from_label "$D_SRC_ROOT")")
    U_DST=$(blkid -o value -s UUID "$dev_root")

    # 1) grub.cfg de la cible : 0 UUID source, >0 UUID cible
    n_src=$(grep -c "$U_SRC" "$cfg" 2>/dev/null || true); n_dst=$(grep -c "$U_DST" "$cfg" 2>/dev/null || true)
    [[ "${n_src:-0}" -eq 0 && "${n_dst:-0}" -gt 0 ]]; _chk "grub.cfg root (source=${n_src:-0}, cible=${n_dst:-0})" $?

    # 2) EFI/ubuntu/grub.cfg de la cible (montage temporaire en lecture seule)
    tmp_efi=$(mktemp -d /tmp/zeta_efi_XXXXXX); rc=1
    if mount -o ro "$dev_efi" "$tmp_efi" 2>/dev/null; then
        grep -q "$U_DST" "$tmp_efi/EFI/ubuntu/grub.cfg" 2>/dev/null; rc=$?
        umount "$tmp_efi"
    fi
    rmdir "$tmp_efi" 2>/dev/null
    _chk "EFI grub.cfg pointe vers l'UUID de la cible" $rc

    # 3) fstab : aucun UUID source (root/home/data/EFI) et UUID cible présents
    rc=0
    for pair in "$D_SRC_ROOT:$D_DST_ROOT" "$D_SRC_HOME:$D_DST_HOME" "$D_SRC_DATA:$D_DST_DATA" "$D_SRC_EFI:$D_DST_EFI"; do
        lbl_s=${pair%%:*}; lbl_d=${pair##*:}
        us=$(blkid -o value -s UUID "$(dev_from_label "$lbl_s")"); ud=$(blkid -o value -s UUID "$(dev_from_label "$lbl_d")")
        [[ -n "$us" ]] && grep -q "$us" "$fstab" 2>/dev/null && rc=1
        [[ -n "$ud" ]] && ! grep -q "$ud" "$fstab" 2>/dev/null && rc=1
    done
    _chk "fstab : UUID de la cible partout, aucun UUID de la source" $rc

    # 4) resume : absent / none = OK ; sinon l'UUID doit être sur le même disque que la cible
    local rf="$D_MNT/etc/initramfs-tools/conf.d/resume" line ruuid rdev
    rc=0
    if [[ -f "$rf" ]]; then
        line=$(grep -E '^RESUME=' "$rf" | tail -1)
        if [[ -n "$line" && "$line" != "RESUME=none" ]]; then
            ruuid=$(echo "$line" | sed -n 's/^RESUME=UUID=//p'); rdev=""
            [[ -n "$ruuid" ]] && rdev=$(blkid -U "$ruuid" 2>/dev/null)
            if [[ -z "$rdev" ]]; then
                rc=1; warn "resume : RESUME=UUID=${ruuid:-?} absent de tous les disques (le boot attendrait une partition inexistante)"
            elif [[ "$(lsblk -no PKNAME "$rdev")" != "$(lsblk -no PKNAME "$dev_root")" ]]; then
                rc=1; warn "resume : l'UUID ${ruuid} est sur un autre disque que la cible ($rdev)"
            fi
            [[ $rc -ne 0 ]] && warn "ALERTE seulement : aucune correction automatique, éditer $rf à la main puis update-initramfs en chroot"
        fi
    fi
    _chk "initramfs resume (absent ou sur le disque de la cible)" $rc

    # 5) étiquette de boot sur la cible (bande verte Seagate / rouge Toshiba)
    [[ -x "$D_MNT/usr/local/bin/zeta-boot-id" ]];              _chk "zeta-boot-id présent sur la cible" $?
    [[ -f "$D_MNT/etc/xdg/autostart/zeta-boot-id.desktop" ]];  _chk "autostart zeta-boot-id présent" $?
    grep -q 'zeta-boot-id' "$D_MNT/etc/bash.bashrc" 2>/dev/null; _chk "ligne zeta-boot-id dans bash.bashrc" $?
    # B7 : le label de la racine de la cible doit tomber dans la bonne branche du case de zeta-boot-id
    lbl_boot=$(lsblk -no LABEL "$dev_root" | head -1)
    [[ "$lbl_boot" == "$D_BOOT_PREFIX"* ]] && grep -q "$D_BOOT_PREFIX\*)" "$D_MNT/usr/local/bin/zeta-boot-id" 2>/dev/null
    _chk "zeta-boot-id : label racine '$lbl_boot' -> branche ${D_BOOT_PREFIX}* (bande attendue)" $?

    echo
    [[ $VB_FAILS -eq 0 ]] && ok "Cible bootable (contrôles statiques OK — le test réel reste le reboot)" \
                          || err "$VB_FAILS contrôle(s) en échec"
    return $(( VB_FAILS > 0 ))
}

# ─── Option 7 : réparer le boot du clone seulement (sans rsync) ──────────────
do_repair_boot(){
    banner "Réparation du boot du clone (fstab + GRUB, sans rsync)"
    require_root_label "$LBL_SG_ROOT" || return 1    # A2 : AVANT toute question/écriture
    [[ $DRYRUN_ONLY -eq 1 ]] && { warn "Mode --dry-run : rien à simuler pour la réparation du boot"; return 1; }
    confirm "Écriture sur le Toshiba : fstab corrigé + update-grub en chroot. Continuer ?" || return 1
    ensure_mounted "$LBL_ROOT" "$MNT_ROOT" || return 1
    fix_fstab
    fix_grub || return 1
    verify_boot
}

# ─── Option 8 : RESTAURATION Toshiba -> disque de travail (sens inverse) ──────
# Labels de la CIBLE : mêmes noms que sur le Seagate d'origine (cf. cahier des charges v2.4)
LBL_TGT_ROOT="Seagate-PC1-root"
LBL_TGT_HOME="Seagate-PC1-home"
LBL_TGT_DATA="Seagate-PC1-data"
LBL_TGT_EFI="SG-PC1-EFI"
RESTORE_BASE="/mnt/zeta_restore"      # points de montage dédiés (marche aussi depuis une clé Live)
RS_ROOT=""; RS_HOME=""; RS_DATA=""    # points de montage SOURCE (Toshiba)
RT_ROOT=""; RT_HOME=""; RT_DATA=""    # points de montage CIBLE (disque de travail)

# Renvoie dans la variable $4 le point de montage de la partition <label> :
# celui qui existe déjà (ex. "/" si on est démarré sur le Toshiba, ou automontage
# GNOME/Live), sinon un montage neuf sous $RESTORE_BASE/<nom> avec les options $3.
# (nameref plutôt que $(...) : un sous-shell perdrait l'enregistrement du montage
#  dans CHROOT_MOUNTS, donc le démontage garanti par le trap EXIT)
mount_for_restore(){
    local label="$1" name="$2" opts="$3" dev mnt
    local -n _out="$4"
    dev=$(dev_from_label "$label")
    [[ -n "$dev" ]] || { err "Partition '$label' introuvable"; return 1; }
    mnt=$(findmnt -rn -o TARGET -S "$dev" | head -1)
    if [[ -n "$mnt" ]]; then
        info "$label déjà monté sur $mnt (réutilisé)"
    else
        mnt="$RESTORE_BASE/$name"; mkdir -p "$mnt"
        _cm -o "$opts" "$dev" "$mnt" || return 1
        ok "$label monté ($dev -> $mnt, $opts)"
    fi
    _out="$mnt"
}

# Post-restauration sur la cible (B6) : fstab inversé, GRUB inversé (+ grub-install si EFI vide), contrôles
restore_post(){
    fix_fstab restore || return 1
    fix_grub  restore || return 1
    verify_boot restore
}

# Garde-fous B1/B2 + montages source/cible : commun à l'option 8 et à l'option 10
_restore_prepare(){
    local cur run_dev l missing_tgt=0 missing_src=0 d_troot d_sroot opts_t="rw"
    cur=$(current_root_label)
    run_dev=$(findmnt -no SOURCE /)
    [[ $DRYRUN_ONLY -eq 1 ]] && { warn "MODE SIMULATION (--dry-run) : cible montée en lecture seule, aucune écriture"; opts_t="ro"; }

    # ── B1 : garde-fou inverse — jamais de restauration sur le système en cours ──
    if [[ "$cur" == "$LBL_TGT_ROOT" ]]; then
        err "Restauration refusée : la racine en cours ('$cur') est le disque CIBLE."
        err "Démarre sur le Toshiba (ou sur une clé Ubuntu Live) puis relance."
        return 1
    fi

    # ── B2 : pré-requis — partitions étiquetées sur la cible, et Toshiba présent ──
    for l in "$LBL_TGT_ROOT" "$LBL_TGT_HOME" "$LBL_TGT_DATA" "$LBL_TGT_EFI"; do
        [[ -n "$(dev_from_label "$l")" ]] || { err "Cible : partition '$l' absente"; missing_tgt=1; }
    done
    for l in "$LBL_ROOT" "$LBL_HOME" "$LBL_DATA"; do
        [[ -n "$(dev_from_label "$l")" ]] || { err "Source : partition '$l' absente (Toshiba branché ?)"; missing_src=1; }
    done
    [[ $missing_src -eq 1 ]] && return 1
    if [[ $missing_tgt -eq 1 ]]; then
        warn "Le disque cible n'a pas les 4 partitions étiquetées attendues."
        warn "Disque neuf ou vierge : utilise l'option 9 (préparation d'un disque neuf)."
        return 1
    fi

    d_troot=$(dev_from_label "$LBL_TGT_ROOT"); d_sroot=$(dev_from_label "$LBL_ROOT")
    # Défense en profondeur (indépendante des labels) : la cible n'est JAMAIS la racine en cours
    if [[ "$d_troot" == "$run_dev" ]]; then
        err "Restauration refusée : $d_troot est la racine en cours d'exécution."; return 1
    fi
    # Source et cible sur le même disque physique = absurde et destructeur
    if [[ "$(lsblk -no PKNAME "$d_troot")" == "$(lsblk -no PKNAME "$d_sroot")" ]]; then
        err "Restauration refusée : source et cible sont sur le même disque physique."; return 1
    fi
    # Les 4 partitions cibles doivent être sur le MÊME disque
    local pk_ref; pk_ref=$(lsblk -no PKNAME "$d_troot")
    for l in "$LBL_TGT_HOME" "$LBL_TGT_DATA" "$LBL_TGT_EFI"; do
        if [[ "$(lsblk -no PKNAME "$(dev_from_label "$l")")" != "$pk_ref" ]]; then
            err "Cible incohérente : '$l' n'est pas sur le même disque que '$LBL_TGT_ROOT'"; return 1
        fi
    done
    ok "Garde-fous OK — racine en cours : '${cur:-inconnue}' · cible : /dev/$pk_ref ($LBL_TGT_ROOT…)"
    LOG="/tmp/zeta_restore_${DATE}.log"      # /home/riemann peut être la SOURCE (démarré sur le Toshiba)

    # ── Montages : source (Toshiba) en lecture seule, cible selon le mode ──
    mkdir -p "$RESTORE_BASE"
    mount_for_restore "$LBL_ROOT"     src-root ro        RS_ROOT || return 1
    mount_for_restore "$LBL_HOME"     src-home ro        RS_HOME || return 1
    mount_for_restore "$LBL_DATA"     src-data ro        RS_DATA || return 1
    mount_for_restore "$LBL_TGT_ROOT" tgt-root "$opts_t" RT_ROOT || return 1
    mount_for_restore "$LBL_TGT_HOME" tgt-home "$opts_t" RT_HOME || return 1
    mount_for_restore "$LBL_TGT_DATA" tgt-data "$opts_t" RT_DATA || return 1
}

# Option 8 : restauration COMPLÈTE (dry-run, puis rsync --delete, puis fstab/GRUB)
_do_restore(){
    _restore_prepare || return 1

    # ── B4 : dry-run automatique AVANT toute écriture ──
    banner "Dry-run automatique (aucune modification à ce stade)"
    DRYRUN_TOTAL=0; DRYRUN_DEL=0
    # ${X%/}/ : "/" reste "/", "/mnt/x" devient "/mnt/x/" (sémantique rsync « contenu de »)
    dryrun_report "restore_root" "${RS_ROOT%/}/" "${RT_ROOT%/}/" \
        --exclude='/lost+found' --exclude='/swapfile' --exclude="$RESTORE_BASE"
    dryrun_report "restore_home" "${RS_HOME%/}/" "${RT_HOME%/}/" --exclude='lost+found' --exclude="$EXCLUDE_SAP"
    dryrun_report "restore_data" "${RS_DATA%/}/" "${RT_DATA%/}/" --exclude='lost+found'
    echo
    echo "  TOTAL : ${DRYRUN_TOTAL} changement(s), dont ${DRYRUN_DEL} suppression(s) côté CIBLE"
    info "Détail complet dans : $DRYRUN_DIR/dryrun_restore_{root,home,data}.log"
    warn "SAP : exclu de la restauration. Le Toshiba n'en garde qu'une ANCIENNE copie pré-exclusion (non restaurée ici)."
    info "Ce qui existe déjà côté cible dans Documents/SAP* est préservé (jamais supprimé)."

    if [[ $DRYRUN_ONLY -eq 1 ]]; then
        ok "Mode simulation (--dry-run) : arrêt ici, aucune écriture effectuée"; return 0
    fi
    # ── B5 : rsync Toshiba -> cible (mêmes options que le clone) ──
    echo
    warn "Cette opération ÉCRASE le disque cible (suppression des fichiers en trop côté cible) :"
    echo "     ${RS_ROOT}  → ${RT_ROOT}"
    echo "     ${RS_HOME}  → ${RT_HOME}  (exclusion : $EXCLUDE_SAP)"
    echo "     ${RS_DATA}  → ${RT_DATA}"
    confirm "Résumé vérifié. Lancer la VRAIE restauration (suppressions incluses) ?" || return 1

    local RSO="-aAXHx --delete --info=progress2"
    banner "1/3 — Racine  →  $LBL_TGT_ROOT"
    rsync $RSO --exclude='/lost+found' --exclude='/swapfile' --exclude="$RESTORE_BASE" \
        "${RS_ROOT%/}/" "${RT_ROOT%/}/" 2>&1 | tee -a "$LOG"
    banner "2/3 — Home  →  $LBL_TGT_HOME"
    rsync $RSO --exclude='lost+found' --exclude="$EXCLUDE_SAP" "${RS_HOME%/}/" "${RT_HOME%/}/" 2>&1 | tee -a "$LOG"
    banner "3/3 — Data  →  $LBL_TGT_DATA"
    rsync $RSO --exclude='lost+found' "${RS_DATA%/}/" "${RT_DATA%/}/" 2>&1 | tee -a "$LOG"
    ok "Données restaurées — log : $LOG"

    restore_post || { err "Post-restauration échouée : la cible n'est PAS bootable"; return 1; }
}

# Enveloppe : démontage garanti (ordre inverse) quoi qu'il arrive dans la fonction lancée
_restore_wrap(){
    local rc
    "$@"; rc=$?
    cleanup_chroot || rc=1
    rmdir "$RESTORE_BASE"/* "$RESTORE_BASE" 2>/dev/null    # ne supprime que des dossiers VIDES
    return $rc
}
do_restore(){      banner "RESTAURATION Toshiba → disque de travail (sens inverse)"; _restore_wrap _do_restore; }
do_restore_only(){ banner "RESTAURATION CIBLÉE d'un chemin (Toshiba → disque de travail)"; _restore_wrap _do_restore_only; }

# ─── Option 9 : préparer un disque NEUF (GPT + mkfs) pour la restauration ─────
# Plan = tailles du Seagate d'origine, en MiB : EFI 1G · root 74,5G · home 186,3G · data 662,2G · swap 7,5G
# ZETA_TEST_LABEL_PREFIX (TEST uniquement, 1-6 car. [A-Za-z0-9]) : labels "<P>-root"… et tailles
# réduites (~1 Go) pour valider ce code sur un fichier image loop, sans disque réel ni doublon de labels.
ND_L_EFI=""; ND_L_ROOT=""; ND_L_HOME=""; ND_L_DATA=""; ND_L_SWAP=""
ND_S_EFI=0; ND_S_ROOT=0; ND_S_HOME=0; ND_S_DATA=0; ND_S_SWAP=0; ND_TOTAL=0
_nd_plan(){
    local p="${ZETA_TEST_LABEL_PREFIX:-}"
    if [[ -n "$p" ]]; then
        [[ "$p" =~ ^[A-Za-z0-9]{1,6}$ ]] || { err "ZETA_TEST_LABEL_PREFIX invalide (1-6 caractères alphanumériques)"; return 1; }
        ND_L_EFI="${p}-EFI"; ND_L_ROOT="${p}-root"; ND_L_HOME="${p}-home"; ND_L_DATA="${p}-data"; ND_L_SWAP="${p}-swap"
        ND_S_EFI=100; ND_S_ROOT=300; ND_S_HOME=200; ND_S_DATA=300; ND_S_SWAP=64
    else
        ND_L_EFI="$LBL_TGT_EFI"; ND_L_ROOT="$LBL_TGT_ROOT"; ND_L_HOME="$LBL_TGT_HOME"; ND_L_DATA="$LBL_TGT_DATA"; ND_L_SWAP="SG-PC1-swap"
        ND_S_EFI=1024; ND_S_ROOT=76288; ND_S_HOME=190771; ND_S_DATA=678093; ND_S_SWAP=7680
    fi
    ND_TOTAL=$(( ND_S_EFI + ND_S_ROOT + ND_S_HOME + ND_S_DATA + ND_S_SWAP ))
}

# Chemin de la partition n° $2 du disque $1 (fiable pour sdX, nvme, loop)
_nd_part(){ lsblk -nlo PATH,PARTN "$1" | awk -v n="$2" '$2==n{print $1}'; }

do_newdisk(){
    banner "DISQUE NEUF — partitionnement GPT + systèmes de fichiers"
    _nd_plan || return 1
    local t l d sz real_sz real_b run_src run_disk plan_ok=1
    # Outils nécessaires (rien n'est écrit tant qu'ils ne sont pas tous là)
    for t in sgdisk mkfs.ext4 mkfs.vfat mkswap partprobe udevadm; do
        command -v "$t" >/dev/null || { err "Outil manquant : $t (sudo apt install gdisk dosfstools util-linux parted)"; plan_ok=0; }
    done
    [[ $plan_ok -eq 1 ]] || return 1

    # Doublons de labels = blkid -L ambigu = restauration dangereuse : on refuse
    for l in "$ND_L_EFI" "$ND_L_ROOT" "$ND_L_HOME" "$ND_L_DATA" "$ND_L_SWAP"; do
        if [[ -n "$(dev_from_label "$l")" ]]; then
            err "Label '$l' déjà présent sur un disque branché : création refusée (doublon)."
            err "Débranche le disque portant ce label (ex. Seagate défectueux) puis relance."
            return 1
        fi
    done

    echo "  Disques détectés :"
    lsblk -o NAME,SIZE,MODEL,SERIAL,TRAN,LABEL | sed 's/^/    /'
    echo
    read -rp "  Chemin COMPLET du disque neuf à effacer (ex. /dev/sdc) : " d
    [[ -n "$d" ]] || { warn "Annulé."; return 1; }
    d=$(readlink -f "$d" 2>/dev/null)
    [[ -b "$d" ]] || { err "'$d' n'est pas un périphérique bloc"; return 1; }
    t=$(lsblk -dno TYPE "$d" 2>/dev/null)
    local allow_loop=0; [[ -n "${ZETA_TEST_LABEL_PREFIX:-}" ]] && allow_loop=1   # loop = fichier image de test seulement
    if [[ "$t" != "disk" && ! ( "$t" == "loop" && $allow_loop -eq 1 ) ]]; then
        err "'$d' n'est pas un disque entier (type '$t') : partition ou périphérique refusé"; return 1
    fi
    # Jamais le disque qui porte le système en cours
    run_src=$(findmnt -no SOURCE /); run_disk=$(lsblk -no PKNAME "$run_src" 2>/dev/null | head -1)
    if [[ -n "$run_disk" && "/dev/$run_disk" == "$d" ]]; then
        err "Refusé : $d porte le système en cours d'exécution"; return 1
    fi
    # Jamais un disque du projet (Toshiba, Seagate, EFI, clones) ni un disque dont une partition est montée
    if lsblk -nlo LABEL "$d" | grep -Eqi '^(Toshiba|TSB|Seagate|SG)-|^swap-clone'; then
        err "Refusé : $d porte une partition de label Toshiba-*/TSB-*/Seagate-*/SG-* (disque existant du projet)"; return 1
    fi
    if lsblk -nlo MOUNTPOINT "$d" | grep -q .; then
        err "Refusé : au moins une partition de $d est montée"; return 1
    fi
    # Double saisie : la taille doit correspondre à celle affichée par lsblk
    real_sz=$(lsblk -dno SIZE "$d"); real_b=$(lsblk -bdno SIZE "$d")
    read -rp "  Tape la taille de $d telle qu'affichée ci-dessus (ex. $real_sz) : " sz
    if [[ "${sz//./,}" != "${real_sz//./,}" ]]; then
        err "Taille saisie ('$sz') ≠ taille réelle ('$real_sz') : abandon"; return 1
    fi
    if (( real_b / 1048576 < ND_TOTAL + 4 )); then
        err "Disque trop petit : $(( real_b / 1048576 )) MiB disponibles, $(( ND_TOTAL + 4 )) MiB nécessaires"; return 1
    fi

    echo
    info "Contenu ACTUEL de $d (sera DÉTRUIT) :"
    lsblk -o NAME,SIZE,FSTYPE,LABEL "$d" | sed 's/^/    /'
    echo
    info "Plan GPT proposé sur $d ($real_sz, modèle : $(lsblk -dno MODEL "$d" | xargs)) :"
    printf "    %-3s %-14s %9s MiB  %s\n" 1 "$ND_L_EFI"  "$ND_S_EFI"  "EFI (FAT32, ef00)"
    printf "    %-3s %-14s %9s MiB  %s\n" 2 "$ND_L_ROOT" "$ND_S_ROOT" "racine (ext4)"
    printf "    %-3s %-14s %9s MiB  %s\n" 3 "$ND_L_HOME" "$ND_S_HOME" "home (ext4)"
    printf "    %-3s %-14s %9s MiB  %s\n" 4 "$ND_L_DATA" "$ND_S_DATA" "data (ext4)"
    printf "    %-3s %-14s %9s MiB  %s\n" 5 "$ND_L_SWAP" "$ND_S_SWAP" "swap"
    echo "    Espace non alloué restant : $(( real_b / 1048576 - ND_TOTAL )) MiB (tailles = celles du Seagate d'origine)"
    if [[ $DRYRUN_ONLY -eq 1 ]]; then
        ok "Mode simulation (--dry-run) : plan affiché, aucune écriture effectuée"; return 0
    fi
    confirm "EFFACEMENT TOTAL de $d ($real_sz) puis création des 5 partitions ci-dessus. Continuer ?" || return 1

    # ── Écriture : à partir d'ici, $d est modifié ──
    sgdisk --zap-all "$d" >/dev/null 2>&1; true      # codes de retour de zap-all non fiables sur disque vierge
    sgdisk -n "1:0:+${ND_S_EFI}M"  -t 1:ef00 -c "1:$ND_L_EFI"  \
           -n "2:0:+${ND_S_ROOT}M" -t 2:8300 -c "2:$ND_L_ROOT" \
           -n "3:0:+${ND_S_HOME}M" -t 3:8300 -c "3:$ND_L_HOME" \
           -n "4:0:+${ND_S_DATA}M" -t 4:8300 -c "4:$ND_L_DATA" \
           -n "5:0:+${ND_S_SWAP}M" -t 5:8200 -c "5:$ND_L_SWAP" "$d" || { err "sgdisk a échoué sur $d"; return 1; }
    partprobe "$d" 2>/dev/null; udevadm settle
    local p1 p2 p3 p4 p5
    p1=$(_nd_part "$d" 1); p2=$(_nd_part "$d" 2); p3=$(_nd_part "$d" 3); p4=$(_nd_part "$d" 4); p5=$(_nd_part "$d" 5)
    [[ -n "$p1" && -n "$p2" && -n "$p3" && -n "$p4" && -n "$p5" ]] || { err "Partitions non détectées après sgdisk"; return 1; }

    mkfs.vfat -F32 -n "$ND_L_EFI" "$p1" >/dev/null   || { err "mkfs.vfat $p1 échoué"; return 1; }
    mkfs.ext4 -q -L "$ND_L_ROOT" "$p2"               || { err "mkfs.ext4 $p2 échoué"; return 1; }
    mkfs.ext4 -q -L "$ND_L_HOME" "$p3"               || { err "mkfs.ext4 $p3 échoué"; return 1; }
    mkfs.ext4 -q -L "$ND_L_DATA" "$p4"               || { err "mkfs.ext4 $p4 échoué"; return 1; }
    mkswap -L "$ND_L_SWAP" "$p5" >/dev/null          || { err "mkswap $p5 échoué"; return 1; }
    udevadm settle

    # Contrôle : chaque label doit pointer vers la bonne partition
    local rc=0 pair
    for pair in "$ND_L_EFI:$p1" "$ND_L_ROOT:$p2" "$ND_L_HOME:$p3" "$ND_L_DATA:$p4" "$ND_L_SWAP:$p5"; do
        [[ "$(dev_from_label "${pair%%:*}")" == "${pair##*:}" ]] && ok "${pair%%:*} → ${pair##*:}" \
            || { err "Label ${pair%%:*} ne pointe pas vers ${pair##*:}"; rc=1; }
    done
    lsblk -o NAME,SIZE,FSTYPE,LABEL "$d" | sed 's/^/    /'
    [[ $rc -eq 0 ]] && ok "Disque prêt. Étape suivante : option 8 (restauration Toshiba → ce disque)"
    return $rc
}

# ─── Option 10 : restauration CIBLÉE d'un fichier ou dossier (sous /home ou /mnt/data) ──
# Sans --delete : on ajoute/remplace seulement, rien n'est supprimé sur la cible.
# Pas de fstab/GRUB : seul le chemin demandé est écrit.
ONLY_PATH=""      # renseigné par --only, sinon demandé à l'écran
_do_restore_only(){
    local p="$ONLY_PATH" base rel src_base dst_base logf total
    [[ -n "$p" ]] || read -rp "  Chemin ABSOLU à restaurer (sous /home ou /mnt/data) : " p
    p="${p%/}"
    if [[ "$p" != /* || "$p" == */../* || "$p" == */.. ]]; then
        err "Chemin absolu sans '..' exigé"; return 1
    fi
    case "$p" in
        /home/*)     base="/home" ;;
        /mnt/data/*) base="/mnt/data" ;;
        *) err "Restauration ciblée limitée à /home/… et /mnt/data/… (le système entier : option 8)"; return 1 ;;
    esac
    rel="${p#"$base"/}"
    if [[ "$base" == "/home" && "$rel" == riemann/Documents/SAP* ]]; then
        err "SAP : exclu des restaurations (ancienne copie pré-exclusion sur le Toshiba, hors périmètre)"; return 1
    fi

    _restore_prepare || return 1       # mêmes garde-fous B1/B2 et mêmes montages que l'option 8
    if [[ "$base" == "/home" ]]; then src_base="${RS_HOME%/}"; dst_base="${RT_HOME%/}"
    else                              src_base="${RS_DATA%/}"; dst_base="${RT_DATA%/}"; fi
    [[ -e "$src_base/$rel" ]] || { err "Absent du Toshiba : $src_base/$rel"; return 1; }

    # --relative + marqueur "/./" : recrée l'arborescence parente sur la cible
    local RSO=(-aAXH --relative)
    banner "Dry-run ciblé (aucune modification à ce stade)"
    mkdir -p "$DRYRUN_DIR"; logf="$DRYRUN_DIR/dryrun_only.log"
    rsync "${RSO[@]}" --dry-run --itemize-changes "$src_base/./$rel" "$dst_base/" > "$logf" 2>&1 \
        || { err "Dry-run rsync en échec (voir $logf)"; return 1; }
    total=$(wc -l < "$logf")
    echo "  ${total} élément(s) à écrire sur la cible (extrait) :"
    head -30 "$logf" | sed 's/^/    /'
    [[ "$total" -gt 30 ]] && echo "    … (suite dans $logf)"
    [[ "$total" -eq 0 ]] && info "Rien à faire : la cible est déjà identique au Toshiba pour ce chemin."
    if [[ $DRYRUN_ONLY -eq 1 ]]; then
        ok "Mode simulation (--dry-run) : arrêt ici, aucune écriture effectuée"; return 0
    fi
    [[ "$total" -eq 0 ]] && return 0

    echo
    warn "Restaure  $src_base/$rel  →  $dst_base/$rel   (SANS suppression : le surplus côté cible est conservé)"
    confirm "Résumé vérifié. Lancer la restauration ciblée ?" || return 1
    rsync "${RSO[@]}" --info=progress2 "$src_base/./$rel" "$dst_base/" 2>&1 | tee -a "$LOG"
    [[ ${PIPESTATUS[0]} -eq 0 ]] || { err "rsync en échec (voir $LOG)"; return 1; }
    ls -ld "$dst_base/$rel"
    ok "Restauré : $dst_base/$rel — log : $LOG"
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
    banner "ZÊTA — Clone PC1 ⇄ Toshiba (allégé)  v2.4"
    echo "  1) Clone incrémental PC1 → Toshiba  (dry-run auto + / , /home [SAP exclu] , /mnt/data)"
    echo "  2) Contrôle SMART Toshiba"
    echo "  3) Vérifier le montage"
    echo "  4) État des sauvegardes (espace)"
    echo "  5) Démonter proprement"
    echo "  6) Vérifier la bootabilité du clone (lecture seule)"
    echo "  7) Réparer le boot du clone seulement (fstab + GRUB, sans rsync)"
    echo "  8) Restaurer Toshiba → disque de travail (sens inverse)"
    echo "  9) Préparer un disque NEUF (GPT + mkfs, labels du Seagate) — avant l'option 8"
    echo " 10) Restaurer UN fichier/dossier précis (sous /home ou /mnt/data, sans suppression)"
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
        8) do_restore ;;
        9) do_newdisk ;;
        10) do_restore_only ;;
        0) echo "Bye."; exit 0 ;;
        *) warn "Choix invalide"; sleep 1 ;;
    esac
    echo; read -rp "  Entrée pour revenir au menu…" _; main_menu
}

# ─── Arguments ────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRYRUN_ONLY=1 ;;
        --only)    [[ -n "${2:-}" ]] || { err "--only exige un chemin absolu"; exit 2; }
                   ONLY_PATH="$2"; shift ;;
        -h|--help) echo "Usage : sudo bash $0 [--dry-run] [--only CHEMIN]"
                   echo "  --dry-run     : options 1, 8, 9, 10 s'arrêtent avant toute écriture (plan / dry-run rsync)"
                   echo "  --only CHEMIN : chemin utilisé par l'option 10 (restauration ciblée), sinon demandé à l'écran"
                   exit 0 ;;
        *) err "Option inconnue : $1 (voir --help)"; exit 2 ;;
    esac
    shift
done

# ─── Garde root ───────────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    err "À lancer avec sudo :  sudo bash ~/projet_zeta/scripts/zeta_backup_toshiba.sh"
    exit 1
fi

main_menu
