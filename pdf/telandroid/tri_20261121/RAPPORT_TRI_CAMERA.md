# Rapport de tri — Camera (synthèse, 21/11/2026)

> Comptages uniquement : aucun nom de fichier, aucune description d'image. Les médias restent sur `/mnt/data` (hors dépôt, hors git). Les photos personnelles sont classées en « autre » sans description.

## 1. Bilan

| Élément | Nombre |
|---|---:|
| Fichiers dans `brut/Camera` | **970** (289 photos, 681 vidéos) |
| Classés par liens physiques | **970** (0 non trié) |
| `sensible = oui` dans Camera | **67** |
| `a_trier` dans Camera | **14** |
| Lots | 12 à 21 (3 lots de photos, 7 lots de vidéos) |

## 2. Tableau par thème

| Type | ia | math | info | zeta | autre | a_trier | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| Photos | 11 | 1 | 188 | 11 | 77 | 1 | 289 |
| Vidéos | 224 | 87 | 207 | 25 | 125 | 13 | 681 |
| **Total** | **235** | **88** | **395** | **36** | **202** | **14** | **970** |

## 3. Cumul avec Screenshots (2 018 fichiers)

| Élément | Nombre |
|---|---:|
| Fichiers de `brut/` | 2 018 (Screenshots 1 048 + Camera 970) |
| Classés par liens (hors 30 exclus Messages/WireGuard) | 1 988 |
| `sensible = oui` au registre | **152** (Screenshots 85 + Camera 67) |
| `a_trier` au registre | **19** (Screenshots 5 + Camera 14) |
| Idées consignées (local) | 74 |

## 4. Méthode

- Photos : planches de 20 vignettes. Vidéos : une image extraite par vidéo (OpenCV, à 30 % de la durée) puis planches de 20.
- Liens physiques (`ln`) vers `brut/Camera/` : 0 octet en double, aucune copie ni déplacement.
- Registre `.registre.csv` : colonnes `theme` et `sensible`, copie `.bak` au début de chaque lot.
- Un `index.md` par dossier thématique ; un rapport de comptage par lot (`RAPPORT_TRI_LOT12.md` à `LOT21.md`).
- Constat : environ un tiers des vidéos enregistrées traite de l'IA, des mathématiques ou de ζ, le reste de l'informatique et du réseau.

---
*Mis à jour le 2026-11-21*
