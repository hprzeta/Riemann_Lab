#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
multi_ia_query.py — Orchestrateur multi-IA (Claude, DeepSeek, Kimi)
═══════════════════════════════════════════════════════════════════════════
Interroge Claude (Anthropic), DeepSeek et Kimi (Moonshot AI) EN PARALLÈLE sur
une même question mathématique/technique (validation croisée ou optimisation
de code) et produit un rapport comparatif Markdown versionné.

Usage :
    python scripts/multi_ia_query.py "Votre question ici"
    python scripts/multi_ia_query.py --file question.txt
    python scripts/multi_ia_query.py "..." --skip kimi          # exclut une IA
    python scripts/multi_ia_query.py "..." --timeout 90

Secrets — ~/projet_zeta/.env (JAMAIS committé, voir .gitignore) :
    ANTHROPIC_API_KEY=...
    DEEPSEEK_API_KEY=...
    KIMI_API_KEY=...              # ou MOONSHOT_API_KEY, les deux sont acceptés
    # Optionnel — surcharge des modèles par défaut :
    CLAUDE_MODEL=claude-sonnet-5
    DEEPSEEK_MODEL=deepseek-chat
    KIMI_MODEL=moonshot-v1-32k

Une clé absente ne bloque PAS les autres IA — le rapport signale juste l'échec
pour celle-ci (voir generer_rapport()).

Sortie : pdf/optimisation/Voie_b_5/md_to_claude/multi_ia_<horodatage>.md
(dossier déjà exclu de git — c'est un staging local, pas versionné)

Auteur : hprzeta — Projet Hypothèse de Riemann
"""

import argparse
import concurrent.futures
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

PROJET_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = PROJET_DIR / ".env"
OUTPUT_DIR = PROJET_DIR / "pdf" / "optimisation" / "Voie_b_5" / "md_to_claude"

load_dotenv(ENV_PATH)

DEFAULT_TIMEOUT = 60  # secondes, par IA

# Modèles par défaut — surchargeables via .env sans toucher au code.
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
KIMI_MODEL = os.getenv("KIMI_MODEL", "moonshot-v1-32k")


def _resultat(ia, modele, ok, erreur, reponse, duree):
    return {"ia": ia, "modele": modele, "ok": ok, "erreur": erreur,
            "reponse": reponse, "duree": duree}


def query_claude(question: str, timeout: int) -> dict:
    """Interroge Claude via l'API Anthropic officielle."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return _resultat("Claude", CLAUDE_MODEL, False,
                          "ANTHROPIC_API_KEY absente de .env", None, 0.0)
    t0 = time.time()
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key, timeout=timeout)
        msg = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": question}],
        )
        texte = "".join(bloc.text for bloc in msg.content if hasattr(bloc, "text"))
        return _resultat("Claude", CLAUDE_MODEL, True, None, texte, time.time() - t0)
    except Exception as e:
        return _resultat("Claude", CLAUDE_MODEL, False, str(e), None, time.time() - t0)


def query_deepseek(question: str, timeout: int) -> dict:
    """Interroge DeepSeek via son API compatible OpenAI (api.deepseek.com)."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return _resultat("DeepSeek", DEEPSEEK_MODEL, False,
                          "DEEPSEEK_API_KEY absente de .env", None, 0.0)
    t0 = time.time()
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com", timeout=timeout)
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": question}],
        )
        texte = resp.choices[0].message.content
        return _resultat("DeepSeek", DEEPSEEK_MODEL, True, None, texte, time.time() - t0)
    except Exception as e:
        return _resultat("DeepSeek", DEEPSEEK_MODEL, False, str(e), None, time.time() - t0)


def query_kimi(question: str, timeout: int) -> dict:
    """Interroge Kimi via l'API Moonshot AI (compatible OpenAI)."""
    api_key = os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        return _resultat("Kimi", KIMI_MODEL, False,
                          "KIMI_API_KEY (ou MOONSHOT_API_KEY) absente de .env", None, 0.0)
    t0 = time.time()
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.moonshot.ai/v1", timeout=timeout)
        resp = client.chat.completions.create(
            model=KIMI_MODEL,
            messages=[{"role": "user", "content": question}],
        )
        texte = resp.choices[0].message.content
        return _resultat("Kimi", KIMI_MODEL, True, None, texte, time.time() - t0)
    except Exception as e:
        return _resultat("Kimi", KIMI_MODEL, False, str(e), None, time.time() - t0)


PROVIDERS = {"claude": query_claude, "deepseek": query_deepseek, "kimi": query_kimi}
ORDRE_AFFICHAGE = {"claude": 0, "deepseek": 1, "kimi": 2}


def interroger_toutes(question: str, timeout: int, skip: set) -> list:
    """Lance les IA actives en parallèle (ThreadPoolExecutor — appels HTTP bloquants).

    Chaque provider capture déjà ses propres exceptions (voir query_*), donc le
    try/except ici ne couvre que le cas résiduel d'une exception dans l'executor
    lui-même — un échec d'IA ne fait jamais tomber les autres.
    """
    actives = {nom: fn for nom, fn in PROVIDERS.items() if nom not in skip}
    resultats = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(len(actives), 1)) as ex:
        futures = {ex.submit(fn, question, timeout): nom for nom, fn in actives.items()}
        for future in concurrent.futures.as_completed(futures):
            nom = futures[future]
            try:
                resultats.append(future.result())
            except Exception as e:
                resultats.append(_resultat(nom.capitalize(), "?", False,
                                            "Exception non gérée : {}".format(e), None, 0.0))
    resultats.sort(key=lambda r: ORDRE_AFFICHAGE.get(r["ia"].lower(), 99))
    return resultats


def generer_rapport(question: str, resultats: list, horodatage: str) -> str:
    maintenant = datetime.now()
    lignes = [
        "> **Fichier :** multi_ia_{}.md · **Dossier :** pdf/optimisation/Voie_b_5/md_to_claude/".format(horodatage),
        "> **Auteur :** hprzeta · **Date :** {}".format(maintenant.strftime("%Y-%m-%d %H:%M")),
        "",
        "# Rapport multi-IA — {}".format(maintenant.strftime("%d/%m/%Y %H:%M")),
        "",
        "## Question posée",
        "",
        "```",
        question,
        "```",
        "",
    ]
    for r in resultats:
        lignes.append("## {} (`{}`)".format(r["ia"], r["modele"]))
        lignes.append("")
        if r["ok"]:
            lignes.append("*Répondu en {:.1f}s*".format(r["duree"]))
            lignes.append("")
            lignes.append(r["reponse"] or "*(réponse vide)*")
        else:
            lignes.append("**❌ Échec** ({:.1f}s) : {}".format(r["duree"], r["erreur"]))
        lignes.append("")
        lignes.append("---")
        lignes.append("")

    n_ok = sum(1 for r in resultats if r["ok"])
    lignes.append("## Résumé")
    lignes.append("")
    lignes.append("**{}/{}** IA ont répondu avec succès.".format(n_ok, len(resultats)))
    for r in resultats:
        statut = "✅" if r["ok"] else "❌"
        lignes.append("- {} {} (`{}`)".format(statut, r["ia"], r["modele"]))
    lignes.append("")
    lignes.append("---")
    lignes.append("*multi_ia_{}.md · pdf/optimisation/Voie_b_5/md_to_claude/ · hprzeta · {}*".format(
        horodatage, maintenant.strftime("%Y-%m-%d")))
    return "\n".join(lignes)


def parse_args():
    p = argparse.ArgumentParser(description="Interroge Claude, DeepSeek et Kimi en parallèle")
    p.add_argument("question", nargs="?", help="Question à poser (ou utiliser --file)")
    p.add_argument("--file", type=str, help="Fichier texte contenant la question")
    p.add_argument("--skip", action="append", default=[], choices=list(PROVIDERS.keys()),
                    help="IA à exclure (répétable), ex. --skip kimi")
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                    help="Timeout par IA en secondes (défaut {}s)".format(DEFAULT_TIMEOUT))
    return p.parse_args()


def main():
    args = parse_args()
    if args.file:
        question = Path(args.file).read_text(encoding="utf-8").strip()
    elif args.question:
        question = args.question
    else:
        print("Erreur : fournir une question en argument ou --file <chemin>")
        sys.exit(1)

    skip = set(args.skip)
    actives = [n for n in PROVIDERS if n not in skip]
    print("Interrogation en parallèle : {}".format(", ".join(actives)))

    resultats = interroger_toutes(question, args.timeout, skip)

    for r in resultats:
        statut = "OK ({:.1f}s)".format(r["duree"]) if r["ok"] else "ÉCHEC : {}".format(r["erreur"])
        print("  {} [{}] : {}".format(r["ia"], r["modele"], statut))

    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    rapport = generer_rapport(question, resultats, horodatage)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "multi_ia_{}.md".format(horodatage)
    out_path.write_text(rapport, encoding="utf-8")
    print("\nRapport écrit : {}".format(out_path))


if __name__ == "__main__":
    main()
