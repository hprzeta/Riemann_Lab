#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""zeta_log_live.py (v1.2) — fenêtre en direct du journal d'un run (alias zeta-log-live).

Usage :
    python3 -I zeta_log_live.py [JOURNAL | auto] [--attendre] [--refresh 2] [--logs DOSSIER]
                                [--sortie DOSSIER] [--sans-png]

Comme zeta-proc-plot : lecture seule, fenêtre rafraîchie toutes les 2 s. Quatre panneaux tirés des lignes du journal
(« [Worker k] zéro #N à t=… — … s », une ligne toutes les 1000 zéros) :
    progression de chaque worker · débit du pool · chronologie (Gantt) · histogramme du temps pour 1000 zéros.
--attendre : à lancer AVANT le run ; la fenêtre attend l'apparition d'un nouveau journal run_T*.log, puis le suit.
Sans --attendre : suit le journal le plus récent (en cours ou terminé).
À la fin du run (ligne « v16 terminée »), les 6 graphiques PNG sont écrits une fois dans
    monitoring/runs/prod/<run>/figures/   (sauf --sans-png), comme avec zeta-log-graph.

Remarque : pendant la détection (de l'ordre de 90 à 160 s au début d'un run T=200000) le journal n'a pas encore de
ligne de progression : la fenêtre l'indique et attend.
"""
import argparse, datetime, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))     # nécessaire avec python -I
import zeta_log_graphes as zg


def phase_du_run(d):
    """Phase lue dans le journal : pool 1, rescan, validation (v1.2)."""
    if d["termine"]:
        return "TERMINÉ"
    if d["rescan_duree_s"] is not None:
        return "rescan terminé — validation et écriture en cours"
    if any(w >= 100 for (w, _n, _t, _s) in d["progression"]) or d["resultat"].get("duree_s"):
        return "rescan en cours (le pool 1 est terminé)"
    return "pool 1 en cours"


def zeros_ecrits(d):
    """Zéros déjà écrits au journal (par pas de 1000), run principal : dernier point de chaque worker."""
    dern = {}
    for w, n, t, s in d["progression"]:
        if w < 100 and n >= dern.get(w, 0):
            dern[w] = n
    for w, v in d["workers"].items():
        if w < 100:                                   # v1.1 : exclut les processus du rescan (sinon > 100 %)
            dern[w] = v["zeros"]
    return sum(dern.values())


def dessiner(fig, axes, d, info):
    """Redessine les quatre panneaux. `info` : dict(etat=..., age=...)."""
    a1, a2, ag, ah = axes
    for ax in axes:
        ax.cla()
    for extra in [x for x in fig.axes if x not in axes]:
        extra.remove()
    T = d["config"].get("T_MAX", "?")
    attendus = d["config"].get("N_zeros_attendus")
    n = zeros_ecrits(d)
    dernier = max([p[3] for p in d["progression"]] or [0])
    if not d["progression"]:
        for ax in axes:
            ax.set_axis_off()
        fig.texts[:] = []
        fig.text(0.5, 0.52, "En attente des premières lignes « zéro #N »…\n"
                 "(détection en cours : de l'ordre de 90 à 160 s au début d'un run T=200000)",
                 ha="center", va="center", fontsize=13, color=zg.INK2)
        fig.text(0.015, 0.975, f"Journal du run T={T} — {info['etat']}", fontsize=13, fontweight="bold", va="top", color=zg.INK)
        return
    for ax in axes:
        ax.set_axis_on()
    zg.tracer_progression(a1, a2, d)
    zg.tracer_gantt(ag, d)
    zg.tracer_hist([ah], d)
    for ax, t in ((a1, "Progression par worker"), (a2, "Débit"), (ah, "Temps pour 1000 zéros")):
        ax.set_title(t, loc="left", fontsize=10, color=zg.INK2)
    fig.texts[:] = []
    part = f" — {zg.fr(n)} zéros écrits sur ≈ {zg.fr(attendus)} ({n / attendus * 100:.0f} %, par pas de 1000)" if attendus else ""
    fig.text(0.015, 0.975, f"Journal du run T={T} — {info['etat']}", fontsize=13, fontweight="bold", va="top", color=zg.INK)
    fig.text(0.015, 0.935, f"dernier point écrit à {zg.fr(dernier, 1)} s du lancement{part}", fontsize=9.5, va="top", color=zg.INK2)
    if info.get("note"):
        fig.text(0.90, 0.012, info["note"], fontsize=8.5, ha="right", va="bottom", color=zg.INK3)


def creer_figure(plt):
    fig = plt.figure(figsize=(14.5, 8.4))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 1], height_ratios=[1.15, 1], left=0.06, right=0.90,
                          top=0.84, bottom=0.11, wspace=0.36, hspace=0.30)
    a1 = fig.add_subplot(gs[0, 0])
    a2 = fig.add_subplot(gs[1, 0], sharex=a1)
    ag = fig.add_subplot(gs[0, 1])
    ah = fig.add_subplot(gs[1, 1])
    return fig, (a1, a2, ag, ah)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("journal", nargs="?", default="auto")
    ap.add_argument("--attendre", action="store_true", help="attendre l'apparition d'un nouveau journal")
    ap.add_argument("--refresh", type=float, default=2.0)
    ap.add_argument("--logs", default=None)
    ap.add_argument("--sortie", default=None, help="dossier des PNG de fin de run")
    ap.add_argument("--sans-png", action="store_true", help="ne pas écrire les PNG à la fin")
    a = ap.parse_args()
    debut = time.time()

    chemin = None
    if a.journal != "auto":
        chemin = os.path.expanduser(a.journal)
        if not os.path.isfile(chemin):
            print("Journal introuvable :", chemin); sys.exit(1)
    else:
        annonce = False
        while True:
            chemin = zg.trouver_journal(a.logs, apres=(debut - 2) if a.attendre else None)
            if chemin or not a.attendre:
                break
            if not annonce:
                print("En attente d'un nouveau journal run_T*.log (Ctrl+C pour annuler)...", flush=True)
                annonce = True
            time.sleep(a.refresh)
        if not chemin:
            print("Aucun journal run_T*.log trouvé."); sys.exit(1)
    print("Journal suivi :", chemin, flush=True)

    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    with matplotlib.rc_context(zg.STYLE):
        fig, axes = creer_figure(plt)
    try:
        fig.canvas.manager.set_window_title("zeta_log_live — " + os.path.basename(chemin))
    except Exception:
        pass
    etat = {"sig": None, "png": False, "t_fin": None, "dernier_changement": time.time()}

    def tour(_):
        try:
            st = os.stat(chemin)
        except OSError:
            return
        sig = (st.st_mtime, st.st_size)
        change = sig != etat["sig"]
        if change:
            etat["sig"] = sig
            etat["dernier_changement"] = time.time()
        # on ne relit que si le fichier a changé, au premier tour, ou tant que les PNG de fin ne sont pas écrits
        if not (change or not etat.get("dessine") or (etat["t_fin"] is not None and not etat["png"] and not a.sans_png)):
            if time.time() - etat["dernier_changement"] < 180 or etat.get("alerte"):
                return
            etat["alerte"] = True                  # une seule fois : afficher « sans nouvelle ligne »
        try:
            d = zg.lire_journal(chemin)
        except Exception:
            return
        silence = time.time() - etat["dernier_changement"]
        if d["termine"]:
            libelle, note = "TERMINÉ", ""
            if etat["t_fin"] is None:
                etat["t_fin"] = time.time()
            if not a.sans_png and not etat["png"] and (d["dossier_suivi"] or time.time() - etat["t_fin"] > 30):
                dossier = a.sortie or zg.dossier_figures(d)
                fichiers = zg.ecrire_pngs(d, dossier)
                etat["png"] = True
                etat["note"] = "%d PNG écrits dans %s" % (len(fichiers), dossier)
                print(etat["note"], flush=True)
            note = etat.get("note", "PNG de fin de run : en attente du dossier de suivi…" if not a.sans_png else "")
        else:
            libelle = phase_du_run(d) if silence < 180 else "sans nouvelle ligne depuis %.0f s (run interrompu ?)" % silence
            note = ""
        with matplotlib.rc_context(zg.STYLE):
            dessiner(fig, axes, d, {"etat": libelle, "note": note})
        etat["dessine"] = True

    anim = FuncAnimation(fig, tour, interval=int(a.refresh * 1000), cache_frame_data=False)
    fig._anim = anim
    plt.show()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
