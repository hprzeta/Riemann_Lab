#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rag_monitor.py — Surveillance du RAG BrainVault (/mnt/vault_rag)
═══════════════════════════════════════════════════════════════════════════
Photo instantanée (ou continue avec --watch) de l'état du vault RAG :

  1. Montage du SSD          — garde mountpoint (leçon du 05/07/2026 :
                               SSD non remonté au reboot → écriture
                               silencieuse sur le disque système)
  2. Espaces disque          — SSD vault_rag ET racine (détecter une
                               écriture au mauvais endroit)
  3. Tailles                 — chromadb/, llamaindex_cache/, agent_logs/
  4. Collections ChromaDB    — noms + nombre de chunks (jauge d'ingestion)
  5. Dernier log d'ingestion — 5 dernières lignes (erreurs visibles)
  6. --test-query            — latence d'une vraie requête vectorielle
                               (embedding + recherche HNSW, sans LLM)

Usage :
  python scripts/rag_monitor.py                # photo instantanée
  python scripts/rag_monitor.py --watch 10     # rafraîchi toutes les 10 s
  python scripts/rag_monitor.py --test-query   # + latence requête

Prérequis : zeta_env activé (chromadb installé). --test-query nécessite
en plus sentence-transformers (déjà installé pour l'ingestion).

Auteur : hprzeta — Projet Riemann_Lab — Objectif 2 (BrainVault)
Date   : 2026-07-05
"""

import argparse
import datetime
import os
import subprocess
import sys
import time
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────
VAULT_RAG = Path(os.environ.get("VAULT_RAG", "/mnt/vault_rag"))
CHROMA_DIR = VAULT_RAG / "chromadb"
CACHE_DIR = VAULT_RAG / "llamaindex_cache"
LOGS_DIR = VAULT_RAG / "agent_logs"
MODELE_EMBEDDING = "all-MiniLM-L6-v2"   # même modèle que l'ingestion
REQUETE_TEST = "Quel est le seuil SEUIL_1NEWTON de la phase 2 Illinois ?"


# ── Garde OBLIGATOIRE : le SSD est-il monté ? ──────────────────────────────
def ssd_monte() -> bool:
    """True si VAULT_RAG est un vrai point de montage (pas un dossier vide)."""
    return subprocess.run(
        ["mountpoint", "-q", str(VAULT_RAG)], capture_output=False
    ).returncode == 0


def espace_disque(chemin: str) -> str:
    """Retourne 'libre / total' pour le système de fichiers portant `chemin`."""
    st = os.statvfs(chemin)
    libre = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    return "{} / {}".format(humain(libre), humain(total))


def humain(octets: float) -> str:
    """Taille lisible (Ko/Mo/Go)."""
    for unite in ("o", "K", "M", "G", "T"):
        if octets < 1024.0:
            return "{:.1f} {}".format(octets, unite)
        octets /= 1024.0
    return "{:.1f} P".format(octets)


def taille_dossier(dossier: Path) -> int:
    """Taille totale d'un dossier en octets (0 s'il n'existe pas)."""
    if not dossier.exists():
        return 0
    total = 0
    for f in dossier.rglob("*"):
        try:
            if f.is_file():
                total += f.stat().st_size
        except PermissionError:
            pass  # lost+found etc.
    return total


def collections_chromadb() -> list:
    """Liste (nom, nb_chunks) des collections ChromaDB du vault."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        return [(c.name, c.count()) for c in client.list_collections()]
    except Exception as e:  # chromadb absent, base verrouillée, etc.
        return [("<erreur: {}>".format(e), -1)]


def dernier_log() -> tuple:
    """(nom du dernier log d'ingestion, 5 dernières lignes)."""
    if not LOGS_DIR.exists():
        return ("(aucun dossier agent_logs)", [])
    logs = sorted(LOGS_DIR.glob("*.log"), key=lambda p: p.stat().st_mtime)
    if not logs:
        return ("(aucun log)", [])
    dernier = logs[-1]
    lignes = dernier.read_text(errors="replace").splitlines()[-5:]
    return (dernier.name, lignes)


def test_latence_requete() -> None:
    """Embedding de la question + recherche HNSW — mesure le retrieval seul."""
    print("── Test requête (retrieval seul, sans LLM) ──")
    try:
        from sentence_transformers import SentenceTransformer
        import chromadb

        t0 = time.time()
        modele = SentenceTransformer(MODELE_EMBEDDING)
        t_chargement = time.time() - t0

        t0 = time.time()
        vecteur = modele.encode([REQUETE_TEST]).tolist()
        t_embedding = time.time() - t0

        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        cibles = [c for c in client.list_collections() if c.count() > 0]
        if not cibles:
            print("  ❌ aucune collection non vide à interroger")
            return
        coll = max(cibles, key=lambda c: c.count())

        t0 = time.time()
        res = coll.query(query_embeddings=vecteur, n_results=3)
        t_recherche = time.time() - t0

        print("  collection interrogée : {} ({} chunks)".format(coll.name, coll.count()))
        print("  chargement modèle     : {:.2f} s (une seule fois par session)".format(t_chargement))
        print("  embedding question    : {:.3f} s".format(t_embedding))
        print("  recherche HNSW        : {:.3f} s  {}".format(
            t_recherche, "✅" if t_recherche < 1.0 else "⚠️ > 1 s, index à vérifier"))
        sources = res.get("metadatas", [[]])[0]
        if sources:
            print("  top-3 sources : " + " · ".join(
                str(m.get("file_name", m.get("source", "?"))) for m in sources))
    except ImportError as e:
        print("  ❌ dépendance manquante : {} (activer zeta_env)".format(e))
    except Exception as e:
        print("  ❌ erreur : {}".format(e))


def photo(test_query: bool = False) -> None:
    """Affiche l'état complet du vault."""
    horodatage = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("═══ RAG MONITOR — {} — {} ═══".format(VAULT_RAG, horodatage))

    # 1. Garde montage — TOUT s'arrête si le SSD n'est pas là
    if not ssd_monte():
        print("❌ vault_rag NON MONTÉ — le dossier {} est un dossier VIDE du".format(VAULT_RAG))
        print("   disque système. NE RIEN ÉCRIRE. Remonter d'abord :")
        print("   sudo mount /mnt/vault_rag   (puis relancer ce script)")
        return
    print("✅ SSD monté  ·  libre vault : {}".format(espace_disque(str(VAULT_RAG))))
    print("             ·  libre racine : {} (doit rester stable !)".format(espace_disque("/")))

    # 2. Tailles
    print("── Tailles ──────────────────────────────")
    for nom, dossier in (("chromadb", CHROMA_DIR),
                         ("llamaindex_cache", CACHE_DIR),
                         ("agent_logs", LOGS_DIR)):
        print("  {:<18}: {}".format(nom, humain(taille_dossier(dossier))))

    # 3. Collections
    print("── Collections ChromaDB ─────────────────")
    for nom, n in collections_chromadb():
        if n >= 0:
            print("  {:<24}: {} chunks".format(nom, n))
        else:
            print("  {}".format(nom))

    # 4. Dernier log
    nom_log, lignes = dernier_log()
    print("── Dernier log : {} ──".format(nom_log))
    for l in lignes:
        prefixe = "⚠️ " if ("ERROR" in l or "Traceback" in l) else "   "
        print(prefixe + l)

    # 5. Latence (optionnel)
    if test_query:
        test_latence_requete()


def main() -> None:
    parser = argparse.ArgumentParser(description="Surveillance du RAG BrainVault")
    parser.add_argument("--watch", type=int, metavar="SECONDES",
                        help="rafraîchir en continu toutes les N secondes")
    parser.add_argument("--test-query", action="store_true",
                        help="mesurer la latence d'une requête vectorielle")
    args = parser.parse_args()

    if args.watch:
        try:
            while True:
                os.system("clear")
                photo(test_query=False)  # pas de test lourd en boucle
                print("\n(Ctrl+C pour quitter — rafraîchi toutes les {} s)".format(args.watch))
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\nArrêt du monitoring.")
            sys.exit(0)
    else:
        photo(test_query=args.test_query)


if __name__ == "__main__":
    main()
