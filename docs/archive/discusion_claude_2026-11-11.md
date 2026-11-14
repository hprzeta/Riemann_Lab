# Archive de session — 11/11/2026 (Parties A et B)

# Partie A — test du site, corrections lots 1 à 5, publication

> Session du 11/11/2026 (soir). Deux prompts de hprzeta : un test du site en lecture seule, puis des corrections en 5 lots. Fin de session : « bye bye ». Aucun extrait de code dans cette archive ; adresses IP et e-mails masqués ([IP], [EMAIL]).

**Turbo Zêta :** RESTAURÉ (vérifié : 4 CPU à leur gouverneur initial, cpu0 = powersave, swappiness 10).
**Capture brute :** *claude-traitement-journalier/session_20261111_1428.log* (script actif ; un « exit » ×2 est demandé pour générer le .md ; non commitée).

---

## 1. Instruction de hprzeta — test de mise à jour du site (lecture seule)

> **PROMPT Claude Code — Test de mise à jour du site (LECTURE SEULE)** — préparé le 11/11/2026 depuis le projet SITE ZETA. Objectif : faire à la place de claude.ai ce qui n'avait pas pu être fait (ouvrir Claude in Chrome) et rendre un rapport.
>
> **Règles :** LECTURE SEULE (aucun fichier modifié, aucun commit, aucun push, aucun commentaire GitHub) ; ne rien saisir dans un formulaire, ne se connecter à aucun compte, n'accepter aucune bannière ; si Chrome demande l'autorisation JavaScript, attendre le clic « Autoriser » ; ne donner que des faits observés, chaque ligne indique comment elle a été vérifiée.
>
> **Étape 1 :** ouvrir Claude in Chrome et créer un onglet « Recherche MAJ site ». **Étape 2 :** parcourir le site en ligne (10 points attendus : bandeau V17 du 03/11/2026 ; stats 10 016 474 zéros, Turing complet, t max 5 000 000 ; tableau v1 à V17 avec lien PDF v16 à v17 ; bloc T=5M avec 97 manquants, 84 paires et 13 isolés ; section IA, RAG réingéré 1258 passages, exploratoire ; 12 animations dont les 4 nouvelles ; issues « 4 ouvertes (#2 à #5) » ; cartes cluster PC1 16 Go, PC2 7,6 Go, PC3 5,7 Go ; gain ×7 490 à T égal ; pied de page « mis à jour le 11/11/2026 »), avec formules, tableaux, un lien par section, erreurs de console. **Étape 3 :** parcourir 8 pages du wiki (Home, Etape-1, Roadmap, Animations, Projet-Zêta redirigée, Plancher, Structure, Configuration). **Étape 4 :** points A à G (commentaires « État au 11/11/2026 » sur les issues #3 à #5 ; occurrences de « 96 manquants » ; cohérence des 4 branches ; note du 11/11 dans les PDF des analyses annotées ; liens externes en HTTP 200 ; absence de secrets et d'identifiants réseau ; restes périmés connus du wiki). **Étape 5 :** tableau de validation (🟢 ok · 🟡 à moitié · 🔴 ko), liste des erreurs, captures, rapport enregistré sous RAPPORT_TEST_MAJ_SITE_20261111_HHMM.md dans pdf/site/maj_site_20261111/ sans commit, et affiché en entier ; terminer par « Test terminé, rien n'a été modifié dans le dépôt » et la sortie de git status --short.

### Résultat du test (rapport de 18h39)

| Élément | Statut | Constat |
|---|---|---|
| Site, points 1 à 10 | 🟢 | tous conformes ; 53 formules rendues, aucune erreur ; 61 liens externes en HTTP 200 |
| 4 nouvelles animations | 🟢 | chargées, 0 erreur KaTeX (contrôle par le DOM) |
| Tableau v1→V17, frise, titre perfs | 🟡 | la frise s'arrêtait à la tuile v16 ; titre de section encore « V16 » |
| Console du navigateur | 🟡 | non concluante (suivi démarré après le chargement) |
| Wiki : 8 pages | 🟢/🟡 | rendu correct ; Projet-Zêta est un stub « page déplacée » ; en-têtes MAJ de Structure et Configuration encore à 2026-06-13 |
| A : issues #3, #4, #5 | 🟢 | commentaire « État au 11/11/2026 » présent |
| B : « 96 manquants » | 🟢 | 3 occurrences, toutes présentées comme historique |
| C : branches | 🟢 | docs/ identique sur les 4 branches |
| D : PDF des analyses | 🔴 | les PDF v13 à v15 et v1 à v16 n'avaient pas la note du 11/11 ; le PDF « déficit » n'est pas suivi par git |
| E : liens externes | 🟢 | 61 sur 61 en 200 |
| F : secrets, identifiants | 🟡 | une adresse e-mail dans une copie « publiable » d'un diagnostic ; docs/archive non audité |
| G : restes périmés du wiki | 🔴 | tous encore présents |

## 2. Instruction de hprzeta — corrections après le test (5 lots)

> **PROMPT Claude Code — Corrections après le test du site du 11/11/2026.** Règles : un lot à la fois, après chaque lot git diff puis STOP et attendre « go » avant tout commit, second STOP avant tout push, jamais --force ; commits sur Riemann_Lab_IA puis cherry-pick -x sur les trois autres branches (site publié depuis Riemann_Lab_IA, dossier /docs ; le wiki est un dépôt séparé) ; copie .bak-AAAAMMJJ avant de modifier un script ou une configuration ; ne pas toucher à monitoring/Monitoring-Runs.md ; aucun fait inventé (chaque chiffre vient de STACK, JOURNAL, Handoff, docs/V17.md ou d'une mesure refaite) ; pas d'IP, de clé ni d'e-mail en public ; règles KaTeX ; pied de page de chaque .md modifié avec date et nombre de lignes exact ; visualiser dans Claude in Chrome (onglet « Recherche MAJ site »).
>
> **Lot 1 — secret en clair (priorité) :** remplacer l'adresse e-mail trouvée par un marqueur, auditer tout le dépôt (docs/archive compris) et le wiki, donner la liste complète avant de corriger autre chose, ne pas réécrire l'historique git, dire seulement si l'adresse figure dans des commits antérieurs. **Lot 2 — site :** ajouter la tuile V17 à la frise, proposer le titre exact de la section perfs avant de le modifier, mettre à jour la date du pied de page, tester liens et formules. **Lot 3 — wiki :** Structure (v4_1 marqué actif), Configuration (4 workers, disque 908 Go à mesurer, en-têtes MAJ), Animations (cours associés des 4 nouvelles, après accord), Plancher (encadrés datés sur les sections v12, « v13 OS » planifié non réalisé), Projet-Zêta inchangé ; grep des mêmes motifs. **Lot 4 — PDF :** régénérer les deux PDF d'analyses depuis les .md du wiki avec le script de génération, vérifier en-tête, pages, note du 11/11 en page 1, tableaux ; archiver les anciens ; dire où est le PDF « déficit » sans le commiter. **Lot 5 — contrôle final :** console suivie avant le chargement, ouverture à l'écran des 4 animations, nommer l'onglet, un lien cliqué par section. **Livrables :** PDF récapitulatif horodaté (ReportLab, ajouts en vert, suppressions en rouge), rapport de test, compte rendu court avec git status --short.

## 3. Déroulé et décisions

### Lot 1 — secret et audit
- L'adresse e-mail se trouvait dans une copie de diagnostic (docs/diagnostics) **exclue de git** (.git/info/exclude) : jamais commitée, jamais publiée. Aucune trace dans l'historique du dépôt ni du wiki. Remplacée par [EMAIL] (copie .bak).
- L'audit complet a trouvé une **vraie IPv4 publique dans le wiki** (guide de commandes, exemple de sortie WireGuard), poussée le 22/08/2026 (commit wiki 9cef38d) ; plus deux DNS de fournisseur dans le JOURNAL. Faux positifs écartés : placeholders de token, UUID de disque, motifs de grep dans les scripts d'audit, bruit binaire des PDF.
- **Décision de hprzeta :** remplacer par des marqueurs ([IP_PC4], [IPv6_PC4], [IP_DNS1], [IP_DNS2]) ; aucune IP d'endpoint ne doit être exposée ; e-mail de contact protonmail conservé en public ; pas de réécriture d'historique (l'ancienne IP reste dans le commit wiki 9cef38d).
- **Décision :** oui au filtre e-mail dans le script de publication des diagnostics (qui masquait IP et MAC mais pas les e-mails).

### Lot 2 — site
- Tuile V17 ajoutée à la frise (1,84 min distribué PC1+PC2, 2 min 40 s PC1 seul, 03/11/2026).
- **Titre de la section perfs, option retenue par hprzeta :** « T=100 000 : 1,6 min en v16 (PC1, turbo, 08/08/2026) · 1,84 min en V17 distribué PC1+PC2, 2 min 40 s sur PC1 seul (03/11/2026) · V17 ».
- **Constat de hprzeta :** le but de la V17 était de voir si le partage PC1 + PC2 fait gagner du temps ; il semble que tout ait tourné sur PC1 et sans turbo. **Tâche notée** (Handoff local et wiki) : mesurer la V17 sur PC1 seul avec turbo, à comparer à la v16 ; non mesuré ici.
- **Règle fixée par hprzeta :** toujours ouvrir Claude in Chrome sur la page modifiée du site pour qu'il voie la modification (écrite dans CLAUDE.md et en mémoire).

### Lot 3 — wiki
- Structure et Arbre : v4_1 marqué historique, V17 désignée active (lancée par le script de run). Configuration : disque mesuré (un seul disque de 931,5 Gio, 5 partitions, environ 907 Go utilisables en ext4), 8 workers depuis la v10. Plancher : encadrés « état de juin 2026, dépassé depuis v16 et V17 » sur trois sections, « v13 OS planifié, non réalisé ». Animations : cours associés validés par hprzeta (gaps vers niveau 5, Illinois et coût RS vers niveau 4, précision mpfr laissée sans cours car aucun cours ne la couvre).

### Lot 4 — PDF des analyses
- Les deux PDF régénérés (7 et 9 pages, note du 11/11 en page 1, tableaux non coupés). La première génération de l'analyse v1 à v16 échouait : le fichier source utilisait la notation \( … \) pour ses formules (34 occurrences), contraire à la règle du projet ; contournée par une copie temporaire convertie, le wiki n'a pas été modifié. **Question restée ouverte :** convertir ces formules dans le wiki ?
- Le PDF « déficit » reste local (dossier ignoré par git), sans référence sur le site ni le wiki.

### Lot 5 et publication
- Console suivie avant chargement : aucun message sur l'accueil ni sur les 4 animations ; toutes les requêtes en 200 ; animations ouvertes à l'écran ; liens cliqués (animation, wiki) ; le lien PDF s'ouvre sur GitHub.
- **Commits :** deux commits sur la branche IA (site, puis dossier pdf/site réservé à cette branche), le premier porté par cherry-pick sur les trois autres branches ; un commit wiki. Audits des lignes ajoutées propres ; un e-mail cité dans le rapport de test a été masqué avant commit. Push sans --force, sur la demande « go push ».
- **En ligne (vérifié dans Claude in Chrome) :** build GitHub Pages terminé, tuile V17 et nouveau titre visibles, 0 erreur de formule, les trois liens PDF en 200.

## 4. Ce qui reste ouvert
- Pied du Handoff du wiki encore daté du 16 août 2026.
- Conversion des formules en notation \( … \) du wiki : décision de hprzeta attendue.
- PDF récapitulatif du début d'après-midi (1615) à archiver ou laisser ; fichiers .bak du jour non commités.
- Fichier de monitoring modifié avant la session, non commité, laissé de côté volontairement.
- Mesure V17 sur PC1 seul avec turbo : à lancer après accord de hprzeta.
- Ancienne IP toujours présente dans l'historique du wiki (non réécrit).


---

# Partie B — Exclusion des .bak de .claude/skills (23h50 → 00h14, début du 12/11)

> Session reprise après un `/clear`. Cette partie ne couvre que ce que cette session a vu ; le travail précédent du même soir est résumé dans la Partie A. Aucun extrait de code ; identifiants masqués ([EMAIL]).

**Turbo Zêta :** RESTAURÉ (vérifié : 4 CPU à leur gouverneur initial (cpu0=powersave), swappiness 10).
**Capture brute :** *claude-traitement-journalier/session_20261111_2036.log* (script actif ; « exit » ×2 demandé pour générer le .md ; non commitée).

## 5. Instruction de hprzeta — correctif du .gitignore

> Le zip MAJ_GITIGNORE_SKILLS_20261111_2340.zip est dans ~/Téléchargements. Dézippe-le dans /home/riemann/projet_zeta/src/ia/prompts, puis lis et applique PROMPT_CORRECTION_GITIGNORE_SKILLS_20261111_2340.md étape par étape. Étape 1 obligatoire : Claude in Chrome, onglet « Mise à jour site », montre la ligne 30 AVANT. Complète le dossier pdf/site/maj_site_<date du jour>. STOP avant commit (j'écrirai « go commit ») et STOP avant push (« go push »). Jamais --force. Montre-moi le résultat à l'écran (défilement, survol, encadré vert sur la nouvelle ligne 31). Termine par le rapport .md + .pdf, et rappelle-moi de donner le .md à claude.ai.

## 6. Déroulé
- **Problème :** la ligne 30 du `.gitignore` ré-incluait tout le dossier skills ; un fichier de sauvegarde `.bak` y aurait été publié par un `git add -A`.
- **Avant :** ligne 30 vue et encadrée en rouge dans Claude in Chrome (le navigateur traduit « skills » en « compétences » à l'affichage ; le fichier réel est inchangé). Faille confirmée par test sur un fichier temporaire.
- **Correctif :** une ligne ajoutée juste après (ligne 31), 10 fichiers skills suivis avant et après, sauvegarde du `.gitignore` rangée dans `pdf/archive/`.
- **« go commit » :** commit `9f902eb` sur Riemann_Lab_IA, cherry-pick `-x` sur Riemann_Lab_C (`ee49846`), main (`8ae1559`) et Riemann_Lab_Test (`9e9fd7d`).
- **Constat :** le `.gitignore` de Riemann_Lab_IA diffère des trois autres d'une ligne vide, antérieure au correctif. **Décision de hprzeta : on la laisse telle quelle, aucun commit.**
- **« go push » :** 4 branches poussées sans `--force`, local = origine. Audit du diff propre (les deux correspondances du grep étaient dans les métadonnées du commit).
- **Après :** ligne 31 encadrée en vert sur main et sur Riemann_Lab_IA. Site non modifié : 59 liens externes en 200, 0 erreur KaTeX, 0 formule brute, pied « mis à jour le 11/11/2026 » inchangé, animations θ(t) et produit eulérien ouvertes sans erreur. Limite : le suivi de la console démarre au premier appel, donc le chargement initial de l'accueil n'est pas couvert.
- **Rapport :** RAPPORT_MAJ_GITIGNORE_SKILLS_20261111_2358 (.md et .pdf) dans pdf/site/maj_site_20261111/ ; le .md a été rangé par claude.ai dans le projet SITE ZETA.

## 7. Instruction de hprzeta — fin de session SITE ZETA

> Fin de session SITE ZETA du 11/11, tout est validé. 1. Ligne vide du .gitignore de Riemann_Lab_IA : on la LAISSE telle quelle, aucun commit. 2. Le rapport RAPPORT_MAJ_GITIGNORE_SKILLS_20261111_2358.md est rangé dans le projet SITE ZETA (par claude.ai). Rien d'autre à déposer. 3. Le projet SITE ZETA ne garde plus que les .md : modifie le hook de fin de session pour qu'il copie seulement les .md dans A_DEPOSER (plus les .pdf). Montre-moi le changement avant de l'enregistrer. 4. Vérifie que le dossier A_DEPOSER n'est ni suivi ni commité par git (git status / git check-ignore). 5. Aucun autre changement, aucun commit, aucun push. Termine par un git status --short des deux dépôts.

- **Hook :** changement montré (3 lignes retirées, 3 ajoutées dans le script de dépôt local), enregistré après « ok hook » ; sauvegarde `.bak-20261112` ; test à blanc : seul le .md est copié. Les .pdf déjà présents dans A_DEPOSER n'ont pas été touchés.
- **A_DEPOSER :** ignoré via `.git/info/exclude` (pour tous les jours), 0 fichier suivi, aucun commit sur aucune branche.
- **État git final :** dépôt du projet : seul le fichier de monitoring, modifié avant la session ; wiki propre.

## 8. Ce qui reste ouvert
- Fichier de monitoring modifié avant la session, non commité, laissé de côté.
- Rapport et captures de cette partie : non commités (dossier pdf/site réservé à la branche IA, sur « go » de hprzeta).
- Points ouverts de la Partie A (formules *\( … \)* du wiki, mesure V17 PC1 seul avec turbo) inchangés.

*Archive du 11/11/2026 (Parties A et B) — rédigée à la clôture de session (« bye bye »), non commitée — 114 lignes*
