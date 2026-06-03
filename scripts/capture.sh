#!/usr/bin/env bash
# =============================================================================
# capture.sh — Enregistre une session Claude Code en .log brut + .md propre
# Auteur  : hprzeta · Projet : Riemann_Lab · Mis à jour : 2 juin 2026
# Usage   : ~/projet_zeta/scripts/capture.sh  (AVANT de lancer claude)
# Arrêt   : 'exit' pour fermer Claude Code, puis 'exit' une 2ème fois → .md généré
# =============================================================================

DOSSIER="$HOME/projet_zeta/claude-traitement-journalier"
HORODATAGE=$(date +%Y%m%d_%H%M)
BRUT="$DOSSIER/session_${HORODATAGE}.log"
PROPRE="$DOSSIER/session_${HORODATAGE}.md"

mkdir -p "$DOSSIER"

echo "============================================================"
echo "  📹  Capture de session Claude Code — Riemann_Lab"
echo "  Fichier propre: $PROPRE"
echo "  → Lance 'claude', puis 'exit' × 2 pour arrêter et générer le .md"
echo "============================================================"
echo ""

# TERM=dumb = terminal sans couleurs ni séquences TUI → .md lisible directement
TERM=dumb script -q -f "$BRUT"

echo ""
echo "⏳ Nettoyage..."

# Avec TERM=dumb le nettoyage est minimal et suffisant
col -b < "$BRUT" \
  | sed 's/\r//g' \
  | sed '/^[[:space:]]*$/d' \
  > "$PROPRE"

echo "✅ Session enregistrée :"
echo "   Propre : $PROPRE  ($(wc -l < "$PROPRE") lignes)"
echo "💡 Ouvrir : code '$PROPRE'"
