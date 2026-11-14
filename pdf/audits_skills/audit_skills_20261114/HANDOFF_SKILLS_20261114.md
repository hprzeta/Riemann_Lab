# HANDOFF — skill `riemann-site-update` (14/11/2026)

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

---
*HANDOFF_SKILLS_20261114.md — 2026-11-14 — 22 lignes*
