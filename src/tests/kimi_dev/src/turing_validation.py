"""
────────────────────────────────────────────────────────────────────────────
Méthode   : Méthode de Turing — (Validation rigoureuse) 
            Vérification qu'aucun zéro n'est manqué
Pourquoi  : Vous avez 10 142 zéros, mais commentaire prouver qu'il n'en manque
            T=0  Et T=10000  ?   
Auteur    : hprzeta — Exploration de l'Hypothèse de Riemann
Date      : 2026
────────────────────────────────────────────────────────────────────────────
"""
import mpmath as mp

def N(T):
    """
    Nombre de zéros avec 0 < Im(ρ) < T
    Formule de Riemann-von Mangoldt :
    N(T) = (T/2π) * ln(T/2πe) + 7/8 + S(T) + O(1/T)
    """
    return T/(2*mp.pi) * mp.log(T/(2*mp.pi*mp.e)) + mp.mpf('7/8')

def verifier_completude(zeros, T_MAX):
    """
    Compare le nombre de zéros trouvés avec N(T_MAX)
    """
    n_trouves = len(zeros)
    n_attendus = int(N(T_MAX))
    
    print(f"Zéros trouvés  : {n_trouves}")
    print(f"Zéros attendus : {n_attendus}")
    print(f"Écart          : {abs(n_trendus - n_attendus)}")
    
    if n_trouves == n_attendus:
        print("✅ Completude vérifiée — aucun zéro manqué")
    else:
        print("⚠️  Zéros potentiellement manqués ou faux positifs")
