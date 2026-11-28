---
name: zeta-token-hygiene
description: "Réduire la consommation de tokens et le coût d'une session Claude Code du projet Riemann_Lab sans perdre en qualité. Utiliser quand la session devient trop longue, lente ou coûteuse, quand le contexte approche d'un seuil de CLAUDE.md, avant un compactage, pour préparer un fichier de passation, pour choisir entre lecture partielle et lecture complète d'un fichier, ou pour mesurer la dépense (/cost). Déclencher sur : trop de tokens, contexte plein, session trop longue, coûte cher, cache de prompt, compactage, passation. Ne pas utiliser pour les calculs de zéros, la théorie ou le debug."
---

# zeta-token-hygiene

Version : 1.0 · MAJ : 2026-11-28

Réduire la dépense de tokens **sans inventer de seuil** : les seuils de contexte sont ceux de
`~/projet_zeta/CLAUDE.md` (section « Gestion autonome du contexte »), repris tels quels ci-dessous.
En cas de doute ou de changement, relire ce fichier : il fait foi.

## 1. Seuils (copie de CLAUDE.md, à relire à la source)

| Seuil | Action prévue par CLAUDE.md |
|---|---|
| 50 % | commit de checkpoint (`wip: checkpoint auto`) — seulement avec l'accord de hprzeta (règle « aucun git add/commit sans validation ») |
| 70 % | push + `docs/session_checkpoint_AAAAMMJJ.md` — idem, sur « go » |
| 80 % | arrêt : plus de nouvelle tâche |
| « 11 % until auto-compact » | STOP immédiat, rapport court |

Conflit apparent : CLAUDE.md demande des commits automatiques, la règle globale exige une validation.
**Ne jamais committer sans « go »** : proposer, attendre.

## 2. Hygiène du cache de prompt

- Le cache porte sur le **préfixe** de la conversation : tout ce qui est stable (CLAUDE.md, skills, outils) doit rester en tête et inchangé.
- Ne pas modifier `CLAUDE.md` ni la liste des skills en cours de session : cela invalide le cache et recoûte tout le préfixe.
- Un cache périmé (pause longue) coûte plus cher à la reprise qu'une session courte : préférer plusieurs petites sessions (déjà prévu par CLAUDE.md pour les runs).

## 3. Lire moins

- Fichier connu : lire une **plage** (`offset`/`limit`), pas le fichier entier. Chercher d'abord (`grep -n`), lire ensuite.
- Journaux et sorties de run : `tail -n`, `grep` ciblé, jamais le fichier complet.
- Ne pas relire un fichier qu'on vient d'écrire ou d'éditer.
- Digest de dépôt : borné (arborescence 2 niveaux, `wc -l`), jamais un `cat` global.
- Un sous-agent isole une exploration large ; seul son résumé revient dans le contexte.

## 4. Passation avant saturation

Avant d'atteindre 70 % : écrire un `.md` court (état, décisions, prochaine action réelle, fichiers touchés),
dans le fichier de passation du projet (`Handoff.md`) ou le dossier de la tâche, avec pied de page
date + nombre de lignes. Ensuite seulement, repartir d'une session neuve. Ne rien recopier dans CLAUDE.md.

## 5. Mesurer

- Claude Code : `/cost` (dépense de la session), `/context` si disponible.
- claude.ai : skill `explain-usage` s'il est présent dans le compte.
- Mesurer avant et après un changement d'habitude ; ne pas annoncer de gain sans mesure
  (règle D20 : tout chiffre non vérifié porte « non vérifiée »).

## 6. Prompts courts et ciblés

Un objectif, un livrable, un critère d'arrêt. Citer les chemins plutôt que décrire. Demander
« montre seulement le diff » ou « les 20 premières lignes » quand cela suffit.

## 7. Outils tiers : candidats « à auditer » uniquement

cache-audit, codeburn, claude-hud, claude-tap, Headroom. **Aucune installation** : passer d'abord
par le skill `skill-install-audit`. (Statuts antérieurs : codeburn isolé dans `~/outils/codeburn/`,
rapport hors ligne seulement ; Headroom écarté pour l'instant — voir `ETAT_SKILLS_ZETA.md`.)

## Ce que ce skill ne fait pas

Il ne touche ni aux calculs, ni aux fichiers de zéros, ni à la configuration. Il conseille ; hprzeta décide.
