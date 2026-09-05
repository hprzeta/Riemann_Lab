# Discussion Claude Code — 5 septembre 2026

> Archive complète de la session du 05/09/2026 — point projet, diagnostic en
> lecture seule du run MARGE=10.0 (segments 0-1), relecture intégrale des 5
> entrées JOURNAL du 18/08, et diff binaire réel `scan_arb.c`/`.so` entre v13
> et v16. Les extraits de code modifiés ne sont pas reproduits ici ; seuls les
> tableaux, rapports, conclusions et les instructions transmises par hprzeta
> sont conservés.

---

## 1. Point projet

**Demande de hprzeta :** « point projet »

Le bloc `PROMPT_REPRISE` de `~/riemann_handoff/Handoff.md` a été affiché tel
quel à l'écran (mécanisme standard du projet), puis résumé en 3 lignes :

1. Dernière MAJ du Handoff : 30/08/2026 — branche active `Riemann_Lab_C`,
   dernier commit `9c72133`, mais déjà 2 commits de plus et 25+ fichiers non
   commités constatés en tête de session (cohérent avec le `git status`
   affiché au démarrage).
2. Trois chantiers en pause depuis le 18/08, jamais revérifiés depuis : Bloc B
   (fiabilité PC1), Bloc C (déficit 177 vs 96 zéros manquants au run T=5M
   v16), et le run MARGE=10.0 (statut inconnu à l'époque).
3. Prochaine action indiquée par le Handoff : trier les fichiers non commités
   avant toute chose, puis vérifier l'état réel du run MARGE=10.0.

---

## 2. Diagnostic run MARGE=10.0 (segments 0-1) — lecture seule stricte

**Instruction explicite de hprzeta :**
> « Reprise Objectif 1 (calcul des zéros) après une parenthèse infra. NE
> RELANCE RIEN, NE TUE RIEN sans mon accord explicite — cette étape est un
> diagnostic en lecture seule. [...] Objectif final : investiguer les 96
> zéros manquants du run T=5M (paires de zéros proches, pas de changement de
> signe sur la grille Z_double). »

### Le run tourne-t-il encore ? Non — confirmé sur 4 axes indépendants

| Vérification | Résultat |
|---|---|
| `pgrep`/`ps` sur `compute_zeros*` | Aucun process actif |
| `tmux ls` | 1 session (`zeta-cluster`) — layout de monitoring standard, panes en échec SSH (bastion injoignable) ou shell idle, aucune trace de calcul |
| `systemd-inhibit --list` | Aucun verrou de calcul actif |
| PID enregistré (`logs/run_T5000000.pid`) | Process inexistant |

### Où s'est-il arrêté ?

Deux runs distincts, à ne pas confondre :

- **Run principal T=5M v16** (`logs/run_T5000000_20260816_193542.log`) :
  terminé proprement (10 016 297/10 016 474 zéros), puis crash PC1 pendant le
  rescan qui a suivi — résultat perdu (déjà connu, bug corrigé depuis).
- **Test A/B MARGE=2.0 vs MARGE=10.0 sur segments 0-1** `[14, 1 391 397]` :
  en réalité **déjà terminé et déjà rapporté** dans `JOURNAL.md` le 18/08 à
  22h30 — le Handoff n'avait simplement jamais été resynchronisé avec cette
  information après le 18/08. Ce n'est pas une anomalie de calcul, c'est une
  dette de documentation.

| | MARGE=2.0 | MARGE=10.0 |
|---|---|---|
| Zéros trouvés | 2 504 087 | 2 504 024 |
| Écart | — | **−63** |

Comparaison zéro à zéro (plus proche voisin) : 70 zéros perdus, 7 gagnés.

**CSV bruts introuvables** : les dossiers `calculs/margeB2`, `margeB10`,
`margeC2`, `margeC10`, `seg01_marge2`, `seg01_marge10` ont disparu (constat
déjà fait le 19/08, cause jamais élucidée) — confirmés toujours absents ce
jour. Seuls les chiffres agrégés du JOURNAL survivent.

**Validation Turing** : jamais appliquée sur cette zone (segments 0-1) — la
méthode exacte θ(T)+S(T) n'a été utilisée que sur `[4,8M;5M]` (déficit de
fond +8 confirmé, indépendant de MARGE).

### Résumé donné à hprzeta

Run mort (aucun process/session/verrou actif) ; test MARGE=10.0 déjà terminé
et documenté depuis le 18/08 ; CSV non exploitables (dossiers disparus) ;
écart 96→177 toujours entièrement ouvert. **Rien exécuté, rien relancé.**

---

## 3. Relecture intégrale des 5 entrées JOURNAL du 18/08 (12h00 → 22h30)

**Demande de hprzeta :** « Relis les entrées JOURNAL.md du 18/08 en entier »

| Heure | Titre | Conclusion clé |
|---|---|---|
| 12h00 | Run T=5M v16 : résultat perdu | Run principal réussi (177 manquants), mais crash pendant le rescan → 31h37 perdues, rien récupérable. Corrigé (`2f2047a`/`a391beb`). |
| 18h00 | "Paires enjambées" invalidée | Calcul GUE : prédiction M≈0,003–0,33 zéro vs 177/96 observés (écart ×10²–10⁴). **Nuance capitale : le 96 (v13) a été validé par `valider_turing()` ; le 177 (v16) ne l'a jamais été** — crash avant cette étape, CSV `_principal` vide. Run v16 réel définitivement irrécupérable. |
| 19h00 | Turing windowé sur `[4,8M;5M]` | Déficit de fond +8/431 837, identique entre MARGE=2.0 et 10.0 → écarte `MARGE_SECURITE` comme cause à haut T. |
| 20h00 | Clôture math formelle | Vérifications numériques conformes ; 5 fichiers wiki mis à jour (`Formules_zeta` §32, `STACK`, `Bibliotheques` §19, `Bonnes-Pratiques-Claude-Code`, `Guide-Linux-Commandes` §26). |
| 22h30 | Test A/B segments 0-1 | MARGE=10.0 trouve 63 zéros de moins (viole la monotonie attendue), dispersés sur 8 workers. Hypothèses écartées : `max_brackets`, dérive flottante cumulative. Hypothèse ouverte : bruit de phase du signe `Z_double`. |

**Répartition du déficit par segment (v13 réel/validé vs v16 réel/non validé) :**

| Segment | Bornes (t) | v13 | v16 |
|---|---|---|---|
| 0 | [14, 737 112] | +18 | **+51** |
| 1 | [737 112, 1 391 397] | +9 | **+49** |
| 2 | [1 391 397, 2 020 448] | +10 | +16 |
| 3–7 | [2 020 448, 5 000 000] | 13/10/9/14/14 | 13/10/9/14/14 |

Conclusion : l'écart 96→177 est concentré à >90 % dans les segments 0-1
(bas T) ; les segments 2-7 sont quasi identiques entre v13 et v16 (code
prouvé bit-identique par diff). Seule piste non testée à l'époque :
diff binaire `scan_arb.c` (commit `d4b3611`) entre les deux runs.

---

## 4. Diff binaire réel `scan_arb.c`/`.so` entre v13 et v16

**Demande de hprzeta :** « Compare le binaire scan_arb.c entre v13 et v16 (diff) »

### Méthode

`scan_arb.so` s'est avéré versionné dans git aux côtés du `.c` — comparaison
binaire réelle possible (pas une hypothèse de diff source). v13 (run
27-29/06) a tourné avec l'état du commit `7914fa3` (26/06, dernier changement
avant le run) ; v16 (run 16-17/08) avec l'état du commit `d4b3611` (04/07),
inchangé depuis jusqu'au run.

| Binaire | Commit | Taille | SHA-256 (tronqué) |
|---|---|---|---|
| v13 | `7914fa3` | 16 104 octets | `9f89eb75a8bd2f00...` |
| v16 | `d4b3611` | 16 216 octets | `a0ad840400f5db8c...` |

**Confirmé : v13 et v16 n'ont jamais exécuté le même code machine.**

### Changement fonctionnel identifié

Le commit `d4b3611` (« cache log_n/isqrt_n RS ») remplace, dans la boucle
Riemann-Siegel de `Z_double()`, une division directe par un terme précalculé
et mis en cache, réutilisé par multiplication. En arithmétique IEEE-754, une
division directe et une multiplication par un inverse précalculé ne
garantissent pas le même résultat au dernier bit — un bruit de quelques ULP
est donc introduit sur **chaque** évaluation de Z(t) dans tout le run (le
cache couvre la totalité de la plage `[14, 5M]`, pas seulement le bas de la
plage). Le reste du diff est purement cosmétique (nommage de constante,
commentaires) — aucun autre écart de comportement.

### Portée et limite

Ce mécanisme correspond exactement à l'hypothèse de bruit de phase du signe
`Z_double` évoquée le 18/08 à 22h30 — désormais rattachée à une ligne de code
et un commit précis, alors qu'elle n'était qu'une conjecture non vérifiée.
**Limite non résolue** : ce bruit s'applique uniformément sur toute la plage
T, alors que le déficit anormal reste concentré à bas T (segments 0-1) — ce
candidat ne suffit donc pas seul à expliquer la concentration observée. Piste
plausible mais partielle, pas une clôture du dossier.

### Prochaine action proposée (non lancée)

Test A/B ciblé binaire `7914fa3` vs `d4b3611` sur les segments 0-1 exacts,
pour mesurer si le retour à la division directe change le compte de zéros.
**Non exécuté — en attente d'un accord explicite de hprzeta.**

---

## 5. Clôture de session

**Demande de hprzeta :** « ok on reprend demain. Met à jour les fichiers qui
faut et bye bye »

**Fichiers mis à jour :**

| Fichier | Action |
|---|---|
| `~/riemann_handoff/Handoff.md` (local, hors dépôt) | Nouvelle entrée `PROMPT_REPRISE` du 05/09 ajoutée en tête, résumant le diagnostic, la relecture JOURNAL et le diff binaire ; prochaine action priorisée |
| `Riemann_Lab.wiki/JOURNAL.md` | Nouvelle entrée datée 2026-09-05 ajoutée en tête (append-only), committée et poussée (`84d24e1`) |
| `docs/archive/discusion_claude_2026-09-05.md`/`.pdf` | Cette archive |

**Volontairement non touché** : `Architecture-Cluster-Zeta.md` et
`Diagnostic-WireGuard-Hotspot.md` du wiki portaient déjà des modifications
locales non commitées, sans rapport avec cette session — laissés intacts
pour ne pas écraser un travail en cours de hprzeta.

**Reste ouvert pour la prochaine session** (rien n'a été retouché) :
- Décider si le test A/B binaire `scan_arb.c` (segments 0-1) doit être lancé.
- Trier/committer les 25 fichiers non commités sur `Riemann_Lab_C`.
- Bloc B (`smartctl`/`dmesg` PC1), WireGuard PC4 / DuckDNS, backup PC3.

---

*Document généré à la demande de hprzeta le 05/09/2026 — archive de session,
Claude Code — Riemann_Lab, branche `Riemann_Lab_C`.*
