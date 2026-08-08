---
name: phase-c-illinois
description: >
  Skill pour la Phase C du projet Riemann_Lab — accélération de l'affinage Illinois
  via un module C/libmpfr (illinois_mpfr.so) appelé depuis Python par ctypes.
  Se déclenche sur : "Phase C", "libmpfr", "Illinois en C", "affinage C",
  "illinois_mpfr", "ctypes", "Voie B", "module C", "branche Riemann_Lab_C",
  "post-fork", "mpfr_t", "accélération Illinois", "compute_zeros_v4_1".
version: 0.5.0
date: 2026-07-06
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

## État Phase C au 8 août 2026 (chronologie complète v4.1 → v16)

| Jalon | Statut |
|---|---|
| Voie B validée (v5, `b8018c0`) — Illinois_C pur 100 %, biais < 1e-13 | ✅ |
| `Z_vect_correct` (détection) — 0 désaccord vs siegelz sur 4 plages | ✅ |
| v4.1 post-fork (`d9bb267`) — **41 z/s, ×39** | ✅ mesuré |
| **Option B — `illinois_refine` fa/fb (`581e34d`)** | ✅ **validé T=300, T=1000, T=10 000** |
| Run T=1000 — 649 zéros, 16.15 z/s, Turing COMPLET, LMFDB 19/20 | ✅ |
| Run T=10 000 — 10 141 zéros, **18.65 z/s**, Turing COMPLET, LMFDB 19/20 | ✅ |
| illinois_C 98.6 % sur T=10 000 (objectif 90 % dépassé) | ✅ |
| **v6 — STEP adaptatif + scan_arb, run T=100k** | ✅ **138 069 zéros, 0 manquant, Turing COMPLET, ~113 min** |
| **v7 — `illinois_refine_adaptive` (64→116 bits)** (`8637098`) | ✅ **138 069, 0 manquant, Turing COMPLET, 30.9 min** |
| v7 benchmark T=5k : 1.47 ms/appel, 1808 z/s → **×16 vs 170 bits** | ✅ |
| v7 benchmark T=100k : 42.05 ms/appel, 74.49 z/s → **×3.7 global** | ✅ |
| **v9 — `brent_refine_adaptive`** (remplace le plan v8 prec_fast/W=8) — T=100k 26.6 min turbo | ✅ |
| **v12 — illinois_refine_arb (Arb, tol=1e-12, 2 phases)** — T=100k 8.8 min · LMFDB 20/20 ✅ | ✅ |
| **v13 — T_SEUIL 200→65, TOL 1e-9→1e-12** — T=100k 8.50 min · commit `77efd10` | ✅ |
| **v14 — cache log_n/isqrt_n** — T=100k 7.7 min (×1.10) · commit `d4b3611` | ✅ |
| **v15 — SEUIL_1NEWTON=20k (Phase 2 adaptative)** — T=100k **4.4 min (×1.93)** · LMFDB 20/20 ✅ | ✅ |
| **v16 — Z_arb à précision fixe (acb_dirichlet_hardy_z, 64 bits)** — T=100k **1.6 min (×2.75)** · LMFDB 20/20 ✅ | ✅ ⭐ |
| **Condition Objectif 2 : T=100k < 5 min** | ✅ **ATTEINTE le 04/07/2026, améliorée le 08/08/2026 (1.6 min)** |
| Run T=5 000 000 v13 — 10 016 377 / 10 016 473 zéros · 96 manquants (grille Z_double) | ✅ terminé |
| Rapport `analyse_problemes_v13_v15.md` + PDF | ✅ FAIT — wiki `2f845e4` · pdf `fda4fb9` |
| RAG vault BrainVault (`/mnt/vault_rag`) — 838 chunks, `rag_monitor.py` | ✅ (05/07/2026) |
| Rapport `v5 → v4.1` (`pdf/optimisation/analyse_problemes_v5_v4_1.pdf`) | ⏳ à faire |
| Run T=5M avec v16 — investigation 96 manquants | ⏳ prochaine session |

---

## v7 — Leçon technique clé (11 juin 2026)

**Contre-intuition :** le gain vient de la **précision** (64 bits → 1 limb mpfr → SIMD),
pas du nombre de termes RS. La théorie prédisait ×4.6 via N_termes ; la réalité est ×16 via précision.

| Param. | v6 | v7 |
|---|---|---|
| Phase 1 précision | 170 bits (3 limbs) | **64 bits (1 limb)** |
| Phase 2 précision | 170 bits | 116 bits (2 limbs) |
| ms/appel T=5k | ~23.5 ms | **1.47 ms** |
| ms/appel T=100k | ~130 ms | **42.05 ms** |

**Règle v7 :** `N_full` termes dans les **deux** phases (N_fast = N_full/4 invalide les signes Z).
`ITER_SWITCH=8`, `MAX_ITER=50`. `prec_fast=64`, `prec_full=116`.

> **v8 (piste prec_fast ∈ {32,48,64,80,96} bits / W=8) — abandonnée au profit de v9 Brent.**
> Détail de l'analyse comparative : `analyse_problemes_v8_v9.md` (wiki).

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
| **T=100k v3** | **0.05/0.010** | **2.0 fixe** | **✅ 0 manquant, Turing COMPLET** |

---

## v9 — `brent_refine_adaptive` (validé 2026-06-12)

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

**Résultats v12→v16 (T=100k, PC1 turbo) :**

| Version | Temps | z/s | Phase 2 |
|---|---|---|---|
| v12 | 8.8 min | 261 | 2 Newton Z_arb (early-exit naturel) |
| v13 | 8.50 min | 271 | idem + T_SEUIL=65 |
| v14 | 7.7 min | 299 | v13 + cache log_n/isqrt_n |
| v15 | 4.4 min | 517 | v14 + SEUIL_1NEWTON=20k |
| **v16** | **1.6 min** | **1407** | v15 + Z_arb précision fixe 64 bits |

**Gain cumulé v13→v15 : ×1.93. Gain v15→v16 : ×2.75. Gain global v1→v16 : ×78 650+**
**Condition Objectif 2 (T=100k < 5 min) : ATTEINTE le 04/07/2026, améliorée le 08/08/2026 (1.6 min) ✅**

---

### v16 — Z_arb à précision fixe (acb_dirichlet_hardy_z, 08/08/2026)

**Diagnostic (`perf record` réel sur `illinois_refine_arb`, 08/08/2026) :**
91% du temps dans GMP+FLINT, exclusivement via `arb_fpwrap_cdouble_hardy_z` (Phase 2).
Mécanisme confirmé depuis le code source FLINT 3.3.1 (`src/arb_fpwrap/fpwrap.c`) :
boucle d'escalade `wp=64` puis doublement (64→128→...→8192 bits), recalcul complet à
chaque niveau, jusqu'à certifier une précision **~1e-16** — largement plus que le besoin
réel (tol=1e-12, ~40 bits). `flags=0` (déjà utilisé) est déjà la variante la moins chère
de l'API `fpwrap` — **aucun gain possible en jouant sur `flags` seul**.

**Solution :** appel direct à la fonction bas niveau `acb_dirichlet_hardy_z(res, t, G,
chi, len, prec)` — précision fixe explicite, UN SEUL calcul, pas d'escalade. Nécessite
`dirichlet_group_t`/`dirichlet_char_t` (q=1 = caractère principal = zêta pure, pattern
confirmé sur le test officiel FLINT `acb_dirichlet/test/t-hardy_z.c`), initialisés une
fois par worker (fork) comme le cache RS.

```c
static void init_dirichlet_trivial(void) {
    if (g_dirichlet_ready) return;
    dirichlet_group_init(g_G, 1);
    dirichlet_char_init(g_chi, g_G);
    dirichlet_char_index(g_chi, g_G, 0);   /* caractère principal mod 1 */
    g_dirichlet_ready = 1;
}

#define PREC_BITS_ARB 64   /* coïncide avec WP_INITIAL de arb_fpwrap */

static double Z_arb(double t) {
    init_dirichlet_trivial();
    acb_t s, res;
    acb_init(s); acb_init(res);
    acb_set_d(s, t);
    acb_dirichlet_hardy_z(res, s, g_G, g_chi, 1, (slong)PREC_BITS_ARB);
    double result = arf_get_d(arb_midref(acb_realref(res)), ARF_RND_NEAR);
    acb_clear(s); acb_clear(res);
    return result;
}
```

**Dépendance nouvelle :** headers FLINT 3.3.1 vendorisés en source
(`c_modules/flint-headers-3.3.1/`) — `apt libflint-dev` = 3.0.1, ABI incompatible
(`dirichlet_group_t`/`dirichlet_char_t` activement modifiés entre versions FLINT, risque
de corruption mémoire silencieuse). `Makefile` : `-I flint-headers-3.3.1` ajouté à la
cible `illinois_arb.so`.

**Précision 64 bits choisie** (vs 48 bits, aussi validé bit-identique à l'ancienne
production sur 300 brackets) : coïncide avec `WP_INITIAL` de `arb_fpwrap` lui-même, marge
~7 décimales au-dessus des ~40 bits nécessaires — jugée plus sûre que 48 bits (~2,4
décimales de marge) face à un cas limite non couvert par l'échantillon de test.

**Validation avant intégration** (isolation stricte — `illinois_arb.c` de production
jamais touché avant validation complète) :
1. Prototype isolé (`compute_zeros_v15_test_lowprec.py`, `illinois_arb_lowprec.so`)
   validé sur run réel **T=10000** : Turing COMPLET, LMFDB 20/20, 10 142 zéros identiques
   à v15, gain bout-en-bout **×1.98** (20,2s → 10,2s).
2. Intégration dans `illinois_arb.c` (v16) revalidée à **T=100000** (protocole standard
   du projet, comme pour v12→v15) : 138 069/138 069 zéros, Turing COMPLET, LMFDB 20/20,
   gain **×2.75** (4.4 min → 1.6 min).

**Piège écarté :** MPFR pur (`illinois_refine`, PREC=170 bits, sans Arb) testé en
comparaison — 11,88× **plus lent** ET ~4 ordres de grandeur **moins précis** que la
version Arb (biais structurel de la RS tronquée, même à haute précision). Ne pas
reproposer cette piste.

---

## Architecture scan-puis-affinage — comportement normal, pas un blocage (2026-08-05)

`compute_zeros_v16.py` (mode distribué et solo, même architecture que v15) exécute, par worker, **deux phases
séquentielles distinctes** :

1. **Scan** : `scan_arb(t_start, t_end, step, ...)` — un seul appel bloquant qui
   parcourt l'intégralité du segment du worker et retourne la liste des brackets
   candidats. Aucune sortie n'est produite pendant cette phase.
2. **Affinage** : boucle sur les brackets, produit les lignes
   `[Worker N] zéro #... à t=... — ...s` (celles que lit `zeta_run_progress.py`).

**Conséquence pratique :** un worker peut rester silencieux pendant une **très longue
durée** (plusieurs heures sur un run T=5M) sans que ce soit un signe de blocage — le
scan avance réellement, simplement sans instrumentation de progression. Observé sur le
run T=5M du 04-05/08/2026 : 0 ligne de log pendant les 4 premières heures (confirmé
aussi sur la tentative du 02/08, tuée après 4h+ sans avoir jamais produit une seule
ligne). Le coût du scan par point croît de plus avec t (plus de termes Riemann-Siegel),
donc les workers sur les segments à t élevé restent silencieux plus longtemps que ceux
à t bas — ordre de complétion cohérent avec ça, pas aléatoire.

**Pour vérifier qu'un worker silencieux calcule réellement** (pas bloqué/mort) :
```bash
ps -o pid,pcpu,stat,etimes,cmd -p <PID>   # état R/S + %CPU non nul + ELAPSED qui croît
```
Un worker en état `R` avec du CPU consommé en continu est normal, même sans ligne de
log. `zeta_run_progress.py` (détail workers, touche `d`) n'affiche un worker qu'après
sa première ligne de progression — c'est voulu, pas un bug d'affichage.

---

## Étapes restantes

> 📍 Liste vivante — voir `Handoff.md` (wiki) → section « REPRENDRE ICI » pour la
> priorité courante. Ne pas dupliquer ici.

1. Rapport `v5 → v4.1` (`pdf/optimisation/analyse_problemes_v5_v4_1.pdf`).
2. Run T=5M avec v16 — investigation des 96 manquants (~18h estimé, réduit par le gain v16).
3. Industrialiser la boucle RAG (retrieval + génération) — voir `STACK.md` § Objectif 2.

---
*Skill du projet Riemann_Lab · Auteur : hprzeta · Mise à jour : 3 juin 2026 · 9 juin 2026 (Mur de latence RÉSOLU ×27) · 10 juin 2026 (STEP adaptatif v2) · 11 juin 2026 (v7 validée 30.9 min — prec_fast=64 bits SIMD) · 12 juin 2026 (v9 Brent validée, sudoers OK) · 4 juillet 2026 (v14 cache RS, v15 SEUIL_1NEWTON, Obj2 ✅, T=5M 96 manquants) · **5 juillet 2026 (fusion des deux lignées v7/v8 et v9-v15 — RAG vault en service)** · **5 août 2026 (architecture scan-puis-affinage documentée)** · **8 août 2026 (v16 — Z_arb précision fixe acb_dirichlet_hardy_z, T=100k 1.6 min, Obj2 amélioré)***
