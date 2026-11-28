---
name: riemann-explicit-formula
description: "Tester numériquement la formule explicite de von Mangoldt avec les zéros non triviaux déjà calculés par Riemann_Lab : comparer psi(x) exact (crible) à la somme tronquée sur les zéros de partie imaginaire au plus T, mesurer l'erreur en fonction de T. Utiliser pour reconstruire psi(x) ou pi(x) à partir des zéros, vérifier un fichier de zéros par un test indépendant, ou explorer la formule de Riemann R(x) et la série de Gram. Ne pas utiliser pour calculer les zéros eux-mêmes, ni pour conclure sur l'hypothèse de Riemann."
---

# riemann-explicit-formula

Version : 1.0 · MAJ : 2026-11-28

## Statuts à afficher dans chaque sortie

| Énoncé | Statut |
|---|---|
| Formule explicite de von Mangoldt | **théorème** |
| Accord numérique observé | **vérifié numériquement** (pas une preuve) |
| Conclusion sur l'hypothèse de Riemann | **aucune** : ce test ne la prouve ni ne l'infirme |

## Formule (théorème)

Pour $x>1$ qui n'est pas une puissance d'un nombre premier, avec $\psi(x)=\sum_{n\le x}\Lambda(n)$ :

$$\psi(x)=x-\sum_{\rho}\frac{x^{\rho}}{\rho}-\ln(2\pi)-\tfrac12\ln\!\left(1-x^{-2}\right)$$

où la somme porte **symétriquement** sur les zéros non triviaux $\rho=\tfrac12+i\gamma$ : on regroupe $\rho$ et $\bar\rho$, soit un terme réel $2\,\text{Re}\!\left(x^{\rho}/\rho\right)$ par zéro de $\gamma>0$. Convergence conditionnelle : la somme tronquée à $|\gamma|\le T$ est une approximation.

## Procédure

1. **Entrées** : lire le chemin du fichier de zéros dans la configuration/Handoff du dépôt ; **ne rien coder en dur**. Si introuvable, demander.
2. **ψ(x) exact** par crible (numpy) pour $x$ modéré (par exemple jusqu'à quelques millions, choisi selon la RAM).
3. **Somme tronquée** : pour une suite de $T$ croissants, calculer $\psi_T(x)=x-2\sum_{0<\gamma\le T}\text{Re}\,(x^{\rho}/\rho)-\ln 2\pi-\tfrac12\ln(1-x^{-2})$ ; mesurer $|\psi(x)-\psi_T(x)|$ en fonction de $T$, pour plusieurs $x$ non puissances de premiers (éviter les sauts de ψ).
4. **Comportement attendu de l'erreur** : cf. Davenport, *Multiplicative Number Theory*, ch. 17. **À vérifier dans le texte avant toute citation** : ne rien affirmer de mémoire sur la forme de la borne.
5. **Option, marquée « expérimental »** : $R(x)=\sum_{n\ge1}\frac{\mu(n)}{n}\,\text{li}(x^{1/n})$ et série de Gram, comparées à $\pi(x)$. La version avec zéros complexes demande de la prudence sur les branches de li (zéros dans le plan complexe) : ne pas présenter de résultat comme acquis.

## Traçabilité obligatoire (en tête de chaque sortie)

- fichier de zéros utilisé (nom, SHA-256) ;
- nombre de zéros réellement utilisés ;
- validation connue de ce fichier (Turing, LMFDB) — la lire, ne pas la supposer ;
- si le fichier concerné est celui du run 5·10⁶ : le journal signale **10 016 297 zéros sur 10 016 474 attendus** (déficit de 177) pour le run V16 ; relire `md/optimisation/analyse_problemes_v16_v17.md` et le Handoff pour savoir quel jeu est la référence actuelle, avant de citer un nombre.

## Précision et mémoire

- `mpmath` pour $x^{\rho}/\rho$ (précision dépendant de $\gamma\ln x$ ; choisir `mp.dps` en conséquence), jamais `joblib` avec mpmath.
- Machine à **8 Go** : traiter par **blocs** de zéros, accumuler en flottant étendu, ne jamais charger tout le fichier si inutile (`np.memmap` / lecture par plages).
- Sorties graphiques : se référer au skill `riemann-viz`.

## Interdits

Ne pas présenter l'accord numérique comme une preuve ; ne pas conclure sur HR ; ne pas modifier les fichiers de zéros.
