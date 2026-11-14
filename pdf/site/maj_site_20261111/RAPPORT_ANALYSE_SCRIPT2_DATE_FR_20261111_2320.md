# Rapport d'analyse — date en français dans build_pdf_riemann.sh (11/11/2026 23:20)

> Analyse sur claude.ai d'après `RAPPORT_MAJ_SCRIPT_DATE_FR_20261111_2304.md` (lu en entier : tout 🟢 sauf l'exception console GitHub « Error: Na », hors dépôt). Aucune modification. Accord de hprzeta : corriger aussi `build_pdf_riemann.sh`.

## Constats
- `build_pdf_riemann_CM.sh` corrigé et publié sur les 4 branches (24ac213, f21b907, 01ddc94, 7cfb759), sha256 identique.
- `build_pdf_riemann.sh` garde `\today` (l.19 et 39) : même défaut, même correctif prévu.
- Aucun PDF publié n'est à régénérer.
- `.gitignore` ligne 30 : décision toujours en attente.

## Tableau de modifications prévues (À FAIRE)
| page | ligne in | ligne out | date heure |
|---|---|---|---|
| scripts/build_pdf_riemann.sh (4 branches) en-tête | bloc MOIS/JOUR/DATE_FR ; sed remplaçant \today dans l'en-tête | — | À FAIRE |
| scripts/build_pdf_riemann.sh l.19 (\date) | \date{… DATE_FR via sed} | \date{… \today} | À FAIRE |
| scripts/build_pdf_riemann.sh l.39 (pied) | Document créé le '+date_fr+' | Document créé le \today{} | À FAIRE |
