/* illinois_mpfr.c — affinage Illinois de la méthode de la sécante en libmpfr
 * Précision : PREC = 170 bits (≈ 51 décimales) — phase d'affinage uniquement
 *
 * Algorithme Illinois (méthode de la sécante avec correction anti-stagnation) :
 *   Théorème : converge super-linéairement (ordre ≈ 1.44 vs 1.0 pour bisection)
 *   Correction : Z(a) *= 0.5 quand le même côté est choisi deux fois de suite
 *
 * Phase C — Riemann_Lab / hprzeta — 23 mai 2026 */

#include <math.h>
#include <mpfr.h>
#include "illinois_mpfr.h"
#include "z_function.h"

/* =========================================================================
 * theta_mpfr — θ(t) à PREC bits (Stirling étendu à t⁻⁵)
 * θ(t) = (t/2)·ln(t/2π) − t/2 − π/8 + 1/(48t) + 7/(5760t³) − 31/(80640t⁵)
 * ========================================================================= */
static void theta_mpfr(mpfr_t result, mpfr_t t, mpfr_t pi) {
    mpfr_t two_pi, half_t, lt, t3, t5, c;
    mpfr_inits2(PREC, two_pi, half_t, lt, t3, t5, c, (mpfr_ptr)NULL);

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
 * Z_mpfr — Z(t) via formule de Riemann-Siegel + correction RS (C₀+C₁)
 *
 * Z(t) = 2·Σ_{n=1}^{N} cos(θ(t)−t·ln n)/√n  +  R(t)
 *   N = ⌊√(t/2π)⌋,  θ(t) calculé à PREC bits
 *
 * Terme de reste R(t) (Berry 1992, cohérent avec riemann_siegel_batch.py) :
 *   τ = √(t/2π),  u = 2·(τ−N)−1 ∈ [−1,1)
 *   Ψ(u)  = cos(π·(u²/2+3/8)) / cos(π·u)
 *   Ψ'(u) = π·[−u·sin(A)·cos(B) + cos(A)·sin(B)] / cos²(B)
 *   R = (−1)^{N−1} · τ^{−1/2} · (Ψ(u) + Ψ'(u)·(u²/2−3/8)/(π·τ))
 *
 * IMPORTANT : cette Z_mpfr est cohérente avec Z_double (même formule,
 * précision supérieure). Cela garantit que Illinois C converge vers le
 * même zéro que la détection. Pour les vrais zéros de Riemann à 1e-12,
 * il faudrait 15+ termes RS ou l'algorithme de Borwein (travail futur).
 * ========================================================================= */
static void Z_mpfr(mpfr_t result, mpfr_t t) {
    mpfr_t pi;
    mpfr_init2(pi, PREC);
    mpfr_const_pi(pi, MPFR_RNDN);

    /* --- θ(t) à PREC bits --- */
    mpfr_t theta;
    mpfr_init2(theta, PREC);
    theta_mpfr(theta, t, pi);

    /* --- τ = √(t/2π), N = ⌊τ⌋ --- */
    double t_d  = mpfr_get_d(t, MPFR_RNDN);
    double pi_d = mpfr_get_d(pi, MPFR_RNDN);
    double tau  = sqrt(t_d / (2.0 * pi_d));
    long   N    = (long)tau;

    /* --- sommation principale à PREC bits --- */
    mpfr_t ln_n, arg, cs, sn, sqn, tmp;
    mpfr_inits2(PREC, ln_n, arg, cs, sn, sqn, tmp, (mpfr_ptr)NULL);
    mpfr_set_ui(result, 0, MPFR_RNDN);

    for (long n = 1; n <= N; n++) {
        mpfr_set_ui(ln_n, (unsigned long)n, MPFR_RNDN);
        mpfr_log(ln_n, ln_n, MPFR_RNDN);                     /* ln(n) — exact: log(1)=0 */
        mpfr_mul(arg, t, ln_n, MPFR_RNDN);                   /* t·ln n */
        mpfr_sub(arg, theta, arg, MPFR_RNDN);                /* θ−t·ln n */
        mpfr_cos(cs, arg, MPFR_RNDN);                        /* cos(·) */
        mpfr_set_ui(sqn, (unsigned long)n, MPFR_RNDN);
        mpfr_sqrt(sqn, sqn, MPFR_RNDN);                      /* √n */
        mpfr_div(tmp, cs, sqn, MPFR_RNDN);
        mpfr_add(result, result, tmp, MPFR_RNDN);
    }
    mpfr_mul_2ui(result, result, 1, MPFR_RNDN);              /* Z = 2·Σ */

    /* --- terme de correction RS (C₀+C₁) en double précision --- */
    double p  = tau - (double)N;             /* partie fractionnaire de τ */
    double u  = 2.0*p - 1.0;                /* u ∈ [−1, 1) */
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

    mpfr_clears(pi, theta, ln_n, arg, cs, sn, sqn, tmp, (mpfr_ptr)NULL);
}

/* =========================================================================
 * illinois_mpfr — affinage d'un zéro par la méthode Illinois en PREC bits
 *
 * Entrée : a_d, b_d (doubles) — intervalle [a,b] avec Z(a)·Z(b) < 0
 * Entrée : tol — tolérance sur |b−a| (typiquement 1e-12)
 * Sortie : partie imaginaire du zéro γ, précision ~12 décimales
 *
 * Algorithme :
 *   1. Sécante : c = b − Z(b)·(b−a)/(Z(b)−Z(a))
 *   2. Si Z(a)·Z(c) < 0 : b←c
 *      Sinon             : a←c, Z(a) *= 0.5  (correction Illinois)
 *   3. Arrêt si |b−a| < tol
 * ========================================================================= */
double illinois_mpfr(double a_d, double b_d, double tol) {
    /* --- variables mpfr — initialisées HORS boucle --- */
    mpfr_t a, b, c, Za, Zb, Zc;
    mpfr_t num, den, diff, abs_diff;
    mpfr_t tol_mpfr;

    mpfr_inits2(PREC, a, b, c, Za, Zb, Zc, (mpfr_ptr)NULL);
    mpfr_inits2(PREC, num, den, diff, abs_diff, tol_mpfr, (mpfr_ptr)NULL);

    /* conversion des bornes double → mpfr */
    mpfr_set_d(a, a_d, MPFR_RNDN);
    mpfr_set_d(b, b_d, MPFR_RNDN);
    mpfr_set_d(tol_mpfr, tol, MPFR_RNDN);

    /* évaluation initiale de Z(a) et Z(b) */
    Z_mpfr(Za, a);
    Z_mpfr(Zb, b);

    /* --- boucle Illinois --- */
    for (int iter = 0; iter < MAX_ITER; iter++) {

        /* vérification de la convergence : |b−a| < tol → arrêt */
        mpfr_sub(diff, b, a, MPFR_RNDN);              /* b − a */
        mpfr_abs(abs_diff, diff, MPFR_RNDN);           /* |b − a| */
        if (mpfr_cmp(abs_diff, tol_mpfr) < 0) {
            break;                                     /* convergence atteinte */
        }

        /* sécante : c = b − Z(b)·(b−a)/(Z(b)−Z(a)) */
        mpfr_sub(den, Zb, Za, MPFR_RNDN);             /* Z(b) − Z(a) */
        mpfr_mul(num, Zb, diff, MPFR_RNDN);           /* Z(b)·(b−a) */
        mpfr_div(num, num, den, MPFR_RNDN);            /* Z(b)·(b−a)/(Z(b)−Z(a)) */
        mpfr_sub(c, b, num, MPFR_RNDN);               /* c = b − ... */

        /* évaluation de Z(c) */
        Z_mpfr(Zc, c);

        /* mise à jour de l'intervalle */
        if (mpfr_sgn(Za) * mpfr_sgn(Zc) < 0) {
            /* le zéro est dans [a, c] : b ← c */
            mpfr_set(b, c, MPFR_RNDN);
            mpfr_set(Zb, Zc, MPFR_RNDN);
        } else {
            /* le zéro est dans [c, b] : a ← c, correction Illinois Za *= 0.5
             * La correction évite la convergence lente quand un côté est choisi
             * plusieurs fois de suite (heuristique Illinois, pas théorème) */
            mpfr_set(a, c, MPFR_RNDN);
            mpfr_set(Za, Zc, MPFR_RNDN);
            mpfr_div_2ui(Za, Za, 1, MPFR_RNDN);      /* Za *= 0.5 */
        }
    }

    /* extraction du résultat : milieu de [a,b] → double */
    mpfr_add(c, a, b, MPFR_RNDN);
    mpfr_div_2ui(c, c, 1, MPFR_RNDN);                 /* c = (a+b)/2 */
    double result = mpfr_get_d(c, MPFR_RNDN);

    /* libération de toutes les variables mpfr */
    mpfr_clears(a, b, c, Za, Zb, Zc, (mpfr_ptr)NULL);
    mpfr_clears(num, den, diff, abs_diff, tol_mpfr, (mpfr_ptr)NULL);

    return result;
}

/* =========================================================================
 * illinois_mpfr_cb — Illinois en double avec callback Python pour Z(t)
 *
 * Voie B : élimine le biais RS C0+C1 (~1e-3) en remplaçant Z_mpfr par
 * un callback fourni par Python = float(mpmath.siegelz(t)).
 *
 * Arithmétique en double (pas mpfr) : le callback retourne déjà ~35 dps
 * converti en double (15-17 chiffres significatifs). Illinois en double
 * est suffisant pour atteindre |b−a| < 1e-12 sur les vrais zéros.
 *
 * Entrée : a_d, b_d — bornes de l'intervalle (zfunc(a)*zfunc(b) < 0)
 * Entrée : tol      — tolérance sur |b−a|
 * Entrée : zfunc    — pointeur de fonction Python (ctypes.CFUNCTYPE)
 * Sortie : double — partie imaginaire du zéro, précision ~1e-14
 * ========================================================================= */
double illinois_mpfr_cb(double a_d, double b_d, double tol, z_func_t zfunc) {
    double a  = a_d, b = b_d;
    double Za = zfunc(a);            /* évaluation initiale via callback Python */
    double Zb = zfunc(b);

    /* vérification du changement de signe — précondition de l'algorithme */
    if (Za * Zb >= 0.0) return (a + b) / 2.0;

    /* cas dégénéré : une borne est déjà quasi-zéro.
     * La sécante déplace c de seulement |Zi|/|Zj| * (b-a) → stagnation garantie.
     * Exemple : |Za| < 1e-11 * |Zb| → a est ~10¹¹x plus proche du zéro que b.
     * Retourner directement la meilleure borne évite 100 appels Python inutiles. */
    double abs_Za = fabs(Za), abs_Zb = fabs(Zb);
    if (abs_Za < abs_Zb * 1e-10) return a;   /* a est quasi-le-zéro */
    if (abs_Zb < abs_Za * 1e-10) return b;   /* b est quasi-le-zéro */

    for (int iter = 0; iter < MAX_ITER; iter++) {
        /* critère d'arrêt : intervalle plus petit que la tolérance */
        if (fabs(b - a) < tol) break;

        double den = Zb - Za;
        if (fabs(den) < 1e-300) break;              /* sécurité : dénominateur nul */

        /* sécante : c = b − Z(b)·(b−a)/(Z(b)−Z(a)) */
        double c  = b - Zb * (b - a) / den;
        double Zc = zfunc(c);                        /* appel callback Python */

        /* mise à jour de l'intervalle */
        if (Za * Zc < 0.0) {
            /* zéro dans [a, c] : b ← c */
            b  = c;
            Zb = Zc;
        } else {
            /* zéro dans [c, b] : a ← c + correction Illinois (Za *= 0.5)
             * Cette correction évite la stagnation quand le même côté est
             * choisi plusieurs fois — heuristique éprouvée (Dowell 1971) */
            a  = c;
            Za = Zc;
            Za *= 0.5;
        }
    }

    /* retourner la borne avec le plus petit résidu (plus robuste que le milieu) */
    return (fabs(Za) < fabs(Zb)) ? a : b;
}
