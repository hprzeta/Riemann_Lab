# Rapport d'analyse — liens « Lire → » vers les chapitres de Formation-Zeta-HR (12/11/2026 13:59)

> Rédigé sur claude.ai (projet SITE ZETA). Aucune modification faite. Source : constat de hprzeta (capture du 12/11), `HANDOFF_SITE_20261112.md` (13:52). Prompt associé : `PROMPT_CORRECTION_ANCRES_FORMATION_20261112_1359.md`.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Lien « Lire → » chapitre 11 | 🔴 | capture hprzeta : URL `…/wiki/Formation-Zeta-HR#ch11`, page affichée en haut (titre et sommaire) | D17 |
| Comportement avant | 🟡 | selon hprzeta, le lien arrivait au bon chapitre ; date du changement inconnue | à établir à l'étape 2 |
| D16 « 0 ancre morte » | 🟡 | la cible existe (`<a name>`), mais le défilement n'a pas été testé : l'outil de navigation de Claude Code ne défile pas, même vers une ancre à `id` classique (session de 13:49) | test de défilement fait par hprzeta |
| Page wiki `Formation-Zeta-HR` | 🟡 | capture : « edited this page on Sep 13 · 1 revision » : pas de changement récent visible | à confirmer à l'étape 2 |

## 2. Causes possibles (non prouvées)

| # | Hypothèse | Comment la vérifier |
|---|---|---|
| H1 | Nos commits du 12/11 ont changé les liens du site | comparaison avec `pdf/archive/index.html.bak-*` et `git log -S` |
| H2 | GitHub ne défile plus vers une ancre `<a name="chN">` (il la renomme en `user-content-chN`) | tester les liens du sommaire et l'ancre automatique du titre |
| H3 | La page s'allonge après le saut (formules, images) et la position est perdue | `scrollY` relevé après 3 s, puis après rechargement |
| H4 | La traduction automatique de Chrome réécrit la page | tester avec la traduction désactivée |

## 3. Décision

| # | Décision |
|---|---|
| D17 | Corriger les liens « Lire → » pour qu'ils arrivent au bon chapitre ; la solution (a, b ou c) est choisie après la preuve de la cause |

## 4. Tableau de modifications (à faire)

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| `docs/index.html` (liens « Lire → », 4 branches) | forme de lien qui arrive au chapitre (selon le diagnostic) | `…/wiki/Formation-Zeta-HR#chN` | À FAIRE |

## 5. Non vérifié depuis claude.ai
- La cause exacte : aucune des hypothèses H1 à H4 n'est prouvée.
- Le nombre exact de liens « Lire → » (environ 14, un par chapitre).

---
*RAPPORT_ANALYSE_ANCRES_FORMATION_20261112_1359.md · projet SITE ZETA · hprzeta · MAJ 12 novembre 2026 13:59 · 40 lignes*
