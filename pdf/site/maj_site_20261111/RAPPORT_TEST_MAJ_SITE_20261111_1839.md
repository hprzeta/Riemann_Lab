# Rapport de test — mise à jour du site du 11/11/2026 (lecture seule)

> Réalisé le 11/11/2026 à 18h39 par Claude Code (Chrome + shell). Aucun fichier du dépôt modifié, aucun commit, aucun commentaire GitHub.
> Statut : 🟢 ok · 🟡 fait à moitié · 🔴 pas fait ou ko.

## 1. Tableau de validation

### Site (https://hprzeta.github.io/Riemann_Lab/)

| Élément | Statut | Preuve (comment vérifié) | Reste à corriger |
|---|---|---|---|
| 1 Bandeau V17 (03/11/2026) | 🟢 | texte de la page lu dans Chrome | Le bandeau dit aussi « 138 069 zéros validés » (T=100k) alors que les stats disent 10 016 474 : cohérent mais peut surprendre |
| 2 Stats du haut | 🟢 | page lue : 10 016 474 · Turing complet · 5 000 000 | — |
| 3 Tableau v1→V17, ligne V17, lien PDF | 🟡 | ligne V17 livrée, lien `analyse_problemes_v16_v17.pdf` présent, répond 200 (curl). Ouverture/lisibilité du PDF non vérifiée à l'écran | Frise « PROGRESSION V1 → V17 » : la dernière tuile est v16 (pas de tuile V17). Titre de la section perfs : « … V16 ⭐ » |
| 4 Bloc T=5M | 🟢 | page lue : 97 retrouvés, 10 016 474, 84 paires + 13 isolés | — |
| 5 Section IA | 🟢 | page lue : 1258 passages, « Exploratoire / WIP » | — |
| 6 Les 4 nouvelles animations | 🟢 | `gaps_gue`, `illinois_adaptatif`, `ntermes_rs`, `prec_mpfr` chargées ; éléments `.katex` : 11 / 21 / 7 / 8, 0 `.katex-error`, pas de `$…$` brut ; capture visuelle seulement de `prec_mpfr` | Rendu des 3 autres contrôlé par le DOM, pas à l'œil |
| 7 Issues ouvertes | 🟢 | texte « 4 ouvertes (#2 à #5, du 14/04/2026) … » | — |
| 8 Cartes cluster | 🟢 | PC1 16 GB + 16 GB swap · PC2 7.6 GB · PC3 5.7 GB Linux Lite | — |
| 9 Gain à T égal | 🟢 | « ×7 490 » (T=10 000) présent ; aucun « ×787,5 » dans le texte | — |
| 10 Pied de page | 🟢 | « mis à jour le 11/11/2026 » | — |
| Formules / tableaux / débordement | 🟢 | 53 `.katex`, 0 erreur, pas de défilement horizontal, 0 image cassée | — |
| Console du navigateur | 🟡 | `read_console_messages` : aucun message, mais le suivi ne démarre qu'au premier appel, après le chargement de la page. Aucune demande d'autorisation JS n'est apparue | Rouvrir la page avec la console déjà suivie pour conclure |
| Un lien cliqué par section | 🟡 | non cliqués à la main ; les 61 liens externes testés en HTTP (voir E) | — |

### Wiki

| Page | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Home | 🟢 | 24 formules rendues, 0 erreur, 6 tableaux ; « Dernière mise à jour : 11 novembre 2026 » | — |
| Etape-1-Calcul-des-zéros… | 🟢 | 20 formules, 0 erreur, 28 tableaux ; MAJ 11/11 | — |
| Roadmap | 🟢 | 6 formules, 0 erreur ; MAJ 2026-11-11 | — |
| Animations | 🟢 | 89 formules, 0 erreur ; MAJ 11/11 | « Cours associé » = « — » pour les 4 nouvelles (voir G) |
| Projet-Zêta | 🟡 | affiche « page déplacée » avec lien vers Accueil : c'est une page-stub, pas une redirection HTTP | À toi de dire si le stub suffit |
| Plancher-Hardware-Architecture | 🟢 | 29 formules, 0 erreur ; pied MAJ 2026-11-11 | l'en-tête dit encore « MAJ : 2026-06-13 » |
| Structure-Projet-Complet | 🟡 | rendu ok ; pied mis à jour le 11/11 | l'en-tête dit « MAJ : 2026-06-13 » |
| Configuration-Materielle-Logicielle | 🟡 | rendu ok (pas de formule) ; pied mis à jour le 11/11 | l'en-tête dit « MAJ : 2026-06-13 » |

### Points A à G

| Point | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| A Issues #3, #4, #5 | 🟢 | ouvertes dans Chrome : commentaire « État au 11/11/2026 … l'issue n'est pas fermée » présent sur chacune (#5 lue en entier) | #2 non re-testée |
| B « 96 manquants » | 🟢 | `grep -n` : lignes 18, 523, 525 — toutes présentées comme historique (« au journal de juin », « conservé comme historique ») | — |
| C Branches | 🟢 | `git diff Riemann_Lab_IA <branche> -- docs` vide pour `main`, `Riemann_Lab_C`, `Riemann_Lab_Test` : docs/ identique. 8 commits récents sur C/main/Test, 9 sur IA | Les hashes diffèrent (cherry-picks). Le commit en plus sur IA est le rangement `pdf/site/` (voulu : branche IA seule). Je n'ai pas apparié message par message |
| D PDF des 3 analyses | 🔴 | `pdftotext` : 0 occurrence de « 11/11/2026 » ou « 05/11/2026 » dans `analyse_problemes_v13_v15.pdf` (dernier commit 04/07) et `analyse_problemes_v1_v16.pdf` (08/08). `analyse_math_deficit_2026-08-18.pdf` n'est **pas suivi par git** (présent seulement en local sous `pdf/optimisation/Voie_b_5/md_to_claude/`, daté 18/08, sans note) | Régénérer les PDF v13_v15 et v1_v16 ; décider si le PDF déficit doit être publié |
| E Liens externes | 🟢 | 61 liens extraits de `docs/index.html`, `curl -L` : 61 × HTTP 200 | Ancres `#…` non vérifiées |
| F Secrets / identifiants | 🟡 | `grep` sur `docs/` (hors `archive/` et `*.bak*`) : aucun `duckdns`, `PRIVATE KEY`, `ghp_`, `github_pat`, `token=`, IPv4 réelle, IPv6, adresse MAC. « passw » = prose (NOPASSWD, mot de passe) ; hits de `T10Demo/…html` = code minifié, faux positifs | Un e-mail en clair : `docs/diagnostics/20261003_CLUSTER_durcissement-ssh.md:19` (`[EMAIL]`). `docs/archive/` non audité |
| G Restes périmés wiki | 🔴 | `grep` : voir ci-dessous | tous encore présents |

Détail G (`grep` sur le wiki) :
- `Structure-Projet-Complet.md` l.47 et l.164 : `compute_zeros_v4_1.py` « ⭐ ACTIF ».
- `Configuration-Materielle-Logicielle.md` l.94 : « multiprocessing (4 workers) » ; l.17 : « 3 partitions ≈ 908 Go » (je n'ai pas vérifié si le chiffre est faux).
- `Animations.md` l.22 à 25 : « Cours associé » = « — » pour les 4 nouvelles animations.
- `Plancher-Hardware-Architecture.md` : §4 « Pourquoi v12 est le plancher de l'i7 », §5, §6 « Projection T=1 000 000 (v12) » toujours là.

## 2. Erreurs rencontrées

- Aucun lien cassé (61/61 en 200), aucune formule non rendue, aucune page qui ne charge pas.
- Console : non concluante (voir ci-dessus).
- Un appel JavaScript a échoué en cours de navigation (« page navigated to a different domain ») : problème de synchronisation de ma part, rejoué avec succès.

## 3. Captures d'écran

Aucune enregistrée : les problèmes trouvés sont textuels (grep, PDF, en-têtes), sans défaut visuel à capturer.

## 4. Limites de ce test

- L'onglet n'a pas pu être nommé « Recherche MAJ site » (pas de fonction de renommage dans l'extension) ; j'ai utilisé l'onglet vide du groupe MCP.
- Les formules des wikis et animations sont contrôlées par le DOM (`math-renderer`, `.katex`), pas par lecture visuelle de chaque page.
- Les liens n'ont pas été cliqués un par un.

---
*Rapport — 11/11/2026 18h39 — lecture seule*
