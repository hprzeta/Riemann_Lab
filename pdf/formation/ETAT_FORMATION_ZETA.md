# ETAT — projet ZETA FORMATION

## État en bref
- **Dernière action :** 21/11/2026 : fiches rangées (`9b67d3c`), modèle d'instructions installé (`db3a22d`), règles `formation` et `vault` (`cb6901a`).
- **Chiffres clés :** Projet ramené à 66 documents texte (25 % de capacité) ; fiches 01 à 09 en local ; 166 textes retirés, 154 non-textes vérifiés sur PC1.
- **Point bloquant :** D3 ouverte (cours de maths ici ou dans MATH ZETA) ; R7 : fusion des deux `Guide_Run_Zeta.md` (2 148 contre 2 127 lignes) à faire par prompt séparé.
- **Prochaine action :** R5, relire les fiches selon la §8 (5 parties, sources officielles) ; écarts relevés le 21/11 listés plus bas.

> Rangé dans le projet sous `claude/ETAT_FORMATION_ZETA_20261121.md`. Point de départ de toute nouvelle session (instructions §3.1).

## Objet

Me former à bien utiliser Claude (claude.ai, Claude Code, skills, MCP, Claude in Chrome) dans le projet zêta, à partir de la documentation officielle d'Anthropic, avec des fiches numérotées du débutant à l'expert.

## Fait

| Date | Quoi |
|---|---|
| 11/10/2026 | Cours gratuits et plan de progression (conversation) |
| 01/11/2026 | « Pratique Zeta » : tests de run et monitoring |
| 05/11/2026 | Rejeu des 13 zéros isolés ; décision « un seul Guide_Run_Zeta tenu à jour » ; `md/` exclu du git |
| 11/11/2026 | Plan des fiches 1 à 8 (conversation) ; 25 prompts extraits vers `src/ia/prompts/FORMATION_ZETA` |
| 21/11/2026 | Audit `audit_formation_20261121` (claude.ai + Claude Code, étapes 0 à 6) : rapport et PDF dans `pdf/formation/audit_formation_20261121/`, tests secrets 0 |
| 21/11/2026 | Nouvelles instructions collées et enregistrées par claude.ai dans Chrome (5 760 caractères, sections 1 à 8) |
| 21/11/2026 | Ménage : 166 textes supprimés (code, journaux, .bak, doublons, `skills/`) ; docs de sécurité transférés vers SECURITE ZETA ; projet ramené à 66 documents texte |
| 21/11/2026 | Procédure type `PROMPT_MAJ_INSTRUCTIONS_MODELE.md` (leçons L1 à L5) ; modèle mis à jour (lignes SECURITE et FORMATION) téléchargé pour installation locale |
| 21/11/2026 | Fiches rangées dans `md/formation/fiches/` et `pdf/formation/fiches/` (commit `9b67d3c`) ; règles `.claude/rules/formation.md` et `vault.md`, garde-fous `git push` (commit `cb6901a`) |

## Constats de l'étape 3 (Claude Code)

- Fiches existantes en local : `Fiche_01` à `Fiche_09`, en `.md` (`md/claude/`) et en PDF (`pdf/claude/`). Elles ne sont pas dans ce projet.
- `Guide_Run_Zeta.md` : la version du projet (2 148 l., 11/11) est plus récente que celle du dépôt (2 127 l., 07/11) ; 23 lignes propres au projet, 2 au dépôt.
- `MODELE_INSTRUCTIONS_PROJET.md` absent du dépôt avant l'installation du 21/11.

## Reste ouvert

| N° | Point | Statut |
|---|---|---|
| R1 | Coller les nouvelles instructions | 🟢 fait le 21/11 |
| R2 | Trancher D3 (cours de maths ici ou dans MATH ZETA) | à décider |
| R3 | Ménage D4 : 🟢 terminé le 21/11 — 166 textes supprimés (sauvegarde JSON sur PC1, `pdf/formation/audit_formation_20261121/sauvegarde/`) et 154 non-textes supprimés après vérification sur PC1 (154/154 🟢, `verif_non_texte_formation_20261121.md`) ; projet : 66 fichiers, 25 % de capacité | 🟢 fait |
| R4 | D5 : 🟢 3 docs de sécurité copiés dans SECURITE ZETA (`secrets_local/`, identiques) puis retirés d'ici ; 🟡 valeurs à remplacer par `[IP-…]` dans `Guide-Linux-Commandes`, `Guide_Scripts_Cluster_Zeta`, `Guide-RAG-BrainVault-Debutant`, `10-complement_methode_git…` | en cours |
| R5 | Fiches 01 à 09 + plan déposés dans `fiches/` (21/11). Reste : les relire selon la §8 (5 parties, sources officielles) | 🟡 en cours |
| R6 | Modèle d'instructions en local : `claude/` du dépôt, commit `db3a22d` (Riemann_Lab_IA) ; copie de SKILLS ZETA à remplacer | 🟡 presque fait |
| R7 | Fusionner les deux `Guide_Run_Zeta.md` (prompt séparé) | à faire |

## Décisions

| N° | Décision | Statut |
|---|---|---|
| D1 | Instructions selon `MODELE_INSTRUCTIONS_PROJET.md`, seule la §8 est propre au projet | adoptée 21/11 |
| D2 | Rapports dans `pdf/formation/audit_formation_<AAAAMMJJ>/` + `A_DEPOSER/` | adoptée 21/11 |
| D3 | Périmètre : usage de Claude ; sort des cours de maths à trancher | ouverte |
| D4 | Pas de code, journal, .bak ni copie de skill dans ce projet | adoptée 21/11 |
| D5 | Documents de sécurité → SECURITE ZETA ; marqueurs `[IP-…]` ailleurs | adoptée 21/11 |
| D6 | Fiches `Fiche_NN_<sujet>.md`, niveaux 0 à 5, 5 parties | proposée |
| D7 | Modèle d'instructions : référence dans le dépôt `~/projet_zeta/claude/`, copie dans SKILLS ZETA (L5) | adoptée 21/11 |

## Plan des fiches

Source : `fiches/Plan_Formation_Claude_Zeta.md` (parcours de 8 semaines, cours Anthropic Academy).

| N° | Niveau | Titre | Statut |
|---|---|---|---|
| 1 | Débutant | Bien parler à Claude (prompts) | À faire |
| 2 | Débutant | Projects, mémoire et préférences | À faire |
| 3 | Intermédiaire | Fichiers, recherche web, artefacts | À faire |
| 4 | Intermédiaire | Fiabilité : méthode des 4D | À faire |
| 5 | Avancé | Claude Code : exécuter et vérifier | En cours |
| 6 | Avancé | Skills et sous-agents | En cours |
| 7 | Avancé | MCP et connecteurs | À faire |
| 8 | Expert | API Claude et agent autonome (Objectif 2) | À faire |
| 9 | Avancé | Piloter Claude Code | En cours |

Écarts relevés le 21/11 (à corriger lors de la relecture) : fiche 6 cite `zeta-diagnostic` (nom actuel `riemann-zeta-diagnostic`, D11) ; les fiches ont 4 parties au lieu des 5 de la §8 (manque « erreurs déjà commises », sauf fiche 4) ; la §8 des instructions ne cite pas code.claude.com ni anthropic.skilljar.com, utilisés par les fiches.

---
<sub>Mis à jour le 2026-11-21 · 78 lignes</sub>
