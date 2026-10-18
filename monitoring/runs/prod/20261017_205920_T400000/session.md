# Fiche de session — T400000

Photographie de l'état de PC1 et du code au moment du run (turbo : lecture `intel_pstate/no_turbo` ou `cpufreq/boost`, **[hypothèse : mécanisme supposé de `zeta_turbo_on.sh`, non vérifié]**).

| Élément | Valeur |
|---|---|
| Run | 20261017_205920_T400000 |
| Type | prod |
| Début | 2026-10-17T20:59:20 |
| Fin | 2026-10-17T21:19:59 |
| Durée | 20min39s |
| Commande | `bash -c printf '400000\nO\n' | python /home/riemann/projet_zeta/src/calculs/optimisation/compute_zeros_v16.py` |
| Code retour | 0 |
| Hôte / noyau | zeta-lab / 7.0.0-38-generic |
| CPU | Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz — 4 threads |
| Gouverneur | performance |
| Turbo au départ | actif (intel_pstate) |
| Turbo à la fin | actif (intel_pstate) |
| Charge 1 min au départ / à la fin | 2.38 / 3.75 |
| RAM totale / dispo (Go) | 15.5 / 9.7 |
| Disque libre (Go) | 26.8 |
| Git | d275736 @ Riemann_Lab_IA, 22 fichiers modifiés non commités |
| Python / paquets | 3.12.3 / numpy 2.4.4, pandas 3.0.2, matplotlib 3.10.8, mpmath 1.3.0 |
| CSV des zéros | `/home/riemann/projet_zeta/calculs/v16_T400000_20261017_205921/zeros_v16_T400000_20261017_205921.csv` |
| Taille du CSV | 56.5 Mo — 640520 zéros |

---
*session.md · MAJ 2026-10-18 · 28 lignes*
