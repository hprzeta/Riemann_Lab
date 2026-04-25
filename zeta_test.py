import numpy as np

def zeta_numerator_roots(g, q, thetas):
    """
    Racines du numérateur P(u) de Z(C/F_q, u).
    thetas : angles de Frobenius (longueur 2g)
    """
    alphas = np.sqrt(q) * np.exp(1j * np.array(thetas))
    # P(u) = prod(1 - alpha_i * u)
    # racines de P(u) : u_i = 1/alpha_i
    roots_u = 1.0 / alphas
    return roots_u

# Exemple : courbe elliptique (g=1) sur F_7
roots = zeta_numerator_roots(g=1, q=7, thetas=[0.8, -0.8])
print(f"Racines : {roots}")
print(f"Modules : {np.abs(roots)}")  # doit être 1/sqrt(7)
