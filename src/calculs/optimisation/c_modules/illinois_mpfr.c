/* illinois_mpfr.c — affinage Illinois de la méthode de la sécante en libmpfr
 * Précision : PREC = 170 bits (≈ 51 décimales) — phase d'affinage uniquement
 *
 * Algorithme Illinois (méthode de la sécante avec correction anti-stagnation) :
 *   Théorème : converge super-linéairement (ordre ≈ 1.44 vs 1.0 pour bisection)
 *   Correction : Z(a) *= 0.5 quand le même côté est choisi deux fois de suite
 *
 * Option B (2026-06-03) : Z_double supprimé.
 *   - Détection des signes : côté Python (Z_batch / mpmath.siegelz)
 *   - Affinage : illinois_refine reçoit fa, fb déjà calculés par Python
 *   - Pas de recalcul des bornes en C → incohérence RS éliminée
 *
 * Phase C — Riemann_Lab / hprzeta — 2026-06-03 */

#include <math.h>
#include <mpfr.h>
#include "illinois_mpfr.h"
/* NOTE : z_function.h retiré — Z_double supprimé (Option B) */

/* =========================================================================
 * theta_mpfr — θ(t) à prec bits (Stirling étendu à t⁻⁵)
 * θ(t) = (t/2)·ln(t/2π) − t/2 − π/8 + 1/(48t) + 7/(5760t³) − 31/(80640t⁵)
 * ========================================================================= */
static void theta_mpfr(mpfr_t result, mpfr_t t, mpfr_t pi, mpfr_prec_t prec) {
    mpfr_t two_pi, half_t, lt, t3, t5, c;
    mpfr_inits2(prec, two_pi, half_t, lt, t3, t5, c, (mpfr_ptr)NULL);

    mpfr_mul_2ui(two_pi, pi, 1, MPFR_RNDN);
    mpfr_div(lt, t, two_pi, MPFR_RNDN);
    mpfr_log(lt, lt, MPFR_RNDN);                   /* ln(t/2π) */
    mpfr_div_2ui(half_t, t, 1, MPFR_RNDN);
    mpfr_mul(result, half_t, lt, MPFR_RNDN);       /* (t/2)·ln(t/2π) */
    mpfr_sub(result, result, half_t, MPFR_RNDN);   /* − t/2 */
    mpfr_div_ui(c, pi, 8, MPFR_RNDN);
    mpfr_sub(result, result, c, MPFR_RNDN);        /* − π/8 */
    mpfr_mul_ui(c, t, 48, MPFR_RNDN);
    mpfr_ui_div(c, 1, c, MPFR_RNDN);
    mpfr_add(result, result, c, MPFR_RNDN);        /* + 1/(48t) */
    mpfr_mul(t3, t, t, MPFR_RNDN);
    mpfr_mul(t3, t3, t, MPFR_RNDN);
    mpfr_mul_ui(c, t3, 5760, MPFR_RNDN);
    mpfr_set_ui(lt, 7, MPFR_RNDN);
    mpfr_div(c, lt, c, MPFR_RNDN);
    mpfr_add(result, result, c, MPFR_RNDN);        /* + 7/(5760t³) */
    mpfr_mul(t5, t3, t, MPFR_RNDN);
    mpfr_mul(t5, t5, t, MPFR_RNDN);
    mpfr_mul_ui(c, t5, 80640, MPFR_RNDN);
    mpfr_set_ui(lt, 31, MPFR_RNDN);
    mpfr_div(c, lt, c, MPFR_RNDN);
    mpfr_sub(result, result, c, MPFR_RNDN);        /* − 31/(80640t⁵) */

    mpfr_clears(two_pi, half_t, lt, t3, t5, c, (mpfr_ptr)NULL);
}

/* =========================================================================
 * Z_mpfr — Z(t) via Riemann-Siegel + correction RS (C₀+C₁) à prec bits
 *
 * Z(t) = 2·Σ_{n=1}^{N} cos(θ(t)−t·ln n)/√n  +  R(t)
 *   N = ⌊√(t/2π)⌋,  θ(t) calculé à prec bits
 *
 * Terme de reste R(t) (Berry 1992) :
 *   τ = √(t/2π),  u = 2·(τ−N)−1 ∈ [−1,1)
 *   Ψ(u)  = cos(π·(u²/2+3/8)) / cos(π·u)
 *   Ψ'(u) = π·[−u·sin(A)·cos(B) + cos(A)·sin(B)] / cos²(B)
 *   R = (−1)^{N−1} · τ^{−1/2} · (Ψ(u) + Ψ'(u)·(u²/2−3/8)/(π·τ))
 *
 * Pour les itérations intermédiaires d'Illinois : le biais RS (C₀+C₁)
 * est ~1e-3 pour N<7 (t<300), mais les SIGNES sont corrects → convergence OK.
 * Pour t≥300 (N≥7), le biais est <1e-3 → résultat final fiable à 1e-3.
 * ========================================================================= */
static void Z_mpfr(mpfr_t result, mpfr_t t, mpfr_prec_t prec) {
    mpfr_t pi;
    mpfr_init2(pi, prec);
    mpfr_const_pi(pi, MPFR_RNDN);

    /* θ(t) à prec bits */
    mpfr_t theta;
    mpfr_init2(theta, prec);
    theta_mpfr(theta, t, pi, prec);

    /* τ = √(t/2π), N = ⌊τ⌋ en double (N est petit, pas besoin de mpfr) */
    double t_d  = mpfr_get_d(t, MPFR_RNDN);
    double pi_d = mpfr_get_d(pi, MPFR_RNDN);
    double tau  = sqrt(t_d / (2.0 * pi_d));
    long   N    = (long)tau;

    /* sommation principale à prec bits */
    mpfr_t ln_n, arg, cs, sqn, tmp;
    mpfr_inits2(prec, ln_n, arg, cs, sqn, tmp, (mpfr_ptr)NULL);
    mpfr_set_ui(result, 0, MPFR_RNDN);

    for (long n = 1; n <= N; n++) {
        mpfr_set_ui(ln_n, (unsigned long)n, MPFR_RNDN);
        mpfr_log(ln_n, ln_n, MPFR_RNDN);                     /* ln(n) */
        mpfr_mul(arg, t, ln_n, MPFR_RNDN);                   /* t·ln n */
        mpfr_sub(arg, theta, arg, MPFR_RNDN);                /* θ−t·ln n */
        mpfr_cos(cs, arg, MPFR_RNDN);                        /* cos(·) */
        mpfr_set_ui(sqn, (unsigned long)n, MPFR_RNDN);
        mpfr_sqrt(sqn, sqn, MPFR_RNDN);                      /* √n */
        mpfr_div(tmp, cs, sqn, MPFR_RNDN);
        mpfr_add(result, result, tmp, MPFR_RNDN);
    }
    mpfr_mul_2ui(result, result, 1, MPFR_RNDN);              /* Z = 2·Σ */

    /* terme de correction RS (C₀+C₁) en double précision */
    double p  = tau - (double)N;
    double u  = 2.0*p - 1.0;
    double A  = pi_d * (u*u/2.0 + 0.375);
    double B  = pi_d * u;
    double cB = cos(B), sB = sin(B);
    double cA = cos(A), sA = sin(A);
    double R  = 0.0;
    if (fabs(cB) > 1e-10) {
        double C0    = cA / cB;
        double dPsi  = pi_d * (-u*sA*cB + cA*sB) / (cB*cB);
        double C1    = dPsi * (u*u/2.0 - 0.375) / (pi_d * tau);
        double signe = ((N - 1) % 2 == 0) ? 1.0 : -1.0;
        R = signe * pow(tau, -0.5) * (C0 + C1);
    }
    mpfr_set_d(tmp, R, MPFR_RNDN);
    mpfr_add(result, result, tmp, MPFR_RNDN);

    mpfr_clears(pi, theta, ln_n, arg, cs, sqn, tmp, (mpfr_ptr)NULL);
}

/* =========================================================================
 * illinois_mpfr — affinage Illinois en PREC bits (ancienne interface)
 *
 * Conservée pour compatibilité descendante. Recalcule Z(a) et Z(b) en C
 * avec Z_mpfr (RS + C₀+C₁). Pour les nouvelles intégrations, préférer
 * illinois_refine qui reçoit fa/fb précalculés par Python.
 *
 * Entrée : a_d, b_d — bornes avec Z_mpfr(a)·Z_mpfr(b) < 0
 * Entrée : tol — tolérance sur |b−a| (typiquement 1e-12)
 * ========================================================================= */
double illinois_mpfr(double a_d, double b_d, double tol) {
    mpfr_t a, b, c, Za, Zb, Zc;
    mpfr_t num, den, diff, abs_diff;
    mpfr_t tol_mpfr;

    mpfr_inits2(PREC, a, b, c, Za, Zb, Zc, (mpfr_ptr)NULL);
    mpfr_inits2(PREC, num, den, diff, abs_diff, tol_mpfr, (mpfr_ptr)NULL);

    mpfr_set_d(a, a_d, MPFR_RNDN);
    mpfr_set_d(b, b_d, MPFR_RNDN);
    mpfr_set_d(tol_mpfr, tol, MPFR_RNDN);

    Z_mpfr(Za, a, PREC);
    Z_mpfr(Zb, b, PREC);

    for (int iter = 0; iter < MAX_ITER; iter++) {
        mpfr_sub(diff, b, a, MPFR_RNDN);
        mpfr_abs(abs_diff, diff, MPFR_RNDN);
        if (mpfr_cmp(abs_diff, tol_mpfr) < 0) break;

        mpfr_sub(den, Zb, Za, MPFR_RNDN);
        mpfr_mul(num, Zb, diff, MPFR_RNDN);
        mpfr_div(num, num, den, MPFR_RNDN);
        mpfr_sub(c, b, num, MPFR_RNDN);

        Z_mpfr(Zc, c, PREC);

        if (mpfr_sgn(Za) * mpfr_sgn(Zc) < 0) {
            mpfr_set(b, c, MPFR_RNDN);
            mpfr_set(Zb, Zc, MPFR_RNDN);
        } else {
            mpfr_set(a, c, MPFR_RNDN);
            mpfr_set(Za, Zc, MPFR_RNDN);
            mpfr_div_2ui(Za, Za, 1, MPFR_RNDN);  /* Za *= 0.5 — correction Illinois */
        }
    }

    mpfr_add(c, a, b, MPFR_RNDN);
    mpfr_div_2ui(c, c, 1, MPFR_RNDN);
    double result = mpfr_get_d(c, MPFR_RNDN);

    mpfr_clears(a, b, c, Za, Zb, Zc, (mpfr_ptr)NULL);
    mpfr_clears(num, den, diff, abs_diff, tol_mpfr, (mpfr_ptr)NULL);
    return result;
}

/* =========================================================================
 * Z_mpfr_eval — évalue Z_mpfr(t) et retourne un double
 * Usage : validation externe, test_illinois.py
 * ========================================================================= */
double Z_mpfr_eval(double t_d) {
    mpfr_t t, result;
    mpfr_init2(t, PREC);
    mpfr_init2(result, PREC);
    mpfr_set_d(t, t_d, MPFR_RNDN);
    Z_mpfr(result, t, PREC);
    double r = mpfr_get_d(result, MPFR_RNDN);
    mpfr_clears(t, result, (mpfr_ptr)NULL);
    return r;
}

/* =========================================================================
 * illinois_mpfr_cb — Illinois en double avec callback Python pour Z(t)
 *
 * Voie B (callback) : élimine le biais RS en remplaçant Z_mpfr par un
 * callback fourni par Python = float(mpmath.siegelz(t)).
 *
 * Entrée : a_d, b_d — bornes avec zfunc(a)·zfunc(b) < 0
 * Entrée : tol      — tolérance sur |b−a|
 * Entrée : zfunc    — pointeur de fonction Python (ctypes.CFUNCTYPE)
 * Sortie : double — partie imaginaire du zéro, précision ~1e-14
 * ========================================================================= */
double illinois_mpfr_cb(double a_d, double b_d, double tol, z_func_t zfunc) {
    double a  = a_d, b = b_d;
    double Za = zfunc(a);
    double Zb = zfunc(b);

    if (Za * Zb >= 0.0) return (a + b) / 2.0;

    double abs_Za = fabs(Za), abs_Zb = fabs(Zb);
    if (abs_Za < abs_Zb * 1e-10) return a;
    if (abs_Zb < abs_Za * 1e-10) return b;

    for (int iter = 0; iter < MAX_ITER; iter++) {
        if (fabs(b - a) < tol) break;

        double den = Zb - Za;
        if (fabs(den) < 1e-300) break;

        double c  = b - Zb * (b - a) / den;
        double Zc = zfunc(c);

        if (Za * Zc < 0.0) {
            b  = c;
            Zb = Zc;
        } else {
            a  = c;
            Za = Zc * 0.5;   /* correction Illinois — Dowell 1971 */
        }
    }

    return (fabs(Za) < fabs(Zb)) ? a : b;
}

/* =========================================================================
 * illinois_refine — affinage Illinois Option B
 *
 * Reçoit les bornes [a, b] ET leurs valeurs Z(a)=fa, Z(b)=fb calculées
 * côté Python par mpmath.siegelz (vraies valeurs, biais RS éliminé à
 * l'initialisation). Les itérations intermédiaires utilisent Z_mpfr à
 * prec_bits de précision — correct dès que N = ⌊√(t/2π)⌋ ≥ 7 (t ≥ 300).
 *
 * Avantage vs illinois_mpfr : pas de recalcul de Za/Zb en C → l'encadrement
 * initial est ancré sur les vrais zéros de Riemann, pas les pseudo-zéros RS.
 *
 * Entrée : a, b       — bornes avec fa·fb < 0
 * Entrée : fa, fb     — Z(a) et Z(b) calculés par mpmath.siegelz côté Python
 * Entrée : prec_bits  — précision interne libmpfr (ex: 170)
 * Entrée : tol        — tolérance sur |b−a| (ex: 1e-12)
 * Entrée : max_iter   — nombre max d'itérations (ex: 100)
 * Sortie : double — partie imaginaire du zéro affiné
 * ========================================================================= */
double illinois_refine(double a, double b, double fa, double fb,
                       int prec_bits, double tol, int max_iter) {
    /* précision interne : au moins PREC bits pour la sécurité numérique */
    mpfr_prec_t prec = (prec_bits >= 64) ? (mpfr_prec_t)prec_bits : PREC;

    double Za = fa;   /* valeurs initiales fournies par Python — pas de recalcul C */
    double Zb = fb;

    if (Za * Zb >= 0.0) return (a + b) / 2.0;

    /* cas dégénéré : une borne est quasi-zéro — évite 100 itérations inutiles */
    if (fabs(Za) < fabs(Zb) * 1e-10) return a;
    if (fabs(Zb) < fabs(Za) * 1e-10) return b;

    /* variables mpfr pour l'évaluation des points intermédiaires */
    mpfr_t mc, Zc_mpfr;
    mpfr_init2(mc, prec);
    mpfr_init2(Zc_mpfr, prec);

    for (int iter = 0; iter < max_iter; iter++) {
        if (fabs(b - a) < tol) break;

        double den = Zb - Za;
        if (fabs(den) < 1e-300) break;            /* dénominateur nul — arrêt */

        /* sécante : c = b − Z(b)·(b−a)/(Z(b)−Z(a)) */
        double c = b - Zb * (b - a) / den;

        /* évaluation Z_mpfr(c) — Z_mpfr est fiable pour t ≥ 300 (N ≥ 7 termes) */
        mpfr_set_d(mc, c, MPFR_RNDN);
        Z_mpfr(Zc_mpfr, mc, prec);
        double Zc = mpfr_get_d(Zc_mpfr, MPFR_RNDN);

        if (Za * Zc < 0.0) {
            b  = c;
            Zb = Zc;
        } else {
            a  = c;
            Za = Zc * 0.5;   /* correction Illinois — réduit la stagnation */
        }
    }

    mpfr_clears(mc, Zc_mpfr, (mpfr_ptr)NULL);

    /* retourner la borne avec le plus petit résidu */
    return (fabs(Za) < fabs(Zb)) ? a : b;
}
