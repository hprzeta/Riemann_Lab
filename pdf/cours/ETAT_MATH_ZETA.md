# ETAT MATH ZETA — 2026-11-21

## État en bref
- **Dernière action :** 21/11/2026 : instructions au modèle commun ; 8 captures de cours copiées en local (`pdf/cours/cours_math_20261121/captures/`, WebP 1456 px).
- **Chiffres clés :** Production **V17** ; dernier run mesuré (07/11/2026, distribué PC1+PC2) : T=10⁶, 1 747 146 zéros (attendus 1 747 144), Turing COMPLET.
- **Point bloquant :** Aucun point bloquant propre au projet ; les captures 7 et 8 ont la même taille mais un contenu différent.
- **Prochaine action :** règle `.claude/rules/cours.md` créée ; prochaine session de cours : à confirmer avec hprzeta.

## Fait
| # | Action | Résultat |
|---|---|---|
| 1 | Instructions sur le modèle commun (§1–7) + §8 spécifique | 🟢 5463 car., 8 sections, vérifié serveur |
| 2 | Sauvegarde des anciennes instructions | 🟢 `claude/INSTRUCTIONS_MATH_ZETA_avant_20261121.md` |
| 3 | §8 reprend toute la pédagogie d'origine | 🟢 niveaux gradués, démonstrations, limites/contre-exemples, SVG, « PDF » = version VAULT |
| 4 | Inventaire | 0 doc texte (hors sauvegarde), 9 fichiers, 2 conversations |
| 5 | Valeurs sensibles (IP, MAC, DDNS, clés, e-mails) | 🟢 aucune |

## Inventaire des fichiers
| Fichier | Type | Date | Constat |
|---|---|---|---|
| screenzeta1–8.png | image | 2026-09-06 | Captures de cours, sources des explications |
| Formation_Zeta_HR_Riemann_Lab 1.pdf | PDF | 2026-09-13 | Suffixe « 1 » = copie ; version .md présente dans ZETA FORMATION |

## Décisions proposées
| # | Proposition | Statut |
|---|---|---|
| D1 | Supprimer `Formation_Zeta_HR_Riemann_Lab 1.pdf` (doublon du .md de FORMATION, §5 « aucun PDF ») | 🟢 fait (supprimé dans l’UI, vérifié API) |
| D2 | Garder les 8 captures dans le projet ; copie locale dans `pdf/cours/cours_math_20261121/captures/` via prompt commun | 🟢 validé → prompt commun |

## Reste ouvert
- Règle `.claude/rules/cours.md` (commune MATH + HR) → prompt Claude Code commun.

<sub>Mis à jour le 2026-11-21 · 33 lignes</sub>
