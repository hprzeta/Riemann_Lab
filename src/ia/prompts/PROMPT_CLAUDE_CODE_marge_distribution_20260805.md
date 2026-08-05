> ⚠️ **ARCHIVE (2026-08-05)** — document historique. Les infos cluster (IP, hostnames,
> versions, état du run) peuvent être périmées. Source de vérité actuelle :
> `Riemann_Lab.wiki/Handoff.md` et `~/riemann_handoff/Handoff.md`.

# Prompt de reprise — MARGE_SECURITE, distribution PC1/PC2, alimentation PC1 — 2026-08-05

## Contexte projet

Riemann_Lab — exploration numérique de l'Hypothèse de Riemann.
Branche active : `Riemann_Lab_C`.
Wiki : `~/projet_zeta/Riemann_Lab.wiki/` (branche master).

**Lire en premier : `Riemann_Lab.wiki/Handoff.md`** (état courant complet).

## Chronologie de la session (02 → 05/08/2026)

### 1. Diagnostic cause racine des 96 manquants — régression `MARGE_SECURITE`

`MARGE_SECURITE` avait été abaissée de 3.0 à 2.0 juste avant le run T=5M du 27-29/06
(commit `a0e6e41`, jamais documenté), annulant sans le dire le correctif du 23/06
(`7914fa3`) déjà posé après un run T=500000 à 8 manquants. Le rescan STEP/2 ajouté en
compensation n'a récupéré que +1 zéro sur 96. Commit `a7fb498` : `MARGE_SECURITE`
restaurée à 3.0.

### 2. Tests non censurés — recalibration κ rejetée, mesure directe décisive

Tentative de recalibrer κ sur 3 points réels (CSV T=100k/500k/5M déjà produits) :
**rejetée** (`63de0f2`) — l'« espacement min » logué dans chaque run n'est pas l'écart
minimal réel entre zéros, seulement l'écart minimal parmi les zéros **détectés**,
plafonné par en-dessous par la résolution du scan (censure à gauche dès qu'un run a des
manquants). Mesure **non censurée** à la place : rescan ciblé fin (`arb_hardy_z`,
précis, STEP/10) sur 3 fenêtres réelles, comparé à une simulation du scan normal sur les
mêmes fenêtres :

| Zone | Manquants à MARGE=3.0 |
|---|---|
| T≈130 060 | 0 |
| T≈865 898 | 0 |
| T≈4 862 705 | **2** ❌ |

Bisection sur la zone haute-T : MARGE≈12 = seuil de suffisance mesuré. `MARGE_SECURITE`
relevée à 15.0 (`a04ea1f`), puis re-testée à 6/8/10 sur les 3 zones → **10.0** retenue
(plus basse valeur qui passe partout). Re-testée une dernière fois précisément au vrai
pivot PC1/PC2 du run T=5M cible (T≈3 469 744, run réel PC1+PC2+pivot sur une fenêtre de
40 unités) : 84 zéros fusionnés, 0 manquant vs référence indépendante. `MARGE_SECURITE
= 10.0` validée solo + en distribution (commit `bbb8a6f`).

### 3. Portage distribution v13→v15 + découverte ratio réel PC2

`zeta_distribute.py` portait encore sur `compute_zeros_v13.py` (jamais adapté depuis
juin) → porté vers `compute_zeros_v15.py`, alias SSH alignés sur le renommage du 16/06
(`zeta-calc-second` + clé `zeta_cluster`). `zeta_sync_pc2.sh` exécuté pour la première
fois : recompilation `illinois_arb.so`/`scan_arb.so` sur PC2 (obsolètes, sans le code
SEUIL_1NEWTON de v15). Commit `38c2b36`.

**Découverte critique :** python-flint 0.8.0 est installé sur PC2 — absent lors de la
mesure historique (52 z/s) qui fondait le split 92,3%/7,7% (ratio ×12 supposé). Remesuré
à neuf, mêmes conditions (v15, T=1000) : **PC1=822,48 z/s, PC2=512,19 z/s → ratio réel
×1,6**. Nouveau split appliqué : PC1 67,4% / PC2 32,6% de N(T).

Validation du pivot en conditions réelles (pas une simulation) : run distribué complet
T=50000, Turing COMPLET (0 manquant, 63519 zéros) + vérification indépendante au pivot
(14/14 zéros identiques, positions concordantes au 8ᵉ chiffre).

### 4. Incident d'alimentation PC1 — 3 redémarrages non planifiés

Run T=5M lancé le 02/08 20h29 (PID 200788) jamais abouti — tué par 3
redémarrages/extinctions non commandés en moins de 24h (03/08 00h45, 03/08 19h19, puis
extinction ~18h45 jusqu'au 04/08 18h19). Reconstitué via `sar` (journal systemd
volatile, un seul boot conservé).

**Cause :** PC1 sur batterie, débranché (2 alertes « Running on LOW Battery »).
`CriticalPowerAction=HybridSleep` à 5% de batterie, mais **aucun `resume=` câblé**
(absent de `/proc/cmdline` et `/etc/initramfs-tools/conf.d/resume`) malgré une swapfile
16G disponible (fichier, pas partition — nécessiterait en plus un `resume_offset=`
précis). La veille hybride ne peut pas reprendre proprement → dégénère en
redémarrage/extinction sauvage.

**Correctif (PC1 uniquement) :**
```bash
sudo sed -i 's/CriticalPowerAction=HybridSleep/CriticalPowerAction=PowerOff/' \
  /etc/UPower/UPower.conf
sudo systemctl restart upower
```
Audit des 4 machines du cluster : aucune politique de veille automatique active nulle
part (PC2/PC3 défauts systemd, PC4/OpenBSD sans `apmd`). Détail →
`Guide-Linux-Commandes.md` §19.

### 5. Lancement du run T=5M v15 (2ᵉ tentative)

Relancé le 04/08 22h48 via `zeta-distribute 5000000`, PID `32270`, secteur vérifié
branché. Segmentation inchangée (PC1 67,4% / PC2 32,6%, MARGE_SECURITE=10.0).

**Observations en cours de run (05/08) :**
- Architecture scan-puis-affinage : chaque worker scanne tout son segment en un seul
  appel bloquant avant de produire la moindre ligne de progression — de longues périodes
  sans donnée affichée sont normales, pas un signe de blocage (vérifier `ps`/CPU réel).
- **PC2 identifié comme goulot d'étranglement probable** : double pénalité — 2 cœurs
  physiques pour 8 workers (oversubscription ×4) **et** segment sur la zone à t la plus
  élevée du run (coût de scan croissant avec t).
- GPU confirmé non exploitable sur les deux machines (PC1 : GTX 960M sm_50 < CUDA 12.x
  NVRTC min sm_60 ; PC2 : CuPy absent) — calcul 100% CPU par construction, mur matériel.
- ETA du 02/08 (~13h, méthode √t) invalidée : calibrée à MARGE=3.0, le run réel tourne à
  MARGE=10.0 (STEP ~3,3× plus fin).

## Fichiers clés

```
src/calculs/optimisation/compute_zeros_v15.py    # _step_adaptatif() : historique MARGE/κ complet en docstring
scripts/zeta_distribute.py                       # V_PC1_DEFAULT/V_PC2_DEFAULT, calculer_pivot()
scripts/zeta_distribute_run.sh                    # wrapper nohup + turbo + dashboard (alias zeta-distribute)
scripts/zeta_run_progress.py                      # dashboard curses — worker visible seulement après 1re ligne de progression
Riemann_Lab.wiki/Handoff.md                       # état courant
Riemann_Lab.wiki/JOURNAL.md                       # entrées 04/08 (en haut) et 02/08 — détail complet
Riemann_Lab.wiki/STACK.md                         # §Cluster Zeta — ratio PC1/PC2 réel + goulot PC2
Riemann_Lab.wiki/Guide-Linux-Commandes.md         # §19 — UPower/HybridSleep/resume=
```

## Contraintes impératives

- `MARGE_SECURITE = 10.0` dans `_step_adaptatif()` — ne pas rebaisser sans nouvelle
  mesure non censurée (rescan `arb_hardy_z` STEP/10 sur zone réelle, pas de recalibration
  offline sur CSV déjà produits — censurés par construction).
- Toujours vérifier `upower -i $(upower -e | grep -i AC)` → `online: yes` avant un run
  long sur PC1 (portable) — `nohup`/`setsid` ne protègent pas d'un vrai poweroff/reboot.
- Avant un prochain run à grande échelle : reconsidérer le split PC1/PC2 ou le nombre de
  workers PC2 (goulot identifié, non corrigé sur ce run).
- Jamais `git add -A` sans `git status` + `grep mcp .gitignore`
- Turbo : `sudo scripts/zeta_turbo_on.sh` avant run · `zeta_turbo_off.sh` après

---
*PROMPT_CLAUDE_CODE_marge_distribution_20260805.md · src/ia/prompts/ · hprzeta · 2026-08-05*
