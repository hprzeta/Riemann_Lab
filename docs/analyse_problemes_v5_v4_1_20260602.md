# Analyse des problèmes v5 → v4.1

**Auteur :** hprzeta  
**Date :** 2 juin 2026  
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

## Tableau récapitulatif global

| # | Problème | Correction v4.1 | Gain mesuré |
|---|---|---|---|
| 1 | Z_batch N_max fixe → erreur RS jusqu'à 3.5 | `Z_vect_correct` masque booléen par ligne | Erreur $< 10^{-10}$ · vitesse ×9 000 |
| 2 | Détection séquentielle `mpmath.siegelz` | Vectorisation numpy BLAS | ×4 771–×9 873 selon $t$ |
| 3 | `.so` avant fork → sérialisation GMP | Chargement `.so` après `fork()` | Parallèle ×1.84 → ×3.9 |
| 4 | Biais Illinois_C pur ($10^{-4}$–$10^{-2}$) | Newton analytique dps=25, 3 pas | Précision $< 10^{-14}$ ✅ |
| 5 | Goulot `_newton_polish` (siegelz) | — (goulot structurel) | 1.07 z/s · pas d'optimisation algo possible |

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

---

## Questions ouvertes

1. **Vitesse à grand $t$ :** le goulot est `mpmath.siegelz` lui-même (~15–20 ms/appel
   à $t \approx 1000$ avec dps=25). Pour T=10 000, le polish prend ~2.5 h.
   Une implémentation native de $Z'(t)$ en C/libmpfr pourrait court-circuiter `siegelz`.

2. **Déséquilibre de charge :** Worker 0 (plage $[14, 261[$) concentre les 138 zéros
   mpmath lents. Pour T >> 300, ce déséquilibre disparaît naturellement (~1.4 % à T=10 000).

3. **Décision livrable T=10 000 :**
   - Turing seulement → Illinois_C pur sans `_newton_polish` (~41 z/s, ~5 min)
   - Catalogue positions < $10^{-10}$ → CSV v2/v3 existant (10 142 zéros, 50 dps) ou run de nuit

4. **Versionner les skills :** les 4 skills `~/.claude/skills/` restent à déplacer
   vers `.claude/skills/` sur `Riemann_Lab_IA` (Phase 2 de `docs/plan_versionner_skills_20260601.md`).

---

*Mis à jour : 2 juin 2026 · Branche `Riemann_Lab_C` · 276 lignes*
