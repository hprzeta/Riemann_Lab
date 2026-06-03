## **09 Pilier1 — Synthèse journalière Phase C v4 : validation hybride et cap vers Illinois C pur** 

Rapport de gel du travail du 27–28 mai 2026 — hprzeta / Riemann_Lab. Ce document rassemble tout ce qui a été validé aujourd’hui : audits, Git, c_modules, runs v4 T=80/T=300/T=650, diagnostic gamma_c vs mpmath, création des piliers Brain Vault 2 et 3, et décision de poursuivre demain sur la voie B : améliorer Z_mpfr/Illinois C pur avec objectif final T=10000. 

## **Décision de gel** 

**On fige l’état actuel : v4 fonctionne comme pipeline hybride fiable. La suite ne consiste pas à lancer plus grand immédiatement, mais à poursuivre demain la voie B pour viser Illinois C pur, puis seulement ensuite préparer des tests plus ambitieux, jusqu’à T=10000.** 

## **1. Résumé exécutif** 

- Branche de travail : Riemann_Lab_C. 

- c_modules compile correctement et illinois_mpfr.so est chargé par compute_zeros_v4.py. 

- test_illinois.py valide les 10 premiers zéros en mode hybride. 

- benchmark_illinois.py mesure un gain isolé important du C/libmpfr, environ ×48.73 face à mpmath.findroot sur t≈500–638. 

- compute_zeros_v4.py est validé fonctionnellement sur T=80, T=300 et T=650. 

- La validation Turing-Backlund est complète : aucun zéro manquant observé sur les runs T=80/T=300/T=650. 

- La validation LMFDB reste stable : 19/20 premiers zéros sous 1e-10, avec le zéro #20 à environ 8.06e-10. 

- Le mode effectif reste 100 % Illinois_C→mpmath : Illinois C pur n’est pas encore accepté comme résultat final. 

- Le diagnostic gamma_c vs mpmath montre que le résidu mpmath.siegelz(gamma_c) est trop grand pour le seuil 1e-8. 

## **2. Documents et piliers produits aujourd’hui** 

|Livrable|Rôle|Statut|
|---|---|---|
|PDF 06 — Lexique IA & Brain<br>Vault|Dictionnaire vivant : Vault, Skills, RAG, agents, grounding,<br>hallucination, provenance.|Créé|
|PDF 07 — Pavé Primalité|Pilier 2 : primalité, produit eulérien, π(x), Λ(n), ψ(x), formule<br>explicite.|Créé|
|brain-vault_ajout_primalite.zip|Pages Markdown initiales pour<br>brain-vault/02_math_zeta/primalite.|Créé|
|PDF 08 — CryptoZeta|Pilier 3 : cybersécurité défensive, RSA, ECC, post-quantique,<br>hash, recovery.|Créé|
|brain-vault_ajout_cryptozeta.zip|Pages Markdown initiales pour brain-vault/03_cyber_crypto.|Créé|
|PDF 09 — présent document|Gel de la journée Phase C v4 et plan de reprise voie B.|Créé|



## **3. Validation c_modules** 

La compilation C a été relancée par make clean puis make. La commande gcc compile illinois_mpfr.c et z_function.c avec -O3, -march=native, -fPIC, -shared, puis lie MPFR, GMP et libm. Aucune erreur de compilation n’a été observée. 

gcc -O3 -march=native -fPIC -Wall -Wextra -shared   -o illinois_mpfr.so illinois_mpfr.c z_function.c -lmpfr -lgmp -lm 

test_illinois.py a validé 10/10 zéros en convergence réelle et 10/10 en proximité LMFDB, avec 3 zéros passant par Illinois C→mpmath et 7 par mpmath.findroot pur. 

benchmark_illinois.py a mesuré 100 intervalles sur t≈500.3–637.9 : Illinois C à 18.9055 ms/zéro contre mpmath.findroot à 921.1937 ms/zéro, soit un gain ×48.73. Ce gain doit être interprété comme gain de pré-affinage C sur fonction RS approchée, pas encore comme remplacement final de mpmath.siegelz. 

## **4. Runs compute_zeros_v4.py validés** 

|Run|Zéros|Durée|Vitesse|Méthode effective|Validation|
|---|---|---|---|---|---|
|T=80|21 trouvés / 21 attendus<br>final|56.3 s|0.37 zéros/s|21/21 Illinois_C→mpmath|Turing complet, LMFDB<br>19/20|
|T=300|138 trouvés / 136 Weyl<br>affichés|128.2 s|1.08 zéros/s|138/138 Illinois_C→mpmath|Turing complet, surplus<br>documentés, LMFDB<br>19/20|
|T=650|377 trouvés / 377 attendus|518.6 s|0.73 zéros/s|377/377 Illinois_C→mpmath|Turing complet, aucun<br>zéro manquant, LMFDB<br>19/20|



Tous les runs T=80, T=300 et T=650 ont confirmé que le pipeline v4 est fonctionnel et que les fichiers CSV/PNG/LOG sont générés correctement. Les surplus Turing doivent rester documentés, mais aucun zéro manquant n’a été signalé. 

## **5. Point de vigilance Turing et Weyl** 

• T=80 : Turing complet, 21 zéros calculés, aucun manquant, surplus total signalé dans certains points intermédiaires. 

• T=300 : Turing complet, 138 zéros calculés, aucun manquant, surplus aux points T≈59.35, 111.03, 241.05 et 299.84. 

• T=650 : Turing complet, 377 zéros calculés, aucun manquant, surplus total de 4 autour de T≈116.23, 517.59 et 648.79. 

• Le résumé global “N attendus Weyl” n’est pas toujours cohérent avec le comptage final Turing. À corriger ou documenter dans v5. 

## **6. Diagnostic de la logique hybride** 

Le grep de compute_zeros_v4.py a confirmé que la détection est effectuée par mpmath.siegelz et que l’affinage est hybride. La racine C gamma_c est acceptée uniquement si abs(mpmath.siegelz(gamma_c)) < 1e-8. Sinon, mpmath.findroot est lancé depuis gamma_c, puis la méthode est classée Illinois_C→mpmath. 

if abs(float(mpmath.siegelz(gamma_c))) < 1e-8: return gamma_c, "illinois_C" 

gamma = float(mpmath.findroot(mpmath.siegelz, gamma_c)) return gamma, "illinois_C→mpmath" 

Cette logique explique pourquoi le pipeline est fiable : le C propose une racine de l’approximation RS, mais la validation finale reste faite sur mpmath.siegelz. 

## **7. Vérification de la boucle Illinois C** 

La vérification numérotée de illinois_mpfr.c a invalidé l’hypothèse d’une boucle vide : la boucle Illinois existe bien. Elle calcule la sécante, évalue Zc, met à jour l’intervalle [a,b], applique une correction Za *= 0.5 dans une branche, puis retourne le milieu final. 

for (int iter = 0; iter < MAX_ITER; iter++) { mpfr_sub(diff, b, a, MPFR_RNDN); if (abs_diff < tol_mpfr) break; 

c = b - Zb * (b-a) / (Zb-Za); Z_mpfr(Zc, c); 

if (Za * Zc < 0) { b = c; Zb = Zc; } else { a = c; Za = Zc; Za *= 0.5; } } 

Le problème n’est donc pas l’absence d’algorithme Illinois. Le problème est l’écart entre la racine de Z_mpfr / RS C et la vraie racine mpmath.siegelz. 

## **8. Diagnostic gamma_c vs mpmath** 

|Échantillon|delta gamma_c - gamma_true|residu_c = siegelz(gamma_c)|Lecture|
|---|---|---|---|
|t≈14.13|8.873e-03|7.043e-03|Trop loin du seuil 1e-8|
|t≈79.34|2.527e-02|6.724e-02|Très loin du seuil|
|t≈297.98|-1.805e-04|-1.059e-03|Meilleur, mais encore trop grand|
|t≈498.58|-6.856e-05|-5.302e-04|Meilleur cas mesuré, encore >1e-8|
|t≈518.24|7.819e-03|2.292e-02|Biais important|
|t≈647.75|-1.280e-02|3.934e-02|Biais important|



Statistiques : moyenne |delta| ≈ 9.17e-03, médiane |delta| ≈ 8.35e-03, maximum |delta| ≈ 2.53e-02. Le plus petit résidu C mesuré est ≈5.30e-04, très supérieur au seuil 1e-8. 

**Décision : ne pas assouplir le seuil 1e-8. Accepter gamma_c avec des résidus de 1e-4 à 1e-2 dégraderait la rigueur scientifique du projet.** 

## **9. Statut scientifique figé ce soir** 

|Composant|Statut|Commentaire|
|---|---|---|
|c_modules / compilation|Validé|illinois_mpfr.so reproductible localement.|
|Boucle Illinois C|Présente|Sécante/Illinois implémentée, mais correction à revoir plus tard.|
|Benchmark C isolé|Très bon|Gain ×48.73, mais sur approximation RS.|
|v4 T=80/T=300/T=650|Validé fonctionnellement|Aucun zéro manquant, Turing complet.|
|Illinois C pur|Non validé|0 % accepté ; gamma_c trop éloigné de mpmath.siegelz.|
|Mode hybride|Validé|C pré-affine, mpmath finalise la racine vraie.|
|Objectif T=10000|Reporté|À reprendre après amélioration voie B.|



## **10. Voie B — plan de reprise demain** 

L’objectif confirmé est Illinois pur puis test T=10000. Pour y arriver, il faut réduire l’écart entre Z_mpfr et mpmath.siegelz. La voie B devient donc le chantier prioritaire : améliorer la fonction C/MPFR pour que gamma_c vérifie réellement mpmath.siegelz(gamma_c) à un seuil strict. 

- Comparer Z_mpfr et mpmath.siegelz sur grille autour de plusieurs zéros pour caractériser le biais local. 

• Auditer z_function.c et illinois_mpfr.c : theta, terme de reste C0/C1, signe, conventions N=floor(sqrt(t/2π)), correction Berry. 

- Vérifier la cohérence avec riemann_siegel_batch.py et mpmath.siegelz. 

- Ajouter un diagnostic CSV : t, Z_double, Z_mpfr, mpmath.siegelz, écarts absolus et relatifs. 

- Étudier l’ajout de termes Riemann-Siegel supplémentaires ou une correction plus fidèle. 

- Revoir la correction Illinois : correction côté stagnant symétrique plutôt qu’asymétrique uniquement Za *= 0.5. 

- Créer une version expérimentale v4b ou v5, sans casser v4 validée. 

- Après amélioration : recompiler, relancer test_illinois, benchmark, T=650, puis seulement T=1000 et T=10000. 

## **11. Commandes utiles pour demain** 

# Reprise contexte cd ~/projet_zeta git checkout Riemann_Lab_C git status 

# Recompiler c_modules cd src/calculs/optimisation/c_modules make clean && make 

# Revalider base python3 test_illinois.py python3 benchmark_illinois.py 

# Ne pas lancer T=10000 avant réduction du biais gamma_c. 

## **12. Conclusion de gel** 

**La journée est une réussite : Phase C v4 est validée comme pipeline hybride fiable jusqu’à T=650, avec Turing complet et aucun zéro manquant. Le diagnostic final explique pourquoi Illinois C pur n’est pas encore accepté : gamma_c est une racine de Z_mpfr/RS approchée, mais pas assez proche de mpmath.siegelz. Demain, le travail reprend sur la voie B pour réduire ce biais et viser l’objectif : Illinois C pur, puis test T=10000.** 

