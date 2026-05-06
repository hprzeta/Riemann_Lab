"""
Module niveau-3 : Produit eulérien
Connexion avec  ζ ( s )  
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""

from mpmath import mp, mpf, zeta
from sympy import primerange
mp.dps = 15
primes = list(primerange(2, 550))
s = 3
produit = mpf(1)
for p in primes:
    produit *= mpf(1) / (1 - mpf(1)/p**s)
print(f"Produit eulérien : {float(produit):.8f}")
print(f"ζ(3) exact       : {float(zeta(3)):.8f}")