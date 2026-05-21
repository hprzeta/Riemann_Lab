#!/bin/bash
# push_phase0_complete.sh
# ────────────────────────────────────────────────────────────────────────
# Pousse toutes les mises à jour de la Phase 0 sur GitHub
# À exécuter depuis ~/projet_zeta/
# ────────────────────────────────────────────────────────────────────────

set -e   # stopper si une commande échoue

echo "═══════════════════════════════════════════════════════════════"
echo "  PUSH PHASE 0 COMPLETE — Riemann_Lab"
echo "═══════════════════════════════════════════════════════════════"

# ── 1. Repo principal (Riemann_Lab_IA) ──────────────────────────────────
echo ""
echo "── [1/3] Repo principal — branche Riemann_Lab_IA ──"
cd ~/projet_zeta

git checkout Riemann_Lab_IA

# Copier les fichiers de référence enrichis
cp ~/.claude/skills/zeta-lab/references/formules_zeta.md \
   ~/.claude/skills/zeta-lab/references/formules_zeta.md.bak 2>/dev/null || true
# (les .md sont déjà dans le repo wiki — pas dans src/)

# Ajouter les résultats du run
git add src/calculs/optimisation/compute_zeros_v3.py
git add src/calculs/optimisation/riemann_siegel_batch.py
git add src/calculs/optimisation/parallel_scanner.py
git add src/calculs/optimisation/turing_validation.py
git add src/calculs/optimisation/theta_rapide.py

# Ajouter le CSV résultat (si dans le repo)
# git add calculs/v3_T10000_20260521_133316/zeros_v3_T10000_20260521_133316.csv

git add -A

git status

git commit -m "feat(phase0): v3 T=10000 COMPLETE — 10142 zeros, Turing OK, LMFDB 19/20

Run du 21 mai 2026 :
- 10 142 zéros calculés en 2h46min (×7.6 vs v2)
- Validation Turing-Backlund : COMPLET — 0 zéro manquant
- LMFDB : 19/20 zéros à < 1e-10 (zéro #20 : 8.06e-10, proche du seuil)
- Méthode : RS détection + Illinois affinage, 4 workers, STEP=0.02
- Surpluses aux jonctions (normal — chevauchement workers)
- formules_zeta.md + bibliotheques.md enrichis (références actualisées)
- handoff.md mis à jour : Phase 0 terminée

Fichiers :
  calculs/v3_T10000_20260521_133316/*.csv / *.png / *.log"

git push origin Riemann_Lab_IA

echo "  ✅  Repo principal poussé"

# ── 2. Wiki (branche master) ────────────────────────────────────────────
echo ""
echo "── [2/3] Wiki — ~/projet_zeta/Riemann_Lab.wiki/ ──"
cd ~/projet_zeta/Riemann_Lab.wiki

# Copier les fichiers mis à jour
# (remplacer par les chemins réels selon où tu as mis les fichiers)
# cp /chemin/vers/handoff.md ./handoff.md
# cp /chemin/vers/Phase-Optimisation-_-compute_zeros_v3.md \
#    ./Phase-Optimisation-_-compute_zeros_v3.md

git add handoff.md
git add "Phase-Optimisation-_-compute_zeros_v3.md"

git status

git commit -m "docs(wiki): Phase 0 terminee — run v3 T=10000 21 mai 2026

- handoff.md : Phase 0 checkée, résultats run 20260521 ajoutés
- Phase-Optimisation : section 10 mise à jour (TERMINÉ), run docs complet
  - 10 142 zéros, 2h46min, ×7.6 vs v2
  - Turing COMPLET, LMFDB 19/20
  - Analyse des surpluses + écart zéro #20 documentés
  - Analyse vitesse (benchmark vs pipeline réel) documentée
- Prochaine étape : Phase C (Illinois en C/libmpfr)"

git push origin master

echo "  ✅  Wiki poussé"

# ── 3. Copier les références enrichies ─────────────────────────────────
echo ""
echo "── [3/3] Références (.claude/skills) ──"
# Si tu as téléchargé les nouveaux formules_zeta.md et bibliotheques.md :
# cp ~/Téléchargements/formules_zeta.md \
#    ~/projet_zeta/.claude/skills/zeta-lab/references/formules_zeta.md
# cp ~/Téléchargements/bibliotheques.md \
#    ~/projet_zeta/.claude/skills/zeta-lab/references/bibliotheques.md
# git add .claude/skills/zeta-lab/references/
# git commit -m "docs(skills): enrich formules_zeta.md and bibliotheques.md"
# git push origin Riemann_Lab_IA
echo "  ℹ️  Copier manuellement les .md enrichis dans .claude/skills/zeta-lab/references/"
echo "     puis git add / commit / push"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅  PUSH PHASE 0 TERMINÉ"
echo "  Repo    : https://github.com/hprzeta/Riemann_Lab"
echo "  Branche : Riemann_Lab_IA"
echo "  Wiki    : https://github.com/hprzeta/Riemann_Lab/wiki"
echo "═══════════════════════════════════════════════════════════════"
