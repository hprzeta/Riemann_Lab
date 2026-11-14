# Rapport d'analyse — date en français dans build_pdf_riemann_CM.sh (11/11/2026 23:10)

> Analyse sur claude.ai d'après `RAPPORT_MAJ_FIABILITE_PDF_20261111_2254.md` (lu en entier). Aucune modification. Accord de hprzeta : corriger le script.

## Constats
- Cause : `\today` (lignes 19 et 53) sort la date en anglais ; le PDF publié a été généré avec une copie temporaire du script, donc la prochaine régénération repassera en anglais.
- Le PDF publié est déjà correct (pied en français) : il ne doit pas être remplacé.
- Hors périmètre, en attente de décision de hprzeta : `.gitignore` ligne 30 (`!.claude/skills/**`) ré-inclut les `.bak` du dossier skills.

## Tableau de modifications prévues (À FAIRE)
| page | ligne in | ligne out | date heure |
|---|---|---|---|
| scripts/build_pdf_riemann_CM.sh (4 branches) l.19 | date française (langue du moteur ou date shell injectée) | \today | À FAIRE |
| scripts/build_pdf_riemann_CM.sh (4 branches) l.53 | date française (idem) | \today | À FAIRE |
| autres scripts avec \today | À déterminer (étape 3), non modifiés sans accord | idem | À DÉCIDER |
