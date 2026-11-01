#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""zeta_log_graphes.py (v1.3) — graphiques tirés du journal d'un run (logs/run_T<N>_<date>.log, calcul v16).

Usage (alias zeta-log-graph) :
    python3 -I zeta_log_graphes.py [JOURNAL | auto] [--graphes 1,2,3,4,5,6] [--sortie DOSSIER] [--logs DOSSIER]

Sans argument (ou « auto ») : prend le journal le plus récent de ~/projet_zeta/logs. Les PNG sont écrits dans
    monitoring/runs/prod/<run>/figures/   (chemin lu dans la ligne « Suivi démarré : … » du journal)
ou, à défaut, dans <dossier du journal>/figures/<nom du journal>/. Lecture seule du journal.

Graphiques (chacun n'utilise que des lignes présentes dans le journal ; un bloc absent donne un graphique sauté,
jamais une valeur inventée ; les grandeurs calculées sont signalées « (calculé) ») :
  1  progression et débit de chaque worker        (lisible pendant le run)
  2  chronologie (Gantt) des workers et du rescan (lisible pendant le run ; rescan en fin de run)
  3  répartition du temps par phase (anneau)      (fin de run : bloc [PROFIL PHASES])
  4  histogramme du temps pour 1000 zéros         (lisible pendant le run)
  5  précision sur les 20 premiers zéros (LMFDB)  (fin de run)
  6  complétude : segments et points de Turing    (fin de run)

Ce module est aussi une bibliothèque : lire_journal(), trouver_journal() et les fonctions tracer_*() sont
réutilisées par zeta_log_live.py (fenêtre en direct) et zeta_plot_proc.py (repères du journal).
Bibliothèques : matplotlib (aucune fenêtre n'est ouverte ici : les figures sont écrites par savefig).
"""
import argparse, glob, math, os, re, statistics, sys, textwrap

import matplotlib
from matplotlib.figure import Figure
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from matplotlib import ticker

VERSION = "1.0"

# ----------------------------------------------------------------------------------------------------------------
#  Lecture du journal
# ----------------------------------------------------------------------------------------------------------------
RE_PROG = re.compile(r"\[Worker (\d+)\] zéro #(\d+) à t=([\d.]+) — ([\d.]+)s")
RE_FIN = re.compile(r"\[Worker (\d+)\] (\d+) zéros en ([\d.]+)s\s*\|\s*arb_C:(\d+)\s+fallback:(\d+)")
RE_SEGW = re.compile(r"^\s*Worker (\d+) : \[([\d.]+), ([\d.]+)\]")
RE_SEGR = re.compile(r"^\s*Seg\s+(\d+)\s+\[\s*([\d.]+),\s*([\d.]+)\]\s+(\d+)/(\d+)")
RE_LMFDB = re.compile(r"^\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+e[+-]\d+)")
RE_TUR = re.compile(r"^\s+([\d.]+)\s+(\d+)\s+(\d+)\s+([+-]?\d+)\s+(\S.*)$")
RE_PROF = re.compile(r"^\s+(detection|arb_C|mpmath_fallback|turing|mpmath_petit_t)\s+([\d.]+)s\s+(\d+)\s+([\d.]+)\s+([\d.]+)%")


def lire_journal(chemin):
    """Retourne un dictionnaire (voir les clés ci-dessous). Les blocs absents restent vides ou None.

    config{T_MAX,N_WORKERS,STEP,N_zeros_attendus}  segments{worker:(t0,t1)}  progression[(worker,n,t,temps_s)]
    workers{w:{zeros,temps_s,arb_C,fallback}}  resultat{trouves,attendus,duree_s,vitesse,methodes}
    rescan_segments[(seg,t0,t1,trouves,attendus)]  rescan_duree_s  rescan_net  lmfdb[(rang,calcule,ref,ecart)]
    turing[(T,calcules,attendus,manquants,statut)]  profil{phase:{cumul_s,appels,ms_appel,pct_mur_W}}
    termine (bool)  dossier_suivi (str|None)  chemin  mtime
    Workers 0 à 7 = run principal ; numéros >= 100 = rescan (100 + n° de segment).
    """
    with open(chemin, encoding="utf-8", errors="replace") as f:
        lignes = f.read().splitlines()
    r = {"config": {}, "segments": {}, "progression": [], "workers": {}, "resultat": {}, "rescan_segments": [],
         "rescan_duree_s": None, "rescan_net": None, "lmfdb": [], "turing": [], "profil": {},
         "termine": False, "dossier_suivi": None, "chemin": os.path.abspath(chemin), "mtime": os.path.getmtime(chemin)}
    dans_turing = dans_rescan = False
    for l in lignes:
        m = re.search(r"T_MAX\s*=\s*(\d+)", l)
        if m and "T_MAX" not in r["config"]:
            r["config"]["T_MAX"] = int(m.group(1))
        m = re.search(r"N_WORKERS\s*=\s*(\d+)", l)
        if m:
            r["config"]["N_WORKERS"] = int(m.group(1))
        m = re.search(r"STEP\s*=\s*([\d.]+)\s*$", l)
        if m and "STEP" not in r["config"]:
            r["config"]["STEP"] = float(m.group(1))
        m = re.search(r"N zéros\s*≈\s*(\d+)", l)
        if m:
            r["config"]["N_zeros_attendus"] = int(m.group(1))
        m = RE_SEGW.match(l)
        if m and not dans_rescan:
            r["segments"][int(m.group(1))] = (float(m.group(2)), float(m.group(3)))
        m = RE_PROG.search(l)
        if m:
            r["progression"].append((int(m.group(1)), int(m.group(2)), float(m.group(3)), float(m.group(4))))
            continue
        m = RE_FIN.search(l)
        if m:
            r["workers"][int(m.group(1))] = dict(zeros=int(m.group(2)), temps_s=float(m.group(3)),
                                                 arb_C=int(m.group(4)), fallback=int(m.group(5)))
            continue
        for cle, motif in (("trouves", r"Zéros trouvés\s*:\s*(\d+)"), ("attendus", r"Attendus \(Weyl\)\s*:\s*(\d+)"),
                           ("duree_s", r"Durée run\s*:.*\(([\d.]+) s\)"), ("vitesse", r"Vitesse\s*:\s*([\d.]+)")):
            m = re.search(motif, l)
            if m:
                r["resultat"][cle] = float(m.group(1)) if cle in ("duree_s", "vitesse") else int(m.group(1))
        m = re.match(r"^\s+(arb_C|mpmath_fallback|mpmath_petit_t)\s*:\s*(\d+)\s+\(", l)
        if m:
            r["resultat"].setdefault("methodes", {})[m.group(1)] = int(m.group(2))
        if "RESCAN CIBLÉ" in l:
            dans_rescan = True
        m = RE_SEGR.match(l)
        if m and "rescannés" not in l:
            r["rescan_segments"].append((int(m.group(1)), float(m.group(2)), float(m.group(3)),
                                         int(m.group(4)), int(m.group(5))))
        m = re.search(r"Rescan terminé en ([\d.]+)s", l)
        if m:
            r["rescan_duree_s"] = float(m.group(1))
        m = re.search(r"\(\+(\d+) nets après déduplication\)", l)
        if m:
            r["rescan_net"] = int(m.group(1))
        if "VALIDATION TURING" in l:
            dans_turing = True
            continue
        if dans_turing:
            m = RE_TUR.match(l)
            if m and "Calculés" not in l:
                r["turing"].append((float(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)),
                                    m.group(5).strip()))
            if "COMPLET" in l:
                dans_turing = False
        if not dans_turing:
            m = RE_LMFDB.match(l)
            if m and "Calculé" not in l:
                r["lmfdb"].append((int(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))))
        m = RE_PROF.match(l)
        if m:
            r["profil"][m.group(1)] = dict(cumul_s=float(m.group(2)), appels=int(m.group(3)),
                                           ms_appel=float(m.group(4)), pct_mur_W=float(m.group(5)))
        m = re.search(r"Suivi démarré : (\S+)", l)
        if m:
            r["dossier_suivi"] = m.group(1)
        if "v16 terminée" in l or "Fin demandée" in l:
            r["termine"] = True
    return r


def trouver_journal(dossier_logs=None, apres=None):
    """Journal run_T*.log le plus récemment modifié (et modifié après `apres`, epoch, si fourni)."""
    dossier_logs = dossier_logs or os.path.expanduser("~/projet_zeta/logs")
    fs = sorted(glob.glob(os.path.join(dossier_logs, "run_T*.log")), key=os.path.getmtime)
    if apres is not None:
        fs = [f for f in fs if os.path.getmtime(f) >= apres]
    return fs[-1] if fs else None


def dossier_figures(d):
    """monitoring/runs/prod/<run>/figures/ (lu dans le journal) ou, à défaut, <dossier du journal>/figures/<journal>/."""
    s = d.get("dossier_suivi")
    if s and os.path.isdir(s):
        return os.path.join(s, "figures")
    base = os.path.splitext(os.path.basename(d["chemin"]))[0]
    return os.path.join(os.path.dirname(d["chemin"]), "figures", base)


def courbes_workers(d, avec_fin=True):
    """{worker: [(temps_s, zéros_cumulés), ...]} du run principal ; avec_fin ajoute la ligne de fin du worker."""
    c = {}
    for w, n, t, s in d["progression"]:
        if w < 100:
            c.setdefault(w, []).append((s, n))
    for w in c:
        c[w].sort()
        if avec_fin and w in d["workers"]:
            c[w].append((d["workers"][w]["temps_s"], d["workers"][w]["zeros"]))
    return c


def courbes_rescan(d):
    c = {}
    for w, n, t, s in d["progression"]:
        if w >= 100:
            c.setdefault(w, []).append((s, n))
    for w in c:
        c[w].sort()
    return c


# ----------------------------------------------------------------------------------------------------------------
#  Style (palette de référence de la compétence dataviz, mode clair) et petits outils
# ----------------------------------------------------------------------------------------------------------------
SURFACE, INK, INK2, INK3, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#7b7a75", "#e6e5e1"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]                    # emplacements catégoriels 1 à 5
RAMPE_BLEUE = ["#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95"]
GRIS = "#c9c8c3"
STYLE = {
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.edgecolor": GRID, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 11, "legend.frameon": False,
}
EXPOSANTS = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def fr(x, dec=0):
    """Nombre au format français : espace pour les milliers, virgule décimale."""
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")


def sci(x, dec=1):
    """1.2e-11 -> « 1,2×10⁻¹¹ »."""
    m, e = f"{x:.{dec}e}".split("e")
    return f"{m.replace('.', ',')}×10{str(int(e)).translate(EXPOSANTS)}"


def titre(fig, t, sous, largeur=118):
    fig.text(0.015, 0.975, t, fontsize=14, fontweight="bold", color=INK, va="top")
    fig.text(0.015, 0.925, textwrap.fill(sous, largeur), fontsize=9.5, color=INK2, va="top", linespacing=1.35)


def pied(fig, d, extra=""):
    T = d["config"].get("T_MAX", "?")
    fig.text(0.015, 0.012, f"Run T={T} · source : journal du run · {extra}".strip(" ·"), fontsize=8, color=INK3, va="bottom")


# ----------------------------------------------------------------------------------------------------------------
#  Tracés sur des axes fournis (réutilisés par la fenêtre en direct)
# ----------------------------------------------------------------------------------------------------------------
def tracer_progression(a1, a2, d):
    """a1 : zéros cumulés par worker ; a2 : débit du pool (fenêtres de 5 s) et de W0 seul. Retourne False si rien à tracer."""
    c = courbes_workers(d)
    if not c:
        return False
    fins = sorted(c, key=lambda w: c[w][-1][0])
    for rang, w in enumerate(fins):
        pts = c[w]
        col = RAMPE_BLEUE[w % 8]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        a1.plot(xs, ys, color=col, lw=2, solid_capstyle="round")
        a1.plot(xs[-1:], ys[-1:], "o", color=col, ms=6, mec=SURFACE, mew=1.5)
        a1.annotate(f"W{w}", (xs[-1], ys[-1]), xytext=(0, 8 + 11 * (rang % 2)), textcoords="offset points",
                    fontsize=8.5, color=INK2, ha="center")
    a1.set_ylim(0, max(max(p[1] for p in v) for v in c.values()) * 1.13 + 1)
    a1.text(0.015, 0.95, "W0 (clair) → W7 (foncé) : segments de t croissants", transform=a1.transAxes,
            fontsize=8.5, color=INK2, va="top")
    a1.set_ylabel("zéros trouvés (cumul)")
    a1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, p: fr(v)))
    # débit : chaque point = 1000 zéros ; fenêtres de 5 s sur l'ensemble des workers
    brut = courbes_workers(d, avec_fin=False)
    larg = 5.0
    tmax = max(p[-1][0] for p in c.values())
    nb = int(tmax // larg) + 1
    tot = [0] * nb
    for pts in brut.values():
        for s_, _n in pts:
            tot[int(s_ // larg)] += 1000
    xs = [(i + 0.5) * larg for i in range(nb)]
    ys = [v / larg for v in tot]
    couvert = tmax - (nb - 1) * larg                      # v1.3 : la dernière fenêtre est incomplète
    if nb > 1 and couvert < 2.5:
        xs, ys, nb = xs[:-1], ys[:-1], nb - 1             # trop courte pour être fiable : retirée
    elif nb > 1:
        xs[-1] = (nb - 1) * larg + couvert / 2.0
        ys[-1] = tot[nb - 1] / couvert                    # normalisée par la durée réellement couverte
    a2.plot(xs, ys, color=CAT[0], lw=2.2)
    if any(ys):
        i_max = max(range(nb), key=lambda i: ys[i])
        a_gauche = xs[i_max] > 0.5 * tmax * 1.05                 # v1.1 : le texte reste dans le cadre
        a2.annotate(f"pic du pool : {fr(ys[i_max])} zéros/s", (xs[i_max], ys[i_max]),
                    xytext=((-215 if a_gauche else 14), -4),
                    textcoords="offset points", fontsize=9, color=INK,
                    arrowprops=dict(arrowstyle="-", color=INK3, lw=0.8))
    if 0 in brut and len(brut[0]) >= 2:
        p0 = brut[0]
        vx = [t1 for (t0, n0), (t1, n1) in zip(p0[:-1], p0[1:])]
        vy = [(n1 - n0) / (t1 - t0) for (t0, n0), (t1, n1) in zip(p0[:-1], p0[1:])]
        a2.plot(vx, vy, color=RAMPE_BLEUE[0], lw=1.8)
        a2.text(0.60, 0.08, "W0 seul (courbe claire)", transform=a2.transAxes, fontsize=8.5, color=INK2, ha="center")
    a2.text(0.45, 0.40, "pool entier\n(courbe foncée)", transform=a2.transAxes, fontsize=8.5, color=INK2, ha="center")
    a2.set_ylabel("débit (zéros/s)")
    a2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, p: fr(v)))
    a2.set_xlabel("temps depuis le lancement du worker (s)")
    a2.set_xlim(0, tmax * 1.05)
    a2.set_ylim(bottom=0)
    return True


def tracer_gantt(ax, d):
    c = courbes_workers(d)
    if not c:
        return False
    t_run = d["resultat"].get("duree_s")
    rc = courbes_rescan(d)
    lignes = []
    for w in sorted(c):
        fini = w in d["workers"]
        fin = d["workers"][w]["temps_s"] if fini else c[w][-1][0]
        lignes.append(dict(nom=f"W{w}", t0=0.0, det=c[w][0][0], fin=fin, fini=fini,
                           attente=(t_run if (fini and t_run) else fin),
                           note=(str(d["workers"][w]["fallback"]) if fini else "")))
    if t_run:
        fin_rescan = d["rescan_duree_s"]
        for w in sorted(rc):
            fin = rc[w][-1][0]
            lignes.append(dict(nom=f"R{w - 100}", t0=t_run, det=t_run + rc[w][0][0], fin=t_run + fin, fini=bool(fin_rescan),
                               attente=t_run + (fin_rescan or fin), note="rescan %d · %s s" % (w - 100, fr(fin, 1))))
    n = len(lignes)
    for i, L in enumerate(lignes):
        y = n - 1 - i
        h = 0.62
        ax.barh(y, L["det"] - L["t0"], left=L["t0"], height=h, color=CAT[0], edgecolor=SURFACE, lw=1.5)
        ax.barh(y, L["fin"] - L["det"], left=L["det"], height=h, color=CAT[2], edgecolor=SURFACE, lw=1.5)
        if L["attente"] > L["fin"] + 0.5:
            ax.barh(y, L["attente"] - L["fin"], left=L["fin"], height=h, color=GRIS, edgecolor=SURFACE, lw=1.5,
                    hatch="///", alpha=0.7)
        if L["fini"]:
            if (L["fin"] - L["det"]) >= 0.11 * max(l_["attente"] for l_ in lignes):    # v1.3 : assez de place dans la barre ?
                ax.text(L["fin"] - 2, y, fr(L["fin"] - L["t0"], 1) + " s", va="center", ha="right", fontsize=8, color=SURFACE)
            elif not L["note"].startswith("rescan"):
                ax.text(max(L["attente"], L["fin"]) + 3, y, fr(L["fin"] - L["t0"], 1) + " s", va="center", ha="left", fontsize=8, color=INK2)
        if L["note"]:
            ax.text(1.01, y, L["note"], transform=ax.get_yaxis_transform(), va="center", fontsize=8.5, color=INK2)
    ax.text(1.01, 1.005, "appels mpmath\nde secours", transform=ax.transAxes, fontsize=8, color=INK3, va="bottom")
    ax.set_yticks(range(n))
    ax.set_yticklabels([L["nom"] for L in reversed(lignes)])
    ax.set_ylim(-0.6, n - 0.4)
    if t_run:
        ax.axvline(t_run, color=INK3, lw=1, ls="--")
        ax.text(t_run + 2, n - 0.5, f"fin du run principal\n{fr(t_run, 1)} s", fontsize=8.5, color=INK2, va="top")
    ax.set_xlabel("temps (s)")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, max(max(L["attente"], L["fin"]) for L in lignes) * 1.04)
    ax.legend(handles=[Patch(color=CAT[0], label="détection + 1er millier"), Patch(color=CAT[2], label="affinage des zéros"),
                       Patch(facecolor=GRIS, hatch="///", label="attend les autres")],
              loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=3, fontsize=8, handlelength=1.4, columnspacing=1.0)
    return True


def blocs_ms(courbes):
    """Durées (ms par zéro) de chaque bloc de 1000 zéros ; le 1er point de chaque worker n'est pas un bloc."""
    out = []
    for pts in courbes.values():
        for (t0, n0), (t1, n1) in zip(pts[:-1], pts[1:]):
            if n1 - n0 >= 999 and t1 > t0:
                out.append((t1 - t0) / (n1 - n0) * 1000.0)
    return out


def tracer_hist(axes, d):
    """axes : [haut, bas] (run principal / rescan) ou [un seul axe] (les deux superposés)."""
    p1 = blocs_ms(courbes_workers(d, avec_fin=False))
    r1 = blocs_ms(courbes_rescan(d))
    if not p1:
        return False
    mx = max(p1 + r1)
    larg = 0.25
    bords = [i * larg for i in range(int(math.ceil(mx / larg)) + 2)]
    series = [(p1, CAT[0], "run principal : 8 workers pour 4 cœurs"), (r1, CAT[1], "rescan : 2 processus pour 4 cœurs")]
    if len(axes) == 1:
        axes = [axes[0], axes[0]]
    for k, (ax, (data, col, nom)) in enumerate(zip(axes, series)):
        if not data:
            continue
        ax.hist(data, bins=bords, color=col, edgecolor=SURFACE, linewidth=1.5, alpha=0.9)
        med = statistics.median(data)
        ax.axvline(med, color=col if axes[0] is axes[1] else INK, lw=1.3, ls="--")
        y_txt = 0.70 if axes[0] is not axes[1] else 0.56 - 0.09 * k      # v1.2 : sous les descriptions (pas de collision)
        droite = med > 0.5 * ax.get_xlim()[1]                       # v1.1 : étiquette du côté libre
        ax.text(med + (-0.08 if droite else 0.08), y_txt, f"médiane {fr(med, 2)} ms/zéro",
                transform=ax.get_xaxis_transform(), fontsize=9, color=INK, va="top", ha=("right" if droite else "left"))
        ax.set_ylabel("nombre de blocs")
        ax.text(0.99, 0.95 - (0.0 if axes[0] is not axes[1] else 0.22 * k), f"{nom}\n{len(data)} blocs · min {fr(min(data), 2)} · max {fr(max(data), 2)} ms",
                transform=ax.transAxes, ha="right", va="top", fontsize=8.5, color=INK2)
    axes[-1].set_xlabel("ms par zéro (durée du bloc de 1000 / 1000)")
    return True


def tracer_lmfdb(ax, d):
    L = d["lmfdb"]
    if not L:
        return False
    seuil, plancher, seuil_t = 1e-9, 1e-15, 65.0
    for i, (r, calc, ref, ec) in enumerate(L):
        col = CAT[0] if calc < seuil_t else CAT[1]
        if ec <= 0:
            ax.plot([i], [plancher * 3], marker="o", ms=7, mfc=SURFACE, mec=col, mew=1.8)
        else:
            ax.bar(i, ec - plancher, bottom=plancher, width=0.72, color=col, edgecolor=SURFACE, linewidth=1.5)
            if ec > 1e-12:
                ax.text(i, ec * 1.5, sci(ec), ha="center", fontsize=7.5, color=INK2)
    ax.set_yscale("log")
    ax.set_ylim(plancher, 1e-8)
    ax.axhline(seuil, color=INK2, lw=1.2, ls="--")
    ax.text(-0.4, seuil * 1.5, "seuil du contrôle : 10⁻⁹", ha="left", fontsize=9, color=INK2)
    ax.set_xticks(range(len(L)))
    ax.set_xticklabels([f"{r}\n{fr(c, 1)}" for r, c, _, _ in L], fontsize=8)
    ax.set_xlabel("rang du zéro (haut) et t (bas)")
    ax.set_ylabel("écart absolu")
    ax.legend(handles=[Patch(color=CAT[0], label="t < 65"), Patch(color=CAT[1], label="t ≥ 65"),
                       Line2D([], [], marker="o", ls="", mfc=SURFACE, mec=INK2, mew=1.6, label="écart affiché 0,00")],
              loc="upper left", fontsize=9, ncol=3)
    pire = max(L, key=lambda x: x[3])
    ax.annotate(f"pire écart : zéro n°{pire[0]}, {sci(pire[3], 2)} ({fr(pire[3] / seuil * 100)} % du seuil)",
                (pire[0] - 1 - 0.36, pire[3] * 0.8), xytext=(-290, -70), textcoords="offset points", fontsize=9, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK3, lw=0.8))
    return True


def tracer_completude(a1, a2, d):
    S, Tg = d["rescan_segments"], d["turing"]
    if not S and not Tg:
        return False
    if S:
        for i, (seg, a, b, tr, at) in enumerate(S):
            ec = tr - at
            if ec == 0:
                a1.plot([i], [0], marker="_", ms=22, mew=3, color=CAT[0])
            else:
                a1.bar(i, ec, width=0.62, color=CAT[1] if ec < 0 else CAT[0], edgecolor=SURFACE, linewidth=1.5)
            a1.text(i, ec + (0.12 if ec >= 0 else -0.12), ("+" if ec > 0 else "") + str(ec).replace("-", "−"),
                    ha="center", va="bottom" if ec >= 0 else "top", fontsize=9, color=INK)
        a1.axhline(0, color=INK2, lw=1)
        a1.set_xticks(range(len(S)))
        a1.set_xticklabels([f"Seg {s[0]}\n{fr(s[1] / 1000, 0)}→{fr(s[2] / 1000, 0)} k" for s in S], fontsize=8)
        a1.set_ylabel("trouvés − attendus (zéros)")
        a1.set_ylim(min(-2, min(s[3] - s[4] for s in S) - 1), max(2, max(s[3] - s[4] for s in S)) + 1)
        a1.grid(axis="x", visible=False)
        a1.legend(handles=[Patch(color=CAT[0], label="surplus ou égal : pas de rescan"),
                           Patch(color=CAT[1], label="déficit : rescan à pas fin")],
                  loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=8.5)
        if d.get("rescan_net") is not None:
            a1.text(0.99, 0.04, f"rescan : +{d['rescan_net']} zéro net après déduplication", transform=a1.transAxes,
                    ha="right", fontsize=9, color=INK2)
    if Tg:
        xs = [t[0] / 1000 for t in Tg]
        ys = [t[1] - t[2] for t in Tg]
        for x, y in zip(xs, ys):
            a2.plot([x, x], [0, y], color=CAT[0], lw=2.2)
        a2.plot(xs, ys, "o", ms=8, color=CAT[0], mec=SURFACE, mew=1.5)
        for x, y in zip(xs, ys):
            a2.text(x, y + 0.14, ("+" if y > 0 else "") + str(y), ha="center", fontsize=9, color=INK)
        a2.axhline(0, color=INK2, lw=1)
        a2.set_xlabel("T du point de contrôle (milliers)")
        a2.set_ylabel("calculés − attendus (zéros)")
        a2.set_ylim(-1, max(ys + [2]) + 1)
        a2.set_title("Turing-Backlund", fontsize=10, color=INK2, loc="left")
        a2.text(0.99, 0.04, "dernier point : écart %d" % ys[-1], transform=a2.transAxes, ha="right", fontsize=9, color=INK2)
    return True


# ----------------------------------------------------------------------------------------------------------------
#  Les six graphiques en fichiers PNG
# ----------------------------------------------------------------------------------------------------------------
def _sauver(fig, dossier, nom):
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, nom + ".png")
    fig.savefig(chemin, dpi=140)
    print("écrit :", chemin)
    return chemin


def png_1(d, dossier):
    fig = Figure(figsize=(10.5, 7.4))
    a1, a2 = fig.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": [1.2, 1]})
    fig.subplots_adjust(left=0.085, right=0.93, top=0.84, bottom=0.09, hspace=0.12)
    titre(fig, "Progression de chaque worker (run principal)",
          "Haut : zéros écrits au journal, un point par millier. Bas : débit du pool, calculé en fenêtres de 5 s. "
          "Avant le 1er point d'une courbe : détection, puis affinage des 1000 premiers zéros.")
    if not tracer_progression(a1, a2, d):
        print("graphique 1 sauté : aucune ligne « zéro #N » dans le journal"); return None
    pied(fig, d, "8 workers sur 4 cœurs logiques")
    return _sauver(fig, dossier, "g1_progression")


def png_2(d, dossier):
    fig = Figure(figsize=(10.8, 6.4))
    ax = fig.subplots()
    fig.subplots_adjust(left=0.07, right=0.86, top=0.82, bottom=0.12)
    titre(fig, "Chronologie du run : qui travaille, quand",
          "« détection » = jusqu'au 1er millier de zéros écrit (borne). Le rescan (R) est placé à la fin du run principal : "
          "début estimé (le journal ne le date pas).")
    if not tracer_gantt(ax, d):
        print("graphique 2 sauté : aucune progression"); return None
    pied(fig, d, "durées écrites dans les barres = fin de chaque worker")
    return _sauver(fig, dossier, "g2_gantt")


def png_3(d, dossier):
    p = d["profil"]
    if not p:
        print("graphique 3 sauté : pas de bloc [PROFIL PHASES] (run non terminé ?)"); return None
    ordre = ["detection", "arb_C", "mpmath_fallback", "turing", "mpmath_petit_t"]
    noms = {"detection": "détection", "arb_C": "affinage Arb (arb_C)", "mpmath_fallback": "mpmath de secours",
            "turing": "validation Turing", "mpmath_petit_t": "mpmath petit t"}
    cles = [k for k in ordre if k in p]
    vals = [p[k]["pct_mur_W"] for k in cles]
    reste = max(0.0, 100.0 - sum(vals))
    W = d["config"].get("N_WORKERS", 8)
    mur = None
    if "detection" in p and p["detection"]["pct_mur_W"] > 0:
        mur = p["detection"]["cumul_s"] / (p["detection"]["pct_mur_W"] / 100.0) / W
    fig = Figure(figsize=(10.5, 6.0))
    ax = fig.add_axes([0.03, 0.06, 0.45, 0.78])
    couleurs = CAT[:len(cles)] + [GRIS]
    ax.pie(vals + [reste], colors=couleurs, startangle=90, counterclock=False,
           wedgeprops=dict(width=0.40, edgecolor=SURFACE, linewidth=2.5))
    ax.set(aspect="equal")
    if mur:
        ax.text(0, 0.07, f"≈ {fr(mur)} s", ha="center", fontsize=17, fontweight="bold", color=INK)
        ax.text(0, -0.12, f"× {W} workers", ha="center", fontsize=10, color=INK2)
        ax.text(0, -0.27, "(calculé)", ha="center", fontsize=8.5, color=INK3)
    titre(fig, "Où passe le temps des workers ?",
          "Part du « mur × workers » (journal, profil des phases). La part grise = 100 % − somme des phases (calculé) : "
          "cœurs inactifs ou temps non compté.")
    y = 0.70
    fig.text(0.53, y + 0.07, "phase", fontsize=9, color=INK3)
    fig.text(0.83, y + 0.07, "cumul", fontsize=9, color=INK3, ha="right")
    fig.text(0.95, y + 0.07, "part", fontsize=9, color=INK3, ha="right")
    for i, k in enumerate(cles + ["reste"]):
        yy = y - i * 0.085
        fig.patches.append(Rectangle((0.53, yy - 0.012), 0.016, 0.03, transform=fig.transFigure, color=couleurs[i]))
        if k == "reste":
            fig.text(0.56, yy, "inactif / non compté", fontsize=10.5, color=INK, va="center")
            fig.text(0.95, yy, fr(reste, 1) + " %", fontsize=10.5, color=INK, va="center", ha="right")
        else:
            fig.text(0.56, yy, noms[k], fontsize=10.5, color=INK, va="center")
            fig.text(0.83, yy, fr(p[k]["cumul_s"], 1) + " s", fontsize=10.5, color=INK2, va="center", ha="right")
            fig.text(0.95, yy, fr(p[k]["pct_mur_W"], 1) + " %", fontsize=10.5, color=INK, va="center", ha="right")
    if "arb_C" in p and "mpmath_fallback" in p:
        fig.text(0.53, y - 6 * 0.085 - 0.02, "arb_C : %s appels à %s ms\nmpmath de secours : %s appels à %s ms"
                 % (fr(p["arb_C"]["appels"]), fr(p["arb_C"]["ms_appel"], 2), fr(p["mpmath_fallback"]["appels"]),
                    fr(p["mpmath_fallback"]["ms_appel"], 2)), fontsize=8.5, color=INK3, va="top")
    pied(fig, d)
    return _sauver(fig, dossier, "g3_anneau_phases")


def png_4(d, dossier):
    r1 = blocs_ms(courbes_rescan(d))
    fig = Figure(figsize=(10.2, 6.6 if r1 else 4.2))
    axes = list(fig.subplots(2 if r1 else 1, 1, sharex=True)) if r1 else [fig.subplots()]
    fig.subplots_adjust(left=0.085, right=0.96, top=0.82, bottom=0.10, hspace=0.18)
    titre(fig, "Combien de temps pour affiner 1000 zéros ?",
          "Un bloc = deux lignes « zéro #N » consécutives d'un même worker, converti en ms par zéro. "
          "Le 1er point de chaque worker est exclu (il contient la détection).")
    if not tracer_hist(axes, d):
        print("graphique 4 sauté : pas assez de lignes de progression"); return None
    pied(fig, d, "queue vers la droite = concurrence entre workers pour les 4 cœurs (déduit)")
    return _sauver(fig, dossier, "g4_histogramme_blocs")


def png_5(d, dossier):
    fig = Figure(figsize=(10.5, 5.8))
    ax = fig.subplots()
    fig.subplots_adjust(left=0.085, right=0.96, top=0.82, bottom=0.17)
    titre(fig, "Précision sur les 20 premiers zéros (référence LMFDB)",
          "Écart |calculé − LMFDB| par zéro, échelle log. Un écart affiché 0,00 est tracé sur le plancher (sous la résolution "
          "d'affichage). Les 14 zéros de t < 65 sont ceux du chemin mpmath « petit t » (déduit : 14 zéros comptés, seuil 65).")
    if not tracer_lmfdb(ax, d):
        print("graphique 5 sauté : pas de bloc « Vérification LMFDB »"); return None
    L = d["lmfdb"]
    pied(fig, d, "score du contrôle : %d zéros sur %d sous le seuil" % (sum(1 for x in L if x[3] < 1e-9), len(L)))
    return _sauver(fig, dossier, "g5_precision_lmfdb")


def png_6(d, dossier):
    fig = Figure(figsize=(11.2, 5.4))
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.5, 1]})
    fig.subplots_adjust(left=0.07, right=0.97, top=0.78, bottom=0.17, wspace=0.28)
    titre(fig, "Complétude : trouvés − attendus",
          "Gauche : par segment de t (une barre sous zéro déclenche le rescan). Droite : points de contrôle de la validation "
          "Turing-Backlund (cumul depuis t = 0).")
    if not tracer_completude(a1, a2, d):
        print("graphique 6 sauté : ni comptage par segment ni points de Turing"); return None
    pied(fig, d, "le surplus est compatible avec les fluctuations de S(T) (heuristique, non prouvé)")
    return _sauver(fig, dossier, "g6_completude")


GRAPHES = {1: png_1, 2: png_2, 3: png_3, 4: png_4, 5: png_5, 6: png_6}


def ecrire_pngs(d, dossier, numeros=(1, 2, 3, 4, 5, 6)):
    """Écrit les PNG demandés dans `dossier` ; retourne la liste des fichiers écrits."""
    out = []
    with matplotlib.rc_context(STYLE):
        for g in numeros:
            try:
                p = GRAPHES[g](d, dossier)
            except Exception as e:                      # un graphique raté ne doit pas empêcher les autres
                print("graphique %d en erreur : %s" % (g, e))
                p = None
            if p:
                out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("journal", nargs="?", default="auto")
    ap.add_argument("--graphes", default="1,2,3,4,5,6")
    ap.add_argument("--sortie", default=None, help="dossier des PNG (défaut : figures/ du run, lu dans le journal)")
    ap.add_argument("--logs", default=None, help="dossier des journaux pour « auto » (défaut : ~/projet_zeta/logs)")
    a = ap.parse_args()
    chemin = trouver_journal(a.logs) if a.journal == "auto" else os.path.expanduser(a.journal)
    if not chemin or not os.path.isfile(chemin):
        print("Aucun journal run_T*.log trouvé."); sys.exit(1)
    d = lire_journal(chemin)
    dossier = a.sortie or dossier_figures(d)
    print("Journal :", chemin)
    if not d["termine"]:
        print("Attention : le journal ne semble pas terminé ; les graphiques de fin de run peuvent manquer.")
    fichiers = ecrire_pngs(d, dossier, [int(x) for x in a.graphes.split(",") if x.strip()])
    print("%d graphique(s) dans %s" % (len(fichiers), dossier))


if __name__ == "__main__":
    main()
