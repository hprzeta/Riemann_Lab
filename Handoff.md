# Riemann_Lab — Handoff
> Dernière mise à jour : **2 juin 2026** · hprzeta
> Branche active : `Riemann_Lab_C` · Dernier commit : `d9bb267` (+ instrumentation à pousser)

> 🧭 **Ce fichier est volontairement court.** Il ne contient que *l'état courant* et la
> *prochaine action*. Il est **remplacé** (pas enrichi) à chaque fin de session.
> - L'historique complet daté → `JOURNAL.md`
> - La stack outils / roadmap / formation → `STACK.md`

---

## 🚀 REPRENDRE ICI

### État (2 juin 2026)

**Runs v4.1 réels effectués** (dossiers `calculs/v4_1_T300_20260602_162919/` et
`calculs/v4_1_T1000_20260602_163940/`) :

| Run | Zéros | Durée | Vitesse | Affinage | Turing | LMFDB |
|---|---|---|---|---|---|---|
| T=300 | 138 | 73.4 s | **1.88 z/s** | 100 % mpmath (C jamais appelé) | ✅ COMPLET | 19/20 |
| T=1000 | 649 | 603.8 s | **1.07 z/s** | 78.7 % Illinois_C + 21.3 % mpmath | ✅ COMPLET | 19/20 |

**⚠️ Découverte clé — le « 41 z/s (×39) » NE se transmet PAS au pipeline.**
- Le ×39 était un **micro-benchmark unitaire du noyau** ; en run réel, le pipeline reste
  à **~1 z/s** = exactement la vitesse de v3 (1.02 z/s à T=10000).
- Segment t≥300 isolé (511 zéros) ≈ **~1 z/s**, pas 41.
- Le temps/zéro **monte** avec t (0.53 → 0.93 s) → goulot **siegelz-dépendant** qui croît
  en O(√t), pas l'itération Illinois.
- **Hypothèse « finition Newton dps=25 » RÉFUTÉE** : lecture du code → cette finition
  N'EXISTE PAS dans `compute_zeros_v4_1.py`. Vrai goulot non encore localisé.
- γ₂₀ = 8.06e-10 (artefact de table LMFDB connu, pas une erreur de calcul).

**Correctif fait :** ajout d'un profileur `chrono_phases.py` + instrumentation de
`compute_zeros_v4_1.py` (phases `detection` / `illinois_C` / `mpmath_petit_t` /
`mpmath_fallback` / `turing`). Compile OK. **À pousser sur `Riemann_Lab_C`.**

### Prochaine action

1. **Pousser** `chrono_phases.py` + `compute_zeros_v4_1.py` instrumenté (voir commandes ci-dessous).
2. **Run profilé T=1000** → lire le bloc `[PROFIL PHASES]` → localiser les ~500 s
   (detection ? illinois_C réel ? mpmath_petit_t ?). **Mesure avant toute réécriture.**
3. **Vérif B** sur [300,700] : `|γ_Illinois_C − γ_référence|` → si <1e-10, Illinois_C pur
   suffit pour le régime *comptage*.
4. **Benchmark Arb vs siegelz** sur [300,700] — **seulement si** le profil désigne
   l'évaluation de Z comme goulot. Mesurer le vrai facteur avant de réécrire.
5. Puis rapport `v5 → v4.1` : `pdf/optimisation/analyse_problemes_v5_v4_1.pdf`.

**En attente (non bloquant) :**
- Pousser `Formules_zeta.md` (929 l., §17) + `Bibliotheques.md` (390 l., §12) sur GitHub **+ wiki**.
- Versionner les 4 skills — Phase 2 du plan `docs/plan_versionner_skills_20260601.md`.

### Commandes d'ouverture

```bash
cd ~/projet_zeta/
source zeta_env/bin/activate
git checkout Riemann_Lab_C
git pull origin Riemann_Lab_C
claude
```

### Commandes de push (instrumentation)

```bash
cd ~/projet_zeta/
git checkout Riemann_Lab_C
cp ~/Téléchargements/chrono_phases.py        src/calculs/optimisation/chrono_phases.py
cp ~/Téléchargements/compute_zeros_v4_1.py   src/calculs/optimisation/compute_zeros_v4_1.py
git add src/calculs/optimisation/chrono_phases.py src/calculs/optimisation/compute_zeros_v4_1.py
git commit -m "feat(v4.1): profileur 3+1 phases pour localiser le goulot du pipeline"
git push origin Riemann_Lab_C
```

---

## ✅ Ce qui fonctionne (état actuel)

| Fichier | Rôle | Statut |
|---|---|---|
| `compute_zeros_v2.py` | Z(t) + Illinois + mpmath 50 dps | ✅ 10 142 zéros |
| `compute_zeros_v3.py` | Orchestrateur parallèle + Turing | ✅ opérationnel — 1.02 z/s (T=10000) |
| `compute_zeros_v5.py` | Illinois_C pur 100 %, biais < 1e-13 | ✅ validé (lent) |
| `compute_zeros_v4_1.py` | Z_batch + Illinois_C post-fork + 4 workers | ⚠️ correct (Turing+LMFDB OK) mais **pipeline ~1 z/s** — ×39 unitaire NON transmis · **instrumenté** |
| `chrono_phases.py` | Profileur 3+1 phases (localisation goulot) | 🆕 à pousser |
| `riemann_siegel.py` | Formule RS | ✅ |
| `theta_rapide.py` | θ(t) via Stirling | ✅ |
| `turing_validation.py` | N(T) Turing-Backlund | ✅ |

---

## ⚠️ Formules critiques — ne jamais reproduire les erreurs

**N(T) — le `e` est obligatoire :**
$$N(T) = \frac{T}{2\pi} \ln\!\left(\frac{T}{2\pi e}\right)$$
Sans le `e` : N(100 000) sous-estimé de ~64 % (49 346 au lieu de 138 067).

**STEP sécurisé (évite les zéros manqués) :**
$$\text{STEP} = \min\!\left(\frac{2\pi}{5 \ln(T_{\max}/2\pi)},\ 0.10\right)$$

**Riemann-Siegel** ($N = \lfloor\sqrt{t/2\pi}\rfloor$, propre à **chaque** $t$) :
$$Z(t) = 2\sum_{n=1}^{N} \frac{\cos(\theta(t) - t \ln n)}{\sqrt{n}} + R(t)$$

**θ(t) asymptotique (Stirling) :**
$$\theta(t) = \frac{t}{2}\ln\frac{t}{2\pi} - \frac{t}{2} - \frac{\pi}{8} + \frac{1}{48t} + \frac{7}{5760\,t^3} + O(t^{-5})$$

**Coût d'une évaluation Z (clé du goulot) :** une somme RS a $N(t)=\lfloor\sqrt{t/2\pi}\rfloor$
termes → coût $\mathcal{O}(\sqrt{t})$ par évaluation. C'est ce qui fait monter le temps/zéro
avec $t$, indépendamment de l'algorithme d'affinage.

---

## 📐 Règles KaTeX (critique)

| ❌ Interdit | ✅ Correct |
|---|---|
| `\operatorname{Re}` | `\text{Re}` |
| `\operatorname{Im}` | `\text{Im}` |

Délimiteurs : `$...$` inline · `$$...$$` display.

---

## 🔐 Rappel sécurité Git

```bash
git status              # TOUJOURS avant git add -A
grep mcp .gitignore     # .mcp.json ne doit JAMAIS être commité
```
Un secret exposé = secret mort : **on le révoque toujours**, on ne suit jamais le lien
« unblock-secret » de GitHub.

---

## 🔗 Références rapides

| Ressource | Lien |
|---|---|
| Site du projet | https://hprzeta.github.io/Riemann_Lab/ |
| LMFDB | https://lmfdb.org/zeros/zeta/ |
| Journal complet | `JOURNAL.md` |
| Stack & roadmap | `STACK.md` |

---

## 🔻 Avant de fermer la session

1. Ajouter un **pavé daté en haut de `JOURNAL.md`** (résumé de la session).
2. **Écraser** la section « REPRENDRE ICI » ci-dessus avec le nouvel état.
3. Ne pas toucher au reste de ce fichier ni à `STACK.md` (sauf nouvel outil).

---
> *Mise à jour : 2 juin 2026 · Handoff.md (1 fichier MD modifié) · ~175 lignes · Auteur : hprzeta*
