# ETAT — projet CLONAGE ZETA

## État en bref
- **Dernière action :** 21/11/2026 : instructions au modèle commun ; clone confirmé fonctionnel et démarrable par hprzeta ; 45 captures sur 45 retrouvées sur PC1.
- **Chiffres clés :** Dépôt : `zeta_backup_toshiba.sh` 900 lignes (v2.4, 10/10) contre 271 dans claude.ai ; `backup_cluster_map.sh` 329 lignes contre 330.
- **Point bloquant :** Ne pas démarrer le clone tant que le tunnel est mort ; restauration inverse (options 8/9/10) jamais testée en réel.
- **Prochaine action :** R2, remplir le journal des erreurs (conversations de juin à octobre) ; retrait des captures du projet claude.ai : décision de hprzeta.

> Rangé sous `claude/ETAT_CLONAGE_ZETA_20261121.md`. Point de départ de toute session (instructions §3.1). Contexte détaillé des sessions précédentes : `contexte_claudeai_20261010.md`.

## Objet

Clone fidèle et démarrable du système de PC1 sur SSD externe USB 3, testé, pour reprendre sans perte en cas de panne du disque local ; scripts de sauvegarde et test de restauration.

## Fait

| Date | Quoi |
|---|---|
| 21/06/2026 | Analyse et plan d'action ; dépannage du démarrage USB/UEFI du Samsung (captures dans le projet) |
| 25/08 → 10/10/2026 | Mise à jour du clonage, labellisation et boot (PC4, Toshiba), configuration du clonage SSD, test de restauration Toshiba |
| 18/10/2026 | Dernière conversation : message d'erreur de clonage (issue non reprise ici) |
| 21/11/2026 | Instructions mises au modèle commun ; ancienne version sauvegardée (`claude/INSTRUCTIONS_CLONAGE_ZETA_avant_20261121.md`) |
| 21/11/2026 | Inventaire : 4 documents (1 contexte, 2 `.sh`, 1 `.py`), 47 captures (38 PNG, 8 JPG, 1 PDF ; 38 Mo), 0 doublon ; 🔴 3 adresses IP dans `zeta_backup_status.py` |

## Journal des erreurs (à ne pas reproduire)

À compléter à chaque erreur : date, commande, cause, correction. Repris des conversations : voir `contexte_claudeai_20261010.md`.

## Mise à jour 2026-11-21 (BACKUP ZETA)
- `zeta_backup_status.py` déplacé dans BACKUP ZETA (version masquée) ; copie supprimée ici.

## Reste ouvert

| N° | Point | Statut |
|---|---|---|
| R1 | Clone fonctionnel et démarrable (confirmé par hprzeta le 21/11/2026) | 🟢 fait |
| R2 | Remplir le journal des erreurs à partir des conversations de juin à octobre | à faire |
| R3 | Règle Claude Code `.claude/rules/clone.md` | prompt commun en fin de migration |

## Décisions

| N° | Décision | Statut |
|---|---|---|
| D1 | Instructions selon le modèle commun ; dossier `pdf/clone/audit_clone_<AAAAMMJJ>/` | adoptée 21/11 |
| D2 | Masquer les 3 adresses IP de `zeta_backup_status.py` par des marqueurs `[IP-…]` | 🟢 fait 21/11 (1 adresses distinctes masquées) |
| D3 | 47 captures (38 Mo) : les retirer du projet après vérification de leur présence sur PC1 (comme pour ZETA FORMATION) | accord 21/11 ; vérification sur PC1 dans le prompt commun de fin de migration |
| D4 | Scripts `.sh` / `.py` : vérifier que la version du dépôt est identique ou plus récente, puis ne garder ici que le contexte | accord 21/11 ; prompt commun de fin de migration |

---
<sub>Mis à jour le 2026-11-21 · 50 lignes</sub>
