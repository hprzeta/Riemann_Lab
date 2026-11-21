# ETAT — projet OPTIMISATION ZETA

## État en bref
- **Dernière action :** 21/11/2026 : instructions au modèle commun ; 24 extraits DeepSeek regroupés en un seul `.md` ; projet renommé OPTIMISATION ZETA.
- **Chiffres clés :** Production **V17** ; dernier run mesuré (07/11/2026, distribué PC1+PC2) : T=10⁶, 1 747 146 zéros (attendus 1 747 144), Turing COMPLET. Débits mesurés : PC1 ≈ 506 z/s, PC2 ≈ 97 z/s ; T=10⁵ : 138 069 zéros en 1,61 min (1 434 z/s, date à confirmer).
- **Point bloquant :** Rescan décalé V17 : gain non mesuré ; synthèse de « Analyse1 optim » (13/09) jamais reprise (R1).
- **Prochaine action :** R2, confronter les recommandations de septembre à la production V17 (benchmark avant/après).

> Rangé sous `claude/ETAT_OPTIMISATION_ZETA_20261121.md`. Point de départ de toute session (instructions §3.1).

## Objet

Auditer les recommandations d'autres IA (Kimi, Grok, DeepSeek…) sur le code de calcul, les procédures et les processus, et ne retenir que ce qui optimise vraiment l'Étape 1 avant l'Étape 2 (VAULT et IA locale).

## Fait

| Date | Quoi |
|---|---|
| 12/09/2026 | Dépôt des recommandations (DeepSeek, Kimi, Grok) et de 24 extraits Python de DeepSeek |
| 13/09/2026 | Conversation « Analyse1 optim » (résultats non repris ici : à résumer à la prochaine session) |
| 21/11/2026 | Instructions mises au modèle commun ; ancienne version sauvegardée (`claude/INSTRUCTIONS_OPTIMISATION_ZETA_avant_20261121.md`) |
| 21/11/2026 | Inventaire : 29 documents (4 `.md`, 1 liste sans extension, 24 `.py` de 0 à 1 ko), 0 doublon, 0 valeur sensible |

## Reste ouvert

| N° | Point | Statut |
|---|---|---|
| R1 | Reprendre la synthèse de « Analyse1 optim » (13/09) dans un `.md` du projet | à faire |
| R2 | Confronter les recommandations à la production actuelle (V17) : beaucoup datent de septembre | à faire |
| R3 | Règle Claude Code `.claude/rules/optimisation.md` | prompt commun en fin de migration |

## Décisions

| N° | Décision | Statut |
|---|---|---|
| D1 | Instructions selon le modèle commun ; dossier `pdf/optimisation/audit_optimisation_<AAAAMMJJ>/` | adoptée 21/11 |
| D2 | Regrouper les 24 extraits `deepseek_python_*.py` dans un seul `extraits_deepseek_20260912.md`, puis retirer les 24 fichiers | 🟢 fait 21/11 (24 → 1 fichier, contenu vérifié) |
| D3 | Renommer le projet « OTIMISATION ZETA » en « OPTIMISATION ZETA » | 🟢 fait 21/11 |
| D4 | `ZETA_Dossier_MATH_VAULT.md` relève de VAULT ZETA : le copier là-bas (il reste ici comme source) | 🟢 fait 21/11 (copie dans VAULT ZETA) |

---
<sub>Mis à jour le 2026-11-21 · 42 lignes</sub>
