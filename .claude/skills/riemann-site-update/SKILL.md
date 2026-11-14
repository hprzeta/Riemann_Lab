---
name: riemann-site-update
description: Mise à jour du site https://hprzeta.github.io/Riemann_Lab/ et du wiki du dépôt hprzeta/Riemann_Lab. À utiliser pour préparer, exécuter ou contrôler une mise à jour du site ou du wiki (prompt « Mise à jour site », dossier maj_site_AAAAMMJJ, corrections KaTeX, liens, renommages wiki, test automatique, STOP avant commit et push).
---

# Riemann_Lab — mise à jour du site et du wiki

Objectif : le site et le wiki reflètent toujours l'avancement réel du projet, sans lien cassé, sans formule mal affichée, sans secret publié.

- Vérification en lecture seule (« Test site », « Vérification site ») : skill `riemann-site-check`.
- Ce skill couvre la **modification**. Il reprend les instructions du projet SITE ZETA et les leçons des mises à jour du 12/09 au 14/11/2026 (`pdf/site/maj_site_*` et les 58 fichiers du projet SITE ZETA : états, prompts, rapports d'analyse).

## 1. Partage des rôles

| Acteur | Fait | Ne fait jamais |
|---|---|---|
| claude.ai | Analyse, rapport, prompt pour Claude Code, fichier d'état, décisions numérotées | Modifier le dépôt, le wiki ou le site |
| Claude Code (PC1) | Exécute le prompt, montre tout à l'écran, mesure, produit les rapports | Commit ou push sans le mot de passage de hprzeta |
| hprzeta | Décide, valide, dépose `A_DEPOSER/` dans le projet SITE ZETA | — |

## 2. Carte du dépôt (à respecter)

| Élément | Règle |
|---|---|
| Site | Publié **uniquement** depuis `Riemann_Lab_IA`, dossier `/docs` |
| Branches | Commit sur `Riemann_Lab_IA`, puis `git cherry-pick -x` sur `Riemann_Lab_C`, `main`, `Riemann_Lab_Test` |
| Wiki | Dépôt séparé `Riemann_Lab.wiki`, branche `master` ; commits wiki séparés des commits de code |
| Local seulement | `src/ia/prompts/`, `md/` (exclu de git), `A_DEPOSER/`, fichiers `.bak*` |
| Rapports | `/home/riemann/projet_zeta/pdf/site/maj_site_<AAAAMMJJ>/` (+ `captures/`, `A_DEPOSER/`) |
| Noms de pages wiki | Sans accent. Renommer avec `git mv` + page de renvoi à l'ancien nom (« Page renommée » + lien) ; mettre à jour tous les liens entrants |

## 3. Sources (dans cet ordre)

1. Le fichier d'état `claude/ETAT_SITE_ZETA_*.md` le plus récent du projet SITE ZETA.
2. Le dernier `HANDOFF_SITE_*.md`, puis `ERREURS_NON_CORRIGEES_*`, `DIAG_DECISIONS_*` et les rapports du dernier `maj_site_*`.
3. Le dépôt : changements depuis la dernière mise à jour du site (`git log`, Handoff.md, JOURNAL.md, STACK.md, wiki, `docs/`, `pdf/`). Tous les projets zêta y écrivent : c'est la source commune.
4. `pdf/site/` sur `Riemann_Lab_IA`, pour le format des mises à jour publiées.

Pour toute valeur (nombre de zéros, version, performances, nombre d'animations…), vérifier **toutes** ses occurrences : site, wiki, README, Journal, PDF publiés. Ce qui n'est écrit nulle part s'appelle **« introuvable »** : ne jamais le déduire, le demander à hprzeta.

## 4. Livrables de claude.ai à chaque analyse

- Rapport .md + .pdf :
  - tableau de validation `élément | 🟢/🟡/🔴 | preuve | reste à corriger` ;
  - tableau horodaté `page | ligne in | ligne out | date heure` : **ligne in = texte NOUVEAU**, **ligne out = texte ACTUEL remplacé** (in en vert, out en rouge dans le PDF) ; relire chaque ligne avant de rendre ;
  - chaque ligne du tableau de validation dit **comment** elle a été vérifiée.
- Prompt pour Claude Code dans **un seul zip** `<SUJET>_<AAAAMMJJ>_<HHMM>.zip`, avec le message prêt à coller.
- Mise à jour de `claude/ETAT_SITE_ZETA_<date>.md` : fait, reste ouvert, décisions **D1, D2…** (numérotation continue d'une session à l'autre).
- Les .md sont rangés dans le projet par claude.ai. Aucun PDF ni doublon dans le projet.

## 5. Modèle de prompt « Mise à jour site »

En tête du prompt : constat, idée, périmètre (« 0 commit » si local), liste des mots de passage.

0. Ranger : `unzip -n ~/Téléchargements/<zip>` dans `src/ia/prompts/`, créer `maj_site_$(date +%Y%m%d)/A_DEPOSER`, y copier le prompt.
1. Claude in Chrome, onglet « Mise à jour site » (le créer s'il n'existe pas), **traduction automatique désactivée** sur `github.com` et `hprzeta.github.io` : état **AVANT** (défiler, survoler, encadrer en rouge, capturer dans `captures/`).
2. Diagnostic en lecture seule, chaque sortie montrée. Ne pas deviner la cause : la prouver. Si l'état réel diffère du prompt : **STOP**, décrire l'écart. STOP « go correction ».
3. Correctif :
   - copie `pdf/archive/<fichier>.bak-<AAAAMMJJHHMM>` avant toute modification ; aucune suppression (un script dépassé est archivé par `git mv`, D20) ;
   - **wiki d'abord, site ensuite** ; un lot à la fois, `git diff` montré après chaque lot ;
   - **STOP** « go commit wiki » / « go push wiki », puis « go commit site » / « go push site » ; jamais `--force` ;
   - site : report sur les 4 branches (`cherry-pick -x`), hash de chaque commit noté.
4. État **APRÈS mesuré en ligne** (pas seulement en local) : 0 zone rouge, `.katex-error` = 0, console sans erreur, liens 200, pied de page affiché ; captures `_apres`.
5. Rapport + un seul `HANDOFF_SITE_<AAAAMMJJ>.md` ; copier les .md dans `A_DEPOSER/` et terminer par : « hprzeta, donne le .md à claude.ai, projet SITE ZETA : il le range lui-même. »

Mots de passage utilisés : `go correction`, `go archive`, `go commit wiki`, `go push wiki`, `go commit site`, `go push site` (ou `go commit 1`, `go commit 2`… par lot), `go install`, `go essai`, `go 🟡`, `go correction avec renvoi`. Rien n'avance sans le mot attendu.

Limites et précautions :

- L'outil de navigation de Claude Code **ne défile pas** vers une ancre : utiliser `scrollIntoView()` pour montrer, et poser à hprzeta une **question fermée** (« après le clic, sans défiler, que voyez-vous : A / B / C ? ») avant de conclure.
- Requêtes vers GitHub : 1 par seconde au plus (`sleep 1`), 3 essais si 429 ou 5xx, `User-Agent` explicite. Scripts d'audit écrits pour un prompt : `maj_site_<AAAAMMJJ>/audit/` (non suivi).
- **Aucun chiffre inventé** : une valeur publiée reprend sa source mot pour mot (par exemple `docs/V17.md`, `STACK.md`, `JOURNAL.md`).
- Si le temps manque : priorité aux fichiers publiés touchés par le `git log` (`docs/`, `README.md`, `.md` du wiki), puis rapport **partiel déclaré**.

## 6. Toujours vérifier

| Point | Critère |
|---|---|
| Secrets | Rechercher : IPv4/IPv6, `fe80::`, MAC, `PRIVATE KEY`, `PrivateKey`, `ghp_`, `github_pat`, `api key`, `token=`, `passw`, `duckdns` hors marqueur `<…>`, e-mails autres que l'adresse publique. Sortie **`fichier:ligne | type`, jamais la valeur** |
| Liens | Tous en 200 (`curl -sSL`, 1 req/s, 3 essais si 429/5xx), ancres comprises (préfixe `user-content-` sur GitHub), 0 lien `[[…]]` vers une page absente |
| Liste blanche | Plotly `docs/images/T10Demo/zeta_demovisualisation.html`, liens issues/Kanban du README (D23), DOI `10.1112/plms/s3-3.1.99` (403 aux robots), pages de renvoi du wiki |
| Formules | `.katex-error` = 0, aucune formule brute visible, règles KaTeX du §7 |
| Console | Aucune erreur JS |
| Lignes | Nombre annoncé dans le pied de page = `wc -l` pour chaque .md modifié |
| Dates | Date de mise à jour en bas de chaque page modifiée ; une nouvelle date seulement si `git log --stat` montre un changement de contenu |
| Mobile | Largeur 390 px : pas de débordement (formules longues dans `.eq-scroll`, D11) |
| Cohérence | Une valeur modifiée l'est partout (site, wiki, README, .md, PDF) |
| Maths | Toute valeur numérique publiée est recalculée (mpmath) avant publication |

Un problème de lien, de formule ou d'affichage signalé par hprzeta passe en priorité : prompt de correction d'abord.

## 7. Règles KaTeX du wiki GitHub (mesurées)

1. GitHub retire le `\` devant la ponctuation ASCII même en mode math : jamais `\_ \# \, \; \! \%` dans `$…$` ou `$$…$$`. Remplacer `\text{a\_b}` par `\text{a-b}` et `\#\text{x}` par `n_{\text{x}}`.
2. Pas de `\operatorname`.
3. Pas de `|` dans une formule de tableau : utiliser `\lvert … \rvert`.
4. Formule en ligne collée à un caractère (`/`, `–`, lettre, parenthèse) ou contenant `_{…}` / `^*` (lu comme italique) : écrire `` $`…`$ ``.
5. Un bloc `$$` est seul sur sa ligne et **précédé d'une ligne vide**, sinon il n'est pas rendu.
6. Du code entre backticks (`\#\{…\}`) est affiché tel quel : ne pas le « corriger ».

Le détecteur `verif_formules_wiki.js` n'est pas validé : il donne des faux positifs (barres `|` de `Formules_zeta` rendues correctement). Un signalement n'est un défaut qu'après mesure sur la page publiée.

## 8. Test automatique du site (PC1, local, 0 commit)

- `~/.local/bin/zeta_test_controles.sh` fait les contrôles mécaniques (liens, lignes, secrets, motifs de formules) **avant** l'appel à Claude ; sortie `controles_<AAAAMMJJ>.md`.
- `~/.local/bin/zeta_test_maj_site.sh` (service `zeta-test-maj`) : Claude sans Bash (`Read`, `Grep`, `Glob`, `WebFetch`) ; `ZETA_FORCE=1` et `ZETA_DEPUIS=<ts>` pour les essais seulement.
- Ne pas toucher : turbo, hooks, `monitoring/Monitoring-Runs.md`, service et minuterie.
- Règles décidées (D1 à D6) : minuterie systemd utilisateur, 10 min après l'ouverture de session puis toutes les 3 h ; au plus un test par jour, seulement si un commit a été publié ; lecture seule stricte ; hors ligne, rien n'est marqué et le test réessaie au passage suivant ; **jamais de mise à jour automatique du site** ; fuseau de référence Paris.

## 9. Pièges d'outils connus

| Piège | Contournement |
|---|---|
| `pkill -f` dans une commande Bash tue son propre shell | `fuser -k <port>/tcp` |
| Autorisation JavaScript de Claude in Chrome jamais acceptée | Playwright (environnement `zeta_env`, sans interface) |
| API `pages/builds/latest` en 404 | Vérifier le contenu servi (texte attendu présent) |
| `lualatex` échoue sur un caractère non ASCII dans `\lstinline` | Translittération dans `scripts/build_pdf_riemann_CM.sh` |
| `.md` écrit par heredoc non protégé | Écrire les .md avec Write ou un heredoc `<<'EOF'` (règle de `CLAUDE.md`) |

## 10. Format des rapports de suivi

- **HANDOFF** : sections datées « Fait et publié (sans `--force`) : hashes », « Reste (à décider par hprzeta) », « Prochaine action ».
- **ERREURS_NON_CORRIGEES** : A finalisé · B décisions de hprzeta · C contradictions entre sources · D contenus périmés laissés en l'état · E outils et environnement · F rappel des règles.
- Points clos sans modification : écrire « clos par décision » ou « clos, aucun défaut mesuré », avec la preuve.
- Aucune valeur identifiante dans les rapports : la remplacer par `[IP]`, `[MAC]`, `[CLÉ]`…
- Les décisions de contenu (D7, D10 à D18, D22 à D27…) restent dans `ETAT_SITE_ZETA_*` : elles changent, ce skill ne garde que les règles durables.

## 11. Méthode de travail

- Demander les compléments au lieu de supposer ; signaler ce qui n'est pas vérifié.
- Rapports et messages courts, en français, avec tableaux.
- Suppression d'un fichier : toujours après accord de hprzeta.

## 12. Copies de ce skill

- Copie de référence : `Riemann_Lab/.claude/skills/riemann-site-update/SKILL.md` (versionnée, lue par Claude Code sur PC1).
- Copie dans le compte Claude (claude.ai, Cowork, Chrome).
- Toute modification part de la copie du dépôt, puis la copie du compte est mise à jour.

---
Mis à jour le 2026-11-14 · 141 lignes
