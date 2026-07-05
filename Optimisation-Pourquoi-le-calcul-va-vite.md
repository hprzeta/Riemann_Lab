# ⚡ Optimisation — Pourquoi le calcul des zéros va vite

> Cours méthodologique : comment on passe de ~1 zéro/seconde à ~15–20 zéros/seconde.
> Cette page explique le **pourquoi mathématique** des choix d'optimisation des versions
> `compute_zeros_v4_1.py` / `compute_zeros_v5.py`.

---

## 1. L'idée fondamentale : deux opérations différentes

Trouver un zéro de $\zeta$ sur la droite critique, c'est **deux étapes distinctes** qu'on
confond souvent (c'est exactement la confusion qui avait fait échouer la v4) :

1. **Détection** — « il y a un zéro *quelque part* entre $t = 14.05$ et $t = 14.10$ ». Grossier.
2. **Affinage** — « il est *exactement* à $t = 14.134725141\ldots$ ». Précis à 12 décimales.

Les deux utilisent la même fonction $Z(t)$, **mais pas de la même façon**. Toute l'optimisation
repose sur cette distinction.

---

## 2. La fonction $Z$ de Hardy (le socle)

On ne cherche pas les zéros de $\zeta$ directement — on passe par la **fonction $Z$ de Hardy** :

$$Z(t) = e^{i\theta(t)} \, \zeta\!\left(\tfrac{1}{2} + it\right)$$

où $\theta(t)$ est la fonction de Riemann-Siegel (la phase).

Sa propriété décisive : **$Z(t)$ est réelle** pour $t$ réel, et $|Z(t)| = \left|\zeta\!\left(\tfrac{1}{2}+it\right)\right|$.
On en déduit l'équivalence fondamentale :

$$\zeta\!\left(\tfrac{1}{2} + it\right) = 0 \iff Z(t) = 0$$

Chercher un zéro de $\zeta$ (fonction complexe, compliquée) revient donc à chercher un zéro
d'une **fonction réelle**, c'est-à-dire un simple **changement de signe**. Énorme simplification.

> 📖 **Fondamentaux** — définition de $\zeta$, équation fonctionnelle et factorisation
> $\zeta\!\left(\tfrac{1}{2}+it\right) = e^{-i\theta(t)} Z(t)$ : voir [[Formules_zeta]] et le cours [[niveau-4-zeta]].

---

## 3. Étape 1 — Détection : seul le **signe** compte

On balaye $t$ par petits pas. Dès que $Z$ change de signe entre deux points consécutifs, c'est
qu'un zéro est coincé entre les deux (théorème des valeurs intermédiaires, puisque $Z$ est continue) :

$$Z(14.05) = +1.1 \quad\text{puis}\quad Z(14.10) = -0.3 \;\Longrightarrow\; \text{zéro dans } [14.05,\ 14.10]$$

Pour cela, **aucune précision n'est nécessaire** : que $Z(14.10)$ vaille $-0.3$ ou $-0.28$, le
signe est le même. Une approximation grossière suffit.

C'est là qu'intervient `Z_batch()` (module `riemann_siegel_batch.py`) : il calcule $Z(t)$ pour
**tout un tableau de $t$ d'un coup** (NumPy vectorisé, voire GPU via CuPy). Calculer 1000 valeurs
en une seule opération est **environ ×50 plus rapide** que d'appeler `mpmath.siegelz` 1000 fois de
suite. La v5 était lente précisément parce qu'elle faisait ces appels un par un.

> **Règle :** `mpmath.siegelz` est interdit pour la détection. On utilise `Z_batch()` partout.

---

## 4. La formule de Riemann-Siegel et le nombre de termes

Pour calculer $Z(t)$, on utilise la **formule de Riemann-Siegel** :

$$Z(t) \approx 2 \sum_{n=1}^{N} \frac{\cos\!\left(\theta(t) - t \ln n\right)}{\sqrt{n}} + R(t),
\qquad N = \left\lfloor \sqrt{\tfrac{t}{2\pi}} \right\rfloor$$

où $R(t)$ est un terme de reste (corrections $C_0, C_1, \ldots$).

> 📖 **Détails** — dérivation de la formule de Riemann-Siegel et de $\theta(t)$ :
> voir [[niveau-5-expert]] et [[Formules_zeta]].

Le point crucial : **$N$ dépend de $t$**. Pour petit $t$, la somme a très peu de termes :

| $t$ | $N = \lfloor\sqrt{t/2\pi}\rfloor$ | Précision RS interne |
|---|---|---|
| $14$ | $1$ (un seul terme !) | imprécise (~$10^{-2}$) |
| $300$ | $6$ | limite |
| $1000$ | $12$ | correcte |
| $10000$ | $39$ | très précise |

C'est pourquoi l'affinage en C (qui recalcule $Z$ avec sa propre formule RS interne) n'est fiable
que pour $t \geq 300$. En dessous, on bascule sur `mpmath` (le *fallback*) — mais cela ne concerne
que **~87 zéros sur 10 142, soit moins de 1 %**. On garde donc la vitesse du C sur 99 % du travail.

---

## 5. Étape 2 — Affinage : la méthode d'Illinois

Une fois le zéro coincé dans $[a, b]$ (avec $Z(a)$ et $Z(b)$ de signes opposés), on le localise
précisément. On trace la **sécante** entre les points $(a, Z(a))$ et $(b, Z(b))$, et on prend le
point $c$ où elle croise l'axe horizontal :

$$c = b - Z(b) \cdot \frac{b - a}{Z(b) - Z(a)}$$

On garde ensuite le sous-intervalle qui encadre encore le zéro, et on recommence. À chaque tour,
l'encadrement se resserre.

### Pourquoi « Illinois » et pas juste « sécante » ?

La méthode brute (regula falsi) a un défaut : parfois une des deux bornes reste **bloquée** (elle
ne bouge jamais), et la convergence devient très lente. L'astuce d'Illinois : quand une borne
stagne, on **divise par 2** la valeur de $Z$ à cette borne. Cela force la sécante à « pivoter »
et décoince la borne.

Résultat : convergence presque aussi rapide que Newton, **mais avec la garantie de toujours rester
encadré** (donc on ne diverge jamais). C'est le compromis idéal pour un calcul automatique sur
10 000 zéros.

### Cas dégénéré (correction de robustesse)

Si la détection place une borne quasi-exactement sur le zéro, par exemple
$|Z_b| \approx 6 \times 10^{-14} \ll |Z_a| \approx 4 \times 10^{-3}$, la sécante donne
$c \approx b$ et Illinois stagne. La parade : retour immédiat de la borne quasi-nulle, et en fin
de boucle on retourne la **meilleure borne** (celle de plus petit $|Z|$), pas le milieu.

---

## 6. Pourquoi le parallélisme marche (le ×4)

Les intervalles à affiner sont **indépendants** les uns des autres : localiser le zéro n°500 ne
dépend pas du zéro n°499. On peut donc répartir les intervalles sur les 4 cœurs du processeur, qui
travaillent simultanément.

> **Contrainte technique :** charger le module C `.so` **après** le `fork()` des processus
> (c'est-à-dire localement, à l'intérieur de chaque worker). Les objets GMP/MPFR ne se partagent
> pas proprement à travers un `fork()` — c'est ce qui faisait planter les premières tentatives.
> `parallel_scanner.py` gère ce chargement post-fork.

---

## 7. Le bilan de l'optimisation

| Levier | Sur quoi il agit | Gain |
|---|---|---|
| `Z_batch()` vectorisé (NumPy / GPU) | la **détection** | ~×50 |
| `illinois_mpfr.so` en C / libmpfr | l'**affinage** | ~×39 |
| 4 workers en parallèle | l'ensemble | ~×4 |

Combinés, ces leviers font passer de **~1 zéro/s** (v5 séquentiel) à **~15–20 zéros/s** (v4.1).
Un run complet jusqu'à $T = 10\,000$ passe ainsi de plusieurs heures à environ 10–15 minutes.

### Pistes pour aller plus loin
- **GPU** : `Z_batch` peut tourner sur la GTX 960M via CuPy (détection en parallèle massif).
- **Pas de balayage adaptatif** : balayer plus large là où les zéros sont espacés (petits $t$),
  plus fin là où ils se resserrent (grands $t$) — économise des calculs de détection inutiles.

---

## 8. Distinction expérimental / conjecture / preuve

> Ces méthodes **localisent numériquement** les zéros non-triviaux de $\zeta(s)$ sur la droite
> critique $\text{Re}(s) = \tfrac{1}{2}$. La validation Turing-Backlund garantit la **complétude
> numérique** (aucun zéro manqué) sur l'intervalle calculé. Ces résultats ne constituent **pas une
> preuve** de l'Hypothèse de Riemann.

---

## Voir aussi

### Cours progressif (du débutant à l'expert)
- [[niveau-0-prerequis]] — prérequis
- [[niveau-1-series]] — séries de Dirichlet
- [[niveau-2-analyse-complexe]] — analyse complexe, prolongement analytique
- [[niveau-3-gamma-dirichlet]] — fonction Gamma, équation fonctionnelle
- [[niveau-4-zeta]] — la fonction $\zeta$, fonction $Z$ de Hardy, $\theta(t)$
- [[niveau-5-expert]] — Riemann-Siegel, méthodes avancées
- [[Parcours-complet]] — vue d'ensemble du parcours

### Formules et références
- [[Formules_zeta]] — recueil des formules clés ($\zeta$, $\theta$, $Z$, $\Xi$)
- [[Katex-cheatsheet]] — commandes KaTeX validées sur GitHub

### Méthode numérique et phases du projet
- [[Methode]] — méthodologie générale de calcul des zéros
- [[Etape-1-Calcul-des-zéros-non-triviaux]] — première approche du calcul
- [[Phase-Optimisation-compute_zeros_v3]] — orchestrateur v3 (Riemann-Siegel + Turing)
- [[Phase-C-compute_zeros_v4]] — accélération Illinois en C / libmpfr
- [[Interprétation-des-résultats-de-tests]] — lecture et validation des résultats

---

> ⚠️ **À vérifier avant le push** : les noms entre `[[ ]]` doivent correspondre **exactement**
> aux titres réels de tes pages wiki (sans le `.md`). Corrige ou retire les liens vers des pages
> qui n'existent pas encore, sinon ils seront morts.

---

*Page créée le 1er juin 2026 — `Optimisation-Pourquoi-le-calcul-va-vite.md` — 1 fichier MD créé, 190 lignes.*
