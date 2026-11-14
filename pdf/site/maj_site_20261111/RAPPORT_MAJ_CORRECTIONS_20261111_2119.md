# Rapport — corrections du wiki après le test du 11/11/2026 (21h)

> Réalisé le 11/11/2026 à 21:19 par Claude Code d'après `PROMPT_MAJ_CORRECTIONS_SITE_20261111_2100.md`. 4 corrections commitées une par une après « go » (e54bca3, 52bedf3, 5d343a7, f637580), puis un seul push du wiki, sans `--force`. Aucune modification du dépôt de code, du site ni des 3 autres branches. Statut : 🟢 ok · 🟡 fait à moitié · 🔴 pas fait ou ko.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| C1 JOURNAL.md l.3446 : fe80:: masquée | 🟢 | git diff -U0 : 1 ligne, fe80::[ID_lien_local] ; grep fe80::<hex>: sur tout le wiki = 0 ; vu sur le wiki public (zone encadrée, capture) ; commit e54bca3. Historique non réécrit (décision) | L'ancienne valeur reste dans l'historique git du wiki (décidé) et dans JOURNAL.md.bak5-20261111 (local, non suivi) |
| C2 Animations.md l.25 : prec_mpfr → [[niveau-4-zeta]] | 🟢 | Vu sur le wiki public (ligne encadrée en vert) ; clic sur le lien : ouvre « Niveau 4 — La fonction zêta en profondeur » ; pied : 11 novembre 2026, 217 lignes (= wc -l) ; commit 52bedf3 | — |
| C3 STACK.md l.344 : annotée, non réécrite | 🟢 | Texte public lu : « 8 animations HTML à l'époque (juin 2026 ; 12 depuis le 11/11/2026) … les 8 premières validées Playwright ✅ » (capture) ; pied 2026-11-11, 706 lignes ; commit 5d343a7 | — |
| C4 Arbre_dossiers_projet.md : compteur au pied | 🟢 | Pied public : « … · 168 lignes » (capture) ; wc -l = 168 ; commit f637580 | — |
| Push du wiki | 🟢 | git push origin master : c53eb42..f637580, sans --force, après audit des 5 lignes ajoutées (RAS) | — |
| Occurrences « 8 animations », « fe80:: » | 🟢 | « 8 animations » : 2 restantes, toutes historiques (STACK.md:344 annotée ; JOURNAL.md:59 déclarée « justifiée »). fe80:: : mentions pédagogiques seulement ; 0 valeur hexadécimale | — |
| Copies des 4 fichiers hors wiki | 🟢 | find sur ~/projet_zeta, ~/riemann_handoff, ~/zeta_inventaire, /mnt/data : une seule copie de chaque (le wiki, suivi, identique). Rien dans md/, pdf/vault/, .claude/skills/ | — |
| E4-1 Montrer à l'écran | 🟢 | Onglet « Mise à jour site » : Animations, STACK, Arbre_dossiers_projet, JOURNAL (zone masquée) vus après push, lignes encadrées, 5 captures | — |
| E4-2 Console + réseau avant chaque chargement | 🟡 | Suivi actif avant chaque chargement. Console : 0 message (Animations, niveau-4-zeta, STACK, Arbre, JOURNAL, 4 animations, site). Réseau : github.com/wiki : toutes 200/204 (Animations, STACK, Arbre) ; 4 animations et site : 0 requête ≥ 400 (outil réseau pour gaps_gue et illinois ; Performance API pour ntermes_rs, prec_mpfr et le site) | Réseau de JOURNAL non relu après chargement (page de 273 Ko, 0 erreur de console) |
| E4-3 Liens : un clic par section + curl | 🟡 | Clics réels : en-tête (dépôt GitHub), Formation chapitre 1, carte Wiki du projet, LMFDB du pied : tous s'ouvrent. curl -L : 59 liens uniques, 59 × HTTP 200 (la page en ligne en compte 59) | Lien CSV de la section « vs LMFDB » non cliqué (risque de téléchargement sans accord) : testé en curl seulement |
| E4-4 Formules KaTeX | 🟢 | 0 .katex-error : site (53 .katex), 4 animations (11/21/7/8), pages wiki touchées et niveau-4-zeta. STACK : 6 occurrences de « $$ » = texte qui documente les règles KaTeX (faux positifs) | — |
| E4-5 analyse_problemes_v1_v16.pdf (main) | 🟢 | Ouvert dans Chrome (viewer GitHub, 141 Ko) : la note du 11/11/2026 est en page 1 (capture) | — |
| E4-6 IPv4 de T10Demo (JS minifié, 4,8 Mo) | 🟢 | 29 motifs distincts : 25 hors plage IPv4 (octet > 255) ; 4 noyés dans des tracés SVG (syntaxe c/q/a) = coordonnées. Aucune adresse réelle | Classement par contexte, valeurs non affichées |
| E4-7 Audit secrets (wiki + docs/, 135 fichiers texte) | 🟢 | E-mails ≠ adresse projet : 0 · duckdns sous-domaine personnel : 0 · ghp_ / github_pat_ / token= / passw= avec valeur : 0 · « PRIVATE KEY » : 1 mention (JOURNAL.md:905, « rien trouvé ») · MAC : 0 · IPv4 à examiner : 0 · IPv6 : seulement des DNS publics (Cloudflare, Google) · fe80:: : 0 | — |
| Hors liste : Dossier-md.md non suivi dans le wiki | 🟡 | git status du wiki : « ?? Dossier-md.md », absent du premier état de la session ; pas créé par ce travail, non touché, non poussé | À identifier par hprzeta (garder, commiter ou supprimer) |

## 2. Tableau de modifications (`git diff -U0 c53eb42..f637580`, wiki)

Ajouts en vert, suppressions en rouge dans le PDF.

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| Animations.md (wiki) | [L25] / [Précision mpfr & limbs](#-animation_prec_mpfr--précision-mpfr--limbs--le-vrai-levier-v7) / Précision binaire, limbs, SIMD / [[niveau-4-zeta]] / | [L25] / [Précision mpfr & limbs](#-animation_prec_mpfr--précision-mpfr--limbs--le-vrai-levier-v7) / Précision binaire, limbs, SIMD / — / | 2026-11-11 21:11 |
| Animations.md (wiki) | [L217] *Animations.md · wiki racine · branche master · hprzeta · MAJ 11 novembre 2026 (4 animations ajoutées ; cours associé de prec_mpfr) · 6 juin 2026 : version initiale · 217 lignes* | [L217] *Animations.md · wiki racine · branche master · hprzeta · MAJ 11 novembre 2026 (4 animations ajoutées) · 6 juin 2026 : version initiale · 217 lignes* | 2026-11-11 21:11 |
| Arbre_dossiers_projet.md (wiki) | [L168] *Arbre_dossiers_projet.md · wiki master · hprzeta · MAJ 10 juin 2026 · 11 novembre 2026 (v4_1 marqué historique) · 168 lignes* | [L168] *Arbre_dossiers_projet.md · wiki master · hprzeta · MAJ 10 juin 2026 · 11 novembre 2026 (v4_1 marqué historique)* | 2026-11-11 21:13 |
| JOURNAL.md (wiki) | [L3446]      obtenue (`fe80::[ID_lien_local]`), mais toujours pas d'adresse | [L3446]      obtenue (`fe80::[VALEUR_RETIRÉE]`), mais toujours pas d'adresse | 2026-11-11 21:10 |
| STACK.md (wiki) | [L344] - [x] Visualisations dans `/docs` — 8 animations HTML à l'époque (juin 2026 ; 12 depuis le 11/11/2026) + index.html, les 8 premières validées Playwright ✅ | [L344] - [x] Visualisations dans `/docs` — 8 animations HTML + index.html, validées Playwright ✅ | 2026-11-11 21:12 |

## 3. Erreurs rencontrées

- Aucune erreur sur les 4 corrections ni sur le push.
- Lien CSV (section « vs LMFDB ») non cliqué volontairement : un clic pourrait télécharger un fichier ; 200 en curl.
- Chrome traduit automatiquement les pages wiki (« membres » pour « limbs ») : sans effet sur le dépôt.
- Sauvegardes locales JOURNAL.md.bak5-20261111 et suivantes : non suivies par git, jamais dans le push ; JOURNAL.md.bak5 contient l'ancienne valeur : à garder local.
- Aucun correctif additionnel nécessaire : pas de prompt de correction supplémentaire.

Captures (nouveaux fichiers) : `captures/corr_wiki_animations_prec_mpfr_apres.jpg`, `captures/corr_wiki_stack_ligne344_apres.jpg`, `captures/corr_wiki_arbre_pied_168_apres.jpg`, `captures/corr_wiki_journal_l3446_masquee_apres.jpg`, `captures/corr_pdf_main_analyse_v1_v16_page1.jpg`.

Aucune valeur identifiante dans ce rapport ([IP], [MAC], [EMAIL], fe80::[ID_lien_local]).

---
*RAPPORT_MAJ_CORRECTIONS_20261111_2119.md · projet SITE ZETA · hprzeta · MAJ 11 novembre 2026 21:19 · 50 lignes*
