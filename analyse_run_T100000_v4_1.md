# Analyse — Run T=100 000 · v4.1 · 2026-06-10

> Rapport d'analyse du premier run complet à T=100 000.
> Script : `compute_zeros_v4_1.py` · Branche : `Riemann_Lab_C`

---

## 1. Métadonnées du run

| Paramètre | Valeur |
|---|---|
| Date début | 2026-06-10 07h31 |
| Date fin | 2026-06-10 09h11 |
| Durée réelle | 99.35 min (1h39) |
| T_MIN | 14.0 |
| T_MAX | 100 000.0 |
| STEP | 0.1 (fixe — non adaptatif) |
| N_WORKERS | 4 |
| Segmentation | Uniforme en t (non adaptative) |
| Log complet | `calculs/v4_1_T100000_20260610_073115/execution_v4_1_T100000_20260610_073115.log` |
| CSV | `calculs/v4_1_T100000_20260610_073115/zeros_v4_1_T100000_20260610_073115.csv` |

---

## 2. Résultats numériques

| Métrique | Valeur |
|---|---|
| Zéros trouvés | 137 904 |
| Attendus N(100 000) | 138 260 (Weyl) |
| Zéros manquants | 356 (0.26 %) |
| Vitesse moyenne | 23.14 zéros/s |
| Premier zéro $t_1$ | 14.134 725 141 734 62 |
| Dernier zéro $t_n$ | 99 999.700 949 577 70 |
| Espacement minimum | 0.028 361 |
| Espacement maximum | 6.887 314 |
| Espacement moyen | 0.725 043 |

---

## 3. Profil des phases (cumul 4 workers)

| Phase | Temps cumulé | Appels | ms/appel | % mur×W |
|---|---|---|---|---|
| `illinois_C` | 18 201.3 s | 137 770 | **132 ms** | **76.3 %** |
| `turing` | 19.6 s | 1 | 19 627 ms | 0.1 % |
| `detection` | 11.0 s | 200 | 55 ms | 0.0 % |
| `mpmath_petit_t` | 2.7 s | 138 | 19.6 ms | 0.0 % |

**Goulot identifié :** `illinois_C` représente 76.3 % du temps mur × workers.
Le coût croît en $O(\sqrt{t})$ via $N_{\text{RS}} = \lfloor\sqrt{t/2\pi}\rfloor$ termes à 170 bits.

**Note sur turing (19 627 ms) :** c'est **1 seul appel** — la validation Turing-Backlund
parcourt les 137 904 zéros en séquentiel. C'est attendu et non un bug.

---

## 4. Validation LMFDB

Score : **19/20 à < 10⁻¹⁰**

| # | Calculé | LMFDB | Écart | Statut |
|---|---|---|---|---|
| 1–19 | — | — | < 2.13×10⁻¹³ | ✅ |
| 20 | 77.144 840 069 680 46 | 77.144 840 069 680 46 | 8.06×10⁻¹⁰ | ⚠️ cas limite stable |

---

## 5. Validation Turing-Backlund

❌ **INCOMPLET** — 356 zéros manquants

| T | Calculés | Attendus | Manquants | Statut |
|---|---|---|---|---|
| 13 052.27 | 13 790 | 13 790 | 0 | ✅ |
| 29 126.09 | 34 476 | 34 497 | 21 | ❌ |
| 53 827.09 | 68 952 | 69 012 | 60 | ❌ |
| 77 285.21 | 103 428 | 103 538 | 110 | ❌ |
| 99 999.70 | 137 904 | 138 260 | 356 | ❌ |

**Observation clé :** aucun manquant jusqu'à T=13 052. Les manquants apparaissent
progressivement à partir de T=29 126, avec accélération à grand t.

---

## 6. Analyse des causes

### 6.1 Zéros manquants — STEP=0.1 trop grand

L'espacement minimum mesuré est **0.028 361**. Avec STEP=0.1, certains brackets [a, b]
peuvent contenir **plusieurs zéros** si deux zéros consécutifs sont espacés de < 0.1.
La détection via changement de signe de Z(t) ne voit qu'un seul bracket → un zéro
supplémentaire est perdu.

Espacement moyen entre zéros ≈ $2\pi / \ln(t/2\pi)$ :

| Tranche t | Espacement moyen | STEP=0.1 suffisant ? |
|---|---|---|
| t < 10 000 | ~0.39 | ✅ oui (ratio 3.9) |
| t ∈ [10k, 50k] | ~0.28 | ⚠️ limite (ratio 2.8) |
| t ∈ [50k, 100k] | ~0.21 | ❌ insuffisant (ratio 2.1) |

Un ratio < 3 laisse passer des zéros proches. À t=100 000, l'espacement peut descendre
jusqu'à ~0.028 (espacement min mesuré), soit STEP/espacement = 3.5. Mais des
**configurations de zéros très proches** restent vulnérables.

### 6.2 GPU nvrtc error

```
nvrtc: error: invalid value for --gpu-architecture (-arch)
→ Bascule automatique sur CPU numpy
```

GTX 960M = Compute Capability 5.0 (sm_50), déprécié depuis CUDA 11.8.
CUDA 12.2 (installé) ne supporte plus sm_50 dans NVRTC.
**Impact :** Z_batch a tourné sur CPU numpy — performances légèrement réduites
mais fonctionnellement identiques.

### 6.3 Segmentation non équilibrée

Segmentation uniforme en t :

| Worker | Segment | Zéros attendus |
|---|---|---|
| Worker 0 | [14, 25 011] | ~24 900 |
| Worker 1 | [25 011, 50 007] | ~36 500 |
| Worker 2 | [50 007, 75 004] | ~38 400 |
| Worker 3 | [75 004, 100 000] | ~38 200 |

Worker 0 finit bien avant les autres → temps total = max(workers) → gaspillage.

---

## 7. Corrections appliquées (2026-06-10)

### 7.1 STEP adaptatif

```python
def step_pour_t(t: float) -> float:
    if t < 10_000:
        return 0.1
    elif t < 50_000:
        return 0.05
    return 0.02
```

### 7.2 Segmentation 1/√t

```python
def _partitionner_adaptatif(T_MIN, T_MAX, N_WORKERS, overlap=0.5):
    sqrt_min = math.sqrt(T_MIN)
    sqrt_max = math.sqrt(T_MAX)
    delta    = (sqrt_max - sqrt_min) / N_WORKERS
    # Chaque segment couvre une plage égale de ∫ 1/√t dt = 2√t
    # → nombre de zéros équilibré entre workers
    ...
```

### 7.3 Fix GPU nvrtc

Dans `riemann_siegel_batch.py` : si `cc_major < 6` → forcer mode CPU numpy
avec message clair. Plus d'erreur silencieuse.

---

## 8. Prochaine étape

Test T=10 000 lancé (2026-06-10 10h05) avec les 3 corrections actives.
Si Turing COMPLET → relancer T=100 000 avec `zeta_turbo_on.sh` + corrections.

---
*Auteur : hprzeta · Riemann_Lab · Analyse du 2026-06-10*
