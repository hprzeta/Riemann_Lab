# ~/projet_zeta/CLAUDE.md — Contexte projet Riemann_Lab
> Configuration projet Claude Code — règles **stables** uniquement.
> Mis à jour : 31 mai 2026

---

## ⚠️ Principe de ce fichier

Ce `CLAUDE.md` ne contient **que des règles permanentes** (langue, formules, conventions,
sécurité). **Aucun état de session ici.** L'état courant, l'historique et la stack vivent dans :

| Fichier | Rôle |
|---|---|
| `Riemann_Lab.wiki/Handoff.md` | ⭐ État courant + prochaine action (lu à chaque reprise) |
| `Riemann_Lab.wiki/JOURNAL.md` | Historique daté (append-only, non lu par défaut) |
| `Riemann_Lab.wiki/STACK.md` | Branches, matériel, outils, roadmap |

> En début de session : **lire `Handoff.md`**, pas ce fichier (chargé automatiquement).
> Ne jamais recopier l'état du Handoff ici.

---

## Projet

Plateforme de recherche sur la fonction zêta de Riemann et l'Hypothèse de Riemann (HR).
Trois axes : **numérique** (calcul des zéros), **mathématique** (théorie), **analytique**.
Long terme (Objectif 2) : agent IA autonome de recherche mathématique.

**Dépôt :** `hprzeta/Riemann_Lab` · **Mail :** `hprzeta@protonmail.com`

---

## 🤖 Gestion autonome du contexte — RÈGLES OBLIGATOIRES

Surveiller en permanence le pourcentage affiché en bas :
`XX% · YYmin restantes · ZZ% until auto-compact`

| Seuil | Action automatique SANS attendre d'instruction |
|---|---|
| **50 %** | `git add -A && git commit -m "wip: checkpoint auto [description]"` |
| **70 %** | `git push origin [branche]` + créer `docs/session_checkpoint_YYYYMMDD.md` |
| **80 %** | Arrêt complet — ne plus lancer de nouvelles tâches |
| **"11 % until auto-compact"** | STOP immédiat — push + rapport court + exit |

**Auto-compact** = résumé automatique de l'historique quand le contexte est plein.
Imparfait → risque d'oublier des contraintes. Toujours committer/pousser AVANT.

**Runs longs :** jamais T>300 si contexte > 40 % · jamais T=10000 dans une session de dév ·
préférer plusieurs petites sessions à une longue.

---

## Règles de communication

- Toujours répondre en **français**
- Formules en **LaTeX** (KaTeX — voir ci-dessous)
- Code **commenté ligne par ligne**
- Distinguer : théorème prouvé / conjecture / heuristique / intuition
- Réponse directe d'abord, puis détails

---

## ⚠️ Règles KaTeX — CRITIQUES

Le wiki GitHub et `docs/index.html` utilisent **KaTeX** (pas MathJax).

| ❌ INTERDIT | ✅ CORRECT |
|---|---|
| `\operatorname{Re}` | `\text{Re}` |
| `\operatorname{Im}` | `\text{Im}` |
| `\operatorname{...}` | `\text{...}` |

Délimiteurs : `$...$` inline · `$$...$$` display — wiki ET `index.html`.

---

## ⚠️ Formules critiques — SOURCE CANONIQUE (ne jamais se tromper)

> Ces formules sont la **référence unique** du projet. Les fichiers `CLAUDE.md` locaux
> (optimisation, c_modules) pointent ici plutôt que de les recopier.

### N(T) — Riemann-von Mangoldt (EXACTE)
```
N(T) ≈ T/(2π) · ln(T/2πe)      ← le 'e' dans 2πe est OBLIGATOIRE
```
Sans le `e` : sous-estimation de 64 % à T=100 000 (49 346 au lieu de 138 067).

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

### Illinois — affinage (sécante modifiée)
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

### Seuil Illinois C (voie B)
```python
T_SEUIL_ILLINOIS_C = 300.0
# t < 300  → N < 7 termes RS → mpmath fallback légitime (~87 zéros sur 10142)
# t ≥ 300  → N ≥ 7 termes RS → Illinois C pur fiable
```

### Visualisation — règle absolue
```python
plt.savefig("fichier.png", dpi=150)
plt.close()    # TOUJOURS — jamais plt.show() en production (bloquant)
```

### Leçon durable — biais Z_mpfr (voie B)
Le biais Z_mpfr (~1e-3) **n'est pas un bug** : limitation structurelle de RS tronquée à
C0+C1 (précision max ~1e-3). Solution : wrapper `mpmath.siegelz`.
`mpc_zeta` est **ABSENT** de libmpc 1.3.1 — ne pas chercher à l'utiliser.

---

## Structure du projet

```
~/projet_zeta/
├── zeta_env/                         # venv Python 3.12
├── src/calculs/optimisation/         # code production
│   ├── compute_zeros_v2.py           # référence (21h) — NE PAS MODIFIER
│   ├── compute_zeros_v3.py           # orchestrateur Phase 0
│   ├── compute_zeros_v4.py           # Phase C hybride — NE PAS MODIFIER
│   ├── compute_zeros_v5.py           # Voie B — Illinois_C pur 100% — NE PAS MODIFIER
│   ├── compute_zeros_v4_1.py         # détection Z_vect_correct + 4 workers (actif)
│   ├── theta_rapide.py · riemann_siegel.py · riemann_siegel_batch.py
│   ├── parallel_scanner.py · turing_validation.py
│   └── c_modules/                    # Phase C (libmpfr) — voir son CLAUDE.md
├── src/ia/prompts/                   # prompts Claude Code
├── docs/                             # GitHub Pages + rapports
├── .mcp.json                         # MCP GitHub — JAMAIS commité (.gitignore)
├── CLAUDE.md                         # ce fichier ⭐
└── Riemann_Lab.wiki/                 # wiki cloné (master) — Handoff/JOURNAL/STACK
```

---

## Stack technique

| Lib | Usage | Note |
|---|---|---|
| `mpmath` | zêta haute précision, Illinois, loggamma | Cœur du calcul |
| `numpy` | Z(t) vectorisé, détection signes | CPU batch |
| `cupy` | Z(t) GPU (GTX 960M, CUDA 12.2) | `cupy-cuda12x` |
| `multiprocessing` | 4 workers (pas joblib) | Fork-safe |
| `libmpfr` | PREC=170 bits dans illinois_mpfr.c | Phase C |
| `libmpc` | v1.3.1 — `mpc_zeta` ABSENT | Ne pas utiliser |

> **Exclu :** SageMath, outils propriétaires. · **Pas de `joblib` avec `mpmath`** (GMP non
> thread-safe). · **`mpc_zeta` absent** dans libmpc 1.3.1 → wrapper mpmath.

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

git checkout Riemann_Lab_IA    # Python, wiki, docs ⭐
git checkout Riemann_Lab_C     # Phase C (Illinois en C)

# Wiki (dépôt séparé — TOUS les .md de suivi vont ici)
cd ~/projet_zeta/Riemann_Lab.wiki/ && git push origin master

# Conventions commits
# feat(phase-c): ... · fix(z_function): ... · docs(handoff): ... · wip: checkpoint auto HHMM
```

⚠️ **Handoff/JOURNAL/STACK vont dans le wiki, jamais dans le repo de code.**
⚠️ **Les `CLAUDE.md`, eux, vivent AVEC le code** (repo `Riemann_Lab_*`), pas dans le wiki.
⚠️ **Avant tout `git add -A` : `git status` + `grep mcp .gitignore`.**

---

## Fichiers de contexte (cascade Claude Code)

| Fichier | Portée |
|---|---|
| `~/.claude/CLAUDE.md` | Global léger — tous projets (local only) |
| `~/projet_zeta/CLAUDE.md` | ⭐ Ce fichier — contexte projet |
| `src/calculs/optimisation/CLAUDE.md` | Règles Illinois, ctypes, précision |
| `src/calculs/optimisation/c_modules/CLAUDE.md` | C : PREC=170, libmpfr, Makefile |

---

## Références

- LMFDB : https://lmfdb.org/zeros/zeta/
- Titchmarsh §4.12 · Turing 1953 · Odlyzko-Schönhage 1988 (liens dans `STACK.md`)

---

## Prochaines priorités

> 📍 **Voir `Handoff.md` → section « REPRENDRE ICI ».** Ne pas dupliquer la liste ici
> (elle change à chaque session ; ce fichier doit rester stable).

---
*Dernière mise à jour : 31 mai 2026 — ~205 lignes (état purgé → Handoff.md)*
