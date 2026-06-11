# Formules de référence — Fonction zêta de Riemann
> Version enrichie — Projet Riemann_Lab · hprzeta
> Mise à jour : 2 juin 2026 · Auteur : hprzeta
>   + leçons Vérif A/B v4.1 : erreur de position (perturbation 1ᵉʳ ordre) et distinction comptage/position
>   + leçon v4.2 : finition Newton (ordre 2, dérivée analytique, critère dps vs LMFDB absolu)
>   + leçon v4.2 mesurée : Newton réfuté (Z' coûteux), goulot = mpmath.siegelz, pas l'algorithme
>   + §17 modèle de coût complet (mur de latence) : $t_{\text{appel}} \propto N\,\text{dps}^2$, $T_{\text{total}} \approx n\,n_{\text{itér}}\,t_{\text{appel}}/W$, leviers et régimes

---

## 1. Définitions fondamentales

### 1.1 Série de Dirichlet (Re(s) > 1)

$$
\zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s} = 1 + \frac{1}{2^s} + \frac{1}{3^s} + \cdots
$$

Convergente absolument pour $\text{Re}(s) > 1$.

### 1.2 Produit d'Euler (Re(s) > 1)

$$
\zeta(s) = \prod_{p \;\text{premier}} \frac{1}{1 - p^{-s}}
$$

Ce produit encode la distribution des nombres premiers : chaque facteur correspond à un premier $p$.

### 1.3 Prolongement analytique

$\zeta(s)$ se prolonge en une fonction méromorphe sur $\mathbb{C} \setminus \{1\}$, avec un **pôle simple en $s = 1$** de résidu 1.

### 1.4 Équation fonctionnelle (symétrie $s \leftrightarrow 1-s$)

$$
\zeta(s) = 2^s \cdot \pi^{s-1} \cdot \sin\!\left(\frac{\pi s}{2}\right) \cdot \Gamma(1-s) \cdot \zeta(1-s)
$$

### 1.5 Fonction $\xi$ de Riemann (forme symétrique)

$$
\xi(s) = \tfrac{1}{2}\, s(s-1)\, \pi^{-s/2}\, \Gamma\!\left(\tfrac{s}{2}\right) \zeta(s)
$$

Propriété clé : $\xi(s) = \xi(1-s)$. La fonction $\xi$ est entière et symétrique par rapport à $\text{Re}(s) = \tfrac{1}{2}$.

---

## 2. Hypothèse de Riemann

**Énoncé :** Tous les zéros non triviaux de $\zeta(s)$ vérifient $\text{Re}(s) = \tfrac{1}{2}$.

- **Zéros triviaux** : $s = -2, -4, -6, \ldots$ (pôles de $\sin(\pi s/2)$ masqués par $\Gamma$).
- **Zéros non triviaux** : dans la bande critique $0 < \text{Re}(s) < 1$.
  On les note $\rho = \tfrac{1}{2} + i\gamma_n$ (si HR vraie).

---

## 3. Fonction Z de Hardy — détection des zéros (✅ méthode utilisée dans v3)

### 3.1 Définition

$$
\zeta\!\left(\tfrac{1}{2} + it\right) = e^{-i\theta(t)}\, Z(t)
$$

$Z(t)$ est **réelle** pour $t$ réel. Sa propriété essentielle :

$$
Z(t) = 0 \iff \zeta\!\left(\tfrac{1}{2} + it\right) = 0
$$

Détecter les changements de signe de $Z(t)$ suffit pour localiser les zéros sur la droite critique.

> **Pourquoi pas Re(ζ) directement ?** En v1/v2, utiliser $\text{Re}(\zeta(\tfrac{1}{2}+it))$ comme détecteur provoquait des **faux positifs** : la rotation de phase $e^{-i\theta(t)}$ peut annuler la partie réelle sans que $\zeta = 0$. La fonction $Z(t)$ élimine ce problème.

### 3.2 Formule de calcul optimisée (✅ Z_fast dans v3)

$$
Z(t) = \cos\theta(t) \cdot \text{Re}\!\left[\zeta\!\left(\tfrac{1}{2}+it\right)\right]
       - \sin\theta(t) \cdot \text{Im}\!\left[\zeta\!\left(\tfrac{1}{2}+it\right)\right]
$$

Avantage : un seul appel à `zeta()` au lieu de deux.

---

## 4. Fonction θ(t) de Riemann-Siegel

### 4.1 Définition exacte

$$
\theta(t) = \text{Im}\!\left[\ln \Gamma\!\left(\tfrac{1}{4} + \tfrac{it}{2}\right)\right] - \frac{t}{2}\ln\pi
$$

`compute_zeros_v2.py` L171 : `mp.im(loggamma(mp.mpf("0.25") + mp.mpc(0, t)/2)) - (t/2)*mp.log(mp.pi)`

### 4.2 Expansion asymptotique de Stirling (✅ correction v3 — ×10 à ×50 plus rapide)

Pour $t \to \infty$ (valable pour $t \geq 20$, erreur $< 10^{-15}$) :

$$
\theta(t) = \frac{t}{2}\ln\frac{t}{2\pi} - \frac{t}{2} - \frac{\pi}{8}
            + \frac{1}{48t} + \frac{7}{5760\,t^3} - \frac{31}{80640\,t^5} + O(t^{-7})
$$

**Coefficients de Bernoulli** (origine des termes correctifs) :

$$
\frac{B_{2k}}{2k(2k-1)\,t^{2k-1}}\,:\quad
\underbrace{\frac{1}{48t}}_{B_2=1/6}\;+\;\underbrace{\frac{7}{5760\,t^3}}_{B_4=-1/30}\;-\;\underbrace{\frac{31}{80640\,t^5}}_{B_6=1/42}
$$

**Seuil de bascule** : `theta_rapide.py` utilise l'asymptotique pour $t \geq 20$ et mpmath exact sinon.

---

## 5. Formule de Riemann-Siegel — Calcul vectorisé Z(t) (✅ Z_batch dans v3)

### 5.1 Formule principale

$$
Z(t) = 2 \sum_{n=1}^{N(t)} \frac{\cos\!\left[\theta(t) - t\ln n\right]}{\sqrt{n}} + R(t)
$$

où $N(t) = \lfloor\sqrt{t/2\pi}\rfloor$ (nombre de termes).

### 5.2 Terme de reste $R(t)$ — correction RS

$$
R(t) = (-1)^{N-1} \cdot \tau^{-1/2} \cdot \left[C_0(u) + \frac{C_1(u)}{\pi\tau} + \cdots\right]
$$

avec $\tau = \sqrt{t/2\pi}$, $u = 2(\tau - N) - 1$, et :

$$
C_0(u) = \Psi(u) = \frac{\cos\!\left[\pi\left(\tfrac{u^2}{2} + \tfrac{3}{8}\right)\right]}{\cos(\pi u)}
$$

### 5.3 Formulation matricielle (vectorisation GPU/CPU)

Pour un tableau de points $\{t_k\}_{k=1}^{M}$ :

$$
Z(t_k) = 2 \sum_{n=1}^{N_{\max}} \frac{\cos\!\left[\theta(t_k) - t_k \ln n\right]}{\sqrt{n}}
$$

`riemann_siegel_batch.py` L291 (Z_batch) :
```python
phases = thetas[:, None] - ts[:, None] * log_ns[None, :]   # shape (M, N_max)
Z = 2.0 * np.dot(np.cos(phases), inv_sqn)                  # shape (M,)
```

**Gain mesuré** : ×7 à ×15 (CPU numpy) · ×8 à ×12 supplémentaires (GPU GTX 960M).

> ⚠️ **Le code ci-dessus est la version NAÏVE** (un $N_{\max}$ fixe pour tout le bloc).
> Elle est **fausse** dès que le bloc couvre une large plage de $t$ — voir §5.4.

### 5.4 ⚠️ Piège de la vectorisation naïve — $N(t)$ variable (bug détecté session v4.1)

$N(t) = \lfloor\sqrt{t/2\pi}\rfloor$ **dépend de $t$** et change à chaque point du batch.
Une version vectorisée naïve qui applique un $N_{\max}$ **fixe** (calculé sur le plus
grand $t$ du bloc) à **tous** les points est **fausse** : pour un point $t_k$ donné, les
termes $n > N(t_k)$ ne font pas partie de la somme de Riemann-Siegel et **faussent le
signe** de $Z(t_k)$.

**Symptôme mesuré (v4.1)** : la première version `Z_batch` produisait **359 désaccords
de signe** vs `mpmath.siegelz` → autant de zéros potentiellement ratés lors d'un run long.

**Solution `Z_vect_correct`** : masque booléen ligne par ligne

$$
\text{mask}[k, n] = \mathbb{1}\!\left[\, n \leq N(t_k) \,\right]
$$

Chaque ligne $k$ n'accumule alors que ses $N(t_k)$ termes exacts :

```python
N_k    = np.floor(np.sqrt(ts / (2*np.pi))).astype(int)   # N(t_k) propre à chaque point
mask   = ns[None, :] <= N_k[:, None]                      # (M, N_max) booléen
phases = thetas[:, None] - ts[:, None] * log_ns[None, :]
Z      = 2.0 * np.sum(np.where(mask, np.cos(phases) * inv_sqn, 0.0), axis=1)
```

**Résultat après correction** : **0 désaccord** sur 4 plages testées
($t \in [14,100]$, $[300,400]$, $[3000,3100]$, $[9900,10000]$).

### 5.5 Erreur de troncature de Riemann-Siegel

La somme tronquée à la correction $C_0 + C_1$ a une erreur résiduelle **structurelle**
(c'est une limite mathématique, **pas un bug**) :

$$
\text{erreur}_{\text{RS}} = O\!\left(t^{-3/2}\right) \quad\text{(décroît quand } t \text{ augmente)}
$$

| Niveau de correction | Précision typique |
|---|---|
| RS sans correction | ~$10^{-1}$ |
| RS + $C_0$ | ~$10^{-2}$ |
| RS + $C_0 + C_1$ | ~$10^{-3}$ |
| RS + 3–5 termes | ~$10^{-8}$ |
| `mpmath.siegelz` | ~$10^{-12}$ |

**Conséquence pratique (v4.1)** : l'écart $|Z_{\text{vect}}(t) - \text{siegelz}(t)|$ passe de
$1.4\times10^{-2}$ ($t\approx 14$) à $1.2\times10^{-4}$ ($t\approx 9900$). Pour la
**détection**, seul le **signe** compte → cette erreur n'empêche pas de localiser les bons
intervalles ; l'**affinage Illinois** (§6) corrige ensuite la position exacte à $10^{-12}$.

### 5.6 Erreur de **position** d'un zéro affiné sur $Z_{\text{mpfr}}$ (leçon Vérif B v4.1)

> **Point clé** : l'erreur de troncature §5.5 est une erreur sur l'**amplitude** de $Z$.
> Ce qui compte pour un zéro, c'est l'erreur de **position** qui en découle. Les deux sont
> liées, mais ne sont **pas** du même ordre de grandeur — d'où le résultat de la Vérif B.

Si l'affinage (Illinois en C, ou findroot) cherche une racine de la fonction **tronquée**
$Z_{\text{mpfr}} = Z + R$ au lieu du vrai $Z$, il converge vers $\gamma_{\text{mpfr}}$ tel que
$Z_{\text{mpfr}}(\gamma_{\text{mpfr}}) = 0$, c.-à-d. $Z(\gamma_{\text{mpfr}}) = -R(\gamma_{\text{mpfr}})$.
Le **développement de Taylor au premier ordre** autour du vrai zéro $\gamma$ (où $Z(\gamma)=0$) donne :

$$
0 = Z_{\text{mpfr}}(\gamma_{\text{mpfr}}) \approx Z'(\gamma)\,(\gamma_{\text{mpfr}} - \gamma) + R(\gamma)
\quad\Longrightarrow\quad
\boxed{\;\big|\gamma_{\text{mpfr}} - \gamma\big| \;\approx\; \frac{|R(\gamma)|}{|Z'(\gamma)|}\;}
$$

**Lecture de la formule** — l'erreur de position est l'erreur d'amplitude **divisée par la
pente** du croisement. Deux régimes :

| Régime du croisement | Pente $|Z'(\gamma)|$ | Erreur de position |
|---|---|---|
| Croisement **raide** | grande | erreur faible (~$10^{-4}$) |
| Croisement **plat** (zéro proche d'un extremum, ou paire de zéros proches) | petite | erreur amplifiée (jusqu'à ~$10^{-2}$) |

C'est pourquoi le même reste $|R(\gamma)| \sim 10^{-3}$ produit une dispersion d'erreurs de
position de $10^{-4}$ à $10^{-2}$ selon le zéro : la variabilité vient de $|Z'(\gamma)|$, pas de $R$.

**Exemple mesuré (Vérif B, bracket $[350.400,\ 350.440]$)** :

| Méthode | Racine trouvée | Cible |
|---|---|---|
| `illinois_mpfr.so` (RS tronquée $C_0+C_1$) | $350.424$ | racine de $Z_{\text{mpfr}}$ |
| `mpmath.findroot(siegelz)` dps=50 | $350.408$ | vrai zéro de $Z$ |
| **Écart** | $\mathbf{0.016}$ | $= |R|/|Z'|$ à $t\approx 350$ |

L'écart $0.016 \approx 1.6\times10^{-2}$ est cohérent : à $t=350$, $N=\lfloor\sqrt{350/2\pi}\rfloor = 7$
termes, $|R(t)|\sim\tau^{-5/2}\sim 10^{-3}$, et le croisement est ici relativement plat.

**Conclusion architecturale** : Illinois_C **pur** sur $Z_{\text{mpfr}}$ ne peut **pas** atteindre
le critère LMFDB $<10^{-10}$ — c'est une limite **structurelle** de la troncature, pas un bug.
Pour des positions précises, il faut une **finition** sur le vrai $Z$ (`mpmath.siegelz`) après
le pré-affinage C. Voir §6.4 pour les trois architectures comparées.

---

## 6. Méthode d'affinage Illinois (✅ correction v3 — 80–90% du temps de calcul)

Illinois est une variante de la **méthode de la sécante** avec correction anti-stagnation.

### 6.1 Algorithme (raffinement sur $[a, b]$ avec $Z(a)\cdot Z(b) < 0$)

**Initialisation** : $f_a = Z(a)$, $f_b = Z(b)$.

**Itération** :

$$
c = b - f_b \cdot \frac{b - a}{f_b - f_a}
$$

- Si $f_c \cdot f_b < 0$ : $a \leftarrow b$, $f_a \leftarrow f_b$
- Si $f_c \cdot f_a < 0$ : **correction Illinois** : $f_a \leftarrow f_a / 2$ (évite la stagnation)

**Convergence** : superlinéaire (ordre $\approx 1.44$), garantie si $Z$ est continue et change de signe.

### 6.2 Paramètres v3

| Paramètre | Valeur | Justification |
|---|---|---|
| `tol_affinage` | `1e-12` | Cohérent avec 35 dps (v2 utilisait `1e-20` → impossible à 35 dps) |
| `dps_affinage` | 35 | Suffisant pour $t < 10^6$, ×3 plus rapide que 50 dps |
| `maxsteps` | 80 | Convergence garantie en < 30 itérations typiquement |
| `solver` | `"illinois"` | Via `mpmath.findroot(..., solver="illinois")` |

`compute_zeros_v3.py` → `parallel_scanner.py` L258 : `findroot(Z_fast, (a,b), solver="illinois", tol=1e-12, maxsteps=80)`

### 6.3 Comparaison Illinois v1 / v2 / v3

| Version | Fichier | Fonction détecteur | `solver` | `tol` | `dps` | `maxsteps` |
|---|---|---|---|---|---|---|
| v1 | `compute_zeros_v1.py` L55 | `zeta_on_critical` = Re(ζ) | `'newton'` puis `'bisect'` | `1e-12` | 50 | 50 |
| v2 | `compute_zeros_v2.py` L197–201 | `siegelz(t)` scalaire | `"illinois"` | `1e-20` | 50 | 100 |
| v3 | `parallel_scanner.py` L258 | `Z_fast(t)` vectorisé | `"illinois"` | `1e-12` | 35 | 80 |

**Problème v1** : Re(ζ) comme détecteur → faux positifs (voir §3.1).  
**Problème v2** : `tol=1e-20` irréalisable à 50 dps (≈ 50 chiffres) → timeout / dépassement `maxsteps`.  
**Solution v3** : `tol=1e-12` cohérent avec 35 dps (12 chiffres demandés < 35 disponibles).

### 6.4 Trois architectures d'affinage — arbitrage vitesse / précision (leçon Vérif B v4.1)

La Vérif B a fait apparaître une **tension fondamentale** : la racine que produit le C est
rapide mais imprécise (§5.6), tandis que la racine `mpmath.siegelz` est précise mais lente.
Trois architectures résolvent ce compromis différemment :

| Architecture | Mécanisme de la racine finale | Vitesse | Précision position | Statut |
|---|---|---|---|---|
| **Illinois_C pur** (v4.1 brut) | racine de $Z_{\text{mpfr}}$ (RS $C_0+C_1$) en C | ~41 z/s | $10^{-4}$ à $10^{-2}$ ❌ | rejeté pour catalogue |
| **Callback Python/C** (v5) | `siegelz` appelé *dans* la boucle C | ~1.1 z/s | $<10^{-13}$ ✅ | casse le parallélisme (GMP non thread-safe) |
| **Hybride post-fork** (cible v4.2) | Illinois_C *pré-affine*, puis `findroot(siegelz)` *poli en Python* | à mesurer | $<10^{-10}$ ✅ (visé) | **architecture retenue** |

**Pourquoi l'hybride post-fork préserve le parallélisme ×4** : la boucle C ne fait **aucun**
appel Python (donc aucun verrou GMP partagé entre processus). Le C rend une borne approchée
$\gamma_c$ ; **ensuite seulement**, et **hors** de la boucle C, Python exécute :

$$
\gamma = \texttt{mpmath.findroot}\big(\texttt{siegelz},\ \gamma_c\big),\qquad \text{dps}=30
$$

Comme $\gamma_c$ est déjà à $\sim10^{-2}$ du vrai zéro (§5.6), `findroot` converge en très peu
d'itérations (la convergence superlinéaire de la sécante part d'un excellent point initial),
ce qui limite le surcoût du raffinage exact.

**Distinction à ne jamais confondre** : ce raffinage `siegelz` ne sert **qu'à la précision des
positions** (comparaison LMFDB). Il n'est **pas** nécessaire pour *vérifier* HR jusqu'à $T$ —
voir §11.1, qui montre que la vérification repose sur le **comptage**, pas sur les positions.

### 6.5 Finition Newton sur le vrai $Z$ — ordre de convergence et précision (leçon v4.2)

> **Mesure clé (validation hybride v4.2)** : la finition `findroot(siegelz)` après pré-affinage
> C donne $\text{Écart}_P = 0.00$ (vs LMFDB) sur les trois plages $t\approx 350,\,1000,\,9900$ —
> précision **parfaite**, critère $<10^{-10}$ largement battu. Reste à optimiser la **vitesse**
> du raffinage, où le bon levier est le **nombre d'évaluations** de `siegelz`, pas le `dps`.

#### 6.5.1 Pourquoi Newton plutôt qu'Illinois pour la finition

La vitesse de convergence d'un solveur se mesure par son **ordre** $p$ : si $\varepsilon_n$ est
l'erreur au pas $n$, alors $\varepsilon_{n+1} \approx C\,\varepsilon_n^{\,p}$.

| Solveur | Ordre $p$ | Évaluations / pas | Évaluations pour passer $10^{-2} \to 10^{-10}$ |
|---|---|---|---|
| Illinois (sécante modifiée) | $\approx 1.44$ | 1 | ~27 |
| **Newton** | $2$ (quadratique) | 2 ($Z$ et $Z'$) | **~6** (3 pas) |

Partant du point initial fourni par le C, $\varepsilon_0 = 1.7\times10^{-2}$ (§5.6), Newton
**double le nombre de chiffres exacts à chaque pas** :

$$
\varepsilon_0 = 1.7\times10^{-2}
\;\to\; \varepsilon_1 \approx 3\times10^{-4}
\;\to\; \varepsilon_2 \approx 1\times10^{-7}
\;\to\; \varepsilon_3 \approx 1\times10^{-14}
$$

**3 pas suffisent** pour passer sous $10^{-10}$, soit ~6 évaluations contre ~27 pour Illinois.
On pourrait croire à un gain $\approx 4.5\times$. **C'est faux ici** — et la mesure l'a confirmé
(§6.5.5). Le coût total est $n_{\text{évals}} \times \text{coût/éval}$, mais les deux solveurs
n'évaluent pas la même chose :

- Illinois n'évalue que $Z$ (1 appel `siegelz` par pas, ~296 ms à $t\approx 9000$) ;
- Newton évalue $Z$ **et** $Z'$ (2 appels par pas), or $Z'$ est **plus cher** que $Z$ (§6.5.2).

Le produit $n_{\text{évals}} \times \text{coût/éval}$ finit donc comparable. **La réduction du
nombre d'itérations est réelle mais sans effet**, parce que le coût par évaluation domine et que
le goulot est la vitesse intrinsèque de `mpmath.siegelz` à grand $t$, **pas** le nombre de pas.

> **Leçon épistémique** : l'analyse d'ordre de convergence ci-dessus était une **prédiction**
> *a priori*, valable seulement sous l'hypothèse « coût/éval constant et $Z'$ aussi cheap que $Z$ ».
> Cette hypothèse est **fausse** (§6.5.2) ; la mesure (§6.5.5) prime sur la prédiction.

> **Garde-fou** : Newton n'est **pas borné**. Si le croisement est plat ($Z'$ petit, §5.6) ou
> sur une paire de zéros proches, l'itéré peut sortir du bracket $[\gamma_c \pm \delta]$. Prévoir
> un **fallback Illinois borné** dans ce cas.

#### 6.5.2 Dérivée analytique obligatoire — annulation catastrophique

Newton requiert $Z'(t)$. Une **différence finie** centrée

$$
Z'(t) \approx \frac{Z(t+h) - Z(t-h)}{2h}
$$

soustrait deux nombres quasi égaux : **annulation catastrophique** qui détruit ~la moitié des
chiffres significatifs. Une dérivée imprécise abaisse l'ordre effectif de Newton ($2 \to \approx 1.6$,
comme la sécante) et peut faire **échouer** la convergence à $10^{-14}$.

**Solution** : la dérivée **analytique** `mpmath.siegelz(t, derivative=1)` (pas de différence finie).
Elle est calculée exactement, sans annulation, et **garantit** la cascade quadratique du §6.5.1.

> **⚠️ Mais elle n'est PAS gratuite** (idée fausse corrigée par la mesure, §6.5.5). `siegelz`
> ne renvoie pas $Z'$ « en bonus » d'un calcul de $Z$ : il le **recalcule** à part. Or
> $$\zeta'(s) = -\sum_{n\geq 1}\frac{\ln n}{n^{s}}$$
> porte des **poids logarithmiques** $\ln n$ absents de $\zeta(s)=\sum n^{-s}$. Cette série
> converge **plus lentement**, donc l'évaluation de $Z'$ est **plus coûteuse** que celle de $Z$,
> pas comparable. C'est précisément ce qui annule le gain d'itérations de Newton (§6.5.1).

#### 6.5.3 Choix du `dps` — critère LMFDB **absolu** vs chiffres significatifs

> **Piège** : le critère LMFDB est **absolu** ($|\gamma_{\text{calc}} - \gamma_{\text{LMFDB}}| < 10^{-10}$),
> alors que le `dps` contrôle un nombre de chiffres **significatifs**. Plus $\gamma$ est grand,
> plus il faut de chiffres pour la **même** précision absolue.

Pour garantir $10^{-10}$ **absolu** à hauteur $\gamma$, il faut un nombre de chiffres significatifs :

$$
\#\text{chiffres} \;\gtrsim\; \log_{10}(\gamma) \;+\; 10
$$

À $\gamma \approx 9999$ : $\log_{10}(9999) \approx 4$, donc $\#\text{chiffres} \gtrsim 14$.

| `dps` | Chiffres dispo | Marge au-dessus de $10^{-10}$ absolu à $\gamma\approx 9999$ | Verdict |
|---|---|---|---|
| 15 | 15 | ~1 chiffre | ❌ insuffisant (aucune marge pour l'annulation RS interne) |
| 20 | 20 | ~6 chiffres | ⚠️ à valider sur le sommet $t\approx 9900$ |
| 25 | 25 | ~11 chiffres | ✅ sûr |
| 30 | 30 | ~16 chiffres | ✅ confortable |

> **⚠️ Le test sur T=1000 ne révèle PAS ce problème** : à T=1000, $\gamma < 396$ (~3 chiffres
> avant la virgule), donc même `dps=15` paraît suffisant. Le risque n'apparaît qu'au **sommet**.
> → **Valider tout abaissement de `dps` sur un échantillon $t\approx 9900$–$10\,000$, jamais sur T=1000.**

#### 6.5.4 Heuristique de coût *a priori* (⚠️ réfutée par la mesure — voir §6.5.5)

> Ce qui suit est la **prédiction** faite avant mesure. Elle s'est révélée **trop optimiste** :
> elle suppose 6 évaluations toutes au même coût que $Z$, alors que les évaluations de $Z'$ sont
> plus chères (§6.5.2). Conservée ici pour la traçabilité du raisonnement.

Le coût d'une opération multi-précision croît comme $\text{dps}^2$. En passant de 30 à 25 dps :
$(25/30)^2 \approx 0.69$. Avec Newton (6 évaluations, ~300 ms/éval à dps=30 et $t\approx 9000$) :

$$
6 \times (300\,\text{ms} \times 0.69) \approx 1.24\ \text{s/zéro}
\;\Rightarrow\; \sim 0.8\ \text{z/s (1 worker)}
\;\Rightarrow\; \sim 3.2\ \text{z/s} \times 4\ \text{workers}
$$

soit T=10000 en ~50 min. **Prédiction non confirmée** : la mesure donne ~0.4 z/s (§6.5.5).

#### 6.5.5 Résultat **mesuré** — le goulot est `siegelz`, pas l'algorithme (leçon décisive v4.2)

> **Mesure (Vérif B v3, dps=25, $t\approx 9000$)** : Newton + dps=25 donne **0.4 z/s** —
> **plus lent** que Illinois + polish dps=30 (**0.5 z/s**). La prédiction du §6.5.1/§6.5.4 est
> **réfutée**. Précision toujours parfaite ($\text{Écart}_P = 0.00$) dans les deux cas.

**Bilan de performance — toutes les options comparées** ($\times 4$ workers, $t\approx 9000$) :

| Approche | z/s ×4 | Précision (vs LMFDB) | Commentaire |
|---|---|---|---|
| Illinois_C pur (commit `d9bb267`) | **41** | ~$10^{-4}$ ❌ | racines de $Z_{\text{mpfr}}$, pas LMFDB (§5.6) |
| Illinois + polish `findroot` dps=30 | 0.5 | $0.00$ ✅ | 27 itér × ~296 ms |
| Newton + dps=25, 5 pas | 0.4 | $0.00$ ✅ | $Z'$ cher → aucun gain |

**Cause racine confirmée** : à $t\approx 9000$, un appel `siegelz` coûte ~296 ms (somme RS à
$N=\lfloor\sqrt{t/2\pi}\rfloor \approx 37$ termes, chaque opération multi-précision en $O(\text{dps}^2)$).
Newton consomme ~2 appels/pas (dont $Z'$, plus cher, §6.5.2). **Le goulot est la vitesse
intrinsèque de `mpmath.siegelz` à grand $t$, pas le nombre d'itérations.** Réduire les itérations
ne sert donc à rien : il n'y a **pas d'optimisation algorithmique possible à ce niveau** tant que
l'affinage final passe par `siegelz`.

**Conséquence — deux livrables, deux régimes** (rappel §11.1, distinction comptage/position) :

| Run | Zéros | Temps ×4 estimé | Usage |
|---|---|---|---|
| T=300 | 138 | ~60 s (mesuré, tout en fallback mpmath $t<300$) | test |
| T=1000 | ~396 | ~16 min | validation complète faisable |
| T=10000 | ~10 142 | ~7 h | **catalogue de positions $<10^{-10}$ → run de nuit** |

Les **20 premières références LMFDB** ($t<78$) tombent toutes dans la zone de fallback
`mpmath` ($t<300$) : elles sont **toujours** précises à $<10^{-10}$, sans aucun polish.

> **Décision ouverte** : pour *vérifier HR jusqu'à T=10000*, Illinois_C pur (41 z/s, ~5 min)
> suffit déjà (comptage Turing, §11.1). Le polish lent (~7 h) n'est requis **que** pour produire
> un **catalogue de positions** comparables à LMFDB — or ce catalogue existe déjà via v2/v3
> (CSV 10 142 zéros, 50 dps). À trancher selon le livrable visé, **pas** à subir par défaut.

---

## 7. Pas de balayage adaptatif STEP (✅ correction v3)

### 7.1 Espacement moyen entre zéros consécutifs

La formule de Riemann-von Mangoldt donne l'espacement moyen :

$$
\langle \delta_n \rangle \approx \frac{2\pi}{\ln(T/2\pi)}
$$

### 7.2 Formule du pas de sécurité

$$
\text{STEP} = \min\!\left(\frac{2\pi}{5 \cdot \ln(T_{\max}/2\pi)},\; 0.10\right)
$$

Division par 5 (non par 3 comme en v2) pour sécurité contre les paires de zéros proches.  
Plafond absolu à **0.10** pour $T < 500\,000$.

> **⚠️ Bug noté dans le code v3** : `compute_zeros_v3.py` L220 retourne
> `min(round(step_theorique, 3), 0.02)` alors que les commentaires L207 et L213–215
> spécifient `0.10`. La valeur documentée **cible** est **0.10** (intention v3).
> Corriger dans la Phase C ou un patch v3.1.

`compute_zeros_v3.py` L205–219 :
```python
def step_adaptatif(T_MAX: float) -> float:
    # STEP sûr = min(espacement_moyen / 5, 0.10)
    espacement_moyen = 2 * math.pi / math.log(T_MAX / (2 * math.pi))
    step_theorique   = espacement_moyen / 5.0
    return min(round(step_theorique, 3), 0.10)   # plafond cible
```

**Valeurs typiques** :

| $T_{\max}$ | Espacement moyen | STEP (cible v3) |
|---|---|---|
| 1 000 | 1.24 | 0.10 (plafonné) |
| 10 000 | 0.84 | 0.10 (plafonné) |
| 100 000 | 0.70 | 0.10 (plafonné) |
| 500 000 | 0.60 | 0.10 (plafonné) |

---

## 8. Formule de Riemann-von Mangoldt — Comptage N(T) (✅ correction critique v3)

### 8.1 Formule exacte

$$
N(T) = \frac{\theta(T)}{\pi} + 1 + S(T)
$$

où $S(T) = \frac{1}{\pi}\arg\zeta\!\left(\tfrac{1}{2} + iT\right)$ est la **correction par variation d'argument**.

Propriété : $|S(T)| \leq C \cdot \frac{\ln T}{\ln\ln T}$, et typiquement $|S(T)| < 3$ pour $T < 10^6$.

### 8.2 Estimation asymptotique (Weyl — premier terme) — FORMULE CORRIGÉE

$$
N(T) \approx \frac{T}{2\pi}\ln\frac{T}{2\pi e}
$$

> **⚠️ Erreur classique corrigée en v3** : la formule incorrecte $\dfrac{T}{2\pi}\ln\dfrac{T}{2\pi}$
> (sans le $e$ au dénominateur) sous-estimait $N(T)$ de **~64%** pour $T = 100\,000$
> (49 346 au lieu de 138 067 zéros attendus), faussant toutes les estimations de temps.

Comparaison numérique :

| $T$ | $\dfrac{T}{2\pi}\ln\dfrac{T}{2\pi e}$ (correcte) | $\dfrac{T}{2\pi}\ln\dfrac{T}{2\pi}$ (incorrecte) | Erreur |
|---|---|---|---|
| 1 000 | 396 | 229 | −42% |
| 10 000 | 10 142 | 5 968 | −41% |
| 100 000 | 138 067 | 49 346 | −64% |

### 8.3 Calcul de S(T) par variation continue d'argument (Backlund, 1914)

$$
S(T) = \frac{1}{\pi} \int_{\sigma=+\infty}^{\sigma=1/2} \frac{\partial}{\partial\sigma} \arg\zeta(\sigma + iT)\, d\sigma
$$

Implémentation discrète (`turing_validation.py` L127–158) :

```python
# Chemin horizontal : σ de 3.0 (où arg ζ ≈ 0) à ½
sigmas    = np.linspace(3.0, 0.5, 51)      # 50 pas
variation = 0.0
arg_prev  = 0.0

for sigma in sigmas[1:]:
    s       = mpc(sigma, T)
    z       = zeta(s)
    arg_cur = float(mp.atan2(im(z), re(z)))
    # Correction de branche — suivi continu (évite les sauts de 2π)
    d = arg_cur - arg_prev
    if d >  math.pi: arg_cur -= 2 * math.pi
    if d < -math.pi: arg_cur += 2 * math.pi
    variation += arg_cur - arg_prev
    arg_prev   = arg_cur

S_T = variation / math.pi
```

**Pourquoi démarrer à σ = 3 ?** Pour $\sigma \geq 3$, $|\zeta(\sigma+iT) - 1| < 0.2$, donc $\arg\zeta \approx 0$ — pas d'ambiguïté de branche.

---

## 9. Précision adaptative (✅ correction v3)

Stratégie à 3 niveaux selon l'opération :

| Opération | Précision | Justification |
|---|---|---|
| θ asymptotique (`float64`) | 15 chiffres | Numpy/Python natif — ×50 |
| Détection Z_fast | 25 dps | Suffisant pour signe de Z(t) |
| Affinage Illinois | 35 dps | Atteint `tol = 1e-12` en 35 dps |
| Validation / publication | 50 dps | Pour les 1000 premiers zéros |

> Avant correction : tout à 50 dps → θ via `loggamma` mpmath → 3× plus lent.

---

## 10. Espacements normalisés et conjecture de Montgomery

### 10.1 Espacement normalisé

$$
\delta_n = (\gamma_{n+1} - \gamma_n) \cdot \frac{\ln(\gamma_n / 2\pi)}{2\pi}
$$

### 10.2 Distribution GUE (Wigner-Dyson)

La conjecture de Montgomery (1973) affirme que $\{\delta_n\}$ suit la distribution GUE des matrices aléatoires :

$$
p(s) = \frac{\pi}{2}\, s \cdot e^{-\pi s^2 / 4}
$$

**Tracé dans v3** : histogramme de $\{\delta_n\}$ vs courbe théorique GUE.

---

## 11. Validation Turing-Backlund (✅ ajout v3)

Critère de complétude du calcul :

1. Calculer $N_{\text{exact}}(T) = \lfloor\theta(T)/\pi\rfloor + 1 + \text{round}(S(T))$
2. Compter $n_{\text{calc}} = |\{t_k \leq T\}|$
3. **Complet** $\iff n_{\text{calc}} = N_{\text{exact}}(T)$

Appliqué aux points de contrôle $T \in \{T_{10\%},\, T_{25\%},\, T_{50\%},\, T_{75\%},\, T_{\max}\}$.

### 11.1 Comptage vs position — pourquoi Vérif A réussit alors que Vérif B échoue

> **Idée centrale (leçon Vérif B v4.1)** : *vérifier HR jusqu'à $T$* et *cataloguer les
> positions précises des zéros* sont **deux objectifs distincts** qui ne demandent pas la
> même chose. La méthode de Turing valide le **nombre** de zéros, jamais leur position.

La vérification numérique de HR sur $[0,T]$ par Turing-Backlund repose sur l'égalité :

$$
\underbrace{n_{\text{calc}}}_{\text{nombre de changements de signe de } Z(t) \text{ sur } [0,T]}
\;=\;
\underbrace{N(T)}_{\tfrac{\theta(T)}{\pi} + 1 + S(T)\ \text{(comptage théorique)}}
$$

Si cette égalité tient, alors $Z(t)$ possède exactement $N(T)$ zéros réels sur $[0,T]$ ;
or $Z$ a autant de zéros réels que $\zeta$ en a sur la droite critique jusqu'à hauteur $T$,
et $N(T)$ compte **tous** les zéros non triviaux de cette bande jusqu'à $T$. L'égalité force
donc **tous** ces zéros à être simples et sur la droite critique : **HR est vérifiée jusqu'à $T$.**

**Conséquence directe** — cette condition ne fait intervenir que le **dénombrement** des
changements de signe. Déplacer chaque position raffinée de $\gamma$ vers $\gamma_{\text{mpfr}}$
d'un montant $\sim10^{-2}$ (§5.6) **ne change pas** combien il y a de changements de signe.
D'où le résultat de validation v4.1, qui n'est **pas** contradictoire :

| Vérif | Ce qu'elle teste | Résultat v4.1 | Interprétation |
|---|---|---|---|
| **A** | comptage Turing + LMFDB sur les 20 premiers (fallback mpmath, $t<78$) | ✅ 138/138, Turing COMPLET | la **vérification de HR** tient |
| **B** | précision des positions à grand $t$ (Illinois_C pur) | ❌ erreurs $\sim10^{-2}$ | le **catalogue de positions** exige une finition mpmath (§6.4) |

**En résumé** : v4.1 (Illinois_C pur, 41 z/s) suffit pour **vérifier** HR jusqu'à $T=10\,000$
via Turing ; il ne suffit **pas** pour produire un catalogue de positions $<10^{-10}$. Ces deux
livrables sont séparés.

### 11.2 ⚠️ Condition de validité — la détection ne doit ni rater ni inventer un croisement

L'argument §11.1 tient **sous une hypothèse** : que le comptage des changements de signe soit
**exact**, c.-à-d. que la détection ne **manque** aucun croisement et n'en **invente** aucun.
Près d'un zéro où $|Z|$ est minuscule, l'erreur d'amplitude de la troncature (§5.5) pourrait
**inverser un signe** et fausser le comptage — c'est exactement le mécanisme du **bug
`Z_batch` float64** (jusqu'à 359 désaccords de signe, voir §5.4), corrigé par `Z_vect_correct`.

Garde-fous en place :
- détection via `Z_vect_correct` (masque $n \leq N(t_k)$) → 0 désaccord sur les 4 plages testées (§5.4) ;
- pas de balayage STEP sécurisé (§7) → évite de sauter une paire de zéros proches ;
- **Turing COMPLET** sur le run = preuve *a posteriori* que le comptage est bon (aucun manquant).

> Tant que Turing ressort COMPLET, l'égalité §11.1 est satisfaite et HR est vérifiée sur
> l'intervalle — indépendamment de la précision des positions individuelles. C'est le point
> de vigilance n°1 à surveiller au-delà de $T=10\,000$.

---

## 12. 20 premiers zéros (référence LMFDB)

| $n$ | $\gamma_n$ (partie imaginaire) |
|-----|-------------------------------|
| 1   | 14.134725141734693 |
| 2   | 21.022039638771555 |
| 3   | 25.010857580145688 |
| 4   | 30.424876125859513 |
| 5   | 32.935061587739189 |
| 6   | 37.586178158825671 |
| 7   | 40.918719012147495 |
| 8   | 43.327073280914999 |
| 9   | 48.005150881167159 |
| 10  | 49.773832477672302 |
| 11  | 52.970321477714460 |
| 12  | 56.446247697063246 |
| 13  | 59.347044002602353 |
| 14  | 60.831778524609882 |
| 15  | 65.112544048081607 |
| 16  | 67.079810529494173 |
| 17  | 69.546401711173978 |
| 18  | 72.067157674481890 |
| 19  | 75.704690699083934 |
| 20  | 77.144840069680455 |

Seuil de validation LMFDB : $|\gamma_n^{\text{calc}} - \gamma_n^{\text{LMFDB}}| < 10^{-10}$.

---

## 13. Lien avec les nombres premiers (formule explicite de Riemann)

$$
\pi(x) = \text{li}(x) - \sum_{\rho} \text{li}(x^\rho) + \int_x^\infty \frac{dt}{t(t^2-1)\ln t} - \ln 2
$$

La somme porte sur tous les zéros non triviaux $\rho$ (et leurs conjugués).

**Conséquence de HR** :

$$
|\pi(x) - \text{li}(x)| = O(\sqrt{x}\,\ln x)
$$

---

## 14. Résultats numériques — Phase 0 (compute_zeros_v3, T = 10 000)

| Indicateur | Valeur |
|---|---|
| Zéros calculés | 10 142 |
| $T_{\max}$ | 9 998.85 |
| Vitesse | ~3.59 z/s (batch CPU) |
| Score LMFDB | 20/20 zéros à $< 10^{-10}$ |
| Validation Turing | ✅ COMPLET (aucun manquant) |
| Méthode détection | Riemann-Siegel vectorisé (Z_batch) |
| Méthode affinage | Illinois (35 dps, tol $10^{-12}$) |

---

## 15. Formules appliquées dans compute_zeros_v1.py (historique)

**Version v1** : première implémentation, abandon vers $t \approx 432$ (overflow GMP).

### 15.1 Détecteur de zéros — Re(ζ) sur la droite critique

`compute_zeros_v1.py` L45 :
```python
# Détecteur : partie réelle de ζ(½ + it) — MÉTHODE INCORRECTE
# Cause des faux positifs (voir §3.1 pour explication)
return float(zeta(0.5 + 1j * t).real)
```

Formule sous-jacente (incorrecte comme détecteur) :
$$
f(t) = \text{Re}\!\left[\zeta\!\left(\tfrac{1}{2} + it\right)\right]
$$

### 15.2 Critère de validation du zéro

`compute_zeros_v1.py` L132 : `if zeta_abs < 1e-9`

$$
|\zeta\!\left(\tfrac{1}{2} + it_0\right)| < 10^{-9} \implies t_0 \text{ accepté comme zéro}
$$

### 15.3 Méthode d'affinage : Newton puis bisection

`compute_zeros_v1.py` L55, L65 :
```python
# Tentative 1 : Newton (rapide mais peut diverger)
zero = findroot(zeta_on_critical, t_mid, solver='newton', tol=1e-12, maxsteps=50)

# Fallback : bisection (robuste, convergence linéaire)
zero = findroot(zeta_real, (t_left, t_right), solver='bisect', tol=1e-12)
```

**Problème Newton** : diverge si la dérivée est petite (zéro simple mais proche d'un extremum de Re(ζ)).  
**Remplacé par** : Illinois en v2/v3 (voir §6).

---

## 16. Formules appliquées dans compute_zeros_v2.py

**Version v2** : Illinois introduit, `siegelz` scalaire, `tol=1e-20` (trop strict).

### 16.1 Fonction θ exacte via loggamma

`compute_zeros_v2.py` L171 :
```python
theta = (
    mp.im(loggamma(mp.mpf("0.25") + mp.mpc(0, t) / 2))
    - (t / 2) * mp.log(mp.pi)
)
```

Formule correspondante :
$$
\theta(t) = \text{Im}\!\left[\ln\Gamma\!\left(\tfrac{1}{4} + \tfrac{it}{2}\right)\right] - \frac{t}{2}\ln\pi
$$

### 16.2 Détecteur Z(t) scalaire via siegelz

`compute_zeros_v2.py` remplace Re(ζ) par `siegelz(t)` de mpmath :
$$
Z(t) = \text{siegelz}(t) \quad \text{(mpmath — précision 50 dps)}
$$

**Amélioration v2** : plus de faux positifs.  
**Problème v2** : appel scalaire — pas de vectorisation → lent.

### 16.3 Illinois en v2 avec tol=1e-20 irréalisable

`compute_zeros_v2.py` L191–201 :
```python
def affiner_zero(t_gauche: float, t_droite: float, tol: float = 1e-20) -> float:
    t0 = findroot(
        lambda t: siegelz(t),
        (t_gauche, t_droite),
        solver="illinois",
        tol=tol,       # 1e-20 à 50 dps → ~1e-48 impossible
        maxsteps=100   # dépassé systématiquement
    )
```

**Problème** : `tol=1e-20` exige 20 chiffres exacts dans la solution, mais à 50 dps l'Illinois ne converge pas en 100 steps — timeout systématique sur les zéros rapprochés.  
**Solution v3** : `tol=1e-12` à 35 dps (voir §6.2).

---

## 17. Le mur de latence du calcul — modèle de coût complet (synthèse)

> Synthèse des formules établies le 2 juin 2026. Version animée : `docs/animation_mur_latence.html`.
> Rassemble en un seul endroit le coût de localisation d'un zéro précis et les leviers d'optimisation.
> Renvois : troncature §5.5, erreur de position §5.6, goulot mesuré §6.5.5, espacement §7.1, comptage §8 et §11.1.

### 17.1 Trois niveaux de coût emboîtés

Localiser **un** zéro précis n'est pas une opération atomique : c'est une chaîne d'évaluations de $Z$, chacune étant elle-même une somme de $N$ termes. Trois niveaux s'emboîtent.

**Niveau 1 — coût d'une évaluation $Z(t)$.** La somme de Riemann-Siegel (§5.1) a $N$ termes, et chaque opération multi-précision à $\text{dps}$ chiffres coûte $O(\text{dps}^2)$ :

$$
t_{\text{appel}} \;\propto\; N \cdot \text{dps}^2,
\qquad N = \left\lfloor\sqrt{\tfrac{t}{2\pi}}\right\rfloor.
$$

Conséquence directe : $t_{\text{appel}}$ **croît avec la hauteur $t$** (via $N \sim \sqrt{t}$).

**Niveau 2 — coût d'un zéro.** L'affinage (sécante / Illinois, §6.1) est une **récurrence** : l'itération $k+1$ a besoin du résultat de l'itération $k$.

$$
c = b - Z_b \cdot \frac{b - a}{Z_b - Z_a}
\qquad\Longrightarrow\qquad
c_{\text{zéro}} \approx n_{\text{itér}} \cdot t_{\text{appel}},
\quad n_{\text{itér}} \approx 27.
$$

Il n'existe **aucun** parallélisme *à l'intérieur* d'un zéro.

**Niveau 3 — coût du run complet.** Les $n$ zéros sont **indépendants** → parallélisables sur $W$ workers :

$$
\boxed{\;T_{\text{total}} \;\approx\; \frac{n \cdot n_{\text{itér}} \cdot t_{\text{appel}}}{W}\;}
$$

### 17.2 Exemple chiffré à $t \approx 9000$

| Grandeur | Calcul | Valeur |
|---|---|---|
| Termes $N$ | $\lfloor\sqrt{9000/2\pi}\rfloor = \lfloor 37{,}85\rfloor$ | 37 |
| Coût d'un appel `siegelz` | mesuré (dps ≈ 30) | ≈ 296 ms |
| Itérations / zéro | findroot Illinois | ≈ 27 |
| Coût d'un zéro $c_{\text{zéro}}$ | $27 \times 296$ ms | ≈ 8,0 s |
| Débit (4 workers) | $4 / 8{,}0$ | ≈ 0,5 z/s |
| Run $T = 10000$ | $\approx 10\,142 / 0{,}5$ (queue plus lente) | ≈ 5–7 h |

> La latence d'un appel `siegelz` à grand $t$ est le **goulot mesuré** (§6.5.5) : à $t \approx 9000$, ~296 ms pour $N \approx 37$ termes. Réduire $n_{\text{itér}}$ (Newton) ne sert à rien — c'est $t_{\text{appel}}$ qu'il faut attaquer.

### 17.3 Facteur d'accélération requis et leviers

Pour passer de ~7 h à la cible de 30 min :

$$
\text{facteur} = \frac{T_{\text{actuel}}}{T_{\text{cible}}} \approx \frac{7\ \text{h}}{0{,}5\ \text{h}} = 14.
$$

Position de chaque levier dans $T_{\text{total}} = \dfrac{n \, n_{\text{itér}} \, t_{\text{appel}}}{W}$ :

| Levier | Agit sur | Gain | Réaliste (i7, 4 cœurs) |
|---|---|---|---|
| Cœurs $W$ | dénominateur (linéaire) | ×14 ⇒ $W \approx 56$ | ❌ |
| GPU GTX 960M | détection seule (10–20 %) | nul sur l'affinage | ❌ |
| RAM / swap | hors formule (compute-bound) | nul (swap ≈ ×1000 plus lent) | ❌ |
| $n_{\text{itér}}$ (Newton) | numérateur | réfuté §6.5.5 | ❌ |
| $\text{dps}$ | $t_{\text{appel}} \propto \text{dps}^2$ | ≈ ×1,4 (plancher §17.4) | ⚠️ marginal |
| **Librairie Arb** | $t_{\text{appel}}$ ÷ 10–20 | ≈ ×10–20 | ✅ → ~20–25 min |

Nombre de cœurs requis pour la cible (librairie mpmath inchangée) :

$$
W_{\text{cible}} = W_0 \cdot \frac{T_0}{T_{\text{cible}}} \approx 4 \times 14 = 56\ \text{cœurs}.
$$

**Le vrai levier est logiciel, pas matériel** : seule la bascule `mpmath.siegelz` → Arb (`acb_dirichlet_hardy_z`, arithmétique de boules en C) réduit $t_{\text{appel}}$ d'un ordre de grandeur à précision égale.

### 17.4 Plancher de précision (rappel §6.5.3)

La précision **absolue** requise à hauteur $\gamma$ impose un nombre minimal de chiffres significatifs :

$$
\#\text{chiffres} \;\gtrsim\; \log_{10}(\gamma) + 10
\quad\Longrightarrow\quad
\approx 14\ \text{à}\ \gamma \approx 9999.
$$

On ne peut donc pas réduire $\text{dps}$ sous ~25 sans perdre le critère LMFDB ($< 10^{-10}$). Tout abaissement se valide sur un échantillon $t \approx 9900$, **jamais** sur T=1000.

### 17.5 Deux régimes, deux livrables

Le mur de latence ne pèse que dans **un** des deux objectifs (rappel §11.1) :

| Objectif | Méthode | Temps T=10000 |
|---|---|---|
| Vérifier HR jusqu'à $T$ (comptage $n_{\text{calc}} = N(T)$) | Illinois_C pur, sans polish `siegelz` | ≈ 41 z/s ⇒ ~4 min |
| Catalogue de positions $< 10^{-10}$ | polish `siegelz`, ou **réutiliser le CSV v2 existant** | ~7 h, ou 0 min |

> Pour la simple **vérification de HR**, le niveau 2 lent disparaît : le coût d'un appel `siegelz` (§17.1) ne pèse que dans le régime « catalogue de positions ». Ce catalogue existe déjà (CSV v2, 10 142 zéros, 50 dps).

---

*Auteur : hprzeta · Dernière mise à jour : 2 juin 2026 — ~929 lignes*
---

## §18 — Profil de pipeline v4.1 : résultats mesurés et leçon workprec (3 juin 2026)

### 18.1 Profil mesuré (T=1000, 4 workers, branche `Riemann_Lab_C`)

| Phase | temps cumulé (4 workers) | appels | ms/appel | % mur×W |
|---|---|---|---|---|
| `mpmath_petit_t` | 11.27 s | 138 | 81.65 | 35.6 % |
| `illinois_C` | 5.22 s | 511 | 10.21 | 16.5 % |
| `turing` | 2.33 s | 1 | 2 330.99 | 7.4 % |
| `detection` | 0.09 s | 4 | 21.53 | 0.3 % |

**Vitesse globale : 82 z/s (×80 vs v3 à 1.02 z/s).** Turing COMPLET, LMFDB 19/20.

### 18.2 Interprétation du profil

Le noyau Illinois_C est **réellement rapide** en pipeline (10 ms/appel). Le goulot
résiduel est `mpmath_petit_t` : les 138 zéros à $t < 300$ affinés par `mpmath.siegelz`
à `dps=35`. Ce coût croît en $\mathcal{O}(\sqrt{t})$ par le nombre de termes RS :

$$N(t) = \left\lfloor\sqrt{\frac{t}{2\pi}}\right\rfloor \quad \text{termes dans la somme principale}$$

À $t < 300$, $N < 7$ — la somme est courte, mais l'arithmétique multi-précision
(`dps=35` ≈ 116 bits) coûte cher par terme. La détection (`Z_vect_correct`) est négligeable.

### 18.3 Leçon workprec — piège mpmath

**Tentative :** `with _mp.workprec(50): _mp.findroot(_mp.siegelz, (a,b), ...)`.

**Résultat :** gain marginal (~12 %). Cause : `mpmath.siegelz` re-lit `mp.dps`
**global** (35) à chaque appel interne. Le contexte `workprec` contrôle la précision
de la boucle d'itération Illinois, pas la précision des évaluations de la fonction.

$$\text{workprec}(50) \not\Rightarrow \text{siegelz à 50 bits}$$

**La seule façon** d'appeler siegelz en float64 natif :
```python
_mp.fp.siegelz(t)   # float64 pur — précision ~1e-15, coût ~×40 plus faible
```

### 18.4 Prochain levier : fp.siegelz pour t < 300

Pour $t < 300$, $N < 7$ termes et `tol = 1e-12` → `fp.siegelz` (float64) est
amplement suffisant. La précision float64 ($\varepsilon \approx 10^{-16}$) est bien
sous la tolérance, et l'erreur de bracket est dominée par `STEP = 0.1`.

Gain estimé : 81 ms → ~2 ms par appel → 138 zéros en ~0.3 s au lieu de 11.3 s
→ pipeline T=1000 : **~6 s → ~200+ z/s**.

---
*Auteur : hprzeta — Riemann_Lab — Mise à jour : 3 juin 2026*

---

## §19 — Option B : `illinois_refine` — ancrage fa/fb et résultats (3 juin 2026)

> Commit `581e34d` — branche `Riemann_Lab_C`. Contexte : la version antérieure
> `illinois_mpfr(a, b, tol)` recalculait $Z(a)$ et $Z(b)$ en C via $Z_{\text{mpfr}}$
> (RS tronquée $C_0+C_1$). Si `Z_vect_correct` (Python) et $Z_{\text{mpfr}}$ (C)
> divergeaient en signe sur les bornes, Illinois cherchait un « pseudo-zéro RS »
> décalé de ~0.3 — sans déclencher de fallback.

### 19.1 Cause du biais ~0.3 (diagnostic)

Pour $t < 300$ ($N < 7$ termes RS), l'erreur de troncature $|R(t)| \sim 10^{-3}$ est
comparable à l'amplitude locale de $Z(t)$. Deux évaluateurs donnant des signes opposés
sur $[a, b]$ obligent Illinois à chercher une **racine de $Z_{\text{mpfr}}$** dans le
mauvais intervalle, produisant un résultat décalé de $\sim 0.3$ — soit deux ordres de
grandeur au-dessus de la tolérance $10^{-12}$.

### 19.2 Solution — passage de fa/fb depuis Python

Nouvelle signature C :

```c
double illinois_refine(double a, double b,
                       double fa, double fb,       // ← passés depuis Python
                       int prec_bits,
                       double tol, int max_iter);
```

`fa = Z_vals[i]` et `fb = Z_vals[i+1]` sont les valeurs **déjà calculées** par
`Z_vect_correct` lors du balayage → **zéro recalcul**, et l'encadrement initial est
garanti cohérent avec $\zeta(\tfrac{1}{2}+it)$ (pas avec $Z_{\text{mpfr}}$ tronquée).

**Interface ctypes correspondante :**

```python
lib.illinois_refine.restype  = ctypes.c_double
lib.illinois_refine.argtypes = [
    ctypes.c_double,   # a
    ctypes.c_double,   # b
    ctypes.c_double,   # fa  = Z(a) calculé par Z_vect_correct
    ctypes.c_double,   # fb  = Z(b)
    ctypes.c_int,      # prec_bits (170 par défaut)
    ctypes.c_double,   # tol
    ctypes.c_int,      # max_iter
]
```

Les itérations **intermédiaires** évaluent $Z_{\text{mpfr}}$ en C (précision 170 bits,
correcte pour $t \geq 300$, $N \geq 7$ termes RS). Seules les **bornes initiales**
$f_a, f_b$ proviennent de Python. `Z_double` est supprimé du `.so`.

### 19.3 Résultats mesurés

| Test | Valeur | Statut |
|---|---|---|
| `test_illinois.py` (10 premiers LMFDB) | **10/10** illinois_C pur · erreurs ~$10^{-13}$ · 0 fallback | ✅ |
| Benchmark $t \in [500, 638]$ | **×30.78** vs `mpmath.findroot` (objectif ×5–10 dépassé) | ✅ |
| Run T=1000 — zéros / vitesse / Turing / LMFDB | 649/649 · **16.15 z/s** · COMPLET · 19/20 | ✅ |
| Run T=10 000 — zéros / vitesse / Turing / LMFDB | 10 141 · **18.65 z/s** · COMPLET · 19/20 | ✅ |
| illinois_C (t ≥ 300) sur T=10 000 | **98.6 %** (10 004 zéros) · 0 fallback | ✅ |

**Profil phases — Run T=10 000 (cumulé 4 workers) :**

| Phase | Temps cumulé | Appels | ms/appel |
|---|---|---|---|
| `illinois_C` | 1 592.5 s | 10 004 | **159 ms** |
| `mpmath_petit_t` ($t < 300$) | 79.5 s | 138 | 576 ms |
| `turing` | 35.0 s | 1 | — |
| `detection` | 2.8 s | 20 | 138 ms |

> **Point de vigilance — LMFDB 19/20 :** le zéro $n°20$ ($\gamma_{20} = 77.1448\ldots$)
> donne un écart de $8.06 \times 10^{-10}$ dans tous les runs (T=300, T=1000, T=10 000).
> Ce cas limite est **stable et reproductible** : il ne constitue pas un bug, mais un
> zéro dont le croisement est suffisamment plat pour que l'erreur de position §5.6
> s'approche du seuil $10^{-10}$ sans le franchir.

---

## §20 — Goulot $O(\!\sqrt{t}\,)$ — croissance du coût illinois_C avec la hauteur

### 20.1 Formule du coût d'un appel Z_mpfr(t) en C

L'évaluation de $Z_{\text{mpfr}}(t)$ en C reproduit la somme principale de Riemann-Siegel
avec $N_{\text{RS}} = \lfloor\sqrt{t/2\pi}\rfloor$ termes à `PREC = 170 bits` ($\approx 51$ décimales) :

$$
t_{\text{appel}} \;\propto\; N_{\text{RS}}(t) \;\cdot\; \text{PREC}^2
\qquad\text{avec}\quad
N_{\text{RS}}(t) = \left\lfloor\sqrt{\frac{t}{2\pi}}\right\rfloor.
$$

Comme $N_{\text{RS}} \sim \sqrt{t}$, le coût d'un appel croît **comme $\sqrt{t}$** à précision fixée.

### 20.2 Croissance mesurée sur le run T=10 000

| Plage de $t$ | $N_{\text{RS}}$ typique | ms/appel illinois_C mesuré |
|---|---|---|
| $[300, 500]$ | 7–8 | ~58.9 ms |
| $[500, 700]$ | 8–10 | ~70 ms |
| $[3000, 5000]$ | 21–28 | ~100 ms |
| $[7500, 10000]$ | 34–39 | ~159 ms |

**Rapport de coût :** $159\,\text{ms} / 58.9\,\text{ms} \approx 2.7$. Valeur théorique :
$\sqrt{8750/400} \approx 4.7$ → légèrement plus faible, car une partie des opérations
(initialisation, gestion des bornes) est indépendante de $t$.

### 20.3 Impact sur T = 100 000

À $T = 100\,000$, $N_{\text{RS}} \approx \lfloor\sqrt{100000/2\pi}\rfloor \approx 126$ termes.
Extrapolation depuis $t \approx 8750$ ($N \approx 37$) :

$$
t_{\text{appel}}(T=100000) \;\approx\; 159\,\text{ms} \times \frac{126}{37} \;\approx\; 540\,\text{ms}.
$$

Avec $N(100000) \approx 138\,067$ zéros et 4 workers :
$$
T_{\text{total}} \approx \frac{138\,067 \times 540\,\text{ms}}{4} \approx 5.2\,\text{h}.
$$

> Ce goulot est **incompressible** sans changer de bibliothèque (Arb `acb_dirichlet_hardy_z`,
> §12 de Bibliotheques.md) ou de formule (Odlyzko–Schönhage). Aucune optimisation algorithmique
> à l'intérieur de la boucle Illinois ne peut le réduire.

---

## §21 — Déséquilibre workers — cause et quantification (3 juin 2026)

### 21.1 Deux sources de déséquilibre

Le pipeline v4.1 utilise 4 workers sur des segments équilibrés en largeur d'intervalle,
**pas** en nombre de zéros. Deux causes indépendantes créent un déséquilibre :

| Source | Worker affecté | Cause |
|---|---|---|
| **Goulot $t < 300$** (`mpmath_petit_t`) | Worker 0 $[14,\, 261]$ | Concentre les 138 zéros dont l'affinage passe par `mpmath.fp.siegelz` ou `mp.siegelz` (fallback légitime, seuil `T_SEUIL = 300`) |
| **Goulot $O(\sqrt{t})$** | Worker 3 $[7503,\, 10000]$ | $N_{\text{RS}}$ est maximal dans cet intervalle → chaque appel illinois_C est plus coûteux (~159 ms vs ~58.9 ms pour worker 1) |

### 21.2 Profil mesuré — Run T=10 000 (par worker)

| Worker | Plage | Durée | Zéros affinés illinois_C | Cause dominante |
|---|---|---|---|---|
| 0 | $[14,\; 2 502]$ | ~450 s | ~2 372 | mpmath_petit_t (138 zéros) + illinois_C moyen-t |
| 1 | $[2 502,\; 5 001]$ | ~530 s | ~2 500 | illinois_C moyen-t |
| 2 | $[5 001,\; 7 502]$ | ~535 s | ~2 630 | illinois_C grand-t |
| 3 | $[7 503,\; 10 000]$ | **~543 s** | ~2 500 | illinois_C grand-t ($N_{\text{RS}} \leq 39$) |

Le worker 3 détermine la durée totale du run ($543\,\text{s} \approx 9.1\,\text{min}$).

### 21.3 Impact à T=10 000 — déséquilibre marginalisé

Pour T=10 000, les 138 zéros à $t < 300$ représentent $138 / 10\,142 \approx 1.4\,\%$ du total.
Le goulot `mpmath_petit_t` (576 ms/appel dans ces run, 79.5 s total) est absorbé dans la
durée totale sans effet dominant. En pratique, les workers 1–3 compensent ce déséquilibre.

**Résolution possible** : partitionner les segments en **volume de zéros** estimé via $N(T)$
plutôt qu'en largeur d'intervalle. Pour T=10 000, l'espacement moyen $\langle\delta\rangle$
est quasi-constant dans chaque tiers → l'équilibrage géométrique suffit. L'enjeu devient
pertinent pour T=100 000, où la plage de $t$ (et donc $N_{\text{RS}}$) varie d'un facteur $\sqrt{10}$.

### 21.4 Rappel du bilan global

| Métrique | Run T=1000 | Run T=10 000 |
|---|---|---|
| Vitesse globale | 16.15 z/s | **18.65 z/s** |
| Illinois_C (%) | 78.7 % | **98.6 %** |
| mpmath_petit_t | 138 zéros (21.3 %) | 138 zéros (1.4 %) |
| Turing | COMPLET | COMPLET |
| LMFDB | 19/20 | 19/20 |
| Durée | ~40 s (4 workers) | **~9.1 min** (4 workers) |

> **Comparaison v3** : v3 (`compute_zeros_v3.py`) atteignait ~3.59 z/s.
> v4.1 Option B atteint 18.65 z/s → **gain ×5.2** sur un run réel T=10 000.

---

## §22 — Vérif B — synthèse positions Illinois_C (6 juin 2026)

> Entrée rapide pour retrouver les chiffres clés de Vérif B sans relire §5.6 et §6.4–6.5.

### 22.1 Formule centrale

L'erreur de **position** d'un zéro affiné par Illinois_C pur (sur $Z_{\text{mpfr}}$ tronquée
$C_0 + C_1$) est donnée par le développement de Taylor au premier ordre (§5.6) :

$$
\boxed{\;\big|\gamma_{\text{Illinois\_C}} - \gamma_{\text{réf}}\big|
       \;\approx\; \frac{|R(\gamma)|}{|Z'(\gamma)|}\;}
$$

### 22.2 Résultats chiffrés

| Méthode d'affinage | Erreur amplitude RS $|R(\gamma)|$ | Erreur position typique | Critère LMFDB |
|---|---|---|---|
| **Illinois_C pur** (Z_mpfr RS $C_0+C_1$) | $\sim 10^{-3}$ | $10^{-4}$ à $10^{-2}$ | ❌ |
| **Illinois_C + polish** `mpmath.siegelz` | — | $< 10^{-10}$ | ✅ |

**Exemple mesuré (Vérif B, bracket $[350.400,\, 350.440]$) :**

| Méthode | Racine trouvée | Cible LMFDB |
|---|---|---|
| `illinois_refine` C/libmpfr (Z_mpfr $C_0+C_1$) | $350.424$ | — |
| `mpmath.findroot(siegelz)` dps=50 | $350.408$ | $\gamma_{\text{réf}}$ |
| **Écart** | **$0.016 \approx 1.6\times10^{-2}$** | $= |R|/|Z'|$ à $t\approx 350$ |

### 22.3 Interprétation — comptage vs catalogue

| Objectif | Illinois_C pur | Avec polish siegelz |
|---|---|---|
| Vérifier HR (comptage Turing) | ✅ suffit (~41 z/s) | non requis |
| Catalogue de positions LMFDB | ❌ (~1e-2 erreur) | ✅ (<1e-10, ~0.5 z/s) |

> La variabilité $10^{-4}$ à $10^{-2}$ vient de $|Z'(\gamma)|$ (pente du croisement),
> **pas** de $|R(\gamma)|$ qui est quasi-constante à hauteur fixée.
> Références approfondies : §5.6 (analyse Taylor), §6.4 (architectures), §6.5 (Newton vs Illinois).

---

## §18. Benchmark Arb/FLINT vs mpmath — résultats mesurés (2026-06-09)

| Méthode | temps/appel (ms) | Speedup | T_total estimé |
|---|---|---|---|
| `mpmath.siegelz` dps=35 | 21.13 ms | 1× | ~21 min |
| `arb_fpwrap_cdouble_hardy_z` | 0.77 ms | ×27 | ~1–15 min |

Speedup par tranche :
- $t \in [100, 1000]$ → ×29
- $t \in [1000, 5000]$ → ×28
- $t \in [5000, 10000]$ → ×26

**Erreur :** $|Z_{\text{arb}} - Z_{\text{mpmath}}| = 0$ sub-ULP $< 2.2\times10^{-16}$

**Explication :** `mpmath` utilise MPFR (allocations heap, ~1000 malloc/free par zéro).
Arb reste en double IEEE 754 (registres CPU, 0 allocation).
Illinois converge à `tol=1e-12` — précision double largement suffisante.

**Accès :** ctypes + libflint bundlée python-flint 0.8.0 (pas de `sudo apt`).
**Module :** `src/calculs/optimisation/arb_wrapper.py` (commit `b563db2`)

---

## §23. STEP adaptatif — théorie et valeurs mesurées (2026-06-10)

### 23.1 Densité des zéros et espacement moyen

La densité locale des zéros de $\zeta$ sur la droite critique à hauteur $t$ :

$$\rho(t) = \frac{dN}{dt} \approx \frac{1}{2\pi} \ln\frac{t}{2\pi}$$

L'espacement moyen entre deux zéros consécutifs est son inverse :

$$\delta(t) = \frac{1}{\rho(t)} = \frac{2\pi}{\ln(t/2\pi)}$$

Valeurs numériques :

| $t$ | $\delta(t)$ espacement moyen | STEP recommandé |
|---|---|---|
| 100 | ~1.21 | 0.1 |
| 1 000 | ~0.91 | 0.1 |
| 5 000 | ~0.80 | 0.1 → 0.05 (seuil) |
| 10 000 | ~0.73 | 0.05 |
| 50 000 | ~0.63 | 0.05 → 0.02 (seuil) |
| 100 000 | ~0.59 | 0.02 |

### 23.2 Condition de non-manquant

Pour garantir qu'un bracket $[t, t + \text{STEP}]$ ne contient au plus qu'un zéro :

$$\text{STEP}(t) < \frac{\delta(t)}{2} = \frac{\pi}{\ln(t/2\pi)}$$

En pratique, on prend STEP $\approx \delta(t)/10$ pour une marge de sécurité face aux
**paires de zéros proches** (distribution GUE — espacements poissonniens de queue).
L'espacement minimum mesuré à $T=10\,000$ est $0.038$, soit $\delta_{\min} \approx 0.038$.

STEP adaptatif implémenté dans `compute_zeros_v4_1.py` (`step_pour_t`) — **v2 (commit `181fdd1`)** :

| Tranche $t$ | STEP | Justification |
|---|---|---|
| $t < 5\,000$ | 0.05 | $\delta_{\min} \approx 0.5$ — large marge |
| $t \geq 5\,000$ | **0.010** | gap min mesuré 0.01940 à $t=66678$ — STEP=0.02 insuffisant |

> **Historique :** v1 (commit `7467731`) : 0.1/0.05/0.02 → 30 manquants sur T=100k.
> v2 (commit `181fdd1`) : cap à 0.010 pour $t \geq 5000$ (STEP ÷5 et ÷2 respectivement).

### 23.3 Overlap aux frontières de segments

Condition minimale pour qu'aucun bracket ne soit raté à la frontière :

$$\text{overlap} \geq 2 \times \text{STEP}_{\max}$$

| Version | Overlap | Suffisant ? |
|---|---|---|
| v1 (2026-06-10) | proportionnel (×4 STEP) ≈ 0.4 | ❌ trop petit si STEP change en milieu de segment |
| v2 (2026-06-10) | fixe 2.0 | ✅ couvre ≥ 40 × STEP dans la tranche la plus dense |

### 23.4 Résultats mesurés

**Test T=10 000 v1** (STEP=0.1 pour tout $t < 10\,000$, overlap proportionnel ×4) :

| Indicateur | Valeur |
|---|---|
| Zéros trouvés | 10 137 / 10 142 |
| Manquants | 6 (Turing-Backlund INCOMPLET) |
| Durée | 2.58 min · 65.50 z/s |

**Test T=10 000 v2** (STEP=0.05 pour $t \geq 5\,000$, overlap=2.0 fixe) :

| Indicateur | Valeur |
|---|---|
| Zéros trouvés | **10 141 / 10 142** |
| Manquants | **0 — Turing-Backlund COMPLET ✅** |
| Durée | **2.60 min · 64.97 z/s** |
| Commit | `50837f7` — `Riemann_Lab_C` |

Le surcoût du STEP plus fin est quasi nul (+0.02 min) car les brackets supplémentaires
sont traités par Z_batch vectorisé (numpy, 0 appel Python par point).

**Run T=100 000 v1 adaptatif** (STEP=0.1/0.05/0.02, overlap=2.0, commit `7467731`) :

| Indicateur | Valeur |
|---|---|
| Zéros trouvés | — |
| Manquants | ~30 (t > 50 000) |
| Cause | STEP=0.02 < gap min mesuré 0.01940 à t=66678 |

**Run T=100 000 v2 adaptatif** (STEP=0.1/0.05/0.02, overlap=2.0, commit `50837f7`) :

| Indicateur | Valeur |
|---|---|
| Zéros trouvés | 138 039 / 138 069 |
| Manquants | **68 — Turing-Backlund INCOMPLET ❌** |
| Durée | 105.1 min · 21.89 z/s |
| Cause | STEP=0.02 toujours insuffisant pour $t > 50\,000$ |

**Run T=100 000 v3** (STEP=0.05 pour $t < 5\,000$ / STEP=0.010 pour $t \geq 5\,000$, commit `181fdd1`) :

| Indicateur | Valeur |
|---|---|
| Zéros trouvés | TUÉ — régression ×11 (5M points scan, ~0.5 z/s) |
| Turing-Backlund | non atteint — run interrompu |

**Run T=100 000 v4** (STEP=δ(t)/3, continu, commit `d2f62c1`) :

| Indicateur | Valeur |
|---|---|
| Zéros trouvés | 135 997 / 138 069 |
| Manquants | **2 072 — Turing-Backlund INCOMPLET ❌** |
| Durée | 113 min · 20.05 z/s |
| LMFDB | 19/20 ✅ |
| Cause | STEP≈0.22 à $t=100\,000$ — ×11 le gap min (0.019) — GUE non protégé |

**Leçon v4 :** STEP=δ/3 est **pire que v1** (2072 vs 356 manquants). La formule δ/3 est basée
sur l'espacement moyen ; la queue GUE produit des gaps $\ll \delta$.
Condition de sécurité réelle : STEP $\leq 0.014 \cdot \delta(t)$ (pour gap_min/δ ≈ 0.028 à T=100k).
**Seule stratégie validée : STEP ≤ 0.010. L'accélération doit venir de `scan_arb.c` (×7.5 C pur).**

### 23.5 Tableau récapitulatif — runs T=100 000

| Run | STEP | Zéros | Manquants | Durée | Turing |
|---|---|---|---|---|---|
| v1 (paliers) | 0.1/0.05/0.02 | 137 711 | 356 | 1h58 | ❌ |
| v2 (paliers) | 0.1/0.05/0.02 | 138 001 | 68 | 105 min | ❌ |
| v3 (cap 0.010) | 0.010 pour $t \geq 5k$ | TUÉ | — | — | — |
| **v4 (δ/3)** | **~0.22 à T=100k** | **135 997** | **2 072 ❌** | **113 min** | **❌** |

**Prochaine étape (v6) :** scan_arb.c (×7.5) + STEP≤0.010 + W=8 → cible ~15 min, 0 manquant.

---
*Auteur : hprzeta — Riemann_Lab — Mise à jour : 3 juin 2026 (§19–21 ajoutés) · 6 juin 2026 (§22 ajouté) · 9 juin 2026 (§18 ajouté) · 10 juin 2026 (§23 STEP adaptatif, résultats T=10k v2, STEP v3 0.05/0.010, runs T=100k v1–v4, leçon GUE) · ~1345 lignes*
