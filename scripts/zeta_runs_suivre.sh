#!/usr/bin/env bash
# ==============================================================================
# zeta_runs_suivre.sh — suivre les livrables de monitoring/runs/ dans git (alias : zeta-runs-suivre)
# Convention (celle des runs déjà suivis) : on suit les LIVRABLES (rapport.md/pdf, session.md,
# meta.json, etat.json, figures/*.png, progress_*, report_en.pdf) ; les fichiers de TRAVAIL
# (*.csv, *.pid, *.log, .fin, *.bak*) restent hors git.
# Par défaut : SIMULATION + AUDIT seulement (rien n'est indexé). Aucun commit n'est jamais fait ici.
# Usage : zeta-runs-suivre              simulation : liste, taille, audit (lecture seule)
#         zeta-runs-suivre --ajouter    indexe (git add) si l'audit est propre ; commit/push : à vous
# Audit : refuse d'indexer si une IP, MAC, jeton, duckdns, clé privée ou e-mail est trouvé.
# ==============================================================================
set -euo pipefail

# Dépôt du projet (le script fonctionne depuis n'importe quel dossier)
DEPOT="$HOME/projet_zeta"
cd "$DEPOT"

# Mode : simulation par défaut, indexation seulement avec --ajouter
MODE="simulation"
case "${1:-}" in
    "") ;;
    --ajouter) MODE="ajouter" ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Option inconnue : $1 (voir --help)" >&2; exit 2 ;;
esac

# Dossier suivi et exclusions (fichiers de travail) sous forme de pathspecs git
R="monitoring/runs"
EXCLUSIONS=(":!$R/**/*.pid" ":!$R/**/*.log" ":!$R/**/.fin" ":!$R/**/*.bak*" ":!$R/**/*.csv")

# Fichier temporaire pour la liste des candidats (supprimé en sortie)
LISTE="$(mktemp)"
trap 'rm -f "$LISTE"' EXIT

# Liste des fichiers que « git add » indexerait (simulation -n), sans les guillemets de git
git add -n "$R" "${EXCLUSIONS[@]}" | sed "s/^add '//; s/'\$//" > "$LISTE"
N=$(wc -l < "$LISTE")

# Rien de nouveau : on s'arrête proprement
if [ "$N" -eq 0 ]; then
    echo "Rien de nouveau à suivre dans $R (tout est déjà indexé ou exclu)."
    exit 0
fi

# Taille réelle cumulée des fichiers candidats (octets, puis Mo)
OCTETS=$(tr '\n' '\0' < "$LISTE" | xargs -0 stat -c %s | paste -sd+ | bc)
echo "Candidats : $N fichiers, $((OCTETS / 1048576)) Mo"
echo "Par dossier :"
cut -d/ -f3 "$LISTE" | sort | uniq -c | sed 's/^/  /'

# --- Audit des fichiers texte (md, json) ---
MOTIF='duckdns|PRIVATE KEY|ghp_|github_pat|api.?key|token=|passw=|([0-9a-f]{2}:){5}[0-9a-f]{2}|\b[0-9]{1,3}(\.[0-9]{1,3}){3}\b|[A-Za-z0-9._-]+@[A-Za-z0-9-]+\.[a-z]+|IP_PC'
TROUVES=0
TEXTES=$(grep -E '\.(md|json)$' "$LISTE" || true)
if [ -n "$TEXTES" ]; then
    # grep -I ignore les binaires ; code 1 = aucune correspondance (normal)
    if printf '%s\n' "$TEXTES" | tr '\n' '\0' | xargs -0 grep -nIiE "$MOTIF" > /tmp/zeta_runs_audit.$$ 2>/dev/null; then
        TROUVES=1
        echo "AUDIT TEXTE : correspondances trouvées (extrait) :"
        head -5 /tmp/zeta_runs_audit.$$ | cut -c1-160 | sed 's/^/  /'
    fi
    rm -f /tmp/zeta_runs_audit.$$
fi

# --- Audit des binaires (png, pdf) : motifs précis seulement (IP, MAC, duckdns) ---
# Le motif e-mail est exclu ici : il donne des faux positifs dans les flux compressés.
MOTIF_BIN='([0-9a-f]{2}:){5}[0-9a-f]{2}|\b[0-9]{1,3}(\.[0-9]{1,3}){3}\b|duckdns'
while IFS= read -r f; do
    if strings -n 6 "$f" | grep -qiE "$MOTIF_BIN"; then
        TROUVES=1
        echo "AUDIT BINAIRE : correspondance dans $f"
    fi
done < <(grep -E '\.(png|pdf)$' "$LISTE" || true)

# Verdict de l'audit : on refuse d'aller plus loin s'il y a un doute
if [ "$TROUVES" -ne 0 ]; then
    echo "AUDIT : NON PROPRE — rien n'est indexé. Vérifiez les lignes ci-dessus." >&2
    exit 3
fi
echo "AUDIT : propre (aucune IP, MAC, jeton, duckdns ni e-mail)."

# Simulation : on s'arrête ici
if [ "$MODE" = "simulation" ]; then
    echo "Simulation seulement. Pour indexer : zeta-runs-suivre --ajouter"
    exit 0
fi

# Indexation réelle (jamais de commit ici)
git add "$R" "${EXCLUSIONS[@]}"
echo "Indexé : $(git diff --cached --name-only -- "$R" | wc -l) fichiers (git add fait, PAS de commit)."
echo "Étapes suivantes (à vous) : git commit, puis cherry-pick -x sur main / Riemann_Lab_C / Riemann_Lab_Test."
