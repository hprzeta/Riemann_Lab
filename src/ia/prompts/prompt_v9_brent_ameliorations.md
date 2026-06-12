# Prompt v9 — Brent C/mpfr + améliorations algorithmiques
**Date prévue :** 2026-06-12 matin
**Branche :** Riemann_Lab_C
**Après :** /clear + lire Handoff.md

---

## CONTEXTE

v7 VALIDÉE T=100k : 138 069 zéros, 0 manquant, Turing COMPLET, 30.9 min, 74.49 z/s
v8 LANCÉE ce matin (PID 8956) : run T=100k en cours, résultats attendus ~09h25
  prec_full=80 bits, illinois_refine_adaptive(64,80), ~29 min estimé

Gains algorithmiques restants sur ce CPU (i7-7500U dual-core HT) : ×1.2-1.3
Référence : ameliorations_v9.md (wiki) + Formules_zeta.md §25

Résultats benchmark v8 (2026-06-11) :
  illinois_refine_adaptive (64,80) : 0.416 ms/appel · ×1.06 vs v7
  W=8 : ×0.99 (context-switching dual-core HT) → W=4 optimal

---

## TÂCHE 0 — Vérifier run v8 en cours

```bash
# Vérifier que le run tourne bien :
ps aux | grep compute_zeros_v8 | grep -v grep
tail -20 logs/run_T100k_v8_*.log

# NE PAS relancer v8 — déjà en cours (PID 8956)
# NE PAS toucher compute_zeros_v8.py pendant le run
```

Attendre la fin (~09h25) avant tout benchmark comparatif.
Critères succès v8 : 0 manquant, Turing COMPLET, ~79 z/s.

---

## TÂCHE 1 — Benchmark illinois réel sur 500 zéros

Avant d'implémenter Brent, mesurer le comportement réel d'Illinois v8 :

```python
# Créer : src/calculs/optimisation/benchmark_methodes.py
# Mesurer sur 500 zéros dans [1000, 100000] :
# - Nombre d'itérations moyen par zéro (phase1 + phase2)
# - ms/appel moyen à t=1k, 10k, 50k, 77k
# - Distribution des itérations (histogramme)
# - Ratio phase1/phase2 (64 bits vs 80 bits)
```

Lancer :
```bash
python src/calculs/optimisation/benchmark_methodes.py \
  2>&1 | tee logs/benchmark_methodes_$(date +%Y%m%d_%H%M).log
```

**NE PAS continuer sans ces chiffres.**

---

## TÂCHE 2 — Implémenter brent_mpfr.c

Fichier : src/calculs/optimisation/c_modules/brent_mpfr.c

### Algorithme de Brent (Van Wijngaarden-Dekker-Brent)

Signature — IDENTIQUE à illinois_refine_adaptive avec prec_fast + prec_full :

```c
/*
 * brent_refine_adaptive — méthode de Brent 2 phases
 * Combine : sécante (rapide) + interpolation quadratique inverse + bissection (robuste)
 * Ordre de convergence : ~1.84 (superlinéaire)
 * Phase 1 : prec=prec_fast bits (64 → 1 limb mpfr → SIMD AVX2)
 * Phase 2 : prec=prec_full bits (80 → 35 dps garanti)
 * Avantage vs Illinois : ~3 iter au lieu de ~5 pour même précision (~×1.2)
 * Même coût/iter : 1 seule évaluation Z(t) par itération
 *
 * Signature identique à illinois_refine_adaptive pour drop-in replacement.
 */
double brent_refine_adaptive(
    double a,         // borne gauche du bracket
    double b,         // borne droite du bracket
    double fa,        // Z(a) pré-calculé côté Python
    double fb,        // Z(b) pré-calculé côté Python
    double t,         // centre (a+b)/2 — utilisé pour N_termes RS
    int prec_fast,    // précision phase 1 (64 bits → 1 limb → SIMD)
    int prec_full,    // précision phase 2 (80 bits → 35 dps)
    int iter_switch,  // nb iter en phase 1 avant switch phase 2
    int max_iter      // max iter total
);
```

Logique interne Brent complète :
```c
// 1. Init : garantir |f(a)| >= |f(b)|
if (fabs(fa) < fabs(fb)) {
    swap(a, b); swap(fa, fb);
}
double c = a, fc = fa;
double s = b, fs = fb;
double d = 0.0, e = b - a;
bool mflag = true;
int prec_use = prec_fast;  // phase 1

for (int i = 0; i < max_iter; i++) {
    // Switch phase 2 après iter_switch itérations
    if (i == iter_switch) prec_use = prec_full;

    // Choisir méthode
    if (fa != fc && fb != fc) {
        // Interpolation quadratique inverse (IQI)
        s = a*fb*fc/((fa-fb)*(fa-fc))
          + b*fa*fc/((fb-fa)*(fb-fc))
          + c*fa*fb/((fc-fa)*(fc-fb));
    } else {
        // Sécante
        s = b - fb*(b-a)/(fb-fa);
    }

    // Conditions de sécurité → bissection
    bool cond1 = !((3*a+b)/4 < s && s < b);
    bool cond2 = mflag  && fabs(s-b) >= fabs(b-c)/2;
    bool cond3 = !mflag && fabs(s-b) >= fabs(c-d)/2;
    bool cond4 = mflag  && fabs(b-c) < TOL;
    bool cond5 = !mflag && fabs(c-d) < TOL;
    if (cond1 || cond2 || cond3 || cond4 || cond5) {
        s = (a + b) / 2.0;  // bissection
        mflag = true;
    } else {
        mflag = false;
    }

    // Évaluer Z(s) avec N_use termes et prec_use bits
    // (appel Z_rs_mpfr_ntermes identique à illinois)
    fs = Z_rs_mpfr_ntermes(s, N_use, prec_use);

    d = c; c = b; fc = fb;
    if (fa * fs < 0) { b = s; fb = fs; }
    else             { a = s; fa = fs; }
    if (fabs(fa) < fabs(fb)) { swap(a,b); swap(fa,fb); }

    // Convergence
    if (fabs(fb) < TOL || fabs(b-a) < TOL) return b;
}
return b;
```

Interface ctypes — MISE À JOUR avec prec_fast + prec_full :
```
restype  = c_double
argtypes = [c_double×5, c_int×4]
           (a, b, fa, fb, t, prec_fast, prec_full, iter_switch, max_iter)
```

---

## TÂCHE 3 — Créer compute_zeros_v9.py

```bash
cp src/calculs/optimisation/compute_zeros_v8.py \
   src/calculs/optimisation/compute_zeros_v9.py
# Modifier : docstring v9, PREFIX="v9", date 2026-06-12
```

Ajouter binding brent avec signature COMPLÈTE :

```python
# Binding brent_refine_adaptive
lib.brent_refine_adaptive.restype = ctypes.c_double
lib.brent_refine_adaptive.argtypes = [
    ctypes.c_double,  # a
    ctypes.c_double,  # b
    ctypes.c_double,  # fa
    ctypes.c_double,  # fb
    ctypes.c_double,  # t
    ctypes.c_int,     # prec_fast  (64)
    ctypes.c_int,     # prec_full  (80)
    ctypes.c_int,     # iter_switch
    ctypes.c_int,     # max_iter
]

# Appel avec fallback illinois
PREC_FAST   = 64
PREC_FULL   = 80
ITER_SWITCH = 3
MAX_ITER    = 30

try:
    zero = lib.brent_refine_adaptive(
        a, b, float(fa), float(fb),
        float((a+b)/2.0),
        PREC_FAST, PREC_FULL, ITER_SWITCH, MAX_ITER
    )
except Exception as e:
    logger.warning(f"brent échoué: {e} → fallback illinois")
    zero = lib.illinois_refine_adaptive(
        a, b, float(fa), float(fb),
        float((a+b)/2.0),
        PREC_FAST, PREC_FULL, ITER_SWITCH, MAX_ITER
    )
```

---

## TÂCHE 4 — Tests unitaires brent

```python
# Créer : src/calculs/optimisation/test_brent.py
# Test γ₁  ≈ 14.134725141734693  → erreur < 1e-10
# Test γ₁₀ ≈ 49.773832477672285  → erreur < 1e-10
# Test γ_grand à t≈77000          → erreur < 1e-10
# Comparer nb itérations Brent vs Illinois sur 100 zéros
# Afficher : iter_moy_brent vs iter_moy_illinois
```

```bash
python src/calculs/optimisation/test_brent.py \
  2>&1 | tee logs/test_brent_$(date +%Y%m%d_%H%M).log
```

---

## TÂCHE 5 — Benchmark comparatif T=5000

**Attendre fin run v8 avant de lancer.**

```
Config A : illinois_refine_adaptive (64,80) → référence v8
Config B : brent_refine_adaptive    (64,80) → v9 candidat

Tableau attendu :
  Méthode  | ms/appel | iter_moy | z/s T=5k | gain vs v8
  illinois | 0.416 ms | ~10      | baseline | ×1.00
  brent    | ?        | ~7 ?     | ?        | ×1.2 ?
```

**Décision go/no-go :**
- gain < ×1.05 → documenter, garder v8 stable, v9 = v8 + doc
- gain ≥ ×1.05 → valider T=10k (0 manquant, Turing COMPLET) puis T=100k

---

## TÂCHE 6 — Benchmark Arb acb_dirichlet_hardy_z (optionnel)

```python
# Comparer sur 500 appels dans [1000, 100000] :
# acb_dirichlet_hardy_z(t, prec=80) vs Z_rs_mpfr_ntermes(t, N, 80)
# Mesurer ms/appel à t=1k, 10k, 50k, 77k
# Si Arb < brent_mpfr sur tout t → envisager remplacement complet
```

---

## TÂCHE 7 — Validation T=10k v9 (si go)

```bash
nohup bash -c 'printf "10000\nO\n" | python \
  src/calculs/optimisation/compute_zeros_v9.py \
  2>&1 | tee logs/run_T10k_v9_$(date +%Y%m%d_%H%M).log' \
  > /dev/null 2>&1 &
```

Critères : 0 manquant, Turing COMPLET, LMFDB 19/20, durée < 3 min.

---

## TÂCHE 8 — Validation T=100k v9 (si T=10k ok)

```bash
nohup bash -c 'printf "100000\nO\n" | python \
  src/calculs/optimisation/compute_zeros_v9.py \
  2>&1 | tee logs/run_T100k_v9_$(date +%Y%m%d_%H%M).log' \
  > /dev/null 2>&1 &
```

Critères : 138 069 zéros, 0 manquant, Turing COMPLET, durée < 25 min.

---

## TÂCHE 9 — Documentation post-v9

Si Brent validé :
- `analyse_problemes_v8_v9.md` + PDF → wiki + Proton Drive
- `Formules_zeta.md §26` : Brent vs Illinois, formule convergence, tableau iter
- `JOURNAL.md` entrée 2026-06-12
- `STACK.md` ligne v9 avec durée mesurée
- Skills `phase-c-illinois/SKILL.md` → ajouter section Brent
- `index.html` → mettre à jour tableau performances v9
- Push wiki + Riemann_Lab_C + Riemann_Lab_IA
- Proton Drive via rclone

Si Brent non validé (gain < ×1.05) :
- `analyse_problemes_v8_v9.md` → section "Brent non retenu, raison"
- JOURNAL.md entrée 2026-06-12
- v9 = v8 rebaptisée + doc

---

## TÂCHE 10 — Commit v9

```bash
git add src/calculs/optimisation/c_modules/brent_mpfr.c \
        src/calculs/optimisation/c_modules/brent_mpfr.h \
        src/calculs/optimisation/c_modules/Makefile \
        src/calculs/optimisation/compute_zeros_v9.py \
        src/calculs/optimisation/benchmark_methodes.py \
        src/calculs/optimisation/test_brent.py
git commit -m "feat(v9): brent_refine_adaptive C/mpfr 2 phases (prec_fast=64, prec_full=80)"
git push origin Riemann_Lab_C
```

---

## RÈGLES ABSOLUES

- STEP = 0.010 fixe — NE JAMAIS MODIFIER
- Charger .so POST-FORK (GMP/MPFR ne se partagent pas cross-fork)
- Ne jamais `git add -A` (protège Handoff.md)
- Handoff.md : local `~/projet_zeta/handoff/`, jamais committer
- Valider T=10k (0 manquant, Turing COMPLET) AVANT T=100k
- NE PAS toucher compute_zeros_v8.py pendant run en cours
- Si Brent gain < ×1.05 → garder v8 stable, documenter proprement
- /clear avant prompt v10
- Vérifier `alias | grep zeta` avant de fermer

---

## RAPPEL MATHÉMATIQUE (Formules_zeta.md §25)

Pourquoi Brent est le seul avantage réel sur ce CPU :

$$t_{\text{eval}}(t) \approx 42\text{ ms à } t=77k \gg t_{\text{overhead arithmétique}}$$

| Méthode | Ordre | Évals/iter | Gain iter | Coût total | Verdict |
|---------|-------|-----------|-----------|------------|---------|
| Newton  | 2     | 2         | ×2        | neutre     | ✗       |
| Halley  | 3     | 3         | ×3        | neutre     | ✗       |
| Illinois| 1.44  | 1         | —         | baseline   | ✓ v8    |
| **Brent**| **~1.84** | **1** | **~×1.4** | **×1.2** | **✅ v9** |

Brent converge en ~3 iter vs ~5 pour Illinois → même coût/iter (1 éval Z) → gain net ~×1.4 local, ~×1.2 global.

Gain estimé v9 : ×1.2 → **~24 min T=100k** (vs 30.9 min v7, vs ~29 min v8)

Gain cumulé v1→v9 estimé : **×5 250 → ~×6 300**

---

*prompt_v9_brent_ameliorations.md · scripts/ia_prompts/ · Riemann_Lab_C · hprzeta · MAJ 2026-06-12*
