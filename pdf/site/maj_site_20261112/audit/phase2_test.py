#!/usr/bin/env python3
# Phase 2 — test de CHAQUE lien (lecture seule) -> audit/liens_statut.csv
# Règles : 1 requête/s vers github.com / raw.githubusercontent.com, 3 essais sur 429/5xx, UA normal.
import csv, os, re, subprocess, sys, time, html, urllib.request, urllib.error, urllib.parse, collections

RACINE = os.path.expanduser("~/projet_zeta")
AUDIT = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
SITE = "https://hprzeta.github.io/Riemann_Lab/"
WIKI = "https://github.com/hprzeta/Riemann_Lab/wiki/"
LENTS = ("github.com", "raw.githubusercontent.com", "hprzeta.github.io")

cache = {}                                  # url sans ancre -> (code, url_finale, titre, corps_html, note)
dernier = collections.defaultdict(float)    # dernière requête par hôte

def requete(url, methode="GET"):
    """Une requête avec 3 essais sur 429/5xx ; renvoie (code, url_finale, corps)."""
    hote = urllib.parse.urlparse(url).netloc
    for essai in range(3):
        attente = 1.05 - (time.time() - dernier[hote])          # 1 requête/s sur les hôtes GitHub
        if hote in LENTS and attente > 0: time.sleep(attente)
        dernier[hote] = time.time()
        rq = urllib.request.Request(url, method=methode, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
        try:
            with urllib.request.urlopen(rq, timeout=25) as r:
                corps = r.read(3_000_000) if methode == "GET" else b""
                return r.status, r.geturl(), corps.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and essai < 2:
                time.sleep(5 * (essai + 1)); continue
            return e.code, url, ""
        except Exception as e:                                    # DNS, TLS, délai
            if essai < 2: time.sleep(3); continue
            return 0, url, "ERR " + type(e).__name__
    return 0, url, ""

def sonder(url):
    """Teste une URL absolue (sans ancre), avec cache. GET direct (nécessaire pour titre + ancres)."""
    if url in cache: return cache[url]
    code, fin, corps = requete(url, "GET")
    m = re.search(r"<title[^>]*>(.*?)</title>", corps, re.S | re.I)
    titre = html.unescape(m.group(1)).strip()[:90] if m else ""
    cache[url] = (code, fin, titre, corps)
    return cache[url]

def ids_de(corps):
    """Ensemble des id / name présents dans un HTML."""
    return set(re.findall(r'\b(?:id|name)\s*=\s*"([^"]+)"', corps))

def sur_branche(branche, chemin):
    """Le fichier existe-t-il sur cette branche ? (git cat-file)"""
    return subprocess.run(["git", "-C", RACINE, "cat-file", "-e", f"{branche}:{chemin}"],
                          capture_output=True).returncode == 0

def résoudre(src, url, typ):
    """Transforme un lien (relatif/[[wiki]]) en (url_absolue, chemin_local|None)."""
    u = url.strip()
    if u.startswith("[["):
        nom = u[2:-2].strip().replace(" ", "-")
        return WIKI + urllib.parse.quote(nom), f"Riemann_Lab.wiki/{nom}.md"
    if re.match(r"^[a-z][a-z0-9+.-]*:", u, re.I) or u.startswith("//"):
        return (("https:" + u) if u.startswith("//") else u), None
    base, _, anc = u.partition("#")
    base = urllib.parse.unquote(base.split("?")[0])
    if src.startswith("Riemann_Lab.wiki/"):                       # lien relatif dans le wiki
        if base == "": return None, None
        if "." not in os.path.basename(base):                     # page wiki
            return WIKI + urllib.parse.quote(base.lstrip("./")) + (("#" + anc) if anc else ""), f"Riemann_Lab.wiki/{base}.md"
        return None, f"Riemann_Lab.wiki/{base}"
    dossier = os.path.dirname(src)                                # docs/… ou racine
    chemin = os.path.normpath(os.path.join(dossier, base)) if base else src
    pub = chemin[5:] if chemin.startswith("docs/") else None
    absu = (SITE + urllib.parse.quote(pub) + (("#" + anc) if anc else "")) if pub and chemin.endswith((".html", ".pdf", ".png", ".svg", ".jpg")) else None
    return absu, chemin

lignes = list(csv.DictReader(open(os.path.join(AUDIT, "liens.csv"), encoding="utf-8")))
sortie = []
n = 0
for L in lignes:
    n += 1
    src, url, typ = L["source"], L["url"], L["type"]
    statut, http, ancre, action, note = "🟢", "", "", "", ""
    if L["texte"] == "(URL nue)" and "…" in url: pass
    if url.lower().startswith(("mailto:", "tel:", "javascript:")):
        sortie.append({**L, "http": "-", "ancre": "-", "statut": "🟢", "action": "", "note": "non HTTP (mailto/tel/js)"}); continue
    if url.startswith("#"):                                       # ancre interne : lire le fichier source
        anc = urllib.parse.unquote(url[1:])
        chemin = os.path.join(RACINE, src)
        ok = None
        if src.endswith(".html"):
            corps = open(chemin, encoding="utf-8", errors="replace").read()
            ok = anc in ids_de(corps)
        else:                                                     # .md : titres GitHub (slug) ou ids html
            corps = open(chemin, encoding="utf-8", errors="replace").read()
            slugs = set()
            for h in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", corps, re.M):
                s = re.sub(r"[^\w\s-]", "", re.sub(r"`|\*|_", "", h).lower()).strip().replace(" ", "-")
                slugs.add(s)
            ok = anc.lower() in slugs or anc in ids_de(corps) or anc.lower().replace("user-content-", "") in slugs
        statut = "🟢" if ok else "🔴"
        sortie.append({**L, "http": "local", "ancre": "présente" if ok else "ABSENTE", "statut": statut,
                       "action": "" if ok else "ancre introuvable dans le fichier", "note": ""}); continue

    absu, local = résoudre(src, url, typ)
    base, _, anc = (absu or "").partition("#")
    anc = urllib.parse.unquote(anc)

    # --- 1) fichier local (dépôt / wiki) ---
    if local:
        if local.startswith("Riemann_Lab.wiki/"):
            ex = os.path.isfile(os.path.join(RACINE, local))
            note = "wiki local " + ("OK" if ex else "ABSENT")
        else:
            ex_i = os.path.isfile(os.path.join(RACINE, local)) or os.path.isdir(os.path.join(RACINE, local))
            ex_m = sur_branche("main", local); ex_ia = sur_branche("Riemann_Lab_IA", local)
            ex = ex_i
            note = f"dépôt: copie locale {'oui' if ex_i else 'NON'}, main {'oui' if ex_m else 'NON'}, IA {'oui' if ex_ia else 'NON'}"
            if ex_i and not (ex_m and ex_ia): statut = "🟡"; action = "fichier absent d'une des branches (non commité ?)"
        if not ex: statut = "🔴"; action = "fichier introuvable"
    # --- 2) test HTTP ---
    if absu and absu.startswith("http"):
        if "[" in absu and "]" in absu and "github" not in absu: pass
        code, fin, titre, corps = sonder(base)
        http = f"{code}" + ("" if fin.rstrip("/") == base.rstrip("/") else f" → {fin[:90]}")
        if code == 0: statut = "🔴"; action = "réseau/DNS/TLS : " + corps[:30]
        elif code == 429: statut = "🟡"; action = "429 : à retester plus tard (pas un lien cassé)"
        elif code >= 400: statut = "🔴"; action = f"HTTP {code}"
        else:
            # page wiki inexistante : redirection vers l'accueil du wiki ou page de création
            if base.startswith(WIKI) and base.rstrip("/") != WIKI.rstrip("/"):
                if fin.rstrip("/") == WIKI.rstrip("/") or "Create" in titre or "create" in fin.lower() or "Welcome" in titre:
                    statut = "🔴"; action = "page wiki inexistante (renvoi vers l'accueil/création)"
                elif urllib.parse.unquote(fin).rstrip("/") != urllib.parse.unquote(base).rstrip("/") and statut != "🔴":
                    statut = "🟡"; action = "redirection : " + fin[:80]
            elif fin.rstrip("/") != base.rstrip("/") and statut == "🟢":
                statut = "🟡"; action = "redirection → " + fin[:80]
            if absu.startswith("http://"): statut = "🟡" if statut == "🟢" else statut; action = (action + " ; ").lstrip(" ;") + "http:// → https://"
            if anc:                                               # vérifier l'ancre dans la page cible
                ids = ids_de(corps)
                present = anc in ids or ("user-content-" + anc) in ids or anc.replace("user-content-", "") in ids
                ancre = "présente" if present else "ABSENTE"
                if not present: statut = "🔴"; action = "ancre absente de la page cible"
                elif re.search(r"%[0-9A-Fa-f]{2}", L["url"].partition("#")[2]) and statut == "🟢":
                    statut = "🟡"; action = "ancre à accents (forme encodée)"
        # ancien format Formation-Zeta-HR#ch…
        if re.search(r"Formation-Zeta-HR#(user-content-)?ch", L["url"]):
            statut = "🟡" if statut == "🟢" else statut
            action = (action + " ; " if action else "") + "ancien format → Formation-Zeta-HR-ChNN"
    elif not local:
        statut, action = "🔴", "URL non résolue"
    sortie.append({**L, "http": http or "-", "ancre": ancre or "-", "statut": statut, "action": action, "note": note})
    if n % 25 == 0: print(f"  … {n}/{len(lignes)}", flush=True)

champs = ["source", "ligne", "texte", "url", "type", "http", "ancre", "statut", "action", "note"]
with open(os.path.join(AUDIT, "liens_statut.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=champs); w.writeheader(); w.writerows(sortie)
c = collections.Counter(x["statut"] for x in sortie)
print("FIN", dict(c), "| URL distinctes sondées :", len(cache))
