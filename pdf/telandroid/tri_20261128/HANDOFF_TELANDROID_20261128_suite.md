# HANDOFF — ZETA-TELANDROID — suite du 28/11/2026 (R22, R21, R25)

> Local uniquement. Un seul fichier de passation pour claude.ai (projet ZETA-TELANDROID). Aucun nom de média, aucun secret. Complète `HANDOFF_TELANDROID_20261128.md`.

## État à la fin de cette suite

- Registre : 2 133 lignes (en-tête compris), CRLF ; statuts : **2 113 `présent`**, 19 `supprime_local`, **0 `copie`** (R22 fait).
- Lots de `brut/` inchangés : `ScreenLot1` 956, `CaptureLot1` 1 043, `ScreenLot2` 114.
- R21 : les 30 fichiers de `CaptureLot1` à un seul lien sont les 16 Messages et 14 WireGuard exclus du tri (`theme = exclu`, 14 `sensible = oui`) : cause établie.
- R25 : `scripts/sync_zeta_android.sh` copie désormais les lots listés dans `LOTS` (`ScreenLot2` pour l'instant) vers `brut/<lot>/`, refuse `ScreenLot1` et `CaptureLot1`, ne copie pas un contenu déjà au registre (sha256, statut `doublon_sha256`) et ne juge « disparus » que les fichiers des lots scannés. `scripts/tri_lot.py` pointe vers `brut/CaptureLot1`.
- Tests : `bash -n`, `py_compile`, `--dry-run` sans téléphone (échec propre, code 2), lot ancien refusé (code 4). **Non testé sur des données** : garde sha256 et enregistrement des doublons.
- Téléphone non sollicité. Aucune sauvegarde hors `/mnt/data`. Rien commité ni poussé.

## Points ouverts

- Fait le 28/11/2026 après ce rapport : `ETAT_TELANDROID_ZETA.md` mis à jour (section 9 : 114 lignes passées à `présent`, 30 fichiers à 1 lien expliqués, scripts adaptés).
- Premier vrai test de `sync_zeta_android.sh --dry-run` avec le téléphone branché (hors de ce prompt) : il lira les fichiers dont la taille existe déjà au registre pour comparer les sha256.
- Vérifier qu'aucun script ne compte les statuts en ignorant le nouveau `doublon_sha256`.
- Décider si `tri_camera.py` doit aussi être adapté aux nouveaux noms avant un éventuel réemploi.
- Restent ouverts du rapport précédent : 2 vidéos en `a_trier` et 5 doublons à thème divergent (le « 6e » compté le matin était un contenu personnel déjà classé ; corrigé le 28/11/2026, traités ensuite par D26) ; idées 75 à 82 à relire.
- Rien n'est commité ni poussé ; aucun `git add` sans « go commit ».

## Fichiers de la session

- Rapport : `pdf/telandroid/tri_20261128/RAPPORT_SUITE_20261128.md` et `.pdf`.
- Sauvegardes : `.registre.csv.bak-20261128-avant-R22`, `scripts/*.bak-20261128` (dans `zeta_android/`).
- Prompt utilisé : `src/ia/prompts/tel_20261128/PROMPT_TELANDROID_ZETA_20261128_v4.md` (local uniquement).

hprzeta, donne le .md à claude.ai, projet ZETA-TELANDROID : il le range lui-même.

---
<sub>Mis à jour le 2026-11-28 · 32 lignes</sub>
