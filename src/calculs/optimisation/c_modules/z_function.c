/* z_function.c — theta(t) Stirling + Z(t) Riemann-Siegel + correction C0+C1
 * Usage : detection des changements de signe (balayage) — doit etre
 * IDENTIQUE a Z_mpfr pour que les intervalles soient coherents avec Illinois.
 * Phase C — Riemann_Lab / hprzeta — 2026-05-24 */

#include <math.h>
#include "z_function.h"

/* theta(t) — asymptotique de Stirling jusqu'a 1/t^3
 * Valide pour t >= 20 (Abramowitz & Stegun 6.1.40) */
static double theta_double(double t) {
    double pi = acos(-1.0);
    double lt = log(t / (2.0 * pi));
    return (t / 2.0) * lt
         - t / 2.0
         - pi / 8.0
         + 1.0 / (48.0 * t)
         + 7.0 / (5760.0 * t * t * t);
}

/* Z(t) — formule de Riemann-Siegel + correction RS (C0+C1, Berry 1992)
 *
 * Somme principale : 2 * Sum_{n=1}^{N} cos(theta(t) - t*ln n) / sqrt(n)
 *   N = floor(sqrt(t/2pi))
 *
 * Terme de reste (correction C0+C1) :
 *   tau = sqrt(t/2pi),  u = 2*(tau-N)-1
 *   Psi(u)  = cos(pi*(u^2/2+3/8)) / cos(pi*u)
 *   Psi'(u) = pi*[-u*sin(A)*cos(B) + cos(A)*sin(B)] / cos^2(B)
 *   R = (-1)^{N-1} * tau^{-1/2} * (Psi(u) + Psi'(u)*(u^2/2-3/8)/(pi*tau))
 *
 * IMPORTANT : cette formule est IDENTIQUE a celle de Z_mpfr (illinois_mpfr.c).
 * Les deux doivent rester coherentes pour que Illinois converge correctement. */
double Z_double(double t) {
    double pi  = acos(-1.0);
    double tau = sqrt(t / (2.0 * pi));
    long   N   = (long) tau;
    double th  = theta_double(t);
    double sum = 0.0;

    for (long n = 1; n <= N; n++) {
        sum += cos(th - t * log((double)n)) / sqrt((double)n);
    }
    double S = 2.0 * sum;

    /* correction C0+C1 — terme de reste de la formule RS */
    double p  = tau - (double)N;
    double u  = 2.0 * p - 1.0;
    double A  = pi * (u * u / 2.0 + 0.375);
    double B  = pi * u;
    double cB = cos(B);

    if (fabs(cB) < 1e-10) return S;   /* evite la division par zero */

    double sB    = sin(B);
    double cA    = cos(A);
    double sA    = sin(A);
    double C0    = cA / cB;
    double dPsi  = pi * (-u * sA * cB + cA * sB) / (cB * cB);
    double C1    = dPsi * (u * u / 2.0 - 0.375) / (pi * tau);
    double signe = ((N - 1) % 2 == 0) ? 1.0 : -1.0;

    return S + signe * pow(tau, -0.5) * (C0 + C1);
}
