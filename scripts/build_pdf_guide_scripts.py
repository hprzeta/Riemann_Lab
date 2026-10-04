#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_pdf_guide_scripts.py — Génère le PDF du guide « Mode d'emploi des scripts Cluster Zêta »
à partir de son .md, avec ReportLab (même aspect que l'édition du 19/09/2026).

Usage :
    python scripts/build_pdf_guide_scripts.py md/script/Guide_Scripts_Cluster_Zeta.md \
           pdf/script/Guide_Scripts_Cluster_Zeta_AAAAMMJJ.pdf

Sécurité : refuse d'écraser un PDF existant (l'ancien PDF reste intact).
Le guide est PRIVÉ (il contient des IP) : ne jamais le copier dans docs/ ni dans le wiki.

Auteur : hprzeta — Riemann_Lab · Version : 2026-10-04
"""
import os                                        # chemins et existence de fichiers
import re                                        # découpage du Markdown
import sys                                       # arguments de la ligne de commande
import textwrap                                  # coupe des longues lignes de code

from reportlab.lib import colors                 # couleurs du document
from reportlab.lib.enums import TA_CENTER        # alignement centré
from reportlab.lib.pagesizes import A4           # format A4
from reportlab.lib.styles import ParagraphStyle  # styles de paragraphe
from reportlab.lib.units import cm               # unités en centimètres
from reportlab.pdfbase import pdfmetrics         # enregistrement des polices
from reportlab.pdfbase.ttfonts import TTFont     # polices TrueType
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle, PageBreak,
                                Preformatted, HRFlowable, KeepTogether)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"   # polices DejaVu (accents et symboles)
# Enregistre les polices : texte, gras, italique, mono et mono gras
for nom, fichier in [("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"),
                     ("DV-I", "DejaVuSans-Oblique.ttf"), ("DV-BI", "DejaVuSans-BoldOblique.ttf"),
                     ("DVM", "DejaVuSansMono.ttf"), ("DVM-B", "DejaVuSansMono-Bold.ttf")]:
    pdfmetrics.registerFont(TTFont(nom, os.path.join(FONT_DIR, fichier)))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")

BLEU = colors.HexColor("#1f4e79")                # bleu des titres et des en-têtes de tableau
VERT = colors.HexColor("#1b6e4f")                # vert du sous-titre
GRIS = colors.HexColor("#666666")                # gris des textes secondaires
CODE_FOND = colors.HexColor("#f2f2f2")           # fond des blocs de commandes
CODE_TEXTE = colors.HexColor("#9c2f2f")          # texte des blocs de commandes
LIGNE_PAIRE = colors.HexColor("#eef3f9")         # lignes alternées des tableaux

# --- Styles --------------------------------------------------------------------------------------
S_TITRE = ParagraphStyle("titre", fontName="DV-B", fontSize=27, leading=32, textColor=BLEU, alignment=TA_CENTER)
S_SOUS = ParagraphStyle("sous", fontName="DV-B", fontSize=16, leading=20, textColor=VERT, alignment=TA_CENTER, spaceAfter=18)
S_INTRO = ParagraphStyle("intro", fontName="DV", fontSize=10, leading=14, alignment=TA_CENTER, spaceAfter=14)
S_DATE = ParagraphStyle("date", fontName="DV", fontSize=8.5, leading=11, textColor=GRIS, alignment=TA_CENTER, spaceAfter=14)
S_H2 = ParagraphStyle("h2", fontName="DV-B", fontSize=17, leading=21, textColor=BLEU, spaceBefore=14, spaceAfter=6, keepWithNext=1)
S_H3 = ParagraphStyle("h3", fontName="DV-B", fontSize=11.5, leading=15, textColor=BLEU, spaceBefore=10, spaceAfter=4, keepWithNext=1)
S_SCRIPT = ParagraphStyle("script", fontName="DVM-B", fontSize=11.5, leading=15, spaceBefore=8, spaceAfter=2, keepWithNext=1)
S_LABEL = ParagraphStyle("label", fontName="DV-B", fontSize=9.5, leading=13, spaceBefore=4, spaceAfter=2, keepWithNext=1)
S_TXT = ParagraphStyle("txt", fontName="DV", fontSize=9, leading=12.6, spaceAfter=3)
S_MACH = ParagraphStyle("mach", fontName="DV", fontSize=8, leading=11, textColor=GRIS, spaceAfter=2, keepWithNext=1)
S_CELL = ParagraphStyle("cell", fontName="DV", fontSize=7.6, leading=9.8)
S_CELLH = ParagraphStyle("cellh", fontName="DV-B", fontSize=7.8, leading=10, textColor=colors.white)
S_CODE = ParagraphStyle("code", fontName="DVM", fontSize=7.6, leading=9.6, textColor=CODE_TEXTE,
                        backColor=CODE_FOND, borderPadding=(4, 5, 4, 5), spaceBefore=2, spaceAfter=7, leftIndent=4)
S_PIED = ParagraphStyle("pied", fontName="DV-I", fontSize=8, leading=10, textColor=GRIS, spaceBefore=8)


def echappe(t):
    """Échappe les caractères réservés du XML de ReportLab."""
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(t):
    """Convertit le Markdown en ligne (gras, code, italique) en balises ReportLab."""
    t = echappe(t)                                                     # protège & < >
    t = re.sub(r"`([^`]+)`", r'<font name="DVM" size="8">\1</font>', t)  # code en ligne
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)                      # gras
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<i>\1</i>", t)   # italique
    return t


def nettoie_titre(t):
    """Retire les ** et les ` d'un titre."""
    return t.replace("**", "").replace("`", "").strip()


def tableau(lignes, largeur):
    """Construit un tableau ReportLab à partir de lignes Markdown (| a | b |)."""
    cellules = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lignes
                if not re.match(r"^\|\s*:?-{3,}", l.strip())]          # ignore la ligne de séparation
    n = len(cellules[0])                                               # nombre de colonnes
    # Poids de chaque colonne = longueur utile max (bornée) pour répartir la largeur
    poids = [max(min(len(re.sub(r"[`*]", "", row[i])), 48) for row in cellules if i < len(row)) + 6 for i in range(n)]
    larg = [largeur * p / sum(poids) for p in poids]
    data = []
    for i, row in enumerate(cellules):                                 # une ligne de Paragraph par ligne MD
        row = (row + [""] * n)[:n]
        data.append([Paragraph(inline(c.replace("<br>", " ")), S_CELLH if i == 0 else S_CELL) for c in row])
    t = Table(data, colWidths=larg, repeatRows=1)                      # en-tête répété sur chaque page
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), BLEU),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGNE_PAIRE]),
                           ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#c8c8c8")),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                           ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
    return [t, Spacer(1, 6)]


def bloc_code(lignes, largeur_car=92):
    """Bloc de commandes : coupe les lignes trop longues pour qu'aucune ne soit tronquée."""
    sortie = []
    for l in lignes:
        morceaux = textwrap.wrap(l, width=largeur_car, subsequent_indent="    ",
                                 break_long_words=True, replace_whitespace=False) or [""]
        sortie.extend(morceaux)
    return Preformatted("\n".join(sortie), S_CODE)


def pied_de_page(canvas, doc):
    """Dessine le pied de page : texte à gauche, numéro de page à droite."""
    canvas.saveState()
    canvas.setFont("DV", 7.5)
    canvas.setFillColor(GRIS)
    canvas.drawString(2 * cm, 1.2 * cm, "Mode d'emploi scripts — Cluster Zêta / Riemann_Lab — hprzeta")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"page {doc.page}")
    canvas.restoreState()


def construit(md_chemin, pdf_chemin):
    """Lit le .md et écrit le PDF."""
    texte = open(md_chemin, encoding="utf-8").read()
    texte = re.sub(r"<!--.*?-->", "", texte, flags=re.S)               # retire les commentaires HTML
    lignes = texte.splitlines()
    largeur = A4[0] - 4 * cm                                           # largeur utile du cadre
    doc = BaseDocTemplate(pdf_chemin, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                          topMargin=1.8 * cm, bottomMargin=2 * cm,
                          title="Mode d'emploi scripts - Cluster Zeta", author="hprzeta")
    doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(2 * cm, 2 * cm, largeur, A4[1] - 3.8 * cm, id="f")],
                                       onPage=pied_de_page)])
    flux, i, premiere_page = [], 0, True
    while i < len(lignes):
        l = lignes[i].rstrip()
        if not l.strip() or l.strip() == "---":                        # lignes vides et filets : ignorés
            i += 1
            continue
        if l.startswith("```"):                                        # bloc de code
            i += 1
            bloc = []
            while i < len(lignes) and not lignes[i].startswith("```"):
                bloc.append(lignes[i])
                i += 1
            flux.append(bloc_code(bloc))
            i += 1
            continue
        if l.startswith("|"):                                          # tableau
            bloc = []
            while i < len(lignes) and lignes[i].startswith("|"):
                bloc.append(lignes[i])
                i += 1
            flux.extend(tableau(bloc, largeur))
            continue
        if l.startswith("## "):                                        # titre de niveau 2
            titre = nettoie_titre(l[3:])
            if premiere_page and titre.startswith("Mode d'emploi"):    # page de couverture
                flux.append(Spacer(1, 3 * cm))
                flux.append(Paragraph("Mode d'emploi des scripts", S_TITRE))
                flux.append(Paragraph("Cluster Zêta — Riemann_Lab", S_SOUS))
                premiere_page = False
            elif re.match(r"^\d+\.\s", titre) or titre.startswith("Aide-mémoire"):   # section numérotée
                if flux and not isinstance(flux[-1], PageBreak) and titre.startswith("1."):
                    flux.append(PageBreak())                           # §1 commence sur une nouvelle page
                flux.append(Paragraph(echappe(titre), S_H2))
                flux.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#bbbbbb"), spaceAfter=4))
            elif titre.startswith("Comment le lancer"):                # libellé de fiche
                flux.append(Paragraph("Comment le lancer :", S_LABEL))
            else:                                                      # nom de script (fiche)
                if not (flux and isinstance(flux[-1], HRFlowable)):    # pas de double filet sous un titre de section
                    flux.append(HRFlowable(width="100%", thickness=0.3, color=colors.HexColor("#d0d0d0"), spaceBefore=6))
                flux.append(Paragraph(echappe(titre), S_SCRIPT))
            i += 1
            continue
        if l.startswith("### "):                                       # titre de niveau 3
            flux.append(Paragraph(echappe(nettoie_titre(l[4:])), S_H3))
            i += 1
            continue
        if l.startswith("- "):                                         # liste à puces
            flux.append(Paragraph("• " + inline(l[2:]), ParagraphStyle("li", parent=S_TXT, leftIndent=12, firstLineIndent=-8)))
            i += 1
            continue
        if l.startswith("*Mis à jour"):                                # pied du .md
            flux.append(Paragraph(inline(l), S_PIED))
            i += 1
            continue
        if l.startswith("Machine :"):                                  # ligne « Machine : ... »
            flux.append(Paragraph(inline(l), S_MACH))
        elif flux and len(flux) < 12 and "Aide-mémoire complet" in l:  # phrase d'accroche de la couverture
            flux.append(Paragraph(inline(l), S_INTRO))
        elif flux and len(flux) < 14 and l.startswith("hprzeta •"):    # ligne auteur/date de la couverture
            flux.append(Paragraph(inline(l), S_DATE))
        elif l.startswith("**À savoir"):                               # piège : marqueur carré
            flux.append(Paragraph("■ " + inline(l), S_TXT))
        else:                                                          # paragraphe courant
            flux.append(Paragraph(inline(l), S_TXT))
        i += 1
    doc.build(flux)


if __name__ == "__main__":
    if len(sys.argv) != 3:                                             # contrôle des arguments
        sys.exit("Usage : build_pdf_guide_scripts.py source.md sortie.pdf")
    src, out = sys.argv[1], sys.argv[2]
    if not os.path.isfile(src):                                        # le .md doit exister
        sys.exit(f"Source introuvable : {src}")
    if os.path.exists(out):                                            # jamais d'écrasement
        sys.exit(f"Refus d'écraser un fichier existant : {out}")
    construit(src, out)
    print(f"PDF généré : {out}")
