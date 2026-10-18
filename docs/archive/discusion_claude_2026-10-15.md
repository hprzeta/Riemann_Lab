# Archive de session du 15 octobre 2026 — V16 (test T1b) puis V17 phase P0

*Auteur : hprzeta — résumé narratif de la session avec Claude (modèle Sonnet). Sans code : narration, données, conclusions et instructions de hprzeta. Capture brute du terminal : **absente** (le script de capture n'était pas lancé avant Claude).*

## 1. Contexte et règles de collaboration

Projet Riemann\_Lab, branche de travail Riemann\_Lab\_IA. Règles rappelées en cours de session : jamais de push forcé ; aucun commit sans validation explicite ; masquer tout secret ; copie de sauvegarde datée avant toute modification de script ; rien d'autre sans « go » ; aucune opération nécessitant les droits administrateur lancée par l'assistant ; aucun résultat numérique ne prouve l'hypothèse de Riemann (statuts : non résolu, corroboré numériquement, certifié numériquement seulement avec garanties explicites, doublon confirmé).

## 2. Première partie — test T1b de la version 16

**Objectif.** Vérifier sur un intervalle réel l'hypothèse que la fonction de déduplication à tolérance 0,01 supprime de vrais zéros.

**Run.** Intervalle [4 900 000 ; 4 986 000], 8 workers, pas de scan adaptatif 3,146e-4, durée 33,0 minutes, code de sortie 0. Un premier lancement avait été interrompu à 16:03 par un redémarrage de la session graphique (avec un calcul distribué lancé en parallèle) ; relancé à 16:12.

**Résultats mesurés.**

| Mesure | Valeur |
|---|---|
| Zéros bruts (8 fichiers de worker) | 185 821 |
| Après déduplication à 0,01 | 185 810 |
| Supprimés | 11 |
| dont doublons artificiels de frontière (écart exactement 0) | 7 |
| dont paires réelles d'écart inférieur à 0,01 | 4 |
| Total conditionnel après réintégration | 185 814 |

Les quatre paires (écarts 3,028e-3 ; 7,169e-3 ; 7,241e-3 ; 7,787e-3) ont été corroborées par mpmath à 30 chiffres (changements de signe de Z, racines distinctes). Formule de Backlund (sans le terme S(T)) : 185 813,56 zéros attendus dans l'intervalle ; le motif observé sur v13 n'est pas reproduit.

**Publications (avec accord).** Rapport d'analyse v16/v17 mis à jour, PDF de 6 pages, ligne « v17 en préparation » dans le tableau du site, wiki ; quatre branches synchronisées.

## 3. Deuxième partie — prompt maître V17 et audit en lecture seule

hprzeta a transmis un long prompt maître (sections 0 à 16) exigeant un audit strictement en lecture seule, un rapport complet (sections A à M) avec étiquettes de provenance (observé, rapporté, déduit, hypothèse, non vérifié), puis l'arrêt avant toute modification.

**Principaux constats de l'audit.**

- La fonction de déduplication fusionne tout écart inférieur ou égal à 0,01 alors que le pas de scan est de l'ordre de 3e-4 ; le rescan refait la même déduplication et ne peut donc pas récupérer ces paires.
- Les « checkpoints » ne sont écrits qu'à la fin de chaque worker ; deux gestionnaires d'exceptions avalent silencieusement les erreurs.
- Le pas de scan de la version 16 n'est pas fixé à 0,010 (contrairement à une prémisse du prompt) : il dépend de la borne haute seule.
- Le déficit de 96 zéros de v13 à 5 millions est réparti en hauteur, il n'est pas concentré dans les deux premiers segments (autre prémisse contredite) ; le dossier du run v16 à 5 millions est vide, donc ses chiffres rapportés sont invérifiables.
- Heuristique GUE : environ 91 paires d'écart inférieur à 0,01 attendues sur [14 ; 5M], du même ordre que le déficit de v13 (incertitude de 20 à 30 %).
- Le second poste de calcul ne peut pas faire tourner la version 16 en l'état (bibliothèques et en-têtes différents) ; rien n'a été modifié de ce côté.

## 4. Troisième partie — phase P0 de V17

### Instructions de hprzeta (extraits verbatim)

> **Priorité absolue : préserver les données, assurer la traçabilité et établir des résultats reproductibles.**

> **La seule proximité numérique ne constitue jamais une preuve d'identité.**

> Ne modifie que de nouveaux fichiers non suivis, dans scripts\_v17/ et tests\_v17/. Ne modifie ni parallel\_scanner.py ni compute\_zeros\_v16.py. N'utilise jamais git add -A. Aucun commit, push ou publication.

> Ne lance pas le test Z-sign avant mon autorisation explicite.

> Ne modifie pas le code pour obtenir un total attendu. Le résultat de 185 814 reste un contrôle de cohérence, pas un objectif.

### Réalisation

Nouvelle fonction de consolidation non destructive : chaque groupe de candidats reçoit exactement un statut (doublon confirmé, distinct, ambigu), avec provenance (fichier, ligne, worker, segment), règle appliquée, justification et limites ; journal des décisions, fichier des cas ambigus, invariant de conservation (aucun candidat perdu), écriture atomique sans écrasement.

Tests D1 à D13 : leurs définitions n'existaient pas dans le dépôt, elles ont été consignées dans le fichier de tests. Premier passage : 4 échecs sur 14 ; trois venaient des données de test (comparaison flottante, clés de provenance en collision), le quatrième (D5) a révélé un **défaut réel de la règle** (les rayons d'incertitude étaient ignorés), que j'avais d'abord masqué en modifiant la donnée de test. Revue de hprzeta : la règle a été corrigée, le test d'origine rétabli. Résultat final : 16 tests sur 16 réussis.

### Rejeu T1b sur les données brutes

| Mesure | Résultat |
|---|---|
| Lignes brutes lues | 185 821 |
| Ancienne déduplication | 185 810 |
| Consolidation V17 | 185 814 |
| Doublons de frontière confirmés | 7 (écart exactement 0, workers adjacents, zones de chevauchement identiques) |
| Paires rapprochées | 4, laissées « ambigu » (variante prudente) |
| Données brutes | SHA-256 identiques avant et après |

Indépendance à l'ordre des entrées vérifiée sur 185 821 candidats (mélanges et inversion) ; provenance vérifiée (22 candidats cités retrouvés à l'identique dans les fichiers bruts).

### Examen de la règle de distinction par le pas de scan

hprzeta n'a pas validé cette règle. Analyse du code : un bracket donne au plus un candidat, donc deux candidats distants de plus de deux pas viennent de deux brackets différents ; mais cela n'établit pas que chaque bracket contienne un vrai zéro (scénario d'une paire factice due à l'erreur de la fonction de détection en double précision, non bornée dans le code). Conclusion : règle non démontrable avec les données disponibles ; variante prudente conservée.

### Test Z-sign (autorisé par hprzeta)

Sur les quatre paires, un seul cœur, basse priorité : rejeu du scan principal et du raffinement (les huit candidats stockés sont retrouvés bit pour bit), évaluation avec mpmath à 30 et 50 chiffres.

| Paire (worker) | Écart | Changements de signe (30 / 50 chiffres) | Z au milieu (valeur absolue) |
|---|---|---|---|
| 1 (worker 2) | 3,028e-3 | 2 / 2 | 3,6e-5 |
| 2 (worker 2) | 7,169e-3 | 2 / 2 | 2,3e-4 |
| 3 (worker 3) | 7,787e-3 | 2 / 2 | 1,6e-3 |
| 4 (worker 5) | 7,241e-3 | 2 / 2 | 9,0e-4 |

Signes identiques entre les deux précisions et identiques à ceux du scan principal ; racines indépendantes à moins de 2,8e-9 des candidats. **Statut : corroboré numériquement, non certifié.** Un changement de signe étaye l'existence d'au moins un zéro, il ne prouve pas l'unicité.

### Décision de hprzeta

> Option recommandée : A, avec Z-sign en corroboration

Les quatre paires restent « ambigu » dans le consolidateur ; le Z-sign est consigné séparément comme corroboration numérique.

## 5. Publication

Commit des quatre fichiers V17 (sans les sorties de calcul), poussé sur Riemann\_Lab\_IA puis synchronisé sans conflit sur les trois autres branches (Riemann\_Lab\_C en avance rapide, main et Riemann\_Lab\_Test par fusion). Handoff local et wiki (Handoff, JOURNAL) mis à jour, puis wiki commité et poussé. Aucun secret ni identifiant réseau dans les lignes ajoutées (audit).

## 6. Reste ouvert

- Choisir la phase suivante : checkpoints périodiques et atomiques, journal des exceptions, contrôles de Turing et de la base LMFDB à réécrire pour un sous-intervalle, conservation du bracket, du segment, du résidu et du rayon dans les sorties.
- Mesurer le coût d'une certification par isolation des zéros (bibliothèque FLINT) sur quelques zéros avant tout engagement.
- Corriger les documents obsolètes (formule du pas, seuil de la voie C) après validation.
- Non commités en local : fichiers de configuration et archive du 10/10 modifiés, plusieurs scripts non suivis, dossier des sorties V17.

*Fin de l'archive du 15/10/2026.*
