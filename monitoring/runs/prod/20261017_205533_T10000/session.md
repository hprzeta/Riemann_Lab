# Fiche de session — T10000

Photographie de l'état de PC1 et du code au moment du run (turbo : lecture `intel_pstate/no_turbo` ou `cpufreq/boost`, **[hypothèse : mécanisme supposé de `zeta_turbo_on.sh`, non vérifié]**).

| Élément | Valeur |
|---|---|
| Run | 20261017_205533_T10000 |
| Type | prod |
| Début | 2026-10-17T20:55:33 |
| Fin | 2026-10-17T20:55:55 |
| Durée | 0min22s |
| Commande | `bash -c printf '10000\nO\n' | python /home/riemann/projet_zeta/src/calculs/optimisation/compute_zeros_v16.py` |
| Code retour | 0 |
| Hôte / noyau | zeta-lab / 7.0.0-38-generic |
| CPU | Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz — 4 threads |
| Gouverneur | performance |
| Turbo au départ | actif (intel_pstate) |
| Turbo à la fin | actif (intel_pstate) |
| Charge 1 min au départ / à la fin | 2.06 / 3.77 |
| RAM totale / dispo (Go) | 15.5 / 9.8 |
| Disque libre (Go) | 26.8 |
| Git | d275736 @ Riemann_Lab_IA, 22 fichiers modifiés non commités |
| Python / paquets | 3.12.3 / numpy 2.4.4, pandas 3.0.2, matplotlib 3.10.8, mpmath 1.3.0 |
| CSV des zéros | `/home/riemann/projet_zeta/calculs/v16_T10000_20261017_205534/zeros_v16_T10000_20261017_205534.csv` |
| Taille du CSV | 0.8 Mo — 10142 zéros |

---
*session.md · MAJ 2026-10-17 · 28 lignes*
