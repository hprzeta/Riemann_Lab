# Audit — copie de référence de 3 skills du compte (R4, R5) — 14/11/2026

> **Dépôt :** `Riemann_Lab` · **Branche source :** `Riemann_Lab_IA`
> **Source :** `SKILLS_R4_R5_20261114.zip` (préparé sur claude.ai, projet SKILLS ZETA)
> **Suite de :** `audit_skills_20261114.md` (skill `riemann-site-update`)

## Réponse directe

Les 3 skills `riemann-site-check`, `zeta-diagnostic` et `riemann-bastion-hardening` sont committés (`4eeaaa9`) et poussés sur les 4 branches, sans `--force`. Le contenu est identique sur toutes les branches (`git diff` vide). Un point 🟡 reste ouvert : la vérification dans une **nouvelle** session Claude Code (R2).

## Tableau d'audit

| # | Contrôle | Résultat | Statut |
|---|---|---|---|
| 0 | Zip extrait dans `src/ia/prompts/skills_r4_r5_20261114/` (3 skills, prompt, rapport d'inventaire) | Fait, dossier cible neuf | 🟢 |
| 0b | Nom du prompt : `PROMPT_INSTALL_…` (majuscules) dans le zip, `PROMPT_install_…` dans la demande | Lu tel quel dans le zip | 🟡 |
| 1 | `captures/` et `A_DEPOSER/` dans le dossier d'audit ; rapport d'inventaire copié | Fait | 🟢 |
| 2 | État AVANT : branche `Riemann_Lab_IA`, 9 skills présents, aucun des 3 dossiers | Constaté | 🟢 |
| R3 | Motif `!.claude/skills/**` dans le `.gitignore` des 4 branches (`Riemann_Lab_IA`, `main`, `Riemann_Lab_C`, `Riemann_Lab_Test`) | Présent partout, lignes 27 à 32 identiques | 🟢 |
| 3 | `git check-ignore -q` sur les 3 chemins | rc=1 (non ignorés) ; aucun STOP | 🟢 |
| 4a | Copie des 3 `SKILL.md` ; `diff` avec la source du zip | Vide pour les 3 | 🟢 |
| 4b | Frontmatter `name:` égal au nom du dossier | Oui, valeur entre guillemets (`name: "…"`), équivalente pour un parseur YAML | 🟡 |
| 4c | Contrôle des secrets par valeurs (IPv4, MAC, `fe80::`, jetons, clé privée, e-mail) | Sortie vide sur les 3 fichiers | 🟢 |
| 4d | Écart volontaire : adresses IP de PC4 remplacées par `[IP-LAN-PC4]` et `[IP-TUNNEL-PC4]` (ligne 12 de `riemann-bastion-hardening`) | Marqueurs présents ; la copie du compte garde l'original (D7 proposé, décision de hprzeta) | 🟡 |
| 4e | Commit (après « go commit ») : 3 fichiers indexés, pas de `git add -A` | `4eeaaa9`, +288 lignes | 🟢 |
| 4f | Audit des lignes ajoutées avant push | Sortie vide | 🟢 |
| 4g | Push `Riemann_Lab_IA`, puis `cherry-pick -x` sur 3 branches dans des worktrees temporaires, push des 3 | Sans conflit, sans `--force` | 🟢 |
| 5a | `git diff Riemann_Lab_IA <branche> -- .claude/skills/` | Vide pour `main`, `Riemann_Lab_C`, `Riemann_Lab_Test` | 🟢 |
| 5b | 4 branches à niveau avec `origin` | 0 commit d'écart partout | 🟢 |
| R2 | `riemann-site-update` et les 3 nouveaux skills visibles dans une **nouvelle** session lancée depuis le dépôt | Non fait : les 3 nouveaux skills apparaissent dans la liste de la session courante après le commit, mais le test demandé (nouvelle session) reste à faire | 🟡 |
| 6 | Rapport + mise à jour du handoff + dépôt dans `A_DEPOSER/` | Fait (ce fichier) | 🟢 |
| — | Aucun point 🔴 | — | 🟢 |

## Commits par branche

| Branche | Commit | Poussé | Plage |
|---|---|---|---|
| `Riemann_Lab_IA` | `4eeaaa9` | oui | `23f76b2..4eeaaa9` |
| `main` | `81759aa` | oui | `84f5495..81759aa` |
| `Riemann_Lab_C` | `d600bc1` | oui | `b7875ca..d600bc1` |
| `Riemann_Lab_Test` | `1bfa7c3` | oui | `f3d756c..1bfa7c3` |

Les 3 reports sont des `cherry-pick -x 4eeaaa9`.

## Méthode et réserves

- Cherry-pick dans des `git worktree` temporaires (supprimés ensuite) : l'arbre de travail de `Riemann_Lab_IA` contient des modifications étrangères (`monitoring/Monitoring-Runs.md`), jamais indexées.
- Aucun skill existant n'a été modifié.
- `src/ia/prompts/` et `A_DEPOSER/` restent locaux. Aucune valeur identifiante dans ce rapport.
- Le rapport n'est pas commité (en attente de « go commit »).

## Écarts à signaler à claude.ai

1. Casse du nom du prompt (`INSTALL` ou `install`) à harmoniser.
2. Frontmatter avec guillemets sur `name:` : les 3 nouveaux skills diffèrent du style sans guillemets de `riemann-site-update` ; à harmoniser si voulu.
3. Décision D7 : garder les marqueurs `[IP-…]` dans le dépôt et l'original dans le compte, ou aligner les deux.

---
*audit_skills_20261114_r4r5.md — 2026-11-14 — 59 lignes*
