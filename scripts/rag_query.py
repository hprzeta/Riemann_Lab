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
    plusieurs couches en RAM système sur cette machine (16 Go depuis le 25/07/2026). Fermer VS Code
    et Firefox avant un test, ou vérifier `free -h` — ce script avertit mais
    ne bloque pas.

Prérequis : zeta_env activé (chromadb, sentence-transformers, requests) ;
`ollama serve` actif (systemd ou manuel) avec le modèle mathstral pull.

Auteur : hprzeta — Projet Riemann_Lab — Objectif 2 (BrainVault)
Date   : 2026-07-19 (mis à jour 2026-10-04 : --k 4 par défaut, avertissement quand le
         prompt dépasse la fenêtre d'ollama, refus « non trouvé » sans faux avertissement)
"""

import argparse
import datetime
import os
import re
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
NUM_CTX_OLLAMA = 4096       # fenêtre de contexte par défaut d'ollama sur cette machine (Guide-Ollama-Pratique.md)
CARS_PAR_TOKEN = 2.5        # estimation (markdown + code), calibrée sur 1 mesure ollama du 04/10/2026 : 7354 tokens pour ~18 600 car. (2,53)

PROMPT_TEMPLATE = """Tu es un assistant technique du projet Riemann_Lab. Réponds \
UNIQUEMENT à partir du contexte ci-dessous (extraits du wiki/code du projet, \
chacun précédé de son fichier source entre crochets, ex. [fichier.md]).

Règle stricte de citation : pour CHAQUE fait, chiffre ou valeur exacte que tu \
donnes, recopie-le TEL QUEL depuis l'extrait source et fais suivre immédiatement \
d'une citation entre crochets avec le nom du fichier exact, ex. « 4 cœurs \
[Architecture-Cluster-Zeta.md] ». N'arrondis pas, ne reformule pas, ne déduis pas \
une valeur par analogie avec une autre. Si une information demandée n'apparaît \
mot pour mot dans AUCUN extrait ci-dessous, écris « non trouvé dans le contexte » \
pour cette information précise plutôt que de l'inventer ou de l'estimer.

--- CONTEXTE ---
{contexte}
--- FIN CONTEXTE ---

Question : {question}
Réponse (avec citation [fichier] après chaque fait) :"""


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
    # device="cpu" forcé : torch 2.11.0+cu130 a abandonné le support Maxwell
    # (CC 5.0, GTX 960M) — plante en CUDA sur l'embedding (incident 25/07/2026).
    # mathstral n'est pas affecté (moteur CUDA natif d'ollama, indépendant de torch).
    modele = SentenceTransformer(MODELE_EMBEDDING, device="cpu")
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


def construit_prompt(question: str, chunks: list) -> str:
    """Prompt complet envoyé au modèle (consigne + contexte + question)."""
    contexte = "\n\n".join(
        "[{}] {}".format(meta.get("file", meta.get("source", "?")), doc)
        for doc, meta, _ in chunks
    )
    return PROMPT_TEMPLATE.format(contexte=contexte, question=question)


def estime_tokens(question: str, chunks: list) -> int:
    """Nombre approximatif de tokens du prompt (sans tokenizer : caractères / CARS_PAR_TOKEN)."""
    return int(len(construit_prompt(question, chunks)) / CARS_PAR_TOKEN)


def k_conseille(question: str, chunks: list) -> int:
    """Plus grand k dont le prompt estimé tient dans NUM_CTX_OLLAMA (au moins 1)."""
    if not chunks:
        return 1
    fixe = estime_tokens(question, [])                       # consigne + question, sans contexte
    par_chunk = (estime_tokens(question, chunks) - fixe) / len(chunks)
    return max(1, int((NUM_CTX_OLLAMA - fixe) / max(par_chunk, 1)))


REFUS_RE = re.compile(r"non\s+trouv[ée]e?s?\s+dans\s+le\s+contexte", re.IGNORECASE)


def est_un_refus(texte_reponse: str) -> bool:
    """True si la réponse est un refus pur (« non trouvé dans le contexte ») sans aucun fait chiffré :
    aucune citation n'est alors attendue. Un refus accompagné de valeurs garde l'avertissement."""
    if not REFUS_RE.search(texte_reponse):
        return False
    reste = REFUS_RE.sub(" ", texte_reponse)
    return not VALEUR_RE.search(reste)


def generation(question: str, chunks: list, modele_llm: str) -> tuple:
    """Envoie le prompt (question + contexte) à mathstral via l'API ollama.
    Retourne (réponse, durée, tokens lus par ollama ou None)."""
    prompt = construit_prompt(question, chunks)

    t0 = time.time()
    reponse = requests.post(
        "{}/api/generate".format(OLLAMA_HOST),
        json={"model": modele_llm, "prompt": prompt, "stream": False},
        timeout=400,   # mathstral à froid : ~1m30-1m47 rien que pour charger (cf. Guide-Ollama-Pratique.md)
    )
    reponse.raise_for_status()
    t_generation = time.time() - t0

    donnees = reponse.json()
    # prompt_eval_count = tokens réellement lus par ollama (plafonné à la fenêtre si le prompt a été tronqué)
    return donnees.get("response", "").strip(), t_generation, donnees.get("prompt_eval_count")


CITATION_RE = re.compile(r"\b([\w\-]+\.(?:md|py|c|h))\b")   # nom de fichier, quels que soient les délimiteurs autour
VALEUR_RE = re.compile(r"\b(?:\d{1,3}(?:\.\d{1,3}){3}|\d+(?:[.,]\d+)?)\b")   # IP ou nombre


def citations_douteuses(texte_reponse: str, chunks: list) -> list:
    """Fichiers cités dans la réponse (entre crochets, parenthèses, ou combinaison des
    deux — mathstral n'est pas cohérent sur le format malgré la consigne) mais absents
    des chunks retrouvés — la citation elle-même est fabriquée.

    Ne prouve PAS que le fait cité est faux : mathstral peut citer une source réelle
    pour une valeur inventée (cf. incident IP cluster 19/07/2026, où les 4 citations
    étaient correctes mais les 4 valeurs fausses) — voir valeurs_non_ancrees() pour
    la vérification qui compte réellement.

    Compare sur le nom de base (`os.path.basename`) : les fichiers de code sont
    indexés avec leur chemin complet (`src/.../illinois_arb.c`, voir
    rag_ingest_corpus.py) mais CITATION_RE n'extrait que le nom de fichier — une
    comparaison stricte sur le chemin complet donnait de faux positifs (testé
    19/07/2026 : `illinois_arb.c` signalé "fabriqué" alors qu'il était bien retrouvé).
    """
    sources_connues = {
        os.path.basename(meta.get("file", meta.get("source", "?")))
        for _, meta, _ in chunks
    }
    citees = set(CITATION_RE.findall(texte_reponse))
    return sorted(c for c in citees if os.path.basename(c) not in sources_connues)


def normaliser_separateurs_milliers(s: str) -> str:
    """Supprime les virgules/espaces utilisés comme séparateurs de milliers
    (20,000 ou 20 000 → 20000) sans toucher aux virgules/espaces suivis d'autre
    chose qu'un chiffre — évite de casser du texte normal ("Newton, la...").
    """
    return re.sub(r"[,\s](?=\d)", "", s)


def valeurs_non_ancrees(texte_reponse: str, chunks: list) -> list:
    """Nombres/IP de la réponse absents (littéralement) du texte des chunks retrouvés.

    Vérification programmatique indépendante de ce que le modèle prétend citer —
    un chiffre halluciné n'apparaît dans aucun chunk source, quelle que soit la
    citation accolée. Ignore les petits entiers (1-2 chiffres, ex. numérotation de
    liste "1.", "2.") pour limiter les faux positifs.

    Compare aussi les formes normalisées (séparateur de milliers ôté) : mathstral
    reformate parfois une valeur correcte (`20000.0` en source → `20,000.0` en
    réponse) — un faux positif observé le 19/07/2026 sinon.
    """
    contexte_brut = "\n".join(doc for doc, _, _ in chunks)
    contexte_norm = normaliser_separateurs_milliers(contexte_brut)
    non_ancres = []
    for m in VALEUR_RE.findall(texte_reponse):
        est_ip = m.count(".") == 3
        significatif = est_ip or len(re.sub(r"[.,]", "", m)) >= 3
        if not significatif:
            continue
        if m in contexte_brut:
            continue
        if normaliser_separateurs_milliers(m) in contexte_norm:
            continue
        non_ancres.append(m)
    return sorted(set(non_ancres))


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
    parser.add_argument("--k", type=int, default=4, help="nombre de chunks retrouvés (défaut 4 depuis le 04/10/2026 : avec le corpus actuel, k=8 donne ~7300 tokens et ollama tronque à 4096, consigne perdue. Le 25/07, k=3/6 ratait le chunk clé au rang 7 sur SEUIL_1NEWTON : le script avertit si le prompt dépasse la fenêtre, k plus grand seulement s'il tient)")
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

    tokens_estimes = estime_tokens(args.question, chunks)
    print("  prompt estimé : ~{} tokens (fenêtre ollama : {})".format(tokens_estimes, NUM_CTX_OLLAMA))
    if tokens_estimes > NUM_CTX_OLLAMA:
        print("⚠️  prompt estimé > fenêtre d'ollama : il sera TRONQUÉ et la consigne de citation (au début) sera "
              "perdue — réponses dégradées possibles. Relance avec --k {} au plus.".format(k_conseille(args.question, chunks)))

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
            texte_reponse, t_generation, tokens_lus = generation(args.question, chunks, args.modele)
            latences["generation"] = t_generation
            print("  génération : {:.1f} s".format(t_generation)
                  + (" — prompt lu par ollama : {} tokens (estimé : {})".format(tokens_lus, tokens_estimes)
                     if tokens_lus is not None else ""))
            if tokens_lus is not None and tokens_lus >= NUM_CTX_OLLAMA - 8:
                print("⚠️  ollama a lu {} tokens (= la fenêtre de {}) : le prompt a été TRONQUÉ, "
                      "la consigne de citation a pu être perdue.".format(tokens_lus, NUM_CTX_OLLAMA))
            print("\n{}".format(texte_reponse))

            non_ancrees = valeurs_non_ancrees(texte_reponse, chunks)
            if non_ancrees:
                print("\n🚫 valeur(s) ABSENTE(S) du contexte source (hallucination probable) : {} "
                      "— ces chiffres n'apparaissent dans AUCUN chunk retrouvé, quelle que soit "
                      "la citation donnée par le modèle.".format(", ".join(non_ancrees)))

            douteuses = citations_douteuses(texte_reponse, chunks)
            if douteuses:
                print("⚠️  citation(s) fabriquée(s) (fichier cité absent des chunks retrouvés) : {}"
                      .format(", ".join(douteuses)))
            elif est_un_refus(texte_reponse):
                print("ℹ️  refus « non trouvé dans le contexte » : aucune citation attendue.")
            elif not CITATION_RE.search(texte_reponse):
                print("⚠️  aucune citation [fichier] dans la réponse malgré la consigne — "
                      "faits non traçables, à vérifier manuellement.")
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
