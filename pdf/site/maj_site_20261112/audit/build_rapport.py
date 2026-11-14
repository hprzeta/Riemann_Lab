#!/usr/bin/env python3
# Génère RAPPORT_AUDIT_COMPLET_<date>_<heure>.md et .pdf à partir des CSV de l'audit (lecture seule du dépôt)
import csv, os, sys, datetime, collections, html, re, json

AUD = os.path.dirname(os.path.abspath(__file__))
DOS = os.path.dirname(AUD)
now = datetime.datetime.now()
STAMP = os.environ.get("STAMP_FORCE", now.strftime("%Y%m%d_%H%M"))   # STAMP_FORCE : remplace la version du jour au lieu d'en créer une autre
MD = os.path.join(DOS, f"RAPPORT_AUDIT_COMPLET_{STAMP}.md")
PDF = os.path.join(DOS, f"RAPPORT_AUDIT_COMPLET_{STAMP}.pdf")
ECH2 = os.environ.get("ECHANTILLON2", "en attente de hprzeta")          # réponse A/B/C du 2e échantillon

def lire(n): return list(csv.DictReader(open(os.path.join(AUD, n), encoding="utf-8")))
apres, avant = lire("liens_statut_final.csv"), lire("liens_statut_final_AVANT.csv")
inout, risques = lire("lignes_in_out.csv"), lire("noms_a_risque.csv")
absent = json.load(open(os.path.join(AUD, "absent_scan.json"))) if os.path.exists(os.path.join(AUD, "absent_scan.json")) else None

def cat(s):
    return "wiki" if s.startswith("Riemann_Lab.wiki") else "site (docs/*.html)" if s.endswith(".html") else "docs/*.md" if s.startswith("docs/") else "README"
ORDRE = ["site (docs/*.html)", "wiki", "docs/*.md", "README"]
STAT = ["🟢", "🟡", "🔴", "⚪"]
def comptes(rows):
    t = {c: collections.Counter() for c in ORDRE}
    for x in rows: t[cat(x["source"])][x["statut"]] += 1
    return t
ta, tb = comptes(avant), comptes(apres)

# liens corrigés = 🔴/🟡 avant et 🟢 après (clé : source, ligne, texte)
cle = lambda x: (x["source"], x["ligne"], x["texte"])
apres_par = {cle(x): x for x in apres}
corriges = [(x, apres_par.get(cle(x))) for x in avant if x["statut"] in ("🔴", "🟡") and apres_par.get(cle(x)) and apres_par[cle(x)]["statut"] == "🟢"]
restants = [x for x in apres if x["statut"] in ("🔴", "🟡")]

def court(s, n=70): s = (s or "").replace("\n", " "); return s if len(s) <= n else s[: n - 1] + "…"
def md_cell(s): return (s or "").replace("|", "\\|")

# ----------------------------- Markdown -----------------------------
L = []
L.append(f"# Rapport — Audit complet des liens du site et du wiki — {now.strftime('%d/%m/%Y')} {now.strftime('%H:%M')}\n")
L.append("> Exécution de `PROMPT_AUDIT_COMPLET_LIENS_20261112_1812.md` (étape 0 adaptée : pas de zip, prompt fourni seul). Aucun `--force`, aucun renommage. STOP respectés : « go archive », « go correction », « go commit wiki », « go push wiki », « go commit site », « go push », « go commit archive ».\n")
L.append("## 1. Synthèse\n")
L.append(f"Liens inventoriés : **{len(apres)}** (avant corrections : {len(avant)}). Statuts : 🟢 200 et cible correcte · 🟡 marche mais à améliorer · 🔴 cassé · ⚪ faux positif d'extraction (exemple de syntaxe ou adresse citée dans le texte, pas un lien).\n")
L.append("| Source | 🟢 avant | 🟡 avant | 🔴 avant | ⚪ avant | 🟢 après | 🟡 après | 🔴 après | ⚪ après |\n|---|---|---|---|---|---|---|---|---|")
for c in ORDRE + ["TOTAL"]:
    a = sum((ta[k] for k in ORDRE), collections.Counter()) if c == "TOTAL" else ta[c]
    b = sum((tb[k] for k in ORDRE), collections.Counter()) if c == "TOTAL" else tb[c]
    L.append(f"| {c} | " + " | ".join(str(a[s]) for s in STAT) + " | " + " | ".join(str(b[s]) for s in STAT) + " |")
L.append("")
L.append(f"Liens passés de 🔴/🟡 à 🟢 par les corrections : **{len(corriges)}**. Liens encore 🔴/🟡 : **{len(restants)}** (voir §2). Site : accueil + 12 animations et wiki : 84 pages sur 84 parcourus dans Claude in Chrome (onglet « Audit liens »).\n")
L.append("## 2. Tableau complet\n")
L.append("Le tableau complet (une ligne par lien : `source | ligne | texte | URL | type | HTTP | ancre | statut | action`) est dans `audit/liens_statut_final.csv` (plus de 300 lignes). Ci-dessous : tous les 🔴 et 🟡 restants, puis le résumé des 🟢.\n")
L.append("### 2.1 Liens encore 🔴 ou 🟡 après corrections\n")
L.append("| Source | Ligne | Texte | URL | HTTP | Statut | Action |\n|---|---|---|---|---|---|---|")
for x in restants:
    L.append(f"| {md_cell(os.path.basename(x['source']))} | {x['ligne']} | {md_cell(court(x['texte'],30))} | {md_cell(court(x['url'],70))} | {md_cell(court(x['http'],25))} | {x['statut']} | {md_cell(court(x['action'],70))} |")
L.append("")
L.append("### 2.2 Liens corrigés (🔴/🟡 avant → 🟢 après)\n")
L.append("| Source | Ligne | URL avant | URL après |\n|---|---|---|---|")
for a, b in corriges:
    L.append(f"| {md_cell(os.path.basename(a['source']))} | {a['ligne']} | {md_cell(court(a['url'],60))} | {md_cell(court(b['url'],60))} |")
L.append("")
L.append("### 2.3 Résumé des 🟢\n")
for c in ORDRE:
    L.append(f"- {c} : {tb[c]['🟢']} liens 🟢 sur {sum(tb[c].values())}.")
L.append("")
L.append("### 2.4 Contrôle `a.absent` du wiki (liens `[[…]]` vers une page inexistante)\n")
if absent is None: L.append("Contrôle non terminé au moment de la rédaction.\n")
else:
    L.append(f"Pages wiki avec au moins un lien `a.absent` : **{len(absent)}** sur 84. " + (json.dumps(absent, ensure_ascii=False) if absent else "Aucune.") + "\n")
L.append("## 3. Échantillon A / B / C de hprzeta\n")
L.append("| Échantillon | Liens | Réponse |\n|---|---|---|")
L.append("| 1 (avant corrections) | 3 « Lire → » (chapitres 1, 7, 14) + 7 liens à ancre (`Formules_zeta#…`, `Bibliotheques#…`) | « c » → interprété : **C** pour les 10 (au bon endroit) |")
L.append(f"| 2 (après corrections) | ancres de `Animations`, sommaire de `Phase-C`, liens `Étape 2/3` de `Home` | {ECH2} |\n")
L.append("## 4. Scripts archivés\n")
L.append("| Script | Écrit quoi | Encore appelé ? | Dépassé ? | Décision |\n|---|---|---|---|---|")
L.append("| `cours/make_wiki_page.py` | page unique `Formation-Zeta-HR.md` (ancres `#chN`) | non (ni cron, ni minuterie, ni hook) | oui (le cours est en index + 14 pages `ChNN`) | **archivé** → `archive/scripts_obsoletes_20261112/` (commit `001f3b2`, 4 branches) |")
L.append("| `scripts/archiver_fichiers_obsoletes_v2.sh` | cite `docs/index.html` dans un message | non | non | gardé |")
L.append("| `scripts/backup_cluster_map.sh` | cite `Riemann_Lab.wiki/` dans un SVG | — | non | gardé |")
L.append("| `scripts/push_phase0_complete.sh` | pousse le wiki | — | non | gardé |")
L.append("| `scripts/rag_ingest_corpus.py` | lit `Riemann_Lab.wiki/*.md` | oui (`rag_query.py`, `zeta_rag.sh`) | non | gardé |\n")
L.append("## 5. Noms à risque (aucun renommage)\n")
pages = [r for r in risques if r["type"] == "page wiki"]; ancres = [r for r in risques if r["type"] == "ancre"]; fich = [r for r in risques if r["type"] == "fichier publié"]
L.append(f"Pages wiki : {len(pages)} · ancres à risque utilisées dans des liens : {len(ancres)} · fichiers publiés (`docs/`, `cours/`, `pdf/`) : {len(fich)}. Détail complet : `audit/noms_a_risque.csv`.\n")
L.append("| Nom actuel | Caractères à risque | Forme encodée | Liens entrants | Nom ASCII proposé |\n|---|---|---|---|---|")
for r in pages:
    L.append(f"| {md_cell(r['nom actuel'])} | {r['caractères à risque']} | {md_cell(r['forme encodée'])} | {r['liens entrants']} | {md_cell(r['nom ASCII proposé'])} |")
L.append("\nLe renommage fera l'objet d'un prompt séparé (le wiki GitHub n'a pas de redirection automatique).\n")
L.append("## 6. Lignes modifiées (page · ligne in · ligne out · date heure)\n")
L.append("| Dépôt | Page | Ligne in | Ligne out | Date heure |\n|---|---|---|---|---|")
for r in inout:
    L.append(f"| {r['depot']} | {md_cell(r['page'])} | {r['ligne_in']} | {r['ligne_out']} | {r['date_heure']} |")
L.append("\nCommits : wiki `2bd4258` · site `05217b8` (IA ; main `4165de3`, C `773bdff`, Test `3aa3c23`) · archive `001f3b2` (IA ; main `33f3ada`, C `ff9dc8b`, Test `cd9f2b8`). Dans le PDF, les lignes supprimées sont en rouge et les lignes ajoutées en vert.\n")
L.append("## 7. Tests habituels\n")
L.append("| Test | Résultat |\n|---|---|")
L.append("| Console (site) | accueil : 0 erreur ; 12 animations parcourues, 0 erreur KaTeX, 0 image cassée. Console non relevée page par page sur les animations. |")
L.append("| `.katex-error` / formules brutes | site : 0 ; wiki : 0 « Unable to render » sur 84 pages ; formules brutes `$$` relevées sur l'accueil du site seulement (0) |")
L.append("| 390 px | accueil du site mesuré dans un cadre de 390 px : largeur utile 376 px, pas de débordement. La fenêtre Chrome n'a pas pu être redimensionnée (viewport resté à 1236 px) ; autres pages non mesurées à 390 px. |")
L.append("| Secrets | audit des lignes ajoutées (IP, MAC, clés, tokens, e-mails) : aucune ligne suspecte sur les 3 commits |")
L.append("| Pieds de page | wiki : 7 pages à la date du jour avec `wc -l` ; site : pied de l'accueil au 12/11/2026 |\n")
L.append("## 8. Ce qui reste non corrigé ou à décider\n")
L.append("- `STACK.md` : lien archive.org de Titchmarsh mort ; aucune édition équivalente vérifiée (l'item trouvé est le tract de 1930).")
L.append("- `README.md` : issues et Kanban GitHub (404 sans connexion) : à tester dans Chrome connecté.")
L.append("- DOI Odlyzko-Schönhage corrigé (Crossref) mais l'éditeur répond 403 aux robots : à confirmer dans Chrome.")
L.append("- Code tiers Plotly dans `docs/images/T10Demo/zeta_demovisualisation.html` : non modifié.")
L.append("- Le choix `Home` Étape 2 → `Animations`, Étape 3 → `Guide-Ollama-Pratique`, Étape 4 sans lien a été fait par Claude (convention de `Structure-Projet-Complet`) : modifiable sur demande.\n")
L.append("---")
L.append(f"*RAPPORT_AUDIT_COMPLET_{STAMP}.md · projet SITE ZETA · hprzeta · {now.strftime('%d/%m/%Y %H:%M')} · NBL lignes*")
txt = "\n".join(L) + "\n"
n = txt.count("\n") ; txt = txt.replace("NBL lignes", f"{n} lignes")
open(MD, "w", encoding="utf-8").write(txt)
print("MD", MD, n, "lignes")

# ----------------------------- PDF (ReportLab) -----------------------------
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
D = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DJ", D + "DejaVuSans.ttf")); pdfmetrics.registerFont(TTFont("DJB", D + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily("DJ", normal="DJ", bold="DJB")
ST = {"h1": ParagraphStyle("h1", fontName="DJB", fontSize=15, spaceAfter=8), "h2": ParagraphStyle("h2", fontName="DJB", fontSize=12, spaceBefore=10, spaceAfter=5),
      "p": ParagraphStyle("p", fontName="DJ", fontSize=8.5, leading=11, spaceAfter=4), "c": ParagraphStyle("c", fontName="DJ", fontSize=7, leading=8.6)}
LBL = {"🟢": ("VERT", "#1a7f37"), "🟡": ("ORANGE", "#b45309"), "🔴": ("ROUGE", "#b91c1c"), "⚪": ("GRIS", "#6b7280")}
def P(s, st="c"): return Paragraph(html.escape(str(s)).replace("\n", "<br/>"), ST[st])
def lab(x): n, c = LBL[x]; return Paragraph(f'<font color="{c}"><b>{n}</b></font>', ST["c"])
def tab(data, widths, head=True, extra=None):
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    s = [("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#999999")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
         ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]
    t.setStyle(TableStyle(s + (extra or []))); return t
def Hd(row): return [Paragraph(f"<b>{html.escape(h)}</b>", ST["c"]) for h in row]
doc = SimpleDocTemplate(PDF, pagesize=landscape(A4), leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24, title=f"Audit complet des liens {STAMP}")
W = landscape(A4)[0] - 48
S = []
S += [Paragraph(f"Audit complet des liens du site et du wiki — {now.strftime('%d/%m/%Y %H:%M')}", ST["h1"]),
      P("Exécution de PROMPT_AUDIT_COMPLET_LIENS_20261112_1812.md (étape 0 adaptée : pas de zip). Aucun --force, aucun renommage. VERT = 200 et cible correcte · ORANGE = à améliorer · ROUGE = cassé · GRIS = faux positif d'extraction (pas un lien).", "p")]
S += [Paragraph("1. Synthèse", ST["h2"])]
d = [Hd(["Source", "VERT av.", "ORANGE av.", "ROUGE av.", "GRIS av.", "VERT ap.", "ORANGE ap.", "ROUGE ap.", "GRIS ap."])]
for c in ORDRE + ["TOTAL"]:
    a = sum((ta[k] for k in ORDRE), collections.Counter()) if c == "TOTAL" else ta[c]; b = sum((tb[k] for k in ORDRE), collections.Counter()) if c == "TOTAL" else tb[c]
    d.append([P(c)] + [P(a[s]) for s in STAT] + [P(b[s]) for s in STAT])
S += [tab(d, [W * 0.2] + [W * 0.1] * 8), Spacer(1, 4),
      P(f"Liens inventoriés : {len(apres)} (avant : {len(avant)}). Passés de rouge/orange à vert : {len(corriges)}. Encore rouge/orange : {len(restants)}. Parcours Chrome : accueil + 12 animations ; wiki 84/84 pages.", "p")]
S += [Paragraph("2. Liens encore rouges ou orange", ST["h2"])]
d = [Hd(["Source", "Ligne", "Texte", "URL", "HTTP", "Statut", "Action"])]
for x in restants: d.append([P(os.path.basename(x["source"])), P(x["ligne"]), P(court(x["texte"], 30)), P(court(x["url"], 80)), P(court(x["http"], 28)), lab(x["statut"]), P(court(x["action"], 80))])
S += [tab(d, [W * .15, W * .05, W * .12, W * .30, W * .1, W * .07, W * .21])]
S += [P("Tableau complet (une ligne par lien) : audit/liens_statut_final.csv.", "p")]
S += [Paragraph("2.2 Liens corrigés", ST["h2"])]
d = [Hd(["Source", "Ligne", "URL avant", "URL après"])]
for a, b in corriges: d.append([P(os.path.basename(a["source"])), P(a["ligne"]), P(court(a["url"], 75)), P(court(b["url"], 75))])
S += [tab(d, [W * .18, W * .06, W * .38, W * .38])]
S += [Paragraph("2.4 Contrôle a.absent du wiki", ST["h2"]), P("Non terminé." if absent is None else f"Pages avec lien vers page inexistante : {len(absent)} sur 84. " + (json.dumps(absent, ensure_ascii=False) if absent else "Aucune."), "p")]
S += [Paragraph("3. Échantillon A / B / C", ST["h2"])]
S += [tab([Hd(["Échantillon", "Liens", "Réponse"]), [P("1 (avant)"), P("3 « Lire → » (ch. 1, 7, 14) + 7 liens à ancre"), P("« c » : interprété C pour les 10")],
           [P("2 (après)"), P("ancres Animations, sommaire Phase-C, liens Étape 2/3 de Home"), P(ECH2)]], [W * .15, W * .55, W * .30])]
S += [Paragraph("4. Scripts archivés", ST["h2"]),
      tab([Hd(["Script", "Écrit quoi", "Encore appelé ?", "Dépassé ?", "Décision"]),
           [P("cours/make_wiki_page.py"), P("page unique Formation-Zeta-HR.md (#chN)"), P("non"), P("oui"), P("archivé → archive/scripts_obsoletes_20261112/ (001f3b2, 4 branches)")],
           [P("scripts/archiver_fichiers_obsoletes_v2.sh"), P("cite docs/index.html"), P("non"), P("non"), P("gardé")],
           [P("scripts/backup_cluster_map.sh"), P("cite le wiki dans un SVG"), P("—"), P("non"), P("gardé")],
           [P("scripts/push_phase0_complete.sh"), P("pousse le wiki"), P("—"), P("non"), P("gardé")],
           [P("scripts/rag_ingest_corpus.py"), P("lit le wiki"), P("oui (rag_query.py, zeta_rag.sh)"), P("non"), P("gardé")]], [W * .28, W * .22, W * .17, W * .08, W * .25])]
S += [Paragraph("5. Noms à risque (aucun renommage)", ST["h2"]), P(f"Pages wiki : {len(pages)} · ancres : {len(ancres)} · fichiers publiés : {len(fich)}. Détail : audit/noms_a_risque.csv.", "p")]
d = [Hd(["Nom actuel", "Risque", "Forme encodée", "Liens entrants", "Nom ASCII proposé"])]
for r in pages: d.append([P(r["nom actuel"]), P(r["caractères à risque"]), P(r["forme encodée"]), P(r["liens entrants"]), P(r["nom ASCII proposé"])])
S += [tab(d, [W * .27, W * .08, W * .30, W * .07, W * .28])]
S += [PageBreak(), Paragraph("6. Lignes modifiées (rouge = supprimé, vert = ajouté)", ST["h2"])]
d = [Hd(["Dépôt", "Page", "Ligne in", "Ligne out", "Date heure", "Supprimé (in)", "Ajouté (out)"])]
for r in inout:
    d.append([P(r["depot"]), P(r["page"]), P(r["ligne_in"]), P(r["ligne_out"]), P(r["date_heure"]),
              Paragraph(f'<font color="#b91c1c">{html.escape(court(r["supprime"], 150))}</font>', ST["c"]),
              Paragraph(f'<font color="#1a7f37">{html.escape(court(r["ajoute"], 150))}</font>', ST["c"])])
S += [tab(d, [W * .06, W * .15, W * .06, W * .06, W * .09, W * .29, W * .29])]
S += [P("Commits : wiki 2bd4258 · site 05217b8 (main 4165de3, C 773bdff, Test 3aa3c23) · archive 001f3b2 (main 33f3ada, C ff9dc8b, Test cd9f2b8).", "p")]
S += [Paragraph("7. Tests habituels", ST["h2"]),
      tab([Hd(["Test", "Résultat"]),
           [P("Console / KaTeX (site)"), P("accueil : 0 erreur console ; 12 animations : 0 .katex-error, 0 image cassée ; console non relevée page par page")],
           [P("Wiki"), P("84 pages parcourues : 0 « Unable to render », 0 page 404")],
           [P("390 px"), P("accueil mesuré dans un cadre de 390 px : 376 px utiles, pas de débordement ; fenêtre non redimensionnable (viewport resté à 1236 px) ; autres pages non mesurées")],
           [P("Secrets"), P("audit des lignes ajoutées : aucune ligne suspecte (3 commits)")]], [W * .2, W * .8])]
S += [Paragraph("8. Reste à décider", ST["h2"])]
for t in ["STACK.md : lien archive.org Titchmarsh mort, aucune édition équivalente vérifiée.", "README.md : issues et Kanban demandent une connexion GitHub (à tester dans Chrome connecté).",
          "DOI Odlyzko-Schönhage corrigé (Crossref), 403 anti-robot à confirmer dans Chrome.", "Code tiers Plotly (zeta_demovisualisation.html) : non modifié.",
          "Home : Étape 2 → Animations, Étape 3 → Guide-Ollama-Pratique, Étape 4 sans lien (choix de Claude, modifiable)."]:
    S.append(P("• " + t, "p"))
doc.build(S); print("PDF", PDF)
