# Rapport de tri — Screenshots (synthèse, 21/11/2026)

> Comptages uniquement : aucun nom de fichier, aucune description d'image, aucune adresse. Les médias restent sur `/mnt/data` (hors dépôt, hors git).

## 1. Bilan

| Élément | Nombre |
|---|---:|
| Captures dans `brut/Screenshots` | **1 048** |
| Triées (liens physiques vers `ia/ math/ info/ zeta/ autre/ a_trier/`) | **1 018** |
| Exclues du tri (Messages 16 + WireGuard 14) | **30** |
| Marquées `sensible = oui` au registre (dont 14 WireGuard) | **85** |
| Classées `a_trier` (doute ou image illisible) | **5** |
| Idées consignées (`md/telandroid/idees_20261121.md`, local) | **66** |

## 2. Tableau par application et par thème

| Application | ia | math | info | zeta | autre | a_trier | exclu | Total | Sensibles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TikTok (lots 1 à 8) | 340 | 50 | 389 | 2 | 27 | 2 | 0 | 810 | 17 |
| YouTube (lot 9) | 0 | 0 | 0 | 84 | 0 | 0 | 0 | 84 | 0 |
| Chrome (lot 10) | 0 | 1 | 1 | 0 | 29 | 1 | 0 | 32 | 19 |
| Perplexity (lot 10) | 6 | 1 | 1 | 0 | 9 | 0 | 0 | 17 | 0 |
| Autres applications (lot 11) | 2 | 1 | 18 | 3 | 49 | 2 | 0 | 75 | 35 |
| Messages | 0 | 0 | 0 | 0 | 0 | 0 | 16 | 16 | 0 |
| WireGuard | 0 | 0 | 0 | 0 | 0 | 0 | 14 | 14 | 14 |
| **Total** | **348** | **53** | **409** | **89** | **114** | **5** | **30** | **1 048** | **85** |

## 3. Lecture rapide

- **zeta (89)** : les 84 captures YouTube forment une seule vidéo de cours sur ζ et l'hypothèse de Riemann ; 5 autres viennent de TikTok, d'un assistant IA et du suivi d'un calcul du projet.
- **autre (114)** : surtout des contenus personnels (Chrome et applications), rangés sans description, plus les contenus hors sujet (physique, religion, divers).
- **Sensibles (85)** : adresses ou clés de réseau, chaînes de type clé dans des notes et brouillons, comptes et informations bancaires, mots de passe visibles. Aucun ne doit sortir de la machine ni entrer dans git.
- **a_trier (5)** : captures indécidables (image presque vide, miniature corrompue, photo d'écran illisible).

## 4. Méthode (identique pour les 11 lots)

- Planches de 20 vignettes (ImageMagick) dans `zeta_android/tri_20261121/planches/`.
- Classement par liens physiques (`ln`) : 0 octet en double, aucune copie ni déplacement depuis `brut/`.
- Registre `.registre.csv` : colonnes `theme` et `sensible`, copie `.bak` au début de chaque lot.
- Un `index.md` par dossier thématique ; un rapport de comptage par lot (`RAPPORT_TRI_LOT1.md` à `RAPPORT_TRI_LOT11.md`).
- Reste hors périmètre de ce rapport : `Camera` (970 fichiers), non trié.

---
*Mis à jour le 2026-11-21*
