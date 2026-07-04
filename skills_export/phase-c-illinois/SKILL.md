---
name: phase-c-illinois
description: >
  Skill pour la Phase C du projet Riemann_Lab — accélération de l'affinage Illinois
  via un module C/libmpfr (illinois_mpfr.so) appelé depuis Python par ctypes.
  Se déclenche sur : "Phase C", "libmpfr", "Illinois en C", "affinage C",
  "illinois_mpfr", "ctypes", "Voie B", "module C", "branche Riemann_Lab_C",
  "post-fork", "mpfr_t", "accélération Illinois", "compute_zeros_v4_1".
version: 0.3.0
date: 2026-06-03
---

# Phase C — Affinage Illinois en C / libmpfr (Voie B)

> Auteur : hprzeta · Mise à jour : 3 juin 2026

## Contexte

Le profilage montre que l'affinage Illinois représente **80–90 % du temps total** ;
la détection Z(t) n'en fait que 10–20 % (et la GPU GTX 960M n'aide que là).
**Objectif Phase C :** accélérer l'affinage via C/libmpfr.

```
Branche GitHub : Riemann_Lab_C
Dossier local  : ~/projet_zeta/src/calculs/optimisation/c_modules/
```

---

## ⚠️ Architecture RETENUE = Voie B Option B (ne pas refaire la Voie A)

**Voie A (ABANDONNÉE)** : réécrire **toute** la formule Riemann-Siegel — y compris
l'évaluation de Z(t) — en C (`Z_mpfr`). Échec : incohérence entre `Z_mpfr` (C) et
`Z_double`, donnant un **biais ~0.3** au lieu de < 1e-12. De plus `mpc_zeta` est
**absent de libmpc 1.3.1**. → Ne pas repartir sur cette voie.

**Voie B Option B (RETENUE — commit `581e34d`, validée T=10 000 le 3 juin 2026)** :

| Étape | Responsable | Précision |
|---|---|---|
| Détection des intervalles (changements de signe) | `Z_vect_correct` (NumPy vectorisé) | signe seul |
| Affinage du zéro dans l'intervalle | `illinois_refine(a, b, fa, fb, ...)` — fa/fb passés depuis Python (valeurs `Z_vect_correct`) | tol = 1e-12 |
| Itérations intermédiaires | $Z_{\text{mpfr}}$ en C — correct pour $t \geq 300$ ($N \geq 7$ termes RS) | 170 bits |
| Seuil de bascule | `T_SEUIL = 300.0` : `t < 300` → `mpmath.fp.siegelz` (float64) ; `t ≥ 300` → Illinois C | — |

**Pourquoi Option B** : `illinois_mpfr(a, b, tol)` (ancienne API) recalculait $Z(a), Z(b)$
en C avec $Z_{\text{mpfr}}$. Pour $t < 300$ ($N < 7$), une incohérence de signe entre
Python et C produisait un biais ~0.3. Option B résout ce problème en ancrant les bornes
sur les valeurs Python (`fa`/`fb`) — les itérations intermédiaires utilisent toujours
$Z_{\text{mpfr}}$ C, correct à $t \geq 300$.

### Interface ctypes Option B

```python
_lib.illinois_refine.restype  = ctypes.c_double
_lib.illinois_refine.argtypes = [
    ctypes.c_double,  # a
    ctypes.c_double,  # b
    ctypes.c_double,  # fa = Z_vect_correct(a) — déjà calculé
    ctypes.c_double,  # fb = Z_vect_correct(b)
    ctypes.c_int,     # prec_bits (170)
    ctypes.c_double,  # tol (1e-12)
    ctypes.c_int,     # max_iter (200)
]
```

---

## 🔑 Deux règles non négociables (leçons v4 / v4.1)

1. **Chargement du `.so` POST-FORK.** Charger `illinois_mpfr.so` **après** le `fork`
   des workers (dans chaque process), jamais avant le `Pool(...)`. Un handle chargé
   avant le fork se sérialise → parallélisme **×1.8** au lieu de ×4. C'est ce
   chargement post-fork qui a débloqué le **×39 / 41 z/s** (commit `d9bb267`).

2. **Arrêt immédiat si `illinois_mpfr.so` absent.** Pas de fallback global silencieux
   (c'était l'une des 5 erreurs architecturales de v4). Le programme doit s'arrêter
   net avec un message clair si le `.so` n'est pas trouvé.

---

## Méthode Illinois — rappel mathématique

Variante de la sécante évitant la stagnation. Sur $[a,b]$ avec $Z(a)\cdot Z(b) < 0$ :

```
1. c = b − Z(b)·(b−a)/(Z(b)−Z(a))          ← sécante
2. Si Z(a)·Z(c) < 0 : b = c
   Sinon            : a = c, Z(a) ← Z(a)/2   ← correction Illinois
3. Répéter jusqu'à |b−a| < tol (1e-12)
```

Convergence superlinéaire (ordre ≈ 1.44). **`tol = 1e-12` cohérent avec `dps = 35`** ;
`tol = 1e-20` est impossible à 35 dps (bug v2).

---

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

> `make clean && make` doit produire le `.so` **sans warning**. `PREC = 170` bits ≈ 51 décimales
> (cf. `c_modules/CLAUDE.md`).

---

## Interface Python (ctypes) — chargement post-fork

```python
import ctypes, os, multiprocessing as mp

SO_PATH = os.path.join(os.path.dirname(__file__), "illinois_mpfr.so")

# ⚠️ Arrêt immédiat si le .so est absent (pas de fallback silencieux)
if not os.path.exists(SO_PATH):
    raise FileNotFoundError(f"illinois_mpfr.so introuvable : {SO_PATH} — compiler avec `make`")

_lib = None  # handle par-process, chargé APRÈS le fork

def _init_worker():
    """Initializer de Pool : chargé dans CHAQUE worker, donc post-fork."""
    global _lib
    _lib = ctypes.CDLL(SO_PATH)
    _lib.illinois_mpfr.restype  = ctypes.c_double
    _lib.illinois_mpfr.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]

def illinois_c(a: float, b: float, tol: float = 1e-12) -> float:
    return _lib.illinois_mpfr(a, b, tol)

# Lancement : le .so n'est PAS chargé dans le process parent
with mp.Pool(4, initializer=_init_worker) as pool:
    ...
```

---

## Prérequis système

```bash
sudo apt install libmpfr-dev libgmp-dev gcc build-essential
mpfr-config --version
```

---

## État Phase C au 4 juillet 2026

| Jalon | Statut |
|---|---|
| Voie B validée (v5, `b8018c0`) — Illinois_C pur 100 %, biais < 1e-13 | ✅ |
| `Z_vect_correct` (détection) — 0 désaccord vs siegelz sur 4 plages | ✅ |
| v4.1 post-fork (`d9bb267`) — **41 z/s, ×39** | ✅ mesuré |
| **Option B — `illinois_refine` fa/fb (`581e34d`)** | ✅ **validé T=300, T=1000, T=10 000** |
| Run T=1000 — 649 zéros, 16.15 z/s, Turing COMPLET, LMFDB 19/20 | ✅ |
| Run T=10 000 — 10 141 zéros, **18.65 z/s**, Turing COMPLET, LMFDB 19/20 | ✅ |
| **v12 — illinois_refine_arb (Arb, tol=1e-12, 2 phases)** — T=100k 8.8 min · LMFDB 20/20 ✅ | ✅ |
| **v13 — T_SEUIL 200→65, TOL 1e-9→1e-12** — T=100k 8.50 min · commit `77efd10` | ✅ |
| **v14 — cache log_n/isqrt_n** — T=100k 7.7 min (×1.10) · commit `d4b3611` | ✅ |
| **v15 — SEUIL_1NEWTON=20k (Phase 2 adaptative)** — T=100k **4.4 min (×1.93)** · LMFDB 20/20 ✅ | ✅ ⭐ |
| **Condition Objectif 2 : T=100k < 5 min** | ✅ **ATTEINTE le 04/07/2026** |
| Run T=5 000 000 v13 — 10 016 377 / 10 016 473 zéros · 96 manquants (grille Z_double) | ✅ terminé |
| Rapport `v5 → v4.1` (`pdf/optimisation/analyse_problemes_v5_v4_1.pdf`) | ⏳ à faire |
| Rapport `analyse_problemes_v13_v15.md` + PDF | ⏳ à faire |
| Run T=5M avec v15 — investigation 96 manquants | ⏳ prochaine session |

---

## Gains mesurés (Option B — run réel T=10 000)

| Composant | Avant (mpmath pur v3) | Après (Option B v4.1) |
|---|---|---|
| Vitesse globale | ~3.59 z/s | **18.65 z/s (×5.2)** |
| Affinage t ≥ 300 | 80–90 % du temps (mpmath) | illinois_C 159 ms/appel à t~9000 |
| Affinage t < 300 | mpmath.findroot 35 dps | mpmath_petit_t (légitime, 1.4 % du total) |
| Turing | COMPLET | COMPLET |
| LMFDB 19/20 | 20/20 (v3) | **19/20** (zéro #20 = 8.06e-10, cas limite stable) |

**Goulot résiduel identifié :** `illinois_C` à grand t — coût croît en $O(\sqrt{t})$ via
$N_{\text{RS}} = \lfloor\sqrt{t/2\pi}\rfloor$ termes à 170 bits. À $t \sim 9000$ : ~159 ms/appel.
Inexistant dans v3 (mpmath pur plafonné à ~296 ms/appel constant). Pertinent pour T=100 000.

---

## Mur de latence — RÉSOLU (2026-06-09)

- `mpmath.siegelz` : 21.13 ms/appel → ~7h pour T=10 000
- `arb_fpwrap_cdouble_hardy_z` : 0.77 ms/appel → ~15 min — **×27**
- Intégré dans `compute_zeros_v4_1.py` (commit `b563db2`, Riemann_Lab_C)
- `arb_wrapper.py` : détection auto libflint bundlée, fallback `mpmath` si absent
- Run T=100 000 (2026-06-10) : 137 904 zéros · 99.35 min · 23.14 z/s
- 356 manquants → cause : STEP=0.1 trop grand à grand t (espacement min = 0.028)
- Fix v1 (commit `7467731`) : `step_pour_t()` → STEP 0.1/0.05/0.02 selon tranche t
- Fix v2 (commit `181fdd1`) : STEP 0.05/0.010 — gap min mesuré 0.01940 à t=66678 (< 0.02)
- Segmentation 1/√t → charge équilibrée entre workers

---

## STEP adaptatif — règle obligatoire (2026-06-10)

**Ne jamais utiliser STEP fixe.** Condition mathématique :

$$\text{STEP}(t) < \frac{\pi}{\ln(t/2\pi)}$$

Valeurs implémentées (`step_pour_t` dans `compute_zeros_v4_1.py`) — **v2, commit `181fdd1`** :

| Tranche $t$ | STEP | Justification |
|---|---|---|
| $t < 5\,000$ | 0.05 | $\delta_{\min} \approx 0.5$ — large marge |
| $t \geq 5\,000$ | **0.010** | gap min mesuré 0.01940 à t=66678 — STEP=0.02 capturait des faux brackets |

**Overlap :** toujours **fixe = 2.0** (jamais proportionnel au STEP).

Résultats mesurés :

| Test | STEP | Overlap | Turing |
|---|---|---|---|
| T=10k v1 | 0.1 fixe | ×4 STEP | ❌ 6 manquants |
| **T=10k v2** | **0.05 pour t≥5k** | **2.0 fixe** | **✅ 0 manquant** (commit `50837f7`) |
| T=100k v1 adaptatif | 0.1/0.05/0.02 | 2.0 fixe | ❌ 30 manquants (t>50k) |
| T=100k v2 adaptatif | 0.1/0.05/0.02 | 2.0 fixe | ❌ 68 manquants · 105 min (STEP=0.02 insuffisant) |
| **T=100k v3** | **0.05/0.010** | **2.0 fixe** | **EN COURS (2026-06-10 16h42)** |

---

## Étapes restantes

1. Analyser run T=100 000 v3 (STEP=0.05/0.010) — Turing-Backlund COMPLET attendu.
2. Si ✅ : documenter résultat dans §23.4 de `Formules_zeta.md` + STACK.md.
3. Rédiger le rapport `v5 → v4.1` (même structure que `v2→v3`).

---
*Skill du projet Riemann_Lab · Auteur : hprzeta · Mise à jour : 3 juin 2026 · 9 juin 2026 (Mur de latence RÉSOLU ×27) · 10 juin 2026 (STEP v3 0.05/0.010 lancé T=100k)*

---

## v13 → v15 — Chronologie et résultats (2026-07-04)

### v14 — Cache RS statique

**Principe :** éviter `log(n)` + `1/sqrt(n)` à chaque terme de la somme RS.

```c
#define N_MAX_CACHE 2100  /* couvre T ≲ 27M */
static double log_n_cache[N_MAX_CACHE + 1];
static double isqrt_n_cache[N_MAX_CACHE + 1];
static int    g_cache_ready = 0;

static void init_rs_cache(void) {
    if (g_cache_ready) return;
    for (int n = 1; n <= N_MAX_CACHE; n++) {
        log_n_cache[n]   = log((double)n);
        isqrt_n_cache[n] = 1.0 / sqrt((double)n);
    }
    g_cache_ready = 1;
}
/* boucle RS : */
sum += cos(th - t * log_n_cache[n]) * isqrt_n_cache[n];
```

Gain ×1.10 sur T=100k. L'init est appelée une fois au premier appel du worker (post-fork).
Fichiers modifiés : `illinois_arb.c` et `scan_arb.c` — commit `d4b3611`.

### v15 — Phase 2 adaptative SEUIL_1NEWTON

**Principe mathématique :**
- Biais Z_rs ≈ C·t^{-5/4} avec C ≈ 0.305 (calibré LMFDB 04/07)
- Erreur après 1 Newton ≈ biais² ≈ C²·t^{-5/2}
- Pour t ≥ 20 000 : biais ≈ 6.4e-7, erreur ≈ 4e-13 < tol=1e-12
- SEUIL_1NEWTON = 20 000 (marge ×2.4 par rapport au minimum strict ≈ 16 000)

```c
#define SEUIL_1NEWTON 20000.0

int n_newton = (t_curr < SEUIL_1NEWTON) ? 2 : 1;
for (int k = 0; k < n_newton; k++) {
    double dZ = (Z_rs_double(t_curr + h) - Z_rs_double(t_curr - h)) / (2.0 * h);
    if (fabs(dZ) < 1e-10) break;
    double Zt = Z_arb(t_curr);
    if (fabs(Zt) < tol) return t_curr;
    double delta = Zt / dZ;
    t_curr -= delta;
    if (fabs(delta) < tol) break;
}
```

**Piège absolu :** ne jamais réduire à 1 Newton pour TOUT t.
1 Newton fixe → erreur ~1.75e-6 à t≈65 (biais_RS=5e-3 → LMFDB 14/20).

**Résultats v12→v15 (T=100k, PC1 turbo) :**

| Version | Temps | z/s | Phase 2 |
|---|---|---|---|
| v12 | 8.8 min | 261 | 2 Newton Z_arb (early-exit naturel) |
| v13 | 8.50 min | 271 | idem + T_SEUIL=65 |
| v14 | 7.7 min | 299 | v13 + cache log_n/isqrt_n |
| **v15** | **4.4 min** | **517** | v14 + SEUIL_1NEWTON=20k |

**Gain cumulé v13→v15 : ×1.93. Gain global v1→v15 : ×28 600+**
**Condition Objectif 2 (T=100k < 5 min) : ATTEINTE le 04/07/2026 ✅**

---

### v9 — brent_refine_adaptive (validé 2026-06-12)

**Résultats :** 138 069 zéros · 0 manquant · Turing COMPLET · 26.6 min turbo · 28.0 min sans turbo

**Pourquoi Brent gagne :**
- Ordre ~1.84 vs Illinois ~1.44 → ~4 iter vs ~6 → même coût/iter (1 éval Z) → ×1.80 global

**Turbo :** gain seulement ×1.05 (vs ×1.63 pour v7). Brent C limité par bande passante mémoire MPFR (ops 64→80 bits), pas par fréquence CPU.

**Fichiers :**
- `src/calculs/optimisation/c_modules/brent_mpfr.c`
- `src/calculs/optimisation/c_modules/brent_mpfr.h`
- `src/calculs/optimisation/compute_zeros_v9.py`

**Paramètres validés :**
- prec_fast=64 · prec_full=80 · tol=1e-11 · max_iter=50
- STEP=0.010 fixe — NE JAMAIS MODIFIER
- Charger `brent_mpfr.so` POST-FORK dans `worker_init()`

**Sudoers :** `/etc/sudoers.d/zeta_turbo` fonctionnel depuis 2026-06-12.
Toujours lancer `zeta_turbo_on.sh` avant run de production. Toujours `zeta_turbo_off.sh` après.

---
*Skill du projet Riemann_Lab · Auteur : hprzeta · Mise à jour : 3 juin 2026 · 9 juin 2026 · 10 juin 2026 · 12 juin 2026 (v9 Brent validée, sudoers OK) · **4 juillet 2026 (v14 cache RS, v15 SEUIL_1NEWTON, Obj2 ✅, T=5M 96 manquants)***
