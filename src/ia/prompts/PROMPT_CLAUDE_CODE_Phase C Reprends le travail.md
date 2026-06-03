Phase C — Reprends le travail. 
Hier soir tu as créé illinois_mpfr.c, illinois_mpfr.h, 
z_function.c, z_function.h, Makefile, test_illinois.py.
La compilation fonctionne (zéro warning).
Le bug : Z_mpfr et Z_double ne sont pas cohérentes.
Solution choisie — Option B :
- Détection : mpmath.siegelz (Python) → intervalles garantis
- Affinage : illinois_mpfr C → précision 170 bits
Il reste :
1. Modifier test_illinois.py avec mpmath.siegelz pour la détection
2. Faire passer le test à ≥ 9/10
3. Benchmark C vs mpmath sur 100 zéros
4. Créer compute_zeros_v4.py
5. Rapport v3→v4

Travaille de façon visible — montre chaque fichier 
que tu modifies et chaque commande que tu exécutes.
Demande confirmation avant chaque étape importante.

