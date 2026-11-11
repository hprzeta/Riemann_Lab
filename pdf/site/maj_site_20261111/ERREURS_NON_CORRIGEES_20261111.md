# Points non corrigés — mise à jour site et wiki du 11/11/2026

> **Usage.** Fichier rechargeable à donner à Claude Code (dépôt `~/projet_zeta`, branche `Riemann_Lab_IA`).
> Il liste ce qui n'a PAS été corrigé lors de la mise à jour du 11/11/2026, avec la cause et l'action proposée.
> **Rien ne se corrige sans « go » de hprzeta** : un lot à la fois, un arrêt avant chaque commit et chaque push, jamais `--force`.
> Sources de la mise à jour : `JOURNAL.md` (pavé 2026-11-11), `Handoff.md` (« REPRENDRE ICI — 11/11/2026 »), PDF `MAJ_SITE_ZETA_20261111_HHMM.pdf`.
> Aucun secret, adresse IP ou identifiant réseau dans ce fichier.

---

## A. Finalisé le 11/11 (commité ET poussé : wiki `daedaa7`, code `96cccc2`, `fcf4921`)

| # | Élément | Où | Action |
|---|---|---|---|
| A1 | Ancre morte `Bibliotheques#17--v13v15…` → `#17bis--v13v15…` (antérieure à la mise à jour) | `docs/index.html` (code, `Riemann_Lab_IA`) | FAIT et POUSSÉ : commit `96cccc2` sur `Riemann_Lab_IA`, porté par `cherry-pick -x` sur `Riemann_Lab_C` (`a6824d5`), `main` (`e2fa466`), `Riemann_Lab_Test` (`f03ddb5`) |
| A2 | Note « levé le 05/11/2026 » en tête de 3 analyses datées | wiki : `analyse_problemes_v13_v15.md`, `analyse_problemes_v1_v16.md`, `analyse_math_deficit_2026-08-18.md` | FAIT et POUSSÉ : commit de clôture du wiki `daedaa7` (voir A3) |
| A3 | Pavé du jour et section « REPRENDRE ICI » | wiki : `JOURNAL.md`, `Handoff.md` | FAIT et POUSSÉ : commit `daedaa7` (avec A2) |
| A4 | Copies locales synchronisées (hors git, `md/…`) : `niveau-1` à `niveau-5`, `analyse_problemes_v13_v15`, `analyse_problemes_v1_v16` | `md/cours`, `md/cpmd`, `md/optimisation` | rien à commiter (dossier `md/` exclu de git) |

## B. Décisions de hprzeta (toutes décidées ; B3 : reste interne)

| # | Point | Constat | Action proposée |
|---|---|---|---|
| B1 | `README.md`, section « État actuel — juillet 2026 » | était : « 10 016 377 (T=5M, 96 manquants) », v15, 517 z/s, 4.4 min, RAM 8 Go | FAIT et POUSSÉ sur décision de hprzeta : `fcf4921` (IA), `0f9a917` (C), `1a0b9cc` (main), `a500b4b` (Test) |
| B2 | Bloc de statistiques du haut du site | « 138 069 zéros validés · 10⁻¹⁵ · t max atteint 99 999 » : décrit le run T=100k seulement | FAIT (décidé : passer à 5·10⁶) : « 10 016 474 zéros · Turing complet » et « t max 5 000 000 » dans `docs/index.html` ; **commité, reste à pousser** |
| B3 | Jeu de référence 5·10⁶ (10 016 474 zéros, SHA-256 `b3a98a34…`) | publication non décidée ; création de la release GitHub refusée par le système d'autorisation | DÉCIDÉ : reste interne ; aucun lien de téléchargement sur le site ; à reconsidérer après le run V17 complet (optionnel) |
| B4 | Issues #2 à #5 (ouvertes le 14/04/2026, dernière mise à jour 13/05/2026) | textes d'avril (« 1000 premiers zéros avec mpmath », « Newton-Raphson ») sans rapport avec l'état réel | FAIT (décidé : commentaire d'état) : un commentaire factuel posté sur chacune des issues #2 à #5, sans les fermer |
| B5 | `pdf/vault/Guide-RAG-BrainVault-Debutant.md` (copie suivie par git) | divergeait déjà du wiki (25 lignes) avant la mise à jour ; la version wiki est passée à 1258 passages | FAIT (décidé : MD + PDF) : `.md` rebasé sur la version wiki (4 lignes anonymisées conservées), PDF régénéré (9 pages) ; **commité sur les 4 branches, reste à pousser** |

## C. Contradictions entre sources, non tranchées

| # | Contradiction | Sources | Action proposée |
|---|---|---|---|
| C1 | Gains cumulés depuis v1 : ×720 (v12, `Plancher`, base 48 h) · ×143 (v12) et ×28 600+ (v15) (`Etape-1`, base 21 h) · ×787,5 (v16, `STACK.md` et site) | `Plancher-Hardware-Architecture.md`, `Etape-1-…md`, `STACK.md`, `docs/index.html` | FAIT (décidé : T égal, T=10 000, v2 → v16 ≈ ×7 490) : section « Gains cumulés à T égal » dans `Etape-1`, site, annotations dans `Etape-1`/`Roadmap`/`STACK` ; FAIT ensuite : note en tête de 6 analyses datées (v7_v8, v8_v9, v9_v10, v10_v12, v13_v15, v1_v16) et ligne de `Formules_zeta` annotée ; PDF de ces analyses non régénérés |
| C2 | v11 : « prototype Illinois Z_rs + 2 Newton, ~15–20 min » (`Plancher`) contre « jamais implémentée » (`Roadmap.md` d'après le `Handoff`) | idem | FAIT (décidé : cache (fa,fb), sans script dédié) : `Plancher`, `Roadmap`, `Handoff` harmonisés ; aucun `compute_zeros_v11.py` ni commit trouvé |
| C3 | Origine du fichier `materielunixlitepc2.txt` (« pcfix2 », Pentium E2140, juin 2026) : le JOURNAL le décrit comme PC3, mais le CPU de PC3 mesuré est l'Athlon II X2 215 | `JOURNAL.md` (18/08, 13/06), `~/zeta_inventaire/MATERIEL/zeta_pc3_backup.txt` | RÉSOLU : PC3 = Acer Aspire M3203 (DMI) ; `pcfix2` (Presario, Pentium E2140) est un autre PC ; `STACK.md` et `Architecture-Cluster-Zeta.md` corrigés ; **commité, reste à pousser** |
| C4 | Cause des manquants à 5·10⁶ : 84 paires + 13 isolés (mesuré le 05/11) contre ≈ 85 + ≈ 12 (analyse du 01/11) | `JOURNAL.md`, `Handoff.md`, `STACK.md` | le site affiche 84 + 13 avec la mention de l'ancienne estimation ; aligner `STACK.md` si besoin |
| C5 | `STACK.md` : « Ubuntu 16.04.7 » (PC3) remplacé par « Linux Lite 3.8 (base Ubuntu 16.04.7) » ; le mot « 16.04.7 » vient de l'inventaire du 03/10, `lsb_release` ne donne que 16.04 | `STACK.md`, inventaire PC3 | RÉSOLU : l'inventaire du 03/10 (`os-release`) confirme Ubuntu 16.04.7 LTS ; libellé conservé |

## D. Contenus périmés laissés en l'état (hors périmètre du lot)

| # | Page | Passage |
|---|---|---|
| D1 | `Structure-Projet-Complet.md` | `compute_zeros_v4_1.py` marqué « ⭐ ACTIF » ; tableau des rôles et statistiques de `src/` de l'époque v4.1 |
| D2 | `Configuration-Materielle-Logicielle.md` | « multiprocessing (4 workers) » (8 workers depuis v10) ; « Disque 1 To, 3 partitions ≈ 908 Go » non revérifié |
| D3 | `Plancher-Hardware-Architecture.md` §4 à §6 | décrit le « plancher » v12 (note d'avertissement ajoutée, texte non réécrit) ; §7 « v13 OS » planifié non réalisé |
| D4 | `STACK.md` | l. 338 « 8 animations » (case historique), l. 413 « R2+R8 rerun T=5M … recoupement des 96 manquants » (case non cochée, en partie réalisée le 05/11), l. 427 « 838 chunks » (historique daté) |
| D5 | `Animations.md`, tableau « Intégration dans le cours » | les 4 nouvelles animations ne sont rattachées à aucune page de cours (colonne « Cours associé » = —) |
| D6 | PDF des 3 analyses datées | `analyse_problemes_v13_v15`, `analyse_problemes_v1_v16`, `analyse_math_deficit` : la note du 11/11 est dans les `.md`, pas dans les PDF publiés |
| D7 | `md/cpmd/analyse_problemes_v16_v17.md`, `md/optimisation/analyse_problemes_v16_v17.md`, copies `analyse_math_deficit` (`md/…`, `pdf/optimisation/Voie_b_5/…`), copies `Guide-RAG` (`md/…`) | divergeaient déjà du wiki avant la mise à jour (non écrasées) |

## E. Outils et environnement

| # | Problème | Détail | Contournement utilisé |
|---|---|---|---|
| E1 | Extension Claude in Chrome : outil JavaScript | « No response to the permission prompt » : fenêtre d'autorisation jamais acceptée | Playwright (zeta_env, sans interface) : 10 pages, 0 erreur de console, 0 requête ≥ 400, 0 erreur de formule |
| E2 | Serveur MCP GitHub | « Authentication Failed: Bad credentials » (non touché) | API publique GitHub pour lire les issues |
| E3 | `scripts/build_pdf_riemann_CM.sh` | échec `lualatex` (`\lstinline`) sur un caractère non ASCII dans du code en ligne (`≤`, `é`, `…`) ; le script n'est pas modifié | CORRIGÉ le 11/11 : translittération dans le script (`.bak-20261111`), testé sur 3 documents |
| E4 | API `pages/builds/latest` | renvoie 404 : statut « built » non lisible | contenu servi vérifié (« V17 en production » présent), PDF servi par `main` vérifié (128 369 octets, `%PDF`) |
| E5 | `pkill -f` dans une commande Bash | a tué son propre shell (motif présent dans sa ligne de commande) | utiliser `fuser -k <port>/tcp` |

## F. Rappel des règles du dépôt à respecter pour la suite

- Copie `.bak-AAAAMMJJ` avant de modifier un script ou un fichier de configuration.
- Audit avant push : `duckdns`, `PRIVATE KEY`, `ghp_`, `github_pat`, `api key`, `token=`, `passw=`, adresses MAC, IPv4/IPv6, e-mails.
- Commits sur `Riemann_Lab_IA` puis `cherry-pick -x` sur `Riemann_Lab_C`, `main`, `Riemann_Lab_Test` ; le site n'est publié que depuis `Riemann_Lab_IA`, dossier `/docs`.
- `src/ia/prompts/` est local seulement ; `md/` est exclu de git.
- KaTeX : pas de `\operatorname`, pas de `\_ \# \, \; \! \%` dans les blocs math, pas de `|` dans une cellule de tableau math.

---
*ERREURS_NON_CORRIGEES_20261111.md · maj_site_20261111 · hprzeta · MAJ 2026-11-11 · 71 lignes*
