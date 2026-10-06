# AGENTS.md — Contrat Claude Code ↔ Codex ↔ Ollama (Riemann_Lab)

> Source de vérité pour les règles projet : `CLAUDE.md` (racine). Ce fichier ne le duplique pas,
> il définit comment Claude Code, Codex et Ollama se répartissent le travail et se transmettent
> le contexte entre eux.

## 1. Répartition des rôles

| Agent | Rôle privilégié | Ne fait jamais |
|---|---|---|
| **Claude Code** | Architecture, refactoring, rédaction mathématique/wiki, orchestration, gardien de `CLAUDE.md` et des skills `.claude/skills/` | Modifier `c_modules/` sans repasser par le skill `phase-c-illinois` |
| **Codex** | Génération de code algorithmique expérimental, tests unitaires, scripts C/`arb_C` | Modifier `CLAUDE.md`, pousser directement sur `main`, toucher `.claude/skills/` sans validation Claude Code |
| **Ollama (mathstral, local)** | Premier filtre / conjectures exploratoires offline avant d'solliciter Claude Code ou Codex (économie de tokens) | Servir de source de vérité — toute réponse Ollama/RAG doit être vérifiée (voir §3) |

## 2. Règles communes (héritées de `CLAUDE.md` et des skills existants)

- **Point d'arrêt obligatoire** avant tout run `T > 50k` : validation explicite de l'utilisateur avant de lancer.
- **Jamais de secret en clair** (token, clé API) dans un commit, `.mcp.json` inclus — toujours via variable d'environnement. Passer par le skill `riemann-security-review` avant tout push touchant `scripts/`, `.mcp.json` ou `c_modules/`.
- **`docs/`** sert GitHub Pages — ne jamais y déplacer ou renommer un fichier sans vérifier l'impact sur le site publié.
- **Le RAG BrainVault** (`/mnt/vault_rag`) est une source de contexte, pas une source de vérité : toute valeur numérique qu'il retourne doit être recoupée avec le fichier source cité (voir `scripts/rag_query.py`, garde-fou `valeurs_non_ancrees()`).

## 3. Protocole de passation (handoff)

Toute tâche confiée d'un agent à l'autre passe par `handoff/` :
- `handoff/claude_to_codex.md` — Claude Code confie une tâche de code à Codex
- `handoff/codex_to_claude.md` — Codex rend la main à Claude Code (revue, intégration, doc)

Chaque fichier est réécrit à chaque passation (pas d'historique empilé — l'historique vit dans `JOURNAL.md` du wiki).

## 4. Repères rapides

| Besoin | Où regarder |
|---|---|
| Règles permanentes, formules canoniques | `CLAUDE.md` |
| Historique et leçons Phase C (Illinois/Arb) | skill `.claude/skills/phase-c-illinois/` |
| Contenu mathématique, KaTeX, wiki | skill `.claude/skills/riemann-lab/` |
| Checklist avant commit | skill `.claude/skills/riemann-code-review/` |
| Checklist sécurité | skill `.claude/skills/riemann-security-review/` |
| Build Phase C | `cd src/calculs/optimisation/c_modules && make && python3 test_illinois.py` |
| Lancer un run | `scripts/zeta_run.sh` (encapsule turbo_on/off) |
| Interroger le RAG BrainVault | `python scripts/rag_query.py --k 8 "<question>"` (vérifier `mountpoint /mnt/vault_rag` avant) |

---
*AGENTS.md créé le 27/09/2026 — Vague V1 du plan de mutualisation skills/MCP.*
