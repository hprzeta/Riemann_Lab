#!/usr/bin/env bash
#
# pdf_to_md_rapide.sh — Convertit les PDF d'un dossier en Markdown (pymupdf4llm)
# ---------------------------------------------------------------------------
# Projet : Riemann_Lab / hprzeta
# Outil  : pymupdf4llm — conversion PDF -> Markdown LÉGÈRE et RAPIDE.
#          ~quelques secondes/PDF, ~200 Mo de RAM, aucun modèle ML à charger.
#          Idéal pour des PDF "texte natif" (rapports, formules) sur 8 Go RAM.
#
# Différence avec pdf_to_md.sh (marker) :
#   - marker         : qualité maximale (OCR, layout, tableaux) MAIS ~22 min/PDF
#                      et ~5 Go RAM -> réservé aux PDF complexes/scannés.
#   - pymupdf4llm    : rapide et léger -> à utiliser par défaut.
#
# Usage :
#   ./pdf_to_md_rapide.sh <dossier_contenant_les_pdf>
#
# Exemple :
#   ./pdf_to_md_rapide.sh ~/projet_zeta/pdf/optimisation/Voie_b_5
#
# Résultat :
#   Pour chaque  monfichier.pdf  ->  monfichier.md  (même nom, même dossier)
#   Les .md déjà présents sont ignorés (ne réécrase pas le travail de marker).
# ---------------------------------------------------------------------------

set -euo pipefail   # arrêt si erreur, variable non définie, ou échec dans un pipe

# --- 1. Vérifier l'argument (dossier dynamique) -----------------------------
if [ $# -ne 1 ]; then
    echo "❌ Usage : $0 <dossier_contenant_les_pdf>"
    echo "   Exemple : $0 ~/projet_zeta/pdf/optimisation/Voie_b_5"
    exit 1
fi

DIR="$1"

# --- 2. Vérifier que le dossier existe --------------------------------------
if [ ! -d "$DIR" ]; then
    echo "❌ Le dossier n'existe pas : $DIR"
    exit 1
fi

# --- 3. Vérifier que pymupdf4llm est disponible dans le venv ----------------
if ! python3 -c "import pymupdf4llm" 2>/dev/null; then
    echo "❌ Module 'pymupdf4llm' introuvable."
    echo "   → Active ton venv, puis : pip install pymupdf4llm"
    exit 1
fi

# --- 4. Compteurs pour le bilan ---------------------------------------------
total=0; ok=0; skip=0; fail=0

echo "📂 Dossier : $DIR"
echo "🔄 Conversion rapide des PDF en Markdown (pymupdf4llm)..."
echo "----------------------------------------------------------------------"

# --- 5. Boucle sur les .pdf (gère les espaces dans les noms) ----------------
while IFS= read -r -d '' pdf; do
    total=$((total + 1))

    base="$(basename "$pdf" .pdf)"   # nom sans chemin ni extension
    target_md="$DIR/$base.md"        # fichier .md attendu

    # 5a. Si le .md existe déjà -> on saute (préserve le travail de marker)
    if [ -f "$target_md" ]; then
        echo "⏭️  Déjà fait  : $base.md (ignoré)"
        skip=$((skip + 1))
        continue
    fi

    echo "▶️  Conversion : $base.pdf"

    # 5b. Conversion via pymupdf4llm en une ligne Python :
    #     - to_markdown(pdf) renvoie tout le texte en Markdown
    #     - on l'écrit dans le .md cible (encodage utf-8 explicite)
    if python3 - "$pdf" "$target_md" <<'PYEOF'
import sys, pymupdf4llm, pathlib
pdf_path, md_path = sys.argv[1], sys.argv[2]
md_text = pymupdf4llm.to_markdown(pdf_path)          # PDF -> texte Markdown
pathlib.Path(md_path).write_text(md_text, encoding="utf-8")
PYEOF
    then
        echo "✅ OK         : $base.md"
        ok=$((ok + 1))
    else
        echo "❌ Échec      : $base.pdf"
        fail=$((fail + 1))
    fi

done < <(find "$DIR" -maxdepth 1 -type f -iname '*.pdf' -print0)

# --- 6. Bilan ---------------------------------------------------------------
echo "----------------------------------------------------------------------"
echo "📊 Bilan : $total PDF | ✅ $ok convertis | ⏭️  $skip ignorés | ❌ $fail échecs"

if [ "$total" -eq 0 ]; then
    echo "ℹ️  Aucun PDF trouvé dans $DIR"
fi
