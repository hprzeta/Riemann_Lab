# Archive de session — Documentation Vagues V1-V3 (plan mutualisation skills/MCP)

Session du 27 septembre 2026. Objectif : intégrer dans le suivi de session du
projet (`JOURNAL.md`/`Handoff.md`) le travail des Vagues V1 à V3 du plan de
mutualisation skills/MCP, déjà commité sur `Riemann_Lab_IA` lors d'une session
précédente — sans toucher au cœur de calcul ni lancer les vagues suivantes.

---

## 1. Consigne initiale

Instruction transmise en une seule fois, citée verbatim (extraits) :

> Contexte : je continue le travail sur les skills de Riemann_Lab (branche
> `Riemann_Lab_IA`). Voici ce qui a été fait aujourd'hui (27/09/2026), à
> intégrer dans le suivi de session du projet (JOURNAL.md et Handoff.md du
> wiki, selon les conventions déjà en place — vérifie d'abord si
> `~/riemann_handoff/Handoff.md` (local, hors dépôt) est toujours la copie
> active la plus à jour [...], et mets à jour la bonne copie en premier ;
> propage ensuite si besoin, sans dupliquer).

Le message détaillait le contenu des Vagues V1-V3 (déjà commité), les
décisions ouvertes et les vagues restantes (V4, V5), et fixait explicitement
le périmètre :

> Ne touche à rien d'autre (pas de Vague V4/V5 sans validation explicite de ma
> part), et ne modifie jamais le cœur de calcul (`compute_zeros_v*.py`,
> `illinois_*`, `scan_arb*`) dans cette tâche de documentation.

---

## 2. Vérification de l'état réel du dépôt

`git status` et `git log --oneline -8` exécutés sur `Riemann_Lab_IA` avant
toute modification, pour confirmer la présence des 4 commits annoncés et
l'absence de modification parasite :

| Commit | Contenu |
|---|---|
| `df46f82` | Vague V1 — `AGENTS.md`, `.mcp.json.example`, `handoff/` |
| `9e0b203` | Vague V2 — 3 nouveaux skills |
| `5e3a44d` | Vague V3 — mise à jour `riemann-code-review`/`riemann-security-review` |
| `70e7463` | Correctif V3 — cache Riemann-Siegel confirmé |

Les 4 commits étaient bien présents, dans l'ordre attendu. Des fichiers non
suivis et modifications non commitées étaient présents dans l'arbre de
travail (PDF, scripts, archives), mais sans rapport avec les Vagues V1-V3 —
laissés tels quels, non touchés.

---

## 3. Copie active de `Handoff.md` — arbitrage

Vérification demandée explicitement dans la consigne avant toute écriture.
Lecture croisée du fichier wiki, qui indique lui-même sa propre péremption :

> ⚠️ Ce fichier était resté figé au 16 août 2026 [...] Le suivi actif de
> session vit en pratique dans `~/riemann_handoff/Handoff.md` (local, hors
> dépôt) — section « REPRISE ICI » — c'est lui qui contient le détail à jour.

Confirmé : `~/riemann_handoff/Handoff.md` (local, jamais commité) est la
copie active. Le `Handoff.md` du wiki n'est qu'un pointeur court,
resynchronisé ponctuellement. Mise à jour effectuée en conséquence : détail
complet dans le fichier local, pointeur court propagé dans le wiki, sans
dupliquer le contenu détaillé.

---

## 4. Mises à jour effectuées

### `~/riemann_handoff/Handoff.md` (local, non versionné)

- Nouveau pavé daté du 27/09/2026 ajouté en tête du bloc `PROMPT_REPRISE`
  (résumé des Vagues V1-V3, état des 7 skills, 6 points en attente).
- Bandeau de synthèse en tête de fichier mis à jour (« Dernière mise à jour »).

### `Riemann_Lab.wiki/Handoff.md`

- Section « REPRENDRE ICI » remplacée par le nouveau résumé (pointeur court
  vers le fichier local), l'ancienne section (MARGE_SECURITE, 13/09) archivée
  sous un titre « 🗄️ Historique », selon le pattern déjà en usage dans ce
  fichier pour les sections closes.

### `Riemann_Lab.wiki/JOURNAL.md`

- Nouveau pavé append-only ajouté en tête (le plus récent en haut, comme
  imposé par la règle du fichier), format « ## AAAA-MM-JJ - HHhMM - titre -
  commit », détaillant les 3 vagues, l'état des 7 skills et les 6 points en
  attente.

Commit unique sur le dépôt wiki (`master`), poussé sur `origin` :

| Commit | Dépôt | Contenu |
|---|---|---|
| `7481432` | `Riemann_Lab.wiki` (master) | Mise à jour Handoff.md + JOURNAL.md — session 27/09 |

Aucun commit ni modification sur le dépôt de code (`Riemann_Lab_IA`) pendant
cette tâche — conforme à la consigne (documentation uniquement).

---

## 5. Points laissés en attente (rappel explicite du périmètre)

Conformément à la consigne, les 6 points suivants ont été documentés dans le
Handoff mais **aucune action n'a été engagée** dessus :

1. Réingestion RAG BrainVault (corpus figé depuis le 25/07/2026).
2. « Cerveau autonome zêta » (vision 23 points) — chantier séparé ou intégré ?
3. Anomalie non résolue : déficit de 63 zéros entre un run
   `MARGE_SECURITE=10.0` et un run `MARGE=2.0`.
4. Vague V4 (tests/CI) — non lancée.
5. Vague V5 (réorganisation `phase-c-illinois`/`CLAUDE.md`/scripts) — non
   lancée.
6. Gate empirique T=100k `MARGE_SECURITE` (reprise dormante antérieure,
   toujours en attente, indépendante de ce chantier skills).

---

*Document créé le 27 septembre 2026 — Riemann_Lab — hprzeta.*
