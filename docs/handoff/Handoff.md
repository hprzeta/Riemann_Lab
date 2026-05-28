# Riemann_Lab — Handoff
> Dernière mise à jour : 24 mai 2026 — hprzeta  
> Branche active : `Riemann_Lab_IA`  
> Branche C : `Riemann_Lab_C` (renommée depuis `phase-C-core` le 18 mai 2026)  
> Rapport v3→v4 : `analyse_problemes_v3_v4.pdf` généré le 24 mai 2026

---

## 🗺️ Contexte général du projet

**Objectif principal :** Explorer l'Hypothèse de Riemann (HR) sous trois angles — numérique, mathématique, analytique.  
**Composante numérique immédiate :** Calculer les 10 000 premiers zéros non-triviaux de ζ(s) sur Re(s) = ½.  
**Long terme (Objectif 2) :** Agent IA autonome de recherche mathématique collaborant avec les IA universitaires.

| Élément | Valeur |
|---|---|
| Dépôt GitHub | `hprzeta/Riemann_Lab` |
| Branche développement Python | `Riemann_Lab_IA` ⭐ |
| Branche développement C | `Riemann_Lab_C` (Phase C — Illinois en C/libmpfr) |
| Branche test | `Riemann_Lab_Test` |
| Branche production | `main` |
| GitHub Pages | `https://hprzeta.github.io/Riemann_Lab/` (depuis `/docs` sur `Riemann_Lab_IA`) |
| Wiki (dépôt séparé) | `~/projet_zeta/Riemann_Lab.wiki/` — branche `master` |
| Environnement Python | `~/projet_zeta/zeta_env/` (Python 3.12) |
| Sources optimisation | `~/projet_zeta/src/calculs/optimisation/` |
| Mail projet | `hprzeta@protomail.com` |

---

## ✅ Ce qui fonctionne

### Code Python opérationnel

| Fichier | Rôle | Statut |
|---|---|---|
| `compute_zeros_v2.py` | Z(t) + affinage Illinois + mpmath 50 dps | ✅ 10 142 zéros en 21h |
| `compute_zeros_v3.py` | Orchestrateur v3 — parallèle + Turing | ✅ opérationnel |
| `riemann_siegel.py` | Formule RS remplace mpmath.zeta() | ✅ ×50 vs v2 |
| `theta_rapide.py` | θ(t) via Stirling — remplace loggamma | ✅ ×10 vs v2 |
| `turing_validation.py` | N(T) Turing-Backlund — complétude garantie | ✅ corrigé |
| `parallel_scanner.py` | Multiprocessing.Pool 4 workers | ✅ opérationnel |
| `riemann_siegel_batch.py` | Z(t) vectorisé NumPy/GPU, fallback 3 niveaux | ✅ opérationnel |
| `benchmark_15min.py` | Bench comparatif `--mode cpu/batch_cpu/batch_gpu` | ✅ opérationnel |

### Infrastructure & affichage
- `animation_theta.html` — animation interactive θ(t), intégrée via iframe dans le wiki ✅
- `docs/index.html` — KaTeX auto-render opérationnel avec délimiteurs `$...$` ✅
- Wiki FR en cours sur branche `master` du repo wiki ✅
- **KaTeX : utiliser `\text{Im}` et `\text{Re}` — jamais `\operatorname`** ✅
- `plt.show()` → remplacé par `plt.savefig()` + `plt.close()` (non bloquant) ✅
- nvtop recompilé depuis les sources (support NVIDIA uniquement, sans Intel) ✅

### GPU GTX 960M — opérationnel depuis le 16 mai 2026
- `sudo prime-select nvidia && sudo reboot` exécuté ✅
- CuPy réinstallé : `cupy-cuda12x` (CUDA 12.2 / Compute 5.0) ✅
- GPU active, bursts 30–50% visibles dans le graphe historique nvtop ✅

### Configuration Claude Code — CLAUDE.md (corrigé 23 mai 2026)

> ⚠️ **Erreur corrigée :** le `CLAUDE.md` projet complet (208 lignes, contexte Riemann) avait été
> copié par erreur dans `~/.claude/CLAUDE.md` (global), écrasant les instructions générales.
> Deux fichiers distincts ont été recréés.

**Hiérarchie correcte — Claude Code lit en cascade :**

```
~/.claude/CLAUDE.md                                          ← 🌍 GLOBAL (26 lignes — léger)
~/projet_zeta/CLAUDE.md                                      ← ⭐ PROJET (208 lignes — Riemann complet)
~/projet_zeta/src/calculs/optimisation/CLAUDE.md             ← 🔧 LOCAL Phase C
~/projet_zeta/src/calculs/optimisation/c_modules/CLAUDE.md   ← 🔩 MODULE C
```

| Fichier | Contenu | Lignes |
|---|---|---|
| `~/.claude/CLAUDE.md` | Langue FR, style, règles légères — tous projets | 26 |
| `~/projet_zeta/CLAUDE.md` | Contexte Riemann complet — formules, stack, GPU, Git | 208 |
| `src/calculs/optimisation/CLAUDE.md` | Phase C — Illinois, ctypes, précision adaptative | 108 |
| `src/calculs/optimisation/c_modules/CLAUDE.md` | Règles C — libmpfr, PREC=170, mémoire, Makefile | 97 |

**Commandes de déploiement :**
```bash
# 1. Global léger (téléchargé depuis Claude.ai le 23 mai)
cp CLAUDE_global_dot-claude.md ~/.claude/CLAUDE.md

# 2. Projet complet
cp CLAUDE_projet_zeta.md ~/projet_zeta/CLAUDE.md

# 3. Locaux Phase C
cp CLAUDE_optimisation.md ~/projet_zeta/src/calculs/optimisation/CLAUDE.md
mkdir -p ~/projet_zeta/src/calculs/optimisation/c_modules/
cp CLAUDE_c_modules.md ~/projet_zeta/src/calculs/optimisation/c_modules/CLAUDE.md
```

**Contenu `~/.claude/` vérifié (screenshot 23 mai 2026) :**
```
~/.claude/
├── CLAUDE.md          ← 7.1 Ko (corrigé — maintenant 26 lignes légères)
├── history.jsonl      ← historique Claude Code (29.7 Ko)
├── MEMORY.md          ← mémoire automatique (955 octets)
├── backups/           ← 5 éléments
├── cache/             ← 1 élément
├── plugins/           ← 5 éléments
├── projects/          ← 2 éléments
│   └── -home-r...ojet-zeta/memory/skills/zeta-lab/
│       ├── SKILL.md           ← 8.6 Ko ✅
│       ├── SKILL_phase_c.md   ← 7.6 Ko ✅
│       └── references/        ← 2 éléments
└── session-env/       ← 7 éléments
```

---

## 📊 Résultats benchmark (tests séquentiels — 16 mai 2026)

> Tests **équitables** : un seul mode à la fois après reboot NVIDIA.

| Mode | Zéros / 15 min | Vitesse | t atteint | Gain vs CPU |
|---|---|---|---|---|
| CPU scalaire (référence) | ~604 | ~0.67 z/s | 944 | — |
| **BATCH_CPU** ✅ | **3 231** | **3.59 z/s** | 4 164 | **×5.3** |
| **BATCH_GPU** ✅ | **3 051** | **3.39 z/s** | 4 596 | **×5.1** |

**Observation clé :** BATCH_CPU ≈ BATCH_GPU — la GTX 960M n'apporte pas de gain supplémentaire.  
**Pourquoi ?** L'affinage Illinois (mpmath, CPU pur) représente **80–90% du temps total**.  
La GPU n'accélère que la détection Z(t) (10–20% du temps).

```
Temps total = Détection Z(t) [10–20%]  +  Affinage Illinois [80–90%]
                    ↑                              ↑
         GPU ×10 ici (bursts 30–50%)      CPU pur — mpmath non portable GPU
```

---

## ⚠️ Formules critiques — erreurs à ne jamais reproduire

### ✅ Formule N(T) CORRECTE
```
N(T) = T/(2π) · ln(T/2πe)
```
Le **`e`** dans `2πe` est obligatoire. Sans lui :

| T | N(T) correct | N(T) sans `e` | Erreur |
|---|---|---|---|
| 10 000 | 10 142 | ~7 300 | −28% |
| 100 000 | **138 067** | ~49 346 | **−64%** |

> ⚠️ L'absence du `e` conduisait à projeter 10h pour T=100 000 ; le temps réel est 20–40h sans batch.

### STEP sécurisé (évite les zéros manquants)
```
STEP = min(2π / (5·ln(T_max/2π)), 0.10)
```

### Formule Riemann-Siegel
```
Z(t) = 2·Σ cos(θ(t) − t·ln n)/√n  +  R(t),   N = ⌊√(t/2π)⌋
```

### θ(t) asymptotique (Stirling)
```
θ(t) = (t/2)·ln(t/2π) − t/2 − π/8 + 1/(48t) + 7/(5760t³) + O(t⁻⁵)
```

---

## 🗂️ Architecture du projet

```
~/projet_zeta/
├── zeta_env/                          # venv Python 3.12
└── src/calculs/optimisation/
    ├── compute_zeros_v2.py            # v2 — référence (21h)
    ├── compute_zeros_v3.py            # v3 — orchestrateur principal
    ├── theta_rapide.py                # θ(t) asymptotique
    ├── riemann_siegel.py              # Z(t) formule RS
    ├── riemann_siegel_batch.py        # Z(t) vectorisé NumPy/GPU
    ├── parallel_scanner.py            # 4 workers multiprocessing
    ├── turing_validation.py           # N(T) Turing-Backlund
    └── benchmark_15min.py             # bench comparatif

~/projet_zeta/Riemann_Lab.wiki/        # Wiki cloné (branche master)

Outputs par run :
calculs/v3_T{TMAX}_{date}/
├── zeros_v3_T{TMAX}_{date}.csv
├── zeros_v3_T{TMAX}_{date}.png       # 3 graphiques
└── execution_v3_T{TMAX}_{date}.log

Rapports PDF (LaTeX via pdflatex) :
pdf/optimisation/analyse_problemes_v2_v3_phase0.pdf   ← v2→v3 (Phase 0)
pdf/optimisation/analyse_problemes_v3_v4.pdf          ← v3→v4 (Phase C) ✅ 24 mai 2026
```

---

## 📋 Wiki — état des pages

| Page | Statut |
|---|---|
| Home.md | ✅ à jour (16 mai 2026) |
| Parcours complet (niveaux 0→5) | ✅ |
| Documentation générale projet ζ(s) | ✅ |
| Guide Git & GitHub | ✅ |
| Guide VSCode | ✅ |
| Tableau symboles mathématiques | ✅ |
| Étape 1 — Calcul des zéros (v1→v2→v3) | 🟡 En cours |
| Phase Optimisation — compute_zeros_v3 | ✅ mis à jour 16 mai 2026 |
| Partie 1 — La Théorie Étape 1 | ✅ |
| **Partie 2 — Z(t), zéros non-triviaux** | ⚪ **À créer** |
| Étape 2 — Visualisations avancées | ⚪ À venir |
| Étape 3 — IA (ZetaCoeffNet…) | ⚪ À venir |
| Étape 4 — Preuves formelles Lean 4 | ⚪ À venir |

**Fix wiki en attente :**
- Corriger lien PDF cassé dans `Phase-Optimisation-_-compute_zeros_v3.md`
- Corriger contenu "Étape 1" (lien mort)
- `git push wiki` après correction

---

## 🖥️ Matériel

| Composant | Valeur |
|---|---|
| CPU | Intel i7, 4 cœurs |
| RAM | 8 GB + 16 GB swap |
| GPU affichage | Intel HD Graphics 620 |
| GPU calcul | NVIDIA GeForce GTX 960M — 4 GB VRAM |
| CUDA | 12.0 / 12.2 — Compute Capability 5.0 |
| OS | Ubuntu, VSCode, Python 3.12 |

**Règle nvtop :** toujours lire le **graphe historique du haut** (fiable), pas la colonne GPU% par processus (trompeuse — bursts ~50ms invisibles à l'échantillonnage 2s).

---

## 🔜 Ce qui reste à faire

### Immédiat — Objectif 1 (10 000 zéros)
- [x] ~~Finaliser le run `compute_zeros_v3` à T=10 000~~ — **10 142 zéros calculés** ✅
- [x] ~~Valider la complétude Turing-Backlund~~ — **validé LMFDB** ✅
- [ ] Comparer avec les tables d'Odlyzko (au-delà des 20 premiers)
- [ ] Ajouter les visualisations Python dans `/docs`
- [ ] Compléter Partie 2 du wiki (Z(t), zéros non-triviaux)
- [ ] Fix lien PDF cassé + push wiki (`Phase-Optimisation-_-compute_zeros_v3.md`)

### Phase C — Accélération Illinois (version v4)
- [x] Architecture C définie et documentée dans `SKILL_phase_c.md`
- [x] `CLAUDE.md` locaux générés (23 mai 2026)
- [x] Prompt de démarrage Claude Code rédigé : `PROMPT_CLAUDE_CODE_PHASE_C.md`
- [x] **Rapport v3→v4 généré** : `analyse_problemes_v3_v4.pdf` (14 pages, 24 mai 2026) ✅
  - 6 problèmes documentés (P1–P6)
  - Code C complet `illinois_mpfr.c` + Makefile + interface ctypes
  - Projections : T=100 000 en 1.5–2.5 h après Phase C

**Problèmes identifiés et documentés (v3→v4) :**

| # | Sévérité | Problème | Statut |
|---|---|---|---|
| P1 | 🔴 HAUTE | Illinois mpmath = 80–90 % du temps | En cours → Phase C |
| P2 | 🔴 HAUTE | CUDA fork() invalide dans multiprocessing | En cours → v4 |
| P3 | 🟡 MOYENNE | Contention BLAS tests concurrents (×2.1) | ✅ Résolu |
| P4 | 🟢 FAIBLE | GPU 0 % liste nvtop (burst 50 ms < échant. 2 s) | ✅ Résolu |
| P5 | 🟢 FAIBLE | nvtop crash Intel HD + prime-select nvidia | ✅ Résolu |
| P6 | 🟢 FAIBLE | CLAUDE.md global écrasé accidentellement | ✅ Résolu |

**Prochaines actions Phase C :**
- [ ] Vérifier prérequis : `sudo apt install libmpfr-dev libgmp-dev` + `mpfr-config --version ≥ 4.0`
- [ ] Créer `c_modules/` et implémenter dans l'ordre :
  1. `z_function.h / z_function.c` — θ(t) Stirling + Z(t) RS en double
  2. `illinois_mpfr.h / illinois_mpfr.c` — Illinois en libmpfr PREC=170 bits
  3. `Makefile` → cible `illinois_mpfr.so`
  4. `test_illinois.py` — validation 10 premiers zéros vs LMFDB (tolérance < 1e-10)
- [ ] Fix fork+CUDA dans `parallel_scanner.py` (init CuPy post-fork via `initializer=`)
- [ ] Benchmark Illinois C vs Illinois mpmath sur 100 zéros → gain attendu ×5–10
- [ ] Intégrer dans `compute_zeros_v4.py` avec fallback automatique mpmath si `.so` absent
- [ ] Phase Arb → `python-flint`, version partielle Odlyzko-Schönhage
- [ ] Pousser `analyse_problemes_v3_v4.pdf` dans `pdf/optimisation/` sur GitHub

### Objectif 2 — Agent IA autonome
- [ ] Cours Anthropic Skilljar : Claude Code 101 → Claude Code in Action (intégration `~/projet_zeta/src/`)
- [ ] MCP intro + avancé → connexion GitHub / wiki / outils
- [ ] Subagents → délégation tâches zêta/Turing/R-S
- [ ] Agent Skills → routines réutilisables
- [ ] Agent capable de : publier sur `hprzeta.github.io/Riemann_Lab/`, générer rapports v→v+1, envoyer résultats à `hprzeta@protomail.com`, collaborer avec IA universitaires spécialisées

### 🤖 Stack complète — Second Cerveau IA

---

#### 1. LLM — Modèles locaux (via Ollama)

> Tous les modèles sont sur `/mnt/data/models_ia/ollama/` — configuré via `OLLAMA_MODELS` dans `.bashrc`.  
> GPU forcé via `OLLAMA_CUDA=1` dans `.bashrc`.  
> ⚠️ **Un seul modèle à la fois** — 4 GB VRAM GTX 960M.

| Modèle | Taille | Statut | Rôle | Priorité |
|---|---|---|---|---|
| `mathstral:latest` | 4.1 GB | ✅ installé | Maths + ζ(s) — raisonnement symbolique | 1 |
| `deepseek-coder:6.7b` | 3.8 GB | ✅ installé | Code Python/C — génération et debug | 2 |
| `qwen3:4b` | ~2.5 GB | ✅ installé | Polyvalent rapide — tâches légères et code | 3 |
| `deepseek-math:7b` | ~3.8 GB | 🔜 À installer | **Meilleur raisonnement math pur** | 4 |
| `phi3:mini` | ~2.3 GB | 🔜 À installer | Modèle ultra-léger — réponses rapides | 5 |

```bash
# Installer les 2 manquants
ollama pull deepseek-math:7b
ollama pull phi3:mini
```

**Configuration `.bashrc` validée (19 mai 2026) :**
```bash
export OLLAMA_MODELS=/mnt/data/models_ia/ollama   # ✅ modèles sur /mnt/data
export OLLAMA_CUDA=1                               # ✅ GPU NVIDIA forcé
export PATH="$HOME/.local/bin:$PATH"              # ✅ binaires locaux
```

**Espace disque `/mnt/data` :**
```
Partition : /dev/sda4 — 651 GB total — 43 GB utilisés — 576 GB libres
Modèles actuels : ~10 GB utilisés (3 modèles)
Après install complète : ~24 GB utilisés (5 modèles)
```

**Note canirun.ai :** le site détecte GTX 960 2 GB (erreur WebGPU) → utiliser GTX 970 4 GB dans le dropdown pour une estimation correcte.

#### LLM en ligne (pas d'installation — utiliser via navigateur)

| Outil | Usage dans le projet |
|---|---|
| **Claude*** | Cerveau principal de session — mémoire, structure, maths longues |
| **Perplexity*** | Recherche web + arXiv + prépublications récentes |
| **Kimi*** | Lecture de longs documents PDF (Titchmarsh, Odlyzko) |
| **DeepSeek*** | Raisonnement mathématique alternatif |
| `canirun.ai` | Vérifier si un modèle tourne sur GTX 960M avant de le télécharger |
| `whichllm` | Comparer les LLM pour choisir le bon pour chaque tâche |

#### LLM — Objectif 2 uniquement

| Outil | Rôle futur |
|---|---|
| **LM Studio** | GUI desktop + API OpenAI-compatible → LangChain, CrewAI, AutoGen |
| **Cursor** | IDE IA — si VSCode + Claude ne suffit plus |
| **llm council** | Faire débattre plusieurs LLM — agent collaboratif multi-modèles |

---

#### 2. Skills Claude

| Skill | Statut | Rôle |
|---|---|---|
| `riemann-lab` | ✅ en place | Mémoire projet — KaTeX, wiki, Python, Git |
| `phase-c-illinois` | ✅ en place | Skill dédié Phase C — libmpfr, Illinois C, ctypes, benchmarks |
| `code-review` | 🔜 À activer | Audit automatique du code Python/C |
| `security-review` | 🔜 À activer | Vérification sécurité des scripts et des `.so` |
| `skills.sh` | 🔜 À explorer | Dépôt de skills communautaires pour Claude |
| `mattpocock/skills` | 🔜 **Objectif 2 uniquement** | Voir note ci-dessous |

**Note `mattpocock/skills` (23 mai 2026) :**
Repo très populaire (~77 000 ⭐, #1 GitHub Trending), publié par Matt Pocock (éducateur TypeScript).
Il publie son `.claude/skills/` personnel comme référence communautaire.
Skills les plus utiles du repo :

| Skill mattpocock | Usage dans Riemann_Lab | Quand |
|---|---|---|
| `/grill-with-docs` | Aligne Claude Code sur le contexte avant de coder — crée un `CONTEXT.md` projet | Début de chaque session Phase C/agent |
| `/diagnose` | Débogage structuré — très utile pour segfaults `illinois_mpfr.c` | Quand le C plante |
| `/caveman` | Réduit la verbosité de l'agent à zéro quand on sait ce qu'on veut | Phase C avancée |
| `/write-a-skill` | Crée de nouveaux skills avec structure progressive | Fabrication skills agent Obj. 2 |

**Verdict :** généraliste TypeScript/web — les skills Riemann_Lab maison (`SKILL.md`, `SKILL_phase_c.md`) sont plus adaptés pour la Phase C. Installer mattpocock/skills pour l'Objectif 2 (agent autonome).

```bash
# Installation (Objectif 2 — pas maintenant)
npx mattpocock/skills install
```

---

#### 3. MCP (Model Context Protocol)

| Outil | Statut | Rôle |
|---|---|---|
| **Context7** | 🔜 À connecter | Injecte la doc à jour (mpmath, numpy, LlamaIndex) dans Claude |

```bash
# Connexion via le menu MCP de Claude
# → chercher "Context7" → connecter
```

---

#### 4. RAG — Second Cerveau (pipeline d'ingestion)

| Outil | Statut | Rôle |
|---|---|---|
| **LlamaIndex** | 🔜 À installer | RAG simple — ingérer PDFs + wiki + GitHub |
| **ChromaDB** | 🔜 À installer | Base vectorielle locale — `~/projet_zeta/brain/` |
| **sentence-transformers** | 🔜 À installer | Embeddings locaux CPU/GPU |
| **LangChain** | 🔜 Objectif 2 | Framework agent complet — plus complexe que LlamaIndex |

```bash
pip install llama-index chromadb sentence-transformers
```

Sources à ingérer : wiki Riemann_Lab · PDFs (Titchmarsh, Odlyzko, rapports) · code src/ · transcripts YouTube (3Blue1Brown, etc.) · LMFDB

---

#### 5. Tools & Automatisation

| Outil | Statut | Rôle |
|---|---|---|
| **Manim** | 🔜 À installer | Animations mathématiques pro (style 3Blue1Brown) — visualiser ζ(s), Z(t) |
| **airllm** | 🔜 À installer | Faire tourner des gros LLM en 8 GB RAM par segmentation mémoire |
| **n8n** (Docker) | 🔜 Objectif 2 | Automatisation no-code : GitHub → mail → calculs → publication |
| **Flowise** | 🔜 Fin Obj 1 | ⭐ Low-code pour construire le Second Cerveau visuellement — Ollama + ChromaDB en drag & drop |
| **Activepieces** | 🔜 Objectif 2 | Automatisation simple open-source (alternative Zapier) — notifications, publications |
| **llmfit** | 🔜 Objectif 2 | Fine-tuning LLM sur tes données zêta |
| **Ollama** (Docker) | 🔜 Objectif 2 | Isoler l'environnement Ollama en conteneur |
| **claw-code** | 🔜 Objectif 2 | Agent CLI open-source (réécriture Rust de Claude Code leaké) — supporte Ollama + skills locaux |
| `build-your-own-x` | 🔜 À consulter | Construire RAG, agent, LLM from scratch — ressource formation |

```bash
# Maintenant
pip install manim airllm

# Flowise (fin Objectif 1 — Second Cerveau visuel)
npx flowise start   # interface web : http://localhost:3000

# Objectif 2
# n8n    → docker run -p 5678:5678 n8nio/n8n
# claw-code → git clone https://github.com/ultraworkers/claw-code
```

> **Priorité low-code :** Flowise d'abord (Second Cerveau) → n8n ensuite (automatisation complète) → Activepieces (notifications légères).

---

#### 6. Formation

| Ressource | Statut | Usage |
|---|---|---|
| **roadmap.sh** | 🔜 À consulter | Roadmaps Python, IA, agents — structurer l'apprentissage |
| **build-your-own-x** | 🔜 À consulter | Implémenter RAG, agent, LLM from scratch |
| **Anthropic Skilljar** | 🔜 Prioritaire Obj 2 | Claude Code 101 → MCP → Subagents → Agent Skills |

---

#### Récapitulatif — installer maintenant vs plus tard

```
── Phase C (maintenant) ─────────────────────────────────────────
sudo apt install libmpfr-dev libgmp-dev gcc build-essential
Connecter MCP Context7 dans Claude Code  ← doc libmpfr 4.x live
Activer skill code-review + security-review dans Claude

── Maintenant (Objectif 1) ──────────────────────────────────────
pip install manim airllm llama-index chromadb sentence-transformers
ollama pull deepseek-math:7b
ollama pull phi3:mini
Connecter MCP Context7 dans Claude
npx flowise start   ← Second Cerveau visuel

── Fin Objectif 1 ───────────────────────────────────────────────
Ingérer wiki + PDFs + YouTube dans ChromaDB via LlamaIndex
Requêtes RAG depuis brain_query.py

── Objectif 2 (agent autonome) ──────────────────────────────────
pip install langchain llmfit
Installer LM Studio       → https://lmstudio.ai
Installer Docker          → Ollama container + n8n + Activepieces
git clone claw-code       → https://github.com/ultraworkers/claw-code
Cours Anthropic Skilljar  → Claude Code 101 → MCP → Subagents
npx mattpocock/skills install  ← skills communautaires agent
```

**Analyse `IA_tools.txt` (23 mai 2026) — outils par priorité :**

| Colonne | Outil | Pertinence Phase C | Pertinence Obj. 2 |
|---|---|---|---|
| MCP | **Context7** | ⭐⭐⭐ doc libmpfr/gcc live | ⭐⭐ doc LangChain/MCP |
| Skills | `code-review` | ⭐⭐⭐ audit code C/ctypes | ⭐⭐ |
| Skills | `security-review` | ⭐⭐ vérif `.so` + interfaces | ⭐ |
| Skills | `mattpocock/skills` | ⭐ trop généraliste (TypeScript) | ⭐⭐⭐ |
| LLM | DeepSeek (en ligne) | ⭐⭐ raisonnement C alternatif | ⭐⭐⭐ |
| Tools | `canirun.ai` | ⭐ vérif python-flint sur GTX 960M | ⭐ |
| Tools | `airllm` | — | ⭐⭐ gros LLM en 8 GB RAM |
| Formation | `build-your-own-x` | ⭐⭐ internals MPFR from scratch | ⭐⭐ |

---

## 🌿 Architecture des branches Git

| Branche | Rôle | Tracking |
|---|---|---|
| `Riemann_Lab_IA` ⭐ | Développement principal — Python, wiki, docs, benchmarks | `origin/Riemann_Lab_IA` |
| `Riemann_Lab_C` | Phase C — module C, libmpfr, Illinois accéléré, ASM | `origin/Riemann_Lab_C` |
| `Riemann_Lab_Test` | Tests ponctuels, Codespaces, expérimentations | `origin/Riemann_Lab_Test` |
| `main` | Production stable — merge depuis `Riemann_Lab_IA` | `origin/main` |

> **Convention :** toutes les branches de travail suivent le préfixe `Riemann_Lab_*`.  
> `phase-C-core` supprimée le 18 mai 2026 → renommée `Riemann_Lab_C`.

### Changer de branche

```bash
git checkout Riemann_Lab_IA   # Python, wiki, docs
git checkout Riemann_Lab_C    # Module C, libmpfr, Illinois C
git checkout Riemann_Lab_Test # Tests ponctuels
```

---

## 📐 Règles KaTeX (rappel critique)

| ❌ Interdit | ✅ Correct |
|---|---|
| `\operatorname{Re}` | `\text{Re}` |
| `\operatorname{Im}` | `\text{Im}` |
| `\operatorname{...}` | `\text{...}` |

Délimiteurs : `$...$` inline, `$$...$$` display — dans `index.html` ET le wiki GitHub.

---

## 🔗 Références

| Ressource | Lien |
|---|---|
| Site du projet | https://hprzeta.github.io/Riemann_Lab/ |
| Code source | https://github.com/hprzeta/Riemann_Lab/tree/Riemann_Lab_IA/src |
| Rapport PDF v2→v3 | `pdf/optimisation/analyse_problemes_v2_v3_phase0.pdf` |
| **Rapport PDF v3→v4** | **`pdf/optimisation/analyse_problemes_v3_v4.pdf`** ← ✅ 24 mai 2026 |
| LMFDB (tables de référence) | https://lmfdb.org/zeros/zeta/ |
| Odlyzko & Schönhage 1988 | https://doi.org/10.1090/S0002-9947-1988-0936813-0 |
| Turing 1953 | https://doi.org/10.1112/plms/s3-3.1.99 |
| Titchmarsh — Theory of ζ (§4.12) | https://archive.org/details/theoryofriemann00titc |

---

## 🚀 Prochaine session — reprendre ici

> **État au 24 mai 2026 :**
> 10 142 zéros calculés et validés (T ≈ 9 998.85) sur `zeros_zeta_T10000_20260424_205325.csv`.
> Rapport v3→v4 généré : `analyse_problemes_v3_v4.pdf` (14 pages, 24 mai 2026).
> 6 problèmes P1–P6 documentés — P3/P4/P5/P6 résolus, P1/P2 en cours (Phase C).
> Stack Ollama : 3 modèles installés sur `/mnt/data` (mathstral, deepseek-coder, qwen3:4b).
> `.bashrc` validé : `OLLAMA_MODELS` + `OLLAMA_CUDA=1` + tous les alias `zeta-*`.
> Branches Git : convention `Riemann_Lab_*` — `Riemann_Lab_C` prête pour la Phase C.
> **CLAUDE.md corrigé** : global `~/.claude/CLAUDE.md` séparé du projet `~/projet_zeta/CLAUDE.md`.
> Prompt Phase C prêt : `PROMPT_CLAUDE_CODE_PHASE_C.md`.

**Reprendre avec :**

1. ✅ Déployer les 4 `CLAUDE.md` (téléchargés depuis Claude.ai le 23 mai) :
   ```bash
   cp CLAUDE_global_dot-claude.md ~/.claude/CLAUDE.md
   cp CLAUDE_projet_zeta.md ~/projet_zeta/CLAUDE.md
   cp CLAUDE_optimisation.md ~/projet_zeta/src/calculs/optimisation/CLAUDE.md
   mkdir -p ~/projet_zeta/src/calculs/optimisation/c_modules/
   cp CLAUDE_c_modules.md ~/projet_zeta/src/calculs/optimisation/c_modules/CLAUDE.md
   ```

2. Pousser le rapport v3→v4 sur GitHub :
   ```bash
   cp analyse_problemes_v3_v4.pdf ~/projet_zeta/pdf/optimisation/
   cd ~/projet_zeta
   git checkout Riemann_Lab_IA
   git add pdf/optimisation/analyse_problemes_v3_v4.pdf
   git commit -m "docs(pdf): add v3->v4 analysis report - Phase C Illinois C/libmpfr"
   git push origin Riemann_Lab_IA
   ```

3. Vérifier prérequis Phase C et démarrer :
   ```bash
   mpfr-config --version   # doit retourner >= 4.0
   gcc --version
   git checkout Riemann_Lab_C
   cd ~/projet_zeta/src/calculs/optimisation/c_modules/
   # Implémenter illinois_mpfr.c (voir SKILL_phase_c.md + rapport v3→v4)
   ```

4. Lancer Claude Code avec le prompt Phase C :
   ```bash
   cd ~/projet_zeta/
   source zeta_env/bin/activate
   git checkout Riemann_Lab_C
   claude
   # Coller le contenu de PROMPT_CLAUDE_CODE_PHASE_C.md
   ```

5. Fix wiki :
   - Corriger lien PDF dans `Phase-Optimisation-_-compute_zeros_v3.md` → pointer vers `analyse_problemes_v3_v4.pdf`
   - `git push wiki` (branche `master`)

6. `ollama pull deepseek-math:7b` + `ollama pull phi3:mini` — compléter la stack LLM

7. Connecter MCP **Context7** dans Claude Code avant de démarrer la Phase C

<!-- Mettre à jour cette section avant de fermer Claude -->

---
*Dernière mise à jour : 24 mai 2026 — 604 lignes*
