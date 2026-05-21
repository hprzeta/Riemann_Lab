---
name: zeta-lab
description: >
  Laboratoire zêta de Riemann — exploration numérique, symbolique et graphique
  de ζ(s) et de l'Hypothèse de Riemann. Se déclenche sur : "calcule les zéros",
  "trace zeta", "vérifie cette formule", "fonction Z de Hardy", "espacement des
  zéros", "PRNG zêta", "hypothèse de Riemann", "zêta de Riemann", "HR", "ζ(",
  "Z(t)", "θ(t)", "Riemann-Siegel", "LMFDB", "nombres premiers",
  "compute_zeros", "Illinois", "Turing-Backlund", "N(T)", "Phase C", "libmpfr",
  "batch_gpu", "batch_cpu", "CuPy", "affinage", "zéros non-triviaux".
version: 0.2.0
date: 2026-05-19
---

# Zeta-Lab — Laboratoire Riemann (v0.2.0)

## État d'avancement au 19 mai 2026

| Étape | Statut | Résultat |
|---|---|---|
| v1 — mpmath.zetazero() | ✅ Terminé | Preuve de concept |
| v2 — Hardy-Z + Illinois 50 dps | ✅ Terminé | **10 142 zéros en 21h** |
| v3 — RS + parallèle + Turing | ✅ Opérationnel | ~3.59 z/s (×5.3 vs v2) |
| GPU GTX 960M — CuPy | ✅ Activé | bursts 30–50% (détection) |
| Phase C — Illinois en C/libmpfr | 🔜 En cours | branche `Riemann_Lab_C` |

## Contexte du projet

```
Chercheur  : hprzeta
GitHub     : https://github.com/hprzeta/Riemann_Lab
Branche    : Riemann_Lab_IA (Python) | Riemann_Lab_C (C/libmpfr)
Dossier    : ~/projet_zeta/src/calculs/optimisation/
Wiki       : ~/projet_zeta/Riemann_Lab.wiki/ (branche master)
Python     : ~/projet_zeta/zeta_env/ (Python 3.12)
Objectif   : 10 000 zéros non-triviaux de ζ(s) sur Re(s) = ½, puis HdR
```

## Règles de réponse

- Toujours en **français**
- Adapter le niveau : expliquer depuis la base, monter en complexité
- Code Python exécutable et testé ; commentaires en français
- Vérifier les résultats contre **LMFDB** quand possible
- Signaler si un résultat est potentiellement un faux positif / erreur numérique
- Pour le wiki : **KaTeX uniquement** — `\text{Re}` et non `\operatorname{Re}`
- Rapports de transition vN→vN+1 : format `.md` + PDF via `pdflatex`

## Stack technique

```
Python 3.12 — numpy, mpmath, scipy, matplotlib, loguru, tqdm, pandas
GPU         — NVIDIA GTX 960M, 4 GB VRAM, CUDA 12.2 / Compute 5.0, CuPy cupy-cuda12x
LLM locaux  — Ollama sur /mnt/data : mathstral, deepseek-coder, qwen3:4b
Env vars    — OLLAMA_MODELS=/mnt/data/ollama, OLLAMA_CUDA=1
```

## Architecture v3 — modules opérationnels

| Module | Rôle | Gain |
|---|---|---|
| `theta_rapide.py` | θ(t) via Stirling asymptotique | ×10 vs loggamma |
| `riemann_siegel.py` | Z(t) formule RS | ×50 vs mpmath.zeta |
| `riemann_siegel_batch.py` | Z(t) vectorisé NumPy/CuPy, fallback 3 niveaux | batch |
| `parallel_scanner.py` | Multiprocessing.Pool, 4 workers | ×4 |
| `turing_validation.py` | N(T) Turing-Backlund, complétude | validation |
| `benchmark_15min.py` | bench `--mode cpu/batch_cpu/batch_gpu` | mesure |
| `compute_zeros_v3.py` | Orchestrateur principal | intégration |

## Benchmarks (16 mai 2026 — séquentiel, après reboot NVIDIA)

| Mode | Zéros / 15 min | Vitesse | Gain vs CPU scalaire |
|---|---|---|---|
| CPU scalaire | ~604 | 0.67 z/s | référence |
| **BATCH_CPU** | **3 231** | **3.59 z/s** | **×5.3** |
| BATCH_GPU | 3 051 | 3.39 z/s | ×5.1 |

**Goulot d'étranglement :** Illinois en mpmath = 80–90% du temps total.
La GPU n'accélère que la détection Z(t) (10–20%). → Phase C : porter Illinois en C/libmpfr.

## Formules critiques — NE JAMAIS SE TROMPER

### N(T) — formule exacte de Riemann-von Mangoldt
```
N(T) = T/(2π) · ln(T/2πe)    ← le 'e' est OBLIGATOIRE
```
Sans `e` : erreur −28% à T=10 000, −64% à T=100 000.

### STEP sécurisé (évite les zéros manquants)
```
STEP = min(2π / (5·ln(T_max/2π)), 0.10)
```

### Formule de Riemann-Siegel
```
Z(t) = 2·Σ_{n=1}^{N} cos(θ(t) − t·ln n) / √n + R(t),   N = ⌊√(t/2π)⌋
```

### θ(t) asymptotique (Stirling)
```
θ(t) = (t/2)·ln(t/2π) − t/2 − π/8 + 1/(48t) + 7/(5760t³) + O(t⁻⁵)
```

### Précision adaptative
```
Détection     : 0 dps (float64 NumPy)
Z_fast(t)     : 35 dps (mpmath)
Illinois final : 50 dps (mpmath)
```

## Données de référence — 10 premiers zéros

| n | γ_n (LMFDB) | γ_n calculé (v2/v3) | Écart |
|---|---|---|---|
| 1 | 14.134725141734693 | 14.134725141734693 | < 1e-14 |
| 2 | 21.022039638771555 | 21.022039638771556 | < 1e-14 |
| 3 | 25.010857580145688 | 25.010857580145688 | < 1e-14 |
| 4 | 30.424876125859513 | 30.424876125859512 | < 1e-14 |

**Résultat principal :** 10 142 zéros jusqu'à T=9 998.85, méthode Hardy-Z + Illinois, 50 dps.

## Workflow standard

### Calcul des zéros
```bash
cd ~/projet_zeta/src/calculs/optimisation/
source ~/projet_zeta/zeta_env/bin/activate
python compute_zeros_v3.py --tmax 10000 --mode batch_cpu
```

### Validation Turing-Backlund
```python
from turing_validation import valider_turing, N_attendu
N_th = N_attendu(T)  # N(T) = T/(2π)·ln(T/2πe)
rapport = valider_turing(zeros_trouves, T)
# Vérifier : delta = N_th - len(zeros) → MANQUE si delta>0, SURPLUS si delta<0
```

### Rapport de transition
Avant chaque version vN→vN+1 : générer `.md` + PDF `pdflatex` avec structure :
- Date, titre "Analyse des problèmes vN→vN+1"
- Par problème : cause mathématique + formules + tableaux + solution
- Tableau récapitulatif global
- Section "Questions ouvertes"

## Bibliothèques

```python
# Calcul de précision
from mpmath import mp, zeta, siegeltheta, siegelz, zetazero
mp.dps = 50  # 50 décimales

# Vectorisation
import numpy as np
import cupy as cp  # GPU — vérifier cp.cuda.is_available()

# Modules projet
from theta_rapide import theta_fast, Z_fast
from riemann_siegel_batch import Z_batch
from turing_validation import valider_turing, N_attendu
from parallel_scanner import calculer_zeros_parallele
```

## KaTeX (wiki GitHub)

```
❌ \operatorname{Re}   →   ✅ \text{Re}
❌ \operatorname{Im}   →   ✅ \text{Im}
```
Délimiteurs : `$...$` inline, `$$...$$` display — partout dans le wiki et index.html.

## Références

| Ressource | Lien |
|---|---|
| Site projet | https://hprzeta.github.io/Riemann_Lab/ |
| LMFDB (zéros) | https://lmfdb.org/zeros/zeta/ |
| Odlyzko & Schönhage 1988 | https://doi.org/10.1090/S0002-9947-1988-0936813-0 |
| Turing 1953 | https://doi.org/10.1112/plms/s3-3.1.99 |
| Titchmarsh — Theory of ζ | https://archive.org/details/theoryofriemann00titc |
| Rapport PDF v2→v3 | `pdf/optimisation/analyse_problemes_v2_v3_phase0_20260511-5.pdf` |
