---
name: phase-c-illinois
description: >
  Skill pour la Phase C du projet Riemann_Lab — accélération de l'affinage Illinois
  via un module C/libmpfr (illinois_mpfr.so) appelé depuis Python par ctypes.
  Se déclenche sur : "Phase C", "libmpfr", "Illinois en C", "affinage C",
  "illinois_mpfr", "ctypes", "Voie B", "module C", "branche Riemann_Lab_C",
  "post-fork", "mpfr_t", "accélération Illinois", "compute_zeros_v4_1".
version: 0.2.0
date: 2026-06-01
---

# Phase C — Affinage Illinois en C / libmpfr (Voie B)

> Auteur : hprzeta · Mise à jour : 1ᵉʳ juin 2026

## Contexte

Le profilage montre que l'affinage Illinois représente **80–90 % du temps total** ;
la détection Z(t) n'en fait que 10–20 % (et la GPU GTX 960M n'aide que là).
**Objectif Phase C :** accélérer l'affinage via C/libmpfr.

```
Branche GitHub : Riemann_Lab_C
Dossier local  : ~/projet_zeta/src/calculs/optimisation/c_modules/
```

---

## ⚠️ Architecture RETENUE = Voie B (ne pas refaire la Voie A)

**Voie A (ABANDONNÉE)** : réécrire **toute** la formule Riemann-Siegel — y compris
l'évaluation de Z(t) — en C (`Z_mpfr`). Échec : incohérence entre `Z_mpfr` (C) et
`Z_double`, donnant un **biais ~0.3** au lieu de < 1e-12. De plus `mpc_zeta` est
**absent de libmpc 1.3.1**. → Ne pas repartir sur cette voie.

**Voie B (RETENUE, validée 100 % en v5 — commit `b8018c0`)** :

| Étape | Responsable | Précision |
|---|---|---|
| Détection des intervalles (changements de signe) | `Z_vect_correct` (NumPy vectorisé) + `mpmath.siegelz` en référence | signe seul |
| Affinage du zéro dans l'intervalle | **Illinois piloté en C** (`illinois_mpfr`), Z(t) évalué en haute précision côté `mpmath.siegelz` | tol = 1e-12 |
| Seuil de bascule | `T_SEUIL = 300.0` : `t < 300` → mpmath pur (car $N=\lfloor\sqrt{t/2\pi}\rfloor < 7$, RS imprécis) ; `t ≥ 300` → Illinois C | — |

> ⚠️ Détail à confirmer contre le code v4.1 réel : l'évaluation de Z(t) à l'intérieur
> de l'itération Illinois passe par `mpmath.siegelz` (Voie B), pas par un `Z_mpfr` C autonome.

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

## État Phase C au 1ᵉʳ juin 2026

| Jalon | Statut |
|---|---|
| Voie B validée (v5, `b8018c0`) — Illinois_C pur 100 %, biais < 1e-13 | ✅ |
| `Z_vect_correct` (détection) — 0 désaccord vs siegelz sur 4 plages | ✅ |
| v4.1 post-fork (`d9bb267`) — **41 z/s, ×39** | ✅ mesuré · tests unitaires OK |
| Validation complète run T=300 (Vérif A) puis T=1000 → T=10 000 | ⏳ à faire |
| Rapport `v5 → v4.1` (`pdf/optimisation/analyse_problemes_v5_v4_1.pdf`) | ⏳ à faire |

---

## Gains

| Composant | Avant (mpmath pur) | Après (Voie B post-fork) |
|---|---|---|
| Affinage Illinois | 80–90 % du temps | accéléré (C + parallélisme ×4) |
| Vitesse globale | ~1.1 z/s (v4.1 séquentiel) | **~41 z/s** (`d9bb267`) |

> Chiffres mesurés sur tests unitaires ; la validation complète (Turing-Backlund +
> LMFDB sur run réel) reste à confirmer avant un run long.

---

## Mur de latence — le prochain levier (voir Formules_zeta §17)

Le **41 z/s** ci-dessus est le débit d'**Illinois_C pur** (racines de la RS tronquée
$Z_{\text{mpfr}}$) : suffisant pour le **comptage** Turing, mais positions imprécises
($\sim 10^{-4}$, §5.6). Dès qu'on exige des positions $<10^{-10}$, il faut un *polish* via
`mpmath.siegelz`, dont la **latence** (~296 ms à $t\approx 9000$) ramène à ~0,5 z/s, soit ~7 h.

- **Le goulot est `siegelz`, pas l'algorithme** — Newton réfuté (Formules_zeta §6.5.5).
- Ni GPU ni RAM ni swap n'agissent dessus ; le seul levier réaliste est **Arb**
  (`acb_dirichlet_hardy_z`, ≈ ×10–20) → voir `Bibliotheques.md §12`.
- Deux régimes à trancher selon le livrable : **comptage** (Illinois_C pur, ~4 min) vs
  **catalogue de positions** (polish ~7 h, ou réutiliser le CSV v2 existant).

---

## Étapes restantes

1. Lancer **Vérif A (T=300)** : Turing COMPLET · LMFDB 19/20 < 1e-10 · Illinois_C ~100 %.
2. **Vérif B précision** : sur ~10 zéros de $[300, 700]$, mesurer $|\gamma_{\text{C}} - \gamma_{\text{polish}}|$
   (verdict régime rapide vs régime comptage).
3. **Benchmark `affinage_arb.py`** vs `siegelz` sur $[300, 700]$ → mesurer le vrai facteur Arb
   avant toute réécriture (seul chemin < 30 min avec positions exactes).
4. Si OK → run **T=1000** → **T=10 000**.
5. Rédiger le rapport `v5 → v4.1` (même structure que `v2→v3`).

---
*Skill du projet Riemann_Lab · Auteur : hprzeta · Mise à jour : 2 juin 2026*
