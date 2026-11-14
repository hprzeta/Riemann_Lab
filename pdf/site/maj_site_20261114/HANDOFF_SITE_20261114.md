# HANDOFF site — 14/11/2026

**Fait et publié (sans `--force`) :** wiki `382c030` (20 formules + titre Ch05, 9 pages + index) et `c81894c` (index, titre du chapitre 5 sans formule dans le lien). Vérifié en ligne : 0 zone rouge, liens et console OK.
**Commité et poussé (`6f85a26`, `Riemann_Lab_IA`) :** détecteur `verif_formules_wiki.js`, diagnostic, rapports, captures (49 fichiers). Restent locaux : `.bak*`, `A_DEPOSER/` (exclus).
**Prochaine action (à décider par hprzeta) :** 1) déposer A_DEPOSER/ dans le projet SITE ZETA ; 2) nouvel essai forcé (règle 10) ; 3) PermitRootLogin no sur PC2 (optionnel) ; 4) valider le détecteur (faux positifs, `=` → EGAL) ; 5) commit + sync de CLAUDE.md (règle heredoc).


## Test automatique V2 (14/11/2026 13:35)
**Fait (local, 0 commit) :** les contrôles de liens, de nombre de lignes, de secrets et de formules sont faits par `~/.local/bin/zeta_test_controles.sh` avant l'appel à Claude ; Claude n'a plus Bash (`zeta_test_maj_site.sh`, `ZETA_FORCE=1`, `ZETA_DEPUIS=<ts>` pour les essais) ; règles 9 et 10 ajoutées au prompt du test. Essai forcé : rapport non partiel sur les contrôles, 0 « Bash a été refusé », 0 valeur identifiante, état du vrai test inchangé. Rapport : `RAPPORT_TEST_AUTO_V2_20261114_1335.md` / `.pdf`.
**Reste (à décider par hprzeta) :** nouvel essai forcé pour éprouver la règle 10 (titre sans heure, WebFetch pour le site en ligne) ; retrait de la note `[[ ]]` de `Optimisation-Pourquoi-le-calcul-va-vite.md` (l. 185-189) **FAIT (`81b0311`)** ; relecture de `PasswordAuthentication yes` (`Architecture-Cluster-Zeta.md:200`) **FAIT (`5da032d`, note « Provisoire »)** ; les formules `\|…\|` de `Formules_zeta.md` : **clos, rendues sans défaut (mesuré en ligne le 14/11, aucun commit)**.


## Correction des formules du 14/11 (après-midi, 14:00)
**Fait et publié (sans `--force`) :** wiki `81b0311` (6 pages + note `[[ ]]` retirée d'Optimisation) et `1b608b2` (JOURNAL : ligne vide avant le bloc `$$`, cause confirmée). Contrôle en ligne : 0 zone rouge sur `analyse_problemes_v1_v16`, `Tableau-Symboles-Mathematiques`, `analyse_math_deficit_2026-08-18`, `Optimisation-Pourquoi-le-calcul-va-vite` ; `.katex-error` 0 partout. **Pages à traiter : 9 → 0 (JOURNAL 2776/4090 clos par décision) + 3 exclues** (`knowledge_base_obj2`, `analyse_problemes_v8_v9`, `Katex-cheatsheet`).
**Y1 à Y3 : clos, aucun défaut mesuré** (`Methode`, `niveau-0-prerequis`, `animation_prec_mpfr.html` : 0 `.katex-error`, liens OK) ; description d'origine introuvable.
**Fait et publié (sans `--force`) :** wiki `85daa59` (v4_1_v5 ligne 197 avec `\mathrm{STEP} = 0.22`, pied de page de `niveau-0-prerequis`, date du pied de `Methode`, règle KaTeX n°5 dans `STACK`). Contrôle en ligne : `analyse_problemes_v4_1_v5` 0 zone rouge (75 rendues), `niveau-0-prerequis` 0 (80 rendues, pied affiché), `STACK` 1 zone (ligne 693, faux positif) ; `.katex-error` 0 et console sans erreur sur les trois.
**JOURNAL 3199 : fait (`1b608b2`).** **Clos par décision (laissés tels quels) :** `JOURNAL` 2776 et 4090-4091 (textes bruts), `knowledge_base_obj2`, `analyse_problemes_v8_v9`, `Katex-cheatsheet`. **STACK 693 : corrigé (`5da032d`).**
**Reste :** rien sur les formules du wiki. Rapport : `RAPPORT_CORRECTION_WIKI_20261114_1400.md`.


## PasswordAuthentication et STACK (14/11, 14:25)
**Fait et publié (sans `--force`) :** wiki `5da032d`. `Architecture-Cluster-Zeta` : note « Provisoire : passer à `PasswordAuthentication no`… » après le bloc de dépannage (ligne 203), visible en ligne, console sans erreur. `STACK` : symboles `$$` et `$` de la note du 12/09 mis en code (ligne 695, ex-693) : **0 zone rouge, 26 formules rendues, `.katex-error` 0** : STACK 693 est fait.
**État réel de PC4 (lecture seule, aucune modification) : 🟢.** Fichier `sshd_config` : `PermitRootLogin no`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `AllowUsers` limité à l'utilisateur d'administration. Comportement mesuré : seule la clé publique est acceptée. `sshd -T` n'a pas pu être lu (droits root requis, `doas` demande un mot de passe).
**Reste :** voir la section suivante (PC2 mesuré, 🟢). Rapport : `RAPPORT_SSH_STACK_20261114.md`.


## PC2 et Formules_zeta (14/11, 14:28)
**État réel de PC2 (lecture seule, aucune modification) : 🟢.** `sshd_config.d/10-zeta-keyonly.conf` : `PasswordAuthentication no` ; `KbdInteractiveAuthentication no` ; `PermitRootLogin` et `PubkeyAuthentication` non définis (défauts). Comportement mesuré : seule la clé publique est acceptée. `sshd -T` non lu (hors du chemin, droits root requis). Le diagnostic publié du 03/10 est confirmé.
**Formules_zeta lignes 707, 748, 1591 : clos, aucun commit.** Sur la page publiée : 630 formules rendues, 0 non rendue, `.katex-error` 0, console sans erreur ; les trois formules (blocs `$$`, barres `|` non protégées) s'affichent correctement (captures `captures/formules_zeta_l707_apres.jpg`, `l748`, `l1591`). Le détecteur les signalait à tort.
**Reste :** PC2 : `PermitRootLogin` non défini = `prohibit-password` (root par clé possible) ; aligner sur PC4 (`no`) — décision hprzeta. Rien d'autre sur les formules du wiki ni sur SSH (PC2 et PC4 en clé seule). Rapport : `RAPPORT_PC2_FORMULES_20261114.md`.

---
*Mis à jour le 2026-11-14 (lignes 4-5 : état du dépôt et prochaine action) — 33 lignes*
