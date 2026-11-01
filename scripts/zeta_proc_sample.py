#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""zeta_proc_sample.py (v3.2) — échantillonne les processus d'un run (type htop, mais écrit dans un fichier).

Usage :
    python3 -I zeta_proc_sample.py [--intervalle 2] [--motif compute_zeros_v] [--sortie DOSSIER] [--test 1_4]
    (--test 1_4 donne proc_1_4_<date>.csv, proc_1_4_<date>_global.csv, proc_1_4_<date>_resume.md)
                                   [--attente-max SECONDES]
Nouveauté v3 : ne compte QUE les interpréteurs Python qui exécutent le script du run (un éditeur, un grep ou
un `tail` dont la ligne de commande contient le nom du script ne sont plus pris pour le run).
Nouveautés v2 :
  - écrit aussi proc_<date>_global.csv (une ligne par échantillon : CPU total, workers actifs, mémoire,
    load, swap) : c'est le fichier lu par le graphique en direct zeta_plot_proc.py ;
  - l'instant de chaque lecture est pris au moment de la lecture du processus (supprime l'artefact
    « CPU > 400 % » de la v1) ;
  - --attente-max : abandonne si aucun run n'apparaît dans ce délai (utile en arrière-plan ; 0 = attendre).

Principe :
  1. attend qu'un processus dont la ligne de commande contient le motif apparaisse ;
  2. toutes les N secondes, lit /proc (lecture seule) : CPU instantané, mémoire, état, threads ;
  3. s'arrête 3 échantillons après la disparition du dernier processus ;
  4. écrit <dossier>/proc_<date>.csv (données) et proc_<date>_resume.md (analyse).
Choix techniques :
  - bibliothèque standard seulement (aucune installation) ;
  - CPU instantané = (variation de utime+stime) / (variation d'horloge) : le %CPU de `ps` est une
    moyenne depuis le démarrage du processus, donc inutilisable pour voir une phase qui change ;
  - lancé en priorité minimale (nice 19) pour ne pas gêner le calcul.
Ne modifie rien sur le système. Sorties par défaut : ~/zeta_captures (hors dépôt git).
"""
import argparse, os, sys, time, datetime

TICK = os.sysconf("SC_CLK_TCK")          # ticks par seconde (100 sous Linux)
PAGE = os.sysconf("SC_PAGE_SIZE")        # taille d'une page mémoire en octets


def lire_proc(pid):
    """Retourne (état, ppid, ticks_cpu, threads, rss_Mo, commande) ou None si le processus a disparu."""
    try:
        with open("/proc/%d/stat" % pid, "rb") as f:
            brut = f.read().decode("utf-8", "replace")
        # le nom est entre parenthèses et peut contenir des espaces : on coupe sur la DERNIÈRE ')'
        reste = brut[brut.rindex(")") + 2:].split()
        etat, ppid = reste[0], int(reste[1])
        ticks = int(reste[11]) + int(reste[12])           # utime + stime
        threads = int(reste[17])
        rss_mo = int(reste[21]) * PAGE / 1048576.0
        with open("/proc/%d/cmdline" % pid, "rb") as f:
            cmd = f.read().replace(b"\0", b" ").decode("utf-8", "replace").strip()
        return etat, ppid, ticks, threads, rss_mo, cmd
    except (OSError, ValueError, IndexError):
        return None


def est_du_run(args, motif):
    """Vrai si la ligne de commande est celle d'un INTERPRÉTEUR PYTHON qui exécute un script dont le chemin
    contient le motif. Exclut : éditeur ou visionneuse qui ouvre ce fichier, grep, tail, bash -c ...,
    python -c "...texte contenant le motif...".
    v3.2 : le SCRIPT EXÉCUTÉ (1er argument qui n'est pas une option) doit lui-même porter le motif. Cela exclut le
    wrapper de monitoring zeta_mon_run.py, qui contient le chemin du calcul dans ses arguments mais n'en est pas un."""
    if not args or not os.path.basename(args[0]).startswith("python"):
        return False
    script = next((a for a in args[1:] if a and not a.startswith("-")), "")
    return script.endswith(".py") and motif in os.path.basename(script)


def trouver(motif, exclus):
    """PID des processus du run (voir est_du_run), hors nous-mêmes."""
    res = []
    for nom in os.listdir("/proc"):
        if nom.isdigit() and int(nom) not in exclus:
            try:
                with open("/proc/%s/cmdline" % nom, "rb") as f:
                    args = f.read().decode("utf-8", "replace").split("\0")
                if est_du_run(args, motif):
                    res.append(int(nom))
            except OSError:
                pass
    return res


def meminfo():
    d = {}
    with open("/proc/meminfo") as f:
        for ligne in f:
            k, v = ligne.split(":")
            d[k] = int(v.split()[0]) / 1024.0           # Ko -> Mo
    return d.get("MemAvailable", 0), d.get("SwapTotal", 0) - d.get("SwapFree", 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--intervalle", type=float, default=2.0)
    ap.add_argument("--motif", default="compute_zeros_v")
    ap.add_argument("--sortie", default=os.path.expanduser("~/zeta_captures"))
    ap.add_argument("--attente-max", type=float, default=0.0,
                    help="secondes d'attente maximale d'un run (0 = illimité)")
    ap.add_argument("--test", default="",
                    help="numéro du test (ex. 1_4) : placé dans le nom des fichiers proc_<test>_<date>*")
    a = ap.parse_args()
    a.test = "".join(c for c in a.test if c.isalnum() or c in "_-")   # nom de fichier sûr
    os.makedirs(a.sortie, exist_ok=True)
    try:
        os.nice(19)
    except OSError:
        pass
    exclus = {os.getpid(), os.getppid()}
    etiq = (a.test + "_") if a.test else ""
    base = os.path.join(a.sortie, "proc_" + etiq + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    print("En attente d'un processus contenant « %s » (Ctrl+C pour annuler)..." % a.motif, flush=True)
    debut_attente = time.time()
    while not trouver(a.motif, exclus):
        if a.attente_max and time.time() - debut_attente > a.attente_max:
            print("Aucun run détecté en %.0f s : abandon." % a.attente_max, flush=True)
            return
        time.sleep(0.5)
    print("Run détecté : échantillonnage toutes les %.1f s -> %s.csv" % (a.intervalle, base), flush=True)

    precedent = {}                       # pid -> (ticks, horloge)
    echantillons = []                    # (t, total_cpu, nb_actifs, rss_total, load1, mem_dispo, swap)
    vides = 0
    t0 = time.time()
    with open(base + ".csv", "w", encoding="utf-8") as out, \
         open(base + "_global.csv", "w", encoding="utf-8") as glob:
        out.write("t_s,pid,ppid,etat,cpu_pct,rss_mo,threads,commande\n")
        glob.write("t_s,epoch,cpu_total,actifs,rss_total_mo,load1,mem_dispo_mo,swap_mo\n")
        while vides < 3:
            debut_tour = time.time()
            total, actifs, rss_tot, vus = 0.0, 0, 0.0, 0
            for pid in trouver(a.motif, exclus):
                info = lire_proc(pid)
                if not info:
                    continue
                maintenant = time.time()                  # instant de la lecture (v2)
                etat, ppid, ticks, thr, rss, cmd = info
                cpu = 0.0
                if pid in precedent:
                    dt = maintenant - precedent[pid][1]
                    if dt > 0:
                        cpu = 100.0 * (ticks - precedent[pid][0]) / TICK / dt
                precedent[pid] = (ticks, maintenant)
                total += cpu; rss_tot += rss; vus += 1
                actifs += cpu >= 20.0
                out.write("%.1f,%d,%d,%s,%.1f,%.0f,%d,%s\n" % (debut_tour - t0, pid, ppid, etat, cpu, rss, thr,
                                                              cmd[:90].replace(",", ";")))
            out.flush()
            with open("/proc/loadavg") as f:
                load1 = float(f.read().split()[0])
            dispo, swap = meminfo()
            if vus:
                vides = 0
                echantillons.append((debut_tour - t0, total, actifs, rss_tot, load1, dispo, swap))
                glob.write("%.1f,%.1f,%.1f,%d,%.0f,%.2f,%.0f,%.0f\n" % (debut_tour - t0, debut_tour, total, actifs,
                                                                       rss_tot, load1, dispo, swap))
                glob.flush()
            else:
                vides += 1
            time.sleep(a.intervalle)

    # ---- analyse ----
    n = len(echantillons)
    if n < 3:
        print("Trop peu d'échantillons (%d) : run trop court pour l'analyse." % n)
        return
    pic = max(e[2] for e in echantillons)
    duree = echantillons[-1][0] - echantillons[0][0] + a.intervalle
    queue = 0
    for e in reversed(echantillons):             # phase finale : au plus 1 processus actif
        if e[2] <= 1:
            queue += 1
        else:
            break
    moy_cpu = sum(e[1] for e in echantillons) / n
    L = ["# Résumé d'échantillonnage — %s" % os.path.basename(base), "",
         "| Mesure | Valeur |", "|---|---|",
         "| motif suivi | `%s` |" % a.motif,
         "| durée observée | %.0f s (%d échantillons, pas %.1f s) |" % (duree, n, a.intervalle),
         "| CPU cumulé moyen | %.0f %% (100 %% = un cœur logique) |" % moy_cpu,
         "| CPU cumulé maximal | %.0f %% |" % max(e[1] for e in echantillons),
         "| pic de processus actifs (≥ 20 %% CPU) | %d |" % pic,
         "| phase finale à 1 processus actif ou moins | %.0f s (%.0f %% de la durée) |" % (queue * a.intervalle, 100.0 * queue * a.intervalle / duree),
         "| mémoire résidente totale maximale | %.0f Mo |" % max(e[3] for e in echantillons),
         "| load average (1 min) maximal | %.2f |" % max(e[4] for e in echantillons),
         "| mémoire disponible minimale | %.0f Mo |" % min(e[5] for e in echantillons),
         "| swap utilisé maximal | %.0f Mo |" % max(e[6] for e in echantillons), "",
         "Lecture : un CPU cumulé moyen proche de 100 × (nombre de cœurs logiques) signifie que les cœurs sont utilisés ;",
         "une longue phase finale à 1 processus actif signale un déséquilibre entre workers (mesuré, pas interprété ici).", "",
         "---", "*Mis à jour : %s — %d lignes*" % (datetime.date.today().isoformat(), 0)]
    L[-1] = "*Mis à jour : %s — %d lignes*" % (datetime.date.today().isoformat(), len(L))
    with open(base + "_resume.md", "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L[:16]))
    print("Fichiers : %s.csv, %s_global.csv et %s_resume.md" % (base, base, base))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrompu.")
        sys.exit(130)
