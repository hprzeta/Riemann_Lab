# Fiche de session — T100000

Photographie de l'état de PC1 et du code au moment du run (turbo : lecture `intel_pstate/no_turbo` ou `cpufreq/boost`, **[hypothèse : mécanisme supposé de `zeta_turbo_on.sh`, non vérifié]**).

| Élément | Valeur |
|---|---|
| Run | 20261105_213329_T100000 |
| Type | prod |
| Début | 2026-11-05T21:33:29 |
| Fin | 2026-11-05T21:35:55 |
| Durée | 2min26s |
| Commande | `bash -c printf '100000\nO\n' | python /home/riemann/projet_zeta/src/calculs/optimisation/compute_zeros_v17.py` |
| Code retour | 0 |
| Hôte / noyau | zeta-lab / 7.0.0-42-generic |
| CPU | Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz — 4 threads |
| Gouverneur | performance |
| Turbo au départ | actif (intel_pstate) |
| Turbo à la fin | actif (intel_pstate) |
| Charge 1 min au départ / à la fin | 2.57 / 6.49 |
| RAM totale / dispo (Go) | 15.5 / 10.5 |
| Disque libre (Go) | 24.4 |
| Git | d50b7f7 @ Riemann_Lab_IA, 30 fichiers modifiés non commités |
| Python / paquets | 3.12.3 / numpy 2.4.4, pandas 3.0.2, matplotlib 3.10.8, mpmath 1.3.0 |
| CSV des zéros | `/home/riemann/projet_zeta/calculs/v17_T100000_20261105_213331/zeros_v17_T100000_20261105_213331.csv` |
| Taille du CSV | 11.9 Mo — 138069 zéros |

---
*session.md · MAJ 2026-11-05 · 28 lignes*
