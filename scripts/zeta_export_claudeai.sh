#!/usr/bin/env bash
# ==============================================================================
# zeta_export_claudeai.sh
# Objectif : produire UN fichier Markdown masqué (état du projet) à déposer à la
#            main dans un Projet claude.ai, pour aligner claude.ai sur Claude Code.
# Sources  : bloc PROMPT_REPRISE de ~/riemann_handoff/Handoff.md + CLAUDE.md projet.
# Sortie   : ~/zeta_inventaire/export_claudeai/contexte_claudeai_AAAAMMJJ.md (600)
# Garanties: lecture seule des sources ; AUCUN réseau, commit, push ni suppression.
#            Masquage = celui de zeta_jsonl_to_md.py ; refus d'écrire si une
#            2e passe de masquage change encore le texte.
# Usage    : bash scripts/zeta_export_claudeai.sh
# ==============================================================================
set -Eeuo pipefail

# --- Chemins -----------------------------------------------------------------
HANDOFF="${HANDOFF:-$HOME/riemann_handoff/Handoff.md}"            # source de vérité (hors repo)
CLAUDE_MD="${CLAUDE_MD:-$HOME/projet_zeta/CLAUDE.md}"             # règles permanentes du projet
MASQUEUR="$(dirname "$(readlink -f "$0")")/zeta_jsonl_to_md.py"   # module de masquage réutilisé
OUT_DIR="${OUT_DIR:-$HOME/zeta_inventaire/export_claudeai}"       # dossier privé, hors dépôt
DATE="$(date +%Y%m%d)"                                            # date du jour
OUT="$OUT_DIR/contexte_claudeai_${DATE}.md"                       # fichier de sortie

# --- Contrôles préalables ----------------------------------------------------
for f in "$HANDOFF" "$CLAUDE_MD" "$MASQUEUR"; do
  [ -r "$f" ] || { echo "ERREUR : fichier illisible ou absent : $f" >&2; exit 1; }
done
command -v python3 >/dev/null || { echo "ERREUR : python3 absent" >&2; exit 1; }

# Refus d'écraser silencieusement un export du jour (piège déjà vécu le 27/09)
if [ -e "$OUT" ]; then
  echo "ERREUR : $OUT existe déjà. Renommez-le ou supprimez-le vous-même, puis relancez." >&2
  exit 1
fi

mkdir -p "$OUT_DIR"          # création du dossier privé si besoin
chmod 700 "$OUT_DIR"         # accès propriétaire seul

# --- Extraction + masquage + écriture (Python, un seul passage) -------------
python3 -I - "$HANDOFF" "$CLAUDE_MD" "$MASQUEUR" "$OUT" <<'PYEOF'
import importlib.util, os, re, sys

handoff, claude_md, masqueur, sortie = sys.argv[1:5]

# Import du module de masquage par chemin (son main() ne s'exécute pas à l'import)
spec = importlib.util.spec_from_file_location("zmask", masqueur)
zmask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(zmask)

# Lecture des sources (lecture seule)
txt_handoff = open(handoff, encoding="utf-8").read()
txt_claude = open(claude_md, encoding="utf-8").read()

# Bloc entre les balises PROMPT_REPRISE (balises incluses)
m = re.search(r"<!-- PROMPT_REPRISE_DEBUT -->.*?<!-- PROMPT_REPRISE_FIN -->", txt_handoff, re.S)
if not m:
    sys.exit("ERREUR : balises PROMPT_REPRISE introuvables dans le Handoff")
bloc = m.group(0)

# Assemblage du document
doc = (
    "# Contexte Riemann_Lab pour claude.ai\n\n"
    "> Généré par `zeta_export_claudeai.sh` — copie MASQUÉE (IP, MAC, e-mails, secrets).\n"
    "> Source de vérité : le Handoff local lu par Claude Code. Cette copie date du jour de génération\n"
    "> et peut être périmée : la régénérer à chaque fin de session.\n"
    "> Les marqueurs `[IPV4]`, `[HOTE_CLUSTER]`, etc. remplacent des valeurs réelles volontairement absentes.\n\n"
    "## 1. État courant (bloc PROMPT_REPRISE du Handoff)\n\n" + bloc + "\n\n"
    "## 2. Règles permanentes du projet (CLAUDE.md)\n\n" + txt_claude + "\n"
)

# 1re passe de masquage
compteurs = {}
masque = zmask.masquer(doc, compteurs)

# 2e passe : doit être sans effet, sinon on refuse d'écrire
c2 = {}
if zmask.masquer(masque, c2) != masque:
    sys.exit("ERREUR : la 2e passe de masquage modifie encore le texte, rien n'est écrit")

# Écriture en mode 600 (création exclusive : n'écrase jamais)
fd = os.open(sortie, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "w", encoding="utf-8") as f:
    f.write(masque)

# Bilan (jamais de valeur masquée affichée, seulement des compteurs)
print(f"OK : {sortie}")
print(f"Taille : {len(masque.encode('utf-8'))//1024} Ko, {masque.count(chr(10))} lignes")
print("Masquages : " + (", ".join(f"{k}={v}" for k, v in sorted(compteurs.items())) or "aucun"))
PYEOF

echo "À faire : relire le fichier, puis le déposer vous-même dans le Projet claude.ai (remplace la version précédente)."
