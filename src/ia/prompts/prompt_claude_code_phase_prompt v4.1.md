RÈGLE ABSOLUE : ne saute aucune étape de test pour aller plus vite.
Si tu es tenté de passer directement à un run long, ARRÊTE-toi et
montre-moi d'abord les chiffres demandés. Attends ma validation
explicite ("OK continue") avant CHAQUE run. Ne lance jamais un run
de plusieurs minutes sans mon feu vert écrit.

Travaille sur la branche Riemann_Lab_C. Objectif : créer
compute_zeros_v4_1.py qui lève le goulot de détection de v5.

CONTEXTE
- v5 (compute_zeros_v5.py) valide Illinois_C pur à 100% mais est lent :
  mpmath.siegelz en détection séquentielle = ~311ms/pas pour t>3000, ~1 z/s.
- Cible v4.1 : ~15-20 z/s.
- NE CASSE PAS compute_zeros_v4.py ni compute_zeros_v5.py : ils restent
  la référence validée. Crée un NOUVEAU fichier, ne modifie pas les anciens.

EXPLICATIONS MATHÉMATIQUES OBLIGATOIRES (formules en LaTeX)
Pour chaque fonction mathématique du code, écris d'abord la formule en
LaTeX bien formatée, puis explique-la, AVANT de coder. Au minimum :
- Fonction Z de Hardy : $Z(t) = e^{i\theta(t)}\,\zeta\!\left(\tfrac12+it\right)$,
  réelle pour t réel, et ses changements de signe ↔ zéros de ζ sur la droite critique.
- θ(t) de Riemann-Siegel : $\theta(t) = \arg\Gamma\!\left(\tfrac14+\tfrac{it}{2}\right) - \tfrac{t}{2}\ln\pi$.
- Formule de Riemann-Siegel tronquée (ce que calcule Z_batch) et pourquoi
  la troncature limite la précision.
- N(T) exact : $N(T) = \dfrac{T}{2\pi}\ln\!\dfrac{T}{2\pi e} - \dfrac{T}{2\pi} + \tfrac78 + S(T) + \dots$
- Pas d'échantillonnage STEP : $\text{STEP} = \min\!\left(\dfrac{2\pi}{5\ln(T/2\pi)},\,0.10\right)$.
RÈGLE KaTeX : utiliser \text{Re}, \text{Im} — JAMAIS \operatorname{...}.
Délimiteurs $...$ inline et $$...$$ display (compatibles wiki GitHub + index.html).

ERREURS DÉJÀ COMMISES — NE PAS LES REPRODUIRE
1. N(T) : formule EXACTE T/(2π)·ln(T/(2πe)), JAMAIS T/(2π)·ln(T/2π) (sous-estimait ~64%).
2. Détection : fonction Z de Hardy pour les changements de signe, JAMAIS
   Re(ζ(½+it)) (faux changements dus à la phase φ(t) → bug v1 vers t≈432).
3. STEP : min(2π/(5·ln(T/2π)), 0.10), sinon on rate des zéros à grand T.
4. Visualisation : plt.savefig() + plt.close(), JAMAIS plt.show() (bloque les logs).
5. Turing : distinguer explicitement MANQUE (delta>0) vs SURPLUS (delta<0).
6. Ne jamais écraser un CSV de run validé ; tout nouveau run = fichier horodaté.

LES 4 CORRECTIONS À APPLIQUER
1. Détection via Z_batch() vectorisé au lieu de mpmath.siegelz (gain ~×50)
2. Parallélisme 4 workers (multiprocessing.Pool)
3. Seuil T_SEUIL = 300.0 : Illinois_C pur au-delà (couvre ~99% des zéros)
4. Arrêt immédiat avec erreur claire si illinois_mpfr.so absent

PROTOCOLE DE TEST OBLIGATOIRE — POINT D'ARRÊT N°1
Z_batch est le nouveau cœur de la détection : valide-le AVANT de l'utiliser.
- Compare Z_batch(t) vs mpmath.siegelz(t) sur : t ∈ [0,100], [300,400],
  [3000,3100], [9900,10000]
- Vérifie que les changements de signe détectés sont IDENTIQUES aux deux méthodes
- Affiche pour chaque plage : écart max |Z_batch - siegelz| ET nombre de
  changements de signe par méthode (doivent coïncider)
- STOP ici. Montre-moi ces chiffres et attends mon "OK continue".

VALIDATION COURTE — POINT D'ARRÊT N°2
Seulement après mon feu vert :
- Run T=300, compare au run v5 validé (Turing COMPLET, LMFDB 19/20, 138/138 zéros)
- Affiche : nb de zéros, statut Turing, comparaison LMFDB, vitesse (z/s)
- STOP ici. Attends mon "OK continue" avant tout run plus long.

RAPPORT DE TRANSITION — SEULEMENT après validation v4.1 réussie
Génère docs/analyse_problemes_v5_v4_1_YYYYMMDD.md (date du jour) :
- En-tête : titre "Analyse des problèmes v5 → v4.1", Auteur : hprzeta,
  Date : <date du jour>, branche Riemann_Lab_C
- Par problème : cause mathématique + formules LaTeX + tableau de mesures
  exactes (écarts, vitesses avant/après) + solution retenue
- Tableau récapitulatif global (correction → gain mesuré)
- Bloc final "Questions ouvertes" (limites, perspectives, matériel)
- Pied de page : date de mise à jour + nombre de lignes du fichier .md créé
- Toutes les formules du rapport en LaTeX, mêmes règles KaTeX que ci-dessus.
Puis copie dans le wiki si pertinent (~/projet_zeta/Riemann_Lab.wiki/,
git push origin master). NE PAS pousser Handoff.md dans le repo principal.

DISCIPLINE GIT
- Commit "wip: checkpoint v4.1" à ~50% de contexte
- git push origin Riemann_Lab_C à ~70%
- À 80% ou "11% until auto-compact" : STOP, push, rapport court, exit

STYLE
- Débutant en Python : code commenté ligne par ligne.
- Explique chaque choix d'architecture ET sa justification mathématique avant de coder.
- Réponds en français.
