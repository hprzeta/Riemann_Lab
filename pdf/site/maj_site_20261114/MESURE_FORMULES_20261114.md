# Mesure des formules non rendues — 6 pages du wiki et Y1 à Y3 (14/11/2026)

> Lecture seule, Claude in Chrome sur les pages publiées. Aucune modification du wiki, aucun commit. Détecteur : `verif_formules_wiki.js` (réécrit, non validé). Résultats bruts : `mesure_vf_<page>.json` (6 fichiers). **Étape 1 terminée : STOP, j'attends « go corr ».**

## 1. Mesure (étape 1a)

| Page | Zones rouges | Formules rendues | `.katex-error` | Fichier JSON |
|---|---|---|---|---|
| analyse_problemes_v1_v16 | 24 (21 blocs) | 0 | 0 | `mesure_vf_analyse_problemes_v1_v16.json` |
| Tableau-Symboles-Mathematiques | 4 | 337 | 0 | `mesure_vf_Tableau-Symboles-Mathematiques.json` |
| JOURNAL | 8 | 82 | 0 | `mesure_vf_JOURNAL.json` |
| analyse_problemes_v4_1_v5 | 5 | 70 | 0 | `mesure_vf_analyse_problemes_v4_1_v5.json` |
| analyse_math_deficit_2026-08-18 | 1 | 152 | 0 | `mesure_vf_analyse_math_deficit_2026-08-18.json` |
| STACK | 2 | 25 | 0 | `mesure_vf_STACK.json` |

Les zones concordent avec le diagnostic de la nuit (24, 4, 8, 5, 1, 2). **Limite des JSON :** l'outil de navigation bloque les chaînes qui ressemblent à des paramètres d'URL ; les extraits sont donc tronqués (70 à 100 caractères) et les signes `=`, `&`, `?` y sont écrits `EGAL`, `ET`, `QQ`. Le nombre de blocs n'est relevé que pour `analyse_problemes_v1_v16`.

## 2. Y1 à Y3 (étape 1b)

| Point | Page | Capture | Console | `.katex-error` | Formules | Liens | Verdict |
|---|---|---|---|---|---|---|---|
| Y1 | `Methode` | prise (rendu correct) | aucune erreur | 0 | 1 `math-renderer`, rendue | 0 lien dans la source ; les 11 liens de la page sont les ancres de titres | **OK** |
| Y2 | `niveau-0-prerequis` | prise (rendu correct) | aucun message | 0 | 80 rendues, 0 non rendue | 1 lien dans la source, 🟢 | **OK**, 2 remarques mineures ci-dessous |
| Y3 | `animation_prec_mpfr.html` (site publié) | prise (rendu correct) | aucun message | 0 | 8 `.katex` | 5 liens (script de contrôles) tous 🟢 ; 2 liens `index.html` sur la page | **OK** |

Remarques mineures sur Y2, non traitées : la citation d'en-tête (2 lignes `>`) s'affiche sur une seule ligne, et la page n'a pas de pied de page (date, nombre de lignes). `Methode` a un pied de page cohérent (150 lignes, `wc -l` égal) mais sa date est ancienne (2026-06-03). **Je n'ai trouvé aucun défaut sur Y1, Y2 ni Y3** ; la description d'origine de ces points reste introuvable, donc un défaut que je n'ai pas mesuré (autre navigateur, mobile, lien externe) n'est pas exclu.

## 3. Tableau des anomalies (étape 1c)

Cause : « mesuré » = observé sur la page ; « hypothèse » = déduit du motif, non démontré. Correction proposée : syntaxe `` $`…`$ `` en inline, `\lvert…\rvert` en tableau (méthode validée sur 9 pages le 13/11).

| page | ligne source | extrait | cause | correction proposée |
|---|---|---|---|---|
| analyse_problemes_v1_v16 | 34 lignes : 16, 47, 49, 70, 71, 99, 102, 116, 117, 130, 132, 134, 135, 137, 139-142, 146, 147, 163, 164, 188, 204, 205, 225, 280, 314, 322, 325, 370, 377, 378, 382 | `(\varepsilon \approx C^2 \cdot t^{-5/2})`, `(5.0\times10^{-3})`… | mesuré : le fichier n'a aucun `$` et écrit ses formules avec `\( … \)`, que GitHub n'interprète pas (il affiche `( … )`) | remplacer chaque `\( … \)` par `` $`…`$ `` (remplacement mécanique, 34 lignes) |
| Tableau-Symboles-Mathematiques | 100 | `\$\sum\_{d \| n} d^k\$` (cellule coupée) | mesuré : barre `\|` non protégée dans une cellule de tableau | `$\sum_{d \mid n} d^k$` |
| Tableau-Symboles-Mathematiques | 101 | `\$\sum\_{p \| n} 1\$` | idem | `$\sum_{p \mid n} 1$` |
| Tableau-Symboles-Mathematiques | 146 | code `` `I_k(T) = \int_0^T \left\| \zeta\left(\frac12+it\right)\right\|^{2k} dt` `` | mesuré : barres `\|` dans un code en ligne, la cellule est coupée en 3 | `$I_k(T) = \int_0^T \lvert\zeta(\tfrac12+it)\rvert^{2k}\,dt$` |
| JOURNAL | 636 | `$\|\zeta(\rho)\|$/$\|\Lambda(\rho)-\Lambda(1-\rho)\|$` | mesuré : la 2ᵉ formule, collée à `/`, n'est pas rendue (la 1ʳᵉ l'est) ; hypothèse : adjacence `/$` | `` $`\lvert\Lambda(\rho)-\Lambda(1-\rho)\rvert`$ `` |
| JOURNAL | 638 | `$\Gamma$/$\theta$` | mesuré : `/$\theta$` non rendu ; même hypothèse | `` $`\theta`$ `` |
| JOURNAL | 792-793 | `$M_1(h)\approx` ⏎ `0{,}06$–$0{,}08$` | mesuré : la formule est coupée par un retour à la ligne, la fin `–$0{,}08$` reste brute | mettre `` $`M_1(h)\approx 0{,}06`$–$`0{,}08`$ `` sur une seule ligne |
| JOURNAL | 2776 | `ζ=e^{−iθ}Z` dans un tableau | mesuré : texte brut sans `$` | `` $`\zeta=e^{-i\theta}Z`$ `` (ou laisser : décision) |
| JOURNAL | 3071 | `$t<300 = $ seuil` | mesuré : `$` fermant précédé d'une espace, formule non fermée | `` $`t<300`$ = seuil `` |
| JOURNAL | 3199 | `$$\underbrace{138}_{\text{zéros}} \times …$$` sur une seule ligne | mesuré : 2 zones, la formule est tronquée ; hypothèse : `_{…}` lu comme italique (cause A du 13/11) | mettre `$$` seul sur sa ligne avant et après la formule |
| JOURNAL | 4090-4091 | `O(t^{-5/4})` | mesuré : texte brut sans `$` | `` $`O(t^{-5/4})`$ `` (ou laisser : décision) |
| analyse_problemes_v4_1_v5 | 35, 152, 183, 213 | `1/$\sqrt{t}$` | mesuré : non rendu (ligne 35 paragraphe, 152 titre h3, 183 tableau, 213 paragraphe) ; hypothèse : adjacence `/$`, comme dans JOURNAL | `` 1/$`\sqrt{t}`$ `` |
| analyse_problemes_v4_1_v5 | 197 | `($\delta_{\min} = 0.019 \ll $ STEP=0.22)` | mesuré : `$` fermant précédé d'une espace | `` ($`\delta_{\min} = 0.019 \ll 0.22`$) `` à valider (le sens de « ≪ STEP » est à confirmer) |
| analyse_math_deficit_2026-08-18 | 117 | `$s_0$ à $T{=}5$M` (en-tête de tableau) | mesuré : `$T{=}5$M` non rendu ; hypothèse : `$` fermant collé à la lettre `M` | `` $`T{=}5\,\text{M}`$ `` |
| STACK | 576 | `$Z(t)$` dans une citation | mesuré : formule non rendue ; **cause non établie** (rien d'évident autour) | `` $`Z(t)`$ `` puis recontrôle ; **vrai positif** |
| STACK | 693 | pied : « blocs $$ multi-lignes … adjacence $ sans espace » | prose qui décrit la syntaxe, pas une formule | **faux positif probable** : laisser tel quel (ou mettre `$$` et `$` en code) |

## 4. Correction hors zones : note `[[ ]]`

`Optimisation-Pourquoi-le-calcul-va-vite.md`, lignes 185-189 : à supprimer à l'étape 2, avec ajustement du pied de page. Les trois pages à ne pas toucher : `knowledge_base_obj2`, `analyse_problemes_v8_v9`, `Katex-cheatsheet`.

## 5. Points de décision pour « go corr »

1. Faut-il corriger les 2 textes bruts sans `$` de `JOURNAL` (lignes 2776 et 4090-4091) ? Ils sont de même nature que ceux de `analyse_problemes_v8_v9` et `knowledge_base_obj2`, que vous avez exclus.
2. `analyse_problemes_v4_1_v5` ligne 197 : sens exact de la formule à confirmer.
3. `STACK` ligne 576 : cause non établie, correction à valider par recontrôle après modification.
4. Pieds de page : `analyse_problemes_v4_1_v5` annonce `~230` lignes pour 227 ; `JOURNAL` annonce 4 791 (`wc -l` : 4791, cohérent). Leur nouvelle date et leur nombre de lignes seront mis à jour à l'étape 2.

---
*MESURE_FORMULES_20261114.md · projet SITE ZETA · hprzeta · mis à jour le 14 novembre 2026 · 63 lignes*
