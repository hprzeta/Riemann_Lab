---
title: "Rapport — installation du test automatique de mise à jour du site"
date: "12/11/2026 01:08"
---

# Rapport — installation du test automatique (PC1)

Prompt exécuté : `PROMPT_INSTALL_TEST_AUTO_MAJ_SITE_20261112_0048.md`. Installation locale uniquement : **0 commit, 0 push**. Le dépôt suivi, le wiki et le site n'ont pas été modifiés.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Étape 0 : dézipper | 🟢 | `unzip -n` : 4 fichiers rangés dans `src/ia/prompts`, aucun écrasement | — |
| Étape 3 : diagnostic | 🟢 | `claude` 2.1.322, options `--allowedTools`/`--disallowedTools`/`-p` présentes, `systemctl --user` = `running`, outils présents | — |
| Script, service, minuterie | 🟢 | `bash -n` OK ; `systemd-analyze --user verify` OK | — |
| 1er essai à la main | 🔴 → corrigé | Rapport vide : le hook `Stop` local a pollué la réponse et le hook `SessionStart` a relancé le turbo via `sudo` | Voir correctif ci-dessous |
| Correctif | 🟢 | `--setting-sources user` + garde-fou (rapport < 400 octets ou contenant « Prêts à déposer… » = échec). 2e essai : rapport de 40 lignes, plus d'appel `sudo` dans le journal, turbo inchangé (ACTIF) | — |
| Garde « une fois par jour » | 🟢 | 2e lancement et passage d'activation : « déjà testé aujourd'hui » | — |
| Lecture seule | 🟢 | `git status` : wiki vide ; dépôt sans changement dû au test (restent `resultats_rescan_phase/` et `resultats_v17/`, déjà présents avant, non comparés à l'état d'avant) | — |
| Aucune valeur identifiante | 🟢 | `grep` IPv4 / `@` / `fe80::` sur le rapport de test : aucune occurrence | — |
| Activation | 🟢 | `enable --now` ; `is-enabled` = enabled, `is-active` = active ; prochain passage dans 2 h 59 | — |
| Qualité du rapport de test | 🟡 | Correction n°1 contradictoire, correction n°2 à contre-sens (date de `V17.md` remise à l'ancienne), recherche des « 96 » interrompue | À relire avant d'agir sur ces corrections |
| Linger | 🟡 | `Linger=no` : la minuterie ne tourne que pendant la session de l'utilisateur (voulu) | Aucun, information seulement |

## 2. Problème rencontré et correctif

Le test lance `claude -p` depuis `~/projet_zeta`, donc les hooks de `.claude/settings.local.json` s'appliquent. Le hook `Stop` a remplacé le rapport par sa propre consigne, et le hook `SessionStart` a rappelé `zeta_turbo_on.sh`. Le correctif est `--setting-sources user` dans la commande, plus un contrôle de validité du rapport avant de marquer le test comme réussi. L'option `--setting-sources user` a aussi pour effet de ne charger que les réglages utilisateur : ce comportement est constaté (plus de `sudo` au journal), pas documenté dans ce rapport.

## 3. Fichiers créés

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| `~/.local/bin/zeta_test_maj_site.sh` | — | 68 lignes (63 à l'origine, 1 ligne modifiée pour l'option, +5 garde-fou) | 12/11/2026 01:01 |
| `~/.local/bin/zeta_test_maj_site.sh.bak-20261112` | — | copie avant correctif | 12/11/2026 00:58 |
| `~/.config/systemd/user/zeta-test-maj.service` | — | 8 lignes | 12/11/2026 00:58 |
| `~/.config/systemd/user/zeta-test-maj.timer` | — | 9 lignes | 12/11/2026 00:58 |
| `src/ia/prompts/PROMPT_TEST_AUTO_MAJ_SITE.md` et 3 autres | — | extraits du zip | 12/11/2026 00:57 |
| `pdf/site/maj_site_20261112/RAPPORT_TEST_AUTO_MAJ_SITE_20261112_0101.md` | — | 40 lignes, 1er vrai rapport de test | 12/11/2026 01:03 |
| `pdf/archive/test_auto_20261112_essai1/` | — | faux rapport et état de l'essai 1 (archivés, rien supprimé) | 12/11/2026 01:01 |

## 4. Retour en arrière

`systemctl --user disable --now zeta-test-maj.timer`, puis déplacer le timer, le service et le script dans `pdf/archive/`, puis `systemctl --user daemon-reload`. On archive, on ne supprime pas.

## 5. Points ouverts

- Relire les 3 corrections proposées par le rapport de test (`docs/index.html:631`, `docs/V17.md`, `README.md`) avant toute action.
- Le prochain test réel est possible dès demain (limite d'un test par jour, et seulement si un commit a été publié).
- Suivre si `OnUnitActiveSec=3h` repart correctement après un changement de jour (observé seulement sur une journée).

---
*RAPPORT_MAJ_TEST_AUTO_20261112_0108.md · 12/11/2026 01:08 · 53 lignes*
