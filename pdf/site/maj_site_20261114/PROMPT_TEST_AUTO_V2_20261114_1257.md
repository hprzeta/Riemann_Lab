# PROMPT Claude Code — Test automatique V2 : contrôles faits par le script, plus de rapport partiel (D28)

> Préparé sur claude.ai (projet SITE ZETA) le 14/11/2026 à 12:57. Rapport d'analyse : `RAPPORT_ANALYSE_TEST_AUTO_V2_20261114_1257.md`.
> **Constat** : le 1er vrai test automatique (13/11 12:40) s'est lancé tout seul, mais son rapport est **partiel** : « Bash a été refusé », donc pas de `curl`, pas de `wc -l`, pas de scan complet des secrets.
> **Idée** : les contrôles mécaniques (liens, nombre de lignes, secrets) sont faits **par le script lui-même, avant** l'appel à Claude, et leurs résultats lui sont donnés. Claude n'a plus besoin de Bash : il analyse.
> **Tout est local** (`~/.local/bin`, `~/.local/share/zeta_test_maj`, `src/ia/prompts`) : **0 commit, 0 push**.

## Règles
1. STOP : « go install » (après le diagnostic), « go essai » (avant l'essai forcé). Rien d'autre à valider : aucun commit.
2. Copie `<fichier>.bak-<AAAAMMJJHHMM>` avant de modifier le script ou le prompt du test.
3. Les nouveaux scripts sont **en lecture seule** : ils ne modifient ni le dépôt, ni le wiki, ni le site ; ils écrivent seulement dans `~/.local/state/zeta_test_maj/` et `pdf/site/maj_site_<date>/`.
4. **Aucune valeur identifiante** dans les sorties : pour un secret trouvé, seulement `fichier:ligne` et le type (IP, MAC, clé…), jamais la valeur.
5. Ne pas toucher : turbo, hooks, `monitoring/Monitoring-Runs.md`, le service et la minuterie (seul le script appelé change).

## Étape 0 — Ranger le prompt
```bash
cd /home/riemann/projet_zeta/src/ia/prompts
unzip -n ~/Téléchargements/TEST_AUTO_V2_20261114_1257.zip
D=/home/riemann/projet_zeta/pdf/site/maj_site_$(date +%Y%m%d); mkdir -p "$D/A_DEPOSER"
cp -p RAPPORT_ANALYSE_TEST_AUTO_V2_20261114_1257.* PROMPT_TEST_AUTO_V2_20261114_1257.md "$D/"
```

## Étape 1 — Diagnostic (lecture seule) — montrer chaque sortie
```bash
S=~/.local/state/zeta_test_maj
ls -l $S; cat $S/dernier_jour; cat $S/erreurs_20261113.log 2>/dev/null | tail -40
journalctl --user -u zeta-test-maj.service --since "2026-11-13" --no-pager | tail -30
systemctl --user list-timers | grep zeta
grep -n 'allowedTools\|disallowedTools\|setting-sources' ~/.local/bin/zeta_test_maj_site.sh
ls /home/riemann/projet_zeta/pdf/site/maj_site_20261112/audit/      # scripts de l'audit du 12/11
```
Expliquer **quelles commandes Bash** ont été refusées le 13/11 et pourquoi (règle d'outils trop étroite, commande composée avec `|`, `for`, `&&`, mode `-p` sans possibilité d'accepter…). **STOP — « go install »** avec le plan ci-dessous.

## Étape 2 — Installation (après « go install »)

### 2a. Script de contrôles `~/.local/bin/zeta_test_controles.sh` (lecture seule)
Reprendre et adapter les scripts de l'audit du 12/11 (les copier dans `~/.local/share/zeta_test_maj/`, ne pas les laisser dépendre d'un dossier daté). Entrée : la date du dernier test (`$S/dernier_ts`). Sortie : un fichier Markdown `$S/controles_<AAAAMMJJ>.md` avec 4 sections :
1. **Liens** : toutes les URL de `docs/**/*.html`, `README.md`, `docs/*.md`, et des `.md` du wiki **modifiés depuis le dernier test** (tous les `.md` du wiki au premier lancement). Code HTTP final (`curl -sSL`, 1 requête/s, 3 essais si 429 ou 5xx), page wiki absente, ancre absente (cible `id` ou `name`, préfixe `user-content-` sur GitHub). Statut 🟢/🟡/🔴. **Liste blanche** (ne pas compter comme erreur) : code tiers Plotly `docs/images/T10Demo/zeta_demovisualisation.html`, liens issues et Kanban du README (D23), DOI `10.1112/plms/s3-3.1.99` (403 aux robots), pages de renvoi du wiki.
2. **Nombre de lignes** : pour chaque `.md` modifié depuis le dernier test (dépôt et wiki), nombre annoncé dans le pied de page contre `wc -l`.
3. **Secrets** : sur les fichiers modifiés depuis le dernier test : IPv4 / IPv6, `fe80::<hex>`, adresse MAC, `PRIVATE KEY`, `ghp_`, `github_pat`, `token=`, `passw`, `duckdns` hors marqueur `<…>`, e-mails autres que l'adresse publique du projet. Sortie : `fichier:ligne | type`, sans la valeur.
4. **Formules (statique)** : dans les `.md` du wiki modifiés, motifs à risque dans les blocs `$`/`$$` (`\operatorname`, `|` dans un tableau math).
Durée maximale : 15 min (`timeout`). Montrer `bash -n` puis un **essai à la main** sur la journée d'hier ; montrer le haut du fichier produit et vérifier qu'il ne contient aucune valeur identifiante.

### 2b. Script principal `~/.local/bin/zeta_test_maj_site.sh`
1. Après la détection « un commit a été publié », lancer `zeta_test_controles.sh`, puis **ajouter le contenu** de `controles_<AAAAMMJJ>.md` à l'entrée donnée à Claude (section « Contrôles déjà faits par le script »).
2. Outils de Claude : `Read`, `Grep`, `Glob`, `WebFetch` seulement ; **retirer Bash** de `--allowedTools` et le mettre dans `--disallowedTools`. Garder `--setting-sources user` et le garde-fou (rapport < 400 octets ou contenant « Prêts à déposer… » = échec).
3. Ajouter une variable `ZETA_FORCE=1` qui ignore « une fois par jour » et « rien de nouveau » (pour les essais seulement).
4. Copier aussi `controles_<AAAAMMJJ>.md` dans `pdf/site/maj_site_<AAAAMMJJ>/` (pas dans `A_DEPOSER/`).

### 2c. Prompt du test `src/ia/prompts/PROMPT_TEST_AUTO_MAJ_SITE.md`
Ajouter une règle 9 : « Les contrôles de liens, de nombre de lignes et de secrets sont **déjà faits** par le script et fournis plus bas. N'utilise pas Bash. Reprends leurs résultats dans le tableau de validation, analyse les 🔴 et 🟡, et propose les corrections. N'écris plus "Bash a été refusé". » Mettre à jour son pied de page (date et nombre de lignes).

## Étape 3 — Essai forcé (après « go essai »)
```bash
ZETA_FORCE=1 systemctl --user start zeta-test-maj.service   # ou : ZETA_FORCE=1 ~/.local/bin/zeta_test_maj_site.sh
journalctl --user -u zeta-test-maj.service -n 30 --no-pager
```
(Si la variable ne passe pas par `systemctl`, lancer le script directement.) Vérifier : rapport **non partiel** (pas de « Bash a été refusé »), contrôles des 4 sections présents, 0 valeur identifiante (`grep -nE '[0-9]{1,3}(\.[0-9]{1,3}){3}|fe80::[0-9a-f]+:'`), `git status` du dépôt et du wiki inchangés, turbo inchangé.

## Étape 4 — Rapport
`RAPPORT_TEST_AUTO_V2_<AAAAMMJJ>_<HHMM>.md` + `.pdf` dans `pdf/site/maj_site_<AAAAMMJJ>/` : tableau de validation (🟢/🟡/🔴, preuve, reste à corriger) et tableau `page | ligne in | ligne out | date heure` (fichiers créés ou modifiés). Copier dans `A_DEPOSER/` : ce rapport, le rapport de l'essai forcé, `HANDOFF_SITE_<AAAAMMJJ>.md`.

Terminer par : **« hprzeta, donne le .md à claude.ai, projet SITE ZETA : il le range lui-même. »**

---
*PROMPT_TEST_AUTO_V2_20261114_1257.md · projet SITE ZETA · hprzeta · MAJ 14 novembre 2026 12:57 · 66 lignes*
