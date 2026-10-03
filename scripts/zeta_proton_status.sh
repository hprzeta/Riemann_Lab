#!/bin/bash
#===============================================================================
# zeta_proton_status.sh - Verifie depuis PC1 l'etat du backup Proton de PC3
#
# A LANCER SUR PC1 (zeta-lab). Interroge PC3 par SSH et lit le flag
# PROTON_KO.flag pose par check_proton.sh (cron 8h sur PC3).
#
# Codes de sortie :
#   0 = Proton OK (pas de flag)
#   1 = Proton KO (flag present) -> a reparer avec fix_proton.sh sur PC3
#   2 = PC3 injoignable en SSH
#
# Usage : ./zeta_proton_status.sh          (affichage lisible)
#         ./zeta_proton_status.sh --quiet  (juste le code retour, pour scripts)
#
# Auteur : hprzeta · MAJ : 2026-09-19
#===============================================================================
set -u

HOST="zeta-backup"                       # alias SSH de PC3
FLAG="/home/pjexosql/PROTON_KO.flag"
QUIET=0
[ "${1:-}" = "--quiet" ] && QUIET=1

say(){ [ "$QUIET" -eq 1 ] || printf '%s\n' "$*"; }

# PC3 joignable ?
if ! ssh -o ConnectTimeout=8 -o BatchMode=yes "$HOST" true 2>/dev/null; then
  say "[?] PC3 ($HOST) injoignable en SSH — etat Proton inconnu."
  exit 2
fi

# Le flag existe-t-il ?
if ssh "$HOST" "test -f $FLAG" 2>/dev/null; then
  say "[X] PROTON KO — backup cloud casse (token expire ?)."
  say "    -> Sur PC3 : bash ~/fix_proton.sh   (regenere le token)"
  # detail eventuel
  if [ "$QUIET" -eq 0 ]; then
    ssh "$HOST" "cat $FLAG" 2>/dev/null | sed 's/^/    | /'
  fi
  exit 1
else
  say "[OK] Proton — backup cloud operationnel."
  exit 0
fi
