# PROMPT Claude Code — Correction : les liens « Lire → » n'arrivent plus au bon chapitre (D17)

> Préparé sur claude.ai (projet SITE ZETA) le 12/11/2026 à 13:59. Rapport d'analyse : `RAPPORT_ANALYSE_ANCRES_FORMATION_20261112_1359.md`.
> **Problème signalé par hprzeta** : sur le site, un lien « Lire → » ouvre `…/wiki/Formation-Zeta-HR#ch11`, mais la page reste en haut (titre, sommaire) au lieu d'aller au chapitre 11. **Avant, il arrivait au bon chapitre.**
> Le rapport D16 de 13:49 disait « 31 ancres trouvées, 0 morte » : la cible existe, mais le **défilement** ne se fait pas. C'est ce qu'il faut corriger.

## Règles
1. **Diagnostic d'abord, sans rien modifier.** Ne pas deviner la cause : la prouver.
2. STOP : « go correction » (après le diagnostic), puis selon la solution « go commit wiki » / « go push wiki » et/ou « go commit site » / « go push ». Jamais `--force`. Site : commit sur `Riemann_Lab_IA` puis `cherry-pick -x` sur les 3 autres branches.
3. Copie `pdf/archive/<fichier>.bak-<AAAAMMJJHHMM>` avant toute modification.
4. Aucune valeur identifiante. Ne pas toucher : turbo, hooks, minuterie, `monitoring/Monitoring-Runs.md`.
5. Claude in Chrome, onglet **« Mise à jour site »** (le créer s'il n'existe pas). **Traduction automatique de Chrome désactivée** pour github.com pendant tous les tests (elle modifie la page).
6. **Limite connue (session de 13:49)** : l'outil de navigation de Claude Code **ne défile pas**, même vers une ancre à `id` classique. Donc `scrollY` mesuré dans l'outil ne prouve rien. Faire d'abord un **test témoin** (une ancre de titre GitHub connue, par exemple un titre de `README.md`) : si le témoin ne défile pas non plus, **ne pas conclure seul** ; le test « arrive au chapitre ? » est fait par **hprzeta**, qui clique chaque URL dans son propre Chrome et répond oui/non. Claude Code peut en revanche prouver la présence et la forme des cibles (`id`, `name`, `user-content-…`).

## Étape 0 — Ranger le prompt
```bash
cd /home/riemann/projet_zeta/src/ia/prompts
unzip -l ~/Téléchargements/MAJ_ANCRES_FORMATION_20261112_1359.zip
unzip -n ~/Téléchargements/MAJ_ANCRES_FORMATION_20261112_1359.zip
D=/home/riemann/projet_zeta/pdf/site/maj_site_$(date +%Y%m%d); mkdir -p "$D/captures" "$D/A_DEPOSER"
cp -p RAPPORT_ANALYSE_ANCRES_FORMATION_20261112_1359.* PROMPT_CORRECTION_ANCRES_FORMATION_20261112_1359.md "$D/"
```

## Étape 1 — Reproduire le problème (état AVANT)
Dans Chrome, sur le site, cliquer un vrai lien « Lire → » (chapitre 11, puis un autre, par exemple le 3). Après **3 secondes**, relever en JavaScript :
```js
[location.hash, window.scrollY,
 !!document.getElementById('user-content-ch11'),
 !!document.querySelector('[name="ch11"],[name="user-content-ch11"]'),
 (document.getElementById('user-content-ch11')||{}).getBoundingClientRect?.().top]
```
Capture `captures/d17_avant_lire_ch11.jpg` (haut de page encadré en rouge). Faire la même chose en **ouvrant l'URL directement** dans un nouvel onglet, puis après un **rechargement (F5)** : noter si le comportement diffère.

## Étape 2 — Trouver la cause (lecture seule) — montrer chaque sortie
```bash
cd /home/riemann/projet_zeta
grep -n 'Formation-Zeta-HR#' docs/index.html | head -20                 # liens actuels
git log --format='%h %ad %s' --date=short -S 'Formation-Zeta-HR#' -- docs/index.html | head
for f in pdf/archive/index.html.bak-*; do echo "$f: $(grep -c 'Formation-Zeta-HR#' "$f")"; grep -o 'Formation-Zeta-HR[^"]*' "$f" | sort -u | head -3; done
W=Riemann_Lab.wiki; git -C $W log --format='%h %ad %s' --date=short -5 -- Formation-Zeta-HR.md
grep -n 'name="ch11"\|id="ch11"\|ch11' $W/Formation-Zeta-HR.md | head
grep -n '^## .*Chapitre 11\|^### .*Chapitre 11' $W/Formation-Zeta-HR.md
sed -n '/Sommaire/,+16p' $W/Formation-Zeta-HR.md                         # format des liens du sommaire
```
Puis, dans Chrome (onglet « Mise à jour site »), tester **trois** formes de lien vers le chapitre 11 et noter pour chacune si la page arrive au chapitre (oui/non, `scrollY`, capture) :
1. le lien actuel `…/Formation-Zeta-HR#ch11` ;
2. le lien du **sommaire de la page wiki** (cliquer « Chapitre 11 » dans le sommaire, relever l'URL obtenue) ;
3. l'ancre automatique du titre du chapitre 11 (survoler le titre, copier son lien `#…`).

Donner un tableau : `forme de lien | URL | arrive au chapitre ? | preuve`. Si le test témoin (règle 6) ne défile pas, laisser la colonne « arrive ? » vide, afficher les 3 URL cliquables et **demander à hprzeta** de les essayer et de répondre (par exemple « 1 non, 2 oui, 3 oui »).

Questions à trancher avec les preuves :
- Les liens du site ont-ils changé aujourd'hui (comparaison avec les `.bak`) ? Si oui, c'est une régression de nos commits : le dire clairement.
- La page wiki a-t-elle changé (dernier commit) ?
- Le problème vient-il du chargement (la page s'allonge après le saut, par exemple formules ou images) ? Indice : `scrollY` > 0 au début puis remonté, ou cible loin de l'écran.

**STOP** : présenter la cause prouvée et la solution retenue parmi :
- **(a)** si le sommaire ou l'ancre de titre marche : remplacer dans `docs/index.html` les liens `#chN` par cette forme qui marche (site seulement, 14 liens environ) ;
- **(b)** si aucune forme ne marche à cause de GitHub : garder les liens, et l'écrire dans le rapport (rien à corriger chez nous) ;
- **(c)** si nos commits ont cassé les liens : restaurer exactement les liens d'avant depuis le `.bak`.

Attendre **« go correction »**.

## Étape 3 — Correctif (selon la solution choisie)
Modifier uniquement les liens concernés. Aperçu local (« aperçu local, rien n'est publié »), puis cliquer les liens modifiés depuis l'aperçu : chaque lien arrive au bon chapitre (`scrollY` > 0, titre du chapitre visible). Pied du site à la date du jour. `git diff`. **STOP — « go commit site ».** Message : `site: liens « Lire → » vers les chapitres de Formation-Zeta-HR (D17)`. Report sur les 3 branches, SHA-256 de `docs/index.html` identique sur les 4. **STOP — « go push »**.
Si une modification du wiki est nécessaire : commit séparé, **STOP — « go commit wiki »**, **STOP — « go push wiki »**.

## Étape 4 — État APRÈS
Après publication GitHub Pages, faire vérifier **tous** les liens « Lire → » : par Claude Code si son outil défile, sinon par hprzeta (liste des URL fournie, réponse oui/non par chapitre). Tableau `chapitre | arrive ? | vérifié par`. Capture `captures/d17_apres_lire_ch11.jpg` (titre du chapitre 11 encadré en vert). Tests : tous les liens en 200, console vide, 0 `.katex-error`, 390 px sans débordement.

## Étape 5 — Rapport
`RAPPORT_CORRECTION_ANCRES_FORMATION_<AAAAMMJJ>_<HHMM>.md` + `.pdf` dans `pdf/site/maj_site_<AAAAMMJJ>/` : tableau de validation, tableau des formes de lien testées, tableau `page | ligne in | ligne out | date heure` (in en vert, out en rouge dans le PDF). Compléter `HANDOFF_SITE_<AAAAMMJJ>.md`. Copier uniquement les `.md` dans `A_DEPOSER/`, **avec** `RAPPORT_MAJ_SITE_RESTES_20261112_1349.md` et le rapport du test automatique du jour s'il existe.

Terminer par : **« hprzeta, donne le .md à claude.ai, projet SITE ZETA : il le range lui-même. »**

---
*PROMPT_CORRECTION_ANCRES_FORMATION_20261112_1359.md · projet SITE ZETA · hprzeta · MAJ 12 novembre 2026 13:59 · 77 lignes*
