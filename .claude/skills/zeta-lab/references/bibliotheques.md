# Bibliothèques Python — Référence Zeta-Lab

## mpmath — Arithmétique haute précision

```python
from mpmath import mp, zeta, zetazero, siegelz, siegeltheta, gamma, log

mp.dps = 50  # 50 décimales (standard projet)

# Évaluation directe
zeta(2)                    # π²/6
zeta(0.5 + 14.1347j)      # proche de 0 (premier zéro)

# Zéros via zetazero (lent mais précis)
zetazero(1)               # 0.5 + 14.1347...j
zetazero(10)              # 0.5 + 49.7738...j

# Fonction Z de Hardy
siegelz(14.1347)          # ≈ 0
siegeltheta(14.1347)      # θ(t)
```

## sympy — Calcul symbolique

```python
from sympy import zeta, gamma, pi, I, re, im, simplify
from sympy.ntheory import primerange, isprime, nextprime

# Symbolique
s = Symbol('s')
zeta(s)                   # objet symbolique

# Nombres premiers
list(primerange(1, 100))  # premiers jusqu'à 100
nextprime(100)            # 101
```

## numpy / scipy — Calcul numérique

```python
import numpy as np
from scipy import special, optimize

# Détection de zéros (moins précis que mpmath)
# Utiliser pour exploration rapide seulement
```

## matplotlib — Visualisation 2D

```python
import matplotlib.pyplot as plt

# Graphique standard
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(t_values, z_values)
ax.set_xlabel("t")
ax.set_ylabel("Z(t)")
plt.savefig("/mnt/data/exports/figures/nom.png", dpi=150)
plt.close()
```

## plotly — Visualisation 3D interactive

```python
import plotly.graph_objects as go

fig = go.Figure(data=go.Surface(z=Z_matrix, x=Re_vals, y=Im_vals))
fig.write_html("/mnt/data/exports/csv/nom.html")
```

## loguru — Logging

```python
from loguru import logger
from pathlib import Path

logger.add(
    Path("/mnt/data/logs/projet_zeta.log"),
    rotation="100 MB",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
logger.info("Calcul démarré")
logger.success(f"Zéro trouvé : t = {t:.15f}")
```

## tqdm — Barres de progression

```python
from tqdm import tqdm

for t in tqdm(np.arange(10, T_MAX, STEP), desc="Recherche zéros"):
    # calcul...
```

## Activation de l'environnement

```bash
source ~/projet_zeta/zeta_env/bin/activate
export PYTHONPATH="${PYTHONPATH}:${HOME}/projet_zeta/src"
python mon_script.py
```
