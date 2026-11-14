# PROMPT de correction — suite du test du 11/11/2026 (2049)

> À charger dans Claude Code. Règles : copie `.bak-AAAAMMJJ` avant toute modification ; aucun `git add` / commit / push sans « go » de hprzeta ; wiki = dépôt séparé (`~/projet_zeta/Riemann_Lab.wiki`, branche master) ; masquer toute valeur identifiante par un marqueur.

## Corrections proposées (une par une, après validation)

1. **`JOURNAL.md` (wiki) ligne 3446** — masquer l'adresse lien-local `fe80::…` (dérivée d'une MAC, EUI-64) par `fe80::[ID_lien_local]`. Contrôle : `grep -n 'fe80::[0-9a-f]\{1,4\}:' Riemann_Lab.wiki/JOURNAL.md` ne renvoie plus rien. Rappel : l'adresse reste dans l'historique git du wiki (réécriture = décision de hprzeta).
2. **`Animations.md` (wiki) ligne 25** — colonne « Cours associé » de `prec_mpfr` : « — » → `[[niveau-4-zeta]]` (proposition, comme `illinois_adaptatif` et `ntermes_rs`). **À valider par hprzeta.** Mettre à jour la date et le compteur de lignes du pied.
3. **`STACK.md` (wiki) ligne 344** — « 8 animations HTML » → « 12 animations HTML » (périmé depuis les 4 nouvelles animations). Mettre à jour le pied.
4. *(mineur)* **`Arbre_dossiers_projet.md` (wiki)** — ajouter le compteur de lignes réel au pied (168 lignes à ce jour).

## Décision de hprzeta (pas un correctif)

- `analyse_math_deficit_2026-08-18.pdf` : non suivi par git (copie locale dans `pdf/optimisation/Voie_b_5/md_to_claude/`). Le publier (branche `Riemann_Lab_IA`, convention `pdf/<sujet>/`) ou le laisser local ?

## Contrôles après correction

`git -C Riemann_Lab.wiki diff --stat` (lecture), `grep` des lignes modifiées, puis ouverture de la page dans Claude in Chrome pour que hprzeta voie le changement.

---
*PROMPT_CORRECTION_MAJ_SITE_20261111_2049.md · hprzeta · 2026-11-11 20:49 · 21 lignes*
