## 6-03 Pilier1  **CRiemann_Lab — Checklist système Linux avant migration v1 — exigences Phase C** 

Cette version ajoute les exigences nécessaires pour compiler et exécuter Riemann_Lab_C : libmpfr, libgmp, gcc, Makefile, multiprocessing, NumPy/CuPy optionnel. 

## **Commandes complémentaires Phase C** 

|Contrôle|Commande / attente|
|---|---|
|Compilateur C|gcc --version ; build-essential installé|
|MPFR/GMP|dpkg -l | grep -E "libmpfr-dev|libgmp-dev" ; mpfr >= 4|
|Make|make --version ; TAB réels dans Makefile|
|Bibliothèque .so|find ~/projet_zeta -name "illinois_mpfr.so" -ls|
|ctypes|python -c "import ctypes; print(ctypes.__name__)"|
|NumPy|python -c "import numpy as np; print(np.__version__)"|
|CuPy optionnel|python -c "import cupy as cp; print(cp.cuda.runtime.getDeviceCount())"|
|Multiprocessing|python -c "import multiprocessing as mp; print(mp.cpu_count())"|



## **Checklist données à récupérer** 

- Dossier calculs/v3_T1000_20260511_212709 complet : CSV final, CSV parallèle, LOG, PNG. 

- Dossier calculs/v3_T10000_20260521_133316 complet : CSV final, CSV parallèle, LOG, PNG. 

- Dossier c_modules complet : .c, .h, Makefile, test_illinois.py, .so si compilé. 

- Fichiers de spécification : CLAUDE_c_modules.md et CLAUDE_optimisation.md. 

- Sorties benchmark : benchmark_15min.py et zeros_batch_cpu_20260516_180214.csv. 

## **Décision selon résultat audit** 

|Cas|Décision|
|---|---|
|libmpfr-dev absent|Installer avant toute tentative v4.1|
|illinois_mpfr.so absent|Classer v4.1 comme non exécutable ; compiler c_modules|
|CUDA/CuPy absent ou instable|Utiliser Z_batch CPU NumPy ; GPU optionnel seulement|
|RAM faible|Réduire bloc interne Z_batch et éviter scans profonds /mnt/data/models_ia|
|Git branches non poussées|Créer archive locale + git bundle avant réinstallation|



## **Commandes recommandées après fin de l’audit** 

cd ~/projet_zeta git branch -vv git status git diff --name-status Riemann_Lab_IA..Riemann_Lab_C git ls-tree -r --name-only Riemann_Lab_C | grep -E "c_modules|compute_zeros_v4|illinois|benchmark|optimisation" find ~/projet_zeta -path "*/c_modules/*" -maxdepth 8 -type f | sort find ~/projet_zeta/calculs -maxdepth 2 -type f | grep -E "20260511|20260521" | sort 

## **Critères de succès Phase C** 

- test_illinois.py valide les 10 premiers zéros LMFDB à tolérance < 1e-10 ou mieux. 

- compute_zeros_v4_1.py refuse de démarrer si le .so manque : comportement attendu. 

- Un mini-run T=1000 v4.1 reproduit 649 ou le nombre attendu selon convention choisie, avec log complet et sans doublons. 

- Un benchmark documente clairement le gain réel C vs mpmath ; sans benchmark, le gain reste un objectif. 

