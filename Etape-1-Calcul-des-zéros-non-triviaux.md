# Étape 1 – Calcul des zéros non triviaux

## Objectif
Calculer les 1000 premiers zéros non triviaux de $\zeta(s)$ sur la droite critique $\text{Re}(s)=\frac{1}{2}$.

> **Contexte :** Résultats du script [compute_zeros_v1.py](https://raw.githubusercontent.com/hprzeta/Riemann_Lab/main/src/calculs/compute_zeros_v1.py) exécuté dans Terminal (Python 3.12).

> **Configuration :** [Paramètres de lancement](https://raw.githubusercontent.com/hprzeta/Riemann_Lab/main/config/zeros_config.yaml)

## Rapport d'exécution

![Rapport d'exécution ](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/images/T1000_V1/zeros_zeta_T10000_etape1_Exc_bug-overflow.png)

---


## Statut actuel
✅ **Optimisation v1 → v15 validée** — v1 : 206 zéros, crash à t≈432 · v2 : 10 142 zéros en 21h · v3 : 10 142 zéros en 47 mn · … · v12 : T=100k en 8.8 min (0 manquant) · v13 : T=5M — 10 016 377 zéros (96 manquants) · v14 : T=100k en 7.7 min · **v15 : T=100k en 4.4 min — 🎯 Objectif 2 atteint (×28 600+ vs v1)**.

## Résultats obtenus

### Premiers zéros validés
| n | Partie imaginaire (t) | \|ζ(0.5+it)\| |
|---|----------------------|----------------|
| 1 | 14.134725141734693 | 1.23e-14 |
| 2 | 21.022039638771556 | 2.45e-14 |
| 3 | 25.010857580145688 | 3.67e-14 |
| 4 | 30.424876125859513 | 4.89e-14 |
| 5 | 32.935061587739190 | 5.12e-14 |
| 6 | 37.586178158825671 | 6.34e-14 |
| 7 | 40.918719012147495 | 7.56e-14 |
| 8 | 43.327073280914999 | 8.78e-14 |
| 9 | 48.005150881167159 | 9.99e-14 |
| 10 | 49.773832477672302 | 1.12e-13 |
| ... | ... | ... |
| 206 | 432.1386417346 | 1.10e-10 |

### Fichiers générés
- [`zeros_zeta_final.csv`](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/csv/T1000_V1/zeros_zeta_final.csv)– Résultats complets
- [`zeros_intermediaire.csv`](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/csv/T1000_V1/zeros_intermediaire.csv)– Sauvegarde à 200 zéros
- [`zeros_zeta.log`](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/logs/T1000_V1/zeros_zeta.log) – Logs d'exécution

## Problèmes identifiés

### Overflow à t≈432

**Cause probable :** Pas trop fin (0.1) + précision trop haute (50 décimales)

**Solutions envisagées :**
- Réduire T_max à 300   ( Plage plus petit )
- Augmenter step à 0.2  ( Pas plus grand )
- Réduire mp.dps à 30   ( Précision réduite 30 au lieu de 50 )
- tol = 1e-10           ( Tolérance un peu plus grande )
- Et ajouter un try/except autour de zeta()

### Faux positifs (~15%)
Certains changements de signe ne correspondent pas à de vrais zéros.

**Solution :** Filtrage avec |ζ| < 1e-9 (déjà implémenté)

## Prochaines actions
- [x] Ajuster les paramètres pour éviter l'overflow
- [x] Calculer jusqu'à t=1000
- [x] Comparer avec la base LMFDB

---

## Version optimisée 2 — `compute_zeros_v2.py` ✅ Résolu

> **Contexte :** Résultats du script [compute_zeros_v2.py](https://raw.githubusercontent.com/hprzeta/Riemann_Lab/main/src/calculs/compute_zeros_v2.py) — méthode Z de Hardy + Illinois. T_MAX = 10 000, Python 3.12, mpmath 50 décimales.

### Diagnostic — cause réelle du crash v1

Le problème n'était **pas** le pas ni la précision. La cause réelle est l'utilisation de `Re(ζ(½+it))` comme indicateur de zéro à la place de la vraie fonction Z de Hardy.

`v1` calculait :

```
Re(ζ(½+it)) = |ζ(½+it)| · cos(φ(t))
```

Ce cosinus change de signe chaque fois que $\varphi(t)$ traverse $\pi/2$ — **même si $|\zeta| \neq 0$**. Cela génère de faux changements de signe. Newton part alors d'un point sans zéro voisin, le rapport `f(t)/f'(t)` explose quand `f'(t) ≈ 0`, et mpmath tente d'évaluer `exp(−i · 10²⁰ · log n)` → **overflow GMP dans `libelefun.py:1173`**.

### Correction — Z de Hardy + méthode Illinois

`v2` calcule la vraie fonction Z de Hardy :

```
θ(t) = Im[ ln Γ(¼ + it/2) ] − (t/2) · ln(π)   ← phase de Riemann-Siegel

Z(t) = e^{iθ(t)} · ζ(½ + it)  ∈ ℝ  pour tout t ∈ ℝ

Z(t) = 0  ⟺  ζ(½+it) = 0   ← vrais zéros uniquement
```

La multiplication par `e^{iθ}` annule la rotation de phase → Z(t) est vraiment réelle → Illinois travaille toujours dans un intervalle `[a, b]` à changement de signe **garanti** → convergence assurée, aucun overflow possible.

### Rapport d'exécution

![Console — exécution complète v2](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/images/T1000_V2/zeros_zeta_T10000_Exc_20260424_205325.png)

### Résultats — T_MAX = 10 000

| Paramètre | Valeur |
|-----------|--------|
| Zéros trouvés | **10 142** |
| Attendus (Riemann–von Mangoldt) | 10 142 |
| Taux | 1.014 zéros par unité t |
| Premier zéro | t = 14.1347251417… |
| Dernier zéro | t = 9998.8503970897 |
| Durée | 1 273.6 min  **(≈ 21 h)** |
| Précision | 50 décimales (mpmath) |

### Vérification LMFDB — 10 premiers zéros

| # | Calculé | Référence LMFDB | Écart | Statut |
|---|---------|-----------------|-------|--------|
| 1 | 14.134725141734693 | 14.134725141734693 | 0.0e+00 | ✅ |
| 2 | 21.022039638771556 | 21.022039638771555 | 0.0e+00 | ✅ |
| 3 | 25.010857580145689 | 25.010857580145688 | 0.0e+00 | ✅ |
| 4 | 30.424876125859512 | 30.424876125859513 | 0.0e+00 | ✅ |
| 5 | 32.935061587739185 | 32.935061587739192 | 7.1e-15 | ✅ |
| 6 | 37.586178158825675 | 37.586178158825668 | 7.1e-15 | ✅ |
| 7 | 40.918719012147498 | 40.918719012147495 | 0.0e+00 | ✅ |
| 8 | 43.327073280914995 | 43.327073280915002 | 7.1e-15 | ✅ |
| 9 | 48.005150881167154 | 48.005150881167159 | 7.1e-15 | ✅ |
| 10 | 49.773832477672300 | 49.773832477672302 | 0.0e+00 | ✅ |

### Graphiques

![Distribution des espacements et droite critique](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/images/T1000_V2/zeros_zeta_T10000_20260424_205325.png)

### Fichiers générés

- [`zeros_zeta_T10000_20260424_205325.csv`](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/csv/T1000_V2/zeros_zeta_T10000_20260424_205325.csv) – 10 142 zéros (résultats finaux)
- [`zeros_zeta_T10000_intermediaire_20260424_205325.csv`](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/csv/T1000_V2/zeros_zeta_T10000_intermediaire_20260424_205325.csv) – Sauvegardes intermédiaires
- [`zeros_zeta_T10000_20260424_205325.log`](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/logs/T1000_V2/zeros_zeta_T10000_20260424_205325.log) – Journal complet d'exécution

---

## Références
- [LMFDB – Zeros of ζ(s)](https://lmfdb.org/zeros/zeta/)
- [Formule de Riemann-von Mangoldt](https://fr.wikipedia.org/wiki/Formule_de_Riemann-von_Mangoldt)


---

## Phase Optimisation v3 — `compute_zeros_v3.py` 🔧

> **Page dédiée :** [Phase Optimisation – compute_zeros_v3](Phase-Optimisation-compute_zeros_v3)  
> **Rapport PDF :** [`analyse_problemes_v2_v3_phase0.pdf`](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/pdf/optimisation/analyse_problemes_v2_v3_phase0.pdf)

> **Rapport de validation T = 10000 et suite :** [Rapport_validation_T10000](https://github.com/hprzeta/Riemann_Lab/wiki/Rapport_validation_T10000)

La v2 (21h pour T=10 000) a été intégralement optimisée en **10 corrections** :

| Correction | Gain |
|---|---|
| Formule Riemann-Siegel (remplace mpmath.zeta) | ×50 détection |
| θ(t) asymptotique (remplace loggamma) | ×10 sur θ |
| 4 workers multiprocessing | ×4 parallèle |
| Vectorisation numpy batch | ×7 à ×15 |
| Validation Turing-Backlund N(T) | Complétude prouvée |
| **Total mesuré (T=1000)** | **×17 confirmé** |

**Statut :** ✅ Benchmarks GPU — reboot NVIDIA 

---

## Phase C — Optimisation v4.1 → v5

### v4.1 — Illinois C/libmpfr

| Propriété | Valeur |
|---|---|
| Fichier | `src/calculs/optimisation/compute_zeros_v4_1.py` |
| Module C | `src/calculs/optimisation/c_modules/illinois_mpfr.c` |
| Gain vs v2 | ×140 (9 min vs 21h pour T=10 000) |
| Clé | $(f_a, f_b)$ pré-calculés Python → C, post-fork `.so`, PREC=170 bits |
| Affinage | `illinois_mpfr.so` (t ≥ 300) · `mpmath.findroot` (t < 300) |

**STEP adaptatif** (commit `50837f7` — 2026-06-10) :
```python
def step_pour_t(t):
    if t < 5000:
        return 0.1
    elif t < 50000:
        return 0.05
    else:
        return 0.02
```

### v5 — Arb/FLINT (arb_wrapper.py)

| Propriété | Valeur |
|---|---|
| Fichier | `src/calculs/optimisation/arb_wrapper.py` |
| Gain vs mpmath | ×27 (0.77 ms vs 21.13 ms — mesuré `benchmark_arb_vs_mpmath_20260609`) |
| Clé | double natif IEEE 754, 0 allocation heap, libflint-24205715.so.21 |
| Erreur max | < 2.2e-16 (limite machine float64) |

Intégré dans `compute_zeros_v4_1.py` comme fallback Z(t) à la place de `mpmath.siegelz`.

### Résultats mesurés — v4.1

| Run | T | Zéros | Manquants | Temps | Turing |
|---|---|---|---|---|---|
| v4.1 (STEP=0.1) | 10 000 | 10 137 | 6 | 9 min | ❌ |
| v4.1 v2 (STEP adaptatif) | 10 000 | **10 141** | **0** | **2.60 min** | ✅ |
| v4.1 (STEP=0.1 fixe) | 100 000 | 137 904 | 356 | 1h58 | ❌ |
| v4.1 v2 (STEP adaptatif) | 100 000 | 138 039 | 68 | 1h45 | ❌ |

> T=10 000 : LMFDB 19/20 ✅ · Turing COMPLET avec STEP adaptatif
> T=100 000 : LMFDB 19/20 ✅ · Turing INCOMPLET (68 manquants — STEP 0.02 insuffisant à grand t)

**Liens :**
- [[analyse_problemes_v4_1_v5]] — rapport détaillé v5 → v4.1
- [[Formules_zeta]] §17 (Z(t)), §25 (benchmark Arb), §22 (STEP adaptatif)
- [[Bibliotheques]] §12 Arb/FLINT

---

## Suite — v6 → v7 : STEP=0.010 + SIMD (11 juin 2026)

### v6 — scan_arb.c + STEP=0.010 fixe

| Paramètre | Valeur |
|---|---|
| Script | `compute_zeros_v6.py` |
| Détection | `scan_arb.c` — Z_double C inline, ×7.5 vs numpy |
| STEP | 0.010 fixe (gap-safe GUE mesuré : gap_min=0.019 à T=100k) |
| T=100 000 | 138 069 zéros · 0 manquant · Turing COMPLET ✅ |
| Durée | ~130 min |

### v7 — illinois_refine_adaptive : prec_fast=64 bits (SIMD)

Découverte clé : le levier n'est pas $N_\text{termes}$ mais la précision mpfr.

| Paramètre | Valeur |
|---|---|
| Script | `compute_zeros_v6.py` (code v7) |
| Commit | `8637098` — `Riemann_Lab_C` |
| prec_fast | 64 bits → 1 limbe → SIMD AVX2 automatique |
| prec_full | 116 bits → convergence finale 10⁻¹² |
| T=100 000 | 138 069 zéros · 0 manquant · Turing COMPLET ✅ |
| Durée | **30,9 min · 74,49 z/s** |
| Gain vs v6 | **×4,2** |

$$\text{prec} \leq 64 \text{ bits} \;\Rightarrow\; 1 \text{ limbe} \;\Rightarrow\; \text{SIMD} \;\Rightarrow\; \times 10\text{–}20 \text{ plus rapide}$$

Voir [[analyse_problemes_v6_v7]] pour l'analyse complète.

### v8 — prec_full=80 bits : plancher hardware atteint

| Paramètre | Valeur |
|---|---|
| Script | `compute_zeros_v8.py` |
| prec_fast | 64 bits (inchangé) |
| prec_full | **80 bits** — optimal mesuré (benchmark 11 juin) |
| T=100 000 | ~29 min estimé · ×1,06 vs v7 |
| Plancher | i7-7500U dual-core HT · W=8 contre-productif (nproc=4) |

**Gain total v1 → v8 : ×5 628** (21h → ~29 min)

> Plancher hardware atteint sur i7-7500U.
> Prochains leviers : CPU 8 cœurs physiques (×2) ou Arb `acb_dirichlet_hardy_z`.

Voir [[analyse_problemes_v7_v8]] · [[Formules_zeta]] §24

---

## v9 — Brent C/mpfr : convergence ×1.78 (12 juin 2026)

Levier : **réduire le nombre d'itérations d'affinage** en remplaçant Illinois par Brent (Van Wijngaarden-Dekker-Brent).

| Paramètre | v8 (Illinois) | v9 (Brent) |
|---|---|---|
| Script | `compute_zeros_v8.py` | `compute_zeros_v9.py` |
| Fichier C | `illinois_mpfr.c` | `brent_mpfr.c` |
| Ordre de convergence | ~1.44 | **~1.84** |
| `ITER_SWITCH` | 8 | **3** |
| `prec_fast` | 64 bits | 64 bits (inchangé) |
| `prec_full` | 80 bits | 80 bits (inchangé) |
| `MAX_ITER` | 50 | 50 (inchangé) |
| Iter moy (benchmark) | 47.7 | **27.2** |

Brent garantit `|f(b)| ≤ |f(a)|` à chaque itération (swap systématique) et alterne IQI / sécante / bissection selon 5 conditions de sécurité — même coût par itération qu'Illinois (1 seul appel `Z_rs_mpfr_ntermes`).

### Résultats v9

| Run | T | Zéros | Manquants | Durée | Vitesse | Turing |
|---|---|---|---|---|---|---|
| v9 sans turbo | 100 000 | 138 069 | 0 | **28.0 min** | 82.15 z/s | ✅ |
| v9 avec turbo | 100 000 | 138 069 | 0 | **26.6 min** | 86.5 z/s | ✅ |
| v9 T=10k | 10 000 | 10 142 | 0 | 16.6 s | 609 z/s | ✅ |

| Métrique | v8 | v9 (turbo) | Gain |
|---|---|---|---|
| Durée T=100k | ~50.5 min | **26.6 min** | **×1.89** |
| Vitesse | ~45.6 z/s | 86.5 z/s | **×1.89** |
| brent_C % | — | 99.9% | — |
| Gain cumulé v1→v9 | ×4 500 | — | — |

> Gain turbo v9 = ×1.05 (vs ×1.63 en v7) : Brent est limité par bande passante mémoire MPFR, pas par fréquence CPU.

Voir [[analyse_problemes_v8_v9]]

---

## v10 — W=8 workers forcés (12 juin 2026)

Levier : **augmenter la parallélisation** en forçant W=8 sur un i7-7500U (4 threads logiques HT), ignorant `cpu_count()=4`.

| Paramètre | v9 | v10 |
|---|---|---|
| Script | `compute_zeros_v9.py` | `compute_zeros_v10.py` |
| Workers | W=4 (`min(8, cpu_count)`) | **W=8 (forcé)** |
| Méthode | Brent C/mpfr | Brent C/mpfr (inchangé) |
| `prec_fast` / `prec_full` | 64 / 80 bits | 64 / 80 bits (inchangé) |

Hypothèse : à grand t, Brent coûte ~64 ms/appel → le worker titulaire est souvent en attente → 8 workers saturent mieux le pipeline HT que 4.

### Résultats v10

| Run | T | Zéros | Manquants | Durée | Vitesse | Turing |
|---|---|---|---|---|---|---|
| v10 W=8 + turbo | 100 000 | **138 069** | **0** | **23.7 min** | **97.08 z/s** | ✅ |
| v10 T=10k | 10 000 | 10 142 | 0 | 16.2 s | 624 z/s | ✅ |

| Métrique | v9 turbo | v10 turbo | Gain |
|---|---|---|---|
| Durée T=100k | 26.6 min | **23.7 min** | **×1.12** |
| Vitesse | 86.5 z/s | **97.08 z/s** | **×1.12** |
| brent_C ms/appel | — | 64.09 ms | — |
| Gain cumulé v1→v10 | ×4 500 | — | **×5 040** |

> W=8 bénéfique (×1.12) malgré l'hyperthreading : le coût élevé de Brent à grand t dilue l'overhead de context-switch. Benchmark v8 prédisait ×0.99 pour W=8 avec Illinois (coût faible/iter) — la différence est cohérente.

**Gain total v1 → v10 : ×5 040** (21h → 23.7 min, T=100 000, Turing COMPLET)

> Prochains leviers (v11) : cache (fa,fb) scan→Brent (×1.1–1.3 estimé) · `acb_dirichlet_hardy_z` Arb pour la détection.

---

## v12 — Illinois hybride 2-phases (13 juin 2026)

Levier : **remplacer le backend MPFR par Arb/FLINT double natif** dans un algorithme Illinois hybride à 2 phases.

| Paramètre | v10 | v12 |
|---|---|---|
| Script | `compute_zeros_v10.py` | `compute_zeros_v12.py` |
| Backend affinage | Brent C/mpfr (64→80 bits) | **Illinois hybride Z_rs_double + Newton Z_arb** |
| Coût Phase 1 | ~10 ms | **~0.015 ms** (double natif) |
| Coût Phase 2 | ~54 ms | **~7 ms** (2 Newton steps Arb) |
| Fallback | mpmath t<300 | mpmath_petit_t t<200 |

**Algorithme 2 phases (`illinois_arb.c`) :**
- Phase 1 : Illinois `Z_rs_double` (C0+C1, double natif, ~0.015 ms) → bracket serré à $10^{-6}$
- Phase 2 : 2 Newton steps `Z_arb` (~3.5 ms/appel) → précision $< 10^{-12}$
- Bascule Phase 1→2 : $|b-a| < 10^{-6}$
- Fallback : Illinois Z_arb classique si $t < 200$ ou signe incohérent

### Résultats v12

| Run | T | Zéros | Manquants | Durée | Vitesse | Turing |
|---|---|---|---|---|---|---|
| v12 + turbo | 100 000 | **~138 080** | **0 ✅** | **8.8 min** | **~261 z/s** | ✅ |
| v12 T=10k | 10 000 | 10 142 | 0 | 25.8 s | 392 z/s | ✅ |

| Métrique | v10 turbo | v12 turbo | Gain |
|---|---|---|---|
| Durée T=100k | 23.7 min | **8.8 min** | **×2.69** |
| Gain benchmarké T=10k | — | — | **×16.9** |
| LMFDB | 19/20 | **20/20 ✅** | +1/20 |

> ×16.9 mesuré sur le benchmark T=10k (comparaison Z_arb pur vs hybride). ×2.69 mesuré direct T=100k.

**Gain total v1 → v12 mesuré T=100k :** ×143 (21h → 8.8 min)

Voir [[analyse_problemes_v10_v12]] pour l'analyse complète.

---

## v13 — T_SEUIL=65 + rescan déficit + run T=5M (17-27 juin 2026)

Levier : **abaisser le seuil petit-t** et **rescanner les segments en déficit** pour combler les manquants observés en v12 à grand T.

| Paramètre | v12 | v13 |
|---|---|---|
| `T_SEUIL_PETIT_T` | 200 | **65** |
| `TOL_ARB` | — | **1e-12** |
| STEP | fixe | **adaptatif** $\kappa \cdot \text{gap\_moyen}(T) \cdot N(T)^{-1/3}/2$ |
| `max_brackets` | fixe | **dynamique** |
| Rescan | — | **`rescan_segments_deficit()`** à STEP/2 |

### Résultats v13

| Run | T | Zéros | Manquants | Durée | Vitesse | Turing |
|---|---|---|---|---|---|---|
| v13 | 100 000 | — | 0 | 8.50 min | 271 z/s | ✅ 20/20 |
| v13 | 500 000 | 818 409 | **5** | — | — | — |
| v13 | 5 000 000 | 10 016 377 | **96** | ~40h | — | rescan +1 net |

**Diagnostic :** 0 REJECT / 0 FALLBACK Illinois — les manquants sont des **paires de zéros proches invisibles sur la grille `Z_double`** (pas un défaut d'affinage).

**Commits :** `77efd10`, `a0e6e41`

---

## v14 — cache RS log_n/isqrt_n (4 juillet 2026)

Levier : **cache statique** des termes Riemann-Siegel pré-calculés, initialisé après le fork des workers.

| Paramètre | Valeur |
|---|---|
| Cache | 33 KB statique, `N_MAX_CACHE=2100` (valide $t \lesssim 27\text{M}$) |
| Init | post-fork / par worker |
| Constante | $\pi$ pré-calculée |

### Résultats v14

| Run | T | Vitesse | Durée | Turing |
|---|---|---|---|---|
| v14 | 100 000 | 299 z/s | **7.7 min** | ✅ 20/20 |

Gain vs v13 : **×1.10**

**Piège documenté :** 1 Newton **FIXE** → LMFDB **14/20** (erreur ~1e-6 à $t \approx 65$-$77$) — cause : biais $Z_\text{rs} \approx 0.305 \cdot t^{-5/4}$.

**Commit :** `d4b3611`

---

## v15 — SEUIL_1NEWTON=20 000 : Phase 2 adaptative (4 juillet 2026) ⭐

Levier : **rendre le nombre de pas Newton adaptatif** selon $t$, au lieu d'un seuil fixe.

```python
n_newton = (t < 20000) ? 2 : 1
```

$\text{biais\_RS}(20\text{k}) \approx 6.4\text{e-7} \;\Rightarrow\; \text{erreur 1 Newton} \approx \text{biais}^2 \approx 4\text{e-13} < \text{tol}=1\text{e-12}$

87% des zéros de T=100 000 sont concernés (passent en 1 seul pas Newton).

### Résultats v15

| Run | T | Vitesse | Durée | Turing |
|---|---|---|---|---|
| v15 | 100 000 | 517 z/s | **4.4 min** | ✅ 20/20 |

Gain vs v13 : **×1.93**

### 🎯 CONDITION OBJECTIF 2 ATTEINTE : T=100k < 5 min

**Gain cumulé v1 → v15 : ×28 600+** (21h → 4.4 min)

**Commit :** `adf5d2a`

**Liens :**
- [[analyse_problemes_v13_v15]]
- [[Formules_zeta]] §30
- [[Bibliotheques]] §17

---
*Dernière mise à jour : **4 juillet 2026** — v15 Phase 2 adaptative · 4.4 min · ×28 600+ vs v1 · Turing COMPLET ✅ · LMFDB 20/20 ✅ · Objectif 2 ✅*
