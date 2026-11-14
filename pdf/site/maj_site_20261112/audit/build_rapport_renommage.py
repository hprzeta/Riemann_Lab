#!/usr/bin/env python3
# Génère RAPPORT_RENOMMAGE_WIKI_<date>_<heure>.md et .pdf (D26 / D27) à partir des CSV du re-test et des commits wiki
import csv, os, re, json, html, subprocess, datetime, collections

AUD = os.path.dirname(os.path.abspath(__file__)); DOS = os.path.dirname(AUD)
R = os.path.expanduser("~/projet_zeta"); W = R + "/Riemann_Lab.wiki"
now = datetime.datetime.now(); STAMP = os.environ.get("STAMP_FORCE", now.strftime("%Y%m%d_%H%M"))
MD = f"{DOS}/RAPPORT_RENOMMAGE_WIKI_{STAMP}.md"; PDF = f"{DOS}/RAPPORT_RENOMMAGE_WIKI_{STAMP}.pdf"
ECH = os.environ.get("ECHANTILLON", "en attente de hprzeta")
def lire(n): return list(csv.DictReader(open(f"{AUD}/{n}", encoding="utf-8")))
apres, avant = lire("liens_statut_final.csv"), lire("liens_statut_final_AVANT_renommage.csv")
entrants = lire("renommage_liens_entrants_AVANT.csv")   # état avant renommage (commit 2bd4258)
absent = json.load(open(f"{AUD}/absent_scan.json")) if os.path.exists(f"{AUD}/absent_scan.json") else None
def run(a): return subprocess.run(a, capture_output=True, text=True).stdout
STAT = ["🟢", "🟡", "🔴", "⚪"]
ca, cb = collections.Counter(x["statut"] for x in avant), collections.Counter(x["statut"] for x in apres)
cle = lambda x: (x["source"], x["ligne"], x["texte"])
nouveaux_rouges = [x for x in apres if x["statut"] == "🔴" and not any(cle(y) == cle(x) and y["statut"] == "🔴" for y in avant)]
rouges = [x for x in apres if x["statut"] == "🔴"]
# lignes in/out des 2 commits wiki
rows = []
for sha, nom in [("8045f4e", "renommages + liens + Animations"), ("7e2da49", "pages de renvoi")]:
    date = run(["git", "-C", W, "log", "-1", "--format=%ci", sha]).strip()[:16]
    d = run(["git", "-C", W, "-c", "core.quotepath=off", "show", "-M", "-U0", "--format=", sha]).split("\n")
    f = None; i = 0
    while i < len(d):
        l = d[i]
        if l.startswith("+++ b/"): f = l[6:]
        m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", l)
        if m and f:
            o, on, n, nn = int(m[1]), (1 if m[2] is None else int(m[2])), int(m[3]), (1 if m[4] is None else int(m[4])); out, inn = [], []; i += 1
            while i < len(d) and not d[i].startswith("@@") and not d[i].startswith("diff "):
                (out if d[i].startswith("-") else inn if d[i].startswith("+") else []).append(d[i][1:]) if d[i][:1] in "+-" else None; i += 1
            rows.append([sha, f, "(aucune)" if on == 0 else o if on == 1 else f"{o}-{o+on-1}", "(supprimée)" if nn == 0 else n if nn == 1 else f"{n}-{n+nn-1}", date, " ⏎ ".join(out)[:140], " ⏎ ".join(inn)[:140]]); continue
        i += 1
NOMS = [("Etape-1-Calcul-des-zéros-non-triviaux", "Etape-1-Calcul-des-zeros-non-triviaux", 19), ("Interprétation-des-résultats-de-tests", "Interpretation-des-resultats-de-tests", 2),
        ("Partie-1-La-Théorie-Étape_1", "Partie-1-La-Theorie-Etape_1", 1), ("Projet-Zêta", "Projet-Zeta", 1), ("Tableau-Symboles-Mathématiques", "Tableau-Symboles-Mathematiques", 2)]
liens_maj = [x for x in entrants if x["type de lien"] != "texte/autre"]
def c(s, n=70): s = (s or "").replace("\n", " "); return s if len(s) <= n else s[: n - 1] + "…"
def e(s): return (s or "").replace("|", "\\|")
reste_anciens = [x for x in entrants if x["type de lien"] == "texte/autre"]

L = [f"# Rapport — Renommage des 5 pages wiki à accents (D26) et titres d'Animations sans symbole (D27) — {now.strftime('%d/%m/%Y %H:%M')}\n"]
L.append("> Exécution de `PROMPT_RENOMMAGE_WIKI_20261112_1949.md`. Choix de hprzeta à l'étape 2 : **« go correction avec renvoi »**. Aucun `--force`. Wiki : commits `8045f4e` et `7e2da49`, poussés (`2bd4258..7e2da49`). Aucun fichier du site, du `README.md` ni des scripts n'a eu besoin d'être modifié (0 lien entrant).\n")
L.append("## 1. Tableau de validation\n")
L.append("| Élément | Statut | Preuve |\n|---|---|---|")
L.append("| 5 pages renommées (`git mv`, historique conservé) | 🟢 | R051 à R099 ; `git log --follow` retrouve l'historique d'avant |")
L.append("| 5 pages de renvoi aux anciens noms | 🟢 | ouvertes dans Chrome : « Page renommée » + lien vers le nouveau nom |")
L.append(f"| 25 liens + 3 mentions mises à jour dans 17 pages | 🟢 | re-test : {cb['🟢']} 🟢, {cb['🟡']} 🟡, {cb['🔴']} 🔴 (avant renommage : {ca['🟢']}/{ca['🟡']}/{ca['🔴']}) |")
L.append(f"| Aucun nouveau 🔴 | {'🟢' if not nouveaux_rouges else '🔴'} | {len(nouveaux_rouges)} nouveau(x) 🔴 par rapport à l'état d'avant |")
L.append("| `Animations` : 13 titres sans symbole, 12 ancres du tableau | 🟢 | 12 ancres sur 12 présentes (cadre vert dans Chrome), 0 manquante |")
L.append(f"| `a.absent` (lien vers page inexistante) | {'🟢' if absent == {} else '🟡' if absent is None else '🔴'} | " + ("scan non terminé" if absent is None else f"{len(absent)} page(s) sur {len(json.load(open(AUD+'/pages_wiki.json')))} avec un lien absent" + (": " + json.dumps(absent, ensure_ascii=False) if absent else "")) + " |")
L.append("| Site, `README.md`, scripts, PDF publiés | 🟢 | 0 lien vers les 5 pages (321 fichiers et 117 PDF scannés) |")
L.append("| Mentions volontairement laissées | 🟡 | 17 historiques + `Guide-Ollama-Pratique` l.101 (citation RAG du 25/07) + `Guide-Git-GitHub` l.105 (exemple de commande) : voir §6 |\n")
L.append("## 2. Renommages\n")
L.append("| Ancien nom | Nouveau nom | Liens entrants (audit) | Renvoi à l'ancien nom |\n|---|---|---|---|")
for a, b, n in NOMS: L.append(f"| `{a}` | `{b}` | {n} | oui |")
L.append("\n`Projet-Zêta` était déjà une page de redirection vers `Home` : son renvoi pointe directement vers `Projet-Zeta` et `Home` (pas de double redirection).\n")
L.append("## 3. Liens mis à jour (état avant : fichier, ligne, forme du lien)\n")
L.append("| Cible | Forme | Fichier | Ligne | Nouveau lien |\n|---|---|---|---|---|")
nv = dict((a, b) for a, b, _ in NOMS)
for x in liens_maj: L.append(f"| `{x['cible'][:38]}` | {x['type de lien']} | {os.path.basename(x['fichier'])} | {x['ligne']} | `{nv[x['cible']]}` |")
L.append("\n`Animations.md` : 13 titres sans symbole (titre principal + 12 sections) ; 12 liens du tableau « Vue d'ensemble » mis à jour vers les ids sans symbole (par exemple `#animation_gamma--fonction-gamma`). Aucun lien extérieur vers ces ancres (site ni autres pages).\n")
L.append("## 4. Échantillon A / B / C de hprzeta\n")
L.append(f"{ECH}\n")
L.append("Remarque : le site ne contient aucun lien vers les 5 pages, donc l'échantillon « dont 2 depuis le site » du prompt est remplacé par des liens depuis la page `Home` du wiki.\n")
L.append("## 5. Lignes modifiées (page · ligne in · ligne out · date heure)\n")
L.append("| Commit | Page | Ligne in | Ligne out | Date heure |\n|---|---|---|---|---|")
for r in rows: L.append(f"| {r[0]} | {e(r[1][:60])} | {r[2]} | {r[3]} | {r[4]} |")
L.append("\nDans le PDF, les lignes supprimées sont en rouge et les ajoutées en vert.\n")
L.append("## 6. Mentions des anciens noms laissées (à décider)\n")
L.append("| Fichier | Ligne | Raison |\n|---|---|---|")
for x in reste_anciens:
    f = os.path.basename(x["fichier"]); rais = "citation RAG du 25/07/2026 (enregistrement)" if "Guide-Ollama" in f else "exemple de commande avec nom préfixé d'un emoji" if "Guide-Git" in f else "historique (journal, archive, rapport daté)"
    if f in ("Formules_zeta.md", "Plancher-Hardware-Architecture.md"): continue
    L.append(f"| {f} | {x['ligne']} | {rais} |")
L.append("\nScripts qui citent un ancien nom : aucun.\n")
L.append("## 7. Tests habituels\n")
L.append("| Test | Résultat |\n|---|---|")
L.append("| Chrome (onglet « Mise à jour site ») | 5 nouvelles pages ouvertes (0 `a.absent`, 0 « Unable to render ») ; 5 anciennes adresses : « Page renommée » avec lien vers le nouveau nom ; `Animations` : 12 ancres encadrées en vert |")
L.append("| `.katex-error` / formule brute | 0 / 0 sur les pages ouvertes (relevé sur les 3 pages longues) |")
L.append("| Secrets | audit des lignes ajoutées : aucune ligne suspecte |")
L.append("| 390 px | non mesuré : aucun changement du site |\n")
L.append("---")
L.append(f"*RAPPORT_RENOMMAGE_WIKI_{STAMP}.md · projet SITE ZETA · hprzeta · {now.strftime('%d/%m/%Y %H:%M')} · NBL lignes*")
txt = "\n".join(L) + "\n"; txt = txt.replace("NBL lignes", f"{txt.count(chr(10))} lignes"); open(MD, "w", encoding="utf-8").write(txt); print("MD", MD)

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
D = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DJ", D + "DejaVuSans.ttf")); pdfmetrics.registerFont(TTFont("DJB", D + "DejaVuSans-Bold.ttf")); pdfmetrics.registerFontFamily("DJ", normal="DJ", bold="DJB")
ST = {"h1": ParagraphStyle("h1", fontName="DJB", fontSize=14, spaceAfter=8), "h2": ParagraphStyle("h2", fontName="DJB", fontSize=11, spaceBefore=9, spaceAfter=4),
      "p": ParagraphStyle("p", fontName="DJ", fontSize=8.3, leading=10.5, spaceAfter=4), "c": ParagraphStyle("c", fontName="DJ", fontSize=6.9, leading=8.4)}
LBL = {"🟢": ("VERT", "#1a7f37"), "🟡": ("ORANGE", "#b45309"), "🔴": ("ROUGE", "#b91c1c"), "⚪": ("GRIS", "#6b7280")}
def P(s, st="c"): return Paragraph(html.escape(str(s)), ST[st])
def S_(s):
    for k, (n, col) in LBL.items(): s = s.replace(k, n)
    return s
def tab(data, widths):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#999")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                           ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)])); return t
def Hd(r): return [Paragraph(f"<b>{html.escape(h)}</b>", ST["c"]) for h in r]
doc = SimpleDocTemplate(PDF, pagesize=landscape(A4), leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24); Wd = landscape(A4)[0] - 48
S = [Paragraph(f"Renommage des 5 pages wiki (D26) et titres d'Animations (D27) — {now.strftime('%d/%m/%Y %H:%M')}", ST["h1"]),
     P("Choix de hprzeta : « go correction avec renvoi ». Wiki : commits 8045f4e et 7e2da49 (poussés). VERT = ok · ORANGE = à décider · ROUGE = problème.", "p")]
S += [Paragraph("1. Validation", ST["h2"])]
val = [Hd(["Élément", "Statut", "Preuve"])]
for line in L:
    if line.startswith("| ") and "Élément" not in line and line.count("|") >= 4:
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[1] in STAT: val.append([P(S_(cells[0]).replace("`", "")), P(S_(cells[1])), P(S_(cells[2]).replace("`", ""))])
S += [tab(val, [Wd * .38, Wd * .08, Wd * .54])]
S += [Paragraph("2. Renommages", ST["h2"]), tab([Hd(["Ancien nom", "Nouveau nom", "Liens entrants", "Renvoi"])] + [[P(a), P(b), P(n), P("oui")] for a, b, n in NOMS], [Wd * .35, Wd * .35, Wd * .15, Wd * .15])]
S += [Paragraph("3. Liens mis à jour", ST["h2"]), tab([Hd(["Cible", "Forme", "Fichier", "Ligne", "Nouveau lien"])] + [[P(x["cible"][:38]), P(x["type de lien"]), P(os.path.basename(x["fichier"])), P(x["ligne"]), P(nv[x["cible"]])] for x in liens_maj], [Wd * .26, Wd * .1, Wd * .26, Wd * .06, Wd * .32])]
S += [P("Animations.md : 13 titres sans symbole ; 12 ancres du tableau mises à jour.", "p"), Paragraph("4. Échantillon A / B / C", ST["h2"]), P(ECH, "p")]
S += [Paragraph("5. Lignes modifiées (rouge = supprimé, vert = ajouté)", ST["h2"])]
d = [Hd(["Commit", "Page", "Ligne in", "Ligne out", "Date heure", "Supprimé (in)", "Ajouté (out)"])]
for r in rows: d.append([P(r[0]), P(r[1][:55]), P(r[2]), P(r[3]), P(r[4]), Paragraph(f'<font color="#b91c1c">{html.escape(c(r[5],120))}</font>', ST["c"]), Paragraph(f'<font color="#1a7f37">{html.escape(c(r[6],120))}</font>', ST["c"])])
S += [tab(d, [Wd * .06, Wd * .17, Wd * .06, Wd * .06, Wd * .09, Wd * .28, Wd * .28])]
doc.build(S); print("PDF", PDF)
