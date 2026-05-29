/* illinois_mpfr.h — signature publique de illinois_mpfr()
 * Interface ctypes Python : cette signature est IMMUABLE
 * Phase C — Riemann_Lab / hprzeta */

#ifndef ILLINOIS_MPFR_H
#define ILLINOIS_MPFR_H

#include <mpfr.h>

/* Précision interne : 170 bits ≈ 51 décimales significatives
 * Cohérent avec 50 dps de mpmath (référence Python) */
#define PREC      170
#define MAX_ITER  100
#define TOL_DEFAULT 1e-12

/* Signature IMMUABLE — l'interface ctypes en dépend directement
 * Entrée  : a_d, b_d tels que Z(a)*Z(b) < 0 (changement de signe détecté)
 * Entrée  : tol — tolérance d'arrêt sur |b−a|
 * Sortie  : partie imaginaire du zéro affiné (double, ~12 décimales utiles) */
double illinois_mpfr(double a_d, double b_d, double tol);

/* Évalue Z_mpfr(t) en un point t et retourne le résultat en double.
 * Usage : validation externe de la convergence Illinois (test_illinois.py).
 * Permet de vérifier |Z_mpfr(résultat)| plutôt que |Z_double(résultat)|. */
double Z_mpfr_eval(double t_d);

/* ── Voie B — callback Python/C ──────────────────────────────────────────
 *
 * Problème : Z_mpfr (RS + C0+C1) a un biais structurel ~1e-3 pour t < 300
 *            → Illinois converge vers un "pseudo-zéro RS", pas le vrai zéro.
 * Solution : permettre à Python de passer sa propre fonction Z(t) = mpmath.siegelz
 *            via un pointeur de fonction C.
 *
 * Type du callback : double (*z_func_t)(double t)
 *   → compatible ctypes.CFUNCTYPE(c_double, c_double) côté Python
 *   → Python gère le GIL automatiquement (appel synchrone, même thread) */
typedef double (*z_func_t)(double t);

/* illinois_mpfr_cb — Illinois en double avec callback Z(t) fourni par Python
 *
 * Entrée : a_d, b_d — intervalle avec changement de signe pour zfunc
 * Entrée : tol      — tolérance sur |b−a| (typiquement 1e-12)
 * Entrée : zfunc    — pointeur vers float(mpmath.siegelz(t)) côté Python
 * Sortie : double — partie imaginaire du vrai zéro, précision ~1e-14
 *
 * Avantage vs illinois_mpfr : biais RS éliminé, converge vers les vrais zéros
 * Coût    : N appels Python (~35 dps) au lieu de N appels C (RS interne)
 * Usage   : illinois_pyZ.py → illinois_c_exact(a, b, tol) */
double illinois_mpfr_cb(double a_d, double b_d, double tol, z_func_t zfunc);

#endif /* ILLINOIS_MPFR_H */
