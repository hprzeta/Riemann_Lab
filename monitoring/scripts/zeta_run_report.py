#!/usr/bin/env python3
"""
zeta_run_report.py — Rapport de monitoring d'UN run : 3 graphiques + commentaires, en MD et PDF.
Appelé automatiquement par zeta_run_watch.py à la fin d'un run ; utilisable à la main :

    zeta-report [dossier_du_run] [--lang fr|en]     # régénère le rapport (défaut : dernier run)
    zeta-index                                      # régénère Monitoring-Runs.md (liste des runs)

Contenu (lu dans runs/<id>/meta.json + data/cluster_metrics_*.csv + CSV des zéros) :
  figures/metrics.png         historique 5 machines (T°, fréquence, load, RAM) sur la durée du run
  figures/zeros_tranches.png  zéros par tranche de t + espacement de chaque zéro
  figures/gue.png             histogramme des espacements vs GUE / Poisson
Les commentaires distinguent MESURÉ (chiffres lus) et HYPOTHÈSE (interprétation non vérifiée).
"""
import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                      # rapport sans fenêtre
import matplotlib.pyplot as plt            # noqa: E402
import numpy as np                         # noqa: E402
import pandas as pd                        # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import zeta_gue_hist as zg                 # noqa: E402
import zeta_plot_live as zl                # noqa: E402
import zeta_plot_metrics as zm             # noqa: E402
from zeta_mon_common import DATA, RUNS, ROOT, csv_du_run, dossiers_runs, ecrire_md, lien   # noqa: E402


# ----------------------------------------------------------------------------- utilitaires
def duree(s):
    s = int(round(s))
    return "%dh%02dmin%02ds" % (s // 3600, s % 3600 // 60, s % 60) if s >= 3600 else "%dmin%02ds" % (s // 60, s % 60)


def N_approx(t):
    """Nombre de zéros jusqu'à t : (t/2π) ln(t/2πe) + 7/8 (Riemann–von Mangoldt, terme S(t) ignoré)."""
    return t / (2 * np.pi) * np.log(t / (2 * np.pi * np.e)) + 7 / 8


def stats_machines(df):
    lignes = []
    if df is None or df.empty:
        return lignes
    for pc in zm.COULEURS:
        d = df[df["machine"] == pc]
        if d.empty:
            continue
        ok = d[d["ok"] == 1]
        num = lambda c: pd.to_numeric(ok[c], errors="coerce").dropna()
        T, F, Ld, R = num("temp_c"), num("freq_mhz"), num("load1"), num("ram_pct")
        lignes.append(dict(pc=pc, nom=zm.NOMS[pc], valide=100.0 * len(ok) / len(d), n=len(d),
                           tmoy=T.mean() if len(T) else np.nan, tmax=T.max() if len(T) else np.nan,
                           t75=100.0 * (T >= 75).mean() if len(T) else np.nan,
                           fmin=F.min() if len(F) else np.nan, fmax=F.max() if len(F) else np.nan,
                           lmax=Ld.max() if len(Ld) else np.nan, rmax=R.max() if len(R) else np.nan,
                           F=F, T=T))
    return lignes


def f1(x, n=1):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else ("%.*f" % (n, x))


# ----------------------------------------------------------------------------- rapport
def verdict_turing(csv):
    """Lit le verdict Turing–Backlund dans le journal d'exécution voisin du CSV (execution_*.log).
    Renvoie None si introuvable, sinon {statut, ok, manquants, lignes} (valeurs lues, jamais devinées)."""
    try:
        if not csv:
            return None
        logs = sorted(Path(csv).parent.glob("execution_*.log"))
        if not logs:
            return None
        txt = logs[-1].read_text(errors="replace")
        m = re.search(r"VALIDATION TURING-BACKLUND\s*\n\s*Statut\s*:\s*(.+)", txt)
        if not m:
            return None
        statut = m.group(1).strip()
        mm = re.search(r"Zéros manquants\s*:\s*(-?\d+)", txt[m.end():])
        # lignes de contrôle « T=… calc=… attendus=… delta=… » qui suivent le statut
        lignes = re.findall(r"^\s*(T=.+?delta=.+)$", txt[m.end():m.end() + 1500], re.M)
        return {"statut": statut, "ok": "COMPLET" in statut and "INCOMPLET" not in statut,
                "manquants": int(mm.group(1)) if mm else None, "lignes": lignes, "log": logs[-1].name}
    except Exception:
        return None


def rapport(run_dir, lang="fr"):
    run_dir = Path(run_dir)
    meta = json.loads((run_dir / "meta.json").read_text())
    meta.setdefault("type", "auto")
    fr = lang == "fr"
    L = lambda a, b: a if fr else b
    t0, t1 = dt.datetime.fromisoformat(meta["t0"]), dt.datetime.fromisoformat(meta["t1"])
    dur = (t1 - t0).total_seconds()
    figdir = run_dir / "figures"
    figdir.mkdir(exist_ok=True)
    B = []                                    # blocs : rendus en MD et en PDF
    h = lambda lv, t: B.append(("h", lv, t))
    p = lambda t: B.append(("p", t))
    ul = lambda x: B.append(("ul", x))
    tb = lambda r: B.append(("tb", r))
    fg = lambda f, c: B.append(("fig", f, c))

    # ---- données machines
    df = zm.lire(DATA, t0=t0, t1=t1)
    if df is not None and not df.empty:
        df.to_csv(run_dir / "metrics.csv", index=False)
    sm = stats_machines(df)
    fig_metrics = None
    if sm:
        f = zm.figure_metrics(df, "%s — %s → %s" % (meta["nom"], t0.strftime("%Y-%m-%d %H:%M:%S"), t1.strftime("%H:%M:%S")), figsize=(14, 7.5))
        f.savefig(figdir / "metrics.png", dpi=110, facecolor=zm.SURFACE)
        plt.close(f)
        fig_metrics = "metrics.png"

    # ---- zéros
    t = None
    csv = meta.get("csv")
    if not (csv and Path(csv).is_file()):
        csv = csv_du_run(meta, t0, t1)
        meta["csv"] = csv
    if csv and Path(csv).is_file():
        try:
            t = zl.lire_zeros(csv)
            if len(t) < 10:
                t = None
        except Exception as e:
            meta["erreur_zeros"] = str(e)
    st = None
    if t is not None:
        w = zl.tranche_auto(t)
        f, (a1, a2) = plt.subplots(2, 1, figsize=(14, 7), constrained_layout=True)
        zl.dessiner(a1, a2, t, w)
        f.savefig(figdir / "zeros_tranches.png", dpi=110)
        plt.close(f)
        f, st = zg.figure_gue(t, 60 if len(t) > 5000 else 25)
        f.set_size_inches(14, 5)
        f.savefig(figdir / "gue.png", dpi=110)
        plt.close(f)

    # ---- débit (etat.csv écrit toutes les 5 s par le superviseur du lanceur)
    deb = None
    fig_debit = None
    try:
        deb = pd.read_csv(run_dir / "etat.csv", parse_dates=["horodatage"])
        deb = deb[deb["zps"].notna() & (deb["zps"] >= 0)]
        if len(deb) >= 5:
            f, ax = plt.subplots(figsize=(14, 3.2), constrained_layout=True)
            ax.plot(deb["horodatage"], deb["zps"], color="#3b78c4", lw=1.4)
            ax.set_ylabel("zéros / s")
            ax.set_title("Débit de calcul pendant le run (zéros écrits dans le CSV par seconde)")
            ax.set_ylim(bottom=0)
            ax.grid(True, alpha=0.3)
            f.savefig(figdir / "debit.png", dpi=110)
            plt.close(f)
            fig_debit = "debit.png"
        else:
            deb = None
    except Exception:
        deb = None

    # ---- en-tête
    demo = bool(meta.get("demo"))
    h(0, L("Rapport de monitoring — run ", "Monitoring report — run ") + meta["nom"])
    if demo:
        p(L("**⚠ DONNÉES SIMULÉES — DÉMONSTRATION DU FORMAT. Ne pas interpréter.**",
            "**⚠ SIMULATED DATA — FORMAT DEMONSTRATION. Do not interpret.**"))
    p(L("Légende : **[mesuré]** = chiffre lu dans les données ; **[heuristique]** / **[hypothèse]** = interprétation non vérifiée ; "
        "**[conjecture]** = résultat non démontré.",
        "Legend: **[measured]** = figure read from data; **[heuristic]** / **[hypothesis]** = unverified interpretation; "
        "**[conjecture]** = unproven result."))
    vt = verdict_turing(csv)
    if vt is not None:
        if vt["ok"]:
            p(L("**Validation Turing–Backlund : %s** [mesuré, lu dans %s] — vérification numérique, pas une certification.",
                "**Turing–Backlund validation: %s** [measured, read from %s] — numerical check, not a certification.") % (vt["statut"], vt["log"]))
        else:
            p(L("**⚠ ALERTE — Validation Turing–Backlund : %s** — %s zéro(s) manquant(s) [mesuré, lu dans %s]. "
                "Les comptages de ce run ne sont PAS complets : ne pas utiliser ces zéros pour une statistique sans les compléter.",
                "**⚠ ALERT — Turing–Backlund validation: %s** — %s missing zero(s) [measured, read from %s]. "
                "This run's counts are NOT complete: do not use these zeros for statistics without completing them.")
              % (vt["statut"], vt["manquants"] if vt["manquants"] is not None else "?", vt["log"]))
            if vt["lignes"]:
                ul(["`%s`" % l.strip() for l in vt["lignes"]])
    else:
        p(L("Validation Turing–Backlund : verdict introuvable (journal `execution_*.log` absent ou illisible) [non vérifié].",
            "Turing–Backlund validation: verdict not found (`execution_*.log` missing or unreadable) [unverified]."))
    h(1, L("1. Résumé", "1. Summary"))
    zps = (len(t) / dur) if (t is not None and dur > 0) else None
    rows = [[L("Grandeur", "Item"), L("Valeur", "Value")],
            ["Run", "%s  (%s)" % (meta["id"], meta.get("type", "?"))],
            [L("Début / fin", "Start / end"), "%s → %s" % (t0.strftime("%Y-%m-%d %H:%M:%S"), t1.strftime("%H:%M:%S"))],
            [L("Durée", "Duration"), duree(dur)],
            [L("Commande (extrait)", "Command (excerpt)"), "`%s`" % meta.get("cmd", "?")[:90]],
            [L("Code retour", "Exit code"), ("%s" % meta["rc"]) if meta.get("rc") is not None else L("inconnu (run non lancé par le lanceur)", "unknown (run not started by the launcher)")],
            [L("Turbo CPU début → fin", "CPU turbo start → end"), "%s → %s" % ((meta.get("session") or {}).get("turbo", "?"), (meta.get("session_fin") or {}).get("turbo", "?"))],
            [L("CSV des zéros", "Zeros CSV"), "`%s`" % (Path(csv).name if csv else L("introuvable", "not found"))],
            ["Turing–Backlund", (vt["statut"] if vt else L("inconnu", "unknown"))]]
    if t is not None:
        rows += [[L("Zéros dans le CSV", "Zeros in CSV"), "%d  [%s]" % (len(t), L("mesuré", "measured"))],
                 ["t min → t max", "%.3f → %.3f" % (t[0], t[-1])],
                 [L("Débit moyen (zéros / durée du run)", "Average rate (zeros / run duration)"), "%.1f /s" % zps]]
    tb(rows)

    # ---- machines
    h(1, L("2. Machines pendant le run", "2. Machines during the run"))
    if fig_metrics:
        fg(fig_metrics, L("Figure 1 — Température, fréquence, charge et RAM des 5 machines (1 mesure/s).",
                          "Figure 1 — Temperature, frequency, load and RAM of the 5 machines (1 sample/s)."))
        tb([[L("Machine", "Machine"), L("Valides", "Valid"), "T moy °C", "T max °C", L("% ≥ 75 °C", "% ≥ 75 °C"),
              "MHz min–max", "load max", "RAM max %"]] +
            [["%s %s" % (m["pc"], m["nom"]), "%.0f %%" % m["valide"], f1(m["tmoy"]), f1(m["tmax"]), f1(m["t75"], 0),
              "%s–%s" % (f1(m["fmin"], 0), f1(m["fmax"], 0)), f1(m["lmax"], 2), f1(m["rmax"])] for m in sm])
        obs, hyp = [], []
        for m in sm:
            if m["valide"] < 90:
                obs.append(L("%s : seulement %.0f %% de mesures valides (machine éteinte, SSH coupé ou capteur absent) [mesuré]",
                             "%s: only %.0f %% valid samples (machine off, SSH down or no sensor) [measured]") % (m["pc"], m["valide"]))
            if not np.isnan(m["tmax"]) and m["tmax"] >= 75:
                obs.append(L("%s : température max %.1f °C, %.0f %% du temps ≥ 75 °C (seuil d'avertissement) [mesuré]",
                             "%s: max temperature %.1f °C, %.0f %% of time ≥ 75 °C (warning threshold) [measured]") % (m["pc"], m["tmax"], m["t75"]))
        pc1 = next((m for m in sm if m["pc"] == "PC1"), None)
        if pc1 is not None and len(pc1["F"]) >= 50:
            k = max(1, len(pc1["F"]) // 5)
            freq_deb, freq_fin = pc1["F"].iloc[:k].median(), pc1["F"].iloc[-k:].median()
            obs.append(L("PC1 : fréquence médiane %.0f MHz sur le 1ᵉʳ cinquième du run, %.0f MHz sur le dernier [mesuré]",
                         "PC1: median frequency %.0f MHz over the first fifth of the run, %.0f MHz over the last [measured]") % (freq_deb, freq_fin))
            if freq_deb - freq_fin >= 300:
                if pc1["tmax"] >= 75:
                    hyp.append(L("La baisse de fréquence PC1 coïncide avec T ≥ 75 °C : compatible avec une limitation thermique [hypothèse — à confirmer, une limite de puissance donne le même symptôme].",
                                 "The PC1 frequency drop coincides with T ≥ 75 °C: consistent with thermal throttling [hypothesis — to confirm, a power limit gives the same symptom]."))
                else:
                    hyp.append(L("Baisse de fréquence PC1 sans T ≥ 75 °C : plutôt limite de puissance ou gouverneur `powersave` [hypothèse — non vérifiée].",
                                 "PC1 frequency drop without T ≥ 75 °C: more likely a power limit or the `powersave` governor [hypothesis — unverified]."))
        h(2, L("Observations", "Observations"))
        ul(obs or [L("Rien d'anormal détecté sur les seuils automatiques [mesuré].", "Nothing abnormal on the automatic thresholds [measured].")])
        if hyp:
            ul(hyp)
    else:
        p(L("Aucune mesure machine sur cette période (logger arrêté ? `zeta-mon-on`).",
            "No machine samples for this period (logger stopped? `zeta-mon-on`)."))

    # ---- zéros
    h(1, L("3. Zéros calculés", "3. Computed zeros"))
    if t is not None:
        fg("zeros_tranches.png", L("Figure 2 — Haut : zéros par tranche de t (bleu/gris alternés) vs densité théorique ln(t/2π)/2π. Bas : espacement normalisé de chaque zéro.",
                                   "Figure 2 — Top: zeros per t-slice (alternating blue/grey) vs theoretical density ln(t/2π)/2π. Bottom: normalized spacing of each zero."))
        att = N_approx(t[-1]) - N_approx(t[0]) + 1
        p(L("Comptage : %d zéros dans le CSV ; formule de Riemann–von Mangoldt (sans terme S(t)) : ≈ %.1f. Écart %+.1f. "
            "**[heuristique]** un écart de quelques unités est normal ; un écart de plusieurs dizaines suggère des zéros manquants ou en double. "
            "**Ce n'est pas une validation : la complétude se vérifie par Turing–Backlund (verdict en tête de ce rapport).**",
            "Count: %d zeros in the CSV; Riemann–von Mangoldt formula (without the S(t) term): ≈ %.1f. Difference %+.1f. "
            "**[heuristic]** a difference of a few units is normal; tens suggest missing or duplicated zeros. "
            "**This is not a validation: completeness is checked by Turing–Backlund (verdict at the top of this report).**") % (len(t), att, len(t) - att))
        fg("gue.png", L("Figure 3 — Espacements normalisés vs GUE (Wigner surmise) et Poisson ; à droite zoom sur la répulsion (échelle log).",
                        "Figure 3 — Normalized spacings vs GUE (Wigner surmise) and Poisson; right: zoom on repulsion (log scale)."))
        tb([[L("Grandeur", "Item"), L("Mesuré", "Measured"), L("Référence", "Reference")],
            [L("Moyenne de s", "Mean of s"), "%.4f" % st["moyenne"], L("1 (par construction)", "1 (by construction)")],
            [L("Variance de s", "Variance of s"), "%.4f" % st["variance"], "GUE ≈ 0.18 ; Poisson = 1"],
            [L("Part s < 0,1", "Share s < 0.1"), "%.3f %%" % (100 * st["part_s01"]), "GUE surmise ≈ 0.11 % ; Poisson ≈ 9.5 %"],
            [L("Plus petit écart brut", "Smallest raw gap"), "%.6f" % st["min_brut"], "—"]])
        p(L("**[conjecture, Montgomery–Odlyzko]** les espacements suivent la loi GUE ; ici la répulsion est %s. "
            "La variance un peu sous 0,18 sur de petites hauteurs relève des corrections de taille finie **[hypothèse]**. "
            "Avec peu de zéros (< quelques milliers) l'histogramme est bruité : ne pas sur-interpréter.",
            "**[conjecture, Montgomery–Odlyzko]** spacings follow GUE; here the repulsion is %s. "
            "A variance slightly below 0.18 at moderate heights is attributed to finite-size corrections **[hypothesis]**. "
            "With few zeros (< a few thousand) the histogram is noisy: do not over-interpret.")
          % (L("nette", "clear") if st["part_s01"] < 0.02 else L("peu marquée (vérifier les données)", "weak (check the data)")))
    else:
        p(L("CSV des zéros introuvable ou trop court : sections 3 non générées. Relancer `zeta-report` après `zeta-run-hint NOM CSV`.",
            "Zeros CSV not found or too short: section 3 not generated. Re-run `zeta-report` after `zeta-run-hint NAME CSV`."))

    if fig_debit is not None:
        fg(fig_debit, L("Figure 4 — Débit (zéros/s) au cours du run, à comparer à la fréquence et à la température de PC1 (figure 1).",
                        "Figure 4 — Throughput (zeros/s) over the run, to compare with PC1 frequency and temperature (figure 1)."))
        z = deb["zps"]
        k = max(1, len(z) // 5)
        d0, d1 = z.iloc[:k].median(), z.iloc[-k:].median()
        if (z > 0).mean() < 0.5:   # CSV écrit seulement en fin de worker (v16) : débit instantané non exploitable
            lignes = [L("Débit instantané non exploitable : le CSV des zéros n'a grossi que sur %.0f %% des mesures (écriture par worker en fin de calcul) ; se fier au débit moyen du résumé [mesuré]",
                        "Instantaneous throughput not usable: the zeros CSV grew on only %.0f %% of the samples (written per worker at the end); rely on the mean throughput in the summary [measured]") % (100 * (z > 0).mean())]
            d0 = d1 = 0
        else:
            lignes = [L("Débit médian : %.0f z/s (min %.0f, max %.0f) ; 1ᵉʳ cinquième %.0f z/s, dernier %.0f z/s [mesuré]",
                        "Median throughput: %.0f z/s (min %.0f, max %.0f); first fifth %.0f z/s, last %.0f z/s [measured]") % (z.median(), z.min(), z.max(), d0, d1)]
        if d0 > 0 and (d0 - d1) / d0 >= 0.10:
            lignes.append(L("Le débit baisse de %.0f %% entre début et fin : à rapprocher de la fréquence/température PC1 [hypothèse — lien non établi par ce rapport]",
                            "Throughput drops by %.0f %% between start and end: compare with PC1 frequency/temperature [hypothesis — link not established by this report]") % (100 * (d0 - d1) / d0))
        ul(lignes)

    # ---- fiche de session (détails dans session.md)
    ses = meta.get("session") or {}
    if ses:
        h(1, L("4. Fiche de session", "4. Session sheet"))
        g = ses.get("git") or {}
        tb([[L("Élément", "Item"), L("Valeur", "Value")],
            ["CPU", "%s (%s %s)" % (ses.get("cpu", "?"), ses.get("cpu_logiques", "?"), L("threads", "threads"))],
            [L("Gouverneur / turbo", "Governor / turbo"), "%s / %s" % (ses.get("gouverneur", "?"), ses.get("turbo", "?"))],
            ["Git", "%s @ %s (%s %s)" % (g.get("commit", "?"), g.get("branche", "?"), g.get("fichiers_modifies", "?"), L("fichiers modifiés", "modified files"))],
            [L("Charge / RAM dispo au départ", "Load / free RAM at start"), "%s / %s Go" % (ses.get("charge_1min", "?"), ses.get("ram_dispo_Go", "?"))],
            [L("Fichier détaillé", "Detailed file"), "`session.md`"]])
        ecrire_session(run_dir, meta, t, dur)

    # ---- interprétation (jamais automatique : fichier interpretation.md rédigé après relecture)
    h(1, L("5. Interprétation", "5. Interpretation"))
    ip = run_dir / "interpretation.md"
    if ip.exists():
        p(L("*Rédigée par Claude Code à partir des chiffres ci-dessus — à valider.*",
            "*Written by Claude Code from the figures above — to be validated.*"))
        B.extend(blocs_md(ip.read_text()))
    else:
        p(L("*Pas encore rédigée. Après relecture des observations, créer `interpretation.md` dans ce dossier puis `zeta-report` : "
            "distinguer mesuré / heuristique / hypothèse / conjecture.*",
            "*Not written yet. After reviewing the observations, create `interpretation.md` in this folder then run `zeta-report`: "
            "separate measured / heuristic / hypothesis / conjecture.*"))

    h(1, L("6. Limites", "6. Limits"))
    ul([L("Mesures toutes les ~1 s (SSH) : les pics plus courts échappent ; PC4 (OpenBSD) n'a pas de mesure de RAM.",
          "Samples about every 1 s (SSH): shorter spikes are missed; PC4 (OpenBSD) has no RAM reading."),
        L("Début/fin du run = apparition/disparition du processus détecté, à quelques secondes près.",
          "Run start/end = detected process appearing/disappearing, within a few seconds."),
        L("Au-delà de 8 000 points par machine, le tracé est sous-échantillonné (les statistiques utilisent toutes les mesures).",
          "Beyond 8,000 points per machine the plot is subsampled (statistics use all samples).")])

    # ---- sorties
    titre = B[0][2]
    md = []
    for b in B:
        k = b[0]
        if k == "h":
            md += ["#" * (b[1] + 1) + " " + b[2], ""]
        elif k == "p":
            md += [b[1], ""]
        elif k == "ul":
            md += ["- " + x for x in b[1]] + [""]
        elif k == "fig":
            md += ["![%s](figures/%s)" % (b[2], b[1]), "", "*%s*" % b[2], ""]
        elif k == "tb":
            r = b[1]
            md += ["| " + " | ".join(r[0]) + " |", "|" + "---|" * len(r[0])]
            md += ["| " + " | ".join(c.replace("|", "\\|") for c in row) + " |" for row in r[1:]] + [""]
    nom_md = "rapport.md" if fr else "report_en.md"
    nlignes = ecrire_md(run_dir / nom_md, "\n".join(md))
    pdf_ok = pdf(run_dir / ("rapport.pdf" if fr else "report_en.pdf"), B, figdir, titre, meta["id"], nlignes)

    rc = meta.get("rc")
    meta.update(statut=("échec (code %s)" % rc) if rc not in (None, 0) else ("terminé" if rc == 0 else "terminé (code inconnu)"), zeros=(len(t) if t is not None else None), duree_s=dur, zps=zps,
                tmax_pc1=(pc1["tmax"] if sm and pc1 is not None else None),
                figures=[f.name for f in sorted(figdir.glob("*.png"))])
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=1, default=float))
    maj_index()
    return nom_md, pdf_ok


def blocs_md(texte):
    """Mini-convertisseur MD -> blocs (titres, puces, paragraphes) pour inclure interpretation.md dans le PDF."""
    out, ul = [], []
    for l in texte.splitlines():
        t = l.strip()
        if not t or t == "---" or re.match(r"^\*.*\.md · MAJ", t):
            continue
        if t.startswith("- "):
            ul.append(t[2:])
            continue
        if ul:
            out.append(("ul", ul))
            ul = []
        m = re.match(r"^(#+)\s+(.*)", t)
        out.append(("h", min(len(m.group(1)) + 1, 2), m.group(2)) if m else ("p", t))
    if ul:
        out.append(("ul", ul))
    return out


def ecrire_session(run_dir, meta, t, dur):
    """session.md : fiche complète du run (commande, machine, code, versions, turbo, CSV)."""
    s = meta.get("session") or {}
    g = s.get("git") or {}
    csv = meta.get("csv")
    rows = [("Run", meta["id"]), ("Type", meta.get("type")), ("Début", meta["t0"]), ("Fin", meta["t1"]), ("Durée", duree(dur)),
            ("Commande", "`%s`" % (meta.get("cmd") or "(non renseignée : run détecté ou lancé à côté)")),
            ("Code retour", meta.get("rc") if meta.get("rc") is not None else "inconnu"),
            ("Hôte / noyau", "%s / %s" % (s.get("hote"), s.get("noyau"))), ("CPU", "%s — %s threads" % (s.get("cpu"), s.get("cpu_logiques"))),
            ("Gouverneur", s.get("gouverneur")), ("Turbo au départ", s.get("turbo")),
            ("Turbo à la fin", (meta.get("session_fin") or {}).get("turbo")),
            ("Charge 1 min au départ / à la fin", "%s / %s" % (s.get("charge_1min"), (meta.get("session_fin") or {}).get("charge_1min"))),
            ("RAM totale / dispo (Go)", "%s / %s" % (s.get("ram_totale_Go"), s.get("ram_dispo_Go"))),
            ("Disque libre (Go)", s.get("disque_libre_Go")),
            ("Git", "%s @ %s, %s fichiers modifiés non commités" % (g.get("commit"), g.get("branche"), g.get("fichiers_modifies"))),
            ("Python / paquets", "%s / %s" % (s.get("python"), ", ".join("%s %s" % kv for kv in (s.get("paquets") or {}).items()))),
            ("CSV des zéros", "`%s`" % csv if csv else "introuvable")]
    if csv and Path(csv).is_file():
        st = Path(csv).stat()
        rows.append(("Taille du CSV", "%.1f Mo — %s zéros" % (st.st_size / 1e6, len(t) if t is not None else "?")))
    texte = ["# Fiche de session — %s" % meta["nom"], "",
             "Photographie de l'état de PC1 et du code au moment du run (turbo : lecture `intel_pstate/no_turbo` ou `cpufreq/boost`, "
             "**[hypothèse : mécanisme supposé de `zeta_turbo_on.sh`, non vérifié]**).", "",
             "| Élément | Valeur |", "|---|---|"] + ["| %s | %s |" % (k, v) for k, v in rows]
    ecrire_md(run_dir / "session.md", "\n".join(texte))


def pdf(chemin, B, figdir, titre, rid, nlignes):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.pdfmetrics import registerFontFamily
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import (Image, KeepTogether, Paragraph, Preformatted, SimpleDocTemplate,
                                        Spacer, Table, TableStyle)
        from PIL import Image as PI
    except ImportError as e:
        print("PDF non généré (%s) — installer :  pip install reportlab pillow" % e)
        return False
    import matplotlib as mpl
    fd = Path(mpl.get_data_path()) / "fonts" / "ttf"            # DejaVu fourni avec matplotlib
    for n, f in (("DV", "DejaVuSans.ttf"), ("DVB", "DejaVuSans-Bold.ttf"), ("DVI", "DejaVuSans-Oblique.ttf"),
                 ("DVM", "DejaVuSansMono.ttf")):
        pdfmetrics.registerFont(TTFont(n, str(fd / f)))
    registerFontFamily("DV", normal="DV", bold="DVB", italic="DVI", boldItalic="DVB")

    def fmt(t):
        t = html.escape(t, quote=False)
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        return re.sub(r"`(.+?)`", r'<font name="DVM" size="8">\1</font>', t)

    S = lambda **k: ParagraphStyle("x", **{**dict(fontName="DV", fontSize=9.5, leading=13.5), **k})
    sty = {"p": S(spaceAfter=6), "c": S(fontName="DVI", fontSize=8.5, leading=11, textColor=colors.HexColor("#444"), spaceAfter=10),
           0: S(keepWithNext=1, fontName="DVB", fontSize=17, leading=21, spaceAfter=10),
           1: S(keepWithNext=1, fontName="DVB", fontSize=13, leading=17, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#1f3d6e")),
           2: S(keepWithNext=1, fontName="DVB", fontSize=11, leading=14, spaceBefore=8, spaceAfter=4), "cell": S(fontSize=8, leading=10.5)}
    W, E = 17 * cm, []
    for b in B:
        k = b[0]
        if k == "h":
            E.append(Paragraph(fmt(b[2]), sty[b[1]]))
        elif k == "p":
            E.append(Paragraph(fmt(b[1]), sty["p"]))
        elif k == "ul":
            E += [Paragraph("• " + fmt(x), ParagraphStyle("u", parent=sty["p"], leftIndent=12, firstLineIndent=-8, spaceAfter=3)) for x in b[1]] + [Spacer(1, 4)]
        elif k == "fig":
            w, hh = PI.open(figdir / b[1]).size
            wd = W if w / hh > 1.5 else 15 * cm
            hd = wd * hh / w
            if hd > 11 * cm:
                hd, wd = 11 * cm, 11 * cm * w / hh
            E.append(KeepTogether([Image(str(figdir / b[1]), wd, hd), Spacer(1, 3), Paragraph(fmt(b[2]), sty["c"])]))
        elif k == "tb":
            r = b[1]
            nc = len(r[0])
            cw = [W / nc] * nc if nc > 3 else ([5 * cm, W - 5 * cm] if nc == 2 else [4.5 * cm, 3.5 * cm, W - 8 * cm])
            data = [[Paragraph(fmt(("**%s**" % c) if i == 0 else c), sty["cell"]) for c in row] for i, row in enumerate(r)]
            t = Table(data, colWidths=cw, repeatRows=1)
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dfe7f3")),
                                   ("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
            E += [KeepTogether([t, Spacer(1, 8)])]

    def pied(c, d):
        c.setFont("DV", 7.5)
        c.setFillColor(colors.grey)
        c.drawString(2 * cm, 1.1 * cm, "%s · MAJ %s · %d lignes (MD)" % (rid, dt.date.today().isoformat(), nlignes))
        c.drawRightString(19 * cm, 1.1 * cm, "p. %d" % d.page)

    SimpleDocTemplate(str(chemin), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm,
                      bottomMargin=1.8 * cm, title=titre, author="hprzeta").build(E, onFirstPage=pied, onLaterPages=pied)
    return True


# ----------------------------------------------------------------------------- index (page wiki)
GALERIE = [("live_zeros.png", "Suivi en direct des zéros (`zeta-live`) : colonnes bleu/gris + espacement de chaque zéro."),
           ("gue.png", "Espacements vs GUE (`zeta-gue`) : la répulsion des zéros, loin de Poisson."),
           ("metrics.png", "Historique des 5 machines (`zeta-metrics`) : T°, fréquence, load, RAM.")]


SECTIONS = [("test", "Runs de test"), ("prod", "Runs de production"), ("auto", "Runs détectés sans lanceur"),
            ("historique", "Historique (sans mesures machines)")]


def maj_index():
    metas = []
    for d in dossiers_runs():
        try:
            m = json.loads((d / "meta.json").read_text())
        except Exception:
            continue
        if m.get("demo"):
            continue
        m["_d"], m["_rel"] = d, d.relative_to(ROOT).as_posix()
        m["_type"] = m.get("type") or ("historique" if m.get("historique") else "auto")
        metas.append(m)
    metas.sort(key=lambda m: m.get("t0", ""), reverse=True)
    out = ["# Monitoring des runs — Zêta", "",
           "Liste de chaque run lancé, avec ses graphiques (générée automatiquement par `zeta_mon_run.py` / `zeta_run_watch.py` / "
           "`zeta_run_report.py`). Chiffres **mesurés** ; interprétations marquées *hypothèse* dans chaque rapport ; "
           "section « Interprétation » rédigée après relecture.", ""]
    gr = [("métriques", "metrics.png"), ("zéros", "zeros_tranches.png"), ("GUE", "gue.png"), ("débit", "debit.png")]
    for typ, titre in SECTIONS:
        ms = [m for m in metas if m["_type"] == typ]
        if not ms:
            continue
        out += ["## " + titre, "", "| Date | Run | Statut | Durée | Zéros | z/s | T max PC1 | Graphiques | Rapport · session |",
                "|---|---|---|---|---|---|---|---|---|"]
        for m in ms:
            rel, base = m["_rel"], m["_d"]
            g = " · ".join("[%s](%s)" % (n, lien("%s/figures/%s" % (rel, f))) for n, f in gr if (base / "figures" / f).exists()) or "—"
            r = " · ".join("[%s](%s)" % (n, lien("%s/%s" % (rel, f))) for n, f in
                           (("MD", "rapport.md"), ("PDF", "rapport.pdf"), ("session", "session.md")) if (base / f).exists()) or "—"
            out.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                (m.get("t0", "")[:10] if m["_type"] == "historique" else m.get("t0", "")[:16].replace("T", " ")), m.get("nom", base.name),
                m.get("statut", "?"), duree(m["duree_s"]) if m.get("duree_s") else "—",
                m.get("zeros") if m.get("zeros") is not None else "—", f1(m.get("zps")) if m.get("zps") else "—",
                f1(m.get("tmax_pc1")) if m.get("tmax_pc1") is not None else "—", g, r))
        out.append("")
    if not metas:
        out += ["| — | aucun run enregistré |", ""]
    dernier = next((m for m in metas if (m["_d"] / "figures" / "metrics.png").exists()), None)
    if dernier:
        out += ["## Dernier run avec historique machines : %s" % dernier.get("nom"), "",
                "![métriques](%s)" % lien(dernier["_rel"] + "/figures/metrics.png"), ""]
        if (dernier["_d"] / "figures" / "zeros_tranches.png").exists():
            out += ["![zéros](%s)" % lien(dernier["_rel"] + "/figures/zeros_tranches.png"), ""]
    gal = [(f, c) for f, c in GALERIE if (ROOT / "galerie" / f).exists()]
    if gal:
        out += ["## Galerie de référence (graphiques conservés)", "",
                "Exemples **réels** de la séance du 2026-10-15 (T1b), pour savoir à quoi ressemble un run sain. "
                "La série machines est courte (quelques minutes) : illustration du format, pas une mesure de run.", ""]
        for f, c in gal:
            out += ["![%s](%s)" % (c, lien("galerie/" + f)), "", "*%s*" % c, ""]
    out += ["## Commandes (PC1)", "",
            "- `zeta-mon-exec --nom N --type test|prod -- <commande>` : lance un run **avec** monitoring (fenêtres pour un test), code retour, rapport",
            "- `zeta-mon-start` / `zeta-mon-stop --code N` : idem pour un run lancé à côté ; `zeta-mon-fenetres` / `zeta-mon-fermer`",
            "- `zeta-mon-on` / `zeta-mon-off` / `zeta-mon-status` : logger machines 1 s + détecteur de secours",
            "- `zeta-live` · `zeta-metrics` · `zeta-gue [--live]` · `zeta-report [run] [--lang en]` · `zeta-index`"]
    ecrire_md(ROOT / "Monitoring-Runs.md", "\n".join(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", nargs="?", default=None)
    ap.add_argument("--lang", default="fr", choices=["fr", "en"])
    ap.add_argument("--index", action="store_true", help="régénère seulement Monitoring-Runs.md")
    a = ap.parse_args()
    if a.index:
        maj_index()
        print("OK :", ROOT / "Monitoring-Runs.md")
        return
    d = a.run_dir
    if not d:
        runs = sorted(dossiers_runs(), key=lambda p: p.name)
        if not runs:
            sys.exit("aucun run dans %s" % RUNS)
        d = runs[-1]
    md, p = rapport(d, a.lang)
    print("OK :", Path(d) / md, "+ PDF" if p else "(sans PDF)")


if __name__ == "__main__":
    main()

# zeta_run_report.py · hprzeta · MAJ 2026-10-17 · 525 lignes
