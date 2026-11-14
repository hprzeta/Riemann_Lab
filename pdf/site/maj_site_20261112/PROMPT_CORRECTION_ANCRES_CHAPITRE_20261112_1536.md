# PROMPT Claude Code — D17 (suite) : arriver DIRECTEMENT sur le chapitre, pas seulement sur la page

> Préparé sur claude.ai (projet SITE ZETA) le 12/11/2026 à 15:36. Rapport d'analyse : `RAPPORT_ANALYSE_ANCRES_CHAPITRE_20261112_1536.md`.

## ⚠️ Malentendu à corriger d'abord
Quand hprzeta a répondu « les 3 arrivent », il voulait dire : **les 3 liens arrivent sur la page `Formation-Zeta-HR`**, mais **en haut de la page**. Il doit ensuite **défiler à la main** jusqu'au chapitre.
**Ce n'est pas le résultat voulu.** Le correctif `#user-content-chN` (publié à 15:31) **ne règle donc pas** le problème.

**Critère de réussite unique** : après un clic sur « Lire → », **sans aucun défilement**, le **titre du chapitre demandé est visible en haut de l'écran**.
Corriger d'abord le rapport `RAPPORT_CORRECTION_ANCRES_FORMATION_20261112_1531.md` et le handoff : D17 = 🔴 non résolu (« arrive sur la page, pas sur le chapitre »).

## Règles
1. Diagnostic d'abord ; ne pas conclure sans la réponse de hprzeta (ton outil ne défile pas).
2. Pour chaque essai, poser à hprzeta **une question fermée** : « Après le clic, sans défiler, que voyez-vous en haut de l'écran ? (A) le titre de la page / le sommaire ; (B) un autre endroit, au-dessus du chapitre ; (C) le titre du chapitre demandé ». Seul **C** est une réussite.
3. STOP : « go correction », puis « go commit wiki » / « go push wiki » et/ou « go commit site » / « go push ». Jamais `--force`. Site : 4 branches (`cherry-pick -x`).
4. Copie `pdf/archive/<fichier>.bak-<AAAAMMJJHHMM>` avant toute modification. Aucune valeur identifiante. Ne pas toucher : turbo, hooks, minuterie, `monitoring/Monitoring-Runs.md`.
5. Traduction automatique de Chrome désactivée sur github.com pour les tests.

## Étape 0 — Ranger le prompt
```bash
cd /home/riemann/projet_zeta/src/ia/prompts
unzip -n ~/Téléchargements/MAJ_ANCRES_CHAPITRE_20261112_1536.zip
D=/home/riemann/projet_zeta/pdf/site/maj_site_$(date +%Y%m%d); mkdir -p "$D/captures" "$D/A_DEPOSER"
cp -p RAPPORT_ANALYSE_ANCRES_CHAPITRE_20261112_1536.* PROMPT_CORRECTION_ANCRES_CHAPITRE_20261112_1536.md "$D/"
```

## Étape 1 — Diagnostic (lecture seule) — montrer chaque sortie
```bash
W=/home/riemann/projet_zeta/Riemann_Lab.wiki; F="$W/Formation-Zeta-HR.md"
wc -l "$F"; grep -n 'name="ch' "$F" | head -20                     # ancres posées
grep -n '^#\{1,3\} .*Chapitre' "$F" | head -20                      # titres des chapitres
grep -c '!\[' "$F"; grep -c '<img' "$F"                              # images
grep -n '<img\|!\[' "$F" | head -20                                  # ont-elles width/height ?
grep -c '\$\$' "$F"                                                  # blocs de formules
```
Dans Chrome (lecture du DOM seulement) : pour le chapitre 11, relever l'`id` exact du lien d'ancre du titre (`a.anchor` ou `[id^="user-content-chapitre-11"]`), et la présence de `name="user-content-ch11"`.

## Étape 2 — Essais par hprzeta (aucune modification)
Afficher ces URL **cliquables**, toutes vers le chapitre 11, et demander pour chacune la réponse A / B / C (règle 2) :
1. `…/wiki/Formation-Zeta-HR#user-content-ch11` (lien actuel)
2. `…/wiki/Formation-Zeta-HR#<ancre automatique du titre du chapitre 11>` (ex. `#chapitre-11--…`, relevée à l'étape 1)
3. Le **sommaire** de la page wiki : cliquer « Chapitre 11 » dans le sommaire, depuis le haut de la page.
4. Les mêmes 1 et 2, mais **après le chargement complet** : ouvrir la page, attendre 5 s, puis coller l'URL avec l'ancre dans la barre d'adresse et valider.

Interprétation à présenter :
- **Si 4 réussit (C) mais pas 1 et 2** : le saut se fait avant la fin du chargement ; images et formules allongent ensuite la page et le chapitre « s'éloigne ». → **Solution W1** : donner une taille fixe aux images du wiki (`<img … width="…" height="…">`) pour que la page ne bouge plus pendant le chargement.
- **Si 3 réussit mais pas 1 et 2** : → **Solution S1** : utiliser dans le site la même forme de lien que le sommaire.
- **Si 2 réussit** : → **Solution S2** : liens du site vers l'ancre automatique des titres.
- **Si rien ne réussit, même 4** : la page est trop lourde pour un saut fiable. → **Solution W2** (plus lourde, **décision de hprzeta requise**) : une page wiki par chapitre (`Formation-Zeta-HR-Ch01` … `Ch14`), la page actuelle devenant un sommaire ; chaque « Lire → » ouvre la page du chapitre, donc arrive forcément au début du chapitre.

**STOP** : présenter le tableau `essai | URL | réponse hprzeta (A/B/C)` et la solution proposée. Attendre **« go correction »** (ou « go correction W2 » pour la solution lourde).

## Étape 3 — Correctif (selon la solution)
- **S1 / S2** : modifier les 14 liens de `docs/index.html` ; aperçu local ; `git diff`. **STOP — « go commit site »**, report sur 4 branches, SHA-256 identique, **STOP — « go push »**.
- **W1** : ajouter `width` / `height` réels aux images de `Formation-Zeta-HR.md` (mesurés sur les fichiers image) ; pied de page : date du jour + `wc -l`. `git -C Riemann_Lab.wiki diff`. **STOP — « go commit wiki »**, **STOP — « go push wiki »**.
- **W2** : seulement après « go correction W2 » : découpage sans perte de contenu (vérifier que la somme des lignes des 14 pages + sommaire = contenu d'origine, hors en-têtes), liens internes et formules vérifiés, puis liens du site vers les 14 pages. Commits wiki et site séparés, mêmes STOP.

## Étape 4 — Vérification finale par hprzeta
Après publication, afficher la liste des **14 liens « Lire → »** du site en ligne et demander à hprzeta de les cliquer : réponse A / B / C pour chacun. **Tous doivent être C.** Tableau `chapitre | réponse`. Tests habituels : liens en 200, console vide, 0 `.katex-error`, 390 px sans débordement.

## Étape 5 — Rapport
`RAPPORT_CORRECTION_ANCRES_CHAPITRE_<AAAAMMJJ>_<HHMM>.md` + `.pdf` (tableau de validation, tableau des essais A/B/C, tableau `page | ligne in | ligne out | date heure` avec in en vert et out en rouge). Compléter `HANDOFF_SITE_<AAAAMMJJ>.md`. Copier uniquement les `.md` dans `A_DEPOSER/` (avec le rapport de 15:31 corrigé).

Terminer par : **« hprzeta, donne le .md à claude.ai, projet SITE ZETA : il le range lui-même. »**

---
*PROMPT_CORRECTION_ANCRES_CHAPITRE_20261112_1536.md · projet SITE ZETA · hprzeta · MAJ 12 novembre 2026 15:36 · 67 lignes*
