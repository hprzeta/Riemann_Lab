# Rapport — correction des formules non rendues, 6 pages du wiki (14/11/2026)

> Wiki `Riemann_Lab.wiki`, branche `master`, commits `81b0311` (14/11/2026 13:57), `1b608b2` (correctif JOURNAL, ligne vide avant `$$`) puis `85daa59` (v4_1_v5 ligne 197, pied de `niveau-0-prerequis`, date de `Methode`, règle KaTeX n°5 dans `STACK`), poussés sans `--force` (`c81894c..81b0311..1b608b2..85daa59`). Contrôle en ligne avec Claude in Chrome à 14:00, détecteur `verif_formules_wiki.js` (réécrit, non validé). Mesures avant : `mesure_vf_<page>.json`.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| analyse_problemes_v1_v16 | 🟢 | 24 zones rouges → 0 ; 47 formules rendues ; `.katex-error` 0 | Rien. |
| Tableau-Symboles-Mathematiques | 🟢 | 4 → 0 ; 340 rendues (337 + 3) ; `.katex-error` 0 | Rien. |
| analyse_math_deficit_2026-08-18 | 🟢 | 1 → 0 ; 153 rendues ; `.katex-error` 0 | Rien. |
| Optimisation-Pourquoi-le-calcul-va-vite | 🟢 | 70 formules rendues, 0 non rendue ; note « À vérifier avant le push » absente de la page ; `.katex-error` 0 | Rien. |
| analyse_problemes_v4_1_v5 | 🟢 | 5 → 1 après `81b0311`, **→ 0 après `85daa59`** ; 75 rendues ; `.katex-error` 0 ; console sans erreur | Rien. Ligne 197 corrigée (`\mathrm{STEP} = 0.22`, sens confirmé par hprzeta). |
| STACK | 🟢 | 2 → 1 ; 26 rendues ; `.katex-error` 0 ; console sans erreur ; règle n°5 visible en ligne après `85daa59`. La ligne 576 est corrigée. | Rien : la zone restante (ligne 693, prose sur la syntaxe) est un faux positif laissé par décision. |
| JOURNAL | 🟢 | 8 → 4 après `81b0311` ; **→ 2 après `1b608b2`** ; 87 rendues ; `.katex-error` 0 ; console sans erreur | Ligne 3199 corrigée : la ligne vide avant `$$` était bien la cause (mesuré). Les lignes 2776 et 4090 (textes bruts) sont closes par décision. |
| Console navigateur | 🟡 | Aucune erreur sur la page Optimisation. Le suivi de la console ne démarre qu'à son premier appel : les autres pages n'ont pas été couvertes. | À refaire si besoin. |
| Y1, Y2, Y3 | 🟢 | Voir `MESURE_FORMULES_20261114.md` : aucun défaut mesuré. Après `85daa59` : `niveau-0-prerequis` a son pied de page (265 lignes), `Methode` sa date du pied. | Description d'origine introuvable. |
| Pages exclues (`knowledge_base_obj2`, `analyse_problemes_v8_v9`, `Katex-cheatsheet`) | ⚪ | Non touchées, non remesurées. | Closes par décision de hprzeta. |

Bilan : sur les 9 pages non corrigées du diagnostic, **4 sont à 0 zone** (v1_v16, Tableau-Symboles, deficit, v4_1_v5 ; Optimisation, hors diagnostic, est aussi conforme), **2 gardent un reste clos par décision** (JOURNAL 2 zones de texte brut, STACK 1 faux positif) et **3 sont exclues** par décision.

## 2. Fichiers modifiés (page | ligne in | ligne out | date heure)

« in » = texte publié, « out » = texte remplacé. Heure : commit `81b0311`.

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| analyse_problemes_v1_v16 | 16, 47, 49, 70-71, 99, 102, 116-117, 130, 132, 134-135, 137, 139-142, 146-147, 163-164, 188, 204-205, 225, 280, 314, 322, 325, 370, 377-378, 382 : `` $`…`$ `` | les mêmes lignes en `\( … \)` (47 formules) | 14/11/2026 13:57 |
| analyse_problemes_v1_v16 | 416 (pied : date) | 416 | 14/11/2026 13:57 |
| Tableau-Symboles-Mathematiques | 100, 101 : `` $`\sum_{d \mid n} d^k`$ ``, `` $`\sum_{p \mid n} 1`$ `` ; 146 : `` $`\int_0^T \lvert\zeta(\tfrac{1}{2}+it)\rvert^{2k}\,dt`$ `` | cellules coupées par `\|` | 14/11/2026 13:57 |
| Tableau-Symboles-Mathematiques | 272 (pied : date) | 272 | 14/11/2026 13:57 |
| JOURNAL | 636, 638, 792-793, 3071 | formules collées, coupées ou non fermées | 14/11/2026 13:57 |
| JOURNAL | 3199-3202 : `$$` / formule / `$$`, ligne vide avant (`1b608b2`) | 3199 : `$$…$$` sur une ligne | 14/11/2026 13:57 puis 14:10 |
| JOURNAL | 4794 (pied : date, 4 794 lignes) | 4791 (4 791 lignes) | 14/11/2026 13:57 puis 14:10 |
| analyse_problemes_v4_1_v5 | 35, 152, 183, 213 : `` 1/$`\sqrt{t}`$ `` | `1/$\sqrt{t}$` | 14/11/2026 13:57 |
| analyse_problemes_v4_1_v5 | 227 (pied : date, 227 lignes) | « ~230 lignes » | 14/11/2026 13:57 |
| analyse_problemes_v4_1_v5 | 197 : `` ($`\delta_{\min} = 0.019 \ll \mathrm{STEP} = 0.22`$) `` ; pied : « ligne 197 comprise » | `($\delta_{\min} = 0.019 \ll $ STEP=0.22)` | 14/11/2026 (`85daa59`) |
| niveau-0-prerequis | 263-265 : pied de page standard (265 lignes) | aucun pied de page (262 lignes) | 14/11/2026 (`85daa59`) |
| Methode | 150 (pied : « 14 novembre 2026 (date du pied de page mise à jour) ») | `MAJ 2026-06-03 · 150 lignes` | 14/11/2026 (`85daa59`) |
| STACK | 42-44, 58-59 : « 5 causes », règle n°5 (`$$` précédé d'une ligne vide) ; pied : 708 lignes | « 4 causes », 4 règles ; pied : 706 lignes | 14/11/2026 (`85daa59`) |
| analyse_math_deficit_2026-08-18 | 117 : `` $`T{=}5\,\text{M}`$ `` ; 428 (pied : date) | `$T{=}5$M` | 14/11/2026 13:57 |
| STACK | 576 : `` $`Z(t)`$ `` ; 706 (pied : date) | `$Z(t)$` | 14/11/2026 13:57 |
| Optimisation-Pourquoi-le-calcul-va-vite | lignes 185-189 supprimées ; pied : 186 lignes, date | note de gabarit `[[ ]]` ; pied : 191 lignes | 14/11/2026 13:57 |

## 3. Points ouverts
- **Aucun point ouvert sur les formules.** JOURNAL 2776 et 4090-4091 (textes bruts), STACK 693 (faux positif) et les 3 pages exclues sont clos par décision.
- **Leçon :** un bloc `$$` doit être précédé d'une ligne vide, sinon il n'est pas rendu (mesuré sur JOURNAL 3199).
- Le détecteur n'est toujours pas validé ; les extraits des JSON sont tronqués et dégradés (`=` → `EGAL`).

---
*RAPPORT_CORRECTION_WIKI_20261114_1400.md · projet SITE ZETA · hprzeta · mis à jour le 14 novembre 2026 · 51 lignes*
