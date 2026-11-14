# Rapport — liens « Lire → » vers Formation-Zeta-HR (D17) — 12/11/2026 15:31

> **CORRECTION 15:40 : D17 = 🔴 NON RÉSOLU.** « Les 3 arrivent » voulait dire : hprzeta arrive sur la PAGE Formation-Zeta-HR, en HAUT, et doit défiler à la main. Le tableau « oui » ci-dessous était une erreur d'interprétation. Suite : `RAPPORT_CORRECTION_ANCRES_CHAPITRE_*`.

> Exécution de `PROMPT_CORRECTION_ANCRES_FORMATION_20261112_1359.md`. Aucun `--force`. Wiki non modifié.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste |
|---|---|---|---|
| Cause de l'échec de `#ch11` | 🟢 prouvée | Le wiki GitHub réécrit `<a name="ch11">` en `<a name="user-content-ch11">` : aucun élément `ch11` n'existe dans la page rendue. Chargement frais : `scrollY` = 0 à chaque essai | — |
| Nos commits ont-ils cassé le lien ? | 🟢 non | Les `.bak` et `git log -S` montrent la même forme `#chN` ; page wiki inchangée depuis le 13/09 | — |
| Traduction automatique de Chrome | 🟢 non cause | L'échec se produit aussi sans traduction | — |
| Liens corrigés (14, `#user-content-chN`) | 🔴 non résolu | en ligne (14 occurrences) ; chapitres 2, 5 et 11 : arrivent EN HAUT de la page, pas au chapitre | autres chapitres non confirmés par hprzeta |
| Mesures automatisées | 🟡 instables | `scrollY` : ch1 et ch14 arrivent ; ch2 à 13 souvent non ; réappliquer l'ancre après chargement arrive. Hypothèse (non prouvée) : saut avant la hauteur finale de la page | à confirmer chez hprzeta |
| Pourquoi « avant, ça marchait » | 🟡 inconnu | rien n'a changé chez nous ; changement côté GitHub non prouvé | — |

## 2. Formes de lien testées

| Forme | URL | Arrive ? | Preuve |
|---|---|---|---|
| Ancien lien | `…/Formation-Zeta-HR#ch11` | non | cible absente du DOM, `scrollY` 0 |
| Nouveau lien | `…/Formation-Zeta-HR#user-content-chN` | non (en haut de la page, ch2, 5, 11 selon hprzeta) | voir §1 |

## 3. Vérification par chapitre

| Chapitre | Arrive ? | Vérifié par |
|---|---|---|
| 2 | arrive sur la page, en haut (pas au chapitre) | hprzeta |
| 5 | arrive sur la page, en haut (pas au chapitre) | hprzeta |
| 11 | arrive sur la page, en haut (pas au chapitre) | hprzeta |
| 1, 14 | oui | outil (chargement frais) |
| 3, 4, 6 à 10, 12, 13 | non confirmé | à tester par hprzeta |

## 4. Modifications

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| `docs/index.html` l. 877–1033 (14 liens) | `href="https://github.com/hprzeta/Riemann_Lab/wiki/Formation-Zeta-HR#user-content-chN"` | `href="https://github.com/hprzeta/Riemann_Lab/wiki/Formation-Zeta-HR#chN"` | 12/11/2026 ~14:15 |

## 5. Publication
Commits `site: liens « Lire → » vers les chapitres de Formation-Zeta-HR (D17)` : IA `c76af4a`, C `a230756`, main `9bdd205`, Test `da175bc` (cherry-pick -x), local = origin. SHA-256 de `docs/index.html` identique sur les 4 (`e082fece…`). Sauvegarde : `pdf/archive/index.html.bak-202611121412`.

## 6. Non vérifié
- Défilement sur les chapitres hors 5 chez hprzeta ; sur un téléphone.
- Captures : `captures/d17_avant_lire_ch11.jpg` faite ; `d17_apres_lire_ch11.jpg` non faite (outil instable).

---
*RAPPORT_CORRECTION_ANCRES_FORMATION_20261112_1531.md · projet SITE ZETA · hprzeta · MAJ 12 novembre 2026 15:31 · 49 lignes*
