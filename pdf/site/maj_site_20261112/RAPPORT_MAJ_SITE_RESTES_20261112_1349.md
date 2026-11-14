# Rapport — restes ouverts du 12/11/2026 (D14, D15, D16)

> Exécution du prompt `PROMPT_MAJ_SITE_RESTES_20261112_0227.md`. Aucun `--force`. Test automatique du jour : `RAPPORT_TEST_AUTO_MAJ_SITE_20261112_0101.md` affiché à hprzeta, ses propositions n'ont pas été appliquées (à analyser sur claude.ai).

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| D14 — ligne « Dernière mise à jour » du wiki `Etape-1…` | 🟢 | commit wiki `2a93821`, poussé (`f481583..2a93821`) ; le 12/11 est en tête, 532 lignes = `wc -l` | — |
| D15 — classe `grid5` | 🟢 | site en ligne : 1 élément `.grid5`, 5 colonnes de 146,4 px (identique à l'avant) ; 390 px : 2 colonnes, `scrollWidth` = `clientWidth` (376 = 376) | — |
| D16 — ancres `#…` | 🟢 | 31 ancres, 31 cibles trouvées (tableau 2) | défilement réel non démontrable par l'outil (voir §4) |
| Liens du site | 🟢 | 32 URL distinctes (hors fragments), toutes en 200 ; 58 liens au total | — |
| Console / réseau | 🟢 | console vide ; 49 requêtes, 0 ≥ 400 | — |
| KaTeX | 🟢 | 0 `.katex-error`, 53 formules rendues, 0 formule brute | — |
| Pied du site | 🟢 | « mis à jour le 12/11/2026 » | — |
| Audit avant commit | 🟢 | lignes ajoutées (wiki et site) : aucune IP, MAC, clé, token ni e-mail | — |

## 2. Ancres (D16)

| Lien | Page | Cible trouvée | Preuve |
|---|---|---|---|
| 6 ancres `Bibliotheques#…` | wiki | oui (6/6) | `id="user-content-…"` |
| 11 ancres `Formules_zeta#…` | wiki | oui (11/11) | `id="user-content-…"` |
| `Formation-Zeta-HR#ch1` à `#ch14` | wiki | oui (14/14) | `<a name="user-content-chN">` (pas d'`id`) |

Aucune ancre morte, aucune ancre corrigée. Aucune ancre interne au site (`#section`).

## 3. Modifications

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| wiki `Etape-1-Calcul-des-zéros-non-triviaux.md` l. 532 | `Dernière mise à jour : **12 novembre 2026** (phrase du rescan alignée sur V17.md) · 11 novembre 2026 — ajout v16 et V17 (…) · … · 12 septembre 2026 (correction rendu KaTeX) — 532 lignes` | `Dernière mise à jour : **11 novembre 2026** — ajout v16 et V17 (…) · … · 12 septembre 2026 (correction rendu KaTeX) · 12 novembre 2026 (phrase du rescan alignée sur V17.md) — 532 lignes` | 12/11/2026 13:49 |
| `docs/index.html` l. 1438 | `<div class="grid5" style="display: grid; grid-template-columns: repeat(5, 1fr); …">` | `<div style="display: grid; grid-template-columns: repeat(5, 1fr); …">` | 12/11/2026 13:49 |
| `docs/index.html` l. 567 (CSS mobile) | `.grid5 { grid-template-columns: repeat(auto-fit, minmax(90px, 1fr)) !important; }` | `div[style*="repeat(5, 1fr)"] { grid-template-columns: … }` | 12/11/2026 13:49 |

## 4. Commits, sauvegardes, limites
- Wiki (`master`) : `2a93821`. Site : IA `ac54d06`, C `f9aa7c2`, main `c685d52`, Test `260ff13` (cherry-pick -x). SHA-256 de `docs/index.html` identique sur les 4 branches (`aa29c369…d561cb`). Local = origin, sans `--force`.
- Sauvegardes : `pdf/archive/Etape-1-Calcul-des-zéros-non-triviaux.md.bak-202611121344` et `pdf/archive/index.html.bak-202611121345`.
- Décision D14 : l'option « réordonner la ligne » a été retenue (« go correction » sans précision). Le wiki n'a pas d'en-tête séparé : une seule ligne fait office d'en-tête et de pied.
- Limite : le défilement réel vers une ancre n'est pas démontrable avec la navigation de l'outil (même une ancre à `id` classique reste à `scrollY` 0) ; seule l'existence de la cible est prouvée. Le test à 390 px se fait dans une iframe de 390 px, pas sur un vrai téléphone.
- Limite : le suivi console n'est actif qu'à partir de son premier appel ; la lecture « console vide » porte sur un chargement fait après ce premier appel.

## 5. Captures (`captures/`)
`d14_avant_pied.jpg` · `d15_avant_grille5.jpg` (rouge) · `d15_apercu_local_grille5.jpg` · `d15_apres_grille5.jpg` (vert). Pas de capture « après » du wiki : la ligne du pied n'est pas recapturée.

---
*RAPPORT_MAJ_SITE_RESTES_20261112_1349.md · projet SITE ZETA · hprzeta · MAJ 12/11/2026 · 47 lignes*
