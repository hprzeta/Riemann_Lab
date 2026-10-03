#!/usr/bin/env bash
# =============================================================================
#  zeta_inventaire.sh  (v2) — Inventaire du cluster Zeta (LECTURE SEULE)
#
#  À lancer depuis PC1 (riemann@zeta-lab). Pour PC2..PC5, le script se connecte
#  en SSH avec les alias de ~/.ssh/config (zeta-calc-second, zeta-backup,
#  zeta-secure, zeta-monitor) et exécute un inventaire qui ne MODIFIE RIEN.
#
#  - Aucune IP, aucun mot de passe, aucune clé n'est écrit dans ce script.
#  - Les secrets (psk, passphrase, wgkey, PrivateKey, token...) sont masqués.
#  - Résultats : ~/zeta_inventaire/ (dossier privé, hors dépôt Git).
#  - Parties qui demandent root (RAM, SMART, pare-feu...) : si sudo/doas sans
#    mot de passe n'est pas disponible, le script propose le « complément
#    root » : TU tapes le mot de passe sudo/doas toi-même (jamais stocké).
#
#  Usage :  ./zeta_inventaire.sh            (menu)
#           ./zeta_inventaire.sh 5          (inventaire PC5 direct)
#           ./zeta_inventaire.sh tous       (les 5 PC)
#           ./zeta_inventaire.sh root 5     (complément root pour PC5)
#           ./zeta_inventaire.sh ajout      (ajout d'un PC, mode à blanc)
# =============================================================================

OUT_DIR="${ZETA_INVENTAIRE_DIR:-$HOME/zeta_inventaire}"
NOMS=(PC1 PC2 PC3 PC4 PC5)
ALIAS=(local zeta-calc-second zeta-backup zeta-secure zeta-monitor)
SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=8 -o ServerAliveInterval=5)
INV_FILES=()

mkdir -p "$OUT_DIR" && chmod 700 "$OUT_DIR"

PAYLOAD="$(mktemp)"
trap 'rm -f "$PAYLOAD"' EXIT

# -----------------------------------------------------------------------------
#  Programme exécuté SUR chaque PC (sh POSIX : fonctionne sous Linux et OpenBSD)
#  Argument 1 : "rootonly" = ne lance que le bloc qui demande les droits root.
# -----------------------------------------------------------------------------
cat > "$PAYLOAD" <<'PAYLOAD_EOF'
#!/bin/sh
MODE="${1:-normal}"
LC_ALL=C; export LC_ALL
PATH="$PATH:/usr/sbin:/sbin:/usr/local/sbin:/usr/local/bin"; export PATH
OS=$(uname -s)

sec()  { printf '\n==================== %s ====================\n' "$1"; }
sub()  { printf '\n--- %s ---\n' "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }
run()  { printf '$ %s\n' "$*"; "$@" 2>&1 || printf '(code retour %s)\n' "$?"; }
# Masque la VALEUR des secrets (le reste de la ligne est conservé quand c'est possible)
mask() {
  sed -E \
    -e 's/((wgkey|wgpsk|wpakey)[[:space:]]+)[^[:space:]]+/\1****/g' \
    -e 's/((^|[[:space:],-])(psk|passphrase|[Pp]rivate[_-]?[Kk]ey|[Pp]reshared[Kk]ey|[Pp]assword|passwd|secret|[Tt]oken|[Aa]pi_?[Kk]ey)[[:space:]=:]+).*/\1****/'
}

# --- Droits root disponibles sans mot de passe ? (jamais de demande interactive ici)
SUDO=""; CANROOT=0
if [ "$(id -u)" -eq 0 ]; then CANROOT=1
elif have sudo && sudo -n true 2>/dev/null; then SUDO="sudo -n"; CANROOT=1
elif have doas && doas -n true 2>/dev/null; then SUDO="doas -n"; CANROOT=1
fi
rr() {
  if [ "$(id -u)" -eq 0 ]; then "$@"
  elif [ -n "$SUDO" ]; then $SUDO "$@"
  else echo "(ignoré : droits root requis) $*"; return 1
  fi
}
rcat() { if [ -r "$1" ]; then cat "$1"; else rr cat "$1"; fi; }
ver()  { have "$1" || return 0; printf '%-10s ' "$1"; "$@" 2>&1 | head -n 1; }

# =============================================================================
#  BLOC ROOT : tout ce qui demande les droits root est regroupé ici
# =============================================================================
root_linux() {
  sub "Barrettes mémoire (dmidecode)"
  rr dmidecode -t memory 2>&1 | grep -E 'ignoré|Size:|Type:|Speed:|Locator:|Manufacturer:|Part Number:|Maximum Capacity|Number Of Devices'

  sub "SMART des disques"
  if have smartctl; then
    for d in /dev/sd? /dev/nvme?n1; do
      [ -b "$d" ] || continue
      echo "# $d"
      rr smartctl -i -H "$d" 2>&1 | grep -E 'ignoré|Model|Device Model|Capacity|Rotation|SMART overall|SMART Health|result'
      rr smartctl -A "$d" 2>&1 | grep -E 'ignoré|Reallocated|Pending|Power_On|Temperature|Wear|Percentage|Available Spare'
    done
  else
    echo "smartctl non installé (apt install smartmontools pour l'état de santé des disques)"
  fi

  sub "Ports en écoute (avec processus)"
  rr ss -tulpn

  sub "Pare-feu"
  have ufw && rr ufw status verbose
  have nft && rr nft list ruleset
  have iptables && rr iptables -S
  have fail2ban-client && rr fail2ban-client status

  sub "WireGuard (clés privées masquées)"
  if have wg; then
    rr wg show
    rr sh -c 'for f in /etc/wireguard/*.conf; do [ -f "$f" ] && { echo "# $f"; cat "$f"; }; done' 2>&1 | mask
  fi

  sub "/etc/network/interfaces et interfaces.d (secrets masqués)"
  for f in /etc/network/interfaces /etc/network/interfaces.d/*; do
    [ -e "$f" ] || continue
    echo "# $f"; rcat "$f" 2>&1 | mask
  done

  sub "sshd : configuration effective"
  rr sshd -T 2>&1 | grep -E 'ignoré|^(port|permitrootlogin|passwordauthentication|pubkeyauthentication|kbdinteractiveauthentication|listenaddress|allowusers|allowgroups|maxauthtries|x11forwarding) '

  sub "crontabs des comptes (root requis)"
  rr sh -c 'for f in /var/spool/cron/crontabs/*; do [ -f "$f" ] && { echo "# $f"; cat "$f"; }; done' 2>&1 | mask
  sub "sudoers.d"
  rr ls -l /etc/sudoers.d 2>&1
}

root_bsd() {
  sub "Disques (disklabel)"
  for d in $(sysctl -n hw.disknames 2>/dev/null | tr ',' ' '); do
    n=${d%%:*}
    echo "# disklabel $n"
    out=$(disklabel "$n" 2>/dev/null) || out=$(rr disklabel "$n" 2>&1)
    echo "$out" | head -n 25
  done

  sub "Pare-feu pf"
  rcat /etc/pf.conf 2>&1 | mask
  rr pfctl -s info 2>&1 | head -n 12

  sub "Services démarrés (rcctl)"
  rr rcctl ls started 2>&1
  rr rcctl ls failed 2>&1

  sub "rc.conf.local et doas.conf"
  rcat /etc/rc.conf.local 2>&1 | mask
  rcat /etc/doas.conf 2>&1 | mask

  sub "crontabs des comptes (root requis)"
  rr sh -c 'for f in /var/cron/tabs/*; do [ -f "$f" ] && { echo "# $f"; cat "$f"; }; done' 2>&1 | mask
}

root_block() {
  sec "$1"
  if [ "$OS" = "Linux" ]; then root_linux; else root_bsd; fi
}

# Mode « complément root » : on lance seulement le bloc root, puis on s'arrête
if [ "$MODE" = "rootonly" ]; then
  echo "Complément root exécuté par : $(id -un) (uid $(id -u)) sur $(hostname)"
  root_block "COMPLEMENT ROOT"
  exit 0
fi

# --- Blocs communs -----------------------------------------------------------
ssh_user_part() {
  sub "Clés et config SSH de $(id -un) (empreintes uniquement, jamais les clés privées)"
  ls -l "$HOME/.ssh" 2>&1
  for k in "$HOME"/.ssh/*.pub; do [ -f "$k" ] && ssh-keygen -lf "$k" 2>&1; done
  if [ -f "$HOME/.ssh/authorized_keys" ]; then
    echo "authorized_keys :"; ssh-keygen -lf "$HOME/.ssh/authorized_keys" 2>&1
  fi
  if [ -f "$HOME/.ssh/config" ]; then
    echo "~/.ssh/config :"; grep -Ev '^[[:space:]]*#' "$HOME/.ssh/config" | mask
  fi
}
comptes() {
  sec "COMPTES"
  run id
  awk -F: '($3>=1000 && $3<60000) || $3==0 {printf "%s uid=%s shell=%s home=%s\n",$1,$3,$7,$6}' /etc/passwd
  run getent group sudo wheel
  run last -n 8
}
scripts_part() {
  sec "SCRIPTS"
  run ls -l /usr/local/bin /usr/local/sbin
  sub "Scripts et fichiers zeta_* wg_* *.sh *.service *.timer dans le home (profondeur 4)"
  find "$HOME" -maxdepth 4 -type f \( -name '*.sh' -o -name 'zeta_*' -o -name 'wg_*' -o -name '*.service' -o -name '*.timer' \) \
    ! -path '*/.cache/*' ! -path '*/.git/*' ! -path '*/node_modules/*' ! -path '*/.local/*' \
    ! -path '*/.config/*' ! -path '*/.vscode*' ! -path '*/.claude/*' ! -path '*/snap/*' \
    -exec ls -l {} + 2>/dev/null
  sub "Environnements Python (pyvenv.cfg)"
  find "$HOME" -maxdepth 4 -name pyvenv.cfg ! -path '*/.cache/*' 2>/dev/null
}

# =============================================================================
sec "IDENTITE"
echo "Hostname      : $(hostname)"
echo "Utilisateur   : $(id -un) (uid $(id -u))"
echo "Date          : $(date '+%Y-%m-%d %H:%M:%S %Z')"
if [ "$CANROOT" -eq 1 ]; then echo "Privileges    : root disponible (${SUDO:-root})"
else echo "Privileges    : NON (certaines sections seront partielles)"; fi
run uname -a
run uptime

if [ "$OS" = "Linux" ]; then

# ------------------------------------------------------------------ LINUX ----
sec "SYSTEME"
run cat /etc/os-release
[ -f /etc/debian_version ] && run cat /etc/debian_version
have lsb_release && run lsb_release -a
run uname -r
[ -f /var/run/reboot-required ] && echo ">>> REDEMARRAGE REQUIS (reboot-required)"

sec "MATERIEL - MACHINE"
for f in sys_vendor product_name product_version board_vendor board_name board_version bios_vendor bios_version bios_date chassis_type; do
  v=$(cat "/sys/class/dmi/id/$f" 2>/dev/null)
  printf '%-16s : %s\n' "$f" "${v:-n/a}"
done

sec "MATERIEL - CPU"
run lscpu

sec "MATERIEL - MEMOIRE"
run free -h
run grep -E 'MemTotal|SwapTotal' /proc/meminfo
have swapon && run swapon --show

sec "MATERIEL - DISQUES"
if lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL,ROTA >/dev/null 2>&1; then
  run lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL,ROTA
else
  run lsblk
fi
run df -hT

sec "MATERIEL - VIDEO / PCI / USB"
have lspci && run lspci
have lsusb && run lsusb
have nvidia-smi && run nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
for f in /sys/class/drm/*/status; do [ -f "$f" ] && echo "$f : $(cat "$f")"; done
run cat /proc/cmdline
have sensors && run sensors
ls /sys/class/power_supply 2>/dev/null | sed 's/^/alimentation : /'

sec "RESEAU"
if ip -br addr >/dev/null 2>&1; then run ip -br addr; else run ip addr; fi
run ip route
run ip -6 route
sub "Interfaces (MAC, état, vitesse, pilote)"
for i in /sys/class/net/*; do
  n=$(basename "$i"); [ "$n" = "lo" ] && continue
  drv=$(basename "$(readlink "$i/device/driver" 2>/dev/null)" 2>/dev/null)
  printf '%s : mac=%s etat=%s vitesse=%s pilote=%s\n' "$n" "$(cat "$i/address" 2>/dev/null)" \
    "$(cat "$i/operstate" 2>/dev/null)" "$(cat "$i/speed" 2>/dev/null)" "$drv"
done
run hostname -f
run cat /etc/hostname
run cat /etc/hosts
run cat /etc/resolv.conf
have resolvectl && run resolvectl status
if have nmcli; then
  run nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device
  run nmcli -t -f NAME,TYPE,DEVICE,AUTOCONNECT connection show
fi
sub "Ports en écoute (sans processus)"
run ss -tuln

sec "SSH - SERVEUR"
have systemctl && systemctl is-active ssh sshd 2>/dev/null
sub "sshd_config (lignes actives)"
grep -hEv '^[[:space:]]*(#|$)' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf 2>&1

sec "LOGICIELS"
sub "Versions des outils clés"
ver python3 --version; ver pip3 --version; ver gcc --version; ver g++ --version
ver make --version; ver cmake --version; ver git --version; ver tmux -V
ver rsync --version; ver rclone version; ver chronyc --version; ver wg --version
ver ssh -V; ver curl --version; ver node --version; ver java -version; ver gdb --version
have nvcc && nvcc --version | tail -n 2
sub "Modules Python clés (python3 système)"
if have python3; then
  for m in mpmath numpy scipy matplotlib flint cupy numba cython sympy; do
    python3 -c "import $m; print('$m', getattr($m,'__version__','?'))" 2>/dev/null || echo "$m : absent"
  done
fi
if have pip3; then sub "pip3 list (système)"; pip3 list 2>/dev/null; fi
sub "Paquets (dpkg)"
if have dpkg-query; then
  echo "Nombre de paquets installés : $(dpkg-query -W -f='${Package}\n' | wc -l)"
  if have apt-mark; then sub "Installés manuellement (apt-mark showmanual)"; apt-mark showmanual | sort; fi
  sub "Liste complète (paquet, version)"
  dpkg-query -W -f='${Package}\t${Version}\n' | sort
fi
have snap && run snap list
have flatpak && run flatpak list

sec "SERVICES ET TACHES PLANIFIEES"
if have systemctl && [ -d /run/systemd/system ]; then
  run systemctl list-unit-files --state=enabled --no-pager
  run systemctl list-units --type=service --state=running --no-pager
  run systemctl --failed --no-pager
  run systemctl list-timers --all --no-pager
  run ls -l /etc/systemd/system
else
  have service && run service --status-all
  have initctl && run initctl list
fi
have timedatectl && run timedatectl
have chronyc && run chronyc tracking
sub "cron de $(id -un)"
run crontab -l
sub "cron système (secrets masqués)"
rcat /etc/crontab 2>&1 | mask
for f in /etc/cron.d/*; do [ -f "$f" ] && { echo "# $f"; mask < "$f"; }; done
run ls /etc/cron.hourly /etc/cron.daily /etc/cron.weekly /etc/cron.monthly
have atq && run atq

sec "MONTAGES (fstab)"
rcat /etc/fstab 2>&1 | mask

sec "MISES A JOUR ET SECURITE"
have apt && echo "Paquets à mettre à jour : $(apt list --upgradable 2>/dev/null | tail -n +2 | wc -l)"
dpkg -l unattended-upgrades 2>/dev/null | tail -n 1

else

# ---------------------------------------------------------------- OPENBSD ----
sec "SYSTEME (BSD)"
run uname -a
run sysctl kern.version
sub "Correctifs installés (syspatch)"
run syspatch -l

sec "MATERIEL (BSD)"
run sysctl hw.vendor hw.product hw.version hw.model hw.ncpu hw.cpuspeed hw.physmem hw.disknames
run sysctl hw.sensors
sub "Détection matérielle au démarrage (dmesg.boot, lignes matériel)"
grep -E ' at |^real mem|^avail mem|^cpu[0-9]*:|^OpenBSD' /var/run/dmesg.boot 2>&1 | head -n 250
sub "Disques"
run df -h

sec "RESEAU (BSD)"
run ifconfig
run netstat -rn
run cat /etc/myname
run cat /etc/mygate
run cat /etc/resolv.conf
run cat /etc/hosts
sub "/etc/hostname.* (clés masquées)"
for f in /etc/hostname.*; do [ -e "$f" ] && { echo "# $f"; rcat "$f" 2>&1 | mask; }; done

sec "SSH - SERVEUR (BSD)"
grep -hEv '^[[:space:]]*(#|$)' /etc/ssh/sshd_config 2>&1
run rcctl check sshd

sec "LOGICIELS (BSD)"
sub "Versions des outils clés"
ver python3 --version; ver git --version; ver rsync --version; ver tmux -V; ver ssh -V
sub "Paquets installés (pkg_info)"
run pkg_info -q

sec "SERVICES ET TACHES PLANIFIEES (BSD)"
run rcctl ls on
sub "cron"
run crontab -l

sec "MONTAGES (fstab)"
rcat /etc/fstab 2>&1 | mask

fi

# Bloc des commandes qui demandent root (ignoré proprement sans sudo/doas)
root_block "DROITS ROOT"

sec "SSH - CLES UTILISATEUR"
ssh_user_part
comptes
scripts_part

sec "FIN DE L'INVENTAIRE"
echo "Inventaire terminé : $(hostname) — $(date '+%Y-%m-%d %H:%M:%S')"
PAYLOAD_EOF

# -----------------------------------------------------------------------------
#  Fonctions du menu
# -----------------------------------------------------------------------------
dernier_inventaire() {   # affiche le chemin du plus récent inventaire d'un PC
  local nom="$1" al="$2"
  ls -1t "$OUT_DIR"/inventaire_"${nom}"_"${al}"_*.txt 2>/dev/null | head -n 1
}

complement_root() {
  local n="$1" nom al out d rc lignes
  nom="${NOMS[$((n-1))]}"; al="${ALIAS[$((n-1))]}"
  out="$(dernier_inventaire "$nom" "$al")"
  if [ -z "$out" ]; then
    echo "Aucun inventaire de $nom : lance d'abord l'inventaire normal."; return 1
  fi
  echo
  echo ">>> Complément root pour $nom ($al)"
  echo "    Le mot de passe sudo (ou doas sur OpenBSD) va être demandé : tape-le toi-même."
  echo "    Il n'est ni lu ni stocké par ce script."
  {
    echo
    echo "# ===== Complément root ajouté le $(date '+%Y-%m-%d %H:%M:%S') ====="
  } >> "$out"

  if [ "$al" = "local" ]; then
    sudo sh "$PAYLOAD" rootonly >> "$out" 2>&1; rc=$?
  else
    d="$(ssh "${SSH_OPTS[@]}" "$al" 'd=$(mktemp -d) && cat > "$d/p.sh" && echo "$d"' < "$PAYLOAD")" || {
      echo "    ÉCHEC : connexion SSH impossible vers $al"; return 1; }
    # -t : terminal pour que sudo/doas puisse demander le mot de passe
    ssh -t -o ConnectTimeout=8 "$al" \
      "if command -v sudo >/dev/null 2>&1; then S=sudo; else S=doas; fi; \$S sh '$d/p.sh' rootonly > '$d/out' 2>&1"
    rc=$?
    ssh "${SSH_OPTS[@]}" "$al" "cat '$d/out'; rm -rf '$d'" >> "$out" 2>&1
  fi

  lignes=$(sed -n '/Complément root ajouté/,$p' "$out" | wc -l)
  if [ "$lignes" -lt 8 ]; then
    echo "    Le complément semble vide (mot de passe refusé ?). Réessaie : ./zeta_inventaire.sh root $n"
    return 1
  fi
  echo "    OK : $lignes lignes ajoutées à $out"
}

inventaire() {
  local n="$1" nom al ts out rc lignes partiel fuite rep
  nom="${NOMS[$((n-1))]}"; al="${ALIAS[$((n-1))]}"
  ts="$(date +%Y%m%d-%H%M%S)"
  out="$OUT_DIR/inventaire_${nom}_${al}_${ts}.txt"

  echo
  echo ">>> Inventaire $nom ($al) en cours (lecture seule)..."
  {
    echo "# INVENTAIRE $nom ($al) — généré par zeta_inventaire.sh le $(date '+%Y-%m-%d %H:%M:%S')"
    echo "# LECTURE SEULE — secrets masqués — fichier PRIVÉ (ne pas publier)"
  } > "$out"
  chmod 600 "$out"

  if [ "$al" = "local" ]; then
    sh "$PAYLOAD" </dev/null >> "$out" 2>&1; rc=$?
  else
    ssh "${SSH_OPTS[@]}" "$al" \
      'f=$(mktemp) && cat > "$f" && sh "$f" </dev/null; rc=$?; rm -f "$f"; exit $rc' \
      < "$PAYLOAD" >> "$out" 2>&1; rc=$?
  fi

  lignes=$(wc -l < "$out")
  partiel=$(grep -c 'ignoré : droits root requis' "$out")
  fuite=$(grep -cE 'BEGIN [A-Z ]*PRIVATE KEY|[Pp]rivate[Kk]ey *= *[A-Za-z0-9+/=]{20,}' "$out")

  if [ "$rc" -ne 0 ] || [ "$lignes" -lt 20 ]; then
    echo "    ÉCHEC (code $rc, $lignes lignes). Dernières lignes :"
    tail -n 5 "$out" | sed 's/^/      /'
    echo "    Vérifie : ssh $al  (clé SSH, machine allumée ?)"
    rm -f "$out"   # on ne garde pas un fichier d'échec
    return 1
  fi
  INV_FILES+=("$out")
  echo "    Fichier : $out"
  echo "    Lignes : $lignes | commandes ignorées (root requis) : $partiel | secrets détectés : $fuite"
  [ "$fuite" -gt 0 ] && echo "    ATTENTION : secret détecté dans le fichier, NE PAS le partager et préviens-moi."

  if [ "$partiel" -gt 0 ]; then
    rep=""
    read -r -p "    Compléter avec les droits root (mot de passe sudo à taper) ? [o/N] " rep
    case "$rep" in o|O|y|Y) complement_root "$n" ;; esac
  fi
  return 0
}

resume() {
  echo
  echo "=== Résumé de cette session ==="
  if [ "${#INV_FILES[@]}" -eq 0 ]; then echo "Aucun inventaire réussi."; return; fi
  for f in "${INV_FILES[@]}"; do echo "  $f  ($(wc -l < "$f") lignes)"; done
  echo "Dossier : $OUT_DIR  (privé, hors dépôt Git)"
  echo "Étape suivante : zeta_rapport.py (génère les tableaux Markdown à partir de ces fichiers)"
}

ajout_pc() {
  local nom ip usr monip prefixe ok=1 o
  echo
  echo "=== AJOUT D'UN NOUVEAU PC — MODE À BLANC ==="
  echo "Aucune modification, aucun fichier envoyé : seulement des vérifications."
  read -r -p "Nom du nouveau PC (ex. zeta-xxx) : " nom
  [[ "$nom" =~ ^[a-z][a-z0-9-]{1,30}$ ]] || { echo "Nom invalide (minuscules, chiffres, tirets)."; return; }
  read -r -p "IP fixe prévue : " ip
  read -r -p "Utilisateur SSH [hprzeta] : " usr; usr="${usr:-hprzeta}"

  if [[ "$ip" =~ ^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$ ]]; then
    for o in "${BASH_REMATCH[@]:1}"; do [ "$o" -le 255 ] || { echo "IP invalide (octet > 255)."; return; }; done
    echo "  [OK ] format de l'IP"
  else
    echo "  [KO ] format de l'IP invalide"; return
  fi

  monip="$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}' | head -n 1)"
  prefixe="${monip%.*}"
  if [ -n "$prefixe" ] && [ "${ip%.*}" = "$prefixe" ]; then
    echo "  [OK ] même réseau /24 que PC1"
  else
    echo "  [KO ] l'IP n'est pas dans le même /24 que PC1"; ok=0
  fi

  if [ -f "$HOME/.ssh/config" ] && grep -Eq "(^|[^0-9])${ip//./\\.}([^0-9]|$)" "$HOME/.ssh/config"; then
    echo "  [KO ] cette IP est déjà dans ~/.ssh/config"; ok=0
  else
    echo "  [OK ] IP absente de ~/.ssh/config"
  fi
  if [ -f "$HOME/.ssh/config" ] && grep -Eiq "^[[:space:]]*Host[[:space:]].*(^|[[:space:]])${nom}([[:space:]]|$)" "$HOME/.ssh/config"; then
    echo "  [KO ] ce nom est déjà un alias dans ~/.ssh/config"; ok=0
  else
    echo "  [OK ] nom absent de ~/.ssh/config"
  fi

  if ping -c1 -W1 "$ip" >/dev/null 2>&1; then
    echo "  [INFO] l'IP répond au ping (machine déjà branchée, ou adresse DÉJÀ UTILISÉE)"
    if timeout 3 bash -c "exec 3<>/dev/tcp/$ip/22" 2>/dev/null; then
      echo "  [INFO] port SSH 22 ouvert"
      if ssh -o BatchMode=yes -o ConnectTimeout=5 "$usr@$ip" true 2>/dev/null; then
        echo "  [OK ] connexion SSH par clé fonctionne déjà pour $usr"
      else
        echo "  [INFO] connexion SSH par clé pas encore active (normal pour un PC neuf)"
      fi
    else
      echo "  [INFO] port SSH 22 fermé (SSH serveur à installer)"
    fi
  else
    echo "  [OK ] l'IP ne répond pas (libre, ou PC encore éteint)"
  fi

  [ "$ok" -eq 1 ] && echo "=> Pré-vérifications OK" || echo "=> Pré-vérifications avec problème : corrige avant de continuer"
  cat <<EOT

Étapes prévues pour $nom ($ip) — NON EXÉCUTÉES ici :
  1. Réserver l'IP dans la box SFR (bail statique) + l'ajouter au plan d'adressage
  2. Installer le serveur SSH et créer/vérifier l'utilisateur $usr
  3. Copier la clé publique de PC1 (ssh-copy-id), puis désactiver le mot de passe SSH
  4. Configurer l'IP fixe filaire (sauvegarde du fichier réseau avant modification)
  5. Ajouter l'alias $nom dans ~/.ssh/config de PC1
  6. Déployer les scripts du cluster et les tâches cron
  7. Lancer l'inventaire du nouveau PC et l'ajouter au document d'architecture

La procédure détaillée et l'application automatisée seront ajoutées
après validation du plan d'adressage.
EOT
}

menu() {
  local c i p
  while true; do
    echo
    echo "================ INVENTAIRE CLUSTER ZETA (lecture seule) ================"
    echo "  1) Inventaire PC1  (zeta-lab, cette machine)"
    echo "  2) Inventaire PC2  (zeta-calc-second)"
    echo "  3) Inventaire PC3  (zeta-backup)"
    echo "  4) Inventaire PC4  (zeta-secure, OpenBSD)"
    echo "  5) Inventaire PC5  (zeta-monitor)"
    echo "  6) Inventaire des 5 PC, l'un après l'autre"
    echo "  7) Compléter un inventaire avec les droits root (mot de passe sudo à taper)"
    echo "  8) Ajout d'un nouveau PC (MODE À BLANC : vérifications seulement)"
    echo "  0) Quitter"
    read -r -p "Choix : " c
    case "$c" in
      1|2|3|4|5) inventaire "$c" ;;
      6) for i in 1 2 3 4 5; do inventaire "$i"; done; resume ;;
      7) read -r -p "Quel PC (1-5) ? " p
         case "$p" in 1|2|3|4|5) complement_root "$p" ;; *) echo "PC invalide." ;; esac ;;
      8) ajout_pc ;;
      0) resume; exit 0 ;;
      *) echo "Choix invalide." ;;
    esac
  done
}

[ "$(hostname)" = "zeta-lab" ] || echo "Attention : ce script est prévu pour PC1 (zeta-lab) ; « local » = cette machine ($(hostname))."

case "${1:-}" in
  1|2|3|4|5) inventaire "$1"; resume ;;
  tous)      for i in 1 2 3 4 5; do inventaire "$i"; done; resume ;;
  root)      case "${2:-}" in 1|2|3|4|5) complement_root "$2" ;; *) echo "Usage : $0 root [1-5]"; exit 1 ;; esac ;;
  ajout)     ajout_pc ;;
  "")        menu ;;
  *)         echo "Usage : $0 [1|2|3|4|5|tous|root N|ajout]"; exit 1 ;;
esac
