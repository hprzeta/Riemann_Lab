# ETAT — projet MATOS ZETA

## État en bref
- **Dernière action :** 21/11/2026 : instructions créées au modèle commun ; recommandations SSD externe ajoutées depuis ZETA FORMATION.
- **Chiffres clés :** SSD 3,8 To rejeté définitivement (f3probe : 0 octet utilisable, retourné au vendeur le 21/06/2026) ; Micron 256 Go en service pour le vault.
- **Point bloquant :** R1 : choix du 21/06 et du 08/07 (SSD, caméras, onduleur) achetés, installés ou abandonnés : à confirmer avec hprzeta.
- **Prochaine action :** R2, vérifier l'inventaire matériel du wiki (STACK.md, Architecture-Cluster-Zeta) ; aucun achat par Claude.

> Rangé sous `claude/ETAT_MATOS_ZETA_20261121.md`. Point de départ de toute session (instructions §3.1).

## Objet

Matériel du projet zêta : machines PC1 à PC5, stockage, alimentation et onduleur, réseau physique, domotique liée au projet (caméras de surveillance).

## Fait

| Date | Quoi |
|---|---|
| 21/06/2026 | Recommandations SSD externe pour le vault (Objectif 2), après le disque à fausse capacité : Samsung T7 Shield 2 To ou Crucial X9 Pro 2 To, achat en circuit fiable, test `f3probe` à réception (`Recommandations_SSD_externe_RiemannLab.md` ; PDF en local dans `pdf/matos/`) |
| 08/07/2026 | 3 conversations : caméras de surveillance extérieure avec contrôle à distance, onduleur autonome (résultats non repris ici) |
| 21/11/2026 | Instructions créées selon le modèle commun (le projet n'en avait pas) |
| 21/11/2026 | Inventaire : 0 document au départ ; recommandations SSD ajoutées depuis ZETA FORMATION |

## Reste ouvert

| N° | Point | Statut |
|---|---|---|
| R1 | Résumer ici les choix faits (SSD du 21/06, caméras et onduleur du 08/07) : achetés, installés, abandonnés ? | à faire avec hprzeta |
| R2 | Vérifier que l'inventaire matériel du wiki (STACK.md, Architecture-Cluster-Zeta) est à jour | à faire |
| R3 | Règle Claude Code `.claude/rules/matos.md` | prompt commun en fin de migration |

## Décisions

| N° | Décision | Statut |
|---|---|---|
| D1 | Instructions selon le modèle commun ; dossier `pdf/matos/audit_matos_<AAAAMMJJ>/` | adoptée 21/11 |
| D2 | Tout disque est vérifié (f3probe, smartctl) avant usage ; aucun achat par Claude | adoptée 21/11 |

---
<sub>Mis à jour le 2026-11-21 · 40 lignes</sub>
