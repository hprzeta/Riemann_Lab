# Rapport d'analyse — restes ouverts du 12/11/2026 (préparé à 02:27 pour le 13/11)

> Rédigé sur claude.ai (projet SITE ZETA). Aucune modification faite. Sources : `ETAT_SITE_ZETA_20261112.md`, `RAPPORT_MAJ_WIKI_D10_20261112_0222.md`, `RAPPORT_MAJ_SITE_D10_D12_20261112_0206.md`. Prompt associé : `PROMPT_MAJ_SITE_RESTES_20261112_0227.md`.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Site sur téléphone (cartes « cours », grille à 5 colonnes) | 🟢 | vérifié par hprzeta le 12/11 | — |
| En-tête de `Etape-1…` (wiki) | 🟡 | « Dernière mise à jour : 11 novembre 2026 », pied au 12/11 | D14 |
| Sélecteur CSS `div[style*="repeat(5, 1fr)"]` | 🟡 | dépend du texte exact d'un style inline (rapport 02:06) | D15 |
| Ancres `#…` des liens du site | 🟡 | jamais vérifiées (curl ne les voit pas) | D16 |
| Test automatique | 🟢 | minuterie active ; prochain test réel au prochain allumage s'il y a un commit publié | lire son rapport à l'étape 0 |
| Pied du PDF du vault | 🟡 | page de note seulement (source absente) | hors périmètre |

## 2. Décisions proposées (confirmées au STOP de l'étape 3)

| # | Décision |
|---|---|
| D14 | aligner l'en-tête de `Etape-1…` sur le pied (12 novembre 2026) |
| D15 | classe dédiée sur la grille à 5 colonnes, sans changer l'affichage |
| D16 | vérifier toutes les ancres ; corriger une ancre morte seulement avec accord |

## 3. Tableau de modifications (à faire)

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| wiki `Etape-1-Calcul-des-zéros-non-triviaux.md` (en-tête) | Dernière mise à jour : 12 novembre 2026 | Dernière mise à jour : 11 novembre 2026 | À FAIRE |
| `docs/index.html` (grille, l. ~1437) | élément avec une classe dédiée (ex. `grid5`) + style inline inchangé | élément sans classe | À FAIRE |
| `docs/index.html` (CSS mobile) | `.grid5 { grid-template-columns: repeat(auto-fit, minmax(90px, 1fr)) !important; }` | `div[style*="repeat(5, 1fr)"] { … }` | À FAIRE |
| ancres mortes éventuelles | cible corrigée | ancre actuelle | À FAIRE si trouvées et acceptées |

## 4. Non vérifié depuis claude.ai
- Numéro exact de la ligne de la grille et texte de l'en-tête de `Etape-1…`.
- Liste des liens avec ancre et existence de leurs cibles.

---
*RAPPORT_ANALYSE_RESTES_20261112_0227.md · projet SITE ZETA · hprzeta · MAJ 12 novembre 2026 02:27 · 38 lignes*
