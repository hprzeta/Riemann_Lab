# -*- coding: utf-8 -*-
"""
scan_arb_wrapper.py — Interface Python vers scan_zeros_arb (scan_arb.so)
═══════════════════════════════════════════════════════════════════════════
Remplace la boucle TAILLE_BLOC + Z_vect_correct dans le worker v4.1.

La détection est déplacée entièrement en C (Z_double, RS C0+C1 double) :
  - 1 appel C par worker au lieu de 102 appels Python-numpy
  - ×5 plus rapide que Z_vect_correct pour le scan pur
  - fa/fb précalculés → illinois_refine Option B sans recalcul Python

Chargement post-fork obligatoire (comme illinois_mpfr.so) :
  l'import de ce module dans le worker (après fork) charge scan_arb.so.
  Ne pas importer au niveau du module parent.

RÈGLE : step ≤ 0.010 (gap minimum mesuré = 0.019 à t=66678)

Auteur : hprzeta — Riemann_Lab_C — 2026-06-10
"""

import ctypes
import os
from typing import List, Tuple

_lib  = None
_STEP = 0.010   # pas gap-safe obligatoire


def _load_lib():
    """Charge scan_arb.so au premier appel (post-fork obligatoire)."""
    global _lib
    if _lib is None:
        so = os.path.join(os.path.dirname(__file__),
                          "c_modules", "scan_arb.so")
        if not os.path.exists(so):
            raise FileNotFoundError(
                f"scan_arb.so introuvable : {so}\n"
                f"Compiler avec : cd c_modules && make scan_arb.so"
            )
        _lib = ctypes.CDLL(so)
        _lib.scan_zeros_arb.restype  = ctypes.c_int
        _lib.scan_zeros_arb.argtypes = [
            ctypes.c_double,                    # t_min
            ctypes.c_double,                    # t_max
            ctypes.c_double,                    # step
            ctypes.POINTER(ctypes.c_double),    # brackets_a
            ctypes.POINTER(ctypes.c_double),    # brackets_b
            ctypes.POINTER(ctypes.c_double),    # fa
            ctypes.POINTER(ctypes.c_double),    # fb
            ctypes.c_int,                       # max_brackets
        ]
    return _lib


def scan_arb(
    t_min:        float,
    t_max:        float,
    step:         float = _STEP,
    max_brackets: int   = 100_000,
) -> List[Tuple[float, float, float, float]]:
    """Détecte les crochets [a,b] où Z(a)·Z(b) < 0 sur [t_min, t_max].

    Retourne une liste de (a, b, fa, fb) où fa=Z(a) et fb=Z(b) sont
    déjà calculés par scan_zeros_arb — illinois_refine Option B les réutilise
    directement, sans recalcul.

    Paramètres
    ----------
    t_min, t_max  — intervalle de scan
    step          — pas fixe (défaut 0.010, gap-safe mesuré)
    max_brackets  — taille max des buffers (défaut 100 000)

    Notes
    -----
    - Charger post-fork (ne pas appeler dans le parent avant Pool)
    - Z_double C0+C1 : précision ~1e-6 → suffisant pour la détection de signes
    - Pour t < 300, Z_double a une erreur ~1e-3 (N < 7 termes RS) :
      le seuil T_SEUIL_ILLINOIS_C dans le worker gère ce cas séparément.
    """
    lib = _load_lib()
    N   = max_brackets
    _a  = (ctypes.c_double * N)()
    _b  = (ctypes.c_double * N)()
    _fa = (ctypes.c_double * N)()
    _fb = (ctypes.c_double * N)()

    n = lib.scan_zeros_arb(t_min, t_max, step, _a, _b, _fa, _fb, N)
    return [(_a[i], _b[i], _fa[i], _fb[i]) for i in range(n)]
