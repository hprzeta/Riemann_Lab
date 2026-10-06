#!/usr/bin/env python3
# =============================================================================
# zeta_jsonl_to_md.py — Transcription Claude Code (.jsonl) -> Markdown propre
# Auteur : hprzeta · Projet : Riemann_Lab · Créé : 6 octobre 2026
# Usage  : zeta-convert-jsontomd [SESSION] [-o DOSSIER] [--liste]
#          SESSION = chemin .jsonl | début d'identifiant | numéro (voir --liste)
#                    (défaut : la session la plus récente = celle en cours)
# Garanties : lecture SEULE du .jsonl ; sorties d'outils et raisonnement omis ;
#             adresses réseau, e-mails et secrets masqués ; sortie en mode 600.
# =============================================================================
import argparse  # lecture des options de la ligne de commande
import glob  # recherche des fichiers .jsonl
import ipaddress  # validation stricte des adresses IPv4/IPv6
import json  # lecture des lignes JSON
import os  # chemins, droits, dates de modification
import re  # expressions régulières de masquage
import sys  # sorties d'erreur et code de retour
from datetime import datetime  # conversion des horodatages UTC -> local

# Dossier où Claude Code range ses transcriptions pour ce projet
DOSSIER_JSONL = os.path.expanduser("~/.claude/projects/-home-riemann-projet-zeta")
# Dossier de sortie par défaut (ignoré par git, cf. .gitignore)
DOSSIER_SORTIE = os.path.expanduser("~/projet_zeta/claude-traitement-journalier")
# Fichier hors git contenant les vraies adresses du cluster (VAR=valeur)
FICHIER_HOTES = os.path.expanduser("~/.config/zeta/cluster_hosts.env")

# --- Motifs de masquage -------------------------------------------------------
# Bloc de clé privée complet (multi-lignes)
RE_CLE_PRIVEE = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?(?:-----END [A-Z ]*PRIVATE KEY-----|$)", re.S)
# Jetons à préfixe connu (GitHub, etc.)
RE_JETON = re.compile(r"\b(?:ghp_|gho_|ghs_|github_pat_|sk-)[A-Za-z0-9_\-]{16,}")
# Affectations « token=..., password: ..., api key = ... » : on garde le nom, on masque la valeur
RE_AFFECT = re.compile(r"(?i)\b(token|passw\w*|password|api[_ -]?key|secret)(\s*[=:]\s*)(?!\*\*\*)([^\s\"'`,;)]+)")
# Noms d'hôte DDNS DuckDNS
RE_DDNS = re.compile(r"(?i)\b[\w-]+\.duckdns\.org\b")
# Adresses e-mail
RE_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
# Adresses MAC
RE_MAC = re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b")
# Candidats IPv4 (validés ensuite par ipaddress)
RE_IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w])")
# Candidats IPv6 : suites hexadécimales avec « : » (validées ensuite par ipaddress)
RE_IPV6 = re.compile(r"(?<![\w:.])[0-9A-Fa-f:]{6,}(?![\w:])")
# Balises de contexte injectées par Claude Code (à retirer des messages utilisateur)
RE_BALISES = re.compile(r"<(system-reminder|command-name|command-message|command-args|local-command-stdout|local-command-caveat)>.*?</\1>", re.S)


def charger_valeurs_hotes():
    """Lit les valeurs réelles du cluster (hors git) pour les masquer à l'identique."""
    valeurs = []  # liste des chaînes à masquer
    try:
        with open(FICHIER_HOTES, encoding="utf-8") as f:  # ouverture en lecture seule
            for ligne in f:  # parcours ligne à ligne
                ligne = ligne.strip()  # retrait des espaces
                if not ligne or ligne.startswith("#") or "=" not in ligne:
                    continue  # on ignore commentaires et lignes invalides
                v = ligne.split("=", 1)[1].strip().strip("'\"")  # valeur sans guillemets
                if len(v) >= 4:  # on évite les valeurs trop courtes (faux positifs)
                    valeurs.append(v)
    except OSError:
        pass  # fichier absent : les motifs génériques restent actifs
    return sorted(set(valeurs), key=len, reverse=True)  # les plus longues d'abord


VALEURS_HOTES = charger_valeurs_hotes()  # chargé une seule fois


def masquer(texte, compteurs):
    """Applique tous les masquages ; incrémente compteurs[nom] pour le bilan."""
    def sub(motif, remplacement, nom, t):
        t2, n = motif.subn(remplacement, t)  # substitution + nombre d'occurrences
        if n:
            compteurs[nom] = compteurs.get(nom, 0) + n  # comptage pour le bilan
        return t2

    for v in VALEURS_HOTES:  # valeurs exactes du cluster
        if v in texte:
            compteurs["hote_cluster"] = compteurs.get("hote_cluster", 0) + texte.count(v)
            texte = texte.replace(v, "[HOTE_CLUSTER]")
    texte = sub(RE_CLE_PRIVEE, "***CLE_PRIVEE***", "cle_privee", texte)
    texte = sub(RE_JETON, "***", "jeton", texte)
    texte = sub(RE_AFFECT, lambda m: f"{m.group(1)}{m.group(2)}***", "secret", texte)
    texte = sub(RE_DDNS, "[DDNS]", "ddns", texte)
    texte = sub(RE_EMAIL, "[EMAIL]", "email", texte)
    texte = sub(RE_MAC, "[MAC]", "mac", texte)

    def ip4(m):  # n'ôte que les vraies IPv4 (0-255 par octet)
        try:
            ipaddress.IPv4Address(m.group(0))
        except ValueError:
            return m.group(0)  # pas une IP : on laisse (ex. 1.2.3.999)
        compteurs["ipv4"] = compteurs.get("ipv4", 0) + 1
        return "[IPV4]"

    def ip6(m):  # n'ôte que les vraies IPv6 (écarte heures, « 1::2 » trop court, etc.)
        s = m.group(0)
        if s.count(":") < 2:
            return s
        try:
            ipaddress.IPv6Address(s)
        except ValueError:
            return s
        compteurs["ipv6"] = compteurs.get("ipv6", 0) + 1
        return "[IPV6]"

    texte = RE_IPV4.sub(ip4, texte)
    texte = RE_IPV6.sub(ip6, texte)
    return texte


def lister_sessions():
    """Retourne les .jsonl triés du plus récent au plus ancien."""
    fichiers = glob.glob(os.path.join(DOSSIER_JSONL, "*.jsonl"))
    return sorted(fichiers, key=os.path.getmtime, reverse=True)


def choisir_session(arg):
    """Résout l'argument (chemin, préfixe d'identifiant, numéro) en fichier .jsonl."""
    sessions = lister_sessions()
    if not arg:  # défaut : la plus récente
        return sessions[0] if sessions else None
    if os.path.isfile(arg):  # chemin direct
        return arg
    if arg.isdigit() and 1 <= int(arg) <= len(sessions):  # numéro de --liste
        return sessions[int(arg) - 1]
    corresp = [s for s in sessions if os.path.basename(s).startswith(arg)]  # préfixe
    return corresp[0] if len(corresp) == 1 else None


def heure_locale(iso):
    """'2026-10-06T15:05:12.123Z' -> datetime local (None si illisible)."""
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone()
    except (ValueError, AttributeError):
        return None


def texte_message(contenu):
    """Extrait uniquement les textes d'un champ content (str ou liste de blocs)."""
    if isinstance(contenu, str):
        return contenu
    morceaux = []
    for b in contenu or []:
        if isinstance(b, dict) and b.get("type") == "text":
            morceaux.append(b.get("text", ""))  # blocs de texte seulement
    return "\n\n".join(morceaux)


def resume_outil(bloc):
    """Une ligne courte pour un appel d'outil (sans sortie)."""
    entree = bloc.get("input") or {}
    # champ le plus parlant selon l'outil
    for cle in ("description", "command", "file_path", "pattern", "url", "query", "skill"):
        if entree.get(cle):
            cible = str(entree[cle]).replace("\n", " ")
            return f"{bloc.get('name', 'outil')} : {cible[:140]}"
    return str(bloc.get("name", "outil"))


def convertir(chemin):
    """Lit le .jsonl et retourne (markdown, premiere_date, compteurs, stats)."""
    compteurs = {}  # bilan des masquages
    blocs = []  # morceaux de markdown, dans l'ordre
    premiere = None  # date du premier message
    stats = {"user": 0, "assistant": 0, "outils": 0}
    outils_en_attente = []  # lignes d'outils à rattacher au prochain texte assistant
    with open(chemin, encoding="utf-8", errors="replace") as f:  # lecture seule
        for ligne in f:
            try:
                o = json.loads(ligne)  # une ligne = un objet JSON
            except json.JSONDecodeError:
                continue  # ligne tronquée : ignorée
            if o.get("isSidechain") or o.get("isMeta"):
                continue  # sous-agents et messages méta : exclus
            t = o.get("type")
            m = o.get("message")
            if t not in ("user", "assistant") or not isinstance(m, dict):
                continue  # attachments, snapshots, etc. : exclus
            d = heure_locale(o.get("timestamp"))
            premiere = premiere or d
            hh = d.strftime("%H:%M") if d else "--:--"
            contenu = m.get("content")
            if t == "user":
                txt = RE_BALISES.sub("", texte_message(contenu)).strip()  # sans balises de contexte
                if not txt:
                    continue  # simple tool_result : omis
                if outils_en_attente:  # on referme les outils de la réponse précédente
                    blocs.append("\n".join(outils_en_attente) + "\n")
                    outils_en_attente = []
                stats["user"] += 1
                blocs.append(f"## 👤 hprzeta — {hh}\n\n{txt}\n")
            else:
                if isinstance(contenu, list):
                    for b in contenu:  # appels d'outils : une ligne chacun
                        if isinstance(b, dict) and b.get("type") == "tool_use":
                            stats["outils"] += 1
                            outils_en_attente.append(f"> 🔧 {resume_outil(b)}")
                txt = texte_message(contenu).strip()
                if txt:
                    if outils_en_attente:  # outils avant le texte
                        blocs.append("\n".join(outils_en_attente) + "\n")
                        outils_en_attente = []
                    stats["assistant"] += 1
                    blocs.append(f"## 🤖 Claude — {hh}\n\n{txt}\n")
    if outils_en_attente:
        blocs.append("\n".join(outils_en_attente) + "\n")
    entete = (
        f"# Transcription Claude Code — {premiere.strftime('%Y-%m-%d') if premiere else 'date inconnue'}\n\n"
        f"> Source : `{os.path.basename(chemin)}` · sorties d'outils et raisonnement interne **omis** · "
        f"adresses, e-mails et secrets **masqués**.\n"
    )
    corps = masquer("\n".join([entete] + blocs), compteurs)  # masquage sur TOUT le texte final
    return corps, premiere, compteurs, stats


def main():
    p = argparse.ArgumentParser(description="Convertit une transcription Claude Code .jsonl en .md")
    p.add_argument("session", nargs="?", help="chemin, début d'identifiant ou numéro (défaut : la plus récente)")
    p.add_argument("-o", "--sortie", default=DOSSIER_SORTIE, help="dossier de sortie")
    p.add_argument("--liste", action="store_true", help="liste les sessions disponibles")
    a = p.parse_args()

    if a.liste:  # mode liste : numéro, date, taille, identifiant
        for i, s in enumerate(lister_sessions(), 1):
            dt = datetime.fromtimestamp(os.path.getmtime(s)).strftime("%Y-%m-%d %H:%M")
            print(f"{i:3d}  {dt}  {os.path.getsize(s) // 1024:6d} Ko  {os.path.basename(s)}")
        return 0

    src = choisir_session(a.session)
    if not src:
        print("Session introuvable (ou préfixe ambigu) — voir --liste", file=sys.stderr)
        return 1

    md, debut, compteurs, stats = convertir(src)
    # Contrôle de sécurité : une 2e passe de masquage ne doit RIEN changer
    reste = {}
    if masquer(md, reste) != md:
        print("⚠️  ÉCHEC du contrôle : des valeurs sensibles subsistent — fichier NON écrit.", file=sys.stderr)
        return 2

    os.makedirs(a.sortie, exist_ok=True)  # création du dossier si besoin
    horo = (debut or datetime.now()).strftime("%Y%m%d_%H%M")
    sortie = os.path.join(a.sortie, f"session_{horo}_jsonl.md")
    fd = os.open(sortie, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)  # créé en 600 d'emblée
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"✅ {sortie}")
    print(f"   {stats['user']} messages hprzeta · {stats['assistant']} réponses Claude · {stats['outils']} appels d'outils (résumés)")
    print(f"   {md.count(chr(10)) + 1} lignes · masquages : {compteurs if compteurs else 'aucun'}")
    print("   Contrôle 2e passe : propre. Fichier non commité (dossier ignoré par git).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
