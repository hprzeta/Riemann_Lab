# Rapport de monitoring — run T200000

Légende : **[mesuré]** = chiffre lu dans les données ; **[heuristique]** / **[hypothèse]** = interprétation non vérifiée ; **[conjecture]** = résultat non démontré.

**Validation Turing–Backlund : ✅ COMPLET** [mesuré, lu dans execution_v16_T200000_20261025_024916.log] — vérification numérique, pas une certification.

## 1. Résumé

| Grandeur | Valeur |
|---|---|
| Run | 20261025_024914_T200000  (prod) |
| Début / fin | 2026-10-25 02:49:14 → 02:55:19 |
| Durée | 6min05s |
| Commande (extrait) | `bash -c printf '200000\nO\n' \| python /home/riemann/projet_zeta/src/calculs/optimisation/c` |
| Code retour | 0 |
| Turbo CPU début → fin | actif (intel_pstate) → actif (intel_pstate) |
| CSV des zéros | `zeros_v16_T200000_20261025_024916.csv` |
| Turing–Backlund | ✅ COMPLET |
| Zéros dans le CSV | 298200  [mesuré] |
| t min → t max | 14.135 → 199999.705 |
| Débit moyen (zéros / durée du run) | 817.0 /s |

## 2. Machines pendant le run

![Figure 1 — Température, fréquence, charge et RAM des 5 machines (1 mesure/s).](figures/metrics.png)

*Figure 1 — Température, fréquence, charge et RAM des 5 machines (1 mesure/s).*

| Machine | Valides | T moy °C | T max °C | % ≥ 75 °C | MHz min–max | load max | RAM max % |
|---|---|---|---|---|---|---|---|
| PC1 zeta-lab | 100 % | 52.0 | 80.0 | 9 | 700–3503 | 14.26 | 32.1 |
| PC2 zeta-calc-second | 100 % | 31.3 | 34.0 | 0 | 2738–2993 | 0.28 | 17.0 |
| PC3 zeta-backup | 100 % | 33.7 | 34.5 | 0 | 2100–2700 | 0.09 | 15.2 |
| PC4 zeta-secure | 100 % | 40.8 | 45.0 | 0 | 1800–1800 | 0.63 | — |
| PC5 zeta-monitor | 100 % | 52.0 | 52.6 | 0 | 1297–1299 | 0.25 | 19.0 |

### Observations

- PC1 : température max 80.0 °C, 9 % du temps ≥ 75 °C (seuil d'avertissement) [mesuré]
- PC1 : fréquence médiane 3100 MHz sur le 1ᵉʳ cinquième du run, 3100 MHz sur le dernier [mesuré]

## 3. Zéros calculés

![Figure 2 — Haut : zéros par tranche de t (bleu/gris alternés) vs densité théorique ln(t/2π)/2π. Bas : espacement normalisé de chaque zéro.](figures/zeros_tranches.png)

*Figure 2 — Haut : zéros par tranche de t (bleu/gris alternés) vs densité théorique ln(t/2π)/2π. Bas : espacement normalisé de chaque zéro.*

Comptage : 298200 zéros dans le CSV ; formule de Riemann–von Mangoldt (sans terme S(t)) : ≈ 298199.9. Écart +0.1. **[heuristique]** un écart de quelques unités est normal ; un écart de plusieurs dizaines suggère des zéros manquants ou en double. **Ce n'est pas une validation : la complétude se vérifie par Turing–Backlund (verdict en tête de ce rapport).**

![Figure 3 — Espacements normalisés vs GUE (Wigner surmise) et Poisson ; à droite zoom sur la répulsion (échelle log).](figures/gue.png)

*Figure 3 — Espacements normalisés vs GUE (Wigner surmise) et Poisson ; à droite zoom sur la répulsion (échelle log).*

| Grandeur | Mesuré | Référence |
|---|---|---|
| Moyenne de s | 1.0000 | 1 (par construction) |
| Variance de s | 0.1630 | GUE ≈ 0.18 ; Poisson = 1 |
| Part s < 0,1 | 0.081 % | GUE surmise ≈ 0.11 % ; Poisson ≈ 9.5 % |
| Plus petit écart brut | 0.014703 | — |

**[conjecture, Montgomery–Odlyzko]** les espacements suivent la loi GUE ; ici la répulsion est nette. La variance un peu sous 0,18 sur de petites hauteurs relève des corrections de taille finie **[hypothèse]**. Avec peu de zéros (< quelques milliers) l'histogramme est bruité : ne pas sur-interpréter.

![Figure 4 — Débit (zéros/s) au cours du run, à comparer à la fréquence et à la température de PC1 (figure 1).](figures/debit.png)

*Figure 4 — Débit (zéros/s) au cours du run, à comparer à la fréquence et à la température de PC1 (figure 1).*

- Débit instantané non exploitable : le CSV des zéros n'a grossi que sur 0 % des mesures (écriture par worker en fin de calcul) ; se fier au débit moyen du résumé [mesuré]

## 4. Fiche de session

| Élément | Valeur |
|---|---|
| CPU | Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz (4 threads) |
| Gouverneur / turbo | performance / actif (intel_pstate) |
| Git | 72bb991 @ Riemann_Lab_IA (28 fichiers modifiés) |
| Charge / RAM dispo au départ | 0.38 / 11.4 Go |
| Fichier détaillé | `session.md` |

## 5. Interprétation

*Pas encore rédigée. Après relecture des observations, créer `interpretation.md` dans ce dossier puis `zeta-report` : distinguer mesuré / heuristique / hypothèse / conjecture.*

## 6. Limites

- Mesures toutes les ~1 s (SSH) : les pics plus courts échappent ; PC4 (OpenBSD) n'a pas de mesure de RAM.
- Début/fin du run = apparition/disparition du processus détecté, à quelques secondes près.
- Au-delà de 8 000 points par machine, le tracé est sous-échantillonné (les statistiques utilisent toutes les mesures).

---
*rapport.md · MAJ 2026-10-25 · 90 lignes*
