# Discussion Claude Code — 6 septembre 2026

> Archive complète de la session du 06/09/2026 — nettoyage des fichiers locaux
> hérités du 05/09, audit de cohérence site/wiki, test A/B expérimental sur le
> déficit de zéros du run T=5M, et diagnostic mathématique définitif du
> phénomène. Les extraits de code modifiés ne sont pas reproduits ici ; seuls
> les tableaux, rapports, conclusions et les instructions transmises par
> hprzeta sont conservés.

---

## 1. Point projet — reprise de session

**Demande de hprzeta :** « point projet ».

Le bloc `PROMPT_REPRISE` de `~/riemann_handoff/Handoff.md` a été affiché tel
quel (mécanisme standard) puis résumé en 3 lignes : session du 05/09 (soirée)
close sur l'accès distant WireGuard (Proton VPN identifié comme cause,
`wg_auto.sh` v2 committé), avec 16 fichiers locaux volontairement laissés non
commités sur `Riemann_Lab_C`, dont un zip suspect (`Pass-20260819...zip`)
jamais ouvert.

---

## 2. Nettoyage des fichiers non commités hérités du 05/09

**Demande de hprzeta :** « passons au prochaine actions ».

### 2.1 Commit des scripts jump-host

`scripts/zeta_monitor.py` et `scripts/zeta_tmux.sh` (modifiés pour router via
le bastion `10.10.0.1` en déplacement) relus intégralement — aucun secret
trouvé (IP LAN et chemins de clés uniquement). Un bug mineur repéré et corrigé
avant commit : une condition `ping` dupliquée sur elle-même dans
`zeta_tmux.sh` (reliquat de copier-coller, inoffensif). **Committé et poussé**
sur `Riemann_Lab_C`.

### 2.2 Fichiers marqués usage privé

Sur choix de hprzeta, `BOX-SFR-GR140IG-Addendum-20260823.md` et
`RAPPORT-SESSION-RESEAU-20260823-v2.md` déplacés vers
`~/riemann_handoff/secrets_local/` (hors dépôt), plutôt que gitignorés sur
place.

### 2.3 Zip `Pass-20260819...zip`

**Instruction explicite de hprzeta :** « mettre dans dossier local secret ne
jamais comiter ce zip pass » — jamais ouvert par Claude Code, déplacé tel
quel. Un commentaire `.gitignore` préexistant (daté du 05/09) confirmait déjà
qu'il contient la clé privée WireGuard du pair téléphone (`10.10.0.3`).

### 2.4 Vérification de sécurité des 5 autres `.zip` et 7 `.bak*`

**Demande de hprzeta :** vérifier le contenu de tous les fichiers non commités
restants avant toute décision.

| Fichier | Résultat de la vérification |
|---|---|
| `brain-vault_ajout_cryptozeta.zip`, `brain-vault_ajout_primalite.zip` | Notes mathématiques, rien de sensible |
| `drive-download-...zip` | 2 PDF personnels (CV, offre d'emploi) — pas un secret de sécurité |
| `files.zip` | Export markdown ancien du wiki, propre |
| `skills-main.zip` | Dépôt open-source de skills, propre |
| 7 `.bak*` de scripts (`wg_auto.sh` ×3, `zeta_monitor.py`, `zeta_tmux.sh` ×2, `rapport_clonage_zeta.md`) | Aucun secret, cohérents avec les versions déjà commitées |
| `Zeta-20260819...zip` (182 Mo) | Extraction complète + grep + inspection visuelle de 4 captures WireGuard : l'app ne montre que la **clé publique** en vue lecture seule, jamais la clé privée. Un fichier `Box fibre.html` (page sauvegardée de l'interface de la box SFR) contient une **IPv6 publique réelle** dans une règle NAT WireGuard — même catégorie de sensibilité que le fichier `BOX-SFR-...` déjà traité. Un fichier `cle_publik_wirgar.jpg` (brouillon email) vérifié comme étant réellement la clé **publique** (correspond au champ « Pair > Clé publique » des captures), donc non sensible par conception WireGuard. |

**Conclusion :** aucune clé privée, mot de passe ou token trouvé dans les 6
zips ni les 7 `.bak*` (hors le zip `Pass-...` déjà identifié comme sensible et
jamais ouvert).

### 2.5 Décision finale — tout déplacer sans tri fichier par fichier

**Instruction explicite de hprzeta :** « tout ce que je ne commit pas met le
dans secret_local jamais comité ». 13 fichiers restants (6 zips + 7 `.bak*`)
déplacés vers `~/riemann_handoff/secrets_local/`. `git status` du dépôt
principal redevenu propre. Règle `.gitignore` (`secrets_local/`) ajoutée en
garde-fou défensif, au cas où ce dossier serait un jour copié par erreur dans
l'arbre du projet. **Committé et poussé.**

---

## 3. Point projet (rappel du bloc de reprise)

**Demande de hprzeta :** « que dit le prompte de reprise » — le bloc le plus
récent du Handoff a été réaffiché intégralement à l'écran (contenu identique
à la section 2 ci-dessus, résumant la session en cours).

---

## 4. Audit de cohérence site/wiki et liens cassés

**Demande de hprzeta :** vérifier que le site (`docs/index.html`) correspond
aux données déclarées dans le wiki (cohérence des valeurs calculées) et
vérifier les liens vers `.pdf/.py/.csv/.png/.svg/.md` (« jen ai trouvé »
cassés). Consigne : faire la liste avant de corriger.

Audit délégué à un agent en tâche de fond (lecture seule, ~7 minutes) sur deux
volets.

### 4.1 Volet A — incohérences de valeurs (résumé, par gravité)

| # | Gravité | Problème |
|---|---|---|
| 1 | Majeur | Erreur de calcul **×100** sur les « gains globaux vs v1 » : le site affichait `×78 650+` (v16) au lieu de `×787,5` réel (21h/1,6min). Même erreur pour v15, v13, v10, v9. Bug présent à l'identique sur le site ET le wiki (copié, pas un désaccord entre les deux). |
| 2 | Majeur | Vitesse PC2 : site affichait « 52 z/s (v13+python-flint) » — en réalité mesuré **sans** python-flint ; avec, c'est 512 z/s (ratio réel ×1,6, pas ×12). |
| 3 | Modéré | CPU PC3 affiché « Intel Pentium E2140 » partout, alors que le CPU réel confirmé (`lscpu`) est **AMD Athlon II X2 215**. |
| 4 | Modéré | Tableau T=10 000 du site : une ligne étiquetée « v2 » affichait en fait les valeurs de v1 ; une ligne (v4.1+Arb) manquante. |
| 5 | Mineur | En-tête de colonne « Gain vs v7 » trompeur ; doublon de titre `## §17` dans `Bibliotheques.md`. |

### 4.2 Volet B — liens cassés

Aucun lien cassé dans `docs/index.html` lui-même. 5 liens cassés dans le wiki
(fichiers `.py`/`.csv` déplacés vers `docs/archive/` sans mise à jour des
liens). 5 liens internes `[[Page]]` pointant vers des pages jamais créées.

---

## 5. Correction complète et retest

**Instruction de hprzeta :** « Tout corriger et retester ».

Toutes les incohérences listées ont été corrigées sur le site et le wiki, à
l'exception de 3 liens `[[Étape-2/3/4]]` explicitement marqués « (à venir) »
(non touchés — ce n'est pas une erreur). Découverte en cours de correction :
`docs/Bibliotheques.md` et `docs/Formules_zeta.md` étaient des copies figées
du wiki (miroir pour le site), manquant plusieurs sections récentes —
resynchronisées. Retest effectué : parsing HTML sans erreur, existence
vérifiée de tous les fichiers cibles des liens corrigés, recherche des
anciennes valeurs dans le code → zéro résidu.

**Point signalé à hprzeta sans être corrigé (hors périmètre de la demande) :**
le même bug de calcul ×100 a été retrouvé répliqué dans des documents datés
(`JOURNAL.md`, le `Handoff.md` du wiki, `Roadmap.md`, tous les
`analyse_problemes_v*.md`) — laissés tels quels, car ce sont des comptes-rendus
historiques et non des références vivantes ; décision de les corriger ou non
explicitement laissée à hprzeta.

**Committé et poussé** sur les deux dépôts (repo principal et wiki), sur
validation explicite de hprzeta après visualisation des diffs.

---

## 6. Test A/B — piste du bruit de phase `Z_double` sur les 96 zéros manquants

### 6.1 Cadrage de la demande

hprzeta a fourni un protocole détaillé pour trancher si l'écart binaire entre
`scan_arb.c` v13 (division directe) et v16 (multiplication par inverse
précalculé) explique les 96 zéros manquants du run T=5M historique, avec un
cadre strict : run court et surveillé (~1-2h max), `systemd-inhibit`,
persistance CSV immédiate, `--skip-rescan`, aucune touche aux clés/réseau.

Une première formulation de la demande a été interrompue par hprzeta
lui-même (« stop tou cest un mauvais prompte ») avant tout calcul — aucune
commande à risque n'avait été exécutée à ce stade (uniquement de la lecture
git). hprzeta a ensuite renvoyé le même protocole détaillé pour relancer
proprement.

### 6.2 Préparation — correction d'une prémisse erronée

Avant de lancer quoi que ce soit, vérification dans le code réel du projet :
contrairement à l'hypothèse de départ (« STEP=0,010 fixe, MARGE_SECURITE=3,0 »),
le STEP est en réalité **adaptatif** depuis le 17/06/2026, et
`MARGE_SECURITE` a été recalibré plusieurs fois au fil du projet (2,0 → 3,0 →
15,0 → 10,0, valeur actuellement validée en production). Le vrai run v13
historique (27/06/2026, celui qui a produit les 96 manquants) utilisait en
réalité **MARGE=2,0, STEP=0,001571** — valeur reconstituée par calcul direct
et confirmée exacte contre la documentation du projet.

**Décision de hprzeta** après présentation de ce constat : reproduire
**exactement** la grille d'apparition du 96 (STEP=0,001571 / MARGE=2,0)
plutôt que la grille plus fine actuellement en production, afin d'isoler la
seule variable « binaire » sans en changer d'autres en même temps.

### 6.3 Exécution du test

Fenêtre retenue : `[14, 1 391 397]` — bornes exactes des segments 0 et 1 du
run historique, là où plus de 90 % du déficit se concentre. 8 workers, mode
turbo, `systemd-inhibit` actif pendant toute la durée.

**Incident méthodologique en cours de route** (documenté tel quel, la leçon
comptant autant que le résultat) : une estimation de durée intermédiaire,
faite pendant que le Run A (binaire v13) tournait encore, s'est révélée trop
pessimiste — un ralentissement observé sur les derniers workers a été
interprété à tort comme un risque de dépassement du budget de plusieurs
heures. hprzeta a proposé de tuer le run et de se limiter aux workers déjà
terminés. En vérifiant l'état réel du processus au moment de reformuler le
plan, le Run A s'était en fait **terminé naturellement, dans les temps**
(69,8 minutes, fenêtre complète). Le Run B (binaire v16, mêmes paramètres
exacts) a ensuite été lancé sur la fenêtre complète, sur validation de
hprzeta, et a pris 48,8 minutes.

**Fausse alerte annexe, clarifiée en cours de test :** hprzeta a signalé
qu'un tableau de bord affichait une erreur rouge côté PC2 (« could not
convert string to float »). Vérification faite avant de poursuivre : cette
erreur provenait d'un processus de supervision totalement indépendant
(`scripts/zeta_run_progress.py`, lancé séparément), dans un panneau
cosmétique de statistiques système interrogeant PC2 par SSH — sans aucun
rapport avec le test A/B, qui tournait intégralement en local sur PC1 sans
aucune dépendance réseau ni PC2.

### 6.4 Résultat du test A/B

| Run | Binaire | Durée | Zéros trouvés |
|---|---|---|---|
| A | v13 (`7914fa3`, division directe) | 69,8 min | 2 504 084 |
| B | v16 (`d4b3611`, cache réciproque) | 48,8 min | 2 504 084 |

**Diff zéro-à-zéro** (plus proche voisin, tolérance 1e-4) : 2 504 084 zéros
appariés, **0 zéro présent dans un run et absent de l'autre, écart maximal
mesuré = 0,000e+00.** Validation Turing exacte appliquée à chaque CSV : déficit
strictement identique aux 5 points de contrôle (33 manquants sur la fenêtre
complète, dont 18 exactement au point historique t=737 112 — reproduction
fidèle et exacte du déficit v13 déjà validé à ce point).

**Conclusion du test :** l'écart binaire ULP division/multiplication n'a
aucun effet mesurable sur la détection des zéros. La piste est réfutée.

---

## 7. Synthèse mathématique définitive du déficit de zéros

hprzeta a fourni un document de synthèse mathématique
(`Analyse-Deficit-Zeros-Grille-20260906.md`), établi par lui à partir de deux
moteurs d'analyse externes indépendants, avec des instructions précises de
mise à jour documentaire (section 8 du document).

### 7.1 Verdict mathématique

1. **Bruit ULP (division vs multiplication) : réfuté** — bruit théorique de
   l'ordre de $10^{-16}$ contre un seuil de détection de l'ordre de $10^{-3}$
   (rapport $10^{13}$), cohérent avec l'écart nul mesuré au test A/B.
2. **Enjambement de paires proches (statistique GUE, Montgomery) :
   négligeable** — de l'ordre de 0,06 à 0,08 zéro attendu sur la fenêtre
   testée, contre 18 à 51 observés (deux ordres de grandeur d'écart), et
   prédisant en plus la mauvaise localisation (déficit croissant à haut $t$,
   alors que l'observation est l'inverse).
3. **Cause réelle retenue : fragilité de la formule de Riemann-Siegel
   tronquée à bas $t$** — le nombre de termes de la somme diminue fortement à
   bas $t$ (un seul terme à $t=14$), rendant toute petite erreur
   d'approximation relativement énorme à cet endroit précis — profil
   exactement conforme au déficit observé.
4. **Non-menace pour l'Hypothèse de Riemann** : il s'agit de zéros **non
   détectés** par une formule tronquée, pas de contre-exemples — ils sont
   bien situés sur la droite critique. L'Objectif 1 du projet reste validé.

### 7.2 Correction d'une explication historique

L'explication « paires de zéros proches non détectées par la grille »,
présente depuis le run v13 (27/06/2026) dans plusieurs documents du projet,
est **définitivement invalidée** par le chiffrage ci-dessus (écart de 3
ordres de grandeur). Cette explication avait déjà été mise en doute une
première fois le 18/08/2026, sans chiffrage définitif à l'époque.

### 7.3 Documentation mise à jour et poussée

| Document | Modification |
|---|---|
| `Formules_zeta.md` (wiki) | Nouvelle section — condition de raté d'un zéro, formule d'enjambement quantifiée, corrections de rigueur relevées par la revue croisée |
| `Bibliotheques.md` (wiki) | Nouvelle section — références théoriques utilisées (Riemann-von Mangoldt, Montgomery, Gaudin, Gonek-Hughes, Farmer-Gonek-Hughes, Turing-Backlund) |
| `JOURNAL.md` (wiki) | Nouvelle entrée datée — verdict complet et correction explicite de l'ancienne explication |
| `STACK.md` (wiki) | Ligne de statut du run T=5M corrigée |
| `Analyse-Deficit-Zeros-Grille-20260906.md` | Document source ajouté au wiki — 2 occurrences d'une notation mathématique non conforme aux règles du projet corrigées avant publication |
| `docs/Formules_zeta.md`, `docs/Bibliotheques.md` (site) | Copies miroir resynchronisées avec le wiki, pour ne pas recréer l'écart corrigé en section 5 |
| Skill mathématique du projet | Mémo ajouté sur les pièges numériques à bas $t$ — non versionné (ne vit qu'en local) |

Tous les diffs ont été montrés intégralement avant tout push, conformément à
la consigne de hprzeta. **Committé et poussé** sur les deux dépôts (wiki et
repo principal) après validation.

---

## 8. Points projet et mise à jour du Handoff

Deux points projet ont été demandés en cours de session (avant et après le
test A/B) — le bloc `PROMPT_REPRISE` de `~/riemann_handoff/Handoff.md` a été
affiché tel quel puis résumé en 3 lignes à chaque fois. Le Handoff a été mis à
jour deux fois : une première fois après le nettoyage des fichiers locaux
(section 2), une seconde fois après le diagnostic complet du déficit de zéros
(sections 6 et 7), chaque fois avec un nouveau bloc daté ajouté en tête,
laissant les blocs précédents inchangés en dessous (fichier append-only).

---

## 9. Clôture de session

**Demande de hprzeta :** « bye bye »

**Résumé des hash de fin de session :**

| Dépôt | HEAD |
|---|---|
| `Riemann_Lab_C` | `a0ddbe9` (poussé) |
| Wiki `master` | `727ff85` (poussé) |

**Chantiers clos cette session :** nettoyage des 16 fichiers locaux hérités du
05/09 (tous déplacés vers `~/riemann_handoff/secrets_local/` ou commités),
audit et correction de la cohérence site/wiki, diagnostic définitif du
déficit de zéros bas-$t$ (piste ULP et piste GUE toutes deux réfutées).

**Volontairement non touché :** le bug de calcul ×100 dans les documents
datés (`JOURNAL.md`, `Handoff.md` du wiki, `Roadmap.md`,
`analyse_problemes_v*.md`) — décision différée à hprzeta. Le test discriminant
proposé par la synthèse mathématique (canal erreur sur $N$ vs canal reste
$R(t)$) et la solution long terme v17 — documentés mais non exécutés.

**Reste ouvert pour la prochaine session :**
- Décider si les documents datés portant le bug ×100 doivent être corrigés ou
  conservés comme archive historique.
- Si repris un jour : test discriminant léger sur la cause exacte du déficit
  bas-$t$ ; solution long terme v17 (schéma hybride de grille).
- Régénération de la clé WireGuard PC4 et du token DuckDNS (action hprzeta,
  hors Claude Code — item hérité de longue date).
- Chantiers hérités si hprzeta souhaite les reprendre : fiabilité de PC1,
  confirmation du bon fonctionnement du backup PC3.

---

*Document généré à la demande de hprzeta le 06/09/2026 — archive de session,
Claude Code — Riemann_Lab, branche `Riemann_Lab_C`.*
