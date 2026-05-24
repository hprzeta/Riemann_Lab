/* z_function.h — signatures de theta_double() et Z_double()
 * Précision : float64 (double) — pour la détection des changements de signe uniquement
 * Phase C — Riemann_Lab / hprzeta */

#ifndef Z_FUNCTION_H
#define Z_FUNCTION_H

/* Z(t) — formule de Riemann-Siegel en double précision
 * theta_double() est interne à z_function.c (static) — non exposée ici */
double Z_double(double t);

#endif /* Z_FUNCTION_H */
