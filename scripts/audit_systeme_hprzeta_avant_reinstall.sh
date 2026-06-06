#!/usr/bin/env bash
set -Eeuo pipefail

# ==============================================================================
# audit_systeme_hprzeta_avant_reinstall.sh
# Objectif : analyser l'ancien système Linux avant réinstallation, inventorier
# paquets, matériel, partitions, GPU, swap, variables utiles, bashrc, services,
# projets locaux, dépôts Git, fichiers Markdown, requirements, scripts et configs.
# Produit une archive .tar.gz à transmettre pour préparer une réinstallation propre.
#
# Usage :
#   chmod +x audit_systeme_hprzeta_avant_reinstall.sh
#   ./audit_systeme_hprzeta_avant_reinstall.sh
#
# Options :
#   OUT_BASE=/chemin ./audit_systeme_hprzeta_avant_reinstall.sh
#   EXTRA_SCAN_DIRS="/mnt/data /home/riemann/projet_zeta" ./audit_systeme_hprzeta_avant_reinstall.sh
# ============================================================================== 

OUT_BASE="${OUT_BASE:-$HOME/hprzeta-system-audit}"
TS="$(date +%F_%H-%M-%S)"
OUT_DIR="$OUT_BASE/audit_$TS"
LATEST_TAR="$OUT_BASE/hprzeta_system_audit_latest.tar.gz"
LOG_FILE="$OUT_BASE/audit_$TS.log"
EXTRA_SCAN_DIRS="${EXTRA_SCAN_DIRS:-/mnt/data $HOME/projet_zeta $HOME/hprzeta-lab $HOME/hprzeta-import}"

mkdir -p "$OUT_DIR"/{system,hardware,packages,python,git,projects,configs,services,logs,security_notes,manifests,checksums}
mkdir -p "$OUT_BASE"

log() { echo "[$(date +%F' '%T)] $*" | tee -a "$LOG_FILE"; }
run_capture() {
  local outfile="$1"; shift
  log "+ $* > $outfile"
  ( "$@" ) > "$outfile" 2>&1 || true
}

redact_file() {
  local src="$1"
  local dst="$2"
  if [ -f "$src" ]; then
    sed -E \
      -e 's/(TOKEN|Token|token)=.*/\1=__REDACTED__/g' \
      -e 's/(SECRET|Secret|secret)=.*/\1=__REDACTED__/g' \
      -e 's/(PASSWORD|Password|password)=.*/\1=__REDACTED__/g' \
      -e 's/(API_KEY|api_key|apikey|ApiKey)=.*/\1=__REDACTED__/g' \
      -e 's/(GITHUB_TOKEN|GH_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY|HF_TOKEN)=.*/\1=__REDACTED__/g' \
      "$src" > "$dst" || true
  fi
}

log "Début audit système hprzeta avant réinstallation"
log "OUT_DIR=$OUT_DIR"
log "EXTRA_SCAN_DIRS=$EXTRA_SCAN_DIRS"

# ------------------------------------------------------------------------------
# 1) Identité système et OS
# ------------------------------------------------------------------------------
run_capture "$OUT_DIR/system/uname.txt" uname -a
run_capture "$OUT_DIR/system/hostname.txt" hostnamectl
run_capture "$OUT_DIR/system/os_release.txt" bash -lc 'cat /etc/os-release'
run_capture "$OUT_DIR/system/locale.txt" locale
run_capture "$OUT_DIR/system/date_timedatectl.txt" timedatectl
run_capture "$OUT_DIR/system/users_groups.txt" bash -lc 'id; groups; whoami'

# ------------------------------------------------------------------------------
# 2) Matériel, disque, partitions, swap
# ------------------------------------------------------------------------------
run_capture "$OUT_DIR/hardware/cpu_lscpu.txt" lscpu
run_capture "$OUT_DIR/hardware/memory_free.txt" free -h
run_capture "$OUT_DIR/hardware/swapon.txt" swapon --show
run_capture "$OUT_DIR/hardware/df_h.txt" df -hT
run_capture "$OUT_DIR/hardware/lsblk.txt" lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,UUID,MODEL
run_capture "$OUT_DIR/hardware/blkid.txt" bash -lc 'blkid 2>/dev/null || true'
run_capture "$OUT_DIR/hardware/mounts.txt" mount
run_capture "$OUT_DIR/hardware/fstab_sanitized.txt" bash -lc 'cat /etc/fstab 2>/dev/null || true'
run_capture "$OUT_DIR/hardware/pci.txt" lspci
run_capture "$OUT_DIR/hardware/usb.txt" lsusb
run_capture "$OUT_DIR/hardware/kernel_modules_nvidia.txt" bash -lc 'lsmod | grep -Ei "nvidia|nouveau|cuda" || true'
run_capture "$OUT_DIR/hardware/nvidia_smi.txt" bash -lc 'nvidia-smi 2>/dev/null || true'
run_capture "$OUT_DIR/hardware/nvidia_settings.txt" bash -lc 'nvidia-settings -q all 2>/dev/null | head -200 || true'
run_capture "$OUT_DIR/hardware/ubuntu_drivers_devices.txt" bash -lc 'ubuntu-drivers devices 2>/dev/null || true'
run_capture "$OUT_DIR/hardware/glxinfo_gpu.txt" bash -lc 'glxinfo -B 2>/dev/null || true'

# ------------------------------------------------------------------------------
# 3) Paquets APT, snaps, flatpak, dépôts
# ------------------------------------------------------------------------------
run_capture "$OUT_DIR/packages/dpkg_get_selections.txt" dpkg --get-selections
run_capture "$OUT_DIR/packages/apt_installed.txt" bash -lc 'apt list --installed 2>/dev/null || true'
run_capture "$OUT_DIR/packages/apt_manual.txt" bash -lc 'apt-mark showmanual 2>/dev/null || true'
run_capture "$OUT_DIR/packages/apt_sources_main.txt" bash -lc 'cat /etc/apt/sources.list 2>/dev/null || true'
mkdir -p "$OUT_DIR/packages/sources.list.d"
cp -a /etc/apt/sources.list.d/* "$OUT_DIR/packages/sources.list.d/" 2>/dev/null || true
run_capture "$OUT_DIR/packages/snap_list.txt" bash -lc 'snap list 2>/dev/null || true'
run_capture "$OUT_DIR/packages/flatpak_list.txt" bash -lc 'flatpak list 2>/dev/null || true'

# ------------------------------------------------------------------------------
# 4) Python, pip, venvs, conda éventuel
# ------------------------------------------------------------------------------
run_capture "$OUT_DIR/python/python_versions.txt" bash -lc 'which python python3 pip pip3 2>/dev/null; python3 --version 2>/dev/null; pip3 --version 2>/dev/null'
run_capture "$OUT_DIR/python/global_pip_freeze.txt" bash -lc 'python3 -m pip freeze 2>/dev/null || true'
run_capture "$OUT_DIR/python/venv_inventory.txt" bash -lc "find '$HOME' /mnt/data -maxdepth 5 -type f -path '*/bin/activate' 2>/dev/null | sort || true"

# pip freeze dans venvs trouvés, limité pour éviter lenteur
VENV_LIST="$OUT_DIR/python/venv_inventory.txt"
mkdir -p "$OUT_DIR/python/venv_freeze"
if [ -s "$VENV_LIST" ]; then
  head -50 "$VENV_LIST" | while read -r activate_file; do
    venv_dir="$(dirname "$(dirname "$activate_file")")"
    safe_name="$(echo "$venv_dir" | sed 's#/#__#g')"
    if [ -x "$venv_dir/bin/python" ]; then
      "$venv_dir/bin/python" -m pip freeze > "$OUT_DIR/python/venv_freeze/${safe_name}.txt" 2>&1 || true
    fi
  done
fi

# ------------------------------------------------------------------------------
# 5) Git, dépôts locaux, projets
# ------------------------------------------------------------------------------
run_capture "$OUT_DIR/git/git_version.txt" git --version
run_capture "$OUT_DIR/git/git_global_config_sanitized.txt" bash -lc 'git config --global --list 2>/dev/null | sed -E "s/(token|password|secret|key)=.*/\1=__REDACTED__/Ig" || true'
run_capture "$OUT_DIR/git/local_git_repos.txt" bash -lc "find '$HOME' /mnt/data -maxdepth 5 -type d -name .git 2>/dev/null | sed 's#/.git$##' | sort || true"

mkdir -p "$OUT_DIR/git/repo_status"
if [ -s "$OUT_DIR/git/local_git_repos.txt" ]; then
  head -100 "$OUT_DIR/git/local_git_repos.txt" | while read -r repo; do
    safe="$(echo "$repo" | sed 's#/#__#g')"
    {
      echo "# Repo: $repo"
      cd "$repo" || exit 0
      echo "## Remote"
      git remote -v || true
      echo "## Branch"
      git branch --show-current || true
      echo "## Commit"
      git rev-parse HEAD || true
      echo "## Status"
      git status --short || true
      echo "## Log"
      git log --oneline --decorate -20 || true
    } > "$OUT_DIR/git/repo_status/${safe}.txt" 2>&1 || true
  done
fi

# ------------------------------------------------------------------------------
# 6) Inventaire projets et fichiers utiles
# ------------------------------------------------------------------------------
run_capture "$OUT_DIR/projects/project_dirs_candidate.txt" bash -lc "find '$HOME' /mnt/data -maxdepth 4 \( -name 'pyproject.toml' -o -name 'requirements*.txt' -o -name 'environment.yml' -o -name 'README.md' -o -name 'CLAUDE.md' -o -name '*.ipynb' \) 2>/dev/null | sort || true"
run_capture "$OUT_DIR/projects/markdown_inventory.txt" bash -lc "find '$HOME' /mnt/data -maxdepth 6 -type f -name '*.md' 2>/dev/null | sort || true"
run_capture "$OUT_DIR/projects/requirements_inventory.txt" bash -lc "find '$HOME' /mnt/data -maxdepth 6 -type f \( -name 'requirements*.txt' -o -name 'pyproject.toml' -o -name 'environment.yml' -o -name 'Pipfile' -o -name 'poetry.lock' \) 2>/dev/null | sort || true"
run_capture "$OUT_DIR/projects/scripts_inventory.txt" bash -lc "find '$HOME' /mnt/data -maxdepth 6 -type f \( -name '*.sh' -o -name '*.py' \) 2>/dev/null | sort || true"

# Copier projets hprzeta/projet_zeta/Riemann_Lab de façon non destructive, sans gros caches
mkdir -p "$OUT_DIR/projects/selected_snapshots"
for d in $EXTRA_SCAN_DIRS; do
  if [ -e "$d" ]; then
    name="$(basename "$d")"
    log "Snapshot léger de $d"
    tar \
      --exclude='.git' \
      --exclude='__pycache__' \
      --exclude='.venv' \
      --exclude='zeta_env' \
      --exclude='node_modules' \
      --exclude='.ipynb_checkpoints' \
      --exclude='*.gguf' \
      --exclude='*.bin' \
      --exclude='*.safetensors' \
      --exclude='*.pt' \
      --exclude='*.pth' \
      --exclude='*.onnx' \
      --exclude='*.mp4' \
      --exclude='*.zip' \
      --exclude='*.tar' \
      --exclude='*.tar.gz' \
      -czf "$OUT_DIR/projects/selected_snapshots/${name}_snapshot_light.tar.gz" -C "$(dirname "$d")" "$(basename "$d")" 2>>"$LOG_FILE" || true
  fi
done

# ------------------------------------------------------------------------------
# 7) Configs utilisateur : bashrc, aliases, profile, cron, systemd
# ------------------------------------------------------------------------------
redact_file "$HOME/.bashrc" "$OUT_DIR/configs/bashrc_sanitized.txt"
redact_file "$HOME/.profile" "$OUT_DIR/configs/profile_sanitized.txt"
redact_file "$HOME/.bash_aliases" "$OUT_DIR/configs/bash_aliases_sanitized.txt"
redact_file "$HOME/.zshrc" "$OUT_DIR/configs/zshrc_sanitized.txt"
run_capture "$OUT_DIR/configs/env_sanitized.txt" bash -lc 'env | sort | sed -E "s/(TOKEN|SECRET|PASSWORD|API_KEY|KEY)=.*/\1=__REDACTED__/Ig"'
run_capture "$OUT_DIR/configs/crontab_user.txt" bash -lc 'crontab -l 2>/dev/null || true'
run_capture "$OUT_DIR/services/systemctl_user_units.txt" bash -lc 'systemctl --user list-unit-files 2>/dev/null || true'
run_capture "$OUT_DIR/services/systemctl_system_units_hprzeta.txt" bash -lc 'systemctl list-unit-files 2>/dev/null | grep -Ei "zeta|ollama|jupyter|docker|syncthing|restic|backup" || true'
run_capture "$OUT_DIR/services/systemctl_running_filtered.txt" bash -lc 'systemctl --type=service --state=running 2>/dev/null | grep -Ei "zeta|ollama|jupyter|docker|syncthing|restic|backup|nvidia" || true'

# Ollama si présent
run_capture "$OUT_DIR/configs/ollama_list.txt" bash -lc 'ollama list 2>/dev/null || true'
run_capture "$OUT_DIR/configs/ollama_service.txt" bash -lc 'systemctl status ollama --no-pager 2>/dev/null || true'

# ------------------------------------------------------------------------------
# 8) Notes sécurité : fichiers sensibles NON copiés
# ------------------------------------------------------------------------------
cat > "$OUT_DIR/security_notes/README_SECURITE.md" <<'EOF'
# Sécurité de cet export

Ce script évite volontairement de copier :
- clés privées SSH,
- fichiers `.env`,
- tokens bruts connus,
- modèles IA volumineux,
- caches et environnements virtuels.

Vérifie quand même l'archive avant partage :

```bash
tar -tzf hprzeta_system_audit_latest.tar.gz | less
```

Et cherche les mots sensibles :

```bash
tar -xzf hprzeta_system_audit_latest.tar.gz -C /tmp/hprzeta_audit_check
grep -RniE 'token|secret|password|api_key|private key' /tmp/hprzeta_audit_check || true
```
EOF

# ------------------------------------------------------------------------------
# 9) Prompt de reprise / analyse
# ------------------------------------------------------------------------------
cat > "$OUT_DIR/manifests/prompt_analyse_systeme_hprzeta.md" <<'EOF'
# Prompt — Analyse ancien système hprzeta avant réinstallation

Tu es l’assistant de reconfiguration du projet hprzeta/Riemann_Lab.

Je fournis une archive d’audit système créée avant réinstallation complète de Linux. Elle contient :
- inventaire OS, partitions, disque, RAM, swap, GPU NVIDIA,
- paquets APT, snaps, flatpaks,
- configs bash/profile/aliases nettoyées,
- services systemd filtrés,
- inventaire Python, pip et venvs,
- inventaire projets locaux, dépôts Git, Markdown, requirements, scripts,
- snapshots légers de dossiers projet,
- informations Ollama si disponibles.

Objectif :
1. Comprendre mon ancienne méthode de travail.
2. Identifier ce qui doit être reproduit, corrigé ou abandonné.
3. Proposer une installation propre Ubuntu 24.04 LTS.
4. Proposer un partitionnement adapté à 1 To, 8 Go RAM, 16 Go swap, GTX 960/960M 4 Go VRAM.
5. Générer une checklist manuelle post-install.
6. Générer un script bootstrap propre pour hprzeta-lab.
7. Intégrer : Riemann_Lab, wiki, recovery_zeta, brain vault, RAG, backups.
8. Éviter les modèles trop lourds et dépendances inutiles.

Contraintes :
- Ne jamais prétendre prouver l’hypothèse de Riemann.
- Distinguer calcul expérimental, preuve formelle, documentation et conjecture.
- Ne pas proposer de commandes destructrices sans sauvegarde.
- Priorité : stabilité, reproductibilité, récupération, faible consommation RAM/VRAM.
EOF

# ------------------------------------------------------------------------------
# 10) Manifest final et checksums
# ------------------------------------------------------------------------------
cat > "$OUT_DIR/manifests/audit_manifest.md" <<EOF
# Audit système hprzeta avant réinstallation

Date : $(date -Iseconds)
Utilisateur : $(whoami)
Home : $HOME
Machine : $(hostname)
Sortie : $OUT_DIR

Archive prévue : $LATEST_TAR

## À transmettre
Le fichier à envoyer est :

\`$LATEST_TAR\`

ou sa version datée dans :

\`$OUT_BASE\`
EOF

log "Création checksums internes"
cd "$OUT_DIR"
find . -type f -not -path './checksums/*' -print0 | sort -z | xargs -0 sha256sum > "$OUT_DIR/checksums/SHA256SUMS.txt" || true

# ------------------------------------------------------------------------------
# 11) Archive finale
# ------------------------------------------------------------------------------
cd "$OUT_BASE"
TAR_FILE="$OUT_BASE/hprzeta_system_audit_$TS.tar.gz"
log "Création archive $TAR_FILE"
tar -czf "$TAR_FILE" "$(basename "$OUT_DIR")"
cp -f "$TAR_FILE" "$LATEST_TAR"
sha256sum "$TAR_FILE" > "$TAR_FILE.sha256"
sha256sum "$LATEST_TAR" > "$LATEST_TAR.sha256"

if command -v zip >/dev/null 2>&1; then
  ZIP_FILE="$OUT_BASE/hprzeta_system_audit_$TS.zip"
  LATEST_ZIP="$OUT_BASE/hprzeta_system_audit_latest.zip"
  log "Création zip $ZIP_FILE"
  zip -qr "$ZIP_FILE" "$(basename "$OUT_DIR")"
  cp -f "$ZIP_FILE" "$LATEST_ZIP"
  sha256sum "$ZIP_FILE" > "$ZIP_FILE.sha256"
  sha256sum "$LATEST_ZIP" > "$LATEST_ZIP.sha256"
fi

log "Audit terminé"
echo
echo "============================================================"
echo "Archive à m'envoyer :"
echo "  $LATEST_TAR"
echo
echo "Archive datée :"
echo "  $TAR_FILE"
echo
echo "Prompt d'analyse inclus :"
echo "  $OUT_DIR/manifests/prompt_analyse_systeme_hprzeta.md"
echo
echo "Log :"
echo "  $LOG_FILE"
echo "============================================================"
