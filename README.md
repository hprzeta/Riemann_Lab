# 📐 Projet Zêta : Exploration de l'Hypothèse de Riemann

> *"Les zéros non triviaux de la fonction zêta de Riemann ont tous une partie réelle égale à 1/2."*  
> — Bernhard Riemann (1859)

## 🎯 Objectif du projet

Ce projet a pour but d'explorer numériquement et symboliquement la **fonction zêta de Riemann** ζ(s), pierre angulaire de la théorie des nombres. L'**Hypothèse de Riemann** (non démontrée à ce jour) affirme que tous les zéros non triviaux de ζ(s) se trouvent sur la droite critique **Re(s) = 1/2**.

Ce projet combine :
- Calculs haute précision
- Visualisations 2D/3D
- Intelligence artificielle locale (LLM)
- Preuves formelles (Lean 4)

## 📁 Structure du projet

```text
/home/riemann/
├── projet_zeta/                         # Dossier principal
│   ├── zeta_env/                        # Environnement virtuel Python
│   ├── src/                             # Code source
│   │   ├── calculs/                     # Calculs sur la fonction zêta
│   │   │   └── demo_complete.py         # Démonstration complète
│   │   ├── ia/                          # Modèles d'IA locaux
│   │   ├── utils/                       # Utilitaires
│   │   └── tests/                       # Tests unitaires
│   ├── scripts/                         # Scripts exécutables
│   ├── notebooks/                       # Jupyter notebooks
│   ├── lean_projects/                   # Projets Lean 4
│   ├── config/                          # Fichiers de configuration
│   ├── docs/                            # Documentation locale
│   └── .vscode/                         # Configuration VS Code
└── /mnt/data/                           # Données volumineuses
    ├── datasets/calculs/                # Fichiers d'entrée
    ├── exports/csv/                     # Résultats CSV
    ├── exports/figures/                 # Graphiques PNG/HTML
    └── logs/                            # Journaux d'exécution


# 📐 Projet Zêta : Exploration de l'Hypothèse de Riemann

## 🛠️ Outils et bibliothèques

 --------------------------------------------------------------------------
| Catégorie              | Outils                         | Priorité       |
|------------------------|--------------------------------|----------------|
| Calcul haute précision | mpmath, sympy, Pari/GP         | 🔴 Haute       |
| Calcul vectoriel       | numpy, scipy                   | 🔴 Haute       |
| Visualisation          | matplotlib, plotly, seaborn    | 🔴 Haute       |
| Gestion données        | pandas, pyarrow                | 🟡 Moyenne     |
| Logging/Monitoring     | loguru, tqdm, memory_profiler  | 🟡 Moyenne     |
| Parallélisation        | joblib, dask, ray              | 🟡 Moyenne     |
| IA complémentaire      | transformers, torch            | 🟢 Optionnelle |
| Preuves formelles      | Lean 4                         | 🟢 Optionnelle |
| Environnement complet  |  SageMath                      | 🟢 Optionnelle |
 ---------------------------------------------------------------------------

## 🚀 Alias de configuration (`.bashrc`)

 ----------------------------------------------------------------------------------------
| Alias        | Commande                                                  | Usage       |
|--------------|-----------------------------------------------------------|-------------|
| zeta         | cd ~/projet_zeta && source zeta_env/bin/activate          | Activer ENv |
| zeta-jupyter | cd ~/projet_zeta/notebooks && | Jupyter Lab               |             |
|              | source ~/projet_zeta/zeta_env/bin/activate && jupyter lab | Jupyter     |
| zeta-spyder  | source ~/projet_zeta/zeta_env/bin/activate &&             | Spyder      |
|              | export QT_API=pyqt5 && spyder                             | Jupyter     |
| zeta-code    | code ~/projet_zeta                                        | VS Code     |
| zeta-data    | cd /mnt/data                                              | Données     |
| `eta-logs    | tail -f /mnt/data/logs/demo_zea.log                       | Logs        |
 ----------------------------------------------------------------------------------------
 
## 🧪 Exécution

```bash
# Activer l'environnement
zeta

# Lancer le script
cd ~/projet_zeta/src/calculs
python demo_complete.py


## 📊 Résultats des tests

============================================================
SORTIE LOG DE TRAITEMENT
============================================================

2026-04-07 23:09:28.610 | INFO  | === Démarrage de la démonstration ===
2026-04-07 23:09:28.650 | INFO  | Précision mpmath configurée à 50 décimales
2026-04-07 23:09:29.273 | INFO  | Lecture : /mnt/data/datasets/calculs/nombres_a_tester.txt
2026-04-07 23:09:29.274 | INFO  | Lu 10 nombres
2026-04-07 23:09:29.311 | INFO  | Traitement séquentiel terminé en 0.0376s
2026-04-07 23:09:29.312 | INFO  | Temps total : 0.7023s

============================================================
RÉSULTATS DES CALCULS
============================================================
ζ(2.0) = 1.6449340668482264364724151666460251892189499012068
ζ(3.0) = 1.2020569031595942853997381615114499907649862923405
ζ(0.5) = -1.4603545088095868128894991525152980124672293310126

## 🔧 Fichiers générés

 ---------------------------------------------------------------
| Type | Chemin                                                 | 
|------|--------------------------------------------------------|
| CSV  | /mnt/data/exports/csv/resultats_zeta.csv               |
| LOG  | /mnt/data/logs/demo_zeta.log                           |
| PNG  | /mnt/data/exports/figures/visualisation_matplotlib.png |
| HTML | /mnt/data/exports/figures/visualisation_plotly.html    |
 ---------------------------------------------------------------
 
## 🧪 Exécution

bash

# 1. Activer l'environnement
zeta

# 2. Lancer le script
cd ~/projet_zeta/src/calculs
python demo_complete.py

## 📚 Références

- [Hypothèse de Riemann - Wikipedia](https://fr.wikipedia.org/wiki/Hypoth%C3%A8se_de_Riemann)
- [Fonction zêta de Riemann - MathWorld](https://mathworld.wolfram.com/RiemannZetaFunction.html)
- [mpmath documentation](https://mpmath.org/)
- [Ollama - LLMs locaux](https://ollama.com/)
- [Documentation Python](https://docs.python.org/fr/3/)
- [GitHub - Projet Zêta](https://github.com/hprzeta/Riemann_Lab)

## 📜 Licence

Projet de recherche personnel - Libre d'utilisation et de modification.
