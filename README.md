Projet Zêta : Exploration de l'Hypothèse de Riemann

    *"Les zéros non triviaux de la fonction zêta de Riemann ont tous une partie réelle égale à 1/2."*
    — Bernhard Riemann (1859)

🎯 Objectif du projet

Ce projet a pour but d'explorer numériquement et symboliquement la fonction zêta de Riemann ζ(s), pierre angulaire de la théorie des nombres. L'Hypothèse de Riemann (non démontrée à ce jour) affirme que tous les zéros non triviaux de ζ(s) se trouvent sur la droite critique Re(s) = 1/2.

Ce projet combine :

    Calculs haute précision

    Visualisations 2D/3D

    Intelligence artificielle locale (LLM)

    Preuves formelles (Lean 4)

📁 Structure du projet
text

/home/riemann/
├── projet_zeta/                         # Dossier principal du projet
│   ├── zeta_env/                        # Environnement virtuel Python
│   │
│   ├── src/                             # Code source
│   │   ├── calculs/                     # Calculs sur la fonction zêta
│   │   │   ├── zeta_core.py             # Fonctions de base
│   │   │   ├── zeros.py                 # Recherche de zéros
│   │   │   ├── analyse.py               # Analyse mathématique
│   │   │   └── demo_complete.py         # Démonstration complète
│   │   ├── ia/                          # Modèles d'IA locaux
│   │   │   ├── ollama_client.py         # Interface avec Ollama
│   │   │   └── prompts.py               # Templates de prompts
│   │   ├── utils/                       # Utilitaires
│   │   │   ├── logger.py                # Gestion des logs
│   │   │   ├── monitoring.py            # Monitoring CPU/GPU/RAM
│   │   │   └── data_manager.py          # Gestion des données
│   │   └── tests/                       # Tests unitaires
│   │
│   ├── scripts/                         # Scripts exécutables
│   │   ├── run_calcul.sh
│   │   ├── run_ia.sh
│   │   └── monitor.sh
│   │
│   ├── notebooks/                       # Jupyter notebooks
│   │   ├── exploration_zeta.ipynb
│   │   ├── analyse_zeros.ipynb
│   │   └── visualisation.ipynb
│   │
│   ├── lean_projects/                   # Projets Lean 4
│   │   └── riemann_hypothesis/
│   │
│   ├── config/                          # Fichiers de configuration
│   │   └── settings.py
│   │
│   ├── docs/                            # Documentation locale
│   │   └── methodologie.md
│   │
│   └── .vscode/                         # Configuration VS Code
│       └── settings.json
│
└── /mnt/data/                           # Données volumineuses
    ├── datasets/                        # Datasets bruts
    │   └── calculs/
    │       └── nombres_a_tester.txt
    ├── exports/                         # Exports CSV, JSON
    │   ├── csv/
    │   │   └── resultats_zeta.csv
    │   └── figures/
    │       ├── visualisation_matplotlib.png
    │       └── visualisation_plotly.html
    └── logs/                            # Logs d'exécution
        └── demo_zeta.log

🛠️ Outils et bibliothèques
Catégorie	Outils	Priorité
Calcul haute précision	mpmath, sympy, Pari/GP	🔴 Haute
Calcul vectoriel	numpy, scipy	🔴 Haute
Visualisation	matplotlib, plotly, seaborn	🔴 Haute
Gestion données	pandas, pyarrow	🟡 Moyenne
Logging/Monitoring	loguru, tqdm, memory_profiler	🟡 Moyenne
Parallélisation	joblib, dask, ray	🟡 Moyenne
IA complémentaire	transformers, torch	🟢 Optionnelle
Preuves formelles	Lean 4	🟢 Optionnelle
Environnement complet	SageMath	🟢 Optionnelle
Détail par outil
Outil	Utilité pour le projet	Statut
mpmath	Calcul haute précision, zéros de ζ(s)	✅ OUI
sympy	Manipulation symbolique de ζ(s)	✅ OUI
numpy	Vecteurs, matrices, FFT	✅ OUI
scipy	Intégrations, optimisation	✅ OUI
matplotlib	Graphiques 2D	✅ OUI
plotly	Graphiques 3D interactifs (bande critique)	✅ OUI
joblib	Parallélisation des calculs	✅ OUI
Pari/GP	Spécialiste en théorie des nombres	✅ OUI
SageMath	Environnement mathématique complet	⚠️ Optionnel
Lean 4	Preuves formelles de l'hypothèse	⚠️ Optionnel
🚀 Alias de configuration (.bashrc)
Alias	Commande	Usage
zeta	cd ~/projet_zeta && source zeta_env/bin/activate	⭐ Activer l'environnement
zeta-jupyter	cd ~/projet_zeta/notebooks && source ~/projet_zeta/zeta_env/bin/activate && jupyter lab	📓 Interface moderne
zeta-notebook	cd ~/projet_zeta/notebooks && source ~/projet_zeta/zeta_env/bin/activate && jupyter notebook	📓 Interface classique
zeta-spyder	source ~/projet_zeta/zeta_env/bin/activate && export QT_API=pyqt5 && spyder	🐍 IDE scientifique
zeta-code	code ~/projet_zeta	💻 IDE général
zeta-data	cd /mnt/data	💾 Données
zeta-docs	cd ~/projet_zeta/docs	📚 Documentation
zeta-logs	tail -f /mnt/data/logs/demo_zeta.log	📋 Monitoring
zeta-monitor	~/projet_zeta/scripts/monitor.sh	📊 Performance
📊 Résultats des tests
Test d'exécution de demo_complete.py
bash

(zeta_env) riemann@zeta-lab:~/projet_zeta/src/calculs$ python demo_complete.py

Sortie console :
text

2026-04-07 23:09:28.610 | INFO     | === Démarrage de la démonstration du projet Zêta ===
2026-04-07 23:09:28.650 | INFO     | Précision mpmath configurée à 50 décimales
2026-04-07 23:09:29.273 | INFO     | Lecture du fichier : /mnt/data/datasets/calculs/nombres_a_tester.txt
2026-04-07 23:09:29.274 | INFO     | Lu 10 nombres
2026-04-07 23:09:29.274 | INFO     | === Traitement SÉQUENTIEL ===
2026-04-07 23:09:29.311 | INFO     | Traitement séquentiel terminé en 0.0376s
2026-04-07 23:09:29.312 | INFO     | === RAPPORT FINAL ===
2026-04-07 23:09:29.312 | INFO     | Nombre de calculs effectués : 10
2026-04-07 23:09:29.312 | INFO     | Temps séquentiel : 0.0376s
2026-04-07 23:09:29.312 | INFO     | Temps total d'exécution : 0.7023s

============================================================
RÉSULTATS DES CALCULS
============================================================
ζ((0.5+14j)) = (1.6302581668434337428933519038366894001715470747867e-5 - 1.035502386950401254451202360128080777272067607025e-7j)
ζ((0.5+21j)) = (2.4558814875624359887254599814050478584681452247767e-5 - 4.2383538330940678490101238077065516525477657181441e-7j)
ζ((0.5+25j)) = (9.0582446084188376507490345772482939491712931898692e-6 - 8.0307186868792086980194777288965074285591526206301e-7j)
ζ(2.0) = 1.6449340668482264364724151666460251892189499012068
ζ(3.0) = 1.2020569031595942853997381615114499907649862923405
ζ(4.0) = 1.0823232337111381915160036965411679037747519487369
ζ(0.5) = -1.4603545088095868128894991525152980124672293310126
ζ(1.5) = 2.6123753486854883433485675679240716305708006524002
ζ(2.5) = 1.3414872572509171797567696933484806452051803006299
ζ(3.5) = 1.1267338673170566464278124868550569121668896651723
============================================================

Fichiers générés
Fichier	Chemin	Description
CSV	/mnt/data/exports/csv/resultats_zeta.csv	Résultats des calculs
Log	/mnt/data/logs/demo_zeta.log	Journal d'exécution
PNG	/mnt/data/exports/figures/visualisation_matplotlib.png	Graphique matplotlib
HTML	/mnt/data/exports/figures/visualisation_plotly.html	Graphique plotly interactif
Aperçu des résultats CSV
csv

s,zeta_s,temps_calcul,reussite
(0.5+14j),(1.6302581668434337e-5 - 1.0355023869504013e-7j),0.001234,True
(0.5+21j),(2.455881487562436e-5 - 4.238353833094068e-7j),0.000987,True
2.0,1.6449340668482264,0.000123,True
3.0,1.2020569031595943,0.000098,True

Visualisations

Le script génère deux visualisations :

    visualisation_matplotlib.png : Graphique 2D avec matplotlib

        Module de ζ(s) pour les réels purs

        Temps de calcul par point

    visualisation_plotly.html : Graphique 3D interactif

        Module de ζ(s) sur la droite critique Re(s)=1/2

        Ouvrir dans un navigateur pour zoomer/interagir

🧪 Comment exécuter la démonstration
1. Préparer le fichier d'entrée
bash

mkdir -p /mnt/data/datasets/calculs
cat > /mnt/data/datasets/calculs/nombres_a_tester.txt << EOF
0.5+14j
0.5+21j
0.5+25j
2
3
4
0.5
1.5
2.5
3.5
EOF

2. Activer l'environnement et lancer
bash

# Activer l'environnement virtuel
zeta

# Aller dans le dossier
cd ~/projet_zeta/src/calculs

# Lancer le script
python demo_complete.py

3. Dans Spyder
bash

zeta-spyder
# Ouvrir le fichier src/calculs/demo_complete.py
# Exécuter avec F5

4. Dans VS Code
bash

zeta-code
# Ouvrir le fichier src/calculs/demo_complete.py
# Terminal intégré (Ctrl+`)
# python demo_complete.py

📚 Références

    Hypothèse de Riemann - Wikipedia

    Fonction zêta de Riemann - Encyclopédie des maths

    mpmath documentation

    Ollama - LLMs locaux

📜 Licence

Projet de recherche personnel - Libre d'utilisation et de modification.
