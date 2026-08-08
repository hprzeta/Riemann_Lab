#!/usr/bin/env python3
# perf_harness.py — charge illinois_arb.so via ctypes et boucle sur des brackets
# précalculés (brackets.json, généré par gen_brackets.py) pour obtenir un run
# assez long (~15-20s) et profilable par `perf record`. Aucun mpmath ici : on
# ne veut pas polluer le profil avec l'overhead de la génération des brackets.

import ctypes
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SO_PATH = os.path.join(HERE, "illinois_arb.so")
BRACKETS_PATH = os.path.join(HERE, "brackets.json")

lib = ctypes.CDLL(SO_PATH)
lib.illinois_refine_arb.restype = ctypes.c_double
lib.illinois_refine_arb.argtypes = [
    ctypes.c_double,  # a
    ctypes.c_double,  # b
    ctypes.c_double,  # fa
    ctypes.c_double,  # fb
    ctypes.c_double,  # tol
    ctypes.c_int,      # max_iter
]

with open(BRACKETS_PATH) as f:
    data = json.load(f)

brackets = data["zone_a_2newton"] + data["zone_b_1newton"]
print(f"{len(brackets)} brackets chargés "
      f"({len(data['zone_a_2newton'])} zone A 2-Newton, "
      f"{len(data['zone_b_1newton'])} zone B 1-Newton)")

REPEATS = int(sys.argv[1]) if len(sys.argv) > 1 else 40
TOL = 1e-12
MAX_ITER = 50

t0 = time.perf_counter()
n_calls = 0
for _ in range(REPEATS):
    for a, b, fa, fb in brackets:
        lib.illinois_refine_arb(a, b, fa, fb, TOL, MAX_ITER)
        n_calls += 1
elapsed = time.perf_counter() - t0

print(f"{n_calls} appels illinois_refine_arb en {elapsed:.2f}s "
      f"({elapsed / n_calls * 1000:.4f} ms/appel)")
