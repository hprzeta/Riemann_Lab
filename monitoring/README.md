# Monitoring Zêta — mode d'emploi

Dossier : `~/projet_zeta/monitoring/` (PC1). Tout le monitoring est ici : scripts, mesures, rapports de runs.

## Ce que ça fait
1. **Logger** : une mesure par seconde (température, fréquence, load, RAM) des 5 machines → `data/cluster_metrics_AAAAMMJJ.csv`.
2. **Détecteur de run** : dès qu'un processus `compute_zeros…` tourne (toi ou Claude Code), un dossier `runs/<date>_<nom>/` est créé ; à la fin, le **rapport** (3 graphiques commentés, MD + PDF) est généré et `Monitoring-Runs.md` (liste des runs, page wiki) est mis à jour.
3. **Graphiques en direct** (à ouvrir à la demande) : `zeta-live`, `zeta-metrics`, `zeta-gue`.

## Installation (une fois, PC1)
```
cd ~/projet_zeta && tar xzf ~/Téléchargements/monitoring_zeta_20261016.tar.gz && bash monitoring/install.sh
```
Puis nouveau terminal et `zeta-mon-on` (à refaire après chaque redémarrage de PC1).

## Commandes (fonctions bash, utilisables comme des alias)
| Commande | Effet |
|---|---|
| `zeta-mon-on` / `zeta-mon-off` / `zeta-mon-status` | démarre / arrête / vérifie logger 1 s + détecteur de runs |
| `zeta-run-hint NOM [CSV\|dossier]` | **avant un run** : donne un nom lisible et le CSV de sortie (facultatif mais recommandé) |
| `zeta-live [csv\|dossier]` | zéros par tranche (bleu/gris) + détail par zéro, en direct |
| `zeta-metrics [minutes] [refresh_s]` | T°/fréquence/load/RAM des 5 machines en direct (défaut 15 min, 2 s) |
| `zeta-gue [csv]` | histogramme des espacements vs GUE |
| `zeta-report [run] [--lang en]` | régénère le rapport d'un run (défaut : dernier) ; `--lang en` pour le rapport définitif en anglais |
| `zeta-index` / `zeta-runs` | régénère `Monitoring-Runs.md` / liste les runs |

## Menu `zeta-script` (PC1)
`zeta-script` (menu des alias) liste aussi ces commandes : ce sont des **fonctions bash** définies dans
`monitoring/zeta_monitoring_alias.sh` (chargé par `~/.bashrc`), lues par le menu sans duplication de code.
Les commandes à fenêtre graphique (⚠) et celles qui demandent des arguments sont signalées avant lancement.

| N° (menu) | Commande | Effet | Machine |
|---|---|---|---|
| 37 | `zeta-mon-on` | démarre logger 1 s + détecteur de runs | PC1 |
| 38 | `zeta-mon-off` | arrête logger + détecteur | PC1 |
| 39 | `zeta-mon-status` | processus, dernière mesure, dernier run, watcher | PC1 |
| 40 ⚠ | `zeta-live` | zéros par tranche en direct (fenêtre) | PC1 |
| 41 ⚠ | `zeta-metrics` | T°/fréquence/load/RAM des 5 machines (fenêtre) | PC1 |
| 42 ⚠ | `zeta-gue` | espacements vs GUE (fenêtre) | PC1 |
| 43 | `zeta-run-hint NOM [csv]` | avant un run : nom + CSV de sortie | PC1 |
| 44 | `zeta-report [run] [--lang en]` | régénère le rapport d'un run | PC1 |
| 45 | `zeta-index` | régénère `Monitoring-Runs.md` | PC1 |
| 46 | `zeta-runs` | liste les derniers runs | PC1 |

> Les numéros suivent l'ordre du menu et peuvent se décaler si un alias est ajouté dans `~/.bashrc`.

## Procédure d'un run
1. **Avant** : `zeta-mon-status` (sinon `zeta-mon-on`), puis `zeta-run-hint "<nom_court>" "<dossier_ou_csv>"`.
   Lancer le run avec un script dont le nom contient `compute_zeros` (sinon watcher avec `--pattern`).
2. **Pendant** : aucune fenêtre graphique, aucun plein écran (écran gelé déjà constaté, run perdu).
3. **Après** (détection automatique) : vérifier `runs/<id>/` (`rapport.md`, `rapport.pdf`, `figures/{metrics,zeros_tranches,gue}.png`),
   relire « Observations » (hypothèses ≠ faits), puis `zeta-report <run> --lang en` pour le rapport définitif.
   Le rapport **ne remplace pas** la validation Turing–Backlund.

Liens : [Monitoring-Runs.md](Monitoring-Runs.md) (liste des runs, page wiki « Monitoring »).

## Arborescence
```
monitoring/
├── scripts/            zeta_log_metrics.py  zeta_run_watch.py  zeta_run_report.py
│                       zeta_plot_live.py  zeta_plot_metrics.py  zeta_gue_hist.py  zeta_mon_common.py
├── data/               cluster_metrics_AAAAMMJJ.csv (1 ligne / machine / seconde)
├── runs/<id>/          meta.json  metrics.csv  rapport.md  rapport.pdf  figures/{metrics,zeros_tranches,gue}.png
├── galerie/            graphiques de référence conservés
├── exemples/demo/      rapport de DÉMONSTRATION (données simulées)
├── Monitoring-Runs.md  liste des runs + liens graphiques (page wiki)
└── logs/               logger.log  watch.log
```

## Réglages
- Motif du processus détecté : `zeta_run_watch.py --pattern <regex>` (défaut `compute_zeros`). Autre nom de script : relancer le watcher à la main avec `--pattern`.
- Intervalle : `zeta-mon-on --intervalle 2` si PC1 sature (défaut 1 s).
- Wiki GitHub : `ZETA_MON_BASEURL=<url raw du dossier monitoring> zeta-index` préfixe les liens des images.
- Variables : `ZETA_MON_ROOT`, `ZETA_PY` (Python du venv), `ZETA_CALCULS` (dossier des CSV de zéros).

## Limites et points à vérifier (non testés sur le cluster réel)
- **[mesuré ici]** chaîne complète testée en environnement simulé : logger 1 s, détection d'un processus, rapport MD+PDF, index.
- **[hypothèse]** SSH multiplexé (`ControlMaster`) supporté par PC2–PC5 et par sshd OpenBSD de PC4 : à confirmer avec `python scripts/zeta_log_metrics.py --test`.
- **[hypothèse]** venv `~/projet_zeta/zeta_env` ; reportlab absent → MD seulement (message affiché) : `pip install reportlab pillow`.
- Début/fin de run = apparition/disparition du processus (à quelques secondes). Le rapport **ne remplace pas** la validation Turing–Backlund.
- PC4 (OpenBSD) : pas de mesure de RAM. Alias SSH de PC5 `zeta-monitor` supposé.
- Aucune fenêtre ne s'ouvre automatiquement pendant un run (le plein écran avait gelé l'écran) : les graphiques en direct restent à la demande.

---
*README.md · MAJ 2026-10-16 · 85 lignes*
