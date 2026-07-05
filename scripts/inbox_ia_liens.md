> **Fichier :** inbox_ia_liens.md · **Dossier :** scripts/
> **Branche :** Riemann_Lab_IA · **Auteur :** hprzeta · **MAJ :** 2026-07-05

# Liens GitHub — branche inbox-ia

Fichiers Markdown disponibles sur la branche `inbox-ia` du dépôt `Riemann_Lab`.
Usage : ingestion RAG BrainVault (Objectif 2 — agent autonome de recherche mathématique).

Généré le : 2026-06-11 · Mis à jour le 2026-07-05 (synchronisation post-bilan `etat_rag_brainvault_20260704.md`)

---

## ⚠️ Règle d'ingestion — code source

`inbox-ia` ne contient **que du Markdown**. Le **code source** (`illinois_arb.c`,
`scan_arb.c`, `compute_zeros_v15.py`, `.claude/skills/`, `docs/index.html`,
`src/ia/prompts/`, scripts `scripts/*.sh`…) n'est **jamais** dupliqué ici : il est
ingéré **directement depuis la branche `Riemann_Lab_C` (raw GitHub)**, chemins
`src/calculs/optimisation/...`. Une seule source de vérité pour le code, pas de
copie à resynchroniser.

---

## Catégories pour le RAG BrainVault

### Analyses techniques (priorité haute — formules + solutions)

- [analyse_problemes_v4_v4_1.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/analyse_problemes_v4_v4_1.md) — Problèmes v4→v4.1 : Z_vect_correct, bottleneck affinage
- [analyse_problemes_v4_1_v5.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/analyse_problemes_v4_1_v5.md) — Problèmes v4.1→v5 : Voie B, arb ×27
- [analyse_problemes_v5_v6.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/analyse_problemes_v5_v6.md) — Problèmes v5→v6 : STEP δ/3 → 2072 manquants, scan_arb
- [analyse_problemes_v4_1_v6_synthese.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/analyse_problemes_v4_1_v6_synthese.md) — Synthèse v4.1→v6 : STEP, N(T) segmentation, résultats 138069
- [analyse_problemes_v6_v7.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/analyse_problemes_v6_v7.md) — Problèmes v6→v7 *(ajouté 05/07)*
- [analyse_problemes_v7_v8.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/analyse_problemes_v7_v8.md) — Problèmes v7→v8 *(rafraîchi 05/07)*
- [analyse_problemes_v8_v9.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/analyse_problemes_v8_v9.md) — Problèmes v8→v9 *(ajouté 05/07)*
- [analyse_problemes_v9_v10.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/analyse_problemes_v9_v10.md) — Problèmes v9→v10 *(ajouté 05/07)*
- [analyse_problemes_v10_v12.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/analyse_problemes_v10_v12.md) — Problèmes v10→v12 *(ajouté 05/07)*
- [analyse_problemes_v13_v15.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/analyse_problemes_v13_v15.md) — Problèmes v13→v15 : cache RS + SEUIL_1NEWTON *(ajouté 05/07)*
- [analyse_problemes_v5_v4_1_20260602.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/analyse_problemes_v5_v4_1_20260602.md) — Variante v5→v4.1 du 02/06 *(ajouté 05/07)*
- [analyse_run_T100000_v4_1.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/analyse_run_T100000_v4_1.md) — Analyse run T=100000 v4.1 *(ajouté 05/07)*

### Maths et algorithmes (priorité haute — raisonnement)

- [Formules_zeta.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Formules_zeta.md) — Formules canoniques : N(T), θ(t), Z(t), Illinois, STEP adaptatif — §1 à §30 *(rafraîchi 05/07 : biais Z_rs + SEUIL_1NEWTON)*
- [Bibliotheques.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Bibliotheques.md) — Stack technique : mpmath, numpy, cupy, libmpfr, runs T=100k — §1 à §17 *(rafraîchi 05/07 : cache RS 33 KB)*
- [maths_v7_ntermes_adaptatif.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/maths_v7_ntermes_adaptatif.md) — Maths v7 : Illinois 2 phases, N_fast, gain ×4.6 théorique

### Plans et architecture

- [plan_v6_riemann.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/plan_v6_riemann.md) — Plan v6 : scan_arb.c, W=8, segmentation N(T)
- [STACK.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/STACK.md) — Branches, matériel, outils, roadmap *(rafraîchi 05/07 : tableau versions, Obj.2 démarré)*
- [Architecture-Cluster-Zeta.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Architecture-Cluster-Zeta.md) — Cluster zeta 3 machines, IPs corrigées .94→.52 *(ajouté 05/07)*
- [Roadmap.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Roadmap.md) — Feuille de route projet *(ajouté 05/07)*
- [Structure-Projet-Complet.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Structure-Projet-Complet.md) — Vue d'ensemble structure *(ajouté 05/07)*
- [Arbre_dossiers_projet.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Arbre_dossiers_projet.md) — Arborescence dossiers *(ajouté 05/07)*
- [Configuration-Materielle-Logicielle.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Configuration-Materielle-Logicielle.md) — Config matériel/logiciel *(ajouté 05/07)*
- [Plancher-Hardware-Architecture.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Plancher-Hardware-Architecture.md) — Plancher hardware *(ajouté 05/07)*
- [Phase-C-compute_zeros_v4.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Phase-C-compute_zeros_v4.md) — Phase C, compute_zeros_v4 *(ajouté 05/07)*
- [Phase-Optimisation-compute_zeros_v3.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Phase-Optimisation-compute_zeros_v3.md) — Phase optimisation v3 *(ajouté 05/07)*
- [Optimisation-Pourquoi-le-calcul-va-vite.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Optimisation-Pourquoi-le-calcul-va-vite.md) — Explication pédagogique des gains *(ajouté 05/07)*
- [MAINTENANCE_2026-06-23.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/MAINTENANCE_2026-06-23.md) — Notes maintenance 23/06 *(ajouté 05/07)*

### Sessions et décisions (contexte décisionnel)

- [recap_session_20260610_11.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/recap_session_20260610_11.md) — Récap sessions 10-11 juin : v6 validée, prompts E→K
- [ia_prompts_riemann_lab_complet.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/ia_prompts_riemann_lab_complet.md) — Tous les prompts Claude Code sessions 1→15, A→L
- [session_20260606.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/session_20260606.md) — Session 06/06 *(ajouté 05/07)*
- [Rapport-Session-27-06-2026.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Rapport-Session-27-06-2026.md) — Run T=5M + P1 fp.siegelz + analyse Obj.2 *(ajouté 05/07)*
- [Rapport_validation_T10000.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Rapport_validation_T10000.md) — Validation T=10000 *(ajouté 05/07)*
- [Interprétation-des-résultats-de-tests.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Interpr%C3%A9tation-des-r%C3%A9sultats-de-tests.md) — Lecture des résultats de tests *(ajouté 05/07)*

### Guides pratiques

- [Bonnes-Pratiques-Claude-Code.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Bonnes-Pratiques-Claude-Code.md) — STEP=0.010, Monitor, /clear, règles runs
- [Guide-Git-GitHub.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Guide-Git-GitHub.md) — Workflow git, nohup + printf + tee, branches
- [Guide-Linux-Commandes.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Guide-Linux-Commandes.md) — §18 wg_auto.sh : bascule WireGuard maison/déplacement *(ajouté 05/07)*
- [Diagnostic-WireGuard-Hotspot.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Diagnostic-WireGuard-Hotspot.md) — Diagnostic + résolution confirmée hotspot mobile *(ajouté 05/07)*
- [Guide-VSCode-Bonnes-Pratiques.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Guide-VSCode-Bonnes-Pratiques.md) — Bonnes pratiques VSCode *(ajouté 05/07)*
- [Guide-Capture-Session-Claude-Code.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Guide-Capture-Session-Claude-Code.md) — Capture de session *(ajouté 05/07)*
- [Archive-Fichiers-Obsoletes.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Archive-Fichiers-Obsoletes.md) — Registre fichiers obsolètes *(ajouté 05/07)*
- [Prompts-Claude-Code.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Prompts-Claude-Code.md) — Prompts Claude Code *(ajouté 05/07)*
- [ORGANISATION_FICHIERS.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/ORGANISATION_FICHIERS.md) — Carte de contexte : où vit quoi, les 6 lieux *(ajouté 05/07)*

### Mémoire long terme

- [JOURNAL.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/JOURNAL.md) — Historique daté append-only complet (T=500k, T=5M, v14, v15, Obj.2) *(ajouté 05/07 — n'avait jamais été poussé)*
- [knowledge_base_obj2.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/knowledge_base_obj2.md) — Base de connaissance agent autonome *(ajouté 05/07, mis à jour : Obj.2 en cours, v15 actif, chemin RAG `/mnt/vault_rag`)*

### Pavés pave1 — Phase C / v4 / v5

- [1_pave1-rapport_zeta_riemann_exploration_numerique_IA_hprzeta.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/1_pave1-rapport_zeta_riemann_exploration_numerique_IA_hprzeta.md)
- [2_pave1-solution_experimental_zeta.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/2_pave1-solution_experimental_zeta.md)
- [3_pave1-recovery_zeta.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/3_pave1-recovery_zeta.md)
- [4_pave1-cerveau_autonome_zeta.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/4_pave1-cerveau_autonome_zeta.md)
- [5_pave1-resume_recuperation_git_systeme_hprzeta.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/5_pave1-resume_recuperation_git_systeme_hprzeta.md)
- [6_01_pave1-cartographie_diagnostic_riemann_lab_v1_C.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/6_01_pave1-cartographie_diagnostic_riemann_lab_v1_C.md)
- [6_02_pave1-plan_migration_recovery_brainvault_rag_v1_C.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/6_02_pave1-plan_migration_recovery_brainvault_rag_v1_C.md)
- [6_03_pave1-checklist_systeme_linux_hprzeta_v1_C.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/6_03_pave1-checklist_systeme_linux_hprzeta_v1_C.md)
- [7_pave1-methode_scripts_post_audit_et_remarques_materiel_hprzeta.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/7_pave1-methode_scripts_post_audit_et_remarques_materiel_hprzeta.md)
- [8-pave1-complement_methode_git_priorites_phase3_hprzeta.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/8-pave1-complement_methode_git_priorites_phase3_hprzeta.md)
- [09_pave1-synthese_journee_phase_c_v4_voie_b_illinois_pur.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/09_pave1-synthese_journee_phase_c_v4_voie_b_illinois_pur.md)

### Pavés pave2 — Primalité et zêta

- [12_pave2-primalite_zeta_riemann_lab.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/12_pave2-primalite_zeta_riemann_lab.md)
- [13_pave2-index_primalite.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/13_pave2-index_primalite.md)
- [14_pave2-lexique_primalite.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/14_pave2-lexique_primalite.md)
- [15_pave2-produit_eulerien.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/15_pave2-produit_eulerien.md)
- [16_pave2-lien_zeros_premiers.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/16_pave2-lien_zeros_premiers.md)
- [17_pave2-limites_ethique_et_perimetre.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/17_pave2-limites_ethique_et_perimetre.md)

### Pavés pave3 — Cryptographie et sécurité

- [18_pave3-cryptozeta_cybersecurite_cryptographie_moderne.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/18_pave3-cryptozeta_cybersecurite_cryptographie_moderne.md)
- [19_pave3-index_crypto.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/19_pave3-index_crypto.md)
- [20_pave3-lexique_cyber_crypto.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/20_pave3-lexique_cyber_crypto.md)
- [21_pave3-primalite_et_rsa.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/21_pave3-primalite_et_rsa.md)
- [22_pave3-zeta_distribution_premiers_crypto.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/22_pave3-zeta_distribution_premiers_crypto.md)
- [23_pave3-post_quantique_nist.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/23_pave3-post_quantique_nist.md)
- [24_pave3-hash_checksum_signature.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/24_pave3-hash_checksum_signature.md)
- [25_pave3-recovery_et_securite_projet.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/25_pave3-recovery_et_securite_projet.md)
- [26_pave3-limites_conjectures_preuves.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/26_pave3-limites_conjectures_preuves.md)

### Objectif 2 — Agent autonome

- [Handoff.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/Handoff.md) — État courant inbox-ia
- [README.md](https://github.com/hprzeta/Riemann_Lab/blob/inbox-ia/README.md) — Index inbox-ia

---

*inbox_ia_liens.md · scripts/ · Riemann_Lab_C · hprzeta · MAJ 2026-07-05 · 130 lignes*
