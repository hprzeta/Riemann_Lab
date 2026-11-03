# Rapport de monitoring — run T20000

Légende : **[mesuré]** = chiffre lu dans les données ; **[heuristique]** / **[hypothèse]** = interprétation non vérifiée ; **[conjecture]** = résultat non démontré.

Validation Turing–Backlund : verdict introuvable (journal `execution_*.log` absent ou illisible) [non vérifié].

## 1. Résumé

| Grandeur | Valeur |
|---|---|
| Run | 20261025_182706_T20000  (prod) |
| Début / fin | 2026-10-25 18:27:06 → 18:28:17 |
| Durée | 1min11s |
| Commande (extrait) | `bash -c printf '20000\nO\n' \| python /home/riemann/projet_zeta/src/calculs/optimisation/co` |
| Code retour | 143 |
| Turbo CPU début → fin | actif (intel_pstate) → actif (intel_pstate) |
| CSV des zéros | `introuvable` |
| Turing–Backlund | inconnu |

## 2. Machines pendant le run

![Figure 1 — Température, fréquence, charge et RAM des 5 machines (1 mesure/s).](figures/metrics.png)

*Figure 1 — Température, fréquence, charge et RAM des 5 machines (1 mesure/s).*

| Machine | Valides | T moy °C | T max °C | % ≥ 75 °C | MHz min–max | load max | RAM max % |
|---|---|---|---|---|---|---|---|
| PC1 zeta-lab | 100 % | 54.7 | 71.0 | 0 | 3500–3502 | 1.02 | 28.7 |
| PC2 zeta-calc-second | 100 % | 33.1 | 35.0 | 0 | 2992–2992 | 0.00 | 16.8 |
| PC3 zeta-backup | 100 % | 33.0 | 33.5 | 0 | 2100–2100 | 0.04 | 15.2 |
| PC4 zeta-secure | 100 % | 47.2 | 52.0 | 0 | 1800–1800 | 0.06 | — |
| PC5 zeta-monitor | 100 % | 53.4 | 53.8 | 0 | 1297–1299 | 0.09 | 18.8 |

### Observations

- PC1 : fréquence médiane 3500 MHz sur le 1ᵉʳ cinquième du run, 3500 MHz sur le dernier [mesuré]

## 3. Zéros calculés

CSV des zéros introuvable ou trop court : sections 3 non générées. Relancer `zeta-report` après `zeta-run-hint NOM CSV`.

## 4. Fiche de session

| Élément | Valeur |
|---|---|
| CPU | Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz (4 threads) |
| Gouverneur / turbo | performance / actif (intel_pstate) |
| Git | 72bb991 @ Riemann_Lab_IA (43 fichiers modifiés) |
| Charge / RAM dispo au départ | 0.76 / 11.4 Go |
| Fichier détaillé | `session.md` |

## 5. Interprétation

*Pas encore rédigée. Après relecture des observations, créer `interpretation.md` dans ce dossier puis `zeta-report` : distinguer mesuré / heuristique / hypothèse / conjecture.*

## 6. Limites

- Mesures toutes les ~1 s (SSH) : les pics plus courts échappent ; PC4 (OpenBSD) n'a pas de mesure de RAM.
- Début/fin du run = apparition/disparition du processus détecté, à quelques secondes près.
- Au-delà de 8 000 points par machine, le tracé est sous-échantillonné (les statistiques utilisent toutes les mesures).

---
*rapport.md · MAJ 2026-10-25 · 63 lignes*
