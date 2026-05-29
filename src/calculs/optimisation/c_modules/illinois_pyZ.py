#!/usr/bin/env python3
# illinois_pyZ.py — Voie B : callback Python pour illinois_mpfr_cb
#
# Problème : illinois_mpfr.so utilise Z_mpfr (RS + C0+C1) avec biais ~9e-3.
# Solution : illinois_mpfr_cb accepte un callback z_func_t ; Python fournit
#            float(mpmath.siegelz(t)) → biais éliminé, précision ~1e-14.
#
# Interface publique :
#   illinois_c_exact(a, b, tol=1e-12) → float
#     Illinois C pur avec Z(t) = mpmath.siegelz, sans fallback mpmath.findroot.
#
# Contrainte respectée : illinois_mpfr(a, b, tol) (ancienne interface) reste
# inchangée et accessible via ctypes comme avant.
#
# Phase C — Riemann_Lab / hprzeta — 2026-05-29

import ctypes
import os
import mpmath

# précision mpmath pour le callback — 35 dps donne ~14-15 chiffres en double
mpmath.mp.dps = 35

# ── chargement de la bibliothèque ────────────────────────────────────────────
_SO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "illinois_mpfr.so")

if not os.path.exists(_SO_PATH):
    raise FileNotFoundError(
        f"illinois_mpfr.so introuvable : {_SO_PATH}\n"
        "Lancer 'make' dans c_modules/ d'abord."
    )

_lib = ctypes.CDLL(_SO_PATH)

# ── ancienne interface — inchangée (compatibilité ctypes existante) ───────────
_lib.illinois_mpfr.restype  = ctypes.c_double
_lib.illinois_mpfr.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]

_lib.Z_double.restype  = ctypes.c_double
_lib.Z_double.argtypes = [ctypes.c_double]

# ── nouvelle interface — Voie B ───────────────────────────────────────────────
# type C du callback : double (*z_func_t)(double t)
_Z_FUNC_T = ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double)

_lib.illinois_mpfr_cb.restype  = ctypes.c_double
_lib.illinois_mpfr_cb.argtypes = [
    ctypes.c_double,   # a_d
    ctypes.c_double,   # b_d
    ctypes.c_double,   # tol
    _Z_FUNC_T,         # zfunc — pointeur de fonction C
]

# ── callback Python → C ───────────────────────────────────────────────────────
def _z_mpmath(t: float) -> float:
    """Évalue la vraie Z(t) de Riemann via mpmath.siegelz.
    Appelé depuis C (illinois_mpfr_cb) à chaque itération Illinois.
    Retourne float64 (~15 chiffres) — suffisant pour |b−a| < 1e-12."""
    return float(mpmath.siegelz(t))

# IMPORTANT : conserver la référence Python vivante tant que le .so est chargé.
# Un GC prématuré de _Z_CB = segfault dans C.
_Z_CB = _Z_FUNC_T(_z_mpmath)


# ── interface publique ────────────────────────────────────────────────────────
def illinois_c_exact(a: float, b: float, tol: float = 1e-12) -> float:
    """Illinois C avec Z(t) = mpmath.siegelz — biais RS éliminé.

    Précondition : mpmath.siegelz(a) * mpmath.siegelz(b) < 0
    Précision    : ~1e-14 (limite double, largement > 1e-12 cible)
    Convergence  : ~15-20 appels mpmath.siegelz (Illinois super-linéaire)

    Retourne la partie imaginaire du zéro γ, vrai zéro de ζ(1/2+it).
    """
    return _lib.illinois_mpfr_cb(float(a), float(b), float(tol), _Z_CB)


def z_double_c(t: float) -> float:
    """Z(t) RS + C0+C1 en C double — pour diagnostic/comparaison uniquement."""
    return _lib.Z_double(float(t))


def illinois_c_rs(a: float, b: float, tol: float = 1e-12) -> float:
    """Illinois C avec Z_mpfr interne (RS + C0+C1) — ancienne interface v4.
    Biais ~9e-3, utile uniquement pour t > 1000 où RS est suffisamment précis."""
    return _lib.illinois_mpfr(float(a), float(b), float(tol))
