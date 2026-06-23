> **Fichier :** ia_prompts_riemann_lab_complet.md · **Dossier :** scripts/ia_prompts/
> **Branche :** Riemann_Lab_C · **Auteur :** hprzeta · **MAJ :** 2026-06-23
> **Créé :** 2026-06-03

# 📚 Recueil COMPLET des prompts — Riemann_Lab
> Historique complet depuis le début du projet (mai → juin 2026)
> 19 sessions récupérées · Classées chronologiquement

---

## SESSION 1 — 9 mai 2026
### Prompt de démarrage projet
> Utilisé pour initialiser le contexte du projet avec Claude

```
Explore l'Hypothèse de Riemann sous trois angles :
1. Numérique : calculer les 10 000 premiers zéros non-triviaux de ζ(s) sur Re(s)=1/2
2. Mathématique : théorie progressive débutant → expert
3. Analytique : propriétés de la fonction zêta

Contraintes :
- Python 3.12, mpmath, numpy, CuPy — PAS SageMath
- Code commenté ligne par ligne
- Visualisations matplotlib
- Explications progressives avec formules LaTeX
```

---

## SESSION 2 — 17 mai 2026
### Prompt v2 → v3 (Phase 0 — 10 problèmes à corriger)
> Résultat : compute_zeros_v3.py + 5 modules + benchmark

```
Voici les 10 problèmes identifiés dans compute_zeros_v2.py :
1. Runtime 21h (trop lent)
2. θ(t) calculé via loggamma (lent)
3. Pas de calcul parallèle
4. Pas de validation Turing-Backlund
5. Précision fixe 50 dps (inutile pour détection)
6. Appels zeta() redondants
7. plt.show() bloquant
8. STEP trop grand → zéros manquants
9. Bug affichage Turing
10. Pas de Z_batch vectorisé

Crée compute_zeros_v3.py avec :
- theta_rapide.py (Stirling asymptotique)
- riemann_siegel.py (formule R-S)
- turing_validation.py (Backlund N(T))
- parallel_scanner.py (4 workers multiprocessing)
- riemann_siegel_batch.py (CPU/GPU via CuPy)
Cible : ×5 minimum vs v2
```

### Prompt Skilljar (contexte apprentissage)
```
https://anthropic.skilljar.com/
Utilise le contexte que tu as sur moi et mon projet
pour me faire un résumé de ce cours
```

---

## SESSION 3 — 19 mai 2026
### Prompt mise à jour Handoff + Second Cerveau IA

```
Mets à jour handoff.md avec :
- Convention branches : Riemann_Lab_IA / Riemann_Lab_C / Riemann_Lab_Test / main
- Stack Ollama validée : mathstral, deepseek-coder:6.7b, qwen3:4b sur /mnt/data
- Architecture Second Cerveau : LlamaIndex + ChromaDB + sentence-transformers
  ingérant wiki + PDFs (Titchmarsh, Odlyzko) + src/ + transcripts YouTube
  avec Ollama (mathstral/deepseek-math:7b) comme LLM local
```

---

## SESSION 4 — 21 mai 2026
### Prompt enrichissement Formules_zeta.md + Bibliotheques.md

```
Enrichis formules_zeta.md et bibliotheques.md avec toutes les formules
appliquées pendant les corrections v2→v3 :
- Formule N(T) corrigée (le 'e' dans T/2πe est obligatoire)
- STEP adaptatif : min(2π / (5·ln(T_max/2π)), 0.02)
- Illinois avec correction anti-stagnation
- Expansion Stirling θ(t) avec 3 termes Bernoulli
- Z(t) optimisé (un seul appel zeta())
- Stratégie précision adaptative : float64 / 25 / 35 / 50 dps
- Critère Turing-Backlund
- Conjecture GUE Montgomery
```

### Prompt validation Phase 0 complète

```
Le run v3 T=10000 est terminé. Interprète les résultats et mets à jour
toute la documentation :
- 10 142 zéros trouvés
- Validation Turing-Backlund : 0 zéro manquant
- LMFDB 19/20 (γ₂₀ à 8.06e-10 — artefact précision 35 dps)
- Runtime 2h46 (×7.6 vs v2)
Produis : handoff.md + Phase-Optimisation wiki + CLAUDE.md + push_phase0.sh
```

---

## SESSION 5 — 22 mai 2026
### Prompt réparation liens MD + règle footer

```
Répare tous les .md dont Étape-1-Calcul-des-zéros-non-triviaux
qui a le lien PDF cassé. J'ai renommé le PDF en analyse_problemes_v2_v3_phase0
(sans date). Nouvelle règle : en bas de chaque MD créé ou modifié,
ajouter la date ET le nombre de lignes.
```

---

## SESSION 6 — 23 mai 2026
### Prompt correction KaTeX + audit Formules_zeta

```
Corrige les erreurs KaTeX dans Formules-zeta.md pour le wiki GitHub.
Audite le fichier pour toutes les formules des 3 versions de compute
(v1, v2, v3) et complète les manques avec références fichiers source
et numéros de ligne.
```

> Leçon KaTeX apprise : `%` non échappé = commentaire silencieux → toujours `\%`

### Prompt génération SKILL.md + CLAUDE.md cascade

```
Génère 4 fichiers CLAUDE.md en cascade :
1. ~/.claude/CLAUDE.md — global léger
2. ~/projet_zeta/CLAUDE.md — contexte projet complet
3. src/calculs/optimisation/CLAUDE.md — Phase C local
4. src/calculs/optimisation/c_modules/CLAUDE.md — règles C

Et crée les skills : code-review + security-review
dans ~/.claude/skills/
```

---

## SESSION 7 — 24 mai 2026
### Prompt Phase C — Implémentation Illinois C/libmpfr
> Fichier : `PROMPT_CLAUDE_CODE_PHASE_C.md`
> Résultat : z_function.h/c + illinois_mpfr.h/c + Makefile + test_illinois.py

```
Tu travailles sur le projet Riemann_Lab (branche Riemann_Lab_C).
Objectif : porter l'algorithme Illinois de Python/mpmath vers C/libmpfr
pour un gain ×5–10 sur l'affinage des zéros.

Tâche 1 — Vérifier prérequis :
  mpfr-config --version  # ≥ 4.0
  gcc --version

Tâche 2 — Créer dans src/calculs/optimisation/c_modules/ :
  - z_function.h / z_function.c : θ(t) Stirling + Z(t) R-S en double
  - illinois_mpfr.h / illinois_mpfr.c : Illinois en libmpfr PREC=170 bits
  - Makefile → cible illinois_mpfr.so

Tâche 3 — Compiler sans warnings :
  make clean && make

Tâche 4 — Valider :
  python test_illinois.py
  # Cible : 10/10 erreurs < 1e-12

Critères de succès :
  - Compilation OK, zéro warning
  - test_illinois.py : 10/10 < 1e-12
  - Benchmark > 10 z/s
  - Commit sur Riemann_Lab_C uniquement
```

### Prompt connexion MCP GitHub

```
Connecte MCP GitHub dans Claude Code.
Config à écrire dans ~/projet_zeta/.mcp.json :
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "TON_TOKEN"}
    }
  }
}
Vérifie avec /mcp → doit afficher github · connected · 26 tools
```

---

## SESSION 8 — 25 mai 2026
### Prompt diagnostic liens wiki 404

```
Les liens wiki dans index.html retournent 404.
Diagnostique et corrige : les fichiers .md ont été déplacés
dans un sous-dossier exercices/cours/ → GitHub Wiki ne sert
que les fichiers à la racine du repo wiki.
Copie tous les .md à la racine, commit, push.
```

---

## SESSION 9 — 30 mai 2026
### Prompt point d'état + priorité immédiate

```
Résume en 5 points l'état actuel du projet Riemann_Lab
et dis-moi quelle est la priorité immédiate.
```

> Utiliser ce prompt à chaque reprise de session pour vérifier
> que Claude a bien compris le contexte avant de travailler.

### Prompt validation Phase C Voie B v5

```
Lis src/ia/prompts/prompt_claude_code_phase_c_voie_b_v5.md.
Travaille uniquement sur la branche Riemann_Lab_C.
Ne casse pas compute_zeros_v4.py validé.
Crée un diagnostic du biais Z_mpfr vs mpmath.siegelz,
puis propose une voie v5 pour obtenir Illinois C pur
avant tout test T=10000.
```

---

## SESSION 10 — 31 mai 2026
### Prompt versionner les skills

```
Phase 2 — Versionner les skills projet.
Déplace les 4 skills (riemann-lab, phase-c-illinois,
riemann-code-review, riemann-security-review)
de ~/.claude/skills/ vers .claude/skills/ (versionné dans le repo).

Procédure SÉCURISÉE :
1. cp (pas mv) vers .claude/skills/
2. Vérifier contenu
3. git add → commit → push
4. Seulement après : rm l'original ~/.claude/skills/

Vérif avant mv :
- .claude/skills/ pas ignoré par .gitignore
- Aucun .mcp.json dans les dossiers (git check-ignore -v)
```

---

## SESSION 11 — 1er juin 2026
### Prompt reprise session v4.1

```
On reprend la Phase C, branche Riemann_Lab_C, commit d9bb267.
v4.1 (illinois_mpfr post-fork, 4 workers, 41 z/s) est committée
mais seulement testée unitairement.

Avant tout run long, valide-la :
1. Vérif A (T=300) puis Vérif B (précision grand t)
   Critères : Turing COMPLET · LMFDB 19/20 < 1e-10 · Illinois_C pur ~100%
2. Si A et B passent → run T=1000, puis T=10000
3. Ensuite : rapport de transition v5→v4.1

Respecte les règles CLAUDE.md :
  commit auto à 50% · push à 70% · STOP à 80%
```

### Prompt nettoyage dossier Claude Code

```
Le vieux dossier projet ~/.claude/projects/-home-riemann
(sans -projet-zeta) est en double avec le bon dossier
-home-riemann-projet-zeta. Supprime l'ancien :
gio trash ~/.claude/projects/-home-riemann
Vérifie qu'il reste uniquement -home-riemann-projet-zeta.
```

---

## SESSION 12 — 2 juin 2026
### Prompt comparaison versions + v5 ultime

```
Dresse un tableau comparatif de toutes les versions
(v1, v2, v3, v4, v4.1, v5) avec leurs + et - sur :
- Vitesse (z/s)
- Précision (LMFDB score)
- Robustesse (zéros manquants)
- Parallélisme
- Goulot principal

Propose une v5 ultime qui regroupe uniquement
ce qui est ++ partout.
```

### Prompt cours animé mur de latence

```
Crée docs/animation_mur_latence.html :
- Cours animé sur le mur de latence siegelz
- Chaîne séquentielle de 27 appels visualisée
- Calculateur interactif : entrer T → voir temps estimé
- Style cohérent avec animation_theta.html existant
- Lier dans index.html (nouvelle carte)
```

---

## SESSION 13 — 2 juin 2026 (nuit)
### Prompt profiler les phases

```
Ajoute un profileur chrono_phases.py au pipeline v4.1.
Instrumente compute_zeros_v4_1.py avec des timers par phase :
  - detection
  - illinois_C
  - mpmath_petit_t
  - mpmath_fallback
  - turing

Affiche en fin de run un bloc [PROFIL PHASES] avec
temps total et % par phase. Commit sur Riemann_Lab_C.
```

---

## SESSION 14 — 3 juin 2026
### Prompt maintenance dépôts (Runbook 4 prompts)

```
Effectue dans l'ordre :

PROMPT 1 — Nettoyage wiki :
  Corriger liens cassés + pages orphelines + en-têtes/pieds

PROMPT 2 — Sync CLAUDE.md sur 4 branches :
  Vérifier hash identique Riemann_Lab_IA/C/Test/main
  Source canonique : Riemann_Lab_C

PROMPT 3 — Socle .gitignore sur 4 branches :
  Ajouter : .mcp.json, *.log, zeta_env/, calculs/,
  pdf/optimisation/Voie_b_5/.pdf_to_md/,
  pdf/optimisation/Voie_b_5/md_to_claude/
  git check-ignore -v .mcp.json sur chaque branche

PROMPT 4 — Branche orpheline inbox-ia :
  git checkout --orphan inbox-ia
  git rm -rf .
  Créer README.md minimal
  git commit + push origin inbox-ia
```

### Prompt pousser MD sur inbox-ia

```
Pousse les 26 pavés MD sur inbox-ia :
  git checkout inbox-ia
  cp ~/projet_zeta/pdf/optimisation/Voie_b_5/md_to_claude/*.md .
  git add *.md
  git commit -m "inbox: ajout 26 pavés Obj2 BrainVault ($(date +%F))"
  git push origin inbox-ia
  git checkout Riemann_Lab_IA
```

---

## Prompt universel — Mise à jour Handoff fin de session
> À coller à la fin de CHAQUE session importante

```
Mets à jour Handoff.md avec l'état exact de fin de session.

Structure :
1. En-tête : date, branche active, dernier commit hash
2. Section "État" : ce qui a été fait (tableau si > 3 items)
3. Section "Découvertes/décisions" clés
4. Section "REPRENDRE ICI" : une seule prochaine action + commande exacte
5. Pied de page : date + nombre de lignes (max 80 lignes)

Puis :
  cp ~/riemann_handoff/Handoff.md \
     ~/projet_zeta/Riemann_Lab.wiki/Handoff.md
  cd ~/projet_zeta/Riemann_Lab.wiki/
  git add Handoff.md
  git commit -m "docs(handoff): fin session $(date +%F)"
  git push origin master
```

---

## 10 leçons apprises sur les prompts Claude Code

1. **Structure obligatoire** : Tâche 1, 2, 3... — Claude suit l'ordre strictement
2. **Critères de succès chiffrés** : `< 1e-12`, `> 15 z/s`, `19/20` — pas vague
3. **Une tâche = un commit** — ne pas mélanger objectifs
4. **Mentionner la branche** dès la première ligne
5. **`/clear` entre prompts** — évite confusion, économise tokens
6. **Après `/clear`** : Claude relit CLAUDE.md auto — pas besoin de tout réexpliquer
7. **Taille idéale** : 20–50 lignes — au-delà, découper
8. **Toujours dire `git check-ignore -v .mcp.json`** avant tout push
9. **`cp` avant `mv`** pour les opérations destructrices — commit = filet de sécurité
10. **Seuil tokens** : `/clear` dès que `uncached > 50k` ou cache COLD affiché

---

---

## SESSION 15 — 3 juin 2026 (nuit)
### Prompt Option B — Fix Illinois + validation T=10000
> Résultat : illinois_refine validé 10/10 < 1e-13 · 18.65 z/s · T=10000 en 9.1 min · Turing COMPLET ✅

```
Implémente l'Option B pour corriger l'affinage Illinois en Phase C.

Contexte : illinois_mpfr.c compile sans warning mais la validation échoue
(erreur ~0.3 au lieu de <1e-12) car Z_mpfr et Z_double sont incohérents.

Solution Option B :
- Détection des changements de signe : utiliser mpmath.siegelz (Python)
- Affinage (Illinois) : utiliser illinois_mpfr.so (C/libmpfr)
- Supprimer Z_double de z_function.c (source de l'incohérence)

Tâche 1 — Modifier illinois_mpfr.c :
  Retirer toute référence à Z_double.
  L'interface C ne reçoit que (a, b, fa, fb) = bornes + valeurs déjà
  calculées par mpmath.siegelz côté Python.
  Signature cible :
    double illinois_refine(double a, double b, double fa, double fb,
                           int prec_bits, double tol, int max_iter);

Tâche 2 — Modifier le wrapper Python (compute_zeros_v4_1.py) :
  Phase détection : utiliser mpmath.siegelz (existant, validé)
  Phase affinage : appeler illinois_refine via ctypes avec (a, b, fa, fb)

Tâche 3 — Recompiler et valider :
  make clean && make
  python test_illinois.py  # cible : 10/10 erreurs < 1e-12

Tâche 4 — Benchmark :
  python benchmark_illinois.py
  # Cible : > 15 z/s

Tâche 5 — Run T=1000 puis T=10000 :
  Critères : Turing COMPLET · LMFDB 19/20 · Illinois C pur > 90% · 0 fallback

Tâche 6 — Si validation OK : commit sur Riemann_Lab_C
  "feat(phase-C): Option B — détection mpmath.siegelz + affinage illinois_mpfr"

Branche : Riemann_Lab_C uniquement. Ne pas toucher Riemann_Lab_IA.
```

> **Résultats obtenus :**
> - T=1000 : 649/649 · 16.15 z/s · Turing COMPLET · LMFDB 19/20 · Illinois C 78.7%
> - T=10000 : 10141/10143 · **18.65 z/s** · Turing COMPLET · LMFDB 19/20 · Illinois C **98.6%**
> - Durée T=10000 : **9.1 min** (vs 2h46 en v3 = ×18)
> - Commit : `581e34d` sur `Riemann_Lab_C`

---

## Prompt consolidé documentation — session 2026-06-09

```
Tâches de documentation — session 2026-06-09.
NE PAS lancer de run de calcul. Documentation uniquement.

TÂCHE 1 — Wiki : Formules_zeta.md
[§18 Benchmark Arb/FLINT — 0.77 ms vs 21.13 ms, ×27, erreur < 2.2e-16]

TÂCHE 2 — Wiki : Bibliotheques.md
[§12 mise à jour VALIDÉ ×27 — tableau paramètres + pattern arb_hardy_z]

TÂCHE 3 — Skill : ~/.claude/skills/phase-c-illinois/SKILL.md
[Section "Mur de latence — RÉSOLU (2026-06-09)" ajoutée]

TÂCHE 4 — Wiki : STACK.md
[Tableau progression v1→v5 — ×1 260 total, ~1 min vs 21h]

TÂCHE 5 — docs/index.html (branche Riemann_Lab_IA)
[Section PROGRESSION V1→V5 HTML après FIN SECTION PERFORMANCES]

TÂCHE 6 — scripts/ia_prompts/ia_prompts_riemann_lab_complet.md
[Résultats session + prompt consolidé]
```

## Session 2026-06-09 — résultats clés

- Speedup Arb : ×27 (0.77 ms vs 21.13 ms)
- T_total estimé v5 : ~15 min (vs 7h mpmath)
- Animations créées : zeros_non_triviaux, equation_fonctionnelle,
  series_dirichlet, produit_eulerien, plan_complexe, gamma,
  distribution_zeros + enrichissement theta
- Header SVG `header_riemann_lab.svg` déployé README + index
- `arb_wrapper.py` intégré `compute_zeros_v4_1.py` (commit `b563db2`)
- Commits : wiki `f9e7061` · Riemann_Lab_C `8358cdb` · Riemann_Lab_IA (ce commit)

---

## Session 2026-06-10 après-midi — STEP v3 0.05/0.010 + run T=100 000 v3

### Contexte de reprise

Runs T=100 000 du matin : tous STEP=0.1 ancien code → dernier résultat 138 050 zéros / 17 manquants / Turing INCOMPLET. Résultat v2 (STEP adaptatif 0.1/0.05/0.02) : 138 039 zéros / 68 manquants. Cause identifiée : gap min mesuré 0.01940 à t=66678, prouvant que STEP=0.02 est insuffisant.

### Fix appliqué — commit `181fdd1`

`step_pour_t()` corrigé :
- Avant (v1) : t<5k→0.1 / t∈[5k,50k]→0.05 / t>50k→0.02
- Après (v2) : t<5k→0.05 / t≥5k→0.010 (cap uniforme ÷5 et ÷2)

### Actions réalisées en session

| Action | Résultat |
|---|---|
| Vérification code STEP adaptatif (TÂCHE 1) | ✅ commit `181fdd1` en place |
| Lancement run T=100k v3 (TÂCHE 2) | PID 311769 · log `run_T100k_step_adaptatif_20260610_1642.log` |
| Formules_zeta.md §23 (TÂCHE 3a) | STEP v3 0.05/0.010 · résultats T=100k v1/v2 · v3 EN COURS |
| Bibliotheques.md §12 (TÂCHE 3b) | Tableau runs complété (v2=68 manquants, v3 EN COURS) |
| STACK.md (TÂCHE 3c) | STEP v3 corrigé · progression v4.1+Arb mise à jour |
| JOURNAL.md (TÂCHE 3d) | Entrée 16h42 ajoutée |
| SKILL phase-c-illinois (TÂCHE 3e) | STEP v3 + tableau T=100k v1/v2/v3 |
| Handoff.md (TÂCHE 5) | État run v3 EN COURS · historique runs |

### Résultats runs T=100 000

| Version | STEP | Zéros | Manquants | Turing |
|---|---|---|---|---|
| v1 | 0.1 fixe | 137 904 / 138 069 | 356 | ❌ |
| v2 | 0.1/0.05/0.02 | 138 039 / 138 069 | 68 | ❌ |
| v3 (0.05/0.010) | TUÉ — régression ×11 vitesse | — | — |
| **v4 (δ/3)** | **EN COURS — PID 328675** | **—** | **attendu ✅** |

---

## Session 2026-06-10 après-midi/soir — Prompts A–D

### Prompt A — Fix STEP δ(t)/3 + relance run T=100k

```
CONTEXTE — Régression vitesse run T=100 000 (10 juin 2026)
Run en cours (PID 311769) : vitesse ~0.5 z/s.
Cause : STEP=0.010 → 5M points Z_batch (vs ~460k avec δ/3).

TÂCHE 1 — Tuer run : kill 311769
TÂCHE 2 — Corriger step_pour_t() :
  STEP = max(0.05, min(0.5, 2π/(3·ln(t/2π))))
  → commit d2f62c1 Riemann_Lab_C
TÂCHE 3 — Relancer nohup → log run_T100k_step_delta3_20260610_1717.log
TÂCHE 4 — Commit + push Riemann_Lab_C
TÂCHE 5 — Handoff.md : run v4 EN COURS (PID 328675)
Vérifier vitesse après 5 min (> 15 z/s).
```

### Prompt B — PDFs analyse v4→v4.1 et v4.1→v5

```
TÂCHE — Générer les 2 PDFs manquants dans l'ordre logique

PDF 1 — analyse_problemes_v4_v4_1.pdf
  Créer analyse_problemes_v4_v4_1.md (wiki) :
  - P1 : Z_double incohérent → Option B (fa,fb) Python — commit 581e34d
  - P2 : .so pré-fork → post-fork — commit d9bb267
  - P3 : Z_batch N_max fixe → Z_vect_correct masque — commit 50837f7

PDF 2 — analyse_problemes_v4_1_v5.pdf
  Compléter analyse_problemes_v4_1_v5.md avec résultats 10 juin :
  - Arb ×27 — commit b563db2
  - STEP δ/3 — commit d2f62c1
  Générer via build_pdf_riemann.sh (xelatex, DejaVu Serif)

Résultat : 4 PDFs côte à côte dans pdf/optimisation/
```

### Prompt C — Documentation finale v5 (après résultat run)

```
CONTEXTE — Run T=100 000 v4 (STEP=δ/3) terminé.
Résultats : [à compléter après notification Monitor]

TÂCHE 1 — Formules_zeta.md §23.4 : remplacer "EN COURS" par chiffres réels
TÂCHE 2 — STACK.md : ligne v4 (δ/3) avec résultats mesurés
TÂCHE 3 — Bibliotheques.md §12 : tableau runs complet
TÂCHE 4 — JOURNAL.md : entrée finale 10 juin (résultats + commits)
TÂCHE 5 — Handoff.md : prochaine action = v6 (scan_arb.c + W=8)
TÂCHE 6 — SKILL phase-c-illinois : résultats T=100k v4
TÂCHE 7 — Push wiki + Riemann_Lab_C
```

### Prompt D — v6 scan_arb.c + W=8 workers (après /clear)

```
CONTEXTE — v5 validée (T=100k Turing COMPLET)
Objectif v6 : ~27 min T=100k (vs ~105 min v5), 0 manquant

LEVIERS :
  L1 — W=8 : N_WORKERS = min(8, cpu_count()) — 1 ligne, gain ×1.3
  L2 — scan_arb.c : détection C pure (×7.5 vs Python)
       scan_zeros_arb(t_min, t_max, step, out_a, out_b, out_fa, out_fb, n_max)
       Backend : arb_fpwrap_cdouble_hardy_z en boucle C
  L3 — Cache fa/fb : scan retourne Z(a)/Z(b) → illinois_refine direct, 0 recalcul
  L4 — Segmentation N(T) : N(b)-N(a) égaux par worker (vs 1/√t)

ESTIMATION :
  v5 ~105 min × W=8 (×1.3) × scan_arb (×2.0) × cache (×1.5) → ~27 min

TÂCHE 0 — Benchmark chrono par phase T=5000 (identifier vrai goulot)
TÂCHE 1 — c_modules/scan_arb.c + ctypes binding
TÂCHE 2 — Intégration compute_zeros_v4_1.py
TÂCHE 3 — Test T=10k v6, Turing COMPLET avant T=100k
```

---

## Session 2026-06-10 soir / 2026-06-11 — Prompts E–L

### Prompt E — Fix régression STEP + relance run T=100k (10 juin soir)

```
CONTEXTE :
Run T=100k STEP=δ/3 (PID 311769) tué — régression ×40 (0.5 z/s)
Cause : STEP=0.02 → 5M points détection → ×40 plus lent

TÂCHE 1 — Tuer run régressif : kill 311769
TÂCHE 2 — Corriger step_pour_t() :
  → STEP = 0.010 fixe (gap-safe mesuré g_min=0.019 à t=66 678)
TÂCHE 3 — Relancer T=100k
  nohup bash -c 'printf "100000\nO\n" | python \
    src/calculs/optimisation/compute_zeros_v4_1.py \
    2>&1 | tee calculs/run_T100k_step_delta3_$(date +%Y%m%d_%H%M).log' &

RÉSULTAT : PID 328675, log run_T100k_step_delta3_20260610_1717.log
  Worker 0 [14-6700] : 27 z/s ✅
  Worker 3 [56700-100k] : 4.3 z/s (N_termes RS bottleneck)
```

### Prompt F — Documentation pendant run (10 juin 19h-22h)

```
TÂCHE 1 — ia_prompts_riemann_lab_complet.md : section prompts A-D
TÂCHE 2 — Bonnes-Pratiques-Claude-Code.md :
  + STEP=0.010 règle absolue
  + Monitor Claude Code timeout 1h
  + /clear avant prompt v6
TÂCHE 3 — Guide-Git-GitHub.md :
  + Pattern run longue durée (nohup + printf + tee)
TÂCHE 4 — plan_v6_riemann.md (wiki) créé
TÂCHE 5 — Skill riemann-lab mis à jour
COMMIT : dc0be02 (wiki), a925999 (Riemann_Lab_C)
```

### Prompt G — Analyse résultat run + PDFs (10-11 juin)

```
CONTEXTE :
Monitor déclenché 19h11 — run T=100k STEP=δ/3 terminé
Turing : INCOMPLET — 2072 manquants ❌
STEP=δ/3≈0.22 >> g_min=0.019 (distribution GUE)

TÂCHE 1 — PDFs analyse :
  analyse_problemes_v4_v4_1.md + PDF ✅
  analyse_problemes_v4_1_v5.md complété + PDF ✅
TÂCHE 2 — Commit + push
```

### Prompt H — Prompt D v6 corrigé (10 juin 19h30, après /clear)

```
ÉTAT :
  STEP=0.1   → 17 manquants ❌
  STEP paliers → 356 manquants ❌
  STEP=δ/3   → 2072 manquants ❌ (pire — GUE gaps << δ)
  RÈGLE : STEP = 0.010 fixe — gap-safe empirique

TÂCHE 0 — Benchmark phases T=5000 :
  illinois_C : ~85% · détection : ~3% · overhead : ~11%

TÂCHE 1 — Créer scan_arb.c :
  scan_zeros_arb(t_min, t_max, step, brackets_a, brackets_b, fa, fb)
  arb_fpwrap rejeté : 175 µs/pt scalaire (×32 trop lent vs numpy)
  Z_double retenu : ~1-2 µs/pt (×88 vs arb)

TÂCHE 2 — Intégrer scan_arb + STEP=0.010 fixe
TÂCHE 3 — Segmentation N(T) équilibrée (remplace 1/√t)

RÉSULTATS (commit d3b4de0) :
  T=5 000  : 115 z/s, Turing COMPLET ✅
  T=10 000 : 75 z/s, Turing COMPLET ✅
  T=100 000: 138 069 zéros, 0 manquant, Turing COMPLET ✅ (~130 min)
  illinois_C = 83% (N_termes RS ≈ √(t/2π))
```

### Prompt I — Prompt unique post-v6 (11 juin, 19 tâches)

```
CONTEXTE : v6 validée (T=100k, 0 manquant, commit d3b4de0)

19 TÂCHES :
  0.  Nommage compute_zeros_v6.py
  1.  Session reconstituée 10 juin
  2.  Récap session PDF → BrainVault
  3.  JOURNAL.md
  4.  STACK.md
  5.  Formules_zeta.md §19/§20/§21
  6.  Bibliotheques.md
  7.  Skills phase-c-illinois + riemann-lab
  8.  Bonnes-Pratiques + Guide-Git
  9.  analyse_problemes_v5_v6.md + PDF
  10. analyse_problemes_v4_1_v6_synthese.md + PDF
  11. Etape-1 section "Suite optimisations v5→v6"
  12. ORGANISATION_FICHIERS.md
  13. ia_prompts archivé
  14. animations gaps_gue + ntermes_rs
  15. index.html 2 pavés + stats 138 069 zéros
  16. plan_v6_riemann.svg → docs/images/
  17. Handoff.md local
  18. PDFs → Proton Drive (3 nouveaux)
  19. Push wiki + Riemann_Lab_IA + Riemann_Lab_C + main

LEÇONS :
  STEP=δ/3 → 2072 manquants (GUE gaps << δ, ratio ~30)
  arb_fpwrap : 175 µs/pt inutilisable pour scan
  illinois_C = 83% = vrai bottleneck (N_termes RS ≈ √(t/2π))
```

### Prompt J — Workflow SVG + maths v7 (11 juin)

```
TÂCHE 1 — workflow_post_version_riemann_lab.svg créé
  10 blocs : 0-Nommage → ... → 10-Push final
  → docs/images/workflow_post_version_riemann_lab.svg

TÂCHE 2 — Maths v7 expliquées :
  Z(t) = 2·Σ cos(θ(t)-t·ln n)/√n, N(t)=⌊√(t/2π)⌋
  Coût : t_appel(t) ≈ 1.1 × N(t) ms
  Phase 1 (bracketing) : N_fast=N(t)/4, 64 bits, tol 1e-4
  Phase 2 (polish) : N_full=N(t), 116 bits, tol 1e-12
  Gain théorique : ×4.6 → ~28 min T=100k
```

### Prompt K — Nettoyage prompts + inbox-ia (11 juin)

```
TÂCHE 1 — Consolidation prompts lieu unique
  ia_prompts_riemann_lab_complet.md : ajout E→K
  src/ia/prompts/*.md absorbés + supprimés
TÂCHE 2 — Régénération inbox_ia_liens.md
TÂCHE 3 — Push inbox-ia nouveaux docs
TÂCHE 4 — PDF maths v7 "Pourquoi c'est lent et comment y remédier"
TÂCHE 5 — animation_illinois_adaptatif.html
```

### Prompt L — v7 N_termes adaptatif illinois_mpfr.c (11 juin, après /clear)

```
CONTEXTE : v6 VALIDÉE : T=100k, 138 069 zéros, 0 manquant, Turing COMPLET ✅
Bottleneck : illinois_C = 83%, N_termes RS ≈ √(t/2π)
  t=77k → N=111 → 123 ms/appel → 4.3 z/s → 130 min T=100k

OBJECTIF v7 : Illinois adaptatif 2 phases
  N_fast = max(5, N(t)/4)
  t_zéro_v7 = 8 × N_fast × 0.08ms + 2 × N(t) × 1.1ms
  Gain ×4.6 → ~28 min T=100k estimé

TÂCHES :
  0. Benchmark chrono phases T=5000 (calibrer iter_switch)
  1. illinois_mpfr.c : illinois_refine_adaptive() 2 phases
  2. illinois_mpfr.c : Z_rs_mpfr_ntermes(t, N_termes, prec)
  3. compute_zeros_v6.py : intégration + fallback
  4. Compilation + test unitaire γ₁ ≈ 14.1347
  5. Benchmark T=5000 v6 vs v7
  6. Test T=10 000 (critère : 0 manquant, Turing COMPLET)
  7. Run T=100 000 v7 (si T=10k validé)
  8. Commit v7

RÈGLES ABSOLUES :
  STEP = 0.010 fixe
  Charger .so POST-FORK
  0 manquant + Turing COMPLET sur T=10k avant T=100k
```

---

*ia_prompts_riemann_lab_complet.md · scripts/ia_prompts/ · Riemann_Lab_IA · hprzeta · MAJ 2026-06-03 · 9 juin 2026 · 10 juin 2026 (soir) · 11 juin 2026 · ~760 lignes*

---

## Prompt M — Fix sudoers + run v9 turbo (2026-06-12)

**Objectif :** fix sudoers zeta_turbo + re-run v9 avec turbo → cible 17 min.

**Résultat :**
- sudoers `/etc/sudoers.d/zeta_turbo` installé ✅
- Note Ubuntu 24.04 : sysctl = `/usr/sbin/sysctl` (pas `/sbin/`)
- Run lancé PID 104516 · log `run_T100k_v9_turbo_20260612_144428.log`
- Durée mesurée : 26.6 min · 86.5 z/s
- Gain turbo : ×1.05 (bottleneck MPFR/mémoire — projection 17 min invalidée)

---

## Prompt N — Documentation post-v9 tout-en-un (2026-06-12)

**Objectif :** intégrer tous les résultats v9 turbo (12 tâches).

**Tâches :** JOURNAL · STACK · Formules_zeta §26 · Bibliotheques §13 ·
SKILL phase-c-illinois · analyse_problemes_v8_v9.md · index.html ·
push wiki + Riemann_Lab_C + Riemann_Lab_IA · prompts · Handoff.md local

---

---

## Session 2026-06-13 — Run v12 + documentation complète

### Résultats v12

- Version : v12 `illinois_refine_arb` (Illinois hybride 2-phases)
- ~138 080 zéros · 0 manquant · 8.8 min (avec turbo) · ×16.9 vs v10 (benchmark T=10k) · ×2.69 direct T=100k
- Turing-Backlund : COMPLET ✅ · LMFDB : 20/20 ✅
- Algorithme : Phase 1 Z_rs_double (~0.015 ms) → bracket 1e-6 · Phase 2 2 Newton Z_arb (~3.5 ms)

### Prompt documentation v12 utilisé

Prompt multi-tâches (15 tâches) envoyé depuis Claude.ai web → Claude Code.
Tâches : 2 rapports d'analyse créés, 9 pages wiki mises à jour, site mis à jour, Handoff réécrit.

---

## Session 23/06/2026

- Alias `zeta-progress` vérifié dans `~/.bashrc` (préexistant depuis le 17/06, pas créé ce soir)
- Run T=500 000 : trou de couverture au pivot PC1/PC2 diagnostiqué (`zeta_distribute.py` sans
  overlap à la frontière, contrairement à l'overlap interne `OVERLAP=0.5` entre workers) — fix
  `OVERLAP_PIVOT=2.0` appliqué (**toujours actif, pas annulé**) ; résultat seul : régression à
  8 manquants (vs 5 référence) par cascade des frontières internes des workers
  (`_partitionner_adaptatif()` recalculée entièrement avec le nouveau `T_MAX`)
- `MARGE_SECURITE` 2.0→3.0 dans `_step_adaptatif()` (`compute_zeros_v13.py`), synchronisé sur
  PC2 par `scp` direct
- Run relancé 22:27:23 (overlap + marge×3) — en cours au moment de cette note, ETA estimée
  ~23:13-23:16 (pas encore terminé)

---

*ia_prompts_riemann_lab_complet.md · scripts/ia_prompts/ · Riemann_Lab_C · hprzeta · MAJ 2026-06-03 · 9 juin 2026 · 10 juin 2026 (soir) · 11 juin 2026 · 12 juin 2026 (Prompts M-N v9 turbo) · 13 juin 2026 (v12 documentation complète) · **23 juin 2026 (run #6 T=500000 en cours, overlap pivot + marge×3)** · 851 lignes*
