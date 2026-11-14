# Rapport — mise en place du dépôt automatique des rapports (projet SITE ZETA)

> Exécuté à 23:32 d'après `PROMPT_MAJ_AUTO_DEPOT_PROJET_20261111_2330.md`, option **A** (préparation locale) choisie par hprzeta après le diagnostic. Statut : 🟢 ok · 🟡 fait à moitié · 🔴 non faisable avec les outils de la session.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Étape 1 : Chrome, projet SITE ZETA, état avant | 🟢 | Liste des projets claude.ai puis page du projet SITE ZETA (« Contexte : 44 fichiers », 9 % de la capacité) ; liste des fichiers lue : 9 rapports .md en double, 1 fichier .bak-20261111 (captures) | — |
| Outil `Projects` (project_info / project_write) dans la session | 🔴 | ABSENT. Outils voisins vérifiés : DesignSync (projets claude.ai/design, réservé à /design-sync), SendToProject (message dans un projet cloud claude.ai/code, seulement via /send-to-project, aucun transfert de fichier), connecteur Claude Docs (documents, pas le Contexte d'un projet) | Aucun moyen documenté de rattacher cette session locale au projet de chat SITE ZETA : le dépôt dans claude.ai reste humain |
| Format du hook Stop (documentation officielle) | 🟢 | Entrée : stop_hook_active, last_assistant_message, background_tasks, session_crons ; sortie : decision block + reason, exit 2, ou hookSpecificOutput.additionalContext ; plafond de 8 continuations de suite ; pas de matcher | — |
| Emplacement du hook | 🟢 | Choisi : .claude/settings.local.json (ignoré par git, .gitignore:28 ; hooks cumulatifs avec le SessionStart du turbo) | — |
| Script scripts/depot_projet_site_zeta.sh | 🟢 | 98 lignes, exécutable, bash -n OK, exclu de git par .git/info/exclude ; anti-boucle (stop_hook_active), interrupteur src/ia/depot_projet_site_zeta.actif, journal sha256, audit des secrets, exclusions .bak/RAPPORT_ANALYSE_*/> 500 Ko, mode --ajouter | — |
| Tests simulés (arbre temporaire) | 🟢 | 11 scénarios : interrupteur absent, dossier vide, stop_hook_active vrai, fichier nouveau, déjà journalisé, .bak, e-mail factice (bloqué, valeur jamais affichée), adresse projet + unité systemd (autorisées), IPv4/MAC/fe80/jeton (bloqués), valeurs bénignes (autorisées), --ajouter, consigne de rapport de session | Les premiers essais de T4/T7/T8 échouaient à cause de mon banc de test (sortie mêlée), refaits en direct |
| Hook écrit dans la configuration | 🟢 | settings.local.json : Stop → depot_projet_site_zeta.sh (timeout 60) ; copie pdf/archive/settings.local.json.bak-20261111 ; JSON valide ; SessionStart conservé ; interrupteur absent jusqu'au « go test réel » (hook inerte) | — |
| Test réel : préparation des rapports du jour | 🟢 | Interrupteur créé à 23:31 ; 19 livrables copiés dans pdf/site/maj_site_20261111/A_DEPOSER/ (2,1 Mo) et journalisés ; 0 .bak, 0 RAPPORT_ANALYSE_*, 0 fichier > 500 Ko ; audit : 0 bloqué | Le 1er appel du test réel s'est fait avec une entrée vide : la consigne JSON n'a pas été affichée |
| Rapport de session | 🟢 | RAPPORT_SESSION_20261111_2332.md rédigé (demandes, actions, hashes, décisions, points ouverts, erreurs) et journalisé | — |
| Dépôt dans le projet SITE ZETA (claude.ai) | 🔴 | Non fait par Claude Code (aucun outil) : A_DEPOSER est prêt à être glissé dans le projet. La liste du projet ne peut donc pas « se mettre à jour » toute seule | Dernier geste : hprzeta |
| Nettoyage proposé (rien supprimé) | 🟡 | Doublons .md du projet : PROMPT_CORRECTION_MAJ_SITE_…2049, PROMPT_MAJ_DECISIONS_SITE_…2137, RAPPORT_MAJ_CORRECTIONS_…2119, RAPPORT_MAJ_DECISIONS_…2147, RAPPORT_MAJ_FIABILITE_PDF_…2254, RAPPORT_MAJ_PUBLICATION_PDF_…2236, RAPPORT_MAJ_SCRIPT_DATE_FR_…2304, RAPPORT_OPTIONS_DECISIONS_…2137, RAPPORT_TEST_MAJ_SITE_…2049 (chacun ×2) ; fichier RAPPORT_MAJ_SCRIPT2_DATE_FR_20261111_2312.md.bak-20261111 | Dites lesquels retirer : une copie par rapport suffit ; l'interface crée un doublon quand le nom existe déjà |
| Aucun commit, push ni suppression dans le projet | 🟢 | git status : aucun fichier suivi modifié ; .gitignore, scripts de PDF et monitoring/Monitoring-Runs.md non touchés | — |

## 2. Tableau de modifications (tout local, 0 commit)

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| scripts/depot_projet_site_zeta.sh (local, non suivi) | [nouveau, 98 lignes] hook Stop : anti-boucle, interrupteur, journal sha256, audit des secrets, copie dans A_DEPOSER, additionalContext | — | 2026-11-11 23:32 |
| .claude/settings.local.json (local, ignoré par git) | [+11 lignes] "Stop": [{ hooks: [{ type: command, command: …/depot_projet_site_zeta.sh, timeout: 60 }] }] | — | 2026-11-11 23:32 |
| .git/info/exclude (local) | [+2] scripts/depot_projet_site_zeta.sh ; pdf/site/*/A_DEPOSER/ | — | 2026-11-11 23:32 |
| src/ia/depot_projet_site_zeta.actif et .log (local) | [nouveaux] interrupteur (vide) ; journal : 19 lignes puis les rapports de session et de mise en place | — | 2026-11-11 23:32 |
| pdf/site/maj_site_20261111/A_DEPOSER/ (local) | [19 fichiers, 2,1 Mo] copies des RAPPORT_/PROMPT_ du jour, puis rapport de session et de mise en place | — | 2026-11-11 23:32 |

## 3. Limites constatées

- **Aucun outil `Projects`** dans la session : le dépôt direct dans le projet claude.ai est impossible ; ce n'est pas un réglage que Claude Code peut faire seul.
- Le hook ne peut que préparer et rappeler : le glisser-déposer final reste humain.
- Le hook ne se déclenche que dans les sessions lancées depuis `~/projet_zeta` et seulement si l'interrupteur existe ; supprimer `src/ia/depot_projet_site_zeta.actif` le désactive.
- Plafond documenté de 8 continuations de suite ; le script ne bloque qu'une fois par fichier nouveau (journal sha256).

Captures : `captures/depot_avant_liste_projets_claude_ai.jpg`, `captures/depot_avant_page_projet_site_zeta.jpg`, `captures/depot_avant_contexte_44_fichiers.jpg`.

---
*RAPPORT_MAJ_AUTO_DEPOT_20261111_2332.md · projet SITE ZETA · hprzeta · MAJ 11 novembre 2026 23:32 · 42 lignes*
