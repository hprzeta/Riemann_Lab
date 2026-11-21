---
paths:
  - "md/telandroid/**"
  - "pdf/telandroid/**"
---
# Projet claude.ai ZETA-TELANDROID
- **ETAT** : `pdf/telandroid/ETAT_TELANDROID_ZETA.md` (point de départ, mis à jour à chaque session ; lien symbolique depuis `zeta_android/`). **Rapports** : `pdf/telandroid/tri_AAAAMMJJ/` (RAPPORT, HANDOFF, `A_DEPOSER/`).
- **Médias uniquement sur `/mnt/data/medias_telephone/zeta_android/`** (accessible par le lien `md/telandroid/zeta_android`) : jamais dans `pdf/`, jamais dans git. `md/` est exclu de git.
- **Aucun nom de fichier personnel ni aucun secret** (clé, jeton, IP, DDNS) dans les `.md` de `pdf/telandroid/`. Aucun nom de fichier des dossiers sensibles.
- **Tout reste en local pour les médias** : jamais de `git add` d'un média ; l'ETAT reste local (`.git/info/exclude`) ; les rapports `.md` ne sont commités que sur « go commit » de hprzeta (audit avant : IP, DDNS, clés).
- **Téléphone en lecture seule** : jamais d'écriture, de déplacement ni de suppression côté téléphone ; jamais `--delete`.
- **Copie brute à chaque branchement** : `zeta_android/scripts/sync_zeta_android.sh` (d'abord `--dry-run`, puis sans option, dans tmux `zeta_android`). Seuls les nouveaux fichiers de `DCIM/Camera` et `DCIM/Screenshots` (tous types) vont dans `brut/Camera/` et `brut/Screenshots/` ; registre `.registre.csv` (sha256) et `sync.log`. Les dossiers sensibles ne sont jamais copiés. Contrôler les tailles à la fin.
- **Le tri thématique vient ensuite**, depuis `brut/`, vers `ia/ math/ info/ zeta/ autre/ a_trier/` (un `index.md` par dossier, une fiche par idée), après accord de hprzeta.
- **Personnel non décrit** : photos et vidéos personnelles ni décrites, ni listées, ni ouvertes. Les dossiers sensibles d'autre_projet (liste dans l'ETAT local ; ancienne base non fusionnée) : jamais ouverts, listés ni touchés.
- **Exclus du tri** : captures WireGuard et Messages.
- **Piège** : jamais `pkill -f` / `pgrep -f` avec un motif présent dans sa propre commande (auto-kill, code 144).
