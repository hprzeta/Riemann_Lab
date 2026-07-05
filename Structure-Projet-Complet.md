> **Fichier :** Structure-Projet-Complet.md · **Dossier :** wiki (racine)
> **Branche :** master (wiki) · **Auteur :** hprzeta · **MAJ :** 2026-06-13

# 🗂️ Structure Complète du Projet — Riemann_Lab

> Version wiki enrichie — reprend le README.md depuis "Structure générale projet"
> jusqu'à "Fichiers générés", enrichie de rôles détaillés et de liens wiki.

---

## 1. Les 6 lieux du projet

Avant l'arbre, comprendre la géographie complète (voir [[ORGANISATION_FICHIERS]]) :

| # | Lieu | Versionné | Description |
|---|------|-----------|-------------|
| 1 | **Local** `~/projet_zeta/` | ❌ | Logs, Handoff, brouillons — état volatil |
| 2 | **Repo principal** `hprzeta/Riemann_Lab` | ✅ | Code, site, config, skills |
| 3 | **Wiki** `Riemann_Lab.wiki` (master) | ✅ | Documentation lisible, cours, JOURNAL |
| 4 | **Skills Claude Code** `~/.claude/skills/` | ✅ via repo | Skills exécutés en terminal |
| 5 | **Skill Claude.ai** `/mnt/skills/user/riemann-lab/` | géré à part | Skill web read-only |
| 6 | **Fichiers projet Claude.ai** | ❌ snapshot | Copie cherchable — pas source de vérité |

---

## 2. Structure générale du projet

```
~/projet_zeta/
│
├── zeta_env/                            # Environnement virtuel Python (gitignorée)
│
├── src/                                 # Code source principal
│   ├── calculs/                         # Algorithmes ζ(s) — recherche des zéros
│   │   ├── optimisation/
│   │   │   ├── c_modules/
│   │   │   │   ├── illinois_mpfr.c      # ⭐ Illinois C/libmpfr PREC=170
│   │   │   │   ├── illinois_mpfr.h
│   │   │   │   ├── illinois_mpfr.so     # .so compilé (chargé post-fork)
│   │   │   │   ├── z_function.c         # Z(t) en C
│   │   │   │   ├── Makefile
│   │   │   │   └── CLAUDE.md            # règles C/libmpfr pour Claude Code
│   │   │   ├── arb_wrapper.py           # Arb/FLINT ×27 vs mpmath.siegelz
│   │   │   ├── compute_zeros_v2.py      # référence v2 — NE PAS MODIFIER
│   │   │   ├── compute_zeros_v3.py      # Phase 0 orchestrateur
│   │   │   ├── compute_zeros_v4.py      # Phase C hybride — NE PAS MODIFIER
│   │   │   ├── compute_zeros_v4_1.py    # ⭐ ACTIF (STEP adaptatif + Arb + Illinois C)
│   │   │   ├── compute_zeros_v5.py      # Voie B pure — NE PAS MODIFIER
│   │   │   ├── parallel_scanner.py      # segmentation + multiprocessing
│   │   │   ├── riemann_siegel_batch.py  # Z(t) vectorisé numpy
│   │   │   └── turing_validation.py     # Turing-Backlund post-calcul
│   │   └── demo_complete.py             # Démonstration complète
│   ├── ia/                              # Modèles IA locaux (Objectif 2)
│   ├── visualisation/                   # Graphiques statiques et interactifs
│   ├── monitoring/                      # Logs, CPU/RAM/GPU, benchmarking
│   ├── utils/                           # Configuration, I/O, décorateurs
│   └── tests/
│       └── cours/                       # Scripts pédagogiques n0–n5
│
├── scripts/
│   ├── zeta_turbo_on.sh                 # ⭐ OBLIGATOIRE avant tout run
│   ├── zeta_turbo_off.sh                # Restaure CPU governor + swappiness
│   ├── zeta_run.sh                      # Run standard enchaîné
│   ├── capture.sh                       # Log sessions Claude Code → .md
│   ├── install_zeta_complete.sh         # Installation auto étapes 1–10
│   └── setup_ollama_final.sh            # Installation Ollama + modèles
│
├── calculs/                             # Résultats de runs (CSV, logs)
│   ├── v4_1_T100000_20260610_105148/    # Run T=100k v2 (138 039 zéros · 68 manquants)
│   └── v4_1_T10000_20260610_103409/     # Run T=10k v2 (10 141 zéros ✅ Turing complet)
│
├── config/
│   └── zeros_config.yaml                # Paramètres T, STEP, workers, PREC
│
├── docs/                                # GitHub Pages (branche Riemann_Lab_IA)
│   ├── images/
│   │   ├── header_riemann_lab.svg       # ⭐ Logo animé (wiki + GitHub Pages)
│   │   └── logo_riemann_lab.png
│   ├── animation_theta.html             # θ(t), Z(t), Backlund — 3 vues
│   ├── animation_distribution_zeros.html
│   ├── animation_gamma.html
│   ├── animation_mur_latence.html
│   ├── animation_plan_complexe.html
│   ├── animation_produit_eulerien.html
│   ├── animation_series_dirichlet.html
│   ├── animation_zeros_non_triviaux.html
│   └── index.html                       # ⭐ Page principale GitHub Pages
│
├── handoff/                             # hors git (local uniquement)
│   └── Handoff.md                       # ⭐ État courant session ("REPRENDRE ICI")
│
├── pdf/
│   ├── cours/                           # PDF niveaux 0–5 + Bibliothèques + Formules
│   └── optimisation/                    # Rapports d'analyse des versions
│
├── Riemann_Lab.wiki/                    # Wiki (dépôt séparé — master)
│
├── .claude/
│   └── skills/                          # Skills versionnés (5 skills actifs)
│
├── CLAUDE.md                            # ⭐ Règles permanentes (4 branches sync)
├── CONTRIBUTING.md
└── README.md
```

Et sur `/mnt/data/` (données volumineuses, hors git) :

```
/mnt/data/
├── datasets/calculs/                    # Fichiers d'entrée
├── exports/csv/                         # Résultats CSV
├── exports/figures/                     # Graphiques PNG/HTML
├── logs/                                # Journaux d'exécution
└── models_ia/ollama/                    # Modèles LLM locaux
    ├── mathstral                        # Spécialisé maths
    ├── deepseek-coder:6.7b
    └── phi3:mini
```

---

## 3. Organisation du code source (`src/`)

| Module | Rôle | Wiki associé |
|--------|------|-------------|
| `src/calculs/` | Algorithmes sur ζ(s), recherche des zéros | [[Etape-1-Calcul-des-zéros-non-triviaux]] |
| `src/calculs/optimisation/` | Pipeline v4.1 — Arb + Illinois C | [[Phase-C-compute_zeros_v4]] |
| `src/calculs/optimisation/c_modules/` | Illinois C/libmpfr PREC=170 | [[Bibliotheques]] |
| `src/visualisation/` | Graphiques statiques et interactifs | [[Étape-2-Visualisations-avancées]] |
| `src/ia/` | Interface Ollama, génération conjectures | [[Étape-3-Intelligence-artificielle]] |
| `src/monitoring/` | Logs, CPU/RAM/GPU, benchmarking | [[STACK]] |
| `src/utils/` | Configuration, I/O fichiers, décorateurs | — |
| `src/tests/cours/` | Scripts pédagogiques niveaux 0–5 | [[Parcours-complet]] |

---

## 4. Rôle des fichiers clés

### Scripts de calcul

| Fichier | Statut | Rôle |
|---------|--------|------|
| `compute_zeros_v4_1.py` | ⭐ ACTIF | Pipeline principal — Z vectorisé + Arb + Illinois C |
| `arb_wrapper.py` | ⭐ actif | Interface Python → `arb_fpwrap_cdouble_hardy_z` (×27) |
| `illinois_mpfr.c` + `.so` | ⭐ actif | Raffinement C/libmpfr PREC=170 (chargé post-fork) |
| `turing_validation.py` | actif | Validation Turing-Backlund N(T) |
| `parallel_scanner.py` | actif | Segmentation $1/\sqrt{t}$ + multiprocessing 4 workers |
| `compute_zeros_v2.py` | archivé | Référence v2 — NE PAS MODIFIER |

### Scripts système

| Script | Rôle | Quand |
|--------|------|-------|
| `zeta_turbo_on.sh` | Arrête 7 services · CPU perf · swappiness=10 | **Avant tout run** |
| `zeta_turbo_off.sh` | Restaure l'état normal | **Après tout run** |
| `zeta_run.sh` | Enchaîne turbo_on → calcul → turbo_off | Run standard |

### Fichiers de configuration

| Fichier | Rôle |
|---------|------|
| `CLAUDE.md` (racine) | Règles permanentes Claude Code — sync 4 branches |
| `zeros_config.yaml` | Paramètres T, STEP, workers, PREC |
| `.mcp.json` | ⚠️ Secret — JAMAIS committer (gitignorée) |

---

## 5. Fichiers générés (non versionnés)

| Type | Chemin | Description |
|------|--------|-------------|
| CSV résultats | `/mnt/data/exports/csv/resultats_zeta.csv` | Zéros calculés par run |
| CSV runs | `~/projet_zeta/calculs/v*/zeros_*.csv` | Résultats détaillés par version |
| LOG exécution | `/mnt/data/logs/demo_zeta.log` | Journal d'exécution |
| LOG runs | `~/projet_zeta/logs/run_T*.log` | Logs de run (gitignorés) |
| PNG graphiques | `/mnt/data/exports/figures/*.png` | Visualisations matplotlib |
| HTML interactif | `/mnt/data/exports/figures/*.html` | Visualisations plotly |
| `Handoff.md` | `~/projet_zeta/handoff/` | État courant session (local) |
| `*.pyc`, `__pycache__/` | partout | Bytecode Python (gitignorés) |
| `zeta_env/` | `~/projet_zeta/` | Venv Python 3.12 (gitignorée) |

---

## 6. Branches du dépôt principal

| Branche | Rôle | Contenu principal |
|---------|------|------------------|
| `Riemann_Lab_IA` ⭐ | Développement principal | `src/`, `docs/`, `.claude/skills/` |
| `Riemann_Lab_C` | Optimisation C | `src/optimisation/c_modules/` |
| `Riemann_Lab_Test` | Expérimentations | Tests, CodeSpaces |
| `main` | Production stable | Merge depuis IA |
| `inbox-ia` (orpheline) | Ingestion documents | Docs pour lecture par Claude |
| `session` (orpheline) | Handoff versionné | `Handoff.md` uniquement |

---

## 7. Structure du wiki (`Riemann_Lab.wiki/`)

Le wiki est un **dépôt séparé** (`master`). Toutes les pages sont à la racine.

| Catégorie | Pages principales |
|-----------|------------------|
| Navigation | [[Home]], [[ORGANISATION_FICHIERS]], [[STACK]], [[JOURNAL]] |
| Maths | [[Formules_zeta]], [[Bibliotheques]], [[Tableau-Symboles-Mathématiques]] |
| Cours | [[niveau-0-prerequis]] → [[niveau-5-expert]], [[Parcours-complet]] |
| Résultats | [[Etape-1-Calcul-des-zéros-non-triviaux]], [[Rapport_validation_T10000]] |
| Hardware | [[Plancher-Hardware-Architecture]], [[Optimisation-Pourquoi-le-calcul-va-vite]] |
| Guides | [[Guide-Git-GitHub]], [[Guide-VSCode-Bonnes-Pratiques]], [[Bonnes-Pratiques-Claude-Code]] |

---

## Voir aussi

- [[ORGANISATION_FICHIERS]] — règles "où va quoi"
- [[Plancher-Hardware-Architecture]] — limites hardware et projections v1→v12
- [[STACK]] — roadmap, outils, matériel
- [[Arbre_dossiers_projet]] — arbre condensé (version courte)

---

*Structure-Projet-Complet.md · wiki racine · branche master · hprzeta · MAJ 2026-06-13 · 170 lignes*
