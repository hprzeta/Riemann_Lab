# Audit — renommage de 2 skills avec le préfixe `riemann-` — 14/11/2026

> Prompt : `src/ia/prompts/rename_skills_20261114/PROMPT_RENAME_SKILLS_20261114.md` (local, non versionné). Règle D1 : le dépôt `.claude/skills/<nom>/` fait référence ; le compte claude.ai reçoit une copie identique. Jamais `--force`, jamais `git add -A`.

## 1. Tableau AVANT / APRÈS

| Élément | AVANT | APRÈS |
|---|---|---|
| Dossier dépôt | `.claude/skills/zeta-diagnostic` | `.claude/skills/riemann-zeta-diagnostic` |
| Dossier dépôt | `.claude/skills/phase-c-illinois` | `.claude/skills/riemann-phase-c-illinois` |
| Dossier d'export | `skills_export/phase-c-illinois` | `skills_export/riemann-phase-c-illinois` |
| `name:` zeta-diagnostic | `"zeta-diagnostic"` | `"riemann-zeta-diagnostic"` |
| `name:` phase-c-illinois | `phase-c-illinois` | `riemann-phase-c-illinois` |
| SHA-256 (16 car.) `zeta-diagnostic` | `a1a5c85d4ad1fae5` | `5bab8a68065122e7` |
| SHA-256 (16 car.) `phase-c-illinois` | `be39ad8fc1b4fcd8` | `665a5b0efb3ef40d` |
| Description (caractères) | non mesurée avant | 167 (zeta-diagnostic) et 374 (phase-c-illinois), limite 1 024 |
| Skills du dépôt | 12 (2 sans préfixe) | 12, tous préfixés `riemann-` |

Seule la ligne `name:` change dans les deux `SKILL.md` : le titre et le pied de page ne citaient pas l'ancien nom (pied de page « 466 lignes » de `phase-c-illinois` toujours exact). Sauvegardes des anciens fichiers dans `pdf/archive/` (`zeta-diagnostic_SKILL.md.bak-…`, `phase-c-illinois_SKILL.md.bak-…`, `skills_export_phase-c-illinois_SKILL.md.bak-…`).

## 2. Archivage des doublons `~/.claude/skills/` (R10)

Rien à déplacer pendant cette session : les 5 doublons (`phase-c-illinois`, `riemann-bastion-hardening`, `riemann-code-review`, `riemann-lab`, `riemann-security-review`) avaient déjà été déplacés (sans suppression) vers `~/archive_skills_utilisateur_20261114/` à 18h21 le même jour. `~/.claude/skills/` ne contient plus que `claude-statusbar` et `synced`. Le « go archive » n'a donc pas été nécessaire.

## 3. Références aux anciens noms

| Fichier:ligne | Catégorie | Action |
|---|---|---|
| `.claude/skills/*/SKILL.md:2` (`name:`, 2 skills) | vivant | corrigé |
| `.claude/skills/riemann-agent-bridge/SKILL.md:31` et `:129` | vivant | corrigé |
| `.claude/skills/riemann-code-review/SKILL.md:120` | vivant | corrigé |
| `.claude/skills/riemann-statistics-gue/SKILL.md:115` | vivant | corrigé |
| `.claude/skills/riemann-lab/references/Bibliotheques.md:479` | vivant | corrigé |
| `docs/Bibliotheques.md:479` | vivant | corrigé |
| `AGENTS.md:11` et `:35` | vivant | corrigé |
| `skills_export/phase-c-illinois/SKILL.md:2` | doute, tranché (recommandation appliquée) | dossier renommé et `name:` corrigé |
| `skills_export/riemann-lab/references/Bibliotheques.md:479` | doute, tranché | corrigé |
| `docs/images/workflow_post_version_riemann_lab.svg:95` | doute, tranché | un mot corrigé (chemin déjà périmé, laissé) |
| `docs/archive/discusion_claude_2026-09-27.md:110` | historique | laissé |
| `scripts/ia_prompts/ia_prompts_riemann_lab_complet.md` (lignes 242, 481, 529, 593, 713, 813) | historique (prompts passés) | laissé |
| `pdf/site/maj_site_20261111/RAPPORT_MAJ_FIABILITE_PDF_20261111_2254.md` (lignes 14, 40 à 43) | historique (rapport daté) | laissé |
| Wiki `JOURNAL.md`, `Handoff.md`, `etat_rag_brainvault_20260704.md` | historique | laissé |
| Wiki `STACK.md:300`, `Arbre_dossiers_projet.md:9`, `Bibliotheques.md:479` | vivant, mais dans le wiki | **non corrigé** (le prompt interdit d'y toucher) : point ouvert |

## 4. Contrôles

- `name:` = nom du dossier pour les 12 skills (vérifié).
- Descriptions ≤ 1 024 pour les 2 skills renommés (167 et 374, `yaml.safe_load`).
- Secrets : sortie vide sur les 2 dossiers, avec les motifs de la règle d'audit du projet (`duckdns`, clés privées, `ghp_`, `github_pat`, `token=`, `passw=`, MAC, IPv4, e-mails). Le modèle `PROMPT_INSTALL_SKILL_MODELE.md` v3 est introuvable dans `src/ia/prompts/` : sa commande « par valeurs » n'a pas été lancée.
- Audit des lignes ajoutées avant commit : aucune correspondance.

## 5. Commits par branche (cherry-pick -x, sans `--force`, worktrees temporaires supprimés)

| Branche | Commit | Fichiers |
|---|---|---|
| `Riemann_Lab_IA` | `03304e1` | 11 (13 insertions, 13 suppressions, 3 renommages) |
| `main` | `dfd4d04` | 11, sans conflit |
| `Riemann_Lab_C` | `6382c79` | 11, sans conflit |
| `Riemann_Lab_Test` | `3480038` | 11, sans conflit |

`git diff Riemann_Lab_IA <branche> -- .claude/skills/` : 0 ligne pour les 3 branches ; idem pour `skills_export/`. Aucun fichier « vivant » absent d'une branche.

Écart de procédure : un `git add -N .` lancé par erreur a marqué en intention d'ajout tous les fichiers non suivis ; annulé aussitôt par `git reset`, rien commité, puis indexation explicite des seuls chemins ciblés.

## 6. Zips pour le compte (`A_DEPOSER/zips_compte/`, locaux, non commités)

| Zip | `SKILL.md` | SHA-256 complet (zip = dépôt, vérifié) |
|---|---|---|
| `riemann-zeta-diagnostic.zip` | 2 305 octets | `5bab8a68065122e7d4a8da2bfef8af6fcfd4e44ed2f5baf8d28336f34c450e08` |
| `riemann-phase-c-illinois.zip` | 20 979 octets | `665a5b0efb3ef40dd53eb0472ddf8fc3432ef6fcaaa2376f5b2c7b7a81d0f0c4` |

Dossier du skill à la racine de chaque zip, aucun fichier `*.bak*`.

## 7. Points ouverts

1. Wiki : corriger `STACK.md:300` et `Arbre_dossiers_projet.md:9` (et `Bibliotheques.md:479`) après accord de hprzeta.
2. Modèle v3 du prompt d'installation introuvable : à retrouver pour relancer le contrôle de secrets « par valeurs ».
3. Décisions déjà ouvertes avant ce prompt (inchangées) : e-mail ligne 112 de `riemann-security-review`, D8b, critère `fe80::`, PC2 `PermitRootLogin`.

## Après Claude Code (hprzeta, sur claude.ai)

Paramètres → Skills : supprimer `zeta-diagnostic` et `phase-c-illinois`, importer les 2 zips de `zips_compte/`, puis donner ce rapport à claude.ai (SKILLS ZETA), qui met à jour les instructions et l'ETAT. Relancer ensuite Claude Code et vérifier `/skills` (12 en « project », tous `riemann-`).

---
*audit_skills_20261114_rename.md — 2026-11-14 — 85 lignes*
