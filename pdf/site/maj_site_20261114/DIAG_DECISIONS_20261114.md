# Décisions à prendre — formules non rendues du wiki et points 🟡 Y1 à Y3 (14/11/2026)

> Lecture seule : aucune modification du wiki, aucun commit. Sources relues : `DIAGNOSTIC_FORMULES_WIKI_20261114.md` (sortie de `verif_formules_wiki.js`, session de la nuit 13-14/11), `RAPPORT_CORRECTION_FORMULES_20261114.md`, `RAPPORT_SESSION_20261114_0015.md`, `HANDOFF_SITE_20261114.md`. Rien n'a été déduit : ce qui n'est pas écrit dans ces fichiers est noté « introuvable ».

## 0. Écart de comptage à connaître

Les rapports parlent de « 10 pages nouvelles ». Le tableau du diagnostic (§2) a bien 10 lignes, mais la première, `Formation-Zeta-HR` (l'index), a été **corrigée** par le commit `c81894c`. Il reste donc **9 pages non corrigées**, pas 10. Contrôle des zones : 24 + 5 + 1 + 8 + 2 + 4 + 1 + 3 + 1 = 49, plus 1 pour l'index = 50 zones brutes, ce qui correspond au diagnostic.

## 1. Pages non corrigées (9)

Le diagnostic ne conserve ni le numéro de ligne ni l'extrait exact des zones : la sortie du détecteur (`window.__vf`) n'a pas été enregistrée. La colonne « extrait » reprend uniquement ce que le diagnostic cite, sous l'étiquette « constat probable, non vérifié ligne à ligne ».

| page | nb zones | ligne | extrait LaTeX | anomalie |
|---|---|---|---|---|
| analyse_problemes_v1_v16 | 24 | introuvable | introuvable | Paragraphes entiers non rendus (« formule cassée entraînant les voisines »). Cause : « à voir sur la source ». |
| JOURNAL | 8 | introuvable | `/$…$` ; `–$0{,}08$` | Formules collées à un caractère voisin (cause C). |
| analyse_problemes_v4_1_v5 | 5 | introuvable | `1/$\sqrt{t}$` | Formule collée à `/` (cause C). |
| Tableau-Symboles-Mathematiques | 4 | introuvable | `\sum_{d` (coupé) | Barre `\|` dans un tableau (cause D « probable »). |
| knowledge_base_obj2 | 3 | introuvable | `O(t^{-1/4})` ; `10^{13}` | Texte brut sans `$`. Corriger ? « probablement non ». |
| STACK | 2 | introuvable | introuvable | « à examiner » : aucune anomalie décrite. |
| analyse_math_deficit_2026-08-18 | 1 | introuvable | `$T{=}5$M` | Formule collée à la lettre M. |
| analyse_problemes_v8_v9 | 1 | introuvable | `O(t^{-3/4})` | Texte brut sans `$`. Corriger ? « probablement non ». |
| Katex-cheatsheet | 1 | introuvable | citation de `\text` | Citation dans une phrase d'une page de documentation KaTeX. Corriger ? « non ». |

Les causes A à D renvoient à une légende qui n'est pas dans les fichiers relus, sauf B (`^*`), C (parenthèse) et A (italique), cités dans le §1 du diagnostic. La cause D n'est pas définie : **introuvable**.

Limites écrites dans le diagnostic : le balayage lit le HTML du serveur et ne voit pas les erreurs de rendu côté navigateur ; les faux positifs « texte brut » (`^{`) sont possibles hors des 9 pages déjà corrigées. Le détecteur est « réécrit, non validé » (l'original est introuvable).

## 2. Points 🟡 Y1 à Y3

Les trois points sont cités une seule fois, par leur nom, dans `HANDOFF_SITE_20261114.md` (« `Methode`, `niveau-0-prerequis`, `animation_prec_mpfr.html` sur « go 🟡 » ») et dans le rapport de correction (« non lancés, pas de « go 🟡 » »). Leur description n'a été écrite dans aucun des fichiers relus, ni dans l'archive de session du 14/11 ni dans le Handoff.

| Point | Cible citée | Problème | Preuve | Correction envisagée |
|---|---|---|---|---|
| Y1 | `Methode` | introuvable | introuvable | introuvable |
| Y2 | `niveau-0-prerequis` | introuvable | introuvable | introuvable |
| Y3 | `animation_prec_mpfr.html` | introuvable | introuvable | introuvable |

Seule trace en dehors de ces documents : `animation_prec_mpfr.html` apparaît dans les CSV de l'audit des liens du 12/11 (`pdf/site/maj_site_20261112/audit/`), sans rapport établi avec Y3. Je ne l'ai pas exploité.

## 3. Pour avancer

- **Y1 à Y3 :** la description d'origine (probablement dans la session de la nuit, non archivée en détail) est à fournir ou à retrouver. Sans elle, « go 🟡 » ne peut pas être préparé honnêtement.
- **Les 9 pages :** pour remplir « ligne » et « extrait », il faut relancer `verif_formules_wiki.js` page par page en enregistrant le résultat. Cette mesure demande Claude in Chrome et n'a pas été faite ici (lecture seule des fichiers locaux).

---
*DIAG_DECISIONS_20261114.md · projet SITE ZETA · hprzeta · mis à jour le 14 novembre 2026 · 47 lignes*
