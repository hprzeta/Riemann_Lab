# Rapport de mise à jour — wiki D10 et phrase du site D13 (12/11/2026 02:22)

> Exécution de `PROMPT_MAJ_WIKI_D10_20261112_0213.md`. Source des valeurs : `docs/V17.md` l. 18, relue avant d'écrire (mesure du 07/11/2026, déficit fabriqué, STEP de scan 0,20 à 0,45, non transposable tel quel à la production). Aucun chiffre inventé.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Wiki D10 (l. 507) | 🟢 | en ligne : ligne du rescan avec le texte court, 0 occurrence de « gain non mesurable » ; pied « … · 12 novembre 2026 (phrase du rescan alignée sur V17.md) — 532 lignes » (`wc -l` = 532) | — |
| Site D13 (l. 1768) | 🟢 | en ligne : texte court + lien `V17.md` (`target=_blank`), 0 occurrence de « 36/118/385 » et de « non mesurable » | — |
| Lien `V17.md` | 🟢 | 200 (`curl`), s'ouvre sur « Riemann_Lab/docs/V17.md » dans Chrome | — |
| Publication | 🟢 | 4 branches du code et wiki : local = origin ; SHA-256 de `docs/index.html` identique (`efa1a7fe…`) ; GitHub Pages servi avec le même SHA | — |
| Liens du site | 🟢 | 41 liens distincts, tous en 200 (`curl -sIL`) | ancres `#…` non vérifiées |
| Formules | 🟢 | site : 53 rendues, 0 `.katex-error`, 0 formule brute ; wiki : 0 erreur de rendu détectée | — |
| Console et réseau | 🟢 | 0 erreur console ; 49 requêtes (3 chargements), toutes en 200 | — |
| Mobile 390 px | 🟢 | `scrollWidth` = `clientWidth` = 373 (iframe de 390 px) ; ordinateur 1219 = 1219 | — |
| Audit des lignes ajoutées | 🟢 | aucune IP, MAC, clé, jeton, e-mail, duckdns, fe80:: (wiki et site) | — |
| Pied du site | 🟢 | « mis à jour le 12/11/2026 » (déjà à la date du jour) | — |
| Captures | 🟡 | `wd10_avant_wiki` et `wd10_apres_wiki` cadrent mal la ligne 507 (défilement) ; pas de capture « avant » du site pour D13 ; pas de capture 390 px (la fenêtre n'a pas pu être redimensionnée, mesures par iframe) | refaire les captures encadrées si nécessaire |

## 2. Écarts et précisions
- **Wiki l. 507** : le texte court est écrit sans répéter « rescan décalé STEP/3 », déjà présent en début de ligne. Le commit `7e583d4` de la ligne est conservé.
- **Pied du wiki** : « Dernière mise à jour : **11 novembre 2026** » est resté en tête ; le segment du 12/11 est ajouté à la fin, comme demandé.
- **Autres occurrences de « non mesurable »** : seulement dans des copies `.bak` du dépôt (historiques, non publiées), laissées telles quelles.
- **Aperçu local** : un premier lancement du serveur local a échoué parce que `pgrep -f` s'était trouvé lui-même ; relancé et vérifié (200), arrêté en fin de session.

## 3. Tableau de modifications

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| wiki `Etape-1-Calcul-des-zéros-non-triviaux.md` l. 507 | gain mesuré le 07/11/2026 sur un déficit fabriqué (STEP de scan 0,20 à 0,45, bien au-dessus de la production), non transposable tel quel à la production, où le rescan ne se déclenche presque jamais — détail chiffré dans `V17.md` | **gain non mesurable en conditions réelles** (rejeu sur 13 isolés : le scan principal les retrouve déjà) | 12/11/2026 02:17 (`f481583`) |
| wiki même page, pied (l. 532) | … · 12 septembre 2026 (correction rendu KaTeX) · 12 novembre 2026 (phrase du rescan alignée sur V17.md) — 532 lignes | … · 12 septembre 2026 (correction rendu KaTeX) — 532 lignes | 12/11/2026 02:17 (`f481583`) |
| `docs/index.html` l. 1768 | V17 : rescan décalé STEP/3 : gain mesuré le 07/11/2026 sur un déficit fabriqué (STEP de scan 0,20 à 0,45, bien au-dessus de la production), non transposable tel quel à la production, où le rescan ne se déclenche presque jamais — détail chiffré dans `V17.md` (lien vers `docs/V17.md`) | V17 : rescan décalé de STEP/3, gain mesuré le 07/11/2026 avec un déficit fabriqué (STEP de scan 0,20 à 0,45, très supérieur à la production) : à 10⁵ (31 095 zéros), 36/118/385 manquants restants en phase 1/3 contre 66/184/605 en phase 0 ; à 10⁶ (9 533 zéros), 16/58/181 contre 20/100/364 ; la phase 0 retrouve parfois des zéros que 1/3 rate ; non transposable tel quel à la production, où le rescan ne se déclenche presque jamais (source : docs/V17.md) | 12/11/2026 02:20 (`abb7e96`) |

## 4. Commits

| Dépôt | Branche | Avant | Après |
|---|---|---|---|
| wiki | `master` | `74320e5` | `f481583` |
| code | `Riemann_Lab_IA` | `2b6edc0` | `abb7e96` |
| code | `Riemann_Lab_C` | `40ce140` | `f142a5c` |
| code | `main` | `f77ef4c` | `9b1035c` |
| code | `Riemann_Lab_Test` | `2e2ffb1` | `fa85f7e` |

Push sans `--force`. Sauvegardes avant : `pdf/archive/Etape-1-Calcul-des-zeros-non-triviaux.md.bak-202611120217` et `pdf/archive/index.html.bak-202611120217`.

## 5. Reste à faire
- Contrôle visuel à 390 px dans un vrai navigateur mobile ; ancres `#…` des liens.
- Captures encadrées de meilleure qualité si besoin.

---
*RAPPORT_MAJ_WIKI_D10_20261112_0222.md · 12/11/2026 02:22 · 52 lignes*
