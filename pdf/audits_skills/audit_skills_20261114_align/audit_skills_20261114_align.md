# Audit — alignement des skills dépôt / compte (D7, D8, R2, R7) — 14/11/2026

> **Dépôt :** `Riemann_Lab` · **Branche source :** `Riemann_Lab_IA`
> **Prompt :** `PROMPT_ALIGN_SKILLS_20261114.md` (rédigé sur claude.ai, projet SKILLS ZETA)
> **Règle D1 :** la copie du dépôt `.claude/skills/<nom>/` fait référence ; le compte reçoit une copie identique.
> **Correction reçue avant l'exécution :** `riemann-site-update` est déjà aligné dans le compte (v3, 141 lignes) : 9 zips au lieu de 10.

## Réponse directe

D8 est appliqué et poussé sur les 4 branches. 9 zips sont prêts pour le compte, identiques au dépôt (SHA-256). Il reste à **importer ces zips dans le compte** (action de hprzeta sur claude.ai) et à trancher 3 points 🟡 : liste « 14 skills » du prompt (le dépôt en a 12), copies de niveau utilisateur, nouvelle session (R2).

## État AVANT / APRÈS (dépôt, `Riemann_Lab_IA`)

| Skill | Lignes AVANT | Lignes APRÈS | SHA-256 AVANT | SHA-256 APRÈS | Changement |
|---|---|---|---|---|---|
| `phase-c-illinois` | 466 | 466 | `be39ad8fc1b4fcd8` | `be39ad8fc1b4fcd8` | aucun |
| `riemann-agent-bridge` | 137 | 137 | `e3cc6523d31f0a5f` | `e3cc6523d31f0a5f` | aucun |
| `riemann-bastion-hardening` | 174 | 174 | `ad3e3ee9f0278990` | `ad3e3ee9f0278990` | aucun (marqueurs `[IP-…]`, D7) |
| `riemann-code-review` | 162 | 162 | `119f21c9dac1c2d4` | `119f21c9dac1c2d4` | aucun |
| `riemann-lab` | 354 | 356 | `71096e29af733a66` | `eadff0d49ba0915e` | **D8** |
| `riemann-lab/references/Bibliotheques.md` | 913 | 913 | `4f25002f9c0879b5` | `4f25002f9c0879b5` | aucun |
| `riemann-lab/references/Formules_zeta.md` | 1656 | 1656 | `9231fcdbd5111801` | `9231fcdbd5111801` | aucun |
| `riemann-literature-scout` | 85 | 85 | `719cd4c9932550e1` | `719cd4c9932550e1` | aucun |
| `riemann-proof-status` | 107 → 97 | 97 | `5c9c1837fa3482c3` → `e0d2fd55dd5da6f4` | `e0d2fd55dd5da6f4` | **description ≤ 1024 (e342b1e)** |
| `riemann-security-review` | 162 | 162 | `85578eea1227c5e9` | `85578eea1227c5e9` | aucun |
| `riemann-site-check` | 69 | 69 | `f8d690fc309dd9b4` | `f8d690fc309dd9b4` | aucun |
| `riemann-site-update` | 141 | 141 | `49f71a1a439f34b4` | `49f71a1a439f34b4` | aucun |
| `riemann-statistics-gue` | 120 | 120 | `6496cb24d43c96a6` | `6496cb24d43c96a6` | aucun |
| `zeta-diagnostic` | 42 | 42 | `a1a5c85d4ad1fae5` | `a1a5c85d4ad1fae5` | aucun |

Lignes : `wc -l` (un de moins que l'éditeur pour certains fichiers). Sauvegarde de `riemann-lab` avant D8 : `pdf/archive/riemann-lab_SKILL.md.bak-202611141803` (local, non commité).

## Tableau d'audit

| # | Contrôle | Résultat | Statut |
|---|---|---|---|
| R2 | Liste des skills vue dans une **nouvelle** session | Non faite : liste relevée dans la session courante (`captures/etape0_liste_skills_session.md`). Les 12 skills du dépôt y figurent | 🟡 |
| 0 | Nombre de skills attendu | Le prompt annonce 14, le dépôt en contient **12** | 🟡 |
| 0b | Copies de niveau utilisateur (`~/.claude/skills/`) | 7 dossiers ; `riemann-lab`, `riemann-code-review`, `riemann-bastion-hardening` **diffèrent** du dépôt ; `phase-c-illinois` et `riemann-security-review` identiques | 🟡 |
| 1 | État AVANT : `git status -s .claude/skills/` | Vide (propre) ; tableau ci-dessus | 🟢 |
| D8 | `riemann-lab` : encadré « Wiki GitHub » après la ligne 40 + 2 titres (53 et 61) | Appliqué, sauvegarde `.bak` faite, diff montré avant le « go D8 » | 🟢 |
| D8b | Bloc « Commandes interdites » (l. 42 à 51, contient `T_{10%}` → `T_{10\%}`) non retitré ; « Piège 1 » (`%` commentaire KaTeX) sous le titre « HTML du site » | Signalé, laissé tel quel (D8 décidé tel quel) | 🟡 |
| 3 | Contrôle des secrets par valeurs sur les 14 fichiers de `.claude/skills/` | 2 lignes : `riemann-security-review` l. 112 (e-mail public du projet, accepté par hprzeta) ; `riemann-site-update` l. 79 (nom de motif `fe80::`, faux positif) | 🟡 |
| 4 | Commit D8 (après « go commit ») : seul `riemann-lab/SKILL.md` indexé | `15e41da` (+4, −2) | 🟢 |
| 4b | Push `Riemann_Lab_IA` + `cherry-pick -x` sur 3 branches (worktrees), push sans `--force` | Sans conflit ; `git diff` sur `.claude/skills/` vide pour chaque branche | 🟢 |
| 5 | 9 zips dans `A_DEPOSER/zips_compte/` (dossier du skill à la racine, `references/` pour `riemann-lab`) | Créés ; `unzip -l` contrôlé ; `.bak*` exclus | 🟢 |
| 5b | SHA-256 de chaque `SKILL.md` zippé = dépôt | Identiques pour les 9 (et les 2 fichiers `references/`) | 🟢 |
| 5c | Secrets dans les zips | Seule la ligne 112 de `riemann-security-review` (e-mail public accepté) | 🟡 |
| D7 | Aligner `riemann-bastion-hardening` (marqueurs `[IP-…]` dans les deux copies) | Zip avec marqueurs prêt ; **le compte n'est pas encore mis à jour** (import à faire) | 🟡 |
| 6 | Commit des rapports | En attente de « go commit » | 🟡 |
| — | Aucun point 🔴 | — | 🟢 |

## Commits D8

| Branche | Commit | Plage poussée |
|---|---|---|
| `Riemann_Lab_IA` | `15e41da` | `1ba9181..15e41da` |
| `main` | `ee9c141` | `81759aa..ee9c141` |
| `Riemann_Lab_C` | `219ae07` | `d600bc1..219ae07` |
| `Riemann_Lab_Test` | `a3e42f6` | `1bfa7c3..a3e42f6` |

Les 3 reports sont des `cherry-pick -x 15e41da`.

## Zips pour le compte (9)

SHA-256 du `SKILL.md` zippé (16 premiers caractères), tous identiques au dépôt : `riemann-bastion-hardening` `ad3e3ee9f0278990` · `riemann-lab` `eadff0d49ba0915e` · `phase-c-illinois` `be39ad8fc1b4fcd8` · `riemann-agent-bridge` `e3cc6523d31f0a5f` · `riemann-code-review` `119f21c9dac1c2d4` · `riemann-literature-scout` `719cd4c9932550e1` · `riemann-proof-status` `e0d2fd55dd5da6f4` (zip refait le 14/11 18h35, voir correction) · `riemann-security-review` `85578eea1227c5e9` · `riemann-statistics-gue` `6496cb24d43c96a6`. Pas de zip pour `riemann-site-update` (déjà aligné dans le compte).

## Méthode et réserves

- Cherry-pick dans des `git worktree` temporaires (supprimés) : l'arbre de travail de `Riemann_Lab_IA` contient des modifications étrangères (`monitoring/Monitoring-Runs.md`), jamais indexées.
- `src/ia/prompts/`, `A_DEPOSER/` (zips compris) et `pdf/archive/` restent locaux. Aucune valeur identifiante dans ce rapport.
- Les copies de niveau utilisateur (`~/.claude/skills/`) n'ont pas été modifiées.

## Écarts à signaler à claude.ai

1. Critère du contrôle de secrets (étape 3) trop large : `fe80::` seul déclenche sur la ligne 79 de `riemann-site-update` ; utiliser `fe80::[0-9a-f]+:`.
2. Nombre de skills du dépôt : 12, pas 14.
3. Copies `~/.claude/skills/` : 3 diffèrent du dépôt (risque de doublon ou de masquage) ; décision à prendre (aligner, supprimer ou laisser).
4. D8b : retitrer ou non le bloc « Commandes interdites » et le « Piège 1 ».
5. E-mail ligne 112 de `riemann-security-review` : laisser (adresse publique) ou remplacer par un marqueur, avant import dans le compte.

## Correction du 14/11/2026 18h35 — `riemann-proof-status`

Import refusé par le compte (« description must be at most 1024 characters »). Bloc `description: |` remplacé par une ligne unique de 722 caractères (`yaml.safe_load`) ; `name:` inchangé. Commit `e342b1e` sur `Riemann_Lab_IA`, reports `af76a0d` (main), `4d771f0` (Riemann_Lab_C), `1f6448c` (Riemann_Lab_Test), sans `--force`. Zip refait (dossier à la racine, 6195 octets), SHA-256 complet du `SKILL.md` : `e0d2fd55dd5da6f40688f342aba407d0553221c0a04cda3ca6a6dcd497c75002`. Les 11 autres descriptions sont toutes < 1024 (maximum : `riemann-security-review`, 934). Ancien zip archivé dans `pdf/archive/`.

## Après Claude Code (hprzeta, sur claude.ai)

Paramètres → Skills : importer les 9 zips (remplacer s'il existe), puis redonner ce rapport à claude.ai (SKILLS ZETA) pour la comparaison SHA-256 des skills dépôt / compte.

---
*audit_skills_20261114_align.md — 2026-11-14 — 91 lignes*
