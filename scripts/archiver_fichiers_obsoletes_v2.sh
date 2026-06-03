#!/bin/bash
# =============================================================================
# archiver_fichiers_obsoletes_v2.sh
# Déplace les fichiers obsolètes vers ~/projet_zeta/docs/archive/
# Version 2 — après analyse de index.html
# Date : 29 mai 2026 — Riemann_Lab / hprzeta
# =============================================================================
#
# FICHIERS PROTÉGÉS (utilisés par le site web) :
#   index.html          → page principale du site
#   animation_theta.html → lien direct depuis index.html (3 fois !)
#   docs/images/T1000_V2/zeros_zeta_T10000_20260424_205325.png → raw GitHub
#   docs/csv/T1000_V2/zeros_zeta_T10000_20260424_205325.csv   → raw GitHub
#
# Ces fichiers ne sont PAS déplacés.
# =============================================================================

PROJET=~/projet_zeta
ARCHIVE=$PROJET/docs/archive
SRC=$PROJET/src/calculs

echo "=== Archivage v2 — fichiers site protégés ==="
echo "Destination : $ARCHIVE"
echo ""

mkdir -p $ARCHIVE/python_obsoletes
mkdir -p $ARCHIVE/csv_anciens
mkdir -p $ARCHIVE/scripts_shell

# =============================================================================
# 1. Scripts Python obsolètes
# =============================================================================
echo "--- Scripts Python obsolètes ---"
PYTHON_FILES=(
    "compute_zeros_v1.py"
    "compute_zeros_v2.py"
    "compute_zeros_test_error1.py"
    "compute_zeros_test_error1_corr1.py"
    "compute_zeros_test_error2.py"
    "zeros_finder.py"
    "calcul_zeta.py"
    "demo_complete.py"
    "verification.py"
    "factorielle__gamma__zeta_.py"
    "prng_zeta_aleatoire.py"
    "ia_zeta.py"
    "config_loader.py"
    "config_loader1.py"
    "plots.py"
    "logger_config.py"
    "cpu_temp_monitor.py"
)

for f in "${PYTHON_FILES[@]}"; do
    found=$(find $PROJET/src -name "$f" 2>/dev/null | head -1)
    if [ -n "$found" ]; then
        mv "$found" $ARCHIVE/python_obsoletes/
        echo "  ✅ $f → archive/python_obsoletes/"
    else
        echo "  ⚠️  $f non trouvé — ignoré"
    fi
done

# =============================================================================
# 2. Fichiers CSV anciens (runs partiels)
# =============================================================================
echo ""
echo "--- Fichiers CSV anciens ---"
CSV_FILES=(
    "zeros_zeta_T40_20260421_190235.csv"
    "riemann_zeros.csv"
    "zeros_intermediaire.csv"
    "resultats_zeta.csv"
    "zeros_partiels_206.csv"
    "zeros_zeta_final.csv"
    "gpu_info.csv"
)

for f in "${CSV_FILES[@]}"; do
    found=$(find $PROJET -name "$f" -not -path "*/archive/*" 2>/dev/null | head -1)
    if [ -n "$found" ]; then
        mv "$found" $ARCHIVE/csv_anciens/
        echo "  ✅ $f → archive/csv_anciens/"
    else
        echo "  ⚠️  $f non trouvé — ignoré"
    fi
done

# =============================================================================
# 3. Scripts shell — setup terminé
# =============================================================================
echo ""
echo "--- Scripts shell obsolètes ---"
SHELL_FILES=(
    "install_zeta_complete.sh"
    "setup_ollama_final.sh"
    "run_computation.sh"
    "monitor2.sh"
)

for f in "${SHELL_FILES[@]}"; do
    found=$(find $PROJET -name "$f" -not -path "*/archive/*" 2>/dev/null | head -1)
    if [ -n "$found" ]; then
        mv "$found" $ARCHIVE/scripts_shell/
        echo "  ✅ $f → archive/scripts_shell/"
    else
        echo "  ⚠️  $f non trouvé — ignoré"
    fi
done

# =============================================================================
# 4. Fichiers divers
# =============================================================================
echo ""
echo "--- Fichiers divers ---"
DIVERS_FILES=(
    "IA_tools.txt"
    "zeros_config1.yaml"
    "zeros_zeta.log"
)

for f in "${DIVERS_FILES[@]}"; do
    found=$(find $PROJET -name "$f" -not -path "*/archive/*" 2>/dev/null | head -1)
    if [ -n "$found" ]; then
        mv "$found" $ARCHIVE/
        echo "  ✅ $f → archive/"
    else
        echo "  ⚠️  $f non trouvé — ignoré"
    fi
done

# =============================================================================
# Résumé
# =============================================================================
echo ""
echo "=== Résumé ==="
echo "Fichiers archivés :"
find $ARCHIVE -type f -newer $ARCHIVE -o -type f | grep -v "^$ARCHIVE$" | sort | sed "s|$ARCHIVE/|  |"
echo ""
echo "=== FICHIERS PROTÉGÉS (non touchés) ==="
echo "  🔒 docs/index.html               ← page principale site"
echo "  🔒 docs/animation_theta.html     ← lié 3x dans index.html"
echo "  🔒 docs/images/T1000_V2/*.png    ← raw GitHub dans index.html"
echo "  🔒 docs/csv/T1000_V2/*.csv       ← raw GitHub dans index.html"
echo ""
echo "✅ Terminé — rien supprimé, tout déplacé dans docs/archive/"
