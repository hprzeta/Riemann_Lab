---
title: "Rapport — corrections issues du 1er test automatique"
date: "12/11/2026 01:26"
---

# Rapport — corrections issues du 1er test automatique (12/11/2026)

Prompt exécuté : `PROMPT_CORRECTIONS_TEST_AUTO_20261112_0115.md`. Décisions : D7 (c) bandeau avec les deux totaux ; D8 turbo non touché ; D9 ancien état gardé. Non touchés : `monitoring/Monitoring-Runs.md`, le wiki, les hooks, le turbo.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Correction 1 : bandeau + pied du site | 🟢 | Site en ligne : bandeau « 10 016 474 zéros calculés (T=5·10⁶) · 138 069 zéros à T=100 000 … », pied « mis à jour le 12/11/2026 » (`captures/corr_apres_bandeau.jpg`, `corr_apres_pied_site.jpg`) | — |
| Bandeau sur une ligne | 🟡 | Non tenu : 2 lignes sur ordinateur (45 px pour 19 px de ligne), 4 lignes à 390 px (avant : 1 et 3). Décision prise : garder le texte D7 (c) sur 2 lignes | Aucun, sauf si hprzeta veut un texte plus court |
| Correction 2 : pied de `V17.md` | 🟢 | Texte brut sur `main` : « 2026-11-05 · 2026-11-07 (…) · 2026-11-12 (date du pied corrigée) — 66 lignes » ; `wc -l` = 66 | — |
| Correction 3 : pied du `README.md` | 🟢 | Texte brut sur `main` : « … (pied de page ajouté) · 101 lignes » ; `wc -l` = 101 | — |
| Report sur 4 branches | 🟢 | `cherry-pick -x` sans conflit ; sha256 identiques sur les 4 branches pour les 3 fichiers (`index.html` `d61766143443`, `V17.md` `046855e33853`, `README.md` `728e13a5e22f`) | — |
| Audit avant push | 🟢 | Aucun motif sensible (IP, MAC, clé, jeton, e-mail, duckdns, fe80::) dans les lignes ajoutées | — |
| Push | 🟢 | 4 branches poussées sans `--force` ; local = origin pour les 4 | — |
| Liens du site | 🟢 | 43 URL distinctes (ancres retirées) toutes en 200 (`curl -sIL`) | Ancres `#…` non vérifiées (`curl` ne les voit pas) |
| Formules | 🟢 | 0 `.katex-error`, 53 formules rendues, 0 formule brute | — |
| Console et réseau | 🟢 | Suivi actif avant le rechargement : console vide ; 16 requêtes, toutes en 200, 0 requête ≥ 400 | — |
| Test automatique | 🟢 | `bash -n` OK ; minuterie active (prochain passage 04:06) ; nouveau prompt `PROMPT_TEST_AUTO_MAJ_SITE.md` en place | Utilisé au prochain test réel (demain) |
| Débordement horizontal à 390 px | 🟡 | Existait déjà avec l'ancien texte : 614 px pour 378 px, causé par le bandeau de formules `.eq-scroll` (KaTeX), pas par le bandeau modifié | Hors périmètre, à traiter à part |
| Phrase du site sur le rescan | 🟡 | Sous le tableau du jeu 5·10⁶, le site dit « gain non mesurable en conditions réelles (rejeu sur les 13 isolés…) » ; `V17.md` dit depuis le 07/11 que le gain a été mesuré avec un déficit fabriqué | À aligner dans une prochaine mise à jour |

## 2. Écarts avec le prompt
- Étape 0 : l'ancien prompt de test a été **déplacé** vers `pdf/archive/PROMPT_TEST_AUTO_MAJ_SITE_avant_20261112_0115.md` au lieu d'être copié en `.bak-20261112`.
- Onglet « Mise à jour site » : il n'existait pas ; l'onglet vide du groupe MCP a été utilisé.
- Objet du commit du 07/11 (correction 2) : formulation choisie d'après `40fca29`, `5ce06cc`, `97862b8` (les commits `672656b` et `173327d` cités par le prompt existent sur une autre branche).
- Report : worktrees temporaires au lieu de `git checkout`, pour ne pas toucher à `Monitoring-Runs.md` modifié ni aux fichiers non suivis. Worktrees retirés.
- Texte GitHub : la traduction automatique du navigateur modifie l'affichage (« crochets », « corrigé ») ; la vérification a donc été faite sur le texte brut.

## 3. Fichiers modifiés

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| `docs/index.html:631` | `138 069 zéros validés · V17 en production (03/11/2026) · 0 manquant ✅ · Obj2 atteint 04/07/2026` | `10 016 474 zéros calculés (T=5·10⁶) · 138 069 zéros à T=100 000 · V17 en production (03/11/2026) · 0 manquant ✅ · Obj2 atteint 04/07/2026` | 12/11/2026 01:21 (commit `2ba709c`) |
| `docs/index.html:1769` | `… mis à jour le 11/11/2026` | `… mis à jour le 12/11/2026` | 12/11/2026 01:21 (commit `2ba709c`) |
| `docs/V17.md:66` | `*Mis à jour : 2026-11-05 — 66 lignes*` | `*Mis à jour : 2026-11-05 · 2026-11-07 (débits interpolés en ln T avec 3e ancre à T=10⁶, mesure du gain du rescan) · 2026-11-12 (date du pied corrigée) — 66 lignes*` | 12/11/2026 01:22 (commit `b695b15`) |
| `README.md:99-101` | (aucun pied) | ligne vide, `---`, `*README.md · hprzeta · MAJ 11 novembre 2026 · 12 novembre 2026 (pied de page ajouté) · 101 lignes*` | 12/11/2026 01:23 (commit `67db8f9`) |

## 4. Commits 

| Branche | Bandeau | `V17.md` | `README.md` |
|---|---|---|---|
| `Riemann_Lab_IA` | `2ba709c` | `b695b15` | `67db8f9` |
| `Riemann_Lab_C` | `cab805c` | `5fc4dd1` | `dfa893b` |
| `main` | `8505f78` | `24e892a` | `b0f2385` |
| `Riemann_Lab_Test` | `a19e169` | `f215bbd` | `fa6f00b` |

Sauvegardes avant modification : `pdf/archive/{index.html,V17.md,README.md}.bak-20261112`. Captures : `captures/corr_avant_*`, `corr_apercu_local_bandeau.jpg`, `corr_apres_*`.

## 5. Retour en arrière
Pour revenir à l'état d'avant : `git revert` des 3 commits sur chaque branche (jamais de `--force`), ou restauration depuis les `.bak-20261112`.

---
*RAPPORT_MAJ_CORRECTIONS_TEST_AUTO_20261112_0126.md · 12/11/2026 01:26 · 59 lignes*
