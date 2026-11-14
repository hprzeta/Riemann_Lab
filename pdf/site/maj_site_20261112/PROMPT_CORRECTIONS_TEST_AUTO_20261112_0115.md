# PROMPT Claude Code — Corrections issues du 1er test automatique (12/11/2026)

> Préparé sur claude.ai (projet SITE ZETA) le 12/11/2026 à 01:15, d'après `RAPPORT_TEST_AUTO_MAJ_SITE_20261112_0101.md` et les décisions de hprzeta. Rapport d'analyse : `RAPPORT_ANALYSE_CORRECTIONS_TEST_AUTO_20261112_0115.md`.

## Décisions de hprzeta
- **D7 = (c)** : le bandeau du site affiche les deux totaux (T=5·10⁶ et T=100 000).
- **D8** : turbo de PC1 laissé tel quel (ne pas y toucher).
- **D9** : ancien fichier d'état gardé (rien à faire ici).

## Règles
1. Un correctif à la fois. **STOP avant chaque commit** (« go commit 1 », « go commit 2 », « go commit 3 »), **STOP avant push** (« go push »). Jamais `--force`. Commits sur `Riemann_Lab_IA`, puis `cherry-pick -x` sur `Riemann_Lab_C`, `main`, `Riemann_Lab_Test`.
2. Copie `.bak-20261112` dans `pdf/archive/` avant de modifier un fichier.
3. Aucune valeur identifiante dans les messages, captures et rapports (`[IP]`, `[MAC]`, `[EMAIL]`).
4. Tout montrer dans Claude in Chrome, onglet **« Mise à jour site »** : défiler, survoler, encadrer (rouge avant, vert après), capturer.
5. Ne pas toucher : `monitoring/Monitoring-Runs.md`, le wiki, les hooks, le turbo (D8).
6. Pied de page : date de mise à jour + `wc -l` exact pour chaque `.md` modifié.

## Étape 0 — Ranger le prompt
```bash
cd /home/riemann/projet_zeta/src/ia/prompts
unzip -l ~/Téléchargements/MAJ_CORR_TEST_AUTO_20261112_0115.zip
cp -p PROMPT_TEST_AUTO_MAJ_SITE.md /home/riemann/projet_zeta/pdf/archive/PROMPT_TEST_AUTO_MAJ_SITE.md.bak-20261112
unzip -o ~/Téléchargements/MAJ_CORR_TEST_AUTO_20261112_0115.zip
```
`PROMPT_TEST_AUTO_MAJ_SITE.md` est remplacé par sa version améliorée (règles 6 à 8).

## Étape 1 — État AVANT dans Chrome (onglet « Mise à jour site »)
- Site `https://hprzeta.github.io/Riemann_Lab/` : encadrer en rouge le bandeau du haut (« 138 069 zéros validés… ») et le pied de page. Capture `captures/corr_avant_bandeau.jpg`.
- `https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/docs/V17.md` : dernière ligne. Capture `captures/corr_avant_V17_pied.jpg`.
- `https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/README.md` : dernière ligne. Capture `captures/corr_avant_README_pied.jpg`.

## Étape 2 — Dossier du jour
```bash
D=/home/riemann/projet_zeta/pdf/site/maj_site_$(date +%Y%m%d); mkdir -p "$D/captures" "$D/A_DEPOSER"
cp -p /home/riemann/projet_zeta/src/ia/prompts/RAPPORT_ANALYSE_CORRECTIONS_TEST_AUTO_20261112_0115.* "$D/"
cp -p /home/riemann/projet_zeta/src/ia/prompts/PROMPT_CORRECTIONS_TEST_AUTO_20261112_0115.md "$D/"
```

## Étape 3 — Diagnostic (lecture seule) — montrer chaque sortie
```bash
cd /home/riemann/projet_zeta
git branch --show-current                                  # Riemann_Lab_IA
git status --short                                         # noter l'état d'avant
sed -n '625,640p' docs/index.html                          # contexte du bandeau
grep -rn "138 069 zéros validés" docs/ README.md Riemann_Lab.wiki/*.md   # autres occurrences
grep -n "mis à jour le" docs/index.html                    # pied du site
git log --format='%h %ad %s' --date=short -- docs/V17.md   # historique de V17.md
git show 672656b 173327d --stat -- docs/V17.md             # ont-ils changé le CONTENU ?
git diff 672656b~1 173327d -- docs/V17.md | head -60
tail -3 docs/V17.md; wc -l docs/V17.md
tail -3 README.md; wc -l README.md
git log -1 --format='%h %ad' --date=short -- README.md
```
**STOP et décrire l'écart** si : la ligne du bandeau n'est pas celle attendue ; « 138 069 zéros validés » apparaît ailleurs (wiki compris : ne rien modifier, le signaler) ; les commits du 07/11 n'ont **pas** changé le contenu de `V17.md` (dans ce cas, la correction 2 est abandonnée). Sinon, attendre **« go correction »**.

## Étape 4 — Correctifs (après « go correction »)

### Correction 1 — bandeau `docs/index.html` (D7 c)
Remplacer, sur la ligne du bandeau seulement :
- out : `138 069 zéros validés · V17 en production (03/11/2026) · 0 manquant ✅ · Obj2 atteint 04/07/2026`
- in : `10 016 474 zéros calculés (T=5·10⁶) · 138 069 zéros à T=100 000 · V17 en production (03/11/2026) · 0 manquant ✅ · Obj2 atteint 04/07/2026`

Garder le balisage HTML existant (n'agir que sur le texte). Pied du site : « mis à jour le 11/11/2026 » → « mis à jour le 12/11/2026 ». Aperçu local (serveur local ou `file://`, « aperçu local, rien n'est publié ») : bandeau sur une ligne en largeur ordinateur et téléphone (390 px), sans débordement. `git diff`. **STOP — « go commit 1 ».**
Message : `site: bandeau avec les deux totaux (T=5e6 et T=100 000)`.

### Correction 2 — pied de `docs/V17.md` (seulement si l'étape 3 l'a confirmé)
- out : `*Mis à jour : 2026-11-05 — 66 lignes*`
- in : `*Mis à jour : 2026-11-05 · 2026-11-07 (<objet du commit du 07/11>) · 2026-11-12 (date du pied corrigée) — <wc -l> lignes*`

`git diff`. **STOP — « go commit 2 ».** Message : `docs(V17): date du pied de page alignée sur les commits du 07/11`.

### Correction 3 — pied de `README.md`
Ajouter à la fin, après une ligne vide puis `---` :
`*README.md · hprzeta · MAJ 11 novembre 2026 · 12 novembre 2026 (pied de page ajouté) · <wc -l> lignes*`
(`<wc -l>` mesuré **après** l'ajout.) `git diff`. **STOP — « go commit 3 ».** Message : `readme: pied de page avec date et nombre de lignes`.

### Report et push
```bash
for b in Riemann_Lab_C main Riemann_Lab_Test; do git checkout "$b" && git cherry-pick -x <h1> <h2> <h3>; done
git checkout Riemann_Lab_IA
for f in docs/index.html docs/V17.md README.md; do for b in Riemann_Lab_IA Riemann_Lab_C main Riemann_Lab_Test; do echo "$b $f $(git show $b:$f | sha256sum | cut -c1-12)"; done; done
```
Les 4 sha256 de chaque fichier doivent être identiques. Audit des lignes ajoutées (IP, MAC, clé, jeton, e-mail, duckdns, fe80::). **STOP — « go push ».** Puis `git push origin Riemann_Lab_IA Riemann_Lab_C main Riemann_Lab_Test` (sans `--force`) ; local = origin pour les 4.

## Étape 5 — État APRÈS dans Chrome
- Suivi console et réseau lancé **avant** le chargement. Attendre la publication GitHub Pages, recharger le site : bandeau encadré en vert, pied « 12/11/2026 ». Captures `captures/corr_apres_bandeau.jpg`, `captures/corr_apres_pied_site.jpg`.
- `V17.md` et `README.md` sur `main` : dernière ligne encadrée en vert (captures).
- Tests : tous les liens de `docs/index.html` en 200 (`curl -sIL`), 0 `.katex-error`, 0 formule brute, console sans erreur, 0 requête ≥ 400.
- Test automatique : `bash -n ~/.local/bin/zeta_test_maj_site.sh` et `systemctl --user list-timers | grep zeta` (la minuterie tourne toujours ; le nouveau prompt sera utilisé au prochain passage).

## Étape 6 — Rapport
`RAPPORT_MAJ_CORRECTIONS_TEST_AUTO_<AAAAMMJJ>_<HHMM>.md` + `.pdf` dans `pdf/site/maj_site_<AAAAMMJJ>/` : tableau de validation (🟢/🟡/🔴, preuve, reste à corriger) et tableau `page | ligne in | ligne out | date heure` (in en vert, out en rouge dans le PDF). Un seul `HANDOFF_SITE_<AAAAMMJJ>.md` (compléter celui du jour). Copier uniquement les `.md` dans `A_DEPOSER/`.

Terminer par : **« hprzeta, donne le .md à claude.ai, projet SITE ZETA : il le range lui-même. »**

---
*PROMPT_CORRECTIONS_TEST_AUTO_20261112_0115.md · projet SITE ZETA · hprzeta · MAJ 12 novembre 2026 01:15 · 97 lignes*
