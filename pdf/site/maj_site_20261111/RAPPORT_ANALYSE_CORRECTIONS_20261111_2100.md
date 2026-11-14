# Rapport d'analyse — corrections après le test du 11/11/2026 (2e passe)

> Généré le 2026-11-11 21:00 depuis le projet SITE ZETA (claude.ai) · analyse en lecture seule, **aucune modification faite par cette analyse**.
> Sources : `RAPPORT_TEST_MAJ_SITE_20261111_2049.md`, `PROMPT_CORRECTION_MAJ_SITE_20261111_2049.md`, wiki `master` (`c53eb42`).

## 1. Verdict sur le prompt de correction de Claude Code

**Gardé :** ses 4 corrections (précises, avec contrôle par `grep`). **Remplacé par un prompt complet**, parce qu'il manquait ce que demande le projet SITE ZETA : étape 1 « ouvrir Claude in Chrome » (onglet « Mise à jour site »), montrer chaque modification de façon interactive, dossier du jour, rapport md + PDF vert/rouge, contrôle des copies et occurrences, liens et formules, date en pied de page, rappel de dépôt dans le projet. **Corrigé :** la correction n° 3 (voir décisions).

## 2. Décisions prises (réversibles)

| Sujet | Décision | Raison |
|---|---|---|
| Cours associé de `prec_mpfr` | `[[niveau-4-zeta]]` | Même famille que `illinois_adaptatif` et `ntermes_rs` (affinage Illinois, précision mpfr, Riemann-Siegel). Réversible. |
| `STACK.md` ligne 344 (« 8 animations ») | **Annoter**, ne pas réécrire | C'est une case cochée historique de juin 2026 (8 animations validées Playwright). La réécrire en « 12 » ferait croire que les 12 ont été validées Playwright. Le prompt de Claude Code proposait de la réécrire. |
| `analyse_math_deficit_2026-08-18.pdf` | **Ne pas publier maintenant** | Ce PDF local décrit l'analyse du 18/08 ; depuis, 96 → 97 manquants et la cause a été mesurée (84 paires + 13 isolés). Le publier tel quel mettrait un contenu périmé en public. Si tu le veux en ligne : le régénérer depuis le `.md` du wiki (qui porte la note du 11/11), puis le ranger dans `pdf/optimisation/`. Réversible. |
| Réécriture de l'historique git du wiki (`fe80::…`) | **Non** | Valeur probablement issue de l'ancienne carte réseau de PC4 (entrée de juin, avant la migration matériel du 16/08) ; risque faible. On masque la ligne actuelle, sans toucher à l'historique. Réversible : à reconsidérer si tu préfères. |
| Corrections hors wiki | Aucune | Les 4 corrections sont toutes dans le wiki (`master`) : pas de commit sur le dépôt, pas de cherry-pick sur les 4 branches, pas de PDF à régénérer. |

## 3. Tableau des modifications à faire

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| JOURNAL.md (wiki) l.3446 — masquer l'adresse lien-local (dérivée d'une MAC) |      obtenue (`fe80::[ID_lien_local]`), mais toujours pas d'adresse |      obtenue (`fe80::[valeur masquée dans ce rapport]`), mais toujours pas d'adresse | À FAIRE |
| Animations.md (wiki) l.25 — cours associé de prec_mpfr | \| [Précision mpfr & limbs](#-animation_prec_mpfr--…) \| Précision binaire, limbs, SIMD \| [[niveau-4-zeta]] \| | \| [Précision mpfr & limbs](#-animation_prec_mpfr--…) \| Précision binaire, limbs, SIMD \| — \| | À FAIRE |
| STACK.md (wiki) l.344 — ANNOTER (ne pas réécrire) cette case historique de juin | - [x] Visualisations dans `/docs` — 8 animations HTML à l'époque (juin 2026 ; 12 depuis le 11/11/2026) + index.html, les 8 premières validées Playwright ✅ | - [x] Visualisations dans `/docs` — 8 animations HTML + index.html, validées Playwright ✅ | À FAIRE |
| Arbre_dossiers_projet.md (wiki) — pied de page | *Arbre_dossiers_projet.md · wiki master · hprzeta · MAJ 10 juin 2026 · 11 novembre 2026 (v4_1 marqué historique) · 168 lignes* | *Arbre_dossiers_projet.md · wiki master · hprzeta · MAJ 10 juin 2026 · 11 novembre 2026 (v4_1 marqué historique)* | À FAIRE |
| Animations.md, STACK.md, JOURNAL.md (wiki) — pieds de page | date « 11 novembre 2026 » + nombre de lignes exact (`wc -l` après modification) | ancienne date et ancien compteur de lignes | À FAIRE |

## 4. Gaps restants hors correctifs (pour information)

- Vérifier à l'écran `analyse_problemes_v1_v16.pdf` dans Chrome (seul `pdftotext` l'a contrôlé).
- Un clic à la main par section du site (non fait au test).
- Suivi réseau démarré **avant** chaque chargement pour les animations et le wiki (limite d'outil au test).
- Les 84 motifs IPv4 de `docs/images/T10Demo/*.html` (bibliothèque JS minifiée) : classer les correspondances distinctes (faux positifs probables : numéros de version).
- Contrôler les copies locales des 4 fichiers (`md/`, `pdf/vault/`, `.claude/skills/`) : ils n'existent pas dans le dépôt, seulement éventuellement hors git.

---
*RAPPORT_ANALYSE_CORRECTIONS_20261111_2100.md · projet SITE ZETA · hprzeta · MAJ 2026-11-11 · 39 lignes*
