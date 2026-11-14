# PROMPT Claude Code — Installer le test automatique de mise à jour du site sur PC1

> Préparé sur claude.ai (projet SITE ZETA) le 12/11/2026 à 00:48. Rapport d'analyse : `RAPPORT_ANALYSE_TEST_AUTO_MAJ_SITE_20261112_0048.md`.
> **But :** au démarrage de session de PC1, puis toutes les 3 h tant qu'il reste allumé, lancer un test de mise à jour **en lecture seule**, **au plus une fois par jour** et **seulement si un commit a été publié** depuis le dernier test.
> **Tout est local** (`~/.local/bin`, `~/.config/systemd/user`, `src/ia/prompts`) : **0 commit, 0 push**.

## Règles
1. **STOP** aux points marqués ; attendre le mot indiqué (« go install », « go activation »).
2. Aucune modification du dépôt suivi, du wiki, du site. Ne pas toucher au hook de fin de session existant ni à `monitoring/Monitoring-Runs.md`.
3. Si un fichier cible existe déjà : copie `.bak-20261112` avant de l'écraser.
4. Aucune valeur identifiante dans les messages et le rapport.
5. Pas de page publique concernée : l'état AVANT/APRÈS se montre **dans le terminal** (sorties de commandes), pas dans Chrome.

## Étape 0 — Ranger le prompt
```bash
mkdir -p /home/riemann/projet_zeta/src/ia/prompts
cd /home/riemann/projet_zeta/src/ia/prompts
unzip -o ~/Téléchargements/MAJ_TEST_AUTO_MAJ_SITE_20261112_0048.zip   # ou ~/Downloads/
```
Le zip contient aussi `PROMPT_TEST_AUTO_MAJ_SITE.md` : c'est le prompt que la minuterie utilisera à chaque test (il reste ici, dans `src/ia/prompts/`, local).

## Étape 1 — État AVANT (terminal)
```bash
systemctl --user list-timers --all | grep -i zeta || echo "aucune minuterie zeta"
ls -l ~/.local/bin/zeta_test_maj_site.sh ~/.config/systemd/user/zeta-test-maj.* 2>&1
```

## Étape 2 — Dossier du jour
```bash
D=/home/riemann/projet_zeta/pdf/site/maj_site_$(date +%Y%m%d); mkdir -p "$D/A_DEPOSER"
cp -p /home/riemann/projet_zeta/src/ia/prompts/RAPPORT_ANALYSE_TEST_AUTO_MAJ_SITE_20261112_0048.* "$D/"
cp -p /home/riemann/projet_zeta/src/ia/prompts/PROMPT_INSTALL_TEST_AUTO_MAJ_SITE_20261112_0048.md "$D/"
```

## Étape 3 — Diagnostic (lecture seule) — montrer chaque sortie
```bash
command -v claude && claude --version          # chemin ABSOLU de claude, à noter (CLAUDE_BIN)
claude --help | grep -iE 'allowedTools|disallowedTools|-p, --print'
systemctl --user is-system-running             # le gestionnaire utilisateur répond ?
command -v notify-send git curl timeout
loginctl show-user "$USER" -p Linger           # info seulement, ne rien changer
grep -n '"SessionEnd"\|"Stop"' ~/.claude/settings.json 2>/dev/null   # hook existant : montrer, ne pas toucher
git -C /home/riemann/projet_zeta branch --show-current
git -C /home/riemann/projet_zeta/Riemann_Lab.wiki branch --show-current
```
**STOP** et décrire l'écart si : `claude` introuvable, options `--allowedTools`/`--disallowedTools` absentes de l'aide, gestionnaire `systemctl --user` indisponible, ou dossiers absents. Sinon, montrer le plan d'installation et attendre **« go install »**.

## Étape 4 — Installation (après « go install »)

### 4a. Script `~/.local/bin/zeta_test_maj_site.sh`
Remplacer `CLAUDE_BIN` par le chemin absolu trouvé à l'étape 3.
```bash
#!/usr/bin/env bash
# zeta_test_maj_site.sh — test de mise à jour du site zêta, LECTURE SEULE.
# Lancé par la minuterie systemd utilisateur zeta-test-maj.timer. Créé le 2026-11-12.
set -u
CLAUDE_BIN=/CHEMIN/ABSOLU/claude
REPO=/home/riemann/projet_zeta
WIKI=$REPO/Riemann_Lab.wiki
PROMPT=$REPO/src/ia/prompts/PROMPT_TEST_AUTO_MAJ_SITE.md
ETAT=$HOME/.local/state/zeta_test_maj
mkdir -p "$ETAT"
JOUR=$(date +%Y%m%d)

# 1. Réseau (PC déplacé, hors ligne) : on réessaiera au prochain passage
curl -s -o /dev/null -m 10 https://github.com || { echo "hors ligne"; exit 0; }

# 2. Au plus une fois par jour
[ "$(cat "$ETAT/dernier_jour" 2>/dev/null)" = "$JOUR" ] && { echo "déjà testé aujourd'hui"; exit 0; }

# 3. Quelque chose a-t-il été publié ? (lecture des têtes distantes, aucun fetch)
TETES=$( { git ls-remote https://github.com/hprzeta/Riemann_Lab.git \
             refs/heads/Riemann_Lab_IA refs/heads/Riemann_Lab_C refs/heads/main refs/heads/Riemann_Lab_Test
           git ls-remote https://github.com/hprzeta/Riemann_Lab.wiki.git refs/heads/master; } | sort )
[ -n "$TETES" ] || { echo "ls-remote vide"; exit 0; }
ANCIENNES=$(cat "$ETAT/dernieres_tetes" 2>/dev/null)
if [ "$TETES" = "$ANCIENNES" ]; then
  echo "$JOUR" > "$ETAT/dernier_jour"; echo "rien de nouveau"; exit 0
fi

# 4. Historique depuis le dernier test (7 jours au premier lancement)
DEPUIS=$(cat "$ETAT/dernier_ts" 2>/dev/null || date -d '7 days ago' +%s)
LOG_CODE=$(git -C "$REPO" log --all --since="@$DEPUIS" --stat --date=iso | head -c 60000)
LOG_WIKI=$(git -C "$WIKI" log --all --since="@$DEPUIS" --stat --date=iso | head -c 30000)

# 5. Test sans interface, outils de lecture seulement
D=$REPO/pdf/site/maj_site_$JOUR; mkdir -p "$D/A_DEPOSER"
R=$D/RAPPORT_TEST_AUTO_MAJ_SITE_${JOUR}_$(date +%H%M).md
cd "$REPO" || exit 1
timeout 30m nice -n 10 "$CLAUDE_BIN" -p "$(cat "$PROMPT")

## Têtes publiées au dernier test
${ANCIENNES:-(premier test)}
## Têtes publiées maintenant
$TETES
## git log du dépôt depuis le dernier test
$LOG_CODE
## git log du wiki depuis le dernier test
$LOG_WIKI" \
  --allowedTools "Read" "Grep" "Glob" "WebFetch" "Bash(curl -s:*)" "Bash(grep:*)" "Bash(wc:*)" \
  --disallowedTools "Edit" "Write" "NotebookEdit" "Bash(git:*)" "Bash(rm:*)" "Bash(mv:*)" "Bash(cp:*)" \
  > "$R" 2> "$ETAT/erreurs_$JOUR.log"
CODE=$?

# 6. Réussite seulement : marquer le test comme fait, pied de page, copie pour claude.ai
if [ $CODE -eq 0 ] && [ -s "$R" ]; then
  echo "$TETES" > "$ETAT/dernieres_tetes"; echo "$JOUR" > "$ETAT/dernier_jour"; date +%s > "$ETAT/dernier_ts"
  N=$(( $(wc -l < "$R") + 3 ))
  printf '\n---\n*%s · test automatique (lecture seule) · %s · %s lignes*\n' \
    "$(basename "$R")" "$(date '+%d/%m/%Y %H:%M')" "$N" >> "$R"
  cp -p "$R" "$D/A_DEPOSER/"
  notify-send "Site zêta" "Test de mise à jour prêt : $(basename "$R")" 2>/dev/null || true
else
  echo "échec du test (code $CODE) : voir $ETAT/erreurs_$JOUR.log"; exit 1
fi
```
Puis : `chmod 755 ~/.local/bin/zeta_test_maj_site.sh && bash -n ~/.local/bin/zeta_test_maj_site.sh`.

### 4b. Service `~/.config/systemd/user/zeta-test-maj.service`
```ini
[Unit]
Description=Test automatique de mise à jour du site zêta (lecture seule)
After=network-online.target

[Service]
Type=oneshot
ExecStart=%h/.local/bin/zeta_test_maj_site.sh
TimeoutStartSec=40min
```

### 4c. Minuterie `~/.config/systemd/user/zeta-test-maj.timer`
```ini
[Unit]
Description=Test de mise à jour du site zêta : 10 min après l'ouverture de session, puis toutes les 3 h

[Timer]
OnStartupSec=10min
OnUnitActiveSec=3h

[Install]
WantedBy=timers.target
```
Contrôle : `systemd-analyze --user verify ~/.config/systemd/user/zeta-test-maj.*`.

### 4d. Premier essai à la main (avant activation)
```bash
systemctl --user daemon-reload
systemctl --user start zeta-test-maj.service      # dure quelques minutes
journalctl --user -u zeta-test-maj.service -n 30 --no-pager
ls -l /home/riemann/projet_zeta/pdf/site/maj_site_$(date +%Y%m%d)/A_DEPOSER/
systemctl --user start zeta-test-maj.service      # 2e essai : doit répondre « déjà testé aujourd'hui »
journalctl --user -u zeta-test-maj.service -n 5 --no-pager
git -C /home/riemann/projet_zeta status --short   # aucun changement dû au test (hors pdf/site/)
git -C /home/riemann/projet_zeta/Riemann_Lab.wiki status --short   # vide
```
Montrer le rapport produit (premières lignes) et vérifier : 0 valeur identifiante (`grep -nE '[0-9]{1,3}(\.[0-9]{1,3}){3}|@|fe80::[0-9a-f]+:'`).

**STOP — attendre « go activation ».**

### 4e. Activation
```bash
systemctl --user enable --now zeta-test-maj.timer
systemctl --user list-timers | grep zeta
```

## Étape 5 — État APRÈS (terminal)
`systemctl --user list-timers | grep zeta` (prochain passage visible) ; `ls -l ~/.local/state/zeta_test_maj/`.

## Retour en arrière
```bash
systemctl --user disable --now zeta-test-maj.timer
mv ~/.config/systemd/user/zeta-test-maj.timer ~/.config/systemd/user/zeta-test-maj.service ~/.local/bin/zeta_test_maj_site.sh /home/riemann/projet_zeta/pdf/archive/
systemctl --user daemon-reload
```
(on archive, on ne supprime pas)

## Étape 6 — Rapport
`RAPPORT_MAJ_TEST_AUTO_<AAAAMMJJ>_<HHMM>.md` + `.pdf` dans `pdf/site/maj_site_<AAAAMMJJ>/` : tableau de validation (🟢/🟡/🔴, preuve, reste à corriger) et tableau `page | ligne in | ligne out | date heure` (fichiers créés). Un seul `HANDOFF_SITE_<AAAAMMJJ>.md`. Copier uniquement les `.md` dans `A_DEPOSER/`.

Terminer par : **« hprzeta, donne le .md à claude.ai, projet SITE ZETA : il le range lui-même. »**

---
*PROMPT_INSTALL_TEST_AUTO_MAJ_SITE_20261112_0048.md · projet SITE ZETA · hprzeta · MAJ 12 novembre 2026 00:48 · 183 lignes*
