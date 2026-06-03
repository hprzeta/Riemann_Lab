#!/usr/bin/env python3
# illinois_pyZ.py — Voie B : wrappers Python pour illinois_mpfr.so
#
# Option B (2026-06-03) :
#   illinois_refine(a, b, fa, fb, ...) — interface principale.
#   fa/fb fournis par Python (mpmath.siegelz) → biais RS éliminé à l'init.
#   Les itérations intermédiaires utilisent Z_mpfr (C) — précis pour t≥300.
#
# Aussi disponible : illinois_c_exact via callback (toutes valeurs via mpmath).
#
# Phase C — Riemann_Lab / hprzeta — 2026-06-03

import ctypes
import os
import mpmath

mpmath.mp.dps = 35

# ── chargement de la bibliothèque ────────────────────────────────────────────
_SO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "illinois_mpfr.so")

if not os.path.exists(_SO_PATH):
    raise FileNotFoundError(
        f"illinois_mpfr.so introuvable : {_SO_PATH}\n"
        "Lancer 'make' dans c_modules/ d'abord."
    )

_lib = ctypes.CDLL(_SO_PATH)

# ── interface principale Option B ─────────────────────────────────────────────
_lib.illinois_refine.restype  = ctypes.c_double
_lib.illinois_refine.argtypes = [
    ctypes.c_double,  # a
    ctypes.c_double,  # b
    ctypes.c_double,  # fa
    ctypes.c_double,  # fb
    ctypes.c_int,     # prec_bits
    ctypes.c_double,  # tol
    ctypes.c_int,     # max_iter
]

# ── interface callback (voie B alternative) ───────────────────────────────────
_lib.illinois_mpfr.restype  = ctypes.c_double
_lib.illinois_mpfr.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]

_Z_FUNC_T = ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double)

_lib.illinois_mpfr_cb.restype  = ctypes.c_double
_lib.illinois_mpfr_cb.argtypes = [
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    _Z_FUNC_T,
]

def _z_mpmath(t: float) -> float:
    """Évalue Z(t) = mpmath.siegelz(t) pour le callback C."""
    return float(mpmath.siegelz(t))

# IMPORTANT : conserver la référence Python vivante — GC prématuré = segfault C.
_Z_CB = _Z_FUNC_T(_z_mpmath)


# ── interfaces publiques ──────────────────────────────────────────────────────

def illinois_c_refine(a: float, b: float, fa: float, fb: float,
                      prec_bits: int = 170, tol: float = 1e-12,
                      max_iter: int = 100) -> float:
    """Illinois C Option B — fa/fb fournis par Python.

    Interface principale. fa et fb doivent être calculés par mpmath.siegelz
    AVANT l'appel (typiquement déjà disponibles depuis le balayage).

    Précondition : fa * fb < 0
    Retourne : partie imaginaire du zéro affiné (précision ~1e-3 pour t<62000,
               ~1e-12 pour t très grand où Z_mpfr est précis).
    """
    return _lib.illinois_refine(float(a), float(b), float(fa), float(fb),
                                int(prec_bits), float(tol), int(max_iter))


def illinois_c_exact(a: float, b: float, tol: float = 1e-12) -> float:
    """Illinois C avec callback mpmath.siegelz — toutes valeurs Z via Python.

    Toutes les évaluations Z (y compris les intermédiaires) passent par
    mpmath.siegelz → précision ~1e-14 même pour t<300.
    Coût : N appels Python par itération (plus lent qu'illinois_c_refine).

    Précondition : mpmath.siegelz(a) * mpmath.siegelz(b) < 0
    """
    return _lib.illinois_mpfr_cb(float(a), float(b), float(tol), _Z_CB)
