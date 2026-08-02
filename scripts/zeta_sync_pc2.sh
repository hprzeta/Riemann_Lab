#!/bin/bash
# zeta_sync_pc2.sh — Synchronise PC2 (zeta-calc-second) et recompile les .so
# Usage : scripts/zeta_sync_pc2.sh
#
# PC2 n'est PAS un dépôt git (pas de .git, git absent du PATH) : le code y est
# synchronisé par rsync/scp manuel. Ce script automatise :
#   1. Vérification de la connectivité PC2
#   2. Sync des sources Python (src/calculs/optimisation/*.py)
#   3. Sync des sources C (c_modules/*.c, *.h, Makefile) — JAMAIS les .so
#      (architectures PC1/PC2 différentes — un .so copié ne fonctionnerait pas)
#   4. Recompilation sur PC2 lui-même : scan_arb.so, illinois_mpfr.so,
#      illinois_arb.so (ce dernier lie libflint-arb système, pas python-flint
#      comme sur PC1 — chemin détecté automatiquement via ldconfig)
#
# Auteur : hprzeta — Riemann_Lab_C — 2026-06-23

set -e

PC2_HOST="zeta-calc-second"
PC2_KEY="$HOME/.ssh/zeta_cluster"
PC2_PROJET="/home/hprzeta/projet_zeta"

PROJET_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$PROJET_DIR/src/calculs/optimisation"

SSH_CMD="ssh -i $PC2_KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=no -o ConnectTimeout=8"

echo "=== zeta_sync_pc2.sh — sync + recompilation PC2 ==="
echo

echo "→ Vérification connectivité PC2 ($PC2_HOST)..."
if ! $SSH_CMD "$PC2_HOST" "echo OK" >/dev/null 2>&1; then
    echo "✗ PC2 inaccessible (éteint / hors réseau / SSH KO). Abandon." >&2
    exit 1
fi
echo "✓ PC2 accessible"
echo

echo "→ Sync sources Python (src/calculs/optimisation/*.py)..."
rsync -avzi \
    -e "$SSH_CMD" \
    --exclude="c_modules" \
    --exclude="__pycache__" \
    --include="*.py" \
    --exclude="*" \
    "$SRC_DIR/" "$PC2_HOST:$PC2_PROJET/src/calculs/optimisation/"
echo

echo "→ Sync sources C (c_modules/*.c, *.h, Makefile — jamais les .so)..."
rsync -avzi \
    -e "$SSH_CMD" \
    --exclude="__pycache__" \
    --include="*.c" --include="*.h" --include="Makefile" \
    --exclude="*.so" --exclude="*" \
    "$SRC_DIR/c_modules/" "$PC2_HOST:$PC2_PROJET/src/calculs/optimisation/c_modules/"
echo

echo "→ Recompilation sur PC2 (architecture différente — jamais de .so copié)..."
$SSH_CMD "$PC2_HOST" bash -s <<'REMOTE_SCRIPT'
set -e
cd /home/hprzeta/projet_zeta/src/calculs/optimisation/c_modules

echo "  [PC2] make scan_arb.so"
make scan_arb.so

echo "  [PC2] make illinois_mpfr.so"
make illinois_mpfr.so

echo "  [PC2] illinois_arb.so — détection libflint-arb système (pas python-flint)"
LIBFLINT_PATH=$(PATH=/sbin:/usr/sbin:$PATH ldconfig -p 2>/dev/null | grep -m1 'libflint-arb\.so' | awk '{print $NF}')
if [ -z "$LIBFLINT_PATH" ]; then
    echo "  ✗ libflint-arb introuvable sur PC2 (apt install libflint-arb2 ?)" >&2
    exit 1
fi
LIBFLINT_DIR=$(dirname "$LIBFLINT_PATH")
LIBFLINT_SO=$(basename "$LIBFLINT_PATH")
echo "  [PC2] libflint trouvé : $LIBFLINT_DIR/$LIBFLINT_SO"
make illinois_arb.so LIBFLINT_DIR="$LIBFLINT_DIR" LIBFLINT_SO="$LIBFLINT_SO"

echo
echo "  [PC2] .so produits :"
ls -la *.so
echo
echo "  [PC2] Dépendances dynamiques :"
ldd scan_arb.so
ldd illinois_mpfr.so
ldd illinois_arb.so
REMOTE_SCRIPT

echo
echo "=== Sync + recompilation PC2 terminée ✓ ==="
