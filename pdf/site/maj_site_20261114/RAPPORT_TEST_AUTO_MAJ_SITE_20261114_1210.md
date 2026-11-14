# Test automatique de mise à jour du site — 14/11/2026
> Lecture seule, sans Chrome. Commits examinés : 0 (dépôt) · 2 (wiki).
> Rapport partiel : plusieurs commandes Bash ont été refusées (`git log`, boucle `curl`). Les vérifications ont donc été faites avec Grep, Read et WebFetch.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Têtes publiées (dépôt) | 🟢 | `Riemann_Lab_IA`, `main`, `Riemann_Lab_C` et `Riemann_Lab_Test` sont identiques au dernier test (fourni en entrée). Le `git log` du dépôt est vide. | — |
| Têtes publiées (wiki `master`) | 🟢 | `0d94a0d` → `c81894c`, soit 2 commits : `382c030` (20 formules en syntaxe `` $`…`$ ``, Ch01-Ch13) et `c81894c` (titre du chapitre 5 sans formule dans le lien de l'index). | — |
| Propagation des valeurs | 🟢 | Le dépôt n'a pas bougé et le wiki ne touche que le cours. Dans `docs/index.html`, 10 016 474 zéros (T=5·10⁶), 138 069 zéros (T=10⁵), V17 du 03/11/2026, 1,84 min (PC1+PC2) et 2 min 40 s (PC1 seul) sont cohérents (lignes 637, 783-787, 1207). Grep ciblé, pas exhaustif sur tout le wiki. | — |
| Site en ligne vs dépôt | 🟢 | WebFetch de `hprzeta.github.io/Riemann_Lab/` : bandeau « 10 016 474 zéros (T=5·10⁶) · 138 069 à T=10⁵ · V17 (03/11/2026) · 0 manquant », « 12 animations en ligne » et V17 « 1,84m » dans la frise. Tout correspond à `docs/index.html`. Le pied de page affiche « mis à jour le 12/11/2026 ». | — |
| Liens de `docs/index.html` | 🟡 | J'ai extrait les URL par Grep (wiki, `raw.githubusercontent`, `blob/main/pdf/optimisation/*.pdf`, `docs/V17.md`, LMFDB, CDN KaTeX). Le test `curl` a été refusé, donc aucun code HTTP n'est vérifié. Seul `wiki/Formation-Zeta-HR-Ch02` a répondu à WebFetch. | Retester les liens avec `curl` en dehors du mode lecture seule. |
| Formules : syntaxe | 🟡 | Les blocs `$$…$$` contiennent `\,` et `\!` (par ex. Ch02:28, Ch05:9, Ch12:9, Ch11:9). Ils sont valides en KaTeX, mais ce sont les motifs à risque de la liste. Dans les cellules de tableau, `|` ne s'est trouvé que dans des `\|`-libres : aucun `|` brut dans une cellule math (Ch04, Ch06, Ch09, Ch10, Ch12 et Ch14 relus par motif). | Voir §2 pour les formules inline qui n'ont pas la syntaxe `` $`…`$ ``. |
| Formules : rendu réel | 🟡 | WebFetch sur Ch02 a renvoyé du texte de source (`\,dx` devenu `,dx`, `O!\left(` avec un `!` parasite). Un outil de conversion en markdown ne reproduit pas le rendu GitHub, et la page peut dater d'avant le commit `382c030` à cause du cache de 15 min. Conclusion non fiable. | À vérifier avec Chrome. |
| Secrets | 🟢 | Grep sur les 15 fichiers `Formation-Zeta-HR*.md` du wiki (`duckdns`, `PRIVATE KEY`, `ghp_`, `github_pat`, `token=`, `passw`, IPv4, `fe80::`, MAC, e-mails) : aucune occurrence. Le dépôt n'a pas de commit nouveau. | — |
| Pieds de page : nombre de lignes | 🟢 | Les 10 fichiers modifiés ont un nombre affiché égal à `wc -l` : index 32, Ch01 142, Ch02 112, Ch03 90, Ch05 85, Ch07 81, Ch08 77, Ch11 75, Ch12 79, Ch13 77. | — |
| Pieds de page : dates | 🟡 | `Formation-Zeta-HR.md` affiche « Mis à jour le 14 novembre 2026 », alors que ses commits datent du 13/11 (23:46 et 23:51). La date est postérieure aux commits, donc aucune correction n'est proposée (règle 8). Je n'ai pas relu la date des 9 autres fichiers. | Contrôler la date des chapitres Ch01 à Ch13 modifiés. |

## 2. Corrections proposées

Aucune correction ferme n'est justifiée par les preuves recueillies. Les formules inline suivantes n'ont pas la syntaxe `` $`…`$ `` et contiennent `\,` ou `\!`. Le commit `382c030` a corrigé le même motif ailleurs, donc elles sont des candidates. Rien n'est vérifié sans rendu réel.

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| Formation-Zeta-HR-Ch02.md:66 (candidate) | ``$`\int_0^\infty x^{s-1}e^{-nx}\,dx=\Gamma(s)/n^s`$`` | `$\int_0^\infty x^{s-1}e^{-nx}\,dx=\Gamma(s)/n^s$` | À FAIRE |
| Formation-Zeta-HR-Ch14.md:42 (candidate, cellule de tableau) | ``$`100\,000`$`` | `$100\,000$` | À FAIRE |
| Formation-Zeta-HR-Ch06.md:51 et :54 (candidates, `\,i`) | ``$`1{,}0 + 9{,}064720\,i`$`` | `$1{,}0 + 9{,}064720\,i$` | À FAIRE |

Les Ch06, Ch09, Ch10 et Ch14 contiennent d'autres formules inline du même type. Elles n'ont pas été touchées par `382c030`.

## 3. Non vérifié ici (à faire avec Chrome)
- Rendu réel des formules corrigées par `382c030` (Ch01, 02, 03, 05, 07, 08, 11, 12, 13 et index). Il faut contrôler l'absence de `.katex-error` et de LaTeX brut sur GitHub.
- Rendu des formules inline restantes (Ch02, Ch06, Ch09, Ch10, Ch14).
- Lien du chapitre 5 dans l'index (`c81894c`), pour vérifier que le titre sans formule s'affiche bien dans le sommaire GitHub.
- Codes HTTP de toutes les URL de `docs/index.html`, en particulier les PDF `blob/main/pdf/optimisation/*.pdf` et `docs/V17.md`.
- Dates de pied de page des chapitres modifiés, autres que l'index.
- Historique git et `git log --stat` complets. Les commandes `git` ont été refusées, donc le détail des commits vient uniquement de l'entrée fournie.

---
*RAPPORT_TEST_AUTO_MAJ_SITE_20261114_1210.md · test automatique (lecture seule) · 14/11/2026 12:11 · 41 lignes*
