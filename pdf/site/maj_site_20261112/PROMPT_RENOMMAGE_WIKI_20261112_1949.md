# PROMPT Claude Code — Renommer les 5 pages wiki à accents (D26) et retirer les symboles des titres de `Animations` (D27)

> Préparé sur claude.ai (projet SITE ZETA) le 12/11/2026 à 19:49. Rapport d'analyse : `RAPPORT_ANALYSE_RENOMMAGE_WIKI_20261112_1949.md`.
> **À lancer APRÈS** `PROMPT_WIKI_STACK_TITCHMARSH_20261112_1945.md` (les deux touchent le wiki).
> Source des noms : `RAPPORT_AUDIT_COMPLET_20261112_1921.md` §5 et `audit/noms_a_risque.csv` (dossier `pdf/site/maj_site_20261112/`).

## Décisions de hprzeta (remplacent D24 et le « pas de renommage » de D25)
- **D26** : renommer les 5 pages wiki dont le nom contient un accent :

| Nom actuel | Nouveau nom | Liens entrants (audit) |
|---|---|---|
| `Etape-1-Calcul-des-zéros-non-triviaux` | `Etape-1-Calcul-des-zeros-non-triviaux` | 19 |
| `Interprétation-des-résultats-de-tests` | `Interpretation-des-resultats-de-tests` | 2 |
| `Partie-1-La-Théorie-Étape_1` | `Partie-1-La-Theorie-Etape_1` | 1 |
| `Projet-Zêta` | `Projet-Zeta` | 1 |
| `Tableau-Symboles-Mathématiques` | `Tableau-Symboles-Mathematiques` | 2 |

- **D27** : dans `Animations.md`, retirer le symbole ou l'emoji placé **au début des titres** (`Γ`, `ℂ`, `🎬`, emoji avec caractère invisible…). Le symbole peut rester dans le tableau « Vue d'ensemble ». Les accents du texte des titres restent.

## Règles
1. Diagnostic en lecture seule d'abord. STOP : « go correction » (avec le choix du renvoi, voir étape 2), « go commit wiki », « go push wiki », « go commit site », « go push ». Jamais `--force`. Site : 4 branches (`cherry-pick -x`).
2. Copie `pdf/archive/<fichier>.bak-<AAAAMMJJHHMM>` de chaque fichier avant modification (wiki et site).
3. Renommer avec `git mv` dans le dépôt du wiki (l'historique de la page est gardé). **Aucune suppression** de contenu.
4. Aucune valeur identifiante. Ne pas toucher : turbo, hooks, minuterie, `monitoring/Monitoring-Runs.md`, code Plotly.
5. Claude in Chrome, onglet « Mise à jour site », traduction automatique désactivée.

## Étape 0 — Ranger le prompt
```bash
cd /home/riemann/projet_zeta/src/ia/prompts
unzip -n ~/Téléchargements/RENOMMAGE_WIKI_20261112_1949.zip
D=/home/riemann/projet_zeta/pdf/site/maj_site_$(date +%Y%m%d); mkdir -p "$D/captures" "$D/A_DEPOSER"
cp -p RAPPORT_ANALYSE_RENOMMAGE_WIKI_20261112_1949.* PROMPT_RENOMMAGE_WIKI_20261112_1949.md "$D/"
```

## Étape 1 — Diagnostic (lecture seule) — montrer chaque sortie
```bash
R=/home/riemann/projet_zeta; W=$R/Riemann_Lab.wiki
git -C $W status --short; git -C $W pull --ff-only; git -C $R status --short
ls $W | grep -P '[^\x00-\x7F]'                       # pages wiki au nom non ASCII
```
Pour chacune des 5 pages, chercher **tous** les liens entrants, sous toutes leurs formes (accent écrit, forme encodée `%C3%A9`, lien `[[…]]`, lien Markdown, lien HTML), dans : tous les `.md` du wiki (y compris `_Sidebar.md`, `_Footer.md`), `docs/**/*.html`, `docs/**/*.md`, `README.md`, et les scripts (`*.py`, `*.sh`) qui citent un nom de page. Comparer avec les chiffres de l'audit.
Pour `Animations.md` : lister chaque titre qui commence par un caractère non ASCII, son ancre actuelle, sa nouvelle ancre, et **tous** les liens qui pointent vers ces ancres (dans le wiki et sur le site).
Lister aussi les **PDF publiés** qui contiennent un lien vers une des 5 pages (on ne les modifie pas : la page de renvoi les couvrira).
Tableau : `cible | forme du lien | fichier | ligne | nouveau lien`.

## Étape 2 — STOP : présenter le plan et demander le choix du renvoi
Expliquer à hprzeta : **le wiki GitHub ne redirige pas**. Si l'ancien nom disparaît, les liens extérieurs (favoris, moteurs de recherche, PDF déjà publiés, autres sites) tombent sur une page vide.
- **« go correction avec renvoi »** (recommandé) : à chaque ancien nom, une page courte : « Cette page a été renommée : [[Nouveau-nom]] » + date. Les liens du projet pointent tous vers le nouveau nom.
- **« go correction sans renvoi »** : l'ancien nom disparaît complètement.

## Étape 3 — Correctifs

### 3a. Wiki
1. `git mv` des 5 pages vers leur nouveau nom.
2. Selon le choix : page de renvoi à chaque ancien nom (ou rien).
3. Remplacer **tous** les liens du wiki vers les anciens noms par les nouveaux noms.
4. `Animations.md` : retirer le symbole de début des titres ; mettre à jour tous les liens vers ces ancres (dans `Animations.md` et les autres pages).
5. Pied de page de chaque page modifiée ou renommée : date du jour + `wc -l` exact.
`git -C $W diff --stat` puis `git -C $W diff` ; audit des lignes ajoutées. **STOP — « go commit wiki ».** Message : `wiki: pages renommées sans accents (D26), titres d'Animations sans symbole (D27)`. **STOP — « go push wiki »**.

### 3b. Site et dépôt (seulement s'il y a des liens à changer)
Mettre à jour les liens de `docs/**/*.html`, `docs/**/*.md`, `README.md`. Pied du site à la date du jour. `git diff`. **STOP — « go commit site »**, report sur les 4 branches, SHA-256 identiques. **STOP — « go push »**.
Scripts qui citent un ancien nom : les **signaler** dans le rapport, ne pas les modifier sans accord.

## Étape 4 — Vérification
1. Re-tester **tous** les liens avec les scripts de l'audit du 12/11 (`pdf/site/maj_site_20261112/audit/`) : site, wiki, `.md`, README. Objectif : aucun nouveau 🔴, aucun lien restant vers un ancien nom (hors pages de renvoi).
2. Wiki : 0 lien `a.absent` (lien vers une page inexistante) sur toutes les pages.
3. Chrome : ouvrir les 5 nouvelles pages et les 5 anciennes adresses (renvoi visible, ou page vide si « sans renvoi ») ; défiler `Animations` avec les titres encadrés en vert ; captures `captures/d26_*.jpg`, `captures/d27_*.jpg`.
4. **Échantillon pour hprzeta** : 5 liens vers les pages renommées (dont 2 depuis le site) + 3 liens d'ancre de `Animations`. Réponse A / B / C ; seul C compte.
5. Tests habituels : 0 `.katex-error`, 0 formule brute, console vide, secrets.

## Étape 5 — Rapport
`RAPPORT_RENOMMAGE_WIKI_<AAAAMMJJ>_<HHMM>.md` + `.pdf` : tableau de validation, tableau des renommages, tableau des liens mis à jour, échantillon A/B/C, tableau `page | ligne in | ligne out | date heure` (in en vert, out en rouge dans le PDF). Compléter `HANDOFF_SITE_<AAAAMMJJ>.md`. Copier uniquement les `.md` dans `A_DEPOSER/`.

Terminer par : **« hprzeta, donne le .md à claude.ai, projet SITE ZETA : il le range lui-même. »**

---
*PROMPT_RENOMMAGE_WIKI_20261112_1949.md · projet SITE ZETA · hprzeta · MAJ 12 novembre 2026 19:49 · 78 lignes*
