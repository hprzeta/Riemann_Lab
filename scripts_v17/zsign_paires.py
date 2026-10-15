# -*- coding: utf-8 -*-
"""
zsign_paires.py — Test Z-sign CIBLÉ sur les 4 paires rapprochées de T1b (corroboration numérique).

Pour chacune des 4 paires (lues dans le rejeu consolider_v17, jamais saisies à la main) :
  1. rejoue le SCAN PRINCIPAL (scan_arb.so, Z_double RS C0+C1) sur une petite fenêtre alignée sur la
     grille du worker (origine = borne basse du segment reconstruit), au pas STEP du log puis STEP/10 ;
  2. raffine les brackets avec illinois_refine_arb (implémentation principale) ;
  3. évalue Z avec mpmath (siegelz) à dps 30 ET dps 50 : signes aux bornes, en 3 points de la paire,
     sur une grille, et racines par bissection indépendante dans chaque bracket ;
  4. compare. Aucune arithmétique d'intervalles : CORROBORATION numérique, pas certification.
     Un changement de signe étaye l'existence d'AU MOINS un zéro ; il ne prouve pas l'unicité.
     L'erreur de Z_double n'est pas bornée dans le code : les écarts Z_double/mpmath mesurés ici
     sont des mesures ponctuelles, pas des bornes.

Usage (un seul cœur, basse priorité) :
  nice -n 19 zeta_env/bin/python3 -B -I scripts_v17/zsign_paires.py <dossier_sortie_neuf>
"""
import ctypes
import json
import math
import os
import sys

sys.dont_write_bytecode = True
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.abspath(os.path.join(ICI, ".."))
import mpmath
from consolider_v17 import reconstruire_segments_v16

OPT = os.path.join(RACINE, "src", "calculs", "optimisation", "c_modules")
DECISIONS = os.path.join(RACINE, "resultats_v17", "p0_rejeu_t1b_20261015", "A_stricte_sans_STEP", "decisions.jsonl")
LOG = os.path.join(RACINE, "calculs", "v16_T4900000_4986000_T1b", "execution_v16_T4986000_T1b.log")
STEP = 0.00031462869333808346       # valeur du log T1b (vérifiée dans rejeu_t1b)
TOL_ARB, MAX_ITER = 1e-12, 50


def charger_libs():
    scan = ctypes.CDLL(os.path.join(OPT, "scan_arb.so"))
    scan.scan_zeros_arb.restype = ctypes.c_int
    P = ctypes.POINTER(ctypes.c_double)
    scan.scan_zeros_arb.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, P, P, P, P, ctypes.c_int]
    ill = ctypes.CDLL(os.path.join(OPT, "illinois_arb.so"))
    ill.illinois_refine_arb.restype = ctypes.c_double
    ill.illinois_refine_arb.argtypes = [ctypes.c_double] * 4 + [ctypes.c_double, ctypes.c_int]
    return scan, ill


def scan_fenetre(scan, t_min, t_max, step, nmax=5000):
    a, b, fa, fb = ((ctypes.c_double * nmax)() for _ in range(4))
    n = scan.scan_zeros_arb(t_min, t_max, step, a, b, fa, fb, nmax)
    return [(a[i], b[i], fa[i], fb[i]) for i in range(n)]


def signe(x):
    return "+" if x > 0 else ("-" if x < 0 else "0")


def Z_mp(t, dps):
    mpmath.mp.dps = dps
    return mpmath.siegelz(mpmath.mpf(t))


def bissection_mp(a, b, dps, nit=45):
    """Bissection mpmath dans [a,b] ; exige un changement de signe de Z à dps donné."""
    mpmath.mp.dps = dps
    lo, hi = mpmath.mpf(a), mpmath.mpf(b)
    zl, zh = mpmath.siegelz(lo), mpmath.siegelz(hi)
    if zl * zh >= 0:
        return None
    for _ in range(nit):
        mid = (lo + hi) / 2
        zm = mpmath.siegelz(mid)
        if zl * zm <= 0:
            hi, zh = mid, zm
        else:
            lo, zl = mid, zm
    return (lo + hi) / 2, hi - lo


def main(sortie):
    if os.path.exists(sortie) and os.listdir(sortie):
        sys.exit(f"Dossier de sortie non vide : {sortie}")
    if not os.path.abspath(sortie).startswith(os.path.join(RACINE, "resultats_v17") + os.sep):
        sys.exit("La sortie doit être sous resultats_v17/")
    os.makedirs(sortie, exist_ok=True)
    segs = reconstruire_segments_v16(4900000.0, 4986000.0, 8, 0.5)
    scan, ill = charger_libs()
    paires = []
    for l in open(DECISIONS):
        d = json.loads(l)
        if d["type_groupe"] == "paire_proche":
            paires.append(d)
    out = []
    for d in paires:
        c1, c2 = d["candidats"]
        t1, t2, w = float(c1["t"]), float(c2["t"]), c1["worker"]
        lo = segs[w][0]
        k0 = math.floor((t1 - lo) / STEP) - 6
        tmin = lo + k0 * STEP
        tmax = t2 + 6 * STEP
        r = {"groupe": d["groupe"], "worker": w, "lignes": [c1["ligne"], c2["ligne"]], "t1": t1, "t2": t2,
             "ecart": t2 - t1, "ecart_en_pas": (t2 - t1) / STEP, "fenetre": [tmin, tmax],
             "origine_grille_reconstruite": lo}
        # (1) scan principal : pas STEP et STEP/10
        br = scan_fenetre(scan, tmin, tmax, STEP)
        br10 = scan_fenetre(scan, tmin, tmax, STEP / 10)
        r["brackets_STEP"] = br
        r["n_brackets_STEP"], r["n_brackets_STEP_sur_10"] = len(br), len(br10)
        r["brackets_STEP_sur_10"] = br10
        # (2) raffinement par l'implémentation principale
        r["racines_principal"] = [ill.illinois_refine_arb(a, b, fa, fb, TOL_ARB, MAX_ITER) for a, b, fa, fb in br]
        r["distance_aux_candidats"] = [min(abs(x - t1), abs(x - t2)) for x in r["racines_principal"]]
        # (3) mpmath dps 30 et 50
        r["mpmath"] = {}
        for dps in (30, 50):
            M = {}
            M["Z(t1)"], M["Z(t2)"] = str(Z_mp(t1, dps)), str(Z_mp(t2, dps))
            tm = (t1 + t2) / 2
            M["Z(milieu)"] = str(Z_mp(tm, dps))
            M["abs_Z_milieu_float"] = float(abs(Z_mp(tm, dps)))
            M["signes_bornes"] = [(signe(Z_mp(a, dps)), signe(Z_mp(b, dps)),
                                   signe(fa), signe(fb)) for a, b, fa, fb in br]   # (mp_a, mp_b, Zdouble_a, Zdouble_b)
            M["ecart_Zdouble_vs_mp_aux_bornes"] = [(float(Z_double_f - Z_mp(pt, dps)))
                                                    for a, b, fa, fb in br
                                                    for pt, Z_double_f in ((a, fa), (b, fb))]
            grille = [tmin + k * STEP for k in range(int((tmax - tmin) / STEP) + 1)]
            sg = [signe(Z_mp(t, dps)) for t in grille]
            M["grille_pas"] = len(grille)
            M["signes_grille"] = "".join(sg)
            M["changements_grille"] = sum(1 for x, y in zip(sg, sg[1:]) if x != y)
            M["racines_independantes"] = []
            for a, b, fa, fb in br:
                res = bissection_mp(a, b, dps)
                M["racines_independantes"].append(None if res is None else
                                                  {"racine": str(res[0]), "largeur_finale": float(res[1])})
            r["mpmath"][str(dps)] = M
        # stabilité des signes entre dps
        r["signes_stables_30_50"] = (r["mpmath"]["30"]["signes_bornes"] == r["mpmath"]["50"]["signes_bornes"]
                                     and r["mpmath"]["30"]["signes_grille"] == r["mpmath"]["50"]["signes_grille"])
        out.append(r)
        print(f"{d['groupe']} w{w} écart={r['ecart']:.6e} ({r['ecart_en_pas']:.1f} pas) brackets STEP={r['n_brackets_STEP']} "
              f"STEP/10={r['n_brackets_STEP_sur_10']} chang.grille mp30/50="
              f"{r['mpmath']['30']['changements_grille']}/{r['mpmath']['50']['changements_grille']} "
              f"|Z(milieu)|={r['mpmath']['50']['abs_Z_milieu_float']:.3e} stable={r['signes_stables_30_50']}", flush=True)
    with open(os.path.join(sortie, "zsign_paires.json"), "w") as f:
        json.dump({"step": STEP, "mpmath_version": mpmath.__version__, "paires": out}, f, indent=1,
                  ensure_ascii=False, default=str)
    return out


if __name__ == "__main__":
    main(sys.argv[1])
