## Makefile — compile illinois_mpfr.so
## Phase C — Riemann_Lab / hprzeta
## IMPORTANT : les recettes utilisent des TAB réels (0x09), pas des espaces

CC     = gcc
CFLAGS = -O3 -march=native -fPIC -Wall -Wextra
LIBS   = -lmpfr -lgmp -lm

all: illinois_mpfr.so

## cible principale : .so partagé appelé via ctypes depuis Python
illinois_mpfr.so: illinois_mpfr.c z_function.c
	$(CC) $(CFLAGS) -shared -o $@ $^ $(LIBS)

## cible de test : compile + lance la validation Python
test: illinois_mpfr.so
	python3 test_illinois.py

## nettoyage
clean:
	rm -f *.so *.o

.PHONY: all test clean
