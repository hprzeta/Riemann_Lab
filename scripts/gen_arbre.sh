#!/bin/bash
# ============================================================
# gen_arbre.sh — Générateur d'arbre de dossier interactif
# Projet : Riemann_Lab / hprzeta
# Usage  : bash gen_arbre.sh
# ============================================================

set -euo pipefail

# ── Couleurs ────────────────────────────────────────────────
BOLD="\e[1m"
CYAN="\e[36m"
GREEN="\e[32m"
YELLOW="\e[33m"
RED="\e[31m"
RESET="\e[0m"

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD}║   🌳 Générateur d'arbre de projet        ║${RESET}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════╝${RESET}"
echo ""

# ── 1. Dossier à explorer ───────────────────────────────────
echo -e "${BOLD}1. Dossier à explorer${RESET}"
read -rp "   Chemin (Entrée = ~/projet_zeta) : " DOSSIER
DOSSIER="${DOSSIER:-$HOME/projet_zeta}"

# Résoudre ~ si saisi manuellement
DOSSIER="${DOSSIER/#\~/$HOME}"

if [ ! -d "$DOSSIER" ]; then
    echo -e "${RED}   ✗ Dossier introuvable : $DOSSIER${RESET}"
    exit 1
fi
echo -e "${GREEN}   ✓ $DOSSIER${RESET}"
echo ""

# ── 2. Profondeur ───────────────────────────────────────────
echo -e "${BOLD}2. Profondeur maximale${RESET}"
read -rp "   Niveau -L (Entrée = 7) : " NIVEAU
NIVEAU="${NIVEAU:-7}"

if ! [[ "$NIVEAU" =~ ^[1-9][0-9]*$ ]]; then
    echo -e "${RED}   ✗ Valeur invalide, utilisation de 7${RESET}"
    NIVEAU=7
fi
echo -e "${GREEN}   ✓ -L $NIVEAU${RESET}"
echo ""

# ── 3. Dossiers/fichiers à exclure ──────────────────────────
echo -e "${BOLD}3. Exclusions (séparées par | , Entrée = zeta_env)${RESET}"
echo -e "   Exemples : ${YELLOW}zeta_env|__pycache__|.git|node_modules${RESET}"
read -rp "   Exclusions : " EXCLUSIONS
EXCLUSIONS="${EXCLUSIONS:-zeta_env}"
echo -e "${GREEN}   ✓ -I \"$EXCLUSIONS\"${RESET}"
echo ""

# ── 4. Nom du fichier de sortie ─────────────────────────────
echo -e "${BOLD}4. Fichier de sortie${RESET}"
NOM_DEFAULT="arbre_$(basename "$DOSSIER")_L${NIVEAU}_$(date +%Y%m%d).txt"
read -rp "   Nom du fichier (Entrée = $NOM_DEFAULT) : " NOM_SORTIE
NOM_SORTIE="${NOM_SORTIE:-$NOM_DEFAULT}"
echo -e "${GREEN}   ✓ $NOM_SORTIE${RESET}"
echo ""

# ── 5. Options supplémentaires ──────────────────────────────
echo -e "${BOLD}5. Options${RESET}"
read -rp "   Inclure les fichiers cachés (dossiers .xxx) ? [o/N] : " CACHES
read -rp "   Inclure les fichiers (pas seulement dossiers) ? [O/n] : " FICHIERS
echo ""

OPTS="--dirsfirst --noreport"
[[ "${CACHES,,}" == "o" ]] && OPTS="$OPTS -a"
[[ "${FICHIERS,,}" != "n" ]] && FICHIERS_OK=true || FICHIERS_OK=false

# ── 6. Vérifier que tree est installé ───────────────────────
if ! command -v tree &>/dev/null; then
    echo -e "${RED}   ✗ 'tree' non installé. Lance : sudo apt install tree${RESET}"
    exit 1
fi

# ── 7. Génération ───────────────────────────────────────────
echo -e "${BOLD}Génération en cours...${RESET}"

# Construire la commande
if $FICHIERS_OK; then
    COMMANDE="tree \"$DOSSIER\" -L $NIVEAU $OPTS -I \"$EXCLUSIONS\""
else
    COMMANDE="tree \"$DOSSIER\" -L $NIVEAU $OPTS -d -I \"$EXCLUSIONS\""
fi

# Exécuter et capturer
eval "$COMMANDE" > "$NOM_SORTIE"

NB_LIGNES=$(wc -l < "$NOM_SORTIE")

echo -e "${GREEN}${BOLD}   ✓ Fichier généré : $NOM_SORTIE ($NB_LIGNES lignes)${RESET}"
echo ""

# ── 8. Afficher les 20 premières lignes ─────────────────────
echo -e "${CYAN}── Aperçu (20 premières lignes) ──────────────────────${RESET}"
head -20 "$NOM_SORTIE"
echo -e "${CYAN}──────────────────────────────────────────────────────${RESET}"
echo ""

# ── 9. Créer version Markdown (.md) ─────────────────────────
NOM_MD="${NOM_SORTIE%.txt}.md"
{
    echo "# 🗂️ Arbre du projet — $(basename "$DOSSIER")"
    echo ""
    echo "> Généré le $(date '+%d %B %Y à %H:%M')  "
    echo "> Profondeur : L${NIVEAU} | Exclusions : \`${EXCLUSIONS}\`"
    echo ""
    echo '```'
    cat "$NOM_SORTIE"
    echo '```'
} > "$NOM_MD"

echo -e "${GREEN}   ✓ Version Markdown  : $NOM_MD${RESET}"
echo ""

# ── 10. Proposition de copie vers le wiki ───────────────────
WIKI_PATH="$HOME/projet_zeta/Riemann_Lab.wiki"
if [ -d "$WIKI_PATH" ]; then
    read -rp "   Copier $NOM_MD vers le wiki ? [O/n] : " COPIE_WIKI
    if [[ "${COPIE_WIKI,,}" != "n" ]]; then
        cp "$NOM_MD" "$WIKI_PATH/arbre_dossiers_projet.md"
        echo -e "${GREEN}   ✓ Copié vers $WIKI_PATH/arbre_dossiers_projet.md${RESET}"
        echo ""
        read -rp "   Pousser sur GitHub (git push) ? [O/n] : " DO_PUSH
        if [[ "${DO_PUSH,,}" != "n" ]]; then
            cd "$WIKI_PATH"
            git add arbre_dossiers_projet.md
            git commit -m "docs: update arbre projet L${NIVEAU} $(date +%Y%m%d)"
            git push origin master
            echo -e "${GREEN}   ✓ Poussé sur GitHub Wiki${RESET}"
        fi
    fi
fi

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD}║   ✅ Terminé                             ║${RESET}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  Fichiers générés :"
echo -e "  ${YELLOW}$NOM_SORTIE${RESET}  ← brut (pour tree manuel)"
echo -e "  ${YELLOW}$NOM_MD${RESET}  ← Markdown (pour wiki GitHub)"
echo ""
