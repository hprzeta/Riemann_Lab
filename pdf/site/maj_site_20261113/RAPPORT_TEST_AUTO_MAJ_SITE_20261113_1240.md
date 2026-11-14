# Test automatique de mise à jour du site — 13/11/2026
> Lecture seule, sans Chrome. Commits examinés : 56 (dépôt, dont environ 40 cherry-picks miroirs) · 5 (wiki).
> **Rapport partiel.** Bash a été refusé pendant ce test. Je n'ai donc pu faire ni `curl`, ni `wc -l`, ni `git log`. J'ai utilisé Grep, Read et WebFetch à la place.

## 1. Tableau de validation
| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Valeurs `10 016 474` et `138 069` dans `docs/index.html` | 🟢 | Grep : lignes 637, 761, 1644, 1733, 1746, 1747, 1761. Elles sont cohérentes entre elles. | — |
| Valeurs dans le README | 🟢 | `README.md:19-20` : 10 016 474 zéros, 138 069 zéros, 1,84 min, 2 min 40 s. | — |
| Valeurs dans `Home.md` | 🟢 | Lignes 9, 23, 76, 136, 137. Les anciennes valeurs de 138 0xx zéros restent présentées comme historique daté (v2, v12). | — |
| Site en ligne et dépôt | 🟢 | WebFetch : bandeau, statistique « 10 016 474 zéros calculés », 138 069 et pied « mis à jour le 12/11/2026 » identiques à `docs/index.html:637` et `:1775`. Le site est à jour. | — |
| Phrase du rescan | 🟡 | La phrase du site en ligne est « rescan décalé STEP/3 (gain mesuré le 07/11 sur un déficit fabriqué, non transposable tel quel à la production) ». Je ne l'ai pas comparée à `docs/V17.md`. | Comparaison à faire. |
| Liens de `docs/index.html` | 🟡 | 74 occurrences d'URL (Grep). Bash étant refusé, je n'ai pas pu faire de `curl` en masse. WebFetch : `wiki/Formation-Zeta-HR-Ch01` répond (« Chapitre 1 — Série de Dirichlet… ») et `https://www.lmfdb.org/zeros/zeta/` répond. Les autres URL ne sont pas testées : Ch02 à Ch14, `blob/main/pdf/optimisation/*.pdf`, ancres du wiki, `raw.githubusercontent.com`, CSV. | Faire un test `curl` complet avec Bash. |
| Ancres du wiki citées par `index.html` | 🟡 | Je n'ai pas vérifié que les ancres (`#15-formules…`, `#cache-log_n…`, etc.) existent encore. Les titres de `Formules_zeta` n'ont pas changé dans les commits examinés. | Vérification à faire. |
| Formules (contrôle statique) | 🟢 | Grep sur les `.md` touchés. `\operatorname` : aucun cas relevé. Les `\,` et `\!` trouvés (Ch03:37, Ch12:9) sont des espacements en bloc `$$` du chapitre. `STACK.md:46-47` et `Phase-C…:30` (`Z\_RS`) sont du texte hors bloc math. J'ai lu 5 fichiers sur 15. | Les 10 autres fichiers (Ch01, Ch02, Ch05 à Ch11, Ch14) contiennent des motifs sans examen ligne à ligne. Rendu KaTeX non vérifiable ici. |
| Secrets (wiki) | 🟡 | Aucune IP, MAC, `fe80::`, `ghp_` ni `PRIVATE KEY` dans les fichiers vérifiés. `Architecture-Cluster-Zeta.md:571-572` : le token est un `<token_duckdns>` et le domaine est « non divulgué » (placeholders). Ligne 200 : `PasswordAuthentication yes` est une option de configuration, pas un secret. Seuls 8 fichiers du wiki ont été scannés. | Dépôt (`docs/`, `README.md`) non scanné. |
| Pied de page README | 🟡 | `README.md:101` annonce « 101 lignes » ; le Read affiche 101 lignes. `wc -l` non exécuté. | — |
| Pieds de page des pages wiki | 🟡 | Les nombres annoncés sont Home 169, Roadmap 207, Animations 217, Architecture 787, Etape-1 532, Projet-Zeta 11. Lignes de pied relevées par Grep aux numéros 169, 207, 217, 787 et 532, donc cohérentes. Le nombre de lignes de Projet-Zeta (11) n'a pas été vérifié avec `wc -l`. | Contrôle `wc -l` à faire sur tous les `.md` modifiés. |
| Pied de page des chapitres Formation-Zeta-HR | 🟡 | Ch01 : « Nombre de lignes du fichier : 142 », cohérent avec le résultat du `git log` (142 lignes ajoutées). `Formation-Zeta-HR.md` : le sommaire dit 32 lignes. | Ch02 à Ch14 non contrôlés. |
| Date de pied de page de `index.html` | 🟢 | `docs/index.html:1775` : « mis à jour le 12/11/2026 ». Les derniers commits du site (`3aa3c23`, `0192cae`) datent du 12/11. | — |

## 2. Corrections proposées
| page | ligne in | ligne out | date heure |
|---|---|---|---|
| — | Aucune correction certaine à proposer. Les valeurs vérifiées sont cohérentes entre le site, le README et `Home.md`. | — | À FAIRE |

## 3. Non vérifié ici (à faire avec Chrome)
- Test des 74 URL de `docs/index.html` avec `curl -L` (seules 2 testées).
- Ancres du wiki et rendu KaTeX (console, `.katex-error`) des 14 pages de chapitre.
- Rendu mobile du bloc de formules (D11) et de la grille à 5 colonnes (D15).
- Scan des secrets sur le dépôt (`docs/`, `README.md`, `pdf/`) et sur les 15 pages `Formation-Zeta-HR*`.
- Nombre de lignes (`wc -l`) de tous les `.md` modifiés.

---
*RAPPORT_TEST_AUTO_MAJ_SITE_20261113_1240.md · test automatique (lecture seule) · 13/11/2026 12:40 · 35 lignes*
