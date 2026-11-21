# Rapport — règles communes des projets ZETA (2026-11-21)

Machine PC1, branche `Riemann_Lab_IA`, base `cb6901a`. Source : `prompt_regles_communes_20261121.zip` (dézippé dans `src/ia/prompts/`, local only). Aucun commit, aucun push à ce stade.

## Synthèse

| Étape | Objet | Heure | Statut |
|---|---|---|---|
| 0 | Préparation, modèles `formation.md` et `vault.md` lus | 18:41 | 🟢 |
| 1 | Diagnostic des dossiers | 18:42 | 🟢 |
| 2 | 9 règles créées | 18:43 | 🟢 |
| 3 | Captures MATH et BACKUP copiées | 18:43 | 🟢 |
| 4 | Captures CLONAGE sur PC1 | 18:44 | 🟡 (45/45 retrouvées, 36 sous un autre format de nom) |
| 5 | Scripts CLONAGE comparés au dépôt | 18:44 | 🟡 (3 empreintes différentes, `diff` impossible) |
| 6 | ORGANISATION_FICHIERS.md comparé au wiki | 18:44 | 🟢 |
| 6b | 14 ETAT annoncés, 12 copiés avec « État en bref » | 18:44 | 🟡 (2 dossiers absents) |
| 6c | Annexe du MODELE | 18:44 | 🟢 |
| 7 | git status, message proposé | 18:44 | 🟢 STOP avant « go commit » |

## Étape 1 — dossiers

| Dossier | md | pdf | src |
|---|---|---|---|
| site, optimisation, matos, clone, diagnostics, cluster, cours, script, archive | oui | oui | non |

`src/<d>` n'existe pour aucun dossier : les `paths:` des règles sont donc `md/<d>/**` et `pdf/<d>/**`. Rien n'a été créé.

## Étape 2 — règles

9 fichiers créés dans `.claude/rules/` (11 à 12 lignes chacun, ≤ 40). `grep` d'IP : vide. Correction après coup : `script.md` cite `ETAT_MONITO_ZETA.md` (le zip porte ce nom, pas `ETAT_MONITO_UPDATE_ZETA.md`).

## Étape 3 — captures

| Destination | Fichiers | Format |
|---|---|---|
| `pdf/cours/cours_math_20261121/captures/` | 8 (`screenzeta1–8.webp`) | WebP 1456×819 |
| `pdf/archive/backup_20261121/captures/` | 3 | WebP (1456×819 puis 2 en 1366×768) |

Aucun écrasement. Points : les 3 noms de `captures_backup` sont en mojibake (`dтАЩ├йcran`, encodage du zip), non renommés ; `.gitignore` n'exclut pas ces captures.

## Étape 4 — captures CLONAGE

45/45 retrouvées. 9 sous leur nom exact (`~/Téléchargements/` ×8, `~/Images/Captures d’écran/` ×1). 36 « Capture d’écran du 20260620 172013.png » existent sous la forme `Capture d’écran du 2026-06-20 17-20-13.png` dans `~/Images/Captures d’écran/` (correspondance par conversion du nom). Aucune suppression ; la suppression dans claude.ai reste une décision de hprzeta.

## Étape 5 — scripts

| Script | Dépôt | Empreinte | Écart |
|---|---|---|---|
| zeta_backup_toshiba.sh | `scripts/` (900 l.) | différente | claude.ai : 271 l. ; dépôt = v2.4 du 10/10 (`b58742f`) |
| backup_cluster_map.sh | `scripts/` (329 l.) | différente | claude.ai : 330 l. ; dépôt à jour au 03/10 (`677064c`) |
| zeta_backup_status.py | `scripts/` (280 l.) | différente (attendu : IP masquées) | 0 IP en clair depuis le 04/10 (`eb46ce4`) |

Les copies claude.ai n'étaient pas dans le zip (empreintes et nombres de lignes seulement) : pas de `diff` ligne à ligne. Les 3 scripts du dépôt sont suivis et sans modification locale.

## Étape 6 — ORGANISATION_FICHIERS.md

Wiki : 169 lignes, MAJ 2026-10-18, empreinte `2d2fa23182bb0fc3` ; copie claude.ai : 150 lignes, MAJ 2026-06-03. Ni IP ni DDNS. Copié dans `A_DEPOSER/`.

## Étape 6b — ETAT

12 copiés (`cp -n`) avec bloc « État en bref » (5 lignes) et pied de page recalculé. Non copiés : `securite` et `skills` (`pdf/securite/` et `pdf/skills/` n'existent pas ; `pdf/secur/` existe) — signalé, rien créé. `pdf/cluster/` et `pdf/script/` sont hors git (`.git/info/exclude`) : leurs ETAT restent locaux. Valeurs « à confirmer » : dernière sauvegarde PC3, date du run T=10⁵, taille du corpus VAULT, contenu pédagogique MATH et HR.

## Étape 6c — MODELE

Annexe « Correspondance projets claude.ai ↔ dossiers locaux » ajoutée (73 → 93 lignes), sections 1 à 7 inchangées, `.bak-20261121` conservé. La ligne « SKILLS ZETA, SECURITE ZETA | skills, securite » reprend le prompt, mais les dossiers réels sont `audits_skills/` et `secur/` (tableau plus haut dans le MODELE) : à arbitrer.

## Reste

- « go commit » puis « go push » de hprzeta (jamais `--force`).
- Dépôt des `.md` de `A_DEPOSER/` dans claude.ai par hprzeta.

<sub>Mis à jour le 2026-11-21 · 72 lignes</sub>
