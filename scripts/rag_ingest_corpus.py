#!/usr/bin/env python3
"""Ingestion RAG BrainVault — corpus Riemann_Lab (Objectif 2).

Sources ingérées (règle d'ingestion, cf. etat_rag_brainvault_20260704.md §3.5) :
  - Wiki (pages courantes, hors Handoff.md) : ~/projet_zeta/Riemann_Lab.wiki/*.md
  - Code source actuel (Riemann_Lab_C) : src/calculs/optimisation/**/*.{py,c,h}
  - Prompts archivés (bandeau ARCHIVE uniquement) : src/ia/prompts/*.md

Sortie : collection ChromaDB "riemann_lab_corpus" sur $VAULT_RAG/chromadb,
cache d'index LlamaIndex sur $VAULT_RAG/llamaindex_cache, log sur $VAULT_RAG/agent_logs.

Usage :
  python scripts/rag_ingest_corpus.py            # 1re ingestion (collection vide)
  python scripts/rag_ingest_corpus.py --reset    # supprime la collection puis ré-ingère

Version 2 — 03/10/2026 :
  - garde « SSD monté » (mountpoint), identique à rag_monitor.py / rag_query.py :
    sans elle, un SSD non monté laissait écrire en silence sur le disque système ;
  - refus d'ingérer dans une collection NON vide sans --reset : relancer le script
    AJOUTAIT les chunks une 2e fois (838 → ~1676) ;
  - option --reset (à utiliser après une copie de sécurité : zeta-rag, option 6).

Version 2.1 — 04/10/2026 :
  - embedding forcé sur CPU (device="cpu") : la GTX 960M (sm_50) n'est plus gérée par torch 2.11.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

import chromadb
from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

VAULT_RAG = Path(os.environ.get("VAULT_RAG", "/mnt/vault_rag"))
PROJET = Path.home() / "projet_zeta"
WIKI_DIR = PROJET / "Riemann_Lab.wiki"
CODE_DIR = PROJET / "src" / "calculs" / "optimisation"
PROMPTS_DIR = PROJET / "src" / "ia" / "prompts"

COLLECTION_NOM = "riemann_lab_corpus"
EXCLUDE_WIKI = {"Handoff.md"}
CODE_EXTS = {".py", ".c", ".h"}


def ssd_monte() -> bool:
    """True si VAULT_RAG est un vrai point de montage (pas un dossier vide du disque système)."""
    return subprocess.run(["mountpoint", "-q", str(VAULT_RAG)]).returncode == 0


def load_wiki_docs():
    docs = []
    for f in sorted(WIKI_DIR.glob("*.md")):
        if f.name in EXCLUDE_WIKI:
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        docs.append(Document(
            text=text,
            metadata={"source": "wiki", "file": f.name, "branch": "master (wiki)"},
        ))
    return docs


def load_code_docs():
    docs = []
    for f in sorted(CODE_DIR.rglob("*")):
        if f.is_dir() or f.suffix not in CODE_EXTS:
            continue
        if f.name.endswith(".bak"):
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        docs.append(Document(
            text=text,
            metadata={"source": "code", "file": str(f.relative_to(PROJET)), "branch": "Riemann_Lab_C"},
        ))
    return docs


def load_prompt_archives():
    docs = []
    if not PROMPTS_DIR.exists():
        return docs
    for f in sorted(PROMPTS_DIR.glob("*.md")):
        text = f.read_text(encoding="utf-8", errors="ignore")
        if "ARCHIVE" not in text:
            continue
        docs.append(Document(
            text=text,
            metadata={"source": "prompt_archive", "file": f.name, "branch": "Riemann_Lab_C"},
        ))
    return docs


def main():
    parser = argparse.ArgumentParser(description="Ingestion du corpus Riemann_Lab dans ChromaDB")
    parser.add_argument("--reset", action="store_true",
                        help="supprime la collection existante avant d'ingérer (évite les doublons)")
    args = parser.parse_args()

    # Garde OBLIGATOIRE : ne rien écrire si le SSD n'est pas monté (leçon du 05/07/2026).
    if not ssd_monte():
        print(f"❌ vault_rag NON MONTÉ ({VAULT_RAG}) — rien n'a été écrit. "
              "Monter d'abord : zeta-rag (option 2) ou sudo mount /mnt/vault_rag.")
        sys.exit(1)

    chroma_client = chromadb.PersistentClient(path=str(VAULT_RAG / "chromadb"))
    if args.reset:
        try:
            chroma_client.delete_collection(COLLECTION_NOM)
            print(f"Collection '{COLLECTION_NOM}' supprimée (--reset).")
        except Exception:
            print(f"Collection '{COLLECTION_NOM}' absente : rien à supprimer.")
    collection = chroma_client.get_or_create_collection(COLLECTION_NOM)
    if collection.count() > 0:
        print(f"❌ La collection '{COLLECTION_NOM}' contient déjà {collection.count()} chunks : "
              "relancer sans --reset ajouterait des doublons. Relancer avec --reset "
              "(après une copie de sécurité).")
        sys.exit(1)

    wiki_docs = load_wiki_docs()
    code_docs = load_code_docs()
    archive_docs = load_prompt_archives()
    all_docs = wiki_docs + code_docs + archive_docs

    print(f"Wiki (pages courantes)      : {len(wiki_docs)} docs")
    print(f"Code source (Riemann_Lab_C) : {len(code_docs)} docs")
    print(f"Prompts archivés (ARCHIVE)  : {len(archive_docs)} docs")
    print(f"Total                       : {len(all_docs)} docs")

    # device="cpu" forcé : torch 2.11.0+cu130 a abandonné le support Maxwell (CC 5.0, GTX 960M)
    # — plante en CUDA à la vectorisation (incident 25/07/2026, répété le 04/10/2026 : l'échec
    # arrivait APRÈS le --reset et laissait la collection vide). Sans effet sur ollama.
    Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", device="cpu")
    Settings.node_parser = SentenceSplitter(chunk_size=800, chunk_overlap=100)

    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
        all_docs, storage_context=storage_context, show_progress=True
    )
    index.storage_context.persist(persist_dir=str(VAULT_RAG / "llamaindex_cache"))

    # index.docstore.docs ne reflète pas fidèlement le contenu du vector store
    # avec un ChromaVectorStore externe — on interroge la collection directement.
    n_chunks = collection.count()

    log_dir = VAULT_RAG / "agent_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"ingestion_{datetime.now():%Y%m%d_%H%M%S}.log"
    with open(log_path, "w") as fh:
        fh.write(f"Ingestion RAG BrainVault — {datetime.now().isoformat()}\n")
        fh.write(f"Wiki docs                : {len(wiki_docs)}\n")
        fh.write(f"Code docs                : {len(code_docs)}\n")
        fh.write(f"Prompt archives (ARCHIVE): {len(archive_docs)}\n")
        fh.write(f"Total docs               : {len(all_docs)}\n")
        fh.write(f"Nombre de nodes (chunks) : {n_chunks}\n")
        fh.write(f"Collection ChromaDB      : {COLLECTION_NOM} @ {VAULT_RAG / 'chromadb'}\n")
        fh.write(f"Remise à zéro (--reset)  : {'oui' if args.reset else 'non'}\n")
        fh.write(f"Cache LlamaIndex         : {VAULT_RAG / 'llamaindex_cache'}\n")

    print(f"Nodes (chunks) indexés : {n_chunks}")
    print(f"Log écrit : {log_path}")


if __name__ == "__main__":
    main()
