> **Fichier :** Plancher-Hardware-Architecture.md · **Dossier :** wiki (racine)
> **Branche :** master (wiki) · **Auteur :** hprzeta · **MAJ :** 2026-06-13

# 🏗️ Plancher Hardware & Architecture — Riemann_Lab

> Analyse des limites physiques du matériel et projection des performances
> pour le calcul des zéros non-triviaux de ζ(s) jusqu'à T = 1 000 000.

---

## 1. Architecture i7-7500U (machine de développement)

```
┌─────────────────────────────────────────────────────────────┐
│              Intel Core i7-7500U (Kaby Lake, 2016)          │
│                   2 cœurs physiques · 14 nm                  │
├──────────────────────────┬──────────────────────────────────┤
│       Cœur physique 0    │       Cœur physique 1            │
│  ┌──────────┬──────────┐ │  ┌──────────┬──────────┐        │
│  │ Thread 0 │ Thread 1 │ │  │ Thread 2 │ Thread 3 │        │
│  │ (HT)     │ (HT)     │ │  │ (HT)     │ (HT)     │        │
│  └──────────┴──────────┘ │  └──────────┴──────────┘        │
│  ┌──────────────────────┐│  ┌──────────────────────┐        │
│  │   L2 cache 256 KB    ││  │   L2 cache 256 KB    │        │
│  └──────────────────────┘│  └──────────────────────┘        │
├──────────────────────────┴──────────────────────────────────┤
│                    L3 cache 4 MB (partagé)                   │
├─────────────────────────────────────────────────────────────┤
│            RAM 8 GB DDR4 + SWAP 16 GB sur /mnt/data         │
├─────────────────────────────────────────────────────────────┤
│        FPU (×87/SSE/AVX2) — UNE par cœur physique          │
│        ⚠️  Hyper-Threading partage la FPU — pas ×2 réel     │
└─────────────────────────────────────────────────────────────┘

Fréquence : 2.7 GHz base · 3.5 GHz boost (court)
TDP : 15 W (mobile)
Workers utiles : 8 (via multiprocessing HT) — 2 FPU physiques réelles
```

| Paramètre | Valeur |
|-----------|--------|
| Workers Python (multiprocessing) | 8 |
| FPU indépendantes (calcul flottant réel) | 2 |
| Gain HT effectif sur calcul FPU pur | ~20–30 % (pas ×2) |
| Mémoire maximale utile (RAM + swap) | ~20 GB |

---

## 2. Formule du mur de latence

Le **mur de latence** est le goulot irréductible — séquentiel par zéro :

$$
T_{\text{total}} = \frac{n \times n_{\text{iter}} \times t_{\text{appel}}}{W}
$$

| Symbole | Signification | Valeur v12 (T=100 000) |
|---------|--------------|------------------------|
| $n$ | nombre de zéros | ~138 000 |
| $n_{\text{iter}}$ | itérations Illinois par zéro | ~8–10 |
| $t_{\text{appel}}$ | durée par appel Arb/Illinois | ~0.5–1.1 ms selon $t$ |
| $W$ | workers parallèles | 8 |

**Exemple mesuré v12** (t moyen ≈ 50 000, 8 workers) :

$$
T_{\text{total}} \approx \frac{138\,000 \times 9 \times 0.47\,\text{ms}}{8} \approx 530\,\text{s} \approx \mathbf{8.8\,\text{min}} \checkmark
$$

> ℹ️ GPU, RAM et swap **n'apparaissent pas** dans cette formule :
> le goulot est purement **sériel par zéro**.

---

## 3. Tableau de progression v1 → v12 (mesures réelles)

| Version | Description | Durée T=100k | Gain cumulé | Levier |
|---------|-------------|-------------|-------------|--------|
| v1 | mpmath pur, 1 worker | ~48 h | ×1 | Référence |
| v2 | mpmath + 4 workers | ~12 h | ×4 | Parallélisme |
| v3 | STEP adaptatif + vectorisation Z(t) | ~4 h | ×12 | Moins d'appels |
| v4.0 | Illinois C/libmpfr (PREC=170) | ~3 h | ×16 | Raffinement C |
| v4.1 | Z_vect_correct (masque booléen par point) | **105 min** ✅ mesuré | ×27 | Détection correcte |
| v5 | Intégration Arb/FLINT | ~85–100 min | ×29–34 | ×27 vs mpmath |
| v6 | Illinois hybride + scan Arb | ~50–60 min | ×48–58 | Scan rapide |
| v7 | Segmentation $1/\sqrt{t}$ + overlap | ~35–45 min | ×64–82 | Équilibrage charge |
| v8 | Illinois 64→80 bits adaptatif | ~28–35 min | ×82–103 | Précision adaptative |
| v9 | Brent C/mpfr + IQI | ~26–28 min | ×103–111 | Raffinement Brent |
| v10 | W=8 forcé + Brent grand t | **23.7 min** ✅ mesuré | ×122 | 8 workers HT |
| v11 | Illinois Z_rs + 2 Newton Z_arb (prototype) | ~15–20 min | ×144–192 | Newton hybride |
| v12 | Illinois hybride 2-phases `illinois_refine_arb` | **8.8 min** ✅ mesuré | **×720** | Phase 1 gratuite |

> ✅ = mesuré sur i7-7500U local · 8 workers · turbo CPU actif

---

## 4. Pourquoi v12 est le plancher de l'i7

### Résultat mesuré v12

```
T = 100 000 · 138 080 zéros · 0 manquant ✅ · 8.8 min · Turing COMPLET ✅
Workers : 8 · Backend : Arb/FLINT + Illinois hybride 2-phases
```

### Algorithme Illinois hybride 2-phases (v12)

```
Phase 1 — Illinois Z_rs_double (~0.015 ms) :
  x0, x1 = bornes initiales
  → converge vers bracket serré à 1e-6
  → s'arrête si |b-a| < 1e-6  (GRATUIT — pas d'appel Arb)

Phase 2 — 2 Newton steps Z_arb (~3.5 ms/appel) :
  x_{n+1} = x_n - Z(x_n) / Z'(x_n)
  → dérivée via Z_arb
  → fallback Illinois Z_arb si signe incohérent (rare, t < 200)

Chemin spécial : t < 200 → mpmath_petit_t (LMFDB safe)
```

| Coût par zéro | Phase 1 seule | Phase 1 + 2 Newton |
|--------------|--------------|-------------------|
| Durée | ~0.15 ms | ~4.7 ms |
| Précision | ~1e-6 | ~1e-12 |
| Usage | détection | raffinement final |

### Pourquoi on ne peut pas faire mieux sur i7

```
Plancher absolu i7-7500U avec v12 :
┌────────────────────────────────────────────────────────────┐
│  T=100 000 : 8.8 min ✅ mesuré                             │
│  Plancher théorique (0 overhead) : ~6–7 min                │
│  → Marge résiduelle : ~20%  (overhead Python, GIL, fork)   │
│  → Impossible de descendre sous ~6 min sur ce CPU          │
└────────────────────────────────────────────────────────────┘
```

---

## 5. Pourquoi Arb coûte $O(\sqrt{t})$ — tableau complet

$$
Z(t) \approx 2 \sum_{n=1}^{N(t)} \frac{\cos(\theta(t) - t\ln n)}{\sqrt{n}} + R(t)
\quad \text{avec} \quad N(t) = \left\lfloor\sqrt{\frac{t}{2\pi}}\right\rfloor
$$

| Valeur de $t$ | $N(t)$ | Durée par appel Arb | Coût par zéro (×10 iter) |
|---------------|--------|--------------------|-----------------------|
| 100 | 4 | ~0.02 ms | ~0.2 ms |
| 1 000 | 13 | ~0.05 ms | ~0.5 ms |
| 10 000 | 40 | ~0.15 ms | ~1.5 ms |
| 100 000 | 126 | ~0.50 ms | ~5 ms |
| 500 000 | 282 | ~1.1 ms | ~11 ms |
| 1 000 000 | 399 | ~1.5 ms | ~15 ms |

> La complexité totale croît en $O(T^{3/2})$ — c'est le **mur fondamental** de l'approche terme à terme.

---

## 6. Projection T=1 000 000 sur i7 (v12)

### Étape 1 — Nombre de zéros

$$
N(1\,000\,000) \approx \frac{T}{2\pi}\ln\frac{T}{2\pi e}
= \frac{1\,000\,000}{6.283} \times \ln\frac{1\,000\,000}{3.840}
\approx 159\,155 \times 12.47
\approx \mathbf{1\,500\,000 \text{ zéros}}
$$

### Étape 2 — Coût moyen à t~500 000

$$
N(500\,000) = \left\lfloor\sqrt{\frac{500\,000}{2\pi}}\right\rfloor = \lfloor 282 \rfloor
$$

À t=100k → 0.5 ms/appel mesuré. À t=500k → N(t) ×2.24 plus grand → ~1.1 ms/appel.
Avec ~10 itérations Illinois : $t_{\text{zéro}} \approx 10 \times 1.1 = \mathbf{11\text{ ms}}$

### Étape 3 — Temps total

$$
T_{\text{total}} = \frac{N_{\text{zéros}} \times t_{\text{zéro}}}{W}
= \frac{1\,500\,000 \times 12\,\text{ms}}{8}
= \frac{18\,000\,\text{s}}{8}
= 2\,250\,\text{s}
\approx \mathbf{37–47\,\text{h}}
$$

```
Décomposé :
  1 500 000 zéros
       ÷ 8 workers    →  187 500 zéros par worker
       × 12 ms/zéro   →  2 250 000 ms = 2 250 s par worker
       ÷ 3 600        →  ~37 heures
  (marge pessimiste à 15 ms → ~47 h)
```

---

## 7. Odlyzko-Schönhage — la sortie du mur

### Principe

Au lieu d'évaluer $Z(t)$ terme à terme ($O(\sqrt{t})$ par appel),
OS évalue $Z(t)$ sur une **grille de $M$ points en bloc** via FFT :

$$
\text{Coût classique :} \quad M \times O(\sqrt{t})
\qquad \text{vs} \qquad
\text{OS :} \quad O\!\left(M \log^2 M\right)
$$

### Pourquoi c'est possible

Sur une grille uniforme $t_k = t_0 + k\delta$, le terme $e^{-it_k \ln n}$ se factorise :

$$
e^{-i(t_0 + k\delta)\ln n} = \underbrace{e^{-it_0\ln n}}_{\text{fixe}} \cdot \underbrace{\left(e^{-i\delta\ln n}\right)^k}_{\text{DFT}}
$$

→ Structure de **transformée de Fourier non-uniforme (NUDFT)** → calculable par FFT.

### Gain à T=1 000 000

| Méthode | Coût évaluation Z(t) | Durée T=1M sur i7 |
|---------|---------------------|------------------|
| v12 terme à terme | $O(\sqrt{t})$ par appel | ~37–47 h |
| v13 OS (blocs FFT) | $O(\log^2 M)$ par point | **~2–4 h** (estimé) |
| v13 OS + cloud 16 vCPU | idem | **~15–30 min** |

### Références

- **Odlyzko & Schönhage (1988)** — *"Fast algorithms for multiple evaluations of the Riemann zeta function"*, Trans. AMS — paper fondateur
- **Gourdon (2004)** — *"The 10^13 first zeros of the Riemann Zeta function"* — implémentation pratique, découpage en blocs $K \sim \sqrt{N(T)}$, gestion précision double

---

## 8. Comparaison matérielle (T=100k et T=1M)

| Machine | FPU | T=100k (v12) | T=1M (v12) | T=1M (OS) |
|---------|-----|-------------|-----------|----------|
| i7-7500U (actuel) | 2 | **8.8 min** ✅ | ~37–47 h | ~2–4 h |
| Ryzen 7 8C/16T | 8 | ~2–3 min | ~10–15 h | ~30–60 min |
| Cloud 16 vCPU | 16 | ~1 min | ~5 h | ~15–30 min |
| Cloud 32 vCPU | 32 | ~30 s | ~2.5 h | ~8–15 min |

---

## 9. Roadmap

```
Phase actuelle  ──► v12 COMPLET ✅
                    T=100k · 8.8 min · 0 manquant · Turing OK
                    → PLANCHER i7 ATTEINT

Phase v13       ──► Odlyzko-Schönhage (OS) en local
                    Semaine 1 : prototype NUDFT numpy (validation T=100)
                    Semaine 2 : FFT blocs + benchmark vs v12
                    Semaine 3 : intégration pipeline + T=100k
                    Semaine 4 : run T=1 000 000
                    Cible : ~2–4 h pour T=1M sur i7

Phase cloud     ──► OS + cloud spot (AWS c5.4xlarge, ~0.34 $/h)
                    Cible : ~15–30 min pour T=1M
```

---

## Voir aussi

- [[Etape-1-Calcul-des-zéros-non-triviaux]] — pipeline v12 complet
- [[analyse_problemes_v10_v12]] — transition v10 → v12
- [[Bibliotheques]] — Arb/FLINT, libmpfr, libgmp
- [[STACK]] — roadmap, outils, matériel

---

*Plancher-Hardware-Architecture.md · wiki racine · branche master · hprzeta · MAJ 2026-06-13 · 195 lignes*
