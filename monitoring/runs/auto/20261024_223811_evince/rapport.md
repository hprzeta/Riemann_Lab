# Rapport de monitoring — run evince

Légende : **[mesuré]** = chiffre lu dans les données ; **[heuristique]** / **[hypothèse]** = interprétation non vérifiée ; **[conjecture]** = résultat non démontré.

Validation Turing–Backlund : verdict introuvable (journal `execution_*.log` absent ou illisible) [non vérifié].

## 1. Résumé

| Grandeur | Valeur |
|---|---|
| Run | 20261024_223811_evince  (auto) |
| Début / fin | 2026-10-24 22:38:11 → 22:38:39 |
| Durée | 0min28s |
| Commande (extrait) | `/usr/bin/evince /home/riemann/projet_zeta/monitoring/runs/auto/20261024_221053_test_comput` |
| Code retour | inconnu (run non lancé par le lanceur) |
| Turbo CPU début → fin | ? → ? |
| CSV des zéros | `introuvable` |
| Turing–Backlund | inconnu |

## 2. Machines pendant le run

![Figure 1 — Température, fréquence, charge et RAM des 5 machines (1 mesure/s).](figures/metrics.png)

*Figure 1 — Température, fréquence, charge et RAM des 5 machines (1 mesure/s).*

| Machine | Valides | T moy °C | T max °C | % ≥ 75 °C | MHz min–max | load max | RAM max % |
|---|---|---|---|---|---|---|---|
| PC1 zeta-lab | 100 % | 40.2 | 59.0 | 0 | 800–3500 | 1.38 | 26.0 |
| PC2 zeta-calc-second | 100 % | 32.4 | 33.0 | 0 | 2992–2992 | 0.05 | 18.3 |
| PC3 zeta-backup | 100 % | 33.9 | 34.0 | 0 | 2100–2700 | 0.00 | 15.2 |
| PC4 zeta-secure | 100 % | 42.3 | 43.0 | 0 | 1800–1800 | 0.03 | — |
| PC5 zeta-monitor | 100 % | 51.9 | 52.0 | 0 | 1297–1299 | 0.03 | 18.2 |

### Observations

- Rien d'anormal détecté sur les seuils automatiques [mesuré].

## 3. Zéros calculés

CSV des zéros introuvable ou trop court : sections 3 non générées. Relancer `zeta-report` après `zeta-run-hint NOM CSV`.

## 5. Interprétation

*Pas encore rédigée. Après relecture des observations, créer `interpretation.md` dans ce dossier puis `zeta-report` : distinguer mesuré / heuristique / hypothèse / conjecture.*

## 6. Limites

- Mesures toutes les ~1 s (SSH) : les pics plus courts échappent ; PC4 (OpenBSD) n'a pas de mesure de RAM.
- Début/fin du run = apparition/disparition du processus détecté, à quelques secondes près.
- Au-delà de 8 000 points par machine, le tracé est sous-échantillonné (les statistiques utilisent toutes les mesures).

---
*rapport.md · MAJ 2026-10-24 · 53 lignes*
