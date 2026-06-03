#!/usr/bin/env bash
#
# pdf_to_md.sh — Convertit en Markdown tous les PDF d'un dossier (via marker)
# ---------------------------------------------------------------------------
# Projet : Riemann_Lab / hprzeta
# Outil  : marker (commande "marker_single") — conversion PDF -> Markdown
#          haute qualité (formules LaTeX, tableaux, maths).
#
# Pourquoi ce script ?
#   Donner un PDF brut à Claude/Claude Code est très coûteux en tokens
#   (il est relu en "cache read" à chaque tour). Un .md pèse 10 à 50x moins.
#   On convertit donc une fois pour toutes les PDF en .md.
#
# Usage :
#   ./pdf_to_md.sh <dossier_contenant_les_pdf>
#
# Exemple (les 9 PDF Voie_b_5) :
#   ./pdf_to_md.sh ~/projet_zeta/pdf/optimisation/Voie_b_5
#
# Résultat :
#   Pour chaque  monfichier.pdf  ->  monfichier.md  (même nom, même dossier)
# ---------------------------------------------------------------------------

set -euo pipefail   # arrêt si erreur, variable non définie, ou échec dans un pipe

# --- 1. Vérifier l'argument (le dossier est passé dynamiquement) ------------
if [ $# -ne 1 ]; then
    echo "❌ Usage : $0 <dossier_contenant_les_pdf>"
    echo "   Exemple : $0 ~/projet_zeta/pdf/optimisation/Voie_b_5"
    exit 1
fi

DIR="$1"   # dossier cible, fourni par l'utilisateur

# --- 2. Vérifier que le dossier existe --------------------------------------
if [ ! -d "$DIR" ]; then
    echo "❌ Le dossier n'existe pas : $DIR"
    exit 1
fi

# --- 3. Vérifier que marker_single est disponible ---------------------------
if ! command -v marker_single >/dev/null 2>&1; then
    echo "❌ La commande 'marker_single' est introuvable."
    echo "   → Active ton venv, puis : pip install marker-pdf"
    echo "   (vérifie : source ~/projet_zeta/zeta_env/bin/activate)"
    exit 1
fi

# --- 4. Compteurs pour le bilan final ---------------------------------------
total=0   # PDF trouvés
ok=0      # conversions réussies
skip=0    # PDF déjà convertis (md existant)
fail=0    # échecs

echo "📂 Dossier : $DIR"
echo "🔄 Conversion des PDF en Markdown..."
echo "----------------------------------------------------------------------"

# --- 5. Boucle sur tous les .pdf --------------------------------------------
#   find ... -print0 + read -d '' : robuste même si un nom contient un espace
while IFS= read -r -d '' pdf; do
    total=$((total + 1))

    base="$(basename "$pdf" .pdf)"   # nom sans chemin ni extension
    target_md="$DIR/$base.md"        # fichier .md final attendu

    # 5a. Si le .md existe déjà -> on saute (évite de reconvertir pour rien)
    if [ -f "$target_md" ]; then
        echo "⏭️  Déjà fait  : $base.md (ignoré)"
        skip=$((skip + 1))
        continue
    fi

    echo "▶️  Conversion : $base.pdf"

    # 5b. marker écrit dans un sous-dossier : $DIR/$base/$base.md (+ images)
    #     --output_format markdown : on veut du .md (pas json/html)
    if marker_single "$pdf" --output_dir "$DIR" --output_format markdown >/dev/null 2>&1; then

        produced="$DIR/$base/$base.md"   # emplacement réel produit par marker

        # 5c. On remonte le .md à côté du PDF, avec le même nom
        if [ -f "$produced" ]; then
            mv "$produced" "$target_md"

            # Le sous-dossier $DIR/$base/ peut contenir des images extraites.
            # S'il est vide après le déplacement du .md, on le supprime.
            # (Décommente la ligne suivante pour supprimer AUSSI les images.)
            # rm -rf "$DIR/$base"
            rmdir "$DIR/$base" 2>/dev/null || true   # supprime seulement si vide

            echo "✅ OK         : $base.md"
            ok=$((ok + 1))
        else
            echo "⚠️  marker a tourné mais aucun .md trouvé pour $base"
            fail=$((fail + 1))
        fi
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
