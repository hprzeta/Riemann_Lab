# Fiche de session — T400000

Photographie de l'état de PC1 et du code au moment du run (turbo : lecture `intel_pstate/no_turbo` ou `cpufreq/boost`, **[hypothèse : mécanisme supposé de `zeta_turbo_on.sh`, non vérifié]**).

| Élément | Valeur |
|---|---|
| Run | 20261103_095447_T400000 |
| Type | prod |
| Début | 2026-11-03T09:54:47 |
| Fin | 2026-11-03T10:15:33 |
| Durée | 20min46s |
| Commande | `bash -c printf '400000\nO\n' | python /home/riemann/projet_zeta/src/calculs/optimisation/compute_zeros_v17.py` |
| Code retour | 0 |
| Hôte / noyau | zeta-lab / 7.0.0-42-generic |
| CPU | Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz — 4 threads |
| Gouverneur | performance |
| Turbo au départ | actif (intel_pstate) |
| Turbo à la fin | actif (intel_pstate) |
| Charge 1 min au départ / à la fin | 2.42 / 2.74 |
| RAM totale / dispo (Go) | 15.5 / 11.5 |
| Disque libre (Go) | 25.6 |
| Git | 43134dd @ Riemann_Lab_IA, 49 fichiers modifiés non commités |
| Python / paquets | 3.12.3 / numpy 2.4.4, pandas 3.0.2, matplotlib 3.10.8, mpmath 1.3.0 |
| CSV des zéros | `/home/riemann/projet_zeta/calculs/v17_T400000_20261103_095511/zeros_v17_T400000_20261103_095511.csv` |
| Taille du CSV | 56.5 Mo — 640526 zéros |

---
*session.md · MAJ 2026-11-03 · 28 lignes*
