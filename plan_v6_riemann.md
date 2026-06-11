# Plan v6 — scan_arb.c + W=8 workers

> **Fichier :** plan_v6_riemann.md
> **Dossier :** wiki racine
> **Branche :** master (wiki)
> **Auteur :** hprzeta · **MAJ :** 2026-06-10

---

## Objectif

T=100 000, Turing-Backlund COMPLET, durée < 20 min (vs 105 min v2b actuelle).

**Contrainte absolue :** STEP ≤ 0.010 — seule valeur garantissant 0 manquant face aux
gaps GUE ($\delta_{\min} \approx 0.019$ mesuré à $t = 66\,678$). Ne pas utiliser δ/3 (v4 : 2072 manquants).

---

## Leçon clé — STEP δ/3 insuffisant (10 juin 2026)

La formule STEP=δ(t)/3 produit STEP≈0.22 à $t=100\,000$, soit ×11 le gap minimum mesuré.
Résultat : 2 072 manquants — pire que v1 (356 avec paliers 0.1/0.05/0.02).

Distribution GUE (Montgomery-Odlyzko) : $P(\text{gap} < s \cdot \delta) \approx \frac{\pi^2}{4} s^2$ pour $s \ll 1$.
Au 1ᵉʳ percentile : gap ≈ 0.14·δ. Pour garantir 0 manquant il faut STEP < gap_min/2 ≈ 0.009.

**Conclusion :** STEP adaptatif basé sur δ seul ne fonctionne pas. L'accélération doit venir
du scan en C, pas de la réduction du nombre de points.

---

## Les 4 leviers v6

### L1 — W=8 workers (1 ligne)

```python
N_WORKERS = min(8, multiprocessing.cpu_count())
```

Gain estimé : ×1.3 (vs W=4) — RAM limitante sur 8 GB, mais 4 → 8 est faisable.
Implémentation : modifier `N_WORKERS = 4` dans `compute_zeros_v4_1.py`.

### L2 — scan_arb.c : détection Z(t) en C pur

Remplacer la boucle Python `Z_batch` numpy par un scan C entier.

```c
/* scan_arb.c */
int scan_zeros_arb(double t_min, double t_max, double step,
                   double *out_a, double *out_b,
                   double *out_fa, double *out_fb, int n_max);
```

Implémentation interne :
```c
arb_fpwrap_cdouble_hardy_z(&z, t_courant, flags);  // 0.77 ms, 0 malloc heap
if (z_prev * z_courant < 0) {
    out_a[n] = t_prev; out_b[n] = t_courant;
    out_fa[n] = z_prev; out_fb[n] = z_courant;
    n++;
}
```

Gain estimé : ×7.5 sur la phase scan (0.77 ms/appel vs Python loop overhead).
Prérequis : `libflint` accessible depuis C (déjà présent via python-flint 0.8.0).

Binding ctypes :
```python
lib_scan = ctypes.CDLL("c_modules/scan_arb.so")
lib_scan.scan_zeros_arb.restype = ctypes.c_int
lib_scan.scan_zeros_arb.argtypes = [
    ctypes.c_double, ctypes.c_double, ctypes.c_double,
    ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
    ctypes.c_int,
]
```

### L3 — Cache fa/fb (0 recalcul d'Illinois)

scan_arb.c retourne déjà `fa=Z(a)` et `fb=Z(b)` → passer directement à `illinois_refine(a,b,fa,fb,...)`.
Élimine 2 appels Arb par zéro dans l'affinage.

Gain estimé : ×1.5 sur la phase affinage.

### L4 — Segmentation par N(T) (balance parfaite)

Remplacer la segmentation 1/√t par une segmentation équilibrant $N(T_j) - N(T_{j-1})$ :

```python
def _partitionner_NT(t_min, t_max, n_workers):
    N_total = N_RV(t_max) - N_RV(t_min)
    targets = [N_RV(t_min) + k * N_total // n_workers for k in range(n_workers + 1)]
    # inverser N_RV pour trouver les T_j correspondants
    bornes = [t_min] + [_chercher_T_pour_N(targets[k]) for k in range(1, n_workers)] + [t_max]
    return bornes
```

Gain estimé : ×1.1 (workers plus synchrones, moins de temps perdu à attendre le plus lent).

---

## Estimation performance v6

| Configuration | Gain vs v2b (105 min) | Durée estimée |
|---|---|---|
| v2b (baseline) | ×1 | 105 min |
| + W=8 (L1) | ×1.3 | ~81 min |
| + scan_arb.c (L2) | ×7.5 sur scan | ~15–25 min |
| + cache fa/fb (L3) | ×1.5 sur affinage | ~12–18 min |
| + segmentation N(T) (L4) | ×1.1 | ~11–16 min |
| **v6 cible (conservateur ×3)** | — | **~35 min** |
| **v6 cible (optimiste)** | — | **~15 min** |

La phase scan représente ~60 % du temps total à T=100k. Avec scan_arb.c ×7.5, on divise
ce goulot par 7.5 → gain global ×3–5 sur le temps total.

---

## Plancher théorique

$$T_{\text{plancher}} = \frac{N(T) \cdot n_{\text{iter,Illinois}} \cdot t_{\text{Illinois,C}}}{W}
= \frac{138\,000 \times 6 \times 85\,\text{ms}}{8} \approx 8.8\,\text{min}$$

Avec Illinois_C à 85 ms/appel (mesuré) et W=8. Le plancher absolu est ~9 min.

---

## Prérequis v6

```bash
# Vérifier libflint accessible depuis C
pkg-config --libs flint           # ou chercher libflint dans le système
find /usr -name "libflint*.so" 2>/dev/null

# Compiler scan_arb.c (exemple)
gcc -O3 -march=native -fPIC -shared -o scan_arb.so scan_arb.c \
    $(pkg-config --cflags --libs flint) -lm

# Tester le binding
python -c "import ctypes; lib = ctypes.CDLL('./scan_arb.so'); print('OK')"
```

---

## Ordre d'implémentation recommandé

1. **Benchmark préalable** : chronomètre par phase sur T=5 000 (scan vs affinage)
   → confirmer que scan est bien le goulot et quantifier le gain Arb
2. **L2 — scan_arb.c** : levier principal (×7.5 estimé)
3. **L3 — cache fa/fb** : intégration facile avec L2
4. **L1 — W=8** : 1 ligne, tester la RAM
5. **L4 — segmentation N(T)** : raffinement final

---

## Validation

- Test T=10 000 v6 : Turing-Backlund COMPLET, LMFDB ≥ 19/20 < 1e-10
- Test T=100 000 v6 : Turing-Backlund COMPLET, 0 manquant
- Comparaison CSV v2b vs v6 : diff sur les 20 premiers zéros LMFDB < 1e-10

---

*plan_v6_riemann.md · wiki racine · master · hprzeta · MAJ 2026-06-10 · ~130 lignes*
