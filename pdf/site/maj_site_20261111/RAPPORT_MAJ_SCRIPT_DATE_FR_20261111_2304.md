# Rapport — date en français dans build_pdf_riemann_CM.sh (11/11/2026)

> Exécuté à 23:04 d'après `PROMPT_MAJ_SCRIPT_DATE_FR_20261111_2310.md`, avec « go correctif », « go commit » et « go push ». Aucun `--force`. Statut : 🟢 ok · 🟡 fait à moitié · 🔴 ko.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Étape 1 : Chrome, onglet « Mise à jour site », état avant | 🟢 | Script sur GitHub (branche Riemann_Lab_IA) : ligne 19 « \date{… \today} » et ligne 53 « Document créé le \today » encadrées ; ligne 9 « export LANG=C.UTF-8 LC_ALL=C.UTF-8 » visible (captures) | — |
| Étape 2 : dossier du jour complété | 🟢 | Rapport d'analyse copié dans pdf/site/maj_site_20261111/ | — |
| Étape 3 : diagnostic | 🟢 | Cause : LC_ALL=C.UTF-8 impose la locale anglaise. Ligne 19 sans effet visible (pandoc 3.1.3 réémet \date{}). Autre script : build_pdf_riemann.sh (l.19 et 39), non modifié. Options testées en dossier temporaire : (a) polyglossia français = 139 lignes de texte changées (tirets longs « — » devenus « --- ») ; (b) date calculée par le shell = pied seul changé. Retenu : (b), sans dépendance à la locale ni aux paquets | — |
| Correctif appliqué (+9 / −3 lignes) | 🟢 | DATE_FR calculée dans le script (noms de mois en dur, « 1er » au premier du mois) ; \today remplacé dans l'en-tête (sed) et dans le pied (argument Python) ; sauvegarde pdf/archive/build_pdf_riemann_CM.sh.bak-20261111 ; bash -n OK ; droits 100755 conservés ; 69 lignes | — |
| Tests en dossier temporaire | 🟢 | (i) analyse_math_deficit_2026-08-18.md sous son vrai nom : 9 pages, note du 11/11 p.1, « 97 manquants » 2, « 84 vraies paires » 1, 0 « November », 0 « [[ » ; (ii) court_test.md : pied « 11 novembre 2026 », accents, guillemets, formule et tableau intacts ; simulation 2026-12-01 « 1er décembre 2026 », 2027-02-01 « 1er février 2027 », 2026-12-31 « 31 décembre 2026 » | — |
| Comparaison avec le PDF publié | 🟢 | Même taille (134 779 octets), 9 pages, texte pdftotext identique, 9 pages identiques pixel par pixel ; seul le sha256 diffère (date de création du fichier : 22:47 / 23:01). PDF publié NON remplacé (il a déjà le bon pied) | — |
| Commit, cherry-pick -x, push (sans --force) | 🟢 | 24ac213 (IA), f21b907 (C), 01ddc94 (main), 7cfb759 (Test) ; sha256 du script identique sur les 4 branches (1e06c9393e70), mode 100755 ; poussé 1 commit par branche, local = origin ; commit sur IA après « go commit », push après « go push » | — |
| Script corrigé sur GitHub (main) | 🟢 | Page main : commit 01ddc94 « now », 69 lignes ; lignes MOIS/JOUR/DATE_FR surlignées ; sed et « python3 - … $DATE_FR » survolés ; pied « '+date_fr+' » présent (captures) | — |
| curl -sIL du script sur main | 🟢 | 302 puis 200, 4 485 octets ; sha256 servi = local (1e06c9393e70) ; occurrences « today » dans le script publié : 2 = le gabarit \date de l'en-tête (remplacé à l'exécution) et la commande sed | — |
| Console GitHub | 🟡 | 1 exception « Error: Na » sur la page GitHub du script (pile « eval at xhr.onreadystatechange »), issue d'un script de la page ou de la traduction automatique de Chrome, pas du dépôt ; aucun message sur le site GitHub Pages | Non reproductible côté dépôt ; à ignorer sauf récurrence |
| Réseau | 🟢 | 130 ressources de la page GitHub : 0 statut ≥ 400 (le statut 0 = requêtes inter-origines opaques) | — |
| Site : non-régression | 🟢 | 59 liens externes en 200 (curl) ; 53 formules, 0 .katex-error ; 0 requête ≥ 400 ; console vide ; pied « mis à jour le 11/11/2026 » | — |
| Audit secrets du diff | 🟢 | Lignes ajoutées : 0 motif (clé, jeton, IP, MAC, e-mail, duckdns, fe80::) | — |
| Autre script build_pdf_riemann.sh (\today l.19 et 39) | 🟡 | Listé, non modifié : pas de réponse de hprzeta sur ce second script | Même correctif possible : à demander |
| .gitignore et monitoring/Monitoring-Runs.md | 🟢 | .gitignore inchangé ; Monitoring-Runs.md non touché (toujours « M », non commité) | Décision .gitignore ligne 30 toujours en attente |

## 2. Tableau de modifications (git diff -U0 réel : `git diff ebd4e14 24ac213`)

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| scripts/build_pdf_riemann_CM.sh (4 branches, 24ac213) | [L8] # Date du pied de page en français (corrigé le 2026-11-11) : DATE_FR calculée dans ce script, sans dépendre de la locale. | — | 2026-11-11 23:02 |
| scripts/build_pdf_riemann_CM.sh (4 branches, 24ac213) | [L11] # Date en français, calculée ici (indépendante de la locale et de LC_ALL=C.UTF-8) : « 1er » pour le premier du mois. ⏎ MOIS=(janvier février mars avril mai juin juillet août septembre octobre novembre | — | 2026-11-11 23:02 |
| scripts/build_pdf_riemann_CM.sh (4 branches, 24ac213) | [L31] sed -i "s/\\\\today/$DATE_FR/" "$WORK/header.tex"   # \date de l'en-tête : date française ⏎ python3 - "$SRC" "$WORK" "$BASE" "$DATE_FR" << 'PY' | [L26] python3 - "$SRC" "$WORK" "$BASE" << 'PY' | 2026-11-11 23:02 |
| scripts/build_pdf_riemann_CM.sh (4 branches, 24ac213) | [L34] src, work, base, date_fr = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] | [L28] src, work, base = sys.argv[1], sys.argv[2], sys.argv[3] | 2026-11-11 23:02 |
| scripts/build_pdf_riemann_CM.sh (4 branches, 24ac213) | [L59]   '{\\small Document créé le '+date_fr+' --- source \\texttt{'+esc+'} --- Riemann\\_Lab --- hprzeta}\n') | [L53]   '{\\small Document créé le \\today{} --- source \\texttt{'+esc+'} --- Riemann\\_Lab --- hprzeta}\n') | 2026-11-11 23:02 |

## 3. Erreurs et réserves

- Surlignage de test sur la page GitHub trop large (tout le fichier) : sans effet sur le dépôt ; la capture « avant/après » montre le surlignage exact.
- Ma prévision « 1 seule occurrence de today » était fausse : 2 attendues (gabarit \date + commande sed).
- Un second script (`build_pdf_riemann.sh`) garde `\today` en attente de votre réponse.
- Aucun prompt de correction additionnel nécessaire.

Captures : `captures/script_avant_ligne53_today_branche_IA.jpg`, `captures/script_avant_ligne19_date_today.jpg`, `captures/script_apres_main_lignes_DATE_FR.jpg`, `captures/script_apres_main_sed_et_python_argument.jpg`.

---
*RAPPORT_MAJ_SCRIPT_DATE_FR_20261111_2304.md · projet SITE ZETA · hprzeta · MAJ 11 novembre 2026 23:04 · 45 lignes*
