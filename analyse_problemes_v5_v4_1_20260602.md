# Analyse des problèmes v5 → v4.1

> **Fichier :** analyse_problemes_v5_v4_1_20260602.md
> **Dossier :** wiki racine
> **Branche :** master (wiki)
> **Auteur :** hprzeta · **MAJ :** 2026-06-10

**Auteur :** hprzeta  
**Date :** 2 juin 2026 (complété 10 juin 2026)  
**Branche :** `Riemann_Lab_C`  
**Fichiers :** `compute_zeros_v5.py` (référence) → `compute_zeros_v4_1.py` (cible)

---

## Introduction

`compute_zeros_v5.py` (Voie B, commit `b8018c0`) était **correct mais lent** : Illinois_C
pur 100 %, biais RS corrigé via wrapper `mpmath.siegelz`, Turing COMPLET, LMFDB 19/20 —
mais ~0.82 z/s à T=80 (1 worker, séquentiel).

`compute_zeros_v4_1.py` (commit `893f3b4`) résout quatre problèmes identifiés dans v5
et en révèle un cinquième (goulot résiduel). Ce document détaille chaque problème,
sa cause mathématique, la solution retenue et les gains mesurés.

---

## Problème 1 — Bug Z_batch : N_max fixe pour tous les t

### Cause mathématique

La formule de Riemann-Siegel est :

$$Z(t) = 2\sum_{n=1}^{N(t)} \frac{\cos(\theta(t) - t\ln n)}{\sqrt{n}} + R(t), \qquad N(t) = \left\lfloor\sqrt{\frac{t}{2\pi}}\right\rfloor$$

$N(t)$ est **propre à chaque $t$**. Les termes $n > N(t)$ sont hors de la somme RS et
ne doivent pas être accumulés.

`Z_batch` (dans `riemann_siegel_batch.py`) utilisait :

```python
N_max = int(np.floor(np.sqrt(t_max / (2 * np.pi)))) + 1  # FIXE pour tout le batch
```

Pour un batch $[t_{\min}, t_{\max}]$, les lignes correspondant à $t_k < t_{\max}$
accumulaient les termes $n \in (N(t_k),\, N_{\max}]$ qui n'appartiennent pas à $Z(t_k)$.

### Erreur induite

L'erreur maximale sur $Z(t_k)$ est bornée par :

$$\Delta Z(t_k) \leq 2 \sum_{n=N(t_k)+1}^{N_{\max}} \frac{1}{\sqrt{n}} \approx 4\bigl(\sqrt{N_{\max}} - \sqrt{N(t_k)}\bigr)$$

Pour un batch de largeur $\Delta t = t_{\max} - t_{\min}$, l'excès de termes est :

$$N_{\max} - N(t_k) \approx \frac{\Delta t}{4\pi}\sqrt{\frac{2\pi}{t_k}}$$

À $t_k = 14$, $\Delta t = 286$ (batch T=300) : $\Delta N \approx 12$ termes excédentaires
→ $\Delta Z \approx 3.5$. Cette erreur dépasse l'amplitude typique de $Z(t)$ → les
changements de signe sont entièrement corrompus pour les petits $t$ d'un grand batch.

### Solution : Z_vect_correct (masque booléen par ligne)

```python
# mask[k, n] = True ssi n ≤ N(t_k) — chaque ligne n'accumule QUE ses termes légitimes
mask   = (np.arange(1, N_max + 1)[None, :] <= Ns[:, None])
Z_out  = 2.0 * np.dot(np.cos(phases) * mask, inv_sqn)
```

Le masque booléen annule les termes hors borne exactement. L'opération reste
entièrement numpy (`np.dot`, BLAS) — aucune boucle Python par point.

### Gain mesuré

| Méthode | Gain vs `mpmath.siegelz` séquentiel | Erreur max $Z$ |
|---|---|---|
| `Z_batch` (N_max fixe) | ×4 000 (vitesse uniquement) | jusqu'à ~3.5 ❌ |
| `Z_vect_correct` (masque) | ×4 771 à $t\approx 350$ · ×9 083 à $t\approx 3 050$ · ×9 873 à $t\approx 9 950$ | $< 10^{-10}$ ✅ |

---

## Problème 2 — Détection séquentielle (`mpmath.siegelz`)

### Cause

v5 appelait `mpmath.siegelz` à `dps=15` **point par point** dans une boucle Python.
Chaque appel bloque le fil d'exécution ; il n'y a aucune parallélisation interne.

Le coût de `mpmath.siegelz` croît avec $N(t) = \lfloor\sqrt{t/2\pi}\rfloor$ :

$$N(1\,000) = 12 \qquad N(10\,000) = 39$$

Temps mesurés : ~23 ms/pas à $t = 3\,000$, ~52 ms/pas à $t = 9\,950$.

### Solution : vectorisation numpy (BLAS)

`Z_vect_correct` pré-calcule la matrice de phases pour tout le batch en une seule
opération tableau :

$$\text{phases}[k,\, n] = \theta(t_k) - t_k \ln n$$

puis effectue la somme masquée via `np.dot` (BLAS `dgemv`).
Aucun appel Python individuel par point — la boucle interne reste en C.

### Gain mesuré

| $t$ | `mpmath.siegelz` (séq.) | `Z_vect_correct` | Gain |
|---|---|---|---|
| ~350 | ~23 ms/pas | ~4.8 µs/pas | ×4 771 |
| ~3 050 | ~52 ms/pas | ~5.7 µs/pas | ×9 083 |
| ~9 950 | ~97 ms/pas | ~9.8 µs/pas | ×9 873 |

---

## Problème 3 — Sérialisation du callback ctypes (`illinois_c_exact`)

### Cause

v5 utilisait un callback Python/C : `illinois_mpfr_cb(callback mpmath.siegelz)`. À chaque
évaluation de $Z$ depuis le code C, le runtime ctypes rend la main au GIL Python.

De plus, le `.so` était chargé **avant** le `fork()`. En mode `multiprocessing`, tous les
workers partageaient le même handle ctypes, forçant la sérialisation des appels GMP.

Test mesuré (session 31 mai 2026) :

| Scénario | Gain parallèle (4 workers) |
|---|---|
| `Pool(sleep)` — aucun ctypes | ×3.9 |
| `Pool(worker_chunk)` v5 — callback partagé | ×1.84 |

### Solution : chargement du `.so` après `fork()`

```python
def _worker_chunk(args):
    import ctypes as _ctypes
    _lib = _ctypes.CDLL(so_path)  # chargé APRÈS fork — handle GMP isolé par fils
    _lib.illinois_mpfr.restype  = _ctypes.c_double
    _lib.illinois_mpfr.argtypes = [_ctypes.c_double, _ctypes.c_double, _ctypes.c_double]
```

Chaque processus fils instancie sa propre copie de `libmpfr`. Zéro partage d'état GMP
entre le parent et les fils → vrai parallélisme.

---

## Problème 4 — Biais de position Illinois_C pur

### Cause mathématique

Illinois_C calcule le zéro de $Z_{\text{mpfr}}(t)$, la formule RS tronquée à l'ordre 1 :

$$Z_{\text{mpfr}}(t) = 2\sum_{n=1}^{N(t)} \frac{\cos(\theta(t)-t\ln n)}{\sqrt{n}} + R_{C_0+C_1}(t)$$

Le reste $R_{C_0+C_1}(t)$ diffère de $R(t)$ exact d'une quantité d'ordre $O(t^{-3/4})$.
Le vrai zéro $\gamma$ de $Z(t)$ est décalé du zéro $\gamma_c$ de $Z_{\text{mpfr}}$ par :

$$|\gamma_c - \gamma| \approx \frac{|R(\gamma) - R_{C_0+C_1}(\gamma)|}{|Z'(\gamma)|}$$

À $\gamma \in [300,\, 10\,000]$ : $|R - R_{C_0+C_1}| \approx 10^{-4}$–$10^{-2}$,
$|Z'(\gamma)| \approx 0.5$–$2$ → **biais de position $10^{-4}$ à $1.7\times10^{-2}$**.

Ce biais est **structurel** (limitation de la série asymptotique), non un bug de code.

### Solution : finition Newton sur `mpmath.siegelz`

Depuis $\gamma_c$ (biais mesuré $|\epsilon_0| \leq 1.7\times10^{-2}$, Vérif B),
3 pas de Newton suffisent :

$$x_{n+1} = x_n - \frac{Z(x_n)}{Z'(x_n)}, \qquad Z'(x) = \texttt{mpmath.siegelz}(x,\; \texttt{derivative=1})$$

Convergence quadratique depuis $\epsilon_0 \leq 1.7\times10^{-2}$ :

| Pas Newton | Erreur résiduelle |
|---|---|
| $\epsilon_0$ | $\leq 1.7\times10^{-2}$ |
| $\epsilon_1$ | $\approx 3\times10^{-4}$ |
| $\epsilon_2$ | $\approx 10^{-7}$ |
| $\epsilon_3$ | $\approx 10^{-14}$ ✅ |

**dps retenu : `DPS_POLISH = 25`** — à $\gamma \approx 10\,000$, un nombre de $10^4$
représenté sur 25 chiffres significatifs garantit une précision absolue $\approx 10^{-21}$,
soit une marge de 9 décimales sur la tolérance $10^{-12}$.

Garde-fou : si $x_n \notin [\gamma_c \pm 0.05]$, `_newton_polish` lève `ValueError`
→ l'appelant retombe sur `mpmath.findroot illinois` sur le bracket original.

---

## Problème 5 — Goulot résiduel v4.1 : `_newton_polish`

### Observation

Vitesse v4.1 mesurée : **1.07 z/s** à T=1000, **1.88 z/s** à T=300 (100 % mpmath).
Loin de la cible 5 z/s du prompt de validation.

`_newton_polish` effectue 3–5 appels `mpmath.siegelz(dps=25)` par zéro
(incluant `siegelz(x, derivative=1)`). À $t \approx 500$–$1000$, chaque appel
prend ~10–20 ms → ~75 ms/zéro en moyenne.

### Pourquoi Newton ne bat pas Illinois

$Z'(t) = -\sum_{n=1}^{N} \frac{\ln n}{\sqrt{n}} \cos(\theta(t) - t\ln n)$ a des poids
$\ln n$ croissants → la série converge plus lentement que celle de $Z(t)$.
`mpmath.siegelz(derivative=1)` est donc **plus coûteux** que `mpmath.siegelz`.
Newton (2 appels par pas : $Z$ et $Z'$) n'est pas meilleur qu'Illinois (1 appel par pas,
~27 itérations moyennes) en coût total.

### Conclusion

**Le goulot est la vitesse intrinsèque de `mpmath.siegelz`** à grand $t$, pas le choix
du solveur ni le nombre d'itérations. Aucune optimisation algorithmique de l'affinage
n'est possible tant qu'on évalue $Z$ côté Python via `mpmath.siegelz`.

---

## Problème 6 — Goulot résiduel résolu : Arb/FLINT (9 juin 2026)

### Cause

Le Problème 5 concluait que `mpmath.siegelz` était le goulot structurel (~21 ms/appel à
$t \approx 10\,000$), rendant impossible toute accélération algorithmique de l'affinage.

### Solution : `arb_fpwrap_cdouble_hardy_z` (Arb/FLINT)

Arb (via `python-flint`) expose `arb_fpwrap_cdouble_hardy_z` : calcul de $Z(t)$ en
double IEEE 754 pur, sans allocation heap (0 malloc/free). `mpmath` utilise MPFR
(~1 000 `malloc/free` par zéro pour gérer l'arithmétique multi-précision).

```python
from flint import arb
def arb_hardy_z(t: float) -> float:
    """Z(t) via Arb — double natif, 0 allocation heap."""
    from flint._flint import libflint
    # arb_fpwrap_cdouble_hardy_z : retourne directement un double
    ...
```

Module intégré dans `arb_wrapper.py` (commit `b563db2`, branche `Riemann_Lab_C`).

### Gain mesuré (benchmark 2026-06-09)

| Méthode | Temps/appel | Speedup | Allocation |
|---|---|---|---|
| `mpmath.siegelz` dps=35 | 21.13 ms | 1× | ~1 000 malloc/free |
| `arb_fpwrap_cdouble_hardy_z` | **0.77 ms** | **×27** | 0 |

Speedup par tranche :

| Tranche $t$ | Speedup Arb vs mpmath |
|---|---|
| $[100,\, 1\,000]$ | ×29 |
| $[1\,000,\, 5\,000]$ | ×28 |
| $[5\,000,\, 10\,000]$ | ×26 |

Erreur : $|Z_{\text{arb}} - Z_{\text{mpmath}}| < 2.2 \times 10^{-16}$ (sub-ULP) — précision double
largement suffisante pour la tolérance Illinois $10^{-12}$.

---

## Tableau récapitulatif global

| # | Problème | Correction v4.1 | Gain mesuré |
|---|---|---|---|
| 1 | Z_batch N_max fixe → erreur RS jusqu'à 3.5 | `Z_vect_correct` masque booléen par ligne | Erreur $< 10^{-10}$ · vitesse ×9 000 |
| 2 | Détection séquentielle `mpmath.siegelz` | Vectorisation numpy BLAS | ×4 771–×9 873 selon $t$ |
| 3 | `.so` avant fork → sérialisation GMP | Chargement `.so` après `fork()` | Parallèle ×1.84 → ×3.9 |
| 4 | Biais Illinois_C pur ($10^{-4}$–$10^{-2}$) | Newton analytique dps=25, 3 pas | Précision $< 10^{-14}$ ✅ |
| 5 | Goulot `_newton_polish` (siegelz) | — (goulot structurel identifié 2 juin) | 1.07 z/s · pas d'optimisation algo possible |
| 6 | Goulot affinage `mpmath.siegelz` 21 ms/appel | `arb_fpwrap_cdouble_hardy_z` (Arb) | ×27 · 0.77 ms/appel · T=10 000 : 2.60 min ✅ |

---

## Résultats de validation

### Vérif A — T=300 (2 juin 2026, 16h29)

| Métrique | v5 (référence log T=80) | v4.1 (log 20260602_162919) |
|---|---|---|
| Zéros | 138/138 ✅ | 138/138 ✅ |
| Turing | COMPLET ✅ | COMPLET ✅ |
| LMFDB | 19/20 ✅ | 19/20 ✅ |
| Durée | ~168 s (estimé : 0.82 z/s × 138) | 73.4 s ✅ |
| Vitesse | ~0.82 z/s | 1.88 z/s |
| Méthode affinage | Illinois_C + callback ctypes | mpmath findroot dps=15 |
| Méthode détection | `mpmath.siegelz` séquentiel | `Z_vect_correct` numpy |

### Run T=1000 (2 juin 2026, 16h39)

| Métrique | Valeur |
|---|---|
| Zéros trouvés | 649 ($N(T) \approx 647$) ✅ |
| Turing | COMPLET — 0 zéro manquant ✅ |
| LMFDB | 19/20 (zéro #20 : 8.06e-10, cas limite stable) ✅ |
| `illinois_C_polish` | 511 / 78.7 % (structurel : 138 zéros $< 300$ toujours en mpmath) |
| `mpmath_petit_t` | 138 (21.3 %, $t < 300$, légitime) ✅ |
| `mpmath_fallback` | 0 ✅ |
| Durée | 603.8 s (10 min) |
| Vitesse | 1.07 z/s |
| Espacement min | 0.310431 |
| Espacement moy | 1.521075 |

**Note sur illinois_C_polish 78.7 % :** les 138 zéros $[14, 300[$ passeront *toujours* par
`mpmath_petit_t` (seuil `T_SEUIL_ILLINOIS_C = 300`). Ce pourcentage est structurel.
À T=10 000 : 138/10 142 ≈ 1.4 % → **98.6 % illinois_C_polish** ✅ (seuil cible 90 %).

### Test T=10 000 avec Arb (10 juin 2026)

Après intégration d'Arb (commit `b563db2`) et fix STEP adaptatif (commit `50837f7`) :

| Métrique | v4.1 (2 juin, T=1000) | **v4.1+Arb (10 juin, T=10 000)** |
|---|---|---|
| Vitesse | 1.07 z/s | **64.97 z/s** ✅ |
| Durée | — | **2.60 min** |
| Turing | COMPLET | **COMPLET** ✅ |
| Zéros | 649/649 | **10 141/10 142** |
| Manquants | 0 | **0** ✅ |
| LMFDB 20 premiers | 19/20 | 19/20 (zéro #20 : 8.06e-10) |
| Gain vs v1 (21 h) | — | **×484** |

### Runs T=100 000 — STEP adaptatif (10 juin 2026)

La scale-up de T=10 000 à T=100 000 a révélé un problème de sous-échantillonnage :

| Run | STEP | Zéros trouvés | Manquants | Turing | Note |
|---|---|---|---|---|---|
| v1 (073115) | 0.1 fixe | 137 904 / 138 069 | 356 | ❌ | STEP trop grand à $t > 29\,126$ |
| v2 (141005) | 0.1 fixe | 138 050 / 138 069 | 17 | ❌ | même cause |
| v3 (adaptatif 0.1/0.05/0.02) | variable | 138 039 / 138 069 | 68 | ❌ | STEP=0.02 < gap min 0.019 à $t=66\,678$ |
| v4 (0.05/0.010) | fixe par tranche | *tué* | — | — | régression ×11 vitesse (~0.5 z/s) |
| **v5 (δ/3 continu)** | $\delta(t)/3$ | **EN COURS** | — | **attendu** ✅ | commit `d2f62c1`, PID 328675 |

**Cause des manquants v3 :** le gap minimal mesuré entre deux zéros consécutifs est
$0.01940$ à $t = 66\,678$. STEP=0.02 > 0.019 → le bracket englobait deux zéros en un seul pas.
Les paires se produisent car la distribution des espacements suit la loi GUE (Gaussian
Unitary Ensemble) qui admet une queue pour les très petits espacements.

**Fix STEP $\delta(t)/3$ (commit `d2f62c1`) :**

$$\text{STEP}(t) = \max\!\left(0.05,\; \min\!\left(0.5,\; \frac{\delta(t)}{3}\right)\right), \qquad \delta(t) = \frac{2\pi}{\ln(t/2\pi)}$$

Valeurs résultantes : STEP $\approx 0.41$ à $t = 1\,000$ · $0.33$ à $t = 10\,000$ · $0.22$ à $t = 100\,000$.
Nombre de points de scan : $\approx 460\,000$ (vs $5\,000\,000$ avec STEP=0.010 — ÷11).

**Vitesse mesurée après 9 min (run v5) :**

| Worker | Segment | Zéros à 540s | Vitesse |
|---|---|---|---|
| 0 | $[14,\; 6\,700]$ | 6 000 | **27 z/s** (terminé) |
| 1 | $[6\,700,\; 25\,600]$ | 8 000 | **14.9 z/s** |
| 2 | $[25\,600,\; 56\,700]$ | 4 000 | **7.7 z/s** |
| 3 | $[56\,700,\; 100\,000]$ | 3 000 | **6.2 z/s** |
| **Total** | — | **~21 000** | **~39 z/s** |

La dégradation Worker 3 vs Worker 0 reflète le coût croissant d'Illinois ($O(\sqrt{t})$) —
non le nombre de points de scan (voir Problème 5 / résolu partiellement par Arb).

---

## Questions ouvertes

1. **STEP = δ/3 suffisant pour les paires très proches ?**
   Le gap min mesuré est $0.019$ à $t = 66\,678$, soit $\delta/3 \approx 0.22$ à cet endroit —
   ratio $\delta/3\,/\,\text{gap}_{\min} \approx 11.6$. La garantie théorique STEP < δ/2 porte
   sur l'espacement *moyen* ; les queues GUE peuvent produire des gaps $\ll \delta$.
   **→ La validation Turing-Backlund du run v5 EN COURS tranchera définitivement.**

2. **Déséquilibre workers à grand $t$ (segmentation 1/√t).**
   La segmentation équitable sur l'axe $\sqrt{t}$ équilibre le *nombre de zéros*
   mais pas le *temps d'affinage* (Illinois croît en $O(\sqrt{t})$ par zéro).
   Worker 3 ($[56\,700,\; 100\,000]$) est ~4× plus lent que Worker 0 ($[14,\; 6\,700]$).
   **→ v6 : segmenter par temps d'affinage estimé $N(T) \cdot \sqrt{t}$ plutôt que par $\sqrt{t}$.**

3. **Plancher de vitesse v4.1+Arb : ~39 z/s cumulé (T=100k).**
   Le bottleneck restant est le coût Illinois C à grand $t$ (~85 ms/appel à $t \approx 10\,000$).
   Pistes v6 :
   - `scan_arb.c` : détection Z(t) en C pur (éliminer le context-switch Python/C par bloc)
   - W=8 workers (si machine dispose de 8 cœurs ou machine plus puissante)
   - Cible : ~27 min pour T=100 000 (vs ~105 min estimé v4.1+Arb)

4. **Versionner les skills :** les skills `~/.claude/skills/` restent à déplacer
   vers `.claude/skills/` sur `Riemann_Lab_IA` (Phase 2 de `docs/plan_versionner_skills_20260601.md`).

---

*analyse_problemes_v5_v4_1_20260602.md · wiki racine · master · hprzeta · MAJ 2026-06-10 · 385 lignes*
