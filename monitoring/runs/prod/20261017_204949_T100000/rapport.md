# Rapport de monitoring — run T100000

Légende : **[mesuré]** = chiffre lu dans les données ; **[heuristique]** / **[hypothèse]** = interprétation non vérifiée ; **[conjecture]** = résultat non démontré.

## 1. Résumé

| Grandeur | Valeur |
|---|---|
| Run | 20261017_204949_T100000  (prod) |
| Début / fin | 2026-10-17 20:49:49 → 20:52:06 |
| Durée | 2min17s |
| Commande (extrait) | `bash -c printf '100000\nO\n' \| python /home/riemann/projet_zeta/src/calculs/optimisation/c` |
| Code retour | 0 |
| Turbo CPU début → fin | actif (intel_pstate) → actif (intel_pstate) |
| CSV des zéros | `introuvable` |

## 2. Machines pendant le run

![Figure 1 — Température, fréquence, charge et RAM des 5 machines (1 mesure/s).](figures/metrics.png)

*Figure 1 — Température, fréquence, charge et RAM des 5 machines (1 mesure/s).*

| Machine | Valides | T moy °C | T max °C | % ≥ 75 °C | MHz min–max | load max | RAM max % |
|---|---|---|---|---|---|---|---|
| PC1 zeta-lab | 100 % | 73.2 | 81.0 | 44 | 2900–3500 | 10.85 | 39.5 |
| PC2 zeta-calc-second | 100 % | 25.1 | 27.0 | 0 | 2863–2992 | 0.01 | 16.9 |
| PC3 zeta-backup | 100 % | 29.9 | 30.4 | 0 | 2100–2100 | 0.11 | 15.2 |
| PC4 zeta-secure | 100 % | 34.9 | 36.0 | 0 | 1800–1800 | 0.09 | — |
| PC5 zeta-monitor | 100 % | 45.5 | 45.8 | 0 | 1297–1299 | 0.15 | 17.7 |

### Observations

- PC1 : température max 81.0 °C, 44 % du temps ≥ 75 °C (seuil d'avertissement) [mesuré]
- PC1 : fréquence médiane 3500 MHz sur le 1ᵉʳ cinquième du run, 3500 MHz sur le dernier [mesuré]

## 3. Zéros calculés

CSV des zéros introuvable ou trop court : sections 3 non générées. Relancer `zeta-report` après `zeta-run-hint NOM CSV`.

## 4. Fiche de session

| Élément | Valeur |
|---|---|
| CPU | Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz (4 threads) |
| Gouverneur / turbo | performance / actif (intel_pstate) |
| Git | d275736 @ Riemann_Lab_IA (22 fichiers modifiés) |
| Charge / RAM dispo au départ | 3.79 / 9.8 Go |
| Fichier détaillé | `session.md` |

## 5. Interprétation

*Pas encore rédigée. Après relecture des observations, créer `interpretation.md` dans ce dossier puis `zeta-report` : distinguer mesuré / heuristique / hypothèse / conjecture.*

## 6. Limites

- Mesures toutes les ~1 s (SSH) : les pics plus courts échappent ; PC4 (OpenBSD) n'a pas de mesure de RAM.
- Début/fin du run = apparition/disparition du processus détecté, à quelques secondes près.
- Au-delà de 8 000 points par machine, le tracé est sous-échantillonné (les statistiques utilisent toutes les mesures).

---
*rapport.md · MAJ 2026-10-17 · 61 lignes*
