#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zeta_progress_rapport.py — Rapport « capture + PDF » de l'écran ZETA RUN PROGRESS (touche r).

Produit, pour CE run, dans un dossier donné :
  progress_capture_<horodatage>.png   image de l'écran courant (rendue depuis les addstr enregistrés)
  progress_rapport_<horodatage>.md    rapport (pied de page : date de MAJ + nombre de lignes)
  progress_rapport_<horodatage>.pdf   même contenu en PDF (ReportLab, même moteur que le rapport de monitoring)

Tout ce qui est expliqué vient du code de zeta_run_progress.py et de compute_zeros_v16.py (références
indiquées dans le texte) ; les seuils du verdict sont ceux AFFICHÉS dans le rapport.
Lecture seule sur les logs. Ne jamais écraser un rapport existant (horodatage + suffixe si collision).

Usage de test :  python scripts/zeta_progress_rapport.py LOG_DU_RUN DOSSIER_SORTIE
"""
import datetime as dt
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "monitoring" / "scripts"))

# Seuils du verdict (affichés tels quels dans le rapport)
ECART_PALIERS_MAX = 2        # écart d'avancement signalé en INFO (pas dans le verdict), en paliers de 1000 zéros
RESCAN_BASE = 100            # convention du moteur v16 (compute_zeros_v16.py:436) : rescan = 100 + segment


# ----------------------------------------------------------------------------- capture de l'écran
class EcranEnregistre:
    """Enveloppe un écran curses : enregistre chaque addstr dans une grille {(y, x): (caractère, attribut)}
    pour pouvoir restituer EXACTEMENT ce qui est affiché (Unicode et couleurs inclus). Le reste est délégué."""

    def __init__(self, ecran):
        self._e = ecran
        self.grille = {}

    def __getattr__(self, nom):
        return getattr(self._e, nom)

    def erase(self):
        self.grille = {}
        return self._e.erase()

    def addstr(self, y, x, texte, attr=0):
        for i, c in enumerate(texte):
            self.grille[(y, x + i)] = (c, attr)
        return self._e.addstr(y, x, texte, attr)


# couleurs des paires de zeta_run_progress.init_colors() : numéro -> (avant-plan, fond)
_PAIRES = {1: ("#38d1e0", None), 2: ("#f2c744", None), 3: ("#000000", "#3fbf5f"), 4: ("#000000", "#f2c744"),
           5: ("#000000", "#e05252"), 6: ("#e8e8e8", None), 7: ("#000000", "#e8e8e8")}


def grille_vers_png(grille, h, w, chemin, pair_number=None):
    """Rend la grille en PNG (police DejaVu Sans Mono, fond sombre). Retourne True si écrit."""
    from PIL import Image, ImageDraw, ImageFont
    police = None
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",):
        if Path(p).is_file():
            police = ImageFont.truetype(p, 15)
    if police is None:
        return False
    gras = None
    if Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf").is_file():
        gras = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 15)
    cw = int(round(police.getlength("M")))
    ch = 20
    img = Image.new("RGB", (cw * w + 16, ch * h + 16), "#14161a")
    d = ImageDraw.Draw(img)
    import curses
    for (y, x), (c, attr) in grille.items():
        if not (0 <= y < h and 0 <= x < w):
            continue
        n = (pair_number or curses.pair_number)(attr) if attr else 0
        fg, bg = _PAIRES.get(n, ("#e8e8e8", None))
        px, py = 8 + x * cw, 8 + y * ch
        if bg:
            d.rectangle([px, py, px + cw, py + ch], fill=bg)
        f = gras if (attr & curses.A_BOLD and gras) else police
        d.text((px, py + 1), c, font=f, fill=fg)
    img.save(chemin)
    return True


# ----------------------------------------------------------------------------- analyse (pure, testable)
def analyser(workers, segments, n_total, solo, elapsed=None, eta_fn=None):
    """Contrôles automatiques + chiffres du rapport. `workers` = {id: (count, t, elapsed)} TOUS ids confondus."""
    principaux = {k: v for k, v in workers.items() if k < RESCAN_BASE}
    rescans = {k: v for k, v in workers.items() if k >= RESCAN_BASE}
    n_seg = len(segments)
    anomalies = []                                   # (niveau, texte) ; niveaux : crit, warn, info

    manquants = sorted(set(segments) - set(principaux)) if segments else []
    for k in manquants:
        anomalies.append(("warn", "Worker %d (segment [%.1f ; %.1f]) : aucun palier lu dans le log — normal au démarrage (< 1000 zéros), "
                                  "anormal si les autres workers sont déjà avancés." % ((k,) + tuple(segments[k]))))
    if segments:
        for k in sorted(principaux):
            if k not in segments:
                anomalies.append(("crit", "Id de worker %d hors de 0..%d (segments annoncés dans l'en-tête du log)." % (k, n_seg - 1)))
    for k in sorted(rescans):
        seg = k - RESCAN_BASE
        if seg in segments:
            anomalies.append(("info", "Id %d = rescan ciblé (STEP/2) du segment %d, convention du moteur (100 + segment) : relit des zéros "
                                      "déjà comptés par le worker %d, donc exclu des totaux." % (k, seg, seg)))
        else:
            anomalies.append(("warn", "Id %d ≥ 100 mais le segment %d n'existe pas dans l'en-tête du log." % (k, seg)))

    vus = {}
    for k, (c, t, e) in sorted(principaux.items()):
        vus.setdefault(round(t, 2), []).append(k)
    for t, ks in vus.items():
        if len(ks) > 1:
            anomalies.append(("crit", "Même valeur de t (%.2f) pour les workers %s : deux workers ne devraient jamais "
                                      "avoir le même dernier zéro." % (t, ks)))

    total = sum(c for c, _, _ in principaux.values())
    total_brut = sum(c for c, _, _ in workers.values())
    if n_total and total > n_total:
        anomalies.append(("crit", "Total des workers principaux (%d) > N(T_MAX) attendu (%d)." % (total, n_total)))
    if n_total and total_brut > n_total and rescans:
        anomalies.append(("info", "Le total brut (%d) dépasse N(T_MAX) (%d) parce qu'il inclut le rescan : c'est ce que l'ancien affichage "
                                  "montrait (9 × 17000 = 153000)." % (total_brut, n_total)))

    comptes = [c for c, _, _ in principaux.values()]
    ecart = (max(comptes) - min(comptes)) if comptes else 0
    if comptes and ecart > ECART_PALIERS_MAX * 1000:
        anomalies.append(("info", "Écart de %d zéros entre le worker le plus et le moins avancé : normal en cours de run (les segments ont "
                                  "le même nombre de zéros attendu, mais les workers n'avancent pas à la même vitesse) ; à comparer "
                                  "au bilan final, où tous doivent converger." % ecart))

    lignes = []                                      # tableau par worker
    for k, (c, t, e) in sorted(principaux.items()):
        a, b = segments.get(k, (None, None))
        avanc = ("%.0f %%" % (100 * (t - a) / (b - a))) if a is not None and b and b > a else "?"
        lignes.append((k, a, b, c, t, e, (c / e) if e else None, avanc))

    niveaux = {n for n, _ in anomalies}
    verdict = "à surveiller" if niveaux & {"crit", "warn"} else "sain"
    eta = eta_fn(segments, principaux, elapsed) if (eta_fn and elapsed is not None) else None
    return dict(principaux=principaux, rescans=rescans, anomalies=anomalies, verdict=verdict, lignes=lignes,
                total=total, total_brut=total_brut, n_total=n_total, n_seg=n_seg, ecart=ecart, solo=solo,
                manquants=manquants, eta=eta, elapsed=elapsed)


# ----------------------------------------------------------------------------- contenu du rapport
def construire_blocs(a, png, horo, log_nom):
    B = []
    h = lambda lv, t: B.append(("h", lv, t))
    p = lambda t: B.append(("p", t))
    ul = lambda x: B.append(("ul", x))
    tb = lambda r: B.append(("tb", r))
    h(0, "Rapport d'écran — ZETA RUN PROGRESS")
    p("Capture du %s · log lu : `%s` · **[mesuré]** = lu dans le log ou à l'écran ; **[critère]** = règle fixée par ce rapport "
      "et affichée ; **[code]** = comportement lu dans `zeta_run_progress.py` / `compute_zeros_v16.py`." % (horo, log_nom))
    icone = {"sain": "✔ SAIN", "à surveiller": "⚠ À SURVEILLER"}[a["verdict"]]
    h(1, "1. Verdict : %s" % icone)
    ul(["**Sain** = aucune anomalie de niveau « critique » ni « à surveiller » ; les notes « info » (ex. rescan) ne comptent pas **[critère]**.",
        "Critiques : id de worker hors 0..n_segments−1 · même t pour deux workers · total des principaux > N(T_MAX).",
        "À surveiller : worker sans palier lu · rescan d'un segment inexistant.",
        "Info seulement (pas de verdict) : rescan connu · total brut incluant le rescan · écart d'avancement entre workers "
        "(normal en cours de run : vitesses différentes) **[critère]**."])
    if a["anomalies"]:
        tb([["Niveau", "Contrôle automatique"]] + [[{"crit": "CRITIQUE", "warn": "À SURVEILLER", "info": "info"}[n], t] for n, t in a["anomalies"]])
    else:
        p("Aucune anomalie détectée par les 5 contrôles ci-dessous.")
    h(2, "Contrôles effectués")
    ul(["worker manquant (segment annoncé sans aucun palier)", "id hors plage 0..n_segments−1", "doublon de t entre workers",
        "total des workers principaux > N(T_MAX)", "écart d'avancement entre workers (information)"])

    # pas de titre séparé : le moteur PDF le laisserait seul en bas de page avant l'image (KeepTogether)
    B.append(("fig", png, "**2. Capture de l'écran** — ZETA RUN PROGRESS à l'instant de la touche r (rendu depuis les appels d'affichage enregistrés)."))

    h(1, "3. Les chiffres de CE run")
    tb([["Grandeur", "Valeur"],
        ["N(T_MAX) attendu", "%s [mesuré, lu dans l'en-tête du log]" % (a["n_total"] if a["n_total"] else "inconnu")],
        ["Segments (workers principaux)", str(a["n_seg"])],
        ["Zéros comptés (principaux, paliers)", "%d" % a["total"]],
        ["Zéros comptés (tous ids, rescan inclus)", "%d" % a["total_brut"]],
        ["Avancement", ("%.1f %%" % (100 * a["total"] / a["n_total"])) if a["n_total"] else "?"],
        ["Rescans présents", ", ".join("R%d(id%d)" % (k - RESCAN_BASE, k) for k in sorted(a["rescans"])) or "aucun"],
        ["ETA(√t)", ("%.1f min" % (a["eta"] / 60)) if a["eta"] is not None else "indisponible (pas assez de données)"]])
    h(2, "Détail par worker")
    rows = [["Worker", "Segment [a ; b]", "Palier (zéros)", "t du dernier zéro", "Écoulé (s)", "z/s", "Avancement"]]
    for k, aa, bb, c, t, e, v, av in a["lignes"]:
        rows.append(["W%d" % k, ("[%.0f ; %.0f]" % (aa, bb)) if aa is not None else "?", str(c), "%.0f" % t, "%.1f" % e,
                     ("%.0f" % v) if v else "?", av])
    tb(rows)
    p("**z/s** = palier ÷ temps écoulé au dernier palier lu, calculé par ce rapport **[critère]** ; "
      "**Avancement** = (t − a) ÷ (b − a) dans le segment du worker **[critère]**.")

    h(1, "4. Lecture de chaque élément de l'écran")
    ul(["**Titre** : « PC1 SOLO (v16) » si le log `run_T*_*.log` est plus récent que `distribute_T*_*.log`, sinon « PC1/PC2 » "
        "(détection par date de modification, `draw()`) **[code]**.",
        "**Barre globale** (en haut) : mode solo = bandeau plein « PC1 100 % — totalité de T_MAX », N(T_MAX) lu dans la ligne « N zéros ≈ … » "
        "du log (`parse_solo_header`). Mode distribué = répartition cible PC1/PC2 de N(T_MAX) lue dans le log maître **[code]**.",
        "**Barres PC1 / PC2** : « zéros X/Y » = X : somme des paliers des workers principaux · Y : zéros assignés à la machine ; "
        "le pourcentage = 100·X/Y plafonné à 100 **[code]**.",
        "**ETA(√t)** : temps restant du PIRE worker, en supposant un coût par zéro ∝ √t, soit coût(a→b) ∝ (2/3)(b^1,5 − a^1,5) "
        "(`eta_sqrt_weighted`) **[code]**. Variante « n/N workers démarrés » : tous les workers n'ont pas encore écrit de palier, "
        "l'estimation ne porte que sur les workers démarrés et peut être trop optimiste (« ≥ »). « ETA(lin, optimiste) » : règle de trois, "
        "utilisée seulement sans données par worker.",
        "**CPU / RAM / DSK** : sonde toutes les %d s (locale pour PC1, SSH pour PC2). CPU = écart de `/proc/stat` sur 0,4 s ; RAM = "
        "(MemTotal − MemAvailable)/MemTotal ; DSK = occupation de `/` (statvfs). Couleur : vert < 60 %%, jaune < 85 %%, rouge au-delà "
        "(`load_pct_color`) **[code]**." % 4,
        "**PC2** : en mode solo, affichée en grisé « non utilisé pour ce run (solo PC1, v16 pas dispo sur PC2) » — c'est un choix du code, "
        "pas une panne **[code]**.",
        "**Détail workers (touche d)** : une entrée par worker, voir ci-dessous."])
    h(2, "Signification exacte de « W3:#17000@t=53662 »")
    ul(["**W3** : worker n°3 (rang dans l'ordre des ids ; l'id brut est ajouté entre parenthèses s'il diffère) **[code]**.",
        "**#17000** : nombre de zéros trouvés PAR CE WORKER dans SON segment, arrondi au millier inférieur : le moteur n'écrit une ligne "
        "qu'aux paliers `(n // 1000) × 1000` (`compute_zeros_v16.py:291`) — c'est un **nombre de zéros**, pas un t **[code]**.",
        "**t=53662** : partie imaginaire t du DERNIER zéro trouvé par ce worker (`zeros_segment[-1]`), arrondie à l'entier ; sans unité "
        "(ordonnée sur la droite critique Re(s)=½) **[code]**.",
        "Le temps écoulé (« — 20,3s » dans le log) est en **secondes depuis le démarrage de ce worker** **[code]**.",
        "**R5(id105)** : rescan ciblé du segment 5 (STEP/2), id = 100 + 5 ; il apparaît sur une ligne « rescan » à part."])

    h(1, "5. Interprétation")
    pr = a["principaux"]
    if pr:
        cs = [c for c, _, _ in pr.values()]
        vit = [c / e for c, _, e in pr.values() if e]
        ul(["**Équilibrage** : paliers de %d à %d zéros (écart %d) ; le moteur découpe [T_MIN ; T_MAX] en segments à nombre de zéros "
            "attendu comparable (`_partitionner_adaptatif`), donc des paliers voisins sont NORMAUX **[mesuré]**." % (min(cs), max(cs), a["ecart"]),
            ("**Vitesse** : de %.0f à %.0f z/s selon le worker (les segments hauts coûtent plus par zéro, coût ∝ √t) **[mesuré]**." % (min(vit), max(vit)))
            if vit else "**Vitesse** : indisponible.",
            ("**Dépassement** : aucun, total principal %d ≤ N(T_MAX) %d **[mesuré]**." % (a["total"], a["n_total"]))
            if (a["n_total"] and a["total"] <= a["n_total"]) else "**Dépassement** : voir les contrôles ci-dessus.",
            "**PC2 non utilisé** : en mode solo le code n'attribue rien à PC2 (la v16 n'est pas disponible sur PC2) **[code]**."
            if a["solo"] else "**PC2** : run distribué, voir la barre PC2 de la capture."])
    else:
        p("Aucun worker n'a encore écrit de palier : le run démarre (phase de scan initiale) ou le log n'est pas celui du run.")

    h(1, "6. Glossaire")
    tb([["Terme", "Débutant", "Expert"],
        ["Zéro", "Valeur de t où la fonction zêta de Riemann s'annule sur la droite critique.", "ζ(½+it) = 0 ; ici zéros non triviaux, comptés par N(T)."],
        ["N(T_MAX)", "Combien de zéros on s'attend à trouver jusqu'à T_MAX.", "Riemann–von Mangoldt : N(T) ≈ (T/2π)·ln(T/2πe) + 7/8 (heuristique de comptage, vérifiée par Turing)."],
        ["Worker", "Un processus qui calcule une tranche de t.", "Process du Pool multiprocessing, un segment [a ; b] chacun (fork)."],
        ["Palier", "Le compteur n'avance que par milliers.", "Journalisation `(n//1000)*1000` du moteur v16."],
        ["Rescan", "Deuxième passage plus fin sur une tranche où il manquait un zéro.", "Rescan à STEP/2 des segments en déficit (déphasage de grille), id 100+segment."],
        ["ETA(√t)", "Temps restant estimé, en tenant compte que le calcul ralentit quand t monte.", "Extrapolation du coût ∫√t dt par worker, max sur les workers."],
        ["Illinois / Arb", "Méthode d'affinage numérique d'un zéro.", "Secante modifiée, Arb/FLINT double précision (`illinois_refine_arb`)."],
        ["Turing", "Test de complétude du nombre de zéros trouvés.", "Vérification numérique via N(T) et la fonction S(T) ; pas une preuve."]])
    return B


# ----------------------------------------------------------------------------- run actif
def _vivant(pid):
    """Processus vivant et non zombie (même critère que le superviseur du monitoring)."""
    try:
        return open("/proc/%d/stat" % int(pid)).read().rsplit(")", 1)[1].split()[0] != "Z"
    except (OSError, ValueError):
        return False


def racine_runs():
    """monitoring/runs (ZETA_MON_ROOT, comme le monitoring, sinon <projet>/monitoring)."""
    import os
    return Path(os.environ.get("ZETA_MON_ROOT", HERE.parent / "monitoring")) / "runs"


def detecter_run_actif(racine=None):
    """Run actif = runs/{test,prod}/<id>/ avec meta.json « en cours », sans fichier .fin, superviseur vivant.
    Retourne (dossier, nb_candidats) ; (None, 0) si aucun. Plusieurs candidats : le plus récent (t0)."""
    import json
    racine = Path(racine) if racine else racine_runs()
    cands = []
    for typ in ("test", "prod"):
        for meta in (racine / typ).glob("*/meta.json"):
            d = meta.parent
            try:
                m = json.loads(meta.read_text())
                pid = (d / "superviseur.pid").read_text().strip()
            except (OSError, ValueError):
                continue
            if m.get("statut") == "en cours" and not (d / ".fin").exists() and _vivant(pid):
                cands.append((m.get("t0", ""), d))
    if not cands:
        return None, 0
    return max(cands)[1], len(cands)


# ----------------------------------------------------------------------------- génération
def chemin_libre(dossier, base, ext):
    """Ne jamais écraser : <base>.<ext>, sinon <base>_2.<ext>, ..."""
    c = Path(dossier) / ("%s.%s" % (base, ext))
    n = 2
    while c.exists():
        c = Path(dossier) / ("%s_%d.%s" % (base, n, ext))
        n += 1
    return c


def generer(dossier, grille, h, w, workers, segments, n_total, solo, log_path, elapsed=None, eta_fn=None, pair_number=None):
    """Écrit PNG + MD + PDF dans `dossier` ; retourne (png, md, pdf) (pdf = None si ReportLab absent)."""
    from zeta_mon_common import ecrire_md
    from zeta_run_report import pdf as pdf_reportlab
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    maintenant = dt.datetime.now()
    horo = maintenant.strftime("%Y%m%d_%H%M%S")
    base = "progress_rapport_%s" % horo
    png = chemin_libre(dossier, "progress_capture_%s" % horo, "png")
    md = chemin_libre(dossier, base, "md")
    pdf_p = md.with_suffix(".pdf")
    if pdf_p.exists():
        pdf_p = chemin_libre(dossier, base, "pdf")
    if not grille_vers_png(grille, h, w, png, pair_number):
        raise RuntimeError("police DejaVu Sans Mono introuvable : capture impossible")
    a = analyser(workers, segments, n_total, solo, elapsed, eta_fn)
    B = construire_blocs(a, png.name, maintenant.strftime("%Y-%m-%d %H:%M:%S"), Path(log_path).name if log_path else "?")
    # --- MD (même contenu que le PDF) + pied de page date/lignes
    L = []
    for b in B:
        if b[0] == "h":
            L += ["#" * (b[1] + 1) + " " + b[2], ""]
        elif b[0] == "p":
            L += [b[1], ""]
        elif b[0] == "ul":
            L += ["- " + x for x in b[1]] + [""]
        elif b[0] == "fig":
            L += ["![%s](%s)" % (b[2], b[1]), "", "*%s*" % b[2], ""]
        elif b[0] == "tb":
            r = b[1]
            L += ["| " + " | ".join(r[0]) + " |", "|" + "---|" * len(r[0])] + ["| " + " | ".join(str(c) for c in x) + " |" for x in r[1:]] + [""]
    n = ecrire_md(md, "\n".join(L))
    ok = pdf_reportlab(pdf_p, B, dossier, "Rapport d'écran — ZETA RUN PROGRESS", md.stem, n)
    return png, md, (pdf_p if ok else None)


if __name__ == "__main__":
    # Test hors TUI : rapport « d'après un log » avec une grille construite à partir du texte du log (sans curses).
    import zeta_run_progress as zrp
    if len(sys.argv) != 3:
        sys.exit("usage : zeta_progress_rapport.py LOG DOSSIER_SORTIE")
    log, sortie = sys.argv[1], sys.argv[2]
    wk = dict(zrp.parse_worker_progress(log))
    seg = zrp.parse_segments(log)
    hd = zrp.parse_solo_header(log)
    grille = {(0, i): (c, 0) for i, c in enumerate("(test hors TUI) écran non disponible : lancer la touche r dans le TUI")}
    print(generer(sortie, grille, 3, 80, wk, seg, hd["n_total"] if hd else None, True, log, elapsed=max((e for _, _, e in wk.values()), default=0),
                  eta_fn=zrp.eta_sqrt_weighted, pair_number=lambda a: 0))
