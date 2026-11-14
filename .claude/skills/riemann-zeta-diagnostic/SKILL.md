---
name: "riemann-zeta-diagnostic"
description: "À utiliser pour tout diagnostic du cluster Zêta (réseau, matériel, services, PC1 à PC5) : où le ranger, comment le nommer, quel gabarit, et comment le publier sans IP."
---

# Diagnostics du cluster Zêta

Tous les diagnostics (.md) du cluster vivent dans UN seul dossier privé. Ce skill fixe l'emplacement, le nommage, le gabarit et la publication.

## Emplacements

- **A (privé, source de vérité)** : `~/zeta_inventaire/DIAGNOSTIC/` (droits 700, fichiers 600), hors dépôt Git. Contient IP et MAC.
- **B (publiable)** : `~/projet_zeta/docs/diagnostics/`, copie SANS IP/IPv6/MAC, générée uniquement par le script `~/projet_zeta/scripts/zeta_diag_publier.sh`. Ne jamais éditer B à la main.

## Nommage

`AAAAMMJJ_PCn_sujet.md` avec PCn = PC1 à PC5, ou CLUSTER pour un sujet transversal. Exemple : `20261003_PC5_ecran-tv.md`.

## Gabarit

1. **Symptôme** : ce qui est observé, sur quelle machine.
2. **Vérifications** : commandes lancées et ce qu'elles ont montré (secrets masqués).
3. **Cause** : distinguer fait établi, hypothèse, intuition.
4. **Correctif** : commandes exactes, une par étape, avec la machine indiquée.
5. **Retour en arrière** : sauvegardes faites (.bak) et commande de restauration.
6. **Résultat** : vérification finale et statut (ouvert / résolu).

Pied de page obligatoire : `*Mis à jour le AAAA-MM-JJ — N lignes*`.

## Procédure à chaque diagnostic

1. Rédiger le fichier dans A, avec le bon nom.
2. Ajouter une ligne dans `INDEX.md` (date, machine, sujet, statut, fichier) et mettre à jour son pied de page.
3. Lancer `~/projet_zeta/scripts/zeta_diag_publier.sh` : il copie A vers B en masquant les adresses et contrôle qu'il ne reste rien.
4. Ne jamais faire `git add` ni `git commit` sans validation explicite de l'utilisateur.

## Règles de travail

- Rien n'est modifié sur les machines sans « go » de l'utilisateur.
- Une commande à la fois, avec la machine indiquée (PC1 = riemann@zeta-lab, PC2 = hprzeta@zeta-calc-second, etc.).
- Toujours une sauvegarde `.bak` avant modification, et le retour en arrière dans le diagnostic.
- Bastion PC4 (OpenBSD) : appliquer aussi le skill `riemann-bastion-hardening` (jamais pf, réseau ou WireGuard via le tunnel).
- Langue : français.