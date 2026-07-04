/* scan_arb.c — Détection C pure des changements de signe de Z(t)
 * via formule Riemann-Siegel C0+C1 en double précision
 *
 * v14 (2026-07-04) — 2 optimisations vs v13 :
 *   1. Cache statique log_n_cache + isqrt_n_cache : évite log(n) et 1/sqrt(n)
 *      à chaque évaluation Z_rs_double → gain ×1.3-2 sur le scan.
 *   2. Constante PI explicite (évite acos(-1.0) répété).
 *
 * Pourquoi Z_double et non arb_fpwrap :
 *   arb_fpwrap_cdouble_hardy_z = 175 µs/point (calcul avec garanties)
 *   Z_double = ~1-2 µs/point (RS double, suffisant pour la détection de signes)
 *   Scan en masse : Z_double est 90-175× plus rapide.
 *
 * Phase C — Riemann_Lab / hprzeta — 2026-07-04 */

#include <math.h>
#include <stdio.h>

/* ── Constante π ─────────────────────────────────────────────────────────── */
#define PI 3.14159265358979323846

/* ── Cache log(n) et 1/sqrt(n) — initialisé une fois par worker ──────────────
 * Couvre jusqu'à T≈27M (N_RS=2100 termes). 33 KB, tient en L2 cache.
 * Multiprocessing (fork) : chaque worker a sa propre copie → pas de race. */
#define N_MAX_CACHE 2100

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

/* ── Log de débogage ─────────────────────────────────────────────────────── */
static FILE *g_scan_log = NULL;

void scan_set_debug_log(const char *path) {
    if (g_scan_log) { fclose(g_scan_log); g_scan_log = NULL; }
    if (path && path[0]) g_scan_log = fopen(path, "a");
}

void scan_close_debug_log(void) {
    if (g_scan_log) { fflush(g_scan_log); fclose(g_scan_log); g_scan_log = NULL; }
}

/* ── θ(t) asymptotique Stirling (valide t ≥ 20) ─────────────────────────── */
static double theta_double(double t) {
    double lt = log(t / (2.0 * PI));
    return (t / 2.0) * lt
         - t / 2.0
         - PI / 8.0
         + 1.0 / (48.0 * t)
         + 7.0 / (5760.0 * t * t * t)
         - 31.0 / (80640.0 * t * t * t * t * t);
}

/* ── Z(t) RS C0+C1 avec cache log_n/isqrt_n ─────────────────────────────────
 * Cache obligatoire : init_rs_cache() doit avoir été appelé avant. */
static double Z_double(double t) {
    double tau = sqrt(t / (2.0 * PI));
    long   N   = (long) tau;
    double th  = theta_double(t);
    double sum = 0.0;
    long   n;

    /* boucle RS : lecture tableau au lieu de log()/sqrt() à chaque terme */
    if (N <= N_MAX_CACHE) {
        for (n = 1; n <= N; n++)
            sum += cos(th - t * log_n_cache[n]) * isqrt_n_cache[n];
    } else {
        /* fallback sans cache si t > ~27M */
        for (n = 1; n <= N; n++)
            sum += cos(th - t * log((double)n)) / sqrt((double)n);
    }
    double S = 2.0 * sum;

    /* correction C0+C1 (Berry 1992) */
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

/* ============================================================
 * scan_zeros_arb — détecte tous les crochets [a,b] où Z(a)·Z(b) < 0
 *
 * Paramètres
 *   t_min, t_max   — intervalle de scan
 *   step           — pas adaptatif (voir _step_adaptatif() Python)
 *   brackets_a/b   — sortie : bornes gauches/droites
 *   fa, fb         — sortie : Z(a) et Z(b) (réutilisés par illinois_refine)
 *   max_brackets   — taille des buffers de sortie (dynamique depuis v13)
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
    /* init cache une fois par worker (idempotent) */
    init_rs_cache();

    int    n = 0;
    long   k = 0;         /* compteur d'itérations (pas de dérive cumulative) */
    double t_prev = t_min;
    double z_prev, z_curr;

    /* point de départ */
    z_prev = Z_double(t_min);

    /* balayage pas à pas — t recalculé depuis t_min à chaque itération
     * (évite l'accumulation d'erreurs d'arrondi sur t += step). */
    while (t_min + (double)(k + 1) * step <= t_max && n < max_brackets) {
        k++;
        double t_curr = t_min + (double)k * step;
        z_curr = Z_double(t_curr);

        if (z_prev * z_curr < 0.0) {
            brackets_a[n] = t_prev;
            brackets_b[n] = t_curr;
            fa[n]         = z_prev;
            fb[n]         = z_curr;
            if (g_scan_log)
                fprintf(g_scan_log, "BRACKET %.15f %.15f %.10f %.10f\n",
                        t_prev, t_curr, z_prev, z_curr);
            n++;
        }
        z_prev = z_curr;
        t_prev = t_curr;
    }
    return n;
}
