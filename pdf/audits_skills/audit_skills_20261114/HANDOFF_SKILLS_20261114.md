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

---
*HANDOFF_SKILLS_20261114.md — 2026-11-14 — 35 lignes*
