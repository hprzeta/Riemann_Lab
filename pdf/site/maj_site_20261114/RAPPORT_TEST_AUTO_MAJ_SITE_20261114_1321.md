# Test automatique de mise à jour du site — 14/11/2026 13:30
> Lecture seule, sans Chrome ni Bash. Commits examinés : 0 (dépôt) · 0 (wiki). Les têtes des 4 branches et du wiki sont identiques entre le dernier test et maintenant. Rapport partiel : le site en ligne n'a pas été comparé, voir §3.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Commits depuis le dernier test | 🟢 | Les 5 têtes (`Riemann_Lab_IA`, `main`, `master`, `Riemann_Lab_Test`, `Riemann_Lab_C`) sont identiques aux deux relevés, et les deux `git log` fournis sont vides. | Rien. |
| Fichiers modifiés non publiés | 🟡 | Le script compte 13 fichiers modifiés dans le dépôt et 37 dans le wiki. Aucun commit ne les couvre. Le `git status` initial montre `monitoring/Monitoring-Runs.md` modifié et de nombreux fichiers non suivis (`docs/archive/`, `pdf/archive/`, `pdf/claude/`, `pdf/site/maj_site_20261111/`, `monitoring/runs/prod/20261105_213329_T100000/`). | Rien n'est en ligne tant que ce n'est pas commité. Le commit reste à valider par hprzeta. |
| Valeurs à propager (étape 2) | 🟡 | Aucun commit nouveau, donc aucune valeur nouvelle à chercher par `git log`. Je n'ai pas relu `Handoff.md` ni `JOURNAL.md`. | À refaire au prochain commit de contenu. |
| Lien `README.md:12` (HTTP 404) | 🟡 | La cible est `github.com/issues?q=...assignee:hprzeta`, une page de recherche personnelle qui exige une session connectée. Un `curl` anonyme reçoit probablement 404. Je n'ai pas pu le confirmer. | À vérifier dans un navigateur connecté. Probable faux positif. |
| Lien `Optimisation-Pourquoi-le-calcul-va-vite.md:185` (`[[]]`) | 🔴 | J'ai lu les lignes 185-187. C'est une note de gabarit laissée dans la page : « ⚠️ À vérifier avant le push : les noms entre `[[ ]]` … ». Le `[[ ]]` est écrit hors code, donc le wiki le lit comme un lien vide. | Retirer la note (voir §2). |
| Lien `STACK.md:53` (`s`, fichier absent) | 🟢 | J'ai lu la ligne 53. Le texte « `](` dans une formule (ex. `ℳ[f](s)`) » est entre accents graves. Le script y voit un lien Markdown `(s)`, mais ce n'est pas un lien. | Rien. Faux positif de l'outil. |
| Autres liens (540 testés) | 🟢 | Rapport du script : 530 🟢, 0 🟡, 7 ⚪. | Rien. |
| Pieds de page (nombre de lignes) | 🟢 | Rapport du script : 43 `.md` vérifiés, aucun écart. | Rien. |
| Dates de pied de page | 🟢 | Aucun commit après les dates affichées, donc aucune nouvelle date à proposer (règle 8). | Rien. |
| Secrets `Architecture-Cluster-Zeta.md:565-578` (duckdns, `token=`) | 🟢 | Lignes lues. Le token est le gabarit `<token_duckdns>` et le sous-domaine est « non divulgué ». Il n'y a aucune valeur réelle. | Rien. |
| Secret `Architecture-Cluster-Zeta.md:200` (`passw`) | 🟡 | La ligne est `PasswordAuthentication yes` dans un exemple de `sshd_config`. C'est un paramètre, pas un secret. Je n'ai pas relu le contexte (l. 190-200) pour voir si la page le présente comme réglage provisoire. | À relire. Si c'est la configuration finale de PC4, le doc devrait dire que l'authentification par mot de passe est à désactiver une fois les clés en place. |
| Formules `Formules_zeta.md:707, 748, 1591` (`\|` dans un tableau) | 🟡 | La sortie de `grep` montre que ces lignes sont des formules d'affichage commençant par `\|` (`\|\pi(x) - \text{li}(x)\| = …`), pas des cellules de tableau. Le script les signale quand même. Le rendu n'est pas vérifiable ici. | À regarder avec Chrome. Pour être sûr, remplacer les `\|…\|` par `\lvert…\rvert`, comme le recommande `STACK.md` règle 3. |
| Formules `Tableau-Symboles-Mathematiques.md:100-101`, `analyse_problemes_v13_v15.md:143` | 🟡 | Signalées par le script. Je n'ai pas ouvert ces fichiers. | À relire. S'il s'agit de `\|X\|` dans une cellule de tableau, utiliser `\lvert X\rvert`. |
| Autres cellules de tableau de `Formules_zeta.md` | 🟢 | Toutes les cellules du `grep` qui contiennent une valeur absolue utilisent déjà `\lvert…\rvert` (l. 225, 239, 1151, 1162, 1741). | Rien. |
| Site en ligne vs dépôt (étape 3) | 🟡 | Non fait : je n'ai pas chargé WebFetch dans cette passe. | Voir §3. |

## 2. Corrections proposées

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| `Riemann_Lab.wiki/Optimisation-Pourquoi-le-calcul-va-vite.md` (l. 183-189) | *(note supprimée.)* Garder le séparateur `---` de la ligne 183 et supprimer les lignes 185 à 189. Après suppression, ajuster le nombre de lignes du pied de page. | `> ⚠️ **À vérifier avant le push** : les noms entre `[[ ]]` doivent correspondre **exactement**` / `> aux titres réels de tes pages wiki (sans le `.md`). Corrige ou retire les liens vers des pages` / `> qui n'existent pas encore, sinon ils seront morts.` | À FAIRE |

Aucune autre correction n'est justifiée. Les points 🟡 du §1 demandent un contrôle visuel ou une relecture, pas une modification de texte.

## 3. Non vérifié ici (à faire avec Chrome)
- Comparer le site `https://hprzeta.github.io/Riemann_Lab/` (bandeau, statistiques, frise, pied de page) avec `docs/index.html` de `Riemann_Lab_IA`. Les têtes n'ont pas bougé depuis le dernier test, donc un écart serait antérieur à ce test.
- Ouvrir `https://github.com/issues?q=is%3Aopen+assignee%3Ahprzeta` connecté, pour confirmer que le 404 du README est un faux positif.
- Rendu KaTeX (console, `.katex-error`) de `Formules_zeta.md` aux lignes 707, 748 et 1591, de `Tableau-Symboles-Mathematiques.md` aux lignes 100-101 et d'`analyse_problemes_v13_v15.md` à la ligne 143.
- Contexte de `Architecture-Cluster-Zeta.md:190-200` (`PasswordAuthentication yes`).
- Relecture de `Handoff.md` (« REPRENDRE ICI ») et de `JOURNAL.md`, pour propager d'éventuelles valeurs nouvelles lors du prochain commit.

---
*RAPPORT_TEST_AUTO_MAJ_SITE_20261114_1321.md · test automatique (lecture seule) · 14/11/2026 13:21 · 40 lignes*
