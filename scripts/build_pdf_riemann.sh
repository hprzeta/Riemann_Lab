#!/usr/bin/env bash
# build_pdf_riemann.sh — convertit un .md (wiki Riemann_Lab) en PDF scientifique (style hprzeta)
# Usage : ./build_pdf_riemann.sh chemin/source.md [sortie.pdf]
# Dépend : pandoc, xelatex (texlive), latexmk, polices DejaVu. Auteur : hprzeta.
set -euo pipefail
export LANG=C.UTF-8 LC_ALL=C.UTF-8
SRC="$1"
OUT="${2:-$(basename "${SRC%.md}").pdf}"
BASE="$(basename "$SRC")"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT

# 1) En-tête de style (titre gras centré, code encadré, maths Computer Modern)
cat > "$WORK/header.tex" << 'EOF'
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{pgfplots}\pgfplotsset{compat=1.18}
\usepackage{titling}
\pretitle{\begin{center}\LARGE\bfseries}\posttitle{\par\end{center}}
\lstset{basicstyle=\ttfamily\footnotesize,breaklines=true,frame=single,columns=fullflexible,keepspaces=true}
\date{\small Auteur : hprzeta --- \today}
EOF

# 2) Pré-traitement : titre H1, emojis, mermaid, marqueurs, pipes nus dans les maths
python3 - "$SRC" "$WORK" "$BASE" << 'PY'
import re, sys
src, work, base = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding='utf-8').read()
s = re.sub(r'[\U0001F000-\U0001FAFF\u2B50\u270F\uFE0F\u2699]', '', s)          # emojis
s = re.sub(r'```mermaid.*?```', '> *(Diagramme Mermaid — version interactive sur le wiki.)*', s, flags=re.S)
s = s.replace('✅', r'$\checkmark$').replace('❌', r'$\times$').replace('⚠', '(!)')
s = s.replace(r'$|z|$', r'$\lvert z\rvert$')                                   # pipe nu en maths/table
lines = s.splitlines(); title=''; out=[]
for l in lines:
    if not title and l.startswith('# '): title = l[2:].strip(); continue
    out.append(l)
open(f'{work}/body.md','w',encoding='utf-8').write(f'---\ntitle: "{title}"\n---\n\n' + '\n'.join(out))
esc = base.replace('_', r'\_')
open(f'{work}/footer.tex','w',encoding='utf-8').write(
  '\\vfill\n\\noindent\\rule{\\textwidth}{0.4pt}\\\\\n'
  '{\\small Document créé le \\today{} --- source \\texttt{'+esc+'} --- Riemann\\_Lab --- hprzeta}\n')
print("Titre:", title)
PY

# 3) Conversion + compilation
pandoc "$WORK/body.md" --from gfm+tex_math_dollars --listings --shift-heading-level-by=-1 \
  -s -t latex -V documentclass=article -V classoption=11pt -V classoption=a4paper \
  -V geometry=margin=2.5cm -V mainfont="DejaVu Serif" -V monofont="DejaVu Sans Mono" \
  -H "$WORK/header.tex" -A "$WORK/footer.tex" -o "$WORK/doc.tex"
sed -i '/\\usepackage{lmodern}/d' "$WORK/doc.tex"
( cd "$WORK" && latexmk -xelatex -interaction=nonstopmode -halt-on-error doc.tex >/dev/null 2>&1 )
cp "$WORK/doc.pdf" "$OUT"
echo "✅ PDF généré : $OUT  ($(pdfinfo "$OUT" 2>/dev/null | awk '/Pages/{print $2}') pages)"
