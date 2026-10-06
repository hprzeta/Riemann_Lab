#!/bin/bash
#===============================================================================
# zeta_backup_horsgit.sh - Sauvegarde sur Proton Drive de ce qui est HORS git
#
# A LANCER SUR PC1 (zeta-lab). Utilise le remote rclone "protondrive:".
# Menu interactif. rclone COPY uniquement : jamais de suppression distante.
#
# Jeux sauvegardes (destination : protondrive:hprzeta/Riemann_Lab/hors_git/) :
#   1) md/            -> md/
#   2) memoire Claude -> memoire_claude/
#   3) suivi          -> suivi/        (riemann_handoff SANS secrets_local)
#   4) non suivis git -> non_suivis/   (hors archives de config sensibles)
#
# Exclus VOLONTAIREMENT : secrets_local, .mcp.json, .env, ~/.ssh, rclone.conf,
#   calculs/ (4 Go > quota Proton 2 Gio), zeta_env/.
#
#   5) calculs legers -> calculs_legers/ (fichiers < 200 Ko : logs, PNG, petits CSV)
#   7) config locale  -> config_locale/ (~/.config/zeta : adresses du cluster, hors git)
#   8) ignores git    -> ignores_git/ (fichiers ignores par .gitignore / info/exclude, NON secrets :
#                        pdf/script, docs/diagnostics, *.bak-*, claude-traitement-journalier...)
#   6) secrets        -> secrets_chiffres/ (archive gpg SYMETRIQUE : secrets_local + secrets du
#                        projet ignores par git (.mcp.json, captures WireGuard, archive box...) ;
#                        phrase de passe saisie au clavier ; jamais en clair ; MANUEL uniquement ;
#                        rotation : seules les 2 archives les plus recentes sont gardees sur Proton)
#
# Usage : zeta-backup-horsgit            (menu)
#         zeta_backup_horsgit.sh --dry   (force la simulation)
#         zeta_backup_horsgit.sh --auto  (sans menu : jeux 1 a 5, 7 et 8, SANS secrets ; cron)
#
# Auteur : hprzeta · MAJ : 2026-10-03
#===============================================================================
set -u

REMOTE="protondrive:hprzeta/Riemann_Lab/hors_git"   # racine cote Proton
PROJ="$HOME/projet_zeta"                            # racine du projet
MEM="$HOME/.claude/projects/-home-riemann-projet-zeta/memory"
HANDOFF="$HOME/riemann_handoff"
TMP="$(mktemp -d)"                                  # dossier temporaire
trap 'rm -rf "$TMP"' EXIT                           # nettoyage a la sortie
DRY=""                                              # vide = envoi reel
AUTO=0                                              # 1 = mode cron, sans menu
for a in "$@"; do                                   # lecture de TOUS les arguments
  case "$a" in
    --dry)  DRY="--dry-run" ;;                      # simulation
    --auto) AUTO=1 ;;                               # mode cron
  esac
done

# Copie via rclone ; affiche le resume, pas le detail
copie(){ # $1=libelle  $2=source  $3=destination  $4..=options rclone
  local lib="$1" src="$2" dst="$3"; shift 3
  echo "--- $lib ---"
  if [ ! -e "$src" ]; then echo "   [!] source absente : $src"; return 1; fi
  timeout 600 rclone copy $DRY --stats-one-line -v "$src" "$dst" "$@" 2>&1 \
    | grep -E 'ERROR|Copied|Transferred|NOTICE: .*(Skipped copy|[0-9] / [0-9])' | tail -4
  return "${PIPESTATUS[0]}"
}

# 1) md/
j_md(){ copie "md/" "$PROJ/md" "$REMOTE/md"; }

# 2) memoire Claude : dossier memory + CLAUDE.md global
j_mem(){
  copie "memoire Claude (memory)" "$MEM" "$REMOTE/memoire_claude/memory"
  copie "CLAUDE.md global" "$HOME/.claude/CLAUDE.md" "$REMOTE/memoire_claude"
}

# 3) suivi : riemann_handoff sans secrets_local
j_suivi(){ copie "suivi (riemann_handoff)" "$HANDOFF" "$REMOTE/suivi" --exclude 'secrets_local/**'; }

# 4) fichiers non suivis par git (liste calculee a chaud)
j_ns(){
  ( cd "$PROJ" && git ls-files --others --exclude-standard -z ) | tr '\0' '\n' \
    | grep -Ev '(backup.*\.tgz|\.env|secret|token|\.key|\.pem)' > "$TMP/ns.txt"
  echo "   ($(wc -l < "$TMP/ns.txt") fichiers non suivis retenus)"
  copie "non suivis git" "$PROJ" "$REMOTE/non_suivis" --files-from "$TMP/ns.txt"
}

# Liste des fichiers ignores par git (gitignore + info/exclude), hors elements deja couverts
# ailleurs ou reconstructibles : zeta_env, calculs/ (jeu 5), wiki (depot a part), logs/ (cron 01h50
# vers PC3 puis Proton), md/ (jeu 1), caches Python.
liste_ignores(){
  ( cd "$PROJ" && git ls-files --others --ignored --exclude-standard ) \
    | grep -vE '^(zeta_env|calculs|Riemann_Lab\.wiki|logs|md)/|^src/calculs/optimisation/calculs/|__pycache__|\.pyc$|^\.claude/scheduled_tasks'
}
# Motif des fichiers SECRETS parmi les ignores (ceux-la partent seulement chiffres, jeu 6)
SECRET_RX='(^|/)(\.mcp\.json|\.env[^/]*)$|wireguard_screenshots/|BOX-SFR|-backup\.tgz$|materielunixlitepc2|pcemmaus|secret|token|\.(key|pem)$'

# 8) fichiers ignores par git, NON secrets
j_ign(){
  liste_ignores | grep -vE "$SECRET_RX" > "$TMP/ign.txt"
  echo "   ($(wc -l < "$TMP/ign.txt") fichiers ignores non secrets retenus)"
  copie "ignores par git (non secrets)" "$PROJ" "$REMOTE/ignores_git" --files-from "$TMP/ign.txt"
}

# 5) calculs legers : fichiers < 200 Ko des deux dossiers calculs/
j_calc(){
  ( cd "$PROJ" && find calculs src/calculs/optimisation/calculs -type f -size -200k ) > "$TMP/calc.txt"
  echo "   ($(wc -l < "$TMP/calc.txt") fichiers legers retenus)"
  copie "calculs legers" "$PROJ" "$REMOTE/calculs_legers" --files-from "$TMP/calc.txt"
}

# 7) config locale : ~/.config/zeta (cluster_hosts.env, hors git, droits 600 conserves)
j_cfg(){ copie "config locale (~/.config/zeta)" "$HOME/.config/zeta" "$REMOTE/config_locale"; }

# Rotation des archives de secrets sur Proton : garde les KEEP_SECRETS plus recentes.
# Garde-fous : ne touche QUE secrets_AAAAMMJJ.tar.gz.gpg dans secrets_chiffres/ ; ne s'execute
# que si le nouvel envoi est confirme present sur Proton ; supprime les plus anciennes seulement.
KEEP_SECRETS=2
rotation_secrets(){ # $1 = nom de l'archive qui vient d'etre envoyee
  local dir="$REMOTE/secrets_chiffres" nouveau="$1" liste n f
  liste="$(rclone lsf "$dir" --files-only 2>/dev/null | grep -E '^secrets_[0-9]{8}\.tar\.gz\.gpg$' | sort)"
  if ! printf '%s\n' "$liste" | grep -qx "$nouveau"; then   # le nouvel envoi doit etre visible
    echo "   [!] rotation sautee : $nouveau introuvable sur Proton"; return 1
  fi
  n=$(printf '%s\n' "$liste" | grep -c .)                    # nombre d'archives presentes
  if [ "$n" -le "$KEEP_SECRETS" ]; then
    echo "   rotation : $n archive(s) sur Proton, rien a supprimer (on garde les $KEEP_SECRETS plus recentes)"; return 0
  fi
  for f in $(printf '%s\n' "$liste" | head -n $((n - KEEP_SECRETS))); do   # les plus anciennes d'abord
    if [ -n "$DRY" ]; then echo "   [simulation] supprimerait : $f"
    elif rclone deletefile "$dir/$f"; then echo "   rotation : ancienne archive supprimee : $f"
    else echo "   [!] suppression impossible : $f"; fi
  done
}

# 6) secrets : archive tar.gz chiffree gpg symetrique (phrase saisie, jamais stockee)
j_sec(){
  local src="$HANDOFF/secrets_local" arc="$TMP/secrets_$(date +%Y%m%d).tar.gz.gpg"
  [ -d "$src" ] || { echo "   [!] absent : $src"; return 1; }
  liste_ignores | grep -E "$SECRET_RX" > "$TMP/sec.txt"             # secrets du projet ignores par git
  echo "   (secrets_local + $(wc -l < "$TMP/sec.txt") fichiers secrets du projet)"
  [ -n "$DRY" ] && { echo "   [simulation] archive non creee"; return 0; }
  echo "   Phrase de passe a saisir (2 fois) :"
  tar -czf - -C "$HANDOFF" secrets_local -C "$PROJ" -T "$TMP/sec.txt" | gpg --symmetric --cipher-algo AES256 -o "$arc" \
    || { echo "   [X] chiffrement echoue, rien envoye"; return 1; }
  local nom_arc rc; nom_arc="$(basename "$arc")"
  copie "secrets chiffres" "$arc" "$REMOTE/secrets_chiffres"; rc=$?
  rm -f "$arc"                                       # aucune copie locale residuelle
  if [ "$rc" -eq 0 ]; then rotation_secrets "$nom_arc"; else echo "   [!] envoi en erreur : rotation sautee, anciennes archives conservees"; fi
}

# Controle prealable : remote Proton joignable
verif(){
  rclone lsd "protondrive:hprzeta" >/dev/null 2>&1 \
    || { echo "[X] Proton injoignable (token expire ? voir zeta_proton_status.sh)"; exit 2; }
}

# Menu
menu(){
  echo "=============================================="
  echo " zeta-backup-horsgit  $( [ -n "$DRY" ] && echo '[SIMULATION]' || echo '[ENVOI REEL]')"
  echo "=============================================="
  echo " 1) md/"
  echo " 2) memoire Claude"
  echo " 3) suivi (riemann_handoff, sans secrets)"
  echo " 4) fichiers non suivis par git"
  echo " 5) calculs legers (< 200 Ko)"
  echo " 6) secrets (chiffres gpg, phrase demandee)"
  echo " 7) config locale (~/.config/zeta)"
  echo " 8) fichiers ignores par git (non secrets)"
  echo " a) TOUT sauf secrets (1 a 5, 7 et 8)"
  echo " d) basculer simulation / envoi reel"
  echo " q) quitter"
  printf " Choix : "
}

verif
if [ "$AUTO" -eq 1 ]; then                           # mode cron : pas de menu
  echo "=== $(date -Iseconds) START horsgit ==="
  j_md; j_mem; j_suivi; j_ns; j_calc; j_cfg; j_ign
  echo "=== $(date -Iseconds) END horsgit ==="
  exit 0
fi
while true; do
  menu; read -r c || break
  case "$c" in
    1) j_md ;;
    2) j_mem ;;
    3) j_suivi ;;
    4) j_ns ;;
    5) j_calc ;;
    6) j_sec ;;
    7) j_cfg ;;
    8) j_ign ;;
    a|A) j_md; j_mem; j_suivi; j_ns; j_calc; j_cfg; j_ign ;;
    d) [ -n "$DRY" ] && DRY="" || DRY="--dry-run" ;;
    q|Q) break ;;
    *) echo "choix invalide" ;;
  esac
done
echo "Termine. Verification : rclone lsd $REMOTE"
