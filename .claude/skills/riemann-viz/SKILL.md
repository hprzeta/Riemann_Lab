---
name: riemann-viz
description: "Graphiques cohérents du projet Riemann_Lab : Z(t) de Hardy avec zéros marqués, module de zeta sur la droite critique, histogrammes d'écarts (lien avec riemann-statistics-gue), coloration de domaine de zeta et de xi. Utiliser quand hprzeta demande de tracer, visualiser, représenter ou exporter une figure PNG ou PDF sur zeta, Z(t), les zéros ou leurs écarts. matplotlib sans écran, palette daltonienne, légende datée avec nombre de zéros. Réutilise les fonctions du dépôt. Ne pas utiliser pour calculer des zéros ni pour des graphiques sans rapport avec zeta."
---

# riemann-viz

Version : 1.0 · MAJ : 2026-11-28

Skill autonome côté PC1. Côté claude.ai, le skill `dataviz` complète pour le style, sans être requis.

## Règles de calcul

- **Réutiliser** les fonctions existantes de `src/calculs/optimisation/` (par ex. `theta_fast`, `Z_fast` dans `theta_rapide.py`). Vérifier leur signature par lecture avant usage ; **ne pas les réécrire**. Formules canoniques : voir `CLAUDE.md` (θ(t), Z(t) de Hardy en un seul appel de ζ).
- Détecter les zéros par changement de signe de $Z(t)$, jamais par $\text{Re}\,\zeta(\tfrac12+it)$ seul (faux positifs).
- Environnement : `source ~/projet_zeta/zeta_env/bin/activate`, `PYTHONPATH` incluant `src`.

## Règles graphiques

- `import matplotlib; matplotlib.use("Agg")` avant `pyplot` (mode sans écran).
- `plt.savefig(..., dpi=150)` puis `plt.close()` ; **jamais** `plt.show()`.
- Sortie : **PNG et PDF** dans le dossier de rapports du sujet (`pdf/<sujet>/`, branche `Riemann_Lab_IA` seulement ; jamais `docs/` ni `ops/*`).
- Palette lisible par les daltoniens (ex. Okabe–Ito) ; ne pas coder l'information par la seule couleur (marqueurs/styles différents).
- Axes **nommés** avec unités ($t$, $Z(t)$, $|\zeta(\tfrac12+it)|$) ; formules en KaTeX/mathtext compatible, pas de `\operatorname` (utiliser `\text`).
- **Légende / pied de figure** : date, version du pipeline ou du script, **nombre de zéros** tracés et fichier source.

## Figures

1. **Z(t) de Hardy** : courbe, zéros marqués (points sur l'axe $Z=0$), plage $t$ choisie par l'utilisateur.
2. **$|\zeta(\tfrac12+it)|$** sur la droite critique, échelle linéaire ou log.
3. **Histogramme des écarts** normalisés (unfolding : voir `riemann-statistics-gue`), avec courbe de référence GUE (conjecture de Montgomery / Odlyzko : comparaison **numérique**, pas une preuve).
4. **Coloration de domaine** de $\zeta$ et de $\xi$ : teinte = argument, luminosité = $\log|f|$.

## Limites (mesurer, ne pas inventer)

- mpmath est lent sur un tableau complexe : **grille plafonnée** (par ex. 800 × 800), calcul **mis en cache** en `.npy` (nom contenant la fonction, la fenêtre, la taille de grille) ; relire le cache avant de recalculer.
- Machine à 8 Go : traiter par blocs de lignes.
- Ne pas annoncer de durée ou de gain sans mesure ; sinon « *non vérifiée* » (règle D20).

## Statuts

Une figure illustre ; elle ne prouve rien. Écrire sous la figure « vérifié numériquement » ou « illustration », jamais « démontré ».
