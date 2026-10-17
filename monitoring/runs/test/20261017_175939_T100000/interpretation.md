### Calcul

- **[mesuré]** 138 069 zéros pour T = 100 000, contre ≈ 138 068,6 par la formule de Riemann–von Mangoldt (écart +0,4). Score LMFDB 20/20 à moins de 10⁻⁹. Validation de Turing : « complet ».
- **[heuristique]** L'accord du comptage avec la formule indique qu'aucun zéro n'est manqué sur cet intervalle. Il ne le démontre pas : le rapport ne remplace pas une validation Turing–Backlund certifiée.

### Machine

- **[mesuré]** PC1 : température moyenne 69,7 °C, maximum 79,0 °C, 13 % du temps au-dessus de 75 °C. Fréquence médiane 3 000 MHz sur le 1ᵉʳ cinquième du run, 3 200 MHz sur le dernier. Charge maximale 14,49. Aucune erreur de lancement.
- **[hypothèse]** La fréquence basse en début de run (2 900 à 3 000 MHz) pourrait venir de la montée en température et de la charge simultanée des 4 threads. Aucune mesure ici ne l'établit : le run ne dure que 97 s de calcul.
- **[mesuré]** PC2 à PC5 sont restés inactifs (charge ≤ 0,3, température ≤ 46 °C) : le run n'a utilisé que PC1.

### Statistique des espacements

- **[mesuré]** Variance des espacements normalisés 0,1614 ; part des espacements inférieurs à 0,1 : 0,073 %.
- **[conjecture, Montgomery–Odlyzko]** Les espacements suivent la loi GUE. La répulsion observée est cohérente avec elle et très loin de Poisson (variance 1, part inférieure à 0,1 de 9,5 %).
- **[hypothèse]** L'écart entre 0,1614 et 0,18 s'expliquerait par des corrections de taille finie à ces hauteurs. Non vérifié ici.

### Limites de ce run

- **[mesuré]** La version v16 écrit le CSV de chaque worker seulement à la fin de ce worker : le débit instantané (`etat.csv`) vaut 0 presque partout et n'est pas exploitable. Seul le débit moyen (868 z/s) est fiable.
- **[mesuré]** Un seul run de test, un seul passage : aucune comparaison avec un autre run, donc aucune conclusion sur la variabilité d'un run à l'autre.

---
*interpretation.md · MAJ 2026-10-17 · 31 lignes*
