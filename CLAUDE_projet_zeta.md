# Riemann_Lab — Instructions pour Claude
> Mis à jour : **21 mai 2026** — Phase 0 terminée ✅

---

## Projet

Plateforme de recherche sur la fonction zêta de Riemann et l'Hypothèse de Riemann (HR).
Trois axes : **numérique** (calcul des zéros), **mathématique** (théorie), **analytique** (propriétés de ζ).
Long terme : agent IA autonome de recherche mathématique (Objectif 2).

**Dépôt :** `hprzeta/Riemann_Lab` · **Mail :** `hprzeta@protomail.com`

---

## État actuel — Phase 0 TERMINÉE ✅

| Jalon | Valeur |
|---|---|
| Zéros calculés | **10 142** (T=10 000, run 20260521) |
| Méthode | Riemann-Siegel détection + Illinois affinage |
| Durée v3 | 2h46min (×7.6 vs v2 qui durait 21h) |
| Validation Turing | ✅ COMPLET — 0 zéro manquant |
| LMFDB | ✅ 19/20 zéros à < 10⁻¹⁰ |
| Prochaine étape | **Phase C** — Illinois en C/libmpfr (×5–10) |

---

## Règles de communication

- Toujours répondre en **français**
- Formules en **LaTeX** (KaTeX — voir règles critiques ci-dessous)
- Code **commenté ligne par ligne**
- Distinguer : théorème prouvé / conjecture / heuristique / intuition
- Donner la réponse directe d'abord, puis les détails

---

## ⚠️ Règles KaTeX — CRITIQUES

Le wiki GitHub et `docs/index.html` utilisent **KaTeX** (pas MathJax).

| ❌ INTERDIT | ✅ CORRECT |
|---|---|
| `\operatorname{Re}` | `\text{Re}` |
| `\operatorname{Im}` | `\text{Im}` |
| `\operatorname{...}` | `\text{...}` |

Délimiteurs : `$...$` inline · `$$...$$` display — dans le wiki ET dans `index.html`.

---

## ⚠️ Formules critiques — ne jamais se tromper

### N(T) — formule EXACTE
```
N(T) ≈ T/(2π) · ln(T/2πe)      ← le 'e' est OBLIGATOIRE
```
Sans le `e` : sous-estimation de 64% à T=100 000 (49 346 au lieu de 138 067).

### STEP adaptatif
```python
STEP = min(2 * math.pi / (5 * math.log(T_MAX / (2 * math.pi))), 0.02)
```

### θ(t) asymptotique (Stirling — valide t ≥ 20)
```
θ(t) = (t/2)·ln(t/2π) − t/2 − π/8 + 1/(48t) + 7/(5760t³) − 31/(80640t⁵)
```

### Z(t) — formule de Hardy optimisée
```
Z(t) = cos(θ)·Re[ζ(½+it)] − sin(θ)·Im[ζ(½+it)]    ← 1 seul appel zeta()
```
**NE PAS** utiliser `Re(ζ(½+it))` seul comme détecteur → faux positifs (rotation de phase).

### Illinois affinage
```python
findroot(lambda x: Z_fast(float(x), dps=35), (t_a, t_b),
         solver="illinois", tol=1e-12, maxsteps=80)
```
`tol=1e-12` cohérent avec 35 dps. `tol=1e-20` à 35 dps = IMPOSSIBLE.

### Précision adaptative (règle v3)
| Opération | dps |
|---|---|
| θ(t) asymptotique | float64 natif |
| Détection signe Z | 25 |
| Affinage Illinois | 35 |
| Validation/publication | 50 |

### Visualisation — règle absolue
```python
plt.savefig("fichier.png", dpi=150)
plt.close()    # TOUJOURS — jamais plt.show() en production (bloquant)
```

---

## Structure du projet

```
/home/riemann/projet_zeta/
├── zeta_env/                         # venv Python 3.12
├── src/calculs/optimisation/         # code production
│   ├── compute_zeros_v3.py           # orchestrateur principal ✅
│   ├── theta_rapide.py               # θ(t) Stirling
│   ├── riemann_siegel_batch.py       # Z(t) vectorisé numpy/CuPy
│   ├── parallel_scanner.py           # 4 workers multiprocessing
│   ├── turing_validation.py          # N(T) Backlund
│   └── benchmark_15min.py
├── calculs/v3_T10000_20260521_133316/  # outputs Phase 0
│   ├── zeros_v3_T10000_20260521_133316.csv   # 10 142 zéros
│   ├── zeros_v3_T10000_20260521_133316.png
│   └── execution_v3_T10000_20260521_133316.log
├── .claude/skills/zeta-lab/references/
│   ├── formules_zeta.md              # toutes les formules (enrichi 21 mai)
│   └── bibliotheques.md             # toutes les libs (enrichi 21 mai)
└── Riemann_Lab.wiki/                 # wiki cloné (branche master)

GitHub : hprzeta/Riemann_Lab
  ├── Riemann_Lab_IA    ← développement principal ⭐
  ├── Riemann_Lab_C     ← Phase C (Illinois en C)
  ├── Riemann_Lab_Test  ← expérimentations
  └── main              ← production stable
```

---

## Stack technique RÉELLE

| Lib | Usage | Note |
|---|---|---|
| `mpmath` | zêta haute précision, Illinois, loggamma | Cœur du calcul |
| `numpy` | Z(t) vectorisé, phases RS, détection signes | CPU batch |
| `cupy` | Z(t) GPU (GTX 960M, CUDA 12.2) | `cupy-cuda12x` |
| `multiprocessing` | 4 workers (pas joblib — incompatible GMP) | Fork-safe |
| `pandas` | sauvegarde/chargement CSV zéros | I/O |
| `matplotlib` | Z(t), espacements, droite critique | Visualisation |
| `loguru` | journal d'exécution | Logging |
| `tqdm` | barres de progression | Interface |

> **⚠️ Exclu :** SageMath, outils propriétaires.
> **⚠️ Ne pas utiliser joblib avec mpmath** — GMP a un état global non thread-safe → corruption mémoire.

---

## Matériel

| Composant | Valeur |
|---|---|
| CPU | Intel i7, 4 cœurs |
| RAM | 8 GB + 16 GB swap |
| GPU calcul | NVIDIA GeForce GTX 960M — 4 GB VRAM, CUDA 12.2, Compute 5.0 |
| GPU affichage | Intel HD Graphics 620 |

**Activation GPU :** `sudo prime-select nvidia && sudo reboot`
**nvtop :** lire le graphe historique du haut (fiable) — pas la colonne GPU% par processus (bursts 50ms invisibles à 2s d'échantillonnage).
**CUDA + fork :** `cudaErrorInitializationError` dans les workers = comportement attendu → bascule CPU numpy automatique.

---

## Workflow Git

```bash
# Activation environnement
source ~/projet_zeta/zeta_env/bin/activate
export PYTHONPATH="${PYTHONPATH}:${HOME}/projet_zeta/src"

# Branches
git checkout Riemann_Lab_IA    # Python, wiki, docs ⭐
git checkout Riemann_Lab_C     # Module C, libmpfr
git checkout Riemann_Lab_Test  # Tests ponctuels

# Convention commits (Conventional Commits — messages en anglais)
git commit -m "feat(phase0): ..."
git commit -m "fix(katex): ..."
git commit -m "docs(wiki): ..."

# Wiki (dépôt séparé)
cd ~/projet_zeta/Riemann_Lab.wiki/
git push origin master
```

---

## Références indispensables

- **`handoff.md`** dans le wiki — état complet du projet session par session
- **`.claude/skills/zeta-lab/references/formules_zeta.md`** — toutes les formules
- **`.claude/skills/zeta-lab/references/bibliotheques.md`** — toutes les libs
- LMFDB : https://lmfdb.org/zeros/zeta/
- Titchmarsh §4.12 : https://sites.math.rutgers.edu/~zeilberg/EM18/TitchmarshZeta.pdf
- Turing 1953 : https://www-users.cse.umn.edu/~odlyzko/doc/turing.zeta.pdf
- Odlyzko & Schönhage (1988) : https://www-users.cse.umn.edu/~odlyzko/doc/arch/fast.zeta.eval.pdf

---

## Prochaines priorités

1. **Phase C** — `illinois_mpfr.c` + Makefile → `.so` → ctypes Python (×5–10 sur l'affinage)
   ```bash
   sudo apt install libmpfr-dev libgmp-dev
   ```
2. Fix lien PDF cassé dans le wiki + `git push origin master`
3. Objectif 2 — Agent IA : Claude Code 101 → MCP → Subagents (Anthropic Skilljar)

---
*Dernière mise à jour : 22 mai 2026 — 208 lignes*
