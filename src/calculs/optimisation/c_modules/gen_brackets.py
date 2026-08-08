#!/usr/bin/env python3
# gen_brackets.py — génère des brackets [a,b,fa,fb] représentatifs pour profiler
# illinois_refine_arb sur les deux branches Phase 2 (SEUIL_1NEWTON=20000) :
#   zone A : t in [500, 5000]      -> 2 Newton (biais_RS grand)
#   zone B : t in [50000, 200000]  -> 1 Newton (biais_RS < 6e-7)
# Sortie : JSON dans le scratchpad, consommé par perf_harness.py (pas de mpmath
# pendant le run profilé, pour ne pas polluer perf avec l'overhead mpmath).

import json
import os
import mpmath

# dps=15 suffit : on ne veut que le signe fa/fb pour amorcer illinois_refine_arb,
# pas une précision de publication (celle-ci vient de illinois_refine_arb lui-même).
mpmath.mp.dps = 15


def collect(t_start, t_end, n_cible, pas):
    brackets = []
    t = t_start
    za = float(mpmath.siegelz(t))
    while len(brackets) < n_cible and t < t_end:
        b = t + pas
        zb = float(mpmath.siegelz(b))
        if za * zb < 0:
            brackets.append((t, b, za, zb))
        t, za = b, zb
    return brackets


print("Collecte zone A (t in [500,5000], 2 Newton attendu)...", flush=True)
zone_a = collect(500.0, 5000.0, 150, 0.1)
print(f"  {len(zone_a)} brackets", flush=True)

print("Collecte zone B (t in [50000,150000], 1 Newton attendu)...", flush=True)
zone_b = collect(50000.0, 150000.0, 150, 0.15)
print(f"  {len(zone_b)} brackets", flush=True)

out = {"zone_a_2newton": zone_a, "zone_b_1newton": zone_b}
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brackets.json")
with open(path, "w") as f:
    json.dump(out, f)
print(f"Écrit : {path}")
