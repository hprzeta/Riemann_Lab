# Prompt Claude Code — v4.1 : fix findroot (affinage)
> Date : **31 mai 2026** · Branche : `Riemann_Lab_C` · Auteur : hprzeta
> Remplace `prompt_claude_code_phase_prompt_v4.1.md` et `..._reprendre_memo.md` (fusionnés ici).
> Modèle conseillé : **Sonnet** (exécution de plan ; garder Opus pour la théorie Obj. 2).

---

## ⚠️ RÈGLE ABSOLUE
Ne saute aucune étape de test pour aller plus vite. Si tu es tenté de lancer
directement un run long, ARRÊTE-toi et montre-moi d'abord les chiffres demandés.
Attends ma validation explicite (« OK continue ») avant CHAQUE run. Ne lance jamais
un run de plusieurs minutes sans mon feu vert écrit.

---

## CONTEXTE (état au 31 mai 2026)
- `compute_zeros_v4_1.py` (commit `368d090`) est **JUSTE mais lent : 1.1 z/s** (cible 15–20).
- La détection `Z_vect_correct` est **VALIDÉE** : 0 désaccord vs `mpmath.siegelz` sur 4 plages.
  → Le Point d'arrêt « validation Z_batch » est **déjà passé**, ne pas le refaire.
- Le goulot restant est **l'affinage** : le callback ctypes `illinois_c_exact` appelle
  `mpmath.siegelz` à dps=35 (1.5–10 ms/appel) et sa sérialisation casse le parallélisme
  (×1.84 au lieu de ×4 ; test : `Pool(sleep)`=×3.9 OK, `Pool(worker_chunk)`=×1.84).

**Périmètre :** modifier `compute_zeros_v4_1.py`. NE PAS toucher à `compute_zeros_v4.py`
ni `compute_zeros_v5.py` (validés, gelés). Travailler uniquement sur `Riemann_Lab_C`.

---

## EXPLICATIONS MATHÉMATIQUES OBLIGATOIRES (avant de coder)
Pour chaque fonction mathématique touchée, écris d'abord la formule en LaTeX bien
formatée, puis explique-la, AVANT de coder. Au minimum :
- Fonction Z de Hardy : $Z(t) = e^{i\theta(t)}\,\zeta\!\left(\tfrac12+it\right)$, réelle pour
  $t$ réel ; ses changements de signe ↔ zéros de ζ sur la droite critique.
- $\theta(t)$ de Riemann-Siegel : $\theta(t) = \arg\Gamma\!\left(\tfrac14+\tfrac{it}{2}\right) - \tfrac{t}{2}\ln\pi$.
- Méthode d'Illinois (fausse position modifiée) et pourquoi `findroot(solver="illinois")` converge.
- Lien dps ↔ tolérance : pourquoi `tol=1e-12` exige un dps suffisant (cf. garde-fou ci-dessous).

**RÈGLE KaTeX :** utiliser `\text{Re}`, `\text{Im}` — JAMAIS `\operatorname{...}`.
Délimiteurs `$...$` inline et `$$...$$` display (compatibles wiki GitHub + index.html).

---

## ERREURS DÉJÀ COMMISES — NE PAS LES REPRODUIRE
1. **N(T)** : forme EXACTE $\dfrac{T}{2\pi}\ln\dfrac{T}{2\pi e}$, JAMAIS $\ln\dfrac{T}{2\pi}$ (sous-estimait ~64 %).
2. **Détection** : fonction Z de Hardy pour les changements de signe, JAMAIS $\text{Re}(\zeta(\tfrac12+it))$ (faux changements dus à la phase → bug v1 vers t≈432).
3. **STEP** : $\min\!\left(\dfrac{2\pi}{5\ln(T/2\pi)},\,0.10\right)$, sinon on rate des zéros à grand T.
4. **Visualisation** : `plt.savefig()` + `plt.close()`, JAMAIS `plt.show()` (bloque les logs).
5. **Turing** : distinguer explicitement MANQUE (delta > 0) vs SURPLUS (delta < 0).
6. **CSV** : ne jamais écraser un run validé ; tout nouveau run = fichier horodaté.

---

## MISSION — appliquer le fix findroot
1. Remplacer l'affinage par callback ctypes par, **directement dans chaque worker** :
   ```python
   mpmath.findroot(lambda x: siegelz(x), (t_a, t_b),
                   solver="illinois", tol=1e-12, maxsteps=80)
   ```
   (plus de callback ctypes → vrai parallélisme).
2. Mettre la précision en CONSTANTE nommée en haut du fichier :
   ```python
   DPS_AFFINAGE = 15   # HYPOTHÈSE — à valider sur les grands t (voir Vérif B)
   ```
   l'appliquer via `mp.dps` autour de l'affinage, et **restaurer `mp.dps` après**.
3. Garder la détection `Z_vect_correct` inchangée (elle marche : 0 désaccord).
4. Garder le parallélisme 4 workers (`parallel_scanner.py`, `multiprocessing`).
   ⚠️ JAMAIS `joblib` avec `mpmath` (GMP non thread-safe).
5. Tracer la méthode réelle dans les stats : `"mpmath_findroot_illinois"` (et non
   `"Illinois_C"`) — compromis assumé : on perd Illinois_C pur, on gagne le vrai ×4.

⛔ **POINT D'ARRÊT** : ne lance AUCUN run long avant d'avoir validé A et B ci-dessous.

---

## VALIDATION (obligatoire — montre les chiffres, attends « OK continue »)

### A. Run T=300 — justesse + vitesse
- 138/138 zéros, Turing-Backlund **COMPLET**, LMFDB **19/20 < 1e-10**.
- Afficher : nb de zéros, statut Turing, comparaison LMFDB, **vitesse (z/s)** et
  **gain parallèle réel** (viser proche de ×4).
- STOP. Montre les chiffres, attends mon feu vert.

### B. Vérif PRÉCISION AUX GRANDS t — critique pour `DPS_AFFINAGE`
> Raison : à $t \approx 9900$, un nombre d'ordre $10^4$ codé sur 15 chiffres
> significatifs ne garantit qu'une précision absolue ~$10^{-11}$ — à la limite de `tol=1e-12`.
- Affiner quelques zéros connus autour de $t \approx 9900$ (réf. `zetazero` ou LMFDB).
- Si l'écart dépasse 1e-10 à grand $t$ → `DPS_AFFINAGE` trop bas : **remonter à 20 puis 25**
  et refaire la vérif. **Documenter le dps finalement retenu.**
- STOP. Montre les écarts par t, attends mon feu vert.

---

## CRITÈRES DE SUCCÈS
- T=300 : 138/138, Turing complet, LMFDB 19/20 < 1e-10.
- Précision tenue à grand t (sinon ajuster `DPS_AFFINAGE` et re-tester).
- Vitesse nettement > 1.1 z/s (cible intermédiaire **> 5 z/s**).
- `plt.savefig()` + `plt.close()`.

---

## ENSUITE (seulement si A et B passent, après mon « OK continue »)
- Run **T=1000** de confirmation. **PAS de T=10000** dans cette session.

---

## RAPPORT DE TRANSITION — seulement après v4.1 validée
Génère `docs/analyse_problemes_v5_v4_1_YYYYMMDD.md` (date du jour) :
- En-tête : titre « Analyse des problèmes v5 → v4.1 », Auteur : hprzeta,
  Date : <date du jour>, branche `Riemann_Lab_C`.
- Par problème : cause mathématique + formules LaTeX + tableau de mesures exactes
  (écarts, vitesses avant/après, gain parallèle, dps retenu) + solution retenue.
- Tableau récapitulatif global (correction → gain mesuré).
- Bloc final « Questions ouvertes » (limites, perspectives, matériel).
- Pied de page : date de mise à jour + nombre de lignes du fichier `.md`.
- Formules en LaTeX, mêmes règles KaTeX que ci-dessus.
- Copier dans le wiki (`~/projet_zeta/Riemann_Lab.wiki/`, `git push origin master`).
  **NE PAS** pousser `Handoff.md` dans le repo de code.

---

## DISCIPLINE GIT (cf. CLAUDE.md)
- Commit `wip: checkpoint v4.1` à ~50 % de contexte.
- `git push origin Riemann_Lab_C` à ~70 %.
- À 80 % ou « 11% until auto-compact » : STOP, push, rapport court, exit.
- Avant tout `git add -A` : `git status` + `grep mcp .gitignore`.

---

## STYLE
- Débutant en Python : code **commenté ligne par ligne**.
- Expliquer chaque choix d'architecture ET sa justification mathématique avant de coder.
- Répondre en **français**. Distinguer théorème / conjecture / heuristique / intuition.

---
*Prompt daté du 31 mai 2026 — fusion de prompt_v4.1.md + reprendre_memo.md + garde-fou dps.*
