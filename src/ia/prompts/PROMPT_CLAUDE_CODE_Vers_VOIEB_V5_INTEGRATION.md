Lis src/ia/prompts/prompt_claude_code_phase_c_voie_b_v5.md.
Lis /home/riemann/projet_zeta/pdf/optimisation/Voie_b_5/Handoff.md la prochaine session 
Lis les PDF de cadrage /home/riemann/projet_zeta/pdf/optimisation/Voie_b_5 si besoin de complément.
Travaille uniquement sur la branche Riemann_Lab_C.
Ne casse pas compute_zeros_v4.py validé.

Contexte : le biais Z_mpfr (~1e-3) vient d'une insuffisance du
développement RS (C0+C1 seulement). mpc_zeta est absent dans
libmpc 1.3.1. La solution retenue est un wrapper Python/C.

Mission1 : implémenter un wrapper qui permet à illinois_mpfr.c
d'obtenir Z(t) avec précision ~1e-12 en appelant mpmath.siegelz(t).
Contrainte absolue : illinois_mpfr.so reste appelable depuis Python
via ctypes exactement comme maintenant.

Critères de succès :
- biais Z moyen < 1e-8 sur t ∈ [300, 650]
- Illinois_C pur > 50% sur run T=650
- Turing-Backlund complet
- LMFDB 20/20 < 1e-10


Tu connais les fichiers Handoff.md, les prompts Phase C et les 9 PDF
de cadrage qui te sont fournis en pièces jointes Voi_b_5.

Tu distingues toujours : calcul expérimental / conjecture / preuve formelle.
Tu ne prétends jamais prouver l'Hypothèse de Riemann.

Pour rappel 
Contexte du générale du projet :
- Objectif 1 : calculer les 10 000 premiers zéros non-triviaux de ζ(s)
  sur la droite critique Re(s) = 1/2
- Objectif 2 : construire un agent IA autonome de recherche mathématique
- Langage : Python 3.12, C/libmpfr, mpmath, NumPy, CuPy
- Machine : Ubuntu, Intel i7, GTX 960M 4GB, CUDA 12.2
- Branche active : Riemann_Lab_C (Phase C — Illinois en C/libmpfr)

État actuel (28/29 mai 2026) :
- compute_zeros_v4.py validé sur T=80/T=300/T=650
- Problème : Illinois_C pur = 0% — biais Z_mpfr ~9e-3 vs mpmath.siegelz
- Priorité immédiate : voie B/v5 — corriger z_function.c, puis v4.1

