# Phase Optimisation — `compute_zeros_v3.py`

> **Lien parent :** [Étape 1 – Calcul des zéros non triviaux](Etape-1-Calcul-des-zéros-non-triviaux)  
> **Rapport PDF complet :** [`analyse_problemes_v2_v3_phase0.pdf`](https://raw.githubusercontent.com/hprzeta/Riemann_Lab/Riemann_Lab_IA/pdf/optimisation/analyse_problemes_v2_v3_phase0.pdf)  
> **Date :** 11–22 mai 2026  
> **Statut :** ✅ Terminée — référence historique · Phase C (v7→v9) active

---

## Sommaire

1. [Contexte — pourquoi optimiser](#1-contexte)
2. [10 problèmes identifiés et résolus](#2-problèmes-résolus)
3. [Architecture v3 — 5 fichiers](#3-architecture-v3)
4. [Gains mesurés](#4-gains-mesurés)
5. [Benchmarks de performance 15 min](#5-benchmarks-15-min)
6. [GPU GTX 960M — intégration CuPy](#6-gpu-gtx-960m)
7. [Fichiers générés](#7-fichiers-générés)
8. [Prochaines étapes](#8-prochaines-étapes)

---

## 1. Contexte

La v2 (`compute_zeros_v2.py`) calculait 10 142 zéros en **21 heures** — purement séquentielle, sans parallélisme, avec appels répétés à `mpmath.zeta()`. L'objectif de cette phase est de ramener ce temps à moins de 1 heure pour T=10 000, et de préparer le passage à T=100 000+.

**Entrée :** `compute_zeros_v2.py` — 21h pour 10 142 zéros  
**Sortie :** `compute_zeros_v3.py` — objectif < 30 min, Turing-Backlund validé

---

## 2. Problèmes résolus

| # | Problème | Gravité | Fichier | Statut |
|---|---|---|---|---|
| 1 | Durée 21h — mpmath.zeta() pour chaque t | 🔴 Haute | `riemann_siegel.py` | ✅ |
| 2 | θ(t) lent via `loggamma` | 🔴 Haute | `theta_rapide.py` | ✅ |
| 3 | Dépendance totale à `mpmath.zeta()` | 🟡 Moyenne | `riemann_siegel.py` | ✅ |
| 4 | Pas de validation Turing-Backlund | 🔴 Haute | `turing_validation.py` | ✅ |
| 5 | Pas de calcul parallèle | 🟡 Moyenne | `parallel_scanner.py` | ✅ |
| 6 | Précision 50 dps fixe pour tout | 🟡 Moyenne | `compute_zeros_v3.py` | ✅ |
| 7 | Double appel `zeta()` redondant | 🟡 Moyenne | `compute_zeros_v3.py` | ✅ |
| 8 | STEP trop grand → zéros manquants | 🔴 Haute | `compute_zeros_v3.py` | ✅ |
| 9 | `plt.show()` bloquant → log non généré | 🟢 Faible | `compute_zeros_v3.py` | ✅ |
| 10 | Bug affichage Turing (surplus ≠ manque) | 🟡 Moyenne | `turing_validation.py` | ✅ |

### Corrections mathématiques clés

**Formule de Riemann-Siegel** (remplace mpmath.zeta) :

$$Z(t) = 2\sum_{n=1}^{N} \frac{\cos(\theta(t) - t\ln n)}{\sqrt{n}} + R(t) \quad \text{avec } N = \left\lfloor\sqrt{\frac{t}{2\pi}}\right\rfloor$$

**θ(t) asymptotique** (remplace loggamma) :

$$\theta(t) = \frac{t}{2}\ln\frac{t}{2\pi} - \frac{t}{2} - \frac{\pi}{8} + \frac{1}{48t} + \frac{7}{5760t^3} + O(t^{-5})$$

**STEP sécurisé** :

$$\text{STEP} = \min\!\left(\frac{2\pi}{5\ln(T_{\max}/2\pi)},\ 0.10\right)$$

**Validation Turing — formule de Riemann–von Mangoldt** :

$$N(T) = \frac{\theta(T)}{\pi} + 1 + S(T) \quad \text{avec } S(T) = \frac{1}{\pi}\arg\zeta\!\left(\tfrac{1}{2}+iT\right)$$

---

## 3. Architecture v3

```
src/calculs/optimisation/
├── theta_rapide.py          # θ(t) asymptotique        — ×10 vs loggamma
├── riemann_siegel.py        # Z(t) formule RS           — ×50 vs mpmath.zeta
├── turing_validation.py     # N(T) Backlund             — complétude garantie
├── parallel_scanner.py      # 4 workers multiprocessing — ×4 parallèle
├── riemann_siegel_batch.py  # Z(t) vectorisé numpy/GPU  — ×7 à ×15
├── compute_zeros_v3.py      # Orchestrateur principal
└── benchmark_15min.py       # Comparaison CPU/batch/GPU
```

**Outputs générés par chaque run :**
```
calculs/v3_T{TMAX}_{date}/
├── zeros_v3_T{TMAX}_{date}.csv      # zéros trouvés
├── zeros_v3_T{TMAX}_{date}.png      # 3 graphiques
└── execution_v3_T{TMAX}_{date}.log  # journal complet
```

---

## 4. Gains mesurés

### T=1000, 4 workers

| Métrique | v2 | v3 | Gain |
|---|---|---|---|
| Durée | ~2h | 6.8 min | **×17** |
| Vitesse | 0.1 z/s | 1.6 z/s | **×16** |
| Validation Turing | ❌ absente | ✅ N(T) Backlund | — |
| Fichier log | ❌ absent | ✅ généré | — |
| LMFDB vérifié | 10 zéros | 20 zéros | ×2 |

### Correction importante — N(T) exact

La formule de Weyl exacte :

$$N(T) = \frac{T}{2\pi}\ln\frac{T}{2\pi e}$$

| T | N(T) correct | N(T) erroné (sans e) | Erreur |
|---|---|---|---|
| 1 000 | 649 | ~420 | -35% |
| 10 000 | 10 142 | ~7 300 | -28% |
| 100 000 | **138 067** | ~49 346 | **-64%** |

> ⚠️ Une estimation initiale incorrecte de N(100 000) = 49 346 (au lieu de 138 067) avait conduit à prévoir ~10h pour T=100 000. Le temps réel est **20–40h** sans batch.

---

## 5. Benchmarks de performance 15 min

### Usage du script

```bash
python benchmark_15min.py --mode cpu       --tmax 10000 --duree 15
python benchmark_15min.py --mode batch_cpu --tmax 10000 --duree 15
python benchmark_15min.py --mode batch_gpu --tmax 10000 --duree 15
```

### Résultats — T=2 500, tests concurrents (3 terminaux) — 13 mai 2026

| Mode | Zéros | Vitesse | Évals | Note |
|---|---|---|---|---|
| CPU scalaire | 636 | 0.705 z/s | 9 696 | Gagnant — N trop petit |
| BATCH_CPU | 567 | 0.630 z/s | 15 003 | Contention BLAS |
| BATCH_GPU | 571 | 0.634 z/s | 15 003 | GPU inactive (CuPy cassé) |

### Résultats — T=10 000, tests concurrents — 13 mai 2026

| Mode | Zéros | Vitesse | Évals | t atteint |
|---|---|---|---|---|
| CPU scalaire | 604 | 0.671 z/s | 9 302 | 944 |
| BATCH_CPU | 540 | 0.599 z/s | 15 003 | 1 041 |
| BATCH_GPU | 542 | 0.602 z/s | 15 003 | 1 044 |

> ⚠️ Tests concurrents biaisés — 3 processus se battent pour les 4 cœurs. Facteur de contention mesuré : **×2.1**

### ✅ Résultats finaux — T=10 000, tests séquentiels — 16 mai 2026

> Tests propres après reboot NVIDIA (`sudo prime-select nvidia`), un seul mode à la fois.

| Mode | Zéros | Vitesse | Évals | t atteint | Gain vs CPU |
|---|---|---|---|---|---|
| CPU scalaire (réf.) | ~604 | ~0.67 z/s | 9 302 | 944 | référence |
| **BATCH_CPU** ✅ | **3 231** | **3.59 z/s** | 45 009 | 4 164 | **×5.3** |
| **BATCH_GPU** ✅ | **3 051** | **3.39 z/s** | 50 001 | 4 596 | **×5.1** |

**Observations clés :**

- Le gain réel est **×5.3** vs CPU scalaire — confirmé en conditions propres
- BATCH_CPU ≈ BATCH_GPU : la GTX 960M n'apporte pas de gain supplémentaire ici
- **Pourquoi GPU ≈ CPU batch ?** L'affinage Illinois (mpmath, CPU pur) représente 80–90% du temps total. La GPU accélère uniquement la détection Z(t) (10–20%)

```
Temps total = Détection Z(t) [10–20%]  +  Affinage Illinois [80–90%]
                    ↑                              ↑
         GPU ×10 ici (bursts 30–50%)      CPU pur — mpmath non portable GPU
```

- Le profil GPU dans nvtop montre des **pics 30–50%** en burst → entre les pics, Illinois CPU reprend à 100%
- Pour aller plus vite : **accélérer Illinois lui-même** → Phase C (module C + Arb)

### Pattern GPU observé dans nvtop

```
GPU%  ████░░░███░░░░████░░░███░░░░████░░░
      ↑ bloc RS    ↑ Illinois CPU  ↑ bloc RS
      (CuPy 40%)  (mpmath 100%)   (CuPy 40%)
```

Température GPU : 52–57°C — aucune surchauffe.

---

## 6. GPU GTX 960M

### Spécifications

| Spec | Valeur |
|---|---|
| Modèle | NVIDIA GeForce GTX 960M |
| Cœurs CUDA | 640 |
| VRAM | 4 096 MB |
| CUDA Version | 12.2 |
| Compute Capability | 5.0 |

### Problèmes CuPy rencontrés

| Erreur | Cause | Solution |
|---|---|---|
| `libnvrtc.so.11.2 not found` | cupy-cuda11x sur CUDA 12 | `pip install cupy-cuda12x` |
| `module 'cupy' has no attribute 'cuda'` | Conflits cupy-cuda11x + cupy-cuda12x | Désinstaller tout, réinstaller cupy-cuda12x |
| GPU-Util = 0% | Mode `prime-select on-demand` | `sudo prime-select nvidia && sudo reboot` |

### Architecture double GPU laptop

| GPU | Rôle | CUDA |
|---|---|---|
| Intel HD Graphics 620 | Affichage écran (économe) | ❌ |
| NVIDIA GTX 960M | Calcul intensif | ✅ |

### Projection avec GPU active

| T_MAX | Zéros | v3 CPU seule | + batch CPU | + batch GPU 960M |
|---|---|---|---|---|
| 10 000 | 10 142 | ~1h | ~8 min | ~3–5 min |
| 100 000 | 138 067 | ~20h | ~4h | ~1h |
| 500 000 | ~750 000 | ~3 sem. | ~2 j | ~5h |

---

## 7. Fichiers générés

### Code source
- [`src/calculs/optimisation/theta_rapide.py`](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/src/calculs/optimisation/theta_rapide.py)
- [`src/calculs/optimisation/riemann_siegel_batch.py`](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/src/calculs/optimisation/riemann_siegel_batch.py)
- [`src/calculs/optimisation/parallel_scanner.py`](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/src/calculs/optimisation/parallel_scanner.py)
- [`src/calculs/optimisation/turing_validation.py`](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/src/calculs/optimisation/turing_validation.py)
- [`src/calculs/optimisation/compute_zeros_v3.py`](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/src/calculs/optimisation/compute_zeros_v3.py)
- [`src/calculs/optimisation/benchmark_15min.py`](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/src/calculs/optimisation/benchmark_15min.py)

### Rapport d'analyse
- [`pdf/optimisation/analyse_problemes_v2_v3_phase0.pdf`](https://raw.githubusercontent.com/hprzeta/Riemann_Lab/Riemann_Lab_IA/pdf/optimisation/analyse_problemes_v2_v3_phase0.pdf) — 14 pages, formules LaTeX

---

## 8. Prochaines étapes

- [x] **Reboot NVIDIA** → `sudo prime-select nvidia && sudo reboot` ✅ 16 mai 2026
- [x] **Test batch_cpu équitable** → **3 231 zéros, 3.59 z/s, ×5.3** ✅ 16 mai 2026
- [x] **Test batch_gpu équitable** → **3 051 zéros, 3.39 z/s, GPU active** ✅ 16 mai 2026
- [x] **Lancer T=10 000** avec v3 → ✅  **10 142 zéros, en 45 mn , CPU_BACTH active** 22 mai 23h04
- [ ] **Phase C** → module C avec libmpfr (×5–10 supplémentaire)
- [ ] **Phase Arb** → python-flint, version partielle Odlyzko-Schönhage


---

## 9. Comprendre les outils de monitoring — nvtop vs htop

### Pourquoi deux outils ?

| Outil | Surveille | Usage |
|---|---|---|
| **htop** | CPU + RAM | Voir les processus Python, leur % CPU, leur mémoire |
| **nvtop** | GPU | Voir l'utilisation globale de la puce graphique |

### Ce que montre htop pendant batch_gpu

```
PID   CPU%   Command
15185  100%  python benchmark_15min.py --mode batch_gpu
```

Le processus Python est à **100% CPU** — c'est normal. Voici pourquoi :

```
Python (1 thread)
    ↓
CuPy : envoie un bloc de calcul à la GPU  → CPU libéré brièvement
    ↓
GPU calcule les phases (burst 30–50%)
    ↓
CuPy : récupère le résultat             → CPU reprend
    ↓
mpmath Illinois : affinage du zéro       → CPU 100% pendant ~1s
    ↓
recommencer...
```

htop ne voit que le thread Python — il mesure **100% CPU** car Illinois mpmath monopolise le cœur entre chaque burst GPU.

### Pourquoi 0% GPU dans la liste des processus nvtop ?

C'est la question la plus déroutante. Dans nvtop, la colonne GPU% par processus affiche **0%** pour Python alors que le graphe global montre **30–50%**.

**Explication :** nvtop échantillonne toutes les 2 secondes. Un burst GPU CuPy dure **~50 ms** (50 millisecondes). Entre deux échantillons de nvtop, le burst est déjà terminé et Illinois CPU a repris :

```
Temps   : 0ms    50ms   200ms  2000ms (=1 sample nvtop)
GPU%    : ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
Illinois: ░░░░████████████████████████████████████████

nvtop sample à 2000ms → voit Illinois (CPU) → affiche GPU=0%
```

**En haut du graphe nvtop** (historique 90s) : les pics sont visibles car nvtop **accumule** les mesures sur le temps et dessine la courbe — les bursts laissent une trace même s'ils sont courts.

### Résumé visuel

```
nvtop — ce que tu vois :

En haut (graphe historique)     En bas (liste processus)
┌─────────────────────────┐     ┌──────────────────────────┐
│  GPU0 %                 │     │ PID   GPU%  CPU%  Command │
│    ████  ██  ███  ██   │     │ 15185   0%  100%  python  │
│  ██    ██  ██   ██  ██ │     │                            │
│ ─────────────────────── │     │ ← 0% car burst trop court │
│ ←  bursts visibles       │     │   pour l'échantillonnage  │
└─────────────────────────┘     └──────────────────────────┘
         ↑ FIABLE                        ↑ TROMPEUSE
```

**Règle :** pour savoir si la GPU travaille, **regarder le graphe du haut**, pas la liste du bas.

### nvtop dans le terminal VSCode vs terminal système

nvtop utilise **ncurses** — une bibliothèque de rendu texte avancé qui nécessite un vrai terminal avec support des séquences d'échappement ANSI complet.

| Terminal | nvtop | Pourquoi |
|---|---|---|
| Terminal système (gnome-terminal) | ✅ Fonctionne | Vrai émulateur VT100 complet |
| Terminal VSCode intégré | ❌ Crash / affichage cassé | Émulation partielle, pas de support ncurses complet |

**Solution adoptée :** nvtop dans le terminal système gnome-terminal, benchmarks dans les terminaux VSCode.

### nvtop crash — Intel HD + mode NVIDIA principal

Après `sudo prime-select nvidia`, nvtop (version apt) crashait avec :
```
parse_drm_fdinfo_intel: Assertion failed (core dumped)
```

**Cause :** la version packagée d'Ubuntu tente de lire les infos du GPU Intel même quand il est désactivé. Le driver DRM Intel n'est plus accessible en mode NVIDIA principal.

**Solution :** recompiler nvtop depuis les sources avec **uniquement le support NVIDIA** :
```bash
cmake .. -DNVIDIA_SUPPORT=ON -DAMDGPU_SUPPORT=OFF -DINTEL_SUPPORT=OFF \
         -DV3D_SUPPORT=OFF -DMSM_SUPPORT=OFF
make -j4 && sudo make install
```



---

## 10. Lancement compute_zeros_v3 — T=10 000 (en cours)

> **Date :** 16 mai 2026 — 23h04  
> **Statut du calcul en cours :** 🟠 Initialisation des 4 worckers en phase de calcul

### Configuration du run

```
T_MIN           = 14.0
T_MAX           = 10 000
STEP (RS)       = 0.1  (adaptatif)
TOL_AFFINAGE    = 1e-12
DPS_AFFINAGE    = 35
N workers       = 4
N zéros attendus = 10 142
Dossier         = calculs/v3_T10000_20260516_230419
```

### Segments des 4 workers

| Worker | Segment | 
|---|---|
| 0 | [14.0, 2510.9] |
| 1 | [2510.1, 5007.4] |
| 2 | [5006.6, 7503.9] |
| 3 | [7503.1, 10000.0] |

### Problème CUDA + multiprocessing — cudaErrorInitializationError

Au démarrage, les 4 workers affichent :

```
⚠️  GPU erreur runtime : cudaErrorInitializationError: initialization error
    → Bascule automatique sur CPU numpy
    → Fix : sudo apt-get install cuda-nvrtc-11-2
```

**Cause technique :**

CUDA ne supporte pas la réinitialisation après un `fork()` Unix.
`multiprocessing.Pool` crée les workers par fork — le contexte CUDA du
processus principal est copié mais invalide dans les workers :

```
Processus principal
    CuPy initialisé (CUDA context valide) ✅
    ↓ fork()
Worker 0  ← copie du contexte CUDA → invalide ❌ cudaErrorInitializationError
Worker 1  ← copie du contexte CUDA → invalide ❌
Worker 2  ← copie du contexte CUDA → invalide ❌
Worker 3  ← copie du contexte CUDA → invalide ❌
```

**Conséquence :** les workers basculent sur le fallback CPU numpy — 
comportement identique au benchmark batch_cpu (3.5 z/s par worker).

**Fix futur (Phase C) :** initialiser CuPy **après** le fork, à l'intérieur 
de chaque worker, pas dans le processus principal.

**Impact sur le calcul actuel :** aucun — les 4 workers CPU batch tournent
normalement à ~90% CPU chacun.

---

## 11. Processus, threads et threads internes — comprendre htop

Lors du lancement de v3, htop montre ~20 lignes pour un seul programme.
Voici l'explication complète.

### Définitions fondamentales

**Un processus** = programme indépendant avec sa propre mémoire isolée.  
**Un thread** = tâche qui tourne dans un processus, partageant sa mémoire.

```
PROCESSUS A (mémoire propre)       PROCESSUS B (mémoire propre)
┌──────────────────────────┐       ┌──────────────────────────┐
│  Thread 1  │  Thread 2   │       │  Thread 1  │  Thread 2   │
└──────────────────────────┘       └──────────────────────────┘
        ↑ isolé complètement               ↑ isolé complètement
```

### Architecture réelle dans compute_zeros_v3.py

```
Processus principal (BLANC htop)
│   Lance multiprocessing.Pool(4)
│   Attend les résultats
│
├── Worker 0 (BLANC) — processus indépendant, mémoire isolée
│       ├── Thread BLAS (VERT) — calcul matriciel numpy
│       ├── Thread BLAS (VERT) — calcul matriciel numpy
│       └── Thread BLAS (VERT) — calcul matriciel numpy
│
├── Worker 1 (BLANC) — processus indépendant
│       ├── Thread BLAS (VERT)
│       ├── Thread BLAS (VERT)
│       └── Thread BLAS (VERT)
│
├── Worker 2 (BLANC)
└── Worker 3 (BLANC)
```

**Total visible dans htop : ~17-20 lignes** pour un seul programme.

### Pourquoi multiprocessing (pas threads) pour les workers ?

```
Threads Python    → partagent la mémoire GMP/mpmath → corruption → crash ❌
Processus séparés → mémoire isolée                  → GMP sûr    → OK   ✅
```

### Pourquoi numpy crée des threads internes BLAS (VERT) ?

`np.dot(cos_phases, inv_sqn)` appelle BLAS (Basic Linear Algebra Subprograms).
BLAS parallélise automatiquement la multiplication matricielle sur plusieurs
threads pour exploiter les instructions SIMD (AVX2) du CPU :

```python
np.dot(matrice_MxN, vecteur_N)
    ↓ BLAS décompose automatiquement
Thread 1 → lignes 0..M/3
Thread 2 → lignes M/3..2M/3
Thread 3 → lignes 2M/3..M
```

### Tableau récapitulatif

| | Processus (BLANC) | Thread interne (VERT) |
|---|---|---|
| Mémoire | Séparée et isolée | Partagée avec le parent |
| Création | Lent (~100ms) | Rapide (~1ms) |
| Crash | Isolé (n'affecte pas les autres) | Peut planter tout le processus |
| Utilisé pour | Workers mpmath Illinois | Calcul matriciel BLAS numpy |
| Visible dans htop | ✅ Oui | ✅ Oui (indenté sous le parent) |

### Load average observé

```
Load average : 8.11  (4 workers × ~2 threads actifs chacun)
```

Normal avec 4 processus intensifs — la machine est utilisée au maximum
de sa capacité de calcul.


---

## Références

- [Rapport complet PDF](https://raw.githubusercontent.com/hprzeta/Riemann_Lab/Riemann_Lab_IA/pdf/optimisation/analyse_problemes_v2_v3_phase0.pdf)
- [LMFDB — Zeros of ζ(s)](https://lmfdb.org/zeros/zeta/)
- [Titchmarsh (1986) PDF — Rutgers](https://sites.math.rutgers.edu/~zeilberg/EM18/TitchmarshZeta.pdf) |
- [Turing (1953) PDF — UMN/Odlyzko](https://www-users.cse.umn.edu/~odlyzko/doc/turing.zeta.pdf) |
- [Odlyzko & Schönhage (1988) PDF — UMN officiel](https://www-users.cse.umn.edu/~odlyzko/doc/arch/fast.zeta.eval.pdf) |


---
*Dernière mise à jour : 12 juin 2026 — liens PDF corrigés (raw), statut mis à jour · 503 lignes*
