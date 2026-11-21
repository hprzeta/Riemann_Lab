# ETAT — projet VAULT ZETA

## État en bref
- **Dernière action :** 21/11/2026 : projet créé par claude.ai ; règle `.claude/rules/vault.md` (`cb6901a`) ; `etat_rag_brainvault_20260704.md` copié depuis MONITO ZETA.
- **Chiffres clés :** Coffre `/mnt/vault_rag` (SSD Micron 256 Go, ext4, en service depuis le 22/06/2026) ; ChromaDB intact ; taille du corpus : à confirmer.
- **Point bloquant :** Aucun point bloquant ; l'état actuel du coffre n'est pas encore déposé dans le projet (R1).
- **Prochaine action :** R1, déposer l'état du coffre et les guides RAG ; R3, jeu de questions à réponse connue pour évaluer le RAG.

> Rangé sous `claude/ETAT_VAULT_ZETA_20261121.md`. Point de départ de toute session (instructions §3.1).

## Objet

Coffre de connaissances BrainVault (RAG) du projet zêta : corpus sourcé dans `/mnt/vault_rag`, indexation locale (ChromaDB, LlamaIndex), modèle local (Ollama, Mathstral), base de l'agent de l'Objectif 2.

## Fait

| Date | Quoi |
|---|---|
| 21/11/2026 | Projet créé par claude.ai (décision de hprzeta) ; instructions conformes au modèle commun, §8 propre au coffre |

## Reste ouvert

| N° | Point | Statut |
|---|---|---|
| R1 | Déposer ici l'état actuel du coffre (`etat_rag_brainvault_*.md`, guides RAG) | à faire |
| R2 | Règle Claude Code `.claude/rules/vault.md` créée (commit `cb6901a`) | 🟢 fait |
| R3 | Jeu de questions à réponse connue pour évaluer le RAG | à faire |

## Décisions

| N° | Décision | Statut |
|---|---|---|
| D1 | Dossier du projet : `md/vault` et `pdf/vault` ; rapports `pdf/vault/audit_vault_<AAAAMMJJ>/` | adoptée 21/11 |
| D2 | Une réponse du RAG n'est jamais un résultat : recoupement avec la source citée | adoptée 21/11 |

---
<sub>Mis à jour le 2026-11-21 · 37 lignes</sub>
