# Rapport de monitoring — run compute_zeros_v16

Légende : **[mesuré]** = chiffre lu dans les données ; **[heuristique]** / **[hypothèse]** = interprétation non vérifiée ; **[conjecture]** = résultat non démontré.

Validation Turing–Backlund : verdict introuvable (journal `execution_*.log` absent ou illisible) [non vérifié].

## 1. Résumé

| Grandeur | Valeur |
|---|---|
| Run | 20261025_193903_compute_zeros_v16  (auto) |
| Début / fin | 2026-10-25 19:39:03 → 19:40:04 |
| Durée | 1min01s |
| Commande (extrait) | `/home/riemann/projet_zeta/zeta_env/bin/python /home/riemann/projet_zeta/src/calculs/optimi` |
| Code retour | inconnu (run non lancé par le lanceur) |
| Turbo CPU début → fin | ? → ? |
| CSV des zéros | `introuvable` |
| Turing–Backlund | inconnu |

## 2. Machines pendant le run

![Figure 1 — Température, fréquence, charge et RAM des 5 machines (1 mesure/s).](figures/metrics.png)

*Figure 1 — Température, fréquence, charge et RAM des 5 machines (1 mesure/s).*

| Machine | Valides | T moy °C | T max °C | % ≥ 75 °C | MHz min–max | load max | RAM max % |
|---|---|---|---|---|---|---|---|
| PC1 zeta-lab | 100 % | 72.7 | 82.0 | 24 | 3000–3500 | 5.69 | 40.1 |
| PC2 zeta-calc-second | 100 % | 32.9 | 34.0 | 0 | 2863–2992 | 0.24 | 17.3 |
| PC3 zeta-backup | 100 % | 33.2 | 34.0 | 0 | 2100–2700 | 0.00 | 15.2 |
| PC4 zeta-secure | 100 % | 45.5 | 46.0 | 0 | 1800–1800 | 0.02 | — |
| PC5 zeta-monitor | 100 % | 54.0 | 54.6 | 0 | 1297–1299 | 1.03 | 19.3 |

### Observations

- PC1 : température max 82.0 °C, 24 % du temps ≥ 75 °C (seuil d'avertissement) [mesuré]

## 3. Zéros calculés

CSV des zéros introuvable ou trop court : sections 3 non générées. Relancer `zeta-report` après `zeta-run-hint NOM CSV`.

## 5. Interprétation

*Pas encore rédigée. Après relecture des observations, créer `interpretation.md` dans ce dossier puis `zeta-report` : distinguer mesuré / heuristique / hypothèse / conjecture.*

## 6. Limites

- Mesures toutes les ~1 s (SSH) : les pics plus courts échappent ; PC4 (OpenBSD) n'a pas de mesure de RAM.
- Début/fin du run = apparition/disparition du processus détecté, à quelques secondes près.
- Au-delà de 8 000 points par machine, le tracé est sous-échantillonné (les statistiques utilisent toutes les mesures).

---
*rapport.md · MAJ 2026-10-25 · 53 lignes*
