---
name: riemann-lab
description: |
  Assistant spécialisé pour le projet GitHub `Riemann_Lab` de hprzeta — recherche et vulgarisation autour de la fonction zêta de Riemann et de l'hypothèse de Riemann.

  Utiliser ce skill dès que l'utilisateur travaille sur :
  - Du contenu mathématique en **français** sur ζ(s), θ(t), Z(t), la fonction Xi, les zéros non-triviaux, l'HdR
  - Du LaTeX/KaTeX destiné au **GitHub Wiki** ou à la page HTML `index.html` du projet
  - Du **code Python** pour calculer, visualiser ou explorer ζ(s) numériquement
  - Des **commits Git**, des messages de branches, ou du contenu pour la branche `Riemann_Lab_IA`
  - Toute tâche liée aux fichiers du dépôt `Riemann_Lab` (docs/, wiki, index.html)

  Déclencher aussi pour : rédaction de cours, formatage Markdown GFM, corrections KaTeX, animations HTML/JS, intégration iframe dans le wiki.
---

# Riemann Lab Skill

Assistant expert pour le projet **Riemann_Lab** — une initiative pédagogique et de recherche
sur la fonction zêta de Riemann (ζ) et l'hypothèse de Riemann (HdR), développée en français.

---

## 1. Contexte du projet

| Élément | Valeur |
|---|---|
| Dépôt GitHub | `hprzeta/Riemann_Lab` |
| Branche de développement | `Riemann_Lab_IA` |
| Branche de production | `main` |
| Branche de test | `Riemann_Lab_Test` |
| GitHub Pages | `/docs` sur `Riemann_Lab_IA` |
| Fichier principal | `docs/index.html` |
| Wiki | `Riemann_Lab.wiki.git` (dépôt séparé, branche `master`) |
| Langue | **Français** (tout contenu, commentaires, commits) |

---

## 2. Règles KaTeX — CRITIQUES

Le projet utilise **KaTeX** (pas MathJax). Certaines commandes LaTeX standard sont bloquées.

### ❌ Commandes interdites
```
\operatorname{Re}   →  utiliser \text{Re}
\operatorname{Im}   →  utiliser \text{Im}
\operatorname{...}  →  toujours remplacer par \text{...}
\bigl\{  \bigr\}    →  utiliser \left\{  \right\}
\bigl(  \bigr)      →  utiliser \left(  \right)
T_{10%}             →  utiliser T_{10\%}  (% = commentaire KaTeX !)
\left\{             →  seul sans \right\} → erreur (souvent causé par % commentaire)
```

### 🔒 Règles d'échappement systématiques (audit 05/07/2026)
- Underscore brut dans `\text{...}` → toujours `\_` (ex: `\text{gap\_moyen}`)
- `%` brut en mode math, y compris dans les indices (ex: `T_{10%}`) → toujours `\%`
- Accolades d'ensemble littérales (notation `{...}`) → toujours `\{ ... \}`
  (ne pas confondre avec les accolades d'arguments de commande `\frac{}{}`, `\text{}`,
  `\sqrt{}`, les exposants/indices `^{}` `_{}`, ou l'idiome virgule française `{,}` —
  ceux-là restent des accolades non échappées, ce sont des arguments LaTeX légitimes)

### ⚠️ Pièges spécifiques GitHub KaTeX (découverts en production)

**Piège 1 — Le `%` est un commentaire dans KaTeX**
```
❌  $T \in \{T_{10%}, T_{25%}\}$     % → coupe la formule ici !
✅  $T \in \{T_{10\%}, T_{25\%}\}$   % \% = symbole pourcentage
```
Symptôme : erreur `Missing or unrecognized delimiter for \left` alors que
`\left` semble correct → chercher un `%` non échappé sur la même ligne.

**Piège 2 — `\bigl` / `\bigr` non reconnus**
```
❌  \bigl\{  \bigr\}
✅  \left\{  \right\}   ← toujours utiliser \left / \right
```

**Piège 3 — `\left\{` sans `\right\}` sur la même ligne**
GitHub KaTeX exige que `\left` et `\right` soient **sur la même ligne** en mode
inline `$...$`. Si la formule s'étend sur plusieurs lignes, passer en mode display `$$...$$`.

### ✅ Commandes validées
```latex
\text{Re}(s)        % partie réelle
\text{Im}(s)        % partie imaginaire
\zeta(s)            % fonction zêta
\Gamma(s)           % fonction Gamma
\theta(t)           % fonction thêta de Riemann-Siegel
Z(t)                % fonction Z de Hardy
\Xi(s)              % fonction Xi de Riemann
\pi(x)              % comptage des nombres premiers
\rho                % zéro non-trivial
\sigma + it         % écriture standard de s
```

### Délimiteurs selon le contexte

| Contexte | Délimiteur inline | Délimiteur display |
|---|---|---|
| `index.html` (auto-render) | `$...$` | `$$...$$` |
| GitHub Wiki | `$...$` | `$$...$$` |
| GitHub Wiki (alternative) | `` `$...$` `` en code | — |

---

## 3. Formatage GitHub Wiki (GFM)

### Structure type d'une page wiki
```markdown
# Titre de la page

## Introduction
Texte en français...

## Formule principale

$$
\zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s}, \quad \text{Re}(s) > 1
$$

## Interprétation
...

## Voir aussi
- [[Lien vers autre page wiki]]
- [[🔬 Interprétation des résultats]]
```

### Conventions wiki
- Noms de pages avec emojis : `🔬-Nom-de-la-page.md`
- Liens internes : `[[Nom de la page]]`
- Pas de `\operatorname` (bloqué par le moteur KaTeX de GitHub)
- Images : hébergées sur la branche `Riemann_Lab_IA`, lien absolu vers `raw.githubusercontent.com`

---

## 4. Formatage HTML (index.html)

Le fichier `docs/index.html` utilise KaTeX avec l'extension **auto-render** et les délimiteurs `$...$`.

### Bannière défilante
La bannière a son propre système de rendu KaTeX — ne pas mélanger avec l'auto-render global.

```html
<!-- Rendu KaTeX manuel pour la bannière -->
katex.render(expression, element, { throwOnError: false });
```

### Formules dans le corps de page
Écrire directement `$...$` ou `$$...$$` dans le HTML — l'auto-render s'en charge.

```html
<p>La fonction zêta est définie par $\zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s}$</p>
```

---

## 5. Code Python — conventions

### État du projet (8 août 2026)

| Version | Méthode affinage | T=100k | Turing | Commit |
|---|---|---|---|---|
| v12 | illinois_refine_arb (Arb, tol=1e-9) | 8.8 min | ✅ COMPLET | `f0e8430` |
| v13 | illinois_refine_arb (Arb, tol=1e-12) | 8.50 min | ✅ COMPLET | `77efd10` |
| v14 | v13 + cache log_n/isqrt_n | 7.7 min (×1.10) | ✅ COMPLET | `d4b3611` |
| v15 | v14 + Phase 2 adaptative SEUIL=20k | 4.4 min (×1.93) | ✅ COMPLET | `adf5d2a` |
| **v16** ⭐ | v15 + Z_arb précision fixe (acb_dirichlet_hardy_z, 64 bits) | **1.6 min (×2.75)** | ✅ COMPLET | `00abe5c` |

**Condition Objectif 2 atteinte le 04/07/2026, améliorée le 08/08/2026 : T=100k = 1.6 min < 5 min ✅**

**v16 — commit `00abe5c` (2026-08-08) :**
- `arb_fpwrap_cdouble_hardy_z(flags=0)` escalade en interne 64→8192 bits visant ~1e-16
  (confirmé depuis le code source FLINT 3.3.1) — surdimensionné vs tol=1e-12 (~40 bits)
- Remplacé par `acb_dirichlet_hardy_z` à précision FIXE 64 bits (un seul calcul)
- Nécessite `c_modules/flint-headers-3.3.1/` (headers vendorisés en source, `apt
  libflint-dev`=3.0.1 incompatible ABI `dirichlet_group_t`/`dirichlet_char_t`)
- Validé run réel T=10000 (prototype isolé, ×1.98) puis T=100000 (intégré, ×2.75)
  avant adoption — Turing COMPLET + LMFDB 20/20 aux deux échelles
- Piste MPFR pur testée et écartée : 11.88× plus lent ET ~4 ordres moins précis

**v14 — commit `d4b3611` (2026-07-04) :**
- Cache statique `log_n_cache[2101]` + `isqrt_n_cache[2101]` dans `illinois_arb.c` et `scan_arb.c`
- 33 KB total — tient en L2 cache — initialisation unique post-fork par worker
- Couvre T≲27M (N_MAX_CACHE=2100 termes RS)
- Gain ×1.10 (évite `log()` + `sqrt()` ≈ 100 cycles/terme → lecture L2 ≈ 4 cycles)

**v15 — commit `adf5d2a` (2026-07-04) :**
- `#define SEUIL_1NEWTON 20000.0` dans `illinois_arb.c` Phase 2
- Biais Z_rs ≈ 0.305·t^{-5/4} → erreur 1 Newton ≈ biais² ≈ 4e-13 < tol pour t≥20k
- 87% des zéros T=100k ont t≥20k → économie 1 appel Z_arb (≈1.8 ms) par zéro
- LMFDB 20/20 validé (vs 14/20 avec 1 Newton fixe pour t<200)

**Leçon T_SEUIL :** scan_arb (Z_double, N_RS termes) a des brackets décalés si N_RS=2 (t<57).
illinois_refine_arb reçoit des signes fa/fb faux → convergence décalée (jusqu'à 3e-9).
Fix : garder arb_hardy_z+mpmath pour t < T_SEUIL (pas de re-éval fa/fb après coup — piège).

**Piège 1 Newton fixe :** réduire à 1 Newton pour TOUT t → erreur ~1.75e-6 à t≈65 (LMFDB 14/20).
Cause : biais_RS(65) ≈ 5e-3 → 1 Newton depuis 5e-3 → erreur ≈ 1.75e-6 >> tol=1e-12.
Solution : `int n_newton = (t < SEUIL_1NEWTON) ? 2 : 1;`

**Leçon STEP GUE :** STEP = δ(t)/3 insuffisant — gap min GUE ≈ 0.019 à t=66 678,
soit 0.028·δ. Formule safe : **STEP ≤ 0.010** (fixe). L'accélération vient de `scan_arb.c`.

### STEP adaptatif — formule (et sa limite)

```python
# STEP safe pour 0 manquant (validé T=10k) :
STEP = min(0.05, 0.010)  # 0.05 pour t<5k, 0.010 pour t≥5k

# STEP δ/3 (commit d2f62c1) — INSUFFISANT pour T=100k :
# STEP = max(0.05, min(0.5, 2*pi / (3*log(t/(2*pi)))))
# → 0.22 à T=100k → 2072 manquants ❌
```

### Bibliothèques privilégiées
```python
import numpy as np
import matplotlib.pyplot as plt
from mpmath import mp, zeta, siegeltheta, siegelz, zetazero
```

### Précision numérique
```python
mp.dps = 50  # 50 décimales pour les calculs de haute précision
```

### Fonctions clés disponibles via mpmath
| Fonction math | Code Python |
|---|---|
| ζ(s) | `zeta(s)` |
| θ(t) | `siegeltheta(t)` |
| Z(t) | `siegelz(t)` |
| ρ_n (n-ième zéro) | `zetazero(n)` |

### Style de code
- Commentaires en **français**
- Noms de variables mathématiquement significatifs (`sigma`, `t`, `s = sigma + 1j*t`)
- Toujours vérifier la convergence / zone critique séparément

### Exemple de structure standard
```python
import numpy as np
import matplotlib.pyplot as plt
from mpmath import mp, zeta, siegelz, siegeltheta

mp.dps = 30  # précision

def calculer_zeros(n_max: int) -> list:
    """Calcule les n_max premiers zéros non-triviaux de ζ sur la droite critique."""
    from mpmath import zetazero
    return [zetazero(n) for n in range(1, n_max + 1)]

def tracer_Z(t_min: float, t_max: float, points: int = 1000):
    """Trace la fonction Z(t) de Hardy sur [t_min, t_max]."""
    t_vals = np.linspace(t_min, t_max, points)
    Z_vals = [float(siegelz(t)) for t in t_vals]
    
    plt.figure(figsize=(12, 4))
    plt.plot(t_vals, Z_vals, 'b-', linewidth=0.8)
    plt.axhline(0, color='r', linewidth=0.5)
    plt.xlabel('$t$')
    plt.ylabel('$Z(t)$')
    plt.title('Fonction $Z(t)$ de Hardy-Littlewood')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('Z_function.png', dpi=150)
    plt.close()  # ⚠️ jamais plt.show() en production (bloquant → fige le run)
```

---

### Runs longs non surveillés — vérification alimentation obligatoire (2026-08-05)

**PC1 (`zeta-lab`) est un portable.** Avant tout lancement d'un run long
(`zeta-distribute`, `zeta_run.sh`) destiné à tourner sans surveillance :

```bash
upower -i $(upower -e | grep -i AC)   # doit afficher : online: yes
```

**Pourquoi c'est nécessaire :** `nohup`/`setsid` protègent un process d'une fermeture
de session ou d'une déconnexion SSH, **pas** d'un vrai `poweroff`/reboot machine. Un run
T=5M lancé le 02/08/2026 a tourné sur batterie (débranché, non détecté) et a été tué par
3 redémarrages non planifiés en moins de 24h : `CriticalPowerAction=HybridSleep` (UPower)
à batterie critique n'a pas pu reprendre proprement (`resume=` non câblé côté kernel
malgré une swapfile disponible) et a dégénéré en extinction sauvage. Correctif appliqué :
`CriticalPowerAction=PowerOff` dans `/etc/UPower/UPower.conf` (arrêt propre et
prévisible en dernier recours). Détail complet → `JOURNAL.md` wiki, entrée 04/08/2026 ;
`Guide-Linux-Commandes.md` §19.

PC2/PC3/PC4 sont alimentés en continu (pas de batterie) — cette vérification ne les
concerne pas.

## 6. Commits Git — Conventional Commits

Toujours en **anglais** (convention), mais les messages de corps peuvent être en français.

```
feat(wiki): add page on Riemann-Siegel theta function
fix(katex): replace \operatorname with \text in wiki pages
docs(index): update KaTeX auto-render configuration
style(html): fix scrolling banner rendering
chore(git): update .gitignore for Python cache files
```

### Branches
```bash
git checkout Riemann_Lab_IA   # développement courant
git checkout Riemann_Lab_Test # tests avant merge
git checkout main             # production
```

---

## 7. Références mathématiques rapides

### Fonction zêta — définitions clés

**Série de Dirichlet** (Re(s) > 1) :
$$\zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s}$$

**Produit eulérien** :
$$\zeta(s) = \prod_{p \text{ premier}} \frac{1}{1 - p^{-s}}$$

**Équation fonctionnelle** :
$$\xi(s) = \xi(1-s), \quad \xi(s) = \frac{1}{2}s(s-1)\pi^{-s/2}\Gamma\!\left(\tfrac{s}{2}\right)\zeta(s)$$

**Factorisation sur la droite critique** :
$$\zeta\!\left(\tfrac{1}{2}+it\right) = e^{-i\theta(t)} Z(t)$$

**Hypothèse de Riemann** : tous les zéros non-triviaux vérifient $\text{Re}(\rho) = \frac{1}{2}$.

---

## 8. Références détaillées

Pour des sujets plus approfondis, consulter :
- `references/katex-cheatsheet.md` — liste complète des commandes KaTeX validées
- `references/python-zeta.md` — recettes Python pour calculs avancés
- `references/wiki-templates.md` — gabarits de pages wiki

---

## 9. Comportement attendu

- Toujours répondre en **français**
- Toujours vérifier que le LaTeX est **compatible KaTeX** avant de le proposer
- Pour le wiki GitHub, toujours utiliser `\text{}` et non `\operatorname{}`
- Pour le HTML, préférer les délimiteurs `$...$` / `$$...$$`
- Pour Python, utiliser **mpmath** pour la précision numérique, NumPy/Matplotlib pour la visualisation
- Signaler explicitement si une formule risque de ne pas s'afficher sur GitHub

---
*Skill du projet Riemann_Lab · Auteur : hprzeta · Mise à jour : 1ᵉʳ juin 2026 · 10 juin 2026 (état v4, leçon STEP GUE, plan v6) · **4 juillet 2026 (v14/v15, Obj2 ✅, piège 1-Newton)** · **5 août 2026 (vérification alimentation obligatoire avant run long PC1)** · **8 août 2026 (v16 — Z_arb précision fixe, Obj2 amélioré à 1.6 min)***
