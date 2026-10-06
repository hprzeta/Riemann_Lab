# Sémantique de MARGE_SECURITE + documentation précision R6 — 2026-09-12/13

> Mode : **LECTURE SEULE**. Investigation + documentation uniquement. Aucune écriture de
> code, aucune modification du moteur, aucun `git commit/push`. Verrou moteur durci
> respecté intégralement (voir Tâche C.3 pour le détail de ce que ce verrou a empêché de
> tester directement).
> Source : `/home/riemann/Téléchargements/PROMPT_marge_securite_et_R6_2026-09-12.md`.
> Dépôt audité : `~/projet_zeta`, branche `Riemann_Lab_C`.

---

## Tâche A — Sémantique exacte de MARGE_SECURITE

**Ce qu'elle contrôle, précisément :** `MARGE_SECURITE` est le diviseur final de la formule
qui produit **`STEP`**, le pas de la grille de balayage en `t` utilisée pour détecter un
changement de signe de `Z(t)` (`_step_adaptatif()`, `compute_zeros_v16.py:707-826`) :

```
min_gap(T) ≈ KAPPA · gap_moyen(T) · N(T)^(-1/3)
STEP(T)    = min_gap(T) / MARGE_SECURITE
```

`STEP` n'est **ni** une demi-largeur de bracket, **ni** une marge de précision numérique,
**ni** un espacement de points de Gram : c'est directement le pas `t_{i+1} - t_i` utilisé
par `np.arange(t_start, t_end, step, ...)` (`compute_zeros_v16.py:216`) et par `scan_arb(...,
step=step, ...)` (`:247`) pour échantillonner `Z(t)` et repérer les changements de signe.

**Effet d'une marge plus grande (STEP plus fin) :** plus de points de grille → plus de
brackets → plus d'appels Illinois/Newton → **surcoût de calcul quasi-linéaire** en
`1/MARGE_SECURITE`. **Effet d'une marge plus petite (STEP plus grossier) :** risque accru
que **deux zéros proches tombent dans le même pas** — leurs deux changements de signe
s'annulent, `Z(a)` et `Z(b)` ont alors le même signe et la paire disparaît **sans laisser de
trace visible** (`compute_zeros_v16.py:710-714`). C'est exactement le mécanisme qui a produit
les 96 manquants du run T=5M à `MARGE_SECURITE=2.0` (voir Tâche B).

**Dédoublonnage / risque de brackets chevauchants :** `MARGE_SECURITE` ne contrôle **pas**
directement un chevauchement de brackets entre workers — celui-ci vient d'un **overlap fixe
de 0.5** entre segments (`compute_zeros_v16.py:107`), indépendant de `STEP`. Le mécanisme qui
neutralise les doublons (qu'ils viennent de cet overlap de segments ou, en théorie, d'un
`STEP` très fin) est `dedupliquer(zeros_bruts, tolerance=0.01)`
(`parallel_scanner.py:148-166`) : deux zéros à distance `< 0.01` sont fusionnés. La fonction
documente elle-même l'hypothèse qui rend cela sûr (`parallel_scanner.py:156-157`) :
« l'espacement minimal entre zéros est ~π/ln(T/2π) ≫ 0.01 pour T < 10⁶ » — donc un
`MARGE_SECURITE` plus grand (STEP plus fin, jusqu'à un facteur ×10 ou plus par rapport à
`0.01`) n'introduit **aucun risque nouveau de fausse fusion de deux zéros distincts** ; il ne
fait que renchérir le coût de calcul.

---

## Tâche B — Git blame aux jalons validés

**⚠️ Correction du prompt source :** le commit `f48da88` cité comme « v16 bit-identique à
T=100k, LMFDB 20/20, Turing complet » est en réalité **sans rapport** —
`git show f48da88 --stat` : `fix(rag): rag_query.py — défaut --k 3→8 (chunk clé souvent hors
top-6)`, 25/07/2026, un fichier du pipeline RAG. Le commit correspondant à la description du
prompt est **`00abe5c`** (`feat(v16): illinois_arb.c — Z_arb à précision fixe
(acb_dirichlet_hardy_z, 64 bits)`, 08/08/2026) : message de commit confirmant « Intégration
(ce commit) revalidée à T=100000 : 138 069/138 069 zéros, Turing COMPLET, LMFDB 20/20 ».
Utilisé ci-dessous à la place de `f48da88`.

| Jalon | Commit | Date | `MARGE_SECURITE` | Résultat connu |
|---|---|---|---|---|
| Run T=5M v13 (96 manquants) | `a0e6e41` | 2026-07-04 | **2.0** (`compute_zeros_v13.py:718` à ce commit) | 10 016 377 / 10 016 473 — **96 manquants** |
| Restauration post-régression | `a7fb498` | 2026-08-02 | 2.0 → **3.0** | Restaure le correctif du 23/06 annulé par `a0e6e41` (pas de run T=5M complet à cette valeur) |
| Mesure non censurée (3 zones ciblées) | `a04ea1f` | 2026-08-02 | 3.0 → **15.0** | 3.0 confirmé **insuffisant** à T≈4,86M (2 zéros manquants sur comparaison directe fin/normal, `compute_zeros_v16.py:772-778`) |
| Redescente validée (3 zones + pivot PC1+PC2) | `bbb8a6f` | 2026-08-02 | 15.0 → **10.0** | 0 manquant sur les 3 zones (6/6, 7/7, 8/8) + 84/84 au pivot réel du run T=5M cible (`:796-818`) |
| v16 intégrée en production, T=100k | `00abe5c` | 2026-08-08 | **10.0** (déjà actif) | 138 069/138 069, Turing COMPLET, LMFDB 20/20 |

**Valeur déjà validée expérimentalement :** `MARGE_SECURITE=10.0` est la **seule** valeur
pour laquelle une trace de validation directe existe à la fois en isolé (3 zones dont
T≈4,86M) et en configuration distribuée réelle (pivot PC1+PC2 du run T=5M cible), documentée
dans le code source lui-même (`compute_zeros_v16.py:796-818`). `3.0` n'a **jamais** été
validé à grande échelle : c'est une valeur de restauration intermédiaire (annulait par erreur
le passage 2.0→3.0 du 23/06), testée ensuite spécifiquement et trouvée **insuffisante**
(`a04ea1f`). La croyance « MARGE_SECURITE=3.0 = calibration validée », répétée dans le
CLAUDE.md racine et les 2 documents externes audités le 12-13/09, est donc **contredite par
l'historique git lui-même**, pas seulement par la valeur actuellement active.

---

## Tâche C — R6 : stratégie précision/termes (documentation, lecture seule)

### C.1 — Précision demandée à Arb : fixe, 64 bits, indépendante de `t`

Confirmé à trois niveaux de source, tous cohérents :
- En-tête du module production : « Précision 64 bits choisie : coïncide avec `WP_INITIAL`
  de `arb_fpwrap`, marge ~7 décimales au-dessus des ~40 bits nécessaires pour `tol=1e-12` »
  (`compute_zeros_v16.py:19-20`).
- Constante C : `#define PREC_BITS_ARB 64` (`c_modules/illinois_arb.c:94`).
- Appel unique, sans escalade : `acb_dirichlet_hardy_z(res, s, g_G, g_chi, 1,
  (slong)PREC_BITS_ARB)` (`c_modules/illinois_arb.c:156`), à l'intérieur de la fonction
  `static double Z_arb(double t)` (`:148`) — **un seul appel, jamais de boucle
  d'escalade**, contrairement à `arb_fpwrap_cdouble_hardy_z` (l'ancien chemin v15, qui
  escaladait en interne 64→128→…→8192 bits, cf. `compute_zeros_v16.py:8-12`).

**Cette précision de 64 bits ne varie jamais avec `t`** — c'est le même appel, à la même
précision fixe, quel que soit `t ∈ [65, T_MAX]` (le chemin `t ∈ [14,65)` utilise un mécanisme
distinct : `arb_hardy_z` — wrapper Python vers `arb_fpwrap_cdouble_hardy_z`, escaladant —
pour la détection, puis `mpmath.fp.siegelz`/`findroot` pour l'affinage, voir
`compute_zeros_v16.py:208-224`).

### C.2 — Table par décade : précision fixe vs borne théorique de Riemann-Siegel

$$
R(t) \approx 2\sqrt{\frac{t}{2\pi}}
$$

| $t$ | $R(t)\approx2\sqrt{t/2\pi}$ (nombre de termes RS) | Précision Arb demandée | Commentaire |
|---|---|---|---|
| $10$ | $\approx 2{,}5$ | 64 bits fixe (hors chemin `illinois_refine_arb` — $t<65$ utilise `arb_hardy_z`+mpmath) | $R$ trop petit pour ce chemin ; zone gérée par le mécanisme dédié `t\in[14,65)` |
| $10^2$ | $\approx 8{,}0$ | 64 bits fixe | Première décade réellement couverte par `illinois_refine_arb`/`Z\_arb` ($t\ge65$) |
| $10^3$ | $\approx 25{,}2$ | 64 bits fixe | $R$ a $\times3$ depuis $10^2$, précision inchangée |
| $10^4$ | $\approx 79{,}8$ | 64 bits fixe | $R$ a $\times10$ depuis $10^2$, précision toujours inchangée |
| $10^5$ | $\approx 252{,}3$ | 64 bits fixe | Échelle de référence du run T=100k (Turing COMPLET, LMFDB 20/20 à cette précision) |
| $5\times10^6$ | $\approx 1783{,}9$ | 64 bits fixe | Borne haute du run T=5M cible ; $R$ a crû $\times\!\sim\!700$ depuis $t=10$, la précision demandée à Arb n'a, elle, jamais changé |

**Commentaire général :** $R(t)$ mesure le **nombre de termes** de la somme de
Riemann-Siegel nécessaires pour évaluer $Z(t)$ — il croît en $O(\sqrt t)$ et gouverne le
**coût** de chaque évaluation. La **précision** demandée à `acb_dirichlet_hardy_z`
(`PREC\_BITS\_ARB=64`) est un réglage **indépendant** : Arb calcule la somme des $R(t)$
termes en arithmétique d'intervalles (ball arithmetic) et renvoie un résultat dont l'erreur
est bornée *pour la précision de travail demandée*, quel que soit le nombre de termes sommés
— augmenter $R(t)$ avec $t$ n'oblige donc pas mécaniquement à augmenter le nombre de bits
pour conserver une erreur bornée à `tol=1e-12` ; c'est une propriété de l'arithmétique Arb
elle-même, pas un choix ajusté manuellement décade par décade dans ce moteur. **Ce document
documente ce choix, il ne le remet pas en cause.**

### C.3 — Vérification échantillonnée (script scratch, hors dépôt, non commité)

**Contrainte du verrou moteur rencontrée et signalée (pas contournée) :** la fonction
`Z_arb` (`c_modules/illinois_arb.c:148`), seule à appeler `acb_dirichlet_hardy_z` à 64 bits
fixes, est déclarée `static` — confirmé par `nm -D illinois_arb.so | grep " T "`, qui ne
liste que `arb_close_debug_log`, `arb_set_debug_log` et `illinois_refine_arb` comme symboles
exportés. **Elle n'est donc pas appelable isolément depuis Python sans modifier le fichier
C** (l'exporter, retirer `static`, recompiler) — interdit par le verrou moteur. Contournement
choisi, strictement en lecture seule : appeler `illinois_refine_arb(a, b, fa, fb, tol,
max_iter)` (la seule fonction exportée qui invoque `Z_arb` en interne) sur des **brackets
réels encadrant un zéro connu**, construits via `mpmath.siegelz` à `dps=50` — c'est
d'ailleurs la façon exacte dont cette fonction est utilisée en production
(raffinement d'un bracket, pas évaluation isolée de `Z(t)`).

Script : `/tmp/marge_r6_check/verif_precision_arb.py` (hors dépôt, non commité, appel-seul
via `ctypes.CDLL`, aucune modification du `.so` ni du `.c`).

| $t$ cible | Zéro réf. (mpmath, dps=50) | Zéro `illinois_refine_arb` | Écart |
|---|---|---|---|
| $14{,}135$ | $14{,}134725141734695$ | $14{,}134725211332571$ | $6{,}960\times10^{-8}$ |
| $100$ | $88{,}809111207634459$ | $88{,}809111207628817$ | $5{,}642\times10^{-12}$ |
| $1000$ | $999{,}791571557412908$ | $999{,}791571557412908$ | $0$ |
| $10000$ | $10000{,}065345414535841$ | $10000{,}065345414535841$ | $0$ |
| $100000$ | $99998{,}510524733457714$ | $99998{,}510524733443162$ | $1{,}455\times10^{-11}$ |
| $4999998$ | $4999998{,}219367451034486$ | $4999998{,}219367451034486$ | $0$ |

**Écart max mesuré : $6{,}960\times10^{-8}$**, au point $t\approx14{,}135$ — **hors du
domaine d'usage réel de `illinois_refine_arb`** : le moteur route explicitement $t<65$ vers
`arb_hardy_z`+mpmath, précisément parce que le nombre de termes RS y est trop faible
($N\_RS\le2$–$3$) pour une détection/affinage fiable via ce chemin — voir la justification
déjà présente dans le code (`compute_zeros_v16.py:186-201`, « Pourquoi 65 et pas 20 ? »). Ce
résultat **confirme** ce garde-fou existant plutôt que de révéler un problème nouveau. Sur
les points **effectivement dans le domaine de production** ($t\ge100$), l'écart maximal
mesuré est $1{,}455\times10^{-11}$ (à $t=10^5$) — légèrement au-dessus de la tolérance cible
interne `TOL_ARB=1e-12`, mais de deux ordres de grandeur inférieur au seuil de tolérance de
dédoublonnage (`0.01`) et sans commune mesure avec l'espacement minimal entre zéros distincts.
**Aucune recalibration n'a été effectuée** — ce chiffre est reporté tel quel pour la synthèse.

---

## STOP — synthèse pour décision

**(a) Ce que contrôle `MARGE_SECURITE` et le sens du risque :** elle divise l'estimation du
plus petit écart attendu entre zéros pour fixer `STEP`, le pas de la grille de détection de
changement de signe de `Z(t)`. Plus grande → grille plus fine → coût de calcul plus élevé,
risque de zéros manqués plus faible. Plus petite → grille plus grossière → moins cher, mais
risque réel de manquer des paires de zéros proches (mécanisme confirmé comme cause des 96
manquants à `MARGE=2.0`). Le mécanisme de dédoublonnage existant (`tolerance=0.01`) absorbe
sans risque documenté toute finesse de grille supplémentaire liée à une marge plus grande.

**(b) Valeur(s) déjà validée(s) trouvée(s) par blame :** `MARGE_SECURITE=10.0` est la seule
valeur avec une trace de validation directe (3 zones isolées dont T≈4,86M, **et** au pivot
réel PC1+PC2 du run T=5M cible) — commits `bbb8a6f` puis intégrée telle quelle dans `00abe5c`
(v16 production, T=100k Turing COMPLET/LMFDB 20/20). `3.0` n'a jamais passé ce test à grande
échelle (`a04ea1f` : insuffisant à T≈4,86M) ; `2.0` a produit les 96 manquants historiques
(`a0e6e41`).

**(c) Écart max de la vérification R6 :** $6{,}960\times10^{-8}$ au point $t\approx14$ (hors
domaine d'usage réel, garde-fou déjà en place) ; $1{,}455\times10^{-11}$ au pire point
effectivement dans le domaine de production ($t=10^5$), $0$ ailleurs.

**Rappel :** ce document ne tranche pas 3.0 vs 10.0 — c'est le gate empirique T=100k
(prompt suivant, hors périmètre ici) qui décidera. Aucun fichier du moteur listé dans le
verrou (`compute_zeros_v16.py`, `compute_zeros_v15.py`, `scripts/zeta_run.sh`,
`riemann_siegel_batch.py`, `c_modules/illinois_arb.c`) n'a été modifié. Aucun commit
effectué. Script de vérification laissé dans `/tmp/marge_r6_check/` (hors dépôt).
