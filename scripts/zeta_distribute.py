#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zeta_distribute.py — Distribution du calcul v15 sur PC1 (local) + PC2 (SSH)
Porté de v13 le 02/08/2026 (cf. commit) — mécanique de segmentation/pivot inchangée,
seul le script cible (compute_zeros_v15.py) et les conventions de nommage changent.
══════════════════════════════════════════════════════════════════════════════
Usage :
    python scripts/zeta_distribute.py <T_MAX>
    python scripts/zeta_distribute.py <T_MAX> --v-pc2 1820  # si python-flint installé

Architecture :
    PC1 (zeta-lab, local)        : [14.0, T_PIVOT]   — turbo actif
    PC2 (zeta-calc-second, SSH)  : [T_PIVOT, T_MAX]   — sans turbo
    Supplément pivot (local)     : [T_PIVOT-OVERLAP_PIVOT, T_PIVOT+OVERLAP_PIVOT]

    Option B (24/06/2026) — overlap appliqué APRÈS le partitionnement, pas avant.
    Tentative précédente (23/06, Option A) : étendre T_MAX de PC1 et T_MIN de PC2
    de ±OVERLAP_PIVOT AVANT de les passer à compute_zeros_v15.py. Problème détecté :
    _partitionner_adaptatif() recalcule TOUTES les frontières internes des workers
    par recherche binaire sur N(T) en fonction de ce T_MAX/T_MIN — changer le pivot
    fait donc glisser en cascade les 7 autres frontières de chaque machine, ce qui a
    fait RÉGRESSER le run (5 → 8 manquants, cf. JOURNAL.md 23/06 soir) en déplaçant
    la phase de grille vers des zones moins favorables (paires de zéros proches,
    répulsion GUE).

    Option B : PC1 et PC2 reçoivent T_PIVOT EXACT (comme le run #4 de référence,
    frontières internes identiques, donc même phase de grille). Le trou de
    couverture structurel au pivot (largeur < 1 STEP, cf. fix du 23/06) est comblé
    par un 3e calcul, indépendant et minuscule, qui scanne uniquement la fenêtre
    [T_PIVOT-OVERLAP_PIVOT, T_PIVOT+OVERLAP_PIVOT] — sans toucher au partitionnement
    de PC1 ni de PC2. La déduplication (tolerance=0.01, fusionner_csv) absorbe le
    chevauchement entre ce supplément et les deux runs principaux.

Étapes :
    1. Calcule T_PIVOT pour équilibrer les deux runs (voir calculer_pivot)
    2. Active zeta_turbo_on.sh sur PC1 (sudo local)
    3. Lance v15 CLI en parallèle : subprocess local + subprocess SSH (bornes EXACTES)
    4. Attend la fin des deux processus
    5. Lance le supplément pivot (local, séquentiel, rapide — quelques zéros)
    6. Récupère le CSV produit par PC2 via scp
    7. Fusionne + déduplique les 3 CSVs (PC1 + PC2 + supplément pivot)
    8. Valide Turing global sur [14, T_MAX]
    9. Génère un rapport de distribution
    10. Désactive zeta_turbo_off.sh

Auteur : hprzeta — Projet Hypothèse de Riemann
Date   : 2026-06-17 · Option B 2026-06-24
"""

import sys
import math
import time
import subprocess
import argparse
import platform
from pathlib import Path
from datetime import datetime

import pandas as pd

# ── Racine du projet (scripts/ est dans projet_zeta/scripts/)
PROJET_DIR = Path(__file__).resolve().parent.parent
SRC_DIR    = PROJET_DIR / "src" / "calculs" / "optimisation"
LOG_DIR    = PROJET_DIR / "logs"
SCRIPTS    = PROJET_DIR / "scripts"

# ── Configuration cluster
# 02/08/2026 : alias zeta-calc-second (~/.ssh/config, clé zeta_cluster) remplace
# l'IP+clé id_acer codées en dur — alignement sur le renommage du 16/06/2026.
PC2_HOST    = "zeta-calc-second"
PC2_SSH_KEY = Path.home() / ".ssh" / "zeta_cluster"
PC2_PROJET  = "/home/hprzeta/projet_zeta"          # chemin absolu sur PC2

# ── Vitesses mesurées v15 T=1000 (02/08/2026, remplace les valeurs v13 obsolètes)
# Découverte du jour : python-flint 0.8.0 EST installé sur PC2 (absent lors de la
# mesure v13 du 17/06 qui donnait 52 z/s "sans python-flint"). Remesuré à neuf en
# conditions identiques (compute_zeros_v15.py --t-min 14 --t-max 1000, N_WORKERS=8
# sur les deux machines bien que PC2 n'ait que 2 cœurs physiques — comportement réel
# du mode distribué, pas corrigé) :
#   PC1 = 822.48 z/s · PC2 = 512.19 z/s → ratio ×1.6 (PAS ×12 comme supposé avant)
# Ancien split théorique 92.3%/7.7% (basé sur 624/52 z/s v13) INVALIDÉ par cette
# mesure — nouveau split réel : PC1 61.6% / PC2 38.4%.
V_PC1_DEFAULT = 822.48   # z/s — PC1, v15, T=1000, mesuré 02/08/2026
V_PC2_DEFAULT = 512.19   # z/s — PC2, v15, T=1000, python-flint présent, mesuré 02/08/2026

# ── Overlap à la frontière PC1/PC2 (fix 23/06/2026 — trou de couverture au pivot)
OVERLAP_PIVOT = 2.0     # largement > 1 STEP (~0.0044 à T=500000)


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — SEGMENTATION
# ═══════════════════════════════════════════════════════════════════════════════

def n_zeros_expected(T: float) -> int:
    """N(T) — Riemann-von Mangoldt. Le 'e' dans 2πe est OBLIGATOIRE."""
    if T < 14.0:
        return 0
    return int(T / (2 * math.pi) * math.log(T / (2 * math.pi * math.e)))


def _t_pour_n(n_cible: int, t_lo: float, t_hi: float) -> float:
    """Inversion N(T) → T par recherche binaire (60 itérations, précision ~1e-6)."""
    for _ in range(60):
        t_mid = (t_lo + t_hi) / 2.0
        if n_zeros_expected(t_mid) < n_cible:
            t_lo = t_mid
        else:
            t_hi = t_mid
    return (t_lo + t_hi) / 2.0


def calculer_pivot(T_MAX: float, v1: float, v2: float) -> float:
    """
    Calcule T_PIVOT tel que PC1 ([14, T_PIVOT]) et PC2 ([T_PIVOT, T_MAX])
    terminent approximativement au même moment.

    Paramètres :
        T_MAX — borne supérieure du calcul global
        v1    — vitesse PC1 en z/s  (ex. 624.0)
        v2    — vitesse PC2 en z/s  (ex. 52.0 ou 1820.0 avec python-flint)

    Retourne :
        T_PIVOT — point de coupure dans [14, T_MAX]

    ──────────────────────────────────────────────────────────────────
    CONTRIBUTION UTILISATEUR — implémenter les ~8 lignes suivantes.

    Indice mathématique :
      Temps PC1 = N(T_PIVOT) / v1
      Temps PC2 = (N(T_MAX) − N(T_PIVOT)) / v2
      Équilibre : Temps PC1 = Temps PC2
      → exprimer N_pivot en fonction de N(T_MAX), v1, v2
      → inverser N_pivot → T_PIVOT avec _t_pour_n()

    Trade-offs à considérer :
      • Segmenter par T absolu (T_PIVOT = T_MAX × v1/(v1+v2)) est faux
        car N(T) n'est pas linéaire en T.
      • Segmenter par N(T) proportionnel est correct mais suppose des
        vitesses constantes. Un overlap ±MARGE peut absorber la variance.
      • Faut-il ajouter une marge de sécurité (ex. +5 %) sur T_PIVOT
        pour compenser les aléas de PC2 (swap, partage CPU) ?
    ──────────────────────────────────────────────────────────────────
    """
    N_total = n_zeros_expected(T_MAX)
    # Part de PC2 à l'équilibre exact : v2 / (v1 + v2)
    N_pc2_eq = int(N_total * v2 / (v1 + v2))
    # Marge -5% sur la part de PC2 → PC2 reçoit moins de zéros → finit avant PC1
    # Raison : PC2 peut swapper ou partager CPU → ralentit imprévisiblement,
    #          ce qui bloquerait l'agrégation Turing si PC2 finit en dernier.
    N_pc2   = int(N_pc2_eq * 0.85)
    N_pivot = N_total - N_pc2
    return _t_pour_n(N_pivot, 14.0, T_MAX)


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — LANCEMENT DES RUNS
# ═══════════════════════════════════════════════════════════════════════════════

def _cmd_venv(commande: str) -> str:
    """Enveloppe une commande pour PC2 — Python3 système (pas de venv sur Debian 12).
    PYTHONPATH = src/calculs/optimisation/ : tous les modules (arb_wrapper, turing…)
    sont à plat dans ce dossier, pas dans un package Python structuré.
    """
    return (
        f"cd {PC2_PROJET} && "
        f"export PYTHONPATH={PC2_PROJET}/src/calculs/optimisation && "
        f"{commande}"
    )


def lancer_pc1(T_PIVOT: float, horodatage: str, log_dir: Path) -> subprocess.Popen:
    """Lance v15 en local sur [14.0, T_PIVOT], en arrière-plan, sans sudo zeta_turbo."""
    script  = SRC_DIR / "compute_zeros_v15.py"
    log_pc1 = log_dir / f"distribute_pc1_{horodatage}.log"
    venv    = PROJET_DIR / "zeta_env" / "bin" / "python"

    cmd = [
        str(venv), str(script),
        "--t-min",      "14.0",
        "--t-max",      str(T_PIVOT),
        "--horodatage", horodatage,
    ]
    print(f"  [PC1] {' '.join(cmd[:3])} … --t-min 14 --t-max {T_PIVOT:.1f}")
    log_pc1.parent.mkdir(parents=True, exist_ok=True)

    env = {
        **__import__("os").environ,
        "PYTHONPATH": str(PROJET_DIR / "src"),
    }
    proc = subprocess.Popen(
        cmd,
        stdout=open(log_pc1, "w"),
        stderr=subprocess.STDOUT,
        cwd=str(PROJET_DIR),
        env=env,
    )
    print(f"  [PC1] PID={proc.pid} — log → {log_pc1.name}")
    return proc, log_pc1


def lancer_pc2(T_PIVOT: float, T_MAX: float, horodatage: str, log_dir: Path) -> subprocess.Popen:
    """Lance v15 sur PC2 via SSH pour [T_PIVOT, T_MAX]."""
    log_pc2 = log_dir / f"distribute_pc2_{horodatage}.log"
    log_pc2.parent.mkdir(parents=True, exist_ok=True)

    # Commande Python sur PC2 (python3 sur Debian 12)
    cmd_py = (
        f"python3 src/calculs/optimisation/compute_zeros_v15.py "
        f"--t-min {T_PIVOT:.6f} --t-max {T_MAX:.6f} --horodatage {horodatage}"
    )
    cmd_ssh = [
        "ssh", "-i", str(PC2_SSH_KEY),
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        PC2_HOST,
        _cmd_venv(cmd_py),
    ]
    print(f"  [PC2] SSH → {PC2_HOST} | --t-min {T_PIVOT:.1f} --t-max {T_MAX:.1f}")

    proc = subprocess.Popen(
        cmd_ssh,
        stdout=open(log_pc2, "w"),
        stderr=subprocess.STDOUT,
    )
    print(f"  [PC2] PID={proc.pid} — log → {log_pc2.name}")
    return proc, log_pc2


def lancer_pivot_supplement(T_PIVOT: float, overlap: float,
                             horodatage: str, log_dir: Path) -> Path:
    """Scan local indépendant de [T_PIVOT-overlap, T_PIVOT+overlap] (Option B).

    Ne touche pas au partitionnement de PC1/PC2 (frontières internes inchangées,
    même phase de grille que le run #4 de référence) — comble le trou de
    couverture structurel au pivot par un calcul à part, minuscule (~quelques
    zéros, largeur 2×overlap), lancé séquentiellement après PC1+PC2.
    """
    script   = SRC_DIR / "compute_zeros_v15.py"
    t_min    = T_PIVOT - overlap
    t_max    = T_PIVOT + overlap
    log_pivot = log_dir / f"distribute_pivot_{horodatage}.log"
    venv     = PROJET_DIR / "zeta_env" / "bin" / "python"

    cmd = [
        str(venv), str(script),
        "--t-min",      str(t_min),
        "--t-max",      str(t_max),
        "--horodatage", horodatage,
    ]
    print(f"  [Pivot] [{t_min:.2f}, {t_max:.2f}] — supplément local …")

    env = {
        **__import__("os").environ,
        "PYTHONPATH": str(PROJET_DIR / "src"),
    }
    ret = subprocess.run(
        cmd,
        stdout=open(log_pivot, "w"),
        stderr=subprocess.STDOUT,
        cwd=str(PROJET_DIR),
        env=env,
    )
    if ret.returncode != 0:
        raise RuntimeError(f"Supplément pivot échoué (code {ret.returncode}) — voir {log_pivot}")
    print(f"  [Pivot] terminé — log → {log_pivot.name}")
    return _trouver_csv(PROJET_DIR / "calculs", t_min, t_max, horodatage)


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — RÉCUPÉRATION ET FUSION
# ═══════════════════════════════════════════════════════════════════════════════

def _trouver_csv(dossier: Path, T_MIN: float, T_MAX: float, horodatage: str) -> Path:
    """Retrouve le CSV v15 dans le dossier de calcul par convention de nommage."""
    nom = f"v15_T{T_MIN:.0f}_{T_MAX:.0f}_{horodatage}"
    cand = dossier / nom
    # chercher le CSV dans le sous-dossier
    csvs = list(cand.glob("zeros_v15_*.csv")) if cand.exists() else []
    if not csvs:
        # fallback : chercher partout sous calculs/
        csvs = sorted(dossier.glob(f"*{horodatage}*/zeros_v15_*.csv"))
    if not csvs:
        raise FileNotFoundError(f"Aucun CSV v15 trouvé pour {nom} dans {dossier}")
    return csvs[0]


def recuperer_csv_pc2(T_PIVOT: float, T_MAX: float,
                       horodatage: str, dossier_local: Path) -> Path:
    """Récupère le CSV de PC2 via scp vers dossier_local/."""
    # Dossier : v15_T{T_MIN:.0f}_{T_MAX:.0f}_{horodatage}/
    # CSV     : zeros_v15_T{T_MAX:.0f}_{horodatage}.csv   ← T_MAX seul (convention sauvegarder_csv v15)
    chemin_remote = (
        f"{PC2_PROJET}/calculs/"
        f"v15_T{T_PIVOT:.0f}_{T_MAX:.0f}_{horodatage}/"
        f"zeros_v15_T{T_MAX:.0f}_{horodatage}.csv"
    )
    csv_local = dossier_local / f"zeros_pc2_T{T_PIVOT:.0f}_{T_MAX:.0f}_{horodatage}.csv"
    cmd = [
        "scp", "-i", str(PC2_SSH_KEY),
        "-o", "StrictHostKeyChecking=no",
        f"{PC2_HOST}:{chemin_remote}",
        str(csv_local),
    ]
    print(f"  [scp] {chemin_remote.split('/')[-1]} → local")
    ret = subprocess.run(cmd, capture_output=True, text=True)
    if ret.returncode != 0:
        raise RuntimeError(f"scp échoué :\n{ret.stderr}")
    print(f"  [scp] ✅ {csv_local.name}")
    return csv_local


def fusionner_csv(csv_paths: list, dossier_out: Path, T_MAX: float) -> Path:
    """Fusionne + déduplique N CSVs (PC1 + PC2 [+ supplément pivot]), trie par partie_imaginaire."""
    dfs = [pd.read_csv(p) for p in csv_paths]

    # Concaténer et trier
    df = pd.concat(dfs, ignore_index=True)
    df = df.sort_values("partie_imaginaire").reset_index(drop=True)

    # Déduplication : supprimer les doublons dans une fenêtre tolerance=0.01
    zeros = df["partie_imaginaire"].tolist()
    filtres = []
    prev = -999.0
    TOL  = 0.01
    for z in zeros:
        if z - prev > TOL:
            filtres.append(z)
            prev = z

    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    df_final = pd.DataFrame({
        "n":                 range(1, len(filtres) + 1),
        "partie_imaginaire": filtres,
        "T_MAX":             T_MAX,
        "version":           "v15_distribue",
        "methode_affinage":  "arb_C_pur",
        "step":              0.010,
        "n_workers":         "PC1+PC2",
        "calcule_le":        horodatage,
    })
    csv_fusion = dossier_out / f"zeros_v15_distribue_T{T_MAX:.0f}_{horodatage}.csv"
    df_final.to_csv(csv_fusion, index=False)
    detail = " + ".join(str(len(d)) for d in dfs)
    print(f"\n  ✅ Fusion : {detail} (bruts) → {len(filtres)} zéros uniques")
    print(f"  CSV fusionné → {csv_fusion.name}")
    return csv_fusion


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — VALIDATION TURING
# ═══════════════════════════════════════════════════════════════════════════════

def valider_turing_local(zeros: list, T_MAX: float) -> dict:
    """Validation Turing-Backlund en important turing_validation du projet."""
    sys.path.insert(0, str(PROJET_DIR / "src" / "calculs" / "optimisation"))
    from turing_validation import valider_turing
    return valider_turing(zeros, dps=30)


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 — RAPPORT
# ═══════════════════════════════════════════════════════════════════════════════

def ecrire_rapport(rapport_path: Path, T_MAX: float, T_PIVOT: float,
                    v1: float, v2: float,
                    duree_pc1: float, duree_pc2: float, duree_total: float,
                    n_pc1: int, n_pc2: int, n_fusion: int,
                    turing: dict):
    """Rapport texte de la session de distribution."""
    lignes = []
    sep = "=" * 65

    def L(t=""): lignes.append(t)

    L(sep)
    L("  RAPPORT DISTRIBUTION v15 — PC1 + PC2")
    L("  Projet : Hypothèse de Riemann — hprzeta")
    L(sep); L()

    L(f"  T_MAX          = {T_MAX:.0f}")
    L(f"  T_PIVOT        = {T_PIVOT:.2f}  ({T_PIVOT/T_MAX*100:.1f}% de T_MAX)")
    L(f"  PC1/PC2 bornes = T_PIVOT exact (Option B — frontières internes inchangées vs run #4)")
    L(f"  Supplément pivot = [{T_PIVOT-OVERLAP_PIVOT:.2f}, {T_PIVOT+OVERLAP_PIVOT:.2f}]  (3e calcul local, après PC1+PC2)")
    L(f"  N(T_PIVOT)     ≈ {n_zeros_expected(T_PIVOT)}")
    L(f"  N(T_MAX)       ≈ {n_zeros_expected(T_MAX)}")
    L()
    L(f"  Vitesses       : PC1={v1:.0f} z/s · PC2={v2:.0f} z/s")
    L(f"  Durée PC1      : {duree_pc1/60:.2f} min  ({duree_pc1:.1f} s)")
    L(f"  Durée PC2      : {duree_pc2/60:.2f} min  ({duree_pc2:.1f} s)")
    L(f"  Durée totale   : {duree_total/60:.2f} min  (mur d'horloge)")
    speedup = n_fusion / duree_total if duree_total > 0 else 0
    L(f"  Vitesse globale: {speedup:.1f} z/s  (n_fusion / durée mur)")
    L()
    L(f"  Zéros PC1  : {n_pc1}")
    L(f"  Zéros PC2  : {n_pc2}")
    L(f"  Zéros fus. : {n_fusion}  (après déduplication tolerance=0.01)")
    L()
    complet = turing.get("complet", False)
    L(f"  Turing : {'✅ COMPLET' if complet else '❌ INCOMPLET'}")
    L(f"  Manquants : {turing.get('manquants_total', 'N/A')}")
    L(sep)
    L(f"  Fin — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    L(sep)

    rapport_path.write_text("\n".join(lignes), encoding="utf-8")
    print(f"  Rapport → {rapport_path.name}")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Distribution du calcul v15 sur PC1+PC2"
    )
    p.add_argument("t_max", type=float,
                   help="Borne supérieure du calcul (ex. 100000)")
    p.add_argument("--v-pc1", type=float, default=V_PC1_DEFAULT,
                   help=f"Vitesse PC1 en z/s (défaut: {V_PC1_DEFAULT})")
    p.add_argument("--v-pc2", type=float, default=V_PC2_DEFAULT,
                   help=f"Vitesse PC2 en z/s (défaut: {V_PC2_DEFAULT})")
    p.add_argument("--dry-run", action="store_true",
                   help="Afficher la segmentation sans lancer le calcul")
    return p.parse_args()


def main():
    args = parse_args()
    T_MAX = args.t_max
    V1    = args.v_pc1
    V2    = args.v_pc2

    if T_MAX < 20:
        print("  T_MAX doit être ≥ 20.")
        sys.exit(1)

    print()
    print("=" * 65)
    print("  DISTRIBUTION v15 — PC1 (local) + PC2 (SSH)")
    print("=" * 65)
    print(f"  T_MAX  = {T_MAX:.0f}")
    print(f"  V_PC1  = {V1:.0f} z/s · V_PC2 = {V2:.0f} z/s")
    print(f"  N(T_MAX) ≈ {n_zeros_expected(T_MAX)}")

    # Calcul du pivot
    try:
        T_PIVOT = calculer_pivot(T_MAX, V1, V2)
    except NotImplementedError as e:
        print(f"\n  ⛔  {e}")
        sys.exit(1)

    print(f"\n  Segmentation (Option B — overlap après partitionnement, pivot exact) :")
    print(f"    PC1 (local) : [14.0, {T_PIVOT:.2f}]  → N≈{n_zeros_expected(T_PIVOT)}")
    print(f"    PC2 (SSH)   : [{T_PIVOT:.2f}, {T_MAX:.0f}]"
          f"  → N≈{n_zeros_expected(T_MAX) - n_zeros_expected(T_PIVOT)}")
    print(f"    Pivot (local, après) : [{T_PIVOT-OVERLAP_PIVOT:.2f}, {T_PIVOT+OVERLAP_PIVOT:.2f}]"
          f"  → N≈{n_zeros_expected(T_PIVOT+OVERLAP_PIVOT) - n_zeros_expected(T_PIVOT-OVERLAP_PIVOT)}")

    t_prevu_pc1 = n_zeros_expected(T_PIVOT) / V1
    t_prevu_pc2 = (n_zeros_expected(T_MAX) - n_zeros_expected(T_PIVOT)) / V2
    print(f"  Durées prévues : PC1 {t_prevu_pc1/60:.1f} min · PC2 {t_prevu_pc2/60:.1f} min")

    if args.dry_run:
        print("\n  [dry-run] — aucun calcul lancé.")
        return

    print()
    if input("  Lancer la distribution ? [O/n] : ").strip().lower() in ("n", "non"):
        sys.exit(0)

    horodatage  = datetime.now().strftime("%Y%m%d_%H%M%S")
    dossier_out = PROJET_DIR / "calculs" / f"v15_distribue_T{T_MAX:.0f}_{horodatage}"
    dossier_out.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # ── Turbo on PC1
    print("\n  Activation turbo PC1...")
    subprocess.run(["sudo", str(SCRIPTS / "zeta_turbo_on.sh")], check=False)

    debut_global = time.time()

    # ── Lancement parallèle PC1 + PC2 (bornes EXACTES — Option B, pas d'overlap ici)
    print("\n  Lancement parallèle...")
    proc_pc1, log_pc1 = lancer_pc1(T_PIVOT, horodatage, LOG_DIR)
    proc_pc2, log_pc2 = lancer_pc2(T_PIVOT, T_MAX, horodatage, LOG_DIR)
    t_debut_pc1 = time.time()
    t_debut_pc2 = t_debut_pc1

    print(f"\n  En attente... (tail -f {log_pc1.name})")

    # ── Attente
    ret_pc1 = proc_pc1.wait()
    duree_pc1 = time.time() - t_debut_pc1
    print(f"  [PC1] terminé en {duree_pc1/60:.2f} min  (ret={ret_pc1})")

    ret_pc2 = proc_pc2.wait()
    duree_pc2 = time.time() - t_debut_pc2
    print(f"  [PC2] terminé en {duree_pc2/60:.2f} min  (ret={ret_pc2})")

    if ret_pc1 != 0:
        subprocess.run(["sudo", str(SCRIPTS / "zeta_turbo_off.sh")], check=False)
        print(f"  ❌ PC1 a échoué (code {ret_pc1}) — voir {log_pc1}")
        sys.exit(1)
    if ret_pc2 != 0:
        subprocess.run(["sudo", str(SCRIPTS / "zeta_turbo_off.sh")], check=False)
        print(f"  ❌ PC2 a échoué (code {ret_pc2}) — voir {log_pc2}")
        sys.exit(1)

    # ── Supplément pivot (Option B) — séquentiel, après PC1+PC2, avant turbo off
    print("\n  Lancement du supplément pivot...")
    csv_pivot = lancer_pivot_supplement(T_PIVOT, OVERLAP_PIVOT, horodatage, LOG_DIR)

    duree_total = time.time() - debut_global

    # ── Turbo off PC1
    subprocess.run(["sudo", str(SCRIPTS / "zeta_turbo_off.sh")], check=False)

    # ── Récupération CSV PC2 (bornes exactes du pivot, sans overlap)
    print("\n  Récupération CSV PC2...")
    csv_pc2_local = recuperer_csv_pc2(T_PIVOT, T_MAX, horodatage, dossier_out)

    # ── CSV PC1
    csv_pc1 = _trouver_csv(
        PROJET_DIR / "calculs", 14.0, T_PIVOT, horodatage
    )
    print(f"  CSV PC1 : {csv_pc1.name}")
    print(f"  CSV pivot : {csv_pivot.name}")

    # ── Fusion à 3 (PC1 + PC2 + supplément pivot)
    print("\n  Fusion des résultats...")
    csv_fusion = fusionner_csv([csv_pc1, csv_pc2_local, csv_pivot], dossier_out, T_MAX)

    # ── Validation Turing globale
    df_fusion = pd.read_csv(csv_fusion)
    zeros = df_fusion["partie_imaginaire"].tolist()
    n_pc1 = len(pd.read_csv(csv_pc1))
    n_pc2 = len(pd.read_csv(csv_pc2_local))

    print("\n  Validation Turing globale...")
    turing = valider_turing_local(zeros, T_MAX)
    complet = turing.get("complet", False)
    print(f"  Turing : {'✅ COMPLET' if complet else '❌ INCOMPLET'}")

    # ── Rapport
    rapport_path = dossier_out / f"rapport_distribution_{horodatage}.txt"
    ecrire_rapport(
        rapport_path, T_MAX, T_PIVOT, V1, V2,
        duree_pc1, duree_pc2, duree_total,
        n_pc1, n_pc2, len(zeros), turing,
    )

    print()
    print("=" * 65)
    print(f"  Distribution terminée — {len(zeros)} zéros dans {dossier_out.name}")
    print(f"  Durée mur : {duree_total/60:.2f} min"
          f"  ({len(zeros)/duree_total:.1f} z/s effectifs)")
    print("=" * 65)


if __name__ == "__main__":
    main()
