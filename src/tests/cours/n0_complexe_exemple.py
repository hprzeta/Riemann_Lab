"""
Module niveau-0 : visualisation complexe
Connexion avec Z(t) de Hardy
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""
from mpmath import mp, mpc, fabs, arg, pi
mp.dps = 15

z = mpc(3, 4)              # z = 3 + 4i
print(f"z      = {z}")
print(f"|z|    = {fabs(z)}")           # 5.0
print(f"arg(z) = {arg(z)} rad")        # 0.9272...
print(f"Re(z)  = {z.real}")            # 3.0
print(f"Im(z)  = {z.imag}")            # 4.0
print(f"z̄      = {z.conjugate()}")    # 3 - 4i
