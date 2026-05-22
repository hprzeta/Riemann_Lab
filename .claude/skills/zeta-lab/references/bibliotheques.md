# Bibliothèques Python — Référence Zeta-Lab
> Version enrichie — Projet Riemann_Lab · hprzeta
> Mise à jour : 2026 — intègre tous les patterns de compute_zeros_v3.py

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

## 12. Tableau récapitulatif — rôle par bibliothèque

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

---
*Dernière mise à jour : 22 mai 2026 — 349 lignes*
