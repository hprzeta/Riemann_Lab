# Audit — installation du skill `riemann-site-update` (PC1)

> **Date :** 2026-11-14 · **Dépôt :** `Riemann_Lab` · **Branche source :** `Riemann_Lab_IA`
> **Source :** `skill_site_20261114_v3.zip` (rédigé par claude.ai, projet SKILLS ZETA)
> **Règle :** la copie du dépôt est la copie de référence ; une copie identique est enregistrée dans le compte Claude.

## Réponse directe

Le skill est installé, committé (`ebf80fc`) et poussé sur `Riemann_Lab_IA`. Il est reporté par `cherry-pick -x` sur `main`, `Riemann_Lab_C` et `Riemann_Lab_Test` : **poussés** le 14/11/2026 (`84f5495`, `b7875ca`, `f3d756c`), sans `--force`. Un point 🟡 : le critère `grep` du prompt est trop large (faux positif sur le mot `PrivateKey`, voir tableau).

## Tableau d'audit

| # | Contrôle | Résultat | Statut |
|---|---|---|---|
| 0 | Zip extrait dans `src/ia/prompts/skill_site_20261114/` (2 fichiers + dossier) | Fait, dossier cible neuf | 🟢 |
| 1 | Dossier d'audit créé (`pdf/audits_skills/audit_skills_20261114/`, `captures/`) | Fait | 🟢 |
| 2 | État AVANT : branche `Riemann_Lab_IA`, `riemann-site-update` absent de `.claude/skills/` | Constaté | 🟢 |
| 3 | `.gitignore` : `.claude/*` ignoré mais `!.claude/skills/**` réintègre les skills ; `git check-ignore -q` → rc=1 (non ignoré) | Aucun STOP déclenché | 🟢 |
| 4a | Copie de `SKILL.md`, `diff` avec la source du zip | Vide (identique) | 🟢 |
| 4b | Frontmatter `name: riemann-site-update` | Présent (ligne 2) | 🟢 |
| 4c | `grep -nE '([0-9]{1,3}\.){3}[0-9]{1,3}\|ghp_\|PrivateKey'` « doit ne rien renvoyer » | Renvoie la ligne 79 : liste des motifs d'audit (mots `PrivateKey`, `ghp_`…), aucune valeur | 🟡 |
| 4d | Audit élargi avant push (IP, MAC, e-mail, `duckdns`, `token=`, `fe80::`…) | Seule la ligne 79 (noms de motifs) ; aucun secret réel | 🟢 |
| 4e | Commit (après « go commit ») : 1 seul fichier indexé, pas de `git add -A` | `ebf80fc`, +141 lignes | 🟢 |
| 4f | Push `Riemann_Lab_IA` (après « go push »), sans `--force` | `f1dea2a..ebf80fc` accepté | 🟢 |
| 4g | Report `cherry-pick -x` sur `main` / `Riemann_Lab_C` / `Riemann_Lab_Test` | Sans conflit ; contenu identique à la source ; ligne `-x` présente | 🟢 |
| 4h | Push des 3 branches reportées (après « go push »), sans `--force` | `bdf53ca..84f5495` (main), `4cdf365..b7875ca` (C), `ded9e60..f3d756c` (Test) ; 4 branches à niveau avec `origin` | 🟢 |
| 5a | État APRÈS : `git log -1 --stat` | `ebf80fc`, 1 fichier changé | 🟢 |
| 5b | Skill visible dans la liste des skills de la session courante | Oui (vu après installation) | 🟢 |
| 5c | Vérification dans une **nouvelle** session lancée depuis le dépôt | Pas encore faite | 🟡 |
| 6 | Rapport + HANDOFF + dépôt dans `A_DEPOSER/` | Fait (ce fichier) | 🟢 |
| — | Aucun point 🔴 | — | 🟢 |

## Commits

| Branche | Commit | Origine | Poussé |
|---|---|---|---|
| `Riemann_Lab_IA` | `ebf80fc` | commit d'origine | oui |
| `main` | `84f5495` | `cherry-pick -x ebf80fc` | oui |
| `Riemann_Lab_C` | `b7875ca` | `cherry-pick -x ebf80fc` | oui |
| `Riemann_Lab_Test` | `f3d756c` | `cherry-pick -x ebf80fc` | oui |

## Méthode et réserves

- Les cherry-pick ont été faits dans des `git worktree` temporaires (supprimés ensuite), pour ne pas toucher à l'arbre de travail de `Riemann_Lab_IA` qui contient des modifications non commitées étrangères à cette tâche (`monitoring/Monitoring-Runs.md`). Aucune de ces modifications n'a été indexée.
- `src/ia/prompts/skill_site_20261114/` reste **LOCAL ONLY** (jamais `git add`).
- Le dossier `A_DEPOSER/` suit la convention du `SKILL.md` : il est rangé dans le dossier de l'audit, local seulement.
- Sur les 3 branches reportées, le motif `!.claude/skills/**` du `.gitignore` n'a pas été vérifié ; sans effet sur un fichier déjà suivi, mais à contrôler avant d'y ajouter d'autres skills.

## Écarts à corriger (pour claude.ai)

1. Prompt d'installation, étape 4 : remplacer le critère `grep … PrivateKey` par un test qui ignore les listes de motifs (ou accepter explicitement la ligne 79 du skill).
2. Prompt d'installation : préciser où se range `A_DEPOSER/` (ici : dossier de l'audit).

---
*audit_skills_20261114.md — 2026-11-14 — 55 lignes*
