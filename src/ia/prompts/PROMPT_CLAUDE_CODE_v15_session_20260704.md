# Prompt de reprise — Session v15 / Objectif 2 — 2026-07-04

## Contexte projet

Riemann_Lab — exploration numérique de l'Hypothèse de Riemann.
Branche active : `Riemann_Lab_C`.
Wiki : `~/projet_zeta/Riemann_Lab.wiki/` (branche master).

**Lire en premier : `Riemann_Lab.wiki/Handoff.md`** (état courant complet).

## État au 04/07/2026

### Versions (T=100 000 zéros, PC1 turbo, 8 workers)

| Version | Temps | Algorithme clé | Commit |
|---|---|---|---|
| v13 | 8.50 min | Illinois 2-phases, TOL 1e-12 | `77efd10` |
| v14 | 7.7 min | + cache log_n/isqrt_n 33 KB | `d4b3611` |
| **v15** ⭐ | **4.4 min** | + SEUIL_1NEWTON=20k | `adf5d2a` |

**Gain cumulé v1→v15 : ×28 600+** (21h → 4.4 min).
**Condition Objectif 2 atteinte : T=100k < 5 min ✅**

### v15 — clé de compréhension

- Biais Z_rs ≈ 0.305·t^{-5/4} → erreur 1 Newton ≈ biais² ≈ C²·t^{-5/2}
- Pour t ≥ 20 000 : erreur ≈ 4e-13 < tol=1e-12 → 1 seul Newton suffit
- 87% des 138 069 zéros T=100k ont t ≥ 20k → économie 1 Z_arb (≈1.8 ms) par zéro
- **Piège absolu :** 1 Newton fixe pour TOUT t → LMFDB 14/20 (erreur 1.75e-6 à t≈65)
- Solution : `int n_newton = (t_curr < 20000.0) ? 2 : 1;`

### Run T=5M terminé

- 10 016 377 / 10 016 473 zéros · **96 manquants**
- Cause : paires proches, pas de changement de signe sur grille Z_double
- 0 REJECT / 0 FALLBACK Illinois confirmé

## Prochain jalon : Objectif 2

**Démarrer l'agent IA autonome de recherche mathématique.**

Pré-requis satisfaits :
- SSD vault RAG : `/mnt/vault_rag` · SSD Micron 1100 256 Go · UUID 9476fad5... · ext4
- Condition numérique : T=100k < 5 min ✅

Étapes :
1. **Anthropic Skilljar** : Claude Code 101 → MCP intro → Subagents → Agent Skills
2. **MCP GitHub** : `.mcp.json` (jamais commité, dans .gitignore)
3. **ChromaDB + LlamaIndex** sur `/mnt/vault_rag`
4. **Agent** : publier site, générer rapports, envoyer résultats

**Alternative :** run T=5M avec v15 (~17h, même STEP → mêmes manquants probables).

## Fichiers clés

```
src/calculs/optimisation/c_modules/illinois_arb.c    # v15 — SEUIL_1NEWTON=20k
src/calculs/optimisation/c_modules/scan_arb.c        # cache RS identique
src/calculs/optimisation/compute_zeros_v15.py        # orchestrateur
Riemann_Lab.wiki/Handoff.md                          # état courant
Riemann_Lab.wiki/STACK.md                            # roadmap + infra
Riemann_Lab.wiki/analyse_problemes_v13_v15.md        # rapport technique
```

## Contraintes impératives

- Jamais `git add -A` sans `git status` + `grep mcp .gitignore`
- `illinois_arb.c` Phase 2 : `n_newton = (t < 20000.0) ? 2 : 1` — ne jamais revenir à 1 Newton fixe
- Turbo : `sudo scripts/zeta_turbo_on.sh` avant run · `zeta_turbo_off.sh` après
- `mpc_zeta` absent de libmpc 1.3.1 — ne pas l'utiliser
- PDF → `pdf/optimisation/` sur Riemann_Lab_IA uniquement
- SVG → `docs/images/` uniquement

---
*PROMPT_CLAUDE_CODE_v15_session_20260704.md · src/ia/prompts/ · hprzeta · 2026-07-04*
