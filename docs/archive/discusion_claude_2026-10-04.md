# Archive de session — 3 et 4 octobre 2026

> Session démarrée le 03/10 vers 23h30 et terminée le 04/10 vers 01h20. Trois chantiers : conversion des PDF en Markdown, sauvegarde sur Proton Drive de ce qui est hors git, retrait des identifiants réseau du dépôt public (purge de l'historique comprise). Aucune adresse, clé ni nom d'hôte n'apparaît dans ce document : ils sont remplacés par des marqueurs entre crochets.

## 1. Conversion des PDF en Markdown (reprise après interruption)

**Consigne de départ (verbatim, extrait) :**

> Tu as été interrompu pendant la conversion PDF vers Markdown. Avant de reprendre, fais-moi un point, sans rien modifier.

**État constaté sur le disque :** le dossier md/ contenait 34 fichiers (712 Ko), tous complets et terminés par leur pied de page. Aucun processus de conversion ne tournait, les PDF étaient intacts et md/ était déjà exclu de git par l'exclusion locale du dépôt. Je n'avais aucun souvenir de la phase ni de la cause de l'arrêt, et je l'ai dit sans le deviner.

**Inventaire (lecture seule) :** 75 PDF dans pdf/, tous avec couche texte (aucun scanné), aucun document réellement confidentiel (les alertes du filtre étaient des mots banals).

| Statut | Nombre |
|---|---|
| Déjà dans md/ | 48 |
| .md existant ailleurs (wiki ou pdf/) | 24 |
| Aucun .md nulle part | 3 |

**Point technique important :** les deux scripts de conversion existants écrivent à côté du PDF et ne sont pas récursifs. Ils ne respectaient donc pas l'arborescence demandée. J'ai utilisé le script rapide sur une copie temporaire des PDF, puis déplacé les résultats dans md/.

**Décisions de hprzeta (verbatim) :**

> go 1

> go 2

> laisse md/ hors de git

**Résultat :** 3 PDF v0 convertis (environ 25 fois plus légers), 24 .md existants copiés tels quels sans écrasement. Au total md/ contient 61 fichiers, 1,1 Mo, et couvre les 75 PDF. La page Dossier-md du wiki, trouvée non suivie (probablement laissée par la session interrompue), a été mise à jour avec les chiffres exacts.

## 2. Sauvegarde sur Proton Drive de ce qui est hors git

**Consigne (verbatim) :**

> tout ce qui est hor git je veux un system de sauhgarde sur proton come fait le script zeta inventaire (md, secret etc )cree des reprtoir aproprier sur proton drive. fait la liste dabor parcrour tout le projet

**Constats de l'inventaire :** le quota Proton est de 2 Gio (environ 1,67 Gio libres). Les calculs pèsent 4,1 Go et ne peuvent pas y tenir. Le dispositif existant passe par PC3 (cron de 01h50 de PC1 vers PC3, puis PC3 vers Proton).

**Choix de hprzeta :** commencer simple, avec un essai à blanc d'abord ; secrets chiffrés par gpg symétrique ; calculs réduits aux petits fichiers ; cron nocturne sans les secrets.

> commence simple, dry-run d'abord

**Réalisé :**

| Élément | Détail |
|---|---|
| Script | zeta_backup_horsgit.sh, avec menu, mode simulation et mode automatique |
| Alias | zeta-backup-horsgit |
| Jeux sauvegardés | md/, mémoire Claude, suivi, fichiers non suivis par git, calculs légers (moins de 200 Ko), configuration locale ; secrets chiffrés en manuel seulement |
| Cron | 02h30 chaque nuit, mode automatique sans secrets, après celui de 01h50 |
| Sécurité | copie uniquement, aucune suppression côté Proton |

**Incident corrigé :** mon filtre avait laissé partir une archive de configuration de PC3 que je voulais exclure (motif trop étroit). Je l'ai supprimée de Proton (jamais ouverte) et corrigé le motif. Le script était aussi mal lu quand on lui passait deux options à la fois ; corrigé.

**Limite à retenir :** cron ne s'exécute que si PC1 est allumé à 02h30. Le test du jeu des secrets n'a jamais été lancé, car il demande la phrase de passe saisie par hprzeta.

## 3. Retrait des identifiants réseau du dépôt public

**Règle rappelée par hprzeta :** ne pas montrer d'adresses IP.

> ne pousse pas car un e regle dit de pas montrer ip

**Chronologie des actions :**

| Étape | Résultat |
|---|---|
| Fichier d'adresses local hors git (droits restreints) | adresses des machines et du bastion lues au démarrage par les scripts |
| Scripts de supervision, tmux, bascule WireGuard, distribution, état de sauvegarde, progression | plus aucune adresse en dur ; la bascule WireGuard n'agit pas sur le tunnel si le fichier manque |
| Documents Markdown, schémas, page du site, carte de sauvegarde | adresses remplacées par des marqueurs ou des libellés PC1 à PC4 |
| 5 archives de discussion et leurs PDF | nettoyés et PDF régénérés avec le même nombre de pages |

> traite les autres scripts avec IP

> 1 2 3 puis push

**Découvertes en cours de route :**
- Le fichier de prompt de juin contenait bien plus que des adresses locales : adresse publique, adresse IPv6, nom du service de nom dynamique et clés publiques WireGuard (pas de clé privée).
- Ces éléments figuraient aussi sur la branche publique main et dans la page du site.
- Quatre PDF encore publics contenaient des identifiants.
- Mes marqueurs entre chevrons étaient pris pour du HTML et disparaissaient à l'affichage ; remplacés par des crochets.

**Purge de l'historique (consigne puis délégation) :**

> laisse finir je vais dormir te laisse tout gerer

Une sauvegarde complète de l'ancien historique a été créée avant toute réécriture (hors dépôt, droits restreints). Les 10 versions de PDF concernées ont été caviardées avec PyMuPDF, ce qui garde la mise en page, puis le texte a été réécrit sur l'ensemble de l'historique. Après vérification (zéro identifiant dans les 725 commits, aucune clé privée), six branches ont été poussées de force : main, Riemann_Lab_C, Riemann_Lab_IA, Riemann_Lab_Test, inbox-ia et la branche euler. La branche session n'avait rien à changer. Tous les identifiants de commit ont changé.

**Problèmes rencontrés et corrigés :**
- Sur main et Riemann_Lab_Test, la substitution avait cassé 7 scripts qui contenaient encore des adresses ; ils ont été restaurés par un commit de correctif lisant le fichier local.
- Mes références temporaires de comparaison faussaient la vérification finale (anciens commits encore comptés) ; supprimées, puis vérification refaite sur les branches seules.
- Une valeur attendue mal saisie et des anciens objets déjà nettoyés ont fait échouer une première tentative de push ; remplacée par une comparaison explicite avec GitHub juste avant le push.

**Dépôt local :** resynchronisé sans toucher à l'arbre de travail (les suppressions et fichiers non suivis de hprzeta sont intacts).

## 4. Ce qui restait à faire à la fin de la partie A

| Point | Détail |
|---|---|
| Wiki public | 9 fichiers contiennent encore des identifiants (dépôt séparé, non traité) |
| Pull request 6 | une référence GitHub pointe encore vers l'ancien historique ; fermer la PR et demander le nettoyage au support GitHub |
| Autres clones | tous les identifiants de commit ont changé ; resynchroniser tout clone ou fork éventuel |
| Jeton du service de nom dynamique | rotation toujours à faire (en attente depuis août) |
| Tests | lancer la commande de bascule WireGuard avec le vrai fichier d'adresses ; relancer le test anti-hallucination du script RAG (l'exemple de citation a changé) |
| Secrets chiffrés | tester le jeu 6 de la sauvegarde (phrase de passe saisie par hprzeta) |
| Sauvegarde de l'ancien historique | à supprimer quand tout est validé |
| Limite du caviardage | seul le texte des PDF est caviardé ; une capture d'écran avec une adresse dans une image ne serait pas détectée |


---

# Partie B — suite de la session (04/10 après-midi → 05/10)

> La session s'est prolongée jusqu'au 05/10 vers 01h30. Cette partie complète la partie A (même journée de travail : un seul fichier d'archive).

## 5. Purge du wiki public

Le wiki (dépôt séparé) a subi le même traitement que le dépôt de code : 465 commits réécrits, branche principale poussée de force après vérification de l'état distant. Deux sauvegardes de l'ancien historique ont été conservées en local (elles contiennent encore les anciennes valeurs). Les adresses ont été remplacées par des marqueurs spécifiques entre crochets. Trois captures d'écran (ollama) n'ont pas pu être analysées automatiquement et restent à vérifier à la main.

## 6. RAG : réingestion, correctif CUDA et test anti-hallucination

- **Réingestion :** le corpus compte désormais 1258 passages. Un premier essai avait échoué (carte graphique trop ancienne pour la version de torch) et laissé la collection vide ; les plongements sont maintenant **forcés sur le processeur** dans le script d'ingestion et dans le moniteur.
- **Fenêtre de contexte :** ollama travaille avec 4096 jetons par défaut. Avec 8 passages, le prompt (environ 7400 jetons) était tronqué et le début des instructions perdu. Le script de requête prend maintenant **4 passages par défaut**, estime la taille du prompt et avertit en cas de dépassement.
- **Citation recopiée :** le modèle recopiait mot pour mot l'exemple du prompt. L'exemple est devenu un modèle de forme explicitement non recopiable. Les refus de type « pas trouvé dans le contexte » sont reconnus et ne déclenchent plus de fausse alerte.
- **Test sur 3 essais :** résultat amélioré, mais un essai sur trois recopie encore un passage hors sujet ; la garde actuelle ne détecte pas cette incohérence. Limite connue, notée dans la compétence du pont d'agent.

## 7. Documentation et sauvegardes

- **Guide des scripts :** mis à jour (819 lignes) et mis en PDF par un nouveau générateur ReportLab ; l'ancien PDF est resté intact.
- **Cartes du cluster :** trois cartes SVG intégrées dans un PDF privé de 11 pages, rangé hors git.
- **Sauvegarde des secrets :** rotation ajoutée (2 archives gardées sur Proton) et document de méthode en Markdown et PDF. Rappel : le jeu 6 démarre déjà en envoi réel, la touche d bascule vers la simulation (une erreur d'instruction a été corrigée dans tous les documents).
- **Bonnes pratiques Claude Code :** nouvelle section ajoutée au wiki.
- **Carte CLAUDE.md et compétences :** PDF rangé dans le dossier des audits de compétences, version Markdown en local.

## 8. Audits en lecture seule

Plusieurs audits de l'historique (références, secrets, adresses électroniques, motifs d'adresses) ont confirmé qu'il ne reste aucun identifiant dans le code (725 commits) ni dans le wiki (465 commits), à l'exception d'un résidu connu (un nom de domaine interne dans la branche inbox-ia, décision : pas de nouvelle purge). Un bundle post-purge vérifié a été copié sur le disque Toshiba.

## 9. Mise à jour des fichiers de règles

- **CLAUDE.md racine :** matériel corrigé (i7-7500U, 2 cœurs / 4 threads, 16 Go), nouvelle section de règles propres au projet (audit, sauvegardes, mesures).
- **CLAUDE.md global :** règles de collaboration valables partout (jamais de push forcé, valeurs secrètes masquées, copie .bak avant modification).
- **Compétences :** riemann-agent-bridge (k=4, garde de citation, limites) et riemann-security-review (section sur ce que GitHub conserve après un filter-repo, exception pour le push forcé avec garde de version).
- **STACK et Handoff public :** STACK complété (disque de clone, RAG) ; Handoff public avec un résumé sans détail d'infrastructure.

## 10. Livraison git

Tout a été poussé : dépôt de code (branche Riemann_Lab_IA, plus portage sur Riemann_Lab_C pour les correctifs concernés) et wiki. Dernier commit de code : fcbafd1. Aucun commit ni push n'a été fait sans « go » explicite.

## 11. Ce qui reste à faire

| Point | Détail |
|---|---|
| Support GitHub | demande à envoyer par hprzeta : PR 6 et anciens sommets du wiki encore référencés |
| Branche Riemann_Lab_C | rattraper les commits manquants et les vagues V1 à V3 des compétences, puis y porter agent-bridge et security-review |
| Branche main | en retard sur presque tout ce qui est récent |
| Fichiers non suivis | auditer les 22 fichiers non suivis et 3 suppressions avant tout commit |
| Tests réels | commande de bascule WireGuard ; jeu 6 (phrase saisie par hprzeta, sans la touche d) puis test de restauration |
| Sauvegarde PC3 | lire le journal rclone de la nuit du 03 au 04 ; supprimer le fichier témoin de pipeline sur PC1, PC3 et Proton |
| Angle mort | zeta-backup-status et zeta-proton ne voient pas tout ; à corriger |
| Jeton DDNS | rotation reportée (à rouvrir si le jeton a été vu en clair) |
| Nettoyage | 4 bundles (dont la copie Toshiba), copies du vault dans exports, fichiers .bak et dossier de sauvegarde du 05/10 |
| Divergence matériel | PC2 et PC3 : STACK et inventaire du 03/10 ne concordent pas |
| Thermique | pic de 94 °C rapporté (non revérifié) ; relevé vérifié à 59 °C |

---
*Archive de session — hprzeta — 2026-10-04 / 05*
