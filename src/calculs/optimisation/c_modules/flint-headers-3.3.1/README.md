# flint-headers-3.3.1/ — headers FLINT vendorisés (source, pas apt)

## Pourquoi ce dossier existe

`illinois_arb.so` charge en runtime `libflint-24205715.so.21.0.0` (bundlée par le
paquet Python `python-flint` 0.8.0 dans `zeta_env/lib/python3.12/site-packages/
python_flint.libs/`), qui correspond à **FLINT version 3.3.1** exactement
(vérifié via le symbole `flint_version` de la bibliothèque : `nm -D` + lecture
du symbole en mémoire).

Le paquet système `apt install libflint-dev` ne fournit que la **version 3.0.1**
— incompatible en ABI pour les types activement modifiés entre versions comme
`dirichlet_group_t` / `dirichlet_char_t`. Utiliser des headers 3.0.1 pour
appeler une `.so` 3.3.1 risquerait une corruption mémoire silencieuse (mauvais
offsets de champs de structure), pas juste un mauvais résultat numérique.

## Provenance exacte

- Source : `https://github.com/flintlib/flint/releases/download/v3.3.1/flint-3.3.1.tar.gz`
- `flint.h` et `flint-config.h` : générés localement via `./configure`
  (`--with-gmp-include=/usr/include/x86_64-linux-gnu --with-gmp-lib=... --with-mpfr-include=...`)
  puis vérifiés exempts de tout chemin absolu machine-spécifique avant commit.
- Les 21 autres headers : copiés tels quels depuis `flint-3.3.1/src/`, licence
  LGPL d'origine préservée dans chaque fichier (en-tête de copyright FLINT
  intact, aucune modification de contenu).
- Sous-ensemble minimal extrait via fermeture transitive réelle
  (`gcc -M` sur `illinois_arb_lowprec.c`) — 23 fichiers, 276 Ko, plutôt que les
  ~800+ headers de la bibliothèque FLINT complète (dont on n'utilise qu'un
  coin : `acb`/`arb`/`mag`/`arf`/`dirichlet`/`acb_dirichlet`).

## Licence

FLINT est distribué sous LGPL v3 (voir en-tête de chaque fichier). Ces headers
sont des déclarations d'interface (pas d'implémentation), vendorisés à des
fins de compatibilité de build — copyright d'origine FLINT/auteurs préservé.

## Utilisation

```makefile
CFLAGS += -I c_modules/flint-headers-3.3.1
```

Lié à l'exécution contre la `.so` déjà présente dans l'environnement Python
(`python_flint.libs/libflint-24205715.so.21.0.0`) — ces headers ne servent
qu'à la compilation, pas à l'édition de liens d'une nouvelle bibliothèque.

## Ne PAS mettre à jour sans vérifier

Si `python-flint` est mis à jour dans `zeta_env` et bundle une version FLINT
différente, ces headers doivent être régénérés pour la nouvelle version
(revérifier `flint_version` de la `.so` réellement chargée) — un décalage de
version redevient un risque ABI silencieux.

---
*flint-headers-3.3.1/ · c_modules/ · Riemann_Lab_C · hprzeta · 08/08/2026*
