# PROMPT CLAUDE CODE — Riemann_Lab Phase C / Voie B / v5

Tu es Claude Code exécuté sur la machine Linux `zeta-lab` dans le dépôt `~/projet_zeta`, branche `Riemann_Lab_C`.

## Mission principale
Améliorer la Phase C pour atteindre l’objectif : **Illinois C pur fiable**, puis préparer une montée de tests jusqu’à **T=10000**.

## Contexte projet
Le projet Riemann_Lab/hprzeta calcule expérimentalement les zéros non triviaux de ζ(s). Il ne prétend jamais prouver l’hypothèse de Riemann. Il distingue toujours : calcul expérimental, validation numérique, documentation, conjecture, preuve formelle.

## État validé à ce jour
- `c_modules` compile correctement : `make clean && make` produit `illinois_mpfr.so`.
- `test_illinois.py` passe sur les 10 premiers zéros en mode hybride.
- `benchmark_illinois.py` mesure un gain isolé C/libmpfr d’environ ×48.73 face à mpmath.findroot sur t≈500–638.
- `compute_zeros_v4.py` fonctionne sur T=80, T=300 et T=650.
- Turing-Backlund est complet sur les runs T=80/T=300/T=650 : aucun zéro manquant.
- LMFDB reste à 19/20 sous 1e-10, avec le zéro #20 à environ 8.06e-10.
- Tous les runs v4 utilisent 100 % `Illinois_C→mpmath` : `Illinois_C` pur est à 0 %.

## Cause technique identifiée
`compute_zeros_v4.py` accepte `gamma_c` comme `Illinois_C` pur seulement si :

```python
abs(float(mpmath.siegelz(gamma_c))) < 1e-8
```

Le diagnostic `phase_c_gamma_c_vs_mpmath.txt` montre que `gamma_c` produit par `illinois_mpfr.so` est trop éloigné du vrai zéro `mpmath.siegelz` :

- moyenne |delta gamma_c - gamma_true| ≈ 9.17e-03 ;
- médiane |delta| ≈ 8.35e-03 ;
- max |delta| ≈ 2.53e-02 ;
- plus petit `abs(mpmath.siegelz(gamma_c))` ≈ 5.30e-04, très au-dessus du seuil 1e-8.

Conclusion : ne pas assouplir le seuil. Il faut réduire le biais entre `Z_mpfr` / `Z_double` et `mpmath.siegelz`.

## Fichiers importants
- `src/calculs/optimisation/compute_zeros_v4.py`
- `src/calculs/optimisation/c_modules/illinois_mpfr.c`
- `src/calculs/optimisation/c_modules/z_function.c`
- `src/calculs/optimisation/c_modules/Makefile`
- `src/calculs/optimisation/c_modules/test_illinois.py`
- `src/calculs/optimisation/c_modules/benchmark_illinois.py`
- `src/calculs/optimisation/riemann_siegel_batch.py`
- `src/calculs/optimisation/theta_rapide.py`
- `src/calculs/optimisation/turing_validation.py`

## Travail demandé — étape 1 : diagnostic comparatif
Créer un script de diagnostic non destructif :

`src/calculs/optimisation/c_modules/diagnostic_zmpfr_vs_mpmath.py`

Ce script doit produire un CSV avec colonnes :

```text
t, Z_double, Z_mpfr, mpmath_siegelz, abs_Zdouble_minus_mpmath, abs_Zmpfr_minus_mpmath, gamma_c, gamma_true, delta_gamma, residu_c
```

Échantillonner :
- autour des 20 premiers zéros ;
- autour de t≈300 ;
- autour de t≈500–650 ;
- éventuellement autour de t≈1000.

Objectif : caractériser précisément le biais de la fonction C.

## Travail demandé — étape 2 : revue math/code
Auditer précisément :
- `theta_double` et `theta_mpfr` ;
- formule du terme de reste Riemann-Siegel C0+C1 ;
- signe `(-1)^(N-1)` ;
- convention `N = floor(sqrt(t/(2π)))` ;
- cohérence entre `Z_double`, `Z_mpfr`, `riemann_siegel_batch.py` et `mpmath.siegelz` ;
- correction Illinois : vérifier si la correction anti-stagnation doit être symétrique selon le côté stagnant.

## Travail demandé — étape 3 : patch expérimental v4b/v5
Ne casse pas `compute_zeros_v4.py` validé. Créer une branche ou des fichiers expérimentaux :

- `compute_zeros_v5.py` ou `compute_zeros_v4b.py` ;
- éventuellement `z_function_v2.c` / `illinois_mpfr_v2.c` si nécessaire ;
- garder `v4` comme référence hybride validée.

## Travail demandé — étape 4 : critères d’acceptation
Avant tout T=10000, il faut obtenir :

1. `make clean && make` OK ;
2. `test_illinois.py` OK ;
3. `benchmark_illinois.py` OK ;
4. `gamma_c` avec `abs(mpmath.siegelz(gamma_c)) < 1e-8` sur une proportion significative ;
5. run T=650 avec `Illinois_C` pur > 0 % ;
6. Turing complet ;
7. LMFDB stable ;
8. seulement ensuite T=1000, puis T=10000.

## Contraintes absolues
- Ne pas prétendre prouver RH.
- Ne pas supprimer les runs validés.
- Ne pas casser v4 validée.
- Ne pas assouplir arbitrairement le seuil 1e-8.
- Ne pas lancer T=10000 avant validation v5 sur T=650 et T=1000.
- Produire des logs reproductibles et des CSV de diagnostic.

## Livrables attendus
- patch clair ou nouveaux fichiers v5 ;
- CSV diagnostic ;
- log `make/test/benchmark` ;
- log run T=650 v5 ;
- rapport court Markdown : `docs/phase_c_voie_b_v5_plan.md`.
