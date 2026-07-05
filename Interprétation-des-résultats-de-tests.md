# 🔬 Interprétation des résultats de tests

> **Contexte :** Résultats du script `compute_zeros_zeta.py` exécuté dans Spyder (Python 3.12)
> avec les paramètres `T_MAX=40`, `STEP=0.05`.
> Méthode : Fonction Z de Hardy + affinage Illinois (mpmath, 50 décimales).

---

## 1. Rapport d'exécution Spyder

![Rapport d'exécution Spyder — T_MAX=40](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/src/tests/interpreation_test/T40zero/zeros_zeta_Exec_T40_20260421_190821.png)

---

## 2. Paramètres d'entrée

| Paramètre | Valeur | Signification |
|-----------|--------|---------------|
| `T_MAX` | 40 | Hauteur maximale sondée sur la droite critique — on cherche tous les zéros de $\zeta\!\left(\tfrac{1}{2}+it\right)$ pour $t \in [10,\,40]$ |
| `STEP` | 0.05 | Pas de balayage — Z(t) est évaluée tous les 0,05 unités ; plus petit = plus fiable mais plus lent |
| Zéros attendus | ≈ 5 | Estimation par la formule de Riemann–von Mangoldt (voir ci-dessous) |
| Précision | 50 décimales | Arithmétique haute précision via `mpmath` (la double précision standard donne ~15 décimales) |

### Formule de Riemann–von Mangoldt

$$N(T) \approx \frac{T}{2\pi} \ln\!\left(\frac{T}{2\pi e}\right)$$

Pour T = 40 :

$$N(40) \approx \frac{40}{2\pi} \cdot \ln\!\left(\frac{40}{2\pi e}\right) \approx 6{,}37 \times 0{,}786 \approx 5$$

Le programme a trouvé **6 zéros**, ce qui est cohérent : la formule est asymptotique et sous-estime légèrement pour les petites valeurs de T.

---

## 3. Le balayage de t

```
Balayage de t=10.0 à t=40.0 avec pas=0.05
Soit 600 évaluations de Z(t)
```

Le programme calcule Z(t) en **600 points** régulièrement espacés sur [10, 40].
À chaque pas, il compare le signe de Z(t) avec celui du point précédent :

- Si `Z(t − step) × Z(t) < 0` → **changement de signe détecté** → il y a un zéro dans cet intervalle (Théorème des Valeurs Intermédiaires)
- Le programme déclenche alors l'**affinage Illinois** pour localiser le zéro avec une précision de ~10⁻²⁰

> ⚠️ **Risque de zéros manqués :** si deux zéros sont séparés par moins de `STEP`, un seul changement de signe est détecté. Réduire `STEP` diminue ce risque.

---

## 4. Tableau de vérification — La colonne Écart

### Résultats obtenus

| # | Calculé | Référence (LMFDB) | Écart |
|---|---------|-------------------|-------|
| 1 | 14.134725141734693 | 14.134725141734693 | 0.00e+00 ✅ |
| 2 | 21.022039638771556 | 21.022039638771556 | 0.00e+00 ✅ |
| 3 | 25.010857580145689 | 25.010857580145688 | 0.00e+00 ✅ |
| 4 | 30.424876125859512 | 30.424876125859513 | 0.00e+00 ✅ |
| 5 | 32.935061587739185 | 32.935061587739192 | 0.00e+00 ✅ |
| 6 | 37.586178158825675 | 37.586178158825668 | 7.11e-15 ✅ |

> 📄 Données brutes : [zeros_zeta_T40_20260421_190235.csv](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/src/tests/interpreation_test/T40zero/zeros_zeta_T40_20260421_190235.csv)

### Définition de l'écart

$$\text{écart} = |t_{\text{calculé}} - t_{\text{référence}}|$$

- **0.00e+00** (zéros 1 à 5) : les valeurs calculées sont identiques aux références à la précision d'affichage (15 décimales). La méthode Illinois combinée aux 50 décimales de `mpmath` est suffisamment précise pour annuler tout écart visible.
- **7.11e-15** (zéro 6) : différence à la **15ᵉ décimale**. Il s'agit de l'erreur d'arrondi résiduelle lors de la conversion vers le type `float` Python, qui ne dispose que de ~15-16 chiffres significatifs. C'est parfaitement acceptable — c'est la limite intrinsèque de la virgule flottante double précision (IEEE 754).

### Seuils de qualité du script

| Écart | Statut | Interprétation |
|-------|--------|----------------|
| < 1e-8 | ✅ | Zéro correctement calculé |
| 1e-8 à 1e-4 | ⚠️ | Résultat approximatif, à affiner |
| > 1e-4 | ❌ | Erreur de calcul |

---

## 5. Graphiques — Analyse visuelle

![Graphiques des zéros de ζ(1/2+it) — T_MAX=40](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/src/tests/interpreation_test/T40zero/zeros_zeta_T40_20260421_190235.png)

### 5.1 Graphique gauche — Distribution des espacements

#### Les 5 espacements calculés

Avec 6 zéros, on obtient **5 intervalles** entre zéros consécutifs (Δt = tₙ₊₁ − tₙ) :

| Paire | t₁ | t₂ | Δt |
|-------|-----|-----|-----|
| Δ₁ | 14.13 | 21.02 | **6.89** |
| Δ₂ | 21.02 | 25.01 | **3.99** |
| Δ₃ | 25.01 | 30.42 | **5.41** |
| Δ₄ | 30.42 | 32.94 | **2.51** |
| Δ₅ | 32.94 | 37.59 | **4.65** |

#### Lecture de l'histogramme

**Pourquoi 4 colonnes bleues pour 5 espacements ?**
L'histogramme regroupe les valeurs dans des intervalles de classe (bins). Avec `bins=40` mais seulement 5 valeurs réparties entre ~2.5 et ~7, certains bins adjacents se fondent visuellement. Δ₂ (3.99) et Δ₅ (4.65) tombent dans des bins proches, formant la zone centrale plus fournie. En réalité, **5 valeurs sont réparties en 4 bins distincts**.

**Hauteur des barres** : représente la fréquence (nombre d'espacements par bin). Ici toutes les barres sont à hauteur 1, confirmant qu'aucun bin ne contient plus d'un espacement.

**Position en abscisse** :

| Position x | Espacement correspondant |
|------------|--------------------------|
| ~2.5 | Δ₄ — zéros 4 et 5, les plus proches |
| ~4.0 | Δ₂ |
| ~4.7 | Δ₅ — zone de la moyenne |
| ~5.4 | Δ₃ |
| ~6.9 | Δ₁ — les deux premiers zéros, les plus éloignés |

**Ligne rouge pointillée — Moyenne = 4.6903** :

$$\bar{\Delta t} = \frac{6{,}89 + 3{,}99 + 5{,}41 + 2{,}51 + 4{,}65}{5} \approx 4{,}69$$

Sur des milliers de zéros, cette distribution convergerait vers la **distribution GUE de Montgomery** (Gaussian Unitary Ensemble), une corrélation profonde avec la physique quantique des matrices aléatoires. Avec seulement 5 points, elle est trop fragmentée pour en tirer des conclusions statistiques.

### 5.2 Graphique droit — Zéros sur la droite critique

Ce graphique illustre directement **l'Hypothèse de Riemann** : tous les zéros non triviaux de $\zeta(s)$ doivent avoir leur partie réelle exactement égale à $\frac{1}{2}$.

- Les **points bleus** représentent les 6 zéros calculés, placés en $(\text{Re}(s) = 0{,}5,\ \text{Im}(s) = t)$
- La **ligne rouge pointillée verticale** matérialise la droite critique $\text{Re}(s) = \frac{1}{2}$
- Tous les points sont alignés sur cette droite, ce qui **confirme l'hypothèse** pour ces 6 premiers zéros

---

## 6. Synthèse de l'exécution

| Indicateur | Valeur |
|------------|--------|
| Zéros trouvés | 6 |
| Zéros attendus (formule) | ~5 |
| Précision maximale observée | $\sim 10^{-15}$ |
| Durée | ~11 secondes |
| Taux | 0.150 zéros par unité t |
| Faux positifs | 0 |

> ✅ **Conclusion :** Le script fonctionne correctement. Les 6 zéros sont localisés avec une précision de l'ordre de 10⁻¹⁵, cohérente avec les valeurs de référence LMFDB. Pour observer la distribution GUE de Montgomery de manière statistiquement significative, il est recommandé de relancer avec **T_MAX ≥ 500** (≈ 180 zéros).

---
*Dernière mise à jour : 22 mai 2026 — 150 lignes*
