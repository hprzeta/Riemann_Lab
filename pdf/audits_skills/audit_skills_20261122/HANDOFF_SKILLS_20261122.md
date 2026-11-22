# HANDOFF SKILLS ZETA — 22/11/2026

> Un seul handoff pour la session. Machine : PC1. Prompt exécuté : `PROMPT_ADOPTION_GRILL_ME_20261122`. Rapport détaillé (en anglais) : `audit_skills_20261122_adoption.md` et `.pdf`.

## Réponse directe

`grill-me` et `grilling` sont adoptés dans le dépôt : **15 skills identiques sur les 4 branches**, poussés sans `--force`. Les 3 nouveaux skills **et** les 4 réimportés sont **confirmés dans le compte** (synchronisation de 17:43:33) : 8 identiques à l'octet, 7 qui ne diffèrent que par la mise en forme de l'en-tête, 0 ancien, 0 absent. Reste à votre charge la vérification `/skills` et le test `/grill-me`.

## Fait

| Élément | Détail |
|---|---|
| Skills tiers | `grilling`, `grill-me` (MIT, © 2026 Matt Pocock), copie identique à `mattpocock/skills` `abeeaf9`, avec `LICENSE` et `SOURCE.md` (D17) |
| Règle D20 | une puce dans `CLAUDE.md` et `AGENTS.md` |
| Commits `Riemann_Lab_IA` | C1 `c25f109`, C2 `5129e36`, C3 `cf24144` (ETAT) |
| Cherry-picks C1 + C2 | `main` `cd7ac88` / `f6d8eae` ; `Riemann_Lab_C` `6558ef8` / `8580522` ; `Riemann_Lab_Test` `7b975ab` / `a37e8bb` |
| Wiki `master` | W1 `2e82ee0` : `STACK.md` (2 lignes + note) et `JOURNAL.md` (entrée en haut) ; site `docs/` non modifié (D18) |
| Zips pour le compte | 3 zips dans `A_DEPOSER/zips_compte/` (SHA-256 du `SKILL.md` = dépôt) |
| Contrôles | secrets par valeurs : 0 (témoin positif 4/4) ; descriptions 51, 152 et 530 caractères ; 0 écart entre branches |

## Écarts de procédure

1. `POUR_SKILLS_ZETA_grill_me_20261122.md` et `~/outils/skills_tiers/` absents : la copie du bac à sable TELANDROID a tenu lieu de copie mise de côté (option B).
2. Coquille du prompt : empreinte attendue de `grilling/SKILL.md` à 63 caractères ; corrigée (prompt et `grilling_SOURCE.md`) avec la valeur réelle confirmée. claude.ai doit corriger sa propre source.
3. Entrée JOURNAL placée **en haut** (règle du fichier), deux phrases reformulées ; pied de `AGENTS.md` complété ; 69 modifications étrangères au lieu de ~217 ; description de wireguard à 530 caractères et non 532.
4. Un `.git/index.lock` vide et périmé (11:49) a été **déplacé** (`.git/index.lock.perime-20261122-1749`), non supprimé.

## Étape 8 : compte vs dépôt (R9 fermé sur le fond)

Dossier `~/.claude/skills/synced/` : synchronisations de 17:23:31 (25 skills), 17:33:32 (3 nouveaux skills présents) puis **17:43:33 (28 skills, après la réimportation des 4 anciens)**. Comparaison finale sur la dernière.

| Groupe (15 skills) | Skills |
|---|---|
| Identiques à l'octet (8) | `grill-me`, `grilling`, `riemann-wireguard-diagnostic`, `riemann-bastion-hardening`, `riemann-proof-status`, `riemann-site-check`, `riemann-site-update`, `riemann-zeta-diagnostic` |
| Seule la mise en forme diffère (7) | `riemann-agent-bridge`, `riemann-code-review`, `riemann-lab`, `riemann-literature-scout`, `riemann-phase-c-illinois`, `riemann-security-review`, `riemann-statistics-gue` : corps, `name`, autres clés et description (espaces normalisés) identiques ; le compte réécrit la description sur une ligne |
| Compte plus ancien | aucun (les 4 anciens sont à jour) |
| Absent du compte | aucun |

Aucune copie autonome de `grill-me`, `grilling` ou `riemann-*` dans `~/.claude/skills/`. L'égalité à l'octet n'est possible que pour 8 skills : le compte normalise l'en-tête des 7 autres, comme avant cette adoption. Ce n'est pas une dérive de contenu.

## Reste à faire

| # | Point | Qui |
|---|---|---|
| `/skills` | nouvelle session Claude Code depuis le dépôt : vérifier « 15 en project » (non vérifiable depuis la session courante) | hprzeta |
| R21 | test `/grill-me` dans une conversation claude.ai (`grilling` chargé ? sous-agents ? questions par tour) | hprzeta |

Fermés aujourd'hui : R19 (import des 3 nouveaux skills) et R9 sur le fond (comparaison sur 15, 0 ancien, 0 absent) ; R18 abandonné (option B suivie, clone neuf de l'amont = référence).

## Nettoyage du soir (D22 et R25)

- **D22 :** la règle « non vérifié » est au § 4 de `claude/MODELE_INSTRUCTIONS_PROJET.md` (95 lignes). Commit `ebdc57a`, poussé sur `Riemann_Lab_IA` seule (`claude/` n'existe pas sur les 3 autres branches).
- **codeburn déplacé, non supprimé** (option a, conforme à TEL-D16) : `~/outils/codeburn` (229 Mo, commit `c08d761`, construit). `--help` vérifié hors ligne sous `strace` : 0 connexion IP. Usage permis : `report` et `--help`, hors ligne, avec `CODEBURN_PRICING_SNAPSHOT_ONLY=1`, `CODEBURN_FX_NO_FETCH=1` et un `HOME` dédié. Jamais `quota`, `sync`, `share`, `web`, `mcp`, `menubar`, `guard`, `optimize`, `update`.
- **Supprimé après « go suppression » :** 13 `.bak-20261122*` (racine, `pdf/archive/`, `pdf/audits_skills/`, `src/ia/prompts/`), le `.git/index.lock.perime-20261122-1749` (14 fichiers, 452 900 octets), puis le bac à sable `~/bac_a_sable/audit_skills_20261122` (44 Mo) et `~/bac_a_sable` (vide). R18 est abandonné.
- **Gardés :** `claude/MODELE_INSTRUCTIONS_PROJET.md.bak-202611221802` (à traiter au prochain nettoyage) et 4 `.bak` de la session site (3 dans `pdf/site/maj_site_20261122/`, 1 dans `scripts/`), hors périmètre.
- Rapport : `audit_skills_20261122_nettoyage.md` et `.pdf`.

## Local, non commité

- Rapports `audit_skills_20261122_nettoyage.md` et `.pdf`, `audit_skills_20261122_adoption.pdf`, captures, zips (`A_DEPOSER/zips_compte/`) et le dossier `nettoyage/`.
- Le présent handoff, modifié après son commit `69332e7` (section « Nettoyage du soir » ajoutée) : à commiter sur « go commit ».
- Les `.bak` conservés cités ci-dessus, plus `HANDOFF_SKILLS_20261122.md.bak-202611221805` (sauvegarde de ce handoff avant sa modification, identique à la version commitée).


---
<sub>HANDOFF_SKILLS_20261122.md · SKILLS ZETA · Mis à jour le 2026-11-22 · 66 lignes</sub>
