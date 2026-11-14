# Rapport d'analyse — dépôt automatique des rapports dans le projet SITE ZETA (11/11/2026 23:30)

> Analyse sur claude.ai. Aucune modification de configuration. Demande de hprzeta : que Claude Code dépose lui-même rapports et rapport de session à la fin de chaque travail.

## Constats
- Tous les rapports du jour sont dans le projet. Les deux scripts de PDF sont corrigés (844cc46 / 743f571 pour `build_pdf_riemann.sh`).
- Le projet contient des **doublons** (chaque rapport listé deux fois) et un fichier `RAPPORT_MAJ_SCRIPT2_DATE_FR_20261111_2312.md.bak-20261111` : conséquence des dépôts manuels répétés.
- Le titre du rapport 2312 dit « build_pdf_riemann_CM.sh » alors qu'il traite `build_pdf_riemann.sh` (cosmétique).
- Limite à vérifier : une session Claude Code locale n'a l'outil `Projects` que si elle est rattachée au projet SITE ZETA. Le prompt commence par ce test et s'arrête s'il échoue.
- Mécanisme proposé : hook `Stop` qui refuse l'arrêt avec une consigne, Claude Code dépose alors les fichiers par `project_write` (même nom = remplacement, plus de doublon) et rédige un rapport de session. Journal local des sha256 pour ne déposer que le nouveau.

## Tableau de modifications prévues (À FAIRE, tout local, 0 commit)
| page | ligne in | ligne out | date heure |
|---|---|---|---|
| scripts/depot_projet_site_zeta.sh (local, non suivi) | [nouveau] script du hook Stop (journal sha256, exclusions .bak/images/secrets) | — | À FAIRE |
| .claude/settings.local.json ou ~/.claude/settings.json | [ajout] hook "Stop" → depot_projet_site_zeta.sh | — | À FAIRE (sur « go ») |
| src/ia/depot_projet_site_zeta.log (local) | [nouveau] journal des dépôts | — | À FAIRE |
| projet SITE ZETA (claude.ai) | RAPPORT_SESSION_20261111_HHMM.md ; rapports manquants | doublons et .bak-20261111 (proposés, jamais supprimés sans accord) | À FAIRE |
