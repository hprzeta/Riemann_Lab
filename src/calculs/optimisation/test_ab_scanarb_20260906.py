"""
Test A/B ciblé — piste "bruit de phase Z_double" sur les 96 zéros manquants v13.
Compare scan_arb.so v13 (7914fa3, division /sqrt(n)) vs v16 (d4b3611, cache
isqrt_n_cache) sur la fenêtre historique des segments 0-1 du run T=5M v13
(27/06/2026), aux conditions d'apparition exactes : STEP=0.001571, MARGE=2.0
(implicite dans le STEP), 8 workers.

Usage : python3 test_ab_scanarb_20260906.py <label> <dossier_sortie>
  <label>          : "runA_v13" ou "runB_v16" (juste pour les logs/CSV)
  <dossier_sortie> : dossier où écrire les checkpoints + le CSV final

Le binaire scan_arb.so effectivement utilisé est celui présent sur le disque
au moment de l'exécution (swap fait par le script appelant AVANT de lancer
celui-ci) — ce script ne touche à aucun fichier de production.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import compute_zeros_v16 as v16

STEP = 0.001571          # grille EXACTE du run v13 original (27/06/2026)
T_MIN, T_MAX = 14.0, 1391397.0   # bornes historiques réelles segments 0+1
N_WORKERS = 8

def main():
    label = sys.argv[1]
    dossier = Path(sys.argv[2])
    dossier.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"  {label} — [{T_MIN}, {T_MAX}] STEP={STEP} N_WORKERS={N_WORKERS}")
    print(f"  scan_arb.so utilisé : {Path(__file__).parent / 'c_modules' / 'scan_arb.so'}")
    print(f"{'='*70}\n")

    t0 = time.time()
    zeros, stats, profil, segments = v16.calculer_zeros_v16(
        T_MIN, T_MAX, N_WORKERS, STEP, v16.TOL_ARB, dossier
    )
    duree = time.time() - t0

    print(f"\n{'='*70}")
    print(f"  RÉSULTATS {label}")
    print(f"{'='*70}")
    print(f"  Zéros trouvés : {len(zeros)}")
    print(f"  Attendus (Weyl) : {v16._n_zeros_expected(T_MAX) - v16._n_zeros_expected(T_MIN):.0f}")
    print(f"  Durée : {duree/60:.1f} min ({duree:.1f}s)")
    print(f"  Vitesse : {len(zeros)/duree:.1f} z/s")
    print(f"  Stats méthodes : {stats}")

    # Persistance CSV IMMÉDIATE — pas de rescan (skip-rescan par construction,
    # calculer_zeros_v16 ne déclenche jamais de rescan lui-même)
    chemin_csv = v16.sauvegarder_csv(
        zeros, stats, T_MAX, STEP, N_WORKERS,
        time.strftime("%Y%m%d_%H%M%S"), dossier, suffixe=f"_{label}",
    )
    print(f"  CSV : {chemin_csv}")

if __name__ == "__main__":
    main()
