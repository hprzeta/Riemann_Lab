> **Fichier :** Roadmap.md · **Dossier :** wiki racine
> **Branche :** master (wiki) · **Auteur :** hprzeta · **MAJ :** 2026-06-12

# 🗺️ Roadmap — Riemann Lab

Feuille de route globale du projet : où on en est, où on va,
et **pourquoi chaque version compte**.

---

## Vue d'ensemble — 2 objectifs

```
Objectif 1 ──────────────────────────────────────────► Objectif 2
Calcul industriel des zéros                          Agent autonome
T=100k validé ✅                                     IA locale + publication
→ T=1M fiable < 5 min/100k                          automatique
```

---

## Objectif 1 — Calcul des zéros non-triviaux

### Pourquoi T=1 000 000 ?

Les 138 069 premiers zéros (T=100k) sont déjà dans LMFDB — pas original.
À T=1M → **~1 500 000 zéros** sur hardware modeste = contribution réelle.
C'est aussi la démonstration que le pipeline est **industriellement fiable**
avant de le confier à un agent autonome.

### Condition de passage à l'Objectif 2

**T=100k en < 5 minutes**, 0 zéro manquant, Turing-Backlund automatisé.

Pourquoi < 5 min ? L'agent autonome (Objectif 2) doit pouvoir lancer
des segments de calcul sans attendre des heures entre chaque résultat.

### Le mur de coût

Le coût croît en $O(T \cdot \sqrt{T})$ — la formule de Riemann-Siegel
nécessite $N(t) \approx \sqrt{t/2\pi}$ termes par évaluation $Z(t)$ :

$$T_{\text{total}} \approx \frac{N(T) \cdot \bar{n}_{\text{iter}} \cdot t_{\text{eval}}(T)}{W}$$

| T | Zéros | v9 (26.6 min/100k) | Cible v12 (< 5 min) |
|---|---|---|---|
| 100 000 | 138 069 | 26.6 min ✅ | < 5 min |
| 500 000 | ~760 000 | ~2.5h | ~25 min |
| **1 000 000** | **~1 500 000** | **~8h** | **~50 min** |

---

## Progression des versions — v1 → v∞

### Versions validées

| Ver. | Temps T=100k | Gain v1→vN | Algo clé | Date |
|---|---|---|---|---|
| v1 | 21h | ×1 | Newton scalar séquentiel | 2026-04 |
| v2 | 2h | ×10 | Illinois + Z(t) brackets | 2026-04 |
| v3 | 45min (T=10k) | ×28 | W=4 parallèle post-fork | 2026-05 |
| v4.1 | 9min (T=10k) | ×140 | Illinois C/libmpfr (fa,fb) | 2026-05 |
| v5 | ~1min (T=10k) | ×1 260 | `arb_fpwrap_cdouble_hardy_z` ×27 | 2026-05 |
| v6 | ~130min | — | `scan_arb.c` Z_double C inline | 2026-06 |
| v7 | 30.9min | ×4.2 vs v6 | `illinois_refine_adaptive` prec=64 SIMD | 2026-06 |
| v8 | ~29min | ~×1.06 vs v7 | prec_full=80 bits | 2026-06 |
| v9 | **26.6min** (turbo) | **×4 500** | `brent_refine_adaptive` C/mpfr 2 phases | 2026-06-12 |

### Versions planifiées

| Ver. | Gain estimé | Algo clé | Cible |
|---|---|---|---|
| **v10** | ×1.6–1.9 | W=8 workers HT + cache (fa,fb) scan→Brent | ~14 min |
| **v11** | ×1.3 | Scan vectorisé AVX2 (4 pts simultanés) | ~10 min |
| **v12** | ×1.5–2 | Précision adaptative par t (prec=48 à petit t) | ~5 min ✅ |

**Cible finale Objectif 1 : v12 < 5 min T=100k → ×~5 400 vs v1**

---

## Leçons clés apprises

### Ce qui accélère vraiment

| Levier | Gain mesuré | Principe |
|---|---|---|
| Arb `hardy_z` vs mpmath | ×27 | double natif, 0 malloc |
| Illinois → Brent C | ×1.80 | ~4 iter vs ~6, même coût/iter |
| prec=64 bits (1 limb SIMD) | ×16 local | AVX2 sur 1 limb mpfr |
| W=4 parallèle | ×4 | post-fork, pas de GIL |

### Ce qui ne sert plus

| Levier | Pourquoi abandonné |
|---|---|
| Turbo CPU (governor performance) | ×1.05 seulement — bottleneck = mémoire MPFR, pas CPU |
| Newton/Halley | 2–3 évals/iter → neutre vs Brent 1 éval |
| Réduction N_termes | Invalide les signes Z_RS → faux zéros |
| `acb_dirichlet_hardy_z` | Plus lent que `arb_fpwrap_cdouble_hardy_z` (allocations) |

### Règles permanentes

- **STEP = 0.010 fixe** — loi de Wigner GUE : $\delta_{\min} \approx 0.030$ → STEP < $\delta_{\min}/3$
- **Charger `.so` POST-FORK** — GMP/MPFR ne se partagent pas cross-fork
- **N_termes = ⌊√(t/2π)⌋** — ne jamais tronquer
- **Passer (fa,fb) Python→C** — éviter 2 recalculs par zéro

---

## Objectif 2 — Agent autonome de recherche

### Prérequis

- ✅ Objectif 1 atteint (< 5 min T=100k)
- ✅ Pipeline 100% fiable (0 zéro manquant, Turing automatisé)
- ✅ BrainVault RAG opérationnel (26 pavés ingérés, RAG WIP)

### Stack prévu

```
LlamaIndex + ChromaDB + sentence-transformers
Ollama local : mathstral · deepseek-coder:6.7b · qwen3:4b
n8n (orchestration workflows)
MCP + Subagents (Claude Code)
```

### Ce que l'agent fera

1. **Lancer des runs** automatiquement sur des segments T disjoints
2. **Valider** Turing-Backlund sans intervention humaine
3. **Publier** résultats sur `hprzeta.github.io/Riemann_Lab/`
4. **Générer** rapports versionnés → wiki + Proton Drive
5. **Collaborer** avec IA universitaires spécialisées (mathématiques)
6. **Explorer** pistes de preuve de l'Hypothèse de Riemann

### Architecture cible

```
compute_zeros_v12.py (< 5 min/segment)
        ↓
   Agent n8n / MCP
   ├── Validation Turing-Backlund
   ├── Push GitHub Pages
   ├── Génération rapport wiki
   └── Mail hprzeta@protonmail.com
        ↓
   BrainVault RAG
   ├── LlamaIndex + ChromaDB
   ├── Ollama mathstral
   └── Ingestion inbox-ia
        ↓
   Collaboration IA universitaires
```

### Formation en cours (Anthropic Skilljar)

| Cours | Statut | Lien Objectif |
|---|---|---|
| Claude Code 101 | ✅ pratiqué | Obj. 1 |
| Claude Code in Action | ✅ pratiqué | Obj. 1 |
| Building with API | 🔄 WIP | Obj. 2 |
| MCP Intro | ⏳ planifié | Obj. 2 |
| MCP Advanced | ⏳ planifié | Obj. 2 |
| Subagents | ⏳ planifié | Obj. 2 |

---

## Horizon — Objectif 3 (recherche formelle)

Une fois l'agent autonome opérationnel :

- **Lean 4** — formalisation des résultats numériques en preuves vérifiées
- **Exploration approaches** — étude des dernières tentatives de preuve de RH
  (approche spectrale, matrices aléatoires GUE, fonctions L, zéros de Selberg)
- **Publication** — rapport académique sur le pipeline + résultats T=1M+

---

## Voir aussi

- [[STACK]] — outils, matériel, formation détaillée
- [[JOURNAL]] — historique daté session par session
- [[Etape-1-Calcul-des-zéros-non-triviaux]] — détail technique v1→v9
- [[Formules_zeta]] — toutes les formules clés
- [Site du projet ↗](https://hprzeta.github.io/Riemann_Lab/)

---

*Roadmap.md · wiki racine · branche master · hprzeta · MAJ 2026-06-12 · 147 lignes*
