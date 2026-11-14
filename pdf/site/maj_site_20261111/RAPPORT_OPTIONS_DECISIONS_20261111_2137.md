# Rapport — 3 décisions ouvertes du 11/11/2026 : quelle est la meilleure option ?

> Analyse en lecture seule réalisée le 11/11/2026 à 21:37 d'après `PROMPT_OPTIONS_DECISIONS_SITE_20261111_2127.md`. Aucune modification, suppression, déplacement ni commit. Onglet Chrome « Recherche MAJ site ».

## D1 — `Dossier-md.md` (wiki local, non suivi)

**Faits établis (preuves) :**

- Dossier-md.md : 1 800 octets, 34 lignes, UTF-8 ; créé (birth) le 2026-10-03 23:48, modifié le 2026-10-17 16:31 (stat). Il n'est donc PAS apparu le 11/11 : mon rapport de 21h19 (« absent du premier état de la session ») était inexact, le fichier existait déjà.
- Contenu : page de règles du dossier local md/ (« versions Markdown des PDF », méthode, limites, « État au 2026-10-03 : 61 fichiers »). Aucune valeur identifiante (grep : 0 IPv4, e-mail, MAC, clé, fe80::).
- Décision déjà prise et répétée : journal du 16/10 (« Non commités, volontairement … Dossier-md.md du wiki »), du 05/11 (« non ajoutés »), du 18/10 (« la page Dossier-md n'est toujours pas suivie » : point resté ouvert).
- Non publié : la requête wiki/Dossier-md renvoie à la page d'accueil (capture). Aucune page wiki, aucun fichier du site ni du dépôt ne le référence (grep). Aucun doublon : Arbre_dossiers_projet et Structure-Projet-Complet ne mentionnent pas md/ ; ORGANISATION_FICHIERS le cite une fois.
- Chiffres périmés : le fichier dit 61 fichiers et 75 PDF ; état réel mesuré : 158 .md dans md/ et 123 PDF dans pdf/. md/ est exclu de git (.git/info/exclude, ligne md/). md/Dossier-md.md n'existe pas encore.

| option | avantages | risques | réversible ? | preuve |
|---|---|---|---|---|
| (a) Le laisser local non suivi | Zéro risque ; respecte la décision répétée depuis le 16/10 | Reste en « ?? » dans git status (bruit permanent, point ouvert depuis le 18/10) ; poussable par un git add -A ; chiffres périmés (61 / 75 au lieu de 158 / 123) | Oui | stat, journaux 16/10, 18/10, 05/11 |
| (b) Le commiter dans le wiki | Documente la méthode md/ pour les lecteurs ; plus de « ?? » | Publie l'organisation d'un dossier privé hors git ; à mettre à jour (chiffres, pied) ; il faut un lien de navigation (aucune page ne le référence) ; 1 commit + 1 push | Oui (revert) mais publié | page non publiée (capture) ; 0 référence |
| (c) Le déplacer dans md/ (md/Dossier-md.md) | Le fichier décrit md/ : il y vit à côté de son sujet ; md/ est local, exclu de git ; supprime le « ?? » du wiki ; rien n'est supprimé ; 0 commit | Perd la visibilité côté wiki (il n'y était pas publié) ; un oubli de mise à jour des chiffres reste possible | Oui (mv inverse) | .git/info/exclude : md/ ; md/Dossier-md.md absent |
| (d) Le supprimer après sauvegarde | Plus aucun bruit | Perd la seule description des règles de md/ ; contraire à « on archive, on ne supprime pas » | Seulement via la sauvegarde | règle de suppression du projet |

**Meilleure option : (c) déplacer Dossier-md.md dans md/ — c'est la page de règles du dossier local md/, jamais publiée, aucune référence, et le déplacer règle le point ouvert depuis le 18/10 sans commit ni suppression.**

## D2 — `analyse_math_deficit_2026-08-18.pdf` (local, non suivi)

**Faits établis (preuves) :**

- analyse_math_deficit_2026-08-18.pdf (local) : 117 912 octets, 8 pages, créé le 18/08/2026 (xdvipdfmx). pdftotext : 0 occurrence de la note du 11/11/2026 ; « 96 manquants » : 2 ; « 97 » et « 84 paires » : 0. Il contredit donc les mesures du 05/11 (97, cause 84 paires + 13 isolés).
- Il est volontairement hors git : .gitignore ligne 77 ignore le dossier pdf/optimisation/Voie_b_5/md_to_claude/ (git check-ignore -v). Le .md voisin du même dossier est aussi périmé (0 note).
- Le .md du wiki (19 653 octets, 427 lignes, modifié le 11/11 15:14) porte la note et il est public (capture : encadré « Note du 11/11/2026 »). Il ne contient aucun lien vers un PDF.
- Références : docs/index.html, README.md, Handoff.md, STACK.md : 0 ; wiki : liens [[analyse_math_deficit_2026-08-18]] (page .md) depuis analyse_problemes_v16_v17, Bonnes-Pratiques-Claude-Code, JOURNAL. Aucun lien mort vers le PDF.
- Convention : les analyses publiées sont dans pdf/optimisation/ (14 analyse_problemes_vX_vY.pdf + analyse_problemes_v16_v17.pdf, 53 fichiers identiques sur les 4 branches). Ce PDF n'y est pas.
- Régénération testée dans un dossier temporaire : bash scripts/build_pdf_riemann_CM.sh in.md out.pdf : code 0, 8,9 s, 9 pages, 133 211 octets, note du 11/11 présente (1), « 97 manquants » présent (1).

| option | avantages | risques | réversible ? | preuve |
|---|---|---|---|---|
| (a) Le laisser local | Déjà voulu (dossier ignoré, .gitignore:77) ; 0 commit ; le .md du wiki est public et annoté ; aucun lien ne pointe vers le PDF | Le PDF local est périmé (96 manquants, sans note) : danger s'il est redéposé comme source dans le projet SITE ZETA | Oui | pdftotext ; .gitignore:77 ; grep références |
| (b) Le publier tel quel | Rapide | Met en public un contenu qui contredit les mesures du 05/11 (96, cause réfutée) et sans la note ; il faut un git add -f (chemin ignoré) | Publié = visible | pdftotext : 0 note, 0 « 97 » |
| (c) Le régénérer depuis le .md annoté puis le publier dans pdf/optimisation/ | PDF à jour (note + 97 manquants, test OK) ; cohérent avec les 14 autres analyses | 1 commit sur Riemann_Lab_IA + 3 cherry-pick -x (4 branches) ; aucun lien ne le référence aujourd'hui (publication sans lecteur) ; liens [[…]] affichés bruts dans le PDF | Oui (revert sur 4 branches) | build test : code 0, 9 pages, note présente |
| (d) Le supprimer au profit du .md du wiki | Une seule source de vérité | Perte de l'archive du 18/08 ; contraire à la règle d'archivage | Non, sauf sauvegarde préalable | règle du projet |

**Meilleure option : (a) le laisser local, en régénérant la copie locale depuis le .md annoté (ancienne version archivée) — le PDF n'a aucun lecteur ni lien, la page du wiki est déjà publique et à jour, et publier coûterait 4 commits pour rien ; (c) reste prêt si vous le voulez en ligne.**

## D3 — sauvegardes locales `*.bak*` du wiki

**Faits établis (preuves) :**

- 73 fichiers .bak* dans le wiki (5,8 Mo). git status --short du wiki : 27 lignes « ?? », dont 26 sont des .bak ; 0 fichier .bak suivi par git.
- Exclusion actuelle : .git/info/exclude du wiki contient *.bak-* (pas de .gitignore dans le wiki). Ce motif couvre .bak-20261111 mais PAS .bak2-, .bak3-, .bak5-… : git check-ignore : JOURNAL.md.bak-20261111 IGNORÉ ; …bak2-… et …bak5-… NON ignorés (poussables par git add -A).
- Valeurs identifiantes : 14 JOURNAL.md.bak* contiennent encore l'ancienne adresse fe80::<hex> (comptage seulement), 15 .bak contiennent des motifs IPv4 (non classés) ; 0 clé/jeton. Cette valeur est déjà publique : 2 commits de origin/master la contiennent, le premier du 2026-06-15 (8845a16).
- Dépôt de code : 27 .bak non ignorés dans git status, 217 .bak* au total ; .gitignore ligne 18 = *.bak seulement, exclude = *.bak-* : même lacune.
- Simulation (git -c core.excludesFile avec *.bak*, rien modifié) : wiki 26 → 0 .bak visibles, code 27 → 0 ; 0 fichier suivi ne porte .bak dans son nom (aucun faux positif).
- Dossiers de sauvegarde hors dépôt déjà utilisés : ~/riemann_handoff (88 .bak, 188 Mo), ~/zeta_inventaire (57 .bak). Règle du projet : copie .bak-AAAAMMJJ avant modification, jamais de suppression (on archive).

| option | avantages | risques | réversible ? | preuve |
|---|---|---|---|---|
| (a) Les laisser telles quelles | Aucune action | 26 .bak du wiki et 27 du code apparaissent dans git status et peuvent partir au prochain git add -A ; 14 contiennent l'ancienne valeur fe80 (déjà publique depuis 06/2026) | — | git check-ignore ; git status |
| (b) Exclure *.bak* (fichier .git/info/exclude des deux dépôts) | Corrige la lacune (.bakN- non couvert) ; local, 0 commit, rien de publié ; aucun faux positif (0 fichier suivi en .bak) ; les copies .bak-AAAAMMJJ continuent comme avant | N'efface rien : les valeurs restent dans les .bak locaux | Oui (retirer la ligne) | simulation : wiki 26 → 0, code 27 → 0 |
| (c) Les déplacer hors du wiki | Dossier du wiki propre | Casse l'habitude cp fichier fichier.bakN ; 73 fichiers à déplacer, chemins à documenter ; inutile une fois (b) en place | Oui | ~/riemann_handoff (88 .bak) existe déjà |
| (d) Purger celles qui contiennent une valeur | Retire la valeur du disque | Irréversible, gain nul : la valeur est publique depuis le 15/06 (8845a16) ; contraire à « on archive » | Non | git log -G sur origin/master |

**Meilleure option : (b) ajouter *.bak* à .git/info/exclude du wiki et du dépôt de code — corrige la vraie lacune (motif .bakN-), local, réversible, sans commit, sans rien effacer ; (d) n'apporte rien (valeur déjà publique).**

## Synthèse

| décision | meilleure option | commandes exactes (NON exécutées) | ce qui change dans le dépôt |
|---|---|---|---|
| D1 Dossier-md.md | (c) déplacer dans md/ | `mv ~/projet_zeta/Riemann_Lab.wiki/Dossier-md.md ~/projet_zeta/md/Dossier-md.md   (retour : mv inverse)` | Wiki : « ?? Dossier-md.md » disparaît. md/ (local, hors git) : +1 fichier. 0 commit. |
| D2 analyse_math_deficit PDF | (a) local + régénération locale | `cd ~/projet_zeta && mkdir -p pdf/archive && cp -p pdf/optimisation/Voie_b_5/md_to_claude/analyse_math_deficit_2026-08-18.pdf pdf/archive/analyse_math_deficit_2026-08-18.pdf.bak-20261111 && bash scripts/build_pdf_riemann_CM.sh Riemann_Lab.wiki/analyse_math_deficit_2026-08-18.md pdf/optimisation/Voie_b_5/md_to_claude/analyse_math_deficit_2026-08-18.pdf   (retour : recopier le .bak)` | Seule la copie locale (ignorée) change ; rien dans git. 0 commit. |
| D3 sauvegardes *.bak* | (b) exclure *.bak* | `for r in ~/projet_zeta/Riemann_Lab.wiki ~/projet_zeta; do cp -p $r/.git/info/exclude $r/.git/info/exclude.bak-20261111; echo '*.bak*' >> $r/.git/info/exclude; done   (retour : restaurer le .bak-20261111)` | git status des 2 dépôts : 26 + 27 lignes « ?? .bak » disparaissent. 0 commit, rien de publié. |

## Changements impliqués par les meilleures options (À FAIRE)

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| Riemann_Lab.wiki/.git/info/exclude | [L+1] *.bak* | — | À FAIRE |
| projet_zeta/.git/info/exclude | [L+1] *.bak* | — | À FAIRE |
| Riemann_Lab.wiki/Dossier-md.md → md/Dossier-md.md | [fichier déplacé, contenu inchangé] | [wiki] Dossier-md.md (non suivi) | À FAIRE |
| md/Dossier-md.md (facultatif) | [L28-31] État au 2026-11-11 : 158 fichiers .md ; 123 PDF dans pdf/ ; [L34] Mis à jour : 2026-11-11 — 34 lignes | [L28-31] État au 2026-10-03 : 61 fichiers ; 75 PDF ; [L34] Mis à jour : 2026-10-03 — 34 lignes | À FAIRE (facultatif) |
| pdf/optimisation/Voie_b_5/md_to_claude/analyse_math_deficit_2026-08-18.pdf (local, ignoré) | [8 → 9 pages] note du 11/11/2026 ; « 97 manquants » (84 paires + 13 isolés) | [8 pages] « 96 manquants », sans note | À FAIRE |

## Erreurs et réserves

- Correction de mon rapport de 21h19 : Dossier-md.md n'est pas apparu pendant la session du 11/11, il existe depuis le 03/10 (laissé non suivi volontairement).
- La simulation d'exclusion (core.excludesFile temporaire) montre aussi « ?? .claude/ » dans le wiki : artefact du test (il remplace l'exclusion globale), pas un fichier à traiter.
- Aucune écriture dans les dépôts : seuls les fichiers de rapport, 3 captures et le dossier temporaire du test de régénération (scratchpad) ont été écrits.

Captures : `captures/opt_wiki_dossier_md_absent_redirige_home.jpg`, `captures/opt_repo_pdf_optimisation_sans_math_deficit.jpg`, `captures/opt_wiki_analyse_math_deficit_note_11_11.jpg`.

Prompt de mise à jour prêt (à lancer seulement après votre décision) : `PROMPT_MAJ_DECISIONS_SITE_20261111_2137.md`.

---
*RAPPORT_OPTIONS_DECISIONS_20261111_2137.md · projet SITE ZETA · hprzeta · MAJ 11 novembre 2026 21:37 · 93 lignes*
