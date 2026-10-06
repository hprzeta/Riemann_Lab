---
name: riemann-proof-status
description: |
  Statut honnête des affirmations mathématiques du projet `Riemann_Lab` de hprzeta — registre append-only distinguant théorème prouvé, conjecture, heuristique, résultat vérifié numériquement, et question transmise sans réponse.

  Utiliser ce skill dès que l'utilisateur demande de :
  - Évaluer si une affirmation (la sienne, celle d'un article, celle générée par Ollama/RAG) est prouvée, conjecturée, ou seulement observée numériquement
  - Consigner un résultat nouveau (calcul, lemme, observation statistique) avec son statut exact
  - Vérifier la fraîcheur d'un statut déjà consigné (un résultat "conjecturé" a-t-il depuis été prouvé ou réfuté dans la littérature ?)
  - Rédiger une section "état de l'art" ou une réponse qui mélange plusieurs niveaux de certitude et risque de les confondre
  - Décider si une piste de recherche doit être transmise (à un humain, à Codex, à un article externe) faute de pouvoir être tranchée ici

  Déclencher aussi pour : toute discussion sur l'Hypothèse de Riemann elle-même, ses équivalents, ou tout résultat "trop beau pour être vrai" qui mérite un statut prudent avant d'être répété.
---

# Riemann Proof Status Skill

Skill de traçabilité épistémique pour `Riemann_Lab`. Il encode noir sur blanc l'exigence
déjà présente dans le style de travail attendu par hprzeta — « distinguer clairement :
théorème prouvé, conjecture, heuristique, intuition » et « signaler immédiatement toute
hypothèse non justifiée » — pour qu'aucune affirmation ne change de statut silencieusement
au fil des sessions.

> Inspiré de deux sources externes analysées le 27/09/2026 (voir `synthese_skills_zeta.md`) :
> le protocole de preuve à 5 statuts du skill `evomath-tao` (dépôt `EvoScientist/EvoSkills`,
> Apache 2.0) et le registre append-only `research-state` du plugin `mathbox` (auteur
> `nidrissi`, MIT). Ni l'un ni l'autre n'a été importé tel quel — ce skill est une
> reformulation sur mesure pour Riemann_Lab, pas une dépendance externe.

---

## 1. Les 5 statuts — jamais un 6ᵉ, jamais un mélange

| Statut | Sens exact | Exemple dans Riemann_Lab |
|---|---|---|
| `PROVED` (prouvé) | Démonstration complète, publiée et relue, ou vérifiée pas à pas dans cette session | L'équation fonctionnelle ξ(s)=ξ(1−s) |
| `CONJECTURED` (conjecturé) | Énoncé précis, jamais démontré, soutenu par des arguments ou indices | L'Hypothèse de Riemann elle-même ; la conjecture de Montgomery (§ skill `riemann-statistics-gue`) |
| `VERIFIED_NUMERICALLY` (vérifié numériquement) | Confirmé sur une plage finie de calcul, jamais une preuve pour tout n | Les 10M+ zéros calculés sont sur Re(s)=½ jusqu'à T≈5M — ne prouve rien au-delà |
| `HEURISTIC` (heuristique) | Argument de plausibilité (densité, moments, analogie RMT), pas un calcul ni une preuve | La répulsion des niveaux façon GUE comme indice en faveur de HdR |
| `HANDED_OFF` (transmis) | Question identifiée mais non tranchée ici — transmise à un humain, à Codex, ou laissée ouverte dans la littérature | Le mécanisme exact du déficit de 63 zéros (§6 `synthese_skills_zeta.md`, point 6) |

**Règle stricte** : une affirmation n'a jamais deux statuts à la fois, et ne change de
statut que par une action explicite consignée (§3), jamais par glissement de langage d'une
réponse à l'autre (ex. passer de « on observe que » à « on a montré que » sans preuve
nouvelle).

---

## 2. Format d'entrée dans le registre

Chaque affirmation notable reçoit un bloc, ajouté (jamais réécrit) dans
`docs/proof_status.md` (ou équivalent wiki — à créer, fichier additif, append-only comme
`JOURNAL.md`) :

```markdown
### <énoncé en une phrase>
- **Statut** : PROVED | CONJECTURED | VERIFIED_NUMERICALLY | HEURISTIC | HANDED_OFF
- **Date** : AAAA-MM-JJ
- **Portée exacte** : (ex. "pour T < 5×10⁶", "pour Re(s)=½ uniquement", "sous HdR")
- **Justification / source** : preuve interne, référence externe (voir `riemann-literature-scout`),
  ou calcul (fichier + commit)
- **Historique de statut** : uniquement si le statut a changé — ligne datée, jamais de réécriture
  du bloc d'origine (ex. "2026-10-02 : CONJECTURED → PROVED, voir arXiv:XXXX.XXXXX")
```

---

## 3. Checklist avant de changer un statut

1. `CONJECTURED`/`HEURISTIC` → `PROVED` : la preuve est-elle relue par une source externe
   fiable (`riemann-literature-scout`) ou vérifiée pas à pas dans cette session avec toutes
   les étapes explicitées (pas de "on peut montrer que...") ?
2. `VERIFIED_NUMERICALLY` → jamais promu directement à `PROVED` : une vérification
   numérique, même sur des milliards de cas, ne devient jamais une preuve. Le seul chemin
   est `VERIFIED_NUMERICALLY` + une preuve indépendante obtenue séparément.
3. Toute affirmation qui semble contredire un résultat déjà `PROVED` déclenche un
   `HANDED_OFF` immédiat (ne jamais trancher seul un conflit avec un théorème établi) —
   recouper avec `riemann-literature-scout` avant toute conclusion.
4. Un résultat produit par Ollama/RAG BrainVault ne peut **jamais** entrer directement en
   `PROVED` ou `VERIFIED_NUMERICALLY` — il entre au mieux en `HEURISTIC`, à re-vérifier
   (cohérent avec le garde-fou `valeurs_non_ancrees()` documenté dans `riemann-agent-bridge`).

---

## 4. Fraîcheur — détecter l'obsolescence

Au début de toute session touchant à l'Objectif 2 (approfondissement de l'HdR), un rapide
`grep` sur `docs/proof_status.md` pour les entrées `CONJECTURED` ou `HANDED_OFF` de plus de
~2 mois : proposer de vérifier si la littérature a bougé entre-temps (via
`riemann-literature-scout`) avant de repartir dessus comme si rien n'avait changé — même
logique que la règle de fraîcheur RAG déjà documentée (corpus figé depuis le 25/07/2026,
voir `synthese_skills_zeta.md` §3bis).

---

## 5. Format de sortie d'une évaluation de statut

1. **Statut proposé** (un seul des 5, jamais un mélange).
2. **Portée exacte** de l'énoncé (sous quelles conditions il est vrai/vérifié).
3. **Ce qui manque** pour monter d'un cran (ex. « pour passer de CONJECTURED à PROVED, il
   manque X »).
4. **Contre-exemples à envisager**, si l'énoncé semble fragile (cohérent avec la règle de
   collaboration « proposer des contre-exemples si une idée semble fragile »).

---
*Skill du projet Riemann_Lab · Créé le 27/09/2026 — inspiré de `evomath-tao` (EvoSkills) et
`research-state` (Mathbox), voir `synthese_skills_zeta.md` §4.2.*
