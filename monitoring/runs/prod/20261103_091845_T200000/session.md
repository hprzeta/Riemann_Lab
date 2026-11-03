# Fiche de session — T200000

Photographie de l'état de PC1 et du code au moment du run (turbo : lecture `intel_pstate/no_turbo` ou `cpufreq/boost`, **[hypothèse : mécanisme supposé de `zeta_turbo_on.sh`, non vérifié]**).

| Élément | Valeur |
|---|---|
| Run | 20261103_091845_T200000 |
| Type | prod |
| Début | 2026-11-03T09:18:45 |
| Fin | 2026-11-03T09:25:09 |
| Durée | 6min24s |
| Commande | `bash -c printf '200000\nO\n' | python /home/riemann/projet_zeta/src/calculs/optimisation/compute_zeros_v16.py` |
| Code retour | 0 |
| Hôte / noyau | zeta-lab / 7.0.0-42-generic |
| CPU | Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz — 4 threads |
| Gouverneur | performance |
| Turbo au départ | actif (intel_pstate) |
| Turbo à la fin | actif (intel_pstate) |
| Charge 1 min au départ / à la fin | 1.4 / 3.34 |
| RAM totale / dispo (Go) | 15.5 / 10.7 |
| Disque libre (Go) | 25.4 |
| Git | 43134dd @ Riemann_Lab_IA, 48 fichiers modifiés non commités |
| Python / paquets | 3.12.3 / numpy 2.4.4, pandas 3.0.2, matplotlib 3.10.8, mpmath 1.3.0 |
| CSV des zéros | `/home/riemann/projet_zeta/calculs/v16_T200000_20261103_091846/zeros_v16_T200000_20261103_091846.csv` |
| Taille du CSV | 26.0 Mo — 298200 zéros |

---
*session.md · MAJ 2026-11-03 · 28 lignes*
