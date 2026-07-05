# Rapport de session — 27 juin 2026

> **Projet :** Riemann_Lab · hprzeta · `hprzeta@protonmail.com`
> **Branche :** `Riemann_Lab_C`
> **Session :** 27 juin 2026, après-midi
> **Modèle IA :** Claude Sonnet 4.6

---

## Résumé exécutif

Session centrée sur deux objectifs : (1) implémenter un mécanisme de rescan ciblé dans
`compute_zeros_v13.py` pour récupérer les zéros manqués par la phase de grille du scan
Z_double, et (2) lancer le premier run à T=5 000 000 (~10 millions de zéros).

La feature rescan a été implémentée, testée et validée sur T=1000. Le run T=5M tourne
depuis 16h02 (ETA 28/06 ~15h30 — 24h de calcul). Une analyse du goulot d'étranglement
a permis d'identifier la prochaine priorité : Illinois hybride Z_double→Arb dans
`illinois_arb.c` (v14, gain ×8 estimé).

---

## Section 1 — Rescan ciblé par déficit (`rescan_segments_deficit`)

### Contexte et motivation

Les 5 zéros manquants du run T=500k (run #4, référence officielle) ont été attribués
définitivement le 26/06 aux **ratés du scan Z_double par phase de grille** — les deux points
d'échantillonnage autour de ces zéros tombent du même côté de Z(t). L'affinage
`illinois_refine_arb` est parfaitement fiable (0 REJECT, 0 FALLBACK sur 818 406 appels,
confirmé par l'instrumentation `ZETA_DEBUG_BRACKETS`).

La solution : après le run principal, détecter les segments en déficit et les re-scanner
avec `STEP/2`. Un pas deux fois plus petit décale la phase de la grille et peut capturer
des zéros manqués lors du premier passage.

### Implémentation

**Modifications dans `compute_zeros_v13.py` :**

| Élément | Changement |
|---|---|
| `calculer_zeros_v13()` | Retourne maintenant un 4-tuple `(zeros, stats, profil, segments)` |
| `rescan_segments_deficit()` | Nouvelle fonction — Section 3b |
| `ecrire_log()` | Paramètre optionnel `rapport_rescan=None` — section [7] dans le log |
| `main()` | Enchaîne rescan → `dedupliquer()` → Turing sur liste complète |
| `MARGE_SECURITE` | Revertée 3.0 → 2.0 (working copy — dans le diff non commité) |

**Logique de `rescan_segments_deficit` :**

1. Calculer les bornes non chevauchantes : `checkpoints = [s[0] for s in segments] + [T_MAX]`
2. Pour chaque segment `i` : `deficit = N(checkpoints[i+1]) - N(checkpoints[i]) - n_trouvés`
3. Si `deficit > 0` : ajouter à la liste des segments à rescanner
4. Lancer tous les rescans en parallèle via `multiprocessing.Pool` (worker IDs 100+i)
5. Fusionner les résultats bruts avec `dedupliquer(zeros + zeros_rescan, tolerance=0.01)`

Le rescan n'est actif qu'en mode interactif local (`_cli.t_min is None`) — désactivé en
mode distribué (`--t-min`/`--t-max`), car les segments PC2 ne sont pas disponibles localement.

### Validation sur T=1000

```
Run principal    : 649 zéros · 0.6s · 1050 z/s · Turing COMPLET ✅ · LMFDB 20/20 ✅
Rescan           : 2 segments détectés en déficit (artefacts N(T), pas de vrais manquants)
                   Workers 102 et 104, rescan parallèle en 0.2s
Après fusion     : 649 zéros · +0 nets (aucun vrai manquant à T=1000 — comportement attendu)
Turing final     : COMPLET ✅
```

Les "déficits" détectés à T=1000 sont des artefacts de l'approximation N(T) (terme S(T)
non pris en compte dans `_n_zeros_expected`). Le rescan confirme qu'aucun zéro ne manque.

---

## Section 2 — Run T=5 000 000

### Paramètres

| Paramètre | Valeur |
|---|---|
| T_MAX | 5 000 000 |
| N(T) attendus | 10 016 473 zéros |
| STEP adaptatif | 0.001571 (×2.8 plus fin qu'à T=500k = 0.0044) |
| MARGE_SECURITE | 2.0 |
| N_WORKERS | 8 (PC1 uniquement, pas distribué) |
| Mode | Interactif local — rescan ciblé actif |
| Turbo | Activé (`zeta_turbo_on.sh`) |

### Segments workers

| Worker | Plage | N(T) attendus ≈ |
|---|---|---|
| 0 | [14.0, 737 112.8] | ~1 252 059 |
| 1 | [737 112.3, 1 391 397.6] | ~1 252 059 |
| 2 | [1 391 397.1, 2 020 448.4] | ~1 252 059 |
| 3 | [2 020 447.9, 2 634 120.2] | ~1 252 059 |
| 4 | [2 634 119.7, 3 236 822.7] | ~1 252 059 |
| 5 | [3 236 822.2, 3 831 051.8] | ~1 252 059 |
| 6 | [3 831 051.3, 4 418 407.6] | ~1 252 059 |
| 7 | [4 418 407.1, 5 000 000.0] | ~1 252 059 |

### État à 17h50 (1h48 écoulées)

- 8 workers actifs (PIDs 46085-46092), 45% CPU chacun
- Progression estimée : ~7.6% (~760k zéros)
- **ETA : 28/06/2026 ~15h30**

### Découverte importante — durée réelle vs estimée

L'estimation initiale de 8.6h était incorrecte. Le facteur oublié :

```
N_RS(T) ≈ √(T / 2π)   ← nombre de termes Riemann-Siegel par éval Arb

N_RS(T=500k)  ≈ 282 termes
N_RS(T=5M)    ≈ 892 termes

Facteur de ralentissement illinois_refine_arb : 892/282 ≈ ×3.16

Durée réelle estimée ≈ 37 min × (12.2 × 3.16) × 89% + 11% scan × 28
                     ≈ 37 × 13.9 ≈ 514 min ≈ 24h
```

Ce facteur √T sera le goulot dominant pour tous les runs à T élevé tant que
`illinois_arb.c` utilise Arb pur. C'est la motivation principale de v14.

---

## Section 3 — Stratégie d'optimisation identifiée

### Analyse du goulot

À T=5M, le profil de temps (extrapolé depuis T=1000) :
- **Affinage Arb (illinois_refine_arb)** : ~89% du temps · coût ∝ N_zeros × N_RS × n_iter
- **Scan C (scan_arb.so)** : ~11% du temps · coût ∝ N_points = T/STEP

### Roadmap d'optimisation

| Niveau | Optimisation | Gain | Effort | T=5M après optimisation |
|---|---|---|---|---|
| **1a** | Distribution PC1+PC2 | ×2 | Immédiat | ~12h |
| **1b** | TOL_ARB 1e-12 → 1e-9 | ×1.4 | 30 min | ~17h |
| **2 ⭐** | **Illinois hybride Z_double→Arb** | **×8** | **2 jours** | **~3h** |
| **3** | Odlyzko-Schönhage | ×50+ | Semaines | < 30 min théorique |

### Niveau 2 — Illinois hybride (priorité v14)

**Fichier :** `src/calculs/optimisation/c_modules/illinois_arb.c`

**Principe :**
```
Actuel (illinois_refine_arb) :
  Toutes les itérations utilisent Arb (coûteux)
  ~25 appels Arb × 892 termes/appel = 22 400 opérations/zéro

Hybride proposé :
  Phase 1 : Z_double (rapide) jusqu'à |b-a| < 1e-6
             → ~20 appels Z_double ≈ O(1) chacun (C0+C1 tronquée)
  Phase 2 : Arb pour les 2-3 dernières itérations de précision
             → ~3 appels Arb × 892 termes = 2 676 opérations/zéro

Gain : 22 400 / 2 676 ≈ ×8.4
```

**Faisabilité :** Z_double a une erreur RS ≈ 1e-4 à T=5M (C0+C1 seulement). Tant que
le bracket |b-a| >> 1e-4, les signes Z_double sont fiables pour l'Illinois. On bascule
sur Arb uniquement quand |b-a| < 1e-4 (garantit l'exactitude du résultat final à 1e-12).

**Implémentation dans `illinois_arb.c` :**
```c
// Phase 1 : Z_double rapide pour converger à ~1e-6
while (fabs(b - a) > 1e-4) {
    c = b - Z_double(b, N_RS) * (b - a) / (Z_double(b, N_RS) - Z_double(a, N_RS));
    // ... logique Illinois standard avec Z_double ...
}
// Phase 2 : Arb pour la précision finale
while (fabs(b - a) > tol) {
    // ... logique Illinois avec Arb ...
}
```

---

## Section 4 — Matériel — upgrade RAM PC1

**Décision :** +16 Go SO-DIMM DDR4 2133 MHz dans le slot libre de l'ASUS ZenBook UX510UWK.

| État | RAM | Swap nécessaire |
|---|---|---|
| Actuel | 8 Go soudés | 16 Go (utilisé sous charge 8 workers) |
| Après upgrade | 24 Go (8 soudés + 16 en slot) | 0 Go (élimination du swap) |

**Impact sur les runs :** le swap est 10-50× plus lent que la RAM. Avec 8 workers et 24 Go,
chaque worker dispose de 3 Go de RAM réelle → amélioration de la vitesse sous charge parallèle.

---

## Section 5 — État des commits (fin de session)

### Commits en attente (branche `Riemann_Lab_C`)

| Fichier | Modification | Condition |
|---|---|---|
| `scripts/zeta_distribute.py` | Option B + `fusionner_csv` généralisée | Non commité (expérimental, laisser en l'état) |
| `src/calculs/optimisation/compute_zeros_v13.py` | Rescan ciblé + MARGE=2.0 | **À committer après validation run T=5M** |

### Commits wiki effectués cette session

| Commit | Fichier | Description |
|---|---|---|
| `15f04a4` | `Handoff.md` | Run T=5M lancé + feature rescan v13 |
| (cette session) | `JOURNAL.md` · `STACK.md` · `Handoff.md` | Mise à jour fin de session |
| (cette session) | `Rapport-Session-27-06-2026.md` | Ce fichier |

### Checklist à la fin du run T=5M (28/06 ~15h30)

```bash
# 1. Vérifier résultat
grep -E "COMPLET|manquant|Turing" ~/projet_zeta/logs/run_v13_T5M.log | tail -10

# 2. Turbo off (OBLIGATOIRE)
sudo scripts/zeta_turbo_off.sh

# 3. Si COMPLET : commit + sync 4 branches
cd ~/projet_zeta
git add src/calculs/optimisation/compute_zeros_v13.py
git commit -m "feat(v13): rescan ciblé par déficit (STEP/2, parallèle) + revert MARGE=2.0"
git push origin Riemann_Lab_C

# 4. Prochaine tâche : v14 Illinois hybride dans illinois_arb.c
```

---

*Rapport-Session-27-06-2026.md · hprzeta · Riemann_Lab_C · Claude Sonnet 4.6*
