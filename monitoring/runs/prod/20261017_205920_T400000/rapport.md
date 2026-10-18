# Rapport de monitoring — run T400000

Légende : **[mesuré]** = chiffre lu dans les données ; **[heuristique]** / **[hypothèse]** = interprétation non vérifiée ; **[conjecture]** = résultat non démontré.

**⚠ ALERTE — Validation Turing–Backlund : ❌ INCOMPLET** — 5 zéro(s) manquant(s) [mesuré, lu dans execution_v16_T400000_20261017_205921.log]. Les comptages de ce run ne sont PAS complets : ne pas utiliser ces zéros pour une statistique sans les compléter.

- `T=50372.17  calc= 64052  attendus= 64052  delta=   +0  ✅ OK`
- `T=114227.16  calc=160130  attendus=160128  delta=   -2  ⚠️  SURPLUS +2`
- `T=213326.60  calc=320260  attendus=320258  delta=   -2  ⚠️  SURPLUS +2`
- `T=308000.72  calc=480390  attendus=480394  delta=   +4  ❌ MANQUE 4`
- `T=399999.68  calc=640520  attendus=640525  delta=   +5  ❌ MANQUE 5`

## 1. Résumé

| Grandeur | Valeur |
|---|---|
| Run | 20261017_205920_T400000  (prod) |
| Début / fin | 2026-10-17 20:59:20 → 21:19:59 |
| Durée | 20min39s |
| Commande (extrait) | `bash -c printf '400000\nO\n' \| python /home/riemann/projet_zeta/src/calculs/optimisation/c` |
| Code retour | 0 |
| Turbo CPU début → fin | actif (intel_pstate) → actif (intel_pstate) |
| CSV des zéros | `zeros_v16_T400000_20261017_205921.csv` |
| Turing–Backlund | ❌ INCOMPLET |
| Zéros dans le CSV | 640520  [mesuré] |
| t min → t max | 14.135 → 399999.681 |
| Débit moyen (zéros / durée du run) | 517.0 /s |

## 2. Machines pendant le run

![Figure 1 — Température, fréquence, charge et RAM des 5 machines (1 mesure/s).](figures/metrics.png)

*Figure 1 — Température, fréquence, charge et RAM des 5 machines (1 mesure/s).*

| Machine | Valides | T moy °C | T max °C | % ≥ 75 °C | MHz min–max | load max | RAM max % |
|---|---|---|---|---|---|---|---|
| PC1 zeta-lab | 100 % | 71.0 | 79.0 | 8 | 2900–3500 | 16.27 | 43.2 |
| PC2 zeta-calc-second | 100 % | 25.0 | 27.0 | 0 | 1995–2993 | 0.56 | 17.0 |
| PC3 zeta-backup | 100 % | 29.4 | 31.4 | 0 | 2100–2700 | 0.40 | 15.2 |
| PC4 zeta-secure | 100 % | 34.7 | 37.0 | 0 | 1800–1800 | 0.40 | — |
| PC5 zeta-monitor | 100 % | 45.4 | 46.4 | 0 | 1297–1299 | 0.41 | 18.8 |

### Observations

- PC1 : température max 79.0 °C, 8 % du temps ≥ 75 °C (seuil d'avertissement) [mesuré]
- PC1 : fréquence médiane 3000 MHz sur le 1ᵉʳ cinquième du run, 3100 MHz sur le dernier [mesuré]

## 3. Zéros calculés

![Figure 2 — Haut : zéros par tranche de t (bleu/gris alternés) vs densité théorique ln(t/2π)/2π. Bas : espacement normalisé de chaque zéro.](figures/zeros_tranches.png)

*Figure 2 — Haut : zéros par tranche de t (bleu/gris alternés) vs densité théorique ln(t/2π)/2π. Bas : espacement normalisé de chaque zéro.*

Comptage : 640520 zéros dans le CSV ; formule de Riemann–von Mangoldt (sans terme S(t)) : ≈ 640525.8. Écart -5.8. **[heuristique]** un écart de quelques unités est normal ; un écart de plusieurs dizaines suggère des zéros manquants ou en double. **Ce n'est pas une validation : la complétude se vérifie par Turing–Backlund (verdict en tête de ce rapport).**

![Figure 3 — Espacements normalisés vs GUE (Wigner surmise) et Poisson ; à droite zoom sur la répulsion (échelle log).](figures/gue.png)

*Figure 3 — Espacements normalisés vs GUE (Wigner surmise) et Poisson ; à droite zoom sur la répulsion (échelle log).*

| Grandeur | Mesuré | Référence |
|---|---|---|
| Moyenne de s | 1.0000 | 1 (par construction) |
| Variance de s | 0.1643 | GUE ≈ 0.18 ; Poisson = 1 |
| Part s < 0,1 | 0.087 % | GUE surmise ≈ 0.11 % ; Poisson ≈ 9.5 % |
| Plus petit écart brut | 0.013053 | — |

**[conjecture, Montgomery–Odlyzko]** les espacements suivent la loi GUE ; ici la répulsion est nette. La variance un peu sous 0,18 sur de petites hauteurs relève des corrections de taille finie **[hypothèse]**. Avec peu de zéros (< quelques milliers) l'histogramme est bruité : ne pas sur-interpréter.

![Figure 4 — Débit (zéros/s) au cours du run, à comparer à la fréquence et à la température de PC1 (figure 1).](figures/debit.png)

*Figure 4 — Débit (zéros/s) au cours du run, à comparer à la fréquence et à la température de PC1 (figure 1).*

- Débit instantané non exploitable : le CSV des zéros n'a grossi que sur 0 % des mesures (écriture par worker en fin de calcul) ; se fier au débit moyen du résumé [mesuré]

## 4. Fiche de session

| Élément | Valeur |
|---|---|
| CPU | Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz (4 threads) |
| Gouverneur / turbo | performance / actif (intel_pstate) |
| Git | d275736 @ Riemann_Lab_IA (22 fichiers modifiés) |
| Charge / RAM dispo au départ | 2.38 / 9.7 Go |
| Fichier détaillé | `session.md` |

## 5. Interprétation

*Pas encore rédigée. Après relecture des observations, créer `interpretation.md` dans ce dossier puis `zeta-report` : distinguer mesuré / heuristique / hypothèse / conjecture.*

## 6. Limites

- Mesures toutes les ~1 s (SSH) : les pics plus courts échappent ; PC4 (OpenBSD) n'a pas de mesure de RAM.
- Début/fin du run = apparition/disparition du processus détecté, à quelques secondes près.
- Au-delà de 8 000 points par machine, le tracé est sous-échantillonné (les statistiques utilisent toutes les mesures).

---
*rapport.md · MAJ 2026-10-18 · 96 lignes*
