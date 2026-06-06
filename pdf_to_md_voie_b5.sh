#!/bin/bash
# pdf_to_md_voie_b5.sh
# Convertit les PDFs de Voie_b_5 en .md et les place dans md_to_claude/
# Auteur: hprzeta — MAJ: 2026-06-03

SRC=~/projet_zeta/pdf/optimisation/Voie_b_5
DST=$SRC/md_to_claude

mkdir -p "$DST"

echo "=== Conversion PDF → MD pour Voie_b_5 ==="
echo "Source : $SRC"
echo "Dest   : $DST"
echo ""

# Mapping PDF → nom MD final (ordre vu dans le gestionnaire de fichiers)
declare -A MAP=(
  ["1-rapport_zeta_riemann_exploration_numerique_IA_hprzeta.pdf"]="1_pave1-rapport_zeta_riemann_exploration_numerique_IA_hprzeta.md"
  ["2-solution_experimental_zeta.pdf"]="2_pave1-solution_experimental_zeta.md"
  ["3-recovery_zeta.pdf"]="3_pave1-recovery_zeta.md"
  ["4-cerveau_autonome_zeta.pdf"]="4_pave1-cerveau_autonome_zeta.md"
  ["5-resume_recuperation_git_systeme_hprzeta.pdf"]="5_pave1-resume_recuperation_git_systeme_hprzeta.md"
  ["01_cartographie_diagnostic_riemann_lab_v1_C.pdf"]="6_01_pave1-cartographie_diagnostic_riemann_lab_v1_C.md"
  ["02_plan_migration_recovery_brainvault_rag_v1_C.pdf"]="6_02_pave1-plan_migration_recovery_brainvault_rag_v1_C.md"
  ["03_checklist_systeme_linux_hprzeta_v1_C.pdf"]="6_03_pave1-checklist_systeme_linux_hprzeta_v1_C.md"
  ["9-methode_scripts_post_audit_et_remarques_materiel_hprzeta.pdf"]="7_pave1-methode_scripts_post_audit_et_remarques_materiel_hprzeta.md"
  ["10-complement_methode_git_priorites_phase3_hprzeta.pdf"]="8-pave1-complement_methode_git_priorites_phase3_hprzeta.md"
  ["09_synthese_journee_phase_c_v4_voie_b_illinois_pur.pdf"]="09_pave1-synthese_journee_phase_c_v4_voie_b_illinois_pur.md"
  ["10-resume_9_pdf_et_prompt_claude_code_phase_c_voie_b_v5.pdf"]="11_pave1-resume_9_pdf_et_prompt_claude_code_phase_c_voie_b_v5.md"
  ["07_pave_primalite_zeta_riemann_lab.pdf"]="12_pave2-primalite_zeta_riemann_lab.md"
  ["08_pilier_cryptozeta_cybersecurite_cryptographie_moderne.pdf"]="13_pave3-cryptozeta_cybersecurite_cryptographie_moderne.md"
)

OK=0
FAIL=0

for PDF in "${!MAP[@]}"; do
  MD="${MAP[$PDF]}"
  SRC_PDF="$SRC/$PDF"
  DST_MD="$DST/$MD"

  if [ ! -f "$SRC_PDF" ]; then
    # Essayer une recherche insensible à la casse
    FOUND=$(find "$SRC" -maxdepth 1 -iname "$PDF" 2>/dev/null | head -1)
    if [ -z "$FOUND" ]; then
      echo "❌ INTROUVABLE : $PDF"
      ((FAIL++))
      continue
    fi
    SRC_PDF="$FOUND"
  fi

  echo -n "→ $PDF ... "
  # Extraction texte via pdftotext
  pdftotext -layout "$SRC_PDF" /tmp/_tmp_extract.txt 2>/dev/null

  if [ -s /tmp/_tmp_extract.txt ]; then
    # Entête MD
    {
      echo "> **Fichier :** $MD · **Dossier :** wiki inbox-ia"
      echo "> **Auteur :** hprzeta · **MAJ :** $(date +%Y-%m-%d)"
      echo ""
      echo "---"
      echo ""
      cat /tmp/_tmp_extract.txt
      echo ""
      echo "---"
      echo "*$MD · inbox-ia · hprzeta · MAJ $(date +%Y-%m-%d)*"
    } > "$DST_MD"
    echo "✅ $(wc -l < "$DST_MD") lignes"
    ((OK++))
  else
    echo "⚠️  PDF scanné ou vide — extraction vide"
    ((FAIL++))
  fi
done

rm -f /tmp/_tmp_extract.txt

echo ""
echo "=== Résultat : $OK OK · $FAIL échecs ==="
echo "Fichiers générés dans : $DST"
ls -la "$DST"
