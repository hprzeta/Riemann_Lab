## *6-02 Pilier1  *Riemann_Lab — Plan de migration, Recovery, Brain Vault et RAG v1 — branche C** 

Objectif : intégrer proprement la branche Riemann_Lab_C, ses runs v3, son module C attendu, et ses artefacts dans la migration hprzeta-lab. 

## **Plan de migration Git multibranche** 

- Avant migration : git status sur chaque branche, puis création d’archives tar.gz par branche. 

- Cloner ou copier explicitement Riemann_Lab_C dans repo-c ; ne pas fusionner immédiatement dans main. 

- Conserver Riemann_Lab_IA séparée pour éviter que les dépendances Ollama/IA polluent la chaîne calcul numérique. 

- Créer un manifest par run : commit, branche, script, paramètres, fichiers produits, hash SHA256. 

|Élément|Action recovery/RAG|
|---|---|
|execution_v3_T1000_20260511_212<br>709.log|Index prioritaire : contient paramètres, durée, Turing, LMFDB, environnement|
|execution_v3_T10000_20260521_13<br>3316.log|Index prioritaire : run v3 majeur T=10000|
|zeros_v3_T*.csv|Stocker dans data/validated si log associé complet|
|zeros_parallel_T*.csv|Stocker comme sortie intermédiaire worker/parallèle|
|zeros_batch_cpu_20260516_180214.<br>csv|Stocker comme benchmark brut, non validé final|
|PNG v3|Stocker dans reports/figures et docs/assets|



## **Brain Vault enrichi** 

brain-vault/ ├── 03_code/ │ ├── versions/compute_zeros_v3.md │ ├── versions/compute_zeros_v4_1.md │ ├── phase_c/illinois_mpfr_spec.md │ └── benchmarks/batch_cpu_20260516.md ├── 02_math_zeta/validation/ │ ├── run_T1000_v3_20260511.md │ ├── run_T10000_v3_20260521.md │ └── note_surplus_turing.md └── 06_recovery/ ├── restore_branch_C.md └── build_illinois_mpfr_so.md 

## **RAG : filtres de confiance** 

|Classe<br>validé<br>intermédiaire<br>spécification<br>legacy|Sources|Usage dans le RAG|
|---|---|---|
||logs v3 complets + CSV final + PNG|Réponses factuelles avec statut expérimental|
||zeros_parallel, benchmark batch_cpu|Analyse performance et debugging seulement|
||CLAUDE_c_modules,<br>CLAUDE_optimisation|Génération de code C/Makefile/tests|
||v1, tests erreurs, démos|À citer comme historique, jamais comme pipeline<br>actif|



## **Scripts à préparer après audit système** 

- backup_all_branches.sh : archive main, IA, C, Test avec hash. 

- restore_branch_C.sh : restaure repo-c, venv minimal, libmpfr-dev/libgmp-dev, puis build c_modules. 

- build_phase_c.sh : cd c_modules && make && python3 test_illinois.py. 

- validate_run_v3.py : compare CSV, log, nombre de lignes, monotonie, doublons, LMFDB, Turing. 

- rag_ingest_riemann_lab_c.py : indexe seulement les fichiers classés validé/spécification. 

## **Point de vigilance majeur** 

• La v4.1 promet une vitesse 15–20 z/s, mais les preuves reçues actuellement documentent surtout v3 à 1.02 z/s pour T=10000. La v4.1 doit donc rester 'pré-production' tant que le .so et son benchmark complet ne sont pas fournis. 

- La fonction Z_batch est centrale : elle doit être testée contre mpmath.siegelz sur plusieurs plages avant de servir à un run définitif. 

- Le seuil t>=300 pour Illinois C doit être conservé comme règle métier Phase C. 

