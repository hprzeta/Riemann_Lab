# État du projet SKILLS ZETA — 14/11/2026 (fin de journée)

> Rédigé sur claude.ai (projet SKILLS ZETA). Remplace la version du matin.

## Réponse directe

**Chantier skills clos le 14/11/2026.** Restent des points mineurs (R9, R12, R13).

Les **12 skills**, tous préfixés `riemann-`, sont alignés entre le dépôt (`.claude/skills/`, 4 branches) et le compte claude.ai. Claude Code les charge depuis le dépôt (`/skills` : 12 en « project »). Le miroir `skills/` de ce projet est supprimé (D9).

## Fait

| Élément | Preuve |
|---|---|
| `riemann-site-update` v3 (141 l.) dans le dépôt et le compte | `ebf80fc` (+ reports) ; compte réimporté à 17:55, 12 sections chargées |
| `riemann-site-check`, `zeta-diagnostic`, `riemann-bastion-hardening` copiés dans le dépôt | `4eeaaa9` (+ reports) |
| D8 : encadré « Wiki GitHub » dans `riemann-lab` | `15e41da` ; reports `ee9c141`, `219ae07`, `a3e42f6` |
| `riemann-proof-status` : description raccourcie (≈ 1 150 → 722 car.) | `e342b1e` ; reports `af76a0d`, `4d771f0`, `1f6448c` ; rapport `e5a35ea` |
| 9 skills importés dans le compte (dont `riemann-lab` et `riemann-bastion-hardening` supprimés puis réimportés) | « Créé par vous » = 12 ; contenus vérifiés au chargement (encadré D8, marqueurs `[IP-…]` D7, nouvelle description) |
| R2 : nouvelle session Claude Code, `/skills` | 12 skills en « project » ; les copies du compte sont accessibles par le préfixe `anthropic-skills:` |
| Instructions du projet, section 8 : bloc « Alignement des skills (dépôt = compte) » | Enregistré et relu (5 912 car.) |
| Modèle de prompt d'installation v3 | `claude/PROMPT_INSTALL_SKILL_MODELE.md` |
| Renommage `zeta-diagnostic` → `riemann-zeta-diagnostic`, `phase-c-illinois` → `riemann-phase-c-illinois` (références « vivantes » corrigées, `skills_export/` compris) | `03304e1` ; reports `dfd4d04`, `6382c79`, `3480038` ; 2 zips importés dans le compte |
| 5 doublons de `~/.claude/skills/` archivés dans `~/archive_skills_utilisateur_20261114/` (sans suppression) | Rapport `audit_skills_20261114_rename.md` ; reste `claude-statusbar` et `synced` |
| Clôture (prompt `PROMPT_CLOTURE_SKILLS_20261114`) : `skills_export/` supprimé (D9, aucun usage vivant, sauvegarde locale) ; wiki `STACK.md:300`, `Arbre_dossiers_projet.md:9`, `Bibliotheques.md:479` renommés ; modèle v3.1 rangé dans `src/ia/prompts/` ; e-mail l. 112, D8b et `fe80::` clos | Code `971062b` ; reports `c539689`, `3bd4635`, `dee56dc` ; wiki `c8dad3b` ; rapport `audit_skills_20261114_cloture.md` |
| R2 et R16 confirmés par hprzeta : `/skills` = 12 « project », tous `riemann-` ; compte = 12 skills, sans anciens noms | Rapport de clôture, étape 1 |
| Rapports | `audit_skills_20261114.md`, `audit_skills_20261114_rename.md`, `audit_skills_20261114_r4r5.md`, `audit_skills_20261114_align.md` (commités sur `Riemann_Lab_IA`) |

## Reste ouvert

| # | Point | Qui |
|---|---|---|
| R9 | Comparaison SHA-256 dépôt / compte des 12 skills (la session claude.ai du 14/11 ne voyait que l'ancienne copie synchronisée) | claude.ai, prochaine session |
| R12 | `riemann-lab` §8 cite `katex-cheatsheet.md`, `python-zeta.md`, `wiki-templates.md` ; `references/` contient `Bibliotheques.md` et `Formules_zeta.md` (D10 proposé) | hprzeta |
| R13 | `skill_riemann-proof-status.md` à la racine du projet : ancienne copie (description longue), hors miroir | hprzeta (supprimer ?) |
| R6 | Erreurs mathématiques trouvées par la vérification du site | Projet SITE ZETA |

## Décisions

| # | Décision |
|---|---|
| D1 | Chaque skill a deux copies identiques : référence dans le dépôt (`.claude/skills/<nom>/`), copie dans le compte. Toute modification part du dépôt. |
| D2 | Les instructions des projets suivent `MODELE_INSTRUCTIONS_PROJET.md` ; seules la section 8 et les `<<…>>` changent. |
| D3 | Les procédures répétitives vivent dans des skills ou des modèles de prompt ; les instructions n'y renvoient que par une ligne. |
| D4 | Les décisions de contenu d'un projet restent dans son `ETAT_*` ; un skill ne garde que les règles durables. |
| D5 | Rapports d'audit des skills : `pdf/audits_skills/audit_skills_<AAAAMMJJ>/`, avec `A_DEPOSER/` dans ce dossier. |
| D6 | Contrôle des secrets par **valeurs** (formats réels), pas par noms de motifs. |
| D7 (adopté) | Aucune IP dans un skill : marqueurs `[IP-LAN-PC4]`, `[IP-TUNNEL-PC4]` dans le dépôt **et** le compte ; vraies valeurs dans `~/.ssh/config`. |
| D8 (adopté) | `riemann-lab` : sur le wiki GitHub, les règles KaTeX mesurées de `riemann-site-update` §7 priment ; les règles `\_`/`\%` ne valent que pour le HTML du site (à revérifier). |
| D9 (adopté) | Pas de troisième copie : le miroir `skills/` du projet SKILLS ZETA est supprimé. |
| D11 (adopté) | Tout skill porte le préfixe `riemann-` (nom du dossier = `name:`). |
| D10 (proposé) | Corriger les noms de fichiers de `riemann-lab` §8 pour qu'ils correspondent à `references/`. |

## Règles apprises le 14/11

- Import dans le compte : **description ≤ 1 024 caractères**, sinon refus.
- Pas d'option « Remplacer » dans Paramètres → Skills : supprimer l'ancienne version, puis importer.
- Un skill du dépôt (« project ») masque la copie du compte de même nom dans Claude Code ; celle-ci reste accessible par `anthropic-skills:<nom>`.

---
*ETAT_SKILLS_ZETA_20261114.md · projet SKILLS ZETA · hprzeta · MAJ 14 novembre 2026 (soir) · 61 lignes*
