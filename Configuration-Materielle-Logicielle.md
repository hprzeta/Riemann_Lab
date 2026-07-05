> **Fichier :** Configuration-Materielle-Logicielle.md · **Dossier :** wiki (racine)
> **Branche :** master (wiki) · **Auteur :** hprzeta · **MAJ :** 2026-06-13

# 💡 Configuration Matérielle & Logicielle — Riemann_Lab

> Référence complète du matériel, de la structure projet et des fichiers générés.
> Source : README.md (branche `Riemann_Lab_IA`) — version wiki enrichie.

---

## 1. Matériel (hardware)

Le projet tourne sur **Ubuntu 24.04.4 LTS** — configuration matérielle ultra-légère :

| Composant | Détails réels | État |
|-----------|--------------|------|
| Disque 1 To | 3 partitions ≈ 908 Go | ✅ OK |
| RAM 8 Go | 7,6 Gi (soit 8 Go) | ✅ OK |
| GPU GTX 960M | nvidia-smi (4 Go VRAM) | ✅ OK |
| Intel Core i7 | i7-7500U (2,7–3,5 GHz) | ✅ OK |

> Pour l'analyse détaillée des limites de ce matériel sur le calcul des zéros,
> voir [[Plancher-Hardware-Architecture]].

---

## 2. Structure générale du projet

```
/home/riemann/
├── projet_zeta/                         # Dossier principal
│   ├── zeta_env/                        # Environnement virtuel Python
│   ├── src/                             # Code source
│   │   ├── calculs/                     # Calculs sur la fonction zêta
│   │   │   └── demo_complete.py         # Démonstration complète
│   │   ├── ia/                          # Modèles d'IA locaux
│   │   ├── utils/                       # Utilitaires
│   │   ├── visualisation/               # Graphiques
│   │   ├── monitoring/                  # Logs systèmes
│   │   └── tests/                       # Tests unitaires
│   ├── scripts/                         # Scripts exécutables
│   ├── notebooks/                       # Jupyter notebooks
│   ├── lean_projects/                   # Projets Lean 4
│   ├── config/                          # Fichiers de configuration
│   ├── docs/                            # GitHub Pages (animations + index.html)
│   └── .vscode/                         # Configuration VS Code
└── /mnt/data/                           # Données volumineuses (hors git)
    ├── datasets/calculs/                # Fichiers d'entrée
    ├── exports/csv/                     # Résultats CSV
    ├── exports/figures/                 # Graphiques PNG/HTML
    ├── models_ia/ollama/                # Modèles LLM locaux
    └── logs/                            # Journaux d'exécution
```

> Pour la structure enrichie avec rôles détaillés et liens wiki,
> voir [[Structure-Projet-Complet]].

---

## 3. Organisation du code source (`src/`)

| Module | Rôle |
|--------|------|
| `src/calculs/` | Algorithmes sur ζ(s), recherche des zéros |
| `src/visualisation/` | Graphiques statiques et interactifs |
| `src/ia/` | Interface Ollama, génération de conjectures |
| `src/monitoring/` | Logs, CPU/RAM/GPU, benchmarking |
| `src/utils/` | Configuration, I/O fichiers, décorateurs |
| `src/tests/` | Tests unitaires |

Exécution : `python -m src.main` ou `./scripts/run_computation.sh`

---

## 4. Fichiers générés dans `/mnt/data`

| Type | Chemin | Description |
|------|--------|-------------|
| CSV | `/mnt/data/exports/csv/resultats_zeta.csv` | Zéros calculés |
| LOG | `/mnt/data/logs/demo_zeta.log` | Journal d'exécution |
| PNG | `/mnt/data/exports/figures/visualisation_matplotlib.png` | Graphique statique |
| HTML | `/mnt/data/exports/figures/visualisation_plotly.html` | Graphique interactif |

---

## 5. Logiciels et bibliothèques

| Catégorie | Outils | Priorité |
|-----------|--------|----------|
| Calcul haute précision | mpmath, Arb/FLINT, libmpfr, libgmp | 🔴 Haute |
| Calcul vectoriel | numpy, scipy | 🔴 Haute |
| Visualisation | matplotlib, plotly | 🔴 Haute |
| Gestion données | pandas, pyarrow | 🟡 Moyenne |
| Parallélisation | multiprocessing (4 workers) | 🟡 Moyenne |
| IA locale (LLM) | Ollama — mathstral, deepseek-coder:6.7b, phi3 | 🟡 Moyenne |
| Preuves formelles | Lean 4 | 🟢 Optionnelle |

> Pour la référence complète des bibliothèques avec versions et installation,
> voir [[Bibliotheques]].

---

## 6. Scripts d'installation

| Script | Étapes couvertes | Usage |
|--------|-----------------|-------|
| `install_zeta_complete.sh` | 1–10 (base + Python + libs) | `./scripts/install_zeta_complete.sh` |
| `setup_ollama_final.sh` | 11 (Ollama + modèles IA) | `./scripts/setup_ollama_final.sh` |

---

## Voir aussi

- [[Plancher-Hardware-Architecture]] — limites hardware, mur de latence, tableau v1→v12
- [[Structure-Projet-Complet]] — arbre enrichi avec rôles et liens wiki
- [[Bibliotheques]] — bibliothèques détaillées (versions, install, benchmarks)
- [[STACK]] — roadmap, outils, matériel, formation

---

*Configuration-Materielle-Logicielle.md · wiki racine · branche master · hprzeta · MAJ 2026-06-13 · 95 lignes*
