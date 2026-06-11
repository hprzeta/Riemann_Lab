# Bibliothèques Python — Référence Zeta-Lab
> Version enrichie — Projet Riemann_Lab · hprzeta
> Mise à jour : 2 juin 2026 · Auteur : hprzeta

---

## Environnement

```bash
# Activation obligatoire avant tout script
source ~/projet_zeta/zeta_env/bin/activate
export PYTHONPATH="${PYTHONPATH}:${HOME}/projet_zeta/src"
python mon_script.py
```

**Modules du projet** (dans `~/projet_zeta/src/calculs/optimisation/`) :
```
theta_rapide.py          # θ(t) asymptotique + Z_fast
riemann_siegel_batch.py  # Z_batch GPU/CPU, scanner_batch + Illinois
turing_validation.py     # N(T), S(T), valider_turing
parallel_scanner.py      # calcul multiprocessing
compute_zeros_v3.py      # orchestrateur principal
```

---

## 1. mpmath — Arithmétique haute précision

**Rôle** : calcul exact de $\zeta(s)$, $\theta(t)$, $\Gamma(s)$, affinage Illinois.

```python
from mpmath import mp, mpc, mpf, zeta, loggamma, zetazero
from mpmath import siegelz, siegeltheta  # wrappers haut niveau
from mpmath import findroot, arg, re, im, pi, log

# ── Précision adaptative (règle v3) ─────────────────────────────────────
mp.dps = 25   # détection rapide (changement de signe Z)
mp.dps = 35   # affinage Illinois (atteint tol=1e-12)
mp.dps = 50   # validation / publication des 1000 premiers zéros

# ── θ(t) exact (pour t < 20 ou vérification) ────────────────────────────
theta_exact = float(
    mp.im(loggamma(mpf("0.25") + mpc(0, t) / 2))
    - (t / 2) * mp.log(mp.pi)
)

# ── Z(t) optimisé — un seul appel à zeta() ──────────────────────────────
import math
s   = mpc("0.5", t)
z   = zeta(s)                              # appel unique
val = math.cos(th) * float(z.real) - math.sin(th) * float(z.imag)

# ── Zéros via zetazero (lent, pour vérification seulement) ──────────────
zetazero(1)    # 0.5 + 14.1347...j  — précis mais ~1 s/zéro
zetazero(10)   # 0.5 + 49.7738...j

# ── Affinage Illinois ────────────────────────────────────────────────────
mp.dps = 35
t0 = findroot(
    lambda x: Z_fast(float(x), dps=35),
    (t_a, t_b),           # intervalle avec changement de signe
    solver="illinois",
    tol=1e-12,
    maxsteps=80,
)
# ⚠️ tol=1e-12 cohérent avec 35 dps.  tol=1e-20 à 35 dps → IMPOSSIBLE (bug v2)

# ── Sauvegarde/restauration de précision ────────────────────────────────
dps_save = mp.dps
mp.dps = 35
# ... calcul ...
mp.dps = dps_save   # toujours restaurer après usage local
```

---

## 2. numpy — Calcul vectorisé (CPU)

**Rôle** : θ(t) vectorisé, matrice de phases RS, détection de signes.

```python
import numpy as np

# ── θ(t) vectorisé (asymptotique de Stirling) ───────────────────────────
LOG_2PI = math.log(2 * math.pi)
PI_8    = math.pi / 8.0

t2 = ts * ts;  t3 = t2 * ts;  t5 = t3 * t2
thetas = (
    (ts / 2.0) * (np.log(ts) - LOG_2PI)
    - ts / 2.0 - PI_8
    + 1.0 / (48.0 * ts)
    + 7.0 / (5760.0 * t3)
    - 31.0 / (80640.0 * t5)
)

# ── Matrice de phases RS (cœur de Z_batch) ──────────────────────────────
ns       = np.arange(1, N_max + 1, dtype=np.float64)
log_ns   = np.log(ns)
inv_sqn  = 1.0 / np.sqrt(ns)

phases = thetas[:, None] - ts[:, None] * log_ns[None, :]  # shape (M, N_max)
Z      = 2.0 * np.dot(np.cos(phases), inv_sqn)            # shape (M,)

# ── Détection des changements de signe ──────────────────────────────────
signes   = np.sign(Z_vals)
passages = np.where(np.diff(signes) != 0)[0]  # indices des changements

# ── Espacements normalisés (conjecture de Montgomery) ───────────────────
ecarts  = np.diff(zeros)
t_mid   = zeros[:-1]
delta_n = ecarts * np.log(np.array(t_mid) / (2 * math.pi)) / (2 * math.pi)
```

---

## 3. CuPy — Calcul vectorisé GPU (NVIDIA GTX 960M)

**Rôle** : accélération ×8 à ×12 de Z_batch via CUDA.

```python
import cupy as cp

# ── Détection GPU ────────────────────────────────────────────────────────
n_devices = cp.cuda.runtime.getDeviceCount()  # 0 si GPU inactive
# ⚠️ Activer le GPU : sudo prime-select nvidia puis redémarrage
# ⚠️ Paquets : pip install cupy-cuda12x  (doit matcher CUDA 12.2)

# ── Calcul GPU identique à numpy, backend différent ─────────────────────
ts_g     = cp.asarray(ts_cpu,     dtype=cp.float64)
thetas_g = cp.asarray(thetas_cpu, dtype=cp.float64)
log_ns_g = cp.asarray(log_ns,     dtype=cp.float64)
inv_sqn_g= cp.asarray(inv_sqn,    dtype=cp.float64)

phases   = thetas_g[:, None] - ts_g[:, None] * log_ns_g[None, :]
Z_g      = 2.0 * cp.dot(cp.cos(phases), inv_sqn_g)

Z_cpu    = cp.asnumpy(Z_g)  # retour vers numpy

# ── Limites mémoire GTX 960M (4 GB VRAM) ────────────────────────────────
# bloc recommandé : int(1_500_000_000 / (N_max * 8))
# T = 10 000  (N_max=39)  → bloc=500 000 → 156 MB ✅
# T = 100 000 (N_max=126) → bloc=200 000 → 201 MB ✅

# ⚠️ BLAS thread contention : benchmarker les modes isolément (pas en concurrent)
```

---

## 4. multiprocessing — Parallélisation (4 cœurs)

**Rôle** : partitionner $[T_{\min}, T_{\max}]$ sur N workers. ×4 de gain.

```python
import multiprocessing

# ⚠️ Ne PAS utiliser joblib avec mpmath :
#    GMP (MPFR) a un état global non thread-safe → corruption mémoire.
#    Solution : multiprocessing (fork → chaque processus a sa propre copie GMP)

n_workers = multiprocessing.cpu_count()  # 4 sur i7

# ── Partitionnement ──────────────────────────────────────────────────────
longueur  = (T_MAX - T_MIN) / n_workers
segments  = [
    (T_MIN + i * longueur, T_MIN + (i + 1) * longueur)
    for i in range(n_workers)
]
# ⚠️ Chevauchement de 2·STEP aux jonctions pour ne rater aucun zéro de bord

# ── Lancement ────────────────────────────────────────────────────────────
with multiprocessing.Pool(n_workers) as pool:
    resultats = pool.map(worker_func, args_list)

# ── Fusion et déduplication ──────────────────────────────────────────────
zeros_bruts = [t for segment in resultats for t in segment]
zeros_bruts.sort()
zeros = dedupliquer(zeros_bruts, tolerance=0.001)
```

---

## 5. pandas — Sauvegarde CSV

**Rôle** : stocker les zéros calculés avec métadonnées.

```python
import pandas as pd
from pathlib import Path
from datetime import datetime

horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
nom_csv    = f"zeros_v3_T{T_MAX:.0f}_{horodatage}.csv"

df = pd.DataFrame({
    "n":                 range(1, len(zeros) + 1),
    "partie_imaginaire": zeros,
    "T_MAX":             T_MAX,
    "methode":           "RS-detection + Illinois-affinage",
    "step_adaptatif":    STEP,
    "n_workers":         N_WORKERS,
    "turing_complet":    True,
    "calcule_le":        horodatage,
})
df.to_csv(str(Path("calculs") / nom_csv), index=False)

# ── Chargement ultérieur ─────────────────────────────────────────────────
df    = pd.read_csv("zeros_zeta_T10000_20260424_205325.csv")
zeros = df["partie_imaginaire"].tolist()
```

---

## 6. matplotlib — Visualisation (sans blocage)

**Rôle** : tracer Z(t), espacements, droite critique.

```python
import matplotlib.pyplot as plt
import numpy as np

# ⚠️ TOUJOURS plt.savefig() + plt.close() — JAMAIS plt.show() en production
#    plt.show() est BLOQUANT : empêche la génération du log/CSV après le graphique.

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle(f"Zéros ζ — {len(zeros)} zéros [T={T_MAX:.0f}]")

# ── Z(t) avec marqueurs aux zéros ───────────────────────────────────────
ax = axes[0]
ax.plot(t_vals, Z_vals, 'b-', linewidth=0.8, label='Z(t)')
ax.axhline(0, color='k', linewidth=0.5)
for t0 in zeros:
    ax.axvline(t0, color='r', linewidth=0.5, alpha=0.4)

# ── Histogramme espacements vs GUE ──────────────────────────────────────
ax = axes[1]
ax.hist(delta_n, bins=50, density=True, alpha=0.75, color='steelblue')
s_vals = np.linspace(0, 4, 200)
gue    = (math.pi / 2) * s_vals * np.exp(-math.pi * s_vals**2 / 4)
ax.plot(s_vals, gue, 'r-', linewidth=2, label='GUE (Wigner-Dyson)')

# ── Droite critique ──────────────────────────────────────────────────────
ax = axes[2]
ax.scatter([0.5] * len(zeros), zeros, s=3, color='darkblue', alpha=0.4)
ax.axvline(0.5, color='r', linestyle='--', linewidth=1.5)

plt.tight_layout()
plt.savefig("zeros_v3.png", dpi=150)
plt.close()    # ← libère la mémoire, ne bloque pas
```

---

## 7. loguru — Logging structuré

**Rôle** : journal d'exécution persistant avec rotation.

```python
from loguru import logger
from pathlib import Path

logger.add(
    Path("~/projet_zeta/logs/projet_zeta.log"),
    rotation="100 MB",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

logger.info(f"Calcul v3 démarré : T_MAX={T_MAX:.0f}")
logger.success(f"Zéro #{n:5d} : t = {t:.14f}  (écart LMFDB : {ecart:.2e})")
logger.warning(f"Worker {wid} : surplus de {delta} zéros aux bords")
logger.error(f"Illinois non convergé : [{t_a:.4f}, {t_b:.4f}]")
```

---

## 8. tqdm — Barres de progression

```python
from tqdm import tqdm

for t in tqdm(np.arange(T_MIN, T_MAX, STEP), desc="Scan Z(t)", unit="pt"):
    # calcul...
```

---

## 9. sympy — Calcul symbolique (exploration, pas production)

```python
from sympy import zeta, gamma, pi, I, re, im, Symbol, simplify
from sympy.ntheory import primerange, isprime, nextprime

s = Symbol('s')
zeta(s)                     # objet symbolique
list(primerange(1, 100))    # premiers jusqu'à 100
nextprime(100)              # 101
```

> **Note** : sympy n'est pas utilisé dans le pipeline de production (trop lent).
> Utiliser mpmath pour les calculs numériques de haute précision.

---

## 10. psutil — Monitoring système

```python
import psutil

n_cores = psutil.cpu_count(logical=True)       # 4 (i7)
ram_gb  = psutil.virtual_memory().total / 1e9  # 8.0 GB
ram_pc  = psutil.virtual_memory().percent      # % utilisé
```

---

## 11. Vérification GPU avant lancement

```bash
# Vérifier que le GPU NVIDIA est actif
nvidia-smi

# Si "no devices found" :
sudo prime-select nvidia
# → reboot nécessaire

# Paquet CuPy correct pour CUDA 12.2 :
pip install cupy-cuda12x --break-system-packages
```

---

## 12. Arb / FLINT — affinage rapide haute précision (levier Phase C)

> **Pourquoi cette section** : la §17 de `Formules_zeta.md` (mur de latence) montre que le
> goulot du calcul est la **latence d'un appel `mpmath.siegelz`** (~296 ms à $t\approx 9000$),
> répétée ~27 fois par zéro. Le **seul levier réaliste** pour des positions $<10^{-10}$ sous
> 30 min n'est ni le GPU ni la RAM (absents de la formule de coût), mais le remplacement de
> `mpmath` par **Arb** à l'étape d'affinage.

**Rôle** : évaluer $Z(t)$ de Hardy en arithmétique de boules (intervalles certifiés, en C),
≈ ×10–20 plus vite que `mpmath.siegelz` à précision égale.

```bash
# ── Installation (Ubuntu) ────────────────────────────────────────────────
sudo apt install libflint-dev libarb-dev            # bibliothèques C
pip install python-flint --break-system-packages    # binding Python (FLINT + Arb)
```

```python
# ── Précision en BITS (≈ dps · 3.33) ─────────────────────────────────────
from flint import arb, ctx
ctx.prec = 200    # ~60 chiffres décimaux

# Fonction clé côté Arb : acb_dirichlet_hardy_z  → Z(t) de Hardy avec bornes
# d'erreur rigoureuses. Si python-flint ne l'expose pas directement, l'appeler
# via un petit wrapper ctypes vers libarb (acb_dirichlet_hardy_z).
```

> Le facteur ×27 est **mesuré** (benchmark 2026-06-09 sur 200 points $t \in [100, 10000]$).
> Bonus à grand volume : l'algorithme **Odlyzko–Schönhage** (multi-évaluation par FFT)
> casse le coût asymptotique — pertinent seulement pour $T \gg 10\,000$.

**Statut : VALIDÉ ×27 (2026-06-09)**

| Paramètre | Valeur |
|---|---|
| Speedup vs mpmath | ×27 mesuré |
| temps/appel | 0.77 ms vs 21.13 ms |
| Précision | double ~15 dps, erreur $< 2.2\times10^{-16}$ |
| Accès | ctypes + libflint bundlée python-flint 0.8.0 |
| Module | `src/calculs/optimisation/arb_wrapper.py` |
| Pattern | `arb_hardy_z(t)` remplace `float(mp.siegelz(t))` |

| Outil | Rôle | Statut projet |
|---|---|---|
| `mpmath.siegelz` | affinage fallback (Voie B) | production — remplacé par Arb |
| Arb `arb_fpwrap_cdouble_hardy_z` | affinage rapide (double natif, 0 malloc) | **VALIDÉ ×27** |
| FLINT | dépendance d'Arb (entiers, polynômes) | requis pour Arb |

### Résultats runs avec Arb (2026-06-10)

| Run | STEP | Zéros | Manquants | Temps | Turing |
|---|---|---|---|---|---|
| T=10 000 v1 | 0.1 fixe | 10 137 / 10 142 | 6 | ~2.58 min | ❌ INCOMPLET |
| T=10 000 v2 | 0.05 pour t≥5k | **10 141 / 10 142** | **0** | **2.60 min** | **✅ COMPLET** |
| T=100 000 v1 | 0.1 fixe | 137 904 / 138 069 | 356 | 1h58 | ❌ INCOMPLET |
| T=100 000 v2 | 0.1/0.05/0.02 adaptatif | 138 039 / 138 069 | 68 | 105.1 min | ❌ INCOMPLET |
| **T=100 000 v3** | **0.05/0.010** | **EN COURS** | **—** | **~3–4h** | **attendu ✅** |

> v1 → STEP=0.1 fixe (trop grand à grand t).
> v2 → STEP adaptatif 0.1/0.05/0.02 + overlap=2.0 (commit `50837f7`) — STEP=0.02 insuffisant à t≥50k.
> v3 → STEP adaptatif 0.05/0.010 (commit `181fdd1`) — lancé 2026-06-10 16h42.

---

## 13. Tableau récapitulatif — rôle par bibliothèque

| Bibliothèque | Usage dans v3 | Mode |
|---|---|---|
| `mpmath` | θ(t) exact, Z_fast, affinage Illinois, validation | CPU précis |
| `numpy` | θ(t) vectorisé, phases RS, détection signes | CPU rapide |
| `cupy` | Z_batch GPU (si GTX 960M active) | GPU ×10 |
| `multiprocessing` | Parallélisation sur 4 cœurs | CPU ×4 |
| `pandas` | Sauvegarde/chargement CSV zéros | I/O |
| `matplotlib` | Z(t), espacements, droite critique | Visualisation |
| `loguru` | Journal d'exécution complet | Logging |
| `tqdm` | Barres de progression | Interface |
| `sympy` | Exploration symbolique seulement | Hors prod. |
| `psutil` | Monitoring CPU/RAM | Diagnostic |
| `arb` / `python-flint` | Affinage Z(t) rapide (levier §17, à benchmarker) | CPU certifié |

---
*Auteur : hprzeta · Dernière mise à jour : 2 juin 2026 — 390 lignes*
---

## §13 — workprec vs fp : précision locale en mpmath (3 juin 2026)

### Contexte
Découvert lors du diagnostic pipeline v4.1 (3 juin 2026) : `workprec` ne contrôle
pas la précision des fonctions mpmath internes.

### workprec — précision de la boucle, pas de la fonction

```python
import mpmath as mp
mp.mp.dps = 35   # global : 35 dps

with mp.workprec(50):           # 50 bits ≈ 15 dps — contexte local
    x = mp.siegelz(100.0)       # ⚠️ siegelz re-lit mp.dps = 35 → précision 35 dps
    y = mp.findroot(
        mp.siegelz, (14.1, 14.2),
        solver="illinois"
    )
    # La boucle Illinois tourne à 50 bits, MAIS chaque éval siegelz = 35 dps
```

**Usage correct de workprec :** opérations arithmétiques pures (additions, multiplications,
racines) — PAS pour les fonctions de haut niveau comme `siegelz`, `zeta`, `gamma`.

### fp — float64 natif (×40 plus rapide que dps=35)

```python
# float64 natif — ~1e-15 de précision, pas de surcharge multi-précision
z = mp.fp.siegelz(t)        # float64
theta = mp.fp.siegeltheta(t)

# findroot en float64 (bracket obligatoire pour stabilité) :
zero = mp.fp.findroot(
    mp.fp.siegelz, (a, b),
    solver="illinois", tol=1e-12, maxsteps=80,
)
```

**Quand utiliser fp :** t < 300 (N < 7 termes RS), tol = 1e-12, bracket fourni.
float64 ($\varepsilon \approx 10^{-16}$) est sous la tolérance → précision suffisante.

**Quand NE PAS utiliser fp :** grand t, précision < 1e-12 exigée, ou validation LMFDB
(qui nécessite ≥ 30 dps pour comparer γ à 14 décimales significatives).

### Résumé comparatif

| API | Précision | Coût relatif | Usage recommandé |
|---|---|---|---|
| `mp.siegelz(t)` dps=35 | ~1e-35 | référence (1×) | affinage final, LMFDB |
| `mp.siegelz(t)` dps=15 | ~1e-15 | ~×4 plus rapide | — (workprec ne marche pas) |
| `mp.fp.siegelz(t)` | ~1e-15 | **~×40 plus rapide** | t<300, bracket fourni |
| C/libmpfr PREC=170 bits | ~1e-50 | ~×10 vs mpmath | t≥300, Illinois_C |

---
*Auteur : hprzeta — Riemann_Lab — Mise à jour : 3 juin 2026*

---

## §14 — ctypes — interface Python ↔ illinois_mpfr.so (Option B, 3 juin 2026)

> Contexte : Phase C, branche `Riemann_Lab_C`. Le module C `illinois_mpfr.so`
> expose `illinois_refine` depuis le commit `581e34d`. Règle post-fork obligatoire
> (voir skill `phase-c-illinois`).

### Règle post-fork — chargement dans chaque worker

```python
import ctypes, os, multiprocessing

SO_PATH = os.path.join(
    os.path.dirname(__file__),
    "c_modules", "illinois_mpfr.so"
)

_lib = None   # handle par-process, initialisé APRÈS le fork

def _init_worker():
    """Chargé dans chaque worker du Pool — post-fork obligatoire."""
    global _lib
    _lib = ctypes.CDLL(SO_PATH)
    # ── illinois_refine : fa/fb passés depuis Python (Option B) ──────────
    _lib.illinois_refine.restype  = ctypes.c_double
    _lib.illinois_refine.argtypes = [
        ctypes.c_double,   # a      — borne gauche de l'intervalle
        ctypes.c_double,   # b      — borne droite
        ctypes.c_double,   # fa     = Z_vect_correct(a) déjà calculé
        ctypes.c_double,   # fb     = Z_vect_correct(b)
        ctypes.c_int,      # prec_bits (170 bits = ~51 décimales)
        ctypes.c_double,   # tol    (1e-12)
        ctypes.c_int,      # max_iter (200)
    ]

# ⚠️ Le .so ne doit PAS être chargé dans le processus parent (avant Pool)
# → chargement pré-fork = handle sérialisé → ×1.8 au lieu de ×4
with multiprocessing.Pool(4, initializer=_init_worker) as pool:
    resultats = pool.map(worker_func, args_list)
```

### Appel dans le worker

```python
def affiner_illinois_c(a: float, b: float,
                       fa: float, fb: float,
                       tol: float = 1e-12) -> float:
    """Affinage illinois via C/libmpfr (Option B).
    fa/fb : valeurs Z déjà calculées par Z_vect_correct — zéro recalcul."""
    return _lib.illinois_refine(a, b, fa, fb, 170, tol, 200)
```

**Pourquoi passer fa/fb ?** Si Illinois recalculait $Z(a), Z(b)$ en C avec $Z_{\text{mpfr}}$
(RS tronquée $C_0+C_1$), une incohérence de signe avec Python produisait un biais ~0.3.
En passant fa/fb depuis Python, l'encadrement initial est ancré sur les vrais zéros de
$\zeta(\tfrac{1}{2}+it)$ — seules les itérations intermédiaires utilisent $Z_{\text{mpfr}}$.

### Résumé comparatif — méthodes d'affinage

| Méthode | ms/appel ($t\!\sim\!500$) | ms/appel ($t\!\sim\!9000$) | Précision position | Statut |
|---|---|---|---|---|
| `mpmath.findroot(siegelz)` dps=35 | ~296 ms | ~296 ms | $<10^{-13}$ ✅ | lent mais fiable |
| `illinois_refine` C/libmpfr 170 bits | ~58.9 ms | ~159 ms | $<10^{-13}$ ✅ | **production** |
| `mp.fp.siegelz` (float64) | ~7 ms | ~7 ms | $\sim10^{-15}$ ✅ | t<300 seulement |

> ⚠️ Arrêt immédiat si `.so` absent — **pas de fallback silencieux** :
> ```python
> if not os.path.exists(SO_PATH):
>     raise FileNotFoundError(f"illinois_mpfr.so introuvable : {SO_PATH} — `make`")
> ```

---
*Auteur : hprzeta — Riemann_Lab — Mise à jour : 3 juin 2026 (§14 ajouté) · 6 juin 2026 (§15 ajouté)*

---

## §15 — chrono_phases.py — Profileur 3+1 phases pipeline v4.1 (6 juin 2026)

> Présent sur `Riemann_Lab_C` depuis commit `d26ed12`.
> Confirmé le 6 juin 2026 (ancêtre de `191d60a`).

### Rôle

Mesurer le temps cumulé, le nombre d'appels et le coût ms/appel pour chacune des
4 phases du pipeline `compute_zeros_v4_1.py` :

| Phase (clé) | Description | Implémentation |
|---|---|---|
| `detection` | Balayage $Z(t)$ vectorisé, changements de signe | `Z_vect_correct` (numpy) |
| `illinois_C` | Affinage haute précision (t ≥ 300) | `illinois_refine` (C/libmpfr, 170 bits) |
| `mpmath_petit_t` | Fallback t < 300 ($N_{\text{RS}} < 7$) | `mp.fp.siegelz` ou `mp.siegelz` dps=35 |
| `turing` | Validation Turing-Backlund en fin de run | `turing_validation.py` |

### Usage

```python
from chrono_phases import ChronoPhases

chrono = ChronoPhases()

# ── Dans la boucle worker ────────────────────────────────────────────────
with chrono.phase("detection"):
    Z_vals = Z_vect_correct(ts)

with chrono.phase("illinois_C"):
    gamma = affiner_illinois_c(a, b, fa, fb)

with chrono.phase("mpmath_petit_t"):
    gamma = mp.fp.findroot(mp.fp.siegelz, (a, b),
                           solver="illinois", tol=1e-12)

with chrono.phase("turing"):
    turing_ok = valider_turing(zeros, T_MAX)

# ── Rapport de fin de run ───────────────────────────────────────────────
chrono.rapport()
# → affiche : Phase | temps cumulé | appels | ms/appel | % mur×W
```

### Résultats typiques

**Run T=1 000 (4 workers, cumulé) — goulot = mpmath_petit_t :**

| Phase | Temps cumulé | Appels | ms/appel | % mur×W |
|---|---|---|---|---|
| `mpmath_petit_t` | 11.27 s | 138 | 81.65 | **35.6 %** |
| `illinois_C` | 5.22 s | 511 | 10.21 | 16.5 % |
| `turing` | 2.33 s | 1 | 2 330.99 | 7.4 % |
| `detection` | 0.09 s | 4 | 21.53 | 0.3 % |

**Run T=10 000 (4 workers, cumulé) — goulot = illinois_C :**

| Phase | Temps cumulé | Appels | ms/appel |
|---|---|---|---|
| `illinois_C` | 1 592.5 s | 10 004 | **159 ms** |
| `mpmath_petit_t` | 79.5 s | 138 | 576 ms |
| `turing` | 35.0 s | 1 | — |
| `detection` | 2.8 s | 20 | 138 ms |

> **Lecture clé :** à T=1 000, le goulot est `mpmath_petit_t` (138 zéros $t < 300$
> via `mp.siegelz` dps=35). À T=10 000, il bascule sur `illinois_C` dont le coût
> croît en $O(\sqrt{t})$ (§20 de `Formules_zeta.md`). La `detection` est
> toujours négligeable (< 0.3 %).

---
*Auteur : hprzeta — Riemann_Lab — Mise à jour : 6 juin 2026 (§15 ajouté) · 9 juin 2026 (§12 mis à jour, VALIDÉ ×27) · 10 juin 2026 (résultats runs Arb §12 : v2 terminé 68 manquants, v3 0.05/0.010 EN COURS)*
