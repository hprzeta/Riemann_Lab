#!/usr/bin/env python3
# ==============================================================================
# zeta_script.py — menu des alias de ~/.bashrc (alias : zeta-script)
# Liste les alias RÉELLEMENT présents dans ~/.bashrc, avec un libellé d'une phrase.
# Aucune écriture : lecture de ~/.bashrc ; un alias n'est lancé qu'après confirmation.
# Usage : zeta-script            (menu)  |  zeta-script --liste  (liste seule)
# Limite : un alias qui fait « cd » ou « source » n'agit que dans le sous-shell
#          lancé ici ; pour qu'il agisse sur votre terminal, tapez-le directement.
# ==============================================================================
import os
import re
import shlex
import subprocess
import sys

BASHRC = os.path.expanduser("~/.bashrc")  # fichier lu en lecture seule

# Libellé d'une phrase par alias (un alias absent d'ici est listé « (pas de libellé) »)
LIBELLES = {
    "ll": "Liste détaillée du dossier, fichiers cachés inclus.",
    "la": "Liste des fichiers, cachés inclus.",
    "l": "Liste compacte en colonnes.",
    "alert": "Notification bureau à la fin d'une longue commande.",
    "zeta-proj": "Aller dans le dossier du projet.",
    "zeta": "Aller dans le projet et activer l'environnement Python.",
    "zeta-docs": "Aller dans le dossier docs.",
    "zeta-data": "Aller dans le dossier de données /mnt/data.",
    "zeta-logs": "Suivre en direct le journal du projet.",
    "zeta-monitor": "Moniteur texte du cluster.",
    "zeta-webmonitor": "Moniteur web du cluster.",
    "zeta-notebook": "Lancer Jupyter Notebook.",
    "zeta-jupyter": "Lancer JupyterLab.",
    "zeta-spyder": "Lancer l'éditeur Spyder.",
    "zeta-code": "Ouvrir le projet dans VS Code.",
    "zeta-python": "Activer l'environnement Python dans src/calculs.",
    "zeta-tmux": "Ouvrir ou rejoindre la session tmux « zeta ».",
    "zeta-run": "Lancer un run de calcul de zéros (avec turbo).",
    "zeta-turbo-on": "Activer le mode turbo avant un calcul (sudo).",
    "zeta-turbo-off": "Désactiver le mode turbo après un calcul (sudo).",
    "wg-auto": "Gérer le tunnel WireGuard automatiquement.",
    "zeta-cluster": "Ouvrir la vue tmux de tout le cluster.",
    "zeta-distribute": "Répartir un run sur plusieurs machines.",
    "zeta-progress-tmux": "Rejoindre la session tmux de progression.",
    "zeta-log": "Dernière ligne du journal du run réparti.",
    "zeta-pid": "Dire si un run réparti est actif.",
    "zeta-progress": "Afficher la progression du run en cours.",
    "zeta-backup-status": "État des sauvegardes.",
    "zeta-clone": "Menu de clonage et restauration du disque (sudo).",
    "zeta-temp": "Surveiller les températures du cluster.",
    "zeta-update": "Mettre à jour les machines du cluster.",
    "zeta-proton": "État de la sauvegarde vers Proton.",
    "zeta-ecran-off": "Désactiver le fond d'écran animé.",
    "zeta-ecran-on": "Réactiver le fond d'écran animé.",
    "zeta-inventaire": "Faire l'inventaire du cluster.",
    "zeta-rag": "Menu du RAG (base de connaissances locale).",
    "zeta-backup-horsgit": "Sauvegarder les fichiers hors dépôt git.",
    "zeta-capture-conv": "Enregistrer la session du terminal (avant claude).",
    "zeta-convert-jsontomd": "Convertir une session Claude Code en Markdown masqué.",
    "zeta-export-claudeai": "Exporter l'état du projet masqué pour claude.ai.",
    "zeta-script": "Ce menu des alias.",
}

# Alias à confirmer avec un avertissement renforcé (sudo, runs lourds, écritures disque)
SENSIBLES = {"zeta-clone", "zeta-turbo-on", "zeta-turbo-off", "zeta-run",
             "zeta-distribute", "zeta-update", "zeta-backup-horsgit"}


def lire_alias():
    """Retourne la liste [(nom, commande)] des alias définis dans ~/.bashrc."""
    resultat = []  # accumulateur
    with open(BASHRC, encoding="utf-8") as f:  # lecture seule
        for ligne in f:  # parcours ligne à ligne
            m = re.match(r"^alias\s+([^=\s]+)=(.*)$", ligne.rstrip("\n"))  # « alias nom=... »
            if not m:
                continue  # ligne qui n'est pas un alias
            nom, brut = m.group(1), m.group(2)  # nom et valeur brute
            try:
                cmd = " ".join(shlex.split(brut))  # retire les guillemets du shell
            except ValueError:
                cmd = brut  # guillemets mal appariés : valeur brute
            resultat.append((nom, cmd))  # on garde dans l'ordre du fichier
    return resultat


def afficher(alias):
    """Affiche le menu numéroté."""
    print("\n  N°  ALIAS                    LIBELLÉ")
    print("  " + "-" * 72)
    for i, (nom, _) in enumerate(alias, 1):  # numérotation à partir de 1
        marque = "⚠" if nom in SENSIBLES else " "  # signale les alias sensibles
        lib = LIBELLES.get(nom, "(pas de libellé)")  # libellé ou valeur par défaut
        print(f"  {i:>2}{marque} {nom:<24} {lib}")
    print("\n  ⚠ = alias sensible (sudo, run lourd ou écriture disque)")


def lancer(nom, cmd):
    """Montre la commande réelle, demande confirmation, puis lance l'alias."""
    print(f"\n  Alias    : {nom}\n  Commande : {cmd}")
    if nom in SENSIBLES:
        print("  ⚠ Alias sensible : relisez la commande avant de confirmer.")
    rep = input("  Lancer ? [o/N] ").strip().lower()  # défaut = non
    if rep not in ("o", "oui"):
        print("  Annulé.")
        return
    # Shell interactif : charge ~/.bashrc, donc l'alias est bien développé
    subprocess.run(["bash", "-ic", nom])


def main():
    alias = lire_alias()  # alias actuels du fichier
    if not alias:
        print("Aucun alias trouvé dans ~/.bashrc")
        return 1
    afficher(alias)
    if "--liste" in sys.argv:  # mode liste seule : pas de menu
        return 0
    while True:  # boucle du menu
        choix = input("\n  Numéro (ou q pour quitter) : ").strip().lower()
        if choix in ("q", "quit", "exit", ""):
            return 0  # sortie propre
        if not choix.isdigit() or not 1 <= int(choix) <= len(alias):
            print("  Numéro invalide.")
            continue
        nom, cmd = alias[int(choix) - 1]  # alias choisi
        lancer(nom, cmd)


if __name__ == "__main__":
    sys.exit(main())
