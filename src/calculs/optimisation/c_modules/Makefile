## Makefile — compile illinois_mpfr.so + scan_arb.so + illinois_arb.so
## Phase C — Riemann_Lab / hprzeta
## IMPORTANT : les recettes utilisent des TAB réels (0x09), pas des espaces

CC     = gcc
CFLAGS = -O3 -march=native -fPIC -Wall -Wextra
LIBS   = -lmpfr -lgmp -lm

## libflint bundlée avec python-flint (chemin absolu + rpath)
LIBFLINT_DIR = $(HOME)/projet_zeta/zeta_env/lib/python3.12/site-packages/python_flint.libs
LIBFLINT_SO  = libflint-24205715.so.21.0.0

all: illinois_mpfr.so scan_arb.so illinois_arb.so

## cible principale : .so partagé appelé via ctypes depuis Python
## Option B : z_function.c retiré — Z_double supprimé (détection côté Python)
## v9 : brent_mpfr.c ajouté dans le même .so (accès à Z_rs_mpfr_ntermes)
illinois_mpfr.so: illinois_mpfr.c brent_mpfr.c
	$(CC) $(CFLAGS) -shared -o $@ $^ $(LIBS)

## scan_arb.so — détection C pure via Z_double (RS double + C0+C1, Berry 1992)
## Pas de dépendance FLINT : arb_fpwrap trop lent pour le scan en masse (×32 numpy)
scan_arb.so: scan_arb.c
	$(CC) $(CFLAGS) -shared -o $@ $< -lm

## illinois_arb.so — v12 : Illinois via arb_fpwrap_cdouble_hardy_z (FLINT 3)
## Pas de headers FLINT requis : prototype déclaré en forward dans illinois_arb.c
illinois_arb.so: illinois_arb.c
	$(CC) $(CFLAGS) -shared -o $@ $< \
		-L$(LIBFLINT_DIR) -l:$(LIBFLINT_SO) \
		-Wl,-rpath,$(LIBFLINT_DIR) \
		-lm

## cibles de test
test: illinois_mpfr.so
	python3 test_illinois.py

test_arb: illinois_arb.so
	python3 test_illinois_arb.py

## nettoyage
clean:
	rm -f *.so *.o

.PHONY: all test test_arb clean
