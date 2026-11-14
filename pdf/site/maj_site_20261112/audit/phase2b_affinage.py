#!/usr/bin/env python3
# Phase 2b — affinage (lecture seule) : revérifie les ancres du wiki sur les pages EN LIGNE,
# corrige les cas [[texte|page]], écarte les faux positifs d'extraction -> liens_statut_final.csv
import csv, os, re, time, urllib.request, urllib.parse, collections

RACINE = os.path.expanduser("~/projet_zeta")
AUDIT = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"}
WIKI = "https://github.com/hprzeta/Riemann_Lab/wiki/"
cache, dernier = {}, [0.0]

def ids_en_ligne(page):
    """Ids 'user-content-…' de la page wiki publiée (1 requête/s)."""
    if page in cache: return cache[page]
    time.sleep(max(0, 1.05 - (time.time() - dernier[0]))); dernier[0] = time.time()
    try:
        h = urllib.request.urlopen(urllib.request.Request(WIKI + urllib.parse.quote(page), headers=UA), timeout=25).read().decode("utf-8", "replace")
        cache[page] = set(re.findall(r'id="user-content-([^"]+)"', h))
    except Exception as e:
        cache[page] = None
    return cache[page]

# Textes qui sont de la DOCUMENTATION (exemples de syntaxe), pas de vrais liens
FAUX_URL = {"[[Page]]", "[[Étape-2/3/4]]", "[[label]]", "s", "[[...]]", "[[Nom de la page]]", "[[ ]]"}
def faux_positif(x):
    u = x["url"]
    if u in FAUX_URL: return "exemple de syntaxe cité dans le texte (pas un lien)"
    if u.endswith(("`", "**")) or u.startswith(")"): return "URL entourée de ` ou ** dans le texte : artefact d'extraction"
    if "localhost" in u or "127.0.0.1" in u: return "adresse locale citée dans le texte"
    if re.match(r"\[\[.*analyse\\_math", u): return "nom échappé \\_ dans un .md d'archive de discussion"
    return None

lignes = list(csv.DictReader(open(os.path.join(AUDIT, "liens_statut.csv"), encoding="utf-8")))
wiki_pages = {f[:-3] for f in os.listdir(RACINE + "/Riemann_Lab.wiki") if f.endswith(".md")}
out = []
for x in lignes:
    src, u = x["source"], x["url"]
    fp = faux_positif(x)
    if fp:
        x.update(statut="⚪", action="faux positif : " + fp); out.append(x); continue
    # [[texte|page]] (barre échappée ou non) : la CIBLE est la partie après la barre
    m = re.match(r"^\[\[(.+?)\\?\|(.+?)\]\]$", u)
    if m and src.startswith("Riemann_Lab.wiki/"):
        cible = m.group(2).strip().replace(" ", "-")
        ok = cible in wiki_pages
        x.update(statut="🟢" if ok else "🔴", http="local", action="" if ok else f"page wiki « {cible} » absente",
                 note=f"cible = {cible}"); out.append(x); continue
    if u in ("[[Home]]",):
        x.update(statut="🟢", action="", note="Home = accueil du wiki"); out.append(x); continue
    # ancres internes d'une page wiki : test sur la page EN LIGNE
    if src.startswith("Riemann_Lab.wiki/") and (u.startswith("#") or u.startswith("[[#")):
        anc = urllib.parse.unquote(u.strip("[]").lstrip("#"))
        page = os.path.basename(src)[:-3]
        ids = ids_en_ligne(page)
        if ids is None: x.update(statut="🟡", action="page en ligne illisible : à retester"); out.append(x); continue
        ok = anc in ids or anc.replace("user-content-", "") in ids
        x.update(http="en ligne", ancre="présente" if ok else "ABSENTE", statut="🟢" if ok else "🔴",
                 action="" if ok else "ancre absente de la page publiée")
        if not ok:
            cand = [i for i in ids if i.startswith(anc.lstrip("-")[:12]) or anc.lstrip("-").replace("_", "") in i.replace("_", "")]
            if cand: x["note"] = "id réel proche : " + cand[0]
        out.append(x); continue
    # liens GitHub qui exigent une connexion (404 en anonyme)
    if re.search(r"github\.com/(issues\?|users/hprzeta/projects)", u):
        x.update(statut="🟡", action="404 sans connexion (page privée/connectée) : à tester dans le Chrome connecté"); out.append(x); continue
    if "doi.org" in u and x["http"].startswith("403"):
        x.update(statut="🟡", action="403 (anti-robot de l'éditeur) : à tester dans le navigateur"); out.append(x); continue
    out.append(x)

champs = ["source", "ligne", "texte", "url", "type", "http", "ancre", "statut", "action", "note"]
with open(os.path.join(AUDIT, "liens_statut_final.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=champs); w.writeheader(); w.writerows(out)
c = collections.Counter(x["statut"] for x in out)
print("FINAL", dict(c))
for s in ("🔴", "🟡"):
    print("=====", s)
    g = collections.OrderedDict()
    for x in out:
        if x["statut"] == s:
            g.setdefault((x["url"][:80], x["action"][:60], x["note"][:40]), []).append(os.path.basename(x["source"])[:22] + ":" + x["ligne"])
    for k, v in g.items(): print(len(v), k, v[:2])
