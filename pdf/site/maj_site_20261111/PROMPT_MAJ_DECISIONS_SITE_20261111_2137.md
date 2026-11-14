# PROMPT Claude Code — appliquer les décisions D1, D2, D3 (à lancer APRÈS la décision de hprzeta)

> Préparé à 21:37 à partir de `RAPPORT_OPTIONS_DECISIONS_20261111_2137.md`. **Ne rien exécuter tant que hprzeta n'a pas confirmé chaque décision.** Seules les décisions confirmées sont appliquées.

## Règles
1. Un correctif à la fois, **STOP avant chaque commit, second STOP avant push**, jamais `--force`, wiki et code séparés. Les 3 décisions recommandées ne produisent **aucun commit** (tout est local) ; si hprzeta choisit une autre option qui en demande (ex. D2 c), ces règles s'appliquent.
2. Copie `.bak-AAAAMMJJ` avant toute modification ; aucune suppression.
3. Aucune valeur identifiante dans les messages et rapports (`[IP]`, `[MAC]`, `[EMAIL]`, `fe80::[ID_lien_local]`).
4. Montrer le résultat dans Claude in Chrome (onglet « Mise à jour site ») quand une page publique est concernée ; sinon `git status --short` des deux dépôts.

## D1 — Déplacer `Dossier-md.md` dans `md/` (si confirmé)
`mv ~/projet_zeta/Riemann_Lab.wiki/Dossier-md.md ~/projet_zeta/md/Dossier-md.md` puis `git -C ~/projet_zeta/Riemann_Lab.wiki status --short` : la ligne `?? Dossier-md.md` doit avoir disparu. Facultatif, sur accord : mettre à jour l'« État » du fichier (158 fichiers .md dans md/, 123 PDF dans pdf/, pied daté du jour avec `wc -l`).

## D2 — Laisser le PDF local et régénérer la copie locale (si confirmé)
Archiver l'ancien : `cp -p pdf/optimisation/Voie_b_5/md_to_claude/analyse_math_deficit_2026-08-18.pdf pdf/archive/analyse_math_deficit_2026-08-18.pdf.bak-20261111`, puis régénérer : `bash scripts/build_pdf_riemann_CM.sh Riemann_Lab.wiki/analyse_math_deficit_2026-08-18.md pdf/optimisation/Voie_b_5/md_to_claude/analyse_math_deficit_2026-08-18.pdf`. Contrôle : `pdftotext` → la note du 11/11 et « 97 manquants » présents ; `git status` ne change pas (dossier ignoré). Si hprzeta préfère publier (option c) : copier le PDF régénéré dans `pdf/optimisation/`, commit sur `Riemann_Lab_IA` (STOP), puis `cherry-pick -x` sur `Riemann_Lab_C`, `main`, `Riemann_Lab_Test` (STOP avant chaque push).

## D3 — Exclure `*.bak*` (si confirmé)
Pour le wiki et le dépôt de code : `cp -p <dépôt>/.git/info/exclude <dépôt>/.git/info/exclude.bak-20261111` puis `echo '*.bak*' >> <dépôt>/.git/info/exclude`. Contrôle : `git status --short` des deux dépôts ne liste plus aucun `.bak` (attendu : 26 et 27 lignes en moins) ; `git ls-files | grep -c '\.bak'` = 0.

## Rapport
`RAPPORT_MAJ_DECISIONS_20261111_HHMM.md` + `.pdf` dans `pdf/site/maj_site_20261111/` (tableau de validation, tableau `page | ligne in | ligne out | date heure`), puis rappel : « hprzeta, dépose maintenant le rapport dans le projet SITE ZETA sur claude.ai. »

---
*PROMPT_MAJ_DECISIONS_SITE_20261111_2137.md · hprzeta · 2026-11-11 21:37 · 24 lignes*
