#!/usr/bin/env python3
# =============================================================================
# zeta_log_lisible.py — Transforme un log brut de terminal (script) en .md lisible
# Auteur : hprzeta · Projet : Riemann_Lab · Créé : 3 novembre 2026
# Usage  : zeta_log_lisible.py LOG [-o SORTIE.md]   (défaut : même nom en .md)
#          zeta_log_lisible.py --tout [DOSSIER]     (régénère tous les .md du dossier)
# Garanties : lecture SEULE du .log ; aucune séquence d'échappement ne subsiste ;
#             sortie en mode 600 ; vérification finale (échec si un caractère de contrôle reste).
# =============================================================================
import argparse  # options de ligne de commande
import glob  # recherche des .log
import os  # chemins et droits
import re  # expressions régulières
import sys  # codes de retour

DOSSIER = os.path.expanduser("~/projet_zeta/claude-traitement-journalier")  # dossier des sessions

# Séquences OSC (titre de fenêtre, etc.) : ESC ] ... BEL ou ESC \
RE_OSC = re.compile(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)")
# Séquences APC/DCS/PM (images Kitty, etc.) : ESC _ ... ESC \
RE_APC = re.compile(r"\x1b[_PX^][^\x1b]*(?:\x1b\\)?")
# Séquences CSI : ESC [ paramètres intermédiaires final
RE_CSI = re.compile(r"\x1b\[([0-?]*)([ -/]*)([@-~])")
# Autres échappements à 2 caractères (ESC 7, ESC 8, ESC =, ESC > ...)
RE_ESC2 = re.compile(r"\x1b[@-Z\\-_0-9=>]")
# Caractères de contrôle restants (on garde \n et \t)
RE_CTRL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
# Ligne ne contenant que du tracé de cadre / espaces
RE_CADRE = re.compile(r"^[\s─│┌┐└┘├┤┬┴┼═║╭╮╰╯▐▛▜▝▘█▀▄▌▖▗·•⏵⏸⎿⤷●○◐]*$")


def _csi(m):
    """Remplace une séquence CSI : saut de ligne si déplacement/effacement, rien sinon."""
    final = m.group(3)
    if final in "HfdABEFJKGST":  # positionnement / effacement : sépare les fragments
        return "\n"
    if final == "C":  # curseur à droite : un espace
        return " "
    return ""  # couleurs (m), modes (h/l), etc. : supprimés


def nettoyer(texte):
    """Retourne le texte lisible (sans séquences d'échappement, sans doublons)."""
    texte = texte.replace("\r\n", "\n").replace("\r", "\n")  # fins de ligne
    texte = re.sub(r".\x08", "", texte, flags=re.S)  # backspace : efface le caractère précédent
    texte = RE_OSC.sub("", texte)  # titres de fenêtre
    texte = RE_APC.sub("", texte)  # APC / DCS
    texte = RE_CSI.sub(_csi, texte)  # CSI
    texte = RE_ESC2.sub("", texte)  # échappements courts
    texte = texte.replace("\x1b", "")  # ESC isolé résiduel
    texte = RE_CTRL.sub("", texte)  # contrôles restants
    sortie, precedent = [], None
    for ligne in texte.split("\n"):
        l = ligne.rstrip()
        if len(l.strip()) < 3 or RE_CADRE.match(l):  # fragments vides ou tracés de cadre
            continue
        if l == precedent:  # redessin identique du TUI
            continue
        sortie.append(l)
        precedent = l
    return "\n".join(sortie) + "\n"


def convertir(src, dst):
    """Lit src, écrit dst (mode 600) et vérifie qu'aucun contrôle ne subsiste."""
    with open(src, encoding="utf-8", errors="replace") as f:  # lecture seule
        brut = f.read()
    propre = nettoyer(brut)
    if re.search(r"[\x00-\x08\x0b-\x1f\x7f]", propre):  # contrôle final
        print(f"⚠️  caractères de contrôle résiduels dans {src}", file=sys.stderr)
        return False
    fd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)  # créé en 600 d'emblée
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(propre)
    print(f"✅ {dst} ({propre.count(chr(10))} lignes)")
    return True


def main():
    p = argparse.ArgumentParser(description="Log brut de terminal -> .md lisible")
    p.add_argument("log", nargs="?", help="fichier .log (ou dossier avec --tout)")
    p.add_argument("-o", "--sortie", help="fichier .md de sortie")
    p.add_argument("--tout", action="store_true", help="régénère tous les .md du dossier")
    a = p.parse_args()
    if a.tout:
        dossier = a.log or DOSSIER
        ok = True
        for log in sorted(glob.glob(os.path.join(dossier, "session_*.log"))):
            ok &= convertir(log, os.path.splitext(log)[0] + ".md")
        return 0 if ok else 2
    if not a.log or not os.path.isfile(a.log):
        print("Fichier .log introuvable", file=sys.stderr)
        return 1
    return 0 if convertir(a.log, a.sortie or os.path.splitext(a.log)[0] + ".md") else 2


if __name__ == "__main__":
    sys.exit(main())
