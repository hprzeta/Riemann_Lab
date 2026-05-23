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
    plt.show()
```

---

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
