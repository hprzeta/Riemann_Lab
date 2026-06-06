import cairosvg
from pathlib import Path

# ── Chemin du fichier SVG ──────────────────────────────────────────
svg_path = Path.home() / "Téléchargements" / "plan_continuite_riemann.svg"  # ← change le nom ici

# ── Sortie dans le même dossier ───────────────────────────────────
png_path = svg_path.with_suffix(".png")

# ── Conversion ────────────────────────────────────────────────────
cairosvg.svg2png(
    url=str(svg_path),
    write_to=str(png_path),
    scale=2.0
)

print(f"✅ PNG créé : {png_path}")
