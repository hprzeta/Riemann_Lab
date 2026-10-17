# Monitoring Zêta — mode d'emploi (v2, 2026-10-17)

Dossier : `~/projet_zeta/monitoring/` (PC1). Scripts, mesures, rapports de runs : tout est ici.

## Lancer un run AVEC monitoring (toi ou Claude Code)
```
zeta-mon-exec --nom "T-test-3min" --type test --csv ~/projet_zeta/calculs/<dossier>/ -- <commande du run>
```
Ce que ça fait automatiquement :
1. crée `runs/test/AAAAMMJJ_HHMMSS_nom/` + fiche de session (commande, git, turbo, CPU, RAM…) ;
2. **type `test`** : ouvre 3 petites fenêtres rangées (zéros en haut à gauche, GUE en bas à gauche, machines à droite), jamais en plein écran ; **type `prod`** : pas de fenêtres (CPU saturé = risque de gel) sauf `--fenetres oui` ;
3. toutes les 5 s : `etat.json` / `etat.csv` (zéros, t courant, z/s, T°/fréquence/load PC1) ;
4. à la fin : code retour, puis `rapport.md` + `rapport.pdf` (figures, observations, fiche de session, section « Interprétation »), et mise à jour de `Monitoring-Runs.md`.

Run lancé à côté (`setsid nohup …`) : `zeta-mon-start --nom N --type prod [--pid PID]` puis `zeta-mon-stop --code 0`.
Run lancé sans rien (filet de sécurité) : le détecteur `zeta_run_watch.py` fait seulement le rapport, dans `runs/auto/`.

## Fréquences d'écriture
| Élément | Écriture |
|---|---|
| CSV machines (`data/`) | toutes les **1 s**, en continu |
| CSV des zéros | **flush toutes les 1–2 s** par le script de calcul (condition du live fluide ; à vérifier dans `compute_zeros_v17.py`) |
| `etat.json` / `etat.csv` | toutes les 5 s |
| Fenêtres : zéros, machines | rafraîchies toutes les **2 s** ; GUE toutes les **30 s** (statistique : inutile plus vite) |
| Rapport MD + PDF, figures finales, `session.md` | **fin de run seulement** |
Maximum utile : 1 s. Lecture incrémentale (zéros) et lecture de la fin du fichier (machines) : fluide même avec des millions de zéros.

## Dossier d'un run
```
runs/<type>/<id>/  meta.json  session.md  etat.json  etat.csv  metrics.csv  superviseur.log
                   figures/{metrics,zeros_tranches,gue,debit}.png
                   rapport.md  rapport.pdf  (report_en.md/.pdf avec --lang en)
                   interpretation.md  ← à rédiger après relecture, puis `zeta-report`
```
`interpretation.md` n'est **jamais** généré automatiquement : mesuré / heuristique / hypothèse / conjecture doivent rester distincts.

## Commandes (fonctions bash chargées par `.bashrc`)
| Commande | Effet |
|---|---|
| `zeta-mon-exec`, `zeta-mon-start`, `zeta-mon-stop` | lanceur de run (voir ci-dessus) |
| `zeta-mon-fenetres [--csv X]`, `zeta-mon-fermer` | ouvre / ferme les 3 fenêtres sans run |
| `zeta-mon-on`, `zeta-mon-off`, `zeta-mon-status` | logger 1 s + détecteur de secours |
| `zeta-run-hint NOM [CSV]` | indice avant un run lancé sans le lanceur |
| `zeta-live [csv]`, `zeta-metrics [min] [s]`, `zeta-gue [csv] [--live]` | graphiques en direct |
| `zeta-report [run] [--lang en]`, `zeta-index`, `zeta-runs` | rapports et index |

## Placement des fenêtres
Géométries calculées pour l'écran (xrandr, sinon 1920×1080) ; surchargeables dans `monitoring/layout.json` (`{"marge":[75,35],"geometries":{"live":"900x500+75+35",...}}`). Variable `ZETA_ECRAN=1920x1080`. **Sous Wayland natif la position peut être ignorée** : ranger avec `Super + flèches`. Backend graphique : Tk ou Qt requis (`python -c "import tkinter"` ou PyQt5).

## Limites et points à vérifier (non testés sur le cluster réel)
- **[mesuré ici, données simulées]** chaîne complète : lanceur, code retour, rapport MD+PDF, index, fenêtres rangées (écran virtuel 1920×1080, Qt).
- **[hypothèse]** turbo lu par `intel_pstate/no_turbo` ou `cpufreq/boost` ; si `inconnu`, adapter `turbo_etat()`.
- **[hypothèse]** SSH multiplexé accepté par PC2–PC5 (dont OpenBSD) : `python scripts/zeta_log_metrics.py --test`.
- Un run très court (< 2 s) est manqué par le détecteur : utiliser `zeta-mon-exec`. Un run de validation utile dure ≥ 2–3 min.
- PC4 : pas de mesure de RAM. Le rapport ne remplace pas la validation Turing–Backlund.

---
*README.md · MAJ 2026-10-17 · 58 lignes*
