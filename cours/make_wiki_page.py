#!/usr/bin/env python3
"""Convertit Cours_Zeta_HR_complet.md en page wiki unique
Formation-Zeta-HR.md : ancres par chapitre, images en raw.githubusercontent,
sommaire ancré, en-tête/pied + nb de lignes.
"""
import re
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Cours_Zeta_HR_complet.md")
OUT = os.path.join(os.path.expanduser("~/projet_zeta/Riemann_Lab.wiki"), "Formation-Zeta-HR.md")

RAW_BASE = "https://raw.githubusercontent.com/hprzeta/Riemann_Lab/Riemann_Lab_IA/cours/figures"
MAJ_DATE = "13 septembre 2026"
AUTHOR = "hprzeta"

with open(SRC, encoding="utf-8") as f:
    text = f.read()

BLOB_BASE = "https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/cours/figures"

# 1) images : figures/chNN_x.png -> URL brute raw.githubusercontent
text = re.sub(r"\(figures/([a-zA-Z0-9_]+\.png)\)", rf"({RAW_BASE}/\1)", text)
# mentions "Source éditable : `figures/chNN_x.svg`" -> lien cliquable vers le blob GitHub
text = re.sub(r"`figures/([a-zA-Z0-9_]+\.svg)`", rf"[figures/\1]({BLOB_BASE}/\1)", text)

# 2) reperer les 14 chapitres et construire les ancres + le sommaire
lines = text.split("\n")
chapters = []  # (index dans lines, titre complet, numero)
for idx, line in enumerate(lines):
    m = re.match(r"^# Chapitre (\d+) — (.+)$", line)
    if m:
        chapters.append((idx, int(m.group(1)), m.group(2)))

assert len(chapters) == 14, f"attendu 14 chapitres, trouve {len(chapters)}"

# inserer les ancres nommees juste avant chaque titre de chapitre (en partant de la fin
# pour ne pas decaler les indices restants)
for idx, num, title in reversed(chapters):
    lines.insert(idx, f'<a name="ch{num}"></a>')

text = "\n".join(lines)

# 3) remplacer le bloc "## Sommaire" (liste actuelle) par une liste ancree
sommaire_lines = []
for _, num, title in chapters:
    sommaire_lines.append(f"{num}. [Chapitre {num} — {title}](#ch{num})")
sommaire_block = "## Sommaire\n\n" + "\n".join(sommaire_lines) + "\n"

text = re.sub(r"## Sommaire\n.*?(?=\n---\n)", sommaire_block, text, count=1, flags=re.DOTALL)

# 4) en-tete wiki (rappel titre + auteur + lien repo) ; le fichier source en a deja un,
#    on l'enrichit d'une mention "Document VAULT — page wiki unique"
text = text.replace(
    "# Cours ζ & Hypothèse de Riemann — édition complète\n",
    "# Cours ζ & Hypothèse de Riemann — édition complète\n\n"
    "*Page wiki unique — Document VAULT, projet Riemann_Lab*\n",
    1,
)

# 5) pied de page : date + auteur + nb de lignes (recalcule sur le fichier final)
text = text.replace(
    "**Nombre de lignes du fichier : 1159**",
    "**Nombre de lignes du fichier : {LINES}**",
)

n_lines = text.count("\n") + 1
text = text.replace("{LINES}", str(n_lines + 1))  # +1 : le remplacement rallonge d'une ligne au pire, corrige ci-dessous

with open(OUT, "w", encoding="utf-8") as f:
    f.write(text)

# recalcule exact apres ecriture (le remplacement de {LINES} peut changer la longueur totale
# de 1 caractere mais pas le nombre de lignes -> on rouvre et corrige si besoin)
with open(OUT, encoding="utf-8") as f:
    final_lines = f.read().split("\n")
actual_n = len(final_lines)
with open(OUT, encoding="utf-8") as f:
    content = f.read()
content = re.sub(r"\*\*Nombre de lignes du fichier : \d+\*\*",
                  f"**Nombre de lignes du fichier : {actual_n}**", content)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(content)

print("Ecrit :", OUT)
print("Chapitres ancres :", len(chapters))
print("Nombre de lignes final :", actual_n)
