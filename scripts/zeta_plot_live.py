#!/usr/bin/env python3
# Wrapper : source unique = monitoring/scripts/zeta_plot_live.py (doublon retiré le 2026-10-17)
import runpy, sys, pathlib; d = pathlib.Path(__file__).resolve().parents[1] / "monitoring/scripts"; sys.path.insert(0, str(d)); sys.argv[0] = str(d / "zeta_plot_live.py"); runpy.run_path(sys.argv[0], run_name="__main__")
