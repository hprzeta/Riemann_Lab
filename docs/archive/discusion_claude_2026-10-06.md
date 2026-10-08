# Archive de session — 6 octobre 2026

> Session du 06/10, de la reprise (« point projet ») jusqu'au « bye bye » de 17h15 environ. Quatre chantiers : vérification de la sauvegarde nocturne vers Proton et retrait du fichier témoin, tri des fichiers non suivis du dépôt, alias SSH à bascule automatique maison / déplacement, et règle de capture de session. Aucun commit de code ; un seul push, côté wiki.
>
> **Capture brute de la session : absente.** Une capture a bien été lancée à 17h05 mais dans un autre terminal que celui de Claude Code ; elle ne contient que des invites vides (538 octets). La conversation complète reste disponible dans le fichier de transcription que Claude Code tient lui-même (dossier de projet de Claude Code, un fichier .jsonl par session, environ 2 Mo pour celle-ci).

## 1. Reprise : « point projet »

**Consigne de hprzeta :** « point projet ».

Lecture du bloc de reprise du Handoff local et résumé en trois lignes : dernier commit `43222bf` sur `Riemann_Lab_IA`, chantier précédent (purge des identifiants réseau, RAG ré-ingéré, sauvegarde « hors git »), prochaine action = lire le journal de la copie nocturne vers Proton. Point d'attention relevé : `Riemann_Lab_C` en retard de trois commits d'outils et `main` sans les quatre.

## 2. Vérification de la sauvegarde nocturne (nuit du 03 au 04/10)

**Consigne de hprzeta (extrait) :** lire le journal de la copie rclone sur PC3, vérifier chez Proton que le fichier témoin est présent, tableau de synthèse, puis s'arrêter.

**Obstacle :** PC3 injoignable en SSH depuis PC1 (délai dépassé). Cause trouvée par hprzeta : PC1 était connecté au partage de connexion du téléphone au lieu de la box ; après reconnexion à la box, SSH a fonctionné.

**Constats (vérifiés dans le journal de PC3) :**

| Point | Résultat |
|---|---|
| Tâche | copie quotidienne à 02h00, compte `pjexosql`, du dossier de sauvegarde vers Proton Drive |
| Nuit 03 → 04/10 | 27 fichiers sur 27 transférés en 48,6 s, aucun échec, témoin copié à 02h00m12 |
| Avertissements | 422 « existe déjà » (bénin, fichiers remplacés), 429 « trop de requêtes » (rclone réessaie), 401 « jeton expiré » certaines nuits (rattrapé) |
| Nuits 05 et 06/10 | « rien à transférer » |
| Contrôle quotidien (8h) | « Proton répond » tous les jours jusqu'au 06/10 |
| Témoin | présent sur PC1 et PC3 (71 octets, 03/10 21h33) ; **confirmé chez Proton par hprzeta dans l'interface web** |

Le listage direct chez Proton n'a pas été fait : le compte SSH `hprzeta` n'a pas la configuration rclone du compte `pjexosql`, et hprzeta a demandé de ne pas toucher à cette configuration ni au jeton.

## 3. Suppression du témoin

**Consigne de hprzeta :** supprimer le témoin sur PC1 et PC3 seulement, un fichier à la fois, sans joker, sans changer les droits ; hprzeta supprime lui-même chez Proton.

- PC1 : supprimé et vérifié (117 → 116 fichiers dans le dossier de journaux).
- PC3 : suppression refusée (dossier appartenant à `pjexosql`, `hprzeta` hors du groupe). Arrêt, comme demandé. Après accord explicite de hprzeta pour un `sudo`, la commande interactive a été lancée par hprzeta lui-même (je ne peux pas saisir de mot de passe) ; vérification ensuite : témoin absent de PC3, 117 fichiers.
- Rappel donné : supprimer chez Proton **après** PC3, pour éviter que la copie de 02h00 le recopie.

## 4. Tri des fichiers non suivis (analyse, puis actions validées)

**Consigne de hprzeta (extrait) :** pour chaque fichier non suivi, chercher IP, MAC, clés, jetons sans afficher les valeurs ; tableau avec proposition ; ne rien modifier ; attendre sa validation fichier par fichier.

**Résultat de l'analyse :** 23 entrées, soit 36 fichiers une fois les dossiers développés (le chiffre attendu était 21 ou 22).

| Catégorie | Nombre |
|---|---|
| Propres | 28 |
| À masquer ou régénérer avant commit | 6 |
| À garder hors dépôt | 2 |

**Alerte :** un ancien PDF de la documentation sécurité contient très probablement un **jeton DNS dynamique réel** (début d'un identifiant coupé par un retour à la ligne, deux occurrences). Hors git, mais le dossier est copié par la sauvegarde nocturne vers PC3 puis Proton. La rotation du jeton reste à décider par hprzeta (en LAN, jamais par le tunnel).

**Décisions de hprzeta, puis actions :**

| Fichier ou groupe | Décision | Action faite |
|---|---|---|
| archive de configuration de PC3 (clés, tâches planifiées, configuration SSH) | hors dépôt | déplacée dans un dossier privé hors dépôt (droits 700) |
| PDF sécurité avec le jeton | hors dépôt | déplacé au même endroit |
| 6 fichiers avec adresses privées | masquer les sources puis régénérer les PDF | 3 sources masquées (2 adresses, 4 adresses fausses d'un test RAG, 1 adresse) ; le fichier d'audit du 12/09 ne contenait que le nom du fournisseur, rien à masquer |
| PDF de la session du 20/09 | régénérer | régénéré avec le script du projet (lualatex), 3 pages, aucune adresse |
| Guide RAG BrainVault pour débutant | régénérer | régénéré avec pandoc et lualatex (12 pages au lieu de 9, mise en page différente), aucune adresse ; remplacé |
| Formation Zêta et Hypothèse de Riemann (19 pages) | régénérer | **non régénérable** : son Markdown est une conversion avec perte (37 images omises, 74 images dans le PDF d'origine, page de garde perdue) ; le PDF d'origine (ReportLab) n'a pas de générateur dans le dépôt ; déplacé hors dépôt |
| sources d'IA tierces (7 fichiers) | hors git | laissées en place, jamais ajoutées |

**Vérification demandée par hprzeta sur le dossier md/ :** 63 fichiers Markdown ; 78 des 90 PDF ont un équivalent du même nom, 12 n'en ont pas (certains existent ailleurs ou sous un autre nom). Six Markdown locaux contiennent encore des adresses (dossier ignoré par git, à ne jamais synchroniser vers un dépôt public). Deux PDF suivis citent le nom du fournisseur DNS dynamique, sans valeur ; contexte non relu.

**Les 26 fichiers restants, présentés en neuf groupes (A à I) :** scripts de cours (2), test A/B du scan (1), schémas et image (4), audits des skills (3), rapports du 12/09 (2), PDF d'optimisation et matériel (3), RAG et vault (6), archive de session du 20/09 (2), suivi du wiki et méthode de sauvegarde chiffrée (3). **Aucun commit, aucun ajout à l'index** ; la validation groupe par groupe de hprzeta est en attente. Décision ouverte : la suppression de l'ancien PDF de la documentation du cluster dont le remplaçant est ignoré par git.

## 5. Alias SSH à bascule automatique maison / déplacement

**Constat de hprzeta :** à distance (tunnel actif), les quatre alias expiraient car ils visaient des adresses du réseau local ; le tunnel ne route que son propre réseau.

**Consigne :** que les quatre alias marchent à l'identique à la maison et à distance, sans saisir de saut à la main ; une étape à la fois, sauvegarde datée avant toute modification, aucun secret affiché, scripts de session et de surveillance non modifiés.

- **Étape 1 (lecture seule) :** les quatre alias pointaient en adresse directe, sans saut ni délai court. La détection des scripts (ping du bastion) se trompe si le tunnel est actif à la maison, ou monté mais mort en déplacement.
- **Étape 2 (proposition) :** détection par test du port 22 de **chaque nœud** plutôt que par ping du bastion, car elle teste la joignabilité de la cible elle-même. Cas limite : un autre réseau avec la même plage d'adresses ; la clé d'hôte refuserait une machine homonyme.
- **Étape 3 (application) :** fichier de configuration SSH réécrit après sauvegarde datée ; vérification de la syntaxe pour les quatre alias en contexte maison (aucun saut, délais de 5 s).
- **Incident :** le test affichait « Connection … succeeded » avec l'adresse ; quatre adresses privées du réseau local se sont affichées dans la conversation. Corrigé en rendant le test silencieux. Les adresses restent visibles dans cet échange, ce qui est irréversible de mon côté.
- **Étape 4 :** bloc modèle d'ajout d'un nouveau poste (plage .57 à .70), sans adresse réelle, intégré à la documentation.

**Tests réels par hprzeta :** à distance, tunnel monté, les quatre alias répondent (le bastion directement par le tunnel, les trois autres par saut), en 2 à 3 secondes ; retour au réseau local, les quatre repassent en direct sans saut. Le transfert TCP sur le bastion est donc bien autorisé.

**Limites :** cas d'un autre réseau avec la même plage non testé sur un vrai réseau ; les scripts de session, de surveillance et de bascule du tunnel gardent leur détection par ping (défauts connus, volontairement non modifiés).

## 6. Mise à jour de la documentation et push du wiki

**Consigne de hprzeta :** « pousse ce qui faut pousser, mets à jour Handoff, guide, etc. »

- Aucun commit de code en attente à pousser ; seules trois suppressions de fichiers déplacés étaient en attente.
- Wiki : journal, Handoff et guide d'accès distant WireGuard mis à jour (nouvelles sections « alias SSH à bascule » et « ajout d'un nouveau poste »). Audit des lignes ajoutées (adresses, clés, jetons) : zéro occurrence après reformulation d'une plage générique. Commit `0dc2146`, poussé sur `master` sans force.
- Handoff local réécrit (bloc de reprise), diagnostic du cluster ajouté dans le dossier privé des diagnostics, indexé et publié sans adresse. Sauvegardes datées dans un dossier de sauvegarde du jour.

## 7. Règle « bye bye » et capture de session

**Questions de hprzeta :** quel script note la session ? est-ce celui du « bye bye » ? le script de capture ne marche pas, pourquoi ?

| Outil | Ce qu'il fait | Qui le déclenche |
|---|---|---|
| Règle « bye bye » | résumé narratif en PDF (tableaux, conclusions, consignes citées, sans code) dans le dossier d'archives, via le script de génération PDF avec lualatex | moi, quand hprzeta le demande ; ce n'est pas un script automatique |
| Script de capture | enregistre le terminal brut, puis génère un Markdown propre | hprzeta, **avant** de lancer Claude Code, dans le même terminal |
| Transcription de Claude Code | conversation complète, enregistrée automatiquement, un fichier par session | personne (automatique) |

**Pourquoi la capture était vide :** elle enregistre uniquement le terminal où elle tourne ; Claude Code tournait dans le terminal intégré de VS Code, déjà ouvert. Pour la dernière capture exploitable (juin, 3 Mo), l'ordre avait été respecté.

**Décisions :** règle « bye bye » conservée et étendue (vérification de la capture à chaque fin de session, rappel de taper `exit` deux fois si elle est active, mention dans l'archive, pas de commit des captures sans audit) ; alias `zeta-capture-conv` créé dans le fichier de configuration du shell (sauvegarde datée) ; hprzeta a demandé de noter en **priorité 1 pour la prochaine étape** l'écriture d'un convertisseur de la transcription de Claude Code vers du Markdown lisible, car il lance Claude Code de façons variées.

## 8. Ce qui restait à faire à la fin de la partie A

1. **Priorité 1 :** écrire le convertisseur de la transcription de Claude Code (fichier .jsonl) en Markdown lisible, en lecture seule, sans longues sorties d'outils.
2. Validation, groupe par groupe (A à I), des 26 fichiers non suivis, puis un seul commit depuis `Riemann_Lab_IA` après audit des lignes ajoutées ; décider de l'ancien PDF de la documentation du cluster et d'ignorer les sources d'IA tierces et les archives de configuration dans le fichier d'exclusion de git.
3. Décider de la rotation du jeton DNS dynamique ; traiter les copies du PDF au jeton et de la Formation déjà présentes sur PC3 et chez Proton.
4. Rattraper `Riemann_Lab_C` (trois commits d'outils) ; `main` n'a aucun des quatre commits.
5. Tester la bascule SSH sur un autre réseau à même plage d'adresses ; décider si les scripts de session et de surveillance adoptent la même détection.
6. Points hérités des sessions précédentes : jeu 6 de la sauvegarde « hors git » jamais exécuté en réel, nettoyage des sauvegardes temporaires, MCP, documentation du stockage, etc. (voir le Handoff).

---

# Partie B — session du soir (06/10, de 21h30 à minuit environ)

> Nouvelle session Claude Code, ouverte après la partie A (un seul fichier d'archive pour la journée). Elle a réalisé la « priorité 1 » de la partie A, trié et commité les 26 fichiers non suivis, aligné les quatre branches du dépôt, puis mis à jour le Handoff et le wiki. **Capture brute de cette session : absente** (aucune capture de terminal n'a été lancée avant Claude Code) ; la transcription automatique de Claude Code est disponible et a été convertie par le nouvel outil de la section 10.

## 9. Reprise : « point projet »

**Consigne de hprzeta :** « point projet ». Le bloc de reprise du Handoff local a été affiché tel quel, avec un résumé en trois lignes : pipeline v16 (1,6 min pour T=100k, 20/20 LMFDB), dernier commit `43222bf`, prochaine action. Rien n'a été exécuté sans accord.

## 10. Convertisseur de transcription (priorité 1 de la partie A)

**Consigne de hprzeta :** « priorité 1 . puis on le teste avec l'alias `zeta-convert-jsontomd` ».

| Élément | Choix |
|----|----------------|
| Script | `scripts/zeta_jsonl_to_md.py` (bibliothèque standard Python), commit `35ad4e7`, poussé |
| Alias | `zeta-convert-jsontomd` dans `~/.bashrc` (sauvegarde datée) ; sans argument : session en cours ; option de liste pour choisir |
| Sortie | dossier des transcriptions, fichier en mode 600, dossier ignoré par git |
| Conservé | messages de hprzeta et textes de Claude ; appels d'outils réduits à une ligne |
| Omis | sorties d'outils, raisonnement interne, balises de contexte |
| Masqué | adresses IPv4/IPv6, MAC, e-mails, noms de domaine dynamique, jetons, clés privées, valeurs réelles du cluster (lues dans un fichier hors git) |
| Garde-fou | une seconde passe de masquage ne doit rien changer, sinon le fichier n'est pas écrit |

**Tests :** trois sessions, dont la plus lourde (11 Mo, 4 443 lignes) réduite à 320 Ko ; une recherche indépendante ne trouve aucune adresse ni MAC résiduelle ; il ne reste que des mots (nom du service, préfixes de jeton) dans des discussions d'audit. **Limites :** sorties d'outils absentes (elles restent dans le fichier d'origine), masquage volontairement large, les 4 443 lignes n'ont pas été relues en entier.

## 11. Tri des fichiers non suivis, groupes A à I

**Consignes de hprzeta :** « go groupe A », puis B, C, D, E, F, G, H, I, « archive du jour ». Pour chaque groupe : lecture du contenu, audit (adresses, secrets, e-mails, chemins personnels, texte extrait des PDF), commit séparé depuis `Riemann_Lab_IA`, sans pousser.

| Groupe | Contenu | Commit | Point notable |
|---|--------|----|-----------|
| A | générateurs du cours (PDF, page wiki) | `e21a309` | non exécutés |
| B | test A/B du balayage v13 contre v16 | `2084ac1` (branche C) | écrit pour le v16 de C ; sur IA il planterait (paramètres absents) ; **question posée, hprzeta a choisi la branche C** |
| C | 3 schémas SVG + plan de continuité | `50af109` | PNG identique octet pour octet à l'ancien, simple déplacement ; schémas relus visuellement |
| D | synthèse des audits de skills (MD+PDF) + copie d'un skill | `bfd7481` | |
| E | 2 rapports du 12/09 | `202a819` | une phrase du rapport à reformuler (historique non purgé) |
| F | 3 PDF dont recommandations SSD externe | `127f478` | |
| G | guides RAG et vault | `fc782df` | ancien guide (avec adresses) supprimé, remplacé par la version masquée |
| H | archive du 20/09 | `7115134` | adresses déjà masquées |
| I | méthode de sauvegarde chiffrée, corrections wiki KaTeX | `85e992b` | aucune phrase de passe ni clé |
| Archive du 06/10 (partie A) | | `06e2367` | |

**Notés, non corrigés :** plan de continuité périmé (compte de zéros ancien, emojis en carrés, faute dans l'adresse de contact) ; deux schémas utilisent une fonctionnalité SVG que les navigateurs gèrent mais pas ImageMagick ; la RAM de PC2 et le modèle de PC3 diffèrent toujours entre les schémas (inventaire du 03/10) et `STACK.md`.

## 12. Audit global et push

**Consigne de hprzeta :** « audit global puis push ». Audit sur 27 fichiers (lignes ajoutées, texte des PDF, valeurs réelles du cluster, adresses, e-mails, UUID, jetons, noms de fichiers sensibles, taille) : aucun résultat. Push sans `--force` : `Riemann_Lab_IA` `35ad4e7` → `06e2367`, `Riemann_Lab_C` `942b5e3` → `2084ac1`. Limite : les PDF n'ont pas été relus page par page.

## 13. Mise à jour du Handoff et du wiki

**Consignes de hprzeta :** « mets à jour le Handoff », puis « go mets à jour le wiki ». Handoff local réécrit (règle « bye bye » étendue au convertisseur, bloc de reprise) ; wiki : `Handoff.md` et `JOURNAL.md` mis à jour (commit `38ab43f`), texte sans détail d'infrastructure, audit des lignes ajoutées à zéro.

## 14. Trois décisions de rangement

**Consigne de hprzeta :** « on enchaîne ». Trois questions posées, recommandations suivies :

| Point | Décision | Résultat |
|------|-----|----------|
| Suppression du PDF de documentation du cluster | restaurer | restauré, aucun commit (son remplaçant est ignoré par git) |
| Dossier des textes d'IA tierces | l'ignorer | règle ajoutée au `.gitignore` (`03df806`), fichiers intacts sur le disque |
| Script de test A/B non suivi sur IA | le laisser | puis devenu suivi par l'alignement des branches |

## 15. Alignement des quatre branches

**Consignes de hprzeta :** « go point 1 », « go étape 1 », « go étape 2 », « go point 1 » pour `main`, puis pour `Riemann_Lab_Test`.

**Constat (lecture seule).** Base commune du 16/08 ; les purges ont réécrit les historiques, donc la comparaison par commit n'était pas fiable et celle par arbres de fichiers l'était. IA était la plus avancée (infrastructure, skills, documentation), mais C avait du code que IA n'avait pas, dont la **persistance du CSV avant le rescan** (ajoutée après la perte de 31 h du run T=5M).

| Étape | Action | Résultat |
|--|---------|-----------|
| 1 | reporter sur IA les gardes `.gitignore` sur les dossiers de secrets (présentes seulement sur C) | `59559c3` |
| 2 | fusion d'essai de C avec IA dans un worktree isolé | 8 conflits de purge tranchés côté IA zone par zone ; artefacts de purge côté C écartés ; 91 fichiers Python et 31 scripts bash sans erreur de syntaxe |
| 2bis | masquage de 14 identifiants de volume d'un rapport de clonage (choix de hprzeta : « les masquer ») | `09a40a4`, PDF régénéré |
| 3 | push de IA et de C | `09a40a4` pour les deux (44 et 60 commits) |
| 4 | `main` | aucun changement propre ; fusion avec arbre identique à IA (vérifié), `b86cf96` ; push demandé « tel quel » |
| 5 | `Riemann_Lab_Test` | IA + 2 fichiers d'expérience d'avril 2026 conservés, `3ca0405` |

**Constat important :** GitHub Pages est servi par `Riemann_Lab_IA` (dossier `docs`), pas par `main` ; la reconstruction a été vérifiée (build réussi, page identique au dépôt). **Non masqués, à décider :** quelques identifiants de disque déjà publics (rapport de clonage, un script) et un DNS public utilisé comme sonde de routage ; ils sont maintenant sur les quatre branches, dont la branche par défaut.

## 16. Nettoyage et dernière mise à jour

**Consigne de hprzeta :** « go nettoie puis mets à jour Handoff et wiki ». Trois worktrees et trois branches temporaires supprimés (têtes vérifiées identiques aux distants ; deux suppressions ont d'abord été refusées par git sans danger). Handoff local et wiki mis à jour (commit wiki `17bdc91`). **Consigne suivante :** « 3 » : compléter la présente archive.

## 17. Ce qui reste à faire

| Point | Détail |
|-----|-------------|
| Jeton DNS dynamique | rotation à arbitrer par hprzeta, en LAN, jamais via le tunnel ; copies d'un PDF au jeton probable déjà dans la sauvegarde nocturne vers Proton |
| Identifiants de disque publics | décider de les masquer ou non (commit sur IA puis propagation aux trois autres branches) |
| Documentation | plan de continuité à régénérer ; divergence de matériel schémas / `STACK.md` ; un dossier d'archives compressées non ajouté au `.gitignore` |
| Réserves de la partie A | jeu 6 de la sauvegarde « hors git » jamais exécuté en réel, test de la bascule SSH sur un autre réseau, MCP, documentation du stockage (voir le Handoff) |
| Capture de session | lancer le script de capture **avant** Claude Code pour avoir la capture brute ; sinon utiliser le convertisseur |

---

# Partie C — fin de session (nuit du 06 au 07/10)

> Suite et clôture de la session du soir : défaut des PDF corrigé, archive commitée, propagation sur les quatre branches, mise à jour du Handoff et du wiki, puis « bye bye ».

## 18. Correction du script de génération des PDF

**Consigne de hprzeta :** « go corrige le script puis commit l'archive ».

**Défaut.** En régénérant la partie B, la dernière colonne de chaque tableau était coupée dans le PDF ; l'ancien PDF du 06/10 avait déjà le même défaut (troisième colonne du tableau « bye bye » absente). **Cause :** le script de génération lisait le Markdown avec le lecteur `gfm` de pandoc, qui ne calcule pas de largeur de colonne, donc les cellules ne passaient pas à la ligne.

| Élément | Décision |
|----|----------------|
| Correctif | lecteur `markdown` de pandoc avec les extensions qui reproduisent `gfm` (liste sans ligne vide, liens nus, texte barré, cases à cocher) ; une ligne de commande et un commentaire d'en-tête |
| Précaution | sauvegarde datée du script avant modification ; commit séparé du commit de l'archive |
| Commits | script `836f873`, archive (partie B, 9 pages) `c1be1b8` |

**Non-régression** (anciens et nouveaux PDF comparés mot à mot, sur 7 documents) :

| Document | Résultat |
|------|-------------|
| archive du 20/09 (sans tableau) | identique |
| archive du 04/10, synthèse des skills (tableaux) | texte coupé restitué (+114 et +1 109 mots) ; les « mots perdus » ne sont que des fragments tronqués de l'ancien rendu |
| 3 pages du wiki riches en formules | même nombre de pages, texte identique ou quasi (un en-tête de tableau se replie sur plusieurs lignes) |
| un guide du dépôt | échoue à la génération avec l'ancien comme avec le nouveau script ; non investigué |

**Limite :** les PDF déjà commités des anciennes archives gardent le défaut tant qu'ils ne sont pas régénérés.

## 19. Push et propagation sur les quatre branches

**Consigne de hprzeta :** « pousse et propage aux 3 autres branches ». Audit avant chaque push (3 fichiers, 99 lignes ajoutées, 1 PDF) : aucun résultat. Aucun `--force`.

| Branche | Avant | Après | Méthode |
|-----|---|---|-------|
| `Riemann_Lab_IA` | `09a40a4` | `c1be1b8` | push direct |
| `Riemann_Lab_C` | `09a40a4` | `c1be1b8` | fast-forward |
| `main` | `b86cf96` | `ded1b78` | fusion de IA, 0 conflit |
| `Riemann_Lab_Test` | `3ca0405` | `ac702b3` | fusion de IA, 0 conflit |

Arbres : `main` et C identiques à IA ; Test = IA + 2 fichiers d'expérience. Le site public est servi par `Riemann_Lab_IA` : reconstruction vérifiée (build réussi, page en ligne). Worktrees et branches temporaires supprimés.

## 20. Mise à jour du Handoff et du wiki

**Consigne de hprzeta :** « go mets à jour le Handoff et le wiki ». Handoff local mis à jour (archive complétée, correctif du script, propagation, prochaines étapes) ; wiki : `Handoff.md` et `JOURNAL.md` (commit `20282d7`, poussé), texte sans détail d'infrastructure, audit des lignes ajoutées à zéro.

## 21. Clôture : « bye bye »

**Capture brute du terminal : absente** pour toute la journée (la capture de 17h05 est vide ; aucune n'était active le soir). Il n'y a donc rien à arrêter. **Substitut :** la transcription automatique de Claude Code a été convertie en Markdown propre par le nouvel outil (1 385 lignes, 34 messages de hprzeta, 91 réponses, contrôle de seconde passe propre), dans le dossier ignoré par git, non commitée. **Pour la prochaine fois :** lancer le script de capture **avant** Claude Code, dans le même terminal ; sinon utiliser le convertisseur.

**Ce qui reste ouvert (voir la section 17) :** rotation du jeton DNS dynamique ; masquage ou non de quelques identifiants de disque déjà publics ; régénération des PDF des anciennes archives avec le script corrigé ; échec de génération d'un guide ; plan de continuité à régénérer ; divergence de matériel entre les schémas et `STACK.md`.

---
*Archive de session du 06/10/2026 (parties A, B et C) — rédigée à la demande de hprzeta (« bye bye »).*
