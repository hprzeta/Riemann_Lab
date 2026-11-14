# Rapport — date en français dans build_pdf_riemann_CM.sh (11/11/2026)

> Exécuté à 23:12 d'après `PROMPT_MAJ_SCRIPT_DATE_FR_20261111_2310.md`, avec « go correctif », « go commit » et « go push ». Aucun `--force`. Statut : 🟢 ok · 🟡 fait à moitié · 🔴 ko.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Étape 1 : Chrome, onglet « Mise à jour site », état avant | 🟢 | Script sur GitHub (branche Riemann_Lab_IA, 51 lignes) : ligne 19 « \date{… \today} » et ligne 39 « Document créé le \today » encadrées (captures) | — |
| Étape 2 : dossier du jour complété | 🟢 | Rapport d'analyse copié dans pdf/site/maj_site_20261111/ | — |
| Étape 3 : diagnostic | 🟢 | Structure identique au jumeau CM (LC_ALL=C.UTF-8, \date en heredoc, même appel Python, même pied) ; différences sans incidence : xelatex au lieu de lualatex, DejaVu Serif, lecteur gfm. Appelants : usage manuel seulement (mentions dans JOURNAL, Handoff, Arbre, guide local md/script) ; aucun script, alias ni enchaînement | — |
| Correctif appliqué (+9 / −3 lignes) | 🟢 | Même méthode : DATE_FR calculée dans le script (noms de mois en dur, « 1er » au premier du mois) ; \today remplacé dans l'en-tête (sed) et dans le pied (argument Python) ; sauvegarde pdf/archive/build_pdf_riemann.sh.bak-20261111 ; bash -n OK ; droits conservés ; 57 lignes | — |
| Tests en dossier temporaire (ancien vs nouveau) | 🟢 | court_test.md : ancien pied « November 11, 2026 », nouveau « 11 novembre 2026 » ; diff de pdftotext = 1 ligne (le pied) ; corps de la page identique pixel par pixel (600 px sur 702), seul le pied change ; accents, guillemets, tiret long, formules et tableau intacts (rendu vu) ; dates simulées : 2026-12-01 « 1er décembre 2026 », 2027-02-01 « 1er février 2027 », 2026-12-31 « 31 décembre 2026 » | — |
| Aucun PDF publié régénéré ni remplacé | 🟢 | Aucune régénération de PDF suivi ; seul le dossier temporaire a été utilisé | — |
| Commit, cherry-pick -x, push (sans --force) | 🟢 | 844cc46 (IA), 3da9d06 (C), 743f571 (main), 7086605 (Test) ; sha256 du script identique sur les 4 branches (34bcc60c9c16), mode 100755 ; poussé 1 commit par branche, local = origin ; commit après « go commit », push après « go push » | — |
| Script corrigé sur GitHub (main) | 🟢 | Commit 743f571 « maintenant », 57 lignes ; lignes MOIS/JOUR/DATE_FR encadrées en vert ; sed et « python3 - … $DATE_FR » survolés ; pied « '+date_fr+' » présent (captures) | — |
| curl -sIL du script sur main | 🟢 | 302 puis 200, 3 254 octets ; sha256 servi = local (34bcc60c9c16) ; « today » dans le script publié : 2 attendues (gabarit \date + commande sed) | — |
| Console / réseau | 🟢 | Console : 0 message (page GitHub du script, site) ; la page GitHub du script : 128 ressources, 0 statut ≥ 400 (statut 0 = inter-origines opaque) | — |
| Site : non-régression | 🟢 | 59 liens externes en 200 (curl) ; 53 formules, 0 .katex-error ; 0 requête ≥ 400 ; pied « mis à jour le 11/11/2026 » | — |
| Audit secrets du diff | 🟢 | Lignes ajoutées : 0 motif (clé, jeton, IP, MAC, e-mail, duckdns, fe80::) | — |
| Fichiers à ne pas toucher | 🟢 | build_pdf_riemann_CM.sh intact (1e06c9393e70) ; .gitignore inchangé ; monitoring/Monitoring-Runs.md non touché (toujours « M », non commité) | Décision .gitignore ligne 30 toujours en attente |
| Guides locaux (md/script, md/cpmd) et wiki | 🟡 | Ils citent build_pdf_riemann.sh sans parler de la date : rien à corriger | Si vous voulez une mention « date en français » dans les guides, à demander |

## 2. Tableau de modifications (git diff -U0 réel : `git diff 24ac213 844cc46`)

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| scripts/build_pdf_riemann.sh (4 branches, 844cc46) | [L5] # Date du pied de page en français (corrigé le 2026-11-11) : DATE_FR calculée dans ce script, sans dépendre de la locale. | — | 2026-11-11 23:10 |
| scripts/build_pdf_riemann.sh (4 branches, 844cc46) | [L8] # Date en français, calculée ici (indépendante de la locale et de LC_ALL=C.UTF-8) : « 1er » pour le premier du mois. ⏎ MOIS=(janvier février mars avril mai juin juillet août septembre octobre novembre | — | 2026-11-11 23:10 |
| scripts/build_pdf_riemann.sh (4 branches, 844cc46) | [L27] sed -i "s/\\\\today/$DATE_FR/" "$WORK/header.tex"   # \date de l'en-tête : date française | — | 2026-11-11 23:10 |
| scripts/build_pdf_riemann.sh (4 branches, 844cc46) | [L29] python3 - "$SRC" "$WORK" "$BASE" "$DATE_FR" << 'PY' | [L23] python3 - "$SRC" "$WORK" "$BASE" << 'PY' | 2026-11-11 23:10 |
| scripts/build_pdf_riemann.sh (4 branches, 844cc46) | [L31] src, work, base, date_fr = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] | [L25] src, work, base = sys.argv[1], sys.argv[2], sys.argv[3] | 2026-11-11 23:10 |
| scripts/build_pdf_riemann.sh (4 branches, 844cc46) | [L45]   '{\\small Document créé le '+date_fr+' --- source \\texttt{'+esc+'} --- Riemann\\_Lab --- hprzeta}\n') | [L39]   '{\\small Document créé le \\today{} --- source \\texttt{'+esc+'} --- Riemann\\_Lab --- hprzeta}\n') | 2026-11-11 23:10 |

## 3. Erreurs et réserves

- Chrome traduit le code à l'écran (« \aujourd'hui » pour today) : sans effet sur le dépôt.
- Aucune erreur sur ce correctif.
- Les deux scripts de génération de PDF sont maintenant corrigés.
- Aucun prompt de correction additionnel nécessaire.

Captures : `captures/script2_avant_ligne39_today_branche_IA.jpg`, `captures/script2_avant_ligne19_date_today.jpg`, `captures/script2_apres_main_lignes_DATE_FR.jpg`, `captures/script2_apres_main_sed_et_python_argument.jpg`.

---
*RAPPORT_MAJ_SCRIPT2_DATE_FR_20261111_2312.md · projet SITE ZETA · hprzeta · MAJ 11 novembre 2026 23:12 · 45 lignes*
