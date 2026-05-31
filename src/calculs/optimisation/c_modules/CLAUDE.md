# src/calculs/optimisation/c_modules/CLAUDE.md — module C Illinois/libmpfr
> Instructions Claude Code — module C de la Phase C.
> Règles **stables** ; aucun état de session ici (→ `Handoff.md`).
> Mis à jour : 31 mai 2026

---

## Ce dossier

Module C de la **Phase C** : `illinois_mpfr` en C/libmpfr, cible ×5–10 vs mpmath Python.
Formules mathématiques canoniques : `~/projet_zeta/CLAUDE.md` (les implémentations C
ci-dessous en sont la transcription `double`).

---

## Fichiers (ordre de création)

```
1. illinois_mpfr.h   ← header (signatures, constantes)
2. z_function.h      ← header Z(t), theta(t)
3. z_function.c      ← θ(t) Stirling + Z(t) RS en C (double)
4. illinois_mpfr.c   ← Illinois en libmpfr (PREC = 170 bits)
5. Makefile          ← cible illinois_mpfr.so
6. test_illinois.py  ← validation ctypes sur 10 zéros LMFDB
```

---

## Constantes immuables — NE PAS MODIFIER

```c
#define PREC    170      /* 170 bits ≈ 51 décimales — cohérent avec 50 dps mpmath */
#define MAX_ITER 100     /* max itérations Illinois — suffisant pour tol=1e-12 */
#define TOL_DEFAULT 1e-12
```

---

## Règles de code C — OBLIGATOIRES

### Mémoire libmpfr
```c
/* ✅ toujours init + clear */
mpfr_t x; mpfr_init2(x, PREC); /* ... */ mpfr_clear(x);
/* ❌ init sans clear = fuite mémoire */
```
Pour les groupes : `mpfr_inits2(PREC, a, b, c, NULL)` / `mpfr_clears(a, b, c, NULL)`.

### Arrondi
Toujours `MPFR_RNDN` (au plus proche). Jamais `MPFR_RNDZ`/`MPFR_RNDU` sauf justification.

### Signatures IMMUABLES (l'interface ctypes en dépend)
```c
double illinois_mpfr(double a_d, double b_d, double tol);  /* exportée */
void   Z_mpfr(mpfr_t result, mpfr_t t);                    /* interne */
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
**Note :** la tabulation Makefile est un **TAB réel** (0x09), pas des espaces.

---

## Implémentations C de référence

```c
/* θ(t) asymptotique Stirling — valide t >= 20 */
static double theta_double(double t) {
    double pi = acos(-1.0);
    double lt = log(t / (2.0 * pi));
    return (t / 2.0) * lt - t / 2.0 - pi / 8.0
           + 1.0 / (48.0 * t) + 7.0 / (5760.0 * t * t * t);
}

/* Z(t) Riemann-Siegel en double — détection de signe */
double Z_double(double t) {
    double pi = acos(-1.0);
    long   N  = (long) sqrt(t / (2.0 * pi));
    double th = theta_double(t), sum = 0.0;
    for (long n = 1; n <= N; n++)
        sum += cos(th - t * log((double)n)) / sqrt((double)n);
    return 2.0 * sum;
}
```

---

## Validation (test_illinois.py)

10 premiers zéros, tolérance < 1e-10 vs LMFDB :
```python
LMFDB_10 = [14.134725141734693, 21.022039638771555, 25.010857580145688,
            30.424876125859513, 32.935061587739189, 37.586178158825671,
            40.918719012147495, 43.327073280914999, 48.005150881167159,
            49.773832477672302]
```

---

## Benchmarks attendus

```
illinois_mpfr C    : X ms/zéro (sur 100 zéros)
illinois mpmath Py : Y ms/zéro
Gain attendu       : Y/X ≥ 5   (objectif ×5–10)
```
Documenter dans `benchmark_phase_c.md` à la racine du dossier.

---
*Dernière mise à jour : 31 mai 2026 — ~115 lignes*
