# Discussion Claude Code — session du 07/11/2026

**Projet :** Riemann_Lab · **Auteur :** hprzeta · **Branche de travail :** Riemann_Lab_IA (4 branches synchronisées)

> Archive narrative de la session (instructions de hprzeta citées, résultats et conclusions). Les extraits de code modifiés sont exclus.

**Fermeture de session.** Turbo Zêta : RESTAURÉ (vérifié : 4 CPU à leur gouverneur initial (cpu0=powersave), swappiness 10).
**Capture brute :** active pendant la session ; fichier `claude-traitement-journalier/session_20261107_1213.log` (le `.md` associé sera généré au second `exit`). Non commitée (volumineuse, risque d'adresses ou de secrets).

---

## 1. Point projet et audit-commit initial

> « point projet »

Bloc de reprise du Handoff du 05/11 lu : pipeline V17 distribué PC1+PC2 ; trois fichiers non commités ; décisions ouvertes (publication du jeu 5·10⁶, seuil de pentes D38).

> « audit puis commit des 3 fichiers » puis « go »

Audit des lignes ajoutées (scripts, documentation, texte du PDF) : aucun motif sensible. Commit `40fca29` sur Riemann_Lab_IA, reporté par cherry-pick sur main, Riemann_Lab_C et Riemann_Lab_Test (`f4e715b`, `3034d85`, `d5b109d`), poussé sans `--force`. `monitoring/Monitoring-Runs.md` laissé de côté, hors demande.

## 2. Décisions de hprzeta

> « ok pour trancher la publication du jeu 5·10⁶ et le seuil de pentes (D38) » — puis questions : release GitHub, licence CC BY 4.0, seuil 3 conservé.
> « pourquoi il est nécessaire de publier ce jeu ? » — puis : « ne pas publier, noter dans le Handoff »

Conclusion : la publication n'est pas nécessaire (choix de visibilité, irréversible en pratique, valeur scientifique limitée face à LMFDB/Odlyzko). **Décision : jeu 5·10⁶ non publié**, référence interne (SHA-256 b3a98a34…53ce0, 10 016 474 zéros). **Seuil de pentes D38 : 3 conservé** (erreur max mesurée 5,6·10⁻¹⁰). Le paquet de publication du 05/11 avait disparu avec l'ancien scratchpad. Noté dans le Handoff.

## 3. Run distribué T = 10⁶ et recalage des vitesses

> « traitons les points ouverts » puis « go, lance le run T=10⁶ »

Simulation à blanc : 29,1 min (PC1) et 24,0 min (PC2) prévues avec les débits 858 / 173 z/s. **Run réel (mesuré) :** 1 747 146 zéros (1 747 144 attendus), **Turing COMPLET** (0 manquant, T_max 999 999,79), **mur 49,34 min** (590 z/s effectifs).

| | Zéros | Durée | Débit |
|---|---|---|---|
| PC1 | 1 497 954 | 49,30 min | ≈ 506 z/s |
| PC2 | 249 192 | 42,97 min | ≈ 97 z/s |

Débits calculés zéros ÷ durée. Les débits figés étaient trop optimistes d'un facteur ≈ 1,7 (PC1) et ≈ 1,8 (PC2).

> « recaler les ancres de vitesses avec ce run » puis « go »

3ᵉ ancre (10⁶ : 506 / 97 z/s), interpolation en ln T par morceaux, valeurs figées hors [10⁵ ; 10⁶] ; prévisions du dry-run à T=10⁶ : 49,7 / 41,0 min contre 49,3 / 43,0 mesurées. Points intermédiaires (2·10⁵, 7·10⁵) interpolés, non mesurés. Commits `5ce06cc`, `7f4c01c`, `e8edc30`, `672656b`.

## 4. Guide de run et PDF

> « régénère le PDF du guide avec la 3ᵉ ancre » puis « go commit le PDF sur les 4 branches »

Le générateur ReportLab d'origine n'existait plus ; PDF produit avec une copie corrigée du script du guide des scripts (spans de code protégés, titre et pied). Guide passé en v0.17 (63 pages). Commits `a61a5b8`, `9950b72`, `b95fbe1`, `46c4319`.

## 5. Fausse piste « erreur ps » (point 3 des points ouverts)

> « enquête sur le point 3, l'erreur ps »

**Conclusion (vérifiée) : fausse piste de ma part.** L'erreur « syntaxe dans la liste des ID de processus » ne figurait pas dans les logs du run ; elle venait de ma propre commande de suivi, le fichier PID étant supprimé en fin de run (correctif D49 du 05/11), donc `ps -p` recevait un argument vide. Reproduit à l'identique. Phrase fausse retirée du guide, PDF régénéré, Handoff corrigé par ajout d'une entrée. Commits `a50d59b`, `a2bf86c`, `e95b485`, `89af531`.

## 6. Les quatre points ouverts

> « ok traitons ces 4 points »

1. **Générateur du PDF du guide** : script `build_pdf_guide_run.py` versionné ; texte du PDF régénéré identique au PDF commité. Commits `1745208`, `6183923`, `4470039`, `7f45da0`.
2. **Compteur du tableau de bord à 0 %** : cause trouvée, ce n'est pas un défaut du tableau de bord. Les workers n'écrivent leur première ligne *zéro #1000* qu'après la phase de scan, silencieuse (mesuré à T=10⁶ : de 1 093 s à 2 717 s sur PC1, 2 316 s et 2 447 s sur PC2). Décision de hprzeta : option A (affichage « phase de scan en cours » au lieu de 0 %). Commits `289667f`, `6bab587`, `627b1de`, `bd39c98`.
3. **`tmux attach` interactif** : à faire par hprzeta dans deux terminaux ; étapes fournies une à une.

> « ok pour tmux tout est ok »

Rapporté par hprzeta ; détails non transmis, non vérifiés séparément par Claude.

4. **Gain du rescan décalé** : décision « chantier de test ».

## 7. Mesure du gain du rescan décalé (déficit fabriqué)

Script `mesure_rescan_phase.py` : scan de base avec un STEP volontairement trop grand (0,20 ; 0,30 ; 0,45), rescan à STEP/2 en phase 0 (ancien) et en phase 1/3 (actuel), référence = scan au STEP de production réel. Zéros manquants restants :

| Segment | STEP gros | Phase 0 | Phase 1/3 |
|---|---|---|---|
| [10⁵ ; 1,2·10⁵] (31 095 zéros) | 0,20 / 0,30 / 0,45 | 66 / 184 / 605 | 36 / 118 / 385 |
| [10⁶ ; 1,005·10⁶] (9 533 zéros) | 0,20 / 0,30 / 0,45 | 20 / 100 / 364 | 16 / 58 / 181 |

La phase 1/3 laisse moins de zéros manquants dans les 6 cas ; la phase 0 retrouve parfois des zéros que 1/3 rate. **Limites :** déficit artificiel (STEP 100 à 300 fois ceux de la production, où le rescan ne se déclenche presque jamais), référence = un scan, deux zones seulement. CSV locaux, non commités. Commits `97862b8`, `a3a79f7`, `60d857b`, `173327d` ; guide v0.18 : `c929715`, `7ea233d`, `f6ffc63`, `856ee02`.

## 8. Option B : progression du scan v17

> « ok option B » — puis « go, commite les 3 fichiers puis synchronise PC2 » et « go, lance le run test T=100000 »

Le scan (un seul appel C opaque) est découpé en environ 40 blocs de pas entiers par worker, avec une ligne `scan N%` entre deux blocs ; le tableau de bord affiche le pourcentage de scan. **Vérifications (mesurées) :** sur [14 ; 20 000], 4 workers, même STEP : 22 491 zéros strictement identiques à l'ancienne version (écart max 0) ; tests existants 12 + 16 OK ; 3 nouveaux tests OK. Commits `984da26`, `c68f134`, `75c9b53`, `185a6b1`.

**PC2 :** synchronisation par le script du dépôt (sauvegarde préalable de sa copie) ; copie identique à celle de PC1, `illinois_arb.so` recompilé (sauvegardé).

**Run distribué test T=10⁵ :** 138 069 zéros, Turing COMPLET, 1,61 min mur (1 434 z/s) ; lignes de scan : PC1 40, PC2 16. **Non vérifié :** le pourcentage de scan n'a pas été vu à l'écran avec un chiffre ; l'égalité zéro à zéro avec l'ancienne version est vérifiée seulement sur [14 ; 20 000]. Une première lecture prématurée de ma part (notification d'une tâche de capture arrêtée seule) a été corrigée.

Guide v0.19 (64 pages) mis à jour puis commité : `d64aeb8`, `978d163`, `1121b5f`, `cc7ab92`.

## 9. État final et points ouverts

- Les 4 branches sont alignées sur `origin`, sans `--force`, avec audit des lignes ajoutées à chaque commit.
- Hors commit : `monitoring/Monitoring-Runs.md` (contenu non examiné), guide `.md` (local), CSV de la mesure du rescan, captures.
- **Ouverts :** vitesses non mesurées entre les ancres (2·10⁵, 7·10⁵) et au-delà de 10⁶ ; pourcentage de scan jamais vu à l'écran avec un chiffre ; égalité zéro à zéro avec l'ancienne version vérifiée seulement sur [14 ; 20 000].

> « bye bye »

---
*Archive de session — 2026-11-07*
