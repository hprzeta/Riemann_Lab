#!/bin/bash
# install.sh — à lancer UNE fois sur PC1 :  bash ~/projet_zeta/monitoring/install.sh
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="${ZETA_PY:-$HOME/projet_zeta/zeta_env/bin/python}"; [ -x "$PY" ] || PY=python3
mkdir -p "$ROOT"/data "$ROOT"/runs "$ROOT"/logs
chmod +x "$ROOT"/scripts/*.py "$ROOT"/*.sh
# anciens CSV du logger (logs/metrics) -> data/ (copie, sans écraser)
if ls "$HOME"/projet_zeta/logs/metrics/cluster_metrics_*.csv >/dev/null 2>&1; then
  cp -n "$HOME"/projet_zeta/logs/metrics/cluster_metrics_*.csv "$ROOT/data/" && echo "anciens CSV copiés dans data/"
fi
# ancien format plat runs/<id>/ -> runs/historique/ (run T1b du 15/10)
mkdir -p "$ROOT/runs/historique"
[ -d "$ROOT/runs/20261015_T1b_historique" ] && mv "$ROOT/runs/20261015_T1b_historique" "$ROOT/runs/historique/" && echo "run historique rangé dans runs/historique/"
# alias (idempotent)
if ! grep -qF "zeta_monitoring_alias.sh" "$HOME/.bashrc"; then
  echo "source \"$ROOT/zeta_monitoring_alias.sh\"   # Zêta monitoring" >> "$HOME/.bashrc"
  echo "alias ajouté dans ~/.bashrc"
fi
echo "Python : $PY"
"$PY" -c "import numpy, pandas, matplotlib; print('numpy/pandas/matplotlib : OK')" || echo "ATTENTION : numpy/pandas/matplotlib manquants"
"$PY" -c "import reportlab, PIL; print('reportlab/pillow (PDF) : OK')" || echo "PDF indisponible : $PY -m pip install reportlab pillow"
"$PY" "$ROOT/scripts/zeta_run_report.py" --index >/dev/null && echo "Monitoring-Runs.md régénéré"
echo
echo "Terminé. Ouvre un NOUVEAU terminal (ou : source ~/.bashrc), puis :  zeta-mon-on"
