# Rapport — points R20, R23, R24, R26, R30 (v5) — 28/11/2026 — ZETA-TELANDROID

> Local uniquement. Machine : PC1. Aucun nom de fichier de média, aucun secret dans ce document. Téléphone non sollicité. Lecture seule : rien n'a été modifié.

## Résumé

R30 : aucun script n'ignore `doublon_sha256` à tort. R20 : la source `DCIM/ScreenLot1` est refusée par le script. R23 : les 2 vidéos `a_trier` viennent de TikTok (prouvé), sujet probable, thème inconnu pour l'une. R24 : 5 doublons à thème divergent (et non 6), décisions de hprzeta en attente. R26 : 8 idées (75 à 82, 32 médias) à relire. Aucune modification de `brut/`, du registre, des idées ni des scripts.

## Tableau de validation

| Étape | Contrôle | Résultat | Verdict |
|---|---|---|---|
| 0 | Prompt v5 extrait dans `src/ia/prompts/tel_20261128/` | Extraction sans écrasement ; `captures/` déjà présent | 🟢 |
| 1 | État avant (lecture seule) | Registre 2 133 lignes, 100 % CRLF ; 2 113 `présent`, 19 `supprime_local`, 0 `copie` ; lots 956 / 1 043 / 114 ; boîte 82 dossiers d'idées + `index.md`, 460 médias | 🟢 |
| 2 | R30 : usages des statuts dans `scripts/` | Aucun endroit n'ignore `doublon_sha256` à tort : le script le saute (l. 166), le crée (l. 214) et ne le juge pas « disparu » ; `tri_lot.py` et `tri_camera.py` ne filtrent pas les statuts. Aucun correctif nécessaire | 🟢 |
| 2 | R30 : limites | Périmètre `scripts/` seulement (pas les autres scripts du dépôt) ; commentaire d'en-tête (l. 7) du script non à jour (cosmétique, non modifié) ; une ligne `doublon_sha256` dont le fichier disparaît du téléphone n'est pas marquée `disparu_du_tel` (sans gravité : pas de copie locale propre) | 🟡 |
| 3 | R20 fermé : source `DCIM/ScreenLot1` refusée | Refus à deux niveaux : garde-fou de configuration (code 4) et `local_pour` ; script inchangé depuis R25 ; aucune copie ni lecture du lot ; téléphone non sollicité | 🟢 |
| 4 | R23 : 2 vidéos `a_trier` de `ScreenLot2` | Lignes de registre 2027 (doublon de la ligne 59, classé `ia`) et 2116 (`a_trier`, 2 liens). `ffprobe` absent : `exiftool` (champs techniques) et `cv2` ; 3 images clés chacune. Source : TikTok **prouvé** (filigrane visible) ; sujet **probable** (2027 : relais d'une annonce sur un mathématicien et la physique quantique ; 2116 : histoire des nombres complexes) ; thème 2027 **inconnu**. Aucune transcription ni modification | 🟡 |
| 4 | R23 : images clés | 6 images de contenus de tiers dans `pdf/telandroid/tri_20261128/captures/` (non suivies par git) : ne pas les inclure dans un `git add -A` | 🟡 |
| 5 | R24 : doublons à thème divergent | **5** (lignes 2027, 2098, 2105, 2108, 2119) et non 6 : le 6e annoncé le 28/11 était le contenu personnel déjà classé `autre`, qui n'est pas un conflit de thème. Options proposées : 2027 A, 2098 B (vers `zeta`), 2105 A, 2108 A, 2119 A (A = garder, B = déplacer). **Décisions de hprzeta en attente** | 🟡 |
| 5 | Textes du 28/11 : « 6 doublons » corrigé en « 5 » | Corrigé après la rédaction de ce rapport, le 28/11/2026 : ETAT, rapport et handoff du matin, rapport et handoff de la suite (mention mise à jour ensuite) | 🟢 |
| 6 | R26 : idées 75 à 82 | 8 fiches cohérentes avec l'index (statut et nombre de médias) ; 32 médias dont 13 doublons liés ; certitude `a_verifier` partout ; relecture de hprzeta en attente (fusions possibles : 79, 81, 82 petites ; 75 recoupe 02 et 68) | 🟡 |
| — | Intégrité en fin de session | Empreintes du registre et de `brut/` identiques à la référence ; 2 133 lignes ; lots 956 / 1 043 / 114 ; 0 `.part` ; scripts et `index.md` de la boîte inchangés ; boîte 82 dossiers, 460 médias | 🟢 |
| — | Téléphone, suppressions, commit, push | Téléphone non sollicité ; aucun fichier copié, déplacé ni supprimé ; aucun commit, push ni publication | 🟢 |

## Avant / après

| Élément | Avant | Après | Verdict |
|---|---|---|---|
| Registre (statuts, lignes, empreinte) | 2 113 / 19 / 0 `copie` ; 2 133 ; `4246a44f…` | identique | 🟢 |
| `brut/ScreenLot1` / `CaptureLot1` / `ScreenLot2` | 956 / 1 043 / 114 | 956 / 1 043 / 114 | 🟢 |
| Boîte à idées : dossiers / médias | 82 / 460 | 82 / 460 | 🟢 |
| `sync_zeta_android.sh`, `tri_lot.py` | modifiés à 13:08 et 13:09 (R25) | inchangés | 🟢 |
| `captures/` (images clés de R23) | 0 image R23 | 6 images (non suivies par git) | 🟡 |

## Tableau horodaté des changements (28/11/2026)

| Heure | Machine | Changement | Périmètre |
|---|---|---|---|
| 13:33 | PC1 | Extraction du prompt v5 (sans écraser) | `src/ia/prompts/tel_20261128/` |
| ≈13:34 | PC1 | Étape 1 : comptages (lecture seule) | registre, `brut/`, boîte |
| ≈13:35 | PC1 | R30 : recherche des usages de statuts ; R20 : test du refus de `ScreenLot1` (copies de test dans le répertoire temporaire) | `scripts/` (lecture seule) |
| 13:37 | PC1 | R23 : lecture des métadonnées et création de 6 images clés | `pdf/telandroid/tri_20261128/captures/` |
| ≈13:40 | PC1 | R24 : repérage des doublons à thème divergent (lecture seule) | registre, dossiers de tri, boîte |
| ≈13:42 | PC1 | R26 : lecture des fiches 75 à 82 (lecture seule) | `boite_a_idee/` |
| 13:43 | PC1 | Contrôle d'intégrité final, puis rédaction des livrables | `pdf/telandroid/tri_20261128/` |

## Sauvegardes et fichiers créés

- Aucune sauvegarde nécessaire : aucun fichier existant n'a été modifié (registre, `brut/`, scripts, boîte, idées).
- Fichiers créés : 6 images clés dans `captures/`, ce rapport, son PDF et le handoff.

## Suite proposée (rien ne s'exécute sans « go »)

- Décider, par média, du sort des 5 doublons à thème divergent (R24) : options proposées 2027 A, 2098 B, 2105 A, 2108 A, 2119 A ; toute application après « go » explicite, avec sauvegardes `.bak-20261128`.
- Relire les idées 75 à 82 et dire si l'on fusionne ou supprime les petites (79, 81, 82) ou si l'on rapproche 75 de 02 et 68 (R26).
- Fait le 28/11/2026 après ce rapport : « 6 doublons » corrigé en « 5 » dans l'ETAT, le rapport et le handoff du matin, le rapport et le handoff de la suite.
- Fait le 28/11/2026 après ce rapport : `ETAT_TELANDROID_ZETA.md` mis à jour (section 10 : R20 fermé, R23, R24, R26, R30).
- R23 : si le contenu des 2 vidéos doit être établi, prévoir une transcription ou un visionnage complet ; sinon laisser la ligne 2116 en `a_trier` ou la passer en `math` sur décision.
- Rien n'est commité ni poussé ; les images clés de `captures/` ne doivent pas être ajoutées à git sans « go commit ».

---
<sub>Mis à jour le 2026-11-28 · 63 lignes</sub>
