---
name: riemann-agent-bridge
description: |
  Coordination multi-agents pour le projet `Riemann_Lab` de hprzeta — répartition des rôles entre Claude Code, Codex et Ollama (Mathstral local), et protocole de passation de tâches.

  Utiliser ce skill dès que l'utilisateur demande de :
  - Confier une tâche de code expérimental à Codex, ou récupérer/intégrer le travail rendu par Codex
  - Rédiger ou lire un fichier de passation dans `handoff/` (`claude_to_codex.md`, `codex_to_claude.md`)
  - Décider qui (Claude Code / Codex / Ollama) doit traiter une tâche donnée
  - Vérifier qu'une réponse issue d'Ollama ou du RAG BrainVault est bien recoupée avant d'être utilisée
  - Toute question sur `AGENTS.md`, le contrat inter-agents, ou l'articulation Claude Code ↔ Codex

  Déclencher aussi pour : point d'arrêt avant un run `T > 50k`, règle "pas de secret en clair", garde-fou anti-hallucination du RAG.
---

# Riemann Agent Bridge Skill

Skill de coordination pour le protocole multi-agents décrit dans `AGENTS.md` (racine du dépôt,
branche `Riemann_Lab_IA`). Ce skill ne duplique pas `AGENTS.md` — il l'exploite : avant toute
tâche impliquant plusieurs agents, relire `AGENTS.md` puis appliquer les règles ci-dessous.

> Source de vérité projet : `CLAUDE.md`. Source de vérité multi-agents : `AGENTS.md`.
> Ce skill est la couche d'exécution : il dit *comment* Claude Code applique ces contrats.

---

## 1. Répartition des rôles (rappel `AGENTS.md` §1)

| Agent | Rôle privilégié | Interdits |
|---|---|---|
| **Claude Code** | Architecture, refactoring, rédaction mathématique/wiki, orchestration, gardien de `CLAUDE.md` et de `.claude/skills/` | Modifier `c_modules/` sans passer par `phase-c-illinois` |
| **Codex** | Code algorithmique expérimental, tests unitaires, scripts C/`arb_C` | Modifier `CLAUDE.md`, push direct sur `main`, toucher `.claude/skills/` sans validation Claude Code |
| **Ollama (mathstral, local)** | Premier filtre / conjectures exploratoires offline, économie de tokens | Faire office de source de vérité — toute sortie doit être vérifiée (§3) |

**Règle de décision rapide** : si la tâche touche à la rigueur mathématique, au wiki, à l'orchestration
ou aux skills → Claude Code. Si elle consiste à écrire/tester un algorithme isolé et bien spécifié →
proposer une passation vers Codex. Si c'est une exploration ouverte à faible enjeu (brainstorm de
conjecture, reformulation) → passer d'abord par Ollama local avant de solliciter un agent distant.

## 1bis. Accès à des modèles distants via OmniRoute (MCP)

Le serveur MCP `omniroute` (`.mcp.json`) donne accès à des modèles tiers (DeepSeek, NVIDIA
Nemotron, etc.) via l'outil `omniroute_route_request` — un canal supplémentaire pour un second avis
ou une exploration à faible enjeu, au même titre qu'Ollama local (§3), mais avec des modèles plus
gros et hébergés à distance.

**Prérequis obligatoires (sinon tout appel échoue silencieusement en `fetch failed`) :**
- `.mcp.json` doit pointer sur le binaire Node 22 explicite (nvm), jamais `node` du PATH système
  (v18 système incompatible, `engines.node: >=22.22.2` requis) — voir `.mcp.json.example`.
- Le **backend HTTP OmniRoute (port 20128) doit tourner en service** : `systemctl --user status
  omniroute`. C'est un processus séparé du serveur MCP stdio — celui-ci n'est qu'une façade qui
  délègue tout appel réel (y compris `route_request`) à ce backend local. S'il n'est pas actif :
  `systemctl --user start omniroute` (unit dans `~/.config/systemd/user/omniroute.service`, à créer
  manuellement si absente — **l'outil Write de Claude Code est bloqué sur ce chemin par le
  classificateur de permission** ; demander à hprzeta de créer/lancer via `!`).
- Toujours préfixer le modèle par son provider (`nvidia/nemotron-3-super-120b-a12b`, pas
  `nemotron-3-super` seul) — sinon `400 Ambiguous model`.

**Limitation connue (non bloquante)** : `omniroute_get_health` / `omniroute_check_quota` /
`omniroute_list_models_catalog` peuvent renvoyer `403 AUTH_001 Invalid management token` (token de
gestion à régénérer côté dashboard OmniRoute) — n'empêche pas `route_request` de fonctionner pour
les providers déjà connectés (ex. NVIDIA). aimlapi/DeepSeek non configuré (`401 No active
credentials`) — utiliser un provider déjà connecté tant que ce n'est pas arbitré.

Toute réponse d'un modèle OmniRoute suit la même règle que pour Ollama (§3) : **source de
contexte, pas source de vérité** — à recouper avant citation.

## 2. Protocole de passation (`handoff/`)

Deux fichiers, réécrits à chaque passation (pas d'historique empilé — l'historique vit dans
`JOURNAL.md` du wiki) :

- **`handoff/claude_to_codex.md`** — sections : Tâche, Contexte, Entrée, Attendu, Contraintes,
  Test de validation.
- **`handoff/codex_to_claude.md`** — sections : Tâche reçue, Ce qui a été fait, Résultats des
  tests, Points ouverts / à vérifier par Claude Code, Fichiers modifiés.

Avant de rédiger une passation vers Codex : vérifier que l'entrée et le format de sortie attendu
sont sans ambiguïté (Codex n'a pas le contexte conversationnel — tout doit être dans le fichier).
Avant d'intégrer un retour de Codex : relire `riemann-code-review` sur les fichiers modifiés,
ne jamais committer directement le travail de Codex sans cette revue.

## 3. Garde-fou Ollama / RAG BrainVault

Le RAG BrainVault (`/mnt/vault_rag`) et Ollama sont des **sources de contexte, pas des sources
de vérité**. Toute valeur numérique qu'ils retournent doit être recoupée avec le fichier source
cité, via le garde-fou déjà en place `valeurs_non_ancrees()` (`scripts/rag_query.py`).

Réflexes obligatoires :
- `mountpoint /mnt/vault_rag` avant toute requête RAG (SSD hot-plug, pas de montage auto).
- `python scripts/rag_query.py --k 8 "<question>"` — ne jamais baisser `k` sous 8 sans raison
  documentée (bug de discrimination des chunks corrigé le 25/07/2026 en passant `k` de 3 à 8).
- Toute conjecture générée par Ollama/Mathstral est étiquetée **heuristique non vérifiée** tant
  qu'elle n'a pas été confirmée par un calcul ou une référence (voir `riemann-literature-scout`
  pour la littérature, `riemann-lmfdb-cross-validation` pour les zéros).

## 4. Règles communes non négociables

- **Point d'arrêt obligatoire** avant tout run `T > 50 000` : validation explicite de
  l'utilisateur avant de lancer, quel que soit l'agent qui a préparé le run.
- **Jamais de secret en clair** (token, clé API) dans un commit, `.mcp.json` inclus — toujours
  via variable d'environnement (`${GITHUB_TOKEN}`). Passer par `riemann-security-review` avant
  tout push touchant `scripts/`, `.mcp.json` ou `c_modules/`.
- **`docs/`** sert GitHub Pages — ne jamais déplacer/renommer un fichier sans vérifier l'impact
  sur le site publié.

## 5. Checklist avant une passation multi-agents

1. La tâche est-elle bien du ressort de l'agent visé (§1) ?
2. Le fichier `handoff/` correspondant est-il complet et autonome (pas de contexte implicite) ?
3. Si la tâche touche `c_modules/` ou `arb_C` → `phase-c-illinois` a-t-il été consulté ?
4. Si la tâche touche `.mcp.json`, `scripts/` ou des secrets → `riemann-security-review` a-t-il
   validé ?
5. Le run est-il `T > 50 000` ? → arrêt et confirmation utilisateur avant exécution.

---
*Skill créé le 27/09/2026 — Vague V2 du plan de mutualisation skills/MCP (voir `synthese_skills_zeta.md` §4.2, item 1).*
