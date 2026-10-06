#!/bin/sh
# zeta_diag_publier.sh — copie les diagnostics privés (A) vers la version publiable (B), sans IP ni MAC.
# A (privé)  : ~/zeta_inventaire/DIAGNOSTIC
# B (dépôt)  : ~/projet_zeta/docs/diagnostics   (aucun git add/commit ici)
SRC="$HOME/zeta_inventaire/DIAGNOSTIC"
DST="$HOME/projet_zeta/docs/diagnostics"
mkdir -p "$DST" || exit 1
for f in "$SRC"/*.md; do
  [ -f "$f" ] || continue
  sed -E \
    -e 's/([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}/<MAC>/g' \
    -e 's/[0-9a-fA-F]{1,4}(:[0-9a-fA-F]{1,4}){3,7}(::)?(\/[0-9]+)?/<IPv6>/g' \
    -e 's/[0-9]{1,3}(\.[0-9]{1,3}){3}(\/[0-9]+)?/<IP>/g' \
    "$f" > "$DST/$(basename "$f")"
  echo "copié : $(basename "$f")"
done
echo "--- Contrôle résiduel (IP/MAC) ---"
grep -nE '([0-9]{1,3}\.){3}[0-9]{1,3}|([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}' "$DST"/*.md || echo "OK : aucune IP ni MAC détectée"
# Bandeau : la version B n'est plus "privée"
sed -i -E 's/^> Document PRIVÉ.*/> Version publiable : IP, IPv6 et MAC masquées. Version complète en privé./' "$DST"/*.md

# Sauvegarde chiffrée de A vers Proton Drive (ne bloque pas si hors ligne)
if command -v rclone >/dev/null 2>&1; then
  for d in DIAGNOSTIC SCHEMAS; do
    if [ -d "$HOME/zeta_inventaire/$d" ] && rclone copy "$HOME/zeta_inventaire/$d" "protondrive:hprzeta/Riemann_Lab/zeta_inventaire/$d" --contimeout 10s --timeout 30s --retries 1 >/dev/null 2>&1; then
      echo "Proton : $d sauvegardé"
    else
      echo "Proton : $d NON sauvegardé (hors ligne ou session expirée)"
    fi
  done
fi
