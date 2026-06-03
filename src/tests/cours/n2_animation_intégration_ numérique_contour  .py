"""
Module niveau-2 : intégration numérique sur un contour  
Connexion avec  ζ ( s )  
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""
from mpmath import mp, mpc, exp, pi, quad, log, re, im
import numpy as np
import matplotlib.pyplot as plt

mp.dps = 15

def integrer_contour(f, centre, rayon, n_points=1000):
    """Intégrale numérique de f sur un cercle de centre et rayon donnés."""
    thetas = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    dtheta = 2*np.pi / n_points
    resultat = mpc(0)
    for theta in thetas:
        z = centre + rayon * exp(mpc(0, theta))
        dz = mpc(0, 1) * rayon * exp(mpc(0, theta)) * dtheta
        resultat += f(z) * dz
    return resultat

# Test 1 : f(z) = 1/z  →  devrait donner 2πi
f1 = lambda z: 1/z
I1 = integrer_contour(f1, mpc(0,0), 1.0)
print(f"∮ 1/z dz  sur |z|=1 :")
print(f"  Résultat numérique : {float(re(I1)):.6f} + {float(im(I1)):.6f}i")
print(f"  Valeur exacte      : 0 + {float(2*pi):.6f}i  (= 2πi)")

# Test 2 : f(z) = z²  →  devrait donner 0 (f holomorphe)
f2 = lambda z: z**2
I2 = integrer_contour(f2, mpc(0,0), 1.0)
print(f"\n∮ z² dz  sur |z|=1 :")
print(f"  Résultat numérique : {float(re(I2)):.2e} + {float(im(I2)):.2e}i")
print(f"  Valeur exacte      : 0 (théorème de Cauchy)")

# Test 3 : formule intégrale — récupérer f(z0) = z0² = (0.5+0.3i)²
z0 = mpc(0.5, 0.3)
f3 = lambda z: z**2 / (z - z0)
I3 = integrer_contour(f3, mpc(0,0), 1.0)
f_reconstitue = I3 / (2 * pi * mpc(0,1))
f_exact = z0**2
print(f"\nFormule intégrale de Cauchy pour f(z)=z², z0={z0}:")
print(f"  f(z0) reconstruit  : {float(re(f_reconstitue)):.6f} + {float(im(f_reconstitue)):.6f}i")
print(f"  f(z0) exact        : {float(re(f_exact)):.6f} + {float(im(f_exact)):.6f}i")