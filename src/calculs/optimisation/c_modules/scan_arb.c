/* scan_arb.c — Détection C pure des changements de signe de Z(t)
 * via formule Riemann-Siegel C0+C1 en double précision
 *
 * Pourquoi Z_double et non arb_fpwrap :
 *   arb_fpwrap_cdouble_hardy_z = 175 μs/point (calcul avec garanties d'erreur)
 *   Z_double = ~2 μs/point (RS double, suffisant pour la détection de signes)
 *   Pour la détection en masse (500k pts/run), Z_double est 30-90× plus rapide.
 *
 * Avantages vs Z_vect_correct Python :
 *   - Élimine la boucle Python "reste RS" (102 appels Python → 4 appels C)
 *   - ~3-5× plus rapide que numpy vectorisé pour le scan pur
 *   - fa/fb précalculés → illinois_refine Option B sans recalcul Python
 *
 * RÈGLE ABSOLUE : step ≤ 0.010 (gap minimum mesuré = 0.019 à t=66678)
 *
 * Phase C — Riemann_Lab / hprzeta — 2026-06-10 */

#include <math.h>

/* ============================================================
 * theta(t) — asymptotique de Stirling jusqu'à 1/t^5
 * Valide pour t ≥ 20 (Abramowitz & Stegun 6.1.40)
 * Identique à theta_double() dans z_function.c
 * ============================================================ */
static double theta_double(double t) {
    double pi = acos(-1.0);
    double lt = log(t / (2.0 * pi));
    return (t / 2.0) * lt
         - t / 2.0
         - pi / 8.0
         + 1.0 / (48.0 * t)
         + 7.0 / (5760.0 * t * t * t)
         - 31.0 / (80640.0 * t * t * t * t * t);
}

/* ============================================================
 * Z(t) — formule de Riemann-Siegel + correction RS (C0+C1, Berry 1992)
 *   N = floor(sqrt(t/2π))
 *   Terme de reste : C0 + C1 en double précision
 * Identique à Z_double() dans z_function.c
 * ============================================================ */
static double Z_double(double t) {
    double pi  = acos(-1.0);
    double tau = sqrt(t / (2.0 * pi));
    long   N   = (long) tau;
    double th  = theta_double(t);
    double sum = 0.0;
    long   n;

    for (n = 1; n <= N; n++) {
        sum += cos(th - t * log((double)n)) / sqrt((double)n);
    }
    double S = 2.0 * sum;

    /* correction C0+C1 — terme de reste de la formule RS */
    double p  = tau - (double)N;
    double u  = 2.0 * p - 1.0;
    double A  = pi * (u * u / 2.0 + 0.375);
    double B  = pi * u;
    double cB = cos(B);

    if (fabs(cB) < 1e-10) return S;   /* évite la division par zéro */

    double sB   = sin(B);
    double cA   = cos(A);
    double sA   = sin(A);
    double C0   = cA / cB;
    double dPsi = pi * (-u * sA * cB + cA * sB) / (cB * cB);
    double C1   = dPsi * (u * u / 2.0 - 0.375) / (pi * tau);
    int    sign = ((N - 1) % 2 == 0) ? 1 : -1;

    return S + sign * pow(tau, -0.5) * (C0 + C1);
}

/* ============================================================
 * scan_zeros_arb — détecte tous les crochets [a,b] où Z(a)·Z(b) < 0
 *
 * Paramètres
 *   t_min, t_max   — intervalle de scan
 *   step           — pas fixe ≤ 0.010 (gap-safe mesuré)
 *   brackets_a/b   — sortie : bornes gauches/droites
 *   fa, fb         — sortie : Z(a) et Z(b) (pour illinois_refine Option B)
 *   max_brackets   — taille des buffers de sortie
 *
 * Retourne le nombre de crochets trouvés.
 * ============================================================ */
int scan_zeros_arb(
    double  t_min,
    double  t_max,
    double  step,
    double *brackets_a,
    double *brackets_b,
    double *fa,
    double *fb,
    int     max_brackets
) {
    int    n = 0;
    double t = t_min;
    double z_prev, z_curr;

    /* évalue Z(t_min) — point de départ */
    z_prev = Z_double(t_min);

    /* balayage pas à pas — boucle entièrement en C (pas d'overhead Python) */
    while (t + step <= t_max && n < max_brackets) {
        t += step;
        z_curr = Z_double(t);

        if (z_prev * z_curr < 0.0) {
            brackets_a[n] = t - step;   /* borne gauche */
            brackets_b[n] = t;           /* borne droite */
            fa[n]         = z_prev;      /* Z(a) précalculé */
            fb[n]         = z_curr;      /* Z(b) précalculé */
            n++;
        }
        z_prev = z_curr;
    }
    return n;
}
