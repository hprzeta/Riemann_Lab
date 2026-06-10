## Makefile — compile illinois_mpfr.so + scan_arb.so
## Phase C — Riemann_Lab / hprzeta
## IMPORTANT : les recettes utilisent des TAB réels (0x09), pas des espaces

CC     = gcc
CFLAGS = -O3 -march=native -fPIC -Wall -Wextra
LIBS   = -lmpfr -lgmp -lm

all: illinois_mpfr.so scan_arb.so

## cible principale : .so partagé appelé via ctypes depuis Python
## Option B : z_function.c retiré — Z_double supprimé (détection côté Python)
illinois_mpfr.so: illinois_mpfr.c
	$(CC) $(CFLAGS) -shared -o $@ $^ $(LIBS)

## scan_arb.so — détection C pure via Z_double (RS double + C0+C1, Berry 1992)
## Pas de dépendance FLINT : arb_fpwrap trop lent pour le scan en masse (×32 numpy)
scan_arb.so: scan_arb.c
	$(CC) $(CFLAGS) -shared -o $@ $< -lm

## cible de test : compile + lance la validation Python
test: illinois_mpfr.so
	python3 test_illinois.py

## nettoyage
clean:
	rm -f *.so *.o

.PHONY: all test clean
