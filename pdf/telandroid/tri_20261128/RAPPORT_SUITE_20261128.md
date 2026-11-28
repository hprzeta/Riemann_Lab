# Rapport — suite du 28/11/2026 (R22, R21, R25) — ZETA-TELANDROID

> Local uniquement. Machine : PC1. Aucun nom de fichier de média, aucun secret dans ce document. Téléphone non sollicité.

## Résumé

R22 : les 114 lignes `copie` du registre sont devenues `présent`. R21 : les 30 fichiers de `CaptureLot1` à un seul lien sont bien les 30 captures exclues du tri (16 Messages, 14 WireGuard). R25 : `sync_zeta_android.sh` et `tri_lot.py` sont adaptés aux nouveaux noms de lots, avec un garde-fou contre les lots anciens. Le registre et `brut/` sont intacts hors le champ `statut` de R22.

## Tableau de validation

| Étape | Contrôle | Résultat | Verdict |
|---|---|---|---|
| 0 | Prompt v4 extrait dans `src/ia/prompts/tel_20261128/` | Extraction sans écrasement ; les fichiers de la session précédente sont intacts | 🟢 |
| 1 | État avant (lecture seule) | Registre 2 133 lignes, 100 % CRLF ; 1 999 `présent`, 114 `copie`, 19 `supprime_local` ; lots 956 / 1 043 / 114 | 🟢 |
| 2 | R22 : 114 lignes `copie` → `présent` | 0 `copie` restante ; 2 113 `présent`, 19 `supprime_local` ; 2 133 lignes, CRLF conservé ; seule la colonne `statut` a changé (114 cellules) ; +342 octets = 114 × 3 | 🟢 |
| 2 | Contrôle textuel de R22 | Mon test `cmp` après `sed` était mal construit et a signalé un faux écart ; les contrôles par colonne et par taille font foi | 🟡 |
| 3 | R21 : 30 fichiers à 1 seul lien dans `CaptureLot1` | Hypothèse confirmée : ce sont les 16 captures Messages et les 14 WireGuard exclues du tri ; 30 / 30 au registre, `theme = exclu` ; aucun autre fichier n'a un seul lien | 🟢 |
| 3 | Champ `sensible` de ces 30 | 14 `oui` (WireGuard), 16 vides (Messages) : convention de leur exclusion, non modifiée | 🟡 |
| 4 | R25 : `sync_zeta_android.sh` | Sources : liste `LOTS = [ScreenLot2]` ; destination `brut/<lot>/` ; lots anciens `ScreenLot1` et `CaptureLot1` refusés (code 4) ; `--dry-run`, registre, sha256 et interdiction de `--delete` conservés | 🟢 |
| 4 | R25 : garde sha256 et statut `doublon_sha256` | Un fichier dont le contenu est déjà au registre n'est pas copié ; sha256 du téléphone lu en flux seulement si la taille existe déjà au registre. Non testé sur des données (téléphone non sollicité) : vérifié par lecture du code et compilation | 🟡 |
| 4 | R25 : détection des fichiers disparus | Ajout nécessaire hors prompt : limitée aux lots scannés, sinon 1 999 lignes des anciens chemins auraient été marquées `disparu_du_tel` | 🟡 |
| 4 | R25 : `tri_lot.py` | 5 lignes modifiées (`brut/Screenshots` → `brut/CaptureLot1`) ; aucune référence à `brut/Camera` ; la ligne 142 (chemin du téléphone dans le registre) volontairement intacte | 🟢 |
| 4 | R25 : `tri_camera.py` | 10 références aux anciens noms, hors périmètre, non modifié | 🟡 |
| 4 | Tests R25 | `bash -n` OK ; `py_compile` OK (script embarqué et `tri_lot.py`) ; `--dry-run` sans téléphone : message clair, code 2, rien écrit ; lot ancien refusé : code 4 ; `local_pour` : seul `ScreenLot2` accepté | 🟢 |
| 4 | Registre et `brut/` après R25 | Inchangés : empreinte du registre, 2 133 lignes, lots 956 / 1 043 / 114, 0 `.part`, `sync.log` inchangé | 🟢 |
| — | Téléphone | Non sollicité dans ce prompt : aucune copie, aucune lecture ; le `--dry-run` de test a utilisé un VFS local | 🟢 |
| — | Sauvegardes hors `/mnt/data`, commit, push | Aucun : tout reste local ; les scripts sont hors dépôt | 🟢 |
| — | `ETAT_TELANDROID_ZETA.md` | Pas mis à jour avec cette suite (il mentionne encore les 114 lignes `copie` et les scripts non adaptés) | 🟡 |
| — | Points du rapport du 28/11 fermés ou ouverts | Fermés : statut `copie` (R22), 30 fichiers à 1 lien (R21), scripts périmés (R25, sauf `tri_camera.py`). Ouverts : 2 vidéos `a_trier`, 5 doublons à thème divergent (le « 6e » compté le matin était un contenu personnel déjà classé, pas un conflit de thème ; corrigé le 28/11/2026, traités ensuite par D26) | 🟡 |

## Avant / après

| Élément | Avant | Après | Verdict |
|---|---|---|---|
| Registre : statut `présent` | 1 999 | 2 113 | 🟢 |
| Registre : statut `copie` | 114 | 0 | 🟢 |
| Registre : statut `supprime_local` | 19 | 19 | 🟢 |
| Registre : lignes (en-tête compris) | 2 133 | 2 133 | 🟢 |
| Registre : taille en octets | 602 274 | 602 616 (+342) | 🟢 |
| `brut/ScreenLot1` / `CaptureLot1` / `ScreenLot2` | 956 / 1 043 / 114 | 956 / 1 043 / 114 | 🟢 |
| `tri_lot.py` : références `brut/Screenshots` | 5 | 0 | 🟢 |
| `sync_zeta_android.sh` : lignes | 238 | 279 | 🟢 |
| `sync_zeta_android.sh` : sources | `DCIM/Camera`, `DCIM/Screenshots` | `DCIM/ScreenLot2` (liste `LOTS`) | 🟢 |

## Tableau horodaté des changements (28/11/2026)

| Heure | Machine | Changement | Périmètre |
|---|---|---|---|
| 13:05 | PC1 | Extraction du prompt v4 (sans écraser) | `src/ia/prompts/tel_20261128/` |
| 13:06 | PC1 | R22 : sauvegarde puis 114 statuts `copie` → `présent` (colonne `statut` seule) | `.registre.csv` ; sauvegarde `…-avant-R22` |
| ≈13:07 | PC1 | R21 : analyse des fichiers à 1 seul lien (lecture seule, comptes) | `brut/CaptureLot1`, registre |
| 13:08 | PC1 | R25 : sauvegardes `.bak-20261128` des deux scripts | `scripts/` |
| 13:08 | PC1 | R25 : modification de `sync_zeta_android.sh` (lots, garde-fou, garde sha256, portée des disparus) | `scripts/sync_zeta_android.sh` |
| 13:09 | PC1 | R25 : modification de `tri_lot.py` (5 lignes) | `scripts/tri_lot.py` |
| ≈13:10 | PC1 | R25 : tests (`bash -n`, `py_compile`, `--dry-run` sans téléphone, garde-fou, `local_pour`) et contrôle registre / `brut/` inchangés | lecture seule |

## Sauvegardes

- `.registre.csv.bak-20261128-avant-R22` (dans `zeta_android/`).
- `scripts/sync_zeta_android.sh.bak-20261128` et `scripts/tri_lot.py.bak-20261128`.
- Aucune suppression ; aucune écriture côté téléphone ; aucun fichier de `brut/` touché.

## Suite proposée (rien ne s'exécute sans « go »)

- Fait le 28/11/2026 après ce rapport : `ETAT_TELANDROID_ZETA.md` mis à jour (section 9 : 114 lignes passées à `présent`, 30 fichiers à 1 lien expliqués, scripts adaptés).
- Premier vrai test de `sync_zeta_android.sh --dry-run` avec le téléphone branché (hors de ce prompt) : il lira les fichiers dont la taille existe déjà au registre pour comparer les sha256.
- Vérifier qu'aucun script ne compte les statuts en ignorant le nouveau `doublon_sha256`.
- Décider si `tri_camera.py` doit aussi être adapté aux nouveaux noms avant un éventuel réemploi.
- Restent ouverts du rapport précédent : 2 vidéos en `a_trier` et 5 doublons à thème divergent (le « 6e » compté le matin était un contenu personnel déjà classé ; corrigé le 28/11/2026, traités ensuite par D26) ; idées 75 à 82 à relire.
- Rien n'est commité ni poussé ; aucun `git add` sans « go commit ».

---
<sub>Mis à jour le 2026-11-28 · 73 lignes</sub>
