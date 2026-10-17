# Prompt pour Claude Code — monitoring v2 : lanceur, fenêtres, rapport de run (à coller tel quel)

```
Contexte : monitoring v2 livré (archive monitoring_v2_20261017.tar.gz, à extraire par-dessus ~/projet_zeta/monitoring/).
Lis d'abord monitoring/README.md. Nouveautés : lanceur `zeta-mon-exec` (ou zeta-mon-start/stop), fenêtres de graphiques
rangées pour les runs de TEST, fiche de session, rapport MD+PDF avec section « Interprétation », dossiers runs/test|prod/<date>_<nom>/.

ÉTAPE 1 — LECTURE SEULE (ne modifie RIEN) puis STOP :
 a. Lis scripts/zeta_run.sh, zeta_distribute_run.sh, zeta_turbo_on.sh/off.sh et compute_zeros_v17.py.
 b. Réponds-moi par un tableau : (1) comment un run démarre aujourd'hui ; (2) où le CSV des zéros est écrit et À QUELLE
    FRÉQUENCE il est vidé (flush) ; (3) comment le turbo « par session » est géré, par quel mécanisme
    (intel_pstate/no_turbo ? autre ?) et s'il faut sudo (sudoers NOPASSWD ?) ; (4) $XDG_SESSION_TYPE (X11 ou Wayland) et
    backend matplotlib dans zeta_env (tkinter ou PyQt5 disponible ?) ; (5) diff entre scripts/zeta_{log_metrics,plot_live,
    plot_metrics,gue_hist}.py et monitoring/scripts/ (doublons) ; (6) la mise à jour du 17/10 (lecture incrémentale,
    `grep -c LecteurZeros monitoring/scripts/zeta_plot_live.py`) est-elle appliquée ?
 c. Propose l'intégration minimale dans zeta_run.sh. Attends mon OK.

ÉTAPE 2 — INSTALLATION (après mon OK) : extraire l'archive par-dessus monitoring/, `bash monitoring/install.sh`, `source ~/.bashrc`,
 `python monitoring/scripts/zeta_log_metrics.py --test` (5 machines OK ?), `zeta-mon-on`, `zeta-mon-status`.
 Doublons : monitoring/scripts/ est la SEULE source ; supprime ou remplace les copies de scripts/ par des wrappers d'une ligne (diff avant).

ÉTAPE 3 — INTÉGRATION (après mon OK) : dans zeta_run.sh, enveloppe le lancement avec
 `zeta_mon_run.py exec --nom <nom> --type test|prod --csv <sortie> -- <commande existante>` (ou start/stop si le run est détaché),
 en gardant le comportement actuel (turbo, arguments, logs). Ne change ni l'algorithme ni le format des colonnes.
 - Turbo : conserve le mécanisme actuel ; n'élargis PAS le sudoers ; si un mot de passe est requis, demande-le-moi.
 - CSV des zéros : si le flush n'est pas fait au moins toutes les 1–2 s, propose le patch minimal (flush périodique basé sur le temps),
   montre le diff, puis vérifie que le débit (z/s) reste identique à ±1 %.
 - `--type test` : fenêtres ON ; `--type prod` : fenêtres OFF (risque de gel déjà vécu). Jamais de plein écran.

ÉTAPE 4 — PREMIER RUN DE TEST RÉEL (après mon OK, jamais avant) : ≥ 2–3 min (≈ 60 000–100 000 zéros, ex. tranche vers t≈4,9·10⁶),
 `--type test`. Pendant : surveille load/température ; si l'écran rame, ferme les fenêtres (`zeta-mon-fermer`) et passe en `--fenetres non`.
 Critères de succès : fenêtres ouvertes et rangées ; runs/test/<id>/ contient meta.json, session.md, etat.csv, metrics.csv,
 figures/{metrics,zeros_tranches,gue,debit}.png, rapport.md, rapport.pdf ; code retour 0 ; Monitoring-Runs.md à jour.

ÉTAPE 5 — APRÈS LE RUN : relis « Observations » ; rédige runs/test/<id>/interpretation.md (sections courtes ; chaque affirmation marquée
 mesuré / heuristique / hypothèse / conjecture ; n'érige JAMAIS une hypothèse en fait ; le rapport n'est pas une validation Turing–Backlund),
 puis `zeta-report <dossier>` ; version définitive : `zeta-report <dossier> --lang en`. Donne-moi le chemin + 3 lignes
 (durée, z/s médian, T max PC1, anomalies).

RÈGLES : monitoring/scripts/ non modifié sans mon accord ; STOP avant tout commit (montre `git status`, .gitignore fourni :
 data/, logs/, metrics.csv, etat.csv ignorés) ; pied de page « date de mise à jour + nombre de lignes » sur chaque MD créé/modifié ;
 mets à jour zeta-script (menu) avec les nouvelles commandes zeta-mon-exec/start/stop/fenetres/fermer.
```

---
*PROMPT_CLAUDE_CODE.md · MAJ 2026-10-17 · 46 lignes*
