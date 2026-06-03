"""
Module niveau-0 : visualisation de rotation  e^(iθ) en fonction de t
Connexion avec Z(t) de Hardy
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""
from mpmath import siegeltheta, exp
import numpy as np                                                                                                                                                                    
import matplotlib.pyplot as plt                           

# --- Données (votre code de départ) ---                                                                                                                                              
t_vals  = np.linspace(1, 30, 300)
theta_vals = [float(siegeltheta(t)) for t in t_vals]                                                                                                                                  
z_vals  = [complex(exp(1j * th)) for th in theta_vals]    
                                                                                                                                                                                  
# --- Extraction Re(z) et Im(z) ---                                                                                                                                                   
re_vals = [z.real for z in z_vals]
im_vals = [z.imag for z in z_vals]                                                                                                                                                    
                                                      
# --- Tracé ---                                                                                                                                                                       
fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
                                                                                                                                                                                  
axes[0].plot(t_vals, re_vals, color='royalblue', linewidth=1.2)                                                                                                                       
axes[0].axhline(0, color='gray', linewidth=0.5, linestyle='--')
axes[0].set_ylabel("$\\cos(\\theta(t))$ = Re$(e^{i\\theta})$")                                                                                                                        
axes[0].set_title("Rotation $e^{i\\theta(t)}$ — composantes en fonction de $t$")                                                                                                      
axes[0].grid(True, alpha=0.3)                                                                                                                                                         
                                                                                                                                                                                  
axes[1].plot(t_vals, im_vals, color='crimson', linewidth=1.2)                                                                                                                         
axes[1].axhline(0, color='gray', linewidth=0.5, linestyle='--')
axes[1].set_ylabel("$\\sin(\\theta(t))$ = Im$(e^{i\\theta})$")                                                                                                                        
axes[1].set_xlabel("$t$")
axes[1].grid(True, alpha=0.3)                                                                                                                                                         
                                                        
plt.tight_layout()                                                                                                                                                                    
plt.savefig("exo2_rotation_theta.png", dpi=150)           
plt.show()  
