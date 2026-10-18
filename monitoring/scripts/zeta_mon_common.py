"""Chemins et utilitaires communs du monitoring Zêta (importé par les autres scripts)."""
import datetime
import json
import os
import re
import subprocess
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("ZETA_MON_ROOT", SCRIPTS.parent))          # ~/projet_zeta/monitoring
DATA, RUNS, LOGS = ROOT / "data", ROOT / "runs", ROOT / "logs"
CALCULS = Path(os.environ.get("ZETA_CALCULS", Path.home() / "projet_zeta" / "calculs"))
BASEURL = os.environ.get("ZETA_MON_BASEURL", "").rstrip("/")          # ex. URL raw GitHub (wiki)
ACTIF = RUNS / ".actif"            # contient « type/id » du run suivi en ce moment
HINT = RUNS / ".hint"              # indice laissé par zeta-run-hint pour le prochain run
FENETRES = RUNS / ".fenetres.json"  # PID des fenêtres de graphiques ouvertes
TYPES = ("test", "prod", "auto", "historique")


def ecrire_md(chemin, texte):
    """Écrit un MD avec pied de page : date de mise à jour + nombre de lignes du fichier."""
    texte = texte.rstrip("\n") + "\n"
    n = len(texte.splitlines()) + 3
    pied = "\n---\n*%s · MAJ %s · %d lignes*\n" % (Path(chemin).name, datetime.date.today().isoformat(), n)
    Path(chemin).write_text(texte + pied, encoding="utf-8")
    return n


def lien(rel):
    return (BASEURL + "/" + rel) if BASEURL else rel


def dossiers_runs():
    """Tous les dossiers de run : runs/<type>/<id>/ (et l'ancien format plat runs/<id>/)."""
    return sorted({f.parent for f in RUNS.glob("*/meta.json")} | {f.parent for f in RUNS.glob("*/*/meta.json")})


def lire_hint(consommer=True):
    """Indice laissé avant un run (zeta-run-hint) : {'nom':..., 'csv':...}."""
    h = {}
    if HINT.exists():
        for l in HINT.read_text().splitlines():
            if "=" in l:
                k, v = l.split("=", 1)
                if v.strip():
                    h[k.strip()] = v.strip()
        if consommer:
            HINT.rename(RUNS / ".hint.utilise")      # valable pour un seul run
    return h


def csv_du_run(meta, t0, t1=None):
    """CSV des zéros d'un run : celui donné (fichier ou dossier), sinon le plus récent modifié pendant le run."""
    t1 = t1 or datetime.datetime.now()
    deb = t0.timestamp() - 30
    c = meta.get("csv")
    if c:
        c = Path(os.path.expanduser(c))
        if c.is_dir():
            fs = [f for f in c.rglob("*.csv") if f.stat().st_mtime >= deb]
            return str(max(fs, key=lambda f: f.stat().st_mtime)) if fs else None
        return str(c) if c.is_file() else None
    cand = []
    if CALCULS.is_dir():
        for f in CALCULS.rglob("*.csv"):
            try:
                st = f.stat()
            except OSError:
                continue
            if deb <= st.st_mtime <= t1.timestamp() + 300 and st.st_size > 0:
                cand.append((st.st_mtime, f))
    return str(max(cand)[1]) if cand else None


def titrer(fig, titre):
    """Titre de la FENÊTRE (barre de titre) à la place de « Figure 1 » ; sans effet si le backend n'en a pas."""
    try:
        fig.canvas.manager.set_window_title(titre)
    except Exception:
        pass


def lignes_workers(csvp, cache):
    """Nombre TOTAL de zéros écrits par TOUS les workers du run (somme sur worker_NNN.csv / worker_NNN.partial.csv).
    Par worker on prend le plus grand des deux (le .partial.csv est supprimé quand le .csv final est écrit :
    pas de double comptage). `cache` : dict {chemin: (mtime, taille, lignes)} pour ne recompter que ce qui change.
    Renvoie (total, t_max) — t_max = plus grande partie imaginaire écrite par un worker (dernière ligne de chaque fichier,
    les zéros d'un worker étant croissants) — ou None s'il n'y a aucun fichier de worker (run hors format v16/v17) :
    l'appelant garde alors son comptage."""
    try:
        racine = Path(csvp).parent
        if racine.name == "checkpoints":
            dossier = racine
        else:
            dossier = racine / "checkpoints"
        if not dossier.is_dir():
            return None
        par_worker, tmax = {}, None
        for f in list(dossier.glob("worker_*.csv")) + list(dossier.glob("worker_*.partial.csv")):
            m = re.match(r"worker_(\d+)(\.partial)?\.csv$", f.name)
            if not m:
                continue
            try:
                st = f.stat()
                cle = str(f)
                if cache.get(cle, (None, None, 0, None))[:2] != (st.st_mtime, st.st_size):
                    with open(f, "rb") as fh:
                        data = fh.read()
                    n = max(data.count(b"\n") - 1, 0)                    # lignes complètes moins l'en-tête
                    tm = None
                    try:                                                  # dernière ligne complète = plus grand t du worker
                        lignes = data[:data.rfind(b"\n")].split(b"\n")
                        col = lignes[0].decode().split(",").index("partie_imaginaire")
                        if len(lignes) > 1:
                            tm = float(lignes[-1].decode().split(",")[col])
                    except Exception:
                        pass
                    cache[cle] = (st.st_mtime, st.st_size, n, tm)
                n, tm = cache[cle][2], cache[cle][3]
                if tm is not None:
                    tmax = tm if tmax is None else max(tmax, tm)
            except OSError:
                continue                                                  # fichier remplacé pendant la lecture
            par_worker[m.group(1)] = max(par_worker.get(m.group(1), 0), n)
        return (sum(par_worker.values()), tmax) if par_worker else None
    except Exception:
        return None


# ----------------------------------------------------------------------------- fenêtres
def ecran_taille():
    """Taille de l'écran (L, H) : variable ZETA_ECRAN=1920x1080, sinon xrandr, sinon 1920x1080."""
    m = re.fullmatch(r"(\d+)x(\d+)", os.environ.get("ZETA_ECRAN", ""))
    if m:
        return int(m.group(1)), int(m.group(2))
    try:
        out = subprocess.run(["xrandr", "--current"], capture_output=True, text=True, timeout=3).stdout
        m = re.search(r"current (\d+) x (\d+)", out)
        if m:
            return int(m.group(1)), int(m.group(2))
    except Exception:
        pass
    return 1920, 1080


def layout(W=None, H=None):
    """Géométries « LxH+X+Y » des 3 fenêtres : zéros en haut à gauche, GUE en bas à gauche, machines à droite.
    Surchargeable par ROOT/layout.json : {"marge": [75, 35], "geometries": {"live": "...", "gue": "...", "metrics": "..."}}"""
    W, H = (W, H) if W else ecran_taille()
    marge = (75, 35)                                           # dock à gauche, barre du haut (GNOME)
    cfg = {}
    try:
        cfg = json.loads((ROOT / "layout.json").read_text())
        marge = tuple(cfg.get("marge", marge))
    except Exception:
        pass
    x0, y0 = marge
    larg, haut = W - x0 - 4, H - y0 - 40                       # 40 px : décorations de fenêtres
    hw, hh = larg // 2 - 10, haut // 2 - 6
    g = {"live": "%dx%d+%d+%d" % (hw, hh, x0, y0),
         "gue": "%dx%d+%d+%d" % (hw, hh, x0, y0 + haut // 2),
         "metrics": "%dx%d+%d+%d" % (hw, haut - 6, x0 + larg // 2, y0)}
    g.update(cfg.get("geometries", {}))
    return g


def parse_geom(s):
    m = re.fullmatch(r"(\d+)x(\d+)(?:\+(-?\d+)\+(-?\d+))?", s.strip())
    if not m:
        raise ValueError("géométrie attendue : LARGEURxHAUTEUR+X+Y (ex. 900x500+75+35)")
    w, h, x, y = m.groups()
    return int(w), int(h), int(x or 0), int(y or 0)


def compacter(geom):
    """Petites fenêtres : polices plus petites (à appeler AVANT de créer la figure)."""
    import matplotlib.pyplot as plt
    if parse_geom(geom)[0] < 1100:
        plt.rcParams.update({"font.size": 8, "axes.titlesize": 9, "legend.fontsize": 7})


def placer(fig, geom, dpi=100):
    """Taille de la figure = taille de la fenêtre ; position si le gestionnaire de fenêtres l'accepte
    (Tk / Qt ; sous Wayland natif la position peut être ignorée : utiliser Super+flèches)."""
    w, h, x, y = parse_geom(geom)
    fig.set_dpi(dpi)
    fig.set_size_inches(w / dpi, h / dpi)
    try:
        import matplotlib
        b = matplotlib.get_backend().lower()
        win = fig.canvas.manager.window
        if "tk" in b:
            win.wm_geometry("%dx%d+%d+%d" % (w, h, x, y))
        elif "qt" in b:
            win.setGeometry(x, y, w, h)
    except Exception:
        pass

# zeta_mon_common.py · hprzeta · MAJ 2026-10-17 · 144 lignes
