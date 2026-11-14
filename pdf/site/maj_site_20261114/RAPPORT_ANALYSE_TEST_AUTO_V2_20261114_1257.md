# Rapport d'analyse — 1er test automatique réel (13/11/2026) et test V2 (14/11/2026 12:57)

> Rédigé sur claude.ai (projet SITE ZETA). Aucune modification faite. Sources : `RAPPORT_TEST_AUTO_MAJ_SITE_20261113_1240.md`, `RAPPORT_SESSION_20261113_1324.md`. Prompt associé : `PROMPT_TEST_AUTO_V2_20261114_1257.md`.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Déclenchement automatique | 🟢 | rapport produit seul le 13/11 à 12:40 après l'ouverture de session | — |
| Valeurs du site (10 016 474, 138 069), README, `Home` | 🟢 | cohérentes entre site en ligne, dépôt et wiki | — |
| Site en ligne = dépôt | 🟢 | bandeau, statistiques, pied « 12/11/2026 » identiques | — |
| Corrections proposées | 🟢 | aucune correction certaine | — |
| Contrôle des liens | 🟡 | 2 URL testées sur 74 : « Bash a été refusé » | D28 |
| Nombre de lignes des `.md` | 🟡 | `wc -l` impossible | D28 |
| Secrets | 🟡 | 8 fichiers du wiki seulement, dépôt non scanné | D28 |
| Formules (statique) | 🟡 | 5 fichiers sur 15 lus | D28 |
| Phrase du rescan | 🟢 | déjà alignée sur `V17.md` et validée le 12/11 (D10, D13) | — |

## 2. Cause
Le test laisse à Claude le soin de lancer les commandes. En mode automatique (`claude -p`), une commande Bash qui ne correspond pas exactement à une règle autorisée (commande composée, boucle, options différentes) est **refusée sans possibilité de l'accepter**. Le rapport devient partiel.

## 3. Solution (D28)
Les contrôles mécaniques sont faits **par un script**, avant Claude, avec des résultats fixes et vérifiables. Claude reçoit ces résultats et ne fait plus que l'analyse (sans Bash).

| Contrôle | Avant (13/11) | Après (V2) |
|---|---|---|
| Liens | 2 sur 74 | tous les liens du site, du README et des pages wiki modifiées |
| Nombre de lignes | non fait | tous les `.md` modifiés |
| Secrets | 8 fichiers | tous les fichiers modifiés (dépôt et wiki), sans afficher les valeurs |
| Formules | 5 fichiers sur 15 | tous les `.md` modifiés (contrôle statique) |

## 4. Points ouverts repris du handoff du 13/11 (hors site)
- Mesure de la V17 sur PC1 avec turbo : projet de calcul, pas SITE ZETA.
- Pages de renvoi du wiki : à garder tant qu'elles servent (aucune urgence).
- Liens issues / Kanban du README : gardés tels quels (D23).

## 5. Tableau de modifications (à faire, local)

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| `~/.local/bin/zeta_test_controles.sh` | nouveau script de contrôles (lecture seule) | — | À FAIRE |
| `~/.local/bin/zeta_test_maj_site.sh` | appel des contrôles, Bash retiré, `ZETA_FORCE` | version du 12/11 | À FAIRE |
| `src/ia/prompts/PROMPT_TEST_AUTO_MAJ_SITE.md` | règle 9 : contrôles fournis, pas de Bash | version du 12/11 | À FAIRE |

## 6. Non vérifié depuis claude.ai
- Le contenu de `erreurs_20261113.log` (quelles commandes ont été refusées).
- La présence et le fonctionnement des scripts de l'audit du 12/11 dans `pdf/site/maj_site_20261112/audit/`.

---
*RAPPORT_ANALYSE_TEST_AUTO_V2_20261114_1257.md · projet SITE ZETA · hprzeta · MAJ 14 novembre 2026 12:57 · 50 lignes*
