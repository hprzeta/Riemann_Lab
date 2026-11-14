# Test automatique de mise à jour du site — 12/11/2026
> Lecture seule, sans Chrome. Commits examinés : ~130 lignes de log, dont 4 branches miroirs (dépôt, via cherry-pick) · 12 (wiki). Rapport partiel : les contrôles sont faits sur les fichiers clés, pas sur tous les `.md` modifiés.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Changements examinés | 🟢 | Journal fourni. Le 11/11 touche `docs/index.html` (stats, tuile V17, 12 animations, RAG), README, wiki (Handoff, STACK, Animations…), les PDF d'analyse et deux scripts de build PDF. | — |
| Valeur « 10 016 474 zéros » (10 016 377 + 97) | 🟢 | `grep` : `docs/index.html:1755` ; stats du haut (site en ligne) ; `Home.md` pied de page. Aucune occurrence de « 10 016 378 », « 96 manquants » ni « 96 zéros manquants » dans `index.html`, README, `docs/*.md`, les `.md` du wiki ni `CLAUDE.md`. | La recherche a été interrompue (limite de temps) : couverture incomplète, notée 🟡 dans la section 3. |
| Site en ligne comparé au dépôt | 🟢 | WebFetch : stats du haut (10 016 474 zéros, t max 5 000 000), tuile V17 « 1,84m », titre Performances, « 12 animations interactives », pied de page « mis à jour le 11/11/2026 ». Tout correspond à `docs/index.html` de `Riemann_Lab_IA`. | — |
| Bandeau du haut (`docs/index.html:631`) | 🟡 | Il affiche « 138 069 zéros validés · V17 en production (03/11/2026) », alors que les stats juste dessous annoncent 10 016 474 zéros. 138 069 est le total à T=100 000 (lignes 1638, 1727, 1740), donc cohérent mais ambigu. | Voir la correction n°1. |
| Liens de `docs/index.html` | 🟢 | `curl -L` : 200 sur dépôt, wiki, issues, `tree/main/src`, LMFDB, `Formation-Zeta-HR`, `Bibliotheques`, `Formules_zeta`, `niveau-4-zeta`, `Cours_Zeta_HR_complet.pdf`, le CSV T=10000 et les PDF `analyse_problemes_v16_v17`, `v1_v16`, `v13_v15`. | Non testés individuellement : les autres PDF d'analyse (v2_v3 à v10_v12), les pages `niveau-0/1/2/3/5`, `Methode`, les polices Google et KaTeX CDN. |
| Ancres de page (`#…`) | 🟡 | `curl` ne voit pas les fragments, donc l'ancre `Bibliotheques#17bis` corrigée le 11/11 n'est pas vérifiée. | À faire avec Chrome. |
| Formules (contrôle statique) | 🟢 | Wiki : `\_ \# \, \; \! \%` trouvés seulement dans du texte ou des notes (`analyse_math_deficit…:5` et `:428`, `STACK.md:46-47`, `Analyse-Deficit…:197`). Les lignes 1762 de `Formules_zeta.md` et 693 de `STACK.md` sont tronquées par l'outil et n'ont pas été relues. Aucun `\operatorname` repéré. | Voir la section 3 pour le rendu. |
| Secrets, IP, MAC, e-mails | 🟢 | Sur `index.html`, README, `CLAUDE.md`, `V17.md` et 12 `.md` du wiki, la seule occurrence est la règle d'audit `CLAUDE.md:204`, qui ne contient aucune valeur. Aucune IPv4, `fe80::<hex>` ni MAC. | Couverture limitée aux fichiers listés ; les PDF et captures ne sont pas relus. |
| Pieds de page : `wc -l` identique | 🟢 | `STACK` 706, `Handoff` 935, `Animations` 217, `Arbre` 168, `analyse_math_deficit` 428, `knowledge_base_obj2` 384, `Home` 169, `Roadmap` 207, `CLAUDE.md` 327. Chaque chiffre est égal au `wc -l`. | — |
| Pied de page de `docs/V17.md` | 🟡 | Date « 2026-11-05 », 66 lignes (égal à `wc -l`), alors que le fichier a été modifié le 07/11 (commits 672656b, 173327d). | Voir la correction n°2. |
| Pied de page de `Handoff.md` | 🟡 | Il contient plusieurs dates empilées : le texte commence par « 16 août 2026 » et la date « Mis à jour le 2026-11-11 — 935 lignes » est au milieu de la ligne. Les chiffres sont justes mais la lecture est confuse. | Facultatif. |
| `README.md` | 🟡 | Dernière ligne : « Libre d'utilisation… », sans date de mise à jour ni nombre de lignes (98 lignes), alors que le README a été modifié le 11/11. | Voir la correction n°3. |

## 2. Corrections proposées

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| `docs/index.html:631` | `10 016 474 zéros calculés (T=5·10⁶) · 138 069 zéros à T=100 000 · V17 en production (03/11/2026) · 0 manquant ✅ · Obj2 atteint 04/07/2026` | `138 069 zéros validés · V17 en production (03/11/2026) · 0 manquant ✅ · Obj2 atteint 04/07/2026` | À FAIRE |
| `docs/V17.md` (pied de page) | `*Mis à jour : 2026-11-07 — 66 lignes*` (si les commits du 07/11 ont changé le contenu, la date est à confirmer) | `*Mis à jour : 2026-11-05 — 66 lignes*` | À FAIRE |
| `README.md` (dernière ligne) | Ajouter `· Mis à jour le 2026-11-11 — <n> lignes` après la ligne de licence, avec `<n>` égal à `wc -l` après la modification | `Projet de recherche personnel - hprzeta - Libre d'utilisation et de modification.` | À FAIRE |

## 3. Non vérifié ici (à faire avec Chrome)
- Rendu réel des formules KaTeX (console, `.katex-error`) sur le site et dans les pages wiki modifiées le 11/11.
- Ancres `#…` des liens du site (notamment `Bibliotheques#17bis…`, `Formules_zeta#…`) et défilement vers la bonne section.
- Les 12 animations : chargement dans les iframes et affichage de la tuile V17.
- Liens non testés individuellement (voir la ligne « Liens » du tableau).
- Occurrences de l'ancienne valeur « 96 » : la recherche a été interrompue, donc les PDF et les `.md` hors fichiers clés ne sont pas couverts. Une relance ciblée sur `pdf/` et `docs/archive/` (en excluant les archives datées, qui sont de l'historique) est utile.
- Les ~40 fichiers non suivis (`pdf/site/maj_site_20261111/`, `docs/archive/`, `monitoring/runs/…`) n'ont pas été examinés pour les secrets.
- Seule la branche `Riemann_Lab_IA` a été comparée au site en ligne, pas `main`.
- Première exécution : aucune tête de branche n'est disponible pour comparaison au test précédent.

---
*RAPPORT_TEST_AUTO_MAJ_SITE_20261112_0101.md · test automatique (lecture seule) · 12/11/2026 01:03 · 40 lignes*
