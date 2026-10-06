# Suivi run T=5M v15 distribué (PC1+PC2)

> Fichier de suivi simple, mis à jour à chaque événement notable pendant l'absence
> de hprzeta (nouveau palier PC1/PC2, erreur, fin du run). Consultable à distance
> (SSH) ou au retour.

**Lancé :** 04/08/2026 22h48 · **PID racine :** `32270`
**Logs :** `logs/distribute_T5000000_nohup_20260804_224841.log` ·
`logs/distribute_pc1_20260804_224851.log` · `logs/distribute_pc2_20260804_224851.log`
**Segmentation :** PC1 `[14, 3469743.76]` (N≈6 749 158) · PC2 `[3469743.76, 5000000]` (N≈3 267 315)
**Résultat final attendu :** `calculs/v15_distribue_T5000000_20260804_224851/rapport_distribution_*.txt`

---

## Journal

**2026-08-05 06:37** — État au départ de hprzeta pour la journée. Aucune erreur détectée.
Run en cours depuis ~7h50 (lancé 04/08 22h48).
- **PC1** : Worker 0 terminé (843 000 zéros). Worker 1 en cours — zéro #623 000 à
  t=851904 (débit ≈111 z/s en phase d'affinage). Workers 2-7 toujours en phase de
  scan (pas de ligne de progression attendue avant un moment — comportement normal,
  cf. `JOURNAL.md` wiki 04-05/08).
- **PC2** : aucune ligne de progression depuis le lancement (7h50) — toujours en
  phase de scan. 8 process SSH actifs, ~24% CPU chacun (confirmé sain, pas bloqué).
  Goulot d'étranglement identifié (2 cœurs physiques + zone à t la plus élevée du run).
- **ETA** : non fiable à ce stade (cf. Handoff/JOURNAL) — pas d'estimation chiffrée
  tant que PC2 n'a pas produit de données réelles.
- Surveillance automatique active côté session Claude Code (poll ~5 min).

**2026-08-05 06:47** — Nouveau palier PC1 : **Worker 2 a terminé sa phase de scan et
affine désormais** (zéro #41 000 à t=990105, après ~28704s). Worker 1 poursuit
(#700 000 à t=892763). Worker 0 toujours terminé (843 000 zéros). Aucune erreur.
PC2 : toujours aucune progression (goulot confirmé).

**2026-08-05 21:25** — **🟢 PC1 TERMINÉ INTÉGRALEMENT.** Les 8 workers ont fini :

| Worker | Zéros | Durée |
|---|---|---|
| 0 | 843 630 | 22 620 s (6h17) |
| 1 | 843 614 | 29 907 s (8h19) |
| 2 | 843 627 | 34 384 s (9h33) |
| 3 | 843 639 | 37 397 s (10h23) |
| 4 | 843 644 | 39 611 s (11h00) |
| 5 | 843 646 | 40 937 s (11h22) |
| 6 | 843 646 | 41 843 s (11h37) |
| 7 | 843 646 | 42 521 s (11h49) |

Total PC1 ≈ **6 749 092 zéros** (attendu N≈6 749 158). Aucune erreur, 0 fallback
anormal. Le process racine (PID 32270) attend maintenant la fin de PC2 avant de
lancer le supplément pivot + fusion + Turing (étapes 5-9 de `zeta_distribute.py`).

**🟡 PC2 : toujours AUCUNE progression après 22h36 de calcul continu.** Vérifié en
profondeur — **pas de blocage, juste très lent** :
- 8 workers en état `R`, ~23,7% CPU chacun (cohérent avec 2 cœurs physiques / 8
  workers), `ELAPSED` = 22:36:25 en croissance continue (pas figé).
- RAM : 1,7/7,6 Gi utilisés, **0 swap** — pas de pression mémoire.
- `load average` 8,89 — cohérent avec 8 process actifs, pas de contention anormale.
- Cause probable (déjà identifiée) : PC2 couvre `[3,47M–5M]`, la zone à t la plus
  élevée de tout le run → coût de scan par point maximal, cumulé au désavantage
  matériel (2 cœurs vs 4 sur PC1). PC1 (turbo, 4 cœurs) a mis 11h49 pour son
  worker le plus lent (Worker 7, zone la plus proche de PC2 en t) ; PC2 démarre
  plus haut encore en t, sans turbo, sur 2 cœurs.
- **Aucune estimation fiable de fin.** À surveiller — si aucune ligne de
  progression n'apparaît dans les prochaines heures, une investigation plus
  poussée (strace, vérif silencieuse d'un blocage réseau/disque) sera nécessaire.

**2026-08-06 (nuit)** — **🔴 RUN ARRÊTÉ MANUELLEMENT sur décision de hprzeta**, après
23h20 sans la moindre ligne de progression côté PC2 (aucune ETA fiable possible).

- PC2 tué via SSH (`pkill -f compute_zeros_v15`) — confirmé arrêté, aucun process
  `python3` restant. **~23h20 de calcul PC2 perdues, non récupérables** (aucun
  résultat partiel n'avait été écrit sur disque — les zéros ne sont sauvegardés
  qu'à la toute fin de chaque worker, aucun n'avait fini).
- Orchestrateur PC1 (`zeta_distribute.py`, PID 32270/32273) déjà auto-terminé au
  moment du kill — la commande SSH bloquante vers PC2 (PID 32465) a remonté un
  code retour 255 (connexion coupée), ce que le script a correctement détecté et
  journalisé : `[PC2] terminé en 1415.33 min (ret=255)` → `❌ PC2 a échoué (code 255)`.
- `zeta_turbo_off.sh` déjà exécuté automatiquement par le script à sa sortie —
  système confirmé restauré (`scaling_governor=powersave` sur les 4 cœurs,
  `swappiness=10`, bluetooth/avahi-daemon actifs). Rien à restaurer manuellement.
- **PC1 : résultats intacts et sauvegardés** —
  `calculs/v15_T14_3469744_20260804_224851/zeros_v15_T3469744_20260804_224851.csv`
  (670 Mo, ~6 749 092 zéros sur `[14, 3469743.76]`), + PNG + log d'exécution.
  Ces résultats PC1 seuls restent exploitables si besoin plus tard (ex. comparaison
  partielle avec le run v13, sans refaire tourner PC1).
- Fichier PID `/tmp/zeta_distribute.pid` nettoyé. Surveillance (Monitor Claude Code)
  arrêtée.

**Bilan factuel du goulot PC2** (pour référence future avant un nouveau run) :
0 zéro produit en 23h20 sur un segment estimé à N≈3 267 315 zéros — confirmé non
bloqué (CPU actif en continu, RAM/swap sains, module C `scan_arb.so` bien chargé,
pas de fallback Python) mais structurellement trop lent pour ce run : 2 cœurs
physiques / 8 workers (×4 oversubscription) + pas de turbo + zone à t la plus
élevée du run (coût de scan croissant avec t). Non résolu — à traiter avant tout
nouveau run distribué à grande échelle (cf. `STACK.md` § Cluster Zeta).

---
*suivi_run_T5M.md · logs/ · hprzeta · run T=5M v15 (PID 32270) — ARRÊTÉ MANUELLEMENT 06/08/2026*
