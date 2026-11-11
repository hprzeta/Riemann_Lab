# Corrections wiki Riemann_Lab — rendu KaTeX + liens cassés
**Date : 2026-09-12** · Auteur du diagnostic : Claude (claude.ai) · À appliquer par : Claude Code
**Repo wiki :** `git clone https://github.com/hprzeta/Riemann_Lab.wiki.git`

## Cause racine (prouvée en local avec KaTeX)
GitHub Flavored Markdown supprime le `\` devant la **ponctuation ASCII** même à l'intérieur
des délimiteurs math `$…$` et `$$…$$`. Donc :
- `\_`  →  `_` nu  →  KaTeX : *"'_' allowed only in math mode"*
- `\#`  →  `#` nu  →  KaTeX : *"macro parameter character # ... in math mode"*

**Règle permanente à retenir :** ne jamais utiliser `\_` ni `\#` dans une formule math destinée
au wiki GitHub. Remplacer l'underscore par un tiret dans `\text{…}`, et `\#` par une lettre
indicée (`n_{\text{…}}`). (Idem `\;`, `\,` : à éviter, GitHub les mange aussi → utiliser des
espaces normaux.)

## A. Corrections de formules — 14 occurrences, 8 fichiers
Ces remplacements de jetons sont **uniques et sûrs** : le motif `X\_Y` (backslash-underscore)
n'existe que dans les `\text{}` math ; le code inline écrit `X_Y` sans backslash et n'est pas touché.

```bash
# Depuis la racine du clone du wiki :
sed -i 's/\\text{gap\\_moyen}/\\text{gap-moyen}/g'                 "Etape-1-Calcul-des-zéros-non-triviaux.md"
sed -i 's/\\text{biais\\_RS}/\\text{biais-RS}/g'                   "Etape-1-Calcul-des-zéros-non-triviaux.md"
sed -i 's/\\text{Illinois\\_C}/\\text{Illinois-C}/g'              "Formules_zeta.md"
sed -i 's/\\text{SEUIL\\_1NEWTON}/\\text{SEUIL-1NEWTON}/g'        "Formules_zeta.md"
sed -i 's/\\text{MARGE\\_SECURITE}/\\text{MARGE-SECURITE}/g'      "STACK.md"
sed -i 's/\\text{MARGE\\_SECURITE}/\\text{MARGE-SECURITE}/g'      "analyse_math_deficit_2026-08-18.md"
sed -i 's/\\text{TOL\\_ARB}/\\text{TOL-ARB}/g'                    "analyse_math_deficit_2026-08-18.md"
sed -i 's/\\text{rs\\_double}/\\text{rs-double}/g'                "analyse_problemes_v10_v12.md"
sed -i 's/\\text{mpfr\\_cos}/\\text{mpfr-cos}/g'                  "analyse_problemes_v7_v8.md"
sed -i 's/\\text{utilisation\\_CPU}/\\text{utilisation-CPU}/g'    "analyse_problemes_v9_v10.md"
sed -i 's/\\text{Illinois\\_C}/\\text{Illinois-C}/g'             "session_20260606.md"
```

Pour le `\#` (Formules_zeta), remplacer les 3 formules "nombre de chiffres" :
- L404 : `\#\text{chiffres} \;\gtrsim\; \log_{10}(\gamma) \;+\; 10`
        → `n_{\text{chiffres}} \gtrsim \log_{10}(\gamma) + 10`
- L909 : `\#\text{chiffres} \;\gtrsim\; \log_{10}(\gamma) + 10`
        → `n_{\text{chiffres}} \gtrsim \log_{10}(\gamma) + 10`
- L407 : `$\#\text{chiffres} \gtrsim 14$`
        → `$n_{\text{chiffres}} \gtrsim 14$`

```bash
sed -i 's/\\#\\text{chiffres} \\;\\gtrsim\\; \\log_{10}(\\gamma) \\;+\\; 10/n_{\\text{chiffres}} \\gtrsim \\log_{10}(\\gamma) + 10/g' "Formules_zeta.md"
sed -i 's/\\#\\text{chiffres} \\;\\gtrsim\\; \\log_{10}(\\gamma) + 10/n_{\\text{chiffres}} \\gtrsim \\log_{10}(\\gamma) + 10/g'       "Formules_zeta.md"
sed -i 's/\$\\#\\text{chiffres} \\gtrsim 14\$/\$n_{\\text{chiffres}} \\gtrsim 14\$/g'                                                 "Formules_zeta.md"
```

### NE PAS TOUCHER
`Tableau-Symboles-Mathématiques.md` L267–269 : `\#\{…\}` est du **code inline** (entre backticks),
affiché littéralement, non rendu → il fonctionne. Y toucher casserait l'affichage voulu.

## B. Liens cassés — DÉCISION UTILISATEUR REQUISE
`Structure-Projet-Complet.md` :
- L129 `[[Étape-2-Visualisations-avancées]]`  → page inexistante
- L130 `[[Étape-3-Intelligence-artificielle]]` → page inexistante

Deux options (à confirmer par hprzeta AVANT modification) :
- **(a) Créer** les pages `Étape-2-Visualisations-avancées.md` et
  `Étape-3-Intelligence-artificielle.md` (sur le modèle d'`Etape-1`).
- **(b) Rediriger** les liens vers l'existant :
  L129 → `[[Animations]]` ; L130 → `[[Guide-Ollama-Pratique]]` ou `[[Guide-RAG-BrainVault-Debutant]]`.

## C. Pieds de page
Sur **chaque page modifiée** (A + B), ajouter à la ligne de mise à jour existante :
`· 12 septembre 2026 (correction rendu KaTeX : \_ et \# — GitHub retirait le backslash en mode math)`

## D. Vérification finale (après édition)
```bash
# Plus aucun \_ dans un \text{} rendu, ni \# hors code inline :
grep -rnoE '\\text\{[^}]*\\_[^}]*\}' *.md      # doit ne rien renvoyer
grep -rn '\\#\\text' *.md                       # doit ne rien renvoyer
# Puis commit + push, et contrôle visuel des 10 pages en ligne.
```
