# Synthèse — Analyse globale v4.1 → v6

> **Fichier :** analyse_problemes_v4_1_v6_synthese.md
> **Dossier :** wiki racine
> **Branche :** master (wiki)
> **Auteur :** hprzeta · **MAJ :** 2026-06-11

---

## Résumé — 4 versions, 1 objectif : T=100 000, 0 manquant

| Version | Problème résolu | Résidu |
|---|---|---|
| **v4.1** | Z_batch bugué (N_max fixe→masque) | vitesse 1.1 z/s, step_pour_t trop grand |
| **v5** | Phase C illinois_C pur 100 % (×30 Illinois) | STEP δ/3 → 2072 manquants à T=100k |
| **v5.1 (fix)** | STEP adaptatif + overlap=2.0 + segmentation 1/√t | 356 manquants encore (T=100k v1) |
| **v6** | scan_arb.c + STEP=0.010 + N(T) bissection | **0 manquant, Turing COMPLET ✅** |

---

## 1. v4.1 → v5 : le mur de latence mpmath

**Problème :** `illinois_mpfr.c` utilisé en Option A (appel Python pour chaque itération)
→ overhead ctypes ~30 µs × 8 itérations × 138k zéros = inutilisable.

**Solution v5 (Option B) :** boucle C complète `illinois_refine(a, b, fa, fb, ...)`.
PREC=170 bits, 10/10 LMFDB, gain ×30.78. Commit `581e34d`.

**Formule Illinois (rappel) :**
$$c = b - Z(b)\cdot\frac{b-a}{Z(b)-Z(a)}, \quad \text{si } Z(a)Z(c)<0 : b\leftarrow c \text{ sinon } a\leftarrow c,\ Z(a)\mathrel{\times}=0.5$$

---

## 2. v5 → v5.1 : STEP trop grand (356 manquants)

**Problème :** STEP fixe 0.1 trop grand pour les gaps GUE. Run T=100k v1 (10 juin) :
137 904 zéros, 356 manquants, 1h58.

**Solution v5.1 (10 juin, session 1) :** STEP adaptatif + overlap=2.0.
Test T=10k : 0 manquant, Turing COMPLET. Commits `7467731`, `50837f7`.

**Insuffisant à T=100k :** STEP=δ/3≈0.22 → 2 072 manquants (run v4 STEP δ/3).

---

## 3. v5.1 → v6 : STEP GUE + scan C

**Problème racine :** la règle STEP=δ/3 ignore la queue de la loi de Wigner.
Le gap minimal mesuré ($\approx 0.019$ à $t \approx 66\,678$) est ×11 inférieur à δ/3.

**Solution v6 (10 juin, session 2) :**

| Composant | Avant | v6 |
|---|---|---|
| Détection | `Z_vect_correct` numpy | `scan_arb.c` Z_double C pur |
| STEP | δ/3 ≈ 0.22 @ T=100k | **0.010 fixe** |
| Segmentation | 1/√t approximatif | N(T) par bissection |

**Règle de sécurité STEP :**
$$\text{STEP}_{\text{safe}} \leq \frac{\delta_{\min}}{2} \approx \frac{0.019}{2} \approx 0.0095 \quad \Rightarrow \quad \text{STEP} = 0.010$$

Résultat : **138 069 zéros, 0 manquant, Turing COMPLET ✅** (run 10 juin ~20h41–22h34).

---

## 4. Tableau de gains cumulés v4.1 → v6

| Axe | v4.1 | v5 | v6 |
|---|---|---|---|
| Illinois (ms/zéro) | ~170 ms | **5.5 ms (×30)** | 5.5 ms |
| Détection (% CPU) | ~40 % | ~15 % | **~6 % (×7.5 scan C)** |
| Manquants T=100k | — | 2072 ❌ | **0 ✅** |
| STEP | 0.022 adaptatif | δ/3 (0.22) | **0.010 fixe** |
| Vitesse globale z/s | 1.1 | ~6 | **~8 (T=10k)** |

---

## 5. Architecture v6 — schéma de flux

```
[Segment t_min→t_max]
         │
         ▼
   scan_arb.c (C)
   Z_double arb_fpwrap
   STEP=0.010
   → brackets [a,b] avec Z(a)·Z(b)<0
         │
         ▼
   illinois_mpfr.c (C)
   PREC=170 bits
   tol=1e-12, maxsteps=80
   → γ raffiné (51 décimales)
         │
         ▼
   validation Python
   LMFDB + Turing-Backlund
```

---

## 6. Analyse des erreurs — tableau complet T=100 000

| Run | Date | STEP | Zéros | Manquants | Turing | Durée |
|---|---|---|---|---|---|---|
| v4 ref | 2026-05-31 | δ/3~0.22 | 135 997 | 2 072 | ❌ | — |
| v5.1 v1 | 2026-06-10 | 0.1/0.05/0.02 | 137 904 | 356 | ❌ | 1h58 |
| **v6 final** | **2026-06-10** | **0.010** | **138 069** | **0** | **✅** | **1h53** |

---

## 7. Formules clés utilisées en v6

**Nombre de zéros attendu :**
$$N(T) = \frac{T}{2\pi}\ln\frac{T}{2\pi e} + 1 + S(T) \approx 138\,069 \text{ pour } T=100\,000$$

**Segmentation par bissection :** trouver $T_k$ tel que $N(T_k) = k\cdot N_{\text{total}}/W$ via dichotomie sur $N(T)$.

**STEP safe :** $0.010 \leq \delta_{\min}/2 \approx 0.019/2 = 0.0095$ — vérifié sur 10 000 premiers zéros LMFDB.

**Coût Illinois :** $T_{\text{illinois}} \approx n_{\text{zeros}} \times n_{\text{iter}} \times N_{\text{termes}}(t) \times 1.1\,\text{ms} / W$

---

## 8. Leçons durables

1. **STEP basé sur δ seul est insuffisant** — utiliser la distribution GUE pour estimer le gap minimal.
2. **scan_arb.c Z_double est fiable** (arb_fpwrap, 0 malloc heap) — pas besoin de mpfr pour la détection.
3. **N(T) par bissection** garantit un équilibrage de charge < 3 % d'écart.
4. **illinois_C = 83 %** — le vrai bottleneck est l'affinage multi-précision, pas la détection.
5. **Option B illinois** (boucle C complète) est incontournable pour les performances.

---

## 9. Questions ouvertes pour v7

1. Réduire PREC 170→100 bits (valider LMFDB < 1e-10 sur 20 premiers)
2. N_termes adaptatif : schéma 2-phases dans `illinois_mpfr.c`
3. STEP=0.010 suffisant jusqu'à T=500 000 ? (gap_min décroît comme $\sqrt{t}^{-1}$)
4. LMFDB #20 (t≈77.14, 8e-10) : corriger ou documenter comme limite RS 2 termes

---

## Voir aussi

- [[analyse_problemes_v4_1_v5]] — v4.1→v5 en détail
- [[analyse_problemes_v5_v6]] — v5→v6 en détail
- [[Formules_zeta]] §19/§20/§21
- [[Bibliotheques]] §12 — tous les runs
- [animation_gaps_gue.html](https://hprzeta.github.io/Riemann_Lab/animation_gaps_gue.html)
- [animation_ntermes_rs.html](https://hprzeta.github.io/Riemann_Lab/animation_ntermes_rs.html)

---
*analyse_problemes_v4_1_v6_synthese.md · wiki racine · branche master · hprzeta · MAJ 2026-06-11 · 115 lignes*
