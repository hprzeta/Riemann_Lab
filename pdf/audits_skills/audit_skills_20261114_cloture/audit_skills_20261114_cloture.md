# Audit — clôture du chantier skills — 14/11/2026

> Prompt : `src/ia/prompts/cloture_skills_20261114/PROMPT_CLOTURE_SKILLS_20261114.md` (local, non versionné). Règle D1 : le dépôt `.claude/skills/<nom>/` fait référence ; D9 : pas d'autre copie ; D11 : tout skill est préfixé `riemann-`. Jamais `--force`, jamais `git add -A`.

## 1. Tableau des étapes

| Étape | Objet | État | Détail |
|---|---|---|---|
| 0 | Rangement du prompt et du modèle v3.1 | 🟢 | `src/ia/prompts/cloture_skills_20261114/` et `src/ia/prompts/PROMPT_INSTALL_SKILL_MODELE.md` (60 lignes, « Version 3.1 » ligne 4). Aucun fichier existant : pas de `.bak`. Dossier ignoré par git (`.gitignore:90`). |
| 1 | État AVANT | 🟢 | Branche `Riemann_Lab_IA`, arbre propre sur `.claude/` et `skills_export/`, 12 skills tous préfixés `riemann-`. |
| 1 | R16 (compte claude.ai) | 🟢 | Réponse de hprzeta : **oui**, « Créé par vous » affiche 12 skills, sans `zeta-diagnostic` ni `phase-c-illinois`. |
| 1 | R2 (`/skills`) | 🟢 | Réponse de hprzeta : **oui**, 12 lignes « project », toutes `riemann-`. |
| 2 | R14 `skills_export/` | 🟢 | Supprimé (voir §2). |
| 3 | R15 wiki | 🟢 | 3 pages corrigées, `c8dad3b` (voir §3). |
| 4 | Commit du code | 🟢 | `971062b`, 4 branches à niveau, diff vide (voir §4). |
| 5 | Handoff : décisions closes | 🟢 | Entrée datée en tête du bloc `PROMPT_REPRISE` (sauvegarde `.bak-…d` faite). |
| 6 | Rapport | 🟡 | Ce fichier ; commit et push à valider (STOP « go commit », « go push »). |

## 2. R14 — `skills_export/` (4ᵉ copie)

- Contenu : 160 Ko ; `riemann-lab/` (`SKILL.md` et 2 références) et `riemann-phase-c-illinois/`.
- Usage vivant : aucun (`git grep` vide hors `pdf/audits_skills/` et `pdf/archive/` ; ni script, ni `.gitignore`, ni `CLAUDE.md`, ni `AGENTS.md`, ni configuration locale). Seules mentions : `md/…/synthese_skills_zeta.md`, document local de synthèse.
- Écart avec `.claude/skills/` : copie en retard. Les lignes propres à `skills_export/` sont périmées (« 96 manquants » avant la révision à 97 ; anciens titres KaTeX sans l'encadré « Wiki GitHub »). Références de `riemann-lab` identiques.
- Sauvegarde locale comparée octet par octet : `pdf/archive/skills_export_202611141924/`.
- Suppression : `git rm -r skills_export/` après « go export » ; 4 fichiers, 3 389 lignes. Aucune mention vivante à retirer.

## 3. R15 — wiki (`Riemann_Lab.wiki`, `master`)

| Page | Ligne | Action |
|---|---|---|
| `STACK.md` | 300 | `phase-c-illinois` → `riemann-phase-c-illinois` (tableau des skills) |
| `Arbre_dossiers_projet.md` | 9 | idem, colonnes alignées |
| `Bibliotheques.md` | 479 | idem |
| `STACK.md` | 307 et 695 | **laissé** : notes datées de l'audit du 06/07/2026 (historique) |
| `JOURNAL.md`, `Handoff.md` du wiki, `etat_rag_brainvault_20260704.md` | — | laissé (historique) |

Aucune occurrence de `zeta-diagnostic` dans les 3 pages. Pieds de page : mention du 14/11 ajoutée, nombre de lignes inchangé (709, 168, 972, vérifié `wc -l`). Audit des lignes ajoutées (commande du modèle v3.1) : sortie vide. Sauvegardes `.bak` rangées dans `pdf/archive/`, hors du wiki.

## 4. Commits par branche (cherry-pick -x, sans `--force`, worktrees temporaires supprimés)

| Dépôt / branche | Commit | Message |
|---|---|---|
| Code `Riemann_Lab_IA` | `971062b` | `chore(skills): remove skills_export copy (D9)` |
| Code `main` | `c539689` | idem, sans conflit |
| Code `Riemann_Lab_C` | `3bd4635` | idem, sans conflit |
| Code `Riemann_Lab_Test` | `dee56dc` | idem, sans conflit |
| Wiki `master` | `c8dad3b` | `docs(wiki): rename skills with riemann- prefix` (`62d8de8..c8dad3b`) |

`git diff Riemann_Lab_IA <branche> -- .claude/skills/ skills_export/` : 0 ligne pour `main`, `Riemann_Lab_C` et `Riemann_Lab_Test`. L'audit des lignes ajoutées avant commit est resté vide.

## 5. Décisions closes et points ouverts

**Clos :**
- E-mail ligne 112 de `riemann-security-review` : adresse publique, laissée.
- D8b : laissé tel quel (l'encadré « Wiki GitHub » prime).
- Critère `fe80::` : le modèle v3.1 utilise `fe80::[0-9a-f]+:`.
- Import des zips de l'alignement : fait.
- Modèle v3 « introuvable » : rangé à l'étape 0 (v3.1).

**Ouvert :**
- PC2 `PermitRootLogin` à aligner sur PC4 (chantier sécurité à part, en LAN, skill `riemann-bastion-hardening`).

**Écarts de procédure signalés :**
- Le zip a été extrait d'abord dans un dossier isolé du scratchpad (fichier téléchargé, non fiable) avant le rangement officiel.
- Le « bye bye » placé au début de la demande a été traité en fin de chantier, après le rapport.

---
*audit_skills_20261114_cloture.md — 2026-11-14 — 68 lignes*
