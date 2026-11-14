# Rapport d'analyse — test automatique de mise à jour du site (12/11/2026 00:48)

> Rédigé sur claude.ai (projet SITE ZETA). Aucune modification faite. Prompt associé : `PROMPT_INSTALL_TEST_AUTO_MAJ_SITE_20261112_0048.md`.

## 1. Besoin exprimé par hprzeta
- Lancer seul un « test de mise à jour » quand il allume PC1 pour travailler (fuseau : Paris).
- PC1 est éteint entre deux journées et déplacé ; parfois travail tard la nuit ; parfois allumé tout le week-end pour un long run.

## 2. Options étudiées

| Option | Déclenchement | Verdict |
|---|---|---|
| Tâche programmée claude.ai | heure fixe, dans le cloud | 🔴 écartée : ne voit pas l'allumage de PC1, pas d'accès au dépôt local |
| Démarrage de session seul | au login de PC1 | 🟡 insuffisant : rien pendant un week-end allumé |
| **Minuterie systemd utilisateur sur PC1** | 10 min après l'ouverture de session, puis toutes les 3 h | 🟢 retenue |
| Mise à jour automatique du site | — | 🔴 refusée : contraire aux STOP « go commit » / « go push » |

## 3. Conception retenue (décisions D1 à D5)

| # | Décision | Raison |
|---|---|---|
| D1 | Minuterie systemd `--user` sur PC1 | couvre allumage, travail de nuit et week-end allumé |
| D2 | Au plus **un test par jour**, et **seulement si un commit a été publié** (comparaison des têtes distantes des 4 branches + wiki) | protège le quota ; rien ne tourne pour rien |
| D3 | **Lecture seule** : outils `Read`, `Grep`, `Glob`, `WebFetch`, `curl -s`, `grep`, `wc` ; `git`, `Edit`, `Write`, `rm`, `mv`, `cp` interdits ; le `git log` est fourni par le script | aucun commit ni écriture possible par le modèle |
| D4 | Hors ligne (PC déplacé) : on ne marque rien, nouvel essai au passage suivant | pas de test perdu |
| D5 | Tout reste local (`~/.local/bin`, `~/.config/systemd/user`, `src/ia/prompts`) : **0 commit, 0 push** | rien à publier, retour arrière simple |

Résultat : un `RAPPORT_TEST_AUTO_MAJ_SITE_<date>_<heure>.md` dans `pdf/site/maj_site_<date>/A_DEPOSER/` et une notification de bureau. hprzeta le donne à claude.ai, qui prépare le prompt de correction (avec Chrome et les STOP habituels).

## 4. Limites (à connaître)
- **Pas de Chrome** en mode sans interface : la console et le rendu KaTeX réel ne sont pas vérifiés. Le test fait un contrôle statique des formules ; le contrôle à l'écran reste dans le prompt de correction.
- Le test ne voit pas les `.md` du projet SITE ZETA (claude.ai) : il part du `git log`, de `Handoff.md` et de `JOURNAL.md`.
- Un test consomme du quota Claude Code (au plus une fois par jour).
- Si la session de PC1 n'est pas ouverte (pas de login), la minuterie utilisateur ne tourne pas.

## 5. Non vérifié depuis claude.ai (contrôlé par Claude Code à l'étape 3)
- Chemin exact de `claude` sur PC1 et présence de `--allowedTools` / `--disallowedTools`.
- Disponibilité de `systemctl --user` et de `notify-send`.
- Hook de fin de session existant (montré, non modifié).

## 6. Tableau de modifications (à faire)

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| `~/.local/bin/zeta_test_maj_site.sh` (local) | [nouveau fichier] script du test, lecture seule | — | À FAIRE |
| `~/.config/systemd/user/zeta-test-maj.service` (local) | [nouveau fichier] service `oneshot` | — | À FAIRE |
| `~/.config/systemd/user/zeta-test-maj.timer` (local) | [nouveau fichier] `OnStartupSec=10min`, `OnUnitActiveSec=3h` | — | À FAIRE |
| `src/ia/prompts/PROMPT_TEST_AUTO_MAJ_SITE.md` (local, non suivi) | [nouveau fichier] prompt du test | — | À FAIRE |

---
*RAPPORT_ANALYSE_TEST_AUTO_MAJ_SITE_20261112_0048.md · projet SITE ZETA · hprzeta · MAJ 12 novembre 2026 00:48 · 51 lignes*
