# PROMPT Claude Code — Wiki `STACK` : retirer le lien mort du livre de Titchmarsh (D25)

> Préparé sur claude.ai (projet SITE ZETA) le 12/11/2026 à 19:45, d'après `RAPPORT_AUDIT_COMPLET_20261112_1921.md` §2.1 et §8. Rapport d'analyse : `RAPPORT_ANALYSE_WIKI_STACK_TITCHMARSH_20261112_1945.md`.
> **Wiki uniquement.** Le site n'est pas touché.

## Décisions de hprzeta
- **D25** : `STACK.md` l. 474 : garder la référence du livre de Titchmarsh, **retirer le lien archive.org mort** (404), préciser l'édition.
- Les 2 liens DOI (l. 472 et 473) **marchent** dans le Chrome de hprzeta : **ne pas y toucher**.
- Rien d'autre : README, symboles de `Animations`, pages à accents et code Plotly restent tels quels (D23, D24, choix du 12/11).

## Règles
STOP : « go commit wiki », « go push wiki ». Jamais `--force`. Copie `pdf/archive/STACK.md.bak-<AAAAMMJJHHMM>` avant modification. Aucune valeur identifiante. Claude in Chrome, onglet « Mise à jour site ».

## Étape 0 — Ranger le prompt
```bash
cd /home/riemann/projet_zeta/src/ia/prompts
unzip -n ~/Téléchargements/WIKI_STACK_TITCHMARSH_20261112_1945.zip
D=/home/riemann/projet_zeta/pdf/site/maj_site_$(date +%Y%m%d); mkdir -p "$D/captures" "$D/A_DEPOSER"
cp -p RAPPORT_ANALYSE_WIKI_STACK_TITCHMARSH_20261112_1945.* PROMPT_WIKI_STACK_TITCHMARSH_20261112_1945.md "$D/"
```

## Étape 1 — État AVANT et diagnostic (lecture seule)
```bash
W=/home/riemann/projet_zeta/Riemann_Lab.wiki
git -C $W status --short; git -C $W pull --ff-only
sed -n '468,478p' $W/STACK.md; tail -1 $W/STACK.md; wc -l $W/STACK.md
grep -rn 'theoryofriemann00titc' $W/*.md /home/riemann/projet_zeta/docs /home/riemann/projet_zeta/README.md
```
Chrome : page wiki `STACK`, faire défiler jusqu'aux références, encadrer en rouge la ligne du livre de Titchmarsh. Capture `captures/d25_avant_stack.jpg`.
**STOP et décrire l'écart** si la ligne 474 ne contient pas le lien `archive.org/details/theoryofriemann00titc`, ou si ce lien apparaît ailleurs.

## Étape 2 — Correctif
Sur la ligne de Titchmarsh seulement, retirer le lien et garder une référence complète, dans le style des lignes voisines, par exemple :
`E. C. Titchmarsh, *The Theory of the Riemann Zeta-Function*, 2ᵉ éd. révisée par D. R. Heath-Brown, Oxford University Press, 1986.`
Ne pas inventer d'autre information (pas d'ISBN, pas de nouveau lien). Pied de page : ajouter `· <JJ> novembre 2026 (lien mort de Titchmarsh retiré)` et `wc -l` exact.
`git -C $W diff` ; audit des lignes ajoutées. **STOP — « go commit wiki ».** Message : `docs(STACK): référence Titchmarsh sans lien mort (D25)`. **STOP — « go push wiki »**.

## Étape 3 — État APRÈS
Chrome : page `STACK` rechargée, ligne encadrée en vert, pied de page visible. Capture `captures/d25_apres_stack.jpg`. Re-tester les liens de `STACK.md` (`curl -sIL`, 1 requête par seconde) : 0 lien 🔴 hors DOI bloqués pour les robots (confirmés par hprzeta). 0 erreur de formule sur la page.

## Étape 4 — Rapport
`RAPPORT_WIKI_STACK_TITCHMARSH_<AAAAMMJJ>_<HHMM>.md` + `.pdf` (tableau de validation, tableau `page | ligne in | ligne out | date heure`, in en vert et out en rouge dans le PDF). Compléter `HANDOFF_SITE_<AAAAMMJJ>.md`. Copier uniquement les `.md` dans `A_DEPOSER/`.

Terminer par : **« hprzeta, donne le .md à claude.ai, projet SITE ZETA : il le range lui-même. »**

---
*PROMPT_WIKI_STACK_TITCHMARSH_20261112_1945.md · projet SITE ZETA · hprzeta · MAJ 12 novembre 2026 19:45 · 47 lignes*
