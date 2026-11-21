# ETAT BACKUP ZETA — 2026-11-21

## État en bref
- **Dernière action :** 21/11/2026 : instructions au modèle commun ; `zeta_backup_status.py` (version masquée) gardé ici seulement ; 3 captures copiées en local.
- **Chiffres clés :** Script du dépôt `scripts/zeta_backup_status.py` : 280 lignes, 0 IP en clair. Dernière sauvegarde PC1→PC3 réussie : à confirmer.
- **Point bloquant :** Pas de sauvegarde PC3 tant que le tunnel distant est mort (voir Handoff) ; copie locale ou USB après chaque run long.
- **Prochaine action :** tester la restauration (cible 3-2-1), puis réparer le tunnel à la maison (Handoff du 21/11/2026), rien ne se lance sans OK de hprzeta.

## Fait
| # | Action | Résultat |
|---|---|---|
| 1 | Instructions sur le modèle commun (§1–7) + §8 spécifique | 🟢 5018 car., 8 sections, vérifié serveur |
| 2 | Sauvegarde des anciennes instructions (227 car.) | 🟢 `claude/INSTRUCTIONS_BACKUP_ZETA_avant_20261121.md` (14 lignes) |
| 3 | §8 : restauration testée = opérationnelle, cible 3-2-1, STOP avant écrasement/suppression, --dry-run, 3 skills | 🟢 |
| 4 | Inventaire | 1 doc, 3 fichiers, 1 conversation |

## Inventaire
| Élément | Date | Constat |
|---|---|---|
| zeta_backup_status.py (10 384 car.) | 2026-09-14 | 1 IP en clair ; même script que CLONAGE ZETA, où il est déjà masqué (+1 ligne de note) |
| 3 captures d’écran du 2026-09-14 (21:32, 21:34, 21:34) | 2026-09-14 | Sources du diagnostic backup |

## Décisions proposées
| # | Proposition | Statut |
|---|---|---|
| D1 | Remplacer ici `zeta_backup_status.py` par la version masquée de CLONAGE ZETA | 🟢 fait (copie masquée, 0 IP, vérifié) |
| D2 | Garder le script uniquement dans BACKUP ZETA (son périmètre) et supprimer la copie de CLONAGE ZETA | 🟢 fait (copie CLONAGE supprimée) |
| D3 | Garder les 3 captures ; copie locale dans `pdf/archive/backup_20261121/captures/` via le prompt commun | 🟢 validé → prompt commun |

## Reste ouvert
- Règle `.claude/rules/archive.md` → prompt Claude Code commun.
- CLONAGE D4 (comparer les scripts avec le dépôt) inclut ce script.

<sub>Mis à jour le 2026-11-21 · 34 lignes</sub>
