# src/calculs/optimisation/CLAUDE.md — Instructions Phase C
> Contexte local Claude Code — optimisation & Phase C (Illinois en C/libmpfr).
> Règles **stables** ; aucun état de session ici (→ `Handoff.md`).
> Mis à jour : 31 mai 2026

---

## Rôle de ce dossier

Cœur du calcul numérique du projet. Modules Python (`compute_zeros_v*.py`) +
portage de l'affinage Illinois en C/libmpfr dans `c_modules/`.

```
Branche C        : Riemann_Lab_C
Dossier C        : c_modules/  (voir son propre CLAUDE.md)
Branche Python   : Riemann_Lab_IA (ne pas modifier depuis Riemann_Lab_C)
```

---

## Pourquoi la Phase C

L'affinage Illinois représente **80–90 % du temps total**. La Phase C cible un gain
×5–10 sur ce goulot. (Détail du goulot courant et de la prochaine action : `Handoff.md`.)

---

## 📍 Formules — SOURCE CANONIQUE

> Les formules N(T), θ(t), Z(t), Illinois et la table de précision adaptative sont
> définies **une seule fois** dans `~/projet_zeta/CLAUDE.md` (chargé en cascade).
> **Ne pas les recopier ici.** Se référer à ce fichier.

Rappel de l'algorithme Illinois (détail local) :
```
Donné [a,b] tel que Z(a)·Z(b) < 0 :
  1. c = b − Z(b)·(b−a) / (Z(b)−Z(a))        ← sécante
  2. Si Z(a)·Z(c) < 0 : b ← c
     Sinon             : a ← c, Z(a) *= 0.5   ← correction Illinois
  3. Répéter jusqu'à |b−a| < 1e-12
Précision cible C : PREC = 170 bits (≈ 51 décimales)
```

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

**Fallback obligatoire :** si `illinois_mpfr.so` absent → `mpmath.findroot(..., solver='illinois')`.
**Sécurité :** en mode production, préférer `raise FileNotFoundError` à une dégradation
silencieuse (un fallback invisible masque les bugs).

---

## Validation — données de référence LMFDB

| n | γ_n (LMFDB) | Tolérance |
|---|---|---|
| 1 | 14.134725141734693 | < 1e-12 |
| 2 | 21.022039638771555 | < 1e-12 |
| 3 | 25.010857580145688 | < 1e-12 |
| 4 | 30.424876125859513 | < 1e-12 |
| 5 | 32.935061587739189 | < 1e-12 |

Critères run : Turing-Backlund complet · LMFDB ≥ 19/20 < 1e-10 · Illinois_C pur > 50 %.

---

## Prérequis système

```bash
sudo apt install libmpfr-dev libgmp-dev gcc build-essential
mpfr-config --version   # doit retourner ≥ 4.0
```

---

## Conventions de code

- Commentaires en **français**
- Tout `mpfr_init2` → `mpfr_clear` correspondant (pas de fuite mémoire)
- `PREC 170` en haut du fichier · arrondi toujours `MPFR_RNDN`
- Pas de `printf` dans les fonctions de calcul (seulement dans `main()` de test)
- `.so` compilé avec `-O3 -march=native -fPIC`

---

## Workflow Git Phase C

```bash
git checkout Riemann_Lab_C
git add c_modules/
git commit -m "feat(phase-c): ..."
git push origin Riemann_Lab_C
```

---

## Règle de double mise à jour — OBLIGATOIRE

À chaque nouvelle formule / correction d'algorithme, enrichir AUSSI les bases de référence
et skills, puis pousser :
- `~/.claude/skills/zeta-lab/references/Formules_zeta.md`
- `~/.claude/skills/zeta-lab/references/Bibliotheques.md`
- `~/.claude/skills/zeta-lab/SKILL.md` · `SKILL_phase_c.md`

---

## Rapport de transition (après chaque vN→vN+1)

`.md` + PDF via `pdflatex` (structure `analyse_problemes_v2_v3_phase0.pdf`) :
cause mathématique, formules, tableaux comparatifs, gains mesurés, questions ouvertes.

---
*Dernière mise à jour : 31 mai 2026 — ~120 lignes (formules dédupliquées → projet CLAUDE.md)*
