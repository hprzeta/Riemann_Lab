# HANDOFF SITE — 12/11/2026

## État
Test automatique de mise à jour du site **installé et activé** sur PC1 (minuterie utilisateur `zeta-test-maj.timer`, 10 min après l'ouverture de session puis toutes les 3 h, au plus un test par jour, seulement si un commit a été publié). Lecture seule, 0 commit, 0 push.

## Fichiers (locaux, hors dépôt)
`~/.local/bin/zeta_test_maj_site.sh` · `~/.config/systemd/user/zeta-test-maj.{service,timer}` · état dans `~/.local/state/zeta_test_maj/` · prompt du test : `src/ia/prompts/PROMPT_TEST_AUTO_MAJ_SITE.md`.

## À savoir
- La commande utilise `--setting-sources user` : sans cela, les hooks locaux du projet (Stop, SessionStart) faussent le rapport et relancent le turbo.
- Un rapport de moins de 400 octets ou contenant « Prêts à déposer… » est refusé (code 99) et le test sera retenté.
- Les rapports sortent dans `pdf/site/maj_site_AAAAMMJJ/` et sont copiés dans `A_DEPOSER/`.

## Corrections du 12/11/2026 (publiées)
- 3 commits poussés sur les 4 branches, sans `--force` : bandeau du site (deux totaux, `2ba709c` sur la branche IA), pied de `docs/V17.md` (`b695b15`), pied de `README.md` (`67db8f9`). Détail et hashes des 4 branches : `RAPPORT_MAJ_CORRECTIONS_TEST_AUTO_20261112_0126.md`.
- Site en ligne vérifié : 43 liens en 200, 0 erreur KaTeX, console vide, 0 requête ≥ 400.
- Le nouveau `PROMPT_TEST_AUTO_MAJ_SITE.md` est en place ; la minuterie l'utilisera au prochain test réel (demain).

## D12, D11, D10 (12/11/2026, publiés à 02:0x)
- 3 commits sur les 4 branches (cherry-pick -x), sans `--force`, local = origin : IA `2b6edc0`, C `40ce140`, main `f77ef4c`, Test `2e2ffb1`. `docs/index.html` identique (SHA-256 `32b16477…`). Détail : `RAPPORT_MAJ_SITE_D10_D12_20261112_0206.md`.
- D12 : bandeau raccourci (1 ligne sur ordinateur, 3 à 390 px). D10 : les deux phrases « gain non mesurable » reprennent `V17.md` l. 18 (mesure du 07/11, déficit fabriqué).
- D11 : `.eq-scroll` n'était pas la cause (clippé par `.eq-band`). Corrigés en CSS mobile : `.links-grid` (style inline), tableau l. 1504, `.cours-grid`, grille inline à 5 colonnes. `scrollWidth` = `clientWidth` à 390 px.
- Sauvegarde avant : `pdf/archive/index.html.bak-202611120156`.

## Wiki D10 et site D13 (12/11/2026, publiés)
- Wiki (`master`) : `f481583`, ligne 507 de `Etape-1-Calcul-des-zéros-non-triviaux.md` alignée sur `V17.md` l. 18, pied « 12 novembre 2026 (phrase du rescan alignée sur V17.md) — 532 lignes ». Poussé sans `--force`.
- Site D13 : la longue phrase de la l. 1768 est remplacée par le texte court avec lien `V17.md` (200). Commits : IA `abb7e96`, C `f142a5c`, main `9b1035c`, Test `fa85f7e` ; `docs/index.html` identique (SHA-256 `efa1a7fe…`), GitHub Pages à jour. Détail : `RAPPORT_MAJ_WIKI_D10_20261112_0222.md`.
- Sauvegardes avant : `pdf/archive/Etape-1-Calcul-des-zeros-non-triviaux.md.bak-202611120217`, `pdf/archive/index.html.bak-202611120217`.

## Restes D14, D15, D16 (12/11/2026, publiés ~13:50)
- Wiki (`master`) : `2a93821`, ligne 532 de `Etape-1-…` réordonnée (12/11 en tête, 532 lignes). Site D15 : classe `grid5` (l. 1438 + CSS l. 567) ; IA `ac54d06`, C `f9aa7c2`, main `c685d52`, Test `260ff13`, `docs/index.html` identique (SHA-256 `aa29c369…`). Sans `--force`, local = origin.
- D16 : 31 ancres, 31 cibles trouvées, 0 morte (`Formation-Zeta-HR#chN` = `<a name>` et non `id`). Site en ligne : 32 URL en 200, 49 requêtes sans erreur, console vide, 0 erreur KaTeX, 390 px sans débordement. Détail : `RAPPORT_MAJ_SITE_RESTES_20261112_1349.md`.
- Sauvegardes : `pdf/archive/Etape-1-Calcul-des-zéros-non-triviaux.md.bak-202611121344`, `pdf/archive/index.html.bak-202611121345`.
- Limite : le défilement réel vers une ancre n'est pas démontrable avec l'outil de navigation.

## D17 liens « Lire → » (12/11/2026, publié ~14:15)
- Cause prouvée : GitHub réécrit `<a name="chN">` en `user-content-chN` ; l'ancien `#chN` ne trouve aucun élément (`scrollY` 0). Nos commits ne sont pas en cause.
- 14 liens passés à `#user-content-chN` : IA `c76af4a`, C `a230756`, main `9bdd205`, Test `da175bc`, SHA-256 identique (`e082fece…`). Détail : `RAPPORT_CORRECTION_ANCRES_FORMATION_20261112_1531.md`.
- **CORRECTION 15:40 : D17 = 🔴 NON RÉSOLU.** hprzeta arrive sur la page Formation-Zeta-HR mais EN HAUT (ch2, 5, 11) et doit défiler à la main. Critère de réussite : titre du chapitre visible sans défiler (réponse C). Suite en cours : `PROMPT_CORRECTION_ANCRES_CHAPITRE_20261112_1536.md`.

## D17 résolu — une page wiki par chapitre (12/11/2026, publié ~17:50)
- hprzeta : « Lire → » arrive sur le titre du chapitre (réponse C, globale). Sommaire du wiki : OK.
- Wiki : `Formation-Zeta-HR` = sommaire ; 14 pages `Formation-Zeta-HR-Ch01` … `Ch14` (commits `13528e2`, `829c297`, `b7d7b9f`). 542 lignes utiles retrouvées à l'identique ; 73 `$$` avant et après.
- Site : 14 liens vers ces pages ; IA `a07a331`, C `c0e989e`, main `5169d67`, Test `0192cae` ; SHA-256 identique (`d4106536…`).
- Erreur corrigée : W1 (taille fixe des images) déformait les 14 images (`13528e2`) ; retirée par `829c297`.
- À savoir : `cours/make_wiki_page.py` génère encore l'ancienne page unique et l'écraserait ; l'ancien contenu en page unique n'existe plus.
- Détail : `RAPPORT_CORRECTION_ANCRES_CHAPITRE_20261112_1804.md`.

## Prochaine action
À décider par hprzeta (rien d'engagé) :
1. Décider si `cours/make_wiki_page.py` doit être adapté à la structure en 14 pages ; contrôle sur un vrai téléphone.
2. Captures encadrées « avant / après » de meilleure qualité (celles de `captures/wd10_*` cadrent mal la ligne 507).
3. Message du commit D11 un peu inexact (cite `.eq-scroll`) : à laisser tel quel, déjà poussé.

---
*HANDOFF_SITE_20261112.md · 12/11/2026 · 56 lignes*

## Audit complet des liens (prompt 18h12) — REPRENDRE ICI
- Étape 0 adaptée : pas de zip, prompt copié dans `src/ia/prompts/` et dans ce dossier ; rapport d'analyse en PDF seul.
- Phase 1 faite : `audit/liens.csv` (849 liens, 332 URL distinctes) via `audit/phase1_inventaire.py`.
- Phase 2 en cours/lancée : `audit/phase2_test.py` → `audit/liens_statut.csv` (journal `audit/phase2.log`).
- Reste : phase 3 (défilement Chrome, onglet « Audit liens », échantillon A/B/C), phase 4 (STOP « go archive »), phase 5 (recensement noms), phase 6 (STOP « go correction »), rapport.
- Aucun commit, aucun renommage, aucune modification de fichier suivi.
- **18h50 (avancement)** : phase 2 et 2b TERMINÉES (`audit/liens_statut.csv` brut, `audit/liens_statut_final.csv` affiné : 788 🟢, 19 🟡, 25 🔴, 17 ⚪ faux positifs d'extraction). Phase 3 : site (accueil + 12 animations) parcouru dans Chrome, 0 erreur console/KaTeX ; wiki : en cours, pages dans l'ordre alphabétique de `audit/pages_wiki.json` (84). REPRENDRE ICI : voir la dernière ligne « wiki page N » ci-dessous.
- wiki page 27/84 (Formules_zeta) vue dans Chrome ; 0 page inexistante, 0 « Unable to render » jusqu'ici. Reprendre à la page 28 (Guide-Capture-Session-Claude-Code) dans l'ordre de audit/pages_wiki.json.
- wiki page 67/84 (analyse_problemes_v5_v6) vue ; reprendre à la page 68 (analyse_problemes_v6_v7). Constat : Structure-Projet-Complet l.151-152 = liens VALIDES (cibles Animations / Guide-Ollama-Pratique), à corriger en 🟢 dans liens_statut_final.csv ; GitHub marque les liens morts a.absent (test à faire sur Home pour Étape-2/3/4).
- **Audit liens — état à 19h30 (session 12/11)** : phases 1, 2, 2b, 3 (site : accueil + 12 animations ; wiki : 84/84 pages défilées dans Chrome), 4 et 5 FAITES en lecture seule. Fichiers : `audit/liens.csv` (849 liens), `audit/liens_statut_final.csv` (790 🟢, 19 🟡, 23 🔴, 17 ⚪ faux positifs d'extraction), `audit/noms_a_risque.csv` (5 pages wiki à accents, 34 ancres à risque, 0 fichier publié), `audit/pages_wiki.json`. En attente : échantillon A/B/C de hprzeta (10 liens), puis « go archive » (cours/make_wiki_page.py proposé), « go correction ». RIEN n'a été modifié, commité ni renommé.
- Contrôle `a.absent` (GitHub marque les liens vers pages inexistantes) lancé dans l'onglet Chrome « Audit liens » (`window.__res`) : 1ʳᵉ trouvaille = `[[#18-pc5-…]]` dans Architecture-Cluster-Zeta ; à finir/relire.
- Échantillon A/B/C : hprzeta a répondu « c » (interprété : les 10 liens = C, au bon endroit ; à reconfirmer si l'intention était autre). Aucun « go archive » / « go correction » reçu à ce stade.
- « go archive » exécuté : cours/make_wiki_page.py déplacé (git mv, indexé, NON commité) vers archive/scripts_obsoletes_20261112/ + LISEZMOI.md ; sauvegarde pdf/archive/make_wiki_page.py.bak-*. En attente : « go commit archive ».
- **« go correction » exécuté (non commité)** : wiki (7 pages : Animations, Phase-C, Phase-Optimisation, Home, Architecture-Cluster, STACK, Etape-1) + site (index.html, animation_theta, animation_zeros_non_triviaux : lmfdb→www). Sauvegardes `pdf/archive/*.bak-<AAAAMMJJHHMM>`. Choix faits : Home Étape-2→Animations, Étape-3→Guide-Ollama-Pratique (convention de Structure-Projet-Complet), Étape-4 sans lien. DOI Odlyzko-Schönhage corrigé (Crossref). NON corrigés : lien archive.org Titchmarsh (aucune édition équivalente vérifiée), README issues/Kanban (connexion requise), code tiers Plotly. En attente : « go commit wiki » → « go push wiki » → « go commit site » → « go push » (+ « go commit archive »).
- « go commit site » exécuté : IA 05217b8, main 4165de3, C 773bdff, Test 3aa3c23 (cherry-pick -x, SHA-256 identiques) ; NON poussé. Archive toujours indexée, non commitée.
- « go push » exécuté : 4 branches poussées sans --force (IA a07a331..05217b8, main 5169d67..4165de3, C c0e989e..773bdff, Test 0192cae..3aa3c23) ; wiki 2bd4258 poussé plus tôt. Reste : « go commit archive » (index git), re-test final des liens corrigés + échantillon, rapport Étape 6 (RAPPORT_AUDIT_COMPLET_*.md/.pdf), contrôle a.absent à relancer.
- « go commit archive » + « go push » exécutés : archive IA 001f3b2, main 33f3ada, C ff9dc8b, Test cd9f2b8, poussés sans --force. Reste : re-test final + a.absent + échantillon + rapport Étape 6.
- **Rapport final généré** : RAPPORT_AUDIT_COMPLET_20261112_1921.md/.pdf (copie .md dans A_DEPOSER/). Re-test : 813 🟢, 14 🟡, 4 🔴 (3 code tiers Plotly + Titchmarsh archive.org), 17 ⚪ ; a.absent : 0 page. Échantillon 2 (après corrections) en attente de hprzeta. Commit du rapport sur Riemann_Lab_IA seule ; push en attente d'un « go push » après le SHA.
- Rapport 4ce4417 poussé sur Riemann_Lab_IA (sans --force). Reste : échantillon 2 A/B/C de hprzeta ; dépôt manuel du .md dans le projet SITE ZETA.
- Échantillon 2 reçu : 1C 2C 3C 4C 5C 6C ; rapport mis à jour (même nom 1921), commité, push en attente de « go push ».
- Rapport mis à jour 1a51693 poussé sur Riemann_Lab_IA (sans --force). Audit des liens terminé ; reste le dépôt manuel du .md dans SITE ZETA et les 4 décisions du §8.
- **Renommage wiki (prompt 19h49) — étape 0 faite, étape 1 faite (lecture seule)** : diagnostic dans audit/renommage_liens_entrants.csv ; 25 liens + 21 mentions (17 historiques) ; 0 lien depuis site/README/scripts/PDF publiés ; STOP étape 2 : attente « go correction avec renvoi » ou « sans renvoi ». NB : PROMPT_WIKI_STACK_TITCHMARSH_20261112_1945 (zip en Téléchargements) pas encore exécuté ; STACK.md l.539 sera touché par les deux.
- **Renommage wiki : « go correction avec renvoi » exécuté, NON commité** : 5 git mv (Etape-1, Interprétation, Partie-1, Projet-Zêta→Zeta, Tableau-Symboles), 5 pages de renvoi aux anciens noms, 28 remplacements de liens/mentions (Formules_zeta l.1411 + Plancher l.100 inclus), Animations : 13 titres sans symbole + 12 ancres du tableau, pieds de page mis à jour. Mentions laissées volontairement : JOURNAL, docs/archive, etat_rag, Archive-Fichiers-Obsoletes (historiques), Guide-Ollama l.101 (citation de réponse RAG du 25/07), Guide-Git-GitHub l.105 (exemple de commande historique à nom préfixé d'un emoji). Sauvegardes pdf/archive/*.bak-202611121956. Attente : « go commit wiki ».
- « go commit wiki » exécuté (renommage) : 2 commits locaux sur master du wiki : 8045f4e (5 renommages R051-R099 + liens + Animations D27, message demandé) puis 7e2da49 (5 pages de renvoi aux anciens noms). NON poussés. Attente : « go push wiki ». Ensuite étape 4 (re-test, a.absent, Chrome, échantillon A/B/C) puis rapport RAPPORT_RENOMMAGE_WIKI_*. Pas de site à commiter a priori.
- « go push wiki » exécuté : 2bd4258..7e2da49 poussés (8045f4e + 7e2da49), sans --force. Reste : étape 4 (re-test liens, a.absent, Chrome, échantillon A/B/C) + rapport RAPPORT_RENOMMAGE_WIKI_*.
- Échantillon renommage : hprzeta a répondu « c » (interprété : les 8 liens = C ; à reconfirmer si autre intention).
- **Renommage wiki terminé (étape 4-5)** : re-test 819 🟢 / 14 🟡 / 4 🔴 (mêmes 4 qu'avant : 3 Plotly + Titchmarsh) / 17 ⚪ ; a.absent 0 sur 89 pages ; Chrome : 5 nouvelles pages, 5 renvois, Animations 12/12 ancres ; échantillon « c » (8 liens). Rapport RAPPORT_RENOMMAGE_WIKI_20261112_2005.md/.pdf (copie .md dans A_DEPOSER/), NON commité (attente « go commit rapport » éventuel). Reste : décisions §8 audit (Titchmarsh, README, DOI) ; prompt PROMPT_WIKI_STACK_TITCHMARSH_20261112_1945 non exécuté.
- Rapport du renommage commité et poussé : 5275a10 sur Riemann_Lab_IA (1a51693..5275a10), sans --force. Renommage wiki entièrement terminé.
- **STACK / Titchmarsh (prompt 19h45, D25)** : étapes 0-1 faites (ligne 474 conforme, lien absent ailleurs), capture captures/d25_avant_stack.jpg ; correctif appliqué dans STACK.md l.474 + pied de page (706 lignes), sauvegarde pdf/archive/STACK.md.bak-202611122012, audit 0 ligne suspecte ; NON commité. Attente : « go commit wiki » → « go push wiki », puis étape 3 (Chrome après, curl des liens de STACK) et rapport RAPPORT_WIKI_STACK_TITCHMARSH_*.
- « go commit wiki » STACK/Titchmarsh : commit local 0d94a0d (non poussé). Attente « go push wiki ».
- « go push wiki » STACK/Titchmarsh : 7e2da49..0d94a0d poussé, sans --force. Reste : étape 3 (Chrome après, curl liens STACK) + rapport RAPPORT_WIKI_STACK_TITCHMARSH_*.
- **STACK/Titchmarsh terminé** : poussé 7e2da49..0d94a0d ; Chrome avant/après (captures d25_*), liens STACK : 4/5 en 200 + DOI Turing 403 (robots) ; rapport RAPPORT_WIKI_STACK_TITCHMARSH_20261112_2013.md/.pdf (md copié dans A_DEPOSER), non commité (attente « go commit rapport » éventuel).
- Rapport STACK/Titchmarsh commité localement (03c4db3), non poussé (attente « go push »).
- Rapport STACK/Titchmarsh poussé : 5275a10..03c4db3 sur Riemann_Lab_IA, sans --force. Tous les prompts du 12/11 (audit liens, renommage, STACK/Titchmarsh) sont terminés.
- bye bye 20h30 : turbo restauré, archive docs/archive/discusion_claude_2026-11-12.md/.pdf fusionnée (non commitée), bloc PROMPT_REPRISE de ~/riemann_handoff/Handoff.md mis à jour.
