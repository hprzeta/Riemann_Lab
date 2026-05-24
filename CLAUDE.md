# Riemann_Lab — Instructions pour Claude

## Projet

Plateforme de recherche sur la fonction zêta de Riemann et l'Hypothèse de Riemann (HR).
Exploration numérique, mathématique et symbolique. Tentative de résolution de la HR.

## Règles de communication

- Toujours répondre en **français**
- Adapter le niveau d'explication : débutant → intermédiaire → expert selon le contexte
- Toujours proposer du code exécutable et testé
- Suggérer les bibliothèques les plus adaptées (mpmath, sympy, sage, flint/arb)

## Structure du projet

```
/home/riemann/projet_zeta/  ← dossier de travail local
GitHub: hprzeta
  └── Riemann_Lab           (main — stable)
  └── Riemann_Lab_IA        (dev — avec IA)
  └── Riemann_Lab_Test      (test — expérimentations)
  └── Riemann_Lab_C         (dev — avec  C : (Illinois en C/libmpfr))
```

## Stack technique

- **Python** : langage principal (numpy, scipy, mpmath, sympy, sage)
- **C++ / ASM** : optimisation des modules de calcul intensif (phase avancée)
- **Shell bash** : automatisation des tâches
- **OS** : Ubuntu 24 LTS

## Bibliothèques prioritaires

| Lib | Usage |
|-----|-------|
| `mpmath` | zêta haute précision, calcul des zéros |
| `sympy` | calcul symbolique, théorie des nombres |
| `sage` | environnement mathématique complet |
| `numpy/scipy` | calcul numérique |
| `flint/arb` | arithmétique certifiée (niveau expert) |
| `primesieve` | génération rapide de nombres premiers |

## Workflow Git

```bash
# Développement normal
git checkout Riemann_Lab_IA
# Tests
git checkout Riemann_Lab_Test
# Développement C optimisation
git checkout Riemann_Lab_C
# Stable → main
git checkout Riemann_Lab && git merge Riemann_Lab_IA
```

## Ressources de référence

- Zéros tabulés : LMFDB (lmfdb.org)
- Tables Odlyzko : référence pour vérification numérique
- arXiv math.NT : état de l'art
- SageMath docs : sagemath.org

### Phase C — lire aussi
- `src/calculs/optimisation/CLAUDE.md` — règles Illinois, ctypes, précision adaptative
- `src/calculs/optimisation/c_modules/CLAUDE.md` — PREC=170, libmpfr, Makefile

### Bases de référence
- `/home/riemann/.claude/skills/zeta-lab/references/Formules_zeta.md`
- `/home/riemann/.claude/skills/zeta-lab/references/Bibliotheques.md`

### Skills actifs
- `/home/riemann/.claude/skills/zeta-lab/SKILL.md`
- `/home/riemann/.claude/skills/zeta-lab/SKILL_phase_c.md`

## Priorités actuelles

1. Apprentissage progressif (débutant → intermédiaire → Expert)
2. Exploration numérique des zéros de zêta
3. Construction des modules Python de base
4. Automatisation future des tâches répétitives
5. Toujours enrichir les bases de référence de Formules_zeta et Bibliotheques et les skills actifs SKILL.md  SKILL_phase_c.md suivantes pour t'améliorer 

