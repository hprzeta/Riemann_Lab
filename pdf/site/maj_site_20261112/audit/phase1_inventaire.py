#!/usr/bin/env python3
# Phase 1 — inventaire de tous les liens (lecture seule) -> audit/liens.csv
import csv, re, sys, glob, os, collections
from urllib.parse import urlparse

RACINE = os.path.expanduser("~/projet_zeta")           # racine du dépôt
SORTIE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "liens.csv")

# --- sources à analyser ---------------------------------------------------
sources = []
sources += sorted(glob.glob(RACINE + "/docs/**/*.html", recursive=True))   # site + animations
sources += sorted(glob.glob(RACINE + "/docs/**/*.md", recursive=True))     # .md de docs/
sources += [RACINE + "/README.md"]
sources += sorted(glob.glob(RACINE + "/Riemann_Lab.wiki/*.md"))           # wiki
sources += sorted(glob.glob(RACINE + "/Riemann_Lab.wiki/_*.md"))
sources = list(dict.fromkeys(s for s in sources if os.path.isfile(s)))     # sans doublon

# --- motifs ---------------------------------------------------------------
RE_ATTR = re.compile(r'<(a|iframe|script|link|img|source|video)\b[^>]*?\b(href|src)\s*=\s*["\']([^"\']*)["\']', re.I)
RE_MD = re.compile(r'(!?)\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)')
RE_WIKI = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
RE_URL = re.compile(r'(?<![\("\'<=\w])(https?://[^\s<>)\]"\']+)')

def type_lien(url, balise=""):
    """Classe un lien selon la nomenclature du prompt."""
    u = url.strip()
    if balise == "iframe": return "iframe"
    if balise in ("img",) : return "image"
    if balise == "script": return "script"
    if balise == "link": return "link"
    if u.startswith("#"): return "ancre interne"
    if u.lower().startswith(("mailto:", "tel:", "javascript:")): return "autre"
    base = u.split("#")[0].split("?")[0].lower()
    if base.endswith(".pdf"): return "PDF"
    if base.endswith((".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp")): return "image"
    if u.startswith("http"):
        p = urlparse(u)
        if "hprzeta.github.io" in p.netloc:
            return "ancre vers une autre page" if "#" in u else "page du site"
        if "github.com" in p.netloc and "/wiki" in p.path and "hprzeta" in p.path:
            return "ancre vers une autre page" if "#" in u else "page wiki"
        if "hprzeta" in p.path and "github" in p.netloc:
            return "ancre vers une autre page" if "#" in u else "fichier du dépôt"
        if "raw.githubusercontent.com" in p.netloc and "hprzeta" in p.path:
            return "fichier du dépôt"
        return "externe"
    # lien relatif
    if "#" in u and not u.startswith("#"): return "ancre vers une autre page"
    return "fichier du dépôt/relatif"

lignes = []
for src in sources:
    rel = os.path.relpath(src, RACINE)
    with open(src, encoding="utf-8", errors="replace") as f:
        contenu = f.read().split("\n")
    en_bloc = False                                    # ignore les blocs de code ```
    for n, ligne in enumerate(contenu, 1):
        if ligne.lstrip().startswith("```"):
            en_bloc = not en_bloc
        if en_bloc and rel.endswith(".md"):
            continue
        vus = set()
        for m in RE_ATTR.finditer(ligne):
            b, _, u = m.groups()
            txt = re.sub(r"<[^>]+>", "", ligne[m.end():m.end()+120].split("</a>")[0]).strip() if b.lower() == "a" else ""
            lignes.append((rel, n, txt, u, type_lien(u, b.lower()))); vus.add(u)
        est_md = rel.endswith('.md')                    # MD et [[wiki]] seulement dans les .md
        for m in (RE_MD.finditer(ligne) if est_md else []):
            img, txt, u = m.groups()
            lignes.append((rel, n, txt, u, type_lien(u, "img" if img else ""))); vus.add(u)
        for m in (RE_WIKI.finditer(ligne) if est_md else []):
            cible, txt = m.group(1), m.group(2) or m.group(1)
            lignes.append((rel, n, txt, "[[" + cible + "]]", "page wiki")); vus.add(cible)
        for m in RE_URL.finditer(ligne):
            u = m.group(1).rstrip(".,;:")
            if u not in vus:
                lignes.append((rel, n, "(URL nue)", u, type_lien(u)))

with open(SORTIE, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["source", "ligne", "texte", "url", "type"]); w.writerows(lignes)

print("Total liens :", len(lignes), "| URL distinctes :", len({l[3] for l in lignes}))
par_type = collections.Counter(l[4] for l in lignes)
print("\nPar type :"); [print(f"  {k:32s} {v}") for k, v in par_type.most_common()]
par_src = collections.Counter(("wiki" if l[0].startswith("Riemann_Lab.wiki") else
                               "site (docs/*.html)" if l[0].endswith(".html") else
                               "docs/*.md" if l[0].startswith("docs/") else "README") for l in lignes)
print("\nPar source :"); [print(f"  {k:32s} {v}") for k, v in par_src.most_common()]
print("\nFichiers analysés :", len(sources))
