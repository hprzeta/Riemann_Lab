"""
Module niveau-2 :  Prolongement de la série
Calculez ζ ( − 1 ) par l'équation fonctionnelle :

ζ ( − 1 ) = 2 − 1 π − 2 sin ! ( − π 2 ) Γ ( 2 ) , ζ ( 2 )

et vérifiez que vous obtenez − 1 12 .
Connexion avec  ζ ( s )  
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""
from mpmath import mp, zeta, pi, gamma, sin
mp.dps = 15
s = -1
val = 2**s * pi**(s-1) * sin(pi*s/2) * gamma(1-s) * zeta(1-s)
print(f"ζ(-1) via équation fonctionnelle = {float(val):.8f}")
print(f"ζ(-1) via mpmath directement     = {float(zeta(-1)):.8f}")