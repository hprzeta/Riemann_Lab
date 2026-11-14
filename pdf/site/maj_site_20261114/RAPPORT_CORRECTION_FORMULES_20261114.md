# Rapport — correction des formules non rendues du wiki (14/11/2026)

Prompt : `PROMPT_CORRECTION_FORMULES_WIKI_20261114.md`. Dépôt : wiki `Riemann_Lab.wiki`, branche `master`, sans `--force`.

## 1. Validation

| Contrôle | Résultat |
|---|---|
| Zones rouges avant (9 pages) | 🟡 21 détectées au lieu de 20 : la 21ᵉ est le titre de Ch05 (texte brut), à corriger sur décision de hprzeta |
| Zones rouges après (9 pages + index) | 🟢 0 (HTML serveur) ; rendu à l'écran 0 en erreur : Ch01 113 · Ch02 83 · Ch03 60 · Ch05 48 · Ch07 40 · Ch08 21 · Ch11 43 · Ch12 73 · Ch13 32 formules rendues |
| Index, ligne du chapitre 5 | 🟢 après 2ᵉ commit (la syntaxe `` $`…`$ `` échouait dans un texte de lien) |
| Liens internes (Ch13 : 10 liens) | 🟢 tous répondent |
| Console navigateur | 🟢 aucune erreur |
| Pieds de page | 🟢 « Mis à jour le 14 novembre 2026 », nombre de lignes inchangé |
| Secrets (IP, MAC, clé, jeton, e-mail) | 🟢 audit des lignes ajoutées : rien |
| Détecteur `verif_formules_wiki.js` | 🟡 réécrit (original introuvable), non validé hors des pages testées |
| Captures | 🟡 avant : 8 pages (pas Ch08) ; après : 10 pages ; format JPEG |
| Pages nouvelles (10, balayage 89 pages) | 🟡 non traitées (décision hprzeta : « laisse les autres ») |
| Points 🟡 optionnels Y1 à Y3 | 🟡 non lancés (pas de « go 🟡 ») |

## 2. Tableau horodaté (page | ligne in | ligne out | date heure)

Commit `382c030` (13/11/2026 23:46). Syntaxe `` $`…`$ `` : les formules des lignes listées passent de `$…$` à `` $`…`$ ``.

| Page | Lignes modifiées | Nature | Date heure |
|---|---|---|---|
| Formation-Zeta-HR-Ch01 | 66, 132, pied | formules protégées ; date | 13/11/2026 23:46 |
| Formation-Zeta-HR-Ch02 | 5, 76, 102, pied | idem | 13/11/2026 23:46 |
| Formation-Zeta-HR-Ch03 | 5, 59, pied | idem | 13/11/2026 23:46 |
| Formation-Zeta-HR-Ch05 | 3 (titre), 5, pied | titre : `|e^{iθ}|=1` et `|n⁻ˢ|` → formules protégées | 13/11/2026 23:46 |
| Formation-Zeta-HR-Ch07 | 33, pied | formules protégées | 13/11/2026 23:46 |
| Formation-Zeta-HR-Ch08 | 47, pied | idem | 13/11/2026 23:46 |
| Formation-Zeta-HR-Ch11 | 37, pied | idem | 13/11/2026 23:46 |
| Formation-Zeta-HR-Ch12 | 59, pied | idem | 13/11/2026 23:46 |
| Formation-Zeta-HR-Ch13 | 47, pied | idem | 13/11/2026 23:46 |
| Formation-Zeta-HR (index) | 17, pied | titre du chapitre 5 | 13/11/2026 23:46 |
| Formation-Zeta-HR (index) | 17 | titre en HTML léger `|e<sup>iθ</sup>|=1 et |n<sup>−s</sup>|` (commit `c81894c`) | 13/11/2026 23:51 |

Le PDF ne code pas les couleurs (vert/rouge) : pas de mise en forme colorée dans cette version.

## 3. Points ouverts
- 10 pages nouvelles à décider : `analyse_problemes_v1_v16` (24 zones), `JOURNAL` (8), `analyse_problemes_v4_1_v5` (5), `Tableau-Symboles-Mathematiques` (4), `knowledge_base_obj2` (3), `STACK` (2), `analyse_math_deficit_2026-08-18` (1), `analyse_problemes_v8_v9` (1), `Katex-cheatsheet` (1). Voir `DIAGNOSTIC_FORMULES_WIKI_20261114.md`.
- Les liens dont le texte contient une formule `` $`…`$ `` en fin de lien ne se rendent pas : à éviter dans le wiki.
- Valider le détecteur JS sur plus de pages si on le garde.

---
*Mis à jour le 2026-11-14 — 47 lignes*
