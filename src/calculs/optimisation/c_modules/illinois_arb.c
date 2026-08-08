/* illinois_arb.c — affinage Illinois via acb_dirichlet_hardy_z (précision fixe)
 *
 * v16 (2026-08-08) — remplacement de Z_arb vs v15 :
 *   arb_fpwrap_cdouble_hardy_z(flags=0) escalade en interne 64→128→...→8192
 *   bits jusqu'à certifier ~1e-16 (confirmé depuis le code source FLINT
 *   3.3.1, src/arb_fpwrap/fpwrap.c) — largement plus que notre besoin réel
 *   (tol=1e-12, ~40 bits). Remplacé par acb_dirichlet_hardy_z appelé à
 *   precision FIXE 64 bits (UN SEUL calcul, pas d'escalade).
 *   Gain mesuré : ×1.98 bout-en-bout sur run réel T=10000 (Turing COMPLET,
 *   LMFDB 20/20, résultats identiques à v15) — voir Handoff.md/JOURNAL.md
 *   wiki, entrée 08/08/2026. 64 bits choisi (coïncide avec WP_INITIAL de
 *   arb_fpwrap, marge ~7 décimales au-dessus des ~40 bits nécessaires).
 *   Nécessite c_modules/flint-headers-3.3.1/ (headers vendorisés en source —
 *   apt libflint-dev = 3.0.1, ABI incompatible avec la .so runtime 3.3.1).
 *
 * v14 (2026-07-04) — optimisation vs v13 :
 *   Cache statique log_n_cache + isqrt_n_cache : évite log(n) et 1/sqrt(n)
 *   à chaque évaluation Z_rs_double — gain ×1.3-2 sur Phase 1 et sur les
 *   appels Z_rs de Phase 2 (dérivée numérique).
 *
 * Note sur Phase 2 (architecture inchangée depuis v13, seul Z_arb change en v16) :
 *   La boucle fait 2 Newton Z_arb avec early-exit si |Zt| < tol.
 *   Pour t > ~50 000 (biais Z_rs < 6e-7) : k=0 suffit → 1 seul Z_arb.
 *   Pour t < 50 000 (biais Z_rs important) : 2 Z_arb nécessaires.
 *   Ne PAS réduire à 1 Newton fixe : échoue pour t ≈ 65-77 (erreur 1e-6).
 *
 * Architecture 2 phases (inchangée depuis v12) :
 *   Phase 1 : Illinois Z_rs (cache, ~0.010 ms/appel) → |b-a| < 1e-6
 *   Phase 2 : 2 Newton Z_arb avec early-exit → erreur < 1e-12
 *
 * Phase C — Riemann_Lab / hprzeta — 2026-08-08 */

#include <math.h>
#include <stdio.h>
#include "flint.h"
#include "acb.h"
#include "acb_dirichlet.h"
#include "dirichlet.h"

/* ── Constante π (évite acos(-1.0) répété à chaque évaluation Z) ─────────── */
#define PI 3.14159265358979323846

/* ── Cache log(n) et 1/sqrt(n) — initialisé une fois par worker ──────────────
 * Couvre jusqu'à T≈27M (N_RS=2100 termes) — 33 KB total, tient en L2 cache.
 * Dans multiprocessing (fork) : chaque worker a sa propre copie → pas de race. */
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

/* ── Log de débogage (activé via arb_set_debug_log) ──────────────────────
 * NULL = désactivé. Chaque worker-fork a sa propre copie → pas de race. */
static FILE *g_arb_log = NULL;

void arb_set_debug_log(const char *path) {
    if (g_arb_log) { fclose(g_arb_log); g_arb_log = NULL; }
    if (path && path[0]) g_arb_log = fopen(path, "a");
}

void arb_close_debug_log(void) {
    if (g_arb_log) { fflush(g_arb_log); fclose(g_arb_log); g_arb_log = NULL; }
}

/* ── Groupe/caractère Dirichlet trivial (q=1) — zêta pure ────────────────────
 * Initialisé une fois par worker (fork), comme le cache RS. acb_dirichlet_
 * hardy_z nécessite ces types même pour la fonction zêta simple (caractère
 * principal mod 1). Pattern confirmé sur le test officiel FLINT
 * acb_dirichlet/test/t-hardy_z.c. */
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

/* Précision fixe Phase 2 — voir en-tête de fichier pour la justification
 * (v16, 08/08/2026). NE PAS baisser sans revalider LMFDB + Turing complet. */
#define PREC_BITS_ARB 64

/* ── θ(t) asymptotique Stirling (valide t ≥ 20) ─────────────────────────── */
static double theta_rs(double t) {
    double lt = log(t / (2.0 * PI));
    return (t / 2.0) * lt
           - t / 2.0
           - PI / 8.0
           + 1.0 / (48.0 * t)
           + 7.0 / (5760.0 * t * t * t)
           - 31.0 / (80640.0 * t * t * t * t * t);
}

/* ── Z_rs_double — formule RS C0+C1 avec cache log_n/isqrt_n ────────────────
 * Cache obligatoire : init_rs_cache() doit avoir été appelé. */
static double Z_rs_double(double t) {
    double tau = sqrt(t / (2.0 * PI));
    long   N   = (long)tau;
    double th  = theta_rs(t);
    double sum = 0.0;
    long   n;

    /* boucle RS avec cache : lecture tableau au lieu de log()/sqrt() */
    if (N <= N_MAX_CACHE) {
        for (n = 1; n <= N; n++)
            sum += cos(th - t * log_n_cache[n]) * isqrt_n_cache[n];
    } else {
        /* fallback sans cache si t dépasse T≈27M (cas théorique) */
        for (n = 1; n <= N; n++)
            sum += cos(th - t * log((double)n)) / sqrt((double)n);
    }
    double S = 2.0 * sum;

    /* correction C0+C1 — terme de reste de la formule RS */
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

/* ── Z_arb — évalue Z(t) via acb_dirichlet_hardy_z à precision fixe (v16) ───
 * UN SEUL calcul à PREC_BITS_ARB bits, pas d'escalade (contrairement à
 * l'ancien arb_fpwrap_cdouble_hardy_z qui visait ~1e-16 en interne). */
static double Z_arb(double t) {
    init_dirichlet_trivial();

    acb_t s, res;
    acb_init(s);
    acb_init(res);
    acb_set_d(s, t);

    acb_dirichlet_hardy_z(res, s, g_G, g_chi, 1, (slong)PREC_BITS_ARB);
    double result = arf_get_d(arb_midref(acb_realref(res)), ARF_RND_NEAR);

    acb_clear(s);
    acb_clear(res);
    return result;
}

/* =========================================================================
 * illinois_refine_arb — affinage hybride : Illinois Z_rs + Newton Z_arb
 *
 * Stratégie en 2 phases (v15 — 2026-07-04) :
 *
 * Phase 1 : Illinois avec Z_rs (cache, ~0.010 ms/appel)
 *   → converge vers pseudo-zéro (erreur biais_RS = O(t^{-5/4}))
 *   → s'arrête à |b−a| < 1e-6
 *
 * Phase 2 : Newton Z_arb adaptatif (~1.8 ms/appel)
 *   → t < SEUIL_1NEWTON : 2 Newton (biais_RS > ~6e-7 → 1 step insuffisant)
 *   → t ≥ SEUIL_1NEWTON : 1 Newton (biais_RS < 6e-7 → quadratique → < tol)
 *   SEUIL_1NEWTON = 20 000 : biais_RS(20k) ≈ 6.4e-7 → erreur ~4e-13 < tol=1e-12.
 *
 * Gain v15 vs v14 : ~87% des zéros T=100k sont à t > 20k → économie 1 Z_arb.
 * Estimation : ×1.77 sur Illinois → T=100k 7.7 → ~4.3 min.
 *
 * Fallback Illinois Z_arb : si signe Z_rs ≠ fa/fb (rare, t < 65)
 *
 * Entrée : a, b       — bornes avec fa·fb < 0 (Z_rs de scan_arb)
 * Entrée : fa, fb     — Z(a), Z(b) de scan_arb
 * Entrée : tol        — tolérance (recommandé : 1e-12)
 * Entrée : max_iter   — max itérations Phase 1 (recommandé : 50)
 * Sortie : double — position du zéro affiné
 * ========================================================================= */

/* Seuil d'activation du mode 1 Newton :
 * biais_RS(t) = C × t^{-5/4}, C ≈ 0.305 (calibré sur LMFDB 04/07/2026).
 * Erreur après 1 Newton ≈ biais² → < tol=1e-12 pour t ≥ ~50 000 (strict).
 * SEUIL_1NEWTON = 20 000 : erreur estimée 4e-13 (marge ×2.4 sur tol). */
#define SEUIL_1NEWTON 20000.0

double illinois_refine_arb(double a, double b, double fa, double fb,
                           double tol, int max_iter) {
    /* init cache au premier appel de ce worker */
    init_rs_cache();

    double Za = Z_rs_double(a);
    double Zb = Z_rs_double(b);

    /* Si Z_rs ne voit pas le changement de signe (rare, t < 65) :
     * fallback Illinois Z_arb sur 15 itérations. */
    if (Za * Zb >= 0.0) {
        if (g_arb_log)
            fprintf(g_arb_log, "FALLBACK_ZRS %.15f %.15f fa=%.10f fb=%.10f Za=%.10f Zb=%.10f\n",
                    a, b, fa, fb, Za, Zb);
        Za = fa; Zb = fb;
        if (Za * Zb >= 0.0) {
            if (g_arb_log)
                fprintf(g_arb_log, "REJECT %.15f %.15f fa=%.10f fb=%.10f Za_orig=%.10f Zb_orig=%.10f\n",
                        a, b, fa, fb, Z_rs_double(a), Z_rs_double(b));
            return (a + b) / 2.0;
        }
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

    /* Phase 1 : Illinois Z_rs (cache) → bracket serré (1e-6) */
    for (int iter = 0; iter < max_iter; iter++) {
        if (fabs(b - a) < 1e-6) break;
        double den = Zb - Za;
        if (fabs(den) < 1e-300) break;
        double c  = b - Zb * (b - a) / den;
        double Zc = Z_rs_double(c);
        if (Za * Zc < 0.0) { b = c; Zb = Zc; }
        else                { a = c; Za = Zc * 0.5; }  /* correction Illinois (Dowell 1971) */
    }

    /* Phase 2 : Newton Z_arb adaptatif (v15)
     * t < SEUIL_1NEWTON : 2 iter (biais_RS grand → 1 Newton insuffisant).
     * t ≥ SEUIL_1NEWTON : 1 iter (biais_RS < 6e-7 → quadratique → < tol).
     * Dérivée via Z_rs (différence centrale h=1e-4). */
    double t_curr  = (fabs(Za) < fabs(Zb)) ? a : b;
    double h       = 1e-4;
    int    n_newton = (t_curr < SEUIL_1NEWTON) ? 2 : 1;

    for (int k = 0; k < n_newton; k++) {
        double dZ = (Z_rs_double(t_curr + h) - Z_rs_double(t_curr - h)) / (2.0 * h);
        if (fabs(dZ) < 1e-10) break;
        double Zt = Z_arb(t_curr);
        if (g_arb_log && k == n_newton - 1)
            fprintf(g_arb_log, "NEWTON_FINAL %.15f Z=%.6e delta=%.6e n_newton=%d\n",
                    t_curr, Zt, Zt / (fabs(dZ) > 1e-10 ? dZ : 1.0), n_newton);
        if (fabs(Zt) < tol) return t_curr;
        double delta = Zt / dZ;
        t_curr -= delta;
        if (fabs(delta) < tol) break;
    }

    return t_curr;
}
