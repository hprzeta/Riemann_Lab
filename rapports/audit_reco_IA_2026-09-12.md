# Audit des recommandations IA (DeepSeek / Kimi / Grok) — 2026-09-12

> Mode : **AUDIT LECTURE SEULE**. Aucun code modifié, aucun commit, aucun push, aucune exécution longue.
> Source : `/home/riemann/Téléchargements/PROMPT_audit_reco_IA_2026-09-12.md`.
> Dépôt audité : `~/projet_zeta`, branche `Riemann_Lab_C`.

---

## Tâche 1 — Vérité terrain

**Pipeline de production réel : `src/calculs/optimisation/compute_zeros_v16.py`.**

Preuve directe — `scripts/zeta_run.sh` (lu intégralement) lance :
```
nohup bash -c "printf '${T_MAX}\nO\n' | python ${SRC_DIR}/compute_zeros_v16.py"
```
C'est le seul point d'entrée production. `zeta_run.sh` encadre le run de `zeta_turbo_on.sh`/`zeta_turbo_off.sh` comme l'exige le CLAUDE.md racine.

`compute_zeros_v15.py` existe toujours (46 494 octets, modifié 08/08/2026) et reste la référence documentée pour le rerun T=5M évoqué dans le prompt (« Plan déjà acté : relancer T=5M en v15 »), mais **le moteur courant lancé par `zeta_run.sh` est v16**, pas v15.

| Élément | Statut | Preuve |
|---|---|---|
| Fonction de Hardy Z(t) | ✅ Présent (arb, pas mpmath) | `compute_zeros_v16.py:63` `from arb_wrapper import arb_hardy_z, info_backend, ARB_DISPONIBLE` ; en-tête `compute_zeros_v16.py:4-17` : « Z_arb (Phase 2, illinois_arb.c) appelle désormais `acb_dirichlet_hardy_z` ». Détection scan_arb C (`scan_arb.c`, Z_double RS+C0/C1) pour t≥20 (`compute_zeros_v16.py:148-149`), arb_hardy_z pour t∈[14,65) (`compute_zeros_v16.py:210-218`). |
| Turing-Backlund | ✅ Présent et loggé | `compute_zeros_v16.py:62` `from turing_validation import valider_turing, N_attendu` ; appel `compute_zeros_v16.py:964` `resultats_turing = valider_turing(zeros, dps=30)` ; section `[6] VALIDATION TURING-BACKLUND` écrite dans le log (`compute_zeros_v16.py:657-665`), avec pour chaque checkpoint T, calculés, attendus, delta, statut. |
| N(T) Riemann–von Mangoldt (facteur e) | ✅ Correct, facteur e présent | `turing_validation.py:75-93` `N_attendu(T) = theta_fast(T)/math.pi + 1.0` (formule exacte via θ, pas l'approximation de Weyl) ; ET dans `compute_zeros_v16.py:93` et `:241` `T/(2*math.pi) * math.log(T/(2*math.pi*math.e))` — le facteur `e` est bien dans le `log`, conforme à la règle canonique du CLAUDE.md racine. |
| Précision (arb adaptatif vs fixe) | ⚠️ Fixe par design (voir A3/R5) | En-tête `compute_zeros_v16.py:4-19` : « Z_arb à précision fixe (acb_dirichlet_hardy_z) […] Précision 64 bits choisie : coïncide avec WP_INITIAL de arb_fpwrap ». `arb_fpwrap_cdouble_hardy_z` escalade en interne 64→128→…→8192 bits *si nécessaire* (comportement Arb natif), donc ce n'est pas un simple float64 aveugle, mais un choix délibéré de précision fixe côté appelant. |
| Journalisation des paramètres de run | ⚠️ Partielle | `ecrire_log()` (`compute_zeros_v16.py:591-690`) journalise T_MIN, T_MAX, STEP, N_WORKERS, TOL_ARB, T_SEUIL_PETIT_T, backend Arb, environnement (Python/OS/mpmath/CPU). **`MARGE_SECURITE` n'est PAS écrite dans le journal** — c'est une constante locale de `_step_adaptatif()` (`compute_zeros_v16.py:822`), jamais passée à `ecrire_log`. Aucun diff automatique vs run précédent. |

**Découverte critique (vigilance terrain) :** le prompt source affirme *« Paramètres verrouillés : MARGE_SECURITE=3.0 […] restaurée (a7fb498) »*. Vérification par `grep` + `git log -S` sur `compute_zeros_v15.py` **et** `compute_zeros_v16.py` :
```
compute_zeros_v16.py:731   commentaire historique : "MARGE_SECURITE = 3.0 (restaurée le 02/08/2026...)"
compute_zeros_v16.py:822   valeur RÉELLEMENT ACTIVE : MARGE_SECURITE = 10.0
```
`git log -p -S "MARGE_SECURITE = 3.0"` montre la séquence réelle : 2.0 → **3.0** (a7fb498) → 15.0 (a04ea1f) → **10.0 (valeur actuelle, commentée « validée en solo (3 zones dont T≈4,86M) »)**. Donc **le prompt source est basé sur un état antérieur de la calibration** — le verrou actuel du code est 10.0, pas 3.0, dans les deux fichiers v15.py et v16.py. Ceci doit être signalé à hprzeta avant tout rerun T=5M : le « correctement calibré » du plan acté doit être réévalué avec MARGE_SECURITE=10.0, pas 3.0.

Fichiers CLAUDE.md locaux lus : `src/calculs/optimisation/CLAUDE.md` (Illinois C, ctypes, PREC=170 bits, fallback obligatoire) et `c_modules/CLAUDE.md` — confirment que le portage C (`illinois_mpfr.so` / `illinois_arb.so`) est le chantier de perf principal, cohérent avec le corpus mémoire.

---

## Tâche 2 — Matrice d'applicabilité

| Reco | Statut | Preuve (fichier:ligne ou extrait) | Action étape 1 |
|---|---|---|---|
| **A1** — bug N(t) recalculé une seule fois pour tout le batch (`compute_zeros_v3.py`) | **DÉJÀ FAIT** (corrigé, mais dans un autre fichier que celui visé) | Le bug réel existait dans `riemann_siegel_batch.py:184-185` (`Z_batch` : `N_max = int(tau_max)+1` fixe pour tout le batch → termes RS parasites pour les petits t). Il a été corrigé par une fonction séparée `Z_vect_correct` (commentaire explicite `riemann_siegel_batch.py:221` : « Corrige le bug de Z_batch : N_max fixe → termes RS parasites pour petit t » ; masquage par ligne `riemann_siegel_batch.py:229-236`, `Ns = floor(taus)`, `mask = (arange<=Ns)`). **Confirmé aussi par la mémoire projet** (session 2026-05-31). Le pipeline v16 n'utilise ni `Z_batch` ni `compute_zeros_v3.py` : il appelle `scan_arb`/`arb_hardy_z` en C/Arb, structurellement insensible à ce bug Python. | Aucune — corrigé historiquement et de toute façon obsolète pour le moteur actuel. |
| **A2** — `residue.py`, `formule_explicite.py`, `equation_fonctionnelle.py` | **ÉTAPE 2** | `find` sur tout le dépôt (hors venv) : aucun fichier de ce nom n'existe. Ce sont des modules théoriques (ψ de von Mangoldt, ξ) hors périmètre « calcul industriel des zéros ». | Hors périmètre étape 1. |
| **A3** — `riemann_siegel.py` : Z(t) + C0 en boucle mpmath | **NE PAS TOUCHER** | Le fichier `riemann_siegel.py` existe et reste utile pour la partie [14,65) via `mp.fp.siegelz`/`mp.fp.findroot` (`compute_zeros_v16.py:214-224`), mais la détection de masse (t≥20) passe par `scan_arb.c` et `arb_hardy_z`/`acb_dirichlet_hardy_z` (Arb/FLINT natif, `compute_zeros_v16.py:4-17`). Remplacer par une boucle mpmath pure serait une **régression de perf majeure** (v16 gagne ×2,75 sur v15 justement en évitant les boucles mpmath sur la masse des zéros). | Ne rien changer. |
| **A4** — `multiprocessing.Pool`, vectorisation numpy float64, précision adaptative | **DÉJÀ FAIT** (supérieur) | `Pool` déjà utilisé : `compute_zeros_v16.py:351` (`with multiprocessing.Pool(processes=N_WORKERS)`) et `:441` (rescan). Vectorisation numpy déjà présente (`riemann_siegel_batch.py`, `Z_vect_correct`). Le moteur va au-delà : cluster multi-machines (cf. dossiers `calculs/v15_distribue_T*`, `--t-min/--t-max` CLI pour distribution, `compute_zeros_v16.py:891-899`) + portage C/Arb à précision garantie (64→8192 bits en interne côté `arb_fpwrap`). Le float64 naïf recommandé par A4 serait **insuffisant pour une certification** (pas de garantie de précision), contrairement à l'escalade Arb déjà en place. | Aucune — l'existant (cluster + Arb + Pool) est strictement supérieur à la reco naïve. |
| **A5** — vérification de symétrie des zéros (conjugué présent) | **ÉTAPE 2 / sans objet ici** | Le pipeline calcule les zéros sur la droite critique σ=½ via Z(t) réel (fonction de Hardy) : par construction, il n'y a pas de zéros "hors droite" à apparier à un conjugué dans ce mode de calcul — la symétrie ρ↔ρ̄ concerne l'équation fonctionnelle globale, pas la détection Z(t). Non vérifiable comme "bug" ici : aucun code de comparaison de conjugués trouvé, cohérent avec le fait que ce n'est pas le mode opératoire du moteur. | Hors périmètre étape 1 (relève de la validation théorique, cf. C3). |
| **R1** — colonnes CSV `\|ζ(ρ)\|` et `\|EF_gap(ρ)\|=\|Λ(ρ)−Λ(1−ρ)\|`, dps=30 | **À RAFFINER** (reco à réduire) | Aucune colonne de ce type dans `sauvegarder_csv()` (`compute_zeros_v16.py:572-589`, colonnes actuelles : zéros, stats, T_MAX, STEP, n_workers). **Point de vigilance tranché** : sur la droite critique, s=½+it, on a 1−s=s̄, donc dès que Λ(ρ) est réel (ce qui est le cas pour un vrai zéro), Λ(ρ)=Λ(1−ρ) est **automatique** — une colonne par zéro sur potentiellement 10M lignes ne certifierait rien de nouveau. L'intérêt réel de R1 est de détecter une **erreur de branche de Γ ou de θ** (bug de continuité de phase), qui se manifesterait par une valeur non nulle. | Patch minimal : script de validation **échantillonné** (ex. 1 zéro sur 10 000, ou N points fixes par décade en T), calculant `\|ζ(ρ)\|` et l'écart de phase à dps=30, **hors du run principal** (pas de colonne CSV en masse). |
| **R2** — certification des 96 manquants via Turing (bornes S(T)) + recoupement N(T) | **À RAFFINER** (l'outillage existe, le rerun manque) | `valider_turing()` déjà appelé et loggé (`compute_zeros_v16.py:964`, section `[6]` du log avec T/calculés/attendus/delta par checkpoint). `N_attendu()` (formule θ/π+1) existe (`turing_validation.py:75-93`). Ce qui manque : le **rerun effectif T=5M avec calibration à jour (MARGE_SECURITE=10.0, pas 3.0)** et un rapport dédié reliant les 96 manquants historiques à des checkpoints Turing précis. | Rerun T=5M (v15 ou v16 selon décision hprzeta) avec le sur-échantillonnage Turing déjà en place ; produire le rapport de recoupement en sortie de run, sans coder de nouveau mécanisme. |
| **R3** — espacements normalisés δₙ=(γₙ₊₁−γₙ)·log(γₙ/2π) | **ÉTAPE 2** | Aucune trace de ce calcul dans `compute_zeros_v16.py` (seuls écarts bruts min/max/moyens sont loggés, `compute_zeros_v16.py:633-637`, sans normalisation GUE). Analyse statistique de la loi GUE = hors périmètre "correction/complétude/vitesse". | Hors périmètre étape 1. |
| **R4** — journal de calibration/paramètres par run (dps, tol, itérations, erreur résiduelle max, valeur des paramètres) | **APPLICABLE** (correctif de fond, cf. plan Tâche 3) | Journal déjà riche (`ecrire_log`, section `[2] PARAMÈTRES v16`) mais **`MARGE_SECURITE` absente** (confirmé Tâche 1), pas de champ dps par étape, pas de diff automatique vs run précédent. C'est très exactement la lacune qui a permis à la régression `MARGE_SECURITE` 3.0→2.0 (commit non documenté) de passer inaperçue avant `a7fb498`. | Patch minimal : ajouter `MARGE_SECURITE` (valeur numérique, pas juste en commentaire) et dps utilisés aux arguments de `ecrire_log()` + `sauvegarder_csv()` metadata ; un script séparé de diff texte entre deux logs successifs (pas de nouvelle dépendance). |
| **R5** — exposer Z(t) | **NE PAS TOUCHER** (déjà exposé, via Arb) | `arb_hardy_z` est déjà exportée et utilisée (`arb_wrapper.py`, importée `compute_zeros_v16.py:63`). Le repasser par une implémentation mpmath comme semble le sous-entendre R5 serait une régression de perf (cf. A3). | Aucune — déjà fait, mieux que la reco. |
| **R6** — documenter R≈2√(t/2π) par décade | **ÉTAPE 2** | Pas de trace de documentation de ce rayon dans le code production ; c'est une note théorique (loi de répartition), pas un correctif de moteur. | Hors périmètre étape 1 — à verser au wiki/STACK si souhaité, pas au code. |
| **R7** — Odlyzko–Schönhage | **OBSOLÈTE / hors périmètre** | Le CLAUDE.md racine liste Odlyzko-Schönhage 1988 en simple référence bibliographique (§Références) ; le moteur v16 utilise Arb/FLINT (RS tronqué + Illinois), pas un algorithme FFT type Odlyzko-Schönhage. Implémenter Odlyzko-Schönhage serait un changement d'algorithme radical, pas un patch étape 1. | Hors périmètre étape 1 — chantier de recherche à part entière si un jour engagé. |
| **R8** — compter/journaliser les points de Gram défaillants | **DÉJÀ FAIT** (sous une forme équivalente) | `rescan_segments_deficit()` (`compute_zeros_v16.py:372-464`) calcule et journalise un **déficit par segment** (`n_attendus - n_trouves`, `compute_zeros_v16.py:417-418`), loggé en section `[7] RESCAN CIBLÉ PAR DÉFICIT` (`compute_zeros_v16.py:672-682`) avec segment, bornes, déficit, récupérés. Ce n'est pas littéralement un test de Gram (Z(gₙ)·(−1)ⁿ>0) mais remplit la même fonction diagnostique (localiser où des zéros manquent), avec une granularité par segment de worker. | Optionnel : ajouter le test de Gram classique en complément fin (par zéro, pas par segment) si le rerun R2 montre que le déficit par segment est insuffisamment précis. Non prioritaire vu que R2/rescan couvrent déjà l'essentiel. |
| **R9** — cartes de phase | **ÉTAPE 2** | Aucune trace dans le moteur (visualisation actuelle = `visualiser()`, nuage de points zéros vs T, `compute_zeros_v16.py` réf. `visualiser`). | Hors périmètre étape 1. |
| **R10** — histogrammes GUE | **ÉTAPE 2** | Idem R3, analyse statistique post-hoc. | Hors périmètre étape 1. |
| **R11** — fiches VAULT | **ÉTAPE 2** | Relève explicitement de l'étape 2 (VAULT/IA locale) mentionnée dans le prompt lui-même. | Hors périmètre étape 1 par définition du prompt source. |
| **R12** — dataset EF (équation fonctionnelle) | **ÉTAPE 2** | Dépend de R1 étendu ; pas de dataset EF dans le dépôt (`find` négatif). | Hors périmètre étape 1. |
| **R13** — garde-fous LLM | **ÉTAPE 2** | Hors calcul numérique ; relève de l'infrastructure IA locale (VAULT/RAG), déjà objet d'un chantier séparé (cf. mémoire projet, session RAG 19/07). | Hors périmètre étape 1. |
| **R14** — Lean 4 | **ÉTAPE 2** | Aucune trace de Lean/formalisation dans le dépôt. Chantier "Objectif 2" (agent IA autonome), pas étape 1. | Hors périmètre étape 1. |
| **R15** — carnet du lab | **ÉTAPE 2 / déjà couvert autrement** | Le rôle de "carnet" est déjà rempli par `Handoff.md`/`JOURNAL.md`/`STACK.md` dans le wiki (mécanisme documenté dans le CLAUDE.md racine du projet). Créer un carnet séparé ferait doublon. | Aucune action — usage existant du wiki à conserver. |
| **C1** — refuser Σn^{-s} si Re(s)≤1+ε, basculer η(s)/RS | **SANS OBJET** (garde-fou non applicable, confirmé) | `grep` récursif sur tout `src/calculs/optimisation/*.py` pour un motif de série de Dirichlet directe (`n**(-s)`, `dirichlet_series`, `sum(1/n**s)`) : **aucune occurrence**. Le pipeline n'utilise jamais Σn^{-s} : il passe systématiquement par Riemann-Siegel tronqué (scan_arb) et `acb_dirichlet_hardy_z` (Arb, formule de Hardy). | Garde-fou déclaré SANS OBJET pour le moteur actuel — ne rien coder. |
| **C2** — `stirling.py` : \|Γ(σ+it)\|≈√(2π)\|t\|^{σ−1/2}e^{−π\|t\|/2}, estimation a priori | **APPLICABLE (mineur) / partiellement couvert** | Aucun fichier `stirling.py` distinct, mais l'estimation asymptotique de θ(t) via Stirling est déjà présente et documentée comme telle dans le CLAUDE.md racine (formule θ(t) canonique, ordre 1/(48t) etc.), utilisée par `theta_rapide.py`/`theta_fast`. Ce qui manque : une fonction *a priori* de taille de |Γ| séparée, utilisable comme garde-fou avant calcul (pas juste dans θ). | Patch minimal, optionnel : petite fonction utilitaire (5-10 lignes) réutilisant l'asymptotique Stirling déjà validée, pour un contrôle de plausibilité en amont — pas un nouveau fichier `stirling.py` séparé, l'intégrer à `theta_rapide.py` existant. |
| **C3** — facteurs de complétion π^{−s/2}Γ(s/2), test ξ(s)=ξ(1−s) | **ÉTAPE 2** | Aucune implémentation de ξ(s) trouvée dans `src/calculs/optimisation/`. C'est un test de cohérence théorique global, pas un besoin du moteur de détection Z(t) qui ne calcule jamais ξ directement. | Hors périmètre étape 1 (rejoint A5/A2). |
| **C4** — séparation `series.py`/`functional_equation.py`/`stirling.py`/`diagnostics.py` | **OBSOLÈTE / non pertinent tel quel** | Aucun de ces 4 fichiers n'existe (recherche négative), et cette architecture en couches suppose un usage de Σn^{-s} (`series.py`) que le moteur n'a pas (cf. C1). Proposer cette séparation reviendrait à documenter un pipeline hypothétique, pas le pipeline Arb/RS réel. | Ne pas appliquer tel quel. Si un jour un module de garde-fou théorique (C2) est ajouté, le nommer/organiser selon les conventions déjà en vigueur dans `src/calculs/optimisation/` plutôt que recréer cette arborescence. |

**Synthèse chiffrée** (24 items au total : A1-A5, R1-R15, C1-C4) :
- DÉJÀ FAIT : 5 (A1, A4, R5, R8, une partie de R15)
- APPLICABLE : 2 (R4, C2)
- À RAFFINER : 3 (R1, R2, C… — voir R1/R2 ci-dessus)
- NE PAS TOUCHER : 2 (A3, R5 — R5 compté aussi en DÉJÀ FAIT car double statut légitime)
- OBSOLÈTE : 2 (R7, C4)
- ÉTAPE 2 / hors périmètre : 12 (A2, A5, R3, R6, R9-R14, C3)
- SANS OBJET : 1 (C1)

---

## Tâche 3 — Plan d'action minimal étape 1

### 1. R4 — Journal de calibration/paramètres par run
- **Coût estimé** : faible (< 1h). Ajout de champs à des fonctions déjà appelées avec toutes les valeurs nécessaires en mémoire.
- **Fichiers concernés** : `compute_zeros_v16.py` (fonctions `ecrire_log()` ligne 591, `sauvegarder_csv()` ligne 572, `_step_adaptatif()` ligne ~822 pour exposer `MARGE_SECURITE` au lieu de la garder locale) ; idem sur `compute_zeros_v15.py` si le rerun T=5M s'y fait.
- **Ce qui NE doit PAS changer** : la valeur elle-même de `MARGE_SECURITE` (rester à 10.0, valeur actuellement active et validée en solo sur 3 zones dont T≈4,86M — ne pas revenir à 3.0 sans nouvelle validation) ; ne pas toucher à `STEP=0.010`/loi GUE ; ne pas toucher au moteur Arb/FLINT.

### 2. R2 + R8 — Rerun T=5M avec Turing loggé + déficit par segment + rapport des 96
- **Coût estimé** : le rerun lui-même est une exécution longue (hors périmètre de CET audit lecture-seule) — à planifier séparément, avec `zeta_turbo_on/off` comme l'exige le CLAUDE.md. Le patch logiciel préalable (relier explicitement les segments en déficit du rescan aux 96 manquants historiques) : faible (quelques heures).
- **Fichiers concernés** : `compute_zeros_v16.py` (`rescan_segments_deficit()` ligne 372, `valider_turing`/`turing_validation.py`), ou `compute_zeros_v15.py` si hprzeta confirme vouloir rester sur v15 pour ce rerun spécifique (cohérence avec le plan déjà acté dans le prompt source).
- **Ce qui NE doit PAS changer** : ne pas re-designer le mécanisme de rescan par déficit, qui existe déjà et fonctionne (section `[7]` du log) ; ne pas introduire de test de Gram complet si le déficit par segment suffit à expliquer les 96.

### 3. R1 — Validation échantillonnée de l'équation fonctionnelle (branche Γ/θ)
- **Coût estimé** : faible à moyen (script autonome, quelques heures) — **explicitement pas une colonne CSV en masse** comme le demandait la reco brute (10M lignes serait un gaspillage de calcul pour une propriété automatique sur la droite critique).
- **Fichiers concernés** : nouveau petit script indépendant (ex. `src/calculs/optimisation/validation_echantillon_EF.py`), consommant un CSV de zéros déjà produit, dps=30, N points fixes (ex. 1 par décade en T + quelques centaines aléatoires).
- **Ce qui NE doit PAS changer** : ne pas ajouter de colonne au CSV principal produit par `sauvegarder_csv()` ; ne pas alourdir le run principal.

### 4. Garde-fou de cohérence \|N_trouvés − N(T)\| < seuil
- **Coût estimé** : très faible (< 30 min) — `N_attendu()` existe déjà (`turing_validation.py:75-93`), il suffit de comparer `len(zeros)` à `N_attendu(T_MAX)` en fin de run et déclencher une alerte (log + éventuellement code de sortie non-zéro) si l'écart dépasse un seuil à définir avec hprzeta.
- **Fichiers concernés** : `compute_zeros_v16.py`, section finale de `main()` (autour de la ligne 988, où `N_attendus (Weyl)` est déjà affiché mais sans seuil d'alerte).
- **Ce qui NE doit PAS changer** : ne pas remplacer la comparaison actuelle "affichage informatif" par un `raise` bloquant sans validation explicite de hprzeta sur le seuil — un run long ne doit pas s'auto-interrompre sur un garde-fou mal calibré.

---

## Tâche 5 — Audit complémentaire : `Recommandations_LAB_et_prompt.md` + `Formation_Zeta_HR_Riemann_Lab.pdf`

**Constat préalable.** Les deux fichiers demandés sont la même synthèse sous deux formes : `Recommandations_LAB_et_prompt.md` reproduit mot pour mot les tableaux A–F et le prompt à coller de la **Partie II/III** du PDF `Formation_Zeta_HR_Riemann_Lab.pdf`. La **Partie I** du PDF (Modules M1–M8) est un cours de fondations mathématiques (convergence de Dirichlet, formule d'Euler, η(s), prolongement analytique, facteurs Γ, résidus) : elle ne contient que deux affirmations reliées au pipeline réel, déjà vérifiées dans les Tâches 1–2 ci-dessus et simplement référencées ici :
- Module 4 : « Règle LAB gravée : utiliser Z(t)=e^{iθ(t)}·ζ(½+it) […] brique n°1 de compute_zeros » → confirmé, voir Tâche 1 (`compute_zeros_v16.py:63`, `:4-17`).
- Module 8 : exemples numériques N(100)≈28,13, N(1000)≈647,74, rappel « ne jamais oublier le e » → formule identique à `_n_zeros_expected()` (`compute_zeros_v16.py:89-93`) et `N_attendu()` (`turing_validation.py:75-92`), déjà confirmée Tâche 1. Non recalculé ici (hors périmètre lecture seule de vérifier une valeur numérique isolée, la formule est la preuve).

**⚠️ Divergence MARGE_SECURITE — 3e occurrence de la même valeur obsolète.** Les deux tableaux A du PDF et du `.md` affirment *« MARGE_SECURITE = 3.0 (calibration validée) »* et le reprennent tel quel dans le bloc « PROMPT prêt à coller ». C'est exactement l'affirmation déjà invalidée en Tâche 1 : la valeur **réellement active dans le code est 10.0** (`compute_zeros_v16.py:822`, `compute_zeros_v15.py:790`), 3.0 n'étant plus qu'un point de passage historique commenté (`:731`). Ces deux nouveaux documents datent du même jour (12/09/2026) que le prompt d'audit initial et propagent donc la même valeur figée avant la recalibration à 10.0 — **si le prompt « prêt à coller » de la Partie III est réutilisé tel quel dans une future session, il réintroduira la fausse croyance 3.0 dans le contexte de Claude Code.** Ceci renforce l'action 2 du bloc STOP ci-dessous.

### Bloc A — Mathématiques & calibration

| Règle | Statut | Preuve | Remarque |
|---|---|---|---|
| Z(t)=e^{iθ(t)}·ζ(½+it), jamais Re(ζ) | PROUVÉ PAR LE CODE | `compute_zeros_v16.py:63`, `:4-17` (déjà établi Tâche 1) | Cohérent avec Module 4 du PDF. |
| N(T)≈(T/2π)·ln(T/2πe), garder le `e` | PROUVÉ PAR LE CODE | `compute_zeros_v16.py:89-93` `_n_zeros_expected` ; `turing_validation.py:75-92` `N_attendu` (déjà établi Tâche 1) | Cohérent avec Module 8 du PDF. |
| STEP=0.010 FIXE | PROUVÉ PAR LE CODE (mais valeur non figée en dur — dérivée) | `compute_zeros_v16.py:822-826` : `STEP` est **calculé** par `_step_adaptatif(T)` = `KAPPA·gap_moyen·N_T^(-1/3)/MARGE_SECURITE`, pas une constante `0.010` littérale dans le code ; `0.010` apparaît en commentaire historique (`:717,753`) comme valeur type observée à un T donné, pas comme constante fixée. | Nuance à noter : la règle du LAB dit « STEP=0.010 FIXE », mais le code n'a pas de `STEP = 0.010` en dur — c'est le **résultat** de la formule adaptative pour la plage T considérée. Ne pas confondre « résultat stable observé » et « constante figée dans le code ». Ne rien changer : la formule adaptative est la source canonique. |
| MARGE_SECURITE=3.0 (calibration validée) | **DIVERGENCE DÉTECTÉE** (3e source obsolète) | `compute_zeros_v16.py:822` : valeur active = `10.0` ; `:731` : `3.0` restauré le 02/08/2026 puis dépassé (`git log -S`, voir Tâche 1) | Voir alerte en tête de section. À trancher avec hprzeta avant tout rerun ou réutilisation du prompt Partie III. |
| Validation = Turing-Backlund, PAS Weyl tronqué ; `_n_zeros_expected` omet Stirling+S(T) | PROUVÉ PAR LE CODE (séparation déjà respectée) | `_n_zeros_expected()` (`compute_zeros_v16.py:89-93`, formule Weyl pure) n'est utilisée **que** pour le partitionnement des workers (`:109-117`) et le calcul de déficit par segment (`:416`) — **jamais** pour la validation finale, qui passe par `valider_turing()`/`N_attendu()` (`:964`, `:865`, `:918`, basé sur `theta_fast`, plus précis que Weyl). | Le pipeline respecte déjà la distinction que la règle demande de préserver : usage interne (Weyl, approximatif, suffisant pour équilibrer des segments) vs validation externe (Turing-Backlund + θ, rigoureux). Rien à corriger. |
| `valider_turing()` atteinte ET loggée | PROUVÉ PAR LE CODE | `compute_zeros_v16.py:964`, section `[6]` du log (déjà établi Tâche 1) | RAS. |
| Déficit concentré en bas-t = artefact d'oversampling | NON VÉRIFIABLE ICI | Aucune trace de cette observation dans le code (c'est une conclusion d'investigation post-run, pas une règle de code) ; le wiki (`Riemann_Lab.wiki/Analyse-Deficit-Zeros-Grille-20260906.md`, présent mais non lu en détail — hors périmètre code) pourrait la documenter. | Observation empirique à confirmer par le rerun R2, pas par lecture statique du code. |

### Bloc B — Numérique & précision

| Règle | Statut | Preuve | Remarque |
|---|---|---|---|
| `to_csv()` immédiatement après le run, avant tout rescan | **PROUVÉ PAR LE CODE** | `compute_zeros_v16.py:933-937`, commentaire explicite : « CSV principal — livrable autonome, écrit AVANT le rescan » ; rescan lancé ensuite `:942-948` ; second CSV consolidé écrit après fusion (`:970`). | Respecté à la lettre — deux CSV distincts (brut avant rescan, consolidé après), pas un seul écrit tardivement. |
| FLINT 3.3.1 headers vendorés (apt = 3.0.1 incompatible) | PROUVÉ PAR LE CODE | `c_modules/Makefile:27-29` : « Headers FLINT 3.3.1 vendorisés en source (apt libflint-dev = 3.0.1, ABI incompatible…) », dossier `flint-headers-3.3.1` référencé. | RAS. |
| `.so` chargés POST-FORK | PROUVÉ PAR LE CODE | `compute_zeros_v16.py:147` : « Charge illinois_arb.so APRÈS le fork() → pas de corruption mémoire partagée » ; `:159-160` chargement `ctypes.CDLL` effectif après fork. | RAS. |
| `acb_dirichlet_hardy_z` 64-bit fixe ×2.75 vs adaptatif, identique bit-à-bit à T=100k | NON VÉRIFIABLE ICI | Le gain ×2,75 v16/v15 est confirmé par la mémoire projet et le prompt source (Tâche 1), mais aucun fichier du dépôt ne contient de comparatif bit-à-bit archivé entre les deux modes de précision à T=100k. | Plausible (cohérent avec l'en-tête `compute_zeros_v16.py:4-19` sur le choix délibéré de précision fixe) mais non prouvable par lecture statique — demanderait de rejouer le comparatif. |
| Seuil Illinois T_SEUIL=300 (C/libmpfr si t≥300, mpmath sinon) | **OBSOLÈTE pour le moteur actuel** | `T_SEUIL_ILLINOIS_C = 300.0` existe bien, mais uniquement dans les anciennes versions `compute_zeros_v4_1.py:89`, `v6.py:92`, `v7.py:94`, `v8.py:100`, `v9.py:103`, `v10.py:107` (ère Illinois/mpfr pré-Arb). À partir de v12 (`compute_zeros_v12.py:11,196,417`) et jusqu'à v16 (`compute_zeros_v16.py:265,623`), le commentaire dit explicitement « Seuil t=300 : SUPPRIMÉ — Arb calcule Z(t) sans biais RS pour tout t ≥ 14 ». | Le CLAUDE.md racine documente encore ce seuil comme règle canonique (`T_SEUIL_ILLINOIS_C = 300.0`) alors qu'il est **abandonné depuis v12** au profit d'Arb. Point de documentation à corriger dans le CLAUDE.md racine (hors périmètre de cet audit lecture seule — signalé, pas modifié). |
| `mp.dps` = 30–50 selon précision requise | PROUVÉ PAR LE CODE | `compute_zeros_v16.py:58` `mpmath.mp.dps = 35` (global) ; `:964` `valider_turing(zeros, dps=30)` ; `theta_rapide.py:159,189` `dps=50` (référence exacte) ; `validate_v4_1.py:185,232,251,355` `dps=50` (référence haute précision), `dps=30` (poli). | Plage 30–50 confirmée, usages différenciés par rôle (exploration vs référence), conforme à la règle. |

### Bloc C — Infrastructure & cluster (4 nœuds)

| Règle | Statut | Preuve | Remarque |
|---|---|---|---|
| Proton VPN OFF avant accès distant au cluster | NON VÉRIFIABLE ICI | Aucun script du dépôt ne pilote Proton VPN (config système hors dépôt). | Convention opérationnelle, pas de code à auditer. |
| wg0 DOWN à la maison / UP en déplacement | **PROUVÉ PAR LE CODE (scripté)** | `scripts/wg_auto.sh:2-3` (commentaire résumant la règle), `:31-32` (`wg-quick down wg0` si maison), `:46-61` (`wg-quick up wg0` + vérif handshake si déplacement). | Automatisé, pas seulement documenté — au-delà de la règle brute. |
| OpenBSD : wgpeer et wgaip sur la même ligne | NON VÉRIFIABLE ICI | La config `hostname.wg0` d'OpenBSD (PC4/zeta-secure) n'est pas dans ce dépôt Python. | Hors périmètre — config système distante. |
| `systemd-inhibit` autour des runs longs | **PROUVÉ PAR LE CODE** | `scripts/zeta_run.sh:38-40` : `systemd-inhibit --what=shutdown:sleep:idle --who="zeta_run.sh" --why="Run T=${T_MAX} en cours" --mode=block nohup bash -c "…compute_zeros_v16.py"`. | Déjà en place — directement actionnable/rassurant pour le futur rerun T=5M (action 4 du plan Tâche 3). |
| PC3 (Python 3.5.2) : `.format()` et non f-strings | NON VÉRIFIABLE ICI | Aucun code Python ciblant PC3 spécifiquement trouvé dans `src/calculs/optimisation/` (scripts cluster dans `scripts/` sont en bash ou visent PC1/PC4). | Rappel opérationnel à revérifier au prochain allumage de PC3, pas vérifiable statiquement sans ce code. |

### Bloc D — RAG / BrainVault (Objectif 2 — hors périmètre étape 1, vérification best-effort)

| Règle | Statut | Preuve | Remarque |
|---|---|---|---|
| Modèle d'embedding identique ingestion/requête (`all-MiniLM-L6-v2`) | PROUVÉ PAR LE CODE (côté requête) | `scripts/rag_query.py:10,48` : `MODELE_EMBEDDING = "all-MiniLM-L6-v2"`, commentaire « même modèle que l'ingestion — ne pas changer ». | Le script d'ingestion lui-même n'a pas été localisé/vérifié (hors scope de cette passe) — seule la moitié « requête » est prouvée ici. |
| Garde `mountpoint -q /mnt/vault_rag \|\| exit 1` | PROUVÉ PAR LE CODE (sous une forme légèrement différente) | `scripts/rag_query.py:77` : `subprocess` appelant `["mountpoint", "-q", str(VAULT_RAG)]` | Vérifie le montage mais via `subprocess.run` plutôt qu'un `|| exit 1` shell littéral — fonctionnellement équivalent. |
| `CUDA_VISIBLE_DEVICES=""` pour sentence-transformers | **NON IMPLÉMENTÉ DANS LE REPO** | Recherche `CUDA_VISIBLE_DEVICES` sur tout le dépôt (hors venv) : aucune occurrence. `rag_query.py:97-98` documente en commentaire le problème (« plante en CUDA sur l'embedding, incident 25/07/2026 ») mais ne fixe pas la variable d'environnement dans le script. | Écart réel entre règle documentée et code : si la garde est appliquée aujourd'hui, c'est manuellement (export shell avant lancement), pas de façon programmatique. Étape 2 (RAG), donc hors correctif étape 1, mais à signaler. |
| `k=8` défaut ChromaDB | PROUVÉ PAR LE CODE | `scripts/rag_query.py:228` : `parser.add_argument("--k", type=int, default=8, …)`, avec justification en commentaire (k=3/6 ratent un chunk clé). | RAS. |

### Bloc E — Git & documentation

| Règle | Statut | Preuve | Remarque |
|---|---|---|---|
| JAMAIS `git add -A` (protège Handoff.md) | **DIVERGENCE DÉTECTÉE (script historique)** | `scripts/push_phase0_complete.sh:36` contient littéralement `git add -A`, à la suite de plusieurs `git add <fichier>` ciblés. Script daté du 21/05/2026 (`git log`), correspond à la clôture de la Phase 0 (v3, T=10000) — antérieur à v16. | Script obsolète (Phase 0, jamais réutilisé depuis a priori) mais toujours présent dans le dépôt : risque si relancé par erreur. Pas de correctif appliqué (lecture seule) — à supprimer ou corriger si hprzeta confirme qu'il est mort. |
| Wiki : pages à la racine (pas de sous-dossier) | PROUVÉ | `ls ~/projet_zeta/Riemann_Lab.wiki/` : tous les `.md` constatés sont à la racine (`Handoff.md`, `JOURNAL.md`, `Analyse-Deficit-Zeros-Grille-20260906.md`, etc.), aucun sous-dossier listé. | RAS. |
| KaTeX `\text{}` pas `\operatorname{}` ; échapper `_`/`%` | COHÉRENT (documenté ailleurs) | Déjà une règle explicite du CLAUDE.md racine (§ Règles KaTeX) — non re-vérifiée fichier par fichier ici (hors scope, ce serait un audit de contenu wiki, pas de code). | Cohérence de règle confirmée entre les 3 documents (CLAUDE.md, recommandations, PDF) — pas de contradiction. |
| Secrets : `git filter-repo` (le `.gitignore` ne purge pas l'historique) | COHÉRENT (déjà vécu) | Mémoire projet : token DuckDNS trouvé exposé en clair et redigé le 22/08/2026 (commit `7ebf94c`), **historique git non purgé** (décision hprzeta documentée). | La règle est connue et un cas réel existe où elle n'a délibérément pas été appliquée (choix assumé, pas un oubli) — à ne pas re-signaler comme un manquement. |
| `rclone copy` (pas `sync`) vers Proton Drive | PROUVÉ PAR LE CODE | `scripts/backup_cluster_map.sh:69` : `/usr/bin/rclone copy ~/backup/` ; `scripts/zeta_backup_status.py:8` : « rclone copy ~/backup/ → protondrive:… ». | RAS — aucune occurrence de `rclone sync` trouvée. |
| En-tête/pied (date + auteur) sur chaque `.md`/`.pdf` | COHÉRENT (déjà observé) | Les deux fichiers audités ici respectent eux-mêmes la règle (pied de page « Auteur : hprzeta — Mis à jour le 12 septembre 2026 … page N » sur le PDF ; pied « 131 lignes » sur le `.md`). | Auto-cohérent, rien à vérifier côté code. |

### Bloc F — Workflow Claude.ai ↔ Claude Code

| Règle | Statut | Preuve | Remarque |
|---|---|---|---|
| Claude.ai = stratégie/maths/prompts, Claude Code = implémentation/fichiers/git | NON VÉRIFIABLE ICI | Convention de collaboration humain-IA, aucun artefact code à confronter. | Cohérente avec le CLAUDE.md racine (séparation des rôles déjà en vigueur). |
| Réponses techniques Partie 1 (code) puis Partie 2 (maths) | NON VÉRIFIABLE ICI | Idem — convention de style de réponse. | — |
| Lancer `claude` depuis `~/projet_zeta/`, jamais `~/` ; `/clear` si tokens non-cachés > ~50k | NON VÉRIFIABLE ICI | Convention de session, pas de trace attendue dans le code. | — |

---

## STOP — en attente de validation

Audit terminé (Tâches 1–5), **aucune modification n'a été apportée au dépôt** hormis ce rapport. Rapport écrit uniquement à `rapports/audit_reco_IA_2026-09-12.md`, non commité.

Actions proposées, à valider individuellement par hprzeta avant tout lancement :

1. **Implémenter R4** (journal de calibration complet, notamment exposer `MARGE_SECURITE` dans le log/CSV) — correctif de fond le moins coûteux et le plus directement lié à l'incident des 96 manquants.
2. **Trancher définitivement la divergence MARGE_SECURITE (3.0 vs 10.0)** — découverte dans le prompt d'audit initial et **confirmée à l'identique dans les deux nouveaux documents audités** (`Recommandations_LAB_et_prompt.md` et le PDF de formation), y compris dans le bloc « prompt prêt à coller pour Claude Code » qui la réinjecterait dans une future session si réutilisé tel quel. Décider quelle valeur sert de référence avant le rerun T=5M, et corriger la documentation (CLAUDE.md racine + ces deux fichiers) en conséquence.
3. **Écrire le script de validation échantillonnée R1** (équation fonctionnelle, branche Γ/θ, dps=30, N points — pas de colonne CSV massive).
4. **Planifier séparément** (hors de cet audit, run long) le rerun T=5M avec Turing complet + rapport des 96 manquants (R2+R8), sur v15 ou v16 selon ce que confirme hprzeta — `systemd-inhibit` déjà en place (`scripts/zeta_run.sh:38-40`), rien à ajouter sur ce point.
5. **Nettoyer la documentation obsolète** repérée pendant cette extension d'audit (à confirmer, aucun fichier modifié) : `T_SEUIL_ILLINOIS_C=300` toujours documenté dans le CLAUDE.md racine alors que supprimé depuis v12 (Arb sans biais RS dès t≥14) ; `scripts/push_phase0_complete.sh` contient encore un `git add -A` (script mort de la Phase 0, mai 2026) qui viole la règle « JAMAIS git add -A ».
