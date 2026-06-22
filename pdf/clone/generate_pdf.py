#!/usr/bin/env python3
"""Régénère rapport_clonage_zeta_enrichi.pdf depuis rapport_clonage_zeta.md via WeasyPrint."""
import sys
from pathlib import Path

import markdown
from weasyprint import HTML, CSS

BASE = Path(__file__).parent
MD_FILE = BASE / "rapport_clonage_zeta.md"
PDF_FILE = BASE / "rapport_clonage_zeta_enrichi.pdf"

CSS_STYLE = """
@page {
    size: A4;
    margin: 2cm 1.8cm;
}
body {
    font-family: "DejaVu Sans", sans-serif;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #1a1a1a;
}
h1 {
    font-size: 20pt;
    color: #0d1117;
    border-bottom: 3px solid #2563eb;
    padding-bottom: 0.2cm;
}
h2 {
    font-size: 15pt;
    color: #1e3a8a;
    margin-top: 1cm;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 0.1cm;
    page-break-before: always;
}
h1 + h2, h2:first-of-type {
    page-break-before: avoid;
}
h3 {
    font-size: 12.5pt;
    color: #1e40af;
    margin-top: 0.6cm;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.4cm 0;
    font-size: 9pt;
}
th, td {
    border: 1px solid #cbd5e1;
    padding: 4px 6px;
    text-align: left;
    vertical-align: top;
}
th {
    background-color: #1e3a8a;
    color: white;
}
tr:nth-child(even) {
    background-color: #f1f5f9;
}
code {
    font-family: "DejaVu Sans Mono", monospace;
    background-color: #f1f5f9;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 9pt;
}
pre {
    background-color: #0d1117;
    color: #e6edf3;
    padding: 0.3cm;
    border-radius: 4px;
    font-size: 8.5pt;
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
}
pre code {
    background-color: transparent;
    color: inherit;
    padding: 0;
}
blockquote {
    border-left: 4px solid #2563eb;
    margin: 0.3cm 0;
    padding: 0.2cm 0.5cm;
    background-color: #eff6ff;
    color: #1e293b;
}
img {
    max-width: 100%;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    margin: 0.2cm 0;
}
hr {
    border: none;
    border-top: 1px solid #cbd5e1;
    margin: 0.5cm 0;
}
a {
    color: #2563eb;
    text-decoration: none;
}
em {
    color: #475569;
}
"""


def main() -> None:
    md_text = MD_FILE.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "toc", "nl2br"],
    )
    html_doc = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><title>Rapport — Clonage et mise à jour système — Projet Zêta</title></head>
<body>{html_body}</body>
</html>"""

    HTML(string=html_doc, base_url=str(BASE)).write_pdf(
        str(PDF_FILE), stylesheets=[CSS(string=CSS_STYLE)]
    )
    print(f"PDF généré : {PDF_FILE} ({PDF_FILE.stat().st_size} octets)")


if __name__ == "__main__":
    main()
