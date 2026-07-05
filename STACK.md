# Riemann_Lab — Stack & Roadmap

> 🛠️ **Référence stable.** Outils, branches, matériel, roadmap formation. Change rarement.
> N'est *pas* relu au démarrage d'une session de calcul. État courant → `Handoff.md`,
> historique daté → `JOURNAL.md`.

---

## 🗺️ Contexte général

| Élément | Valeur |
|---|---|
| Dépôt GitHub | `hprzeta/Riemann_Lab` |
| Branche dév. Python | `Riemann_Lab_IA` ⭐ |
| Branche dév. C | `Riemann_Lab_C` (Phase C — Illinois en C/libmpfr) |
| Branche test | `Riemann_Lab_Test` |
| Branche production | `main` |
| GitHub Pages | `https://hprzeta.github.io/Riemann_Lab/` (depuis `/docs` sur `Riemann_Lab_IA`) |
| Wiki (dépôt séparé) | `~/projet_zeta/Riemann_Lab.wiki/` — branche `master` |
| Logo PNG | `docs/images/logo_riemann_lab.png` — 500×235 px, 11 Ko, exporté via cairosvg depuis le SVG animé |
| venv Python | `~/projet_zeta/zeta_env/` (Python 3.12) |
| Sources optimisation | `~/projet_zeta/src/calculs/optimisation/` |
| Mail projet | `hprzeta@protonmail.com` |

**Objectifs :**
1. **Numérique** — calculer les 10 000 premiers zéros non-triviaux de ζ(s) sur Re(s)=½ ✅ (10 142).
2. **Recherche** — agent IA autonome de recherche mathématique collaborant avec des IA universitaires.

---

## 🌿 Branches Git

| Branche | Rôle |
|---|---|
| `Riemann_Lab_IA` ⭐ | Développement principal — Python, wiki, docs, benchmarks |
| `Riemann_Lab_C` | Phase C — module C, libmpfr, Illinois accéléré, ASM |
| `Riemann_Lab_Test` | Tests ponctuels, Codespaces |
| `main` | Production — merge depuis `Riemann_Lab_IA` |

> Convention : toutes les branches suivent le préfixe `Riemann_Lab_*`.
> `phase-C-core` supprimée le 18 mai 2026 → renommée `Riemann_Lab_C`.

```bash
git checkout Riemann_Lab_IA   # Python, wiki, docs
git checkout Riemann_Lab_C    # Module C, libmpfr, Illinois C
git checkout Riemann_Lab_Test # Tests ponctuels
```

---

## 🖥️ Matériel

### Machine principale — `zeta-lab`

| Composant | Valeur |
|---|---|
| IP | 192.168.1.24 · WiFi |
| CPU | Intel i7, 4 cœurs |
| RAM | 8 GB soudés + **upgrade prévu : +16 Go SO-DIMM DDR4 2133 MHz → 24 Go total** |
| Swap actuel | 16 GB (nécessaire sous charge 8 workers — disparaîtra après upgrade) |
| GPU affichage | Intel HD Graphics 620 |
| GPU calcul | NVIDIA GeForce GTX 960M — 4 GB VRAM |
| CUDA | 12.0 / 12.2 — Compute Capability 5.0 (< 6.0 → NVRTC non supporté) |
| OS | Ubuntu, VSCode, Python 3.12 |

> **nvtop :** lire le graphe historique du haut (fiable), pas la colonne GPU%
> par processus (bursts ~50 ms invisibles à l'échantillonnage 2 s).
> `OLLAMA_MODELS=/mnt/data/models_ia/ollama` · `OLLAMA_CUDA=1` (`.bashrc`).
> 1 seul modèle LLM à la fois (4 GB VRAM).

### Stockage — disque rejeté

> **SSD 3.8 To externe (USB, `/dev/sdb`) — REJETÉ.** Testé sur `zeta-lab` (PC1)
> le 21 juin 2026 en vue d'un volume dédié au vault RAG/ChromaDB de l'Objectif 2.
> `mkfs.ext4` a échoué (erreur d'E/S), dmesg a révélé une erreur SCSI
> *« Logical block address out of range »* dès ~2,03 To (bien avant les 3,81 To
> annoncés). Confirmation finale par `f3probe --destructive` : **capacité
> utilisable = 0 octet (0 bloc)**. Disque défectueux ou frauduleux (fausse
> capacité). Retourné au vendeur / mis au rebut. **Ne jamais réintégrer ce
> disque au projet.**

### Stockage — vault RAG (Objectif 2)

> **SSD Micron 1100 256 Go (`Micron_1100_MTFDDAK256TBN`, S/N `1702155DE7AA`)
> — EN SERVICE depuis le 22 juin 2026.** Disque de remplacement après le rejet
> du SSD 3,8 To ci-dessus (modèle différent, capacité réelle confirmée :
> 256 GB / 238,47 GiB). SMART : `PASSED`, 89 % lifetime remaining, 1991 h
> d'usage, 1002 cycles d'allumage — usure normale (occasion).
> ⚠️ Anomalie mineure non bloquante : liaison SATA négociée à 1,5 Gb/s
> (max 6,0 Gb/s) + 2 erreurs CRC UDMA, probablement câble/port — à surveiller.

| Élément | Valeur |
|---|---|
| Device | `/dev/sdb1` (partition unique, GPT, pleine disque) |
| Filesystem | ext4 — `mkfs.ext4 -i 8192 -m 1 -L vault_rag` |
| UUID | `9476fad5-8512-4e0d-8cd4-50c9acae01c2` |
| Point de montage | `/mnt/vault_rag` (`fstab` : `defaults,noatime`) |
| Propriétaire | `riemann:riemann` |
| Arborescence | `chromadb/` · `corpus/` · `llamaindex_cache/` · `agent_logs/` |
| Usage | Vault RAG/ChromaDB — Objectif 2 (agent IA autonome de recherche) |
| Mise en service | 22 juin 2026 |

### Cluster Zeta — toutes les machines

| Hostname | Matériel | CPU | RAM | IP locale | IP VPN | Réseau | Rôle |
|---|---|---|---|---|---|---|---|
| `zeta-lab` | Machine principale | Intel i7 · 4 cœurs | 8 GB + 16 GB swap | 192.168.1.24 | 10.10.0.2 | WiFi | Calcul + orchestration |
| `zeta-calc-second` | HP Compaq 8000 Elite CMT · CM HP 3647h | Core2Duo E8400 3 GHz | 4 GB DDR3 | 192.168.1.52 | — | Gigabit ETH | Nœud calcul auxiliaire |
| `zeta-backup` | Compaq-Presario SG3210FR · CM ECS Livermore8 | Pentium E2140 1.6 GHz | 3 GB DDR2 | 192.168.1.22 | — | 100 Mbit ETH | Relais backup → ProtonDrive |
| **`zeta-secure`** | **PC4 — bastion VPN/pare-feu** | **x86 i386** | — | **192.168.1.54** | **10.10.0.1** | **ETH · OpenBSD 7.9** | **Point d'entrée VPN externe ✅** |

> Renommage effectué le 2026-06-13 : `hp3647h` → `zeta-hp3647h` · `pcfix2` → `zeta-livermore8`.
> PC4 `zeta-secure` ajouté le 2026-06-15 — bastion WireGuard IPv6, accessible depuis 4G.
> Renommage 2026-06-16 : `zeta-hp3647h` → `zeta-calc-second` · `zeta-livermore8` → `zeta-backup` · `zeta-del.local` → `zeta-secure` (PC4).
> Préfixe `zeta-` uniforme sur tout le cluster.
> Accès externe : `zeta-secure.duckdns.org:51820` (AAAA — CGNAT IPv4 sur la box SFR).
> Doc complète : `Architecture-Cluster-Zeta.md` §10-15.

---

## 🔧 Infrastructure backup

### Pipeline nocturne (automatique)

| Étape | Machine source | Heure | Destination | Commande |
|---|---|---|---|---|
| 1 — rsync local→Acer | `zeta-lab` (cron 01h50) | 01h50 | `pjexosql@192.168.1.22:~/backup/` | `rsync -aq -e 'ssh -i ~/.ssh/id_acer' logs/ wiki/ pdf/` |
| 2 — rclone Acer→cloud | `zeta-backup` (cron 02h00) | 02h00 | `protondrive:hprzeta/Riemann_Lab/backup/` | `/usr/bin/rclone copy ~/backup/` |

- Clé SSH `~/.ssh/id_acer` (ed25519, sans passphrase) — connexion automatique `zeta-lab → zeta-backup`
- Répertoires sauvegardés : `logs/` · `wiki/` · `pdf/`

### Scripts & diagrammes

| Fichier | Commit | Rôle |
|---|---|---|
| `scripts/backup_cluster_map.sh` | `cd11a5f` | Génère les 2 SVGs ci-dessous |
| `docs/images/backup_cluster_map.svg` | `cd11a5f` | Diagramme du pipeline backup (rsync + rclone) |
| `docs/images/topo_machines_zeta.svg` | `cd11a5f` | Topologie matérielle du cluster Zeta |
| `docs/backup_cluster_map.svg` | `c33fb3a` | Copie racine docs/ |
| `docs/topo_machines_zeta.svg` | `c33fb3a` | Copie racine docs/ |

---

## 🤖 Stack « Second Cerveau IA »

### LLM locaux (Ollama)

| Modèle | Taille | Statut | Rôle |
|---|---|---|---|
| `mathstral:latest` | 4.1 GB | ✅ | Maths + ζ(s) symbolique |
| `deepseek-coder:6.7b` | 3.8 GB | ✅ | Code Python/C |
| `qwen3:4b` | ~2.5 GB | ✅ | Polyvalent rapide |
| `deepseek-math:7b` | ~3.8 GB | 🔜 | Meilleur raisonnement math pur |
| `phi3:mini` | ~2.3 GB | 🔜 | Ultra-léger |

```bash
ollama pull deepseek-math:7b
ollama pull phi3:mini
```

### LLM en ligne (navigateur)

| Outil | Modèle | Usage |
|---|---|---|
| Claude | Sonnet 4.5 | Cerveau de session — mémoire, structure, maths longues, wiki |
| Copilot ⭐ | GPT-4.5 | Cadrage Phase C, génération PDF + prompts voie B/v5 |
| Perplexity | — | Recherche web + arXiv |
| Kimi | — | Lecture longs PDF (Titchmarsh, Odlyzko) |
| DeepSeek | — | Raisonnement math alternatif |

### Skills Claude

| Skill | Statut | Rôle |
|---|---|---|
| `riemann-lab` | ✅ | Mémoire projet — KaTeX, wiki, Python, Git |
| `phase-c-illinois` | ✅ | Phase C — libmpfr, Illinois C, ctypes |
| `code-review` | 🔜 | Audit code Python/C |
| `security-review` | 🔜 | Vérif sécurité scripts et `.so` |
| `mattpocock/skills` | 🔜 (Obj. 2) | Skills communautaires généralistes |

### MCP · RAG · Tools

| Outil | Statut | Rôle |
|---|---|---|
| Context7 (MCP) | 🔜 | Doc à jour (mpmath, numpy, libmpfr) injectée dans Claude |
| LlamaIndex | 🔜 | RAG — ingestion PDFs + wiki + GitHub |
| ChromaDB | 🔜 | Base vectorielle locale `~/projet_zeta/brain/` |
| sentence-transformers | 🔜 | Embeddings locaux |
| Manim | 🔜 | Animations math (style 3Blue1Brown) |
| Flowise | 🔜 (fin Obj. 1) | Second Cerveau visuel low-code |
| n8n / Activepieces | 🔜 (Obj. 2) | Automatisation GitHub → mail → publication |
| LangChain / LM Studio | 🔜 (Obj. 2) | Framework agent complet |

```bash
pip install manim llama-index chromadb sentence-transformers
npx flowise start   # http://localhost:3000
```

---

## 📋 Roadmap

### Objectif 1 — finalisation (10 000 zéros → 100 000 zéros)
- [x] Run `compute_zeros_v4_1` à T=10 000 — **10 141 zéros, Turing COMPLET, 18.65 z/s** ✅
- [x] Comparer aux tables LMFDB — 19/20 précision ≤ 1e-10 ✅
- [x] Visualisations dans `/docs` — 8 animations HTML + index.html, validées Playwright ✅
- [x] Logo PNG statique `docs/images/logo_riemann_lab.png` — README + wiki Home.md, 4 branches ✅
- [x] Run T=100 000 — **138 069 zéros, Turing COMPLET, 30.9 min, 74.49 z/s (v7)** ✅
- [x] Site GitHub Pages mis à jour v6+v7 — commit `9dc0d23`, vérifié 11 juin 2026 ✅
- [x] Benchmark v8 — prec_fast/prec_full + W=4 vs W=8 → plancher hardware i7 atteint ✅
- [x] Fix lien PDF cassé dans `Phase-Optimisation-compute_zeros_v3.md` + `git push origin master`. ✅ corrigé (raw.githubusercontent.com)
- [x] v9 Brent C/mpfr : 26.6 min (turbo) · ×1.80 vs v8 ✅
- [x] v10 W=8 forcé : 23.7 min · ×5040 vs v1 ✅
- [x] v12 : Illinois hybride 2-phases (illinois_arb.c) — **8.8 min T=100k · 0 manquant · Turing COMPLET ✅**
- [x] **v13 + rescan ciblé par déficit** — Section 3b `rescan_segments_deficit()`, STEP/2 parallèle — validé T=1000 ✅ — commit `77efd10`
- [x] **Run T=5 000 000 terminé** (04/07/2026, PC1 turbo, ~38h) — **10 016 377 / 10 016 473 zéros · 96 manquants** · cause : paires proches non détectées par grille Z_double
- [x] **v14 — Cache RS statique log_n/isqrt_n** — gain ×1.10 · T=100k 7.7 min · commit `d4b3611` ✅
- [x] **v15 — Phase 2 adaptative SEUIL_1NEWTON=20k** — gain ×1.93 vs v13 · T=100k 4.4 min · **Condition Obj2 atteinte ✅** · commit `adf5d2a`
- [ ] Wiki — Partie 2 (Z(t), zéros non-triviaux).
- [ ] Rapport `analyse_problemes_v13_v15.md` + PDF dans `pdf/optimisation/`

### Phase C — accélération Illinois
- [x] Appliquer + valider Option B (`illinois_refine` fa/fb depuis Python) — T=10 000 ✅
- [x] Instrumentation brackets `ZETA_DEBUG_BRACKETS` — commits `7914fa3` + `2b94b9f` ✅
- [x] Rescan ciblé par déficit `rescan_segments_deficit()` dans v13 — validé T=1000 ✅
- [x] **v14 — Cache RS statique** (`illinois_arb.c` + `scan_arb.c`) — Phase 1 accélérée · 7.7 min T=100k ✅
  - log_n_cache[2101] + isqrt_n_cache[2101] · 33 KB · init post-fork · couverture T≲27M
  - **Condition Obj2 : T=100k < 5 min. Écart résiduel v14 : 7.7 → 5 min.**
- [x] **v15 — Phase 2 adaptative SEUIL_1NEWTON=20 000** — `#define SEUIL_1NEWTON 20000.0` ✅
  - biais_RS(20k) ≈ 6.4e-7 → erreur 1 Newton ≈ 4e-13 < tol · 87% des zéros T=100k bénéficient
  - **Condition Obj2 atteinte le 2026-07-04 : T=100k = 4.4 min < 5 min ✅**
- [ ] **v16 — Odlyzko-Schönhage** (long terme) — O(N log²N) vs O(N × √T) → gain ×50+ à T=5M
- [ ] Rapport `analyse_problemes_v13_v15.md` + PDF · investigation 96 manquants T=5M au prochain run v15
- [ ] Rapport `v5 → v4.1` : `pdf/optimisation/analyse_problemes_v5_v4_1.pdf`.

### Objectif 2 — agent IA autonome (**DÉMARRAGE — condition Obj1 atteinte le 04/07/2026**)
- [x] **Condition préalable : T=100k < 5 min** — atteinte le 04/07/2026 avec v15 (4.4 min) ✅
- [ ] Anthropic Skilljar : Claude Code 101 → MCP intro/avancé → Subagents → Agent Skills.
- [ ] MCP → connexion GitHub / wiki.
- [ ] Agent capable de : publier sur `hprzeta.github.io/Riemann_Lab/`, générer les
      rapports v→v+1, envoyer les résultats à `hprzeta@protonmail.com`, collaborer
      avec des IA universitaires.
- [ ] RAG vault (`/mnt/vault_rag`) : ChromaDB + LlamaIndex sur SSD Micron 1100 256 Go.
- [ ] Investigation 96 manquants T=5M : run v15 à T=5M pour confirmer réduction.

### Formation
| Ressource | Usage |
|---|---|
| roadmap.sh | Roadmaps Python, IA, agents |
| build-your-own-x | Implémenter RAG / agent / LLM from scratch |
| Anthropic Skilljar | Parcours Claude Code → MCP → Subagents |

---

## 📚 PDF de cadrage et cours (Voie B5)

| PDF | Thème | Message clé |
|---|---|---|
| 01 | Cartographie diagnostic | Conserver l'historique, ne pas repartir de zéro |
| 02 | Migration / Brain Vault / RAG | Structure, recovery, données validées |
| 03 | Checklist Linux | Git, GPU, Python, Ollama, partitions |
| 04 | Scripts post-audit | Extraction archive, mini-audit Git |
| 05 | Complément Git | Branches confirmées, `Riemann_Lab_C` = c_modules |
| 06 | Lexique IA & Brain Vault | Vault, RAG, Skills, agents, grounding |
| 07 | Pavé primalité | Premiers, produit eulérien, ψ(x), formule explicite |
| 08 | CryptoZeta | RSA, ECC, post-quantique, hash, recovery |
| 09 | Synthèse Phase C v4 voie B | v4 hybride validé T=650 |
| 10 | Résumé + prompt v5 | Passerelle → Claude Code voie B/v5 |

---

## 🔗 Références

| Ressource | Lien |
|---|---|
| Site du projet | https://hprzeta.github.io/Riemann_Lab/ |
| Code source | https://github.com/hprzeta/Riemann_Lab/tree/Riemann_Lab_IA/src |
| LMFDB | https://lmfdb.org/zeros/zeta/ |
| Odlyzko & Schönhage 1988 | https://doi.org/10.1090/S0002-9947-1988-0936813-0 |
| Turing 1953 | https://doi.org/10.1112/plms/s3-3.1.99 |
| Titchmarsh — Theory of ζ (§4.12) | https://archive.org/details/theoryofriemann00titc |

---

## Progression des versions — T = 10 000 zéros

| Version | Temps | Gain vs v1 | Algorithme clé | Formule principale |
|---|---|---|---|---|
| v1 | 21h | — | Newton scalar | $\zeta(\frac{1}{2}+it)$ Newton séquentiel, 1 worker |
| v2 | 2h | ×10 | Illinois + Z(t) | $Z(t) = e^{i\theta(t)}\zeta(\frac{1}{2}+it)$ · bracket Illinois |
| v3 | 45min | ×28 | Parallèle W=4 | T/W par worker · post-fork .so · N(T) corrigé |
| v4.1 | 9min | ×140 | Illinois C/libmpfr | `illinois_mpfr.c` · $(f_a, f_b)$ pré-calculés Python→C |
| **v4.1+Arb** | **2.60 min** | **×484** | **Arb + STEP adaptatif** | Arb ×27 · STEP 0.05/0.010 · overlap=2.0 · Turing COMPLET |

> ×484 = 21h / 2.60 min — mesuré T=10 000 (2026-06-10 · commit `50837f7`).
> STEP adaptatif **v3** (commit `181fdd1`) : 0.05 (t<5k) / 0.010 (t≥5k) + overlap fixe 2.0.

Speedup Arb vs mpmath : ×27 (0.77 ms vs 21.13 ms, mesuré `benchmark_arb_vs_mpmath_20260609`)

---

## Progression des versions — T = 100 000 zéros

| Version | Temps | Gain | Zéros | Algorithme clé | Commit |
|---|---|---|---|---|---|
| v1 (STEP=0.1 fixe) | ~1h58 | — | 137 904 | baseline | — |
| v2 (STEP adaptatif 0.1/0.05/0.02) | ~105 min | — | 138 039 | Turing INCOMPLET ❌ | — |
| v3 (STEP adaptatif 0.05/0.010) | ~113 min | — | 138 069 | scan_arb.c Z_double | `181fdd1` |
| v6 (STEP=0.010 fixe, scan_arb.c) | ~130 min | — | 138 069 | Z_double C inline · 0 manquant ✅ | `b676e88` |
| v7 (illinois_refine_adaptive) | 30.9 min | ×4.2 vs v6 | 138 069 | prec=64 bits → 1 limb → SIMD ×16 | `8637098` |
| v8 (prec_full=80 bits) | 50.5 min* | ×1.06 vs v7 | 138 069 | prec_full 116→80 bits | — |
| v9 (Brent C/mpfr) | 26.6 min (turbo) · 28.0 min (sans) | ×1.80 vs v8 | 138 069 | Brent IQI+sécante+bissection (ordre ~1.84) | `1c8c0ab` |
| **v10 (W=8 forcé)** | **23.7 min (turbo)** | **×1.12 vs v9** | **138 069** | **W=8 forcé — Brent grand t dilue overhead HT** | `c9fad76` |
| **v12 (Illinois hybride 2-phases)** | **8.8 min (turbo) ✅ mesuré** | **×2.69 vs v10 · ×16.9 benchmark** | **~138 080** | **Z_rs_double Phase 1 (0.015 ms) + 2 Newton Z_arb Phase 2** | `f0e8430` |
| **v13 PC1 seul** | **8.50 min ✅** | **×1.04 vs v12** | **138 069** | **T_SEUIL_PETIT_T 200→65 · TOL_ARB 1e-9→1e-12 · scan_arb C** | `77efd10` |
| **v13 distribué PC1+PC2** | **8.50 min mur ✅** | **×20 000+ vs v1** | **138 069** | **zeta_distribute.py · pivot N(T) marge −15% · Turing COMPLET** | `98de98e` |
| **v14 (cache log_n/isqrt_n)** | **7.7 min ✅** | **×1.10 vs v13** | **138 069** | **Cache RS statique 33 KB · init post-fork · Phase 2 inchangée (2 Newton early-exit)** | `d4b3611` |
| **v15 (SEUIL_1NEWTON=20k) ⭐** | **4.4 min ✅** | **×1.93 vs v13 · ×28 600+ vs v1** | **138 069** | **Phase 2 adaptative : 1 Newton si t≥20k (87% des zéros T=100k) · LMFDB 20/20** | `adf5d2a` |

*v9 : gain turbo ×1.05 seulement — bottleneck MPFR/mémoire (vs ×1.63 pour v7). Swappiness déjà à 10 lors du run sans turbo.*
*v10 : W=8 forcé sur i7-7500U (2 cœurs physiques, 4 logiques). Gain ×1.12 > ×0.99 benchmark v8 — car Brent grand t (~64 ms/appel) dilue l'overhead HT du context-switch.*

**Gain global v1 → v9 mesuré sans turbo : ×4 300** (21h → 28 min)
**Gain global v1 → v9 avec turbo : ×4 500** (21h → 26.6 min)
**Gain global v1 → v10 avec turbo : ×5 040** (21h → 23.7 min)
**Gain global v1 → v13 distribué PC1+PC2 : ×20 000+** (21h → 8.5 min mur)
**Gain global v1 → v15 (PC1 local) : ×28 600+** (21h → 4.4 min) — **Condition Objectif 2 atteinte ✅ le 2026-07-04**

---

## Progression — T = 5 000 000 zéros

| Version | Temps | Zéros | Statut | Note |
|---|---|---|---|---|
| **v13 PC1 local + rescan ciblé — TERMINÉ** | **~38h réel (lancé 27/06 16h02 → terminé ~04/07)** | **10 016 377 / 10 016 473** | **96 manquants — run terminé** | STEP=0.001571 · 8 workers · turbo · N_RS=892 termes Arb |

> **96 manquants** : cause identifiée = paires de zéros très proches dont le changement de signe
> ne passe pas à travers la grille Z_double (phase de grille défavorable). Non lié à Illinois.
> Prochaine piste : run v15 à T=5M pour confirmer réduction (Phase 1 cache + Phase 2 adaptative).

---

## Progression — T = 500 000 zéros

| Version | Temps | Zéros | Statut | Commit |
|---|---|---|---|---|
| **v13 distribué PC1+PC2 — run #4 (RÉFÉRENCE OFFICIELLE)** | **35.36 min mur** | **818 409 / 818 414 (99,9994 %)** | **Turing INCOMPLET (5 manquants) — accepté comme limitation connue** | `8f755eb` |
| v13 distribué + `OVERLAP_PIVOT=2.0` seul (Option A) — run #5 | 41.55 min mur | 818 406 / 818 414 | ❌ 8 manquants — pire | non commité |
| v13 distribué + overlap (A) + `MARGE_SECURITE=3.0` — run #6 | 45.34 min mur | 818 408 / 818 414 | ❌ 6 manquants — toujours pire | non commité |
| v13 distribué Option B (frontières originales + supplément pivot séparé) + MARGE×3 — run #7 | 43.36 min mur | 818 405 / 818 414 | ❌ 9 manquants — pire que tout | non commité |

> **24/06 — 4 tentatives de levée des 5 manquants, aucune n'a fait mieux que le run #4.**
> Diagnostic après-midi du 23/06 (3 méthodes post-hoc) épuisé sans résultat ; relecture
> `Formules_zeta.md`/`Bibliotheques.md` + skill `riemann-code-review` a fait remonter le
> trou de couverture structurel au pivot PC1/PC2 (`zeta_distribute.py` sans overlap, run #5)
> et une marge STEP « quasi-échec ×1,28 » documentée dans le code lui-même. 2 jeux de
> frontières (originales / décalées par l'overlap) × 2 marges (2.0 / 3.0) testés — **aucune
> combinaison ne bat les 5 manquants du run #4** :
>
> | Run | Frontières workers | MARGE_SECURITE | Manquants |
> |---|---|---|---|
> | #4 | originales | 2.0 | **5** |
> | #5 | décalées (Option A) | 2.0 | 8 |
> | #6 | décalées (Option A) | 3.0 | 6 |
> | #7 | originales (Option B) | 3.0 | 9 |
>
> **Conclusion :** `STEP`/`MARGE_SECURITE` n'est pas un paramètre monotone — chaque valeur
> définit une grille d'échantillonnage différente, et la phase exacte de cette grille compte
> au moins autant que la taille nominale de la marge. Continuer à tâtonner cette valeur à
> l'aveugle n'a pas de garantie de convergence. **Décision (hprzeta, 24/06) : arrêt du
> tâtonnement.** Le run #4 reste la référence officielle. Prochaine piste, si reprise un jour :
> instrumenter `scan_arb.c`/`illinois_refine_arb` pour logger directement les brackets
> rejetés lors d'un run réel, plutôt que deviner via STEP. Détail complet : `JOURNAL.md`
> sessions 23/06 (soir) et 24/06.
>
> **Historique (ancien diagnostic, après-midi 23/06) :** 3 méthodes de localisation post-hoc
> sur le run #4 (analyse statistique des écarts, scan à phase de grille décalée, bisection
> N_exact) — toutes négatives ou faux positifs sur les 5 manquants d'alors.

### Infrastructure — zeta_turbo

| Script | Commit | État | Note |
|---|---|---|---|
| `zeta_turbo_on.sh` | — | ✅ fonctionnel | sudoers `/etc/sudoers.d/zeta_turbo` installé 2026-06-12 · gain mesuré : 26.6 min T=100k |
| `zeta_turbo_off.sh` | — | ✅ fonctionnel | restauration CPU governor + swappiness + services |
| `zeta_run.sh` | `33205f2` | ✅ mis à jour | pointe sur `compute_zeros_v12.py` depuis 2026-06-13 (était v4_1) |
| `zeta_sync_pc2.sh` | `23a79b7` | ⚠️ créé, non testé | rsync sources Python+C vers PC2 + recompile `scan_arb.so`/`illinois_mpfr.so`/`illinois_arb.so` (détection auto `libflint-arb` système via `ldconfig`) — à valider, PC2 injoignable le 23/06 |

> **Découverte v7 :** réduire $N_\text{termes}/4$ invalide les signes Z_rs (faux zéros).
> Le vrai levier : `prec_fast = 64 bits` → 1 limbe mpfr → SIMD AVX2 automatique.
> Gain ×16 local (phase 1), ×3.7 global. Analyse : `analyse_problemes_v6_v7.md`.

> **Benchmark v8 :** `prec_full=80 bits` → ×1.06 (gain marginal). W=8 contre-productif sur
> i7-7500U (dual-core HT, 4 threads logiques). Plancher hardware atteint. Voir §24 Formules_zeta.md.

> **v9 Brent :** gain ×1.78 sur benchmark [1000,50000], +3% seulement sur T=10k (faible t → N_full petit).
> Gain T=100k attendu supérieur (majorité des zéros à grand t → N_full élevé). Analyse : `analyse_problemes_v8_v9.md`.

**Run T=10 000 v4.1+Arb validé :** 10 141/10 142 zéros · 2.60 min · Turing COMPLET · LMFDB 19/20

---
> *Mise à jour : 6 juin 2026 · 9 juin 2026 · 10 juin 2026 · 11 juin 2026 · 12 juin 2026 · 13 juin 2026 · 15 juin 2026 (VPN WireGuard IPv6) · 16 juin 2026 (renommage hostnames) · 21 juin 2026 (SSD 3.8 To rejeté) · 23 juin 2026 (T=500k run #4 référence officielle, zeta_sync_pc2.sh) · 24 juin 2026 (arrêt tâtonnement STEP) · 27 juin 2026 — v13 rescan ciblé implémenté, run T=5M lancé · **4 juillet 2026 — T=5M terminé (96 manquants), v14 (7.7 min ×1.10), v15 (4.4 min ×1.93), Condition Obj2 atteinte ✅, démarrage Objectif 2** · STACK.md*
