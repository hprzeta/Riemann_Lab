# Monitoring report — run T100000

Legend: **[measured]** = figure read from data; **[heuristic]** / **[hypothesis]** = unverified interpretation; **[conjecture]** = unproven result.

## 1. Summary

| Item | Value |
|---|---|
| Run | 20261017_175939_T100000  (test) |
| Start / end | 2026-10-17 17:59:39 → 18:02:18 |
| Duration | 2min39s |
| Command (excerpt) | `bash -c printf '100000\nO\n' \| python /home/riemann/projet_zeta/src/calculs/optimisation/c` |
| Exit code | 0 |
| CPU turbo start → end | actif (intel_pstate) → actif (intel_pstate) |
| Zeros CSV | `zeros_v16_T100000_20261017_175940.csv` |
| Zeros in CSV | 138069  [measured] |
| t min → t max | 14.135 → 99999.701 |
| Average rate (zeros / run duration) | 868.4 /s |

## 2. Machines during the run

![Figure 1 — Temperature, frequency, load and RAM of the 5 machines (1 sample/s).](figures/metrics.png)

*Figure 1 — Temperature, frequency, load and RAM of the 5 machines (1 sample/s).*

| Machine | Valid | T moy °C | T max °C | % ≥ 75 °C | MHz min–max | load max | RAM max % |
|---|---|---|---|---|---|---|---|
| PC1 zeta-lab | 100 % | 69.7 | 79.0 | 13 | 2900–3500 | 14.49 | 42.6 |
| PC2 zeta-calc-second | 100 % | 25.1 | 26.0 | 0 | 2870–2993 | 0.29 | 16.9 |
| PC3 zeta-backup | 100 % | 29.5 | 30.0 | 0 | 2100–2700 | 0.27 | 15.2 |
| PC4 zeta-secure | 100 % | 34.5 | 36.0 | 0 | 1800–1800 | 0.05 | — |
| PC5 zeta-monitor | 100 % | 45.5 | 45.9 | 0 | 1297–1299 | 0.06 | 18.3 |

### Observations

- PC1: max temperature 79.0 °C, 13 % of time ≥ 75 °C (warning threshold) [measured]
- PC1: median frequency 3000 MHz over the first fifth of the run, 3200 MHz over the last [measured]

## 3. Computed zeros

![Figure 2 — Top: zeros per t-slice (alternating blue/grey) vs theoretical density ln(t/2π)/2π. Bottom: normalized spacing of each zero.](figures/zeros_tranches.png)

*Figure 2 — Top: zeros per t-slice (alternating blue/grey) vs theoretical density ln(t/2π)/2π. Bottom: normalized spacing of each zero.*

Count: 138069 zeros in the CSV; Riemann–von Mangoldt formula (without the S(t) term): ≈ 138068.6. Difference +0.4. **[heuristic]** a difference of a few units is normal; tens suggest missing or duplicated zeros. **This is not a validation: completeness is proven by Turing–Backlund, outside this report.**

![Figure 3 — Normalized spacings vs GUE (Wigner surmise) and Poisson; right: zoom on repulsion (log scale).](figures/gue.png)

*Figure 3 — Normalized spacings vs GUE (Wigner surmise) and Poisson; right: zoom on repulsion (log scale).*

| Item | Measured | Reference |
|---|---|---|
| Mean of s | 1.0000 | 1 (by construction) |
| Variance of s | 0.1614 | GUE ≈ 0.18 ; Poisson = 1 |
| Share s < 0.1 | 0.073 % | GUE surmise ≈ 0.11 % ; Poisson ≈ 9.5 % |
| Smallest raw gap | 0.014705 | — |

**[conjecture, Montgomery–Odlyzko]** spacings follow GUE; here the repulsion is clear. A variance slightly below 0.18 at moderate heights is attributed to finite-size corrections **[hypothesis]**. With few zeros (< a few thousand) the histogram is noisy: do not over-interpret.

![Figure 4 — Throughput (zeros/s) over the run, to compare with PC1 frequency and temperature (figure 1).](figures/debit.png)

*Figure 4 — Throughput (zeros/s) over the run, to compare with PC1 frequency and temperature (figure 1).*

- Instantaneous throughput not usable: the zeros CSV grew on only 6 % of the samples (written per worker at the end); rely on the mean throughput in the summary [measured]

## 4. Session sheet

| Item | Value |
|---|---|
| CPU | Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz (4 threads) |
| Governor / turbo | performance / actif (intel_pstate) |
| Git | 2de45af @ Riemann_Lab_IA (27 modified files) |
| Load / free RAM at start | 2.46 / 9.8 Go |
| Detailed file | `session.md` |

## 5. Interpretation

*Written by Claude Code from the figures above — to be validated.*

### Calcul

- **[mesuré]** 138 069 zéros pour T = 100 000, contre ≈ 138 068,6 par la formule de Riemann–von Mangoldt (écart +0,4). Score LMFDB 20/20 à moins de 10⁻⁹. Validation de Turing : « complet ».
- **[heuristique]** L'accord du comptage avec la formule indique qu'aucun zéro n'est manqué sur cet intervalle. Il ne le démontre pas : le rapport ne remplace pas une validation Turing–Backlund certifiée.

### Machine

- **[mesuré]** PC1 : température moyenne 69,7 °C, maximum 79,0 °C, 13 % du temps au-dessus de 75 °C. Fréquence médiane 3 000 MHz sur le 1ᵉʳ cinquième du run, 3 200 MHz sur le dernier. Charge maximale 14,49. Aucune erreur de lancement.
- **[hypothèse]** La fréquence basse en début de run (2 900 à 3 000 MHz) pourrait venir de la montée en température et de la charge simultanée des 4 threads. Aucune mesure ici ne l'établit : le run ne dure que 97 s de calcul.
- **[mesuré]** PC2 à PC5 sont restés inactifs (charge ≤ 0,3, température ≤ 46 °C) : le run n'a utilisé que PC1.

### Statistique des espacements

- **[mesuré]** Variance des espacements normalisés 0,1614 ; part des espacements inférieurs à 0,1 : 0,073 %.
- **[conjecture, Montgomery–Odlyzko]** Les espacements suivent la loi GUE. La répulsion observée est cohérente avec elle et très loin de Poisson (variance 1, part inférieure à 0,1 de 9,5 %).
- **[hypothèse]** L'écart entre 0,1614 et 0,18 s'expliquerait par des corrections de taille finie à ces hauteurs. Non vérifié ici.

### Limites de ce run

- **[mesuré]** La version v16 écrit le CSV de chaque worker seulement à la fin de ce worker : le débit instantané (`etat.csv`) vaut 0 presque partout et n'est pas exploitable. Seul le débit moyen (868 z/s) est fiable.
- **[mesuré]** Un seul run de test, un seul passage : aucune comparaison avec un autre run, donc aucune conclusion sur la variabilité d'un run à l'autre.

## 6. Limits

- Samples about every 1 s (SSH): shorter spikes are missed; PC4 (OpenBSD) has no RAM reading.
- Run start/end = detected process appearing/disappearing, within a few seconds.
- Beyond 8,000 points per machine the plot is subsampled (statistics use all samples).

---
*report_en.md · MAJ 2026-10-17 · 109 lignes*
