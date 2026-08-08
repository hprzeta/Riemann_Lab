/* illinois_arb_lowprec.c — variante expérimentale de illinois_refine_arb
 *
 * Différence avec illinois_arb.c (production, NE PAS MODIFIER) :
 *   Phase 2 utilise acb_dirichlet_hardy_z directement, à precision FIXE
 *   (prec_bits passé en paramètre, un seul calcul, pas de boucle d'escalade),
 *   au lieu de arb_fpwrap_cdouble_hardy_z (flags=0) qui vise systématiquement
 *   une précision certifiée ~1e-16 (escalade 64->128->...->8192 bits).
 *
 * Objectif : mesurer si le fait de ne cibler que ~1e-12 (au lieu de ~1e-16)
 * réduit le coût mesuré par perf record (91% du temps dans GMP+FLINT).
 *
 * Nécessite les headers FLINT 3.3.1 (récupérés en source, PAS via apt qui
 * n'a que 3.0.1 — ABI dirichlet_group_t/dirichlet_char_t incompatible).
 * Phase C — Riemann_Lab / hprzeta — expérimental, 08/08/2026 */

#include <math.h>
#include <stdio.h>
#include "flint.h"
#include "acb.h"
#include "acb_dirichlet.h"
#include "dirichlet.h"

#define PI 3.14159265358979323846
#define N_MAX_CACHE 2100
#define SEUIL_1NEWTON 20000.0

/* ── cache log(n)/1/sqrt(n) — identique à illinois_arb.c (Phase 1) ────────── */
static double log_n_cache[N_MAX_CACHE + 1];
static double isqrt_n_cache[N_MAX_CACHE + 1];
static int    g_cache_ready = 0;

static void init_rs_cache(void) {
    if (g_cache_ready) return;
    int n;
    for (n = 1; n <= N_MAX_CACHE; n++) {
        log_n_cache[n]   = log((double)n);
        isqrt_n_cache[n] = 1.0 / sqrt((double)n);
    }
    g_cache_ready = 1;
}

/* ── groupe/caractère Dirichlet trivial (q=1) — zêta pure ───────────────────
 * Initialisé une fois par worker (fork), comme le cache RS. */
static dirichlet_group_t g_G;
static dirichlet_char_t  g_chi;
static int g_dirichlet_ready = 0;

static void init_dirichlet_trivial(void) {
    if (g_dirichlet_ready) return;
    dirichlet_group_init(g_G, 1);
    dirichlet_char_init(g_chi, g_G);
    dirichlet_char_index(g_chi, g_G, 0);   /* caractère principal mod 1 */
    g_dirichlet_ready = 1;
}

/* ── stubs debug log — identiques à illinois_arb.c, présents pour que
 * compute_zeros_v15_test_lowprec.py (copie quasi à l'identique du worker
 * de production) puisse binder ces symboles sans crasher, même si le
 * logging n'est pas exercé pendant ce test (ZETA_DEBUG_BRACKETS non défini). */
static FILE *g_arb_log = NULL;

void arb_set_debug_log(const char *path) {
    if (g_arb_log) { fclose(g_arb_log); g_arb_log = NULL; }
    if (path && path[0]) g_arb_log = fopen(path, "a");
}

void arb_close_debug_log(void) {
    if (g_arb_log) { fflush(g_arb_log); fclose(g_arb_log); g_arb_log = NULL; }
}

static double theta_rs(double t) {
    double lt = log(t / (2.0 * PI));
    return (t / 2.0) * lt - t / 2.0 - PI / 8.0
           + 1.0 / (48.0 * t) + 7.0 / (5760.0 * t * t * t)
           - 31.0 / (80640.0 * t * t * t * t * t);
}

static double Z_rs_double(double t) {
    double tau = sqrt(t / (2.0 * PI));
    long   N   = (long)tau;
    double th  = theta_rs(t);
    double sum = 0.0;
    long   n;

    if (N <= N_MAX_CACHE) {
        for (n = 1; n <= N; n++)
            sum += cos(th - t * log_n_cache[n]) * isqrt_n_cache[n];
    } else {
        for (n = 1; n <= N; n++)
            sum += cos(th - t * log((double)n)) / sqrt((double)n);
    }
    double S = 2.0 * sum;

    double p  = tau - (double)N;
    double u  = 2.0 * p - 1.0;
    double A  = PI * (u * u / 2.0 + 0.375);
    double B  = PI * u;
    double cB = cos(B);
    if (fabs(cB) < 1e-10) return S;

    double sB   = sin(B);
    double cA   = cos(A);
    double sA   = sin(A);
    double C0   = cA / cB;
    double dPsi = PI * (-u * sA * cB + cA * sB) / (cB * cB);
    double C1   = dPsi * (u * u / 2.0 - 0.375) / (PI * tau);
    int    sign = ((N - 1) % 2 == 0) ? 1 : -1;
    return S + sign * pow(tau, -0.5) * (C0 + C1);
}

/* ── Z_arb_lowprec — acb_dirichlet_hardy_z, UN SEUL calcul à prec_bits fixe ── */
double Z_arb_lowprec(double t, int prec_bits) {
    init_dirichlet_trivial();

    acb_t s, res;
    acb_init(s);
    acb_init(res);
    acb_set_d(s, t);

    acb_dirichlet_hardy_z(res, s, g_G, g_chi, 1, (slong)prec_bits);
    double result = arf_get_d(arb_midref(acb_realref(res)), ARF_RND_NEAR);

    acb_clear(s);
    acb_clear(res);
    return result;
}

/* ── illinois_refine_arb_lowprec — même architecture 2-phases que la
 * production (illinois_arb.c), Phase 2 utilise Z_arb_lowprec au lieu de
 * Z_arb (arb_fpwrap). prec_bits exposé en paramètre pour balayer plusieurs
 * valeurs sans recompiler. ────────────────────────────────────────────── */
double illinois_refine_arb_lowprec(double a, double b, double fa, double fb,
                                   double tol, int max_iter, int prec_bits) {
    init_rs_cache();

    double Za = Z_rs_double(a);
    double Zb = Z_rs_double(b);

    if (Za * Zb >= 0.0) {
        Za = fa; Zb = fb;
        if (Za * Zb >= 0.0) return (a + b) / 2.0;
        for (int iter = 0; iter < 15 && fabs(b - a) > tol; iter++) {
            double den = Zb - Za;
            if (fabs(den) < 1e-300) break;
            double c = b - Zb * (b - a) / den;
            double Zc = Z_arb_lowprec(c, prec_bits);
            if (Za * Zc < 0.0) { b = c; Zb = Zc; }
            else                { a = c; Za = Zc * 0.5; }
        }
        return (fabs(Za) < fabs(Zb)) ? a : b;
    }

    for (int iter = 0; iter < max_iter; iter++) {
        if (fabs(b - a) < 1e-6) break;
        double den = Zb - Za;
        if (fabs(den) < 1e-300) break;
        double c  = b - Zb * (b - a) / den;
        double Zc = Z_rs_double(c);
        if (Za * Zc < 0.0) { b = c; Zb = Zc; }
        else                { a = c; Za = Zc * 0.5; }
    }

    double t_curr   = (fabs(Za) < fabs(Zb)) ? a : b;
    double h        = 1e-4;
    int    n_newton = (t_curr < SEUIL_1NEWTON) ? 2 : 1;

    for (int k = 0; k < n_newton; k++) {
        double dZ = (Z_rs_double(t_curr + h) - Z_rs_double(t_curr - h)) / (2.0 * h);
        if (fabs(dZ) < 1e-10) break;
        double Zt = Z_arb_lowprec(t_curr, prec_bits);
        if (fabs(Zt) < tol) return t_curr;
        double delta = Zt / dZ;
        t_curr -= delta;
        if (fabs(delta) < tol) break;
    }

    return t_curr;
}
