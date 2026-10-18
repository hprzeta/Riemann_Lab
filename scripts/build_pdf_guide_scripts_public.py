#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_pdf_guide_scripts_public.py — Variante PUBLIABLE du guide « Mode d'emploi des scripts Cluster Zêta ».

Ne modifie NI le .md source NI scripts/build_pdf_guide_scripts.py : lit le .md privé, remplace
les IP internes et le domaine DDNS par des placeholders, REFUSE de produire le PDF s'il reste
un motif sensible, puis appelle construit() du générateur d'origine.

Aucune valeur réelle (IP, domaine) n'est écrite dans ce fichier : les remplacements se font
par POSITION (colonne d'adresses du tableau des machines) et par motif, jamais par valeur.

Usage :
    python scripts/build_pdf_guide_scripts_public.py md/script/Guide_Scripts_Cluster_Zeta.md \
           <dossier_versionné>/Guide_Scripts_Cluster_Zeta_AAAAMMJJ_public.pdf

Méthode reprise de scripts/zeta_diag_publier.sh : masquage par regex, puis contrôle résiduel
bloquant ; la version publiable n'est jamais éditée à la main.
"""
import os                                        # chemins et existence de fichiers
import re                                        # remplacements et contrôle résiduel
import sys                                       # arguments de la ligne de commande
import tempfile                                  # .md anonymisé temporaire (jamais conservé)
import importlib.util                            # import du générateur d'origine par son chemin

# Ligne du tableau des machines : |PCn zeta-xxx|<colonne adresses>|reste...  (colonne 2 = adresses)
LIGNE_MACHINE = re.compile(r"^\|(PC([1-5]) zeta-[\w-]+)\|[^|]*\|", re.M)
# Placeholder de la colonne d'adresses, par numéro de machine
PLACEHOLDER_ADRESSE = {
    "1": "local (<IP-PC1>)",                     # PC1 : orchestrateur local
    "2": "<IP-PC2>",                             # PC2 : second nœud de calcul
    "3": "<IP-PC3>",                             # PC3 : backup
    "4": "<IP-BASTION-WG> / <IP-BASTION-LAN>",   # PC4 : bastion (adresse WireGuard / adresse LAN)
    "5": "<IP-PC5>",                             # PC5 : monitoring
}
# Autres remplacements (motif → placeholder), chacun attendu exactement 1 fois
AUTRES = [
    (r"(?i)duckdns", "<DOMAINE-DDNS>"),                                           # service DDNS
    (re.escape("(révision de l'édition du 19/09/2026)"),                          # bandeau publiable
     "(révision de l'édition du 19/09/2026) · version publiable : IP et domaine DDNS masqués"),
]

# Motifs qui ne doivent PLUS exister dans le texte anonymisé (même logique que zeta_diag_publier.sh)
INTERDITS = {
    "IPv4": r"\b(\d{1,3}\.){3}\d{1,3}\b",
    "MAC": r"\b([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b",
    "IPv6": r"\b[0-9a-fA-F]{1,4}(:[0-9a-fA-F]{1,4}){3,7}\b",
    "DDNS": r"(?i)duckdns",
    "e-mail": r"[\w.-]+@[\w-]+\.[a-z]{2,}",
    "secret": r"ghp_|github_pat|PRIVATE KEY",
}


def charge_generateur():
    """Importe construit() depuis scripts/build_pdf_guide_scripts.py sans le modifier."""
    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_pdf_guide_scripts.py")
    spec = importlib.util.spec_from_file_location("build_pdf_guide_scripts", chemin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def anonymise(texte):
    """Remplace par position/motif, vérifie chaque remplacement, puis le contrôle résiduel."""
    # 1) Colonne d'adresses du tableau des machines : les 5 lignes PC1..PC5 doivent être trouvées
    vues = []

    def remplace_ligne(m):
        vues.append(m.group(2))                                          # mémorise le numéro de PC
        return f"|{m.group(1)}|{PLACEHOLDER_ADRESSE[m.group(2)]}|"       # garde le nom, masque l'adresse

    texte = LIGNE_MACHINE.sub(remplace_ligne, texte)
    if sorted(vues) != ["1", "2", "3", "4", "5"]:                        # source modifiée : on s'arrête
        sys.exit(f"Tableau des machines : lignes PC1..PC5 attendues, trouvé {sorted(vues)}")
    # 2) Autres remplacements : exactement 1 occurrence chacun
    for motif, nouveau in AUTRES:
        texte, n = re.subn(motif, lambda _m, r=nouveau: r, texte)
        if n != 1:
            sys.exit(f"Remplacement attendu 1 fois, trouvé {n} fois : {motif!r}")
    # 3) Contrôle résiduel bloquant (les commentaires HTML du .md sont contrôlés aussi)
    for nom, motif in INTERDITS.items():
        trouve = [m.group(0) for m in re.finditer(motif, texte)]
        if trouve:
            sys.exit(f"Contrôle résiduel : {len(trouve)} motif(s) {nom} restant(s) — PDF non généré")
    return texte


if __name__ == "__main__":
    if len(sys.argv) != 3:                                               # contrôle des arguments
        sys.exit("Usage : build_pdf_guide_scripts_public.py source.md sortie_public.pdf")
    src, out = sys.argv[1], sys.argv[2]
    if not os.path.isfile(src):                                          # le .md doit exister
        sys.exit(f"Source introuvable : {src}")
    if not out.endswith("_public.pdf"):                                  # suffixe obligatoire
        sys.exit("Le fichier de sortie doit se terminer par _public.pdf")
    if os.path.exists(out):                                              # jamais d'écrasement
        sys.exit(f"Refus d'écraser un fichier existant : {out}")
    texte = anonymise(open(src, encoding="utf-8").read())                # .md anonymisé en mémoire
    gen = charge_generateur()                                            # générateur d'origine
    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False) as tmp:
        tmp.write(texte)                                                 # écrit le .md anonymisé
        chemin_tmp = tmp.name
    try:
        gen.construit(chemin_tmp, out)                                   # rendu identique à l'original
    finally:
        os.unlink(chemin_tmp)                                            # le .md temporaire est supprimé
    print(f"PDF publiable généré : {out}")
