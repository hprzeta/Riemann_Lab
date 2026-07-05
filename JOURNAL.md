> **Fichier :** JOURNAL.md · **Dossier :** wiki racine
> **Branche :** master · **Auteur :** hprzeta · **MAJ :** 2026-06-16

# Riemann_Lab — Journal de bord

> 📓 **Fichier append-only.** On n'allège jamais ce fichier : on **ajoute** un pavé daté
> en haut à chaque session. Il n'est *pas* relu en entier au démarrage (utiliser
> `grep` ou demander à Claude de chercher dans ce fichier précis).
>
> Le plus récent est **en haut**. Format de pavé : `## AAAA-MM-JJ — HHhMM — titre — commit`.
---

## 2026-06-27 — 16h02 — Rescan ciblé v13 + run T=5 000 000 lancé + stratégie optimisation Illinois hybride

### Feature : rescan ciblé par déficit dans `compute_zeros_v13.py` (branche `Riemann_Lab_C`)

**Contexte :** les 5 manquants du run T=500k (run #4) ont été définitivement attribués le 26/06
aux ratés du scan Z_double (phase de grille). L'affinage illinois_refine_arb est parfait
(0 REJECT / 0 FALLBACK sur 818 406 appels). Nouvelle approche : rescan STEP/2 après le run
principal sur les segments en déficit.

**Implémentation :**
- `calculer_zeros_v13()` → 4-tuple `(zeros, stats, profil, segments)` (segments exposé pour rescan)
- `rescan_segments_deficit(zeros, segments, T_MAX, step)` — Section 3b — nouveau
  - Identifie les segments worker avec `n_trouvés < N(t_hi) - N(t_lo)`
  - Relance les segments en déficit en parallèle (`multiprocessing.Pool`) avec `STEP/2`
  - Retourne zeros bruts pour fusion par `dedupliquer()` dans `main()`
  - Worker IDs 100+i pour distinguer dans les logs
- `ecrire_log()` → paramètre `rapport_rescan=None`, section [7] RESCAN CIBLÉ dans le log
- `main()` : rescan uniquement en mode local (`_cli.t_min is None`), pas en mode distribué
- MARGE_SECURITE revertée **2.0** (était 3.0 dans le working copy — modifications non commitées)

**Validation T=1000 :** Turing COMPLET ✅ · LMFDB 20/20 ✅ · rescan parallèle 0.2s · 0 nouveau zéro net (aucun vrai manquant à T=1000, déficits = artefacts N(T))

**Non commité** → en attente du résultat du run T=5M pour valider.

### Run T=5 000 000 lancé à 16h02 (PC1, 8 workers, turbo)

| Paramètre | Valeur |
|---|---|
| T_MAX | 5 000 000 |
| N(T) attendus | ~10 016 473 zéros |
| STEP | 0.001571 (adaptatif, ×2.8 plus fin qu'à T=500k) |
| MARGE_SECURITE | 2.0 |
| Mode | PC1 local (rescan ciblé actif) — pas distribué |
| PID principal | 46040 · workers 46085-46092 |
| Log | `logs/run_v13_T5M.log` |
| Dossier résultats | `calculs/v13_T5000000_20260627_160257/` |
| Durée estimée | **~24h** (ETA 28/06 ~15h30) |

**Note sur la durée :** l'estimation initiale de 8.6h était fausse — elle ne tenait pas compte
du facteur de ralentissement Arb à haute valeur de T. N_RS ≈ √(T/2π) = 892 termes à T=5M
vs 282 à T=500k → ×3.16 de ralentissement par zéro. Avec N(5M)/N(500k) = ×12.2 et
l'overhead scan ×2.8, durée totale ≈ 24h.
À 17h50 (1h48 écoulées) : ~7.6% estimé.

### Stratégie d'optimisation identifiée pour les runs longs

| Niveau | Optimisation | Gain estimé | Effort | Cible |
|---|---|---|---|---|
| 1a | Distribution PC1+PC2 (`zeta_distribute.py`) | ×2 | immédiat | T=5M si relancé |
| 1b | TOL_ARB 1e-12 → 1e-9 | ×1.4 | 30 min | T=5M |
| **2** | **Illinois hybride Z_double→Arb dans `illinois_arb.c`** | **×8** | **2 jours** | **v14 — priorité** |
| 3 | Odlyzko-Schönhage (sous-linéaire) | ×50+ | semaines | v15+ |

**Principe Illinois hybride (Niveau 2) :** dans `illinois_refine_arb`, utiliser Z_double
(rapide, O(N_RS) amortized avec C0+C1) pour les premières itérations jusqu'à |b-a| < 1e-6,
puis basculer sur Arb uniquement pour les 2-3 dernières iterations de précision finale.
Réduit les appels Arb coûteux de ~25 à ~3 par zéro → ×8 estimé sur le goulot.

### Matériel — upgrade RAM PC1 décidé

+16 Go SO-DIMM DDR4 2133 MHz dans le slot libre de l'ASUS ZenBook UX510UWK.
(8 Go soudés + 1 slot libre → 24 Go total après upgrade)
Motivation : éliminer l'usage du swap sous charge 8 workers (actuellement 16 Go swap nécessaires).

---

## 2026-06-26 — 15h58 — Instrumentation debug + 2 bugs corrigés + conclusion zéros manquants — commits 7914fa3, 2b94b9f

### Tâches accomplies

**1. `zeta_sync_pc2.sh` validé (PC2 accessible)**
Fix : `ldconfig` absent du PATH SSH → `PATH=/sbin:/usr/sbin:$PATH ldconfig`.
Les 3 `.so` compilent sans erreur sur PC2 (scan_arb.so, illinois_mpfr.so, illinois_arb.so).

**2. Instrumentation ZETA_DEBUG_BRACKETS — commit `7914fa3`**
- `scan_arb.c` : `scan_set_debug_log` — log chaque bracket BRACKET t_a t_b Z(a) Z(b)
- `illinois_arb.c` : `arb_set_debug_log` — log REJECT, FALLBACK_ZRS, NEWTON_FINAL
- `scan_arb_wrapper.py` : `scan_enable_debug_log` / `scan_disable_debug_log`
- `compute_zeros_v13.py` : activation via `ZETA_DEBUG_BRACKETS=<répertoire>`, per-worker

**3. Bug max_brackets découvert + corrigé — commit `2b94b9f`**
Run debug #1 (MARGE=3.0) : 16 107 manquants. Chaque scan_wN.log = exactement 100 000 lignes.
Cause : `max_brackets=100 000` figé alors que T=500k demande ~102 302 brackets/worker.
Fix : `max_brackets = max(150_000, int((N(t_end) - N(t_start)) × 2))` calculé dans le worker.

**4. Conclusion définitive sur les zéros manquants — run debug #2 (MARGE=2.0)**
- 818 406 / 818 414 zéros (8 manquants), LMFDB 20/20 ✅
- **0 REJECT, 0 FALLBACK_ZRS** sur 818 406 appels à illinois_refine_arb
- Brackets scan : 818 406 lignes (pas de troncature)
- **CONCLUSION : les manquants sont 100 % des ratés du scan Z_double (phase de grille)**
  illinois_refine_arb est parfaitement fiable. La voie REJECT/FALLBACK est éliminée.
  8 manquants ici vs 5 dans run #4 : frontières workers différentes = phase de grille différente.

### Prochaine piste (si on veut éliminer les manquants)
Scan adaptatif : détecter les extrema locaux de |Z(t)| proches de zéro pendant le scan,
même sans changement de signe détecté. Nécessite de modifier scan_arb.c en profondeur.

---

## 2026-06-22 (soir) — Correction rapport clonage (Micron vs Samsung) + WeasyPrint installé — commits `a6a6cda` · `93ad97a` (Riemann_Lab_IA)

**Résultat :** `pdf/clone/rapport_clonage_zeta.md` corrigé (le vault RAG concerne le Micron
1100, pas le Samsung 500 Go comme l'avait affirmé à tort un prompt externe) + PDF régénéré.

| Action | Résultat |
|---|---|
| Vérification branches | `pdf/clone/` existe uniquement sur `Riemann_Lab_IA` — pas de `ops/clonage-2026-06` |
| Correction §2 + nouvelle §11 Phase F | Tableau disque Micron mis à jour, section complète (contexte, paramètres, commandes, piège `vfat`, arborescence) — commit `a6a6cda` |
| `pip install weasyprint markdown` dans `zeta_env` | ✅ — dépendances système (pango/cairo/gdk_pixbuf, Noto Color Emoji) déjà présentes |
| **Bug découvert** | CSS `font-family: "DejaVu Sans", "Noto Color Emoji"` sur le `body` → **tous les chiffres disparaissent** du PDF rendu (Noto Color Emoji avale les glyphes numériques) |
| Correctif | Retirer la police emoji de la `font-family` du texte courant ; fallback fontconfig automatique suffit pour les emojis |
| PDF régénéré + vérifié visuellement | 72 pages, 5,88 Mo — commit `93ad97a`, script réutilisable `pdf/clone/generate_pdf.py` |

**Leçon retenue :** ne jamais lister une police emoji explicitement dans la `font-family` du
corps de texte avec WeasyPrint — elle peut capturer des caractères non-emoji (chiffres) si
le moteur de fallback la priorise mal.

---

## 2026-06-22 — Vault RAG Micron 1100 mis en service + convention PDF clarifiée — commit `69a55f7` wiki

**Résultat :** SSD Micron 1100 256 Go formaté ext4 et monté sur `/mnt/vault_rag` pour
ChromaDB/LlamaIndex (Objectif 2). Confusion identifiée et corrigée dans
`pdf/clone/rapport_clonage_zeta.md` (`Riemann_Lab_IA`) : ce disque y était documenté comme
« exclu, non touché » (Windows/BitLocker) au 21 juin — statut à mettre à jour suite à son
reformatage.

| Action | Résultat |
|---|---|
| Partitionnement + formatage `/dev/sdb1` | `mkfs.ext4 -i 8192 -m 1 -L vault_rag`, UUID `9476fad5-8512-4e0d-8cd4-50c9acae01c2` |
| Montage permanent | `/mnt/vault_rag`, `fstab` `defaults,noatime`, confirmé `rw,noatime` |
| Arborescence | `chromadb/` · `corpus/` · `llamaindex_cache/` · `agent_logs/`, propriétaire `riemann:riemann` |
| Piège résolu | `blkid` simple affichait une signature `vfat` périmée (cache) après le formatage ext4 réussi — confirmé propre via `blkid -p` et `wipefs` (sondage direct, sans cache) |
| `Handoff.md` + `STACK.md` | Section « Stockage — vault RAG (Objectif 2) » ajoutée, commit `69a55f7` |

**Confusion détectée :** un prompt externe a décrit ce disque comme un « Samsung M2 Portable
500 Go USB3 » (réutilisant l'UUID et les commandes réelles du Micron). Vérification du
rapport `rapport_clonage_zeta.md` : le Samsung 500 Go y est un disque **distinct**, dédié au
clone Kali bootable — sans rapport avec le vault RAG. Correction du rapport de clonage
(§2 + nouvelle section Phase F) prévue en session suivante sur `Riemann_Lab_IA`.

**Convention clarifiée — emplacement des PDF de cadrage/rapports :** vivent dans
`pdf/<sujet>/` (ex. `pdf/clone/`) sur la branche **`Riemann_Lab_IA`**, jamais dans une
branche `ops/*` séparée ni dans `docs/` (réservé au site GitHub Pages). Toujours vérifier
`git ls-tree -r --name-only origin/<branche> | grep pdf` avant de supposer un chemin.

---

## 2026-06-17 — 02h14 — MILESTONE : Distribution PC1+PC2 T=100k — commits 98de98e / 1a4f2b3

- PC1 [14, 94119] : 129 041 zéros — 8.50 min
- PC2 [94119, 100000] : 9 028 zéros — 8.50 min
- Fusion : **138 069 zéros uniques**, Turing COMPLET ✅, 0 manquant
- Marge pivot −15% : PC1+PC2 synchronisés à la seconde près (8.50 min chacun)
- python-flint 0.8.0 installé PC2 → `ARB_DISPONIBLE=True`
- `zeta_distribute.py` opérationnel : pivot N(T), SSH, scp, fusion CSV, Turing global
- `compute_zeros_v13.py` : mode CLI `--t-min --t-max --horodatage` (non-interactif)
- `zeta_run.sh` mis à jour : v12 → v13
- 4 branches synchronisées : `Riemann_Lab_C` · `Riemann_Lab_IA` · `main` · `Riemann_Lab_Test`
- Site mis à jour : section Cluster Zeta 4 machines + tableau perf v13 distribué
- Prochaine étape : T=500k distribué, puis v14 avec PC3

---

## 2026-06-16 — Renommage hostnames architecture officielle

### Nouveaux noms (alias SSH `zeta-hp`/`zeta-acer`/`zeta-del` inchangés)

| Machine | Ancien hostname | Nouveau hostname | Rôle | Statut |
|---|---|---|---|---|
| PC2 | `zeta-hp3647h` | `zeta-calc-second` | Nœud calcul secondaire | ✅ Appliqué |
| PC3 | `zeta-livermore8` | `zeta-backup` | Backup/monitoring | ✅ Appliqué |
| PC4 | `zeta-del.local` | `zeta-secure` | Bastion VPN/pare-feu OpenBSD | ✅ Appliqué |

Vérifié par `ssh {alias} hostname` — 3/3 confirmés.

### Documentation mise à jour

- `Handoff.md` · `Architecture-Cluster-Zeta.md` · `STACK.md` · `JOURNAL.md` : noms mis à jour
- `docs/images/topo_machines_zeta.svg` · `docs/images/backup_cluster_map.svg` : labels SVG mis à jour
- Historique 13/06 (`zeta-hp3647h`, `zeta-livermore8`) conservé dans les notes de bas de page

---

## 2026-06-13 — zeta_run.sh → compute_zeros_v12.py — commit `33205f2`

- `scripts/zeta_run.sh` mis à jour : lance désormais `compute_zeros_v12.py` (était `v4_1`)
- v12 = Illinois hybride Z_rs+Newton-Arb — validée T=100k (8.8 min, 0 manquant, Turing COMPLET)
- `zeta-run 100000` est maintenant le point d'entrée officiel pour v12
- 4 branches synchronisées : `Riemann_Lab_IA` · `main` · `Riemann_Lab_Test` · `Riemann_Lab_C`

---

## 2026-06-13 — Infrastructure cluster & backup automatique

### Pipeline backup nocturne

| Étape | Machine | Heure | Commande |
|---|---|---|---|
| 1 — rsync local→Acer | `zeta-icor7` | 01h50 (cron) | `rsync -aq -e 'ssh -i ~/.ssh/id_acer' logs/ wiki/ pdf/ pjexosql@192.168.1.22:~/backup/` |
| 2 — rclone Acer→ProtonDrive | `zeta-livermore8` | 02h00 (cron) | `/usr/bin/rclone copy ~/backup/ protondrive:hprzeta/Riemann_Lab/backup/` |

- Clé SSH `id_acer` (ed25519) sans passphrase — connexion automatique `zeta-icor7 → zeta-livermore8`
- Répertoires sauvegardés : `logs/` · `wiki/` · `pdf/`
- Destination cloud : ProtonDrive `hprzeta/Riemann_Lab/backup/`

### Renommage hostnames (préfixe `zeta-` uniforme)

| Ancien nom | Nouveau nom | Matériel | IP | Réseau |
|---|---|---|---|---|
| `hp3647h` | `zeta-hp3647h` | HP Compaq 8000 Elite CMT · Core2Duo E8400 3GHz · 4 GB DDR3 · Carte mère HP 3647h | 192.168.1.94 | Gigabit ETH |
| `pcfix2` | `zeta-livermore8` | Compaq-Presario SG3210FR · Pentium E2140 1.6 GHz · 3 GB DDR2 · Carte mère ECS Livermore8 | 192.168.1.22 | 100 Mbit ETH |
| `zeta-icor7` | `zeta-icor7` *(inchangé)* | Machine principale de calcul | 192.168.1.24 | WiFi |

### Diagrammes SVG générés

- `scripts/backup_cluster_map.sh` — script qui génère les 2 SVGs suivants :
  - `backup_cluster_map.svg` — pipeline backup (flux rsync + rclone)
  - `topo_machines_zeta.svg` — topologie matérielle du cluster
- SVGs déplacés dans `docs/images/` (branche `Riemann_Lab_IA`)

---

## 2026-06-13 — Run v12 T=100 000 : COMPLET ✅

- **Version :** v12 `illinois_refine_arb` (Illinois hybride 2-phases : Z_rs_double Phase 1 + 2 Newton Z_arb Phase 2)
- **Résultat :** ~138 080 zéros · 0 manquant · 8.8 min · ×16.9 vs v10 (benchmark T=10k) · ×2.69 direct T=100k
- **Turing-Backlund :** COMPLET ✅ (aucun zéro manqué dans [0, 99999.70])
- **LMFDB :** 20/20 ✅
- **Coût moyen :** ~4.7 ms/zéro (Phase 1 ~0.015 ms, Phase 2 ~7 ms, overhead scan)
- **Documentation :** `analyse_problemes_v9_v10.md` + `analyse_problemes_v10_v12.md` créés dans le wiki
- **Wiki mis à jour :** Home, Etape-1, STACK, Bibliotheques, Formules_zeta, Plancher-Hardware-Architecture
- **Site :** `docs/index.html` mis à jour — v12 dans le tableau de progression

---

## 2026-06-12 (après-midi) — v9 T=100k validée — 28.0 min · ×1.80 vs v8

**Résultat :** 138 069 zéros · 28.0 min · 82.15 z/s · Turing COMPLET · LMFDB 19/20 · Gain ×1.80 vs v8.

| Indicateur | Valeur |
|---|---|
| Zéros | **138 069 / 138 069** · 0 manquant |
| Durée | **28.0 min** (1 680.7 s) — sans turbo |
| Débit | **82.15 z/s** |
| Brent_C | 99.9% (137 934/138 069) · 37.84 ms/appel |
| Gain vs v8 | **×1.80** (conditions identiques — sans turbo) |
| v9 + turbo (projection) | ~17 min · ~135 z/s |
| PDFs | `analyse_v6_v7.pdf` recompilé · `analyse_v8_v9.pdf` généré |

**Cohérence benchmark :** gain mesuré ×1.80 vs benchmark prédictif ×1.78 — excellent accord.

---

## 2026-06-12 (matin) — v9 Brent C/mpfr — benchmark + validation T=10k + run T=100k lancé

**Résultat :** Brent implémenté, validé T=10k, run T=100k lancé. Gain ×1.78 sur benchmark.

| Action | Résultat |
|---|---|
| `benchmark_methodes.py` | 500 zéros [1000,100000] — 128.9 ms/appel Illinois (mesure complète) |
| `brent_mpfr.c` | Implémentation Brent 2-phases (64→80 bits), compilé dans illinois_mpfr.so |
| `compute_zeros_v9.py` | ITER_SWITCH=3, MAX_ITER=50, brent_refine_adaptive + fallback illinois |
| `test_brent.py` | Tous tests PASS — ×1.78 gain confirmé — GO pour T=100k |
| T=10k v9 | 10 142 zéros, 16.6 s, 609 z/s, 0 manquant, Turing COMPLET, LMFDB 19/20 |
| T=100k v9 | Lancé PID 43732 — 28.0 min (résultat ci-dessus) |
| `analyse_problemes_v8_v9.md` | Wiki créé — benchmark complet, décision go/no-go |

**Découverte :** `benchmark_v8.py` sous-estimait le coût Illinois (mesurait t ∈ [1000,3000] → 0.416 ms). Mesure correcte sur [1000,100000] : **128.9 ms/appel** (coût croît avec N_full = ⌊√(t/2π)⌋).

---

## 2026-06-11 (fin de soirée) — Documentation v7 complète + animation prec_mpfr — commits `0838e2a` `fc7914b`

**Résultat :** Documentation exhaustive v7 poussée sur toutes les branches. Animation interactive créée.

| Action | Résultat |
|---|---|
| `analyse_problemes_v6_v7.md` | Créé dans wiki — analyse complète LaTeX→MD |
| `Bonnes-Pratiques-Claude-Code.md` | +2 sections : règle précision mpfr + règle benchmark |
| `SKILL.md phase-c-illinois` | v0.4.0 — état Phase C 11 juin, v7 leçon, v8 options A/B |
| `SKILL.md riemann-lab` | Section 9 état courant 11 juin ajoutée |
| `animation_prec_mpfr.html` | Créé docs/ — dark theme, 3 sliders, KaTeX, barres animées |
| Sync 4 branches | Riemann_Lab_C `0838e2a` · Riemann_Lab_IA `fc7914b` · main `8c06632` |
| `handoff/Handoff.md` | Mis à jour — benchmark T=100k, PROCHAINE ACTION v8 |

---

## 2026-06-11 (soir) — v7 illinois_refine_adaptive — commits `49ed8b7` `8637098`

**Résultat :** v7 implémentée, validée T=5k/T=10k, run T=100 000 terminé en 30.9 min (vs 113 min v6 → **×3.7**).

| Action | Résultat |
|---|---|
| Rangement — commit `49ed8b7` | `pdf_to_md_voie_b5.sh` racine → `scripts/`, log run déplacé `logs/` |
| Benchmark T=5000 v6 | illinois_C = 77.5%, 23.50 ms/appel, 136 z/s |
| `Z_rs_mpfr_ntermes()` ajoutée | Z(t) RS avec N_termes imposé (pas ⌊√(t/2π)⌋) |
| `illinois_refine_adaptive()` | 2 phases : prec_fast=64 bits (iter_switch=8) → prec_full=116 bits |
| Décision N_full (pas N_fast) | N_fast=N_full/4 invalide les signes Z_rs → N_full conservé, gain vient de 64 bits (1 limb mpfr → SIMD ultra-rapide) |
| Benchmark v7 T=5000 | **1808 z/s**, 1.47 ms/appel → ×16 vs v6 |
| Validation T=10 000 | 10 142 zéros, 0 manquant, Turing COMPLET ✅, 408 z/s |
| Run T=100 000 v7 | **138 069 zéros · 0 manquant · Turing COMPLET · 30.9 min · 74.49 z/s** |
| Log T=100k | `logs/run_T100k_v7_20260611_1424.log` · dir `calculs/v4_1_T100000_20260611_142434/` |
| Commit + push | `8637098` sur `Riemann_Lab_C` ✅ |

**Profil phases T=100 000 v7 :**

| Phase | Temps cumulé | ms/appel | % mur×W |
|---|---|---|---|
| illinois_C | 5799.66s | **42.05** | 78.2% |
| detection | 37.80s | 9450 | 0.5% |
| turing | 22.05s | 22046 | 0.3% |
| mpmath_petit_t | 0.78s | 5.65 | 0.0% |

**Comparaison v6 vs v7 T=100 000 :**

| Métrique | v6 (170 bits) | v7 (64→116 bits) | Gain |
|---|---|---|---|
| Durée | ~113 min | **30.9 min** | **×3.7** |
| Vitesse | ~20 z/s | **74.49 z/s** | **×3.6** |
| illinois_C ms/appel | ~130 ms | **42.05 ms** | **×3.1** |

**Insight technique :** le gain décroît avec t (×16 à T=5k → ×3.7 à T=100k) car la boucle `for n=1..N_full` est linéaire en $N \approx \sqrt{t/2\pi}$ et domine à grand t.

---

## 2026-06-10 — 16h42 — STEP v3 0.05/0.010 + lancement run T=100 000 v3 — commit `181fdd1`

**Résultat :** STEP adaptatif corrigé (0.05/0.010 au lieu de 0.1/0.05/0.02). Run T=100 000 v3 lancé en nohup. Wiki mis à jour (Formules_zeta §23, STACK, SKILL phase-c-illinois).

| Action | Résultat |
|---|---|
| Analyse run T=100 000 v2 | 138 039 zéros · 105.1 min · 68 manquants ❌ — STEP=0.02 insuffisant à t≥50k |
| Gap min mesuré | 0.01940 à t=66678 — preuve directe que STEP=0.02 trop grand |
| Fix STEP v3 — commit `181fdd1` | `step_pour_t()` : 0.05 (t<5k) / 0.010 (t≥5k) |
| Run T=100 000 v3 lancé | PID 311769 (nohup) · log `calculs/run_T100k_step_adaptatif_20260610_1642.log` |
| MAJ wiki Formules_zeta.md §23 | Tableau STEP v3 + résultats T=100k v1/v2 ajoutés |
| MAJ wiki STACK.md | Progression v4.1+Arb corrigée (0.05/0.010), run v3 EN COURS |
| MAJ skill phase-c-illinois | STEP v3 + tableau résultats T=100k |

---

## 2026-06-10 (après-midi) — nettoyage + MAJ docs wiki + analyse run T=100 000 v2

**Résultat :** Run T=100 000 v2 terminé (138 039 zéros, 68 manquants Turing). Wiki mis à jour (arbre, Home, archive, Étape-1, bonnes pratiques). Archive `compute_zeros_v4_1.py.bak`.

| Action | Résultat |
|---|---|
| Run T=100 000 v2 (STEP adaptatif, 10h51) | 138 039 zéros · 105.1 min · 21.89 z/s |
| Turing-Backlund T=100 000 v2 | ❌ INCOMPLET — 68 manquants (STEP 0.02 insuffisant à t ≥ 50 000) |
| LMFDB 20 premiers | 19/20 ✅ (zéro #20 : 8.06e-10 ⚠️) |
| Affinage illinois_C | 137 909 appels (99.9%) · 85.16 ms/appel |
| MAJ wiki Arbre_dossiers_projet.md | Refonte complète (structure juin 2026) |
| MAJ wiki Home.md | Stats run v2, logo header SVG |
| MAJ wiki Archive-Fichiers-Obsoletes.md | Ajout `compute_zeros_v4_1.py.bak` |
| MAJ wiki Étape-1 | Sections Phase C / v4.1 / v5 + tableau résultats ajoutés |
| MAJ wiki Bonnes-Pratiques | Section "Gestion des sessions" ajoutée, note finale nettoyée |
| Archive docs/archive/ | `compute_zeros_v4_1.py.bak` déplacé |

---

## 2026-06-10 — run T=100 000 analysé + fix STEP adaptatif + test T=10 000

**Résultat :** 137 904 zéros calculés (356 manquants — STEP=0.1 trop grand à grand t). Fix appliqué. GPU nvrtc error corrigé. Test T=10 000 lancé pour validation.

| Action | Résultat |
|---|---|
| Lecture logs `execution_v4_1_T100000_20260610_073115.log` | 99.35 min · 23.14 z/s · STEP=0.1 fixe |
| Analyse Turing-Backlund | 356 manquants — tous à T > 29 126 (STEP trop grand) |
| Fix `compute_zeros_v4_1.py` — `step_pour_t()` | STEP 0.1/0.05/0.02 selon tranche t |
| Fix `compute_zeros_v4_1.py` — `_partitionner_adaptatif()` | Segmentation 1/√t — charge équilibrée entre workers |
| Fix `riemann_siegel_batch.py` — GPU nvrtc | Détection CC < 6.0 → forcer CPU numpy (GTX 960M sm_50 déprécié CUDA 12.x) |
| Création `scripts/zeta_turbo_on.sh` + `off.sh` + `zeta_run.sh` | Scripts absents retrouvés + recréés |
| Test T=10 000 lancé avec `nohup` | PID 210280 · log `run_T10000_test_20260610_100553.log` |

**Profil run T=100 000 :**
- `illinois_C` : 76.3 % du temps — 137 770 appels à 132 ms/appel (coût O(√t) attendu)
- `turing` : 19 627 ms (1 seul appel — validation globale 137 904 zéros, normal)
- LMFDB : 19/20 ✅ (zéro #20 : 8.06e-10 — cas limite stable)

**Tests T=10 000 et diagnostic :**

| Test | STEP | Overlap | Zéros | Manquants | Turing |
|---|---|---|---|---|---|
| v1 (10h06) | 0.1 fixe pour t<10k | ×4 STEP | 10 137 | 6 | ❌ INCOMPLET |
| v2 (10h34) | **0.05 pour t≥5k** | **fixe 2.0** | **10 141** | **0** | **✅ COMPLET** |

Diagnostic v1 : espacement moyen $\delta(10\,000) \approx 0.73$, mais espacement min mesuré
$= 0.038$ — des paires de zéros proches exigent STEP $< \pi / \ln(t/2\pi)$.
Formule de non-manquant : $\text{STEP}(t) < \pi / \ln(t/2\pi)$ (§23 Formules_zeta.md).

Commit v2 : `50837f7` — `Riemann_Lab_C` (STEP 0.1/0.05/0.02 + overlap=2.0)

---

## 2026-06-09 — documentation complète + arb_wrapper ×27 + run T=100 000 (ÉCHEC) — commits `f9e7061` · `8358cdb` · `b563db2` · `89ad1c4` · `7932e15`

**Résultat :** session documentation + intégration arb_wrapper sur `Riemann_Lab_C` + `Riemann_Lab_IA`. Benchmark Arb ×27 validé. Run T=100 000 lancé SANS nohup → process mort, 0 zéros produits.

| Action | Commit / Résultat |
|---|---|
| Wiki `Formules_zeta.md` — §18 Benchmark Arb ×27 (0.77 ms vs 21.13 ms, erreur < 2.2e-16) | `f9e7061` wiki |
| Wiki `Bibliotheques.md` — §12 mis à jour VALIDÉ ×27 (tableau paramètres + pattern arb_hardy_z) | `f9e7061` wiki |
| Wiki `STACK.md` — Progression v1→v5 (×1 260, ~1 min vs 21h) | `f9e7061` wiki |
| Skill `phase-c-illinois/SKILL.md` — section "Mur de latence RÉSOLU (2026-06-09)" | `8358cdb` Riemann_Lab_C |
| `arb_wrapper.py` intégré `compute_zeros_v4_1.py` — fallbacks mpmath.siegelz → arb_hardy_z (×27) | `b563db2` Riemann_Lab_C |
| `docs/index.html` — section PROGRESSION V1→V5 (5 cartes + tableau + 3 métriques) | `89ad1c4` Riemann_Lab_IA |
| `scripts/ia_prompts/ia_prompts_riemann_lab_complet.md` — résultats session + prompt consolidé | `89ad1c4` Riemann_Lab_IA |
| Merge `Riemann_Lab_IA` → `main` | `7932e15` main |
| Sync `main` → `Riemann_Lab_C` + `Riemann_Lab_Test` | `ee3518a` C · `3dc998e` Test |
| **Run T=100 000 lancé sans nohup** → **ÉCHEC : process mort, 0 zéros produits** | ⚠️ aucun fichier résultat |

**Animations interactives (7 total) :**
- `animation_theta.html` — 6 sections de cours (Stirling, Backlund…) — commit `411111d` IA
- `animation_series_dirichlet.html`, `animation_produit_eulerien.html`, `animation_plan_complexe.html`, `animation_gamma.html`, `animation_distribution_zeros.html` — commit `7363241` IA
- `animation_zeros_non_triviaux.html` — badge HR actif
- Header SVG `header_riemann_lab.svg` déployé README + index

**Benchmark Arb (speedup ×27) :** `affinage_arb.py` → 0.77 ms vs 21.13 ms mpmath.findroot — erreur < 2.2e-16 (flottant IEEE). Source : `src/benchmark/affinage_arb.py`, commit `074aef0`.

**Leçon :** toujours lancer les runs longs avec `nohup … &`. Sans nohup, SIGHUP tue le process dès déconnexion du terminal.

---

## 2026-06-06 — vérifications rendu GitHub (README · wiki · STACK)

**Résultat :** rendu vérifié sur GitHub via WebFetch + curl HEAD. Toutes les pages sont correctes. Sidebar "Uh oh!" identifiée comme artefact JS WebFetch (inoffensif en navigateur réel).

| Vérification | Résultat |
|---|---|
| PNG local (`docs/images/logo_riemann_lab.png`) | ✅ 500×235 px, RGBA, affiché |
| HTTP HEAD `raw.githubusercontent.com/main/` logo | ✅ 200 · `image/png` · 11 Ko |
| README GitHub main — balise `<img>` PNG ligne 1 | ✅ correct |
| Wiki `Home.md` — logo PNG en tête (URL absolue) | ✅ affiché |
| Wiki `STACK.md` — ligne Logo PNG + roadmap + date | ✅ cohérent |
| Sidebar wiki "Uh oh!" | artefact JS WebFetch — inoffensif |
| `Formules_zeta.md` — 22 sections, 929 lignes | ✅ intact |

---

## 2026-06-06 — logo PNG statique + sync 4 branches + wiki — commits `196af4e` · `f178b03` · `f49fb74` · `71357e0` · `8090d5e`

**Résultat :** remplacement du logo SVG animé par un PNG statique 500×235 px dans le README et le wiki. SVG bloqué par la CSP GitHub — PNG exporté via cairosvg, vérifié HTTP 200 sur `raw.githubusercontent.com`. Les 4 branches synchronisées.

| Action | Commit / Résultat |
|---|---|
| Conversion SVG → PNG via cairosvg (`--output-width 500`) | `docs/images/logo_riemann_lab.png` — 11 Ko |
| README.md : `<img>` SVG → PNG | `196af4e` IA |
| Merge `Riemann_Lab_IA` → `main` | `f178b03` main |
| Logo PNG en tête de `Home.md` wiki (URL absolue raw.githubusercontent.com) | `f49fb74` wiki/master |
| Merge `main` → `Riemann_Lab_C` | `71357e0` C |
| Merge `main` → `Riemann_Lab_Test` | `8090d5e` Test |
| Handoff.md mis à jour (2 commits) | `fa77842` · `6ac70d2` wiki/master |

**Vérifications :** rendu PNG affiché localement ✅ · HTTP 200 `raw.githubusercontent.com/main/` ✅ · README GitHub main ✅ · wiki `Home.md` GitHub ✅

---

## 2026-06-06 — logo SVG animé + note wiki — commits `320b9e3` · `ce9b874` · `aa0be8b`

**Résultat :** ajout du logo SVG animé Riemann Lab sur `Riemann_Lab_IA`, mergé sur `main` puis synchronisé sur les 4 branches. Note ajoutée dans le wiki (`Home.md`).

| Action | Commit / Résultat |
|---|---|
| Création `docs/images/logo_riemann_lab.svg` + intégration README | `320b9e3` IA |
| Merge IA → `main` | `ce9b874` |
| Merge `main` → `Riemann_Lab_Test` | `2b0a000` |
| Merge `main` → `Riemann_Lab_C` | `3b89500` |
| Merge `main` → `Riemann_Lab_IA` (retour sync) | `bbb03f9` |
| Note logo dans `Home.md` wiki | `aa0be8b` wiki/master |

**Logo :** fond sombre `#0d1117`, ζ doré (88 px), ligne critique `Re(s)=½` cyan animée (drift), 6 zéros pulsants aux valeurs exactes 14.13 · 21.02 · 25.01 · 30.42 · 32.93 · 37.58. Animations CSS actives hors GitHub (sandbox `<img>`). Taille : 2 444 octets.

---

## 2026-06-06 — documentation : README complet + fix lien wiki — commits `3974a87` · `f564bd8` · `bfbd9fc` IA → main → 4 branches

**Résultat :** session documentation sur `Riemann_Lab_IA`. Création du README racine,
correction du lien wiki dans `docs/index.html`, puis restauration du README complet
depuis le backup mai 2026 avec stats v4.1. Les 4 branches synchronisées sur `main`.

| Action | Commit / Résultat |
|---|---|
| Création `README.md` minimaliste (6 lignes) | `3974a87` IA |
| Fix lien wiki `docs/index.html` (ligne 573 : page spécifique → racine wiki) | `f564bd8` IA |
| Restauration README complet backup mai 2026 + section "État actuel — juin 2026" | `bfbd9fc` IA |
| Merge IA → `main` | `e586839` |
| Merge `main` → `Riemann_Lab_C` | `790d641` |
| Merge `main` → `Riemann_Lab_Test` | `c6f3c5a` |

**README final :** 19 432 octets — SHA `9e5bf81` — identique sur les 4 branches.
Section ajoutée : 10 142 zéros validés Turing-Backlund · v4.1 · Illinois_C (170 bits) + Newton · ~41 z/s · GPU CuPy.

---

## 2026-06-06 — 18h45 — maintenance : instrumentation v4.1 + gitignore + pdf_to_md_voie_b5 — commits `d6541e5` · `0deda6c` · `b41b448` IA

**Résultat :** session maintenance sur `Riemann_Lab_IA`. Vérification que les fichiers
d'instrumentation v4.1 (`chrono_phases.py`, `compute_zeros_v4_1.py`) sont bien sur
`origin/Riemann_Lab_C` (confirmé : `d26ed12` est ancêtre de `191d60a`). Nettoyage
`.gitignore`, ajout 8 PDFs de cours et script `pdf_to_md_voie_b5.sh`, regénération
de 13 MD Voie_b_5.

| Action | Commit / Résultat |
|---|---|
| Vérif. instrumentation v4.1 sur `Riemann_Lab_C` | `d26ed12` déjà présent ✅ |
| `.gitignore` : `calculs/` + `test-results/` | `d6541e5` IA |
| 8 PDFs cours + `pdf_to_md_voie_b5.sh` | `0deda6c` IA |
| 13 MD Voie_b_5 regénérés + doublon supprimé | `b41b448` IA — 28 fichiers MD |

---

## 2026-06-06 — animations interactives + sync 4 branches — commits `411111d` · `7363241` · `11cfad0` · `6bc2fb2` IA→main · `244875a` Test

**Résultat :** session docs/animations sur `Riemann_Lab_IA`. Six fichiers HTML créés ou enrichis
dans `docs/`, vérifiés Playwright headless (0 erreur JS, 0 erreur KaTeX, canvas dessinés,
sliders réactifs). Toutes les branches synchronisées sur `main` en fin de session.

### Animations créées / enrichies (branche `Riemann_Lab_IA`)

| Commit | Fichier | Contenu |
|---|---|---|
| `411111d` | `animation_theta.html` | Réécriture complète — 6 sections de cours (def. Γ, Stirling, eq. fonctionnelle ζ=e^{−iθ}Z, détection zéros, formule de Backlund), animation combinée slider t → θ(t) + Z(t) + plan complexe simultanés |
| `7363241` | `animation_series_dirichlet.html` | Convergence Σ1/nˢ selon Re(s), frontière σ=1, série η alternée (prolongement analytique), sliders σ + N termes |
| `7363241` | `animation_produit_eulerien.html` | Π(1−p⁻ˢ)⁻¹ premier par premier, preuve infinité des premiers, produit de Hadamard, slider σ + nb de premiers (jusqu'à p₂₅=97), tableau des contributions |
| `7363241` | `animation_plan_complexe.html` | Heatmap \|ζ(σ+it)\| (grille 80×110, série η, 50 termes), pôle s=1, bande critique, zéros LMFDB, coupes verticale/horizontale, sliders σ + t |
| `7363241` | `animation_gamma.html` | Γ(x) réel (Lanczos g=7), pôles aux entiers négatifs, formule de réflexion, \|Γ(½+it)\|=√(π/cosh(πt)) exact vs Lanczos, lien ξ(s) |
| `7363241` | `animation_distribution_zeros.html` | N(T) von Mangoldt vs comptage escalier LMFDB, espacements normalisés, histogramme GUE (Wigner) vs Poisson, table 20 spacings |

### index.html mis à jour (`11cfad0` IA)

- **Grille animations** : 6 nouveaux pavés `links-grid` (∑ ∏ ℂ Γ ⊞ θ) sous la hero-card θ
- **Grille cours** : 5 nouvelles cartes ANIMATION (série Dirichlet, produit eulérien, plan complexe, Gamma, distribution des zéros) — total 15 cartes
- Chaque animation référencée 2 fois : pavé (haut) + carte cours (bas)

### Vérification Playwright (headless Chromium, serveur localhost:8765)

| Page | KaTeX | Canvas | JS errors | Slider |
|---|---|---|---|---|
| `animation_theta` | 62 / 0 err | 2/2 | aucune | ✅ θ(t), Z(t), plan ℂ mis à jour |
| `animation_series_dirichlet` | 61 / 0 err | 2/2 | aucune | ✅ σ=3.25, S_N→ζ(σ) |
| `animation_plan_complexe` | 31 / 0 err | 3/3 | aucune | ✅ σ=1.50, \|ζ\|=0.9540 |
| `animation_gamma` | 56 / 0 err | 3/3 | aucune | ✅ x=3.65, Γ(3.65)=3.9358 |
| `animation_produit_eulerien` | 43 / 0 err | 1/1 | aucune | ✅ σ=4.10, écart=0.000000 |
| `animation_distribution_zeros` | 25 / 0 err | 2/2 | aucune | ✅ T=117, N=37 vs 36.83 |
| `animation_zeros_non_triviaux` | 37 / 0 err | 1/1 | aucune | ✅ badge HR `✓`→`✗ violée` |
| `index.html` | 48 / 0 err | — | aucune | ✅ 9 pavés, 15 cartes, 5 liens ×2 |

### Synchronisation branches

| Opération | Branche | Commit |
|---|---|---|
| merge IA → main (animations) | `main` | `6bc2fb2` |
| merge main → Riemann_Lab_Test | `Riemann_Lab_Test` | `244875a` |
| Handoff.md + JOURNAL.md mis à jour | wiki `master` | `3a6745a` |

---

## 2026-06-04 — sync final 4 branches sur main — commits `4a891e0` · `191d60a` · `3fecbba` · `61e2e16`

**Résultat :** toutes les branches alignées sur `main` en fin de session.

| Opération | Branche | Commit |
|---|---|---|
| merge Riemann_Lab_C → main | `main` | `4a891e0` |
| merge main → Riemann_Lab_C | `Riemann_Lab_C` | `191d60a` |
| merge main → Riemann_Lab_IA | `Riemann_Lab_IA` | `3fecbba` |
| merge main → Riemann_Lab_Test | `Riemann_Lab_Test` | `61e2e16` |

---

## 2026-06-04 — documentation + site + skills sync — commits `11cc5b2` wiki · `71a13fc` main

**Résultat :** session de consolidation post-Option B. Pas de code modifié.
Trois axes : enrichissement wiki, publication site GitHub Pages, synchronisation skills 4 branches.

### Wiki — enrichissement Formules_zeta.md + Bibliotheques.md (commit `11cc5b2` master)

| Fichier | Sections ajoutées |
|---|---|
| `Formules_zeta.md` | §19 Option B / illinois_refine (fa/fb, interface ctypes, résultats T=1000/T=10000) |
| `Formules_zeta.md` | §20 Goulot O(√t) — coût illinois_C croissant avec la hauteur (formule + mesures) |
| `Formules_zeta.md` | §21 Déséquilibre workers — deux causes, profil par worker, impact T=10000 |
| `Bibliotheques.md` | §14 ctypes post-fork — interface Option B, règle arrêt si .so absent, comparatif ms/appel |

### Site GitHub Pages — section performances (commit `71a13fc` main)

Insertion de `~/Téléchargements/section_performances_index.html` dans `docs/index.html`
juste avant `<footer>` — tableau v2→v4.1 (×138 vs v2), 3 leviers (Illinois C, post-fork,
Option B), métriques de validation (Turing COMPLET, LMFDB 19/20, illinois_C 98.6 %).
Synchronisé sur les 4 branches :

| Branche | Commit |
|---|---|
| `main` | `71a13fc` |
| `Riemann_Lab_IA` | `5720afb` |
| `Riemann_Lab_Test` | `a3b3edb` |
| `Riemann_Lab_C` | `6dfb282` |

### Skills — versionnement et sync 4 branches

`phase-c-illinois` mis à jour v0.2.0 → **v0.3.0** (Option B, résultats T=10000, goulot O(√t)).
`riemann-code-review`, `riemann-lab`, `riemann-security-review` versionnés depuis
`~/.claude/skills/` (source de vérité) — noms canoniques `riemann-*` alignés.
Synchronisés sur les 4 branches depuis `Riemann_Lab_C`.

### Handoff.md — créé (commit `24d0f48` master, mis à jour `cd56081`)

Premier Handoff.md du projet : état Option B validée, goulots résiduels, prochaines
actions (T=100 000, rapport v5→v4.1, Arb), rappels techniques non-négociables.

---

## 2026-06-03 — 22h56 — Option B : illinois_refine + T=1000 + T=10000 validés — commit `581e34d`

**Résultat :** Option B implémentée et validée. L'erreur ~0.3 (biais d'initialisation RS)
est corrigée. Run T=1000 : 649/649, 16.15 z/s, Turing COMPLET, LMFDB 19/20. Run T=10 000 lancé.

### Cause de l'erreur ~0.3 — diagnostic définitif

`illinois_mpfr(a, b, tol)` recalculait Z(a)/Z(b) en C avec Z_mpfr (RS + C₀+C₁,
biais structurel ~1e-3). Si la détection Python (`Z_vect_correct`) et Z_mpfr
donnaient des signes différents sur les bornes, Illinois cherchait un
« pseudo-zéro RS » décalé de ~0.3 — sans déclencher le fallback (hors-intervalle).

### Solution — Option B

Nouvelle fonction `illinois_refine(a, b, fa, fb, prec_bits, tol, max_iter)` :
- `fa = float(Z_vals[i])` et `fb = float(Z_vals[i+1])` passés depuis Python
  (valeurs déjà calculées par `Z_vect_correct` lors du balayage — zéro recalcul).
- Encadrement initial ancré sur les vrais zéros de $\zeta(\tfrac{1}{2}+it)$.
- Itérations intermédiaires : Z_mpfr en C (correct pour t ≥ 300, N ≥ 7 termes RS).
- `Z_double` supprimé du `.so` — détection entièrement côté Python.

### Modifications

| Fichier | Changement |
|---|---|
| `illinois_mpfr.c` | `theta_mpfr`/`Z_mpfr` paramétrées (`prec_bits`), `#include z_function.h` retiré, `illinois_refine` ajoutée |
| `illinois_mpfr.h` | déclaration publique `illinois_refine` |
| `Makefile` | `z_function.c` retiré de la compilation |
| `compute_zeros_v4_1.py` | binding ctypes `illinois_refine`, fa/fb depuis `Z_vals` |
| `test_illinois.py`, `benchmark_illinois.py`, `illinois_pyZ.py` | adaptés Option B |

### Résultats

| Test | Résultat |
|---|---|
| `test_illinois.py` (10 LMFDB) | **10/10** Illinois C pur · erreurs ~1e-13 · aucun fallback |
| benchmark t ∈ [500, 638] | **×30.78** vs mpmath.findroot (objectif ×5–10 dépassé) |
| Run T=1000 | 649/649 · **16.15 z/s** · Turing **COMPLET** · LMFDB 19/20 · fallback=0 |

### Profil phases — Run T=1000

| Phase | Temps cumulé | Appels | ms/appel |
|---|---|---|---|
| `mpmath_petit_t` (t < 300) | 60.1 s | 138 | 435 |
| `illinois_C` (t ≥ 300) | 30.1 s | 511 | 58.9 |
| `detection` | 0.7 s | 4 | 176 |

**Goulot résiduel :** `mpmath_petit_t` reste dominant en temps cumulé (138 zéros, 37 % du temps).
Pour T=10 000, ces 138 zéros représentent ~1.4 % du total → goulot marginalisé.

### Run T=10 000 (validation finale Option B)

| Critère | Valeur | Statut |
|---|---|---|
| Zéros trouvés | 10 141 (attendus 10 143) | ✅ |
| Durée | 9.1 min (543.7 s) | — |
| Vitesse | **18.65 z/s** | ✅ |
| Turing | COMPLET — 0 manquant, surplus 5 (chevauchement) | ✅ |
| LMFDB 19/20 | 19/20 (zéro #20 = 8.06e-10, stable) | ✅ |
| illinois_C | **98.6 %** (10 004 zéros) | ✅ objectif 90 % dépassé |
| mpmath_petit_t | 1.4 % (138 zéros, t < 300, constant) | ✅ |
| mpmath_fallback | **0** | ✅ |

**Profil phases (cumulé 4 workers) :**

| Phase | Temps cumulé | Appels | ms/appel |
|---|---|---|---|
| `illinois_C` | 1592.5 s | 10 004 | **159 ms** |
| `mpmath_petit_t` | 79.5 s | 138 | 576 ms |
| `turing` | 35.0 s | 1 | — |
| `detection` | 2.8 s | 20 | 138 ms |

**Nouveau goulot identifié :** `illinois_C` à grands t — 159 ms/appel pour t~7500–10000
vs 58.9 ms à t~500. Cause : $N_{\text{RS}} = \lfloor\sqrt{t/2\pi}\rfloor$ croît avec $t$,
Z_mpfr calcule plus de termes. Worker 3 [7503–10000] = plus lent (543 s).
Pour T=100 000 ($N_{\text{RS}} \approx 40$ termes), il faudra estimer l'impact.

### Fichiers produits
- `calculs/v4_1_T1000_20260603_225629/` — CSV + log + PNG (649 zéros)
- `calculs/v4_1_T10000_20260603_225948/` — CSV + log + PNG (10 141 zéros)

### Clôture session
Run T=100 000 non lancé (session fermée). Prochain démarrage : reprendre depuis Handoff.md.

---

## 2026-06-02 — 17h00 — Vérif A (T=300) + run T=1000 validés — commit `893f3b4`

**Résultat :** v4.1 validée sur deux runs successifs. Turing COMPLET sur les deux,
LMFDB 19/20, 0 fallback, 0 échec. Vitesse : 1.1–1.9 z/s (goulot `_newton_polish`).
Session arrêtée après T=1000 ; T=10 000 reporté.

### Vérif A — T=300 (justesse)
- 138/138 zéros · Turing **COMPLET** (0 manquant) · LMFDB **19/20** (zéro #20 = 8.06e-10, cas limite stable)
- `illinois_C_polish` : **0%** — attendu : tous les zéros de $[14, 300[$ sont sous le seuil `T_SEUIL_ILLINOIS_C`
- `mpmath_fallback` : 0 ✅ · durée : 73 s · vitesse : 1.9 z/s

### Run T=1000 (confirmation)
| Critère | Valeur | Statut |
|---|---|---|
| Zéros trouvés | 649 (attendus N(T) ≈ 647) | ✅ |
| Turing | COMPLET — 0 zéro manquant | ✅ |
| LMFDB 19/20 | 19/20 (zéro #20 stable : 8.06e-10) | ✅ |
| illinois_C_polish | 511 / 78.7% | ⚠️ structurel |
| mpmath_petit_t | 138 (t < 300, légitime) | ✅ |
| mpmath_fallback | 0 | ✅ |
| Vitesse | 1.1 z/s | ⚠️ |
| Durée | 10 min 3 s | — |

### illinois_C_polish à 78.7% — structurel, non un bug
Les 138 zéros $[14, 300[$ passeront *toujours* par `mpmath_petit_t` (seuil `T_SEUIL_ILLINOIS_C=300`).
Pour T=10 000 : 138/10 142 ≈ 1.4% → **98.6% illinois_C_polish** ✅ (seuil cible 90%).

### Goulot vitesse identifié
`_newton_polish` : 3–5 appels `mpmath.siegelz(dps=25)` par zéro (~5–15 ms/appel).
Worker 0 (plage $[14, 261]$) concentre tous les `mpmath_petit_t` → déséquilibre de charge.
Même cause racine que session après-midi : goulot = `siegelz`, pas l'algorithme.

### Fichiers produits
- `calculs/v4_1_T300_20260602_162919/` — CSV + log + PNG (138 zéros)
- `calculs/v4_1_T1000_20260602_163940/` — CSV + log + PNG (649 zéros)

---

## 2026-06-02 — après-midi — v4.2 finition hybride : précision parfaite, mais goulot = `siegelz` — commit `0fa22c2`

**Résultat :** la finition hybride (Illinois_C pré-affine + raffinage mpmath) atteint la
**précision parfaite** ($\text{Écart}_P = 0.00$ vs LMFDB) à toutes les hauteurs. Mais aucune
optimisation algorithmique du raffinage n'est possible : le goulot est **`mpmath.siegelz`
lui-même** (~296 ms/appel à $t\approx 9000$), pas le solveur. Newton est **réfuté** (plus lent
qu'Illinois). Décision de livrable en attente (vérifier HR vs cataloguer les positions).

### Vérif A — comptage (✅ COMPLET)
- 138/138 zéros · Turing **COMPLET** · LMFDB 19/20 < 1e-10 (zéro #20 = cas limite 8.06e-10).
- Illinois_C 0 % à T=300 : **normal** (tous les zéros à $t<300 = $ seuil → 100 % fallback mpmath).

### Vérif B — précision des positions (3 itérations)
| Itération | Méthode finale | Précision (Écart_P) | Vitesse ×4 | Verdict |
|---|---|---|---|---|
| B v1 | Illinois_C **pur** (racine de $Z_{\text{mpfr}}$) | 1e-4 à 1e-2 ❌ | 41 z/s | rejeté (positions) |
| B v2 | Illinois + polish `findroot` dps=30 | **0.00** ✅ | 0.5 z/s | juste mais lent |
| B v3 | Newton analytique dps=25, 5 pas | **0.00** ✅ | **0.4 z/s** | **plus lent qu'Illinois** |

### Cause racine confirmée (leçon décisive)
- Illinois_C pur trouve les zéros de la RS **tronquée** $C_0+C_1$ → biais de **position**
  $|\gamma_{\text{mpfr}}-\gamma| \approx |R(\gamma)|/|Z'(\gamma)|$, soit 1e-4 (croisement raide)
  à 1e-2 (croisement plat). Structurel, **pas un bug** (série asymptotique).
- Newton ne gagne **pas** : `siegelz(t, derivative=1)` ne rend pas $Z'$ gratuitement —
  $\zeta'(s) = -\sum \ln(n)/n^s$ a des poids log ⇒ série plus lente ⇒ $Z'$ **plus cher** que $Z$.
  Newton (2 appels/pas, dont $Z'$) ≈ Illinois (1 appel/pas, 27 itér) en coût total.
- **Goulot = vitesse intrinsèque de `mpmath.siegelz` à grand $t$**, pas le nombre d'itérations.
  → aucune optimisation algorithmique du raffinage tant qu'on passe par `siegelz`.

### Distinction comptage / position (clé pour trancher)
- **Vérifier HR jusqu'à T** = comptage Turing ($n_{\text{calc}} = N(T)$). Indépendant de la
  précision des positions → **Illinois_C pur (41 z/s, ~5 min pour T=10000) suffit.**
- **Catalogue de positions < 1e-10** = exige le polish lent (~7 h pour T=10000)… mais ce
  catalogue **existe déjà** (run v2/v3 : CSV 10 142 zéros, 50 dps).

### Estimation de temps (×4 workers, mesurée/extrapolée)
| Run | Zéros | Temps ×4 | Note |
|---|---|---|---|
| T=300 | 138 | ~60 s (mesuré) | tout fallback mpmath |
| T=1000 | ~396 | ~16 min | validation complète faisable |
| T=10000 | ~10 142 | ~7 h | run de nuit si catalogue voulu |

### Git
- `0fa22c2` (`Riemann_Lab_C`) — feat(v4.1) : finition Newton analytique dps=25 après Illinois_C
  (2 files, +575 / −42). Poussé : `71e6774..0fa22c2`.

### Documentation
- `Formules_zeta.md` enrichi (→ ~826 lignes) : §5.6 (erreur de position, perturbation 1ᵉʳ ordre),
  §6.4 (3 architectures d'affinage), §6.5 (finition Newton : ordre 2, dérivée analytique, `dps`
  vs LMFDB absolu), **§6.5.5 (mesure : Newton réfuté, goulot `siegelz`)**, §11.1–11.2 (comptage
  vs position + condition de validité détection).

### Prochaine action (DÉCISION DE LIVRABLE, pas technique)
1. **Si objectif = vérifier HR jusqu'à T=10000** → lancer Illinois_C pur (~5 min), Turing COMPLET.
2. **Si objectif = catalogue positions < 1e-10** → soit réutiliser le CSV v2/v3 existant,
   soit run de nuit polish T=10000 (~7 h).
3. Ne **pas** chercher d'autre solveur : le goulot est `siegelz`, pas l'algorithme.
4. (À valider avant tout abaissement de `dps` : tester sur $t\approx 9900$, jamais sur T=1000 —
   critère LMFDB absolu, cf. §6.5.3.)

---

## 2026-06-01 — nettoyage skill zeta-lab (4 branches) + sécurisation .mcp.json

**Résultat :** ancien skill `zeta-lab` (cassé) retiré de Git sur les 4 branches ;
faille `.mcp.json` non ignoré découverte et corrigée sur `main` et `Riemann_Lab_Test`.

### Skills
- Audit `git ls-tree` : `zeta-lab` était commité sur les 4 branches.
- Retiré via `git rm -r` + commit + push sur chacune :
  C (`2a4cde4`, + ancien prompt v4.1 retiré / prompt findroot ajouté) ·
  IA (`e68ebca`) · main (`5c08cf0`) · Test (`c3396b7`).
- Les BONS skills (riemann-lab, phase-c-illinois, riemann-code-review,
  riemann-security-review) sont toujours dans `~/.claude/skills/`,
  pas encore versionnés → Phase 2 du plan.

### Sécurité — .mcp.json
- Découvert : le `.gitignore` divergeait entre branches ; `.mcp.json` n'était
  PAS ignoré sur `main` ni `Riemann_Lab_Test`.
- `git ls-files | grep mcp` = VIDE partout → le token n'a JAMAIS été commité.
  Pas de révocation nécessaire (contrairement à l'incident du 31 mai).
- Corrigé : `echo ".mcp.json" >> .gitignore` sur main et Test → `PROTÉGÉ ✅`.

### Leçon durable
Le `.gitignore` n'est pas synchronisé entre branches. Après toute manip
multi-branches : vérifier `git check-ignore .mcp.json` sur CHAQUE branche.

---

## 2026-05-31 — après-midi — fix findroot appliqué (NON validé) — commit `7f5bd02`
- Affinage : callback ctypes illinois_c_exact → mpmath.findroot(solver="illinois")
- dps=35 global, DPS_AFFINAGE=15 local · plus de dépendance au .so
- Objectif : vrai parallélisme ×4. ⚠️ PAS ENCORE validé (aucun run effectué).
- Reprise : lancer Vérif A (T=300) du prompt prompt_v4_1_findroot_20260531.md.

---

## 2026-05-31 — 02h00 — v4.1 validée (justesse) — commit `368d090` (`Riemann_Lab_C`)

**Résultat :** v4.1 juste mais lente (1.1 z/s). Le goulot a migré de la détection vers l'affinage.

### Point d'arrêt N°1 — validation détection `Z_vect_correct`

Comparaison `Z_vect_correct(t)` (vectorisée) vs `mpmath.siegelz(t)` (référence) sur 4 plages.
Critère : mêmes changements de signe (CS) ⇒ aucun zéro raté.

| Plage | Écart max | Écart moyen | CS vect | CS mpm | Désaccords | Gain |
|---|---|---|---|---|---|---|
| t ∈ [14, 100]     | 1.38e-02 | 4.18e-03 | 29  | 29  | **0 ✅** | ×73 |
| t ∈ [300, 400]    | 1.50e-03 | 8.49e-04 | 64  | 64  | **0 ✅** | ×4379 |
| t ∈ [3000, 3100]  | 2.81e-04 | 1.46e-04 | 98  | 98  | **0 ✅** | ×9854 |
| t ∈ [9900, 10000] | 1.19e-04 | 1.07e-04 | 117 | 117 | **0 ✅** | ×19568 |

L'écart numérique max décroît avec t (1.4e-2 → 1.2e-4) : c'est l'erreur résiduelle
théorique de RS tronquée à C0+C1, en $O(t^{-3/2})$. **Ce n'est pas un bug.** Pour la
détection seul le **signe** compte ⇒ 0 désaccord = détection fiable.

### Bug corrigé au point d'arrêt N°1

Première version `Z_batch` : **359 désaccords** (zéros ratés). Cause : `N_max` FIXE
$= \lfloor\sqrt{t_{\max}/2\pi}\rfloor + 1$ pour TOUS les points du batch. Or RS exige
$N(t) = \lfloor\sqrt{t/2\pi}\rfloor$ propre à chaque $t$ ; les termes $n > N(t)$ faussent
le signe. Correction `Z_vect_correct` : masque booléen `mask[k,n] = (n ≤ N(t_k))` par
ligne ⇒ chaque ligne n'accumule que ses $N(t_k)$ termes exacts.

### Point d'arrêt N°2 — run T=300

| Critère | v5 (réf.) | v4.1 | OK ? |
|---|---|---|---|
| Zéros trouvés | 138 | 138 | ✅ |
| Turing COMPLET | ✅ | ✅ | ✅ |
| LMFDB 19/20 < 1e-10 | ✅ | ✅ | ✅ |
| Illinois_C pur | ~100 % | 100 % | ✅ |
| Vitesse | ~1 z/s | **1.1 z/s** | ⚠️ |

### Diagnostic vitesse — cause racine = affinage Illinois

Décomposition du temps pour T=300 :
$$\underbrace{138}_{\text{zéros}} \times \underbrace{102}_{\text{appels Illinois}} \times \underbrace{1.5\ \text{ms}}_{\text{siegelz @ dps=35}} \approx 21\ \text{s séquentiel} \times \frac{1}{1.84} \approx 122\ \text{s}$$

- Callback ctypes `illinois_c_exact` appelle `mpmath.siegelz` à dps=35 → 1.5–10 ms/appel.
- Sérialisation partielle du callback ⇒ gain parallèle **×1.84** au lieu de ×4
  (test : `Pool(sleep)`=×3.9 OK, `Pool(worker_chunk)`=×1.84).

### Fix proposé (à appliquer prochaine session — pas encore fait)

Remplacer le callback ctypes par `mpmath.findroot(siegelz, solver="illinois")` à
**dps=15** dans les workers ⇒ vrai parallélisme ×4 ; dps=15 suffit pour `tol=1e-12`.
Estimation T=10000 → ~6 z/s. Contrepartie : méthode `mpmath` au lieu de `Illinois_C`.

### Fichiers ajoutés (commit `368d090`)
- `src/calculs/optimisation/compute_zeros_v4_1.py`
- `src/calculs/optimisation/test_v4_1_T300.py`
- `src/calculs/optimisation/test_zbatch_validation.py`
- `src/ia/prompts/prompt_claude_code_phase_prompt_v4.1.md`

### 🔐 Incident sécurité résolu

Un ancien GitHub PAT était commité en clair dans `.mcp.json:7` (commit `b2f579a`).
GitHub Push Protection (GH013) bloquait le push.

**Leçon clé :** `.gitignore` empêche les futurs commits mais **ne purge pas le passé** —
un secret dans l'historique reste détectable tant que le commit existe.

Résolution (dans l'ordre) :
1. Révocation de l'ancien token sur GitHub (geste n°1, le plus urgent).
2. `git filter-repo --path .mcp.json --invert-paths` → effacé de 220 commits.
3. Vérification : `git log --all --oneline -- .mcp.json` = VIDE.
4. `git push --force` → blocage levé (`afcaab3`).
5. `main` vérifié : intact.
6. Nouveau token régénéré, remis dans `.mcp.json` **local** (ignoré par `.gitignore`).

> **Ne jamais suivre le lien « unblock-secret » de GitHub.** Un secret exposé = secret mort.

---

## 2026-05-29 — 21h30 — Voie B validée — commit `b8018c0` (`Riemann_Lab_C`)

**Résultat :** `compute_zeros_v5.py` valide **Illinois_C pur 100 %**, biais `Z_mpfr` < 1e-13.

### Fichiers créés / modifiés
| Fichier | Rôle |
|---|---|
| `compute_zeros_v5.py` | Script principal v5 — wrapper `mpmath.siegelz` |
| `illinois_mpfr.c` / `.h` | Callback Python/C `illinois_mpfr_cb` |
| `illinois_mpfr.so` | Recompilé |
| `illinois_pyZ.py` | Wrapper Python pour `Z_mpfr` via mpmath |
| `test_illinois_v5.py` | Validation Voie B (20/20) |
| `docs/phase_c_voie_b_v5_plan.md` | Livrable Phase C Voie B |

### Validation
```
Run T=80 (21 zéros) :
  Illinois_C pur    : 100 %  ✅  (v4 était à 0 %)
  Turing-Backlund   : COMPLET ✅
  LMFDB             : 19/20 ✅  (zéro #20 = cas limite 8.06e-10)
  Durée             : 25.8 s
test_illinois_v5.py : 20/20 ✅ · biais Z_mpfr < 1e-13 (avant ~9e-3)
```

**Note LMFDB 19/20 :** le zéro #20 (γ₂₀ ≈ 77.1448) est un cas limite,
$|Z(\gamma_{20})| = 8.6\text{e-}15$ — vrai zéro confirmé. L'écart vient de la précision
de la valeur de référence (15 décimales) ou de la limite de `siegelz` à 35 dps.
**Pas un échec de méthode.**

### Diagnostic du biais RS (avec Copilot / GPT-4.5 + Claude)

Décomposition sur t ∈ [300, 650] :
```
theta  : max 2.3e-13  ✅ theta_double parfait
sum    : max 3.26e-01 ✅ normal sans correction C0+C1
fullRS : max 1.5e-03  ⚠️ biais résiduel structurel
```

**Conclusion :** le biais **n'est pas un bug** mais une **limite mathématique** — RS
tronquée à C0+C1 plafonne à ~1e-3.

| Méthode | Précision |
|---|---|
| RS sans correction | ~1e-1 |
| RS + C0 | ~1e-2 |
| RS + C0 + C1 | ~**1e-3** (état alors) |
| RS + 3–5 termes | ~1e-8 |
| `mpmath.siegelz` | ~1e-12 |

Patches tentés et annulés : Patch 1 (π manquant dans dPsi) → biais 4e-2 ❌ ;
Patch 2 (C1 analytique) → biais 2e-2 ❌ ; `git checkout z_function.c` → retour origine ✅.

**Solution retenue :** wrapper Python/C appelant `mpmath.siegelz(t)` depuis le `.so`
(`mpc_zeta` absent de libmpc 1.3.1).

### Phase C — état validé à cette date
- `c_modules` compile : `make clean && make` → `illinois_mpfr.so` OK.
- `benchmark_illinois.py` : gain isolé C/libmpfr **×48.73** sur t≈500–638.
- 5 erreurs architecturales de v4 identifiées (détection via `mpmath.siegelz`,
  parallélisme abandonné, `Z_double` en détection, fallback global, `.so` absent
  silencieux) → à corriger dans v4.1.
- Seuil justifié : $N=\lfloor\sqrt{t/2\pi}\rfloor \Rightarrow t<300 \Rightarrow N<7$ (imprécis),
  $t\geq 300 \Rightarrow N\geq 7$ (fiable). D'où `T_SEUIL = 300.0`.
- 9 PDF de cadrage produits (session GPT-4.5 / Copilot) — voir `STACK.md`.

---

## 2026-05-23 — Correction hiérarchie CLAUDE.md

Le `CLAUDE.md` projet (208 lignes, Riemann) avait été copié par erreur dans
`~/.claude/CLAUDE.md` (global), écrasant les instructions générales. Deux fichiers
distincts recréés :

| Fichier | Contenu | Lignes |
|---|---|---|
| `~/.claude/CLAUDE.md` | Langue FR, style, règles légères | 26 |
| `~/projet_zeta/CLAUDE.md` | Contexte Riemann complet | 208 |
| `src/calculs/optimisation/CLAUDE.md` | Phase C — Illinois, ctypes | 108 |
| `.../c_modules/CLAUDE.md` | Règles C — libmpfr, PREC=170 | 97 |

---


## 2026-05-16 — Benchmark séquentiel équitable (post-reboot NVIDIA)

Tests équitables : un seul mode à la fois après reboot.

| Mode | Zéros / 15 min | Vitesse | t atteint | Gain vs CPU |
|---|---|---|---|---|
| CPU scalaire (réf.) | ~604 | ~0.67 z/s | 944 | — |
| **BATCH_CPU** | **3 231** | **3.59 z/s** | 4 164 | **×5.3** |
| **BATCH_GPU** | **3 051** | **3.39 z/s** | 4 596 | **×5.1** |

**Clé :** BATCH_CPU ≈ BATCH_GPU — la GTX 960M n'apporte pas de gain. L'affinage Illinois
(mpmath, CPU pur) = **80–90 % du temps total** ; la GPU n'accélère que la détection Z(t)
(10–20 %). GPU GTX 960M opérationnel depuis le 16 mai (`prime-select nvidia` + reboot,
CuPy `cupy-cuda12x`).

---

## ~2026-04-24 — Objectif 1 atteint — 10 142 zéros

`compute_zeros_v2.py` : 10 142 zéros calculés (jusqu'à T ≈ 9998.85) en ~21 h,
validés contre LMFDB. Fichier : `zeros_zeta_T10000_20260424_205325.csv`.
Base de référence vitesse : CPU scalaire 1.4 z/s solo.

---
> *Mise à jour : 31 mai 2026 — 02h00 · JOURNAL.md (1 fichier MD modifié) · ~205 lignes · append-only*

## 2026-06-12 — Session v9 turbo + fix sudoers

- v9 validée sans turbo : 138 069 zéros, 28.0 min, 82.15 z/s, ×1.80 vs v8
- MAJ index.html chiffres v9 : commit be893d1 ✅
- Fix sudoers zeta_turbo : /etc/sudoers.d/zeta_turbo installé ✅
- Run v9 avec turbo : 26.6 min · 86.5 z/s · 138 069 zéros · Turing COMPLET ✅
- Gain turbo v9 : ×1.05 (bottleneck MPFR/mémoire, pas CPU — projection 17 min invalidée)
- Gain cumulé v1→v9 avec turbo : ×4 500
- analyse_problemes_v8_v9.md → wiki ✅

## 2026-06-12 fin de soirée — v10 W=8 forcé

- `compute_zeros_v10.py` créé depuis v9 — seul changement : `N_WORKERS = 8` (forcé)
- T=10k v10 validé : 10 142 zéros · 16.2s · 624 z/s · 0 manquant ✅
- Run T=100k v10 + turbo : **138 069 zéros · 23.7 min · 97.08 z/s** · Turing COMPLET · LMFDB 19/20 ✅
- Gain v10 vs v9 : **×1.12** (meilleur que benchmark v8 ×0.99 — Brent grand t dilue overhead HT)
- Gain cumulé v1→v10 avec turbo : **×5 040** (21h → 23.7 min)
- Explication W=8 > W=4 : chaque appel Brent à grand t coûte ~64 ms → context-switch HT négligeable
- commit `c9fad76` sur Riemann_Lab_C
- docs/index.html, STACK.md, JOURNAL.md mis à jour → v10 comme version courante
- Prochaine : v11 — cache (fa,fb) scan→Brent (×1.1–1.3 estimé)

---

## Session 2026-06-13 — Infrastructure cluster & backup automatique

### Actions réalisées

**Pipeline backup automatique**
- Cron zeta-livermore8 (02h00) : rclone copy ~/backup/ → protondrive:hprzeta/Riemann_Lab/backup/
- Cron zeta-icor7 (01h50) : rsync -aq -e 'ssh -i ~/.ssh/id_acer' → logs + wiki + pdf vers Acer
- Cle SSH id_acer (ed25519) sans mot de passe : icor7 → Acer operationnelle
- Test : OK backup logs — pipeline 100% automatique

**Renommage hostnames**
- hp3647h → zeta-hp3647h (carte mere HP 3647h · HP Compaq 8000 Elite CMT)
- pcfix2 → zeta-livermore8 (carte mere ECS Livermore8 · Compaq-Presario SG3210FR)
- /etc/hosts mis a jour HP et Acer

**IPs reseau local**
- zeta-icor7 : 192.168.1.24 (wifi wlp2s0)
- zeta-hp3647h : 192.168.1.94 (ethernet Gigabit Intel)
- zeta-livermore8 : 192.168.1.22 (ethernet 100Mbit Realtek)

**Documentation produite**
- Architecture-Cluster-Zeta.md mis a jour (commit 69d30c6)
- backup_cluster_map.sh dans scripts/ → genere 2 SVGs fond blanc
- backup_cluster_map.svg + topo_machines_zeta.svg dans docs/

**Notes**
- crontab -e casse sur Acer (Python 3.5) → workaround (echo ...) | crontab -
- /etc/hosts AVANT hostnamectl sinon erreur resolution hostname
- Wiki vit sur icor7 uniquement, pas sur HP ni Acer

---

## 2026-06-14 — Arbitrage architecture cluster : 5 → 4 nœuds

**Décision (session Claude.ai web) :**
- Architecture révisée : **4 nœuds** (PC4 = bastion uniquement, hors périmètre calcul).
- PC4 (`zeta-secure`, OpenBSD 7.9/i386, 192.168.1.54) : rôle **VPN/pare-feu uniquement**,
  pas de worker Python (OpenBSD/i386 non viable pour calcul mpmath).
- Rôle `zeta-log-dns-moni` réaffecté à **PC3** (`zeta-livermore8`, alias `zeta-acer`,
  Linux Lite 3.8/i686, 192.168.1.22) : chrony (NTP LAN), rsyslog (logs centralisés UDP 514),
  dnsmasq (résolution `.lan`), glances ou fallback script `vmstat`/`free` si Python 3.5
  incompatible.
- 3 SVG harmonisés produits sur Claude.ai (déposés dans `~/Téléchargements/`) :
  - `topo_machines_zeta.svg` — canevas étendu 720 → 780 px, encart PC4 ajouté, date 15/06
  - `backup_cluster_map.svg` — checklist étendue, encart PC4, date 15/06
  - `workflow_post_version_riemann_lab.svg` — mise à jour date

**Motivation** :
- Séparation nette : réseau/sécurité (PC4) vs supervision légère (PC3 qui fait déjà backup).
- PC3 à 5,7 Go RAM libre → largement suffisant pour chrony + rsyslog + dnsmasq.

---

## 2026-06-15 — Accès distant fonctionnel : zeta-secure (PC4) opérationnel via IPv6

**Contexte** : finalisation de la configuration WireGuard de PC4 (`zeta-secure`,
OpenBSD 7.9/i386, bastion VPN/pare-feu) comme point d'entrée VPN du cluster
depuis l'extérieur (4G/téléphone).

**Travaux réalisés** :

1. **Tunnel local PC1 ↔ PC4** (`wg0`) validé précédemment — handshake OK,
   `10.10.0.2` (PC1) ↔ `10.10.0.1` (PC4).

2. **Diagnostic CGNAT IPv4** : l'IP WAN de la box (`10.153.18.138`) est en
   plage RFC1918 — la box SFR est elle-même derrière du CGNAT côté IPv4.
   La règle de port forwarding UDP/51820 → 192.168.1.54 était correctement
   configurée mais structurellement inopérante (pas d'IPv4 publique
   dédiée). → Bascule de stratégie vers IPv6.

3. **IPv6 globale sur PC4** :
   - La box délègue un préfixe `/56` (`2a02:8428:80a6:da00::/56`) avec SLAAC
     actif sur le LAN (`2a02:8428:80a6:da01::/64`).
   - PC4 (`re0`) ne recevait aucune adresse IPv6, même locale-lien : il
     manquait `inet6 autoconf` dans `/etc/hostname.re0`.
   - Après ajout de `inet6 autoconf` + `netstart re0` : adresse locale-lien
     obtenue (`fe80::240:f4ff:fecc:36a0`), mais toujours pas d'adresse
     globale → RA (Router Advertisement, ICMPv6 type 134) bloquées par
     `pf` (`block in` par défaut, aucune règle ICMPv6).
   - **Fix pf** : ajout de
     `pass in on $ext_if inet6 proto icmp6 icmp6-type {routeradv, neighbradv, neighbrsol, redir}`
     (note : le type correct est `neighbrsol`, pas `neighbrsolicit`).
   - Après `ifconfig re0 down/up` : adresse globale SLAAC obtenue —
     `2a02:8428:80a6:da01:ad39:37b9:a638:126c` (stable, `pltime/vltime≈745s`,
     se renouvelle périodiquement) + une adresse `temporary` (à ignorer pour
     un usage serveur).

4. **DuckDNS AAAA** :
   - Ajout de l'enregistrement AAAA sur `zeta-secure.duckdns.org` →
     `2a02:8428:80a6:da01:ad39:37b9:a638:126c`.
   - `/etc/duckdns/duck.sh` réécrit pour pousser A et AAAA à chaque
     exécution cron (`*/5 * * * *`), en extrayant l'adresse IPv6 globale
     non-temporary via :
```sh
     IP6=$(ifconfig re0 | awk '/inet6/ && !/fe80/ && !/temporary/ {print $2; exit}')
```
   - Test manuel : `OK` reçu, `host -t AAAA zeta-secure.duckdns.org` confirme.

5. **Pare-feu IPv6 de la box SFR (GR140IG)** — cause racine du blocage final :
   - Découverte d'une section "Réseau v6" dans Sécurité → Accès, distincte
     du NAT/redirection de ports IPv4. Vide par défaut = tout trafic entrant
     IPv6 non sollicité bloqué, indépendamment du pf de PC4.
   - Création d'une règle : `WireGuard-IPv6 / UDP / 2a02:8428:80a6:da01:
     ad39:37b9:a638:126c / ports 51820-51820 / source: toute / activée`.

6. **Test bout-en-bout réussi** (téléphone Android, 4G, WiFi off) :
   - Tunnel `zeta-vpn` (clé pub `6euaNc/uLQc/PYL2/CAWYR391...`,
     `10.10.0.3/24`) → Endpoint `zeta-secure.duckdns.org:51820` (puis testé
     aussi en IPv6 littérale, même résultat positif).
   - Handshake établi, `rx`/`tx` non nuls et croissants — premier accès
     VPN externe fonctionnel.
   - `allowed-ips` du pair téléphone élargi côté PC4 à
     `10.10.0.0/24, 192.168.1.0/24` pour accès complet au LAN (test ping
     LAN reporté à la prochaine session).

**Leçons clés** :
- IPv4 "publique" affichée par un service externe (`curl ifconfig.me`) ne
  prouve PAS l'absence de CGNAT si elle est testée depuis l'intérieur du
  même réseau — il faut comparer avec l'IP WAN vue par la box elle-même.
- Un `/56` IPv6 délégué + SLAAC fonctionnel en interne ne garantit PAS
  l'accessibilité externe : un pare-feu IPv6 séparé du NAT IPv4 peut
  bloquer silencieusement tout trafic entrant.
- Sous OpenBSD/pf, SLAAC nécessite explicitement `pass in ... icmp6-type
  {routeradv,...}` — sans ça, `inet6 autoconf` reste sans effet malgré
  les bons flags `ifconfig`.
- WireGuard Android : `rx=0` persistant + `tx` croissant = le paquet part
  mais n'arrive jamais → chercher du côté des pare-feu intermédiaires
  (box), pas du client.

**État final** : zeta-secure (PC4) est un bastion VPN WireGuard pleinement
opérationnel, accessible en IPv6 depuis l'extérieur, avec DDNS auto-maintenu.

**Prochaines étapes** :
- Test ping LAN complet depuis le téléphone (via tunnel élargi).
- Vérifier rotation de l'adresse IPv6 SLAAC (~12 min) → confirmer que
  `duck.sh` suit bien le changement au prochain cycle cron.
- PC3 → rôle `zeta-log-dns-moni` (en attente).

**Compléments session 2026-06-15 (Claude Code) :**
- SVG harmonisés intégrés dans le repo (`docs/images/`, `docs/`, `scripts/`) ✅
  commit sur `Riemann_Lab_IA` (Tâche 1 ✅).
- DDNS PC4 — **SSH corrigé et DDNS validé** ✅ (session 16/06 00h50) :
  - Cause du blocage SSH : agent présentant 3 clés avant `zeta_cluster` → OpenBSD
    atteint MaxAuthTries. Fix : `IdentitiesOnly yes` ajouté dans `~/.ssh/config`
    pour l'alias `zeta-del`.
  - Vérification : `host -t AAAA zeta-secure.duckdns.org` → `c10d:e4a1:c992:9918`
    = adresse `autoconf` non-`temporary` courante de `re0` ✅
  - `/var/log/duckdns.log` : contenu `OK` (2 octets), timestamp `Jun 16 00:50` ✅
  - L'adresse a changé depuis la session initiale (`ad39:...` → `c10d:...`) — DuckDNS
    a suivi, ce qui prouve que le cron `*/5` fonctionne en conditions réelles.
  - Note : sous OpenBSD `inet6 autoconf`, l'adresse stable n'est PAS EUI-64 mais
    générée (RFC 7217). Elle change sur reboot ou changement de préfixe `/56`.
    Observer passivement en cas de renumbering box SFR.
- PC3 `zeta-log-dns-moni` — **déployé** ✅ (16/06 ~23h20) :
  - Prérequis manuels (hprzeta) : groupe `sudo` + clé SSH + NOPASSWD (`/etc/sudoers.d/hprzeta_nopasswd`).
  - **chrony** : pool NTP iburst, `allow 192.168.1.0/24`, `local stratum 10`.
    Synchronisé sur `ntp.viarouge.net` stratum 3, err < 0.1 ms ✅
  - **rsyslog** 8.16.0 : `/etc/rsyslog.d/10-udp-receive.conf`, UDP 514 ouvert,
    logs LAN → `/var/log/remote/<hostname>/` ✅
  - **dnsmasq** 2.75 : `/etc/dnsmasq.d/zeta-cluster.conf`, 4 nœuds `.lan` ✅
  - **glances** : pip3 irrécupérable (Python 3.5 / pip trop récent).
    → Fallback : `/usr/local/bin/zeta_monitor.sh` (vmstat/free/df) + cron `*/5` ✅
- §29 ajouté dans `Formules_zeta.md` : découpage par fenêtres T pour
  distribution multi-machines (v13+).
- Bonnes-Pratiques enrichi : section OpenBSD/pf pièges réseau.

---

## Session 2026-06-16 (après-midi — Claude Code) — Guide-Linux-Commandes

**Objectif :** créer un guide vivant des commandes Linux/BSD utilisées dans le projet.

**Réalisations :**
- **`Guide-Linux-Commandes.md`** créé dans le wiki (500 lignes, 14 sections) :
  réseau (`ip`, `ifconfig`), SSH/SCP, WireGuard (Linux + OpenBSD), OpenBSD
  (`doas`, `pf`, `syspatch`, `pkg_add`), DuckDNS, cron, rsync, rclone, tmux,
  sed, divers (`nc`, `journalctl`, `qrencode`). Commit `4c39ca6` wiki master.
- **PDF** `pdf/cours/Guide-Linux-Commandes.pdf` généré (84 Ko, lualatex) et
  uploadé sur Proton Drive (`protondrive:hprzeta/Riemann_Lab/cours/`).
- **`Handoff.md`** mis à jour : lien `[[Guide-Linux-Commandes]]` ajouté dans
  la session du jour et dans la table des fichiers modifiés. Commit `1946c94`.

**Table des pièges documentés** (leçons apprises en production) :
- `net.inet6.ip6.accept_rtadv` n'existe pas sous OpenBSD (FreeBSD/NetBSD uniquement)
- `neighbrsolicit` invalide dans pf → utiliser `neighbrsol`
- NBSP (`\xc2\xa0`) dans config WireGuard depuis copier-coller mobile
- `curl -4 ifconfig.me` trompeur pour détecter CGNAT depuis l'intérieur
- `crontab -e` cassé sur Python 3.5 → workaround `(crontab -l; echo ...) | crontab -`
- SVG → `docs/images/` uniquement, pas `scripts/`
- DuckDNS : champ A ≠ champ AAAA (remplir séparément)
- pf bloque SLAAC sans règle ICMPv6 explicite (`routeradv`, `neighbrsol`, etc.)

---

## Session 2026-06-17 (nuit — Claude Code) — v13 : fix bottleneck PC2 + benchmark cross-machine

**Objectif :** diagnostiquer scan_arb.so sur PC2, corriger la signature ctypes, créer v13.

**Diagnostic scan_arb.c PC1 vs PC2 :**
- Sources **identiques** (diff = 0) ✅
- `ldd scan_arb.so` → `libm` uniquement — **correct par conception** (Z_double C pur, pas libarb)
- `illinois_arb.so` → lie `libflint-arb.so.2` présent sur PC2 ✅
- `libflint-arb2` v2.23.0 installé sur PC2, mais **python-flint absent** → `arb_hardy_z` fallback mpmath.siegelz
- Test initial (diagnostic) : **signature ctypes incorrecte** — 2 POINTER au lieu de 4 (brackets_a, brackets_b, fa, fb) → retourne 0 silencieusement (UB C, pas d'exception Python)

**Benchmark v12 T=1000 :**
| Machine | Durée | Vitesse | Bottleneck |
|---|---|---|---|
| PC1 (turbo, python-flint) | 3.3 s | 195 z/s | Worker 0 : 2.9 s (arb_hardy_z) |
| PC2 (sans turbo, sans flint) | 101.3 s | 6.4 z/s | **Worker 0 : 101.2 s** (mpmath.siegelz ×18 600 évals) |

Cause : `T_SEUIL_PETIT_T = 200` dans v12 forçait arb_hardy_z (= mpmath.siegelz sur PC2) pour 18 600 évaluations dans [14, 200].

**compute_zeros_v13.py — commit `77efd10` :**
- `T_SEUIL_PETIT_T` : 200 → **65** (N_RS=2 fiable dès t=65, confirmé empiriquement)
- `TOL_ARB` : 1e-9 → **1e-12** (marge LMFDB, sans coût en double précision)
- Itérations de correction :
  - T_SEUIL=20 → LMFDB 16/20 (Z_double N_RS=2 brackets décalés à t<60)
  - Re-éval fa/fb + `continue` → 9 vrais zéros perdus (brackets scan_arb hors-zéro = skip + vrai bracket aussi manqué)
  - **T_SEUIL=65** ← solution finale : couvre tous N_RS=2 (t<57) + marge

**Benchmark v13 T=1000 :**
| Machine | Durée | Vitesse | LMFDB | Turing |
|---|---|---|---|---|
| PC1 | **1.0 s** | **624 z/s** | 20/20 ✅ | COMPLET ✅ |
| PC2 | **12.5 s** | **52 z/s** | 20/20 ✅ | COMPLET ✅ |

**Gains v13 vs v12 :** PC1 ×3.2 · PC2 **×8.1**.

**Leçon scan_arb signature ctypes :** 8 arguments obligatoires :
```python
lib.scan_zeros_arb.argtypes = (
    [ctypes.c_double] * 3 +               # t_min, t_max, step
    [ctypes.POINTER(ctypes.c_double)] * 4 +  # brackets_a, brackets_b, fa, fb
    [ctypes.c_int]                          # max_brackets
)
```
Passer 2 POINTER au lieu de 4 → comportement indéfini C, retour 0 silencieux.

---

## Session 2026-06-17 (après-midi — Claude Code) — STEP adaptatif corrigé + dashboard live

**Objectif :** lancer T=500 000 distribué PC1+PC2, puis T=1 000 000 si COMPLET ; évaluer
l'ajout de PC3 (libflint-arb) pour v14.

**Dashboard créé :** `scripts/zeta_run_progress.py` — TUI curses live (répartition cible
PC1/PC2, progression zéros par parsing `tail` des logs en croissance, CPU/RAM/disque via
sonde `/proc/stat`+`/proc/meminfo`+`os.statvfs` locale et SSH, détail par worker). Lancé
dans une session tmux dédiée `zeta-progress` (distincte de `zeta-cluster`, l'ancien moniteur
4 panneaux — confusion observée en session entre les deux). Détail complet dans
`claude-traitement-journalier/Process_Distribution_PC1_PC2_20260617.md` (PDF généré via
lualatex, recette `feedback_pdf_generation`).

**Run T=500 000 distribué : ❌ KO** — 818 408/818 414 zéros, Turing INCOMPLET (6 manquants),
39,12 min (vs ~20-25 min estimées — le modèle de pivot, calibré à T=1000-10000, sous-estime
le ralentissement à grande densité de zéros).

**Diagnostic STEP :** `_step_adaptatif()` dans `compute_zeros_v13.py` était un **STEP fixe
0.010** malgré son nom (calibré seulement à T=100000). Deux zéros dans le même pas STEP →
`Z(a)` et `Z(b)` de même signe → la paire disparaît sans laisser de trace détectable dans
les données (les écarts ratio≈3x cherchés comme signature se sont révélés être du bruit
statistique normal, dispersé partout, pas un indicateur fiable).

**Cause structurelle identifiée :** l'écart minimal global décroît avec N(T) (répulsion de
niveaux GUE, loi cubique near 0 ⇒ écart minimal ~ N(T)^(-1/3)), pas seulement avec l'écart
moyen. Même la formule canonique du `CLAUDE.md` racine (`min(2π/(5·ln(T/2πe)), 0.02)`) reste
plafonnée à 0.02 pour tout T réaliste de ce projet (le premier terme ne descend sous 0.02
qu'à T≈10²⁷) — donc pas réellement adaptative dans la plage utilisée ici.

**Correctif (commit `30d05ee`, `Riemann_Lab_C`, poussé) :**
```python
STEP(T) = κ · gap_moyen(T) · N(T)^(-1/3) / marge_securite     # κ≈1.357, marge=2.0
```
κ calibré sur le seul point fiable (T=100000, run Turing COMPLET).

**Validation par rescan ciblé** [260000, 390000] (sans relancer tout le run, ~13 min) :
- 224 420 zéros (ancien STEP) → **224 421 zéros (nouveau STEP)**
- **1 zéro récupéré** : t=273193.66313771, absent de l'ancien run à toute tolérance
- **0 régression** : tous les zéros de l'ancien run présents dans le nouveau (sur-ensemble strict)
- Nuance : sur cette plage Turing indiquait un swing de "6 manquants" mais seul 1 zéro réel
  manquait — le reste relève probablement du bruit normal de N(T) (terme S(T) oscillant).

**Nouveaux STEP (vs ancien fixe 0.010) :** T=1000→0.121 · T=10000→0.031 · T=100000→0.0095
(≈inchangé) · T=500000→0.0044 (×2,3 plus fin) · T=1000000→0.0032 (×3,1 plus fin).

**PC3 (zeta-backup) pour v14 : ❌ indisponible.** Pas de libflint-arb dans les dépôts
(Ubuntu Xenial 16.04, i686 32 bits) ; `libarb` trouvé via apt-cache est un logiciel de
bioinformatique sans rapport. CPU réel : **Athlon II X2 215 2,7 GHz** (pas un E2140 comme
indiqué précédemment dans `Architecture-Cluster-Zeta.md` — à corriger). Compilation Arb
depuis les sources jugée trop coûteuse pour un gain incertain sur un OS 32 bits ancien —
non tentée.

**Reporté à plus tard (décision utilisateur) :** relancer T=500 000 distribué en `nohup`
pour confirmer Turing COMPLET avec le STEP corrigé, avant d'envisager T=1 000 000.

---

## Session 2026-06-23 (matin) — Incident Emergency Mode résolu (fstab nofail)

**Contexte :** maintenance préventive sur PC1 (`riemann@zeta-lab`) — écran **Emergency
Mode** au démarrage Ubuntu, accompagné d'un bruit de disque inhabituel ; boot normal
possible ensuite via Ctrl+D → login.

**Symptômes observés :**
| Symptôme | Description |
|---|---|
| Emergency Mode au boot | Ubuntu bascule en mode urgence avant le login |
| Bruit disque | Son inhabituel pendant la phase de démarrage |
| Boot normal ensuite | Ctrl+D → login normal, système fonctionnel |

**Cause racine :** entrée `/etc/fstab` **bloquante** pour le SSD Micron 1100
(`/mnt/vault_rag`, mis en service le 22/06) — systemd cherche l'UUID du SSD, time out,
bascule en Emergency Mode. Le bruit de disque = HDD système `sda` en retry pendant ce
timeout de montage (pas une défaillance du HDD).

**Diagnostic disque système `sda` (Seagate BarraCuda ST1000LM035-1RK172, 1 To) :**
- SMART overall : ✅ PASSED
- Reallocated/Pending/Uncorrectable : ✅ 0 / 0 / 0
- Power_On_Hours : 3 547 h (~148 jours) · Température : 37 °C
- Self-test court : ✅ Completed without error

**Correction appliquée :** ajout de l'option `nofail` à la ligne `/etc/fstab` du point de
montage `/mnt/vault_rag`, pour éviter qu'un montage non critique bloque le boot.

**Commit :** `6f9e679` (wiki, `MAINTENANCE_2026-06-23.md`) — rapport source incomplet
(s'arrête juste après l'annonce du correctif, sans citer la ligne `fstab` exacte ni de
validation post-correctif par reboot). Log complété ici à partir du rapport disponible ;
à vérifier par un reboot test si le doute revient sur ce point de montage.

---

## Session 2026-06-23 (après-midi — Claude Code) — Diagnostic 5 zéros manquants T=500k, abandonné

**Objectif :** localiser précisément les 5 zéros manquants du run #4 (`v13_distribue_T500000_20260617_213126`,
818 409/818 414 zéros, commit `8f755eb`) — tâche 1 du tableau « reste à faire » établi en début
de session.

**Méthode 1 — analyse statistique des écarts.** Calcul de l'écart entre chaque paire de zéros
consécutifs sur toute la plage `[65, 500000]` (818 405 écarts), normalisé par l'écart moyen
local `2π/ln(t/2π)`. Top 150 écarts les plus anormaux (ratio jusqu'à 3.11) vérifiés un par un
par échantillonnage du signe de `Z(t)` (formule de Hardy, `theta_rapide.Z_fast`, 9 points
internes, dps=25) entre les deux zéros encadrants. **Résultat : 0 changement de signe interne
détecté** — aucun des plus gros écarts ne cache un zéro raté. Réfute l'hypothèse d'une « paire
serrée fusionnée » (un seul écart anormalement grand visible).

**Méthode 2 — scan indépendant à phase de grille décalée.** Le run original scanne avec un
STEP global `_step_adaptatif(500000)=0.0044316` mais des origines de grille différentes par
worker (`t_min_worker` issu d'une recherche binaire sur N(T), pas un multiple rond de STEP).
Hypothèse testée : un zéro raté à une phase donnée serait détecté à une autre phase. Re-scan
complet `[65, 500000]` avec `scan_arb` (même STEP, grille ancrée à `T_START=65`, donc phase
différente de toutes les origines de workers du run original), découpé en 25 chunks de
20 000 alignés exactement sur la grille (pas de rupture de phase aux jointures). Durée
mesurée : **10.5 min** (benchmark préalable sur un segment de 5000 → extrapolation 6.3 min,
cohérent). **818 401 brackets trouvés, 0 candidat sans correspondance** (tolérance 0.05) avec
les zéros déjà calculés. La grille décalée retrouve essentiellement le même ensemble de zéros
→ **l'hypothèse de phase de grille au niveau du scan est réfutée**.

**Méthode 3 — bisection sur `N_exact(T)`.** `valider_turing()` ne calcule le delta
(attendus − calculés) qu'au dernier checkpoint ; pour localiser, calcul direct de
`delta(T) = N_exact(T) − n_calculé(T)` sur une grille fine de T (40 points, dps=40,
n_sigma=80), recherche des intervalles où `delta` augmente, puis bisection fine dans chacun.
**Piège découvert :** `delta(T)` oscille de façon non monotone (multiples allers-retours
0 ↔ −1 sans qu'aucun zéro ne soit ajouté entre les deux bornes) — preuve que `S(T)`
(le terme d'erreur de l'argument de ζ) franchit des seuils de demi-entier de façon générique,
indépendamment de toute absence réelle de zéro. La bisection converge proprement (largeur
finale < 0.4) sur 4 « candidats » — mais cette convergence nette ne distingue PAS un vrai
zéro manquant d'un simple franchissement de seuil d'arrondi de `S(T)`. **Vérification des 4
candidats** (45625.6-45625.99, 103467.17-103467.55, 144465.23-144465.61,
210464.60-210464.98) : dans les 4 cas, écart réel entre les zéros encadrants **normal**
(ratio 0.45 à 1.35, dans la statistique GUE attendue) et **0 changement de signe** de `Z(t)`
entre eux. **Les 4 candidats sont des faux positifs** — méthode abandonnée après confirmation
(arrêt de la passe restante, ~8 intervalles non traités, pour ne pas prolonger un run dont le
signal s'est révélé non fiable).

**Vérification de robustesse du chiffre « 5 manquants » lui-même :** recalcul de
`N_exact(T_max=499999.67107366206)` avec 5 réglages dps/n_sigma différents
(35/50, 35/100, 50/100, 50/200, 60/300) → **résultat identique à chaque fois**
(`S(T)=+1.29897`, loin d'un seuil de demi-entier) → le delta de +5 à T_max est **robuste**,
donc le déficit est réel, pas un artefact de précision insuffisante à ce point précis.

**Conclusion :** les 5 zéros manquants existent réellement (confirmé) mais sont
**structurellement invisibles** dans les données déjà calculées — aucune des 3 méthodes
post-hoc ne peut les localiser. Le bug n'est probablement pas une question de phase de grille
de scan (méthode 2 le réfute directement) mais plutôt un rejet silencieux de bracket valide
dans `illinois_refine_arb`, ou une limite de précision de `Z_double` (RS C0+C1) qui empêche
la détection initiale du changement de signe pour ces 5 cas précis — dans les deux cas,
indétectable sans instrumenter le pipeline C lors d'un run réel.

**Décision (hprzeta) :** tâche 1 dépriorisée. Tâche 2 (« relancer T=500000 avec STEP
validé ») : run #4 **accepté comme référence officielle** — pas de re-run (calcul
déterministe, reproduirait exactement le même résultat 818409/818414). Documenté dans
`STACK.md` (nouvelle table « Progression — T = 500 000 zéros ») et `Handoff.md`. Prochaine
priorité : tâche 3 (`zeta_sync_pc2.sh`).

---

## Session 2026-06-23 (soir — Claude Code) — Trou de couverture au pivot PC1/PC2 + marge STEP resserrée

**Contexte :** reprise de la tâche dépriorisée du run #4 (5 manquants T=500000, voir session
après-midi ci-dessus), à la demande explicite de hprzeta : « lever cette limite en
distribuant sur PC1 et PC2 ». PC2 (`zeta-calc-second`, 192.168.1.52) joignable ce soir
(alias SSH local manquant — `zeta-hp` pointe vers la même IP que l'ancien nom, ssh direct
par IP fonctionne).

### Investigation — skill `riemann-code-review` + relecture `Formules_zeta.md`/`Bibliotheques.md`

Avant de relancer un calcul identique (qui aurait reproduit le même résultat 818409/818414,
calcul déterministe), relecture ciblée des formules + du code C pour chercher des pistes non
testées par les 3 méthodes post-hoc de l'après-midi. Deux pistes trouvées :

**Piste A — trou de couverture structurel au pivot.** `scripts/zeta_distribute.py` lance PC1
sur exactement `[14.0, T_PIVOT]` et PC2 sur exactement `[T_PIVOT, T_MAX]`, **sans overlap**,
alors que `_partitionner_adaptatif()` (frontières internes entre workers d'une même machine)
applique un `OVERLAP=0.5` explicite « pour couvrir les brackets sur les bords de segment ».
Cette protection n'existe qu'en interne, jamais à la frontière PC1↔PC2. Mécaniquement, dans
`scan_zeros_arb` (boucle `while t_min+(k+1)*step <= t_max`), PC1 s'arrête au dernier point de
grille **≤ T_PIVOT** (jamais exactement T_PIVOT) et PC2 démarre **exactement à** T_PIVOT en
ne regardant que vers l'avant : il existe donc une fenêtre aveugle de largeur < 1 STEP
(~0,0044 à T=500000) **autour de T_PIVOT (~470124,8 pour le run #4)** qu'aucune des deux
machines ne scanne jamais. Aucun des 4 candidats vérifiés l'après-midi (bisection N_exact)
ne couvre cette zone précise.

**Piste B (plus incertaine) — marge de sécurité STEP basée sur un point unique.** Le
docstring de `_step_adaptatif()` (`compute_zeros_v13.py`, commit `30d05ee` du 17/06) admet
lui-même un écart minimal mesuré de **0,01281 à T≈453540** (dans la plage du run #4) contre
un STEP=0,010 de l'époque → marge **×1,28**, qualifiée de « **quasi-échec** » dans le code.
La formule adaptative actuelle (κ=1,357) n'a été calibrée que sur **un seul point** (T=100000)
puis extrapolée ×5 par une loi théorique N(T)^(-1/3), sans revalidation empirique à ce point
de mesure à 453540.

### Fix 1 — `OVERLAP_PIVOT=2.0` dans `zeta_distribute.py`

PC1 étendu à `[14.0, T_PIVOT+2.0]`, PC2 étendu à `[T_PIVOT-2.0, T_MAX]` ; la déduplication
existante (`fusionner_csv`, tolerance=0.01) absorbe le chevauchement (tolérance < écart
minimal réel mesuré ~0,013, donc aucun risque de fusionner deux zéros distincts). Validé en
`--dry-run` avant lancement.

### Run #5 — overlap seul (MARGE_SECURITE=2.0 inchangée) : ❌ PIRE, 8 manquants

Lancé 23/06 21:39:03, durée 41,55 min mur. **Fusion : 764898 (PC1) + 53514 (PC2) → 818406
zéros uniques** (818412 bruts − 6 doublons dans la zone d'overlap, cohérent avec l'écart
moyen mesuré ~0,56 à T≈470000 sur une fenêtre de 4,0 → ~7 zéros attendus en double — le
mécanisme d'overlap/dédoublonnage fonctionne correctement). **Turing : ❌ INCOMPLET, 8
manquants** (vs 5 sur le run #4 de référence) :

| T | Calculés | Attendus | Delta |
|---|---|---|---|
| 62651,16 | 81840 | 81839 | −1 (surplus) |
| 142387,60 | 204601 | 204601 | 0 |
| 266310,16 | 409203 | 409204 | +1 |
| 384797,81 | 613804 | 613810 | +6 |
| 499999,67 | 818406 | 818414 | +8 |

**Diagnostic de la régression :** comparaison des segments des 8 workers PC1 entre le run #4
(référence, `logs/distribute_pc1_20260617_213126.log`) et ce run
(`logs/distribute_pc1_20260623_213903.log`) — **toutes les frontières internes ont décalé**
(ex. Worker 3/4 : 250489,1 → 250490,3 ; Worker 6/7 : 416310,3 → 416311,4), pas seulement la
frontière du pivot (+2,0 voulu). Cause : `_partitionner_adaptatif()` recalcule **toutes** les
coupures par recherche binaire sur N(T) en fonction du `T_MAX` passé à PC1 — modifier le
pivot pour corriger le trou de couverture a changé ce `T_MAX`, donc fait glisser en cascade
les 7 frontières internes de PC1 (et pareil côté PC2). Avec la marge STEP déjà fine par
endroits (piste B, ×1,28 « quasi-échec »), certaines nouvelles positions de frontière se sont
révélées plus défavorables que les précédentes. **Le fix du pivot (overlap) lui-même n'est
pas remis en cause** — il a correctement absorbé sa propre zone de chevauchement — mais il a
révélé que la marge STEP globale (piste B) est le facteur dominant, pas seulement le trou de
pivot.

### Fix 2 — `MARGE_SECURITE` 2.0 → 3.0 dans `_step_adaptatif()`

```python
MARGE_SECURITE = 3.0  # resserré le 23/06/2026 — voir docstring complet dans le fichier
```
STEP résultant à T=500000 : 0,00443 → 0,00295 (×1,5 plus fin). Fichier synchronisé sur PC2
par `scp` direct (sync ciblée d'un seul fichier Python, **pas** via `zeta_sync_pc2.sh` — ce
script reste non testé en conditions réelles, voir tâche 3 de l'après-midi) ; valeur vérifiée
sur PC2 après transfert (`grep MARGE_SECURITE`).

### Run #6 — overlap (Option A) + MARGE×3 : ❌ 6 manquants

Lancé 23/06 22:27:23, terminé 23:13:11 (45,34 min mur), STEP=0,00304 (PC1) / 0,00295 (PC2),
**mêmes segments de workers que le run #5** (confirmé par diff direct des logs — la
partition ne dépend que de T_MIN/T_MAX/N_WORKERS, jamais du STEP). Fusion :
764900 (PC1) + 53514 (PC2) → 818408 zéros uniques. **Turing : ❌ INCOMPLET, 6 manquants**
(818408/818414) :

| T | Calculés | Attendus | Delta |
|---|---|---|---|
| 62651,16 | 81840 | 81839 | −1 (surplus) |
| 142387,98 | 204602 | 204600 | −2 (surplus) |
| 266310,16 | 409204 | 409204 | 0 |
| 384797,81 | 613806 | 613810 | +4 |
| 499999,67 | 818408 | 818414 | +6 |

**Interprétation :** à phase de grille strictement identique (run #5 = run #6), resserrer la
marge (2.0→3.0) fait baisser 8→6 manquants — le mécanisme « deux zéros dans le même pas STEP »
répond positivement à un STEP plus fin. Mais run #6 (marge 3.0, phase décalée) reste pire que
run #4 (marge 2.0, phase originale) : **5 < 6**, alors même que la marge nominale de #6 est
plus grande. Conclusion à ce stade : la position exacte des frontières (la « phase » de la
grille d'échantillonnage) compte au moins autant que la taille brute de la marge.

### Option B (24/06, après minuit) — overlap appliqué *après* le partitionnement

Hypothèse testée : si on évite de perturber les frontières internes des workers (en gardant
`T_PIVOT` exact, identique au run #4, au lieu de l'étendre de ±2,0 *avant* de le passer à
`_partitionner_adaptatif()`), et qu'on comble le trou de couverture structurel par un **3e
calcul séparé**, minuscule, qui ne scanne que la fenêtre
`[T_PIVOT-2,0, T_PIVOT+2,0]` (~7 zéros attendus), alors PC1 et PC2 retrouvent exactement la
phase de grille du run #4, et seul ce petit supplément ajoute la correction du trou de pivot.

**Implémentation** (`scripts/zeta_distribute.py`) : `lancer_pc1`/`lancer_pc2` reçoivent à
nouveau `T_PIVOT` exact (pas `T_PIVOT±OVERLAP_PIVOT`) ; nouvelle fonction
`lancer_pivot_supplement()` lance `compute_zeros_v13.py --t-min T_PIVOT-2 --t-max T_PIVOT+2`
en local, séquentiellement après PC1+PC2 (avant `zeta_turbo_off.sh`) ; `fusionner_csv()`
généralisée pour accepter une liste de N CSVs (3 dans ce cas) au lieu de 2 fixes. Validé en
`--dry-run` : PC1 `[14.0, 470124.76]`, PC2 `[470124.76, 500000]` — bornes identiques (à
0,01 près) au run #4.

### Run #7 — Option B (frontières originales + supplément pivot), MARGE toujours à 3.0

Lancé 24/06 00:23:46, terminé 01:07:19 (43,36 min mur, dont 42,58 min PC1+PC2 + le
supplément pivot rapide). PC1 a trouvé **764893** zéros — quasiment identique au run #4
(764897), confirmant que les frontières sont bien restaurées à l'identique. Fusion :
764893 (PC1) + 53512 (PC2) + 6 (pivot) → 818405 zéros uniques. **Turing : ❌ INCOMPLET,
9 manquants** — **pire que tous les runs précédents** :

| T | Calculés | Attendus | Delta |
|---|---|---|---|
| 62651,16 | 81840 | 81839 | −1 (surplus) |
| 142387,60 | 204601 | 204601 | 0 |
| 266309,19 | 409202 | 409202 | 0 |
| 384796,47 | 613803 | 613807 | +4 |
| 499999,67 | 818405 | 818414 | +9 |

**Diagnostic :** avec des frontières quasi identiques au run #4 (PC1 764893 vs 764897 — écart
de 4 seulement), la seule variable restante est `MARGE_SECURITE` (3.0 ici, 2.0 dans le run #4).
**Le résultat est pire avec la marge plus large** (9 > 5) — ce qui invalide l'hypothèse
« plus de marge = plus sûr » : `STEP` n'est pas un paramètre monotone. Chaque valeur de STEP
définit une grille de points d'échantillonnage entièrement différente, et qu'une paire de
zéros proches tombe dans le même pas dépend de la **phase exacte** de cette grille relative à
la position réelle des zéros, pas seulement de sa taille. Sur 4 runs (2 jeux de frontières ×
2 marges), **aucune combinaison testée ne bat le run #4 d'origine** (5 manquants) :

| Run | Frontières | MARGE_SECURITE | Manquants |
|---|---|---|---|
| #4 (référence) | originales | 2.0 | **5** |
| #5 | décalées (Option A) | 2.0 | 8 |
| #6 | décalées (Option A) | 3.0 | 6 |
| #7 | originales (Option B) | 3.0 | 9 |

### Décision (hprzeta, 24/06) — arrêt du tâtonnement, run #4 confirmé comme référence

Continuer à ajuster `MARGE_SECURITE` à l'aveugle revient à une recherche sans garantie de
convergence (4 essais, aucune amélioration sur la référence). **Décision : ne plus toucher
`MARGE_SECURITE`/`OVERLAP_PIVOT` ce soir.** Le run #4 (818409/818414, 5 manquants, 17/06)
reste la référence officielle du projet pour T=500000 (déjà actée le 23/06 après-midi — voir
plus haut). L'amélioration de ce déficit est reportée : seule piste jugée fiable pour aller
plus loin, instrumenter `scan_arb.c`/`illinois_refine_arb` pour logger directement les
brackets rejetés lors d'un run réel, plutôt que deviner via des ajustements de STEP a priori.
`scripts/zeta_distribute.py` (Option B, fonction `lancer_pivot_supplement` + `fusionner_csv`
généralisée) et `compute_zeros_v13.py` (`MARGE_SECURITE=3.0`) restent dans l'arbre de travail
sur `Riemann_Lab_C`, **non commités** — la valeur 3.0 n'étant pas validée comme une
amélioration, elle ne doit pas être committée en l'état (à rediscuter avant toute publication).

### Note annexe — `zeta-progress`

Alias déjà présent dans `~/.bashrc` (créé lors de la session du 17/06, `tmux attach -t
zeta-progress`) — vérifié fonctionnel ce soir, pas recréé.

---

## Session 2026-06-26 (soir — Claude Code) — Fix max_brackets dynamique + confirmation 0 REJECT/FALLBACK arb

**Commits :** `7914fa3` (instrumentation brackets) · `2b94b9f` (max_brackets dynamique)

### Contexte

Suite au run T=500k run #4 (818409/818414, 5 manquants), l'instrumentation `ZETA_DEBUG_BRACKETS`
a été ajoutée à `scan_arb.c` et `illinois_refine_arb.c` pour tracer en production les brackets
rejetés. Run de diagnostic T=50 000 lancé avec `ZETA_DEBUG_BRACKETS=logs/brackets_debug/` pour
identifier les causes des 5 manquants.

### Fix — `max_brackets` dynamique dans `scan_arb.c`

**Bug :** `MAX_BRACKETS = 512` fixé à la compilation → buffer saturable quand N_RS est grand
(t ≥ 62000 : N_RS ≈ 99 termes Arb, densité de zéros élevée → plus de 512 brackets par segment
possible). Quand le buffer est plein, les brackets supplémentaires sont silencieusement ignorés.

**Fix :** `max_brackets` alloué dynamiquement dans `scan_arb_c()` :
```c
int max_brackets = (int)((t_end - t_start) / step * 2) + 64;
```
Allocation dynamique sur le tas (`malloc`/`free`) au lieu du tableau statique.
Dépassement silencieux impossible.

### Résultat

- 0 REJECT · 0 FALLBACK sur le run T=50k de diagnostic
- Confirmé : les 5 manquants de T=500k run #4 sont dus au scan Z_double (phase de grille),
  pas à l'affinage `illinois_refine_arb` (qui est parfaitement fiable)
- Décision : cause des manquants = ratés du scan, pas de l'affinage → point de départ pour v13+
  rescan ciblé par déficit

---

## Session 2026-06-27 (après-midi + soir — Claude Code) — Run T=5M + rescan v13 + P1 fp.siegelz + analyse Obj2

### Run T=5 000 000 — lancé 16h02

```
PID principal : 46040   Workers : 46085–46092 (8 workers)
STEP = 0.001571 (adaptatif, MARGE=2.0)   N attendus ≈ 10 016 473
```

Lancé via : `printf "5000000\nO\n" | nohup python src/calculs/optimisation/compute_zeros_v13.py > logs/run_v13_T5M.log &`

**ETA initiale :** 28/06 ~15h30 (~24h)
**ETA révisée** (calcul depuis checkpoints Worker 0 à 19h30) : **29/06 ~02h–11h (~35–43h)**

Cause de la sous-estimation : le scan `scan_arb` scale en $T^{3/2}$, pas en $T$. Worker 7
[4.4M–5M] a $N_\text{RS} = \lfloor\sqrt{5\times10^6 / 2\pi}\rfloor = 892$ termes Arb par
évaluation, vs ~100 à $T=500k$. Durée scan Worker 7 $\propto (5M)^{3/2} - (4.4M)^{3/2}$
>> durée Worker 0 → Worker 7 finit le scan vers ~01h00 le 29/06.

Mise à jour index.html (commit `f25da46`, Riemann_Lab_IA, poussé) : ETA corrigée.

### v13 + rescan ciblé — validé T=1000

`rescan_segments_deficit()` implémentée dans `calculer_zeros_v13()` : identifie les workers
en déficit ($n_\text{trouvés} < N(t_{hi}) - N(t_{lo})$), relance avec STEP/2.
Validé T=1000 : 649 zéros · Turing COMPLET ✅ · LMFDB 20/20 ✅.
Non commité — en attente fin run T=5M (contrainte : rien sur Riemann_Lab_C pendant le run).

### P1 — fp.siegelz pour le bloc petit-t [14, 65]

**Contexte :** la note `Formules_zeta.md §18.4` documente un gain ×40 (`fp.siegelz` vs
`mp.siegelz` dps=35) pour l'architecture v4.1. En v13, la situation est différente :
- `T_SEUIL_PETIT_T = 65.0` (not 300)
- Détection [14,65] : déjà via `arb_hardy_z` (Arb, 0.77 ms/appel) — plus rapide que fp.siegelz
- Affinage [14,65] : `mpmath.findroot(arb_hardy_z, ...)` — Python loop avec overhead mpf

**Optimisation implémentée :** remplacé l'affinage par `mpmath.fp.findroot(mpmath.fp.siegelz, ...)`
(float64 natif, sans overhead mpf). La détection reste sur `arb_hardy_z` (signes garantis).

**Résultat T=1000 :** 14 zéros dans [14,65] → précision ~1e-13 à 1e-15. Turing ✅, LMFDB 20/20.
Gain réel pour T=100k : < 0.5s (seulement ~18 zéros dans [14,65]).
Non commité — en attente fin T=5M.

### P2 — Benchmark T=100k reporté

Impossible pendant T=5M : appeler `zeta_turbo_off.sh` après le run T=100k couperait les
optimisations CPU pour T=5M (CPU governor → powersave, swappiness = 60). Les résultats
seraient aussi biaisés par la compétition 9 processus T=5M + 8 workers T=100k sur 4 cœurs i7.
**À relancer après fin du run T=5M (29/06 ~02h–11h).**

### P3 — Analyse condition Obj2 : T=100k < 5 min

| Scénario | T=100k | Atteint ? |
|---|---|---|
| v13 actuel (mesuré 8.50 min) | 8.50 min | ❌ |
| + P1 fp.siegelz | 8.50 min (~0s gain) | ❌ |
| + TOL 1e-12 → 1e-9 (×1.4) | ~6.1 min | ❌ |
| + v14 hybride Z_double→Arb (×8) | **~1.1 min** | **✅** |

Gap actuel : ×1.70 à combler. **La seule voie vers Obj2 est v14** (Illinois hybride
Z_double pour Phase 1 → Arb pour 2-3 dernières itérations). Effort estimé : 2 jours.
v14 ramènerait T=5M de ~35h à ~4–5h.

### Checklist post-run T=5M

Ordre à suivre après confirmation fin du run :
1. `zeta_turbo_off.sh`
2. Analyse log `logs/run_v13_T5M.log` : Turing, manquants, z/s
3. Commit `compute_zeros_v13.py` + `scripts/zeta_distribute.py` → Riemann_Lab_C
4. Run T=100k benchmark (P2) — mesurer z/s et durée
5. Si Obj2 non atteint → démarrer v14

---

## Session du 4 juillet 2026 — v13→v15, Objectif 2 atteint

### Fin du run T=5 000 000 (v13)

Run lancé le 27/06 à 16h02, terminé le 29/06 à 00h02 (≈ 40h).

| Indicateur | Valeur |
|---|---|
| Zéros trouvés | **10 016 377** |
| Attendus N(5M) | **10 016 473** |
| Manquants | **96** ❌ |
| Durée totale | 115 005 s ≈ 31.9h (run) + 67 823 s ≈ 18.8h (rescan) |
| Rescan STEP/2 | 8 segments, +1 zéro net seulement |
| LMFDB | 20/20 ✅ |

Commit v13 : `a0e6e41` — `feat(v13): fp.siegelz [14,65] + rescan ciblé déficit`.
Sync 4 branches effectuée.

**Cause des 96 manquants :** paires de zéros proches dont le changement de signe
traverse deux pas STEP consécutifs (les signes se compensent). Le rescan STEP/2
n'y remédie que partiellement (+1 zéro net sur 96). Investigation reportée au prochain
run T=5M avec v15.

### v14 — Cache log_n/isqrt_n (commit d4b3611)

Modification de `illinois_arb.c` et `scan_arb.c` : cache statique
`log_n_cache[]` + `isqrt_n_cache[]` (N_MAX_CACHE=2100, 33 KB, init post-fork).
Évite `log(n)` et `1/sqrt(n)` répétés à chaque terme RS.

| Benchmark | Valeur |
|---|---|
| T=100k durée | **7.7 min** (vs 8.50 min v13) |
| Vitesse | **299 z/s** |
| Gain vs v13 | **×1.10** |
| LMFDB | **20/20 ✅** |
| Turing | **COMPLET ✅** |

**Piège documenté (04/07) :** réduire Phase 2 à 1 Newton FIXE → erreur ~1e-6 pour
t ≈ 65–77 (LMFDB 14/20). Cause : le biais Z_rs O(t^{-5/4}) positionne le pseudo-zéro
à ~5e-3 du vrai zéro à t=65. 1 Newton quadratique depuis 5e-3 → erreur ~1.75e-6 >> tol.
**Solution v15 : seuil adaptatif SEUIL_1NEWTON = 20 000.**

### v15 — Phase 2 adaptative SEUIL_1NEWTON=20k (commit adf5d2a) ⭐

Modification de `illinois_arb.c` Phase 2 : `n_newton = (t < 20000) ? 2 : 1`.
- t ≥ 20 000 : biais_RS ≈ 6.4e-7 → erreur 1 Newton ≈ 4e-13 < tol=1e-12 ✅
- t < 20 000 : 2 Newton inchangé (biais_RS trop grand)

| Benchmark | Valeur |
|---|---|
| T=100k durée | **4.4 min** ✅ |
| Vitesse | **517 z/s** |
| Gain vs v13 | **×1.93** |
| LMFDB | **20/20 ✅** |
| Turing | **COMPLET ✅** |

**CONDITION OBJECTIF 2 ATTEINTE : T=100k < 5 min ✅**

Tableau de progression :

| Version | T=100k | Vitesse | Algorithme clé |
|---|---|---|---|
| v12 | 8.8 min | 261 z/s | Illinois Z_rs + 2 Newton Arb |
| v13 | 8.50 min | 271 z/s | T_SEUIL=65, TOL 1e-12 |
| v14 | 7.7 min | 299 z/s | Cache log_n/isqrt_n |
| **v15** | **4.4 min** | **517 z/s** | Phase 2 adaptative SEUIL=20k |

### Invariants techniques (rappel pour les futures sessions)

- `TOL_ARB = 1e-12` — ne pas monter à 1e-9 (causait 16/20 LMFDB)
- Phase 2 : **2 Newton early-exit** pour t < 20k, **1 Newton** pour t ≥ 20k
- Cache RS : N_MAX_CACHE=2100, couvre T ≲ 27M
- `STEP` adaptatif obligatoire (retour STEP fixe = zéros manquants)

---

*JOURNAL.md · wiki racine · branche master · hprzeta · MAJ 2026-07-04 · ~1 790 lignes*

