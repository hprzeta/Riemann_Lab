#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""zeta_plot_proc.py (v2) — graphique en direct des processus d'un run, avec les repères du journal.

Lit les fichiers écrits par zeta_proc_sample.py (zeta-proc) :
    proc_<date>_global.csv   une ligne par échantillon (CPU total, workers actifs, mémoire, load, swap)
    proc_<date>.csv          une ligne par processus et par échantillon

Usage :
    python3 -I zeta_plot_proc.py [CSV_GLOBAL | DOSSIER] [--refresh 2] [--apres "AAAA-MM-JJ HH:MM:SS"]
                                 [--sortie image.png] [--min-echantillons 3]

Comme zeta-live : prend le fichier le plus récemment modifié, lecture incrémentale (seules les lignes
nouvelles sont lues), rafraîchissement toutes les 2 s, rien d'affiché avant 3 échantillons.
Avec --sortie, écrit une image PNG une fois (sans fenêtre) puis s'arrête.

Trois graphiques empilés :
  1. CPU de chaque processus (100 % = un cœur logique) : on voit les workers finir un à un ;
  2. workers actifs (≥ 20 % CPU) et cœurs occupés, avec la « phase finale » ombrée quand au plus un
     processus travaille alors que d'autres cœurs sont libres ;
  3. mémoire résidente totale (Mo) et load average (échelle de droite).
Nouveauté v2 : --journal auto|CHEMIN|non (défaut auto). Le journal du run (logs/run_T*.log) fournit des REPÈRES
superposés aux trois graphiques : fin de chaque worker du pool 1 (W0 à W7), début et fin du rescan.
  - auto : prend le journal dont la date de dernière modification est la plus proche de la fin du CSV (±15 min) ;
  - CHEMIN : un journal précis ; non : aucun repère (comportement v1).
Alignement des horloges : le CSV compte depuis la détection du run, le journal depuis le lancement des workers.
Les 8 PIDs du pool 1 disparaissent TOUS ENSEMBLE (mesuré au cas 1.5) : on ne peut donc pas les aligner sur leur mort. On
utilise la dernière seconde où chaque worker a travaillé (CPU >= 20 %), triée, comparée aux fins du journal triées ;
décalage = médiane des écarts, incertitude = écart maximal à cette médiane (affichée dans le titre).
Avec --sortie auto, le PNG est écrit dans <dossier de suivi du run>/figures/ (comme zeta-log-graph).
Lecture seule. Bibliothèques : numpy et matplotlib (+ zeta_log_graphes.py, dans le même dossier, pour lire le journal).
"""
import argparse, datetime, glob, os, statistics, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))     # nécessaire avec python -I
try:
    import zeta_log_graphes as zg                                    # lecture du journal (facultatif)
except Exception:                                                    # absent ou matplotlib indisponible : pas de repères
    zg = None

SEUIL_ACTIF = 20.0          # % CPU à partir duquel un processus est « actif » (même seuil que zeta-proc)


def trouver_global(cible, apres):
    """Retourne le fichier *_global.csv demandé, ou le plus récent d'un dossier (modifié après `apres`)."""
    if cible and os.path.isfile(cible):
        return cible
    dossier = cible or os.path.expanduser("~/zeta_captures")
    fichiers = sorted(glob.glob(os.path.join(dossier, "proc_*_global.csv")), key=os.path.getmtime)
    if apres is not None:
        fichiers = [f for f in fichiers if os.path.getmtime(f) >= apres]
    return fichiers[-1] if fichiers else None


class Suivi:
    """Lecture incrémentale d'un CSV qui grossit : on garde la position et on ne lit que les lignes complètes."""

    def __init__(self, chemin):
        self.chemin, self.pos, self.entete = chemin, 0, None

    def nouvelles_lignes(self):
        if not os.path.exists(self.chemin):
            return []
        with open(self.chemin, "rb") as f:
            f.seek(self.pos)
            brut = f.read()
        fin = brut.rfind(b"\n")
        if fin < 0:
            return []                                    # ligne en cours d'écriture : on attend
        self.pos += fin + 1
        lignes = brut[:fin].decode("utf-8", "replace").split("\n")
        if self.entete is None and lignes:
            self.entete = lignes.pop(0)
        return [l for l in lignes if l.strip()]


class Donnees:
    def __init__(self, global_csv):
        self.sg = Suivi(global_csv)
        self.sp = Suivi(global_csv[:-len("_global.csv")] + ".csv")
        self.g = {k: [] for k in ("t", "epoch", "cpu", "actifs", "rss", "load", "mem", "swap")}
        self.p = {}                                      # pid -> ([t], [cpu])
        self.ordre = []                                  # pid dans l'ordre d'apparition
        self.ppid = {}                                   # pid -> ppid

    def maj(self):
        for l in self.sg.nouvelles_lignes():
            v = l.split(",")
            try:
                for k, x in zip(self.g, v):
                    self.g[k].append(float(x))
            except ValueError:
                pass
        for l in self.sp.nouvelles_lignes():
            v = l.split(",", 7)
            try:
                t, pid, cpu = float(v[0]), int(v[1]), float(v[4])
            except (ValueError, IndexError):
                continue
            if pid not in self.p:
                self.p[pid] = ([], [])
                self.ordre.append(pid)
                try:
                    self.ppid[pid] = int(v[2])
                except ValueError:
                    pass
            self.p[pid][0].append(t)
            self.p[pid][1].append(cpu)

    def n(self):
        return len(self.g["t"])


def phase_finale(actifs, ncpu):
    """Indice de début de la phase finale (au plus 1 actif en fin de série, après un pic ≥ 2), ou None."""
    if not actifs or max(actifs) < min(4, ncpu):
        return None
    i = len(actifs)
    while i > 0 and actifs[i - 1] <= 1:
        i -= 1
    return i if len(actifs) - i >= 2 and i > 0 else None


def choisir_journal(option, dossier_logs, epoch_fin):
    """Journal à utiliser : None (non / introuvable), ou chemin. `auto` = run_T*.log dont la date de modification est la
    plus proche de la fin du CSV, à ±15 minutes."""
    if zg is None or option == "non":
        return None
    if option != "auto":
        return os.path.expanduser(option) if os.path.isfile(os.path.expanduser(option)) else None
    dossier = os.path.expanduser(dossier_logs or "~/projet_zeta/logs")
    cand = [(abs(os.path.getmtime(f) - epoch_fin), f) for f in glob.glob(os.path.join(dossier, "run_T*.log"))]
    cand = [c for c in cand if c[0] <= 900]
    return min(cand)[1] if cand else None


def marqueurs(d, jr, intervalle):
    """Repères du journal dans l'horloge du CSV. Retourne None si l'alignement est impossible (pas encore de worker fini)."""
    if not jr or not d.g["t"]:
        return None
    nw = jr["config"].get("N_WORKERS") or 8
    enfants = [p for p in d.ordre if d.ppid.get(p) in d.p]            # fils d'un processus suivi
    pool1 = enfants[:nw]
    t_now = d.g["t"][-1]
    fins_csv = []
    for pid in pool1:
        tt, cc = d.p[pid]
        actifs = [i for i, c in enumerate(cc) if c >= SEUIL_ACTIF]
        if actifs and tt[actifs[-1]] <= t_now - 3 * intervalle:         # a fini de travailler (inactif depuis 3 pas)
            fins_csv.append(tt[actifs[-1]] - intervalle / 2.0)
    fins_j = sorted((v["temps_s"], w) for w, v in jr["workers"].items() if w < 100)
    fins_csv.sort()
    m = min(len(fins_csv), len(fins_j))
    if m == 0:
        return None
    ecarts = [fins_csv[i] - fins_j[i][0] for i in range(m)]
    off = statistics.median(ecarts)
    res = max(abs(e - off) for e in ecarts)
    out = dict(off=off, res=res, m=m, fins=[("W%d" % w, t + off) for t, w in fins_j], rescan_debut=None, rescan_fin=None,
               fin_principal=None)
    t_run = jr["resultat"].get("duree_s")
    if t_run:
        out["fin_principal"] = t_run + off
        out["rescan_debut"] = t_run + off                                # approximation : transition de 4 s environ (mesuré 1.5)
        if jr["rescan_duree_s"]:
            out["rescan_fin"] = t_run + jr["rescan_duree_s"] + off
    # naissance observée des processus du rescan (information de contrôle)
    nes = [d.p[p][0][0] for p in enfants[nw:]]
    out["rescan_naissance_csv"] = min(nes) if nes else None
    return out


def dessiner(plt, np, fig, axes, d, ncpu, intervalle, mk=None, nom_journal=None):
    a1, a2, a3 = axes
    for extra in [x for x in fig.axes if x not in (a1, a2, a3)]:
        extra.remove()                                   # supprime l'axe jumeau (load) avant de redessiner
    for ax in (a1, a2, a3):
        ax.cla()
    t = np.array(d.g["t"]); act = d.g["actifs"]
    couleurs = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    # 1. CPU par processus (seulement ceux qui ont déjà travaillé)
    k = 0
    for pid in d.ordre:
        tt, cc = d.p[pid]
        if max(cc) >= SEUIL_ACTIF:
            a1.plot(tt, cc, lw=1.1, color=couleurs[k % len(couleurs)], label=str(pid))
            k += 1
    a1.set_ylabel("CPU par processus (%)")
    a1.set_ylim(0, 145 if mk else 115)
    if 0 < k <= 12:
        a1.legend(ncol=4 if mk else 6, fontsize=7, loc="upper left" if mk else "upper right", title="PID", title_fontsize=7, framealpha=0.6)
    # 2. workers actifs et cœurs occupés
    a2.step(t, act, where="post", color="tab:red", lw=1.5, label="workers actifs (≥ 20 % CPU)")
    a2.plot(t, np.array(d.g["cpu"]) / 100.0, color="tab:blue", lw=1.2, label="cœurs occupés (CPU total / 100)")
    a2.axhline(ncpu, color="gray", ls="--", lw=0.8, label="cœurs logiques (%d)" % ncpu)
    deb = phase_finale(act, ncpu)
    texte = ""
    if deb is not None:
        a2.axvspan(t[deb], t[-1] + intervalle, color="orange", alpha=0.25, label="phase finale (≤ 1 actif)")
        texte = " — phase finale : %.0f s" % (t[-1] + intervalle - t[deb])
    a2.set_ylabel("workers / cœurs")
    a2.set_ylim(0, max(ncpu, max(act) if act else 1, max(d.g["cpu"]) / 100.0 if d.g["cpu"] else 1) * 1.15)
    a2.legend(fontsize=7, loc="upper right", ncol=2, framealpha=0.6)
    # 3. mémoire et load
    a3.plot(t, d.g["rss"], color="tab:green", lw=1.2, label="mémoire résidente totale (Mo)")
    a3.set_ylabel("Mo", color="tab:green"); a3.set_xlabel("temps depuis la détection du run (s)")
    b3 = a3.twinx()
    b3.plot(t, d.g["load"], color="tab:purple", lw=1.2, label="load average (1 min)")
    b3.set_ylabel("load", color="tab:purple")
    b3.axhline(ncpu, color="gray", ls=":", lw=0.8)
    a3.set_ylim(bottom=0)
    for ax in (a1, a2, a3):
        ax.grid(alpha=0.25)
    # repères du journal (v2)
    texte_j = ""
    if mk:
        gris, orange = "#6b6b66", "#eb6834"
        for i, (nom, x) in enumerate(mk["fins"]):
            if x > t[-1] + intervalle:
                continue                                                 # worker pas encore fini à cet instant
            for ax in (a1, a2, a3):
                ax.axvline(x, color=gris, lw=0.8, ls=(0, (3, 2)), alpha=0.7, zorder=1)
            a1.text(x, (138, 127, 116)[i % 3], nom, rotation=90, fontsize=7, color=gris, ha="center", va="top")
        for cle, lib in (("rescan_debut", "début du rescan"), ("rescan_fin", "fin du rescan")):
            x = mk[cle]
            if x is not None and x <= t[-1] + intervalle:
                for ax in (a1, a2, a3):
                    ax.axvline(x, color=orange, lw=1.1, ls="-", alpha=0.85, zorder=1)
                a1.text(x, 138, lib, rotation=90, fontsize=7, color=orange, ha="right", va="top")
        from matplotlib.lines import Line2D
        proxies = [Line2D([], [], color=gris, lw=0.9, ls=(0, (3, 2)), label="fin d'un worker (journal)"),
                   Line2D([], [], color=orange, lw=1.1, label="rescan : début / fin (journal)")]
        h, l = a2.get_legend_handles_labels()
        a2.legend(h + proxies, l + [p.get_label() for p in proxies], fontsize=7, loc="upper right", ncol=2, framealpha=0.6)
        texte_j = "\nrepères du journal %s — alignement ±%.1f s (%d workers)" % (os.path.basename(nom_journal or ""), mk["res"], mk["m"])
    resume = d.sg.chemin[:-len("_global.csv")] + "_resume.md"      # écrit par zeta-proc quand le run est fini
    fini = os.path.exists(resume) or (time.time() - d.g["epoch"][-1]) > max(10.0, 4 * intervalle)
    cpu_moy = sum(d.g["cpu"]) / len(d.g["cpu"])
    fig.suptitle("Processus du run — %s — %.0f s — CPU moyen %.0f %% — swap max %.0f Mo%s"
                 % ("TERMINÉ" if fini else "en cours", t[-1] + intervalle, cpu_moy, max(d.g["swap"]), texte) + texte_j,
                 fontsize=10)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cible", nargs="?", default=None)
    ap.add_argument("--refresh", type=float, default=2.0)
    ap.add_argument("--apres", default=None, help='ignorer les fichiers modifiés avant "AAAA-MM-JJ HH:MM:SS"')
    ap.add_argument("--sortie", default=None, help="écrire une image PNG et s'arrêter")
    ap.add_argument("--min-echantillons", type=int, default=3)
    ap.add_argument("--journal", default="auto", help="auto | CHEMIN | non : repères du journal du run (défaut auto)")
    ap.add_argument("--logs", default=None, help="dossier des journaux (défaut ~/projet_zeta/logs)")
    a = ap.parse_args()
    apres = datetime.datetime.fromisoformat(a.apres).timestamp() if a.apres else None

    import matplotlib
    if a.sortie:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    ncpu = os.cpu_count() or 4

    # attendre qu'un fichier apparaisse (comme zeta-live) ; en mode image, pas d'attente
    chemin = trouver_global(a.cible, apres)
    while chemin is None and not a.sortie:
        time.sleep(a.refresh)
        chemin = trouver_global(a.cible, apres)
    if chemin is None:
        print("Aucun fichier proc_*_global.csv trouvé."); sys.exit(1)
    d = Donnees(chemin)
    fig, axes = plt.subplots(3, 1, figsize=(9, 7.5), sharex=True, gridspec_kw={"hspace": 0.12})
    try:
        fig.canvas.manager.set_window_title("zeta_plot_proc — " + os.path.basename(chemin))
    except Exception:
        pass

    if a.sortie:
        d.maj()
        if d.n() < a.min_echantillons:
            print("Trop peu d'échantillons (%d)." % d.n()); sys.exit(1)
        jchemin = choisir_journal(a.journal, a.logs, d.g["epoch"][-1])
        jr = zg.lire_journal(jchemin) if jchemin else None
        mk = marqueurs(d, jr, a.refresh)
        if a.journal != "non":
            print("Journal : %s" % (jchemin or "aucun journal correspondant (repères non affichés)"))
        if mk:
            print("Alignement : décalage %.1f s, incertitude ±%.1f s (%d workers appariés)" % (mk["off"], mk["res"], mk["m"]))
            if mk["rescan_debut"] is not None and mk["rescan_naissance_csv"] is not None:
                print("Début du rescan : repère du journal %.1f s ; naissance observée des processus du rescan (CSV) %.1f s"
                      % (mk["rescan_debut"], mk["rescan_naissance_csv"]))
        dessiner(plt, np, fig, axes, d, ncpu, a.refresh, mk, jchemin)
        sortie = a.sortie
        if sortie == "auto":
            dossier = zg.dossier_figures(jr) if jr else os.path.dirname(chemin)
            os.makedirs(dossier, exist_ok=True)
            sortie = os.path.join(dossier, os.path.basename(chemin)[:-len("_global.csv")] + "_processus.png")
        fig.savefig(sortie, dpi=110, bbox_inches="tight")
        print("Image écrite :", sortie)
        return

    from matplotlib.animation import FuncAnimation

    etat = {"chemin": None, "mtime": None, "jr": None}

    def tour(_):
        d.maj()
        if d.n() >= a.min_echantillons:           # rien d'affiché avant 3 échantillons
            if a.journal != "non" and zg is not None:
                jchemin = choisir_journal(a.journal, a.logs, d.g["epoch"][-1])          # le journal peut apparaître après le CSV
                try:
                    mt = os.path.getmtime(jchemin) if jchemin else None
                except OSError:
                    mt = None
                if jchemin != etat["chemin"] or mt != etat["mtime"]:
                    etat.update(chemin=jchemin, mtime=mt, jr=zg.lire_journal(jchemin) if jchemin else None)
            mk = marqueurs(d, etat["jr"], a.refresh)
            dessiner(plt, np, fig, axes, d, ncpu, a.refresh, mk, etat["chemin"])
    anim = FuncAnimation(fig, tour, interval=int(a.refresh * 1000), cache_frame_data=False)
    fig._anim = anim                               # garder une référence : sinon l'animation s'arrête
    plt.show()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
