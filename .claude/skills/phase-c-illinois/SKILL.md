---
name: phase-c-illinois
description: >
  Skill pour la Phase C du projet Riemann_Lab — portage de l'affinage Illinois
  en C avec libmpfr/libmpc pour ×5–10 sur le goulot d'étranglement actuel.
  Se déclenche sur : "Phase C", "libmpfr", "Illinois en C", "affinage C",
  "python-flint", "arb", "extension Python C", "ctypes", "cffi",
  "Odlyzko-Schönhage", "module C", "branche Riemann_Lab_C",
  "accélération Illinois", "mpfr_t", "mpfr_set_d", "mpfr_cos".
version: 0.2.0
date: 2026-05-31
---

# Phase C — Illinois en C / libmpfr

> Skill lié : `riemann-lab` (contexte général, KaTeX, Python, wiki).
> Formules canoniques : `riemann-lab/references/formules_zeta.md`.
> État courant du projet : `Riemann_Lab.wiki/Handoff.md` (ne pas dupliquer ici).

## Contexte

Le profilage montre que l'affinage Illinois (méthode de la sécante modifiée, 50 dps via
mpmath) représente **80–90 % du temps total**. La GPU n'accélère que la détection Z(t)
(10–20 %).

**Objectif de la Phase C :** porter Illinois en C avec libmpfr pour ×5–10 sur l'affinage.

```
Branche GitHub : Riemann_Lab_C
Dossier local  : ~/projet_zeta/src/calculs/optimisation/c_modules/
```

## Méthode Illinois — rappel mathématique

Variante de la sécante pour trouver les zéros de Z(t), sans la stagnation de la sécante pure :

```
Étant donné a, b tels que Z(a)·Z(b) < 0 :
  1. c = b − Z(b)·(b−a) / (Z(b)−Z(a))          ← sécante
  2. Si Z(a)·Z(c) < 0 : b = c                   ← réduire [a,c]
     Sinon            : a = c, Z(a) *= 0.5       ← correction Illinois
  3. Répéter jusqu'à |b−a| < tolérance (1e-12)
```

La précision 50 dps dans mpmath implique du flottant multi-précision à chaque itération.
libmpfr fait la même chose en C en éliminant l'overhead Python.

## Architecture C

```
c_modules/
├── illinois_mpfr.c   ← affinage Illinois libmpfr (mpfr_t 170 bits ≈ 51 décimales)
├── illinois_mpfr.h
├── z_function.c      ← Z(t) en C (formule RS, float64 pour la détection)
├── z_function.h
├── Makefile          ← compile en .so partagé
└── test_illinois.py  ← test Python via ctypes
```

## Squelette illinois_mpfr.c

```c
#include <mpfr.h>
#include <stdio.h>
#include <math.h>

#define PREC 170  /* 170 bits ≈ 51 décimales */
#define MAX_ITER 100

/* Z_mpfr : Z(t) via Riemann-Siegel en précision MPFR (version simplifiée) */
void Z_mpfr(mpfr_t result, mpfr_t t) {
    mpfr_t theta, sum, term, n_val, ln_n, cos_arg;
    mpfr_inits2(PREC, theta, sum, term, n_val, ln_n, cos_arg, NULL);

    /* N = floor(sqrt(t / 2π)) */
    mpfr_t pi2, t_sur_2pi;
    mpfr_inits2(PREC, pi2, t_sur_2pi, NULL);
    mpfr_const_pi(pi2, MPFR_RNDN);
    mpfr_mul_ui(pi2, pi2, 2, MPFR_RNDN);
    mpfr_div(t_sur_2pi, t, pi2, MPFR_RNDN);
    mpfr_sqrt(t_sur_2pi, t_sur_2pi, MPFR_RNDN);
    long N = mpfr_get_si(t_sur_2pi, MPFR_RNDZ);

    theta_mpfr(theta, t);                     /* θ(t) asymptotique */

    mpfr_set_ui(sum, 0, MPFR_RNDN);
    for (long n = 1; n <= N; n++) {
        mpfr_set_si(n_val, n, MPFR_RNDN);
        mpfr_log(ln_n, n_val, MPFR_RNDN);              /* ln(n)       */
        mpfr_mul(cos_arg, t, ln_n, MPFR_RNDN);         /* t·ln(n)     */
        mpfr_sub(cos_arg, theta, cos_arg, MPFR_RNDN);  /* θ − t·ln(n) */
        mpfr_cos(term, cos_arg, MPFR_RNDN);            /* cos(...)    */
        mpfr_sqrt(n_val, n_val, MPFR_RNDN);            /* √n          */
        mpfr_div(term, term, n_val, MPFR_RNDN);        /* cos/√n      */
        mpfr_add(sum, sum, term, MPFR_RNDN);
    }
    mpfr_mul_ui(result, sum, 2, MPFR_RNDN);            /* 2·Σ */

    mpfr_clears(theta, sum, term, n_val, ln_n, cos_arg, pi2, t_sur_2pi, NULL);
}

/* illinois_mpfr : affine un zéro dans [a_d, b_d] à tolérance tol. Retour : double */
double illinois_mpfr(double a_d, double b_d, double tol) {
    mpfr_t a, b, c, Za, Zb, Zc, fa;
    mpfr_inits2(PREC, a, b, c, Za, Zb, Zc, fa, NULL);

    mpfr_set_d(a, a_d, MPFR_RNDN);
    mpfr_set_d(b, b_d, MPFR_RNDN);
    Z_mpfr(Za, a);
    Z_mpfr(Zb, b);

    for (int i = 0; i < MAX_ITER; i++) {
        mpfr_t num, den, diff;
        mpfr_inits2(PREC, num, den, diff, NULL);
        mpfr_sub(diff, b, a, MPFR_RNDN);
        mpfr_mul(num, Zb, diff, MPFR_RNDN);
        mpfr_sub(den, Zb, Za, MPFR_RNDN);
        if (mpfr_zero_p(den)) { mpfr_clears(num, den, diff, NULL); break; } /* sécu div/0 */
        mpfr_div(num, num, den, MPFR_RNDN);
        mpfr_sub(c, b, num, MPFR_RNDN);
        Z_mpfr(Zc, c);

        mpfr_sub(diff, b, a, MPFR_RNDN);
        mpfr_abs(diff, diff, MPFR_RNDN);
        if (mpfr_get_d(diff, MPFR_RNDN) < tol) { mpfr_clears(num, den, diff, NULL); break; }

        mpfr_mul(fa, Za, Zc, MPFR_RNDN);
        if (mpfr_sgn(fa) < 0) {
            mpfr_set(b, c, MPFR_RNDN);
            mpfr_set(Zb, Zc, MPFR_RNDN);
        } else {
            mpfr_set(a, c, MPFR_RNDN);
            mpfr_set(Za, Zc, MPFR_RNDN);
            mpfr_mul_d(Za, Za, 0.5, MPFR_RNDN);        /* correction Illinois */
        }
        mpfr_clears(num, den, diff, NULL);
    }

    double result = mpfr_get_d(c, MPFR_RNDN);
    mpfr_clears(a, b, c, Za, Zb, Zc, fa, NULL);
    return result;
}
```

## Makefile

```makefile
CC = gcc
CFLAGS = -O3 -march=native -fPIC -Wall
LIBS = -lmpfr -lgmp -lm

all: illinois_mpfr.so

illinois_mpfr.so: illinois_mpfr.c z_function.c
	$(CC) $(CFLAGS) -shared -o $@ $^ $(LIBS)

test: test_illinois.py illinois_mpfr.so
	python3 test_illinois.py

clean:
	rm -f *.so *.o
```
**Note :** la tabulation Makefile est un **TAB réel** (0x09), pas des espaces.

## Interface Python (ctypes)

```python
import ctypes, os, math

so_path = os.path.join(os.path.dirname(__file__), 'illinois_mpfr.so')
if not os.path.exists(so_path):
    raise FileNotFoundError(so_path)   # pas de dégradation silencieuse

lib = ctypes.CDLL(so_path)
lib.illinois_mpfr.restype  = ctypes.c_double
lib.illinois_mpfr.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]

def illinois_c(a: float, b: float, tol: float = 1e-12) -> float:
    """Affinage Illinois en C/libmpfr — ×5 vs mpmath."""
    if not (math.isfinite(a) and math.isfinite(b)):       # valider avant l'appel C
        raise ValueError(f"entrées non finies a={a}, b={b}")
    return lib.illinois_mpfr(a, b, tol)

# Vérification : premier zéro entre t=14.0 et t=14.3
zero1 = illinois_c(14.0, 14.3, 1e-12)
print(f"Premier zéro : {zero1:.15f}  (réf 14.134725141734693)")
```

## Prérequis système

```bash
sudo apt install libmpfr-dev libgmp-dev gcc build-essential
mpfr-config --version   # doit retourner ≥ 4.0
```

## Étapes de la Phase C

1. Implémenter `illinois_mpfr.c` avec θ(t) en libmpfr
2. Valider sur les 10 premiers zéros (écart < 1e-12 vs LMFDB)
3. Benchmark Illinois C vs Illinois mpmath (sur 100 zéros)
4. Intégrer via ctypes (fallback mpmath si `.so` absent, sinon `raise`)
5. Rapport vN→vN+1 : `.md` + PDF pdflatex

## Pièges connus (leçons validées)

- **Biais Z_mpfr ~1e-3 = limite mathématique, pas un bug** : RS tronqué à C0+C1 plafonne
  à ~1e-3. Solution : wrapper `mpmath.siegelz`. `mpc_zeta` est **ABSENT** de libmpc 1.3.1.
- **Callback ctypes lent** : `siegelz` à dps=35 via ctypes coûte 1.5–10 ms/appel et casse
  le parallélisme (×1.84 au lieu de ×4). Piste : `findroot(siegelz, solver="illinois")`
  à dps=15 dans les workers (dps=15 suffit pour tol=1e-12).

## Prochaine étape : python-flint / Arb

Après libmpfr : `python-flint` (bindings FLINT/Arb) pour une arithmétique certifiée
(interval arithmetic) — base de la méthode Odlyzko-Schönhage partielle.

```bash
pip install python-flint   # Arb inclus
```

## Gains attendus

| Composant | Avant (mpmath) | Après (C/libmpfr) | Gain |
|---|---|---|---|
| Illinois affinage | 80–90 % du temps | ~15–20 % | ×5–10 |
| Détection Z(t) | BATCH_CPU 3.59 z/s | inchangé | — |
| **Total estimé** | **3.59 z/s** | **~15–20 z/s** | **×4–6** |

Projection T=100 000 : 138 067 zéros ÷ 15 z/s ≈ **2.5 h**.

---
*Dernière mise à jour : 31 mai 2026 — frontmatter nettoyé, prêt pour `phase-c-illinois/SKILL.md`*
