#!/bin/bash
# =============================================================================
# zeta_point_maj.sh — Point de situation + MAJ guide + préparation commit
# Destiné à l'instance CLAUDE CODE (exécution sur PC1 zeta-lab)
# Projet Zêta / Riemann Lab — hprzeta/Riemann_Lab
# Version : 1.0 — 30/08/2026
#
# Ce que fait le script :
#   1. POINT   — collecte l'état système RÉEL (lecture seule) et l'affiche
#   2. GUIDE   — ajoute un bloc daté au guide canonique (sauvegarde préalable)
#   3. DÉPÔT   — git add + commit LOCAL, puis S'ARRÊTE avant le push
#                (le push est affiché mais PAS exécuté : confirmation humaine)
#
# Aucune opération destructive. Le push reste manuel.
# =============================================================================

set -uo pipefail

# ─── Paramètres (à ajuster si les chemins diffèrent) ─────────────────────────
REPO_DIR="${ZETA_REPO:-$HOME/projet_zeta}"   # racine du dépôt git local
GUIDE="rapport_clonage_zeta.md"              # fichier canonique (dans le dépôt)
BRANCH="Riemann_Lab_IA"                      # branche de développement
DATE_TAG=$(date +%Y-%m-%d)
DATE_FULL=$(date +%Y-%m-%d\ %H:%M)

RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; BLU='\033[0;34m'; CYN='\033[0;36m'; NC='\033[0m'
banner(){ echo -e "\n${BLU}══════════════════════════════════════════════════${NC}\n${BLU}  $1${NC}\n${BLU}══════════════════════════════════════════════════${NC}\n"; }
ok(){ echo -e "${GRN}✅ $1${NC}"; }; warn(){ echo -e "${YLW}⚠️  $1${NC}"; }; err(){ echo -e "${RED}❌ $1${NC}"; }; info(){ echo -e "${CYN}ℹ️  $1${NC}"; }

# =============================================================================
# 1. POINT DE SITUATION — collecte lecture seule
# =============================================================================
banner "1/3 — POINT DE SITUATION (lecture seule)"

STATE=$(mktemp /tmp/zeta_point_XXXX.md)

{
  echo "#### État système collecté — $DATE_FULL"
  echo
  echo '**Disques et montages :**'
  echo '```'
  lsblk -o NAME,SIZE,LABEL,MOUNTPOINT,FSTYPE 2>/dev/null | grep -vE 'loop|snap'
  echo '```'
  echo
  echo '**Racine active :**'
  echo '```'
  findmnt -o SOURCE,TARGET,LABEL,UUID / 2>/dev/null
  echo '```'
  echo
  echo '**Alias Zêta présents :**'
  echo '```'
  grep -nE "alias zeta-(clone|temp)=" "$HOME/.bashrc" 2>/dev/null || echo "(aucun alias zeta-clone/zeta-temp trouvé)"
  echo '```'
  echo
  echo '**Script de clonage :**'
  echo '```'
  ls -l "$HOME/projet_zeta/scripts/zeta_backup_toshiba.sh" 2>/dev/null || echo "(zeta_backup_toshiba.sh ABSENT)"
  echo '```'
  echo
  echo '**Occupation du clone Toshiba (si monté) :**'
  echo '```'
  for m in Toshiba-PC1-root Toshiba-PC1-home Toshiba-PC1-data; do
    p="/media/riemann/$m"
    if mountpoint -q "$p" 2>/dev/null; then
      df -h "$p" | tail -1 | awk -v M="$m" '{printf "%-20s %s util / %s (%s)\n", M, $3, $2, $5}'
    else
      echo "$m : non monté"
    fi
  done
  echo '```'
} > "$STATE"

cat "$STATE"
ok "État collecté dans $STATE"

# =============================================================================
# 2. MISE À JOUR DU GUIDE — bloc narratif daté + état collecté
# =============================================================================
banner "2/3 — MISE À JOUR DU GUIDE"

# Localiser le guide dans le dépôt
if [[ ! -d "$REPO_DIR/.git" ]]; then
  warn "Pas de dépôt git à '$REPO_DIR'. Recherche…"
  FOUND=$(find "$HOME" -maxdepth 3 -type d -name .git 2>/dev/null | head -1)
  [[ -n "$FOUND" ]] && REPO_DIR=$(dirname "$FOUND")
fi
[[ -d "$REPO_DIR/.git" ]] || { err "Dépôt git introuvable. Ajuste ZETA_REPO puis relance."; exit 1; }
info "Dépôt : $REPO_DIR"

GUIDE_PATH="$REPO_DIR/$GUIDE"
[[ -f "$GUIDE_PATH" ]] || GUIDE_PATH=$(find "$REPO_DIR" -name "$GUIDE" 2>/dev/null | head -1)
if [[ -z "${GUIDE_PATH:-}" || ! -f "$GUIDE_PATH" ]]; then
  GUIDE_PATH="$REPO_DIR/$GUIDE"
  warn "Guide absent — création d'un nouveau fichier : $GUIDE_PATH"
  echo "# Rapport de clonage — Cluster Zêta" > "$GUIDE_PATH"
fi
info "Guide : $GUIDE_PATH"

cp "$GUIDE_PATH" "$GUIDE_PATH.bak-$DATE_TAG"   # sauvegarde (cp, pas tee)
ok "Sauvegarde : $GUIDE_PATH.bak-$DATE_TAG"

# --- Bloc narratif rédigé par Claude coordinateur (contexte du 30/08) ---------
cat >> "$GUIDE_PATH" <<'ZETA_NARRATIF'

---

## Session 2026-08-30 — Resynchronisation PC1 et script de clone v2.0

### Contexte (constaté, non supposé)
- Booté sur **PC1 local** confirmé : racine `/` = `sda1`, label `Seagate-PC1-root`.
- **Désynchronisation détectée** : `~/.bashrc` de PC1 datait du **5 août**, alors que
  le travail de la session du **25 août** (script `zeta_backup_toshiba.sh` + alias
  `zeta-clone` / `zeta-temp`) était **absent**. Cause non tranchée avec certitude :
  soit le script n'a jamais été copié (`cp`) sur ce PC1, soit ce PC1 a été restauré
  à un état antérieur au 25/08. **Fait établi** : ces éléments ont dû être recréés.

### Corrections appliquées
- **Labels du clone Toshiba renommés** : `Toshiba-PC1-root/home/data`
  (auparavant `root-clone` / `home-clone` / `data-clone`).
  Points de montage réels : `/media/riemann/Toshiba-PC1-{root,home,data}`.
- **Script régénéré en v2.0** (version allégée PC1 → Toshiba) :
  chemins corrigés, **montage automatique** des 3 partitions (sdb2/sdb3 n'étaient
  pas montées), identification **par label** (jamais par `sdX`), correction du
  `fstab` du clone par `cp` (retour d'expérience : `tee` échoue en silence).
- **Alias recréés** dans `~/.bashrc` : `zeta-clone`, `zeta-temp`.

### Point de vigilance (à respecter avant tout clone réel)
- L'option 1 du script fait `rsync --delete`. Vu l'écart de dates, le clone Toshiba
  pourrait contenir des fichiers **plus récents** que PC1. **Ne jamais lancer le
  clone sans simulation préalable** :
  `sudo rsync -aAXHxn --delete / /media/riemann/Toshiba-PC1-root/ | grep '^deleting'`.
  Si des fichiers importants apparaissent en `deleting`, NE PAS synchroniser dans ce sens.

### Reste à faire
- [ ] Simulation `rsync -n` avant premier clone réel (validation humaine).
- [ ] Valider bootabilité du clone (F2 BIOS, désactiver `sda`) — reporté depuis juillet.
- [ ] Labellisation OpenBSD PC4 (`disklabel`) — reporté.
- [ ] Valider `nofail` fstab Micron 1100 (`/mnt/vault_rag`) au reboot.

ZETA_NARRATIF

# --- Injecter l'état système collecté ----------------------------------------
{
  echo "### Annexe — état système au $DATE_FULL"
  echo
  cat "$STATE"
  echo
  NLINES=$(wc -l < "$GUIDE_PATH")
  echo "*Mis à jour le $DATE_TAG — $((NLINES)) lignes.*"
} >> "$GUIDE_PATH"

ok "Guide mis à jour ($(wc -l < "$GUIDE_PATH") lignes)"

# =============================================================================
# 3. MISE À JOUR DU DÉPÔT — add + commit LOCAL (push NON exécuté)
# =============================================================================
banner "3/3 — PRÉPARATION DU COMMIT (push manuel)"

cd "$REPO_DIR" || { err "cd $REPO_DIR impossible"; exit 1; }

CUR_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
info "Branche courante : $CUR_BRANCH (attendue : $BRANCH)"
[[ "$CUR_BRANCH" == "$BRANCH" ]] || warn "Tu n'es pas sur $BRANCH — vérifie avant de committer."

# Stager le guide + le script s'il est versionné dans le dépôt
git add "$GUIDE_PATH" 2>/dev/null || true
[[ -f "$REPO_DIR/scripts/zeta_backup_toshiba.sh" ]] && git add "scripts/zeta_backup_toshiba.sh" 2>/dev/null || true

echo
info "Fichiers indexés :"
git status --short

COMMIT_MSG="docs(clone): resync PC1 state + regenerate toshiba backup script v2.0

- corrige les points de montage (Toshiba-PC1-root/home/data)
- montage automatique des 3 partitions + fix fstab par cp
- recree les alias zeta-clone / zeta-temp
- consigne la desynchronisation PC1 du 30/08"

git commit -m "$COMMIT_MSG" 2>&1 | tail -3 || warn "Rien à committer (ou déjà à jour)."

echo
banner "COMMIT LOCAL FAIT — PUSH À CONFIRMER"
warn "Le push vers GitHub n'est PAS automatique. Pour publier, après relecture :"
echo -e "${CYN}   git push origin $BRANCH${NC}"
echo
info "Pour annuler le commit local (avant push) :  git reset --soft HEAD~1"
ok  "Point de situation terminé."
