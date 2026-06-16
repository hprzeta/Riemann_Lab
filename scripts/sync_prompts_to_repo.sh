#!/bin/bash
# sync_prompts_to_repo.sh
# Copie les prompts depuis ~/Téléchargements vers src/ia/prompts/ et commit
# Auteur : hprzeta — MAJ 2026-06-16
# Usage : bash sync_prompts_to_repo.sh

set -e

REPO="$HOME/projet_zeta"
PROMPTS_DIR="$REPO/src/ia/prompts"
DOWNLOADS="$HOME/Téléchargements"
BRANCH="Riemann_Lab_IA"

echo "=== Sync prompts → src/ia/prompts/ ==="

# 1. Aller sur la bonne branche
cd "$REPO"
git checkout "$BRANCH"
echo "✓ Branche : $BRANCH"

# 2. Créer le dossier si besoin
mkdir -p "$PROMPTS_DIR"

# 3. Liste des prompts à copier (depuis ~/Téléchargements)
PROMPTS=(
  "PROMPT_CLAUDE_CODE_cluster_zeta_20260616.md"
  "PROMPT_CLAUDE_CODE_cluster2_zeta_20260616.md"
  "prompt_claude_code_20260615_suite.md"
  "prompt_doc_v12.md"
  "prompt_post_v9_turbo_12taches.md"
  "prompt_v9_brent_ameliorations.md"
  "prompt_v4_1_findroot_20260531.md"
  "Prompts-Claude-Code.md"
)

COPIED=0
for f in "${PROMPTS[@]}"; do
  SRC="$DOWNLOADS/$f"
  DST="$PROMPTS_DIR/$f"
  if [ -f "$SRC" ]; then
    cp "$SRC" "$DST"
    echo "  ✓ Copié : $f"
    ((COPIED++))
  else
    echo "  ⚠ Absent : $f (skip)"
  fi
done

echo ""
echo "=== $COPIED fichier(s) copiés ==="

# 4. Vérifier git status
echo ""
git status "$PROMPTS_DIR"

# 5. Commit si des fichiers ont changé
CHANGED=$(git diff --name-only "$PROMPTS_DIR" 2>/dev/null; git ls-files --others --exclude-standard "$PROMPTS_DIR" 2>/dev/null)

if [ -z "$CHANGED" ]; then
  echo "Rien à committer — prompts déjà à jour."
else
  echo ""
  echo "Fichiers modifiés/nouveaux :"
  echo "$CHANGED"
  echo ""
  git add "$PROMPTS_DIR"
  git commit -m "docs(prompts): sync prompts Claude Code sessions mai-juin 2026 → src/ia/prompts/"
  git push origin "$BRANCH"
  echo "✓ Push OK sur $BRANCH"
fi

echo ""
echo "=== Terminé ==="
echo "Prompts disponibles dans : $PROMPTS_DIR"
ls -la "$PROMPTS_DIR"
