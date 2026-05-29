# Riemann_Lab — Instructions pour Claude
> Mis à jour : **29 mai 2026** — Phase C Voie B validée ✅

---

## Projet

Plateforme de recherche sur la fonction zêta de Riemann et l'Hypothèse de Riemann (HR).
Trois axes : **numérique** (calcul des zéros), **mathématique** (théorie), **analytique** (propriétés de ζ).
Long terme : agent IA autonome de recherche mathématique (Objectif 2).

**Dépôt :** `hprzeta/Riemann_Lab` · **Mail :** `hprzeta@protomail.com`

---

## État actuel — Phase C Voie B validée ✅

| Jalon | Valeur |
|---|---|
| Zéros calculés | **10 142** (T=10 000, run 20260521) |
| Méthode | Riemann-Siegel détection + Illinois affinage |
| Durée v3 | 2h46min (×7.6 vs v2 qui durait 21h) |
| Validation Turing | ✅ COMPLET — 0 zéro manquant |
| LMFDB | ✅ 19/20 zéros à < 10⁻¹⁰ |
| Phase C Voie B | ✅ `compute_zeros_v5.py` — Illinois_C pur 100% |
| Commit voie B | `b8018c0` — poussé sur `Riemann_Lab_C` |
| Branche active | `Riemann_Lab_C` |

### Fichiers Phase C validés (commit b8018c0)
- `compute_zeros_v5.py` — orchestrateur v5, wrapper mpmath.siegelz
- `illinois_mpfr.c/.h` — modifiés, callback Python/C `illinois_mpfr_cb`
- `illinois_pyZ.py` — wrapper Python pour Z_mpfr via mpmath.siegelz
- `test_illinois_v5.py` — validation Voie B (20/20 convergences)
- `docs/phase_c_voie_b_v5_plan.md` — rapport livrable

### Résultats validés Voie B
```
Run T=80  : Illinois_C pur 100%, Turing COMPLET, LMFDB 19/20, 25.8s
Run T=300 : Illinois_C pur 100%, Turing COMPLET, LMFDB 19/20, 138/138 zéros
biais Z   : < 1e-13 (vs ~9e-3 avant voie B)
```

### Goulot identifié
`mpmath.siegelz` en détection séquentielle → ~311ms/pas pour t > 3000.
Run T=650 complet ~30 min. → Résolu par v4.1 (Z_batch vectorisé).

---

## 🤖 Gestion autonome du contexte — RÈGLES OBLIGATOIRES

Claude Code surveille en permanence le pourcentage affiché en bas :
`XX% · YYmin restantes · ZZ% until auto-compact`

| Seuil | Action automatique SANS attendre d'instruction |
|---|---|
| **50%** | `git add -A && git commit -m "wip: checkpoint auto [description]"` |
| **70%** | `git push origin [branche]` + créer `docs/session_checkpoint_YYYYMMDD.md` |
| **80%** | Arrêt complet — ne plus lancer de nouvelles tâches |
| **"11% until auto-compact"** | STOP immédiat — push + rapport court + exit |

### Règle auto-compact
**Auto-compact** = Claude Code résume automatiquement l'historique quand le contexte
est plein. Ce résumé est imparfait → risque d'oublier des contraintes ou répéter du travail.
→ Toujours committer et pousser AVANT d'atteindre auto-compact.

### Règle des runs longs
- Ne jamais lancer un run > T=300 si le contexte dépasse 40%
- Ne jamais lancer T=10000 dans la même session qu'un gros développement
- Préférer plusieurs petites sessions plutôt qu'une longue session à risque

### Checkpoint automatique (format)
```bash
git add -A
git commit -m "wip: checkpoint auto $(date +%H%M) — [ce qui est fait]"
git push origin Riemann_Lab_C
```
Puis créer `docs/session_checkpoint_YYYYMMDD_HHMM.md` :
- ce qui est fait
- ce qui reste à faire
- commande exacte pour reprendre

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

### Seuil Illinois C (voie B)
```python
T_SEUIL_ILLINOIS_C = 300.0
# t < 300  → N < 7 termes RS → mpmath fallback légitime (~87 zéros sur 10142)
# t ≥ 300  → N ≥ 7 termes RS → Illinois C pur fiable
```

### Z_mpfr — leçon voie B (29 mai 2026)
Le biais Z_mpfr (~1e-3) n'est PAS un bug de code — c'est une limitation RS :
RS tronqué à C0+C1 → précision max ~1e-3. Solution : wrapper mpmath.siegelz.
`mpc_zeta` est ABSENT dans libmpc 1.3.1 — ne pas chercher à l'utiliser.

---

## Structure du projet

```
/home/riemann/projet_zeta/
├── zeta_env/                         # venv Python 3.12
├── src/calculs/optimisation/         # code production
│   ├── compute_zeros_v3.py           # orchestrateur Phase 0 ✅
│   ├── compute_zeros_v4.py           # Phase C hybride ✅ (NE PAS MODIFIER)
│   ├── compute_zeros_v5.py           # Phase C Voie B ✅ (Illinois_C pur 100%)
│   ├── theta_rapide.py               # θ(t) Stirling
│   ├── riemann_siegel_batch.py       # Z(t) vectorisé numpy/CuPy
│   ├── parallel_scanner.py           # 4 workers multiprocessing
│   ├── turing_validation.py          # N(T) Backlund
│   └── c_modules/                    # Phase C
│       ├── illinois_mpfr.c           # Illinois en libmpfr PREC=170 ✅
│       ├── illinois_mpfr.h
│       ├── illinois_mpfr.so          # compilé ✅
│       ├── illinois_pyZ.py           # wrapper Python Z_mpfr → mpmath ✅
│       ├── z_function.c              # θ(t) + Z(t) en double
│       ├── z_function.h
│       ├── test_illinois_v5.py       # validation Voie B 20/20 ✅
│       ├── Makefile
│       └── CLAUDE.md                 # règles C locales
├── src/ia/prompts/                   # prompts Claude Code
│   ├── prompt_claude_code_phase_c_voie_b_v5.md
│   └── PROMPT_CLAUDE_CODE_V4_INTEGRATION.md
├── docs/
│   ├── phase_c_voie_b_v5_plan.md    # rapport Voie B ✅
│   └── handoff/Handoff.md           # état projet (aussi dans wiki)
├── .mcp.json                         # MCP GitHub connecté
├── CLAUDE.md                         # ce fichier ⭐
└── Riemann_Lab.wiki/                 # wiki cloné (branche master)
```

---

## Stack technique

| Lib | Usage | Note |
|---|---|---|
| `mpmath` | zêta haute précision, Illinois, loggamma | Cœur du calcul |
| `numpy` | Z(t) vectorisé, phases RS, détection signes | CPU batch |
| `cupy` | Z(t) GPU (GTX 960M, CUDA 12.2) | `cupy-cuda12x` |
| `multiprocessing` | 4 workers (pas joblib) | Fork-safe |
| `libmpfr` | PREC=170 bits dans illinois_mpfr.c | Phase C |
| `libmpc` | installé v1.3.1 — `mpc_zeta` ABSENT | Ne pas utiliser |

> **⚠️ Exclu :** SageMath, outils propriétaires.
> **⚠️ Ne pas utiliser joblib avec mpmath** — GMP non thread-safe.
> **⚠️ mpc_zeta absent** dans libmpc 1.3.1 — utiliser wrapper mpmath.

---

## Matériel

| Composant | Valeur |
|---|---|
| CPU | Intel i7, 4 cœurs |
| RAM | 8 GB + 16 GB swap |
| GPU | NVIDIA GTX 960M — 4 GB VRAM, CUDA 12.2 |

**Activation GPU :** `sudo prime-select nvidia && sudo reboot`

---

## Workflow Git

```bash
source ~/projet_zeta/zeta_env/bin/activate
export PYTHONPATH="${PYTHONPATH}:${HOME}/projet_zeta/src"

# Branches
git checkout Riemann_Lab_IA    # Python, wiki, docs ⭐
git checkout Riemann_Lab_C     # Phase C (Illinois en C) ← ACTIF

# Wiki (dépôt séparé — TOUS les .md vont ici)
cd ~/projet_zeta/Riemann_Lab.wiki/
git push origin master

# Convention commits
git commit -m "feat(phase-c): ..."
git commit -m "fix(z_function): ..."
git commit -m "docs(handoff): ..."
git commit -m "wip: checkpoint auto HHMM — [description]"
```

⚠️ **Handoff.md ne va JAMAIS dans le repo principal** — wiki uniquement.

---

## Fichiers de contexte complémentaires

- `src/calculs/optimisation/CLAUDE.md` — règles Illinois, ctypes, précision
- `src/calculs/optimisation/c_modules/CLAUDE.md` — PREC=170, libmpfr, Makefile
- `Riemann_Lab.wiki/Handoff.md` — état complet session par session ⭐
- `Riemann_Lab.wiki/Bonnes-Pratiques-Claude-Code.md` — guide gestion tokens

---

## Références

- LMFDB : https://lmfdb.org/zeros/zeta/
- Titchmarsh §4.12 : https://sites.math.rutgers.edu/~zeilberg/EM18/TitchmarshZeta.pdf
- Turing 1953 : https://www-users.cse.umn.edu/~odlyzko/doc/turing.zeta.pdf

---

## Prochaines priorités

1. **v4.1** — combiner Z_batch (détection) + illinois_mpfr_cb (affinage) + 4 workers
   - Prompt : `src/ia/prompts/PROMPT_CLAUDE_CODE_V4_INTEGRATION.md`
   - Objectif : > 5 z/s (vs ~1 z/s en v5 séquentiel)
2. **Run T=650** avec v4.1 → puis T=1000 → puis T=10000
3. **Rapport v3→v4** — `.md` + PDF via `pdflatex`
4. Fix lien PDF cassé dans le wiki + `git push origin master`
5. **Objectif 2** — Agent IA : MCP + Subagents

---
*Dernière mise à jour : 29 mai 2026 — 284 lignes*
