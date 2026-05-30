## 6-01 Pilier1  **Riemann_Lab — Cartographie et diagnostic v1 — branche C intégrée** 

Mise à jour après réception des éléments Riemann_Lab_C : scripts v3/v4.1, modules batch, journaux T=1000/T=10000, visuels et sorties CSV. 

## **Synthèse exécutive** 

• Le dépôt local contient quatre branches structurantes : main, Riemann_Lab_IA, Riemann_Lab_Test et Riemann_Lab_C. La branche active visible sur la capture était Riemann_Lab_IA ; Riemann_Lab_C porte la Phase C optimisation C/libmpfr. 

• La chaîne v3 est une version opérationnelle : détection Riemann-Siegel, affinage Illinois via mpmath, multiprocessing 4 workers, validation Turing-Backlund et génération CSV/PNG/LOG. 

• La chaîne v4.1 est une correction architecturale de v4 : retour à Z_batch pour la détection, chargement du .so après fork, seuil C à t>=300 et erreur immédiate si illinois_mpfr.so absent. 

• Les résultats T=10000 du 21/05/2026 forment un corpus validé expérimentalement distinct du CSV historique 24/04/2026. Ils doivent être conservés comme run v3 indépendant, pas écrasés. 

## **Branches et rôle** 

|Branche|Rôle|Décision de migration|
|---|---|---|
|main|Base publique/stable historique|Conserver propre, publier docs validées<br>uniquement|
|Riemann_Lab_IA|Branche IA locale/Ollama et assistants|Séparer de la Phase C pour éviter<br>mélanges|
|Riemann_Lab_Test|Tests et expériences|Archive contrôlée ou sandbox|
|Riemann_Lab_C|Phase C optimisation C/libmpfr, v3 -> v4/v4.1|À cloner explicitement et intégrer comme<br>branche technique active|



## **Runs numériques reçus** 

|Run|Paramètres|Résultat|Statut|
|---|---|---|---|
|v3 T=1000 —<br>20260511_212709|STEP=0.1, 4 workers, 35 dps, Illinois<br>mpmath|649 zéros, 4.45 min, 2.43 z/s, t<br>dernier≈999.7915715574|Validé expérimental ;<br>surplus dans comptage<br>Turing à documenter|
|v3 T=10000 —<br>20260521_133316|STEP=0.02, 4 workers, 35 dps, Illinois<br>mpmath|10142 zéros, 165.81 min, 1.02<br>z/s, t dernier≈9998.8503970897|Corpus v3 majeur ;<br>indépendant du run<br>historique 20260424|
|batch_cpu —<br>20260516_180214|Sortie brute batch CPU|Doublons et désordres locaux ;<br>utile benchmark|Ne pas classer comme<br>CSV validé final|



## **Diagnostic mis à jour** 

• Le projet possède maintenant deux validations T=10000 : une v2 historique à 50 dps datée 20260424, et une v3 optimisée datée 20260521 à 35 dps. Les deux doivent être versionnées séparément. 

• Les journaux v3 indiquent un statut Turing global complet, mais les lignes de contrôle affichent des SURPLUS +1/+2. Cela doit être expliqué dans la documentation comme un problème de convention de comptage ou de correction S(T), et non passé sous silence. 

• La comparaison LMFDB est excellente sur 19/20 premiers zéros ; le 20e affiche un écart d’environ 8.06e-10 dans les runs v3, au-dessus du seuil 1e-10. À conserver comme point de vigilance. 

• Les PNG v3 sont utiles pour publication : Z de Hardy locale, histogramme des espacements normalisés vs GUE, et droite critique. Le T=10000 est plus robuste statistiquement que le T=1000. 

## **Arborescence recommandée après intégration Riemann_Lab_C** 

~/hprzeta-lab/ ├── repo-main/ ├── repo-ia/ ├── repo-c/ # checkout Riemann_Lab_C │ └── src/calculs/optimisation/ │ ├── compute_zeros_v3.py │ ├── compute_zeros_v4_1.py │ ├── theta_rapide.py │ ├── riemann_siegel_batch.py │ ├── parallel_scanner.py │ ├── turing_validation.py │ └── c_modules/ ├── data/validated/ │ ├── T10000_v2_20260424_205325/ │ ├── T1000_v3_20260511_212709/ │ └── T10000_v3_20260521_133316/ └── data/raw/benchmarks/batch_cpu_20260516_180214/ 

## **Décisions** 

- Classer compute_zeros_v3.py comme version de production expérimentale CPU 4 workers. 

- Classer compute_zeros_v4_1.py comme branche de transition vers Phase C, exigeant compilation du .so. 

- Classer CLAUDE_c_modules.md et CLAUDE_optimisation.md comme spécifications techniques Phase C. 

- Créer une note d’écart Turing/LMFDB avant toute annonce de validation finale. 

