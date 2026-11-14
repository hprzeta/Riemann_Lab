# Rapport de test — mise à jour du site du 11/11/2026 (lecture seule, 2e passe)

> Réalisé le 11/11/2026 à 20:49 par Claude Code (Chrome + shell), d'après `PROMPT_TEST_MAJ_SITE_20261111_2036.md`. Aucun fichier du dépôt ni du wiki modifié, aucun commit. Statut : 🟢 ok · 🟡 fait à moitié · 🔴 pas fait ou ko.
> Onglet Chrome renommé « Recherche MAJ site ». Suivi de la console lancé avant le premier chargement du site.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| S1 Frise V1→V17 : tuile « V17 ✦ » après « v16 ✦ » | 🟢 | Vu à l'écran (défilement, survol de la tuile, capture) ; DOM : 1 tuile « V17 ✦ », 1,84m · PC1+PC2 · 2 min 40 s PC1 seul · 03/11/2026 | — |
| S2 Titre de la section perfs | 🟢 | Vu à l'écran + texte DOM : « 1,6 min en v16 (PC1, turbo, 08/08/2026) · 1,84 min en V17 distribué PC1+PC2, 2 min 40 s sur PC1 seul (03/11/2026) · V17 ⭐ » ; plus de « V16 ⭐ » | — |
| S3 Bandeau, stats, ligne V17 du tableau | 🟢 | DOM : « V17 en production (03/11/2026) », 10 016 474, 5 000 000, « Turing complet ». Le mot « livrée » n'existe pas dans la page ; la ligne V17 est bien là (« En production depuis le 03/11/2026 », lien v16→v17 PDF) | Libellé du prompt (« livrée ») ≠ texte réel : sans conséquence |
| S4 Bloc T=5M, cartes cluster, gain | 🟢 | Vu à l'écran : 97 manquants = 84 vraies paires + 13 isolés ; 10 016 377 + 97 = 10 016 474. Cartes : PC1 16 GB, PC2 7.6 GB, PC3 5.7 GB (écrits « GB » avec point décimal) ; « ×7 490 » lu | — |
| S5 12 animations, 4 nouvelles ouvertes, curseur, formules | 🟢 | 12 liens animation_*.html. Les 4 ouvertes : gaps_gue (STEP 0,100→0,030, risque 1,1 %→0,1 %), illinois_adaptatif (t 77 000→7 500, gain ×4,68), ntermes_rs (t 10 000→84 100, N_termes 39→115), prec_mpfr (64→204 bits, 4 limbs, SIMD NON). .katex : 11 / 21 / 7 / 8 ; .katex-error : 0 ; texte brut \( ou $$ : 0 | Observation à confirmer : libellé de l'axe vertical de la courbe de gaps_gue peu lisible à cette taille d'écran |
| S6 Pied de page | 🟢 | DOM : « novembre 2026 · mis à jour le 11/11/2026 » | — |
| W1 Structure-Projet-Complet | 🟢 | Vu à l'écran : compute_zeros_v17.py « ⭐ ACTIF » (arborescence) + tableau des rôles ; v4_1 « historique » | — |
| W2 Configuration-Materielle-Logicielle | 🟢 | Vu à l'écran : « 5 partitions … mesuré le 11/11/2026 » ; DOM : « 8 workers depuis v10 ; 4 jusqu'à v9 » | — |
| W3 Plancher-Hardware-Architecture | 🟢 | Vu à l'écran (encadré au §4) ; DOM : 3 encadrés « État de juin 2026, dépassé depuis v16… » (§4, §5, §6) | — |
| W4 Animations : colonne Cours associé | 🟢 | DOM + capture : gaps = niveau-5-expert, illinois_adaptatif et ntermes_rs = niveau-4-zeta ; prec_mpfr = « — » (point connu CONFIRMÉ) | prec_mpfr : proposition niveau-4-zeta, à valider (voir prompt de correction) |
| W5 Home, Etape-1, Roadmap, Projet-Zêta | 🟢 | Vus à l'écran un par un. Occurrences « V17 » : Home 12, Etape-1 14, Roadmap 5. Projet-Zêta = « page déplacée » (redirection vers l'accueil) | — |
| 3c PDF sur main (note du 11/11 en page 1) | 🟡 | git ls-tree origin/main : les 2 PDF présents ; pdftotext page 1 : 2 occurrences « 11/11/2026 » chacun ; analyse_problemes_v13_v15.pdf ouvert dans Chrome (viewer GitHub, branche main, 129 Ko) | analyse_problemes_v1_v16.pdf non ouvert dans Chrome (vérifié seulement par pdftotext) |
| V1 Liens externes de docs/index.html | 🟡 | 59 liens uniques extraits, curl -L : 59 × HTTP 200, 0 échec | Un clic à la main par section non fait ; liens ouverts dans Chrome : animations, wiki, PDF |
| V2 Formules (KaTeX) | 🟢 | Site, 4 animations, pages wiki W1–W5 : 0 .katex-error, 0 texte brut \( ou $$ non rendu | — |
| V3 Console et requêtes en échec | 🟡 | Suivi console lancé AVANT le 1er chargement du site : 0 message sur site et 4 animations. 2 erreurs « Oversized browser stats delivery failed » viennent de github.githubassets.com (télémétrie GitHub, pages wiki), pas du code du dépôt. Réseau (suivi démarré au dernier rechargement) : 16 requêtes, toutes 200 | Le suivi réseau n'a pas couvert les animations ni le wiki (limite de l'outil : démarre au 1er appel) |
| V4 Secrets / identifiants (site, docs/, pdf/site/, wiki) | 🟢 | 150 fichiers texte suivis. E-mails autres que l’adresse publique du projet [EMAIL] : 0. duckdns : mentions du nom du service dans docs/archive/ ; 3 pages wiki citent l'URL publique [DDNS_PC4]/update (aucun sous-domaine personnel, jeton en variable). PRIVATE KEY, ghp_, github_pat_ : 0. IPv4 : wiki = 2 DNS publics + 1 masque 255.x + 5 locales (127.x / 0.0.0.0). MAC : 0 dans le texte. docs/images/T10Demo/*.html = bibliothèque JS minifiée (faux positifs « Token= », IPv4, MAC) | Les 84 motifs IPv4 de T10Demo (JS minifié) non vérifiés un à un |
| V5 Adresse lien-local EUI-64 dans le wiki | 🔴 | CONFIRMÉ : 1 seule occurrence, JOURNAL.md ligne 3446 (fe80::[MASQUÉ dans ce rapport]) ; 0 ailleurs (wiki, docs/, pdf/site/) | À masquer dans JOURNAL.md (hors test lecture seule) : voir prompt de correction |
| V6 Historique git : ancienne adresse yahoo | 🟢 | git log --all --oneline -S'yahoo' : 0 commit dans le dépôt ET dans le wiki (après git fetch). Rien à purger | — |
| V7 Synchro des 4 branches | 🟢 | docs/ identique : IA vs main, C, Test = 0 fichier différent (origin). Commits du jour : IA 11, main/C/Test 9 chacune. Wiki : master = origin/master (c53eb42) | La liste « absents » par hash est trompeuse (cherry-picks, hashes différents) ; équivalence confirmée sur docs/, pas commit par commit |
| V8 Occurrences obsolètes restantes | 🟡 | « ACTIF » avec v4_1 : 0 · « 908 Go » : 0 · « v16 version courante » : 0 · « 96 manquants » : seulement en contexte v13/juin (Handoff 771/823, Etape-1 18/523/525, analyse_*) · « 4 workers » : contextes historiques (Plancher:80, Phase-C-v4:72, Animations:130/157, Etape-1:161, maths_v7:42, session_20260606, Bibliotheques:595/604, Structure:170 qui précise « 8 depuis v10 ») | STACK.md ligne 344 : « 8 animations » à passer à 12 (périmé) |
| V9 Dates de pied de page | 🟡 | 10 pages wiki testées : pied = 11 novembre 2026 / 2026-11-11 ; compteurs de lignes = lignes réelles (ex. Structure 244, Plancher 288, Home 169) ; docs/index.html « mis à jour le 11/11/2026 » | Arbre_dossiers_projet.md : pied sans compteur de lignes (168 lignes réelles) : mineur |
| Hors liste : analyse_math_deficit_2026-08-18.pdf | 🔴 | git ls-files : non suivi ; existe en local dans pdf/optimisation/Voie_b_5/md_to_claude/ | Décision de hprzeta : publier ou non (pas un correctif) |
| Hors liste : traduction automatique de Chrome | 🟡 | Sur les pages wiki, le texte affiché dit « membres » et « Plancher » alors que le dépôt dit « limbs » (Animations.md l.25, l.178) : traduction du navigateur, pas une erreur du dépôt | Aucun (information) |

## 2. Tableau de modifications

Lignes **in** = ajoutées (vert dans le PDF) · **out** = supprimées (rouge). Repris du rapport d'analyse du 11/11 20:36, contrôlé contre ce qui a été constaté.

| page | ligne in | ligne out | date heure | contrôle |
|---|---|---|---|---|
| docs/index.html (b0b9975) | [L1201] Performances — … 1,6 min en v16 (PC1, turbo, 08/08/2026) · 1,84 min en V17 distribué PC1+PC2, 2 min 40 s sur PC1 seul (03/11/2026) · V17 ⭐ ; [L1498-1502] tuile « V17 ✦ » 1,84m | [L1201] Performances — … 1.6 min à T=100 000 · v16 ⭐ | 2026-11-11 19:43 | constaté S1, S2 |
| CLAUDE.md (b0b9975) | [L299] règle « Claude in Chrome toujours ouvert sur la page modifiée » ; [L327] pied 327 lignes | [L326] pied 326 lignes | 2026-11-11 19:43 | non testé (fichier dépôt) |
| scripts/zeta_diag_publier.sh (b0b9975) | [L2][L14] filtre e-mail → [EMAIL] | [L2] « sans IP ni MAC » | 2026-11-11 19:43 | non testé |
| Animations.md (wiki c53eb42) | [L22-24] cours associés niveau-5-expert / niveau-4-zeta ×2 | [L22-24] « — » ×3 | 2026-11-11 19:44 | constaté W4 |
| Structure-Projet-Complet.md (wiki) | [L47-49][L165-166] compute_zeros_v17.py ⭐ ACTIF ; v4_1 historique ; [L170] 8 depuis v10 | [L47][L164][L168] v4_1 ⭐ ACTIF ; 4 workers | 2026-11-11 19:44 | constaté W1 |
| Configuration-Materielle-Logicielle.md (wiki) | [L17] 5 partitions mesurées ; [L94] 8 workers depuis v10 ; 4 jusqu'à v9 ; [L2] MAJ 2026-11-11 | [L17] 3 partitions ≈ 908 Go ; [L94] 4 workers ; [L2] MAJ 2026-06-13 | 2026-11-11 19:44 | constaté W2 |
| Plancher-Hardware-Architecture.md (wiki) | [L108][L155][L176] encadrés « État de juin 2026, dépassé… » (§4, §5, §6) | [L2] MAJ 2026-06-13 | 2026-11-11 19:44 | constaté W3 |
| Arbre_dossiers_projet.md (wiki) | [L123] v4_1 « historique, remplacé par la V17 » | [L123] v4_1 « ACTIF » | 2026-11-11 19:44 | grep V8 : plus d'ACTIF v4_1 |
| Guide-Linux-Commandes.md / JOURNAL.md (wiki) | [IP_PC4], [IPv6_PC4], [IP_DNS1], [IP_DNS2] (adresses masquées) | adresses en clair (3 valeurs) | 2026-11-11 19:44 | grep V4 : aucune adresse privée restante |
| Handoff.md (wiki) | [L82] À FAIRE : mesurer la V17 sur PC1 seul avec turbo | — | 2026-11-11 19:44 | lu au « point projet » |
| Animations.md (wiki) — À FAIRE | [L25] / Précision mpfr & limbs / … / [[niveau-4-zeta]] / (proposition) | [L25] « — » | À FAIRE | constaté : encore « — » |
| JOURNAL.md (wiki) — À FAIRE | [L3446] fe80::[ID_lien_local] (proposition) | [L3446] adresse lien-local dérivée d'une MAC | À FAIRE | constaté : encore en clair |
| STACK.md (wiki) — À FAIRE (nouveau) | [L344] « 12 animations HTML » (proposition) | [L344] « 8 animations HTML » | À FAIRE | trouvé par ce test (V8) |

## 3. Erreurs rencontrées

- Liens : 0 erreur (59/59 en 200).
- Formules : 0 erreur KaTeX (site, 4 animations, pages wiki W1–W5).
- Console : 0 message du site et des animations ; 2 erreurs de télémétrie GitHub (github.githubassets.com) sur les pages wiki, hors dépôt.
- Réseau : 16 requêtes du site, toutes 200 ; animations et wiki non couverts par le suivi réseau (limite de l'outil).
- Reste à corriger : JOURNAL.md l.3446 (adresse lien-local) ; Animations.md l.25 (cours de prec_mpfr) ; STACK.md l.344 (« 8 animations ») ; pied d'Arbre_dossiers_projet.md (mineur).
- Décision de hprzeta : publication ou non de analyse_math_deficit_2026-08-18.pdf.

Captures (nouveaux fichiers) : `captures/test2036_site_frise_tuile_V17.jpg`, `captures/test2036_pdf_main_analyse_v13_v15.jpg`.

Prompt de correction rechargeable : `PROMPT_CORRECTION_MAJ_SITE_20261111_2049.md`.

Aucun fait inventé : chaque ligne indique sa méthode. Aucun secret recopié (valeurs remplacées par [MASQUÉ], [EMAIL], [HOTE]).

---
*RAPPORT_TEST_MAJ_SITE_20261111_2049.md · projet SITE ZETA · hprzeta · MAJ 2026-11-11 20:49 · 70 lignes*
