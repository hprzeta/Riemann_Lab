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

#endif /* ILLINOIS_MPFR_H */
