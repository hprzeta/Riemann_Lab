#!/usr/bin/env bash
# make_assistant_archive_summary.sh
# Résume un ou plusieurs fichiers .zip / .tar / .tar.gz / .tgz / .tar.bz2 / .tbz2 / .tar.xz / .txz
# dans un fichier texte exploitable par assistant, sans décompresser les archives.
#
# Usage simple :
#   ./make_assistant_archive_summary.sh archive1.zip archive2.tar.gz
#
# Usage avec sortie personnalisée :
#   ./make_assistant_archive_summary.sh -o assistant_pack_audit_resume_global.txt archive1.zip archive2.tar.gz
#
# Usage auto dans le dossier courant :
#   ./make_assistant_archive_summary.sh --auto
#
# Options :
#   -o, --output FICHIER     Nom du fichier texte de sortie
#   --auto                  Cherche automatiquement les archives dans le dossier courant
#   --max-lines N           Limite le nombre de lignes affichées par archive (défaut: 20000)
#   --sha256                Calcule sha256sum des archives
#   -h, --help              Affiche l'aide

set -u

OUT="assistant_pack_audit_resume_global.txt"
AUTO=0
MAX_LINES=20000
DO_SHA256=0
ARCHIVES=()

usage() {
  sed -n '1,35p' "$0" | sed 's/^# \{0,1\}//'
}

log_section() {
  local title="$1"
  {
    echo
    echo "====================================================================="
    echo "===== ${title}"
    echo "====================================================================="
  } >> "$OUT"
}

list_zip() {
  local f="$1"
  if command -v unzip >/dev/null 2>&1; then
    unzip -l "$f" 2>&1 | head -n "$MAX_LINES" >> "$OUT"
  elif command -v zipinfo >/dev/null 2>&1; then
    zipinfo "$f" 2>&1 | head -n "$MAX_LINES" >> "$OUT"
  else
    echo "ERREUR: unzip/zipinfo indisponible pour lister $f" >> "$OUT"
  fi
}

list_tar() {
  local f="$1"
  tar -tf "$f" 2>&1 | head -n "$MAX_LINES" >> "$OUT"
}

archive_type() {
  local f="$1"
  case "$f" in
    *.zip|*.ZIP) echo "zip" ;;
    *.tar|*.tar.gz|*.tgz|*.tar.bz2|*.tbz2|*.tar.xz|*.txz|*.TAR|*.TGZ) echo "tar" ;;
    *) echo "unknown" ;;
  esac
}

human_size() {
  local f="$1"
  if command -v du >/dev/null 2>&1; then
    du -h "$f" 2>/dev/null | awk '{print $1}'
  else
    ls -lh "$f" 2>/dev/null | awk '{print $5}'
  fi
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -o|--output)
      [[ $# -ge 2 ]] || { echo "Option $1 nécessite un fichier de sortie" >&2; exit 2; }
      OUT="$2"
      shift 2
      ;;
    --auto)
      AUTO=1
      shift
      ;;
    --max-lines)
      [[ $# -ge 2 ]] || { echo "Option --max-lines nécessite un nombre" >&2; exit 2; }
      MAX_LINES="$2"
      shift 2
      ;;
    --sha256)
      DO_SHA256=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      while [[ $# -gt 0 ]]; do ARCHIVES+=("$1"); shift; done
      ;;
    *)
      ARCHIVES+=("$1")
      shift
      ;;
  esac
done

if [[ "$AUTO" -eq 1 ]]; then
  while IFS= read -r -d '' f; do
    ARCHIVES+=("$f")
  done < <(find . -maxdepth 1 -type f \( \
    -iname '*.zip' -o \
    -iname '*.tar' -o \
    -iname '*.tar.gz' -o \
    -iname '*.tgz' -o \
    -iname '*.tar.bz2' -o \
    -iname '*.tbz2' -o \
    -iname '*.tar.xz' -o \
    -iname '*.txz' \
  \) -print0 | sort -z)
fi

if [[ "${#ARCHIVES[@]}" -eq 0 ]]; then
  echo "Aucune archive fournie. Exemple :" >&2
  echo "  $0 -o assistant_pack_audit_resume_global.txt audit.zip audit.tar.gz" >&2
  echo "Ou :" >&2
  echo "  $0 --auto" >&2
  exit 2
fi

# Create/overwrite output
{
  echo "===== RÉSUMÉ ARCHIVES POUR ASSISTANT ====="
  echo "Date génération : $(date -Is 2>/dev/null || date)"
  echo "Machine         : $(hostname 2>/dev/null || true)"
  echo "Utilisateur     : $(whoami 2>/dev/null || true)"
  echo "Répertoire      : $(pwd)"
  echo "Fichier sortie  : $OUT"
  echo "Archives reçues : ${#ARCHIVES[@]}"
  echo
  echo "===== OUTILS DISPONIBLES ====="
  command -v unzip >/dev/null 2>&1 && unzip -v | head -n 2 || echo "unzip: absent"
  command -v tar >/dev/null 2>&1 && tar --version | head -n 1 || echo "tar: absent"
  command -v sha256sum >/dev/null 2>&1 && echo "sha256sum: présent" || echo "sha256sum: absent"
} > "$OUT"

log_section "LISTE DES ARCHIVES"
for f in "${ARCHIVES[@]}"; do
  if [[ -e "$f" ]]; then
    printf '%s | type=%s | taille=%s\n' "$f" "$(archive_type "$f")" "$(human_size "$f")" >> "$OUT"
  else
    printf '%s | ERREUR: fichier introuvable\n' "$f" >> "$OUT"
  fi
done

if [[ "$DO_SHA256" -eq 1 ]]; then
  log_section "SHA256 DES ARCHIVES"
  for f in "${ARCHIVES[@]}"; do
    if [[ -f "$f" ]]; then
      if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$f" >> "$OUT" 2>&1
      else
        echo "sha256sum absent : impossible pour $f" >> "$OUT"
      fi
    fi
  done
fi

# Global local context
log_section "CONTEXTE DU DOSSIER COURANT"
{
  echo "--- ls -lah . ---"
  ls -lah . 2>&1
  echo
  echo "--- du -sh ./* ---"
  du -sh ./* 2>/dev/null | sort -h || true
} >> "$OUT"

# Per archive detail
idx=0
for f in "${ARCHIVES[@]}"; do
  idx=$((idx + 1))
  log_section "ARCHIVE ${idx}/${#ARCHIVES[@]} : $f"
  if [[ ! -e "$f" ]]; then
    echo "ERREUR: fichier introuvable : $f" >> "$OUT"
    continue
  fi

  {
    echo "Chemin : $f"
    echo "Type   : $(archive_type "$f")"
    echo "Taille : $(human_size "$f")"
    echo
    echo "--- Métadonnées ls ---"
    ls -lh "$f" 2>&1
    echo
    echo "--- Contenu archive, limité à $MAX_LINES lignes ---"
  } >> "$OUT"

  case "$(archive_type "$f")" in
    zip) list_zip "$f" ;;
    tar) list_tar "$f" ;;
    *)
      echo "Type inconnu : tentative avec tar -tf puis unzip -l" >> "$OUT"
      tar -tf "$f" 2>&1 | head -n "$MAX_LINES" >> "$OUT" || true
      unzip -l "$f" 2>&1 | head -n "$MAX_LINES" >> "$OUT" || true
      ;;
  esac

done

log_section "FIN"
{
  echo "Résumé généré : $OUT"
  echo "Taille résumé : $(human_size "$OUT")"
  echo
  echo "Commande conseillée pour m'envoyer le résumé :"
  echo "  ls -lh '$OUT'"
  echo
  echo "Si besoin de compresser seulement ce résumé :"
  echo "  zip assistant_pack_resume_txt.zip '$OUT'"
} >> "$OUT"

echo "✅ Résumé créé : $OUT"
echo "📄 Taille : $(human_size "$OUT")"
echo "➡️  Envoie-moi ce fichier texte en priorité."
