---
name: code-review
dossier: /home/riemann/.claude/skills/code-review
description: >
  Audit et révision de code pour le projet Riemann_Lab. Se déclenche sur :
  "audite ce code", "révise ce fichier", "vérifie ce C", "relis illinois_mpfr",
  "check ctypes", "code review", "améliore ce code", "problème dans ce fichier",
  "optimise", "refactorise", "clean code", "qualité du code".
version: 1.0.0
date: 2026-05-23
---

# Code Review — Riemann_Lab

## Priorités d'audit pour ce projet

### Code C (Phase C — illinois_mpfr.c, z_function.c)

1. **Mémoire libmpfr** — chaque `mpfr_init2()` a-t-il son `mpfr_clear()` ?
   - Chercher tout `return` sans `mpfr_clears()` avant
   - Variables de boucle : init/clear hors de la boucle, pas dedans

2. **Précision** — `PREC = 170` bits utilisé partout ?
   - Pas de `mpfr_init()` sans `_2` (précision par défaut insuffisante)
   - Mode d'arrondi : toujours `MPFR_RNDN`

3. **Interface ctypes** — signature immuable :
   ```c
   double illinois_mpfr(double a_d, double b_d, double tol);
   ```
   Tout changement casse l'interface Python

4. **Makefile** — tabulations réelles (0x09), pas des espaces

5. **Performances** — allocation dans une boucle = ralentissement ×N
   - Variables `mpfr_t` temporaires : déclarer hors boucle, réutiliser

### Code Python (compute_zeros_v*.py)

1. **plt.show()** interdit en production → toujours `plt.savefig()` + `plt.close()`
2. **joblib** interdit avec mpmath → utiliser `multiprocessing.Pool`
3. **N(T)** : formule avec `e` obligatoire : `T/(2π)·ln(T/2πe)`
4. **STEP** : `min(2π / (5·ln(T_max/2π)), 0.10)`
5. Fallback ctypes : si `.so` absent → revenir à mpmath.findroot

## Format du rapport de review

Pour chaque problème trouvé :
- **Fichier et ligne** : `illinois_mpfr.c:87`
- **Sévérité** : 🔴 Critique / 🟡 Avertissement / 🔵 Style
- **Cause** : explication courte
- **Correction** : code corrigé

## Règles générales

- Commentaires en français
- Variables mathématiquement significatives (`t_a`, `t_b`, `zero_t`, pas `x`, `y`)
- Pas de magic numbers — utiliser des constantes nommées

---
*Dernière mise à jour : 23 mai 2026*
