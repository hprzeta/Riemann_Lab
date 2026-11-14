# Rapport — application des décisions D1 (c), D2 (a), D3 (b) du 11/11/2026

> Exécuté à 21:47 d'après `PROMPT_MAJ_DECISIONS_SITE_20261111_2137.md`. Aucun commit, aucun push, aucune suppression. Statut : 🟢 ok · 🟡 fait à moitié · 🔴 ko.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| D1 (c) Dossier-md.md → md/ | 🟢 | cp -p vers md/Dossier-md.md.bak-20261111 puis mv ; cmp : contenu identique (1 800 octets, 34 lignes) ; ls du wiki : fichier absent ; md/Dossier-md.md présent | Chiffres de l'« État » (61 fichiers / 75 PDF) non mis à jour : facultatif, non demandé |
| D2 (a) PDF local régénéré | 🟢 | ancien PDF archivé dans pdf/archive/…pdf.bak-20261111 (117 912 octets, 0 note) ; régénéré par build_pdf_riemann_CM.sh depuis le .md annoté du wiki : 9 pages ; pdftotext : « Note du 11/11/2026 » 1, « 97 manquants » 1, « 84 vraies paires » 1 ; git status du PDF : 0 (dossier ignoré) | — |
| D3 (b) exclusion *.bak* | 🟢 | copies .git/info/exclude.bak-20261111 (wiki et code) puis ajout de *.bak* : wiki = *.bak-* *.bak*, code = scripts/*.bak-* *.bak-* *.bak* | Si une copie future s'appelle autrement que *.bak*, elle n'est pas couverte |
| Contrôle 1 : git status --short | 🟢 | wiki : 27 lignes « ?? » avant → 0 après (26 .bak + Dossier-md.md en moins, arbre propre). Code : 67 → 40 lignes, 27 .bak en moins, 0 .bak restant | Restent les nouveautés du jour (livrables pdf/site/…) et l'état d'avant la session (monitoring/Monitoring-Runs.md modifié) |
| Contrôle 2 : git ls-files | grep -c '.bak' | 🟢 | code : 0 ; wiki : 0 | — |
| Contrôle 3 : pdftotext du PDF régénéré | 🟢 | note du 11/11/2026 et « 97 manquants » présentes (voir D2) | — |
| Pages publiques | 🟢 | Aucune page publique concernée (wiki et site inchangés, 0 commit, 0 push) : Chrome non utilisé | — |
| Aucun commit, push ni suppression | 🟢 | git log inchangé ; aucune suppression : seulement 1 mv, 3 copies .bak-20261111, 1 régénération, 2 lignes ajoutées aux exclusions | — |

## 2. Tableau de modifications

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| Riemann_Lab.wiki/.git/info/exclude | [L2] *.bak* | — | 2026-11-11 21:47 |
| projet_zeta/.git/info/exclude | [L+1] *.bak* | — | 2026-11-11 21:47 |
| Riemann_Lab.wiki/Dossier-md.md → md/Dossier-md.md | [md/] Dossier-md.md (1 800 octets, contenu inchangé) | [wiki] Dossier-md.md | 2026-11-11 21:47 |
| pdf/optimisation/Voie_b_5/md_to_claude/analyse_math_deficit_2026-08-18.pdf (local, ignoré) | [9 pages] Note du 11/11/2026 ; 97 manquants ; 84 vraies paires | [8 pages] « 96 manquants », sans note (archivé en .bak-20261111) | 2026-11-11 21:47 |

## 3. Retours en arrière

- D1 : `mv ~/projet_zeta/md/Dossier-md.md ~/projet_zeta/Riemann_Lab.wiki/Dossier-md.md`.
- D2 : `cp -p ~/projet_zeta/pdf/archive/analyse_math_deficit_2026-08-18.pdf.bak-20261111 ~/projet_zeta/pdf/optimisation/Voie_b_5/md_to_claude/analyse_math_deficit_2026-08-18.pdf`.
- D3 : restaurer `.git/info/exclude.bak-20261111` dans chaque dépôt.

---
*RAPPORT_MAJ_DECISIONS_20261111_2147.md · projet SITE ZETA · hprzeta · MAJ 11 novembre 2026 21:47 · 34 lignes*
