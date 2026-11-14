#!/usr/bin/env python3
# Diagnostic D26/D27 (lecture seule) : tous les liens entrants vers les 5 pages à accents + titres d'Animations
import os, re, glob, unicodedata, urllib.parse, subprocess, csv, sys
R = os.path.expanduser("~/projet_zeta"); W = R + "/Riemann_Lab.wiki"
NOMS = {"Etape-1-Calcul-des-zéros-non-triviaux": "Etape-1-Calcul-des-zeros-non-triviaux",
        "Interprétation-des-résultats-de-tests": "Interpretation-des-resultats-de-tests",
        "Partie-1-La-Théorie-Étape_1": "Partie-1-La-Theorie-Etape_1",
        "Projet-Zêta": "Projet-Zeta",
        "Tableau-Symboles-Mathématiques": "Tableau-Symboles-Mathematiques"}
def formes(n):
    f = {n: "accent (NFC)", unicodedata.normalize("NFD", n): "accent (NFD)",
         urllib.parse.quote(n): "encodé %XX", urllib.parse.quote(n).lower(): "encodé %xx"}
    return f
# fichiers à scanner (hors dépendances, sauvegardes et dossiers de travail)
fich = []
for base, pat in [(W, "*.md"), (R + "/docs", "**/*.html"), (R + "/docs", "**/*.md"), (R, "README.md")]:
    fich += glob.glob(os.path.join(base, pat), recursive=True)
for ext in ("py", "sh"):
    for p in glob.glob(R + f"/**/*.{ext}", recursive=True):
        if not any(s in p for s in ("zeta_env", "/pdf/", "/src/ia/prompts", "/.git/", "__pycache__")): fich.append(p)
fich = sorted(set(f for f in fich if os.path.isfile(f) and ".bak" not in os.path.basename(f)))
lignes = []
for ancien, nouveau in NOMS.items():
    for forme, label in formes(ancien).items():
        for f in fich:
            try: txt = open(f, encoding="utf-8", errors="replace").read().split("\n")
            except Exception: continue
            for i, l in enumerate(txt, 1):
                if forme in l:
                    k = "[[…]]" if "[[" in l and forme in l[l.find("[["):] else "Markdown" if "](" in l and forme in l[l.find("]("):] else "HTML href" if "href=" in l else "texte/autre"
                    lignes.append((ancien, label, k, os.path.relpath(f, R), i, l.strip()[:110].replace(ancien, "«ANCIEN»")))
print("fichiers scannés :", len(fich))
cnt = {}
for a in NOMS:
    n = [x for x in lignes if x[0] == a]; cnt[a] = n
    print(f"\n### {a} -> {NOMS[a]} : {len(n)} occurrence(s) dans {len(set(x[3] for x in n))} fichier(s)")
    for x in n: print(f"  {x[3]}:{x[4]}  [{x[2]} / {x[1]}]  {x[5]}")
w = csv.writer(open(os.path.dirname(os.path.abspath(__file__)) + "/renommage_liens_entrants.csv", "w", newline="", encoding="utf-8"))
w.writerow(["cible", "forme", "type de lien", "fichier", "ligne", "extrait"]); w.writerows(lignes)
