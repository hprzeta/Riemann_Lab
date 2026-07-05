# Base de Connaissance — Riemann_Lab
## Pour l'entraînement de l'agent IA autonome (Objectif 2)
> Généré le 19 mai 2026 · Mis à jour le 5 juillet 2026 — hprzeta

---

## 1. Identité du projet

**Nom :** Riemann_Lab  
**Chercheur :** hprzeta  
**GitHub :** https://github.com/hprzeta/Riemann_Lab  
**Site :** https://hprzeta.github.io/Riemann_Lab/  
**Mail :** hprzeta@protonmail.com  
**Wiki :** https://github.com/hprzeta/Riemann_Lab/wiki  

**Double objectif :**
- **Obj. 1** (atteint, poursuivi) : Calcul des zéros non-triviaux de ζ(s), validé ×LMFDB. État au 04/07/2026 : version v15 en production, **10 016 377 zéros** calculés au total, T=100 000 en 4.4 min (517 z/s), run T=5 000 000 terminé.
- **Obj. 2** (**démarré le 04/07/2026**) : Agent IA autonome de recherche mathématique sur l'Hypothèse de Riemann, collaborant avec IA universitaires. Ce document sert de base de connaissance initiale pour son ingestion RAG (voir §7.2).

---

## 2. Mathématiques fondamentales

### 2.1 Fonction zêta de Riemann

**Série de Dirichlet** (Re(s) > 1) :
$$\zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s}$$

**Produit eulérien** :
$$\zeta(s) = \prod_{p \text{ premier}} \frac{1}{1 - p^{-s}}$$

**Prolongement analytique :** ζ(s) est définie sur ℂ \ {1}, pôle simple en s=1.

**Équation fonctionnelle :**
$$\zeta(s) = 2^s \pi^{s-1} \sin\!\left(\frac{\pi s}{2}\right) \Gamma(1-s)\,\zeta(1-s)$$

**Fonction ξ (symétrique) :**
$$\xi(s) = \tfrac{1}{2}s(s-1)\pi^{-s/2}\Gamma\!\left(\tfrac{s}{2}\right)\zeta(s), \qquad \xi(s) = \xi(1-s)$$

### 2.2 Hypothèse de Riemann

**Énoncé :** Tous les zéros non-triviaux de ζ(s) sont sur la droite critique Re(s) = ½.

**Zéros triviaux :** s = −2, −4, −6, … (zéros des facteurs sin(πs/2) dans l'équation fonctionnelle)  
**Zéros non-triviaux :** dans la bande critique 0 < Re(s) < 1

### 2.3 Fonction Z de Hardy

$$Z(t) = e^{i\theta(t)}\,\zeta\!\left(\tfrac{1}{2}+it\right) \in \mathbb{R} \text{ pour } t \in \mathbb{R}$$

**Propriété clé :** Z(t) = 0 ⟺ ζ(½ + it) = 0

Les zéros de Z(t) sont exactement les parties imaginaires des zéros non-triviaux.

### 2.4 Fonction θ(t) de Riemann-Siegel

$$\theta(t) = \text{Im}\!\left[\ln\Gamma\!\left(\tfrac{1}{4}+\tfrac{it}{2}\right)\right] - \frac{t}{2}\ln\pi$$

**Approximation asymptotique (Stirling) — utilisée en production :**
$$\theta(t) = \frac{t}{2}\ln\frac{t}{2\pi} - \frac{t}{2} - \frac{\pi}{8} + \frac{1}{48t} + \frac{7}{5760t^3} + O(t^{-5})$$

### 2.5 Formule de Riemann-Siegel

$$Z(t) = 2\sum_{n=1}^{N}\frac{\cos(\theta(t)-t\ln n)}{\sqrt{n}} + R(t), \qquad N = \left\lfloor\sqrt{\frac{t}{2\pi}}\right\rfloor$$

Le terme de reste R(t) = O(t^{-1/4}) est négligeable pour la détection.

### 2.6 Comptage des zéros — Formule de Riemann-von Mangoldt

$$N(T) = \frac{T}{2\pi}\ln\frac{T}{2\pi e} + O(\ln T)$$

⚠️ **Erreur classique :** utiliser T/(2π)·ln(T/2π) — oubli du **e** dans 2πe.

| T | N(T) correct | Sans e | Erreur |
|---|---|---|---|
| 10 000 | 10 142 | ~7 300 | −28% |
| 100 000 | 138 067 | ~49 346 | −64% |

### 2.7 Méthode de Turing-Backlund (validation de complétude)

Si on a calculé N zéros jusqu'à T, et N(T) = ⌊T/(2π)·ln(T/2πe)⌋,
alors si N ≥ N(T), on a trouvé **tous** les zéros (aucun manquant).

```
delta = N(T) - N_trouvé
delta > 0 : MANQUE (zéros ratés)
delta < 0 : SURPLUS (faux positifs ou T_max dépassé)
delta = 0 : PARFAIT
```

### 2.8 Méthode Illinois (affinage)

Méthode de la sécante modifiée pour affiner un zéro dans un intervalle [a,b] :

```
1. c = b - Z(b)·(b-a)/(Z(b)-Z(a))     ← sécante
2. Si Z(a)·Z(c) < 0 : b ← c
   Sinon            : a ← c, Z(a) ← Z(a)/2    ← correction Illinois
3. Répéter jusqu'à |b-a| < 1e-12
```

### 2.9 Conjecture de Montgomery — espacements GUE

Les espacements normalisés entre zéros consécutifs suivent la distribution
des valeurs propres d'une matrice aléatoire GUE :
$$p(s) = \frac{\pi}{2}\,s\,e^{-\pi s^2/4}$$

C'est une connexion profonde entre la théorie analytique des nombres et la physique quantique.

### 2.10 Formule explicite de Riemann

$$\pi(x) = \text{li}(x) - \sum_{\rho}\text{li}(x^{\rho}) - \ln 2 + \int_x^{\infty}\frac{dt}{t(t^2-1)\ln t}$$

L'HR implique : $|\pi(x) - \text{li}(x)| = O(\sqrt{x}\ln x)$

---

## 3. État computationnel au 04 juillet 2026 (v15)

> Section historique conservée ci-dessous (§3.1-3.2 d'origine, mai 2026) pour mémoire de la
> trajectoire v3→v15. État courant en premier.

### 3.0 Résultats courants (v15)

| Calcul | Résultat |
|---|---|
| Total cumulé | **10 016 377 zéros** non-triviaux calculés |
| T = 100 000 | 4.4 min, 517 z/s (v15, SEUIL_1NEWTON=20k) |
| T = 5 000 000 | Run complet terminé (juillet 2026) |
| Affinage Illinois | Porté en C (`illinois_arb.c`/`.so`), gain majeur vs mpmath pur — Phase C **terminée et en production** (le goulot 80-90% décrit en §3.4 est résolu) |
| Précédent v13→v15 | Voir `analyse_problemes_v13_v15.md` (cache RS + SEUIL_1NEWTON) sur le wiki |

### 3.1 Résultats obtenus (historique, mai 2026)

| Calcul | Résultat | Fichier |
|---|---|---|
| 10 142 zéros jusqu'à T=9 998.85 | Hardy-Z + Illinois, 50 dps | `zeros_zeta_T10000_20260424_205325.csv` |
| 20 zéros de référence | LMFDB | `riemann_zeros.csv` |
| Benchmark BATCH_CPU 15 min | 3 231 zéros, 3.59 z/s | — |
| Benchmark BATCH_GPU 15 min | 3 051 zéros, 3.39 z/s | — |

### 3.2 Validation LMFDB (10 premiers zéros)

Tous les zéros calculés vérifient Re(s) = ½ à moins de 1e-14 d'écart avec LMFDB.

```
γ₁ = 14.134725141734693  (LMFDB)   vs   14.134725141734693  (calculé)  → Δ < 1e-14
γ₂ = 21.022039638771555  (LMFDB)   vs   21.022039638771556  (calculé)  → Δ < 1e-14
```

### 3.3 Architecture logicielle (Python v3)

```
compute_zeros_v3.py         ← orchestrateur
├── theta_rapide.py         ← θ(t) Stirling ×10
├── riemann_siegel.py       ← Z(t) RS ×50
├── riemann_siegel_batch.py ← Z(t) vectorisé NumPy/CuPy
├── parallel_scanner.py     ← 4 workers multiprocessing
├── turing_validation.py    ← N(T) complétude
└── benchmark_15min.py      ← bench
```

### 3.4 Goulot d'étranglement identifié

```
Temps total = Détection Z(t) [10-20%] + Affinage Illinois [80-90%]
                    ↑                            ↑
           GPU ×10 ici (30-50% GPU)    CPU pur mpmath — non GPU
```

**Solution Phase C :** porter Illinois en C + libmpfr → ×5–10 sur l'affinage.

> ✅ **Mise à jour 04/07/2026 :** Phase C terminée et en production (`illinois_arb.c`/`.so`,
> branche `Riemann_Lab_C`). Le goulot Illinois est résolu ; voir §3.0 pour les gains mesurés.
> Architecture v3 (§3.3) obsolète — orchestrateur courant : `compute_zeros_v15.py`.

---

## 4. Hardware

| Composant | Valeur |
|---|---|
| CPU | Intel i7, 4 cœurs |
| RAM | 8 GB + 16 GB swap |
| GPU | NVIDIA GTX 960M, 4 GB VRAM, CUDA 12.2, Compute 5.0 |
| GPU display | Intel HD Graphics 620 |
| OS | Ubuntu 24 LTS |
| Python | 3.12 dans ~/projet_zeta/zeta_env/ |
| nvtop | Recompilé depuis sources — lire le graphe historique, pas la colonne GPU% |

---

## 5. Branches Git

| Branche | Rôle |
|---|---|
| `Riemann_Lab_IA` | Python, wiki, docs, benchmarks — branche principale |
| `Riemann_Lab_C` | Phase C : Illinois en C, libmpfr, ASM |
| `Riemann_Lab_Test` | Tests, expérimentations |
| `main` | Production stable |

---

## 6. Stack LLM locale (Ollama)

```
/mnt/data/ollama/ — partition 651 GB, 590 GB libres
OLLAMA_MODELS=/mnt/data/ollama
OLLAMA_CUDA=1  ← GPU forcé

Modèles installés (état 04/07/2026, tous les 4 présents) :
- mathstral:latest       ← mathématiques (4.1 GB)
- deepseek-coder:6.7b    ← code Python/C (3.8 GB)
- qwen3:4b               ← usage général (2.5 GB)
- phi3:mini              ← modèle léger (2.2 GB)
```

---

## 7. Feuille de route — Objectif 2

### 7.1 Agent IA autonome — Architecture cible

```
Agent principal (Claude Code / claw-code)
    │
    ├── compute_zeros_v4.py  ← calcul + Illinois C
    │        ↓
    ├── turing_validation.py ← validation
    │        ↓
    ├── ChromaDB             ← base vectorielle locale (wiki + PDFs + code)
    │        ↓
    ├── LlamaIndex / RAG     ← requêtes sémantiques
    │        ↓
    ├── Ollama (mathstral)   ← raisonnement local
    │        ↓
    ├── n8n / Flowise        ← orchestration no-code
    │        ↓
    └── GitHub + Site + Mail ← publication automatique
```

### 7.2 Pipeline d'ingestion RAG

> **État 04/07/2026** (bilan complet : `etat_rag_brainvault_20260704.md`) :
> `chromadb` (1.5.9), `langchain`/`langchain-community`/`langchain-core`, `sentence-transformers`
> (5.3.0) **installés** dans `zeta_env`. **`llama-index` manquant** — à installer avant la
> première ingestion. Stockage : SSD dédié **`/mnt/vault_rag`** (et non `~/projet_zeta/brain/`),
> structure `corpus/`, `chromadb/`, `llamaindex_cache/`, `agent_logs/`. Convention d'environnement :
> `VAULT_RAG=/mnt/vault_rag`.

Sources à ingérer dans ChromaDB :
- Wiki Riemann_Lab (pages courantes .md — voir règle d'ingestion dans `etat_rag_brainvault_20260704.md`)
- PDFs : Titchmarsh, Odlyzko (référencés, non possédés localement à ce jour), rapports vN→vN+1, handoff
- Code source (`src/`) — **ingéré directement depuis la branche `Riemann_Lab_C` (raw GitHub)**, jamais dupliqué sur `inbox-ia`
- Transcripts YouTube (3Blue1Brown, etc.)
- LMFDB (tables de zéros)
- arXiv math.NT (prépublications récentes)

```bash
pip install llama-index llama-index-vector-stores-chroma llama-index-embeddings-huggingface
# Chemin : $VAULT_RAG=/mnt/vault_rag (SSD dédié, monté nofail)
```

### 7.3 Cours Anthropic Skilljar — Parcours recommandé

**Objectif 1 (10 000 zéros + Phase C) :**
1. Claude Code 101 → intégration dans ~/projet_zeta/src/
2. Claude Code in Action → automatisation des runs

**Objectif 2 (agent autonome) :**
1. Building with Claude API → agent dialoguant avec IA
2. MCP intro + avancé → connexion GitHub / wiki / outils
3. Subagents → délégation tâches zêta/Turing/R-S
4. Agent Skills → routines réutilisables zêta

**MCP + Subagents = brique manquante** entre compute_zeros_v3.py et l'agent
publiant sur hprzeta.github.io, générant rapports, envoyant résultats à hprzeta@protonmail.com.

---

## 8. Approches modernes de l'Hypothèse de Riemann

### 8.1 Approches numériques

**Odlyzko-Schönhage (1988) :** Calcul de Z(t) en O(T^{1/3+ε}) au lieu de O(T^{1/2}).
Basé sur des méthodes de sommation rapide (FFT). Permet d'atteindre T = 10^{22}.

**État de l'art (2024) :** Plus de 10^{13} zéros vérifiés sur la droite critique.

### 8.2 Approches théoriques actives

**Approche spectrale :** Chercher un opérateur auto-adjoint dont les valeurs propres
sont les parties imaginaires des zéros (connexion avec GUE / matrices aléatoires).

**Approche géométrique (Connes) :** Via la géométrie non-commutative,
interprétation des zéros comme spectre d'un opérateur de Dirac.

**Approche algébrique :** Équivalences via les fonctions L de Dirichlet,
la conjecture de Birch-Swinnerton-Dyer, et les motifs de Grothendieck.

**Blocages actuels :**
- Aucun opérateur explicite connu avec le bon spectre
- La méthode de Connes donne une formule trace, mais pas la preuve
- Les analogues en corps finis (prouvés par Weil/Deligne) ne se transfèrent pas directement

### 8.3 Équivalents de l'Hypothèse de Riemann

| Équivalent | Énoncé |
|---|---|
| Cramér | $|\pi(x) - \text{li}(x)| = O(\sqrt{x}\ln x)$ |
| Robin | $\sigma(n) < e^\gamma n\ln\ln n$ pour $n > 5040$ |
| Li | Les coefficients de Li $\lambda_n$ sont tous positifs |
| Weil | Réinterprétation via les distributions |

---

## 9. Principes de collaboration pour l'Objectif 2

- **Claude** : cerveau principal — structure, maths longues, cohérence sur longues sessions
- **Perplexity** : recherche web + arXiv + prépublications récentes
- **Kimi** : lecture longs PDFs (Titchmarsh, Odlyzko)
- **DeepSeek** : raisonnement mathématique alternatif
- **Ollama (mathstral)** : calcul local, pas de fuite de données

**Règle de validation :**
- Théorème prouvé : citer la source
- Conjecture : marquer "Conjecture"
- Heuristique / intuition : marquer explicitement
- Si une démonstration bloque : dire exactement où

---

## 10. Fichiers clés du projet

| Fichier | Description |
|---|---|
| `compute_zeros_v3.py` | Orchestrateur principal |
| `theta_rapide.py` | θ(t) asymptotique Stirling |
| `riemann_siegel.py` | Z(t) formule Riemann-Siegel |
| `riemann_siegel_batch.py` | Z(t) vectorisé NumPy/CuPy |
| `parallel_scanner.py` | Scanner parallèle 4 workers |
| `turing_validation.py` | Validation N(T) Turing-Backlund |
| `benchmark_15min.py` | Bench comparatif modes |
| `zeros_zeta_T10000_*.csv` | 10 142 zéros calculés |
| `riemann_zeros.csv` | 20 zéros de référence LMFDB |
| `handoff.md` | État projet complet |
| `formules_zeta.md` | Formulaire de référence |
| `analyse_problemes_v2_v3_*.pdf` | Rapport transition v2→v3 |

---

## 11. Commandes utiles

```bash
# Activer l'environnement
source ~/projet_zeta/zeta_env/bin/activate

# Lancer un calcul
python compute_zeros_v3.py --tmax 10000 --mode batch_cpu

# Benchmark 15 min
python benchmark_15min.py --mode batch_cpu --tmax 10000

# Git — pousser sur la branche principale
git checkout Riemann_Lab_IA
git add -A && git commit -m "feat: ..." && git push origin Riemann_Lab_IA

# Ollama
ollama list          # modèles disponibles
ollama run mathstral # démarrer mathstral

# Compiler module C (Phase C)
cd ~/projet_zeta/src/calculs/optimisation/c_modules/
make && python test_illinois.py
```

---

*Ce document est la base de connaissance principale pour l'agent IA autonome.*
*À ingérer dans ChromaDB via LlamaIndex.*
*Mettre à jour à chaque transition de version vN→vN+1.*

---
*Auteur : hprzeta · Dernière mise à jour : 5 juillet 2026 — 384 lignes*
