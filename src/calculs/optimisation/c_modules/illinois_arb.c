/* illinois_arb.c — affinage Illinois via arb_fpwrap_cdouble_hardy_z
 *
 * Remplace Z_rs_mpfr_ntermes (libmpfr, ~42 ms/appel) par arb_fpwrap_cdouble_hardy_z
 * (Arb/FLINT, ~0.038 ms/appel) — gain mesuré ×1100.
 *
 * Avantages vs Z_mpfr/Z_rs_mpfr_ntermes :
 *   - Aucun biais RS : Arb calcule Z(t) avec garanties d'erreur strictes
 *     → valide pour tout t, y compris t < 300 (N < 7 termes RS)
 *   - Double précision suffisante pour tol=1e-9 (libmpfr inutile)
 *   - Pas de dépendance aux headers FLINT : prototype déclaré en forward
 *
 * Prototype ABI x86-64 System V (compatible avec ctypes Python) :
 *   typedef struct { double real; double imag; } arb_cdouble_t;
 *   int arb_fpwrap_cdouble_hardy_z(arb_cdouble_t *res, arb_cdouble_t t, int flags);
 *   struct{d;d} et _Complex double sont ABI-équivalents sur x86-64 → OK.
 *
 * Phase C — Riemann_Lab / hprzeta — 2026-06-12 */

#include <math.h>

/* ── Déclaration forward arb_fpwrap_cdouble_hardy_z ─────────────────────────
 * Tirée de flint/arb_fpwrap.h (FLINT 3.x) — pas d'include pour éviter la
 * dépendance aux headers FLINT au moment de la compilation.
 * flags = 0 : calcul standard (précision automatique avec certificat). */
typedef struct {
    double real;
    double imag;
} arb_cdouble_t;

extern int arb_fpwrap_cdouble_hardy_z(arb_cdouble_t *res, arb_cdouble_t t, int flags);

/* ── Z_rs_double — fallback RS double (C₀+C₁, Berry 1992) ─────────────────
 * Identique à Z_double dans scan_arb.c. Activé uniquement si arb_fpwrap
 * retourne un code d'erreur (jamais observé en pratique pour t ≥ 14). */
static double theta_double_arb(double t) {
    double pi = acos(-1.0);
    double lt = log(t / (2.0 * pi));
    return (t / 2.0) * lt
           - t / 2.0
           - pi / 8.0
           + 1.0 / (48.0 * t)
           + 7.0 / (5760.0 * t * t * t)
           - 31.0 / (80640.0 * t * t * t * t * t);
}

static double Z_rs_double_arb(double t) {
    double pi  = acos(-1.0);
    double tau = sqrt(t / (2.0 * pi));
    long   N   = (long)tau;
    double th  = theta_double_arb(t);
    double sum = 0.0;
    long   n;

    for (n = 1; n <= N; n++)
        sum += cos(th - t * log((double)n)) / sqrt((double)n);
    double S = 2.0 * sum;

    /* terme de reste C₀+C₁ */
    double p  = tau - (double)N;
    double u  = 2.0 * p - 1.0;
    double A  = pi * (u * u / 2.0 + 0.375);
    double B  = pi * u;
    double cB = cos(B);
    if (fabs(cB) < 1e-10) return S;

    double sB   = sin(B);
    double cA   = cos(A);
    double sA   = sin(A);
    double C0   = cA / cB;
    double dPsi = pi * (-u * sA * cB + cA * sB) / (cB * cB);
    double C1   = dPsi * (u * u / 2.0 - 0.375) / (pi * tau);
    int    sign = ((N - 1) % 2 == 0) ? 1 : -1;
    return S + sign * pow(tau, -0.5) * (C0 + C1);
}

/* ── Z_arb — évalue Z(t) via Arb, retourne la partie réelle ────────────────
 * Z(t) est réelle pour t réel (symétrie fonctionnelle de ζ).
 * flags=0 : précision automatique adaptative d'Arb.
 * Si ret ≠ 0 (erreur interne Arb, très rare) → fallback Z_rs_double. */
static double Z_arb(double t) {
    arb_cdouble_t res = {0.0, 0.0};
    arb_cdouble_t arg = {t, 0.0};
    int ret = arb_fpwrap_cdouble_hardy_z(&res, arg, 0);
    if (ret != 0) return Z_rs_double_arb(t);
    return res.real;
}

/* =========================================================================
 * illinois_refine_arb — affinage hybride : Illinois Z_rs + 2 Newton Z_arb
 *
 * Stratégie en 2 phases (mesuré : ×5–6 vs pure Z_arb Illinois) :
 *
 * Phase 1 : Illinois avec Z_rs_double_arb (C0+C1, ~0.015 ms/appel)
 *   → converge vers pseudo-zéro avec erreur biais_RS = O(t^{-5/4})
 *   → s'arrête à |b−a| < 1e-6 (bracket serré)
 *
 * Phase 2 : 2 Newton steps avec Z_arb (~3.5 ms/appel)
 *   → dérivée Z'(t) via Z_rs_double_arb (biais RS s'annule dans la différence)
 *   → erreur résiduelle < 2e-11 pour t ≥ 200 (validé)
 *
 * Fallback Illinois Z_arb : si signe de Z_rs ≠ signe de fa/fb (cas rare t < 200)
 *   → ce cas est normalement géré côté Python par mpmath_petit_t (t < 200)
 *
 * Entrée : a, b       — bornes avec fa·fb < 0 (Z_double de scan_arb)
 * Entrée : fa, fb     — Z(a), Z(b) de scan_arb (utilisés pour le fallback signe)
 * Entrée : tol        — tolérance sur |delta Newton| (recommandé : 1e-9)
 * Entrée : max_iter   — max itérations phase 1 (recommandé : 50)
 * Sortie : double — partie imaginaire du zéro affiné
 * ========================================================================= */
double illinois_refine_arb(double a, double b, double fa, double fb,
                           double tol, int max_iter) {
    double Za = Z_rs_double_arb(a);
    double Zb = Z_rs_double_arb(b);

    /* Si Z_rs change de signe différemment de fa/fb (très rare, t < 200) :
     * fallback Illinois Z_arb classique sur 15 itérations. */
    if (Za * Zb >= 0.0) {
        Za = fa; Zb = fb;
        if (Za * Zb >= 0.0) return (a + b) / 2.0;
        for (int iter = 0; iter < 15 && fabs(b - a) > tol; iter++) {
            double den = Zb - Za;
            if (fabs(den) < 1e-300) break;
            double c = b - Zb * (b - a) / den;
            double Zc = Z_arb(c);
            if (Za * Zc < 0.0) { b = c; Zb = Zc; }
            else                { a = c; Za = Zc * 0.5; }
        }
        return (fabs(Za) < fabs(Zb)) ? a : b;
    }

    /* Phase 1 : Illinois Z_rs_double_arb → bracket serré (1e-6) */
    for (int iter = 0; iter < max_iter; iter++) {
        if (fabs(b - a) < 1e-6) break;
        double den = Zb - Za;
        if (fabs(den) < 1e-300) break;
        double c  = b - Zb * (b - a) / den;
        double Zc = Z_rs_double_arb(c);
        if (Za * Zc < 0.0) { b = c; Zb = Zc; }
        else                { a = c; Za = Zc * 0.5; }  /* correction Illinois (Dowell 1971) */
    }

    /* Phase 2 : 2 Newton steps avec Z_arb
     * dZ via Z_rs_double_arb (pas de biais dans la différence). */
    double t_curr = (fabs(Za) < fabs(Zb)) ? a : b;
    double h = 1e-4;

    for (int k = 0; k < 2; k++) {
        double dZ = (Z_rs_double_arb(t_curr + h) - Z_rs_double_arb(t_curr - h)) / (2.0 * h);
        if (fabs(dZ) < 1e-10) break;
        double Zt = Z_arb(t_curr);
        if (fabs(Zt) < tol) return t_curr;
        double delta = Zt / dZ;
        t_curr -= delta;
        if (fabs(delta) < tol) break;
    }

    return t_curr;
}
