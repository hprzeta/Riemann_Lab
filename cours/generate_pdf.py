#!/usr/bin/env python3
"""Génère Cours_Zeta_HR_complet.pdf à partir de Cours_Zeta_HR_complet.md (ReportLab).
Usage: python3 generate_pdf.py
"""
import os
import re
from datetime import date

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image, Table,
    TableStyle, NextPageTemplate, PageBreak, KeepTogether, FrameBreak,
)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(HERE, "Cours_Zeta_HR_complet.md")
PDF_PATH = os.path.join(HERE, "Cours_Zeta_HR_complet.pdf")
FIG_DIR = os.path.join(HERE, "figures")

AUTHOR = "hprzeta"
REPO_URL = "github.com/hprzeta/Riemann_Lab"
TITLE = "Cours ζ & Hypothèse de Riemann"
MAJ_DATE = "13 septembre 2026"

# ---------------------------------------------------------------- polices --
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-It", os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-BoldIt", os.path.join(FONT_DIR, "DejaVuSans-BoldOblique.ttf")))
pdfmetrics.registerFont(TTFont("DejaVuMono", os.path.join(FONT_DIR, "DejaVuSansMono.ttf")))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold",
                               italic="DejaVu-It", boldItalic="DejaVu-BoldIt")

# ------------------------------------------------------- conversion LaTeX --
LATEX_CMD = {
    "sigma": "σ", "Sigma": "Σ", "zeta": "ζ", "xi": "ξ",
    "Xi": "Ξ", "Gamma": "Γ", "gamma": "γ", "pi": "π",
    "theta": "θ", "Theta": "Θ", "infty": "∞", "rho": "ρ",
    "eta": "η", "delta": "δ", "Delta": "Δ", "alpha": "α",
    "beta": "β", "varepsilon": "ε", "epsilon": "ε",
    "psi": "ψ", "Psi": "Ψ", "phi": "φ", "Phi": "Φ",
    "chi": "χ", "mu": "μ", "nu": "ν", "lambda": "λ",
    "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥",
    "ne": "≠", "neq": "≠", "to": "→", "times": "×",
    "cdot": "·", "cdots": "⋯", "ldots": "…", "dots": "…",
    "pm": "±", "mp": "∓", "forall": "∀", "exists": "∃",
    "in": "∈", "notin": "∉", "subset": "⊂", "emptyset": "∅",
    "wedge": "∧", "vee": "∨", "Rightarrow": "⇒",
    "Leftrightarrow": "⇔", "iff": "⇔", "mapsto": "↦",
    "partial": "∂", "checkmark": "✓", "sim": "∼",
    "approx": "≈", "equiv": "≡", "propto": "∝",
    "int": "∫", "oint": "∮", "sum": "Σ", "prod": "Π",
    "lim": "lim", "log": "log", "ln": "ln", "arg": "arg", "exp": "exp",
    "Res": "Rés", "sin": "sin", "cos": "cos", "tan": "tan",
    "quad": "  ", "qquad": "    ", "!": "", ",": " ", ";": " ", " ": " ",
    "left": "", "right": "", "displaystyle": "", "big": "", "Big": "",
    "bigg": "", "Bigg": "", "dagger": "†",
    "Longrightarrow": "⟹", "longrightarrow": "⟶", "leftrightarrow": "↔",
    "cong": "≅", "bigoplus": "⊕", "setminus": "∖", "cup": "∪", "cap": "∩",
    "cross": "×",
}
GREEK_CACHE_KEYS = sorted(LATEX_CMD.keys(), key=len, reverse=True)

MATHBB = {"C": "ℂ", "R": "ℝ", "N": "ℕ", "Z": "ℤ", "Q": "ℚ"}


def _find_matching_brace(s, start):
    """s[start] == '{' ; renvoie l'indice de la '}' correspondante."""
    depth = 0
    for i in range(start, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(s) - 1


def _extract_arg(s, i):
    """i pointe juste après une commande ; extrait le prochain groupe {...}, la
    prochaine commande \\xxx, ou le prochain caractère isolé."""
    while i < len(s) and s[i] == " ":
        i += 1
    if i < len(s) and s[i] == "{":
        j = _find_matching_brace(s, i)
        return s[i + 1:j], j + 1
    if i < len(s) and s[i] == "\\":
        m = re.match(r"\\[A-Za-z]+", s[i:])
        if m:
            return m.group(0), i + len(m.group(0))
        if i + 1 < len(s):
            return s[i:i + 2], i + 2
    if i < len(s):
        return s[i], i + 1
    return "", i


def _replace_frac(s):
    out = []
    i = 0
    pattern = re.compile(r"\\(?:d|t)?frac")
    while True:
        m = pattern.search(s, i)
        if not m:
            out.append(s[i:])
            break
        out.append(s[i:m.start()])
        num, j = _extract_arg(s, m.end())
        den, j = _extract_arg(s, j)
        num_c = latex_to_markup(num)
        den_c = latex_to_markup(den)
        out.append(f"({num_c})/({den_c})")
        i = j
    return "".join(out)


def _replace_sqrt(s):
    out = []
    i = 0
    pattern = re.compile(r"\\sqrt")
    while True:
        m = pattern.search(s, i)
        if not m:
            out.append(s[i:])
            break
        out.append(s[i:m.start()])
        arg, j = _extract_arg(s, m.end())
        out.append("√(" + latex_to_markup(arg) + ")")
        i = j
    return "".join(out)


def _replace_wrapped(s, cmdname, fmt):
    out = []
    i = 0
    pattern = re.compile(r"\\" + cmdname + r"\b")
    while True:
        m = pattern.search(s, i)
        if not m:
            out.append(s[i:])
            break
        out.append(s[i:m.start()])
        arg, j = _extract_arg(s, m.end())
        out.append(fmt(latex_to_markup(arg)))
        i = j
    return "".join(out)


def _replace_underbrace(s):
    out = []
    i = 0
    pattern = re.compile(r"\\(?:under|over)brace")
    while True:
        m = pattern.search(s, i)
        if not m:
            out.append(s[i:])
            break
        out.append(s[i:m.start()])
        content, j = _extract_arg(s, m.end())
        k = j
        while k < len(s) and s[k] == " ":
            k += 1
        label = ""
        if k < len(s) and s[k] == "_":
            label, k = _extract_arg(s, k + 1)
            j = k
        content_c = latex_to_markup(content)
        if label:
            out.append(f"{content_c} ({latex_to_markup(label)})")
        else:
            out.append(content_c)
        i = j
    return "".join(out)


def _replace_supersub(s):
    # ^{...} et _{...} -> <super>/<sub> ; ^x et _x (1 caractere) idem
    out = []
    i = 0
    pattern = re.compile(r"[\^_]")
    while True:
        m = pattern.search(s, i)
        if not m:
            out.append(s[i:])
            break
        out.append(s[i:m.start()])
        tag = "super" if m.group(0) == "^" else "sub"
        arg, j = _extract_arg(s, m.end())
        content = latex_to_markup(arg)
        if content.strip():
            out.append(f"<{tag}>{content}</{tag}>")
        i = j
    return "".join(out)


def latex_to_markup(text):
    """Convertit un fragment LaTeX (contenu entre $...$ ou $$...$$) en markup ReportLab."""
    s = text
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = s.replace("\\%", "%").replace("\\_", "_")
    s = re.sub(r"\\[,;!]", " ", s)
    s = re.sub(r"\\ ", " ", s)
    s = _replace_frac(s)
    s = _replace_sqrt(s)
    s = _replace_underbrace(s)
    s = _replace_wrapped(s, "mathrm", lambda c: c)
    s = _replace_wrapped(s, "text", lambda c: c)
    s = _replace_wrapped(s, "mathcal", lambda c: c)
    s = _replace_wrapped(s, "pmod", lambda c: f"(mod {c})")
    s = _replace_wrapped(s, "overline", lambda c: c + "̅" if len(c) == 1 else c + "̄")
    s = _replace_wrapped(s, "bar", lambda c: c + "̅" if len(c) == 1 else c + "̄")

    def mathbb_fmt(c):
        return MATHBB.get(c.strip(), c)
    s = _replace_wrapped(s, "mathbb", mathbb_fmt)

    s = _replace_supersub(s)

    # commandes simples (mots) -> dictionnaire, plus longues d'abord
    def cmd_repl(m):
        name = m.group(1)
        return LATEX_CMD.get(name, name)
    s = re.sub(r"\\([A-Za-z]+)", cmd_repl, s)
    # backslash + caractere isole restant (espacements \, \; \! deja geres, fallback)
    s = re.sub(r"\\(.)", r"\1", s)
    s = s.replace("{", "").replace("}", "")
    s = re.sub(r"  +", " ", s)
    return s.strip()


# ----------------------------------------------------- markdown -> markup --
def escape_xml(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline_markdown(text):
    """Convertit une ligne de markdown (hors blocs) en markup ReportLab, formules $..$ / $$..$$ incluses.

    Stratégie : on extrait d'abord les segments de maths ($$..$$ / $..$) et on les
    remplace par des jetons opaques (caractères de contrôle) afin que **gras** /
    *italique* puissent porter sur toute la ligne, y compris à travers une formule
    inline, sans que la regex ne s'y perde.
    """
    math_store = []
    i, n = 0, len(text)
    buf = []
    while i < n:
        if text[i:i + 2] == "$$":
            j = text.find("$$", i + 2)
            if j == -1:
                buf.append(text[i:]); i = n; continue
            math_store.append(latex_to_markup(text[i + 2:j]))
            buf.append(f"\x01{len(math_store) - 1}\x02")
            i = j + 2
        elif text[i] == "$":
            j = text.find("$", i + 1)
            if j == -1:
                buf.append(text[i:]); i = n; continue
            math_store.append(latex_to_markup(text[i + 1:j]))
            buf.append(f"\x01{len(math_store) - 1}\x02")
            i = j + 1
        else:
            buf.append(text[i]); i += 1
    t = escape_xml("".join(buf))

    # code `...` -> jeton opaque (protege le contenu, ex. underscores/asterisques, du gras/italique)
    def _store_code(m):
        math_store.append(f'<font face="DejaVuMono" size="9">{m.group(1)}</font>')
        return f"\x01{len(math_store) - 1}\x02"
    t = re.sub(r"`([^`]+)`", _store_code, t)

    # liens [texte](url)
    t = re.sub(r"\[([^\]]+)\]\((https?[^)]+)\)",
                r'<link href="\2" color="#1a4f8a"><u>\1</u></link>', t)
    # gras/italique (peuvent maintenant enjamber une formule, remplacee par un jeton opaque)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)([^*]+?)\*(?!\*)", r"<i>\1</i>", t)

    def _restore(m):
        return math_store[int(m.group(1))]
    t = re.sub(r"\x01(\d+)\x02", _restore, t)
    return t


# ------------------------------------------------------------- styles ------
styles = {}
styles["CoverTitle"] = ParagraphStyle("CoverTitle", fontName="DejaVu-Bold", fontSize=28,
                                       leading=34, alignment=TA_CENTER, textColor=colors.HexColor("#0d2647"))
styles["CoverSub"] = ParagraphStyle("CoverSub", fontName="DejaVu", fontSize=14, leading=20,
                                     alignment=TA_CENTER, textColor=colors.HexColor("#333333"))
styles["CoverMeta"] = ParagraphStyle("CoverMeta", fontName="DejaVu", fontSize=11, leading=16,
                                      alignment=TA_CENTER, textColor=colors.HexColor("#555555"))
styles["TOCTitle"] = ParagraphStyle("TOCTitle", fontName="DejaVu-Bold", fontSize=18,
                                     leading=24, spaceAfter=14, textColor=colors.HexColor("#0d2647"))
styles["ChapterTitle"] = ParagraphStyle("ChapterTitle", fontName="DejaVu-Bold", fontSize=18,
                                         leading=23, spaceBefore=0, spaceAfter=10,
                                         textColor=colors.white, backColor=colors.HexColor("#0d2647"),
                                         borderPadding=(8, 8, 8, 8))
styles["SourceNote"] = ParagraphStyle("SourceNote", fontName="DejaVu-It", fontSize=9, leading=12,
                                       spaceAfter=8, textColor=colors.HexColor("#555555"))
styles["FormuleTitle"] = ParagraphStyle("FormuleTitle", fontName="DejaVu-Bold", fontSize=12,
                                         leading=15, spaceBefore=6, spaceAfter=4,
                                         textColor=colors.HexColor("#0d2647"))
styles["Formule"] = ParagraphStyle("Formule", fontName="DejaVuMono", fontSize=11, leading=16,
                                    alignment=TA_CENTER, spaceBefore=4, spaceAfter=8,
                                    backColor=colors.HexColor("#f0f0f5"), borderPadding=(6, 6, 6, 6))
LEVEL_COLORS = {
    "🟢": ("#1a6b34", "#e7f5ea"),  # vert debutant
    "🔵": ("#1a4f8a", "#e8f0fa"),  # bleu intermediaire
    "🟠": ("#8a5a1a", "#fbeedd"),  # orange expert
    "🔴": ("#8a1a1a", "#fbe4e4"),  # rouge tres expert
}
styles["LevelTitle"] = {}
for emo, (fg, bg) in LEVEL_COLORS.items():
    styles["LevelTitle"][emo] = ParagraphStyle(f"LevelTitle_{fg}", fontName="DejaVu-Bold",
                                                fontSize=11.5, leading=15, spaceBefore=8, spaceAfter=6,
                                                textColor=colors.white, backColor=colors.HexColor(fg),
                                                borderPadding=(5, 6, 5, 6))
styles["Body"] = ParagraphStyle("Body", fontName="DejaVu", fontSize=10, leading=14.5,
                                 spaceAfter=6, alignment=TA_LEFT)
styles["SchemaTitle"] = ParagraphStyle("SchemaTitle", fontName="DejaVu-Bold", fontSize=12,
                                        leading=15, spaceBefore=10, spaceAfter=6,
                                        textColor=colors.HexColor("#0d2647"))
styles["Caption"] = ParagraphStyle("Caption", fontName="DejaVu-It", fontSize=8.5, leading=11,
                                    alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=10)
styles["CalloutTitle"] = {
    "exemple": ParagraphStyle("CO_ex_t", fontName="DejaVu-Bold", fontSize=10.5,
                               textColor=colors.HexColor("#1a6b34")),
    "piege": ParagraphStyle("CO_pi_t", fontName="DejaVu-Bold", fontSize=10.5,
                             textColor=colors.HexColor("#8a5a1a")),
    "lab": ParagraphStyle("CO_lab_t", fontName="DejaVu-Bold", fontSize=10.5,
                           textColor=colors.HexColor("#5a2f8a")),
}
styles["CalloutBody"] = {
    "exemple": ParagraphStyle("CO_ex_b", fontName="DejaVu", fontSize=9.3, leading=13),
    "piege": ParagraphStyle("CO_pi_b", fontName="DejaVu", fontSize=9.3, leading=13),
    "lab": ParagraphStyle("CO_lab_b", fontName="DejaVu", fontSize=9.3, leading=13),
}
CALLOUT_BG = {"exemple": "#eaf6ec", "piege": "#fdf1e0", "lab": "#f1eafb"}
styles["TableHeader"] = ParagraphStyle("TableHeader", fontName="DejaVu-Bold", fontSize=8.7,
                                        leading=11, textColor=colors.white)
styles["TableCell"] = ParagraphStyle("TableCell", fontName="DejaVu", fontSize=8.7, leading=11.5)
styles["TOCEntry"] = ParagraphStyle("TOCEntry", fontName="DejaVu", fontSize=11, leading=20,
                                     textColor=colors.HexColor("#1a4f8a"))

# ---------------------------------------------------------------- parsing --
def callout_kind(line):
    if "📐" in line:
        return "exemple"
    if "⚠️" in line or "⚠" in line:
        return "piege"
    if "🔗" in line:
        return "lab"
    return None


def parse_table(lines, i):
    rows = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        rows.append(row)
        i += 1
    if len(rows) >= 2 and re.match(r"^:?-+:?$", rows[1][0].replace(" ", "")):
        del rows[1]
    return rows, i


def build_table_flowable(rows, avail_width):
    ncols = len(rows[0])
    data = []
    header = [Paragraph(inline_markdown(c), styles["TableHeader"]) for c in rows[0]]
    data.append(header)
    for r in rows[1:]:
        r = r + [""] * (ncols - len(r))
        data.append([Paragraph(inline_markdown(c), styles["TableCell"]) for c in r[:ncols]])
    colw = avail_width / ncols
    t = Table(data, colWidths=[colw] * ncols, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d2647")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#bbbbbb")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6fa")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


AVAIL_WIDTH = A4[0] - 2 * 2.0 * cm


def build_story(md_path):
    with open(md_path, encoding="utf-8") as f:
        lines = f.read().split("\n")

    story = []
    chapter_no = 0
    i = 0
    n = len(lines)

    # ---- page de garde ----
    story.append(Spacer(1, 5 * cm))
    story.append(Paragraph(TITLE, styles["CoverTitle"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Fondements analytiques expliqués niveau par niveau"
                            " — du Lycée au doctorat —", styles["CoverSub"]))
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph("14 chapitres gradés · démonstrations · exemples "
                            "numériques recalculés · schémas", styles["CoverMeta"]))
    story.append(Spacer(1, 2.5 * cm))
    story.append(Paragraph(f"Document VAULT — projet <b>Riemann_Lab</b>", styles["CoverMeta"]))
    story.append(Paragraph(f"{REPO_URL}", styles["CoverMeta"]))
    story.append(Paragraph(f"Auteur : {AUTHOR} — Mis à jour le {MAJ_DATE}", styles["CoverMeta"]))
    story.append(NextPageTemplate("normal"))
    story.append(PageBreak())

    # ---- table des matieres ----
    story.append(Paragraph("Table des matières", styles["TOCTitle"]))
    toc = TableOfContents()
    toc.levelStyles = [styles["TOCEntry"]]
    story.append(toc)
    story.append(PageBreak())

    while i < n:
        raw = lines[i]
        line = raw.rstrip()

        if not line.strip():
            i += 1
            continue

        if line.startswith("# Chapitre"):
            chapter_no += 1
            title_txt = line[2:].strip()
            story.append(KeepTogether([Paragraph(escape_xml(title_txt), styles["ChapterTitle"])]))
            # bookmark / TOC entry cible
            story.append(_Bookmark(f"ch{chapter_no}", title_txt))
            i += 1
            continue

        if line.startswith("# "):  # titre principal (deja traite en page de garde)
            i += 1
            continue

        if line.startswith("## Sommaire"):
            # on saute le sommaire textuel du .md (remplace par la TOC generee)
            i += 1
            while i < n and not lines[i].startswith("#"):
                i += 1
            continue

        if line.startswith("## Schéma"):
            title_txt = line[3:].strip()
            story.append(Paragraph(escape_xml(title_txt), styles["SchemaTitle"]))
            i += 1
            continue

        if line.startswith("## "):
            title_txt = line[3:].strip()
            story.append(Paragraph(inline_markdown(title_txt), styles["FormuleTitle"]))
            i += 1
            continue

        if line.startswith("### "):
            title_txt = line[4:].strip()
            emo = title_txt[0] if title_txt[:1] in styles["LevelTitle"] else None
            style = styles["LevelTitle"].get(emo, styles["FormuleTitle"])
            clean = title_txt[1:].strip() if emo else title_txt
            story.append(Paragraph(escape_xml(clean), style))
            i += 1
            continue

        if line.strip() == "---":
            i += 1
            continue

        if line.strip().startswith("!["):
            m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
            if m:
                alt, relpath = m.group(1), m.group(2)
                imgpath = os.path.join(HERE, relpath)
                if os.path.exists(imgpath):
                    from PIL import Image as PILImage
                    iw, ih = PILImage.open(imgpath).size
                    max_w = AVAIL_WIDTH * 0.92
                    ratio = max_w / iw
                    disp_w, disp_h = max_w, ih * ratio
                    max_h = 9.5 * cm
                    if disp_h > max_h:
                        disp_h = max_h
                        disp_w = iw * (max_h / ih)
                    story.append(Spacer(1, 4))
                    story.append(Image(imgpath, width=disp_w, height=disp_h, hAlign="CENTER"))
            i += 1
            continue

        if line.strip().startswith(">"):
            block = []
            while i < n and lines[i].strip().startswith(">"):
                block.append(lines[i].strip()[1:].strip())
                i += 1
            kind = None
            for bl in block:
                k = callout_kind(bl)
                if k:
                    kind = k
                    break
            kind = kind or "lab"
            # 1ere ligne = titre (garde emoji), reste = corps
            body_lines = [b for b in block[1:] if b]
            CALLOUT_LABEL = {"exemple": "Exemple numérique", "piege": "Piège / limite",
                             "lab": "Lien avec le LAB"}
            title_p = Paragraph(CALLOUT_LABEL[kind], styles["CalloutTitle"][kind])
            body_ps = [Paragraph(inline_markdown(b), styles["CalloutBody"][kind]) for b in body_lines if b.strip()]
            inner = [title_p, Spacer(1, 3)] + body_ps
            tbl = Table([[inner]], colWidths=[AVAIL_WIDTH])
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(CALLOUT_BG[kind])),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor(CALLOUT_BG[kind])),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ]))
            story.append(Spacer(1, 4))
            story.append(tbl)
            story.append(Spacer(1, 4))
            continue

        if line.strip().startswith("|"):
            rows, i = parse_table(lines, i)
            if rows:
                story.append(Spacer(1, 3))
                story.append(build_table_flowable(rows, AVAIL_WIDTH))
                story.append(Spacer(1, 6))
            continue

        if line.strip().startswith("$$"):
            block = []
            full = line.strip()
            if full.count("$$") >= 2 and len(full) > 2:
                math_src = full.strip("$")
                i += 1
            else:
                i += 1
                while i < n and "$$" not in lines[i]:
                    block.append(lines[i])
                    i += 1
                if i < n:
                    i += 1
                math_src = " ".join(block)
            markup = latex_to_markup(math_src)
            story.append(Paragraph(markup, styles["Formule"]))
            continue

        # paragraphe normal (accumulate jusqu'a ligne vide ou marqueur)
        para_lines = [line]
        i += 1
        while i < n and lines[i].strip() and not lines[i].startswith(("#", ">", "|", "!", "$", "---")):
            para_lines.append(lines[i].strip())
            i += 1
        text = " ".join(para_lines)
        story.append(Paragraph(inline_markdown(text), styles["Body"]))

    return story


class _Bookmark(Paragraph):
    """Flowable invisible qui pose un signet PDF + alimente la TOC."""
    def __init__(self, key, title):
        super().__init__("", ParagraphStyle("invisible", fontSize=1, leading=1))
        self.key = key
        self.title = title

    def draw(self):
        pass

    def wrap(self, aw, ah):
        return (0, 0)


# --------------------------------------------------------- doc template ----
class ChapterDocTemplate(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, _Bookmark):
            self.canv.bookmarkPage(flowable.key)
            self.canv.addOutlineEntry(flowable.title, flowable.key, level=0)
            self.notify("TOCEntry", (0, flowable.title, self.page, flowable.key))


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(colors.HexColor("#0d2647"))
    canvas.rect(0, h - 1.15 * cm, w, 1.15 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("DejaVu-Bold", 9)
    canvas.drawString(1.4 * cm, h - 0.78 * cm, "Riemann_Lab — Formation ζ & Hypothèse de Riemann")
    canvas.setFont("DejaVu", 8.5)
    canvas.drawRightString(w - 1.4 * cm, h - 0.78 * cm, "Document VAULT")

    canvas.setStrokeColor(colors.HexColor("#cccccc"))
    canvas.line(1.4 * cm, 1.15 * cm, w - 1.4 * cm, 1.15 * cm)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.setFont("DejaVu", 8)
    canvas.drawString(1.4 * cm, 0.75 * cm, f"Auteur : {AUTHOR} — Mis à jour le {MAJ_DATE} — {REPO_URL}")
    canvas.drawRightString(w - 1.4 * cm, 0.75 * cm, f"page {doc.page}")
    canvas.restoreState()


def main():
    doc = ChapterDocTemplate(PDF_PATH, pagesize=A4,
                              leftMargin=2 * cm, rightMargin=2 * cm,
                              topMargin=1.9 * cm, bottomMargin=1.6 * cm,
                              title=TITLE, author=AUTHOR)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    tmpl = PageTemplate(id="normal", frames=[frame], onPage=header_footer)
    cover_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="cover")
    cover_tmpl = PageTemplate(id="cover", frames=[cover_frame], onPage=lambda c, d: None)
    doc.addPageTemplates([cover_tmpl, tmpl])

    story = build_story(MD_PATH)
    doc.multiBuild(story)
    print("PDF genere :", PDF_PATH)


if __name__ == "__main__":
    main()
