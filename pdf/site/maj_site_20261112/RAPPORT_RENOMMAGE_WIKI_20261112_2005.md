# Rapport — Renommage des 5 pages wiki à accents (D26) et titres d'Animations sans symbole (D27) — 12/11/2026 20:06

> Exécution de `PROMPT_RENOMMAGE_WIKI_20261112_1949.md`. Choix de hprzeta à l'étape 2 : **« go correction avec renvoi »**. Aucun `--force`. Wiki : commits `8045f4e` et `7e2da49`, poussés (`2bd4258..7e2da49`). Aucun fichier du site, du `README.md` ni des scripts n'a eu besoin d'être modifié (0 lien entrant).

## 1. Tableau de validation

| Élément | Statut | Preuve |
|---|---|---|
| 5 pages renommées (`git mv`, historique conservé) | 🟢 | R051 à R099 ; `git log --follow` retrouve l'historique d'avant |
| 5 pages de renvoi aux anciens noms | 🟢 | ouvertes dans Chrome : « Page renommée » + lien vers le nouveau nom |
| 25 liens + 3 mentions mises à jour dans 17 pages | 🟢 | re-test : 819 🟢, 14 🟡, 4 🔴 (avant renommage : 813/14/4) |
| Aucun nouveau 🔴 | 🟢 | 0 nouveau(x) 🔴 par rapport à l'état d'avant |
| `Animations` : 13 titres sans symbole, 12 ancres du tableau | 🟢 | 12 ancres sur 12 présentes (cadre vert dans Chrome), 0 manquante |
| `a.absent` (lien vers page inexistante) | 🟢 | 0 page(s) sur 89 avec un lien absent |
| Site, `README.md`, scripts, PDF publiés | 🟢 | 0 lien vers les 5 pages (321 fichiers et 117 PDF scannés) |
| Mentions volontairement laissées | 🟡 | 17 historiques + `Guide-Ollama-Pratique` l.101 (citation RAG du 25/07) + `Guide-Git-GitHub` l.105 (exemple de commande) : voir §6 |

## 2. Renommages

| Ancien nom | Nouveau nom | Liens entrants (audit) | Renvoi à l'ancien nom |
|---|---|---|---|
| `Etape-1-Calcul-des-zéros-non-triviaux` | `Etape-1-Calcul-des-zeros-non-triviaux` | 19 | oui |
| `Interprétation-des-résultats-de-tests` | `Interpretation-des-resultats-de-tests` | 2 | oui |
| `Partie-1-La-Théorie-Étape_1` | `Partie-1-La-Theorie-Etape_1` | 1 | oui |
| `Projet-Zêta` | `Projet-Zeta` | 1 | oui |
| `Tableau-Symboles-Mathématiques` | `Tableau-Symboles-Mathematiques` | 2 | oui |

`Projet-Zêta` était déjà une page de redirection vers `Home` : son renvoi pointe directement vers `Projet-Zeta` et `Home` (pas de double redirection).

## 3. Liens mis à jour (état avant : fichier, ligne, forme du lien)

| Cible | Forme | Fichier | Ligne | Nouveau lien |
|---|---|---|---|---|
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | Animations.md | 160 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | Architecture-Cluster-Zeta.md | 777 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | Markdown | Home.md | 23 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | Home.md | 145 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | Optimisation-Pourquoi-le-calcul-va-vite.md | 178 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | Markdown | Phase-Optimisation-compute_zeros_v3.md | 3 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | Plancher-Hardware-Architecture.md | 281 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | Projet-Zêta.md | 8 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | Roadmap.md | 77 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | Roadmap.md | 201 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | STACK.md | 539 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | Structure-Projet-Complet.md | 148 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | Structure-Projet-Complet.md | 229 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | analyse_problemes_v10_v12.md | 3 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | analyse_problemes_v13_v15.md | 5 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | analyse_problemes_v1_v16.md | 5 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | analyse_problemes_v7_v8.md | 3 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | analyse_problemes_v8_v9.md | 3 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Etape-1-Calcul-des-zéros-non-triviaux` | [[…]] | analyse_problemes_v9_v10.md | 3 | `Etape-1-Calcul-des-zeros-non-triviaux` |
| `Interprétation-des-résultats-de-tests` | Markdown | Home.md | 22 | `Interpretation-des-resultats-de-tests` |
| `Interprétation-des-résultats-de-tests` | [[…]] | Optimisation-Pourquoi-le-calcul-va-vite.md | 181 | `Interpretation-des-resultats-de-tests` |
| `Partie-1-La-Théorie-Étape_1` | Markdown | Home.md | 24 | `Partie-1-La-Theorie-Etape_1` |
| `Projet-Zêta` | Markdown | Home.md | 18 | `Projet-Zeta` |
| `Tableau-Symboles-Mathématiques` | Markdown | Home.md | 21 | `Tableau-Symboles-Mathematiques` |
| `Tableau-Symboles-Mathématiques` | [[…]] | Structure-Projet-Complet.md | 227 | `Tableau-Symboles-Mathematiques` |

`Animations.md` : 13 titres sans symbole (titre principal + 12 sections) ; 12 liens du tableau « Vue d'ensemble » mis à jour vers les ids sans symbole (par exemple `#animation_gamma--fonction-gamma`). Aucun lien extérieur vers ces ancres (site ni autres pages).

## 4. Échantillon A / B / C de hprzeta

Échantillon (8 liens : 4 depuis `Home` vers les pages renommées, 1 ancien nom → renvoi → nouveau nom, 3 ancres d'`Animations`) : réponse de hprzeta « c » → interprété **C pour les 8** (au bon endroit), le 12/11/2026.

Remarque : le site ne contient aucun lien vers les 5 pages, donc l'échantillon « dont 2 depuis le site » du prompt est remplacé par des liens depuis la page `Home` du wiki.

## 5. Lignes modifiées (page · ligne in · ligne out · date heure)

| Commit | Page | Ligne in | Ligne out | Date heure |
|---|---|---|---|---|
| 8045f4e | Animations.md | 1 | 1 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 14-25 | 14-25 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 31 | 31 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 48 | 48 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 60 | 60 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 73 | 73 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 85 | 85 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 98 | 98 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 112 | 112 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 124 | 124 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 136 | 136 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 150 | 150 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 160 | 160 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 164 | 164 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 178 | 178 | 2026-11-12 19:58 |
| 8045f4e | Animations.md | 217 | 217 | 2026-11-12 19:58 |
| 8045f4e | Architecture-Cluster-Zeta.md | 777 | 777 | 2026-11-12 19:58 |
| 8045f4e | Architecture-Cluster-Zeta.md | 787 | 787 | 2026-11-12 19:58 |
| 8045f4e | Etape-1-Calcul-des-zeros-non-triviaux.md | 532 | 532 | 2026-11-12 19:58 |
| 8045f4e | Formules_zeta.md | 1411 | 1411 | 2026-11-12 19:58 |
| 8045f4e | Formules_zeta.md | 1762 | 1762 | 2026-11-12 19:58 |
| 8045f4e | Home.md | 18 | 18 | 2026-11-12 19:58 |
| 8045f4e | Home.md | 21-24 | 21-24 | 2026-11-12 19:58 |
| 8045f4e | Home.md | 145 | 145 | 2026-11-12 19:58 |
| 8045f4e | Home.md | 169 | 169 | 2026-11-12 19:58 |
| 8045f4e | Interpretation-des-resultats-de-tests.md | 150 | 150 | 2026-11-12 19:58 |
| 8045f4e | Optimisation-Pourquoi-le-calcul-va-vite.md | 178 | 178 | 2026-11-12 19:58 |
| 8045f4e | Optimisation-Pourquoi-le-calcul-va-vite.md | 181 | 181 | 2026-11-12 19:58 |
| 8045f4e | Optimisation-Pourquoi-le-calcul-va-vite.md | 191 | 191 | 2026-11-12 19:58 |
| 8045f4e | Partie-1-La-Theorie-Etape_1.md | 146 | 146 | 2026-11-12 19:58 |
| 8045f4e | Phase-Optimisation-compute_zeros_v3.md | 3 | 3 | 2026-11-12 19:58 |
| 8045f4e | Phase-Optimisation-compute_zeros_v3.md | 504 | 504 | 2026-11-12 19:58 |
| 8045f4e | Plancher-Hardware-Architecture.md | 100 | 100 | 2026-11-12 19:58 |
| 8045f4e | Plancher-Hardware-Architecture.md | 281 | 281 | 2026-11-12 19:58 |
| 8045f4e | Plancher-Hardware-Architecture.md | 288 | 288 | 2026-11-12 19:58 |
| 8045f4e | Projet-Zeta.md | 8 | 8 | 2026-11-12 19:58 |
| 8045f4e | Projet-Zeta.md | 11 | 11 | 2026-11-12 19:58 |
| 8045f4e | Roadmap.md | 77 | 77 | 2026-11-12 19:58 |
| 8045f4e | Roadmap.md | 201 | 201 | 2026-11-12 19:58 |
| 8045f4e | Roadmap.md | 207 | 207 | 2026-11-12 19:58 |
| 8045f4e | STACK.md | 539 | 539 | 2026-11-12 19:58 |
| 8045f4e | STACK.md | 706 | 706 | 2026-11-12 19:58 |
| 8045f4e | Structure-Projet-Complet.md | 148 | 148 | 2026-11-12 19:58 |
| 8045f4e | Structure-Projet-Complet.md | 227 | 227 | 2026-11-12 19:58 |
| 8045f4e | Structure-Projet-Complet.md | 229 | 229 | 2026-11-12 19:58 |
| 8045f4e | Structure-Projet-Complet.md | 244 | 244 | 2026-11-12 19:58 |
| 8045f4e | Tableau-Symboles-Mathematiques.md | 272 | 272 | 2026-11-12 19:58 |
| 8045f4e | analyse_problemes_v10_v12.md | 3 | 3 | 2026-11-12 19:58 |
| 8045f4e | analyse_problemes_v10_v12.md | 196 | 196 | 2026-11-12 19:58 |
| 8045f4e | analyse_problemes_v13_v15.md | 5 | 5 | 2026-11-12 19:58 |
| 8045f4e | analyse_problemes_v13_v15.md | 307 | 307 | 2026-11-12 19:58 |
| 8045f4e | analyse_problemes_v1_v16.md | 5 | 5 | 2026-11-12 19:58 |
| 8045f4e | analyse_problemes_v1_v16.md | 416 | 416 | 2026-11-12 19:58 |
| 8045f4e | analyse_problemes_v7_v8.md | 3 | 3 | 2026-11-12 19:58 |
| 8045f4e | analyse_problemes_v7_v8.md | 157 | 157 | 2026-11-12 19:58 |
| 8045f4e | analyse_problemes_v8_v9.md | 3 | 3 | 2026-11-12 19:58 |
| 8045f4e | analyse_problemes_v8_v9.md | 176 | 176 | 2026-11-12 19:58 |
| 8045f4e | analyse_problemes_v9_v10.md | 3 | 3 | 2026-11-12 19:58 |
| 8045f4e | analyse_problemes_v9_v10.md | 171 | 171 | 2026-11-12 19:58 |
| 7e2da49 | Etape-1-Calcul-des-zéros-non-triviaux.md | (aucune) | 1-10 | 2026-11-12 19:58 |
| 7e2da49 | Interprétation-des-résultats-de-tests.md | (aucune) | 1-10 | 2026-11-12 19:58 |
| 7e2da49 | Partie-1-La-Théorie-Étape_1.md | (aucune) | 1-10 | 2026-11-12 19:58 |
| 7e2da49 | Projet-Zêta.md | (aucune) | 1-12 | 2026-11-12 19:58 |
| 7e2da49 | Tableau-Symboles-Mathématiques.md | (aucune) | 1-10 | 2026-11-12 19:58 |

Dans le PDF, les lignes supprimées sont en rouge et les ajoutées en vert.

## 6. Mentions des anciens noms laissées (à décider)

| Fichier | Ligne | Raison |
|---|---|---|
| Archive-Fichiers-Obsoletes.md | 96 | historique (journal, archive, rapport daté) |
| Guide-Ollama-Pratique.md | 101 | citation RAG du 25/07/2026 (enregistrement) |
| JOURNAL.md | 868 | historique (journal, archive, rapport daté) |
| etat_rag_brainvault_20260704.md | 90 | historique (journal, archive, rapport daté) |
| etat_rag_brainvault_20260704.md | 110 | historique (journal, archive, rapport daté) |
| Archive-Fichiers-Obsoletes.md | 93 | historique (journal, archive, rapport daté) |
| Guide-Git-GitHub.md | 105 | exemple de commande avec nom préfixé d'un emoji |
| JOURNAL.md | 869 | historique (journal, archive, rapport daté) |
| etat_rag_brainvault_20260704.md | 99 | historique (journal, archive, rapport daté) |
| Archive-Fichiers-Obsoletes.md | 95 | historique (journal, archive, rapport daté) |
| etat_rag_brainvault_20260704.md | 102 | historique (journal, archive, rapport daté) |
| discusion_claude_2026-11-11.md | 18 | historique (journal, archive, rapport daté) |
| discusion_claude_2026-11-11.md | 28 | historique (journal, archive, rapport daté) |
| discusion_claude_2026-11-11.md | 41 | historique (journal, archive, rapport daté) |
| JOURNAL.md | 48 | historique (journal, archive, rapport daté) |
| etat_rag_brainvault_20260704.md | 102 | historique (journal, archive, rapport daté) |
| Archive-Fichiers-Obsoletes.md | 89 | historique (journal, archive, rapport daté) |
| JOURNAL.md | 734 | historique (journal, archive, rapport daté) |
| etat_rag_brainvault_20260704.md | 102 | historique (journal, archive, rapport daté) |

Scripts qui citent un ancien nom : aucun.

## 7. Tests habituels

| Test | Résultat |
|---|---|
| Chrome (onglet « Mise à jour site ») | 5 nouvelles pages ouvertes (0 `a.absent`, 0 « Unable to render ») ; 5 anciennes adresses : « Page renommée » avec lien vers le nouveau nom ; `Animations` : 12 ancres encadrées en vert |
| `.katex-error` / formule brute | 0 / 0 sur les pages ouvertes (relevé sur les 3 pages longues) |
| Secrets | audit des lignes ajoutées : aucune ligne suspecte |
| 390 px | non mesuré : aucun changement du site |

---
*RAPPORT_RENOMMAGE_WIKI_20261112_2005.md · projet SITE ZETA · hprzeta · 12/11/2026 20:06 · 175 lignes*
