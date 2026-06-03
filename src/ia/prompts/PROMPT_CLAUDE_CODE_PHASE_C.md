# Prompt de démarrage — Phase C / Claude Code
# À coller dans le terminal Claude Code au démarrage de session
# Mis à jour : 23 mai 2026

---

## PROMPT CLAUDE CODE — PHASE C : Illinois en C/libmpfr

```
Tu es mon assistant de recherche pour le projet Riemann_Lab (hprzeta/Riemann_Lab).
Je travaille sur la Phase C : porter l'affinage Illinois de Python/mpmath vers C/libmpfr
pour accélérer le calcul des zéros non-triviaux de la fonction zêta de Riemann.

## Contexte technique

- Branche active : Riemann_Lab_C
- Dossier cible  : ~/projet_zeta/src/calculs/optimisation/c_modules/
- Environnement  : Ubuntu, Python 3.12 (venv ~/projet_zeta/zeta_env/), CUDA 12.2 / GTX 960M
- Déjà installé  : libmpfr-dev, libgmp-dev, gcc

## Problème à résoudre

compute_zeros_v3.py atteint 3.59 z/s (zéros/seconde) mais l'affinage Illinois en mpmath
représente 80-90% du temps de calcul. La GPU ne peut pas accélérer mpmath.
Objectif Phase C : porter Illinois en C/libmpfr → ×5–10 sur l'affinage → ~15–20 z/s total.

## Ce qui existe déjà

Le fichier SKILL_phase_c.md contient :
- Le squelette de illinois_mpfr.c (fonction Z_mpfr + illinois_mpfr)
- Le Makefile
- L'interface ctypes Python (test_illinois.py)

Les formules exactes sont dans CLAUDE.md (racine du projet) et dans
src/calculs/optimisation/CLAUDE.md.

## Tâche 1 — Vérification de l'environnement

Avant toute chose, vérifie :
1. `mpfr-config --version` → doit retourner ≥ 4.0
2. `gcc --version` → doit être disponible
3. `ls ~/projet_zeta/src/calculs/optimisation/c_modules/` → le dossier existe-t-il ?
4. `git branch` depuis ~/projet_zeta/ → doit afficher Riemann_Lab_C

## Tâche 2 — Créer la structure c_modules/

Si le dossier c_modules/ n'existe pas, le créer :
```bash
mkdir -p ~/projet_zeta/src/calculs/optimisation/c_modules/
cd ~/projet_zeta/src/calculs/optimisation/c_modules/
```

Puis créer dans cet ordre :
1. z_function.h  — header avec signatures theta_double() et Z_double()
2. z_function.c  — θ(t) Stirling + Z(t) RS en double (pour la détection)
3. illinois_mpfr.h — header avec signature illinois_mpfr()
4. illinois_mpfr.c — Illinois complet en libmpfr à PREC=170 bits
5. Makefile      — cible illinois_mpfr.so
6. test_illinois.py — validation sur les 10 premiers zéros LMFDB

## Tâche 3 — Implémenter z_function.c

theta_double(t) — formule asymptotique de Stirling :
θ(t) = (t/2)·ln(t/2π) − t/2 − π/8 + 1/(48t) + 7/(5760t³)

Z_double(t) — formule de Riemann-Siegel :
Z(t) = 2·Σ_{n=1}^{N} cos(θ(t) − t·ln n) / √n,   N = ⌊√(t/2π)⌋

Ces fonctions travaillent en double précision (float64) — elles servent à la
DÉTECTION des changements de signe, pas à l'affinage.

## Tâche 4 — Implémenter illinois_mpfr.c

Voici le schéma exact de l'algorithme Illinois à PREC=170 bits :

Entrée : a_d, b_d (doubles) tels que Z(a)·Z(b) < 0, tol = 1e-12
Sortie : double (partie imaginaire du zéro affiné)

Étapes :
1. Convertir a_d, b_d en mpfr_t (mpfr_set_d)
2. Calculer Za = Z_mpfr(a), Zb = Z_mpfr(b)  [Z(t) en MPFR 170 bits]
3. Boucle MAX_ITER=100 :
   a. c = b − Zb·(b−a)/(Zb−Za)   [sécante]
   b. Zc = Z_mpfr(c)
   c. Si |b−a| < tol → break
   d. Si Za·Zc < 0 : b←c, Zb←Zc
      Sinon         : a←c, Za←Zc, Za *= 0.5   [correction Illinois]
4. Retourner mpfr_get_d(c, MPFR_RNDN)

IMPORTANT — gestion mémoire :
- Chaque mpfr_init2() doit avoir son mpfr_clear() correspondant
- Utiliser mpfr_inits2(PREC, a, b, c, ..., NULL) et mpfr_clears(a, b, c, ..., NULL)
- Les variables temporaires (num, den, diff) à l'intérieur de la boucle
  doivent être init/clear HORS de la boucle pour éviter les allocations répétées

## Tâche 5 — Compiler et tester

```bash
cd ~/projet_zeta/src/calculs/optimisation/c_modules/
make clean && make
# Doit produire : illinois_mpfr.so sans warnings
python3 test_illinois.py
# Doit afficher : écart < 1e-10 pour les 10 premiers zéros
```

## Tâche 6 — Benchmark Illinois C vs Illinois Python

Mesurer sur les 100 premiers zéros :
- Temps illinois_mpfr (C via ctypes) : X ms/zéro
- Temps illinois Python (mpmath.findroot, 35 dps) : Y ms/zéro
- Gain = Y/X → doit être ≥ 5

Sauvegarder les résultats dans benchmark_phase_c.md

## Tâche 7 — Intégrer dans compute_zeros_v3.py → v4

Modifier compute_zeros_v3.py pour créer compute_zeros_v4.py :
- Importer illinois_c depuis c_modules/
- Fallback automatique vers mpmath si illinois_mpfr.so absent
- Garder tous les benchmarks Turing-Backlund et la validation LMFDB

## Tâche 8 — Rapport de transition v3→v4

Générer analyse_problemes_v3_v4_phaseC_YYYYMMDD.md + PDF via pdflatex.
Structure identique à analyse_problemes_v2_v3_phase0.pdf :
- Date, titre, contexte
- Par problème : cause mathématique + formules + solution + gains mesurés
- Tableau récapitulatif
- Questions ouvertes (python-flint/Arb, Odlyzko-Schönhage partiel)

## Règles de communication

- Réponds en FRANÇAIS
- Code C commenté ligne par ligne en français
- Toujours distinguer : théorème prouvé / conjecture / heuristique
- Si un problème de compilation survient, diagnostique complètement avant de proposer une correction
- Signale immédiatement tout risque de segfault ou fuite mémoire dans le code C

## Références à consulter si besoin

- SKILL_phase_c.md : squelettes de code complets (dans le projet)
- CLAUDE.md racine : formules critiques (N(T), STEP, Z(t), θ(t))
- LMFDB : https://lmfdb.org/zeros/zeta/ (validation des zéros)
- libmpfr doc : https://www.mpfr.org/mpfr-current/mpfr.html

Commence par la Tâche 1 (vérification environnement) et rapporte les résultats
avant de passer à la Tâche 2.
```

---

## Notes d'utilisation

**Comment lancer Claude Code :**
```bash
cd ~/projet_zeta/
source zeta_env/bin/activate
git checkout Riemann_Lab_C
claude   # ou `claude --dangerously-skip-permissions` si tu veux éviter les confirmations
```

**Fichiers à mettre dans .claude/ (copier depuis ce projet) :**
```bash
# Depuis ton projet local
cp CLAUDE.md ~/projet_zeta/CLAUDE.md                # déjà là ✅

# Créer les CLAUDE.md locaux (télécharger depuis Claude.ai)
cp CLAUDE_optimisation.md ~/projet_zeta/src/calculs/optimisation/CLAUDE.md
cp CLAUDE_c_modules.md    ~/projet_zeta/src/calculs/optimisation/c_modules/CLAUDE.md
```

Claude Code lit automatiquement tous les CLAUDE.md dans la hiérarchie de dossiers.
Pas besoin de les référencer explicitement dans le prompt.

**MCP à activer (si disponible) :**
- Context7 → documentation libmpfr 4.x en temps réel dans Claude Code

---
*Prompt Phase C — 23 mai 2026*
