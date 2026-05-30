## **07 — Pavé Primalité, Produit eulérien et lien zéros ↔ nombres premiers** 

Manuel de consolidation pour hprzeta / Riemann_Lab — à intégrer dans le Brain Vault et à enrichir au fil des sessions. Ce document complète le lexique IA/Brain Vault et crée un pilier mathématique dédié à la primalité. 

## **Positionnement dans le projet** 

Le projet Riemann_Lab est très avancé sur le calcul expérimental des zéros, l’optimisation Riemann-Siegel, la validation Turing-Backlund et la Phase C C/libmpfr. Le pilier primalité sert à expliquer pourquoi ces zéros sont importants : ils gouvernent les oscillations dans la distribution des nombres premiers. 

**Règle scientifique : ce pavé primalité documente des liens mathématiques et numériques. Il ne transforme jamais un calcul de zéros en preuve de l’hypothèse de Riemann.** 

## **1. Pourquoi ajouter un pilier primalité ?** 

- Pour relier les zéros non triviaux calculés par Riemann_Lab à la distribution des nombres premiers. 

• Pour expliquer le produit eulérien, la fonction de comptage π(x), la fonction de von Mangoldt Λ(n) et la formule explicite. 

- Pour structurer les anciens fichiers de cours et de tests autour du produit eulérien et des PRNG zêta. 

- Pour éviter que la partie calcul des zéros reste isolée de son sens arithmétique. 

• Pour préparer un futur RAG capable de répondre clairement aux questions : « pourquoi les zéros de zêta parlent-ils des nombres premiers ? ». 

## **2. Éléments déjà repérés dans le projet** 

|Élément repéré|Lecture projet|Action recommandée|
|---|---|---|
|src/tests/cours/n3_<br>Produit_eulériene.py|Cours/test autour du produit eulérien.|Renommer proprement et migrer vers<br>src/calculs/primalite/.|
|src/tests/cours/n3_<br>visualisation_produit_<br>eulérien_et_convergence.py|Visualisation pédagogique du lien ζ(s) et<br>produit sur les premiers.|Conserver comme exemple pédagogique.|
|src/tests/prng_zeta_aleatoire.p<br>y et PRNG_ZETA.py|Exploration expérimentale zêta/aléatoire.|Classer dans legacy/prng puis auditer.|
|Fichiers niveau 5 liés à formule<br>explicite / statistiques|Pont potentiel entre zéros, π(x), GUE et<br>premiers.|Créer une page Vault dédiée au lien zéros<br>↔ premiers.|
|Phase C et<br>compute_zeros_v4.py|Calcul/affinage des zéros.|Relier les sorties validées à des<br>visualisations π(x), Li(x), oscillations.|



## **3. Structure Brain Vault à ajouter** 

brain-vault/02_math_zeta/primalite/ ├── 00_index_primalite.md ├── 01_lexique_primalite.md ├── 02_nombres_premiers.md ├── 03_tests_primalite.md ├── 04_crible_eratosthene.md ├── 05_produit_eulerien.md ├── 06_fonction_pi_x_et_Li.md ├── 07_von_mangoldt.md ├── 08_formule_explicite.md ├── 09_lien_zeros_premiers.md ├── 10_experiences_numeriques.md └── 99_limites_conjectures_preuves.md 

Cette structure sépare les bases arithmétiques, les algorithmes, les formules liées à ζ(s), les expériences numériques et les limites scientifiques. 

## **4. Structure code recommandée** 

src/calculs/primalite/ ├── __init__.py ├── crible_eratosthene.py ├── miller_rabin.py ├── produit_eulerien.py ├── fonction_pi_x.py ├── von_mangoldt.py ├── formule_explicite.py ├── visualisation_premiers.py └── tests_primalite.py 

docs/primalite/ ├── README.md └── exemples.md 

Le code primalité doit rester séparé de src/calculs/optimisation/ afin de ne pas mélanger la détection des zéros et les expériences arithmétiques. 

## **5. Lexique primalité initial** 

## **Nombre premier** 

Entier naturel supérieur à 1 qui possède exactement deux diviseurs positifs : 1 et lui-même. 

## **Nombre composé** 

Entier naturel supérieur à 1 qui n’est pas premier, donc factorisable en plusieurs facteurs non triviaux. 

## **Factorisation unique** 

Théorème fondamental de l’arithmétique : tout entier supérieur à 1 se décompose de manière unique en produit de nombres premiers, à l’ordre près. 

## **Crible d’Ératosthène** 

Algorithme qui génère les nombres premiers jusqu’à une borne N en éliminant les multiples. 

## **Test de primalité** 

Procédure décidant ou estimant si un entier est premier. Peut être déterministe ou probabiliste. 

## **Miller-Rabin** 

Test probabiliste de primalité très rapide, utile en pratique, mais à documenter comme probabiliste sauf bases déterministes adaptées. 

## **π(x)** 

Fonction de comptage des nombres premiers : nombre de premiers inférieurs ou égaux à x. 

## **Li(x)** 

Intégrale logarithmique, approximation classique de π(x). 

## **Théorème des nombres premiers** 

Énonce que π(x) est asymptotiquement équivalent à x/log(x). 

## **Produit eulérien** 

Identité reliant ζ(s) aux nombres premiers : ζ(s)=∏p (1-p^{-s})^{-1} pour Re(s)>1. 

## **Λ(n)** 

Fonction de von Mangoldt : log(p) si n est une puissance de premier p^k, 0 sinon. 

## **ψ(x)** 

Fonction de Chebyshev pondérée par Λ(n), souvent plus naturelle que π(x) dans la formule explicite. 

## **Formule explicite** 

Formule reliant une fonction de comptage des premiers aux zéros de ζ(s). 

## **Oscillations** 

Écarts entre π(x), Li(x), ψ(x) et leurs approximations, influencés par les zéros non triviaux. 

## **RH et premiers** 

L’hypothèse de Riemann impose des bornes fortes sur l’erreur dans la distribution des nombres premiers. 

## **6. Chemin pédagogique du pavé primalité** 

|Niveau|Sujet|Objectif pédagogique|
|---|---|---|
|Niveau 1|Divisibilité, premiers, composés|Comprendre ce qu’est un premier et pourquoi la factorisation est<br>centrale.|
|Niveau 2|Cribles et tests|Savoir générer et tester des premiers expérimentalement.|
|Niveau 3|Produit eulérien|Voir le premier pont profond entre ζ(s) et les nombres premiers.|
|Niveau 4|π(x), Li(x), PNT|Comprendre la répartition moyenne des nombres premiers.|
|Niveau 5|Λ(n), ψ(x), formule explicite|Relier les zéros de ζ aux fluctuations des premiers.|
|Niveau 6|Expériences Riemann_Lab|Utiliser les zéros calculés pour visualiser des oscillations sans<br>prétendre prouver RH.|



## **7. Pont formel : zêta, Euler, premiers** 

Le point d’entrée du pavé primalité est le produit eulérien. Il exprime que la fonction zêta encode la multiplicativité des entiers et la structure des nombres premiers. Pour Re(s)>1 : 

ζ(s) = Σ_{n≥1} 1/n^s = ∏_{p premier} 1 / (1 - p^{-s}) 

Ce pont justifie que l’étude analytique de ζ(s), y compris ses zéros, possède des conséquences sur la distribution des nombres premiers. 

## **8. Pont expérimental : zéros calculés et distribution des premiers** 

- Les runs v3/v4 produisent des zéros numériques sur la droite critique. 

- Ces zéros peuvent être utilisés dans des visualisations de formules explicites tronquées. 

- Une formule explicite tronquée est une expérience numérique, pas une preuve. 

- Le Vault doit conserver les paramètres : nombre de zéros utilisés, T_MAX, précision, source CSV, commit, date et script. 

- Chaque graphique π(x) vs Li(x) ou ψ(x) reconstruit doit citer les zéros et le run utilisé. 

## **9. Modèle de page Vault : lien zéros ↔ premiers** 

# Lien zéros de zêta ↔ nombres premiers 

## ## Idée courte 

Les zéros non triviaux de ζ(s) contrôlent les oscillations des fonctions de comptage des nombres premiers. 

## ## Objets 

- π(x) : compte les premiers ≤ x 

- Li(x) : approximation de π(x) 

- Λ(n) : fonction de von Mangoldt - ψ(x) : somme de Λ(n) jusqu’à x - ρ : zéro non trivial de ζ(s) 

## ## Expérience Riemann_Lab 

- Run utilisé : <v3/v4, T_MAX, date> 

- Source CSV : <chemin> 

- Nombre de zéros : <N> - Script : <chemin> - Limite : reconstruction tronquée, non preuve 

## À ne pas confondre 

- validation numérique ≠ preuve 

- visualisation ≠ démonstration 

- zéro calculé ≠ connaissance de tous les zéros 

## Tags #primalite #zeta #zeros #formule-explicite #vault 

## **10. Modifications concrètes à faire dans le Brain Vault** 

mkdir -p brain-vault/02_math_zeta/primalite 

cat > brain-vault/02_math_zeta/primalite/00_index_primalite.md <<'EOF' # Index — Primalité et nombres premiers 

Ce dossier relie les calculs de zéros de Riemann_Lab à la distribution des nombres premiers. 

## Pages 

1. Lexique primalité 

2. Nombres premiers 

3. Tests de primalité 

4. Crible d'Ératosthène 

5. Produit eulérien 

6. π(x) et Li(x) 

7. Fonction de von Mangoldt 

8. Formule explicite 

9. Lien zéros ↔ premiers 

10. Expériences numériques 11. Limites, conjectures, preuves EOF 

cat > brain-vault/02_math_zeta/primalite/01_lexique_primalite.md <<'EOF' # Lexique primalité 

- Nombre premier : entier > 1 ayant exactement deux diviseurs positifs. 

- Nombre composé : entier > 1 non premier. 

- π(x) : nombre de premiers ≤ x. 

- Li(x) : approximation analytique de π(x). 

- Λ(n) : fonction de von Mangoldt. 

- ψ(x) : somme de Λ(n) pour n ≤ x. 

- Produit eulérien : lien entre ζ(s) et les premiers. 

- Formule explicite : lien entre zéros de ζ et fonctions de comptage des premiers. EOF 

## **11. Scripts à créer plus tard** 

|Script|Rôle|Priorité|
|---|---|---|
|crible_eratosthene.py|Générer premiers ≤ N pour tests et visualisations.|Haute|
|miller_rabin.py|Tester primalité de grands entiers.|Moyenne|
|produit_eulerien.py|Comparer somme ζ(s) et produit sur les premiers pour<br>Re(s)>1.|Haute|
|fonction_pi_x.py|Calculer π(x), comparer x/log(x), Li(x).|Haute|
|von_mangoldt.py|Calculer Λ(n) et ψ(x).|Haute|
|formule_explicite.py|Expériences tronquées avec zéros calculés.|Après validation v3/v4|
|visualisation_premiers.py|Graphiques pédagogiques pour Wiki/PDF.|Moyenne|



## **12. Conclusion** 

Le pavé primalité doit devenir le deuxième pilier mathématique du projet, complémentaire au pilier calcul des zéros. Le projet aura alors deux colonnes reliées : calculer/valider des zéros, puis expliquer et visualiser leur impact sur les nombres premiers. 

