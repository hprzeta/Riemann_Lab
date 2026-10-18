# Archive de session — 17/10/2026

Projet Riemann_Lab — session Claude Code du 17/10/2026 (branche Riemann_Lab_IA).

**Turbo Zêta :** RESTAURÉ (vérifié : 4 CPU à leur gouverneur initial (cpu0=powersave), swappiness 10) — première étape du « bye bye », code de sortie 0. Au second « bye bye » de la journée : « Turbo Zêta : RIEN À RESTAURER » (code 0, état déjà restauré), TURBO_STATUS=INACTIF.

**Capture brute du terminal :** active, fichier claude-traitement-journalier/session_20261017_1533.log ; le .md est généré à la fermeture (taper exit deux fois). Non commitée.

Cette archive reprend la narration, les tableaux et les conclusions de la session ; aucun extrait de code n'y figure.

---

## 1. Point projet

Sur la demande « point projet », le bloc de reprise du Handoff a été lu et résumé :

- **Version du pipeline :** V17 (compute_zeros_v17.py) ; turbo par session actif ; monitoring installé et validé à blanc.
- **Dernier commit au départ :** 2de45af ; travail non commité : dossier monitoring, résultats V17, archives de discussion, 4 anciens scripts de monitoring.
- **Prochaine action annoncée :** tester le monitoring sur un vrai run court.

## 2. Monitoring v2 — étape 1, état des lieux en lecture seule

hprzeta a transmis un prompt en 5 étapes (lecture seule, installation, intégration, premier run de test, interprétation), avec la règle de s'arrêter à chaque étape pour attendre son OK.

| Question | Constat (mesuré) |
|---|---|
| Démarrage d'un run | zeta_run.sh active le turbo avec arrêt des services, puis lance le calcul compute_zeros_v16.py (et non la v17) sous systemd-inhibit, en arrière-plan, puis attend la fin |
| CSV des zéros | écrit seulement à la fin de chaque worker (v16) ; la v17 écrit un fichier partiel toutes les 60 secondes |
| Turbo | gouverneur performance, EPP, swappiness 10 ; le boost matériel no_turbo n'est pas modifié ; sudo sans mot de passe sur deux scripts du dépôt (modifiables par l'utilisateur, durcissement root non fait) |
| Affichage | session Wayland (XWayland), backend matplotlib qtagg, tkinter et PyQt5 disponibles |
| Doublons | les 4 scripts de scripts/ différaient de ceux de monitoring/scripts/ ; la mise à jour de lecture incrémentale n'était appliquée que dans monitoring/ |

Proposition retenue : envelopper la commande du run par le lanceur de monitoring, en mode production par défaut (sans fenêtres) et en mode test à la demande.

> « OK pour l'étape 2, reste sur v16 » — hprzeta

## 3. Étape 2 — installation, puis étape 3 — intégration

- Archive monitoring_v2 extraite (13 fichiers écrasés, chacun sauvegardé en .bak-20261017), script d'installation lancé, test des 5 machines : PC1 à PC5 tous OK, logger et détecteur de runs actifs.
- Anomalie notée : PC1 affichait une charge d'environ 2,5 à 2,9 au repos ; cause non cherchée.
- Intégration dans zeta_run.sh : le calcul v16 est enveloppé par le lanceur (type production par défaut, test via la variable ZETA_MON_TYPE) ; le turbo, le log, le PID et les services sont inchangés ; repli sur l'ancien lancement si le lanceur est absent.
- Les 4 scripts doublons de scripts/ sont remplacés par des wrappers d'une ligne vers monitoring/scripts/ (source unique) ; le menu zeta-script reçoit les commandes zeta-mon-exec, start, stop, fenetres, fermer.
- Limite signalée d'emblée : avec la v16, le graphique des zéros en direct et le débit instantané ne se remplissent qu'à la fin des workers.

## 4. Étape 4 — premier run de test (T = 50 000)

Run de 41 secondes de calcul, 63 519 zéros, LMFDB 20/20, validation de Turing « complète ». Machine : PC1 jusqu'à 73 °C, charge 7. Les trois fenêtres de graphiques se sont ouvertes.

Défauts constatés :

- Le rapport n'a pas été généré : un conflit de nom de variable dans le script de rapport (une variable de débit réécrite par une médiane de fréquence).
- Le débit instantané était à zéro, car le CSV n'est écrit qu'en fin de worker.
- Les fenêtres des zéros et du GUE restaient vides.

> « plot metric affiche bien mais les deux autre plot affiche rien ! c'est normal ? » — hprzeta

**Cause (mesurée) :** le lanceur transmet l'heure de début en heure locale, mais deux scripts la lisaient avec pandas qui suppose UTC ; le seuil se retrouvait 2 heures dans le futur et filtrait tous les CSV, sans message d'erreur. Le défaut est indépendant de la v16.

## 5. Corrections et premier commit

Avec l'accord de hprzeta (« OK pour les deux patchs »), trois corrections dans monitoring/scripts/ :

1. Lecture de l'heure de début en heure locale (fenêtres zéros et GUE).
2. Renommage des variables de fréquence dans le rapport (un premier renommage avait lui-même collisionné avec une fonction ; corrigé).
3. Débit instantané signalé « non exploitable » quand le CSV n'a grossi que sur moins de la moitié des mesures, au lieu d'afficher 0 z/s.

Chaque fichier a une copie de sauvegarde. Le commit bff901f (52 fichiers) a été créé sur Riemann_Lab_IA après audit des lignes ajoutées (secrets, adresses IP, MAC, e-mails : 0 résultat), puis propagé : Riemann_Lab_C par avance rapide, main et Riemann_Lab_Test par fusion sans conflit (dans un worktree temporaire), puis Riemann_Lab_IA poussée. Les quatre branches étaient à niveau, sans --force.

## 6. Run de test T = 100 000 et explications

- **Premier run T = 100 000 :** 2 min 39 s, 138 069 zéros (attendu environ 138 068,6), LMFDB 20/20, Turing « complet » ; PC1 max 79 °C ; débit moyen 868 z/s. Rapport FR/EN et interprétation rédigée à la main (mesuré / heuristique / hypothèse / conjecture). hprzeta a confirmé que les trois fenêtres s'affichaient bien.
- **zeta-mon-fermer contre zeta-mon-stop :** fermer envoie un signal de fin aux trois fenêtres du lanceur, sans rapport ; stop déclare le run terminé et génère le rapport (inutile avec l'enveloppe exec). La commande restait « introuvable » dans le terminal de hprzeta car ce terminal avait été ouvert avant l'installation (il faut recharger le fichier de configuration du shell).
- **Erreurs de lancement de hprzeta :** commande tapée depuis le dossier personnel (chemin relatif introuvable), puis nom de variable écrit avec des tirets au lieu de tirets bas. La bonne forme a été donnée ; l'alias zeta-run accepte le préfixe de variable (vérifié sur un alias inoffensif).

## 7. Guide des scripts — inventaire, MD, PDF, menu

> « Objectif : que CHAQUE script et CHAQUE alias existant soit documenté dans les MD, puis dans les PDF. Aucun oubli toléré. » — hprzeta (prompt en 4 étapes)

**Inventaire (lecture seule) :** 188 scripts (180 hors téléphone) et 58 alias ou fonctions. Avant : 41 scripts et 32 alias documentés ; manquants : 147 scripts et 26 alias.

**Décisions de hprzeta :**

> « 1 je prend ta proposition. 2 ok on exclux et document rien ce que qui concerne telephone. 3 ce scripte devra centraliser tout les scripe de monirting pour tout lancer dun coup 4 on gardre comme tel »

Autrement dit : fiches complètes pour scripts/, monitoring/, V17, tests et alias ; tableaux courts pour src/ ; scripts du téléphone et du DNS exclus et non documentés ; le script zeta_webmonitor.py (cible de l'alias zeta-webmonitor, fichier inexistant) est documenté « non créé » avec le rôle prévu de centraliser le lancement du monitoring ; les trois scripts de Proton et du RAG situés dans les téléchargements gardent leur mention.

**Résultat :**

| | Existant | Documenté dans le MD | Documenté dans le PDF |
|---|---|---|---|
| Scripts (hors téléphone) | 180 | 180 | 180 |
| Alias et fonctions | 58 | 58 | 58 |

- Le guide MD passe de 819 à 1 468 lignes (sections 8b à 8e et 10b), le PDF fait 30 pages avec un pied de page « mis à jour le … » et « page i / N ». 39 noms de scripts sont coupés par un retour à la ligne dans le PDF mais présents.
- Des sections anciennes (zeta_run.sh, turbo) ont reçu une mise à jour datée ; le gain de vitesse du turbo « +15 à 30 % » est noté comme non démontré (benchmarks du 16/10 : environ 2 %, dans la dispersion).
- Le MD et les PDF sont exclus de git (le guide contient des adresses) ; seul le générateur de PDF modifié est suivi.
- hprzeta a demandé d'ajouter au menu les 7 fonctions de couleurs de terminal ; le menu compte maintenant 58 entrées. Commit d275736, propagé aux quatre branches (fusions sans conflit), poussé sans --force.

## 8. Runs supplémentaires : production T = 10 000 et T = 400 000

| Run | Durée | Zéros | LMFDB | Turing | Remarques |
|---|---|---|---|---|---|
| Test T = 100 000 (20h08) | 2 min 43 s | 138 069 | 20/20 | complet | débit 847 z/s ; PC1 max 77 °C ; load max 14,5 |
| Production T = 10 000 | 22 s suivi (8 s de calcul) | 10 142 | 20/20 | complet | aucune fenêtre ; pas de figure de débit (trop peu de points) |
| Production T = 400 000 | 20 min 39 s | 640 520 | 20/20 | **5 zéros manquants** | débit moyen 517 z/s ; PC1 max 79 °C ; load max 16,3 |

**Run de 400 000 (demandé pour 15 minutes) :** calcul principal 676,7 s, rescan ciblé 521,5 s (3 segments en déficit, gain net de 1 zéro), puis validation ; le rescan avait été sous-estimé. La figure de débit est générée mais plate à zéro : le suivi est resté figé sur un seul CSV de worker. Le rapport ne signale pas l'échec de la validation de Turing (5 zéros manquants, vers t = 308 000 et t = 400 000) ; c'est la limite connue de la v16 à grande hauteur, pas un défaut du monitoring. La charge a été surveillée toutes les 20 secondes : load 13 à 16 pendant environ 10 minutes, 67 à 73 °C relevés, aucun emballement (seuil d'arrêt à 95 °C jamais approché).

**Piège découvert :** quatre runs de T = 100 000 lancés par hprzeta depuis le dossier personnel ont écrit leurs CSV dans un dossier calculs du dossier personnel (chemin relatif), hors du projet ; trois de ces rapports n'ont donc pas leurs sections sur les zéros. Correctif proposé : se placer dans le dossier du projet avant le lancement dans zeta_run.sh. Non appliqué.

## 9. Handoff et état final

Le bloc de reprise du Handoff a été mis à jour à chaque jalon (monitoring, commits, guide, runs, piège). Quatre copies de sécurité du Handoff ont été faites.

**Branches (toutes poussées) :** Riemann_Lab_IA et Riemann_Lab_C au commit d275736 ; main à 82b2ac8 ; Riemann_Lab_Test à 952bd4f.

**Non commité :** le fichier de configuration ignoré (lignes du chantier téléphone, local), l'archive du 10/10 modifiée, les archives des 15 et 16/10, les dossiers de runs de monitoring (9 au total aujourd'hui), les résultats V17.

## 10. Prochaines actions (extrait du Handoff)

1. Corriger zeta_run.sh pour qu'il se place dans le dossier du projet.
2. Faire lire au rapport le verdict de la validation de Turing et l'afficher en tête.
3. Rendre le débit instantané utilisable en additionnant tous les CSV de workers.
4. Zéros manquants à grande hauteur (chantier V17) ; choix entre v16 et v17 pour le prochain gros run.
5. Inchangé : sort de zeta_webmonitor.py, fichier de configuration git racine, page wiki du monitoring, durcissement des droits sudo (action root), run T = 5M avec la v17, rotation du jeton DuckDNS.


## 11. Partie B — après le premier « bye bye » (fin de journée)

La session a continué après la première clôture. Cette partie complète l'archive du jour sans remplacer la partie A (sections 1 à 10), déjà commitée (fd4d283).

**Question de hprzeta sur les commits**

> « tu a valider les comit? »

Vérification de l'état réel plutôt que réponse de mémoire :

| Commit | Contenu | Accord de hprzeta |
|---|---|---|
| bff901f | monitoring v2, intégration dans zeta_run.sh, wrappers, menu (52 fichiers) | après « OK pour le patch du débit puis le commit », puis « pousser » |
| d275736 | menu zeta-script à 58 entrées et générateur de PDF (2 fichiers) | « go, commit puis propage et pousse » |

Les quatre branches étaient identiques en local et sur origin (écart nul) ; audit des lignes ajoutées sans résultat, simulation des fusions sans conflit, jamais de --force. **Non validé :** aucun test automatique n'a été lancé sur ces commits ; les contrôles se limitent à la compilation et à des essais réels (six runs avec le lanceur, menu affiché, générateur de PDF exécuté). Un fichier suivi a changé après les commits : le fichier de liste des runs du monitoring, régénéré automatiquement.

**Commit de l'archive du jour**

> « commite aussi l'archive d'aujourd'hui »

Audit du MD et du texte extrait du PDF : un seul résultat, la phrase « rotation du jeton DuckDNS » (nom du chantier, sans jeton, sans nom de domaine, sans adresse). Commit fd4d283 sur Riemann_Lab_IA (2 fichiers, 128 lignes ajoutées, aucune suppression).

**Propagation**

> « pousse et propage aux 3 autres branches »

Simulation sans conflit pour main et Riemann_Lab_Test, audit du diff propre. Riemann_Lab_C par avance rapide ; main (89a170c) et Riemann_Lab_Test (7e61c84) par fusion sans conflit dans un worktree temporaire ; poussé sans --force. Les quatre branches sont à niveau : Riemann_Lab_IA et Riemann_Lab_C à fd4d283.

**Mise à jour du Handoff**

> « oui, mets à jour le Handoff »

Le commit d'archive et les nouveaux hashes sont notés dans l'entrée « fin de soirée ». Une première tentative a échoué sans rien écrire, car la phrase à remplacer figurait dans deux entrées ; elle a été relancée en ne ciblant que l'entrée du dessus (copie de sécurité faite).

**Second « bye bye »**

- Turbo : « RIEN À RESTAURER » (déjà restauré au premier « bye bye »).
- Capture brute du terminal : toujours active (fichier session_20261017_1533.log) ; à fermer par exit deux fois ; non commitée.
- Cette partie B de l'archive est écrite après le commit fd4d283 : elle n'est pas encore commitée, en attente de l'accord de hprzeta.

---
*discusion_claude_2026-10-17.md · MAJ 2026-10-17 · 170 lignes*
