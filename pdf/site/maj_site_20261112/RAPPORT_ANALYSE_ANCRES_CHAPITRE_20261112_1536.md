# Rapport d'analyse — D17 (suite) : arriver directement sur le chapitre (12/11/2026 15:36)

> Rédigé sur claude.ai (projet SITE ZETA). Aucune modification faite. Source : capture du terminal de Claude Code (15:34) et précision de hprzeta. Prompt associé : `PROMPT_CORRECTION_ANCRES_CHAPITRE_20261112_1536.md`.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Correctif de 15:31 (`#user-content-chN`, 14 liens, 4 branches) | 🔴 | hprzeta : les liens ouvrent la page `Formation-Zeta-HR` **en haut**, il faut défiler jusqu'au chapitre | D17 non résolu |
| Malentendu | 🔴 | « les 3 arrivent » voulait dire « arrivent sur la page », compris comme « arrivent au chapitre » | critère de réussite précisé |
| Cause « GitHub réécrit `name` en `user-content-` » | 🟡 | vraie, mais ne suffit pas à expliquer l'échec avec `#user-content-ch11` | à reprendre |
| Indice | 🟡 | page très longue ; 10 images au-dessus du chapitre 11 (selon Claude Code) ; formules | à tester (essai 4) |

## 2. Critère de réussite (nouveau)
Après un clic sur « Lire → », **sans défilement**, le **titre du chapitre** est en haut de l'écran. Réponse de hprzeta A / B / C ; seul C compte.

## 3. Solutions selon le résultat des essais

| Solution | Quand | Ampleur |
|---|---|---|
| S1 | le lien du sommaire du wiki fonctionne | site seul, 14 liens |
| S2 | l'ancre automatique du titre fonctionne | site seul, 14 liens |
| W1 | le saut marche seulement une fois la page chargée | wiki : taille fixe des images |
| W2 | rien ne marche | wiki : une page par chapitre (décision de hprzeta) |

## 4. Décision

| # | Décision |
|---|---|
| D17 | Critère : arriver au titre du chapitre sans défiler ; solution choisie après les essais de hprzeta |

## 5. Tableau de modifications (à faire)

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| `docs/index.html` (14 liens « Lire → ») et/ou wiki `Formation-Zeta-HR.md` | selon S1, S2, W1 ou W2 | `…/Formation-Zeta-HR#user-content-chN` (depuis 15:31) | À FAIRE |

## 6. Non vérifié depuis claude.ai
- Le rapport de 15:31 lui-même (non reçu) ; les hashes du correctif de 15:31.
- La cause exacte : seuls les essais de hprzeta la trancheront.

---
*RAPPORT_ANALYSE_ANCRES_CHAPITRE_20261112_1536.md · projet SITE ZETA · hprzeta · MAJ 12 novembre 2026 15:36 · 43 lignes*
