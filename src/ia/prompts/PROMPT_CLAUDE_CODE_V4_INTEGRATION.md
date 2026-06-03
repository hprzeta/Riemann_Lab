# PROMPT CLAUDE CODE — compute_zeros_v4_1.py
# Intégration détection batch v3 + Illinois C v4
# Date    : 24 mai 2026
# Usage   : coller dans Claude Code depuis ~/projet_zeta/
#           source zeta_env/bin/activate && git checkout Riemann_Lab_C

---

## 🎯 Objectif

Créer `compute_zeros_v4_1.py` qui combine :
- **Détection**  → `Z_batch()` de `riemann_siegel_batch.py` (NumPy/CuPy, ×50 vs mpmath)
- **Affinage**   → `illinois_mpfr.so` C/libmpfr (×39 vs mpmath) pour t ≥ 300
- **Fallback**   → `mpmath.findroot` pour t < 300 uniquement (légitime — N < 7 termes)
- **Parallèle**  → 4 workers `parallel_scanner.py` (comme v3)
- **Validation** → Turing-Backlund (comme v3)

Résultat attendu : **~15–20 z/s** (vs 1.0 z/s en v4, vs 3.59 z/s en v3)

---

## 📐 COMPRENDRE LE PROBLÈME — lire avant de coder

### Il y a deux opérations totalement différentes

```
ÉTAPE 1 — DÉTECTION              ÉTAPE 2 — AFFINAGE
"Il y a un zéro entre            "Où est-il exactement ?"
 t=14.05 et t=14.10"             → 14.134725141734693...
```

Elles utilisent toutes les deux Z(t), mais PAS de la même façon.

### Étape 1 — Détection : on veut juste le SIGNE de Z(t)

On balaye par pas de 0.05. On cherche quand Z change de signe :

```
t=14.00  Z=+2.4  (positif)
t=14.05  Z=+1.1  (positif)
t=14.10  Z=-0.3  ← changement de signe → zéro entre 14.05 et 14.10
```

Pour ça, une approximation grossière suffit.
Z_batch() est correct même à t=14, même avec N=1 terme.
→ Z_batch() est la bonne fonction pour la détection, toujours.

### Étape 2 — Affinage : on veut 12 DÉCIMALES EXACTES

Illinois C calcule Z(t) en interne via sa propre formule RS (Z_mpfr dans le .so).
Le nombre de termes dans la somme RS dépend de t :

    N = floor(sqrt(t / 2π))

    t =    14  → N =  1 terme   → Z_mpfr interne imprécis (~0.01 d'erreur)
    t =   100  → N =  3 termes  → Z_mpfr interne approximatif
    t =   300  → N =  6 termes  → Z_mpfr interne à la limite
    t =  1000  → N = 12 termes  → Z_mpfr interne correct
    t = 10000  → N = 39 termes  → Z_mpfr interne très précis ✅

Avec N=1 terme à t=14, Illinois C converge vers un FAUX zéro.
→ Fallback mpmath nécessaire pour t < 300 (87 zéros sur 10 142, soit < 1%).

### La confusion fatale de v4

V4 a confondu ces deux colonnes :

```
                  Z_batch()          Z_mpfr INTERNE au .so
                  (détection)        (affinage Illinois C)
                  ────────────────   ─────────────────────
t =   14 (N=1)   ✅ correct          ❌ trop imprécis
t =  300 (N=6)   ✅ correct          ⚠️  limite
t = 1000 (N=12)  ✅ correct          ✅ correct
t = 10000(N=39)  ✅ correct          ✅ correct
```

Parce que Z_mpfr (affinage interne au .so) était imprécis pour petit t,
v4 a conclu que TOUTE formule RS était imprécise pour petit t.
Et a remplacé AUSSI la détection par mpmath.siegelz. C'était inutile.

### Ce que v4.1 doit faire — règle simple

```python
T_SEUIL_ILLINOIS_C = 300.0   # en dessous : N < 7 termes, Illinois C peu fiable

# Détection → Z_batch() PARTOUT, sans exception
# Affinage  → Illinois C si t >= 300, fallback mpmath si t < 300
```

Impact sur T=10 000 :
    t < 300  → ~87 zéros  → mpmath fallback (< 1% du temps total)
    t ≥ 300  → ~10 055 zéros → Illinois C ×39  (99% du temps total)

---

## 🚨 ERREURS EXACTES DE v4 — code ligne par ligne

### Erreur 1 — mpmath.siegelz pour la DÉTECTION (lignes 90, 158, 164, 247)

Ce que v4 a fait :
```python
# v4 ligne 90 — MAUVAIS
def trouver_intervalle_mpmath(t, b):
    return float(mpmath.siegelz(t)) * float(mpmath.siegelz(b)) < 0

# v4 ligne 158–164 — MAUVAIS (boucle principale)
with mpmath.workdps(dps_detect):
    za = float(mpmath.siegelz(t))   # appelé à CHAQUE pas du balayage

# v4 ligne 247 — MAUVAIS (même dans le graphique !)
Z_vals = [float(mpmath.siegelz(t)) for t in t_plot]  # 600 appels mpmath
```

Cause de l'erreur : confusion entre Z_mpfr interne .so (imprécis petit t)
et Z_batch numpy (précis partout). La détection n'a pas besoin de mpmath.siegelz.

Ce que v4.1 doit faire :
```python
# Détection — CORRECT
from riemann_siegel_batch import Z_batch
t_array = np.arange(t_debut, t_fin, step)
Z_vals  = Z_batch(t_array)                       # vectorisé, ×50 plus rapide
idx     = np.where(np.diff(np.sign(Z_vals)))[0]  # tous les changements de signe

# Visualisation — CORRECT
Z_vals = Z_batch(t_plot)   # pas mpmath.siegelz
```

Règle : mpmath.siegelz est interdit dans v4.1. Partout.

---

### Erreur 2 — Parallélisme abandonné (lignes 16, 474–477)

Ce que v4 a fait :
```python
# v4 docstring ligne 16
# v4  Exécution  : séquentiel (parallèle prévu v5)

# v4 ligne 474–477
zeros, stats = scanner_zeros(T_MIN, T_MAX, pas, TOL, barre=True, dps_detect=15)
```

Cause de l'erreur : croyance que ctypes + multiprocessing était incompatible.
C'est faux. parallel_scanner.py gère déjà ça depuis v3.
Il suffit de charger le .so APRÈS le fork(), à l'intérieur du worker.

Ce que v4.1 doit faire :
```python
# CORRECT
from parallel_scanner import calculer_zeros_parallele, dedupliquer
N_WORKERS   = multiprocessing.cpu_count()
zeros_bruts = calculer_zeros_parallele(T_MIN, T_MAX, STEP, N_WORKERS,
                                        affinage_fn=affiner_v4_1)
zeros       = dedupliquer(zeros_bruts)
```

Règle : scanner_zeros() séquentiel de v4 est interdit dans v4.1.

---

### Erreur 3 — Z_double du .so utilisé comme détection (lignes 65–76, 106)

Ce que v4 a fait :
```python
# v4 lignes 65–66 — Z_double exposé depuis le .so
lib.Z_double.restype  = ctypes.c_double
lib.Z_double.argtypes = [ctypes.c_double]

# v4 ligne 106 — Z_double comme pré-check
if _LIB is not None and Z_double(a) * Z_double(b) < 0:
    gamma_c = illinois_c(a, b, tol)
```

Cause de l'erreur : tentative d'utiliser Z_double scalaire du .so pour la
détection, puis confusion quand Z_double (imprécis à petit t) ne coïncidait
pas avec mpmath.siegelz → fallback déclenché inutilement à grand t aussi.

Ce que v4.1 doit faire :
```python
# CORRECT : illinois_mpfr uniquement depuis le .so
lib.illinois_mpfr.restype  = ctypes.c_double
lib.illinois_mpfr.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]
# Z_double du .so n'est PAS chargé ni utilisé
```

Règle : seul illinois_mpfr() est appelé depuis le .so. Pas Z_double.

---

### Erreur 4 — Fallback mpmath trop large (lignes 109–117)

Ce que v4 a fait :
```python
# v4 lignes 109–117 — fallback déclenché sur TOUT le domaine
gamma_c = illinois_c(a, b, tol)
if abs(float(mpmath.siegelz(gamma_c))) < 1e-8:
    return gamma_c, "illinois_C"
# Résidu > 1e-8 → fallback, même à t=9000 !
gamma = float(mpmath.findroot(mpmath.siegelz, gamma_c))
return gamma, "illinois_C→mpmath"
```

Conséquence : logs affichent "methode=illinois_C-mpmath" même à grand t,
gain ×39 partiellement annulé sans raison mathématique.

Ce que v4.1 doit faire :
```python
# CORRECT : fallback limité à t < T_SEUIL_ILLINOIS_C = 300
T_SEUIL_ILLINOIS_C = 300.0

def affiner_v4_1(a: float, b: float, tol: float = 1e-12) -> tuple:
    """Affinage avec seuil mathématiquement justifié.
    
    t < 300 : N < 7 termes RS → Illinois C imprécis → mpmath (légitime)
    t ≥ 300 : N ≥ 7 termes RS → Illinois C fiable  → gain ×39
    """
    t_mid = (a + b) / 2.0

    if t_mid >= T_SEUIL_ILLINOIS_C:
        # Zone Illinois C — N suffisant pour la précision libmpfr
        try:
            zero = lib.illinois_mpfr(a, b, tol)
            if a - 1e-10 <= zero <= b + 1e-10:
                return zero, "illinois_C"
        except Exception:
            pass  # rare — Turing détectera

    # Fallback mpmath : t < 300 (légitime) ou échec Illinois C (rare)
    zero = float(mpmath.findroot(mpmath.siegelz, t_mid))
    methode = "mpmath_petit_t" if t_mid < T_SEUIL_ILLINOIS_C else "mpmath_fallback"
    return zero, methode
```

Logs attendus dans v4.1 :
```
illinois_C       : 10055 zéros  (99%)   ← gain ×39
mpmath_petit_t   :    87 zéros  (< 1%)  ← t < 300, légitime
mpmath_fallback  :     0 zéros  (0%)    ← ne doit presque jamais apparaître
illinois_C→mpmath:     0 zéros  (0%)    ← INTERDIT
```

---

### Erreur 5 — .so absent → dégradation silencieuse (lignes 59–61)

Ce que v4 a fait :
```python
# v4 lignes 59–61 — MAUVAIS : continue sans .so
if not _SO_PATH.exists():
    print("[AVERTISSEMENT] introuvable — affinage en mpmath seul.")
    return None   # continue en mode dégradé silencieux
```

Ce que v4.1 doit faire :
```python
# CORRECT : arrêt immédiat
if not SO_PATH.exists():
    raise FileNotFoundError(
        f"illinois_mpfr.so introuvable : {SO_PATH}\n"
        f"Compiler : cd c_modules && make"
    )
```

---

## 📊 Tableau de référence — d'où vient chaque composant

```
Composant                Fichier source           Fonction
─────────────────────────────────────────────────────────────
Détection Z(t) batch     riemann_siegel_batch.py  Z_batch(t_array)
Détection Z(t) scalaire  theta_rapide.py          Z_fast(t, dps=25)
Affinage Illinois C      c_modules/illinois_C.so  lib.illinois_mpfr(a,b,tol)
Parallélisme             parallel_scanner.py      calculer_zeros_parallele()
Validation Turing        turing_validation.py     valider_turing(zeros, dps=30)
N(T) attendu             turing_validation.py     N_attendu(T_MAX)
```

Ne jamais réimplémenter ces fonctions — importer uniquement.

---

## 🔧 Architecture du worker v4.1

Le .so doit être chargé APRÈS fork(), à l'intérieur du worker :

```python
T_SEUIL_ILLINOIS_C = 300.0

def worker_v4_1(args):
    """
    Worker multiprocessing v4.1.
    - .so chargé APRÈS fork() → pas de corruption mémoire
    - CuPy initialisé APRÈS fork() → pas de cudaErrorInitializationError
    - Z_batch() pour détection vectorisée
    - Illinois C pour t ≥ 300, mpmath pour t < 300
    """
    t_start, t_end, step, so_path = args

    # Charger .so APRÈS fork
    import ctypes, numpy as np
    lib = ctypes.CDLL(str(so_path))
    lib.illinois_mpfr.restype  = ctypes.c_double
    lib.illinois_mpfr.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]

    # Import Z_batch APRÈS fork (CuPy init post-fork si disponible)
    from riemann_siegel_batch import Z_batch
    import mpmath

    zeros_segment = []
    TAILLE_BLOC   = 5000
    t_courant     = t_start

    while t_courant < t_end:
        t_fin_bloc = min(t_courant + TAILLE_BLOC * step, t_end)
        t_array    = np.arange(t_courant, t_fin_bloc, step)
        if len(t_array) < 2:
            break

        # Détection vectorisée — Z_batch correct partout (même t=14)
        Z_vals = Z_batch(t_array)
        idx    = np.where(np.diff(np.sign(Z_vals)))[0]

        for i in idx:
            a    = float(t_array[i])
            b    = float(t_array[i + 1])
            t_mid = (a + b) / 2.0
            try:
                if t_mid >= T_SEUIL_ILLINOIS_C:
                    # Illinois C — N ≥ 7 termes, fiable
                    zero = lib.illinois_mpfr(a, b, 1e-12)
                else:
                    # mpmath — t < 300, N < 7 termes, Illinois C imprécis
                    zero = float(mpmath.findroot(mpmath.siegelz, t_mid))

                if a - 1e-10 <= zero <= b + 1e-10:
                    zeros_segment.append(zero)
            except Exception:
                pass  # Turing détectera

        t_courant = float(t_array[-1]) + step

    return zeros_segment
```

---

## ⚠️ Règles absolues du projet

```python
# STEP sécurisé
STEP = min(2 * math.pi / (5 * math.log(T_MAX / (2 * math.pi))), 0.10)

# N(T) — le 'e' est obligatoire
N = int((T_MAX / (2*math.pi)) * math.log(T_MAX / (2*math.pi*math.e)))

# Visualisation
plt.savefig(chemin_png, dpi=150)
plt.close()   # jamais plt.show()

# Commentaires en français
# Variables : t_courant, Z_vals, zeros_segment, t_mid
```

---

## 📋 Structure de compute_zeros_v4_1.py

```
Section 0 — Docstring (différences v4 → v4.1, les 5 erreurs corrigées)
Section 1 — Imports + chargement .so (arrêt si absent)
Section 2 — Constante T_SEUIL_ILLINOIS_C = 300.0 + justification
Section 3 — worker_v4_1() (Z_batch + seuil Illinois C / mpmath)
Section 4 — Paramètres (copier v4 — même interface)
Section 5 — LMFDB (copier v3/v4 — 20 références)
Section 6 — Visualisation (Z_batch au lieu de mpmath.siegelz)
Section 7 — CSV + Log (copier v4, changer "v4" → "v4.1")
Section 8 — main() → calculer_zeros_parallele → Turing → LMFDB → log → PNG
```

Ne pas modifier : v3.py, v4.py, parallel_scanner.py, riemann_siegel_batch.py

---

## 🧪 Critères de succès

### Test T=20 (1 zéro, < 3 secondes)
```
Premier zéro : 14.134725141734693  (écart < 1e-10)
Méthode      : mpmath_petit_t  (t=14 < 300 — normal et attendu)
```

### Test T=500 (~149 zéros, < 20 secondes)
```
Score LMFDB  : 20/20 à < 1e-10
Turing       : COMPLET — 0 zéro manquant
Workers      : 4
```

### Vérification des logs (critère binaire absolu)
```
✅ DOIT apparaître :
   illinois_C        (t ≥ 300 — majorité des zéros)
   mpmath_petit_t    (t < 300 — ~87 zéros, légitime)
   Z_batch           (détection)
   Workers : 4

❌ NE DOIT PAS apparaître :
   mpmath.siegelz    (détection — interdit)
   illinois_C→mpmath (fallback non borné — interdit)
   séquentiel        (parallélisme obligatoire)
   Z_double          (du .so — ne pas charger)
```

---

## 🔗 Fichiers de référence

```
compute_zeros_v3.py          ← source parallélisme + Z_batch
compute_zeros_v4.py          ← source illinois_mpfr.so (Sections 1–2 à adapter)
riemann_siegel_batch.py      ← interface Z_batch()
parallel_scanner.py          ← interface calculer_zeros_parallele()
c_modules/illinois_mpfr.so   ← compilé, opérationnel
pdf/optimisation/analyse_problemes_v3_v4.pdf  ← diagnostic P1–P6
```

Branche active : Riemann_Lab_C

---
*Prompt v3 — 24 mai 2026 — Riemann_Lab / hprzeta*
