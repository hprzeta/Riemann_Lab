# Phase C — Voie B / v5 : Illinois C pur via callback mpmath

> Date : 29 mai 2026 — hprzeta  
> Branche : `Riemann_Lab_C`  
> Statut : ✅ Validé sur T=80 (100% Illinois C pur)

---

## 1. Problème identifié

| Symptôme | Valeur |
|---|---|
| Illinois_C pur sur T=650 (v4) | 0% |
| Méthode utilisée (v4) | 100% `Illinois_C→mpmath` |
| Cause | Biais Z_mpfr (RS+C0+C1) ~9e-3 vs vrais zéros |
| Conséquence | `abs(mpmath.siegelz(gamma_c)) ≈ 5e-4` ≫ seuil 1e-8 |

### Cause mathématique

La formule Riemann-Siegel tronquée à C0+C1 est une série **asymptotique** :

$$\text{erreur} \sim \tau^{-5/2}, \quad \tau = \sqrt{t/2\pi}$$

| Approximation RS | Précision |
|---|---|
| C0 seulement | ~1e-2 |
| C0 + C1 (état v4) | ~**1e-3** |
| C0+C1+C2+... (3-5 termes) | ~1e-8 |
| `mpmath.siegelz` | ~1e-12 |

`mpc_zeta` (alternative via libmpc) est **absent** dans libmpc 1.3.1.

---

## 2. Solution retenue — Voie B : callback Python/C

### Architecture

```
Python                          C (.so)
──────────────────              ──────────────────────────────
_z_mpmath(t):                   illinois_mpfr_cb(a, b, tol, zfunc):
  return float(                   Za = zfunc(a)   ← appelle Python
    mpmath.siegelz(t))            Zb = zfunc(b)
                                  for iter ...:
_Z_CB = CFUNCTYPE(                  c  = sécante
  c_double, c_double              Zc = zfunc(c)  ← appelle Python
)(_z_mpmath)                      ...
                                  return meilleure_borne
illinois_c_exact(a, b, tol) ──→ illinois_mpfr_cb(a, b, tol, _Z_CB)
```

### Contraintes respectées

- `illinois_mpfr(a, b, tol)` — interface immuable, **inchangée** ✅
- `illinois_mpfr.so` — chargeable via `ctypes.CDLL` comme avant ✅
- `compute_zeros_v4.py` — **non modifié** ✅

---

## 3. Fichiers créés / modifiés

| Fichier | Type | Modification |
|---|---|---|
| `c_modules/illinois_mpfr.h` | Modifié | Ajout `typedef z_func_t` + signature `illinois_mpfr_cb` |
| `c_modules/illinois_mpfr.c` | Modifié | Ajout `illinois_mpfr_cb` (Illinois en double + callback) |
| `c_modules/illinois_pyZ.py` | Nouveau | Wrapper Python : charge .so, définit callback, expose `illinois_c_exact` |
| `c_modules/test_illinois_v5.py` | Nouveau | Validation Voie B vs v4 sur 20 premiers zéros LMFDB |
| `compute_zeros_v5.py` | Nouveau | Orchestrateur v5 utilisant `illinois_c_exact` |
| `docs/phase_c_voie_b_v5_plan.md` | Nouveau | Ce fichier |

---

## 4. Correction de robustesse — cas dégénéré

### Problème détecté

Quand la détection (`mpmath.siegelz` à 15 dps) place une borne quasi-exactement sur le zéro :

$$|Z_b| \approx 6 \times 10^{-14} \ll |Z_a| \approx 4 \times 10^{-3}$$

La sécante donne :

$$c = b - Z_b \cdot \frac{b-a}{Z_b - Z_a} \approx b - 0 = b$$

Illinois stagne : 100 itérations sans avancer, retourne $(a+b)/2$.

### Correction

Deux ajouts dans `illinois_mpfr_cb` :

```c
// 1. Avant la boucle — retour immédiat si une borne est quasi-zéro
if (fabs(Za) < fabs(Zb) * 1e-10) return a;
if (fabs(Zb) < fabs(Za) * 1e-10) return b;

// 2. Fin de boucle — retourner la meilleure borne (pas le milieu)
return (fabs(Za) < fabs(Zb)) ? a : b;
```

---

## 5. Résultats de validation

### test_illinois_v5.py — 20 premiers zéros LMFDB

| Méthode | Convergences | LMFDB < 1e-10 | Temps médian |
|---|---|---|---|
| `illinois_c_exact` (Voie B) | **20/20** | **19/20** | **21 ms/zéro** |
| `illinois_c_rs` (v4 référence) | 0/10 | 0/10 | — |

Biais éliminé : résidus $\|Z_\text{Riemann}(\gamma_c)\| \leq 5 \times 10^{-13}$ sur tous les 20.

### Run v5 T=80

| Critère | Résultat |
|---|---|
| Zéros calculés | 21 (attendus : 21) |
| Illinois_C pur | **100%** (v4 : 0%) |
| Illinois_C→mpmath | 0% |
| mpmath fallback | 0% |
| Turing-Backlund | ✅ COMPLET |
| LMFDB 20/20 | 19/20 (zéro #20 = cas limite 8.06e-10) |
| Durée | 25.8s |

---

## 6. Note sur le zéro #20

$\gamma_{20} \approx 77.1448...$. Le score LMFDB 19/20 (pas 20/20) est un cas limite :
- `illinois_c_exact` calcule $\gamma_{20}$ avec $|Z_\text{Riemann}(\gamma_{20})| = 8.6 \times 10^{-15}$ — **vrai zéro confirmé**
- L'écart par rapport à la valeur LMFDB stockée dans le code est 8.06e-10
- Cause probable : légère imprécision de la valeur de référence stockée (15 décimales), ou limite de `mpmath.siegelz` à 35 dps

Ce n'est **pas** un échec de la méthode — Illinois C pur a convergé correctement.

---

## 7. Prochaines étapes

1. **Immédiat** : run T=650 → valider Illinois_C pur > 50%
2. **v4.1** : corriger les 5 erreurs architecturales (Handoff §Phase C) :
   - Détection via `Z_batch()` (interdit : mpmath.siegelz en détection → lent)
   - Parallélisme 4 workers
   - Seuil `T_SEUIL_ILLINOIS_C = 300` (mathématiquement justifié)
3. **T=1000** puis **T=10000** après validation v4.1

---

## 8. Distinction expérimental / conjecture / preuve

> Ce document décrit des **calculs expérimentaux** visant à localiser les zéros non-triviaux
> de $\zeta(s)$ sur la droite critique $\text{Re}(s) = \tfrac{1}{2}$.
> La validation Turing-Backlund garantit la **complétude numérique** (aucun zéro manqué)
> dans l'intervalle calculé, sous réserve de la précision de `mpmath.siegelz`.
> Ces résultats ne constituent **pas une preuve** de l'Hypothèse de Riemann.

---

*Rapport généré le 29 mai 2026 — Phase C Voie B*
