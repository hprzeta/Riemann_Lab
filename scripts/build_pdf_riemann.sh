#!/usr/bin/env bash
# build_pdf_riemann.sh — convertit un .md (wiki Riemann_Lab) en PDF scientifique (style hprzeta)
# Usage : ./build_pdf_riemann.sh chemin/source.md [sortie.pdf]
# Dépend : pandoc, xelatex (texlive), latexmk, polices DejaVu. Auteur : hprzeta.
# Date du pied de page en français (corrigé le 2026-11-11) : DATE_FR calculée dans ce script, sans dépendre de la locale.
set -euo pipefail
export LANG=C.UTF-8 LC_ALL=C.UTF-8
# Date en français, calculée ici (indépendante de la locale et de LC_ALL=C.UTF-8) : « 1er » pour le premier du mois.
MOIS=(janvier février mars avril mai juin juillet août septembre octobre novembre décembre)
JOUR="$(date +%-d)"; [ "$JOUR" = 1 ] && JOUR="1er"
DATE_FR="$JOUR ${MOIS[$(( $(date +%-m) - 1 ))]} $(date +%Y)"
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

sed -i "s/\\\\today/$DATE_FR/" "$WORK/header.tex"   # \date de l'en-tête : date française
# 2) Pré-traitement : titre H1, emojis, mermaid, marqueurs, pipes nus dans les maths
python3 - "$SRC" "$WORK" "$BASE" "$DATE_FR" << 'PY'
import re, sys
src, work, base, date_fr = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
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
  '{\\small Document créé le '+date_fr+' --- source \\texttt{'+esc+'} --- Riemann\\_Lab --- hprzeta}\n')
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
