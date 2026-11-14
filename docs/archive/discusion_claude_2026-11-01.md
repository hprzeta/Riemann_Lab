# Archive de session — 01/11/2026

Projet Riemann_Lab — une seule session Claude Code (branche Riemann_Lab_IA), du 25/10 au 01/11/2026 pour le contexte, longue journée et soirée du 01/11. Thème : préparer le « run distribué PC1 + PC2 » du guide de formation (fiche 2.3), puis les corrections et vérifications qui en ont découlé.

**Turbo Zêta :** RESTAURÉ (vérifié : 4 CPU à leur gouverneur initial (cpu0=powersave), swappiness 10) — première étape du « bye bye ». Après restauration : 39 services actifs, cups et cups-browsed actifs, aucun calcul sur PC1 ni PC2.

Cette archive reprend la narration, les tableaux et les conclusions de la session ; aucun extrait de code n'y figure. Le rapport détaillé (privé, hors dépôt) est ~/zeta_inventaire/DIAGNOSTIC/20261025_PC2_v16_distributed_feasibility.md (1 572 lignes, sections 1 à 41).

---

## 1. Consignes permanentes de hprzeta pendant la session

- Réponses et rapports **en français** ; étiquetage obligatoire **mesuré / lu dans le code / déduit / hypothèse** ; si un résultat contredit un rapport précédent, le signaler **en premier**.
- **Lecture seule** tant que hprzeta n'a pas dit « go » ; avant toute modification, point d'arrêt ; **ne jamais copier un .so de PC1 vers PC2** ; **une seule session** par chantier ; label unique pour chaque run sur PC2.
- **Aucun git add / commit / push sans validation explicite** ; pas de zeta_diag_publier.sh sans « go ».

---

## 2. PC2 et la V16 : audit, réparation, validation

| Sujet | Résultat | Statut |
|---|---|---|
| Panne distribuée du 15/10 | PC2 échouait à l'import (ImportError) ; PC1 avait continué seule environ 22 minutes sans que l'erreur soit vue | mesuré |
| Cause | apt autoremove --purge du 19/09 a supprimé python3-packaging et python3-dateutil dont dépendaient pandas et matplotlib installés par pip | mesuré |
| Réparation | pip install --user --no-deps des trois paquets (niveau utilisateur, sans sudo) ; test préalable ajouté à zeta_distribute.py | mesuré |
| V16 sur PC2 | environnement de test dédié ; .so compilés **sur** PC2 (jamais copiés) ; mêmes zéros que PC1 à ≤ 1 pas de flottant | mesuré |
| Déterminisme de PC2 | trois runs identiques bit à bit | mesuré |
| Workers sur PC2 | 2, 4 ou 8 workers : même débit (2 cœurs saturés) | mesuré |

**Rapport de débit PC1/PC2 (V16) :** 2,6 sur la plage [14 ; 100 000] (journal : 226 s contre 87 s) ; 3,2 à 3,6 en tranche étroite vers 100 000 et 500 000 ; 5,4 à 6,2 pour **planifier un pivot** (vitesses moyennes sur la plage propre à chaque machine) ; un pivot proche de 430 000 pour T_MAX = 500 000, PC2 recevant 12 à 16 % des zéros.

**zeta_distribute.py :** option --part-pc2, débits par défaut 815,16 et 138,15 z/s, test préalable de PC2, arrêt croisé PC1/PC2 (non testé sur un vrai calcul distant), commentaire du facteur de marge corrigé (15 %).

---

## 3. Précision de la V16

- **Cause des erreurs sur les paires proches** : l'affinage s'arrêtait à 1e-6 puis ne faisait qu'**un** pas de Newton à dérivée approchée ; erreurs de 5e-7 à 1,7e-6 sur les paires de zéros proches.
- **Correction** : second pas de Newton quand |Z′| < 3 ; maximum des paires d'écart < 0,05 ramené à 2,6e-10 ; surcoût +4,5 à 5,4 % sur PC1, +2,8 % sur PC2.
- **Découverte :** la tolérance « 1e-12 » absolue est **impossible en float64 au-delà de t ≈ 16 384** (le pas des flottants dépasse le seuil). Il faut une tolérance **relative** (en pas de flottant) ; le choix de k reste à décider.
- **Correction de mes propres affirmations :** l'hypothèse « le plancher restant vient de la dérivée Z_rs » est réfutée ; le seuil |Z′| < 3 suffit à partir de 5·10⁵ mais pas entre 2·10⁴ et 6,5·10⁴ (jusqu'à 445 pas pour une paire, 91 pas pour un zéro isolé).

| Mesure à haute altitude | Résultat |
|---|---|
| Tranches vers 500 000 et 5 000 000 (840 zéros certifiés par Arb 200 bits) | binaire corrigé au plancher du flottant (≥ 98 % à moins d'un demi-pas) |
| Ancien binaire à 500 000 | 2 paires au-dessus de 1e-9 (max 8,7e-9), pente |Z′| ≈ 0,38 |
| Test test_illinois_arb.py (3 échecs sur 20) | critère réel 1e-8 ; échecs aux zéros n° 1 à 3 (t < 26), fonction appelée hors de son domaine : défaut du test, pas des zéros livrés |

---

## 4. Premier run distribué réel PC1 + PC2 (V15, T = 20 000)

- **Défaut de l'enveloppe** : zeta-distribute échouait avec EOFError : le test préalable de PC2 lançait ssh sans stdin explicite, et ssh consommait le « O » envoyé par l'enveloppe. Cause **introduite par mon propre ajout** du test préalable ; reproduite en bac à sable puis corrigée (stdin vide sur les appels ssh/scp). L'enveloppe affichait en plus « run lancé » sans preuve.
- **Run** : 22 491 zéros (6 doublons au pivot), Turing complet, 69 s de mur ; PC1 30 s, PC2 54 s dont 30 s de validation de Turing locale sans objet ; PC2 facteur limitant.
- **Comparaison avec la V15 seule sur [14 ; 20 000]** : 134 zéros diffèrent sur 22 491 (max 6,2e-9). **Cause isolée** : le pas de balayage dépend des bornes du run ; la partie PC1 du run distribué est identique bit à bit à la V15 lancée sur les mêmes bornes de segment. Ce n'est pas une erreur de distribution ; aucune des deux versions n'est systématiquement la bonne.
- **Tableau de bord PC2** : l'erreur « could not convert string to float » venait d'un ssh sans saut par le bastion (« No route to host »), **pas** de la virgule décimale. Corrigée.

---

## 5. Artefact de lecture des CSV

pandas.read_csv par défaut modifie environ 13 % des valeurs de 1 à 2 pas de flottant. Il expliquait un désaccord de comptage entre deux sessions parallèles (136 479 contre 136 244 zéros identiques ; écart maximal 4,37e-11 contre 1,46e-11). Avec une lecture exacte : **136 244 identiques (98,7 %), écart maximal 1,46e-11 = 1 pas**. Neuf chiffres du §15 de l'autre session étaient faussés par cette lecture. Corrigé dans fusionner_csv (lecture exacte, déduplication seulement entre sources à 1e-5 au lieu de « tout zéro à moins de 0,01 du précédent »). L'audit des autres scripts : aucun impact mesurable.

---

## 6. Validation de Turing : défaut de N\_exact

- N_exact calculait la partie entière de θ/π plus l'arrondi de S ; **faux de −1 dès que la partie fractionnaire de θ/π dépasse 0,5**. Les « SURPLUS +1/+2 » des journaux étaient des artefacts (pas un chevauchement des workers) et le test pouvait masquer un zéro manquant.
- Corrigé (arrondi de la somme θ/π + 1 + S), et points de contrôle évalués à T + 1e-4 (N(T) est discontinue en un zéro). Nouveau dossier de tests tests_turing/ (5 tests ; 12 échecs avant correction).
- Rejeu : plus aucun surplus sur 4 runs réels (T = 20 000, 100 000, 200 000 ×2) ; comptes totaux confirmés.

---

## 7. Jeu V13 à T = 5·10⁶ : cause des manquants

**97 manquants** (le journal de juin disait 96 ; la somme de ses déficits par segment vaut 97).

| Cause | Part | Statut |
|---|---|---|
| Vraies paires de zéros distants de 0,003 à 0,0099, supprimées par la déduplication à 0,01 | ≈ 85 | mesuré (14 sur les 21 premiers manques localisés par dichotomie ; prédiction par la loi de répulsion des matrices aléatoires compatible) |
| Zéros isolés perdus en silence : l'affinage sort de son crochet, le repli mpmath lève une erreur, le bloc try/except: pass abandonne le zéro | ≈ 12 | mécanisme reproduit ; fréquence globale : hypothèse |

L'hypothèse « paires plus serrées que le pas de balayage » est **réfutée** (écart minimal 1,9 pas V13). Sur la tranche [4,9·10⁶ ; 4,986·10⁶], V13 et V16 donnent la même liste ; la V17 conserve 4 paires que la déduplication supprime. J'ai aussi constaté, en lisant le suivi du projet, que l'entrée du JOURNAL du 15/10 contenait déjà les 4 paires de ce test (T1b) : mon constat en est une réplication, étendue au jeu complet. Estimation d'un complément du jeu (non lancé) : de 35 minutes à 2,5 heures en ciblé, environ 30 heures en complet.

---

## 8. Synchronisation avec le Guide Run v0.15 (tenu côté Claude.ai)

Comparaison du guide (1 727 lignes, 15 fiches du cas 1, 38 écarts, 58 bonnes pratiques) à mes rapports : environ 40 éléments exacts, **15 faux, imprécis ou périmés**, 10 contradictions (dont 7 internes au guide). Principaux : « ≤ 1 pas flottant » (faux entre 2·10⁴ et 6,5·10⁴), « aucun run distribué réel » (périmé), cause de l'EOFError inconnue, déduplication à 0,01. Liste de 18 corrections à transmettre côté Claude.ai ; ajout d'un écart E50 (N_exact). Le guide lui-même n'a jamais été modifié.

---

## 9. Modifications du dépôt (commits et pushs, toujours après « go »)

| Commit sur Riemann_Lab_IA | Contenu |
|---|---|
| 6263b1e | turbo : cups-browsed relancé avec cups + tests (36 OK) |
| 2f5b4be | distribution : stdin des appels ssh, fusion exacte, enveloppe qui vérifie le démarrage, sonde PC2 par le bastion |
| 180a63a | illinois_arb : second pas de Newton si |Z′| < 3 (le .so suivi est à recompiler sur chaque machine) |
| d750e3f | Turing : N_exact corrigé, points de contrôle à T + 1e-4, dossier tests_turing/ |
| 1d5b8f1 | CLAUDE.md : 11 services arrêtés (et non 12) |
| a1708fc | outils d'observation d'un run (option ZETA_MON_EXTRA, désactivée par défaut) + 4 scripts |

- **Synchronisation des autres branches** par cherry-pick -x (et non par fusion complète : les PDF et scripts d'infra restent sur IA uniquement) : Riemann_Lab_C, main, Riemann_Lab_Test à niveau pour ces six commits ; tests verts dans chaque worktree avant push.
- **Wiki** (dépôt séparé) : trois commits poussés (suivi du 01/11, correction de l'état des commits, clarification du STACK, suite de la nuit).
- **Incident** : un verrou git périmé (vide, du 30/10) a empêché les premiers commits ; supprimé après vérification qu'aucun processus ne le tenait.
- **Autorisation** : un push non explicitement demandé a été refusé par le contrôle d'autorisation ; non contourné ; poussé après un « go » explicite.
- **GitHub Pages** : vérifié ; servi par la branche Riemann_Lab_IA, dossier /docs (et non main) ; builds « built » ; page d'accueil identique à docs/index.html ; 9 liens internes sur 9 en HTTP 200 ; wiki en ligne à jour.

---

## 10. Guides locaux

Mises à jour locales (hors git) : §17 du guide des commandes Linux (démarrage vérifié de zeta-distribute, cause de l'EOFError, turbo coupé en fin de run) et guide des scripts (options, fusion, sonde) ; PDF du guide des scripts régénéré (31 pages, édition du 01/11).

---

## 11. État en fin de session et reprise demain

**Rien en cours de calcul.** Turbo restauré. Tout le code de la session est poussé sur les 4 branches et le wiki est à jour.

**Point levé en fin de session : l'index monitoring/Monitoring-Runs.md a été restauré à l'état du dernier commit (option C, après clarification : l'option A était déjà faite et n'incluait pas l'index).** Copie de l'ancienne version conservée localement ; les 45 dossiers de runs restent sur disque, non suivis et non publiés ; chaque nouveau run réécrira l'index (décision D éventuelle). Plus aucun fichier suivi n'est modifié.

**Prochaines actions à reprendre demain (rien ne se lance sans OK de hprzeta) :**

1. (fait) Index restauré ; éventuellement trancher l'option D (sortir l'index du suivi).
2. Corriger la cause des manquants dans le code de production : remplacer la déduplication à 0,01 par la consolidation V17, journaliser les échecs d'affinage au lieu de les taire.
3. Compléter ou non le jeu à 5·10⁶ (97 zéros manquants).
4. Distribution : brancher la V16, lancer un run distribué à T = 100 000 (avec et sans --part-pc2), supprimer la validation de Turing locale inutile sur PC2, rendre la grille de détection indépendante des bornes.
5. Précision : choisir la tolérance relative (k), second pas de Newton dépendant de t.
6. Documentation : outils d'observation dans le guide des scripts ; transmettre au Guide Run les 18 corrections.
