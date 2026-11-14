# PROMPT Claude Code — Audit complet de TOUS les liens du site et du wiki, défilement visible, archivage des anciens scripts, recensement des noms à accents

> Préparé sur claude.ai (projet SITE ZETA) le 12/11/2026 à 18:12. Rapport d'analyse : `RAPPORT_ANALYSE_AUDIT_LIENS_20261112_1812.md`.
> **Demande de hprzeta** : que **tous** les liens pointent au bon endroit, **sans exception** ; voir **défiler dans Claude in Chrome** toutes les pages du site et du wiki ; archiver les anciens scripts ; recenser les noms avec accents ou caractères spéciaux.
> Ce prompt est **long** : il se fait en plusieurs sessions si besoin. À chaque fin de session, écrire où on en est dans le handoff (« REPRENDRE ICI : phase X, page Y »).

## Décisions de hprzeta
- **D19** : audit exhaustif de tous les liens (site, wiki, `.md` publiés, PDF publiés), tableau de statut complet.
- **D20** : les scripts qui produisent une ancienne structure sont **archivés** (déplacés, jamais supprimés).
- **D21** : les noms avec accents ou caractères spéciaux sont **recensés** ici ; **aucun renommage** dans ce prompt (décision séparée, voir phase 5).

## Règles
1. Phases 1 à 3 : **lecture seule**. Aucune modification avant le STOP « go correction ».
2. STOP : « go correction » (liste des corrections), « go archive » (liste des scripts), puis « go commit wiki » / « go push wiki », « go commit site » / « go push », « go commit archive » / « go push ». Jamais `--force`. Site : 4 branches (`cherry-pick -x`).
3. Copie `pdf/archive/<fichier>.bak-<AAAAMMJJHHMM>` avant toute modification.
4. Les scripts d'audit écrits pour ce prompt vont dans `pdf/site/maj_site_<AAAAMMJJ>/audit/` (non suivi, **pas** dans le dépôt).
5. Requêtes vers GitHub : **1 par seconde au plus** (`sleep 1`), 3 essais en cas d'erreur 429 ou 5xx, `User-Agent` normal. Un 429 n'est **pas** un lien cassé : retester plus tard.
6. Aucune valeur identifiante dans les rapports et captures. Ne pas toucher : turbo, hooks, minuterie du test automatique, `monitoring/Monitoring-Runs.md`.
7. Traduction automatique de Chrome **désactivée** sur `github.com` et `hprzeta.github.io` pendant tout l'audit.
8. **Limite connue** : ton outil de navigation ne défile pas tout seul vers une ancre. Pour montrer une ancre, utilise `scrollIntoView()` (démonstration visuelle) ; la preuve qu'un lien « arrive au bon endroit » reste : la cible existe **et** hprzeta confirme sur un échantillon (phase 3).

## Étape 0 — Ranger le prompt
```bash
cd /home/riemann/projet_zeta/src/ia/prompts
unzip -n ~/Téléchargements/AUDIT_LIENS_20261112_1812.zip
D=/home/riemann/projet_zeta/pdf/site/maj_site_$(date +%Y%m%d); mkdir -p "$D/audit" "$D/captures/audit" "$D/A_DEPOSER"
cp -p RAPPORT_ANALYSE_AUDIT_LIENS_20261112_1812.* PROMPT_AUDIT_COMPLET_LIENS_20261112_1812.md "$D/"
```

## Phase 1 — Inventaire de tous les liens (lecture seule)
Sources, **toutes** :
- site : `docs/index.html` et tout autre `docs/**/*.html` ;
- dépôt : `README.md`, `docs/**/*.md`, et tout `.md` lié depuis le site ;
- wiki : tous les `Riemann_Lab.wiki/*.md`, y compris `_Sidebar.md` et `_Footer.md` s'ils existent ;
- PDF publiés et liés depuis le site ou le wiki (liens cliquables extraits avec `pypdf`, annotations `/URI`) ;
- animations (`iframe src`, `script src`, `link href`, images `src`).

Pour chaque lien, relever : `source | ligne | texte du lien | URL | type` (externe, page du site, page wiki, fichier du dépôt, ancre interne, ancre vers une autre page, image, iframe, PDF). Écrire le tout dans `audit/liens.csv`. Montrer le nombre total par source et par type.

## Phase 2 — Test de chaque lien, sans exception (lecture seule)
Pour chaque URL distincte :
1. **Code HTTP final** (`curl -sSL -o /dev/null -w '%{http_code} %{url_effective}'`, `HEAD` puis `GET` si `HEAD` échoue). Noter les **redirections** (URL finale différente).
2. **Page wiki inexistante** : une page wiki absente peut renvoyer vers l'accueil du wiki ou une page de création. Comparer l'URL finale et le titre de la page avec ceux attendus.
3. **Ancre** : télécharger la page cible et vérifier qu'un élément porte l'`id` ou le `name` (sur GitHub, avec le préfixe `user-content-`). Une ancre vers un titre à accents : noter sa forme encodée (`%C3%A9`).
4. **Ancien format** : tout lien vers `Formation-Zeta-HR#ch…` ou `#user-content-ch…` → statut 🟡 « à remplacer par `Formation-Zeta-HR-ChNN` ».
5. **Liens locaux** (fichiers du dépôt) : le fichier existe-t-il sur `main` et sur `Riemann_Lab_IA` ?

Statut : 🟢 200 et cible correcte · 🟡 marche mais à améliorer (redirection, ancien format, `http://`, ancre à accents) · 🔴 cassé (4xx/5xx, page wiki inexistante, ancre absente, fichier absent).
Résultat dans `audit/liens_statut.csv`, et **tableau complet** dans le rapport (voir étape 6).

## Phase 3 — Défilement visible dans Claude in Chrome
Onglet **« Audit liens »**. Lancer un enregistrement GIF si l'outil le permet (`audit_site.gif`, `audit_wiki.gif`).
1. **Site** : ouvrir `https://hprzeta.github.io/Riemann_Lab/`, faire défiler **toute** la page de haut en bas, lentement (par écrans), en **survolant chaque lien** ; encadrer en rouge chaque lien 🔴 et en orange chaque 🟡 de la phase 2. Une capture par écran (`captures/audit/site_NN.jpg`). Relever la console et les requêtes ≥ 400.
2. **Wiki** : pour **chaque page** du wiki (barre latérale « Pages », environ 84), l'ouvrir, la faire défiler du haut en bas, encadrer les liens 🔴/🟡, relever les `.katex-error` et formules brutes. Une capture par page au minimum (`captures/audit/wiki_<page>.jpg`).
3. **Ancres** : pour chaque lien avec ancre, ouvrir l'URL puis `document.getElementById(...)?.scrollIntoView()` pour **montrer** la cible encadrée en vert.
4. **Échantillon pour hprzeta** : choisir **10 liens à ancre** (dont 3 « Lire → ») et lui demander de les cliquer dans son propre Chrome. Réponse A / B / C (A = haut de page, B = ailleurs, C = au bon endroit). Seul C compte.

## Phase 4 — Scripts anciens à archiver (lecture seule, puis STOP)
```bash
cd /home/riemann/projet_zeta
grep -rlE 'Formation-Zeta-HR|\.wiki/|docs/index\.html|make_wiki' --include='*.py' --include='*.sh' . | grep -v '^./pdf/archive'
```
Pour chaque script trouvé (dont `cours/make_wiki_page.py`) : ce qu'il écrit, s'il produit une structure **dépassée** (page unique du cours, anciens liens `#chN`, anciennes valeurs), s'il est appelé ailleurs (`grep -rn <nom>` dans scripts, hooks, minuteries, `crontab -l`, `systemctl --user list-timers`). Tableau `script | écrit quoi | encore appelé ? | dépassé ? | proposition (archiver / garder / adapter)`.
**STOP — « go archive »** : `git mv` des scripts retenus vers `archive/scripts_obsoletes_<AAAAMMJJ>/`, avec un `LISEZMOI.md` (pourquoi, date, remplacé par quoi). Aucun appel restant vers eux (sinon le signaler, ne pas modifier les hooks). **STOP — « go commit archive »**, report sur les 4 branches, **STOP — « go push »**.

## Phase 5 — Recensement des noms à risque (lecture seule, aucun renommage)
Lister tous les **noms de pages wiki, fichiers publiés et ancres** qui contiennent : lettres accentuées (é, è, à, ç…), caractères grecs (ζ…), tiret long `—` ou demi-tiret `–`, apostrophe, espace, `&`, parenthèses, doubles tirets `--`, ou tiret en début/fin.
Pour chacun : `nom actuel | caractères à risque | forme encodée dans l'URL | nombre de liens entrants (phase 1) | nom ASCII proposé`.
Règle de proposition : minuscules ou casse actuelle conservée, **sans accent** (é→e, ç→c), espaces et tirets longs → `-`, pas de `--`, pas de caractère spécial. Exemple : `Etape-1-Calcul-des-zéros-non-triviaux` → `Etape-1-Calcul-des-zeros-non-triviaux`.
**Ne rien renommer.** Le renommage fera l'objet d'un prompt séparé, après décision de hprzeta (le wiki GitHub n'a pas de redirection automatique).

## Phase 6 — Corrections (après « go correction »)
Présenter la liste des liens 🔴 et 🟡 avec la correction proposée pour chacun ; hprzeta peut en exclure (« go correction sauf … »).
- **Wiki** : corrections ; pied de page (date du jour + `wc -l`) de chaque page modifiée. `git -C Riemann_Lab.wiki diff`, audit des lignes ajoutées. **STOP — « go commit wiki »**, **STOP — « go push wiki »**.
- **Site et `.md` du dépôt** : corrections ; pied du site à la date du jour. `git diff`. **STOP — « go commit site »**, report 4 branches, SHA-256 identique, **STOP — « go push »**.
- Puis **re-tester** tous les liens corrigés (phase 2) et redemander un échantillon à hprzeta.

## Étape 6 — Rapport
`RAPPORT_AUDIT_COMPLET_LIENS_<AAAAMMJJ>_<HHMM>.md` + `.pdf` dans `pdf/site/maj_site_<AAAAMMJJ>/` :
1. Synthèse : nombre de liens par source et par statut (🟢/🟡/🔴), avant et après corrections.
2. **Tableau complet** : `source | ligne | texte | URL | type | HTTP | ancre | statut | action`. Si plus de 300 lignes, le tableau complet est dans `audit/liens_statut.csv`, et le rapport contient tous les 🔴 et 🟡 + le résumé des 🟢.
3. Échantillon A/B/C de hprzeta.
4. Scripts archivés (tableau de la phase 4).
5. Noms à risque (tableau de la phase 5).
6. Tableau `page | ligne in | ligne out | date heure` (in en vert, out en rouge dans le PDF).
7. Tests habituels : console, `.katex-error`, formules brutes, 390 px, secrets.
Compléter `HANDOFF_SITE_<AAAAMMJJ>.md`. Copier uniquement les `.md` dans `A_DEPOSER/` (pas les CSV ni les captures).

Terminer par : **« hprzeta, donne le .md à claude.ai, projet SITE ZETA : il le range lui-même. »**

---
*PROMPT_AUDIT_COMPLET_LIENS_20261112_1812.md · projet SITE ZETA · hprzeta · MAJ 12 novembre 2026 18:12 · 92 lignes*
