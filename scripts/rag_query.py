#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rag_query.py — Boucle RAG réutilisable : retrieval (ChromaDB) + génération (mathstral)
═══════════════════════════════════════════════════════════════════════════
Remplace les commandes Python ad hoc one-shot utilisées jusqu'ici pour tester
le RAG BrainVault (Objectif 2). Deux étapes :

  1. Retrieval — embedding de la question (sentence-transformers,
     all-MiniLM-L6-v2 — DOIT être identique au modèle d'ingestion, voir
     rag_ingest_corpus.py) puis recherche HNSW dans la collection ChromaDB
     "riemann_lab_corpus" (/mnt/vault_rag/chromadb).
  2. Génération — les chunks retrouvés sont injectés dans un prompt envoyé à
     mathstral via l'API HTTP locale d'ollama (http://127.0.0.1:11434).

Usage :
  python scripts/rag_query.py "Quel est le seuil SEUIL_1NEWTON ?"
  python scripts/rag_query.py "IP cluster ?" --k 5 --no-llm   # retrieval seul
  python scripts/rag_query.py "..." --modele mathstral --log

⚠️  Leçon du crash du 06/07/2026 (voir Handoff.md) : mathstral (4,1 Go) charge
    plusieurs couches en RAM système sur cette machine (8 Go). Fermer VS Code
    et Firefox avant un test, ou vérifier `free -h` — ce script avertit mais
    ne bloque pas.

Prérequis : zeta_env activé (chromadb, sentence-transformers, requests) ;
`ollama serve` actif (systemd ou manuel) avec le modèle mathstral pull.

Auteur : hprzeta — Projet Riemann_Lab — Objectif 2 (BrainVault)
Date   : 2026-07-19
"""

import argparse
import datetime
import os
import sys
import time
from pathlib import Path

import requests

# ── Configuration (mêmes valeurs que rag_ingest_corpus.py / rag_monitor.py) ─
VAULT_RAG = Path(os.environ.get("VAULT_RAG", "/mnt/vault_rag"))
CHROMA_DIR = VAULT_RAG / "chromadb"
LOGS_DIR = VAULT_RAG / "agent_logs"
COLLECTION_NOM = "riemann_lab_corpus"
MODELE_EMBEDDING = "all-MiniLM-L6-v2"   # même modèle que l'ingestion — ne pas changer
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
MODELE_LLM_DEFAUT = "mathstral"
RAM_LIBRE_SEUIL_MO = 1500   # avertissement en dessous (leçon crash 06/07)

PROMPT_TEMPLATE = """Tu es un assistant technique du projet Riemann_Lab. Réponds \
UNIQUEMENT à partir du contexte ci-dessous (extraits du wiki/code du projet). \
Si le contexte ne contient pas la réponse, dis-le clairement — n'invente rien.

--- CONTEXTE ---
{contexte}
--- FIN CONTEXTE ---

Question : {question}
Réponse :"""


def ssd_monte() -> bool:
    """True si VAULT_RAG est un vrai point de montage (garde reprise de rag_monitor.py)."""
    import subprocess
    return subprocess.run(
        ["mountpoint", "-q", str(VAULT_RAG)], capture_output=False
    ).returncode == 0


def ram_libre_mo() -> float:
    """RAM disponible en Mo (colonne 'disponible' de /proc/meminfo)."""
    with open("/proc/meminfo") as f:
        for ligne in f:
            if ligne.startswith("MemAvailable:"):
                return int(ligne.split()[1]) / 1024
    return -1.0


def retrieval(question: str, k: int) -> tuple:
    """Embedding de la question + recherche HNSW. Retourne (chunks, latences)."""
    from sentence_transformers import SentenceTransformer
    import chromadb

    t0 = time.time()
    modele = SentenceTransformer(MODELE_EMBEDDING)
    t_chargement = time.time() - t0

    t0 = time.time()
    vecteur = modele.encode([question]).tolist()
    t_embedding = time.time() - t0

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    coll = client.get_collection(COLLECTION_NOM)

    t0 = time.time()
    res = coll.query(query_embeddings=vecteur, n_results=k)
    t_recherche = time.time() - t0

    documents = res.get("documents", [[]])[0]
    metadonnees = res.get("metadatas", [[]])[0]
    distances = res.get("distances", [[]])[0]
    chunks = list(zip(documents, metadonnees, distances))

    latences = {"chargement": t_chargement, "embedding": t_embedding, "recherche": t_recherche}
    return chunks, latences


def generation(question: str, chunks: list, modele_llm: str) -> tuple:
    """Envoie le prompt (question + contexte) à mathstral via l'API ollama."""
    contexte = "\n\n".join(
        "[{}] {}".format(meta.get("file", meta.get("source", "?")), doc)
        for doc, meta, _ in chunks
    )
    prompt = PROMPT_TEMPLATE.format(contexte=contexte, question=question)

    t0 = time.time()
    reponse = requests.post(
        "{}/api/generate".format(OLLAMA_HOST),
        json={"model": modele_llm, "prompt": prompt, "stream": False},
        timeout=400,   # mathstral à froid : ~1m30-1m47 rien que pour charger (cf. Guide-Ollama-Pratique.md)
    )
    reponse.raise_for_status()
    t_generation = time.time() - t0

    return reponse.json().get("response", "").strip(), t_generation


def ecrire_log(question: str, chunks: list, texte_reponse: str, latences: dict) -> Path:
    """Log horodaté dans agent_logs, même convention que rag_ingest_corpus.py."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / "rag_query_{:%Y%m%d_%H%M%S}.log".format(datetime.datetime.now())
    with open(log_path, "w") as fh:
        fh.write("RAG query — {}\n".format(datetime.datetime.now().isoformat()))
        fh.write("Question : {}\n\n".format(question))
        fh.write("--- Chunks retrouvés ---\n")
        for doc, meta, dist in chunks:
            fh.write("[{}] (distance {:.3f})\n{}\n\n".format(
                meta.get("file", meta.get("source", "?")), dist, doc))
        fh.write("--- Latences ---\n")
        for etape, t in latences.items():
            fh.write("{:<12}: {:.3f} s\n".format(etape, t))
        if texte_reponse:
            fh.write("\n--- Réponse mathstral ---\n{}\n".format(texte_reponse))
    return log_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Boucle RAG BrainVault — retrieval + génération")
    parser.add_argument("question", help="question en langage naturel")
    parser.add_argument("--k", type=int, default=3, help="nombre de chunks retrouvés (défaut 3)")
    parser.add_argument("--modele", default=MODELE_LLM_DEFAUT, help="modèle ollama (défaut mathstral)")
    parser.add_argument("--no-llm", action="store_true", help="retrieval seul, sans appel LLM")
    parser.add_argument("--log", action="store_true", help="écrire un log dans agent_logs")
    args = parser.parse_args()

    if not ssd_monte():
        print("❌ vault_rag NON MONTÉ ({}) — sudo mount /mnt/vault_rag puis relancer.".format(VAULT_RAG))
        sys.exit(1)

    print("── Retrieval ──")
    try:
        chunks, latences = retrieval(args.question, args.k)
    except Exception as e:
        print("❌ retrieval échoué : {}".format(e))
        sys.exit(1)

    if not chunks:
        print("❌ aucun chunk retrouvé (collection vide ?)")
        sys.exit(1)

    print("  chargement modèle embedding : {:.2f} s".format(latences["chargement"]))
    print("  embedding question          : {:.3f} s".format(latences["embedding"]))
    print("  recherche HNSW               : {:.3f} s".format(latences["recherche"]))
    print("  top-{} chunks :".format(args.k))
    for doc, meta, dist in chunks:
        nom = meta.get("file", meta.get("source", "?"))
        apercu = doc[:80].replace("\n", " ")
        print("    · {} (distance {:.3f}) — {}...".format(nom, dist, apercu))

    texte_reponse = ""
    if args.no_llm:
        print("\n(--no-llm : génération sautée)")
    else:
        ram = ram_libre_mo()
        if 0 <= ram < RAM_LIBRE_SEUIL_MO:
            print("\n⚠️  RAM disponible {:.0f} Mo (< {} Mo) — risque de kill systemd-oomd. "
                  "Ferme VS Code/Firefox avant de continuer (voir Handoff.md, incident 06/07)."
                  .format(ram, RAM_LIBRE_SEUIL_MO))

        print("\n── Génération ({}) ──".format(args.modele))
        try:
            texte_reponse, t_generation = generation(args.question, chunks, args.modele)
            latences["generation"] = t_generation
            print("  génération : {:.1f} s".format(t_generation))
            print("\n{}".format(texte_reponse))
        except requests.exceptions.ConnectionError:
            print("❌ ollama injoignable sur {} — `ollama serve` est-il actif ? "
                  "(systemctl status ollama)".format(OLLAMA_HOST))
            sys.exit(1)
        except Exception as e:
            print("❌ génération échouée : {}".format(e))
            sys.exit(1)

    if args.log:
        log_path = ecrire_log(args.question, chunks, texte_reponse, latences)
        print("\nLog écrit : {}".format(log_path))


if __name__ == "__main__":
    main()
