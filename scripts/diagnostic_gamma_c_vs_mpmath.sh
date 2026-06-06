#!/usr/bin/env bash
# diagnostic_gamma_c_vs_mpmath.sh
# Phase C — diagnostic du biais entre gamma_c produit par illinois_mpfr.so
# et gamma_true corrigé par mpmath.siegelz.
#
# Usage :
#   cd ~/projet_zeta/src/calculs/optimisation
#   chmod +x diagnostic_gamma_c_vs_mpmath.sh
#   ./diagnostic_gamma_c_vs_mpmath.sh
#
# Sortie :
#   ~/phase_c_gamma_c_vs_mpmath.txt

set -euo pipefail

OUT="$HOME/phase_c_gamma_c_vs_mpmath.txt"
PYTMP="/tmp/diagnostic_gamma_c_vs_mpmath.py"

cat > "$PYTMP" <<'PY'
import ctypes
import mpmath
from pathlib import Path

mpmath.mp.dps = 35

SO = Path("c_modules/illinois_mpfr.so")
if not SO.exists():
    raise FileNotFoundError(f"Bibliothèque introuvable: {SO.resolve()}")

lib = ctypes.CDLL(str(SO))
lib.illinois_mpfr.restype = ctypes.c_double
lib.illinois_mpfr.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]


def sz(t):
    return float(mpmath.siegelz(t))


def find_interval_around_zero(t0, step=0.05, width=2.0):
    a = max(14.0, t0 - width)
    b = a + step
    prev = sz(a)
    x = b
    while x <= t0 + width:
        cur = sz(x)
        if prev * cur < 0:
            return x - step, x
        prev = cur
        x += step
    return None


samples = [
    14.13472514173469,
    79.33737502024937,
    299.84032605372130,
    500.0,
    520.0,
    648.786400888782,
]

print("gamma_ref,a,b,gamma_c,gamma_true,delta,residu_c,residu_true")
for ref in samples:
    interval = find_interval_around_zero(ref)
    if not interval:
        print(f"{ref:.15f},NO_INTERVAL")
        continue

    a, b = interval
    gamma_c = lib.illinois_mpfr(float(a), float(b), 1e-12)
    gamma_true = float(mpmath.findroot(mpmath.siegelz, gamma_c))

    print(
        f"{ref:.15f},"
        f"{a:.15f},"
        f"{b:.15f},"
        f"{gamma_c:.15f},"
        f"{gamma_true:.15f},"
        f"{(gamma_c - gamma_true):.6e},"
        f"{sz(gamma_c):.6e},"
        f"{sz(gamma_true):.6e}"
    )
PY

{
  echo "===== DATE ====="
  date
  echo
  echo "===== PWD ====="
  pwd
  echo
  echo "===== BRANCH ====="
  git -C "$HOME/projet_zeta" branch --show-current 2>/dev/null || true
  echo
  echo "===== CHECK SO ====="
  ls -lh c_modules/illinois_mpfr.so
  echo
  echo "===== DIAGNOSTIC gamma_c vs mpmath ====="
  python3 "$PYTMP"
} 2>&1 | tee "$OUT"

echo
echo "✅ Diagnostic terminé. Fichier créé : $OUT"
echo "➡️  Envoie-moi ce fichier : phase_c_gamma_c_vs_mpmath.txt"
