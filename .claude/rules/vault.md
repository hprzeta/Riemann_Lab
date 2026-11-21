---
paths:
  - "md/vault/**"
  - "pdf/vault/**"
---
# Projet claude.ai VAULT ZETA
- Point de départ : l'ETAT le plus récent (`claude/ETAT_VAULT_ZETA_*.md` dans le projet claude.ai).
- Coffre : `/mnt/vault_rag` (chromadb/, corpus/, llamaindex_cache/, agent_logs/).
- Toute pièce du corpus a une source et un statut ; une réponse du RAG ou d'Ollama est recoupée avant tout usage (skill riemann-agent-bridge).
- Rapports : `pdf/vault/audit_vault_<AAAAMMJJ>/` + `A_DEPOSER/`.
- Skills : riemann-agent-bridge, riemann-literature-scout, riemann-proof-status.
