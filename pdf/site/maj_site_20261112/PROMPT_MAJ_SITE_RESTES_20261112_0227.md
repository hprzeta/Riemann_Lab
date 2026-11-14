# PROMPT Claude Code — Restes ouverts du 12/11 (à lancer le 13/11/2026 ou après)

> Préparé sur claude.ai (projet SITE ZETA) le 12/11/2026 à 02:27, d'après `claude/ETAT_SITE_ZETA_20261112.md` et `RAPPORT_MAJ_WIKI_D10_20261112_0222.md`. Rapport d'analyse : `RAPPORT_ANALYSE_RESTES_20261112_0227.md`.
> hprzeta a vérifié le site sur son téléphone le 12/11 : **OK** (cartes « cours », grille à 5 colonnes).

## Décisions (à confirmer au STOP de l'étape 3)
- **D14** : en-tête du wiki `Etape-1-Calcul-des-zéros-non-triviaux.md` (« Dernière mise à jour : 11 novembre 2026 ») aligné sur le pied (12 novembre 2026).
- **D15** : remplacer le sélecteur CSS fragile `div[style*="repeat(5, 1fr)"]` par une classe dédiée sur la grille (l. ~1437 de `docs/index.html`), sans changer l'affichage.
- **D16** : vérifier les ancres `#…` de tous les liens du site ; ne corriger une ancre morte qu'avec accord.

## Règles
1. Un correctif à la fois. STOP : « go correction » (après le diagnostic), « go commit wiki », « go push wiki », « go commit site », « go push ». Jamais `--force`. Site : commit sur `Riemann_Lab_IA` puis `cherry-pick -x` sur `Riemann_Lab_C`, `main`, `Riemann_Lab_Test` (worktrees temporaires acceptés).
2. Copie `pdf/archive/<fichier>.bak-<AAAAMMJJHHMM>` avant toute modification.
3. Aucune valeur identifiante. Ne pas toucher : turbo, hooks, `monitoring/Monitoring-Runs.md`, minuterie du test automatique.
4. Tout montrer dans Claude in Chrome, onglet **« Mise à jour site »** (le créer s'il n'existe pas) : encadré rouge avant, vert après, captures dans `captures/`. Pour les captures, faire défiler jusqu'à la ligne concernée **avant** de capturer.
5. Pied de page : date du jour + `wc -l` exact pour chaque `.md` modifié ; « mis à jour le <JJ/MM/AAAA> » pour le site.

## Étape 0 — Ranger le prompt et lire le test automatique du jour
```bash
cd /home/riemann/projet_zeta/src/ia/prompts
unzip -l ~/Téléchargements/MAJ_SITE_RESTES_20261112_0227.zip
unzip -n ~/Téléchargements/MAJ_SITE_RESTES_20261112_0227.zip
D=/home/riemann/projet_zeta/pdf/site/maj_site_$(date +%Y%m%d)
ls -l "$D/A_DEPOSER/" 2>/dev/null | grep RAPPORT_TEST_AUTO || echo "pas de test automatique aujourd'hui"
journalctl --user -u zeta-test-maj.service --since today --no-pager | tail -5
```
S'il existe un `RAPPORT_TEST_AUTO_MAJ_SITE_<date>_*.md` du jour : **l'afficher en entier** à hprzeta, sans agir sur ses propositions (claude.ai les analysera). S'il n'existe pas, dire pourquoi d'après le journal (« rien de nouveau », « hors ligne », « déjà testé »…).

## Étape 1 — État AVANT dans Chrome
Suivi console et réseau lancé avant chaque chargement.
- Wiki `Etape-1-Calcul-des-zéros-non-triviaux` : en-tête « Dernière mise à jour » et pied encadrés en rouge. Capture `captures/d14_avant_entete.jpg`.
- Site : la grille à 5 colonnes encadrée en rouge (largeur ordinateur). Capture `captures/d15_avant_grille5.jpg`.

## Étape 2 — Dossier du jour
```bash
mkdir -p "$D/captures" "$D/A_DEPOSER"
cp -p /home/riemann/projet_zeta/src/ia/prompts/RAPPORT_ANALYSE_RESTES_20261112_0227.* "$D/"
cp -p /home/riemann/projet_zeta/src/ia/prompts/PROMPT_MAJ_SITE_RESTES_20261112_0227.md "$D/"
```

## Étape 3 — Diagnostic (lecture seule) — montrer chaque sortie
```bash
cd /home/riemann/projet_zeta
git status --short; git -C Riemann_Lab.wiki status --short
head -8 "Riemann_Lab.wiki/Etape-1-Calcul-des-zéros-non-triviaux.md" | grep -n "mise à jour"
grep -n 'repeat(5, 1fr)' docs/index.html                     # grille et règle CSS
grep -oE 'href="[^"]*#[^"]+"' docs/index.html | sort -u        # liens avec ancre
```
**D16 — ancres** : pour chaque lien avec `#…`, ouvrir la page dans Chrome et vérifier en JavaScript que la cible existe : `document.getElementById(decodeURIComponent(location.hash.slice(1)))` ou, sur GitHub, l'identifiant préfixé `user-content-`. Pour les ancres internes au site (`#section`), vérifier l'`id` dans `docs/index.html`. Donner un tableau `lien | page | cible trouvée (oui/non) | preuve`.

Montrer ensuite les correctifs prévus (D14 : ligne exacte ; D15 : nom de classe proposé, par exemple `grid5`, et la règle CSS ; D16 : liste des ancres mortes et la cible proposée pour chacune).
**STOP et décrire l'écart** si la grille à 5 colonnes n'existe plus ou si plusieurs éléments portent ce style. Sinon, attendre **« go correction »** (hprzeta peut exclure un point, par exemple « go correction sauf D16 »).

## Étape 4 — Correctifs

### 4a. Wiki — D14 (et ancres mortes du wiki si D16 en trouve et que hprzeta les accepte)
En-tête « Dernière mise à jour : 12 novembre 2026 » ; pied : ajouter le segment du jour si autre chose change, `wc -l` exact. `git -C Riemann_Lab.wiki diff`. Audit des lignes ajoutées. **STOP — « go commit wiki ».** **STOP — « go push wiki ».**

### 4b. Site — D15 (et ancres mortes du site si acceptées)
Ajouter la classe à la grille (le style inline reste), puis dans le `@media (max-width: 600px)` remplacer `div[style*="repeat(5, 1fr)"]` par `.<classe>`. Contrôle en aperçu local (« aperçu local, rien n'est publié ») : affichage identique en largeur ordinateur, et à 390 px `scrollWidth` = `clientWidth`. Pied du site à la date du jour. `git diff`. **STOP — « go commit site ».** Message : `site: classe dédiée pour la grille à 5 colonnes (D15)`. Report sur les 3 autres branches, SHA-256 de `docs/index.html` identique sur les 4. **STOP — « go push »**.

## Étape 5 — État APRÈS dans Chrome
- Wiki : en-tête encadré en vert (capture `d14_apres_entete.jpg`).
- Site après publication GitHub Pages : grille encadrée en vert (capture `d15_apres_grille5.jpg`) ; ancres corrigées cliquées une à une.
- Tests : tous les liens en 200, 0 `.katex-error`, 0 formule brute, console vide, 0 requête ≥ 400, `scrollWidth` = `clientWidth` à 390 px.

## Étape 6 — Rapport
`RAPPORT_MAJ_SITE_RESTES_<AAAAMMJJ>_<HHMM>.md` + `.pdf` dans `pdf/site/maj_site_<AAAAMMJJ>/` (tableau de validation, tableau des ancres, tableau `page | ligne in | ligne out | date heure` avec in en vert et out en rouge dans le PDF). Un seul `HANDOFF_SITE_<AAAAMMJJ>.md`. Copier uniquement les `.md` (rapport, handoff, et le rapport du test automatique du jour s'il existe) dans `A_DEPOSER/`.

Terminer par : **« hprzeta, donne le .md à claude.ai, projet SITE ZETA : il le range lui-même. »**

---
*PROMPT_MAJ_SITE_RESTES_20261112_0227.md · projet SITE ZETA · hprzeta · MAJ 12 novembre 2026 02:27 · 73 lignes*
