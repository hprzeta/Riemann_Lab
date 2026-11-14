# Archive de session — 05/11/2026

Projet Riemann_Lab — sessions Claude Code du 05/11/2026 (branche Riemann_Lab_IA). **Partie A** : session de 18h56 (sections 1 à 8). **Partie B** : session de 20h19 (sections 9 à 22).

**Turbo Zêta :** RESTAURÉ (vérifié : 4 CPU à leur gouverneur initial (cpu0=powersave), swappiness 10) — première étape du « bye bye » (Partie A, puis à nouveau en fin de Partie B, ligne identique).

**Captures brutes :** Partie A : `claude-traitement-journalier/session_20261105_1856.log` ; Partie B : `claude-traitement-journalier/session_20261105_2019.log` (processus *script* actif, le `.md` associé sera généré au second `exit`). Une capture intermédiaire `session_20261105_1920.log` existe sans `.md`.

Cette archive reprend la narration, les tableaux et les conclusions de la session ; aucun extrait de code n'y figure.

---

# PARTIE A — session de 18h56

## 1. Point projet

> point projet

Bloc de reprise du Handoff affiché tel quel, puis résumé en trois lignes : pipeline V17, dernier commit `c92c202` (03/11), prochaine action soumise à l'OK de hprzeta. Rien n'a été exécuté à ce stade.

## 2. Décision : jeu fusionné gardé comme référence 5·10⁶

> garder le jeu fusionné comme référence 5·10⁶

Vérification en lecture seule : fichier de 904 Mo, 10 016 474 zéros, somme de contrôle SHA-256 enregistrée, dossier `calculs/` ignoré par git, CSV V13 d'origine intact. Décision consignée dans le Handoff local et dans la mémoire du projet. Publication : décision à part, non prise.

## 3. Rescan décalé en phase pour la V17

> rescan décalé en phase pour la V17

**Constat sur le code (mesuré).** Le rescan démarrait à `seg_a` avec un pas STEP/2 : sa grille contenait donc exactement celle du scan principal, et un zéro collé à un point de grille restait invisible.

**Modification.** Constante `RESCAN_PHASE = 1/3` : les workers de rescan démarrent à `seg_a + STEP/3`. La grille du rescan est désormais à au moins STEP/6 de la grille principale. Copie `.bak-20261105` faite avant modification.

**Test (mesuré).** Sur les 97 zéros du complément, avec une grille placée à 3·10⁻⁷ du zéro : 97/97 retrouvés avec l'ancien départ, 97/97 avec le départ décalé. Pas de régression, mais le test ne discrimine pas : le gain n'est pas démontré.

## 4. Commit et synchronisation des 4 branches

> commit et synchronise les 4 branches

Audit des lignes ajoutées propre (aucun secret, adresse ou jeton). Commit sur `Riemann_Lab_IA` puis cherry-pick sur les trois autres branches, poussées sans `--force` et vérifiées alignées sur `origin`.

| Branche | Commit |
|---|---|
| Riemann_Lab_IA (source) | `7e583d4` |
| Riemann_Lab_C | `0f585d0` |
| Riemann_Lab_Test | `abc8454` |
| main | `5f02190` |

## 5. Synchronisation de PC2 et mise à jour du Handoff

> go synchroniser PC2 — oui, mets à jour le Handoff

PC2 avait l'ancienne version et aucun calcul en cours. Ancien fichier conservé en `.bak-20261105`, copie faite, somme de contrôle identique des deux côtés, compilation vérifiée sur PC2. Les deux autres fichiers V17 de PC2 n'ont pas été revérifiés depuis le 03/11. Handoff local mis à jour (copie `.bak2` préalable).

## 6. Rejeu de validation sur les 13 isolés

> go rejeu long de validation

**Méthode.** Grille exacte du worker V13 d'origine (pas lu dans le CSV V13), 13 isolés, petites fenêtres, code V17. Trois scans comparés.

| Scan | Zéros retrouvés |
|---|---|
| Principal (grille exacte V13) | 13/13 |
| Rescan ancien | 13/13 |
| Rescan décalé | 13/13 |

**Conclusions.**
- L'hypothèse de la grille est reconfirmée : les 13 zéros sont à 1,1·10⁻⁷ – 5,7·10⁻⁷ d'un point de grille V13.
- Le scan principal de la V17 les retrouve déjà tous : le décalage de phase ne peut rien y ajouter. **Aucun gain mesurable.**
- Cause plausible, **non testée** : correctifs V17 absents de la V13 (marge de bracket de 2 ulp, élargissement du bracket). V13 et V17 n'ont pas été comparés.
- Limite : petites fenêtres seulement ; un run V17 complet sur [14 ; 1,77·10⁶] (environ 3,25 millions de zéros, environ 2 h 15) n'a pas été fait.

hprzeta a choisi de clore ici (option 1) : résultat consigné dans le Handoff, `RESCAN_PHASE` conservé comme garantie théorique.

## 7. Documentation du wiki

> go documentation — go commit et push du wiki

Nouvelle entrée du `JOURNAL.md` (2026-11-05) et résumé « REPRENDRE ICI » dans le `Handoff.md` du wiki, sans détail d'infrastructure. Audit propre, puis commit `c388cd7` poussé sur `master`, aligné sur `origin/master`. Les fichiers `.bak` et `Dossier-md.md` non suivis n'ont pas été ajoutés.

## 8. État final

- Quatre branches du dépôt de code et wiki à jour sur `origin`.
- Jeu de référence 5·10⁶ : fusionné, hors dépôt, publication non décidée.
- Ouvert : run V17 complet sur [14 ; 1,77·10⁶] (non jugé nécessaire) et publication éventuelle du jeu de référence.
- Non committés : les archives de session (cette archive comprise) et les captures brutes.

---

# PARTIE B — session de 20h19

## 9. Point projet

> point projet

Bloc de reprise du Handoff affiché en extrait (le bloc fait 122 Ko) et résumé en trois lignes : pipeline V17, dernier commit `7e583d4`, aucune action imposée.

## 10. Lecture des sessions du 01/11 au 05/11 (lecture seule)

> Mission : lecture seule. Ne lance aucun calcul, ne modifie, ne déplace et ne supprime aucun fichier… questions A à F avec preuve ou « aucune trace ».

32 fichiers de session recensés. Réponses établies :

| Question | Réponse | Preuve |
|---|---|---|
| Run distribué réel depuis le 01/11 ? | Oui : V15 à T=20000 le 01/11 (22 491 zéros, 325 z/s, Turing COMPLET), V17 à T=1000 le 03/11 (649 zéros) | dossiers de calcul et rapports |
| Version de `zeta_run.sh` | V17 (commit `43134dd`) | `zeta_run.sh:56` |
| `zeta_distribute.py` | basculé de V15 à V17 par `931a5bf` | `git show --stat` |
| Modifications non commitées du 01/11 | toutes commitées le 01/11 | `git log` |
| « 96 » contre « 97 » | aucune trace du 96 dans les sessions ; explication déduite plus bas | voir section 11 |

Fiches 2.4 (suivi) et 2.5 (pannes) : aucune trace dans les sessions. Limites dites : sessions du 01/11 non lues en entier, `.log` illisibles à plus de 90 %.

## 11. Vérifications des points ouverts (étape 1)

> Étape 1 : vérifier les points ouverts a à g, tableau fait / non fait / indéterminé avec preuve.

| Point | Résultat |
|---|---|
| Commit `931a5bf` | fait les deux : bascule de `zeta_distribute` en V17 et correctif V17 (vérifié) |
| Empreintes PC1/PC2 | identiques pour les trois fichiers Python de calcul (vérifié) ; `illinois_arb.c` différent sur PC2 |
| 96 → 97 | déduit : l'ancien `N_exact` était faux de −1 (10 016 377 sur 10 016 473 attendus) ; attendu corrigé 10 016 474 = 10 016 377 + 97 |
| « Manquants : -1 » du run V15 | déduit : run lancé avant la correction du module de validation de Turing |
| Script de synchronisation de PC2 | existe, non adapté à la V17 |

## 12. Guide de run unique

> go source (15), archive le reste, fichier d'ajouts dans Téléchargements

Le guide devient un fichier unique, local (`md/Guide_Run_Zeta.md`), avec un PDF du même nom commité (`pdf/Guide_Run_Zeta.pdf`). 20 anciennes copies `.md`/`.zip` et 18 PDF archivés (jamais supprimés). Les ajouts v0.16 sont fusionnés : fiches 2.2 bis à 2.6, écarts E50 à E55, pistes D41 à D50, étiquette « mesuré en V16 » sur les fiches 1.2 à 1.10. Règle permanente écrite dans `CLAUDE.md`. Commit `d50b7f7` et cherry-picks `4ac00ac`, `16d1f26`, `467541a`, poussés sans `--force`.

## 13. Resynchronisation de PC2

> go marche étapes 1 à 3

Découverte : PC2 a deux arborescences ; `zeta_distribute` vise celle dont le code C était ancien. Sauvegardes faites, fichier source copié, bibliothèque recompilée sur PC2 (jamais copiée), test distribué à T=1000 : 649 zéros, Turing COMPLET, écart nul avec le run du 03/11. Limite dite : à T=1000 le second pas de Newton n'est pas sollicité.

## 14. Runs distribués V17 à T=20000 et T=100000

> fait tout ce qui est non fait avant le bye bye final

| Run | Zéros | Turing | Durée |
|---|---|---|---|
| T=20000 | 22 491 (comme en V15) | COMPLET | 0,53 min |
| T=100000 | 138 069 | COMPLET | 1,84 min |
| T=100000, PC1 seul | 138 069 | — | 2 min 40 s |

Comparaisons : 473 zéros sur 138 069 diffèrent de plus de 2 pas flottants entre PC1 seul et distribué (écart maximal 3,35·10⁻⁸), effet de la grille et non de PC2. V13 contre V17 sur t ≤ 10⁵ : même nombre, écart maximal 3,47·10⁻⁸.

## 15. Pannes d'un run distribué

Calcul de PC2 arrêté par PID : PC1 s'arrête en 27 s, sans orphelin, turbo et services intacts. Ctrl+C : PC2 sans orphelin, mais **le calcul de PC1 continuait seul et les services restaient arrêtés** ; réparé à la main. Deux de mes premiers envois de signal avaient raté leur cible (essais non comptés).

## 16. Corrections de code et documentation V17

> go audit + commit + cherry-pick des 3 fichiers — go push des 4 branches puis mets à jour le Handoff

Script de synchronisation de PC2 adapté à la V17 et testé ; page de documentation V17 créée dans le dépôt. Commits `1bdc998` (IA), `23f2460`, `cf0bc7e`, `89d8487`, poussés. Handoff mis à jour à chaque étape.

## 17. Points ouverts traités (première partie)

> traite les point ouvert

| Point | Résultat |
|---|---|
| Second pas de Newton isolé | 560 zéros, mêmes intervalles : erreur maximale 1,67·10⁻⁶ avec un seul pas, 1,89·10⁻¹⁰ avec le second ; plus proche du vrai zéro dans 280 cas sur 280 |
| Ctrl+C | corrigé : arrêt de PC1 et PC2, services redémarrés, code 130, 0 processus restant |
| Suivi (alias) | **ma première lecture était fausse** : les alias marchent avec le lanceur `zeta-distribute` ; seul défaut réel, le PID restait affiché après la fin d'un run, corrigé |
| Vitesses par défaut | passées à 1121 / 472 z/s ; T=100000 : 1,84 → 1,57 min |

Commit `423cbc0` (IA), `b8e2850`, `5367a58`, `4984a46`, poussés ; Handoff mis à jour.

## 18. Remesure à plus grand T

> fait les point ouver ok publication remesure test tmux et pente

Les débits dépendent de T :

| Run T=5·10⁵ | PC1 | PC2 | Mur |
|---|---|---|---|
| débits fixes 1121 / 472 | 11,90 min | 19,90 min | 19,96 min |
| débits interpolés en ln T | 14,37 min | 11,57 min | **14,41 min (−28 %)** |

818 415 zéros et Turing COMPLET dans les deux cas. Validé seulement entre 10⁵ et 5·10⁵ ; au-delà, valeurs figées à celles de 5·10⁵, à remesurer. Un modèle de coût ajusté ne tient que jusqu'à 5·10⁵ : inutilisable plus haut. Les deux runs diffèrent par 1 773 zéros à plus de 2 pas, maximum 2,06·10⁻⁷.

## 19. Test de tmux

L'erreur du 01/11 est **confirmée** : cause = terminal de type *dumb*. Avec un vrai type de terminal, l'attache au tableau de bord fonctionne (répartition PC1 74,8 % / PC2 25,2 % à T=5·10⁵). Testé dans un pseudo-terminal, pas dans une fenêtre graphique.

## 20. Zéros de pente 3 à 4,4

60 zéros difficiles, intervalles étroits reconstruits, vérité par calcul à 25 chiffres :

| Seuil du second pas | Erreur maximale |
|---|---|
| aucun (1 pas) | 5,9·10⁻⁹ |
| 3 (actuel) | 5,6·10⁻¹⁰ |
| 5 | 4,4·10⁻¹⁰ |
| 8 | 0 |

Le seuil actuel suffit à 10⁻⁹. Surcoût des seuils 5 et 8 **non mesuré**. Les écarts de 10⁻⁷ entre deux runs **non reproduits** par ce test.

## 21. Publication du jeu 5·10⁶ — bloquée

Paquet préparé hors dépôt : fichier compressé de 76 Mo, intègre, somme de contrôle du contenu décompressé identique à la référence, notes bilingues avec limites connues, licence CC BY 4.0 proposée par défaut. La création de la release publique sur le dépôt (public, sans licence) a été **refusée par le système d'autorisation** de Claude Code ; je ne l'ai pas contournée. À faire par hprzeta : autoriser la règle, ou lancer la commande lui-même ; confirmer licence, nom de tag et dépôt.

## 22. État final de la Partie B

- Poussé sur les quatre branches : documentation V17, script de synchronisation de PC2, correctif Ctrl+C, lanceur, vitesses (jusqu'à `4984a46` pour Test).
- **Non commités** : correctif des vitesses interpolées, mise à jour de la page V17 et du PDF du guide (nouvelles mesures) ; guide `.md` local à jour.
- Handoff local à jour (entrée « fin de nuit »).
- Ouvert : décision sur le seuil du second pas (garder 3 ou mesurer 5) ; publication du jeu 5·10⁶ ; remesure des débits au-delà de 5·10⁵ ; écarts de 10⁻⁷ entre runs à grand T.
- Capture brute : `claude-traitement-journalier/session_20261105_2019.log` (active ; deux `exit` demandés).
