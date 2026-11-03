#!/usr/bin/env bash
# =============================================================================
# capture.sh — Enregistre une session Claude Code en .log brut + .md propre
# Auteur  : hprzeta · Projet : Riemann_Lab · Mis à jour : 2 juin 2026
# Usage   : ~/projet_zeta/scripts/capture.sh  (AVANT de lancer claude)
# Arrêt   : 'exit' pour fermer Claude Code, puis 'exit' une 2ème fois → .md généré
# =============================================================================

# Tout le corps est dans main() : bash lit la fonction en entier AVANT de l'exécuter,
# donc modifier ce fichier pendant une session n'a plus d'effet (cf. panne du 03/11/2026)
main() {
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

  # Repère horaire : sert à retrouver la transcription .jsonl créée pendant cette session
  REPERE=$(mktemp)
  # TERM=dumb = terminal sans couleurs ; le .log reste BRUT (archive), le .md est généré proprement ensuite
  TERM=dumb script -q -f "$BRUT"

  echo ""
  echo "⏳ Nettoyage..."

  # 1) Nettoyeur du log brut : aucune séquence d'échappement ne subsiste (repli toujours produit)
  python3 -I "$HOME/projet_zeta/scripts/zeta_log_lisible.py" "$BRUT" -o "$PROPRE" \
    || { col -b < "$BRUT" | sed 's/\r//g' | sed 's/\x1b[^a-zA-Z]*[a-zA-Z]//g' | sed '/^[[:space:]]*$/d' > "$PROPRE"; }

  # 2) Version LISIBLE de référence : transcription .jsonl (dialogue seul, secrets masqués)
  JSONL=$(find "$HOME/.claude/projects/-home-riemann-projet-zeta" -maxdepth 1 -name '*.jsonl' -newer "$REPERE" -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
  [ -z "$JSONL" ] && JSONL=$(find "$HOME/.claude/projects/-home-riemann-projet-zeta" -maxdepth 1 -name '*.jsonl' -mmin -1440 -newermt "$(date -r "$BRUT" '+%F %T' 2>/dev/null)" 2>/dev/null | head -1)
  rm -f "$REPERE"
  if [ -n "$JSONL" ]; then
    python3 -I "$HOME/projet_zeta/scripts/zeta_jsonl_to_md.py" "$JSONL" -o "$DOSSIER" || echo "⚠️  conversion .jsonl échouée (le .md nettoyé reste disponible)"
  fi

  echo "✅ Session enregistrée :"
  echo "   Brut   : $BRUT"
  echo "   Nettoyé: $PROPRE  ($(wc -l < "$PROPRE") lignes)"
  echo "   Lisible: voir session_*_jsonl.md dans $DOSSIER (dialogue seul)"
  echo "💡 Ouvrir : code '$PROPRE'"
}

main "$@"
exit $?
