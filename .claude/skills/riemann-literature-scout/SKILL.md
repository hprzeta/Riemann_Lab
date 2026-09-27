---
name: riemann-literature-scout
description: |
  Veille bibliographique pour le projet `Riemann_Lab` de hprzeta — suivi arXiv et des publications universitaires (US, Chine, Russie) autour de la fonction zêta de Riemann et de l'hypothèse de Riemann.

  Utiliser ce skill dès que l'utilisateur demande de :
  - Chercher, résumer ou classer des articles récents sur ζ(s), l'HdR, les zéros non-triviaux, la répartition des nombres premiers
  - Faire un point de veille (arXiv, préprints, séminaires) sur une approche particulière (Lean/formalisation, méthodes GUE, produits eulériens, etc.)
  - Comparer les approches de plusieurs équipes/institutions (Princeton/IAS, MIT, Michigan, Berkeley, Stanford ; Tsinghua, Peking, CAS ; Steklov, MGU)
  - Alimenter `docs/bibliographie/` ou une section "état de l'art" du wiki

  Déclencher aussi pour : rédaction de résumés gradués (débutant → expert) d'un article, identification de blocages/limites d'une preuve.
---

# Riemann Literature Scout Skill

Skill de veille bibliographique pour `Riemann_Lab`. Correspond à `riemann-litwatch` (Kimi) et
`arxiv-veille-zeta` (DeepSeek) dans les audits croisés — unifié ici sous un seul skill.

---

## 1. Périmètre de veille

| Zone | Institutions prioritaires | Angles suivis |
|---|---|---|
| 🇺🇸 États-Unis | Princeton/IAS, MIT, University of Michigan, UC Berkeley, Stanford | Analyse analytique, méthodes de moments, GUE/RMT, formules explicites |
| 🇨🇳 Chine | Tsinghua, Peking University, Chinese Academy of Sciences (CAS) | Théorie analytique des nombres, cribles, estimations de sommes d'exponentielles |
| 🇷🇺 Russie | Steklov Mathematical Institute, MGU (Lomonossov) | Tradition analytique russe (Vinogradov, Korobov), méthodes de la fonction zêta |
| Formalisation | Mathlib/Lean community (transversal) | Prolongement analytique, équation fonctionnelle — alimente le stub `riemann-formal-lean` |

Sources : arXiv (`math.NT`, `math.CA`), pages de publications des laboratoires ci-dessus,
zbMATH/MathSciNet quand accessible, LMFDB pour les données de référence.

## 2. Méthode de veille

1. **Requête ciblée** plutôt que balayage large : partir d'un mot-clé précis (ex. "pair
   correlation nontrivial zeros", "Riemann-Siegel asymptotics", "Lean formalization zeta
   functional equation") plutôt que "Riemann Hypothesis" seul (trop de bruit).
2. **Filtrer par récence** : privilégier les 24 derniers mois sauf demande explicite d'un
   historique ; toujours donner la date de publication.
3. **Classer chaque résultat** selon la même distinction que le style de travail attendu par
   l'utilisateur : **théorème prouvé**, **conjecture**, **heuristique**, **intuition**. Ne
   jamais présenter un résultat non publié/non review comme établi.
4. **Résumé gradué** (conforme à la pédagogie du projet) : (a) une phrase pour un débutant,
   (b) le résultat formel avec notation standard, (c) pourquoi ça compte pour l'HdR ou pour
   `Riemann_Lab` spécifiquement.

## 3. Sortie type

Pour chaque article retenu, produire un bloc :

```markdown
### <Titre> — <Auteurs>, <année>
- **Source** : arXiv:XXXX.XXXXX / <institution>
- **Statut** : théorème prouvé | conjecture | heuristique
- **Résumé (1 phrase)** : ...
- **Résultat formel** : ... (LaTeX)
- **Pertinence Riemann_Lab** : lien avec v16 / Étape 2 (GUE) / formalisation Lean / autre
- **Limites signalées par les auteurs** : ...
```

Ces blocs alimentent `docs/bibliographie/` (voir arborescence §4.5 de `synthese_skills_zeta.md`).

## 4. Garde-fous

- Ne jamais inventer une référence ou une cote arXiv : si l'accès réseau est indisponible ou
  incertain, le dire explicitement plutôt que de fabriquer un résultat plausible.
- Un résultat qui semble contredire l'HdR ou un résultat classique déclenche une vérification
  renforcée (double source) avant d'être reporté à l'utilisateur.
- Toujours distinguer un résultat sur l'HdR **générale** d'un résultat sur une **portion** de la
  droite critique ou une famille de fonctions L particulière (confusion fréquente dans les
  résumés grand public).
- Le MCP `arxiv-mcp-server` (voir §4.3 de `synthese_skills_zeta.md`, priorité 🔴 3) est le canal
  privilégié une fois configuré ; en son absence, WebSearch/WebFetch directs sur arXiv.

## 5. Articulation avec les autres skills

- Un résultat statistique (corrélation de paires, spacing) → transmettre à
  `riemann-statistics-gue` pour comparaison avec les données numériques du projet.
- Un résultat de formalisation → transmettre au stub `riemann-formal-lean`.
- Une conjecture à tester numériquement → passer par `riemann-agent-bridge` pour décider si
  Ollama (premier filtre) ou Claude Code/Codex traite la vérification.

---
*Skill créé le 27/09/2026 — Vague V2 du plan de mutualisation skills/MCP (voir `synthese_skills_zeta.md` §4.2, item 2).*
