# Riemann_Lab — Handoff
> Dernière mise à jour : 28 mai 2026 — hprzeta  
> Branche active : `Riemann_Lab_IA`  
> Branche C : `Riemann_Lab_C` (renommée depuis `phase-C-core` le 18 mai 2026)

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
pdf/optimisation/analyse_problemes_v2_v3_phase0.pdf
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
- [ ] Finaliser le run `compute_zeros_v3` à T=10 000 (🟠 en calcul)
- [ ] Valider la complétude Turing-Backlund sur les 10 142 zéros
- [ ] Comparer avec les tables d'Odlyzko et la base LMFDB
- [ ] Ajouter les visualisations Python dans `/docs`
- [ ] Compléter Partie 2 du wiki (Z(t), zéros non-triviaux)
- [ ] Fix lien PDF cassé + push wiki

### Phase C — Accélération Illinois (état au 28 mai 2026)

> **Contexte de travail :** En parallèle de Claude, GPT-4.5 (via Copilot / Teams professionnel)
> a été utilisé pour consolider l'état et produire 9 PDF de cadrage + 2 prompts opérationnels.
> Les décisions ci-dessous résultent de cette collaboration multi-LLM.

#### Ce qui est validé ✅

- [x] `c_modules` compile : `make clean && make` → `illinois_mpfr.so` OK
- [x] `test_illinois.py` passe sur 10 premiers zéros **en mode hybride**
- [x] `benchmark_illinois.py` : gain isolé C/libmpfr **×48.73** sur t≈500–638
- [x] `compute_zeros_v4.py` tourne sur T=80, T=300, T=650
- [x] Turing-Backlund complet sur T=80/T=300/T=650 — 0 zéro manquant
- [x] LMFDB : 19/20 premiers zéros < 1e-10 (zéro #20 ≈ 8.06e-10)

#### Diagnostic complet — nuit du 28-29 mai 2026 ✅

**Session de diagnostic avec Copilot (GPT-4.5) + Claude simultanément.**

Script Python pur de décomposition sur t ∈ [300, 650] :

```
theta  : mean=7.6e-14  max=2.3e-13  ✅ theta_double est PARFAIT
sum    : mean=1.95e-01 max=3.26e-01 ✅ normal sans correction C0+C1
fullRS : mean=7.3e-04  max=1.5e-03  ⚠️ biais résiduel — voir ci-dessous
```

**Conclusion du diagnostic :**

> Le biais **n'est PAS un bug de code**. C'est une **limitation mathématique structurelle** :
> la formule RS tronquée à C0+C1 seulement donne une précision ~1e-3 maximum.
> `mpmath.siegelz` utilise bien plus de termes (Euler-Maclaurin adaptatif).

| Méthode | Précision |
|---|---|
| RS sans correction | ~1e-1 |
| RS + C0 seulement | ~1e-2 |
| RS + C0 + C1 | ~**1e-3** (état actuel) |
| RS + 3–5 termes | ~1e-8 |
| mpmath.siegelz | ~1e-12 |

**Patches tentés et annulés :**
- ❌ Patch 1 (π manquant dans dPsi) → biais aggravé à 4e-2
- ❌ Patch 2 (nouvelle formule C1 analytique) → biais aggravé à 2e-2
- ✅ `git checkout z_function.c` → revenu à l'état original

**Solution retenue : Option B — remplacer Z_mpfr par ζ(1/2+it) direct**

$$Z(t) = \Re\left(e^{i\theta(t)} \cdot \zeta\!\left(\tfrac{1}{2}+it\right)\right)$$

- `mpc_zeta` testé → **ABSENT** dans libmpc 1.3.1 (pas implémenté dans libmpc standard)
- **Solution prochaine session :** wrapper Python/C appelant `mpmath.siegelz(t)` depuis le `.so`

#### Prochaine étape — wrapper Python/C 🔜

```python
# Concept : illinois_mpfr.c appelle Python via ctypes inversé
# ou : Z_mpfr délègue à un sous-process Python mpmath
# Contrainte : illinois_mpfr.so reste appelable depuis Python via ctypes
```

**Commande de reprise :**
```
Donne-moi le wrapper Python/C qui permet à illinois_mpfr.c
d'appeler mpmath.siegelz(t) avec précision 1e-12,
sans mpc_zeta (absent dans libmpc 1.3.1).
Contrainte : illinois_mpfr.so reste appelable depuis Python via ctypes.
```

**Étape 2 — v4.1 : corriger l'architecture (après validation voie B)**

> Prompt opérationnel : `src/ia/prompts/PROMPT_CLAUDE_CODE_V4_INTEGRATION.md`

5 erreurs architecturales identifiées dans v4 à corriger dans `compute_zeros_v4_1.py` :

| Erreur | Impact | Correction |
|---|---|---|
| Détection via `mpmath.siegelz` | ×50 lenteur | → `Z_batch()` partout |
| Parallélisme abandonné | ×4 lenteur | → `calculer_zeros_parallele()` 4 workers |
| `Z_double` du .so en détection | faux fallbacks | → ne charger que `illinois_mpfr` |
| Fallback mpmath sur tout le domaine | Illinois_C→mpmath à 100% | → seuil `T_SEUIL = 300.0` |
| `.so` absent → dégradation silencieuse | bugs invisibles | → `raise FileNotFoundError` |

**Seuil mathématiquement justifié :**
$$N = \lfloor\sqrt{t/2\pi}\rfloor \implies t < 300 \Rightarrow N < 7 \text{ termes (imprécis)}, \quad t \geq 300 \Rightarrow N \geq 7 \text{ (fiable)}$$

Répartition attendue sur T=10 000 :
```
illinois_C      : ~10 055 zéros (99%)  — gain ×39
mpmath_petit_t  :     ~87 zéros  (<1%) — t < 300, légitime
mpmath_fallback :       ~0 zéros  (0%) — ne doit pas apparaître
```

#### Prompt combiné à donner à Claude Code

```
Lis src/ia/prompts/prompt_claude_code_phase_c_voie_b_v5.md.
Travaille uniquement sur la branche Riemann_Lab_C.
Ne casse pas compute_zeros_v4.py validé.

Phase 1 (voie B) :
  Crée diagnostic_zmpfr_vs_mpmath.py, audite z_function.c,
  propose un patch v5 pour réduire le biais Z_mpfr vs mpmath.siegelz.

Phase 2 (v4.1) — seulement si Phase 1 valide (Illinois_C pur > 0%) :
  Applique les 5 corrections architecturales de PROMPT_CLAUDE_CODE_V4_INTEGRATION.md :
  - Détection via Z_batch() partout (interdit : mpmath.siegelz en détection)
  - Parallélisme 4 workers (parallel_scanner.py)
  - Seuil T_SEUIL_ILLINOIS_C = 300.0 (mathématiquement justifié)
  - Arrêt immédiat si .so absent
  - Créer compute_zeros_v4_1.py (ne pas modifier v4.py)

Critères de succès : 20/20 LMFDB < 1e-10, Turing complet, Illinois_C pur > 50%.
```

#### Critères de succès avant T=10 000

1. `make clean && make` OK
2. `test_illinois.py` OK (10/10)
3. `benchmark_illinois.py` OK
4. `Illinois_C` pur > 0 % sur run T=650
5. Turing-Backlund complet
6. LMFDB 20/20 < 1e-10
7. Puis T=1000, **ensuite seulement T=10 000**

#### 9 PDF de cadrage produits (session GPT-4.5 / Copilot)

| PDF | Thème | Message clé |
|---|---|---|
| 01 | Cartographie diagnostic | Conserver l'historique, ne pas repartir de zéro |
| 02 | Migration / Brain Vault / RAG | Structure hprzeta-lab, recovery, données validées |
| 03 | Checklist Linux avant migration | Linux, Git, GPU, Python, Ollama, partitions |
| 04 | Scripts post-audit | Extraction légère archive audit, mini-audit Git |
| 05 | Complément Git / priorités | Branches confirmées, Riemann_Lab_C contient c_modules |
| 06 | Lexique IA & Brain Vault | Vault, RAG, Skills, agents, grounding, provenance |
| 07 | Pavé primalité | Nombres premiers, produit eulérien, ψ(x), formule explicite |
| 08 | CryptoZeta | RSA, ECC, post-quantique, hash, recovery |
| 09 | Synthèse journée Phase C v4 voie B | v4 hybride validé T=650 ; Illinois C pur non validé |
| 10 | Résumé 9 PDF + prompt v5 | Passerelle → Claude Code voie B/v5 |

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

| Outil | Modèle | Usage dans le projet |
|---|---|---|
| **Claude** | Claude Sonnet 4.5 | Cerveau principal de session — mémoire, structure, maths longues, wiki |
| **Copilot** ⭐ | GPT-4.5 Reflexion | Cadrage Phase C, génération 9 PDF + prompts voie B/v5 — **auteur de la base de travail v4→v5** |
| **Perplexity** | — | Recherche web + arXiv + prépublications récentes |
| **Kimi** | — | Lecture de longs documents PDF (Titchmarsh, Odlyzko) |
| **DeepSeek** | — | Raisonnement mathématique alternatif |
| `canirun.ai` | — | Vérifier si un modèle tourne sur GTX 960M avant de le télécharger |
| `whichllm` | — | Comparer les LLM pour choisir le bon pour chaque tâche |

**Accéder à Copilot (GPT-4.5) depuis la station Linux personnelle :**

> Copilot est accessible depuis n'importe quel navigateur avec le compte professionnel Microsoft.
> Pas d'installation requise — évite le copier-coller entre ordi de travail et station zeta-lab.

```
# Option A — Copilot standalone (recommandé)
https://copilot.microsoft.com
→ Se connecter avec le compte professionnel @entreprise.com
→ Même modèle GPT-4.5 que dans Teams

# Option B — Teams web (si contexte projet Teams nécessaire)
https://teams.microsoft.com
→ Même compte professionnel
→ Accès Copilot directement dans Teams depuis Linux

# Option C — VS Code (si licence GitHub Copilot séparée disponible)
# Extensions VS Code → chercher "GitHub Copilot"
# ⚠️ Nécessite une licence GitHub Copilot distincte de la licence M365
# → Vérifier avec le service IT si incluse dans la licence Enterprise
```

**Workflow recommandé multi-machine :**
```
Station Linux (zeta-lab)          Ordi de travail
─────────────────────────         ──────────────────────────
Claude.ai         (ici)           Copilot via Teams
copilot.microsoft.com ← même URL  Copilot via Teams
↓                                 ↓
Télécharger le fichier .md        Générer le .md
→ cp ~/Téléchargements/X.md ~/projet_zeta/...
```

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
| LMFDB (tables de référence) | https://lmfdb.org/zeros/zeta/ |
| Odlyzko & Schönhage 1988 | https://doi.org/10.1090/S0002-9947-1988-0936813-0 |
| Turing 1953 | https://doi.org/10.1112/plms/s3-3.1.99 |
| Titchmarsh — Theory of ζ (§4.12) | https://archive.org/details/theoryofriemann00titc |

---

## 🚀 Prochaine session — reprendre ici

> **État au 29 mai 2026 — 2h30 :**
> - Diagnostic complet z_function.c terminé (nuit 28-29 mai)
> - Biais = insuffisance RS (C0+C1 → ~1e-3) — PAS un bug de code
> - mpc_zeta absent dans libmpc 1.3.1 → patch MPC impossible
> - Solution : wrapper Python/C pour Z_mpfr via mpmath.siegelz
> - z_function.c revenu à l'état original (git checkout)
> - Agent Copilot `Riemann_Lab` créé sur m365.cloud.microsoft ✅

---

### Étape 1 — Ouvrir Claude Code

```bash
cd ~/projet_zeta/
source zeta_env/bin/activate
git checkout Riemann_Lab_C
claude
```

---

### Étape 2 — Coller ce texte dans Claude Code

```
Lis src/ia/prompts/prompt_claude_code_phase_c_voie_b_v5.md.
Travaille uniquement sur la branche Riemann_Lab_C.
Ne casse pas compute_zeros_v4.py validé.

Contexte : le biais Z_mpfr (~1e-3) vient d'une insuffisance du
développement RS (C0+C1 seulement). mpc_zeta est absent dans
libmpc 1.3.1. La solution retenue est un wrapper Python/C.

Mission : implémenter un wrapper qui permet à illinois_mpfr.c
d'obtenir Z(t) avec précision ~1e-12 en appelant mpmath.siegelz(t).
Contrainte absolue : illinois_mpfr.so reste appelable depuis Python
via ctypes exactement comme maintenant.

Critères de succès :
- biais Z moyen < 1e-8 sur t ∈ [300, 650]
- Illinois_C pur > 50% sur run T=650
- Turing-Backlund complet
- LMFDB 20/20 < 1e-10
```

---

### Étape 3 — Après validation Phase C

- **Rapport v3→v4** : `.md` + PDF via `pdflatex`
  → `pdf/optimisation/analyse_problemes_v3_v4.pdf`
- **Fix wiki** : lien PDF cassé dans `Phase-Optimisation-_-compute_zeros_v3.md`
  ```bash
  cd ~/projet_zeta/Riemann_Lab.wiki/
  git add . && git commit -m "fix(wiki): correct PDF link"
  git push origin master
  ```

<!-- Mettre à jour cette section avant de fermer Claude -->

---
*Dernière mise à jour : 29 mai 2026 — 742 lignes*
