# -*- coding: utf-8 -*-
"""
mesure_rescan_phase.py — Mesure du gain du rescan décalé en phase (RESCAN_PHASE = 1/3) de compute_zeros_v17.py.

Question (point ouvert du Handoff) : le rescan décalé de STEP/3 rattrape-t-il plus de zéros que l'ancien
rescan (phase 0, grille contenant la grille principale) ? En production le rescan ne se déclenche que s'il
y a un déficit ; à T=10^6 il n'y en avait pas. On FABRIQUE donc un déficit : scan de base avec un STEP
volontairement trop grand (des paires de zéros tombent dans une même cellule et échappent au test de signe).

Protocole (tout est calculé par les fonctions de production, worker_v17, sans les modifier) :
  - référence : scan au STEP de production sur [A, B]  → ensemble de zéros « vrai » (étalon interne) ;
  - pour chaque STEP_gros : scan de base, puis rescan à STEP_gros/2 en phase 0 et en phase 1/3
    (mêmes arguments que rescan_segments_deficit : départ = A + phase·STEP_gros, pas = STEP_gros/2) ;
  - un zéro de référence est « retrouvé » si un zéro de l'ensemble testé est à moins de TOL_MATCH.

Sortie : tableau brut (aucune interprétation). Écrit un CSV de résultats dans le dossier donné.

Lancement :
    PYTHONPATH=src zeta_env/bin/python -I tests_v17/mesure_rescan_phase.py [A] [LONGUEUR] [dossier_sortie]
    (défauts : A=100000, LONGUEUR=1000, dossier=resultats_rescan_phase/)
Aucun fichier du dépôt n'est modifié ; la sortie va dans le dossier indiqué.
"""
import bisect                                    # recherche dichotomique dans les zéros triés
import csv                                       # écriture du CSV de résultats
import multiprocessing                           # un job par processus (fork : .so chargé après le fork)
import sys                                       # arguments de la ligne de commande
import time                                      # chronométrage
from pathlib import Path                         # chemins

# Le module de production est importé tel quel (aucune modification) ; le chemin est ajouté explicitement.
RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "src" / "calculs" / "optimisation"))
import compute_zeros_v17 as v17                  # worker_v17, SO_PATH, TOL_ARB, RESCAN_PHASE

TOL_MATCH = 1e-5                                 # un zéro est « retrouvé » à moins de 1e-5 du zéro de référence
STEPS_GROS = (0.20, 0.30, 0.45)                  # pas de scan volontairement trop grands (espacement moyen ≈ 0,65 à t=1e5)


def step_production(t_max: float) -> float:
    """STEP de production RÉEL : _step_adaptatif de compute_zeros_v17 (la formule min(..., 0,02) du CLAUDE.md
    est trop grossière ici : à T=1e5 elle donne 0,02, alors que la production utilise ≈ 7e-4 à 1e6)."""
    return v17._step_adaptatif(t_max)


def job(args):
    """Exécute worker_v17 sur un segment ; renvoie (étiquette, zéros triés, durée en s)."""
    etiquette, t_a, t_b, step = args             # étiquette du job, bornes, pas
    debut = time.time()                          # chronomètre local
    # Mêmes arguments que la production : (t_start, t_end, step, so_path, tol, worker_id, checkpoint_dir)
    zeros, _stats, _prof, _prov = v17.worker_v17((t_a, t_b, step, v17.SO_PATH, v17.TOL_ARB, 0, None))
    return etiquette, sorted(zeros), time.time() - debut


def retrouves(reference, testes):
    """Nombre de zéros de `reference` ayant un zéro de `testes` à moins de TOL_MATCH ; et la liste des manquants."""
    testes = sorted(testes)                      # tri pour la dichotomie
    manquants = []                               # zéros de référence non retrouvés
    for z in reference:
        k = bisect.bisect_left(testes, z)        # position d'insertion
        proche = min((abs(testes[j] - z) for j in (k - 1, k) if 0 <= j < len(testes)), default=1e9)
        if proche > TOL_MATCH:
            manquants.append(z)
    return len(reference) - len(manquants), manquants


def main():
    a = float(sys.argv[1]) if len(sys.argv) > 1 else 100000.0        # début du segment
    longueur = float(sys.argv[2]) if len(sys.argv) > 2 else 1000.0   # longueur du segment
    sortie = Path(sys.argv[3]) if len(sys.argv) > 3 else RACINE / "resultats_rescan_phase"
    sortie.mkdir(parents=True, exist_ok=True)
    b = a + longueur                                                 # fin du segment
    step_ref = step_production(b)                                    # pas de la référence

    # Liste des jobs : 1 référence + (base, rescan phase 0, rescan phase 1/3) par STEP_gros.
    jobs = [("ref", a, b, step_ref)]
    for s in STEPS_GROS:
        jobs.append((f"base_{s}", a, b, s))                                       # scan de base
        jobs.append((f"rescan_phase0_{s}", a + 0.0 * s, b, s / 2.0))              # ancien rescan (grille ⊃ base)
        jobs.append((f"rescan_phase13_{s}", a + v17.RESCAN_PHASE * s, b, s / 2.0))  # rescan actuel (décalé)
    print(f"Segment [{a:.0f} ; {b:.0f}] · STEP référence {step_ref:.5f} · {len(jobs)} jobs · RESCAN_PHASE={v17.RESCAN_PHASE:.4f}", flush=True)

    # Exécution en parallèle (4 processus, chacun charge le .so après le fork).
    debut = time.time()
    with multiprocessing.Pool(processes=4) as pool:
        res = {e: (z, d) for e, z, d in pool.imap_unordered(job, jobs)}
    print(f"Calculs terminés en {time.time() - debut:.1f} s", flush=True)

    ref = res["ref"][0]                                              # ensemble de référence
    lignes = []                                                      # lignes du tableau de sortie
    for s in STEPS_GROS:
        base = res[f"base_{s}"][0]
        r0 = res[f"rescan_phase0_{s}"][0]
        r13 = res[f"rescan_phase13_{s}"][0]
        n_base, man_base = retrouves(ref, base)                      # retrouvés par le scan de base seul
        n_p0, man_p0 = retrouves(ref, base + r0)                     # base + rescan phase 0
        n_p13, man_p13 = retrouves(ref, base + r13)                  # base + rescan phase 1/3
        # Zéros récupérés par chaque rescan parmi ceux que la base avait manqués.
        rec0 = set(man_base) - set(man_p0)
        rec13 = set(man_base) - set(man_p13)
        lignes.append({
            "step_gros": s, "n_ref": len(ref), "base_retrouves": n_base, "base_manquants": len(man_base),
            "phase0_manquants_restants": len(man_p0), "phase13_manquants_restants": len(man_p13),
            "recuperes_phase0": len(rec0), "recuperes_phase13": len(rec13),
            "recuperes_par_13_seul": len(rec13 - rec0), "recuperes_par_0_seul": len(rec0 - rec13),
        })

    # Affichage brut du tableau (aucune interprétation).
    cles = list(lignes[0].keys())
    print("\n" + " | ".join(cles))
    for l in lignes:
        print(" | ".join(str(l[c]) for c in cles))
    with open(sortie / f"mesure_rescan_phase_A{int(a)}_L{int(longueur)}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cles)                       # en-tête puis lignes
        w.writeheader()
        w.writerows(lignes)
    print(f"\nCSV : {sortie}")


if __name__ == "__main__":
    main()
