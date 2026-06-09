> **Fichier :** ia_prompts_riemann_lab_complet.md · **Dossier :** scripts/ia_prompts/
> **Branche :** Riemann_Lab_IA · **Auteur :** hprzeta · **MAJ :** 2026-06-03

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

*ia_prompts_riemann_lab_complet.md · scripts/ia_prompts/ · Riemann_Lab_IA · hprzeta · MAJ 2026-06-03 · 9 juin 2026 · ~500 lignes*
