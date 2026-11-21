# ETAT HR ZETA — 2026-11-21

## État en bref
- **Dernière action :** 21/11/2026 : instructions au modèle commun ; `ORGANISATION_FICHIERS.md` remplacé par la version du wiki (169 lignes, MAJ 18/10), déposée dans `A_DEPOSER/`.
- **Chiffres clés :** Production **V17** ; dernier run mesuré (07/11/2026, distribué PC1+PC2) : T=10⁶, 1 747 146 zéros (attendus 1 747 144), Turing COMPLET.
- **Point bloquant :** Aucun point bloquant propre au projet.
- **Prochaine action :** règle `.claude/rules/cours.md` créée ; contenu pédagogique à reprendre : à confirmer avec hprzeta.

## Fait
| # | Action | Résultat |
|---|---|---|
| 1 | Instructions sur le modèle commun (§1–7) + §8 spécifique | 🟢 5458 car., 8 sections, vérifié serveur |
| 2 | Sauvegarde des anciennes instructions (5138 car.) | 🟢 `claude/INSTRUCTIONS_HR_ZETA_avant_20261121.md` (121 lignes) |
| 3 | §8 : Objectif 1 (calcul industriel, millions de zéros), Objectif 2, pédagogie, 7 skills | 🟢 |
| 4 | Inventaire | 1 doc, 0 fichier, 58 conversations |
| 5 | Valeurs sensibles (IP, MAC, DDNS, clés, e-mails, /home) | 🟢 aucune dans ORGANISATION_FICHIERS.md |

## Écarts corrigés par la migration
| Ancien texte | Nouveau |
|---|---|
| « 10 000 premiers zéros » | Échelle industrielle (millions de zéros), comme les préférences du compte |
| Adresse `[E-MAIL]` (faute de frappe) | Retirée des instructions : l'adresse publique reste dans les préférences du compte |
| Deux sections « 6. Langue » | Fusionnées dans §7 du modèle |

## Inventaire
| Fichier | Taille | Date | Constat |
|---|---|---|---|
| ORGANISATION_FICHIERS.md | 8707 car., 150 lignes | 2026-06-03 | Copie d'une page du wiki (branche master) ; peut-être périmée |

## Décisions proposées
| # | Proposition | Statut |
|---|---|---|
| D1 | Remplacer `ORGANISATION_FICHIERS.md` par la version actuelle du wiki (diff via prompt commun), puis supprimer l'ancienne copie | 🟢 validé → prompt commun |

## Reste ouvert
- Règle `.claude/rules/cours.md` (commune MATH + HR) → prompt Claude Code commun.

<sub>Mis à jour le 2026-11-21 · 38 lignes</sub>
