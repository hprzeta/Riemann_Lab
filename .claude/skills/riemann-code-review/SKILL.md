---
name: riemann-code-review
description: |
  Audit et revue de code pour le projet `Riemann_Lab` de hprzeta — code Python (mpmath, numpy, multiprocessing, matplotlib) et C/libmpfr (ctypes, illinois_mpfr).

  Utiliser ce skill dès que l'utilisateur demande de :
  - Relire, auditer, ou critiquer un script de calcul de zéros (compute_zeros_*, riemann_siegel*, parallel_scanner, turing_validation)
  - Vérifier une implémentation Riemann-Siegel, Hardy-Z, θ(t), ou l'affinage Illinois
  - Réviser un module C/libmpfr (illinois_mpfr.c, z_function.c) ou son binding ctypes
  - Détecter des régressions connues avant un run long (détection de signe, précision, parallélisme)
  - Préparer une nouvelle version (vN → vN+1) côté code

  Déclencher aussi pour : choix de précision mpmath, vectorisation numpy/cupy, sécurité multiprocessing, performance.
---

# Riemann Code Review Skill

Skill de revue de code spécialisé pour `Riemann_Lab`. Il encode les **bugs réels déjà
rencontrés** dans le projet pour ne jamais les reproduire. Toute revue de code de calcul
doit passer cette checklist **avant** d'autoriser un run long.

> Auteur : hprzeta · Mise à jour : 1ᵉʳ juin 2026

---

## 1. Périmètre

| Couche | Fichiers typiques | Points de vigilance |
|---|---|---|
| Détection Z(t) | `riemann_siegel_batch.py`, `theta_rapide.py` | N(t) variable, signe, vectorisation |
| Affinage | `parallel_scanner.py`, `compute_zeros_v*.py` | Illinois, tol ↔ dps, parallélisme |
| Validation | `turing_validation.py` | N(T) avec le `e`, S(T), branche d'argument |
| Module C | `illinois_mpfr.c/.h`, `z_function.c/.h` | PREC, libmpfr, binding ctypes, fork |

---

## 2. Checklist détection — la plus rentable

1. **Détecteur = Hardy-Z, jamais Re(ζ).** `Re(ζ(½+it))` introduit de faux changements de
   signe via la rotation de phase φ(t) → bug qui a cassé v1 vers t≈432. Vérifier que le
   détecteur est `siegelz` / `Z_fast` / `Z_vect_correct`, pas `zeta(...).real`.

2. **N(t) propre à CHAQUE point.** $N(t)=\lfloor\sqrt{t/2\pi}\rfloor$ dépend de t. Une
   vectorisation avec un `N_max` **fixe** appliqué à tout le batch est FAUSSE : les termes
   $n>N(t_k)$ faussent le signe. Symptôme historique : **359 désaccords** vs `mpmath.siegelz`.
   → Exiger un **masque booléen** `mask[k,n] = (n ≤ N(t_k))` (pattern `Z_vect_correct`).

3. **Validation de la détection avant tout run long.** Comparer les changements de signe
   de la version vectorisée vs `mpmath.siegelz` sur ≥ 4 plages
   ($[14,100]$, $[300,400]$, $[3000,3100]$, $[9900,10000]$).
   - **0 désaccord** = OK même si l'écart numérique est ~1e-3 (troncature RS normale, $O(t^{-3/2})$).
   - **≥ 1 désaccord** ou nb de CS différent = STOP, diagnostiquer.

4. **STEP de balayage sécurisé** : `min(2π/(5·ln(T/2π)), 0.10)`. Division par 5 (pas 3) pour
   les paires de zéros proches. Repérer tout pas fixe trop grand → zéros ratés à grand T.

---

## 3. Checklist affinage Illinois

1. **Cohérence tol ↔ dps.** `tol=1e-12` exige ~12 chiffres → OK à `dps=35`. `tol=1e-20`
   à 35 (ou 50) dps est **impossible** → timeout / `maxsteps` dépassé (bug v2). Refuser tout
   `tol` plus strict que ce que les dps permettent.
2. **Solver = `"illinois"`**, pas `"newton"` (diverge près d'un extremum) ni `"bisect"` seul.
3. **Illinois = 80–90 % du temps total** → c'est LA cible d'optimisation, pas la détection.
4. **Module C post-fork** : si l'affinage utilise `illinois_mpfr.so`, le handle doit être
   chargé **après** le `fork` des workers (sinon sérialisation → parallélisme ×1.8 au lieu de ×4).
   Vérifier l'ordre : `Pool(...)` PUIS chargement du `.so` dans chaque worker.

---

## 4. Checklist précision & arithmétique

| Opération | Précision attendue | Drapeau si écart |
|---|---|---|
| θ asymptotique (float64) | 15 chiffres, t ≥ 20 | mpmath exact en dessous de t=20 |
| Détection `Z_fast` | 25 dps | suffisant pour le signe |
| Affinage Illinois | 35 dps | atteint tol=1e-12 |
| Validation/publication | 50 dps | 1000 premiers zéros |

- **Toujours restaurer `mp.dps`** après un bloc local (`dps_save = mp.dps … mp.dps = dps_save`).
- **Ne JAMAIS mélanger joblib + mpmath** : GMP/MPFR a un état global non thread-safe →
  corruption mémoire. Utiliser `multiprocessing` (fork = copie GMP par process).

---

## 5. Checklist validation Turing-Backlund

1. **N(T) avec le `e`** : $\frac{T}{2\pi}\ln\frac{T}{2\pi e}$. Sans le `e`, sous-estimation
   de ~64 % à T=100 000 → toutes les durées sont fausses. C'est une erreur silencieuse : à traquer.
2. **S(T)** : suivi continu de l'argument (correction de branche ±2π), départ à σ=3 où arg ζ≈0.
3. **Distinguer explicitement MANQUE (delta>0) vs SURPLUS (delta<0)** dans l'affichage.

---

## 6. Checklist module C / ctypes

- `PREC` libmpfr cohérent avec la précision Python visée (cf. `c_modules/CLAUDE.md`, PREC=170).
- `mpc_zeta` **absent** de libmpc 1.3.1 → passer par un wrapper `mpmath.siegelz` côté Python.
- `make clean && make` doit produire le `.so` **sans warning**.
- Le code Python doit **arrêter immédiatement** si `illinois_mpfr.so` est absent (pas de
  fallback global silencieux — c'était une des 5 erreurs de v4).

---

## 7. Checklist visualisation & I/O

- **`plt.savefig()` + `plt.close()`**, jamais `plt.show()` (bloquant → empêche la suite du run).
- CSV : horodatage dans le nom, métadonnées (méthode, dps, T_MAX, turing_complet).
- Logs structurés (`loguru`) avec écart LMFDB par zéro.

---

## 8. Format de sortie d'une revue

1. **Verdict** : 🟢 prêt pour run / 🟡 corrections mineures / 🔴 STOP avant run.
2. **Bugs bloquants** (référence à la section concernée ci-dessus).
3. **Corrections proposées** (diff minimal).
4. **Si du code de calcul est fourni** : appliquer le format projet — *Partie 1 (code)*
   puis *Partie 2 (les maths : pourquoi c'est correct / pourquoi ça va vite)*.

---
*Skill du projet Riemann_Lab · Auteur : hprzeta · Mise à jour : 1ᵉʳ juin 2026*
