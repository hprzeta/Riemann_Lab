# État du projet SKILLS ZETA — 22/11/2026

> Rédigé sur claude.ai (projet SKILLS ZETA). Remplace `ETAT_SKILLS_ZETA_20261114.md` comme point de départ.
> Passation reçue de ZETA-TELANDROID (TEL-D13) : le suivi des skills revient à SKILLS ZETA.

## Réponse directe

Dépôt : **13 skills** `riemann-*`, identiques sur les 4 branches. Compte claude.ai : **12** (il manque `riemann-wireguard-diagnostic`).
Adoption de `grill-me` + `grilling` (Matt Pocock, MIT) décidée (D17 à D20) ; prompt prêt : `PROMPT_ADOPTION_GRILL_ME_20261122` (zip). Il attend `POUR_SKILLS_ZETA_grill_me_20261122.md` (STOP si absent ou si un SHA-256 diffère). Cible : **15 skills** (13 `riemann-*` + 2 tiers) dans le dépôt et le compte.

## État vérifié (clone du 22/11, `Riemann_Lab_IA` = `43b6b48`)

| Élément | Constat | État |
|---|---|---|
| `.claude/skills/` (IA, main, C, Test) | 13 skills identiques ; `CLAUDE.md` et `AGENTS.md` identiques sur les 4 branches | 🟢 |
| `riemann-wireguard-diagnostic` | 135 lignes, 1 fichier, description de 532 caractères, aucune IP | 🟢 importable tel quel |
| Compte claude.ai | 12 skills, sans wireguard | 🔴 → prompt d'adoption |
| Wiki `STACK.md` § Skills Claude | 13 lignes ✅ + `mattpocock/skills` 🔜 | 🟡 → prompt d'adoption |
| Site `docs/*.html` | aucun nombre de skills affiché | ⚪ inchangé (D18) |
| Instructions du projet, section 8 | « Skills existants (12) », sans wireguard | 🔴 → texte fourni dans le rapport, à coller par hprzeta |
| `pdf/audits_skills/ETAT_SKILLS_ZETA.md` (dépôt) | version du 14/11, « 12 skills » | 🔴 → remplacé par ce fichier (prompt, étape 4c) |
| Dossier `skills/` de ce projet (16 fichiers) | en contradiction avec D9 | 🟡 |

## grill-me + grilling : recoupement

| Point | Rapport TELANDROID | Vérification claude.ai (clone amont) | Accord |
|---|---|---|---|
| Commit | `abeeaf95660b…` (19/11/2026) | `abeeaf9` (19/11/2026) | 🟢 |
| Licence | MIT | MIT, © 2026 Matt Pocock | 🟢 |
| `grill-me/SKILL.md` | `caaf8b8de1684f96…` | `caaf8b8d…6ef88637`, 7 lignes | 🟢 |
| `grilling/SKILL.md` | `a146842ed93ca43d…` | `a146842e…42d4e2`, 30 lignes | 🟢 |
| Fichiers annexes | 2 × `agents/openai.yaml` | idem (pour Codex) | 🟢 |
| Scripts, hooks, réseau | aucun | aucun | 🟢 |
| Test manuel `/grill-me` (22/11, Claude Code, bac à sable, plan fictif « bibliothèque de 500 livres ») | concluant : `Skill(grilling)` chargé, 6 questions utiles, aucune action sans accord, ne devine pas | — | 🟢 |
| 6 questions par tour | relevé 🟡 | comportement voulu par `grilling` (« frontier » posée en un tour) | 🟢 |
| Estimation chiffrée non vérifiée | relevé 🟡 | traité par D20 (règle dans `CLAUDE.md` / `AGENTS.md`) | 🟢 |
| Test dans le compte claude.ai | non fait | — | 🟡 après import (R21) |

## Reste ouvert

| # | Point | Qui |
|---|---|---|
| R18 | `POUR_SKILLS_ZETA_grill_me_20261122.md` + SHA-256 des copies de `~/outils/skills_tiers/` | Claude Code (TELANDROID) |
| R19 | Import de `riemann-wireguard-diagnostic`, `grilling`, `grill-me` dans le compte, puis comparaison SHA-256 | prompt d'adoption + hprzeta |
| R20 | Comptes « 12 skills » : section 8 des instructions (texte fourni), ETAT du dépôt (prompt) | hprzeta + prompt |
| R21 | Compte claude.ai : `disable-model-invocation`, renvoi vers `grilling`, sous-agents | test après import |
| R23 | Signaler à SITE ZETA la portée de D52 (`docs/` seulement ; les skills suivent D1/D19) | hprzeta |
| R24 | Modèle `PROMPT_INSTALL_SKILL_MODELE.md` v3.2 (exception D17) à copier aussi dans `src/ia/prompts/` | prompt d'adoption, étape 0 |
| R9 | Comparaison SHA-256 dépôt / compte (15 skills) | prompt d'adoption, étape 8 |
| R12 | `riemann-lab` §8 : noms de fichiers de `references/` | hprzeta |

Fermés le 22/11 : R17 (test `/grill-me`), R22 (numérotation TEL- acceptée).

## Décisions

D1 à D9 et D11 : inchangées (voir `ETAT_SKILLS_ZETA_20261114.md`). D10 (SKILLS ZETA) : toujours proposée.

| # | Décision (22/11/2026, hprzeta) |
|---|---|
| D17 | Les skills tiers gardent leur nom d'origine, avec `LICENSE` et `SOURCE.md` dans leur dossier (exception écrite à D11). Appliqué à `grill-me` et `grilling`. |
| D18 | Pas de nombre de skills sur le site. |
| D19 | Les skills, tiers compris, vont sur les 4 branches (comme D1). La règle D52 de SITE ZETA (« 4 branches » limité à `docs/`) ne vise que `docs/`. |
| D20 | Les copies tierces restent identiques à l'amont ; l'adaptation au projet passe par `CLAUDE.md` / `AGENTS.md` : « toute réponse recommandée chiffrée est marquée *non vérifiée* ». |
| D21 | Les décisions reçues de ZETA-TELANDROID sont notées TEL-Dn dans ce projet. |

Reçues de ZETA-TELANDROID :

| # | Décision |
|---|---|
| TEL-D10 | Aucun skill ni plugin tiers sans audit de sécurité et essai en bac à sable |
| TEL-D12 | Écartés pour l'instant : claude-mem, Headroom, caveman, MathModelAgent, dépôt « armée d'agents » |
| TEL-D13 | Le suivi des skills revient à SKILLS ZETA |
| TEL-D15 | `grill-me` audité et testé (22/11, Claude Code) : concluant ; adopter, en copiant `grilling` avec |
| TEL-D16 | codeburn : isolé dans `~/outils/codeburn/`, `report` hors ligne seulement |

À voir plus tard (🟡) : find-skills, claude-hud, Graphify, last30days, agent-vault (voir `IDEES_POUR_SKILLS.md`).

---
<sub>ETAT_SKILLS_ZETA_20261122.md · projet SKILLS ZETA · hprzeta · Mis à jour le 2026-11-22 · 79 lignes</sub>
