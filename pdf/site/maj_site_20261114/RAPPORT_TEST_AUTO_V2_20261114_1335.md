# Rapport — Test automatique V2 : contrôles faits par le script (D28)

> 14/11/2026 13:35 · exécution de `PROMPT_TEST_AUTO_V2_20261114_1257.md` (étapes 0 à 4). **Tout est local : 0 commit, 0 push.** Turbo, hooks, `monitoring/Monitoring-Runs.md`, service et minuterie non touchés.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Étape 0 : prompt rangé | 🟢 | Zip extrait sans écrasement dans `src/ia/prompts`, 3 fichiers copiés dans `maj_site_20261114/`. | Rien. |
| Diagnostic du refus de Bash | 🟡 | `--allowedTools` ne contenait que `curl -s:*`, `grep:*`, `wc:*` ; `git` était interdit ; mode `-p` sans accord possible. Les trois `erreurs_*.log` sont vides. La commande exacte refusée n'est dans aucun log : cause **déduite**, non mesurée. | Aucun, Bash est retiré. |
| `zeta_test_controles.sh` + `zeta_controles.py` (liens, lignes, secrets, formules) | 🟢 | `bash -n` et `py_compile` OK. Essais à la main : 94 liens, 10 `.md`, puis 537 liens et 43 `.md`. Sortie sans valeur identifiante (grep IPv4 / `fe80::` : 0). | Liste blanche non testée sur Plotly, DOI et pages de renvoi (aucun cas présent dans les essais). |
| `zeta_test_maj_site.sh` : contrôles avant Claude, sans Bash, `ZETA_FORCE`, copie des contrôles | 🟢 | `bash -n` OK, sauvegarde `.bak-202611141316`. Essai forcé : code 0, rapport de 40 lignes, 0 occurrence de « refusé ». | Rien. |
| Prompt du test : règles 9 et 10 | 🟢 | Sauvegardes `.bak-202611141316` et `.bak-202611141325`, pied de page à 51 lignes, égal à `wc -l`. | La règle 10 n'a pas été éprouvée par un nouvel essai forcé. |
| Essai forcé non partiel | 🟡 | 0 « Bash a été refusé », 4 sections de contrôles présentes, 0 valeur identifiante, `git status` du dépôt et du wiki inchangés, turbo `ACTIF`, `dernier_ts` inchangé. Reste partiel sur un point : l'étape 3 (site en ligne) n'a pas été faite. | Règle 10 ajoutée (WebFetch). À vérifier au prochain essai. |
| Interprétation « fichiers non publiés » | 🟡 | Le rapport de l'essai a pris les fichiers trouvés avec `ZETA_DEPUIS` (avant-hier) pour du travail non commité. Erreur due à l'essai, pas au script. | Règle 10 ajoutée. |
| Faux positif `STACK.md:53` (`](s)` en code en ligne) | 🟢 | Les accents graves sont retirés avant l'extraction. Plus signalé. | Rien. |
| Faux positif `README.md:12` (issues de l'utilisateur, 404 anonyme) | 🟢 | `github.com/issues?…` ajouté à la liste blanche. Essai : 537 liens, 🟢 529 · 🔴 0 · ⚪ 8. | Contrôler le lien dans le Chrome connecté. |
| Heure fausse dans le titre du rapport (13:30 au lieu de 13:21) | 🟡 | Règle 10 : date seulement dans le titre. | À vérifier au prochain essai. |
| Corrections de contenu proposées par l'essai | 🟡 | Une seule : retirer la note de gabarit `[[ ]]` de `Optimisation-Pourquoi-le-calcul-va-vite.md` (l. 185-189). **Non appliquée** (wiki, hors périmètre de ce prompt). | À décider par hprzeta. |
| Relire `PasswordAuthentication yes` (`Architecture-Cluster-Zeta.md:200`), formules `\|…\|` de `Formules_zeta.md` | 🟡 | Relevés par l'essai, non traités ici. | Relecture et rendu avec Chrome. |

## 2. Fichiers créés ou modifiés

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| `~/.local/bin/zeta_test_controles.sh` | nouveau, 14 lignes | — | 14/11/2026 13:15 |
| `~/.local/share/zeta_test_maj/zeta_controles.py` | nouveau, 234 lignes (2 retouches : accents graves, liste blanche issues) | `.bak-202611141325` (version avant retouches) | 14/11/2026 13:28 |
| `~/.local/share/zeta_test_maj/reference_audit_20261112/` | 5 scripts copiés de l'audit du 12/11 | — | 14/11/2026 13:15 |
| `~/.local/bin/zeta_test_maj_site.sh` | 80 lignes | 68 lignes (`.bak-202611141316`) | 14/11/2026 13:17 |
| `src/ia/prompts/PROMPT_TEST_AUTO_MAJ_SITE.md` | 51 lignes (règles 9 et 10) | 49 lignes (`.bak-202611141316`) | 14/11/2026 13:30 |
| `~/.local/state/zeta_test_maj/controles_20261114.md` | généré, copié dans `maj_site_20261114/` | — | 14/11/2026 13:31 |
| `maj_site_20261114/RAPPORT_TEST_AUTO_MAJ_SITE_20261114_1321.md` | rapport de l'essai forcé, 40 lignes | — | 14/11/2026 13:21 |
| `maj_site_20261114/RAPPORT_TEST_AUTO_V2_20261114_1335.md` et `.pdf` | ce rapport | — | 14/11/2026 13:35 |
| `maj_site_20261114/HANDOFF_SITE_20261114.md` | section « Test automatique V2 » ajoutée | 8 lignes | 14/11/2026 13:35 |

---
*RAPPORT_TEST_AUTO_V2_20261114_1335.md · projet SITE ZETA · hprzeta · 14 novembre 2026 13:35 · 37 lignes*
