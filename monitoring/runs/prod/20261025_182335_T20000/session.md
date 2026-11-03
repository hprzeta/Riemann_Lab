# Fiche de session — T20000

Photographie de l'état de PC1 et du code au moment du run (turbo : lecture `intel_pstate/no_turbo` ou `cpufreq/boost`, **[hypothèse : mécanisme supposé de `zeta_turbo_on.sh`, non vérifié]**).

| Élément | Valeur |
|---|---|
| Run | 20261025_182335_T20000 |
| Type | prod |
| Début | 2026-10-25T18:23:35 |
| Fin | 2026-10-25T18:23:40 |
| Durée | 0min05s |
| Commande | `bash -c printf '20000\nO\n' | python /home/riemann/projet_zeta/src/calculs/optimisation/compute_zeros_v16.py` |
| Code retour | 130 |
| Hôte / noyau | zeta-lab / 7.0.0-38-generic |
| CPU | Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz — 4 threads |
| Gouverneur | performance |
| Turbo au départ | actif (intel_pstate) |
| Turbo à la fin | actif (intel_pstate) |
| Charge 1 min au départ / à la fin | 0.92 / 2.21 |
| RAM totale / dispo (Go) | 15.5 / 11.4 |
| Disque libre (Go) | 25.6 |
| Git | 72bb991 @ Riemann_Lab_IA, 42 fichiers modifiés non commités |
| Python / paquets | 3.12.3 / numpy 2.4.4, pandas 3.0.2, matplotlib 3.10.8, mpmath 1.3.0 |
| CSV des zéros | introuvable |

---
*session.md · MAJ 2026-10-25 · 27 lignes*
