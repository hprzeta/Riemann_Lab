# HANDOFF — skills du dépôt (14/11/2026)

## État

- Skill installé : `.claude/skills/riemann-site-update/SKILL.md` (141 lignes, identique à la source du zip).
- `Riemann_Lab_IA` : commit `ebf80fc`, **poussé** (`f1dea2a..ebf80fc`).
- `main` (`84f5495`), `Riemann_Lab_C` (`b7875ca`), `Riemann_Lab_Test` (`f3d756c`) : `cherry-pick -x` fait, sans conflit, **poussés** (sans `--force`).
- Rapport d'audit : `pdf/audits_skills/audit_skills_20261114/audit_skills_20261114.md` (aucun 🔴, trois 🟡).

## Reste à faire (dans l'ordre)

1. ~~Push des 3 branches~~ : **fait** (4 branches à niveau avec `origin`).
2. Ouvrir une **nouvelle** session Claude Code dans le dépôt et vérifier que `riemann-site-update` figure dans la liste des skills.
3. Donner le .md à claude.ai (projet SKILLS ZETA) pour corriger le critère `grep … PrivateKey` du prompt d'installation (faux positif sur la ligne 79 du skill) et préciser l'emplacement de `A_DEPOSER/`.

## Points d'attention

- `monitoring/Monitoring-Runs.md` modifié et de nombreux fichiers non suivis existaient avant la tâche : rien n'a été indexé en dehors du skill.
- `src/ia/prompts/` reste LOCAL ONLY.

## Ajout R4 / R5 — 3 skills du compte copiés dans le dépôt

- `riemann-site-check`, `zeta-diagnostic`, `riemann-bastion-hardening` : commit `4eeaaa9` sur `Riemann_Lab_IA`, **poussé** (`23f76b2..4eeaaa9`).
- Reports `cherry-pick -x`, **poussés** : `main` `81759aa`, `Riemann_Lab_C` `d600bc1`, `Riemann_Lab_Test` `1bfa7c3`. `git diff` sur `.claude/skills/` vide entre `Riemann_Lab_IA` et chaque branche.
- R3 🟢 : motif `!.claude/skills/**` présent dans le `.gitignore` des 4 branches.
- Rapport : `audit_skills_20261114_r4r5.md` (aucun 🔴, quatre 🟡).

### Reste à faire

1. **R2** : nouvelle session Claude Code dans le dépôt ; vérifier que `riemann-site-update` et les 3 nouveaux skills figurent dans la liste.
2. Donner les .md de `A_DEPOSER/` à claude.ai (projet SKILLS ZETA) : décision D7 (marqueurs `[IP-…]` dans le dépôt, original dans le compte), casse du nom du prompt, guillemets sur `name:`.
3. « go commit » du rapport `audit_skills_20261114_r4r5.md`, du handoff mis à jour et de `RAPPORT_INVENTAIRE_SKILLS_20261114.md` (non commités), puis « go push » sur `Riemann_Lab_IA` seulement.

## Ajout alignement dépôt / compte (D7, D8, R7) — 14/11/2026

- **D8 appliqué** : `riemann-lab` (encadré « Wiki GitHub » et 2 titres), commit `15e41da` sur `Riemann_Lab_IA`, reports `main` `ee9c141`, `Riemann_Lab_C` `219ae07`, `Riemann_Lab_Test` `a3e42f6` ; tout est **poussé**, `git diff` sur `.claude/skills/` vide entre les 4 branches.
- **9 zips** prêts (local) : `pdf/audits_skills/audit_skills_20261114_align/A_DEPOSER/zips_compte/` ; SHA-256 des `SKILL.md` identiques au dépôt. Pas de zip pour `riemann-site-update` (déjà aligné dans le compte).
- Rapport : `audit_skills_20261114_align.md` (aucun 🔴, 8 🟡).

### Reste à faire

1. **hprzeta, sur claude.ai** : Paramètres → Skills, importer les 9 zips (remplacer s'il existe) ; redonner le rapport à claude.ai (SKILLS ZETA) pour la comparaison SHA-256.
2. **R2** : lancer une vraie nouvelle session dans le dépôt et vérifier la liste (12 skills attendus, pas 14).
3. **Décisions** : copies `~/.claude/skills/` (3 diffèrent du dépôt) ; e-mail ligne 112 de `riemann-security-review` ; D8b (bloc « Commandes interdites », « Piège 1 »).
4. **« go commit »** puis **« go push »** (`Riemann_Lab_IA` seulement) du rapport d'alignement, du handoff et de `captures/etape0_liste_skills_session.md` (étape 6 du prompt).

---
*HANDOFF_SKILLS_20261114.md — 2026-11-14 — 48 lignes*
