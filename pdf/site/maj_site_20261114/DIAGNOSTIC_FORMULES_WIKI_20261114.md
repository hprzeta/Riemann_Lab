# Diagnostic formules non rendues — wiki (14/11/2026)

Lecture seule. Détecteur : `verif_formules_wiki.js` (réécrit le 14/11, non validé). Balayage : 89 pages (HTML récupéré sur GitHub), 71 « zones » brutes sur 19 pages. Captures « avant » : `captures/` (Ch01 à Ch13, sans Ch08).

## 1. Les 9 pages 🔴 connues : 21 zones (attendu 20 + le titre de Ch05)

| Page | Zones | Cause |
|---|---|---|
| Ch01 | 2 | A (italique) |
| Ch02 | 3 | A |
| Ch03 | 4 | A, B (`^*`) |
| Ch05 | 2 | A + **titre** `Chapitre 5 — Module |e^{iθ}|=1 et |n⁻ˢ|` (texte brut, à corriger : décision hprzeta 14/11) |
| Ch07 | 1 | C (parenthèse) |
| Ch08 | 4 | B |
| Ch11 | 1 | C |
| Ch12 | 1 | C |
| Ch13 | 3 | B |

## 2. Nouvelles pages (hors du bilan du 13/11) : 50 zones brutes, tri à confirmer

| Page | Zones | Constat probable (non vérifié ligne à ligne) | Corriger ? |
|---|---|---|---|
| Formation-Zeta-HR | 1 | même titre de Ch05 repris dans l'index | oui (avec le titre de Ch05) |
| analyse_problemes_v1_v16 | 24 | paragraphes entiers non rendus (formule cassée entraînant les voisines) | à voir sur la source |
| analyse_problemes_v4_1_v5 | 5 | `1/$\sqrt{t}$` : formule collée à `/` (cause C) | à décider |
| analyse_math_deficit_2026-08-18 | 1 | `$T{=}5$M` : formule collée à la lettre M | à décider |
| JOURNAL | 8 | `/$…$`, `–$0{,}08$` : formules collées (cause C) | à décider |
| STACK | 2 | à examiner | à décider |
| Tableau-Symboles-Mathematiques | 4 | `\sum_{d` coupé : barre `|` dans un tableau (cause D probable) | à décider |
| analyse_problemes_v8_v9 | 1 | `O(t^{-3/4})` : texte brut sans `$` | probablement non |
| knowledge_base_obj2 | 3 | `O(t^{-1/4})`, `10^{13}` : texte brut sans `$` | probablement non |
| Katex-cheatsheet | 1 | citation de `\text` dans une phrase (page de doc KaTeX) | non |

Limites : le balayage lit le HTML du serveur, il ne voit pas les erreurs de rendu côté navigateur. Les faux positifs « texte brut » (`^{`) sont possibles hors des 9 pages.

---
*Mis à jour le 2026-11-14 — 41 lignes*
