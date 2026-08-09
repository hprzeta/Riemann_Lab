# Prompt v9 — Brent C/mpfr + améliorations algorithmiques
**Date prévue :** 2026-06-12 matin
**Branche :** Riemann_Lab_C
**Après :** /clear + lire Handoff.md

---

## CONTEXTE

v8 VALIDÉE : prec_full=80 bits, ~29 min T=100k (plancher i7-7500U)
Gains algorithmiques restants sur ce CPU : ×1.2-1.3
Référence : ameliorations_v9.md (wiki) + Formules_zeta.md §25

Résultats benchmark v8 (2026-06-11) :
  illinois_refine_adaptive (64,80) : 0.416 ms/appel · ×1.06 vs v7
  W=8 : ×0.99 (context-switching dual-core HT) → W=4 optimal

---

## TÂCHE 0 — Run T=100k v8 (si pas encore fait)

```bash
ps aux | grep compute_zeros | grep -v grep
# Si aucun run actif → lancer :
nohup bash -c 'printf "100000\nO\n" | python \
  src/calculs/optimisation/compute_zeros_v8.py \
  2>&1 | tee logs/run_T100k_v8_$(date +%Y%m%d_%H%M).log' \
  > /dev/null 2>&1 &
echo "PID: $!"
# Monitor : Turing-Backlund, timeout 5400s
```

Durée estimée : ~29 min
Critères : 0 manquant, Turing COMPLET, ~79 z/s

---

## TÂCHE 1 — Benchmark T=5000 illinois vs méthodes alternatives

Avant d'implémenter, mesurer le comportement réel d'Illinois :

```python
# Ajouter dans benchmark_v8.py ou créer benchmark_methodes.py
# Mesurer sur 500 zéros dans [1000, 100000] :
# - Nombre d'itérations moyen par zéro
# - ms/appel moyen
# - Distribution des itérations (histogramme)
```

Lancer :
```bash
python src/calculs/optimisation/benchmark_methodes.py \
  2>&1 | tee logs/benchmark_methodes_$(date +%Y%m%d_%H%M).log
```

NE PAS continuer sans ces chiffres.

---

## TÂCHE 2 — Implémenter brent_mpfr.c

Fichier : src/calculs/optimisation/c_modules/brent_mpfr.c

### Algorithme de Brent (Van Wijngaarden-Dekker-Brent)

```c
/*
 * brent_refine_adaptive — méthode de Brent 2 phases
 * Combine : sécante (rapide) + bissection (robuste)
 * Ordre de convergence : ~1.84 (superlinéaire)
 * Phase 1 : prec=64 bits (1 limb, SIMD)
 * Phase 2 : prec=80 bits (35 dps garanti)
 * Avantage vs Illinois : convergence légèrement plus rapide (~×1.2)
 * Même coût/iter : 1 évaluation Z(t)
 */
double brent_refine_adaptive(
    double a, double b,
    double fa, double fb,
    double t,
    int iter_switch,
    int max_iter
);
```

Logique interne Brent :
```c
// Variables Brent
double s, d, e;
bool mflag;

// Initialiser : a=borne avec |f(a)| > |f(b)|
if (fabs(fa) < fabs(fb)) {
    swap(a, b); swap(fa, fb);
}
s = b; // point sécante
e = b - a;
d = e;
mflag = true;

for (int i = 0; i < max_iter; i++) {
    // Choisir méthode : sécante ou interpolation inverse
    if (fa != fs && fb != fs) {
        // Interpolation quadratique inverse
        s = a*fb*fc/((fa-fb)*(fa-fc))
          + b*fa*fc/((fb-fa)*(fb-fc))
          + c*fa*fb/((fc-fa)*(fc-fb));
    } else {
        // Sécante
        s = b - fb*(b-a)/(fb-fa);
    }
    // Conditions de sécurité → bissection si besoin
    // ...
    // Évaluer Z(s) avec N_use termes, prec_use bits
}
```

Interface ctypes identique à illinois_refine_adaptive :
  restype = c_double
  argtypes = [c_double×5, c_int×2]

---

## TÂCHE 3 — Modifier compute_zeros_v8.py → v9

```python
# Ajouter binding brent :
lib.brent_refine_adaptive.restype = ctypes.c_double
lib.brent_refine_adaptive.argtypes = [
    ctypes.c_double,  # a
    ctypes.c_double,  # b
    ctypes.c_double,  # fa
    ctypes.c_double,  # fb
    ctypes.c_double,  # t
    ctypes.c_int,     # iter_switch
    ctypes.c_int,     # max_iter
]

# Remplacer illinois_refine_adaptive par brent_refine_adaptive
# Garder illinois comme fallback
try:
    zero = lib.brent_refine_adaptive(
        a, b, float(fa), float(fb),
        float((a+b)/2.0), ITER_SWITCH, MAX_ITER
    )
except Exception as e:
    logger.warning(f"brent échoué: {e} → fallback illinois")
    zero = lib.illinois_refine_adaptive(...)
```

---

## TÂCHE 4 — Tests unitaires

```python
# Test γ₁ ≈ 14.1347
# Test γ₁₀ ≈ 49.7738
# Test γ_grand à t=77000
# Critère : erreur < 1e-10
# Comparer nb itérations Brent vs Illinois
```

---

## TÂCHE 5 — Benchmark comparatif T=5000

```
Config A : illinois_refine_adaptive (64,80) → référence v8
Config B : brent_refine_adaptive (64,80)    → v9

Tableau attendu :
  Method  | ms/appel | iter_moy | z/s T=5k | gain
  illinois| 0.416 ms | ~10      | baseline | ×1.00
  brent   | ?        | ~7 ?     | ?        | ×1.2 ?
```

Si gain < ×1.05 → documenter et garder illinois (v8 stable).
Si gain ≥ ×1.05 → valider sur T=10k puis T=100k.

---

## TÂCHE 6 — Benchmark Arb acb_dirichlet_hardy_z

```python
# Comparer sur 500 appels dans [1000, 100000] :
import flint
# acb_dirichlet_hardy_z(t, prec=80) vs Z_rs_mpfr_ntermes(t, N, 80)
# Mesurer ms/appel à t=1k, 10k, 50k, 77k
```

Si Arb < illinois_mpfr sur tout t → envisager remplacement.

---

## TÂCHE 7 — Nommage compute_zeros_v9.py

```bash
cp src/calculs/optimisation/compute_zeros_v8.py \
   src/calculs/optimisation/compute_zeros_v9.py
# Modifier : docstring v9, PREFIX="v9", date 2026-06-12
```

---

## TÂCHE 8 — Documentation post-v9

Si Brent validé :
- analyse_problemes_v8_v9.md + PDF
- Formules_zeta.md §26 (Brent vs Illinois sur Z(t))
- JOURNAL.md entrée 2026-06-12
- STACK.md ligne v9
- Etape-1 section v8→v9
- Skills mis à jour
- Push complet + Proton Drive
- Suivre workflow_post_version_riemann_lab.svg

---

## TÂCHE 9 — Commit v9

```bash
git add src/calculs/optimisation/c_modules/brent_mpfr.c \
        src/calculs/optimisation/c_modules/brent_mpfr.h \
        src/calculs/optimisation/c_modules/Makefile \
        src/calculs/optimisation/compute_zeros_v9.py
git commit -m "feat(v9): brent_refine_adaptive — Brent C/mpfr 2 phases"
git push origin Riemann_Lab_C
```

---

## RÈGLES ABSOLUES

- STEP = 0.010 fixe — NE JAMAIS MODIFIER
- Charger .so POST-FORK
- Ne jamais git add -A
- Handoff.md : local, jamais committer
- Valider T=10k (0 manquant, Turing COMPLET) avant T=100k
- Si Brent gain < ×1.05 → garder v8 stable, documenter
- /clear avant prompt v10
- Vérifier alias | grep zeta avant de fermer

---

## RAPPEL MATHÉMATIQUE (Formules_zeta.md §25)

Pourquoi Illinois reste compétitif vs méthodes d'ordre supérieur :

$$t_{\text{eval}}(t) \approx 42\text{ ms à } t=77k \gg t_{\text{overhead}}$$

Newton (ordre 2, 2 évals) : coût ×2, gain ×2 → neutre
Halley (ordre 3, 3 évals) : coût ×3, gain ×3 → neutre
Brent  (ordre ~2, 1 éval) : coût ×1, gain ×1.4 → ✅ seul avantage réel

Gain Brent estimé : ×1.2 → ~24 min T=100k (vs 29 min v8)

---

*prompt_v9_brent_ameliorations.md · scripts/ia_prompts/ · Riemann_Lab_IA · hprzeta · 2026-06-12*
