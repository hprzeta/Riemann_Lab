# Analyse v8 → v9 — Brent C/mpfr vs Illinois

**Date :** 2026-06-12  
**Branche :** Riemann_Lab_C  
**Auteur :** hprzeta  

---

## 1. Contexte

v8 (11 juin 2026) avait atteint le **plancher hardware** du i7-7500U :
- `prec_full = 80 bits` → gain ×1.06 vs v7 (116 bits) → marginal
- `W = 8 workers` → ×0.99 vs W=4 → context-switching dual-core HT
- Référence v7 T=100k : **30.9 min, 74.49 z/s** (avec turbo)

Seul levier algorithmique restant : **réduire le nombre d'itérations** d'affinage.

---

## 2. Hypothèse v9

La méthode de Brent (Van Wijngaarden-Dekker-Brent) a un **ordre de convergence ~1.84** vs Illinois-modifié ~1.44. Chaque itération coûte **1 seul appel Z_rs_mpfr_ntermes** (identique à Illinois). Gain attendu : ×1.2–1.4 local sur les itérations → ×1.2 global (gain asymptotique réduit par la détection, turing, etc.).

| Méthode   | Ordre | Évals/iter | Gain iter | Verdict  |
|-----------|-------|-----------|-----------|----------|
| Illinois  | 1.44  | 1         | baseline  | ✓ v8     |
| **Brent** | **~1.84** | **1** | **~×1.7** | **✅ v9** |

---

## 3. Implémentation

### brent_mpfr.c

Fichier : `src/calculs/optimisation/c_modules/brent_mpfr.c`

Algorithme IQI + sécante + bissection avec 5 conditions de sécurité :
```
cond1 : s ∉ [(3a+b)/4, b] → force la convergence vers b
cond2 : mflag && |s-b| ≥ |b-c|/2 → pas assez de progrès
cond3 : !mflag && |s-b| ≥ |c-d|/2 → idem
cond4 : mflag && |b-c| < tol → stagnation
cond5 : !mflag && |c-d| < tol → stagnation
```

Invariant Brent : `|f(b)| ≤ |f(a)|` maintenu à chaque itération par swap.

### Paramètres v9

```python
ITER_SWITCH = 3   # Brent : 3 itérations phase1 suffisent (vs 8 Illinois)
MAX_ITER    = 50  # identique à v8 par sécurité
PREC_FAST   = 64  # phase 1 — 1 limbe SIMD (inchangé)
PREC_FULL   = 80  # phase 2 — optimal mesuré (inchangé)
```

### Compilation

```bash
cd src/calculs/optimisation/c_modules
make illinois_mpfr.so
# GCC compile illinois_mpfr.c brent_mpfr.c ensemble → même .so
```

---

## 4. Benchmarks

### 4.1 benchmark_methodes.py — Illinois (v8 référence)

500 zéros distribués dans [1000, 100000] depuis le CSV T=100k v7.

| Métrique | Valeur |
|---|---|
| ms/appel moyen | **128.9 ms** |
| ms/appel médiane | 118.4 ms |
| ms/appel t=1k | 6.76 ms |
| ms/appel t=10k | 53.28 ms |
| ms/appel t=50k | 106.43 ms |
| ms/appel t=77k | 192.56 ms |
| Iter phase1 (moy) | 8.0 (ITER_SWITCH fixe) |
| Iter phase2 (moy Python) | 39.7 |
| Iter totales (moy) | 47.7 |

**Observation clé :** le coût croît fortement avec t (proportionnel à N_full = floor(√(t/2π)) × coût MPFR). Le benchmark précédent (benchmark_v8.py) ne mesurait que t ∈ [1000, 3000] → 0.416 ms biaisé bas.

### 4.2 test_brent.py — Comparaison Brent vs Illinois (100 zéros, t ∈ [1000, 50000])

| Méthode | ms/appel moy | iter moy | gain |
|---------|-------------|----------|------|
| Illinois (v8) | 12.0 ms | 45.1 | baseline |
| **Brent (v9)** | **6.75 ms** | **27.2** | **×1.78** |

### 4.3 Validation T=10k v9

| Indicateur | v8 | v9 | Δ |
|---|---|---|---|
| Zéros | 10 142 | 10 142 | = |
| Durée | 17.2 s | **16.6 s** | −3.5% |
| Vitesse | 591 z/s | **609 z/s** | +3% |
| Turing | COMPLET | COMPLET | = |
| LMFDB | 19/20 | 19/20 | = |
| brent_C % | — | 98.6% | — |

**Note :** à petit t (T=10k), le gain Brent est modeste (+3%) car N_full est petit (faible coût/iter). Le gain ×1.78 du benchmark (t ∈ [1000,50000]) devrait être mieux représenté à T=100k où la majorité des zéros est à grand t.

---

## 5. Limitation RS connue (t < 300)

`brent_refine_adaptive` utilise `Z_rs_mpfr_ntermes` dont l'erreur intrinsèque est O(t^{-3/4}).  
Pour t < 300 : N_full < 7 termes → erreur RS ~1e-2 → imprécis.  
**Identique à Illinois v8** — pour t < 300, v9 utilise mpmath.findroot (1.4% des zéros).

---

## 6. Décision go/no-go

| Critère | Seuil | v9 | Verdict |
|---|---|---|---|
| Gain ms/appel (benchmark) | ≥ ×1.05 | **×1.78** | ✅ GO |
| T=10k zéros manquants | 0 | 0 | ✅ GO |
| T=10k Turing | COMPLET | COMPLET | ✅ GO |
| T=10k LMFDB | ≥ 19/20 | 19/20 | ✅ GO |

**Décision : GO pour T=100k v9.**

---

## 7. Questions ouvertes

- Le gain réel sur T=100k sera mesuré fin de run (estimé ~43 min sans turbo, ~35 min avec).
- Si gain < ×1.1 : explorer Arb `acb_dirichlet_hardy_z` (TÂCHE 6 — optionnelle).
- Amélioration possible : pré-calculer `mpfr_const_pi` une seule fois par worker (évite N_iter recomputations) → gain supplémentaire possible.

---

*analyse_problemes_v8_v9.md · Riemann_Lab.wiki/master · 2026-06-12 · ~120 lignes*

---

## 8. Résultats réels T=100k (mesurés 2026-06-12)

| Indicateur | v8 | v9 sans turbo | v9 avec turbo |
|---|---|---|---|
| Algorithme | Illinois C/mpfr | **Brent C/mpfr** | **Brent C/mpfr** |
| Durée T=100k | ~50.5 min | **28.0 min** | **26.6 min** |
| Vitesse | ~45.6 z/s | **82.15 z/s** | **86.5 z/s** |
| Gain vs v8 | — | **×1.80** | **×1.89** |
| Gain turbo v9 | — | — | **×1.05** |
| Zéros / manquants | 138 069 / 0 | 138 069 / 0 | 138 069 / 0 |
| Turing | COMPLET | COMPLET | COMPLET |
| LMFDB | 19/20 | 19/20 | 19/20 |
| Gain cumulé v1→v9 | — | ×4 300 | **×4 500** |

### Gain turbo ×1.05 — explication

Le gain turbo v9 (×1.05) est bien inférieur au gain turbo v7 (×1.63) :
- Brent C est limité par **bande passante mémoire** (opérations MPFR 64→80 bits), pas par fréquence CPU
- Le governor `performance` accélère le calcul ALU mais pas les accès mémoire/cache MPFR
- Note : swappiness était déjà à 10 lors du run "sans turbo" → comparaison légèrement biaisée

## 9. Fix sudoers (2026-06-12)

`/etc/sudoers.d/zeta_turbo` installé — `zeta_turbo_on.sh` fonctionnel sans mot de passe.
⚠️ Ubuntu 24.04 : sysctl = `/usr/sbin/sysctl` (pas `/sbin/sysctl`).

## 10. Prochaines étapes — v10

- W=8 workers → ×1.6–1.9 (CPU i7 dual-core HT, 4 threads logiques → W=8 peut aider si idle threads)
- Cache (fa,fb) scan→Brent → ×1.1–1.3 (évite 2 évals Z de setup)
- Cible : ~10 min T=100k

*analyse_problemes_v8_v9.md · Riemann_Lab.wiki/master · MAJ 2026-06-12 soir · résultats réels run turbo*
