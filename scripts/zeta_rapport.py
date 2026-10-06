#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zeta_rapport.py — Rapports Markdown du cluster Zeta, à partir des inventaires.

Ce script est en LECTURE SEULE :
  - il ne se connecte à aucun PC ;
  - il ne modifie jamais les fichiers d'inventaire ;
  - il écrit uniquement dans ~/zeta_inventaire/RAPPORT/ (dossier privé).

Entrée  : ~/zeta_inventaire/inventaire_PCn_*.txt  (le plus récent de chaque PC,
          produit par zeta_inventaire.sh)
Sortie  : PCn_<nom>.md              rapport complet d'un PC (tableaux)
          PCn_annexe_paquets.md     liste exhaustive des paquets
          CLUSTER_comparatif.md     comparatif des 5 PC + adressage observé

Usage   : ./zeta_rapport.py            (menu)
          ./zeta_rapport.py 3          (rapport PC3)
          ./zeta_rapport.py tous       (5 rapports + comparatif)
          ./zeta_rapport.py comparatif (comparatif seul)
"""

import glob
import os
import re
import sys
from datetime import datetime
from pathlib import Path

INV_DIR = Path(os.environ.get("ZETA_INVENTAIRE_DIR", Path.home() / "zeta_inventaire"))
OUT_DIR = INV_DIR / "RAPPORT"

PCS = {
    1: ("PC1", "zeta-lab"),
    2: ("PC2", "zeta-calc-second"),
    3: ("PC3", "zeta-backup"),
    4: ("PC4", "zeta-secure"),
    5: ("PC5", "zeta-monitor"),
}

BANNIERE = ("> **DOCUMENT PRIVÉ** : contient des IP, adresses MAC et empreintes SSH. "
            "Ne pas publier (wiki public, GitHub Pages, dossier `docs/`).")

CHASSIS = {"3": "Tour (desktop)", "4": "Desktop compact", "6": "Mini-tour", "7": "Tour",
           "8": "Portable", "9": "Portable (laptop)", "10": "Portable (notebook)",
           "13": "Tout-en-un", "30": "Tablette", "31": "Convertible"}


# =============================================================================
#  1. LECTURE D'UN FICHIER D'INVENTAIRE
# =============================================================================
RE_SEC = re.compile(r"^={20} (.+?) ={20}$")     # ==== TITRE ====
RE_SUB = re.compile(r"^--- (.+?) ---$")         # --- sous-titre ---


def nettoyer(lignes):
    """Retire les lignes vides au début et à la fin d'une liste de lignes."""
    lignes = list(lignes)
    while lignes and not lignes[0].strip():
        lignes.pop(0)
    while lignes and not lignes[-1].strip():
        lignes.pop()
    return lignes


class Inventaire:
    """Un fichier d'inventaire découpé en blocs : sections, sous-titres, commandes."""

    def __init__(self, chemin):
        self.chemin = Path(chemin)
        self.lignes = self.chemin.read_text(encoding="utf-8", errors="replace").splitlines()
        self.blocs = []                       # liste de (genre, titre, lignes)
        courant = ("debut", "", [])
        self.blocs.append(courant)
        for ln in self.lignes:
            m = RE_SEC.match(ln)
            if m:
                courant = ("sec", m.group(1), [])
                self.blocs.append(courant)
                continue
            m = RE_SUB.match(ln)
            if m:
                courant = ("sub", m.group(1), [])
                self.blocs.append(courant)
                continue
            if ln.startswith("$ "):
                courant = ("cmd", ln[2:], [])
                self.blocs.append(courant)
                continue
            courant[2].append(ln)
        self.bsd = any(g == "sec" and "(BSD)" in t for g, t, _ in self.blocs)
        self.ident = self._kv(self.section("IDENTITE"))

    # --- accès aux blocs -----------------------------------------------------
    def _chercher(self, genre, prefixe):
        # Plusieurs blocs peuvent porter le même titre (partie « droits root »
        # ignorée, puis « complément root » réussi) : on garde celui qui a le
        # moins de lignes « (ignoré … »; à égalité, le dernier.
        meilleur, score = [], None
        for g, t, lignes in self.blocs:
            if g == genre and t.startswith(prefixe):
                bloc = nettoyer(lignes)
                n = sum(1 for ln in bloc if ln.startswith("(ignoré"))
                if score is None or n <= score:
                    meilleur, score = bloc, n
        return meilleur

    def cmd(self, prefixe):
        """Sortie de la première commande `$ prefixe...`."""
        return self._chercher("cmd", prefixe)

    def sub(self, prefixe):
        """Contenu du premier sous-titre `--- prefixe... ---`."""
        return self._chercher("sub", prefixe)

    def section(self, prefixe):
        """Lignes d'une section avant son premier sous-bloc."""
        return self._chercher("sec", prefixe)

    def tout_contient(self, motif):
        return any(re.search(motif, ln) for ln in self.lignes)

    @staticmethod
    def _kv(lignes, sep=":"):
        d = {}
        for ln in lignes:
            if sep in ln:
                k, v = ln.split(sep, 1)
                d.setdefault(k.strip(), v.strip())
        return d

    # --- informations générales ---------------------------------------------
    @property
    def hostname(self):
        return self.ident.get("Hostname", "?")

    @property
    def date(self):
        return self.ident.get("Date", "?")

    @property
    def root_ok(self):
        return self.ident.get("Privileges", "").startswith("root")

    @property
    def nb_ignores(self):
        return sum(1 for ln in self.lignes if "ignoré : droits root requis" in ln)

    @property
    def complement_root(self):
        return self.tout_contient(r"Complément root ajouté")


# =============================================================================
#  2. PETITS OUTILS DE MISE EN FORME MARKDOWN
# =============================================================================
def esc(x):
    return str(x).replace("|", "\\|").replace("\n", " ")


def tableau(entetes, lignes):
    """Tableau Markdown. Si aucune ligne : liste vide (la section est omise)."""
    if not lignes:
        return []
    out = ["| " + " | ".join(esc(e) for e in entetes) + " |",
           "|" + "|".join("---" for _ in entetes) + "|"]
    for r in lignes:
        out.append("| " + " | ".join(esc(c) for c in r) + " |")
    out.append("")
    return out


def code(lignes, langue=""):
    return ["```" + langue] + list(lignes) + ["```", ""]


def titre(niveau, texte):
    return ["", "#" * niveau + " " + texte, ""]


def info(texte):
    return [texte, ""]


def raccourcir(lignes, maxi=40):
    if len(lignes) <= maxi:
        return list(lignes)
    return list(lignes[:maxi]) + [f"... ({len(lignes) - maxi} lignes de plus dans l'inventaire)"]


def ignore(lignes):
    """Vrai si la sortie ne contient que le message « ignoré : droits root »."""
    return bool(lignes) and all("ignoré : droits root requis" in ln for ln in lignes if ln.strip())


# =============================================================================
#  3. EXTRACTION DES INFORMATIONS (Linux)
# =============================================================================
def os_nom(inv):
    if inv.bsd:
        m = re.search(r"^OpenBSD \S+ (\S+)", " ".join(inv.cmd("uname -a")))
        return f"OpenBSD {m.group(1)}" if m else "OpenBSD"
    kv = Inventaire._kv(inv.cmd("cat /etc/os-release"), "=")
    return kv.get("PRETTY_NAME", "?").strip('"')


def noyau(inv):
    if inv.bsd:
        m = re.search(r"^OpenBSD \S+ \S+ (\S+)", " ".join(inv.cmd("uname -a")))
        return m.group(1) if m else "?"
    r = inv.cmd("uname -r")
    return r[0] if r else "?"


def architecture(inv):
    txt = " ".join(inv.cmd("uname -a"))
    m = re.search(r"\b(x86_64|amd64|i[3-6]86|aarch64|arm\w*)\b", txt)
    return m.group(1) if m else "?"


def uptime(inv):
    txt = " ".join(inv.cmd("uptime"))
    m = re.search(r"up\s+(.*?),\s+\d+ users?", txt)
    return m.group(1).strip() if m else txt.strip()


def lscpu(inv):
    return Inventaire._kv(inv.cmd("lscpu"))


def modele_machine(inv):
    if inv.bsd:
        kv = Inventaire._kv(inv.cmd("sysctl hw.vendor"), "=")
        return kv.get("hw.vendor", "?"), kv.get("hw.product", "?")
    kv = Inventaire._kv(inv.sub("") if False else inv.section("MATERIEL - MACHINE"))
    return kv.get("sys_vendor", "?"), kv.get("product_name", "?").strip()


def ram_total(inv):
    """Retourne (ram_texte, swap_texte)."""
    if inv.bsd:
        kv = Inventaire._kv(inv.cmd("sysctl hw.vendor"), "=")
        try:
            return f"{int(kv['hw.physmem']) / 1024 ** 3:.1f} Gio", "—"
        except (KeyError, ValueError):
            return "?", "—"
    ram = swap = "?"
    for ln in inv.cmd("free -h"):
        p = ln.split()
        if p and p[0] == "Mem:" and len(p) > 1:
            ram = p[1].replace("Gi", " Gio").replace("Mi", " Mio")
        if p and p[0] == "Swap:" and len(p) > 1:
            swap = p[1].replace("Gi", " Gio").replace("Mi", " Mio")
    return ram, swap


def cpu_resume(inv):
    """Retourne (modèle, coeurs, mhz_max)."""
    if inv.bsd:
        kv = Inventaire._kv(inv.cmd("sysctl hw.vendor"), "=")
        return kv.get("hw.model", "?"), kv.get("hw.ncpu", "?"), kv.get("hw.cpuspeed", "?")
    c = lscpu(inv)
    mhz = c.get("CPU max MHz", "")
    mhz = mhz.split(".")[0] if mhz else "?"
    return c.get("Model name", "?"), c.get("CPU(s)", "?"), mhz


def lspci_lignes(inv):
    out = []
    for ln in inv.cmd("lspci"):
        m = re.match(r"^(\S+) ([^:]+): (.*)$", ln)
        if m:
            out.append((m.group(1), m.group(2), m.group(3)))
    return out


def disques(inv):
    """Liste de (nom, taille, modèle, genre) pour les disques physiques."""
    res = []
    if inv.bsd:
        kv = Inventaire._kv(inv.cmd("sysctl hw.vendor"), "=")
        noms = [d.split(":")[0] for d in kv.get("hw.disknames", "").split(",") if d]
        tailles = {}
        for ln in inv.lignes:
            m = re.match(r"^(sd\d+): (\d+)MB,", ln)
            if m:
                tailles[m.group(1)] = f"{int(m.group(2)) / 1024:.1f}G"
        vus = set()
        for ln in inv.lignes:
            m = re.match(r"^(sd|cd)(\d+) at .*?<([^>]*)>", ln)
            if m and (m.group(1) + m.group(2)) not in vus:
                n = m.group(1) + m.group(2)
                vus.add(n)
                modele = ", ".join(x.strip() for x in m.group(3).split(",")[:2])
                if m.group(1) == "sd":
                    res.append((n, tailles.get(n, "?"), modele, "disque"))
                else:
                    res.append((n, "—", modele, "optique"))
        if not res:
            res = [(n, "?", "?", "disque") for n in noms]
        return res
    for ln in inv.cmd("lsblk"):
        m = re.match(r"^(\S+)\s+(\S+)\s+(disk|rom)\s*(.*)$", ln)
        if not m or m.group(1).startswith(("loop", "zram")):
            continue
        reste = m.group(4).strip()
        rota = None
        mm = re.match(r"^(.*?)\s+([01])$", reste)
        if mm:
            reste, rota = mm.group(1).strip(), mm.group(2)
        genre = "optique" if m.group(3) == "rom" else ("HDD" if rota == "1" else "SSD/NVMe" if rota == "0" else "?")
        res.append((m.group(1), m.group(2), reste or "?", genre))
    return res


def systemes_fichiers(inv):
    """Lignes (source, type, taille, utilisé, dispo, %, monté sur) hors pseudo-systèmes."""
    res = []
    if inv.bsd:
        for ln in inv.cmd("df -h")[1:]:
            p = ln.split(None, 5)
            if len(p) == 6:
                res.append((p[0], "ffs", p[1], p[2], p[3], p[4], p[5]))
        return res
    for ln in inv.cmd("df -hT")[1:]:
        p = ln.split(None, 6)
        if len(p) == 7 and p[5].endswith("%") and p[1] not in ("tmpfs", "devtmpfs", "squashfs", "overlay", "efivarfs", "ramfs"):
            res.append(tuple(p))
    return res


def interfaces(inv):
    """Liste de dicts décrivant chaque interface réseau."""
    res = []
    if inv.bsd:
        nom = None
        for ln in inv.cmd("ifconfig"):
            m = re.match(r"^(\w+): flags=\S+<([^>]*)>", ln)
            if m:
                nom = m.group(1)
                d = {"nom": nom, "etat": "UP" if "UP" in m.group(2).split(",") else "DOWN",
                     "ipv4": [], "mac": "", "vitesse": "", "pilote": "", "type": ""}
                res.append(d)
                continue
            if not res:
                continue
            d = res[-1]
            m = re.match(r"^\s+lladdr (\S+)", ln)
            if m:
                d["mac"] = m.group(1)
            m = re.match(r"^\s+inet (\d+\.\d+\.\d+\.\d+) netmask (0x[0-9a-f]+)", ln)
            if m:
                bits = bin(int(m.group(2), 16)).count("1")
                d["ipv4"].append(f"{m.group(1)}/{bits}")
            m = re.match(r"^\s+media: (.*)$", ln)
            if m:
                d["vitesse"] = m.group(1)
            m = re.match(r"^\s+wgport (\d+)", ln)
            if m:
                d["pilote"] = f"WireGuard, port {m.group(1)}"
        for d in res:
            d["type"] = type_interface(d["nom"])
        return [d for d in res if d["nom"] not in ("enc0",)]
    macs = {}
    for ln in inv.sub("Interfaces (MAC"):
        m = re.match(r"^(\S+) : mac=(\S*) etat=(\S*) vitesse=(\S*) pilote=(.*)$", ln)
        if m:
            macs[m.group(1)] = m.groups()[1:]
    for ln in inv.cmd("ip -br addr"):
        p = ln.split()
        if len(p) < 2 or p[0] == "lo":
            continue
        ipv4 = [a for a in p[2:] if re.match(r"^\d+\.\d+\.\d+\.\d+/\d+$", a)]
        mac, etat, vit, pilote = macs.get(p[0], ("", "", "", ""))
        vit = vit if vit and vit != "-1" else ""
        res.append({"nom": p[0], "etat": p[1], "ipv4": ipv4, "mac": mac,
                    "vitesse": (vit + " Mbit/s") if vit else "", "pilote": pilote,
                    "type": type_interface(p[0])})
    return res


def type_interface(nom):
    if nom.startswith("wl"):
        return "Wi-Fi"
    if nom.startswith(("en", "eth", "re", "em", "igc", "ix", "bge", "bnx")):
        return "Ethernet"
    if nom.startswith("wg"):
        return "VPN WireGuard"
    if nom.startswith(("docker", "br-", "veth", "virbr", "tun", "tap", "pflog")):
        return "Virtuelle"
    return "?"


def passerelle(inv):
    if inv.bsd:
        for ln in inv.cmd("netstat -rn"):
            p = ln.split()
            if len(p) >= 2 and p[0] == "default" and re.match(r"^\d+\.\d+\.\d+\.\d+$", p[1]):
                return p[1]
        return "?"
    for ln in inv.cmd("ip route"):
        m = re.match(r"^default via (\S+) dev (\S+)", ln)
        if m:
            return m.group(1)
    return "?"


def dns(inv):
    lignes = inv.cmd("cat /etc/resolv.conf")
    return [ln.split()[1] for ln in lignes if ln.startswith("nameserver") and len(ln.split()) > 1]


def mode_ip(inv):
    """Dict interface -> 'static' ou 'dhcp' (si /etc/network/interfaces est lisible)."""
    res = {}
    textes = inv.sub("/etc/network/interfaces")
    for ln in textes:
        m = re.match(r"^\s*iface (\S+) inet (static|dhcp)", ln)
        if m:
            res[m.group(1)] = m.group(2)
    if inv.bsd:
        cur = None
        for ln in inv.sub("/etc/hostname."):
            m = re.match(r"^# /etc/hostname\.(\S+)$", ln)
            if m:
                cur = m.group(1)
            m = re.match(r"^inet (\d+\.\d+\.\d+\.\d+) ", ln)
            if m and cur:
                res[cur] = "static"
    return res


def ports_ecoute(inv):
    lignes = inv.cmd("ss -tulpn") or inv.cmd("ss -tuln")
    vus = {}
    for ln in lignes:
        p = ln.split()
        if len(p) < 5 or p[0] not in ("tcp", "udp"):
            continue
        addr, _, port = p[4].rpartition(":")
        if not port.isdigit():
            continue
        proc = ",".join(re.findall(r'\("([^"]+)"', " ".join(p[6:])))
        e = vus.setdefault((p[0], int(port)), {"addr": set(), "proc": ""})
        e["addr"].add(addr.strip("[]") or "*")
        if proc:
            e["proc"] = proc
    return [(proto, port, ", ".join(sorted(v["addr"])), v["proc"] or "—")
            for (proto, port), v in sorted(vus.items(), key=lambda x: (x[0][0], x[0][1]))]


def reglages_ssh(inv):
    """Réglages du serveur SSH : sshd -T (minuscules) sinon fichier de config."""
    cles = ["port", "permitrootlogin", "passwordauthentication", "pubkeyauthentication",
            "kbdinteractiveauthentication", "allowusers", "allowgroups", "maxauthtries", "x11forwarding"]
    res = {}
    for ln in inv.lignes:                      # sortie de « sshd -T »
        p = ln.split(None, 1)
        if len(p) == 2 and p[0] in cles:
            res.setdefault(p[0], p[1].strip())
    if res:
        res["_source"] = "sshd -T (réglage effectif)"
        return res
    src = (inv.section("SSH - SERVEUR") + inv.sub("sshd_config") + inv.section("SSH - SERVEUR (BSD)"))
    for ln in src:                              # fichier de configuration
        p = ln.split(None, 1)
        if len(p) == 2 and p[0].lower() in cles:
            res.setdefault(p[0].lower(), p[1].strip())
    res["_source"] = "sshd_config (lignes actives ; défauts d'OpenSSH pour le reste)"
    return res


def cles_ssh(inv):
    """Empreintes des clés : (locales, autorisées, alias_ssh_config)."""
    lignes = inv.sub("Clés et config SSH")
    re_fp = re.compile(r"^(\d+) (SHA256:\S+) (.*) \((\w+)\)$")
    locales, autorisees, config = [], [], []
    mode = "loc"
    for ln in lignes:
        if ln.startswith("authorized_keys"):
            mode = "aut"
            continue
        if ln.startswith("~/.ssh/config"):
            mode = "cfg"
            continue
        m = re_fp.match(ln)
        if m and mode == "loc":
            locales.append(m.groups())
        elif m and mode == "aut":
            autorisees.append(m.groups())
        elif mode == "cfg":
            config.append(ln)
    return locales, autorisees, config


def alias_ssh(config):
    """Tableau des alias de ~/.ssh/config : liste de dicts."""
    res, cur = [], None
    for ln in config:
        p = ln.strip().split(None, 1)
        if len(p) < 2:
            continue
        if p[0].lower() == "host":
            cur = {"alias": p[1], "hostname": "", "user": "", "cle": ""}
            res.append(cur)
        elif cur is not None:
            k = p[0].lower()
            if k == "hostname":
                cur["hostname"] = p[1]
            elif k == "user":
                cur["user"] = p[1]
            elif k == "identityfile":
                cur["cle"] = os.path.basename(p[1])
    return res


def comptes(inv):
    res = []
    for ln in inv.section("COMPTES") + inv.cmd("id") + inv.lignes:
        m = re.match(r"^(\S+) uid=(\d+) shell=(\S+) home=(\S+)$", ln)
        if m and (m.group(1), m.group(2)) not in [(r[0], r[1]) for r in res]:
            res.append(m.groups())
    return res


def groupe_sudo(inv):
    for ln in inv.cmd("getent group"):
        m = re.match(r"^(sudo|wheel):\S*:\d+:(.*)$", ln)
        if m:
            return m.group(1), m.group(2)
    return "", ""


def jobs_cron(lignes, avec_user):
    """Extrait les tâches cron : (planification, utilisateur, commande)."""
    res = []
    for ln in lignes:
        s = ln.strip()
        if not s or s.startswith("#") or re.match(r"^[A-Z_]+=", s):
            continue
        if avec_user:
            m = re.match(r"^(@\w+|\S+\s+\S+\s+\S+\s+\S+\s+\S+)\s+(\S+)\s+(.*)$", s)
            if m:
                res.append(m.groups())
        else:
            m = re.match(r"^(@\w+|\S+\s+\S+\s+\S+\s+\S+\s+\S+)\s+(.*)$", s)
            if m:
                res.append((m.group(1), "", m.group(2)))
    return res


def cron_utilisateur(inv):
    lignes = inv.cmd("crontab -l")
    if not lignes or "no crontab" in lignes[0].lower():
        return []
    return lignes


def services_actifs(inv):
    res = []
    for ln in inv.cmd("systemctl list-units --type=service --state=running"):
        m = re.match(r"^\s*(\S+\.service)\s+loaded\s+active\s+running\s+(.*)$", ln)
        if m:
            res.append((m.group(1), m.group(2)))
    return res


def unites_activees(inv):
    res = []
    for ln in inv.cmd("systemctl list-unit-files --state=enabled"):
        m = re.match(r"^(\S+\.(service|timer|socket|path|target))\s+enabled", ln)
        if m:
            res.append(m.group(1))
    return res


def timers(inv):
    res = []
    for ln in inv.cmd("systemctl list-timers"):
        p = ln.split()
        if len(p) >= 2 and p[-2].endswith(".timer"):
            suivant = " ".join(p[:4]) if p[0] != "-" else "—"
            res.append((p[-2], p[-1], suivant))
    return res


def mises_a_jour(inv):
    for ln in inv.lignes:
        m = re.match(r"^Paquets à mettre à jour : (\d+)", ln)
        if m:
            return int(m.group(1))
    return None


def nb_paquets(inv):
    for ln in inv.lignes:
        m = re.match(r"^Nombre de paquets installés : (\d+)", ln)
        if m:
            return int(m.group(1))
    if inv.bsd:
        return len(inv.cmd("pkg_info -q"))
    return None


def scripts_home(inv):
    """Fichiers trouvés dans le home : (chemin, taille, date)."""
    res = []
    for ln in inv.sub("Scripts et fichiers"):
        m = re.match(r"^\S+\s+\d+\s+\S+\s+\S+\s+(\d+)\s+(\w{3}\s+\d+\s+[\d:]+)\s+(.+)$", ln)
        if m and "/.ssh/" not in m.group(3):
            res.append((m.group(3), m.group(1), m.group(2)))
    return res


# =============================================================================
#  4. POINTS D'ATTENTION AUTOMATIQUES
# =============================================================================
def points_attention(inv):
    pts = []
    ssh = reglages_ssh(inv)
    if inv.nb_ignores and not inv.complement_root:
        pts.append(("INFO", f"Inventaire partiel : {inv.nb_ignores} commandes demandent root "
                            "(lancer le complément root du script d'inventaire)."))
    pw = ssh.get("passwordauthentication")
    if pw is None:
        pw_txt = "non précisé (défaut OpenSSH : activé)"
    else:
        pw_txt = pw
    if pw is None or pw.lower() == "yes":
        pts.append(("ATTENTION", f"SSH : authentification par mot de passe active ({pw_txt}). "
                                 "Les clés suffiraient (à valider avant tout changement)."))
    if ssh.get("permitrootlogin", "").lower() == "yes":
        pts.append(("ATTENTION", "SSH : connexion directe de root autorisée avec mot de passe."))
    if inv.ident.get("Privileges", "").startswith("root disponible (sudo -n)"):
        pts.append(("INFO", "Le compte d'inventaire a sudo SANS mot de passe (à comparer aux autres PC)."))
    nom_os = os_nom(inv)
    m = re.search(r"Ubuntu (\d+)\.(\d+)", nom_os)
    if m and (int(m.group(1)), int(m.group(2))) <= (20, 4):
        pts.append(("ATTENTION", f"{nom_os} : fin du support standard (plus de correctifs de sécurité "
                                 "sans abonnement ESM)."))
    m = re.search(r"Debian GNU/Linux (\d+)", nom_os)
    if m and int(m.group(1)) <= 11:
        pts.append(("ATTENTION", f"{nom_os} : version ancienne (vérifier le support de sécurité)."))
    if not inv.bsd and architecture(inv).startswith("i") and "64-bit" in lscpu(inv).get("CPU op-mode(s)", ""):
        pts.append(("INFO", "Noyau 32 bits sur un processeur compatible 64 bits (mémoire adressable "
                            "et performances limitées)."))
    n = mises_a_jour(inv)
    if n:
        pts.append(("INFO", f"{n} paquets à mettre à jour."))
    if inv.tout_contient(r"REDEMARRAGE REQUIS"):
        pts.append(("INFO", "Redémarrage requis (mises à jour installées)."))
    for itf in interfaces(inv):
        if itf["type"] == "Wi-Fi" and itf["ipv4"]:
            pts.append(("INFO", f"Connexion Wi-Fi ({itf['nom']}, {', '.join(itf['ipv4'])}) : pas de filaire."))
        if itf["type"] == "Ethernet" and itf["vitesse"] and itf["vitesse"].startswith("100 "):
            pts.append(("INFO", f"Lien Ethernet limité à 100 Mbit/s ({itf['nom']}, pilote {itf['pilote'] or '?'})."))
    pub = [x for x in dns(inv) if re.match(r"^\d+\.\d+\.\d+\.\d+$", x)
           and not re.match(r"^(192\.168\.|10\.|172\.(1[6-9]|2\d|3[01])\.|127\.)", x)]
    if pub:
        pts.append(("INFO", f"DNS du FAI utilisés directement ({', '.join(pub)}) au lieu de la box."))
    for fs in systemes_fichiers(inv):
        pct = re.sub(r"\D", "", fs[5])
        if pct and int(pct) >= 85:
            pts.append(("ATTENTION", f"Disque presque plein : {fs[6]} à {fs[5]}."))
    cron_txt = "\n".join(cron_utilisateur(inv))
    if re.search(r"\b\d+\.\d+\.\d+\.\d+\b", cron_txt):
        pts.append(("ATTENTION", "Une tâche cron contient une adresse IP écrite en dur "
                                 "(fragile si l'IP change : préférer un alias SSH)."))
    if not inv.bsd and not cron_utilisateur(inv) and not timers(inv):
        pts.append(("INFO", "Aucune tâche planifiée détectée pour ce compte."))
    return pts


# =============================================================================
#  5. CONSTRUCTION D'UN RAPPORT PAR PC
# =============================================================================
def section_identification(inv):
    out = titre(2, "1. Identification")
    lignes = [
        ("Nom d'hôte", inv.hostname),
        ("Inventaire du", inv.date),
        ("Compte utilisé", inv.ident.get("Utilisateur", "?")),
        ("Droits root pendant l'inventaire",
         "oui" if inv.root_ok else ("oui, via complément root" if inv.complement_root else "non")),
        ("Système", os_nom(inv)),
        ("Noyau", noyau(inv)),
        ("Architecture", architecture(inv)),
        ("Allumé depuis", uptime(inv)),
    ]
    return out + tableau(["Élément", "Valeur"], lignes)


def section_attention(inv):
    pts = points_attention(inv)
    out = titre(2, "2. Points d'attention (détectés automatiquement)")
    if not pts:
        return out + info("Aucun point d'attention détecté.")
    out += tableau(["Niveau", "Constat"], pts)
    out += info("*Constats uniquement : aucune modification n'est faite sans validation.*")
    return out


def section_materiel(inv):
    out = titre(2, "3. Matériel")
    vendor, produit = modele_machine(inv)
    modele_cpu, coeurs, mhz = cpu_resume(inv)
    ram, swap = ram_total(inv)
    if inv.bsd:
        out += tableau(["Élément", "Valeur"], [
            ("Constructeur", vendor), ("Modèle", produit), ("Processeur", modele_cpu),
            ("Cœurs", coeurs), ("Fréquence", f"{mhz} MHz"), ("Mémoire vive", ram)])
        temp = [ln for ln in inv.cmd("sysctl hw.sensors") if "cpu0.temp0" in ln]
        if temp:
            out += info("Température CPU au moment de l'inventaire : " + temp[0].split("=")[1])
    else:
        kv = Inventaire._kv(inv.section("MATERIEL - MACHINE"))
        c = lscpu(inv)
        out += titre(3, "Machine")
        out += tableau(["Élément", "Valeur"], [
            ("Constructeur", vendor), ("Modèle", produit),
            ("Carte mère", f"{kv.get('board_vendor', '?')} {kv.get('board_name', '?')} (rév. {kv.get('board_version', '?')})"),
            ("BIOS", f"{kv.get('bios_vendor', '?')} {kv.get('bios_version', '?')} ({kv.get('bios_date', '?')})"),
            ("Type de châssis", CHASSIS.get(kv.get("chassis_type", ""), kv.get("chassis_type", "?")))])
        out += titre(3, "Processeur")
        out += tableau(["Élément", "Valeur"], [
            ("Modèle", modele_cpu), ("Cœurs logiques", coeurs),
            ("Threads par cœur", c.get("Thread(s) per core", "?")),
            ("Fréquence max", f"{mhz} MHz"), ("Cache L2", c.get("L2 cache", "—")),
            ("Cache L3", c.get("L3 cache", "—")),
            ("Virtualisation", c.get("Virtualization", "—")),
            ("Modes", c.get("CPU op-mode(s)", "?"))])
        out += titre(3, "Mémoire")
        out += tableau(["Élément", "Valeur"], [("RAM visible par le système", ram), ("Swap", swap)])
        barrettes = inv.sub("Barrettes mémoire")
        if barrettes and not ignore(barrettes):
            out += code(raccourcir(barrettes, 60))
        else:
            out += info("Détail des barrettes (slots, types) : non disponible sans root.")
    out += titre(3, "Disques")
    out += tableau(["Disque", "Taille", "Modèle", "Type"], disques(inv))
    out += titre(3, "Systèmes de fichiers montés")
    out += tableau(["Source", "Type", "Taille", "Utilisé", "Libre", "Util.", "Monté sur"], systemes_fichiers(inv))
    if not inv.bsd:
        part = [ln for ln in inv.cmd("lsblk") if not ln.startswith(("loop", "zram"))]
        if part:
            out += titre(3, "Partitions")
            out += code(part)
        smart = inv.sub("SMART")
        if smart and not ignore(smart):
            out += titre(3, "État de santé des disques (SMART)")
            out += code(raccourcir(smart, 60))
        else:
            out += info("État de santé SMART : non disponible (root requis ou smartmontools absent).")
    if inv.bsd:
        mat = [ln for ln in inv.sub("Détection matérielle") if re.match(r"^(\w+\d+) at ", ln)]
        out += titre(3, "Périphériques détectés au démarrage (dmesg)")
        out += code(raccourcir(mat, 70))
    else:
        pci = lspci_lignes(inv)
        gpu = [(b, d) for b, t, d in pci if t.startswith(("VGA", "3D", "Display"))]
        nic = [(t.split()[0], d) for b, t, d in pci if t.startswith(("Ethernet", "Network"))]
        out += titre(3, "Graphique, réseau et autres composants")
        out += tableau(["Catégorie", "Composant"],
                       [("Graphique", d) for _, d in gpu] +
                       [(t, d) for t, d in nic] +
                       [("Audio", d) for b, t, d in pci if t.startswith("Audio")])
        nvidia = inv.cmd("nvidia-smi")
        if len(nvidia) >= 2:
            out += info("GPU NVIDIA (nom, mémoire, pilote) : " + nvidia[1])
        sorties = []
        for ln in inv.section("MATERIEL - VIDEO / PCI / USB") + inv.cmd("lsusb")[:0]:
            m = re.match(r"^/sys/class/drm/card\d+-(\S+)/status : (\S+)$", ln)
            if m:
                sorties.append(m.groups())
        for g, t, lignes in inv.blocs:                       # lignes libres de la section vidéo
            if g == "cmd" and t.startswith("lsusb"):
                for ln in lignes:
                    m = re.match(r"^/sys/class/drm/card\d+-(\S+)/status : (\S+)$", ln)
                    if m:
                        sorties.append(m.groups())
        out += tableau(["Sortie vidéo", "État"], sorties)
        usb = [ln for ln in inv.cmd("lsusb") if "root hub" not in ln and ln.startswith("Bus")]
        if usb:
            out += titre(3, "Périphériques USB (hors hubs)")
            out += code([re.sub(r"^Bus \d+ Device \d+: ID ", "", ln) for ln in usb])
        alim = [ln.split(" : ")[1] for ln in inv.lignes if ln.startswith("alimentation : ")]
        if alim:
            out += info("Alimentation : " + ", ".join(alim) + (" (portable avec batterie)" if "BAT0" in alim else ""))
        if pci:
            out += titre(3, "Liste PCI complète")
            out += code([f"{b} {t}: {d}" for b, t, d in pci])
    return out


def section_reseau(inv):
    out = titre(2, "4. Réseau")
    modes = mode_ip(inv)
    lignes = []
    for i in interfaces(inv):
        mode = modes.get(i["nom"], "")
        mode_txt = {"static": "IP fixe", "dhcp": "DHCP"}.get(mode, "non lisible")
        lignes.append((i["nom"], i["type"], i["etat"], ", ".join(i["ipv4"]) or "—", mode_txt,
                       i["mac"] or "—", i["vitesse"] or "—", i["pilote"] or "—"))
    out += tableau(["Interface", "Type", "État", "IPv4", "Mode IP", "MAC", "Vitesse / média", "Pilote"], lignes)
    out += tableau(["Élément", "Valeur"], [
        ("Passerelle par défaut", passerelle(inv)),
        ("Serveurs DNS", ", ".join(dns(inv)) or "—")])
    routes = inv.cmd("netstat -rn")[:12] if inv.bsd else inv.cmd("ip route")
    if routes:
        out += titre(3, "Table de routage IPv4")
        out += code(routes)
    cfg = inv.sub("/etc/network/interfaces") if not inv.bsd else inv.sub("/etc/hostname.")
    if cfg and not ignore([ln for ln in cfg if not ln.startswith("#")]):
        out += titre(3, "Configuration réseau (secrets masqués)" if inv.bsd else
                     "Fichiers /etc/network/interfaces* (secrets masqués)")
        out += code(cfg)
    elif not inv.bsd:
        out += info("Fichiers /etc/network/interfaces* : non lisibles sans root (ou réseau géré par NetworkManager).")
    ports = ports_ecoute(inv)
    out += titre(3, "Ports en écoute")
    out += tableau(["Protocole", "Port", "Adresses", "Processus"], ports)
    wg = inv.sub("WireGuard") if not inv.bsd else []
    if wg and not ignore(wg):
        out += titre(3, "WireGuard")
        lg = [re.sub(r"(peer: )(\S{8})\S*", r"\1\2…", ln) for ln in wg]
        out += code(raccourcir(lg, 40))
    if inv.bsd:
        peers = []
        for ln in inv.sub("/etc/hostname."):
            for m in re.finditer(r"wgpeer (\S{8})\S* .*?wgaip (\S+)", ln):
                peers.append((m.group(1) + "…", m.group(2)))
            for m in re.finditer(r"\bpeer (\S{8})\S* allowed-ips (\S+)", ln):
                peers.append((m.group(1) + "…", m.group(2)))
        if peers:
            out += titre(3, "WireGuard : pairs déclarés (clés tronquées)")
            out += tableau(["Pair (début de clé publique)", "IP autorisées"], peers)
    pf = inv.sub("Pare-feu")
    out += titre(3, "Pare-feu")
    if pf and not ignore(pf) and not all("ignoré" in ln for ln in pf if ln.strip()):
        out += code(raccourcir([ln for ln in pf if "ignoré" not in ln], 50))
    elif inv.root_ok or inv.complement_root:
        out += info("Aucune règle de pare-feu active (nftables/iptables vides) : tout le trafic entrant est autorisé.")
    else:
        out += info("Règles de pare-feu : non vérifiables sans root (ou aucun pare-feu installé).")
    return out


def section_securite(inv):
    out = titre(2, "5. Sécurité")
    ssh = reglages_ssh(inv)
    def v(cle, defaut):
        return ssh.get(cle, f"non précisé (défaut : {defaut})")
    out += titre(3, "Serveur SSH")
    out += tableau(["Réglage", "Valeur"], [
        ("Port", v("port", "22")),
        ("Connexion root", v("permitrootlogin", "prohibit-password")),
        ("Mot de passe SSH", v("passwordauthentication", "yes")),
        ("Clé publique", v("pubkeyauthentication", "yes")),
        ("Comptes autorisés", v("allowusers", "tous")),
        ("X11Forwarding", v("x11forwarding", "no")),
        ("Source", ssh.get("_source", "?"))])
    locales, autorisees, config = cles_ssh(inv)
    out += titre(3, "Clés SSH (empreintes seulement)")
    out += tableau(["Origine", "Algorithme", "Empreinte", "Commentaire"],
                   [("Clé locale", t, fp, c) for b, fp, c, t in locales] +
                   [("Clé autorisée à se connecter", t, fp, c) for b, fp, c, t in autorisees])
    alias = alias_ssh(config)
    if alias:
        out += titre(3, "Alias SSH (~/.ssh/config)")
        out += tableau(["Alias", "HostName", "Utilisateur", "Clé"],
                       [(a["alias"], a["hostname"] or "—", a["user"] or "—", a["cle"] or "—") for a in alias])
    return out


def section_logiciels(inv):
    out = titre(2, "6. Logiciels")
    outils = []
    for ln in inv.sub("Versions des outils clés"):
        p = ln.split(None, 1)
        if p:
            outils.append((p[0], p[1] if len(p) > 1 else ""))
    out += titre(3, "Outils clés détectés")
    out += tableau(["Outil", "Version"], outils)
    mods = []
    for ln in inv.sub("Modules Python clés"):
        m = re.match(r"^(\S+) : absent", ln)
        if m:
            mods.append((m.group(1), "absent"))
            continue
        p = ln.split(None, 1)
        if len(p) == 2:
            mods.append((p[0], p[1]))
    if mods:
        out += titre(3, "Modules Python scientifiques (python3 système)")
        out += tableau(["Module", "Version"], mods)
    envs = inv.sub("Environnements Python")
    out += info("Environnements virtuels Python trouvés : " + (", ".join(f"`{e}`" for e in envs) if envs else "aucun (profondeur 4)"))
    n = nb_paquets(inv)
    out += titre(3, "Paquets")
    out += info(f"Nombre de paquets installés : **{n if n is not None else '?'}** "
                "(liste exhaustive : fichier annexe `PCn_annexe_paquets.md`).")
    manuels = inv.sub("Installés manuellement")
    if manuels:
        utiles = [m for m in manuels if not m.startswith("lib")]
        out += info(f"Paquets installés manuellement hors bibliothèques ({len(utiles)} sur {len(manuels)}) :")
        out += [", ".join(f"`{u}`" for u in utiles), ""]
    if inv.bsd:
        sp = inv.sub("Correctifs installés")
        out += info(f"Correctifs syspatch installés : {len([x for x in sp if x.strip()])}")
    snaps = inv.cmd("snap list")
    if len(snaps) > 1:
        out += titre(3, "Snap")
        out += tableau(["Nom", "Version"], [(p[0], p[1]) for p in (ln.split() for ln in snaps[1:]) if len(p) >= 2][:60])
    return out


def section_services(inv):
    out = titre(2, "7. Services et horloge")
    if inv.bsd:
        actifs = [ln for ln in inv.cmd("rcctl ls on")]
        out += titre(3, "Services activés au démarrage (rcctl)")
        out += [", ".join(f"`{a}`" for a in actifs) or "—", ""]
        st = inv.sub("Services démarrés")
        if st and not ignore(st):
            out += titre(3, "Services démarrés / en échec")
            out += code(st)
        else:
            out += info("Services démarrés / en échec : non vérifiables sans root.")
        return out
    out += titre(3, "Services en cours d'exécution")
    out += tableau(["Service", "Description"], services_actifs(inv))
    activees = unites_activees(inv)
    if activees:
        out += titre(3, "Unités activées au démarrage")
        out += [", ".join(f"`{u}`" for u in activees), ""]
    echec = inv.cmd("systemctl --failed")
    if echec:
        out += info("Unités en échec : " + ("aucune" if any("0 loaded units" in ln for ln in echec) else "voir inventaire"))
    kv = Inventaire._kv(inv.cmd("timedatectl"))
    if kv:
        out += tableau(["Horloge", "Valeur"], [
            ("Fuseau horaire", kv.get("Time zone", "?")),
            ("Horloge synchronisée", kv.get("System clock synchronized", "?")),
            ("Service NTP", kv.get("NTP service", "?"))])
    return out


def section_taches(inv):
    out = titre(2, "8. Tâches planifiées")
    cu = cron_utilisateur(inv)
    out += titre(3, f"Crontab de {inv.ident.get('Utilisateur', '?').split()[0]}")
    if cu:
        out += code(cu)
    else:
        out += info("Aucune crontab pour ce compte.")
    sysj = jobs_cron(inv.sub("cron système"), avec_user=True)
    if sysj:
        out += titre(3, "Cron système (/etc/crontab et /etc/cron.d)")
        out += tableau(["Planification", "Utilisateur", "Commande"], sysj)
    autres = inv.sub("crontabs des comptes") or inv.cmd("sh -c for f in /var/spool/cron") or inv.cmd("sh -c for f in /var/cron")
    out += titre(3, "Crontabs des autres comptes (root, etc.)")
    if autres and not ignore(autres):
        out += code(autres)
    else:
        out += info("Non vérifiées (root requis).")
    dossiers, cur = {}, None
    for ln in inv.cmd("ls /etc/cron.hourly"):
        m = re.match(r"^(/etc/cron\.\w+):$", ln)
        if m:
            cur = m.group(1)
            dossiers[cur] = []
        elif cur and ln.strip():
            dossiers[cur].append(ln.strip())
    out += tableau(["Dossier", "Scripts"], [(d, ", ".join(s) or "(vide)") for d, s in sorted(dossiers.items())])
    tm = timers(inv)
    if tm:
        out += titre(3, "Timers systemd")
        out += tableau(["Timer", "Déclenche", "Prochain passage"], tm)
    return out


def section_scripts(inv):
    out = titre(2, "9. Scripts")
    sc = scripts_home(inv)
    loc = [ln for ln in inv.cmd("ls -l /usr/local/bin") if not ln.startswith("total")]
    out += titre(3, "/usr/local/bin et /usr/local/sbin")
    noms = [re.sub(r"^\S+\s+\d+\s+\S+\s+\S+\s+\d+\s+\w+\s+\d+\s+\S+\s+", "", ln) for ln in loc if ln.startswith("-")]
    out += info(", ".join(f"`{n}`" for n in noms) if noms else "Vide.")
    out += titre(3, "Scripts et fichiers zeta_* / wg_* / *.sh dans le home")
    if sc:
        out += tableau(["Chemin", "Taille (octets)", "Date"], sc[:80])
        if len(sc) > 80:
            out += info(f"... et {len(sc) - 80} autres fichiers (voir l'inventaire).")
    else:
        out += info("Aucun script trouvé (profondeur 4 sous le home).")
    return out


def section_comptes(inv):
    out = titre(2, "10. Comptes et connexions")
    out += tableau(["Compte", "UID", "Shell", "Dossier personnel"], comptes(inv))
    g, membres = groupe_sudo(inv)
    if g:
        out += info(f"Membres du groupe `{g}` : {membres or '—'}")
    last = [ln for ln in inv.cmd("last") if ln.strip() and not ln.startswith("wtmp")]
    if last:
        out += titre(3, "Dernières connexions")
        out += code(last)
    fstab = []
    for ln in inv.section("MONTAGES"):
        s = ln.strip()
        if s and not s.startswith("#"):
            p = s.split()
            if len(p) >= 4:
                fstab.append((p[0], p[1], p[2], p[3]))
    if fstab:
        out += titre(2, "11. Montages permanents (fstab)")
        out += tableau(["Source", "Point de montage", "Type", "Options"], fstab)
    return out


def rapport_pc(inv, n):
    nom, alias = PCS[n]
    out = [f"# {nom} — {alias} : matériel, réseau, logiciels, services", "", BANNIERE, "",
           f"Source : `{inv.chemin.name}` (inventaire du {inv.date})", ""]
    for f in (section_identification, section_attention, section_materiel, section_reseau,
              section_securite, section_logiciels, section_services, section_taches,
              section_scripts, section_comptes):
        out += f(inv)
    return pied_de_page(out)


def pied_de_page(lignes):
    """Ajoute en bas : date de mise à jour et nombre de lignes du fichier (consigne du projet)."""
    pied = ["", "---", ""]
    total = len(lignes) + len(pied) + 1
    pied.append(f"*Mis à jour le {datetime.now():%Y-%m-%d %H:%M} — {total} lignes*")
    return lignes + pied


def annexe_paquets(inv, n):
    nom, alias = PCS[n]
    out = [f"# {nom} — {alias} : annexe, liste exhaustive des paquets", "", BANNIERE, "",
           f"Source : `{inv.chemin.name}`", ""]
    if inv.bsd:
        out += titre(2, "Paquets installés (pkg_info)")
        out += tableau(["Paquet"], [(p,) for p in inv.cmd("pkg_info -q")])
    else:
        paquets = []
        for ln in inv.sub("Liste complète"):
            if "\t" in ln:
                a, b = ln.split("\t", 1)
                paquets.append((a, b))
        out += titre(2, f"Paquets système ({len(paquets)})")
        out += tableau(["Paquet", "Version"], paquets)
        pip = inv.sub("pip3 list")
        pr = [tuple(ln.split()[:2]) for ln in pip[2:] if len(ln.split()) >= 2]
        if pr:
            out += titre(2, f"Paquets Python pip3 ({len(pr)})")
            out += tableau(["Paquet", "Version"], pr)
    return pied_de_page(out)


# =============================================================================
#  6. COMPARATIF DU CLUSTER
# =============================================================================
def comparatif(invs):
    """invs : dict n -> Inventaire."""
    nums = sorted(invs)
    ent = ["Critère"] + [f"{PCS[n][0]} {invs[n].hostname}" for n in nums]
    lignes = []

    def ligne(libelle, fonction):
        lignes.append([libelle] + [fonction(invs[n]) for n in nums])

    ligne("Modèle", lambda i: " ".join(modele_machine(i)))
    ligne("Processeur", lambda i: cpu_resume(i)[0])
    ligne("Cœurs / fréquence max", lambda i: f"{cpu_resume(i)[1]} / {cpu_resume(i)[2]} MHz")
    ligne("RAM", lambda i: ram_total(i)[0])
    ligne("Disque(s)", lambda i: "; ".join(f"{d[1]} {d[2]} ({d[3]})" for d in disques(i) if d[3] != "optique") or "?")
    ligne("Système", os_nom)
    ligne("Noyau / architecture", lambda i: f"{noyau(i)} / {architecture(i)}")
    ligne("Réseau (type, IP)", lambda i: "; ".join(
        f"{x['nom']} {x['type']} {', '.join(x['ipv4'])}" for x in interfaces(i)
        if x["ipv4"] and x["type"] in ("Ethernet", "Wi-Fi")) or "?")
    ligne("Vitesse du lien", lambda i: "; ".join(x["vitesse"] for x in interfaces(i) if x["vitesse"] and x["type"] == "Ethernet") or "—")
    ligne("Passerelle", passerelle)
    ligne("DNS", lambda i: ", ".join(dns(i)) or "—")
    ligne("SSH : mot de passe", lambda i: reglages_ssh(i).get("passwordauthentication", "non précisé (défaut oui)"))
    ligne("SSH : root", lambda i: reglages_ssh(i).get("permitrootlogin", "non précisé (défaut prohibit-password)"))
    ligne("Droits root à l'inventaire", lambda i: "oui" if i.root_ok else ("oui (complément)" if i.complement_root else "non"))
    ligne("Paquets installés", lambda i: str(nb_paquets(i) or "?"))
    ligne("Services en cours", lambda i: str(len(services_actifs(i))) if not i.bsd else str(len(i.cmd("rcctl ls on"))))
    ligne("Tâches cron utilisateur", lambda i: str(len(jobs_cron(cron_utilisateur(i), False))))
    ligne("Points d'attention", lambda i: str(len(points_attention(i))))

    out = ["# Cluster Zeta — comparatif des 5 PC", "", BANNIERE, ""]
    dates = ", ".join(f"{PCS[n][0]} {invs[n].date}" for n in nums)
    out += [f"Sources : inventaires du {dates}", ""]
    out += titre(2, "1. Comparatif matériel et système")
    out += tableau(ent, lignes)

    out += titre(2, "2. Adressage observé (état actuel, avant toute modification)")
    adr = []
    for n in nums:
        i = invs[n]
        modes = mode_ip(i)
        for x in interfaces(i):
            if x["ipv4"] and x["type"] in ("Ethernet", "Wi-Fi", "VPN WireGuard"):
                adr.append((PCS[n][0], i.hostname, x["nom"], x["type"], ", ".join(x["ipv4"]),
                            {"static": "IP fixe", "dhcp": "DHCP"}.get(modes.get(x["nom"], ""), "non lisible"),
                            passerelle(i) if x["type"] != "VPN WireGuard" else "—"))
    out += tableau(["PC", "Nom d'hôte", "Interface", "Type", "IPv4", "Mode IP", "Passerelle"], adr)
    out += info("*« non lisible » : le mode (fixe ou DHCP) n'a pas pu être lu sans root, ou la machine "
                "utilise NetworkManager. Le plan d'adressage cible sera proposé séparément, avec validation.*")

    out += titre(2, "3. Points d'attention par PC")
    pts = []
    for n in nums:
        for niveau, texte in points_attention(invs[n]):
            pts.append((PCS[n][0], niveau, texte))
    out += tableau(["PC", "Niveau", "Constat"], pts)
    return pied_de_page(out)


# =============================================================================
#  7. FICHIERS ET MENU
# =============================================================================
def dernier_inventaire(n):
    """Chemin de l'inventaire le plus récent du PC n (ou None)."""
    nom = PCS[n][0]
    fichiers = glob.glob(str(INV_DIR / f"*inventaire_{nom}_*.txt"))
    return max(fichiers, key=lambda f: Path(f).name.split("inventaire_")[1], default=None)


def ecrire(nom_fichier, lignes):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(OUT_DIR, 0o700)
    chemin = OUT_DIR / nom_fichier
    chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    os.chmod(chemin, 0o600)
    print(f"    écrit : {chemin}  ({len(lignes)} lignes)")
    return chemin


def faire_rapport(n):
    chemin = dernier_inventaire(n)
    nom, alias = PCS[n]
    if not chemin:
        print(f">>> {nom} : aucun inventaire trouvé dans {INV_DIR}")
        print("    Lance d'abord : zeta_inventaire.sh")
        return None
    print(f">>> Rapport {nom} ({alias}) à partir de {Path(chemin).name}")
    inv = Inventaire(chemin)
    ecrire(f"{nom}_{alias}.md", rapport_pc(inv, n))
    ecrire(f"{nom}_annexe_paquets.md", annexe_paquets(inv, n))
    return inv


def faire_comparatif(invs=None):
    invs = invs or {}
    for n in PCS:
        if n not in invs:
            chemin = dernier_inventaire(n)
            if chemin:
                invs[n] = Inventaire(chemin)
    if len(invs) < 2:
        print(">>> Comparatif : il faut au moins 2 inventaires.")
        return
    print(">>> Comparatif du cluster")
    ecrire("CLUSTER_comparatif.md", comparatif(invs))


def faire_tout():
    invs = {}
    for n in PCS:
        inv = faire_rapport(n)
        if inv:
            invs[n] = inv
    faire_comparatif(invs)
    print(f"\nRapports dans : {OUT_DIR}")


def afficher_inventaires():
    print("\nInventaires utilisés (le plus récent de chaque PC) :")
    for n, (nom, alias) in PCS.items():
        c = dernier_inventaire(n)
        print(f"  {nom:4} {alias:18} {Path(c).name if c else '— aucun —'}")


def menu():
    while True:
        print("\n================ RAPPORTS CLUSTER ZETA (lecture seule) ================")
        for n, (nom, alias) in PCS.items():
            print(f"  {n}) Rapport {nom}  ({alias})")
        print("  6) Les 5 rapports + comparatif")
        print("  7) Comparatif du cluster seulement")
        print("  8) Voir les inventaires utilisés")
        print("  0) Quitter")
        choix = input("Choix : ").strip()
        if choix in ("1", "2", "3", "4", "5"):
            faire_rapport(int(choix))
        elif choix == "6":
            faire_tout()
        elif choix == "7":
            faire_comparatif()
        elif choix == "8":
            afficher_inventaires()
        elif choix == "0":
            print(f"Rapports dans : {OUT_DIR}")
            return
        else:
            print("Choix invalide.")


def main(argv):
    if len(argv) <= 1:
        menu()
    elif argv[1] in ("1", "2", "3", "4", "5"):
        faire_rapport(int(argv[1]))
    elif argv[1] == "tous":
        faire_tout()
    elif argv[1] == "comparatif":
        faire_comparatif()
    else:
        print("Usage : zeta_rapport.py [1|2|3|4|5|tous|comparatif]")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
