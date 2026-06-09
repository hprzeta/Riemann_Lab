"""
arb_wrapper.py — Z(t) via Arb/FLINT arb_fpwrap_cdouble_hardy_z
═══════════════════════════════════════════════════════════════
Expose arb_hardy_z(t) comme remplacement direct de mpmath.siegelz.
Précision : double (~15 dps) — suffisant pour l'affinage Illinois à tol=1e-12.
Speedup mesuré vs mpmath dps=35 : ~27× (benchmark 2026-06-09).

Si la libflint bundlée est introuvable, arb_hardy_z replie sur mpmath.siegelz
sans bruit — le calcul continue, juste plus lentement.

Auteur : hprzeta — Riemann_Lab_C
"""

import ctypes
import glob
import os
import sys

import mpmath


# ─── Découverte de la libflint (bundlée avec python-flint) ──────────────────

def _localiser_libflint() -> str | None:
    """Retourne le chemin absolu de libflint-*.so.21+ bundlée avec python-flint.

    Stratégie : remonter depuis flint.__file__ vers le dossier
    python_flint.libs/ voisin, qui contient le .so avec les symboles
    acb_dirichlet_hardy_z et arb_fpwrap_cdouble_hardy_z.
    """
    try:
        import flint as _flint_pkg
    except ImportError:
        return None  # python-flint non installé

    # Dossier site-packages contenant le package flint/
    site_packages = os.path.dirname(os.path.dirname(os.path.abspath(_flint_pkg.__file__)))
    pattern = os.path.join(site_packages, "python_flint.libs", "libflint-*.so*")
    candidats = sorted(glob.glob(pattern))

    # Garder seulement les .so version ≥ 21 (FLINT 3 — acb_dirichlet fusionné)
    for chemin in candidats:
        nom = os.path.basename(chemin)
        try:
            # Format : libflint-<hash>.so.<major>.<minor>.<patch>
            version_str = nom.split(".so.")[-1] if ".so." in nom else "0"
            major = int(version_str.split(".")[0])
            if major >= 21:  # FLINT 3.0 → soversion 21
                return chemin
        except (ValueError, IndexError):
            continue

    return None


# ─── Chargement ctypes ───────────────────────────────────────────────────────

class _CDoubleComplex(ctypes.Structure):
    """Représentation ctypes de _Complex double (ABI x86-64 System V)."""
    _fields_ = [("real", ctypes.c_double), ("imag", ctypes.c_double)]


def _charger_arb_hardy_z(chemin_so: str):
    """Charge arb_fpwrap_cdouble_hardy_z et retourne un callable (t: float) -> float."""
    lib = ctypes.CDLL(chemin_so)
    fn = lib.arb_fpwrap_cdouble_hardy_z
    fn.restype = ctypes.c_int
    fn.argtypes = [ctypes.POINTER(_CDoubleComplex), _CDoubleComplex, ctypes.c_int]

    # Buffer partagé — évite une allocation ctypes par appel
    _buf = _CDoubleComplex(0.0, 0.0)

    def _arb_hardy_z(t: float) -> float:
        """Évalue Z(t) via Arb/FLINT. Retourne partie réelle (Z est réelle pour t réel)."""
        fn(ctypes.byref(_buf), _CDoubleComplex(float(t), 0.0), 0)
        return _buf.real

    return _arb_hardy_z


# ─── Initialisation au chargement du module ──────────────────────────────────

_libflint_chemin = _localiser_libflint()

if _libflint_chemin is not None:
    try:
        arb_hardy_z = _charger_arb_hardy_z(_libflint_chemin)
        ARB_DISPONIBLE = True
        ARB_BACKEND = f"Arb/FLINT ({os.path.basename(_libflint_chemin)})"
    except (OSError, AttributeError) as _e:
        # .so trouvé mais symbole absent ou chargement raté
        arb_hardy_z = mpmath.siegelz
        ARB_DISPONIBLE = False
        ARB_BACKEND = f"mpmath.siegelz (fallback — {_e})"
else:
    arb_hardy_z = mpmath.siegelz
    ARB_DISPONIBLE = False
    ARB_BACKEND = "mpmath.siegelz (fallback — python-flint introuvable)"


# ─── Diagnostic (appelable manuellement ou depuis le main de v4_1) ───────────

def info_backend() -> str:
    """Retourne une ligne décrivant le backend actif."""
    statut = "✓ actif" if ARB_DISPONIBLE else "⚠ fallback"
    return f"arb_wrapper [{statut}] — {ARB_BACKEND}"
