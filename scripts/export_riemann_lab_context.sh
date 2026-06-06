#!/usr/bin/env bash
set -Eeuo pipefail

# ==============================================================================
# export_riemann_lab_context.sh
# Objectif : récupérer le dépôt hprzeta/Riemann_Lab + son wiki, extraire les
# Markdown, docs, skills, scripts, configs, requirements, inventaires et logs Git,
# puis produire une archive à transmettre pour reconfiguration hprzeta.
#
# Usage :
#   chmod +x export_riemann_lab_context.sh
#   ./export_riemann_lab_context.sh
#
# Options :
#   BASE_DIR=/chemin ./export_riemann_lab_context.sh
#   REPO_URL=https://... WIKI_URL=https://... ./export_riemann_lab_context.sh
# ============================================================================== 

BASE_DIR="${BASE_DIR:-$HOME/hprzeta-import}"
REPO_URL="${REPO_URL:-https://github.com/hprzeta/Riemann_Lab.git}"
WIKI_URL="${WIKI_URL:-https://github.com/hprzeta/Riemann_Lab.wiki.git}"
TS="$(date +%F_%H-%M-%S)"
REPO_DIR="$BASE_DIR/Riemann_Lab"
WIKI_DIR="$BASE_DIR/Riemann_Lab.wiki"
OUT_DIR="$BASE_DIR/riemann_lab_context_export_$TS"
LATEST_LINK="$BASE_DIR/riemann_lab_context_export_latest"
LOG_FILE="$BASE_DIR/export_riemann_lab_context_$TS.log"

mkdir -p "$BASE_DIR"

log() { echo "[$(date +%F' '%T)] $*" | tee -a "$LOG_FILE"; }
run() { log "+ $*"; "$@" 2>&1 | tee -a "$LOG_FILE"; }

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log "Commande manquante: $1"
    return 1
  fi
}

install_hint() {
  cat <<'EOF'

Une commande nécessaire est absente. Sur Ubuntu, installe au minimum :
  sudo apt update
  sudo apt install -y git tar gzip findutils coreutils zip

Puis relance :
  ./export_riemann_lab_context.sh
EOF
}

trap 'log "ERREUR ligne $LINENO. Consulte le log : $LOG_FILE"' ERR

log "Début export Riemann_Lab contexte"
log "BASE_DIR=$BASE_DIR"
log "REPO_URL=$REPO_URL"
log "WIKI_URL=$WIKI_URL"

for c in git tar gzip find sort cp mkdir date sha256sum; do
  need_cmd "$c" || { install_hint; exit 1; }
done

# 1) Cloner ou mettre à jour le dépôt principal
if [ ! -d "$REPO_DIR/.git" ]; then
  log "Clonage dépôt principal..."
  run git clone "$REPO_URL" "$REPO_DIR"
else
  log "Dépôt principal déjà présent : mise à jour..."
  cd "$REPO_DIR"
  run git remote -v
  run git fetch --all --prune
  # On évite de casser un dépôt local modifié : pull seulement si possible.
  if git diff --quiet && git diff --cached --quiet; then
    run git pull --ff-only || log "Pull principal impossible, export avec état local existant."
  else
    log "Dépôt principal avec modifications locales : pas de pull automatique destructif."
  fi
fi

# 2) Cloner ou mettre à jour le wiki
if [ ! -d "$WIKI_DIR/.git" ]; then
  log "Clonage wiki..."
  if git clone "$WIKI_URL" "$WIKI_DIR" 2>&1 | tee -a "$LOG_FILE"; then
    log "Wiki cloné."
  else
    log "Wiki non cloné. Vérifie accès, URL, droits ou existence du wiki."
  fi
else
  log "Wiki déjà présent : mise à jour..."
  cd "$WIKI_DIR"
  run git fetch --all --prune || true
  if git diff --quiet && git diff --cached --quiet; then
    run git pull --ff-only || log "Pull wiki impossible, export avec état local existant."
  else
    log "Wiki avec modifications locales : pas de pull automatique destructif."
  fi
fi

# 3) Créer sortie
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"/{repo_markdown,repo_selected,wiki,git_info,inventories,manifests,skills,docs_flat,checksums}

# 4) Copier Markdown du dépôt principal avec chemins conservés
log "Extraction fichiers Markdown du dépôt principal..."
cd "$REPO_DIR"
find . -type f -name "*.md" -not -path "./.git/*" -print0 \
  | while IFS= read -r -d '' f; do
      mkdir -p "$OUT_DIR/repo_markdown/$(dirname "$f")"
      cp -a "$f" "$OUT_DIR/repo_markdown/$f"
    done

# 5) Copier éléments importants du dépôt principal
log "Copie éléments sélectionnés du dépôt..."
for item in README.md CONTRIBUTING.md CLAUDE.md LICENSE .gitignore docs config scripts requirements .claude src images notebooks lean_projects; do
  if [ -e "$REPO_DIR/$item" ]; then
    cp -a "$REPO_DIR/$item" "$OUT_DIR/repo_selected/" || true
  fi
done

# 6) Extraction spécifique des skills et fichiers agent si présents
log "Extraction skills/agents..."
if [ -d "$REPO_DIR/.claude" ]; then
  cp -a "$REPO_DIR/.claude" "$OUT_DIR/skills/claude" || true
fi
if [ -d "$REPO_DIR/.agents" ]; then
  cp -a "$REPO_DIR/.agents" "$OUT_DIR/skills/agents" || true
fi
find "$REPO_DIR" \( -iname "*skill*" -o -iname "*prompt*" -o -iname "*agent*" \) \
  -not -path "*/.git/*" -print > "$OUT_DIR/inventories/skills_prompts_agents_paths.txt" || true

# 7) Copier wiki complet si présent
if [ -d "$WIKI_DIR" ]; then
  log "Copie du wiki..."
  rsync -a --exclude='.git' "$WIKI_DIR/" "$OUT_DIR/wiki/" 2>/dev/null || cp -a "$WIKI_DIR"/* "$OUT_DIR/wiki/" 2>/dev/null || true
fi

# 8) Inventaires dépôt et wiki
log "Création inventaires..."
cd "$REPO_DIR"
git rev-parse HEAD > "$OUT_DIR/git_info/repo_commit.txt" || true
git branch --show-current > "$OUT_DIR/git_info/repo_branch.txt" || true
git remote -v > "$OUT_DIR/git_info/repo_remotes.txt" || true
git log --oneline --decorate -50 > "$OUT_DIR/git_info/repo_git_log_last_50.txt" || true
git status --short > "$OUT_DIR/git_info/repo_status_short.txt" || true
find . -not -path "./.git/*" -type f | sort > "$OUT_DIR/inventories/repo_file_inventory.txt" || true
find . -not -path "./.git/*" -type f -name "*.md" | sort > "$OUT_DIR/inventories/repo_markdown_inventory.txt" || true

if [ -d "$WIKI_DIR/.git" ]; then
  cd "$WIKI_DIR"
  git rev-parse HEAD > "$OUT_DIR/git_info/wiki_commit.txt" || true
  git branch --show-current > "$OUT_DIR/git_info/wiki_branch.txt" || true
  git remote -v > "$OUT_DIR/git_info/wiki_remotes.txt" || true
  git log --oneline --decorate -50 > "$OUT_DIR/git_info/wiki_git_log_last_50.txt" || true
  git status --short > "$OUT_DIR/git_info/wiki_status_short.txt" || true
  find . -not -path "./.git/*" -type f | sort > "$OUT_DIR/inventories/wiki_file_inventory.txt" || true
  find . -not -path "./.git/*" -type f -name "*.md" | sort > "$OUT_DIR/inventories/wiki_markdown_inventory.txt" || true
fi

# 9) Manifest local
log "Création manifest..."
{
  echo "# Export Riemann_Lab context"
  echo
  echo "Date export: $(date -Iseconds)"
  echo "Base dir: $BASE_DIR"
  echo "Repo URL: $REPO_URL"
  echo "Wiki URL: $WIKI_URL"
  echo
  echo "## Machine"
  uname -a || true
  echo
  echo "## Distribution"
  if [ -f /etc/os-release ]; then cat /etc/os-release; fi
  echo
  echo "## Git"
  git --version || true
  echo
  echo "## Python"
  python3 --version || true
  echo
  echo "## Notes"
  echo "Archive prévue pour transmission à l'assistant afin de préparer la base de reconfiguration hprzeta."
  echo "Ne contient pas volontairement le dossier .git complet. Contient commits/logs/inventaires utiles."
} > "$OUT_DIR/manifests/export_manifest.md"

# 10) Checklist de reprise conversationnelle
cat > "$OUT_DIR/manifests/prompt_reprise_hprzeta.md" <<'EOF'
# Prompt de rappel — reprise hprzeta / Riemann_Lab

Tu es l’assistant du projet hprzeta. Nous reprenons une conversation précédente sur la reconfiguration du dépôt GitHub `hprzeta/Riemann_Lab`.

## Contexte déjà établi
- Projet : exploration numérique/symbolique de ζ(s), hypothèse de Riemann, IA locale, visualisation, Lean 4.
- Machine cible principale : PC ASUS Linux Ubuntu 24.04 LTS, Intel i7, 8 Go RAM, 16 Go swap, disque 1 To, NVIDIA GTX 960/960M 4 Go VRAM.
- Dépôt principal : https://github.com/hprzeta/Riemann_Lab
- Wiki : https://github.com/hprzeta/Riemann_Lab.wiki.git
- Objectif : migrer/reconfigurer le projet vers une architecture plus robuste : `hprzeta-lab`, recovery, brain vault, RAG, sauvegardes et reprise catastrophe.

## Documents PDF déjà produits dans la conversation
- `solution_experimental_zeta.pdf`
- `solution_experimental_zeta_pc_asus.pdf`
- `recovery_zeta.pdf`
- `cerveau_autonome_zeta_23_points.pdf`

## Principes décidés
1. Utiliser des modèles locaux légers : `qwen2.5-coder:1.5b`, `qwen2.5-coder:3b`, `llama3.2:3b`.
2. OpenHands seulement ponctuellement ; Aider + Ollama prioritaire sur le PC local.
3. Mettre en place `hprzeta-recovery-agent` pour checkpoints, crash reports, error_memory et reprise.
4. Ajouter `hprzeta-knowledge-steward-agent` pour Obsidian/Markdown, formules, lemmes, erreurs, succès et guide de formation.
5. Ajouter `hprzeta-disaster-recovery-agent` pour restauration sur machine vierge ou secours.
6. Utiliser Git, Restic, Syncthing, éventuellement Raspberry Pi/VPS/MinIO/Healthchecks pour réplication et reprise catastrophe.

## Ce que contient l’archive transmise
- Markdown du dépôt principal.
- Markdown du wiki.
- Dossiers sélectionnés : docs, scripts, config, requirements, .claude, src, notebooks, images si présents.
- Inventaires de fichiers.
- Logs Git récents.
- Manifest d’export.

## Travail demandé maintenant
1. Lire l’archive.
2. Cartographier l’existant.
3. Identifier les doublons, dépendances et scripts déjà présents.
4. Proposer une migration douce vers `~/hprzeta-lab/` sans casser le dépôt actuel.
5. Produire :
   - plan de reconfiguration,
   - structure cible,
   - scripts bootstrap Ubuntu 24.04,
   - README_RESTORE.md,
   - RESTORE_CHECKLIST.md,
   - architecture Obsidian Brain Vault,
   - intégration Recovery Zeta,
   - plan RAG initial.

Important : ne jamais prétendre prouver l’hypothèse de Riemann. Distinguer expérimentation numérique, conjecture, preuve formelle et documentation.
EOF

# 11) Checksums internes
log "Création checksums..."
cd "$OUT_DIR"
find . -type f -not -path "./checksums/*" -print0 | sort -z | xargs -0 sha256sum > "$OUT_DIR/checksums/SHA256SUMS.txt" || true

# 12) Archives finales
cd "$BASE_DIR"
TAR_FILE="$BASE_DIR/riemann_lab_context_export_$TS.tar.gz"
LATEST_TAR="$BASE_DIR/riemann_lab_context_export_latest.tar.gz"
log "Création archive tar.gz..."
tar -czf "$TAR_FILE" "$(basename "$OUT_DIR")"
cp -f "$TAR_FILE" "$LATEST_TAR"
sha256sum "$TAR_FILE" > "$TAR_FILE.sha256"
sha256sum "$LATEST_TAR" > "$LATEST_TAR.sha256"

# Symlink latest si possible
rm -f "$LATEST_LINK"
ln -s "$OUT_DIR" "$LATEST_LINK" 2>/dev/null || true

# Zip optionnel
if command -v zip >/dev/null 2>&1; then
  ZIP_FILE="$BASE_DIR/riemann_lab_context_export_$TS.zip"
  LATEST_ZIP="$BASE_DIR/riemann_lab_context_export_latest.zip"
  log "Création archive zip..."
  zip -qr "$ZIP_FILE" "$(basename "$OUT_DIR")"
  cp -f "$ZIP_FILE" "$LATEST_ZIP"
  sha256sum "$ZIP_FILE" > "$ZIP_FILE.sha256"
  sha256sum "$LATEST_ZIP" > "$LATEST_ZIP.sha256"
fi

log "Export terminé."
echo
echo "============================================================"
echo "Archive principale à m'envoyer :"
echo "  $LATEST_TAR"
echo
echo "Archive datée :"
echo "  $TAR_FILE"
echo
echo "Prompt de reprise inclus dans :"
echo "  $OUT_DIR/manifests/prompt_reprise_hprzeta.md"
echo
echo "Log :"
echo "  $LOG_FILE"
echo "============================================================"
