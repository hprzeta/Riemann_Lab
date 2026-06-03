# Riemann_Lab — Journal de bord

> 📓 **Fichier append-only.** On n'allège jamais ce fichier : on **ajoute** un pavé daté
> en haut à chaque session. Il n'est *pas* relu en entier au démarrage (utiliser
> `grep` ou demander à Claude de chercher dans ce fichier précis).
>
> Le plus récent est **en haut**. Format de pavé : `## AAAA-MM-JJ — HHhMM — titre — commit`.
---

## 2026-06-02 — après-midi — v4.2 finition hybride : précision parfaite, mais goulot = `siegelz` — commit `0fa22c2`

**Résultat :** la finition hybride (Illinois_C pré-affine + raffinage mpmath) atteint la
**précision parfaite** ($\text{Écart}_P = 0.00$ vs LMFDB) à toutes les hauteurs. Mais aucune
optimisation algorithmique du raffinage n'est possible : le goulot est **`mpmath.siegelz`
lui-même** (~296 ms/appel à $t\approx 9000$), pas le solveur. Newton est **réfuté** (plus lent
qu'Illinois). Décision de livrable en attente (vérifier HR vs cataloguer les positions).

### Vérif A — comptage (✅ COMPLET)
- 138/138 zéros · Turing **COMPLET** · LMFDB 19/20 < 1e-10 (zéro #20 = cas limite 8.06e-10).
- Illinois_C 0 % à T=300 : **normal** (tous les zéros à $t<300 = $ seuil → 100 % fallback mpmath).

### Vérif B — précision des positions (3 itérations)
| Itération | Méthode finale | Précision (Écart_P) | Vitesse ×4 | Verdict |
|---|---|---|---|---|
| B v1 | Illinois_C **pur** (racine de $Z_{\text{mpfr}}$) | 1e-4 à 1e-2 ❌ | 41 z/s | rejeté (positions) |
| B v2 | Illinois + polish `findroot` dps=30 | **0.00** ✅ | 0.5 z/s | juste mais lent |
| B v3 | Newton analytique dps=25, 5 pas | **0.00** ✅ | **0.4 z/s** | **plus lent qu'Illinois** |

### Cause racine confirmée (leçon décisive)
- Illinois_C pur trouve les zéros de la RS **tronquée** $C_0+C_1$ → biais de **position**
  $|\gamma_{\text{mpfr}}-\gamma| \approx |R(\gamma)|/|Z'(\gamma)|$, soit 1e-4 (croisement raide)
  à 1e-2 (croisement plat). Structurel, **pas un bug** (série asymptotique).
- Newton ne gagne **pas** : `siegelz(t, derivative=1)` ne rend pas $Z'$ gratuitement —
  $\zeta'(s) = -\sum \ln(n)/n^s$ a des poids log ⇒ série plus lente ⇒ $Z'$ **plus cher** que $Z$.
  Newton (2 appels/pas, dont $Z'$) ≈ Illinois (1 appel/pas, 27 itér) en coût total.
- **Goulot = vitesse intrinsèque de `mpmath.siegelz` à grand $t$**, pas le nombre d'itérations.
  → aucune optimisation algorithmique du raffinage tant qu'on passe par `siegelz`.

### Distinction comptage / position (clé pour trancher)
- **Vérifier HR jusqu'à T** = comptage Turing ($n_{\text{calc}} = N(T)$). Indépendant de la
  précision des positions → **Illinois_C pur (41 z/s, ~5 min pour T=10000) suffit.**
- **Catalogue de positions < 1e-10** = exige le polish lent (~7 h pour T=10000)… mais ce
  catalogue **existe déjà** (run v2/v3 : CSV 10 142 zéros, 50 dps).

### Estimation de temps (×4 workers, mesurée/extrapolée)
| Run | Zéros | Temps ×4 | Note |
|---|---|---|---|
| T=300 | 138 | ~60 s (mesuré) | tout fallback mpmath |
| T=1000 | ~396 | ~16 min | validation complète faisable |
| T=10000 | ~10 142 | ~7 h | run de nuit si catalogue voulu |

### Git
- `0fa22c2` (`Riemann_Lab_C`) — feat(v4.1) : finition Newton analytique dps=25 après Illinois_C
  (2 files, +575 / −42). Poussé : `71e6774..0fa22c2`.

### Documentation
- `Formules_zeta.md` enrichi (→ ~826 lignes) : §5.6 (erreur de position, perturbation 1ᵉʳ ordre),
  §6.4 (3 architectures d'affinage), §6.5 (finition Newton : ordre 2, dérivée analytique, `dps`
  vs LMFDB absolu), **§6.5.5 (mesure : Newton réfuté, goulot `siegelz`)**, §11.1–11.2 (comptage
  vs position + condition de validité détection).

### Prochaine action (DÉCISION DE LIVRABLE, pas technique)
1. **Si objectif = vérifier HR jusqu'à T=10000** → lancer Illinois_C pur (~5 min), Turing COMPLET.
2. **Si objectif = catalogue positions < 1e-10** → soit réutiliser le CSV v2/v3 existant,
   soit run de nuit polish T=10000 (~7 h).
3. Ne **pas** chercher d'autre solveur : le goulot est `siegelz`, pas l'algorithme.
4. (À valider avant tout abaissement de `dps` : tester sur $t\approx 9900$, jamais sur T=1000 —
   critère LMFDB absolu, cf. §6.5.3.)

---

## 2026-06-01 — nettoyage skill zeta-lab (4 branches) + sécurisation .mcp.json

**Résultat :** ancien skill `zeta-lab` (cassé) retiré de Git sur les 4 branches ;
faille `.mcp.json` non ignoré découverte et corrigée sur `main` et `Riemann_Lab_Test`.

### Skills
- Audit `git ls-tree` : `zeta-lab` était commité sur les 4 branches.
- Retiré via `git rm -r` + commit + push sur chacune :
  C (`2a4cde4`, + ancien prompt v4.1 retiré / prompt findroot ajouté) ·
  IA (`e68ebca`) · main (`5c08cf0`) · Test (`c3396b7`).
- Les BONS skills (riemann-lab, phase-c-illinois, riemann-code-review,
  riemann-security-review) sont toujours dans `~/.claude/skills/`,
  pas encore versionnés → Phase 2 du plan.

### Sécurité — .mcp.json
- Découvert : le `.gitignore` divergeait entre branches ; `.mcp.json` n'était
  PAS ignoré sur `main` ni `Riemann_Lab_Test`.
- `git ls-files | grep mcp` = VIDE partout → le token n'a JAMAIS été commité.
  Pas de révocation nécessaire (contrairement à l'incident du 31 mai).
- Corrigé : `echo ".mcp.json" >> .gitignore` sur main et Test → `PROTÉGÉ ✅`.

### Leçon durable
Le `.gitignore` n'est pas synchronisé entre branches. Après toute manip
multi-branches : vérifier `git check-ignore .mcp.json` sur CHAQUE branche.

---

## 2026-05-31 — après-midi — fix findroot appliqué (NON validé) — commit `7f5bd02`
- Affinage : callback ctypes illinois_c_exact → mpmath.findroot(solver="illinois")
- dps=35 global, DPS_AFFINAGE=15 local · plus de dépendance au .so
- Objectif : vrai parallélisme ×4. ⚠️ PAS ENCORE validé (aucun run effectué).
- Reprise : lancer Vérif A (T=300) du prompt prompt_v4_1_findroot_20260531.md.

---

## 2026-05-31 — 02h00 — v4.1 validée (justesse) — commit `368d090` (`Riemann_Lab_C`)

**Résultat :** v4.1 juste mais lente (1.1 z/s). Le goulot a migré de la détection vers l'affinage.

### Point d'arrêt N°1 — validation détection `Z_vect_correct`

Comparaison `Z_vect_correct(t)` (vectorisée) vs `mpmath.siegelz(t)` (référence) sur 4 plages.
Critère : mêmes changements de signe (CS) ⇒ aucun zéro raté.

| Plage | Écart max | Écart moyen | CS vect | CS mpm | Désaccords | Gain |
|---|---|---|---|---|---|---|
| t ∈ [14, 100]     | 1.38e-02 | 4.18e-03 | 29  | 29  | **0 ✅** | ×73 |
| t ∈ [300, 400]    | 1.50e-03 | 8.49e-04 | 64  | 64  | **0 ✅** | ×4379 |
| t ∈ [3000, 3100]  | 2.81e-04 | 1.46e-04 | 98  | 98  | **0 ✅** | ×9854 |
| t ∈ [9900, 10000] | 1.19e-04 | 1.07e-04 | 117 | 117 | **0 ✅** | ×19568 |

L'écart numérique max décroît avec t (1.4e-2 → 1.2e-4) : c'est l'erreur résiduelle
théorique de RS tronquée à C0+C1, en $O(t^{-3/2})$. **Ce n'est pas un bug.** Pour la
détection seul le **signe** compte ⇒ 0 désaccord = détection fiable.

### Bug corrigé au point d'arrêt N°1

Première version `Z_batch` : **359 désaccords** (zéros ratés). Cause : `N_max` FIXE
$= \lfloor\sqrt{t_{\max}/2\pi}\rfloor + 1$ pour TOUS les points du batch. Or RS exige
$N(t) = \lfloor\sqrt{t/2\pi}\rfloor$ propre à chaque $t$ ; les termes $n > N(t)$ faussent
le signe. Correction `Z_vect_correct` : masque booléen `mask[k,n] = (n ≤ N(t_k))` par
ligne ⇒ chaque ligne n'accumule que ses $N(t_k)$ termes exacts.

### Point d'arrêt N°2 — run T=300

| Critère | v5 (réf.) | v4.1 | OK ? |
|---|---|---|---|
| Zéros trouvés | 138 | 138 | ✅ |
| Turing COMPLET | ✅ | ✅ | ✅ |
| LMFDB 19/20 < 1e-10 | ✅ | ✅ | ✅ |
| Illinois_C pur | ~100 % | 100 % | ✅ |
| Vitesse | ~1 z/s | **1.1 z/s** | ⚠️ |

### Diagnostic vitesse — cause racine = affinage Illinois

Décomposition du temps pour T=300 :
$$\underbrace{138}_{\text{zéros}} \times \underbrace{102}_{\text{appels Illinois}} \times \underbrace{1.5\ \text{ms}}_{\text{siegelz @ dps=35}} \approx 21\ \text{s séquentiel} \times \frac{1}{1.84} \approx 122\ \text{s}$$

- Callback ctypes `illinois_c_exact` appelle `mpmath.siegelz` à dps=35 → 1.5–10 ms/appel.
- Sérialisation partielle du callback ⇒ gain parallèle **×1.84** au lieu de ×4
  (test : `Pool(sleep)`=×3.9 OK, `Pool(worker_chunk)`=×1.84).

### Fix proposé (à appliquer prochaine session — pas encore fait)

Remplacer le callback ctypes par `mpmath.findroot(siegelz, solver="illinois")` à
**dps=15** dans les workers ⇒ vrai parallélisme ×4 ; dps=15 suffit pour `tol=1e-12`.
Estimation T=10000 → ~6 z/s. Contrepartie : méthode `mpmath` au lieu de `Illinois_C`.

### Fichiers ajoutés (commit `368d090`)
- `src/calculs/optimisation/compute_zeros_v4_1.py`
- `src/calculs/optimisation/test_v4_1_T300.py`
- `src/calculs/optimisation/test_zbatch_validation.py`
- `src/ia/prompts/prompt_claude_code_phase_prompt_v4.1.md`

### 🔐 Incident sécurité résolu

Un ancien GitHub PAT était commité en clair dans `.mcp.json:7` (commit `b2f579a`).
GitHub Push Protection (GH013) bloquait le push.

**Leçon clé :** `.gitignore` empêche les futurs commits mais **ne purge pas le passé** —
un secret dans l'historique reste détectable tant que le commit existe.

Résolution (dans l'ordre) :
1. Révocation de l'ancien token sur GitHub (geste n°1, le plus urgent).
2. `git filter-repo --path .mcp.json --invert-paths` → effacé de 220 commits.
3. Vérification : `git log --all --oneline -- .mcp.json` = VIDE.
4. `git push --force` → blocage levé (`afcaab3`).
5. `main` vérifié : intact.
6. Nouveau token régénéré, remis dans `.mcp.json` **local** (ignoré par `.gitignore`).

> **Ne jamais suivre le lien « unblock-secret » de GitHub.** Un secret exposé = secret mort.

---

## 2026-05-29 — 21h30 — Voie B validée — commit `b8018c0` (`Riemann_Lab_C`)

**Résultat :** `compute_zeros_v5.py` valide **Illinois_C pur 100 %**, biais `Z_mpfr` < 1e-13.

### Fichiers créés / modifiés
| Fichier | Rôle |
|---|---|
| `compute_zeros_v5.py` | Script principal v5 — wrapper `mpmath.siegelz` |
| `illinois_mpfr.c` / `.h` | Callback Python/C `illinois_mpfr_cb` |
| `illinois_mpfr.so` | Recompilé |
| `illinois_pyZ.py` | Wrapper Python pour `Z_mpfr` via mpmath |
| `test_illinois_v5.py` | Validation Voie B (20/20) |
| `docs/phase_c_voie_b_v5_plan.md` | Livrable Phase C Voie B |

### Validation
```
Run T=80 (21 zéros) :
  Illinois_C pur    : 100 %  ✅  (v4 était à 0 %)
  Turing-Backlund   : COMPLET ✅
  LMFDB             : 19/20 ✅  (zéro #20 = cas limite 8.06e-10)
  Durée             : 25.8 s
test_illinois_v5.py : 20/20 ✅ · biais Z_mpfr < 1e-13 (avant ~9e-3)
```

**Note LMFDB 19/20 :** le zéro #20 (γ₂₀ ≈ 77.1448) est un cas limite,
$|Z(\gamma_{20})| = 8.6\text{e-}15$ — vrai zéro confirmé. L'écart vient de la précision
de la valeur de référence (15 décimales) ou de la limite de `siegelz` à 35 dps.
**Pas un échec de méthode.**

### Diagnostic du biais RS (avec Copilot / GPT-4.5 + Claude)

Décomposition sur t ∈ [300, 650] :
```
theta  : max 2.3e-13  ✅ theta_double parfait
sum    : max 3.26e-01 ✅ normal sans correction C0+C1
fullRS : max 1.5e-03  ⚠️ biais résiduel structurel
```

**Conclusion :** le biais **n'est pas un bug** mais une **limite mathématique** — RS
tronquée à C0+C1 plafonne à ~1e-3.

| Méthode | Précision |
|---|---|
| RS sans correction | ~1e-1 |
| RS + C0 | ~1e-2 |
| RS + C0 + C1 | ~**1e-3** (état alors) |
| RS + 3–5 termes | ~1e-8 |
| `mpmath.siegelz` | ~1e-12 |

Patches tentés et annulés : Patch 1 (π manquant dans dPsi) → biais 4e-2 ❌ ;
Patch 2 (C1 analytique) → biais 2e-2 ❌ ; `git checkout z_function.c` → retour origine ✅.

**Solution retenue :** wrapper Python/C appelant `mpmath.siegelz(t)` depuis le `.so`
(`mpc_zeta` absent de libmpc 1.3.1).

### Phase C — état validé à cette date
- `c_modules` compile : `make clean && make` → `illinois_mpfr.so` OK.
- `benchmark_illinois.py` : gain isolé C/libmpfr **×48.73** sur t≈500–638.
- 5 erreurs architecturales de v4 identifiées (détection via `mpmath.siegelz`,
  parallélisme abandonné, `Z_double` en détection, fallback global, `.so` absent
  silencieux) → à corriger dans v4.1.
- Seuil justifié : $N=\lfloor\sqrt{t/2\pi}\rfloor \Rightarrow t<300 \Rightarrow N<7$ (imprécis),
  $t\geq 300 \Rightarrow N\geq 7$ (fiable). D'où `T_SEUIL = 300.0`.
- 9 PDF de cadrage produits (session GPT-4.5 / Copilot) — voir `STACK.md`.

---

## 2026-05-23 — Correction hiérarchie CLAUDE.md

Le `CLAUDE.md` projet (208 lignes, Riemann) avait été copié par erreur dans
`~/.claude/CLAUDE.md` (global), écrasant les instructions générales. Deux fichiers
distincts recréés :

| Fichier | Contenu | Lignes |
|---|---|---|
| `~/.claude/CLAUDE.md` | Langue FR, style, règles légères | 26 |
| `~/projet_zeta/CLAUDE.md` | Contexte Riemann complet | 208 |
| `src/calculs/optimisation/CLAUDE.md` | Phase C — Illinois, ctypes | 108 |
| `.../c_modules/CLAUDE.md` | Règles C — libmpfr, PREC=170 | 97 |

---


## 2026-05-16 — Benchmark séquentiel équitable (post-reboot NVIDIA)

Tests équitables : un seul mode à la fois après reboot.

| Mode | Zéros / 15 min | Vitesse | t atteint | Gain vs CPU |
---

## 2026-06-03 — 01h00→02h00 — Diagnostic pipeline v4.1 + 82 z/s validé

### Objectif de la session
Analyser pourquoi le « 41 z/s (×39) » du benchmark unitaire ne se transmettait pas
au pipeline réel (T=1000 → 1.07 z/s). Instrumenter, mesurer, corriger.

### Résultats mesurés

| Étape | Vitesse | Note |
|---|---|---|
| v3 T=10000 (référence) | 1.02 z/s | pipeline séquentiel |
| v4.1 runs initiaux T=1000 | 1.07 z/s | ×39 unitaire NON transmis |
| v4.1 + Z_vect_correct + bracket | **82–84 z/s** | ✅ **×80 vs v3** |
| v4.1 + workprec(50) | 82 z/s | neutre (voir ci-dessous) |

### Instrumentation — `chrono_phases.py` (nouveau fichier)
Profileur 4+1 phases (`detection` / `illinois_C` / `mpmath_petit_t` /
`mpmath_fallback` / `turing`). Ajouté à `compute_zeros_v4_1.py` via 6 insertions
chirurgicales (zéro logique de calcul modifiée). Compile OK.

### Profil mesuré (T=1000, version finale)
```
phase            temps_cumul   appels   ms/appel   % mur×W
mpmath_petit_t      11.27s      138      81.65     35.6%
illinois_C           5.22s      511      10.21     16.5%
turing               2.33s        1    2330.99      7.4%
detection            0.09s        4      21.53      0.3%
```
→ Illinois_C réel = **10 ms/appel** (pas 24 ms supposés). Détection = négligeable.
→ Goulot résiduel = `mpmath_petit_t` (138 zéros t<300, siegelz dps=35 interne).

### Correctifs validés (Claude Code + hprzeta)
1. `Z_batch` → `Z_vect_correct` : N(t) propre à chaque point (bug N_max fixe corrigé).
2. `findroot(siegelz, t_mid)` → `findroot(siegelz, (a,b), solver="illinois")` : bracket
   robuste, ne peut plus diverger.
3. `workprec(50)` sur mpmath_petit_t : **gain marginal** (~12 %) car `siegelz` interne
   force sa propre précision — le contexte `workprec` ne la contrôle pas.

### Leçon clé — piège workprec mpmath
`with _mp.workprec(50): _mp.findroot(_mp.siegelz, ...)` ne passe PAS dps=15 à siegelz.
siegelz re-lit `mp.dps` global (35). Seule façon de forcer float64 : `_mp.fp.siegelz`.
→ **Prochain levier : remplacer siegelz par fp.siegelz sur t<300** → ~2 ms/appel vs 82 ms.

### Hypothèse réfutée
Pas de « finition Newton dps=25 » dans `compute_zeros_v4_1.py` — hypothèse abandonnée
après lecture du code. Bonne pratique : lire le code avant de supposer le goulot.

### Git — nouvelle règle branche `session`
`Handoff.md` versionné sur branche orpheline `session` (aucun ancêtre commun).
Motif `**/Handoff.md` dans `.gitignore` de toutes les branches de code.
Vérifié : `git ls-files | grep -ci handoff` → 0 sur code, 1 sur session.

### Comportement Claude Code à retenir
- Modifie les fichiers **sans demander** si aucune règle explicite ne l'en empêche.
- Timeout agent = **5 min** → runs longs : `printf "T\nO\n" | python script.py | tee log`.
- Lit le Handoff du **wiki** (pas la branche `session`) → contexte potentiellement périmé.
- Rapport de vitesse sans run réel = **fabrication** (62.91 z/s annoncé mais timeout).

### Commits de la session
- `Riemann_Lab_C` : `compute_zeros_v4_1.py` instrumenté + `chrono_phases.py` +
  `patch_workprec.py` → 82 z/s validé, Turing COMPLET, LMFDB 19/20.
- `session` : `Handoff.md` mis à jour (branche orpheline).
- 4 branches de code : `**/Handoff.md` hors suivi Git.

### Prochaine action
Remplacer `_mp.siegelz` par `_mp.fp.siegelz` (float64 natif) sur le segment t<300
→ 81 ms → ~2 ms/appel → pipeline estimé ~200+ z/s → run T=10000 en ~1 min.

---

|---|---|---|---|---|
| CPU scalaire (réf.) | ~604 | ~0.67 z/s | 944 | — |
| **BATCH_CPU** | **3 231** | **3.59 z/s** | 4 164 | **×5.3** |
| **BATCH_GPU** | **3 051** | **3.39 z/s** | 4 596 | **×5.1** |

**Clé :** BATCH_CPU ≈ BATCH_GPU — la GTX 960M n'apporte pas de gain. L'affinage Illinois
(mpmath, CPU pur) = **80–90 % du temps total** ; la GPU n'accélère que la détection Z(t)
(10–20 %). GPU GTX 960M opérationnel depuis le 16 mai (`prime-select nvidia` + reboot,
CuPy `cupy-cuda12x`).

---

## ~2026-04-24 — Objectif 1 atteint — 10 142 zéros

`compute_zeros_v2.py` : 10 142 zéros calculés (jusqu'à T ≈ 9998.85) en ~21 h,
validés contre LMFDB. Fichier : `zeros_zeta_T10000_20260424_205325.csv`.
Base de référence vitesse : CPU scalaire 1.4 z/s solo.

---
> *Mise à jour : 31 mai 2026 — 02h00 · JOURNAL.md (1 fichier MD modifié) · ~205 lignes · append-only*
