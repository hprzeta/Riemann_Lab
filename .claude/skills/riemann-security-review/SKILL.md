---
name: security-review
dossier:/home/riemann/.claude/skills/security-review
description: >
  Audit de sécurité et robustesse pour le projet Riemann_Lab. Se déclenche sur :
  "segfault", "risque de crash", "cette interface est-elle sûre", "vérif sécurité",
  "security review", "risque .so", "ctypes dangereux", "buffer overflow",
  "fuite mémoire", "memory leak", "undefined behavior", "UB", "valgrind".
version: 1.0.0
date: 2026-05-23
---

# Security Review — Riemann_Lab

## Risques spécifiques à ce projet

### Interface ctypes ↔ C (.so)

**Risque #1 — Mauvais type ctypes**
```python
# ❌ DANGEREUX — type incorrect → comportement indéfini
lib.illinois_mpfr.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float]

# ✅ CORRECT
lib.illinois_mpfr.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]
lib.illinois_mpfr.restype  = ctypes.c_double
```

**Risque #2 — .so chargé sans vérification d'existence**
```python
# ❌ DANGEREUX — segfault si .so absent
lib = ctypes.CDLL("illinois_mpfr.so")

# ✅ CORRECT — fallback obligatoire
import os
so_path = os.path.join(os.path.dirname(__file__), 'illinois_mpfr.so')
if os.path.exists(so_path):
    lib = ctypes.CDLL(so_path)
    USE_C = True
else:
    USE_C = False
    # fallback mpmath
```

**Risque #3 — Appel avec NaN ou inf**
```python
# ❌ DANGEREUX — NaN dans illinois_mpfr → loop infinie ou UB côté C
illinois_c(float('nan'), 14.3)

# ✅ CORRECT — valider avant d'appeler
import math
if not (math.isfinite(a) and math.isfinite(b)):
    raise ValueError(f"illinois_c : entrées non finies a={a}, b={b}")
```

### Code C — libmpfr

**Risque #4 — Division par zéro dans la sécante**
```c
// ❌ si Zb == Za → division par zéro
mpfr_sub(den, Zb, Za, MPFR_RNDN);
mpfr_div(num, num, den, MPFR_RNDN);  // UB si den == 0

// ✅ tester avant de diviser
if (mpfr_zero_p(den)) break;  // convergé ou dégénéré
```

**Risque #5 — Boucle infinie si tolérance impossible**
```c
// MAX_ITER = 100 doit toujours stopper la boucle
// Ne jamais utiliser while(1) sans compteur
```

**Risque #6 — Accès à t hors domaine**
```c
// Z(t) via formule RS n'est valide que pour t >= 14 (premier zéro)
// Pour t < 14 : comportement indéfini (N=0, somme vide)
if (t < 14.0) { /* erreur */ }
```

## Checklist de validation avant compilation

- [ ] `mpfr_init2` / `mpfr_clear` : compte = count dans chaque fonction
- [ ] Chaque `return` est précédé de `mpfr_clears(...)`
- [ ] `den` testé non-nul avant division
- [ ] `MAX_ITER` toujours respecté (pas de `while(1)` nu)
- [ ] Côté Python : `argtypes` et `restype` explicitement déclarés
- [ ] Côté Python : fallback mpmath si `.so` absent
- [ ] Côté Python : validation `isfinite(a)` et `isfinite(b)` avant appel

## Outils de diagnostic recommandés

```bash
# Détecter fuites mémoire et UB
valgrind --leak-check=full --track-origins=yes python3 test_illinois.py

# Sanitizers GCC (ajouter au Makefile en mode debug)
CFLAGS_DEBUG = -fsanitize=address,undefined -g
```

---
*Dernière mise à jour : 23 mai 2026*
