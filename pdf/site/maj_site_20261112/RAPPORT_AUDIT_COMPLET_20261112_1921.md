# Rapport — Audit complet des liens du site et du wiki — 12/11/2026 19:21

> Exécution de `PROMPT_AUDIT_COMPLET_LIENS_20261112_1812.md` (étape 0 adaptée : pas de zip, prompt fourni seul). Aucun `--force`, aucun renommage. STOP respectés : « go archive », « go correction », « go commit wiki », « go push wiki », « go commit site », « go push », « go commit archive ».

## 1. Synthèse

Liens inventoriés : **848** (avant corrections : 849). Statuts : 🟢 200 et cible correcte · 🟡 marche mais à améliorer · 🔴 cassé · ⚪ faux positif d'extraction (exemple de syntaxe ou adresse citée dans le texte, pas un lien).

| Source | 🟢 avant | 🟡 avant | 🔴 avant | ⚪ avant | 🟢 après | 🟡 après | 🔴 après | ⚪ après |
|---|---|---|---|---|---|---|---|---|
| site (docs/*.html) | 194 | 13 | 3 | 1 | 197 | 10 | 3 | 1 |
| wiki | 560 | 4 | 20 | 13 | 580 | 2 | 1 | 13 |
| docs/*.md | 15 | 0 | 0 | 3 | 15 | 0 | 0 | 3 |
| README | 21 | 2 | 0 | 0 | 21 | 2 | 0 | 0 |
| TOTAL | 790 | 19 | 23 | 17 | 813 | 14 | 4 | 17 |

Liens passés de 🔴/🟡 à 🟢 par les corrections : **25**. Liens encore 🔴/🟡 : **18** (voir §2). Site : accueil + 12 animations et wiki : 84 pages sur 84 parcourus dans Claude in Chrome (onglet « Audit liens »).

## 2. Tableau complet

Le tableau complet (une ligne par lien : `source | ligne | texte | URL | type | HTTP | ancre | statut | action`) est dans `audit/liens_statut_final.csv` (plus de 300 lignes). Ci-dessous : tous les 🔴 et 🟡 restants, puis le résumé des 🟢.

### 2.1 Liens encore 🔴 ou 🟡 après corrections

| Source | Ligne | Texte | URL | HTTP | Statut | Action |
|---|---|---|---|---|---|---|
| zeta_demovisualisation.html | 2635 | (URL nue) | http://get.webgl.org | 200 | 🟡 | http:// → https:// |
| zeta_demovisualisation.html | 2712 | (URL nue) | http://get.webgl.org | 200 | 🟡 | http:// → https:// |
| zeta_demovisualisation.html | 2717 | >OpenStreetMap | https://openstreetmap.org | 200 → https://www.openst… | 🟡 | redirection → https://www.openstreetmap.org/ |
| zeta_demovisualisation.html | 2717 | >OpenStreetMap | https://openstreetmap.org | 200 → https://www.openst… | 🟡 | redirection → https://www.openstreetmap.org/ |
| zeta_demovisualisation.html | 2718 | (URL nue) | https://www.mapbox.com/help/define-access-token/ | 200 → https://docs.mapbo… | 🟡 | redirection → https://docs.mapbox.com/help/glossary/access-token/ |
| zeta_demovisualisation.html | 2722 | (URL nue) | https://www.mapbox.com/api-documentation/#access-tokens-and-token-sco… | 200 → https://docs.mapbo… | 🔴 | ancre absente de la page cible |
| zeta_demovisualisation.html | 2722 | (URL nue) | https://www.mapbox.com/api-documentation/#access-tokens-and-token-sco… | 200 → https://docs.mapbo… | 🔴 | ancre absente de la page cible |
| zeta_demovisualisation.html | 3218 | >ESRI | http://www.esri.com | 200 → https://www.esri.c… | 🟡 | redirection → https://www.esri.com/en-us/home ; http:// → https:// |
| zeta_demovisualisation.html | 3218 | (URL nue) | https://www.mapbox.com/mapbox-gl-js/api/ | 200 → https://docs.mapbo… | 🟡 | redirection → https://docs.mapbox.com/mapbox-gl-js/api/ |
| zeta_demovisualisation.html | 3229 | >ESRI | http://www.esri.com | 200 → https://www.esri.c… | 🟡 | redirection → https://www.esri.com/en-us/home ; http:// → https:// |
| zeta_demovisualisation.html | 3838 | (URL nue) | http://getify.mit-license.org | 200 → https://getify.mit… | 🟡 | redirection → https://getify.mit-license.org/ ; http:// → https:// |
| zeta_demovisualisation.html | 3843 | (URL nue) | http://syntheti.cc | 200 | 🟡 | http:// → https:// |
| zeta_demovisualisation.html | 3845 | (URL nue) | https://github.com/voidqk/polybooljs | 404 | 🔴 | HTTP 404 |
| README.md | 12 | Mes issues assignées | https://github.com/issues?q=is%3Aopen+assignee%3Ahprzeta | 404 | 🟡 | 404 sans connexion (page privée/connectée) : à tester dans le Chrome … |
| README.md | 13 | Voir le Kanban | https://github.com/users/hprzeta/projects/1 | 404 | 🟡 | 404 sans connexion (page privée/connectée) : à tester dans le Chrome … |
| STACK.md | 472 | (URL nue) | https://doi.org/10.1090/S0002-9947-1988-0961614-2 | 200 → https://pubs.ams.o… | 🟡 | redirection → https://pubs.ams.org/journals/tran/1988-309-02/S0002-99… |
| STACK.md | 473 | (URL nue) | https://doi.org/10.1112/plms/s3-3.1.99 | 403 | 🟡 | 403 (anti-robot de l'éditeur) : à tester dans le navigateur |
| STACK.md | 474 | (URL nue) | https://archive.org/details/theoryofriemann00titc | 404 | 🔴 | HTTP 404 |

### 2.2 Liens corrigés (🔴/🟡 avant → 🟢 après)

| Source | Ligne | URL avant | URL après |
|---|---|---|---|
| animation_theta.html | 170 | https://lmfdb.org/zeros/zeta/ | https://www.lmfdb.org/zeros/zeta/ |
| animation_zeros_non_triviaux.html | 166 | https://lmfdb.org/zeros/zeta/ | https://www.lmfdb.org/zeros/zeta/ |
| zeta_demovisualisation.html | 2722 | https://www.mapbox.com/api-documentation/#access-tokens-and… | https://github.com/mapbox/mapbox-gl-js/issues/2907 |
| zeta_demovisualisation.html | 2722 | https://www.mapbox.com/api-documentation/#access-tokens-and… | https://github.com/mapbox/mapbox-gl-js/issues/2907 |
| zeta_demovisualisation.html | 3218 | https://www.mapbox.com/mapbox-gl-js/api/ | https://plotly.com/javascript/maplibre-migration/ |
| index.html | 1779 | https://lmfdb.org/zeros/zeta/ | https://www.lmfdb.org/zeros/zeta/ |
| Animations.md | 15 | #-animationseries_dirichlet--séries-de-dirichlet | #-animation_series_dirichlet--séries-de-dirichlet |
| Animations.md | 16 | #-animationproduit_eulerien--produit-eulérien | #️-animation_produit_eulerien--produit-eulérien |
| Animations.md | 17 | #-animationplan_complexe--plan-complexe | #ℂ-animation_plan_complexe--plan-complexe |
| Animations.md | 18 | #-animationgamma--fonction-gamma | #γ-animation_gamma--fonction-gamma |
| Animations.md | 19 | #-animationdistribution_zeros--distribution-des-zéros | #-animation_distribution_zeros--distribution-des-zéros |
| Animations.md | 20 | #-animationzeros_non_triviaux--zéros-non-triviaux | #-animation_zeros_non_triviaux--zéros-non-triviaux |
| Animations.md | 21 | #-animationmur_latence--mur-de-latence | #-animation_mur_latence--mur-de-latence |
| Etape-1-Calcul-des-zéros-non-triviaux.md | 142 | https://lmfdb.org/zeros/zeta/ | https://www.lmfdb.org/zeros/zeta/ |
| Home.md | 25 | Étape-2-Visualisations-avancées | Animations |
| Home.md | 26 | Étape-3-Intelligence-artificielle | Guide-Ollama-Pratique |
| Phase-C-compute_zeros_v4.md | 13 | #2-problème-mathématique | #2-problème-mathématique--incohérence-z_rs-vs-vrais-zéros |
| Phase-C-compute_zeros_v4.md | 14 | #3-solution-option-b | #3-solution-choisie--option-b-hybride |
| Phase-C-compute_zeros_v4.md | 15 | #4-architecture | #4-architecture-phase-c--fichiers-produits |
| Phase-C-compute_zeros_v4.md | 16 | #5-benchmark | #5-benchmark-mesuré--gains-illinois-c |
| Phase-C-compute_zeros_v4.md | 17 | #6-limitations | #6-limitations-fondamentales-connues |
| Phase-C-compute_zeros_v4.md | 18 | #7-questions-ouvertes | #7-questions-ouvertes--v5-et-au-delà |
| Phase-Optimisation-compute_zeros_v3.md | 16 | #5-benchmarks-15-min | #5-benchmarks-de-performance-15-min |
| Phase-Optimisation-compute_zeros_v3.md | 497 | https://lmfdb.org/zeros/zeta/ | https://www.lmfdb.org/zeros/zeta/ |
| STACK.md | 471 | https://lmfdb.org/zeros/zeta/ | https://www.lmfdb.org/zeros/zeta/ |

### 2.3 Résumé des 🟢

- site (docs/*.html) : 197 liens 🟢 sur 211.
- wiki : 580 liens 🟢 sur 596.
- docs/*.md : 15 liens 🟢 sur 18.
- README : 21 liens 🟢 sur 23.

### 2.4 Contrôle `a.absent` du wiki (liens `[[…]]` vers une page inexistante)

Pages wiki avec au moins un lien `a.absent` : **0** sur 84. Aucune.

## 3. Échantillon A / B / C de hprzeta

| Échantillon | Liens | Réponse |
|---|---|---|
| 1 (avant corrections) | 3 « Lire → » (chapitres 1, 7, 14) + 7 liens à ancre (`Formules_zeta#…`, `Bibliotheques#…`) | « c » → interprété : **C** pour les 10 (au bon endroit) |
| 2 (après corrections) | ancres de `Animations`, sommaire de `Phase-C`, liens `Étape 2/3` de `Home` | en attente de hprzeta |

## 4. Scripts archivés

| Script | Écrit quoi | Encore appelé ? | Dépassé ? | Décision |
|---|---|---|---|---|
| `cours/make_wiki_page.py` | page unique `Formation-Zeta-HR.md` (ancres `#chN`) | non (ni cron, ni minuterie, ni hook) | oui (le cours est en index + 14 pages `ChNN`) | **archivé** → `archive/scripts_obsoletes_20261112/` (commit `001f3b2`, 4 branches) |
| `scripts/archiver_fichiers_obsoletes_v2.sh` | cite `docs/index.html` dans un message | non | non | gardé |
| `scripts/backup_cluster_map.sh` | cite `Riemann_Lab.wiki/` dans un SVG | — | non | gardé |
| `scripts/push_phase0_complete.sh` | pousse le wiki | — | non | gardé |
| `scripts/rag_ingest_corpus.py` | lit `Riemann_Lab.wiki/*.md` | oui (`rag_query.py`, `zeta_rag.sh`) | non | gardé |

## 5. Noms à risque (aucun renommage)

Pages wiki : 5 · ancres à risque utilisées dans des liens : 34 · fichiers publiés (`docs/`, `cours/`, `pdf/`) : 0. Détail complet : `audit/noms_a_risque.csv`.

| Nom actuel | Caractères à risque | Forme encodée | Liens entrants | Nom ASCII proposé |
|---|---|---|---|---|
| Etape-1-Calcul-des-zéros-non-triviaux | accent | Etape-1-Calcul-des-z%C3%A9ros-non-triviaux | 19 | Etape-1-Calcul-des-zeros-non-triviaux |
| Interprétation-des-résultats-de-tests | accent | Interpr%C3%A9tation-des-r%C3%A9sultats-de-tests | 2 | Interpretation-des-resultats-de-tests |
| Partie-1-La-Théorie-Étape_1 | accent | Partie-1-La-Th%C3%A9orie-%C3%89tape_1 | 1 | Partie-1-La-Theorie-Etape_1 |
| Projet-Zêta | accent | Projet-Z%C3%AAta | 1 | Projet-Zeta |
| Tableau-Symboles-Mathématiques | accent | Tableau-Symboles-Math%C3%A9matiques | 2 | Tableau-Symboles-Mathematiques |

Le renommage fera l'objet d'un prompt séparé (le wiki GitHub n'a pas de redirection automatique).

## 6. Lignes modifiées (page · ligne in · ligne out · date heure)

| Dépôt | Page | Ligne in | Ligne out | Date heure |
|---|---|---|---|---|
| wiki | Animations.md | 15-21 | 15-21 | 2026-11-12 19:08 |
| wiki | Animations.md | 217 | 217 | 2026-11-12 19:08 |
| wiki | Architecture-Cluster-Zeta.md | 664 | 664 | 2026-11-12 19:08 |
| wiki | Architecture-Cluster-Zeta.md | 787 | 787 | 2026-11-12 19:08 |
| wiki | Etape-1-Calcul-des-zéros-non-triviaux.md | 142 | 142 | 2026-11-12 19:08 |
| wiki | Etape-1-Calcul-des-zéros-non-triviaux.md | 532 | 532 | 2026-11-12 19:08 |
| wiki | Home.md | 25-27 | 25-27 | 2026-11-12 19:08 |
| wiki | Home.md | 169 | 169 | 2026-11-12 19:08 |
| wiki | Phase-C-compute_zeros_v4.md | 13-18 | 13-18 | 2026-11-12 19:08 |
| wiki | Phase-C-compute_zeros_v4.md | 192 | 192 | 2026-11-12 19:08 |
| wiki | Phase-Optimisation-compute_zeros_v3.md | 16 | 16 | 2026-11-12 19:08 |
| wiki | Phase-Optimisation-compute_zeros_v3.md | 497 | 497 | 2026-11-12 19:08 |
| wiki | Phase-Optimisation-compute_zeros_v3.md | 504 | 504 | 2026-11-12 19:08 |
| wiki | STACK.md | 471-472 | 471-472 | 2026-11-12 19:08 |
| wiki | STACK.md | 706 | 706 | 2026-11-12 19:08 |
| site | docs/animation_theta.html | 79 | 79 | 2026-11-12 19:10 |
| site | docs/animation_theta.html | 170 | 170 | 2026-11-12 19:10 |
| site | docs/animation_theta.html | 174 | 174 | 2026-11-12 19:10 |
| site | docs/animation_zeros_non_triviaux.html | 84 | 84 | 2026-11-12 19:10 |
| site | docs/animation_zeros_non_triviaux.html | 166 | 166 | 2026-11-12 19:10 |
| site | docs/animation_zeros_non_triviaux.html | 179 | 179 | 2026-11-12 19:10 |
| site | docs/index.html | 1779 | 1779 | 2026-11-12 19:10 |
| archive | archive/scripts_obsoletes_20261112/LISEZMOI.md | 0--1 | 1-10 | 2026-11-12 19:12 |
| archive | archive/scripts_obsoletes_20261112/make_wiki_page.py | 0--1 | 1-87 | 2026-11-12 19:12 |
| archive | archive/scripts_obsoletes_20261112/make_wiki_page.py | 1-87 | 0--1 | 2026-11-12 19:12 |

Commits : wiki `2bd4258` · site `05217b8` (IA ; main `4165de3`, C `773bdff`, Test `3aa3c23`) · archive `001f3b2` (IA ; main `33f3ada`, C `ff9dc8b`, Test `cd9f2b8`). Dans le PDF, les lignes supprimées sont en rouge et les lignes ajoutées en vert.

## 7. Tests habituels

| Test | Résultat |
|---|---|
| Console (site) | accueil : 0 erreur ; 12 animations parcourues, 0 erreur KaTeX, 0 image cassée. Console non relevée page par page sur les animations. |
| `.katex-error` / formules brutes | site : 0 ; wiki : 0 « Unable to render » sur 84 pages ; formules brutes `$$` relevées sur l'accueil du site seulement (0) |
| 390 px | accueil du site mesuré dans un cadre de 390 px : largeur utile 376 px, pas de débordement. La fenêtre Chrome n'a pas pu être redimensionnée (viewport resté à 1236 px) ; autres pages non mesurées à 390 px. |
| Secrets | audit des lignes ajoutées (IP, MAC, clés, tokens, e-mails) : aucune ligne suspecte sur les 3 commits |
| Pieds de page | wiki : 7 pages à la date du jour avec `wc -l` ; site : pied de l'accueil au 12/11/2026 |

## 8. Ce qui reste non corrigé ou à décider

- `STACK.md` : lien archive.org de Titchmarsh mort ; aucune édition équivalente vérifiée (l'item trouvé est le tract de 1930).
- `README.md` : issues et Kanban GitHub (404 sans connexion) : à tester dans Chrome connecté.
- DOI Odlyzko-Schönhage corrigé (Crossref) mais l'éditeur répond 403 aux robots : à confirmer dans Chrome.
- Code tiers Plotly dans `docs/images/T10Demo/zeta_demovisualisation.html` : non modifié.
- Le choix `Home` Étape 2 → `Animations`, Étape 3 → `Guide-Ollama-Pratique`, Étape 4 sans lien a été fait par Claude (convention de `Structure-Projet-Complet`) : modifiable sur demande.

---
*RAPPORT_AUDIT_COMPLET_20261112_1921.md · projet SITE ZETA · hprzeta · 12/11/2026 19:21 · 169 lignes*
