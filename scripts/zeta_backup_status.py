#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zeta_backup_status.py — Vérification de l'activité du pipeline de sauvegarde
═══════════════════════════════════════════════════════════════════════════
Pipeline surveillé (cf. STACK.md § Infrastructure backup) :
  1. PC1 (zeta-lab, cron 01h50) : rsync logs/ + wiki/ + pdf/ → PC3 (pjexosql@192.168.1.22)
  2. PC3 (zeta-backup, cron 02h00) : rclone copy ~/backup/ → protondrive:hprzeta/Riemann_Lab/backup/

Sources utilisées :
  - PC1 : /var/log/syslog (déclenchement du cron rsync — le job est silencieux,
    -aq, donc syslog ne donne QUE la preuve de déclenchement, pas le succès)
  - PC3 (SSH pjexosql@192.168.1.22, clé ~/.ssh/id_acer — PAS l'alias zeta-backup,
    qui pointe sur l'utilisateur hprzeta, différent du compte propriétaire de
    ~/backup/) :
      - mtime des fichiers sous ~/backup/{logs,wiki,pdf} → preuve indirecte
        d'atterrissage rsync
      - ~/backup/rclone_cron.log → statut réel du rclone (succès/échec/crash)

Usage :
    python scripts/zeta_backup_status.py                  # 7 derniers jours
    python scripts/zeta_backup_status.py --date 2026-08-04
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta

PC3_HOST = "192.168.1.22"
PC3_USER = "pjexosql"
PC3_KEY = "~/.ssh/id_acer"
PC3_BACKUP_DIR = "/home/pjexosql/backup"
SSH_TIMEOUT = 12

PC1_SYSLOG_PATHS = ["/var/log/syslog", "/var/log/syslog.1"]

DATE_RE = re.compile(r"^(\d{4}/\d{2}/\d{2}) (\d{2}:\d{2}:\d{2})")


def ssh_pc3(remote_cmd, timeout=SSH_TIMEOUT):
    """Exécute une commande sur PC3 en tant que pjexosql. Retourne (stdout, ok)."""
    key = os.path.expanduser(PC3_KEY)
    args = [
        "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=6",
        "-i", key, "{}@{}".format(PC3_USER, PC3_HOST), remote_cmd,
    ]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return proc.stdout, proc.returncode == 0
    except subprocess.TimeoutExpired:
        return None, False
    except FileNotFoundError:
        return None, False
    except Exception:
        return None, False


def parse_args():
    p = argparse.ArgumentParser(description="Statut du pipeline de sauvegarde PC1 → PC3 → ProtonDrive")
    p.add_argument("--date", type=str, default=None,
                    help="Date précise à vérifier (AAAA-MM-JJ). Par défaut : 7 derniers jours.")
    return p.parse_args()


def date_range(date_str):
    if date_str:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Format de date invalide : {} (attendu AAAA-MM-JJ)".format(date_str))
            sys.exit(1)
        return [d]
    today = datetime.now().date()
    return [today - timedelta(days=i) for i in range(6, -1, -1)]


# ── PC1 : déclenchement du cron rsync (preuve d'exécution, pas de succès) ──

def check_pc1_cron_triggers(dates):
    """Retourne {date: 'déclenché'|'non trouvé'} en scannant le(s) syslog(s) local(aux)."""
    triggered = set()
    for path in PC1_SYSLOG_PATHS:
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", errors="ignore") as f:
                for line in f:
                    if "CRON" in line and "rsync" in line and "id_acer" in line and "backup" in line:
                        # Format syslog : 2026-08-05T01:50:01...
                        m = re.match(r"^(\d{4}-\d{2}-\d{2})T", line)
                        if m:
                            triggered.add(m.group(1))
        except Exception:
            continue
    result = {}
    for d in dates:
        key = d.strftime("%Y-%m-%d")
        result[key] = "déclenché" if key in triggered else "non trouvé"
    return result


# ── PC3 : preuve d'atterrissage rsync (fraîcheur des fichiers) ─────────────

def check_pc3_rsync_landing(dates):
    """Retourne {date: bool} — au moins un fichier modifié ce jour-là sous ~/backup/{logs,wiki,pdf}."""
    oldest = min(dates).strftime("%Y-%m-%d")
    cmd = (
        "find {d}/logs {d}/wiki {d}/pdf -type f -newermt '{oldest} 00:00:00' "
        "-printf '%TY-%Tm-%Td\\n' 2>/dev/null | sort -u"
    ).format(d=PC3_BACKUP_DIR, oldest=oldest)
    out, ok = ssh_pc3(cmd, timeout=20)
    if not ok or out is None:
        return None  # PC3 injoignable
    seen = set(line.strip() for line in out.splitlines() if line.strip())
    return {d.strftime("%Y-%m-%d"): (d.strftime("%Y-%m-%d") in seen) for d in dates}


# ── PC3 : statut réel rclone (succès / échec / crash) ──────────────────────

def fetch_rclone_log_events(dates):
    """Une seule commande distante : récupère les lignes datées + les crashs Go
    ('fatal error:'), pour reconstruire les blocs par jour localement."""
    oldest_rclone = min(dates).strftime("%Y/%m/%d")
    cmd = (
        "grep -nE '^[0-9]{{4}}/[0-9]{{2}}/[0-9]{{2}} |^fatal error:' "
        "{d}/rclone_cron.log 2>/dev/null | awk -F: -v d='{oldest}' "
        "'{{line=$0; sub(/^[0-9]+:/,\"\",line); print line}}'"
    ).format(d=PC3_BACKUP_DIR, oldest=oldest_rclone)
    out, ok = ssh_pc3(cmd, timeout=20)
    if not ok or out is None:
        return None
    return out.splitlines()


def parse_rclone_events(lines, dates):
    """Regroupe les lignes par date (format rclone AAAA/MM/JJ) et détecte succès/échec."""
    wanted = {d.strftime("%Y/%m/%d"): d.strftime("%Y-%m-%d") for d in dates}
    blocks = {}  # date iso -> dict(heure, transferred, fatal, errors[])
    current_key = None

    for raw in lines:
        m = DATE_RE.match(raw)
        if m:
            rclone_date, heure = m.group(1), m.group(2)
            if rclone_date in wanted:
                iso = wanted[rclone_date]
                if iso not in blocks:
                    blocks[iso] = {"heure": heure, "transferred": None, "fatal": False, "errors": []}
                current_key = iso
                if "Transferred:" in raw:
                    blocks[iso]["transferred"] = raw.split("Transferred:", 1)[1].strip()
                elif " ERROR " in raw or ": ERROR" in raw or "ERROR :" in raw:
                    blocks[iso]["errors"].append(raw.strip())
            else:
                current_key = None  # date hors de la fenêtre demandée
        elif raw.startswith("fatal error:"):
            if current_key is not None:
                blocks[current_key]["fatal"] = True
                blocks[current_key]["errors"].append(raw.strip())

    return blocks


def build_rclone_status(dates):
    lines = fetch_rclone_log_events(dates)
    if lines is None:
        return None  # PC3 injoignable
    blocks = parse_rclone_events(lines, dates)
    result = {}
    for d in dates:
        key = d.strftime("%Y-%m-%d")
        b = blocks.get(key)
        if b is None:
            result[key] = {"heure": "—", "statut": "SAUTÉ", "taille": "—", "erreur": "aucune ligne trouvée"}
            continue
        if b["transferred"] and not b["fatal"]:
            statut = "SUCCÈS"
            erreur = ""
        elif b["fatal"]:
            statut = "ÉCHEC"
            erreur = "crash rclone (fatal error Go) — " + (b["errors"][0] if b["errors"] else "?")
        elif b["errors"]:
            statut = "ÉCHEC"
            erreur = b["errors"][-1]
        else:
            statut = "ÉCHEC"
            erreur = "log présent mais aucun résumé 'Transferred:' trouvé"
        result[key] = {
            "heure": b["heure"],
            "statut": statut,
            "taille": b["transferred"] or "N/A",
            "erreur": erreur[:90],
        }
    return result


# ── Affichage ────────────────────────────────────────────────────────────

def print_table(title, headers, rows, widths):
    print("\n{}".format(title))
    print("=" * len(title))
    fmt = "  ".join("{{:<{}}}".format(w) for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for row in rows:
        cells = [str(c)[:w] for c, w in zip(row, widths)]
        print(fmt.format(*cells))


def main():
    args = parse_args()
    dates = date_range(args.date)

    print("Statut backup — {} → {} ({} jour(s))".format(
        dates[0].strftime("%d/%m/%Y"), dates[-1].strftime("%d/%m/%Y"), len(dates)))

    # PC1 → PC3 (rsync)
    triggers = check_pc1_cron_triggers(dates)
    landing = check_pc3_rsync_landing(dates)

    rows = []
    for d in dates:
        key = d.strftime("%Y-%m-%d")
        trig = triggers[key]
        if landing is None:
            atterrissage = "PC3 injoignable"
        else:
            atterrissage = "fichiers reçus" if landing[key] else "aucun fichier détecté"
        rows.append((d.strftime("%d/%m/%Y"), "01:50", trig, atterrissage))
    print_table(
        "Sync 1 — PC1 → PC3 (rsync logs/wiki/pdf)",
        ["Date", "Heure cron", "Déclenchement (PC1)", "Atterrissage (PC3)"],
        rows, [12, 10, 22, 24],
    )
    print("  Note : rsync tourne en mode silencieux (-aq) — aucun log de succès/échec")
    print("  côté PC1. 'Atterrissage' = preuve indirecte (fichier modifié ce jour-là sur PC3).")
    print("  'non trouvé' = pas de ligne CRON pour cette date dans /var/log/syslog(.1)")
    print("  (rotation, OU machine éteinte à 01:50 ce jour-là — à ne pas confondre avec un échec du job).")

    # PC3 → ProtonDrive (rclone)
    rclone_status = build_rclone_status(dates)
    if rclone_status is None:
        print("\nSync 2 — PC3 → ProtonDrive (rclone) : PC3 INJOIGNABLE (timeout SSH)")
    else:
        rows = []
        for d in dates:
            key = d.strftime("%Y-%m-%d")
            r = rclone_status[key]
            rows.append((d.strftime("%d/%m/%Y"), r["heure"], r["statut"], r["taille"], r["erreur"]))
        print_table(
            "Sync 2 — PC3 → ProtonDrive (rclone)",
            ["Date", "Heure", "Statut", "Taille transférée", "Erreur"],
            rows, [12, 10, 8, 20, 60],
        )
        n_echec = sum(1 for d in dates if rclone_status[d.strftime("%Y-%m-%d")]["statut"] == "ÉCHEC")
        if n_echec:
            print("\n  ⚠️  {}/{} jour(s) en ÉCHEC sur la période affichée.".format(n_echec, len(dates)))


if __name__ == "__main__":
    main()
