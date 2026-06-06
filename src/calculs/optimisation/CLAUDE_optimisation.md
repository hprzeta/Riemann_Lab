# CLAUDE.md — src/calculs/optimisation/
> Contexte local pour Claude Code — Phase C (Illinois en C/libmpfr)
> Mis à jour : 23 mai 2026

---

## Rôle de ce dossier

Ce dossier contient le **cœur du calcul numérique** du projet Riemann_Lab.
Actuellement : `compute_zeros_v3.py` + modules Python.
Phase C en cours : portage de l'affinage Illinois en C/libmpfr → `c_modules/`.

---

## État de la branche courante

```
Branche active   : Riemann_Lab_C
Dossier C        : ~/projet_zeta/src/calculs/optimisation/c_modules/
Branche Python   : Riemann_Lab_IA (ne pas modifier depuis Riemann_Lab_C)
```

---

## Objectif immédiat — Phase C

Porter `illinois_mpfr` de Python/mpmath vers C/libmpfr.

**Pourquoi :** Illinois représente **80–90% du temps total** de calcul.
La Phase C cible ×5–10 sur ce goulot → ~15–20 z/s au lieu de 3.59 z/s.

**Architecture à construire :**
```
c_modules/
├── illinois_mpfr.c     ← affinage Illinois avec libmpfr (PREC = 170 bits ≈ 51 dps)
├── illinois_mpfr.h     ← header
├── z_function.c        ← Z(t) Riemann-Siegel en C (float64 pour la détection)
├── z_function.h
├── Makefile            ← compile → illinois_mpfr.so
└── test_illinois.py    ← validation via ctypes (10 premiers zéros vs LMFDB)
```

---

## Formules critiques — NE JAMAIS SE TROMPER

### Z(t) — formule de Riemann-Siegel
```
Z(t) = 2 · Σ_{n=1}^{N} cos(θ(t) − t·ln n) / √n  +  R(t)
N = ⌊√(t/2π)⌋
```

### θ(t) — approximation de Stirling (valide pour t ≥ 20)
```
θ(t) = (t/2)·ln(t/2π) − t/2 − π/8 + 1/(48t) + 7/(5760t³) − 31/(80640t⁵)
```

### N(T) — formule de Riemann-von Mangoldt (EXACTE)
```
N(T) = T/(2π) · ln(T/2πe)      ← le 'e' dans 2πe est OBLIGATOIRE
```

### Illinois — algorithme (méthode de la sécante modifiée)
```
Donné [a,b] tel que Z(a)·Z(b) < 0 :
  1. c = b − Z(b)·(b−a) / (Z(b)−Z(a))       ← sécante
  2. Si Z(a)·Z(c) < 0 : b ← c
     Sinon             : a ← c, Z(a) *= 0.5  ← correction Illinois
  3. Répéter jusqu'à |b−a| < 1e-12
Précision cible : PREC = 170 bits (≈ 51 décimales)
```

---

## Précision adaptative (règle v3 / v4)

| Opération          | Précision          | Implémentation |
|--------------------|---------------------|----------------|
| θ(t) détection     | float64 natif       | NumPy / C double |
| Z(t) détection     | float64 natif       | NumPy / C double |
| Affinage Illinois  | 170 bits ≈ 51 dps   | libmpfr (Phase C) |
| Validation finale  | 50 dps              | mpmath Python |

---

## Interface Python ↔ C (ctypes)

```python
import ctypes, os
lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), 'c_modules/illinois_mpfr.so'))
lib.illinois_mpfr.restype  = ctypes.c_double
lib.illinois_mpfr.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]

def illinois_c(a: float, b: float, tol: float = 1e-12) -> float:
    """Affinage Illinois via C/libmpfr. Fallback mpmath si .so absent."""
    return lib.illinois_mpfr(a, b, tol)
```

**Fallback obligatoire :** si `illinois_mpfr.so` est absent → revenir à `mpmath.findroot(..., solver='illinois')`.

---

## Validation — données de référence LMFDB

| n | γ_n (LMFDB)            | Tolérance attendue |
|---|-------------------------|---------------------|
| 1 | 14.134725141734693      | < 1e-12             |
| 2 | 21.022039638771555      | < 1e-12             |
| 3 | 25.010857580145688      | < 1e-12             |
| 4 | 30.424876125859513      | < 1e-12             |
| 5 | 32.935061587739189      | < 1e-12             |

---

## Prérequis système

```bash
sudo apt install libmpfr-dev libgmp-dev gcc build-essential
mpfr-config --version   # doit retourner ≥ 4.0
```

---

## Convention de code C dans ce projet

- Commentaires en **français**
- Tout `mpfr_init2` → `mpfr_clear` correspondant (pas de fuite mémoire)
- Constante `PREC 170` définie en haut du fichier
- Mode d'arrondi : toujours `MPFR_RNDN` (arrondi au plus proche)
- Pas de `printf` dans les fonctions de calcul (seulement dans `main()` de test)
- `.so` compilé avec `-O3 -march=native -fPIC`

---

## Workflow Git Phase C

```bash
git checkout Riemann_Lab_C
# tout le code C va dans c_modules/
git add c_modules/
git commit -m "feat(phase-c): illinois_mpfr.c initial implementation"
git push origin Riemann_Lab_C
```

---

## Rapport de transition v3→v4 (obligatoire après Phase C)

Format : `.md` + PDF via `pdflatex` (même structure que `analyse_problemes_v2_v3_phase0.pdf`).
Contenu : cause mathématique, formules, tableaux comparatifs, gains mesurés, questions ouvertes.

---
*Dernière mise à jour : 23 mai 2026 — 108 lignes*
