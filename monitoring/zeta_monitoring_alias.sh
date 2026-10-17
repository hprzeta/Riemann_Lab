# zeta_monitoring_alias.sh — commandes du monitoring Zêta (à « source »-er depuis ~/.bashrc, fait par install.sh)
# Ce sont des fonctions bash (comme des alias, mais qui acceptent des arguments).
export ZETA_MON_ROOT="${ZETA_MON_ROOT:-$HOME/projet_zeta/monitoring}"
export ZETA_PY="${ZETA_PY:-$HOME/projet_zeta/zeta_env/bin/python}"
[ -x "$ZETA_PY" ] || export ZETA_PY=python3
_zs() { echo "$ZETA_MON_ROOT/scripts/$1"; }
_zcalc() { echo "${ZETA_CALCULS:-$HOME/projet_zeta/calculs}"; }

zeta-mon-on() {   # logger 1 s + détecteur automatique de runs (arrête d'abord les anciens)
  mkdir -p "$ZETA_MON_ROOT"/data "$ZETA_MON_ROOT"/runs "$ZETA_MON_ROOT"/logs
  pkill -f zeta_log_metrics.py 2>/dev/null; pkill -f zeta_run_watch.py 2>/dev/null; sleep 1
  setsid nohup nice -n 19 "$ZETA_PY" "$(_zs zeta_log_metrics.py)" "$@" > "$ZETA_MON_ROOT/logs/logger.log" 2>&1 &
  setsid nohup nice -n 19 "$ZETA_PY" "$(_zs zeta_run_watch.py)" > "$ZETA_MON_ROOT/logs/watch.log" 2>&1 &
  sleep 2; zeta-mon-status
}
zeta-mon-off() { pkill -f zeta_log_metrics.py; pkill -f zeta_run_watch.py; echo "monitoring arrêté"; }
zeta-mon-status() {
  echo "== processus =="; pgrep -af "zeta_log_metrics.py|zeta_run_watch.py" | cut -c1-110 || echo "(aucun : lancer zeta-mon-on)"
  echo "== dernière mesure =="; tail -n 5 "$ZETA_MON_ROOT"/data/cluster_metrics_$(date +%Y%m%d).csv 2>/dev/null || echo "(pas de CSV du jour)"
  echo "== dernier run =="; ls -1t "$ZETA_MON_ROOT/runs" 2>/dev/null | head -3
  echo "== watcher =="; tail -n 3 "$ZETA_MON_ROOT/logs/watch.log" 2>/dev/null
}
zeta-live()    { nice -n 19 "$ZETA_PY" "$(_zs zeta_plot_live.py)" "${1:-$(_zcalc)}" --colonne partie_imaginaire "${@:2}"; }
zeta-metrics() { nice -n 19 "$ZETA_PY" "$(_zs zeta_plot_metrics.py)" --minutes "${1:-15}" --refresh "${2:-2}"; }
zeta-gue()     { "$ZETA_PY" "$(_zs zeta_gue_hist.py)" "${1:-$(_zcalc)}" --colonne partie_imaginaire "${@:2}"; }   # ajouter --live pour la fenêtre rafraîchie (30 s)

# --- Lanceur de run avec monitoring (recommandé : toi ET Claude Code) ---
zeta-mon-exec()     { "$ZETA_PY" "$(_zs zeta_mon_run.py)" exec "$@"; }      # --nom N --type test|prod [--csv X] [--fenetres auto|oui|non] -- commande...
zeta-mon-start()    { "$ZETA_PY" "$(_zs zeta_mon_run.py)" start "$@"; }     # run lancé à côté : --nom N --type test|prod [--pid PID]
zeta-mon-stop()     { "$ZETA_PY" "$(_zs zeta_mon_run.py)" stop "$@"; }      # --code N [--attendre]
zeta-mon-fenetres() { "$ZETA_PY" "$(_zs zeta_mon_run.py)" fenetres "$@"; }  # ouvre les 3 fenêtres rangées (sans run)
zeta-mon-fermer()   { "$ZETA_PY" "$(_zs zeta_mon_run.py)" fermer; }         # ferme les fenêtres de graphiques
zeta-run-hint() {  # AVANT un run : zeta-run-hint NOM [CSV_ou_dossier]
  [ -z "$1" ] && { echo "usage : zeta-run-hint NOM [CSV|dossier]"; return 1; }
  mkdir -p "$ZETA_MON_ROOT/runs"; printf 'nom=%s\ncsv=%s\n' "$1" "$2" > "$ZETA_MON_ROOT/runs/.hint"
  echo "indice enregistré pour le prochain run : $1 ${2:+(csv : $2)}"
}
zeta-report() {    # régénère le rapport : zeta-report [dossier_run] [--lang en]
  "$ZETA_PY" "$(_zs zeta_run_report.py)" "$@"; }
zeta-index()   { "$ZETA_PY" "$(_zs zeta_run_report.py)" --index; }
zeta-runs()    { ls -1t "$ZETA_MON_ROOT/runs" | head -20; }
