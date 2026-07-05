# Arbre des dossiers — Riemann_Lab
> Structure du dépôt `~/projet_zeta/` — mise à jour : **10 juin 2026**

```
/home/riemann/projet_zeta
├── .claude/
│   ├── settings.local.json
│   └── skills/
│       ├── phase-c-illinois/           ← skill Phase C (libmpfr, Illinois C)
│       ├── riemann-code-review/        ← skill revue de code Python/C
│       ├── riemann-lab/                ← skill principal (KaTeX, wiki, Python, Git)
│       └── riemann-security-review/    ← skill audit sécurité
│
├── calculs/                            ← résultats de runs (csv, png, log)
│   ├── v4_1_T100000_20260610_073115/   ← run T=100k v1 (137 904 zéros)
│   ├── v4_1_T100000_20260610_105148/   ← run T=100k v2 (138 039 zéros)
│   ├── v4_1_T10000_20260610_100617/    ← test T=10k v1 (10 137 zéros)
│   ├── v4_1_T10000_20260610_103409/    ← test T=10k v2 (10 141 zéros ✅)
│   ├── v4_1_T1000_20260602_163940/
│   ├── v4_1_T1000_20260606_185648/
│   ├── v4_1_T300_20260602_162919/
│   └── v5_T650_*/                      (anciens runs v5 prototypage)
│
├── claude-traitement-journalier/       ← hors git (.gitignore)
│   └── session_YYYYMMDD_HHMM.{log,md} ← logs sessions Claude Code
│
├── config/
│   └── zeros_config.yaml
│
├── csv/                                ← anciens CSV (pré-v4)
│   ├── T1000_V1/
│   └── T1000_V2/
│
├── docs/                               ← GitHub Pages (branch Riemann_Lab_IA)
│   ├── archive/
│   │   ├── csv_anciens/
│   │   ├── python_obsoletes/
│   │   └── scripts_shell/
│   ├── csv/
│   │   ├── T1000_V1/
│   │   └── T1000_V2/
│   ├── images/
│   │   ├── header_riemann_lab.svg      ← logo animé (GitHub Pages / wiki)
│   │   ├── logo_riemann_lab.png        ← logo PNG statique (README)
│   │   ├── logo_riemann_lab.svg
│   │   ├── T1000_V2/
│   │   └── T10Demo/
│   ├── logs/
│   │   └── T1000_V2/
│   ├── animation_distribution_zeros.html
│   ├── animation_gamma.html
│   ├── animation_mur_latence.html
│   ├── animation_plan_complexe.html
│   ├── animation_produit_eulerien.html
│   ├── animation_series_dirichlet.html
│   ├── animation_theta.html
│   ├── animation_zeros_non_triviaux.html
│   └── index.html                      ← GitHub Pages principal
│
├── handoff/                            ← hors git (local uniquement)
│   └── Handoff.md                      ← état courant ("REPRENDRE ICI")
│
├── logs/
│   ├── archive/
│   │   └── run_T100000_20260610_073009.log
│   ├── benchmark_arb_latest.log
│   ├── benchmark_arb_vs_mpmath_20260609_202356.log
│   ├── run_T100000_20260610_073106.log
│   ├── run_T100000_v2_20260610_105132.log
│   ├── run_T10000_test_20260610_100553.log
│   ├── run_T10000_v2_20260610_103348.log
│   ├── T1000_V1/
│   └── T1000_V2/
│
├── pdf/
│   ├── cours/
│   │   ├── niveau-0-prerequis.pdf … niveau-5-expert.pdf
│   │   ├── Bibliotheques.pdf
│   │   └── Formules_zeta.pdf
│   └── optimisation/
│       ├── analyse_problemes_v2_v3_phase0.pdf
│       ├── analyse_problemes_v3_v4.pdf
│       └── Riemann_Lab_Optimisation.pdf
│
├── requirements/
│   ├── requirements_workspace.txt
│   ├── requirements_zeta_global.txt
│   ├── requirements_zeta_ia.txt
│   └── requirements_zeta_system.txt
│
├── Riemann_Lab.wiki/                   ← wiki (dépôt séparé — master)
│   └── [voir wiki GitHub — Handoff, JOURNAL, STACK, Étape-1…]
│
├── scripts/
│   ├── ia_prompts/
│   │   └── ia_prompts_riemann_lab_complet.md
│   ├── zeta_run.sh                     ← run standard (turbo_on → calcul → turbo_off)
│   ├── zeta_turbo_off.sh               ← restaure CPU governor + swappiness
│   ├── zeta_turbo_on.sh                ← mode perf. (+15–30 % calcul)
│   ├── capture.sh                      ← log sessions Claude Code → .md
│   ├── build_pdf_riemann.sh
│   ├── gen_arbre.sh
│   └── [autres scripts utilitaires]
│
├── src/
│   ├── benchmark/
│   │   └── affinage_arb.py             ← benchmark Arb ×27 (2026-06-09)
│   ├── calculs/
│   │   ├── optimisation/
│   │   │   ├── c_modules/
│   │   │   │   ├── illinois_mpfr.c     ← affinage Illinois C/libmpfr PREC=170
│   │   │   │   ├── illinois_mpfr.h
│   │   │   │   ├── illinois_mpfr.so    ← .so compilé (post-fork, ctypes)
│   │   │   │   ├── z_function.c
│   │   │   │   ├── z_function.h
│   │   │   │   ├── Makefile
│   │   │   │   ├── CLAUDE.md           ← règles C/libmpfr
│   │   │   │   └── test_illinois.py
│   │   │   ├── arb_wrapper.py          ← Arb/FLINT ×27 vs mpmath
│   │   │   ├── compute_zeros_v2.py     ← référence (21h) — NE PAS MODIFIER
│   │   │   ├── compute_zeros_v3.py     ← orchestrateur Phase 0
│   │   │   ├── compute_zeros_v4.py     ← Phase C hybride — NE PAS MODIFIER
│   │   │   ├── compute_zeros_v4_1.py   ← ACTIF (STEP adaptatif + Arb + Illinois C)
│   │   │   ├── compute_zeros_v5.py     ← Voie B pure — NE PAS MODIFIER
│   │   │   ├── parallel_scanner.py
│   │   │   ├── riemann_siegel_batch.py ← Z(t) vectorisé numpy + GPU fallback
│   │   │   ├── riemann_siegel.py       (no batch_version/)
│   │   │   ├── theta_rapide.py
│   │   │   ├── turing_validation.py
│   │   │   └── CLAUDE.md               ← règles Illinois, ctypes, précision
│   │   └── calcul_zeta.py, compute_zeros_v1.py…
│   ├── ia/
│   │   └── prompts/
│   ├── monitoring/
│   │   └── logger_config1.py
│   ├── tests/
│   │   ├── archive/
│   │   └── cours/                      ← scripts pédagogiques n0–n5
│   └── utils/
│
├── zeta_env/                           ← venv Python 3.12 (ne pas committer)
│
├── CLAUDE.md                           ← règles permanentes projet ⭐
├── CONTRIBUTING.md
└── README.md
```

## Notes

| Symbole | Signification |
|---|---|
| `←` | Nouveau depuis mai/juin 2026 ou remarque importante |
| `⭐` | Fichier clé à lire en priorité |
| hors git | Présent sur Linux mais ignoré par `.gitignore` |

## Fichiers hors git (.gitignore)

| Fichier | Raison |
|---|---|
| `zeta_env/` | venv — trop lourd |
| `claude-traitement-journalier/` | logs sessions (personnel) |
| `handoff/` | état courant (local) |
| `.mcp.json` | tokens secrets |
| `__pycache__/` | bytecode Python |
| `*.pyc` | bytecode compilé |

---
*Arbre_dossiers_projet.md · wiki master · hprzeta · MAJ 10 juin 2026*
