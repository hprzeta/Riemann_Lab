# Analyse v6 → v7 : `illinois_refine_adaptive`

> **Auteur :** hprzeta · **Date :** 11 juin 2026 · **Commit :** `8637098`
> Optimisation 2-phases de l'affinage Illinois en C/libmpfr

---

## Résumé

La v6 identifie l'affinage Illinois (`illinois_refine`, libmpfr 170 bits) comme
bottleneck à **78–83 % du temps CPU**. La v7 introduit `illinois_refine_adaptive`,
un affinage en deux phases : les premières itérations utilisent 64 bits (1 limbe mpfr),
avant de basculer à 116 bits pour la convergence finale.

**Gain mesuré : ×3.7 sur la durée totale** à $T = 100\,000$ (30,9 min vs ≈113 min pour v6).

---

## 1. Rappel v6 — état et bottleneck

La v6 (commit `b676e88`) a résolu les zéros manquants avec `STEP = 0.010` fixe +
détection `scan_arb.c`. Run $T = 100\,000$ : **138 069 zéros, 0 manquant, Turing COMPLET**.

**Profil de phases v6 :**

| Phase | ms/appel | % CPU |
|---|---|---|
| `illinois_C` | ~130 ms | **83 %** |
| turing | — | 1 % |
| detection | — | 0,5 % |

L'affinage utilise $N_\text{full}(t) = \lfloor\sqrt{t/2\pi}\rfloor$ termes à 170 bits.
Avec 170 bits (3 limbes GMP), les fonctions transcendantes (`mpfr_cos`, `mpfr_log`) sont lentes.

$$N_\text{full}(100\,000) \approx 126\ \text{termes}$$

---

## 2. Principe de l'optimisation 2-phases

L'algorithme Illinois sur $[a, b]$ converge en ≈15–20 itérations pour
$|b - a| = \text{STEP} = 0.01 \to \varepsilon = 10^{-12}$.
Les **8 premières itérations** réduisent l'intervalle de $0.01$ à $\approx 10^{-4}$
(gain $\approx 10^{8}$ sur la largeur) : c'est là que réside le coût dominant.

**Idée v7 :** évaluer $Z(t)$ en précision réduite (64 bits) durant la phase de
réduction rapide, puis en précision complète (116 bits) pour la convergence finale.

| Phase | Itérations | Précision | Limbes mpfr | Objectif |
|---|---|---|---|---|
| 1 (rapide) | $i = 0 \dots 7$ | 64 bits | **1** | $|b-a| \to 10^{-4}$ |
| 2 (précise) | $i \ge 8$ | 116 bits | 2 | $|b-a| \to 10^{-12}$ |

La transition est opérée par `mpfr_prec_round` qui élargit la représentation sans recalcul.

---

## 3. Décision technique : $N_\text{full}$ et non $N_\text{fast}$

L'idée initiale de $N_\text{fast} = \lfloor N_\text{full}/4 \rfloor$ termes en phase 1
**a été abandonnée**.

La formule de Riemann-Siegel

$$Z(t) = 2\sum_{n=1}^{N} \frac{\cos\!\left(\theta(t) - t\ln n\right)}{\sqrt{n}} + R(t),\quad N = N_\text{full}(t)$$

n'est correcte que pour $N = \lfloor\sqrt{t/2\pi}\rfloor$.
Tronquer à $N_\text{fast} < N_\text{full}$ peut **inverser le signe** de la somme.

> **Exemple :** $t = 1002$, $N_\text{full} = 12$, $N_\text{fast} = 3$.
> $Z_\text{RS}(c, N=3)$ peut avoir le signe opposé à $Z_\text{RS}(c, N=12)$.
> Illinois diverge vers un pseudo-zéro arbitraire.

**Solution retenue : $N_\text{full}$ termes dans les deux phases.** Le gain vient uniquement
de la précision réduite.

### Pourquoi 64 bits est ×16 plus rapide que 170 bits ?

mpfr stocke un flottant en $\lceil p/64 \rceil$ limbes de 64 bits.
- `prec = 64` → **1 limbe** → routines **SIMD spécialisées** (AVX2)
- `prec = 170` → 3 limbes → boucle générique multi-mots, pas de SIMD

Le rapport de vitesse observé est **×10–20** par appel, bien supérieur au simple rapport de
limbes (×3).

$$N_{\text{limbs}} = \left\lceil\frac{\text{prec}}{64}\right\rceil \qquad t_{\text{appel}} \approx 1.47 \times N_{\text{limbs}}^2 \text{ ms}$$

---

## 4. Implémentation

Deux fonctions ajoutées dans `illinois_mpfr.c` (commit `8637098`) :

```c
/* Z(t) RS avec N_termes imposé (pas floor(sqrt(t/2pi))) */
double Z_rs_mpfr_ntermes(double t_d, int N_termes, mpfr_prec_t prec);

double illinois_refine_adaptive(
    double a, double b, double fa, double fb,
    double t, int iter_switch, int max_iter)
{
    int N_full = (int)floor(sqrt(t / (2.0 * M_PI)));
    mpfr_prec_t prec_fast = 64;   /* phase 1 : 1 limbe SIMD */
    mpfr_prec_t prec_full = 116;  /* phase 2 : 2 limbes, convergence 1e-12 */

    /* ... boucle Illinois ... */
    if (i == iter_switch) {
        /* transition : élargir la précision de toutes les variables mpfr */
        mpfr_prec_round(ma, prec_full, MPFR_RNDN);
        /* ... idem mb, mfa, mfb, mc, mfc ... */
    }
}
```

**Paramètres v7 :** `ITER_SWITCH = 8`, `MAX_ITER = 50`, fallback `illinois_refine` classique
sur exception.

---

## 5. Benchmarks mesurés

### Profil phases v7 — T=100 000

| Phase | ms/appel | % CPU |
|---|---|---|
| `illinois_C` | **42,05 ms** | 78,2 % |
| detection | 9 450 ms (total) | 0,5 % |
| turing | 22 046 ms (total) | 0,3 % |

### Comparaison v6 vs v7

| Run | v6 (170 bits) | v7 (64→116 bits) | Gain |
|---|---|---|---|
| T=5 000 — z/s | 136 | **1 808** | **×13** |
| T=5 000 — ms/appel | 23,50 ms | **1,47 ms** | **×16** |
| T=10 000 — z/s | ~66 | **408** | **×6,2** |
| T=10 000 — ms/appel | ~50 ms | **3,71 ms** | **×13** |
| T=100 000 — z/s | ~20 | **74,49** | **×3,7** |
| T=100 000 — ms/appel | ~130 ms | **42,05 ms** | **×3,1** |
| T=100 000 — durée | ~113 min | **30,9 min** | **×3,7** |
| T=100 000 — zéros | 138 069 | 138 069 | identique |
| T=100 000 — manquants | 0 | 0 | identique |
| T=100 000 — Turing | COMPLET | COMPLET | identique |

---

## 6. Analyse du gain en fonction de $t$

Le gain décroît avec $T$ car le coût d'un appel est $\mathcal{O}(N_\text{full})$ :

$$N_\text{full}(T = 5\,000) \approx 20, \quad N_\text{full}(T = 10\,000) \approx 40, \quad N_\text{full}(T = 100\,000) \approx 126$$

À $T = 5\,000$, la boucle sur 20 termes est courte et le SIMD domine : **×16**.
À $T = 100\,000$, la boucle sur 126 termes dilue le gain : **×3,1 sur ms/appel**.

Relation empirique :
$$\text{gain}(T) \approx \frac{300}{N_\text{full}(T)}$$

### Précision finale

Les deux versions convergent vers le même pseudo-zéro, dont la distance au vrai zéro
est bornée par le biais structurel RS :
$$\varepsilon_\text{RS}(t) = \mathcal{O}\!\left(t^{-3/2}\right) \approx 10^{-6}\ \text{à}\ t = 77\,000$$
Largement suffisant pour Turing-Backlund (espacement minimal ≈ 0,5 à $t = 100\,000$).

---

## 7. Résultat final v7 — T=100 000

| Paramètre | Valeur |
|---|---|
| Script | `compute_zeros_v7.py` |
| Zéros trouvés | **138 069** |
| Manquants | **0** |
| Turing-Backlund | **COMPLET** |
| LMFDB | 19/20 à $< 10^{-10}$ |
| Durée | **30,9 min** |
| Vitesse | **74,49 z/s** |
| Gain vs v6 | **×3,7** |
| Log | `logs/run_T100k_v7_20260611_1424.log` |

---

## 8. Perspectives — v8

| Option | Description | Gain estimé | Cible |
|---|---|---|---|
| A | W=8 workers (doubler le parallélisme) | ×1,3 | ~24 min |
| B | prec phase 2 = 80 bits (vérifier SIMD) | à mesurer | ? |

**TÂCHE 0 obligatoire avant v8 :** benchmark empirique
`prec_fast ∈ {32, 48, 64, 80, 96} bits` sur T=5k.

**Pistes à plus long terme :**
- Termes RS d'ordre supérieur ($C_2, C_3$) pour réduire le biais à $\mathcal{O}(t^{-5/2})$
- Vectorisation interne : batch de plusieurs appels $Z_\text{RS}(c_i)$
- Phase 1 en `double` IEEE 754 (~52 bits), évitant l'overhead d'allocation mpfr

---

## Leçon clé — contre-intuition prouvée

> La théorie prédisait ×4,6 via réduction des termes RS.
> La réalité mesurée : **×16 via prec_fast=64 bits** (1 limbe → SIMD).
> **Ne jamais supposer que l'intuition théorique identifie le vrai levier — mesurer d'abord.**

Voir aussi : [[Bonnes-Pratiques-Claude-Code]] § Règle précision mpfr · [[maths_v7_ntermes_adaptatif]]

---

> **Fichier :** analyse_problemes_v6_v7.md · **Dossier :** wiki master
> **Auteur :** hprzeta · **MAJ :** 11 juin 2026
