# Monitoring des runs — Zêta

Liste de chaque run lancé, avec ses graphiques (générée automatiquement par `zeta_mon_run.py` / `zeta_run_watch.py` / `zeta_run_report.py`). Chiffres **mesurés** ; interprétations marquées *hypothèse* dans chaque rapport ; section « Interprétation » rédigée après relecture.

## Runs de test

| Date | Run | Statut | Durée | Zéros | z/s | T max PC1 | Graphiques | Rapport · session |
|---|---|---|---|---|---|---|---|---|
| 2026-10-17 17:59 | T100000 | terminé | 2min39s | 138069 | 868.4 | 79.0 | [métriques](runs/test/20261017_175939_T100000/figures/metrics.png) · [zéros](runs/test/20261017_175939_T100000/figures/zeros_tranches.png) · [GUE](runs/test/20261017_175939_T100000/figures/gue.png) · [débit](runs/test/20261017_175939_T100000/figures/debit.png) | [MD](runs/test/20261017_175939_T100000/rapport.md) · [PDF](runs/test/20261017_175939_T100000/rapport.pdf) · [session](runs/test/20261017_175939_T100000/session.md) |
| 2026-10-17 17:50 | T50000 | terminé | 2min16s | 63519 | 467.1 | 77.0 | [métriques](runs/test/20261017_175028_T50000/figures/metrics.png) · [zéros](runs/test/20261017_175028_T50000/figures/zeros_tranches.png) · [GUE](runs/test/20261017_175028_T50000/figures/gue.png) · [débit](runs/test/20261017_175028_T50000/figures/debit.png) | [MD](runs/test/20261017_175028_T50000/rapport.md) · [PDF](runs/test/20261017_175028_T50000/rapport.pdf) · [session](runs/test/20261017_175028_T50000/session.md) |

## Historique (sans mesures machines)

| Date | Run | Statut | Durée | Zéros | z/s | T max PC1 | Graphiques | Rapport · session |
|---|---|---|---|---|---|---|---|---|
| 2026-10-15 | T1b (t ∈ [4 900 000 ; 4 986 000]) — historique | historique (sans mesures machines) | — | 185810 | — | — | [zéros](runs/historique/20261015_T1b_historique/figures/zeros_tranches.png) · [GUE](runs/historique/20261015_T1b_historique/figures/gue.png) | — |

## Dernier run avec historique machines : T100000

![métriques](runs/test/20261017_175939_T100000/figures/metrics.png)

![zéros](runs/test/20261017_175939_T100000/figures/zeros_tranches.png)

## Galerie de référence (graphiques conservés)

Exemples **réels** de la séance du 2026-10-15 (T1b), pour savoir à quoi ressemble un run sain. La série machines est courte (quelques minutes) : illustration du format, pas une mesure de run.

![Suivi en direct des zéros (`zeta-live`) : colonnes bleu/gris + espacement de chaque zéro.](galerie/live_zeros.png)

*Suivi en direct des zéros (`zeta-live`) : colonnes bleu/gris + espacement de chaque zéro.*

![Espacements vs GUE (`zeta-gue`) : la répulsion des zéros, loin de Poisson.](galerie/gue.png)

*Espacements vs GUE (`zeta-gue`) : la répulsion des zéros, loin de Poisson.*

![Historique des 5 machines (`zeta-metrics`) : T°, fréquence, load, RAM.](galerie/metrics.png)

*Historique des 5 machines (`zeta-metrics`) : T°, fréquence, load, RAM.*

## Commandes (PC1)

- `zeta-mon-exec --nom N --type test|prod -- <commande>` : lance un run **avec** monitoring (fenêtres pour un test), code retour, rapport
- `zeta-mon-start` / `zeta-mon-stop --code N` : idem pour un run lancé à côté ; `zeta-mon-fenetres` / `zeta-mon-fermer`
- `zeta-mon-on` / `zeta-mon-off` / `zeta-mon-status` : logger machines 1 s + détecteur de secours
- `zeta-live` · `zeta-metrics` · `zeta-gue [--live]` · `zeta-report [run] [--lang en]` · `zeta-index`

---
*Monitoring-Runs.md · MAJ 2026-10-17 · 48 lignes*
