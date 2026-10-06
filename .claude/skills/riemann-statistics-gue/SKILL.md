---
name: riemann-statistics-gue
description: |
  Analyse statistique des zéros non-triviaux calculés par `Riemann_Lab` de hprzeta — écarts normalisés, corrélation de paires de Montgomery, comparaison GUE vs Poisson (Étape 2 de la roadmap).

  Utiliser ce skill dès que l'utilisateur demande de :
  - Calculer ou interpréter les écarts normalisés entre zéros consécutifs (unfolding, densité locale N(t))
  - Étudier la corrélation de paires (pair correlation) et la comparer à la conjecture de Montgomery
  - Comparer la distribution des écarts à l'ensemble unitaire gaussien (GUE) vs une distribution de Poisson
  - Produire des visualisations (histogrammes d'écarts, fonction de corrélation de paires, comparaison de densités)
  - Toute question sur "Étape 2" de la roadmap (analyse statistique des 10M+ zéros déjà calculés)

  Déclencher aussi pour : lien avec la théorie des matrices aléatoires (RMT), tests de Kolmogorov-Smirnov sur la distribution des écarts.
---

# Riemann Statistics GUE Skill

Skill d'analyse statistique pour `Riemann_Lab` — exploite le CSV des zéros déjà calculés
(actuellement ~10M à T≈5M, voir `synthese_skills_zeta.md` §3ter pour les chiffres de production
réels) pour tester la conjecture de Montgomery-Odlyzko : la distribution locale des zéros de ζ(s)
suit statistiquement celle des valeurs propres de matrices aléatoires unitaires (GUE).

> Prérequis pédagogique : ce skill présuppose la connaissance de N(t) (fonction de comptage) et
> de θ(t) (fonction de Riemann-von Mangoldt), déjà couvertes par `riemann-lab`. Toujours rappeler
> les définitions avant d'utiliser les formules ci-dessous si l'utilisateur ne les a pas sous les
> yeux (niveau débutant → expert, progression graduée).

---

## 1. Rappels théoriques nécessaires

**Écarts normalisés (unfolding).** Si `γ_n` est le n-ième zéro non-trivial (`ζ(1/2 + iγ_n) = 0`),
la densité locale des zéros croît avec `t` selon :
N(T) ≈ (T / 2π) log(T / 2π) − T / 2π + 7/8 + S(T)


L'écart **normalisé** (unfolded) est défini par : δ_n = (γ_{n+1} − γ_n) · (log(γ_n / 2π) / 2π)


Cette normalisation ramène la densité moyenne des écarts à 1, ce qui rend les `δ_n` comparables
entre eux quelle que soit la hauteur `t` — condition nécessaire pour toute comparaison statistique.

**Conjecture de Montgomery (corrélation de paires, 1973).** La fonction de corrélation de paires
des zéros normalisés converge (conjecturalement, sous HdR) vers :

R₂(x) = 1 − (sin(πx) / πx)²


C'est exactement la forme de la corrélation de paires des valeurs propres du GUE (Gaussian Unitary
Ensemble) — d'où l'intérêt de la comparaison. **Statut : conjecture**, appuyée par des vérifications
numériques massives (Odlyzko notamment) mais non démontrée.

**GUE vs Poisson.** Si les zéros étaient distribués "au hasard" sans corrélation (Poisson), on
observerait `R₂(x) = 1` (pas de répulsion). L'observation empirique constante depuis Odlyzko (années
1980) est une forte **répulsion des niveaux** (`R₂(x) → 0` quand `x → 0`), cohérente avec GUE et
incompatible avec Poisson — un argument heuristique fort en faveur de HdR, pas une preuve.

## 2. Méthodologie numérique

1. **Charger** le CSV des zéros (`csv/zeros_v16_*.csv` ou équivalent — vérifier la version/date
   avant tout calcul, cf. anomalie de comptage documentée en §3ter/§6 de `synthese_skills_zeta.md`).
2. **Valider la complétude** de la plage étudiée (Turing-Backlund) avant toute statistique — un
   zéro manquant fausse localement les écarts adjacents.
3. **Unfold** les écarts avec la formule ci-dessus (utiliser `mpmath` pour `log`/précision cohérente
   avec le reste du pipeline).
4. **Histogramme des écarts** normalisés, à comparer visuellement à la densité de Wigner-Dyson
   (GUE) et à la densité exponentielle (Poisson).
5. **Corrélation de paires empirique** `R₂(x)` sur une fenêtre `x ∈ [0, 3]` typiquement, avec
   binning adapté à la taille de l'échantillon (peu de zéros → binning grossier, risque de bruit
   trompeur — le signaler).
6. **Test quantitatif** (Kolmogorov-Smirnov ou Anderson-Darling) contre la distribution GUE
   théorique, avec p-value reportée sans sur-interprétation (rejeter Poisson n'est pas confirmer
   GUE avec certitude).

## 3. Code Python pédagogique — squelette

```python
import numpy as np
import pandas as pd
import mpmath as mp

def charger_zeros(path_csv: str) -> np.ndarray:
    """Charge les zéros gamma_n depuis le CSV de production (colonne 'gamma')."""
    df = pd.read_csv(path_csv)
    return df["gamma"].to_numpy()

def ecarts_normalises(gammas: np.ndarray) -> np.ndarray:
    """Unfolding : delta_n = (gamma_{n+1} - gamma_n) * log(gamma_n / 2pi) / (2pi)."""
    ecarts_bruts = np.diff(gammas)
    facteur = np.log(gammas[:-1] / (2 * np.pi)) / (2 * np.pi)
    return ecarts_bruts * facteur

def correlation_paires_empirique(deltas_cumules: np.ndarray, x_max: float = 3.0, nb_bins: int = 60):
    """Estimation empirique de R2(x) par comptage de paires à distance x sur la droite unfoldée."""
    # Implémentation de référence : voir Odlyzko (1987, 2001) pour la méthode de binning.
    ...
```

*(squelette volontairement incomplet — à compléter avec l'utilisateur selon le CSV réellement
disponible ; ne pas halluciner de valeurs numériques tant que le fichier n'a pas été inspecté.)*

## 4. Garde-fous

- **Ne jamais annoncer une confirmation de HdR** : une bonne adéquation empirique à GUE est un
  indice statistique, pas une preuve — le rappeler systématiquement dans les conclusions.
- Vérifier la **complétude Turing-Backlund** de la plage avant toute statistique fine (un zéro
  manquant décale tous les écarts locaux autour de lui).
- Croiser tout résultat qui semble original ou surprenant avec `riemann-literature-scout`
  (Montgomery/Odlyzko et travaux ultérieurs) avant de le présenter comme une observation nouvelle.
- En cas d'échantillon petit (quelques milliers de zéros), signaler explicitement le risque de
  bruit statistique avant toute comparaison quantitative (KS-test peu puissant à petit N).

## 5. Articulation avec les autres skills

- Données sources → pipeline `riemann-lab` / `phase-c-illinois` (calcul des zéros).
- Résultats théoriques de référence → `riemann-literature-scout`.
- Validation croisée des zéros avant analyse → `riemann-lmfdb-cross-validation`.

---
*Skill créé le 27/09/2026 — Vague V2 du plan de mutualisation skills/MCP (voir `synthese_skills_zeta.md` §4.2, item 3 ; correspond à l'Étape 2 de la roadmap).*
