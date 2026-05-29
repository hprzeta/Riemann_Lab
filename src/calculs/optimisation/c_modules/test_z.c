#include <stdio.h>
#include <math.h>
#include <mpfr.h>

#define PREC 170

/* prototypes */
double Z_double(double t);

/* déclaration de Z_mpfr (copiée de illinois_mpfr.c) */
void Z_mpfr_wrapper(double t_double, double *result) {
    mpfr_t t, res;
    mpfr_init2(t, PREC);
    mpfr_init2(res, PREC);

    mpfr_set_d(t, t_double, MPFR_RNDN);

    extern void Z_mpfr(mpfr_t result, mpfr_t t);  // fonction interne
    Z_mpfr(res, t);

    *result = mpfr_get_d(res, MPFR_RNDN);

    mpfr_clear(t);
    mpfr_clear(res);
}

int main() {
    double t;
    double z_d, z_m;
    double err;

    printf("# t\tZ_double\tZ_mpfr\t|err|\n");

    for (t = 50.0; t <= 700.0; t += 10.0) {
        z_d = Z_double(t);
        Z_mpfr_wrapper(t, &z_m);

        err = fabs(z_d - z_m);

        printf("%.2f\t%.10e\t%.10e\t%.3e\n", t, z_d, z_m, err);
    }

    return 0;
}