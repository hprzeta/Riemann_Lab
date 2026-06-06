# CLAUDE.md — c_modules/
> Instructions pour Claude Code — module C Illinois/libmpfr
> Mis à jour : 23 mai 2026

---

## Ce dossier

Contient le module C de la **Phase C** du projet Riemann_Lab.
Objectif : implémenter `illinois_mpfr` en C avec libmpfr pour ×5–10 vs mpmath Python.

---

## Fichiers attendus (à créer dans cet ordre)

```
1. illinois_mpfr.h      ← header (signatures, constantes)
2. z_function.h         ← header Z(t), theta(t)
3. z_function.c         ← θ(t) Stirling + Z(t) RS en C (double précision)
4. illinois_mpfr.c      ← Illinois en libmpfr (PREC = 170 bits)
5. Makefile             ← cible illinois_mpfr.so
6. test_illinois.py     ← validation ctypes sur 10 zéros LMFDB
```

---

## Constantes immuables — NE PAS MODIFIER

```c
#define PREC    170      /* 170 bits = ~51 décimales — cohérent avec 50 dps mpmath */
#define MAX_ITER 100     /* max itérations Illinois — suffisant pour tol=1e-12 */
#define TOL_DEFAULT 1e-12
```

---

## Règles de code C — OBLIGATOIRES

### Mémoire libmpfr
```c
/* ✅ CORRECT — toujours init + clear */
mpfr_t x;
mpfr_init2(x, PREC);
/* ... utilisation ... */
mpfr_clear(x);

/* ❌ INTERDIT — init sans clear = fuite mémoire */
mpfr_t x;
mpfr_init2(x, PREC);
return result;   /* x non libéré ! */
```

**Règle :** utiliser `mpfr_inits2(PREC, a, b, c, NULL)` et `mpfr_clears(a, b, c, NULL)` pour les groupes.

### Arrondi
Toujours `MPFR_RNDN` (arrondi au plus proche). Jamais `MPFR_RNDZ` ni `MPFR_RNDU` sauf justification explicite.

### Signature de `illinois_mpfr`
```c
/* Signature IMMUABLE — l'interface ctypes Python en dépend */
double illinois_mpfr(double a_d, double b_d, double tol);
```

### Signature de `Z_mpfr`
```c
/* Interne — appelée uniquement depuis illinois_mpfr */
void Z_mpfr(mpfr_t result, mpfr_t t);
```

---

## Makefile — cible obligatoire

```makefile
CC     = gcc
CFLAGS = -O3 -march=native -fPIC -Wall -Wextra
LIBS   = -lmpfr -lgmp -lm

all: illinois_mpfr.so

illinois_mpfr.so: illinois_mpfr.c z_function.c
	$(CC) $(CFLAGS) -shared -o $@ $^ $(LIBS)

test: illinois_mpfr.so
	python3 test_illinois.py

clean:
	rm -f *.so *.o
```

**Note :** la tabulation dans Makefile est un **TAB réel** (0x09), pas des espaces.

---

## Formule θ(t) à implémenter en C (double)

```c
/* theta(t) asymptotique de Stirling — valide pour t >= 20 */
static double theta_double(double t) {
    double pi = acos(-1.0);
    double lt = log(t / (2.0 * pi));
    return (t / 2.0) * lt - t / 2.0 - pi / 8.0
           + 1.0 / (48.0 * t)
           + 7.0 / (5760.0 * t * t * t);
}
```

## Formule Z(t) à implémenter en C (double)

```c
/* Z(t) Riemann-Siegel en double — pour la détection de signe */
double Z_double(double t) {
    double pi   = acos(-1.0);
    long   N    = (long) sqrt(t / (2.0 * pi));
    double th   = theta_double(t);
    double sum  = 0.0;
    for (long n = 1; n <= N; n++) {
        sum += cos(th - t * log((double)n)) / sqrt((double)n);
    }
    return 2.0 * sum;
}
```

---

## Test de validation (test_illinois.py)

Le test doit vérifier les 10 premiers zéros avec tolérance `< 1e-10` vs LMFDB :

```python
LMFDB_10 = [
    14.134725141734693, 21.022039638771555, 25.010857580145688,
    30.424876125859513, 32.935061587739189, 37.586178158825671,
    40.918719012147495, 43.327073280914999, 48.005150881167159,
    49.773832477672302
]
```

---

## Benchmarks attendus

Après compilation et tests :
```
illinois_mpfr C    : mesurer sur 100 zéros → X ms/zéro
illinois mpmath Py : mesurer sur 100 zéros → Y ms/zéro
Gain attendu       : Y/X ≥ 5 (objectif ×5–10)
```

Documenter les résultats dans `benchmark_phase_c.md` à la racine du dossier.

---
*Dernière mise à jour : 23 mai 2026 — 97 lignes*
