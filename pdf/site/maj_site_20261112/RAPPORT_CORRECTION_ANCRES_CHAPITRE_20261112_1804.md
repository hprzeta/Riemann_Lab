# Rapport — D17 suite : « Lire → » arrive directement sur le chapitre — 12/11/2026

> Exécution de `PROMPT_CORRECTION_ANCRES_CHAPITRE_20261112_1536.md`. Aucun `--force`. Rapport précédent (15:31) corrigé : D17 y est marqué non résolu.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste |
|---|---|---|---|
| D17 : « Lire → » arrive sur le titre du chapitre | 🟢 | réponse de hprzeta : C (« C est ok », réponse globale, pas chapitre par chapitre) | — |
| Sommaire de la page wiki | 🟢 | hprzeta : « ça marche bien » | — |
| Pages wiki (sommaire + 14 chapitres) | 🟢 | 200 ; titre `Chapitre N` ; 0 erreur KaTeX ; 73 lignes `$$` avant = 73 après | — |
| Aucune perte de contenu | 🟢 | 542 lignes utiles de l'original retrouvées à l'identique et dans l'ordre dans les 14 pages | — |
| Site en ligne | 🟢 | 14 liens `Formation-Zeta-HR-ChNN` ; 0 `.katex-error` ; 390 px : 373 = 373 ; pied 12/11/2026 | console non relevée |
| Cause du saut raté | 🟡 non prouvée | fresh load : `scrollY` 0 après 4 s alors que le chapitre 11 est à 31 139 px ; collé après chargement : arrive (essai 4a = C) | cause exacte inconnue |
| Générateur `cours/make_wiki_page.py` | 🟡 | produit encore l'ancienne page unique et l'écraserait s'il était relancé | à adapter si hprzeta le veut |

## 2. Essais A / B / C (chapitre 11)

| Essai | URL | Réponse hprzeta |
|---|---|---|
| 1 | `Formation-Zeta-HR#user-content-ch11` (chargement frais) | A |
| 1′ | `Formation-Zeta-HR#ch11` (ancien lien) | A |
| 3 | « Chapitre 11 » dans l'ancien sommaire (`#ch11`) | A |
| 4a | page ouverte, attendre, coller `…#user-content-ch11` | C |
| 3 (après S0) | « Chapitre 11 » dans le sommaire corrigé | C |
| W1 (images avec taille) | 14 images | non testé pour « Lire → » : images déformées (rapport 0,84 au lieu de 1,4), retiré |
| Final | 14 liens « Lire → » vers les pages de chapitre | C |

## 3. Tableau de modifications (in en vert, out en rouge dans le PDF)

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| wiki `Formation-Zeta-HR.md` (sommaire) | `[Chapitre N — …](#user-content-chN)` (commit `13528e2`) puis `[Chapitre N — …](Formation-Zeta-HR-ChNN)` (commit `b7d7b9f`) | `[Chapitre N — …](#chN)` | 12/11/2026 |
| wiki `Formation-Zeta-HR.md` (images) | `<img … width height>` (commit `13528e2`), annulé par `829c297` | `![alt](url)` | 12/11/2026 |
| wiki `Formation-Zeta-HR-Ch01.md` à `Ch14.md` | 14 pages créées (de 75 à 142 lignes), navigation, pied de page | contenu d'un seul fichier de 1175 lignes | 12/11/2026 |
| `docs/index.html` (14 liens « Lire → ») | `…/wiki/Formation-Zeta-HR-ChNN` | `…/wiki/Formation-Zeta-HR#user-content-chN` (15:31), `#chN` avant | 12/11/2026 |

## 4. Commits (sans `--force`, local = origin)
- Wiki (`master`) : `13528e2` (sommaire + images avec taille), `829c297` (images remises), `b7d7b9f` (découpage W2).
- Site : IA `a07a331`, C `c0e989e`, main `5169d67`, Test `0192cae` ; `docs/index.html` identique (SHA-256 `d4106536…`).
- Sauvegardes : `pdf/archive/Formation-Zeta-HR.md.bak-202611121600`, `…bak-202611121620`, `…bak-202611121650`, `pdf/archive/index.html.bak-202611121712`.

## 5. Erreur commise et corrigée
W1 (largeur/hauteur fixes sur les images) a déformé les 14 images pendant environ 20 minutes en ligne (publiée `13528e2`, corrigée `829c297`). Mesure après correction : rapports 1,15 à 1,56, 0 image déformée, page de 41 717 px.

## 6. Non vérifié
- Réponse C chapitre par chapitre : hprzeta a répondu « C est ok » pour l'ensemble.
- Console du navigateur sur le site en ligne (suivi non lancé).
- Cause exacte du saut raté sur la page unique ; sans objet maintenant que chaque chapitre a sa page.

---
*RAPPORT_CORRECTION_ANCRES_CHAPITRE_20261112_1804.md · projet SITE ZETA · hprzeta · MAJ 12 novembre 2026 · 52 lignes*
