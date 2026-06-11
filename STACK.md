# Riemann_Lab — Stack & Roadmap

> 🛠️ **Référence stable.** Outils, branches, matériel, roadmap formation. Change rarement.
> N'est *pas* relu au démarrage d'une session de calcul. État courant → `Handoff.md`,
> historique daté → `JOURNAL.md`.

---

## 🗺️ Contexte général

| Élément | Valeur |
|---|---|
| Dépôt GitHub | `hprzeta/Riemann_Lab` |
| Branche dév. Python | `Riemann_Lab_IA` ⭐ |
| Branche dév. C | `Riemann_Lab_C` (Phase C — Illinois en C/libmpfr) |
| Branche test | `Riemann_Lab_Test` |
| Branche production | `main` |
| GitHub Pages | `https://hprzeta.github.io/Riemann_Lab/` (depuis `/docs` sur `Riemann_Lab_IA`) |
| Wiki (dépôt séparé) | `~/projet_zeta/Riemann_Lab.wiki/` — branche `master` |
| Logo PNG | `docs/images/logo_riemann_lab.png` — 500×235 px, 11 Ko, exporté via cairosvg depuis le SVG animé |
| venv Python | `~/projet_zeta/zeta_env/` (Python 3.12) |
| Sources optimisation | `~/projet_zeta/src/calculs/optimisation/` |
| Mail projet | `hprzeta@protonmail.com` |

**Objectifs :**
1. **Numérique** — calculer les 10 000 premiers zéros non-triviaux de ζ(s) sur Re(s)=½ ✅ (10 142).
2. **Recherche** — agent IA autonome de recherche mathématique collaborant avec des IA universitaires.

---

## 🌿 Branches Git

| Branche | Rôle |
|---|---|
| `Riemann_Lab_IA` ⭐ | Développement principal — Python, wiki, docs, benchmarks |
| `Riemann_Lab_C` | Phase C — module C, libmpfr, Illinois accéléré, ASM |
| `Riemann_Lab_Test` | Tests ponctuels, Codespaces |
| `main` | Production — merge depuis `Riemann_Lab_IA` |

> Convention : toutes les branches suivent le préfixe `Riemann_Lab_*`.
> `phase-C-core` supprimée le 18 mai 2026 → renommée `Riemann_Lab_C`.

```bash
git checkout Riemann_Lab_IA   # Python, wiki, docs
git checkout Riemann_Lab_C    # Module C, libmpfr, Illinois C
git checkout Riemann_Lab_Test # Tests ponctuels
```

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

> **nvtop :** lire le graphe historique du haut (fiable), pas la colonne GPU%
> par processus (bursts ~50 ms invisibles à l'échantillonnage 2 s).
> `OLLAMA_MODELS=/mnt/data/models_ia/ollama` · `OLLAMA_CUDA=1` (`.bashrc`).
> 1 seul modèle LLM à la fois (4 GB VRAM).

---

## 🤖 Stack « Second Cerveau IA »

### LLM locaux (Ollama)

| Modèle | Taille | Statut | Rôle |
|---|---|---|---|
| `mathstral:latest` | 4.1 GB | ✅ | Maths + ζ(s) symbolique |
| `deepseek-coder:6.7b` | 3.8 GB | ✅ | Code Python/C |
| `qwen3:4b` | ~2.5 GB | ✅ | Polyvalent rapide |
| `deepseek-math:7b` | ~3.8 GB | 🔜 | Meilleur raisonnement math pur |
| `phi3:mini` | ~2.3 GB | 🔜 | Ultra-léger |

```bash
ollama pull deepseek-math:7b
ollama pull phi3:mini
```

### LLM en ligne (navigateur)

| Outil | Modèle | Usage |
|---|---|---|
| Claude | Sonnet 4.5 | Cerveau de session — mémoire, structure, maths longues, wiki |
| Copilot ⭐ | GPT-4.5 | Cadrage Phase C, génération PDF + prompts voie B/v5 |
| Perplexity | — | Recherche web + arXiv |
| Kimi | — | Lecture longs PDF (Titchmarsh, Odlyzko) |
| DeepSeek | — | Raisonnement math alternatif |

### Skills Claude

| Skill | Statut | Rôle |
|---|---|---|
| `riemann-lab` | ✅ | Mémoire projet — KaTeX, wiki, Python, Git |
| `phase-c-illinois` | ✅ | Phase C — libmpfr, Illinois C, ctypes |
| `code-review` | 🔜 | Audit code Python/C |
| `security-review` | 🔜 | Vérif sécurité scripts et `.so` |
| `mattpocock/skills` | 🔜 (Obj. 2) | Skills communautaires généralistes |

### MCP · RAG · Tools

| Outil | Statut | Rôle |
|---|---|---|
| Context7 (MCP) | 🔜 | Doc à jour (mpmath, numpy, libmpfr) injectée dans Claude |
| LlamaIndex | 🔜 | RAG — ingestion PDFs + wiki + GitHub |
| ChromaDB | 🔜 | Base vectorielle locale `~/projet_zeta/brain/` |
| sentence-transformers | 🔜 | Embeddings locaux |
| Manim | 🔜 | Animations math (style 3Blue1Brown) |
| Flowise | 🔜 (fin Obj. 1) | Second Cerveau visuel low-code |
| n8n / Activepieces | 🔜 (Obj. 2) | Automatisation GitHub → mail → publication |
| LangChain / LM Studio | 🔜 (Obj. 2) | Framework agent complet |

```bash
pip install manim llama-index chromadb sentence-transformers
npx flowise start   # http://localhost:3000
```

---

## 📋 Roadmap

### Objectif 1 — finalisation (10 000 zéros → 100 000 zéros)
- [x] Run `compute_zeros_v4_1` à T=10 000 — **10 141 zéros, Turing COMPLET, 18.65 z/s** ✅
- [x] Comparer aux tables LMFDB — 19/20 précision ≤ 1e-10 ✅
- [x] Visualisations dans `/docs` — 8 animations HTML + index.html, validées Playwright ✅
- [x] Logo PNG statique `docs/images/logo_riemann_lab.png` — README + wiki Home.md, 4 branches ✅
- [x] Run T=100 000 — **138 069 zéros, Turing COMPLET, 30.9 min, 74.49 z/s (v7)** ✅
- [x] Site GitHub Pages mis à jour v6+v7 — commit `9dc0d23`, vérifié 11 juin 2026 ✅
- [x] Benchmark v8 — prec_fast/prec_full + W=4 vs W=8 → plancher hardware i7 atteint ✅
- [ ] v8 test T=10 000 en cours — critères : Turing COMPLET · LMFDB 19/20 · 0 manquant
- [ ] Wiki — Partie 2 (Z(t), zéros non-triviaux).
- [ ] Fix lien PDF cassé dans `Phase-Optimisation-compute_zeros_v3.md` + `git push origin master`.
- [ ] v9 en réflexion : CPU upgrade (W=8 réel) ou algo (Arb acb_dirichlet_hardy_z)

### Phase C — accélération Illinois
- [x] Appliquer + valider Option B (`illinois_refine` fa/fb depuis Python) — T=10 000 ✅
- [ ] Rapport `v5 → v4.1` : `pdf/optimisation/analyse_problemes_v5_v4_1.pdf`.

### Objectif 2 — agent IA autonome
- [ ] Anthropic Skilljar : Claude Code 101 → MCP intro/avancé → Subagents → Agent Skills.
- [ ] MCP → connexion GitHub / wiki.
- [ ] Agent capable de : publier sur `hprzeta.github.io/Riemann_Lab/`, générer les
      rapports v→v+1, envoyer les résultats à `hprzeta@protonmail.com`, collaborer
      avec des IA universitaires.

### Formation
| Ressource | Usage |
|---|---|
| roadmap.sh | Roadmaps Python, IA, agents |
| build-your-own-x | Implémenter RAG / agent / LLM from scratch |
| Anthropic Skilljar | Parcours Claude Code → MCP → Subagents |

---

## 📚 PDF de cadrage et cours (Voie B5)

| PDF | Thème | Message clé |
|---|---|---|
| 01 | Cartographie diagnostic | Conserver l'historique, ne pas repartir de zéro |
| 02 | Migration / Brain Vault / RAG | Structure, recovery, données validées |
| 03 | Checklist Linux | Git, GPU, Python, Ollama, partitions |
| 04 | Scripts post-audit | Extraction archive, mini-audit Git |
| 05 | Complément Git | Branches confirmées, `Riemann_Lab_C` = c_modules |
| 06 | Lexique IA & Brain Vault | Vault, RAG, Skills, agents, grounding |
| 07 | Pavé primalité | Premiers, produit eulérien, ψ(x), formule explicite |
| 08 | CryptoZeta | RSA, ECC, post-quantique, hash, recovery |
| 09 | Synthèse Phase C v4 voie B | v4 hybride validé T=650 |
| 10 | Résumé + prompt v5 | Passerelle → Claude Code voie B/v5 |

---

## 🔗 Références

| Ressource | Lien |
|---|---|
| Site du projet | https://hprzeta.github.io/Riemann_Lab/ |
| Code source | https://github.com/hprzeta/Riemann_Lab/tree/Riemann_Lab_IA/src |
| LMFDB | https://lmfdb.org/zeros/zeta/ |
| Odlyzko & Schönhage 1988 | https://doi.org/10.1090/S0002-9947-1988-0936813-0 |
| Turing 1953 | https://doi.org/10.1112/plms/s3-3.1.99 |
| Titchmarsh — Theory of ζ (§4.12) | https://archive.org/details/theoryofriemann00titc |

---

## Progression des versions — T = 10 000 zéros

| Version | Temps | Gain vs v1 | Algorithme clé | Formule principale |
|---|---|---|---|---|
| v1 | 21h | — | Newton scalar | $\zeta(\frac{1}{2}+it)$ Newton séquentiel, 1 worker |
| v2 | 2h | ×10 | Illinois + Z(t) | $Z(t) = e^{i\theta(t)}\zeta(\frac{1}{2}+it)$ · bracket Illinois |
| v3 | 45min | ×28 | Parallèle W=4 | T/W par worker · post-fork .so · N(T) corrigé |
| v4.1 | 9min | ×140 | Illinois C/libmpfr | `illinois_mpfr.c` · $(f_a, f_b)$ pré-calculés Python→C |
| **v4.1+Arb** | **2.60 min** | **×484** | **Arb + STEP adaptatif** | Arb ×27 · STEP 0.05/0.010 · overlap=2.0 · Turing COMPLET |

> ×484 = 21h / 2.60 min — mesuré T=10 000 (2026-06-10 · commit `50837f7`).
> STEP adaptatif **v3** (commit `181fdd1`) : 0.05 (t<5k) / 0.010 (t≥5k) + overlap fixe 2.0.

Speedup Arb vs mpmath : ×27 (0.77 ms vs 21.13 ms, mesuré `benchmark_arb_vs_mpmath_20260609`)

---

## Progression des versions — T = 100 000 zéros

| Version | Temps | Gain | Zéros | Algorithme clé | Commit |
|---|---|---|---|---|---|
| v1 (STEP=0.1 fixe) | ~1h58 | — | 137 904 | baseline | — |
| v2 (STEP adaptatif 0.1/0.05/0.02) | ~105 min | — | 138 039 | Turing INCOMPLET ❌ | — |
| v3 (STEP adaptatif 0.05/0.010) | ~113 min | — | 138 069 | scan_arb.c Z_double | `181fdd1` |
| v6 (STEP=0.010 fixe, scan_arb.c) | ~130 min | — | 138 069 | Z_double C inline · 0 manquant ✅ | `b676e88` |
| v7 (illinois_refine_adaptive) | 30.9 min | ×4.2 vs v6 | 138 069 | prec=64 bits → 1 limb → SIMD ×16 | `8637098` |
| **v8 (prec_full=80 bits)** | **~29 min** | **×1.06 vs v7** | **138 069** | **prec_full 116→80 bits (×1.06 benchmark)** | — |

**Gain global v1 → v8 : ×5 628** (21h → ~29 min)

> **Découverte v7 :** réduire $N_\text{termes}/4$ invalide les signes Z_rs (faux zéros).
> Le vrai levier : `prec_fast = 64 bits` → 1 limbe mpfr → SIMD AVX2 automatique.
> Gain ×16 local (phase 1), ×3.7 global. Analyse : `analyse_problemes_v6_v7.md`.

> **Benchmark v8 :** `prec_full=80 bits` → ×1.06 (gain marginal). W=8 contre-productif sur
> i7-7500U (dual-core HT, 4 threads logiques). Plancher hardware atteint. Voir §24 Formules_zeta.md.

**Run T=10 000 v4.1+Arb validé :** 10 141/10 142 zéros · 2.60 min · Turing COMPLET · LMFDB 19/20

---
> *Mise à jour : 6 juin 2026 · 9 juin 2026 (Progression v1→v5) · 10 juin 2026 (×484 T=10k) · **11 juin 2026 (v6+v7, ×5 292) · 11 juin 2026 soir (v8 prec_full=80 bits, plancher i7)** · STACK.md · ~235 lignes · logo PNG*
