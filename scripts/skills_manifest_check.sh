#!/usr/bin/env bash
# skills_manifest_check.sh — compare les hashs des skills du dépôt au manifeste.
# Lecture seule, sans réseau. Code de sortie : 0 = aligné, 1 = dérive, 2 = erreur d'usage.
# Hash = SHA-256 du CORPS de SKILL.md (sans frontmatter), espaces de fin de ligne
# et lignes vides finales retirés (le compte ne conserve que name + description).
set -u

# Racine du dépôt : dossier parent de scripts/ (aucun chemin en dur)
RACINE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS="${RACINE}/.claude/skills"
MANIFEST="${SKILLS}/MANIFEST.md"

# Vérifications préalables
[ -d "$SKILLS" ] || { echo "ERREUR : dossier introuvable : .claude/skills" >&2; exit 2; }
[ -f "$MANIFEST" ] || { echo "ERREUR : MANIFEST.md introuvable" >&2; exit 2; }

# Tout le calcul est fait par python3 en mode isolé (-I), sans écriture ni réseau
exec python3 -I - "$SKILLS" "$MANIFEST" <<'PYEOF'
import sys, os, re, glob, hashlib

skills_dir, manifest = sys.argv[1], sys.argv[2]

def corps(chemin):
    """Retourne le corps normalisé (sans frontmatter) d'un SKILL.md."""
    with open(chemin, encoding="utf-8") as f:
        lignes = f.read().split("\n")
    # Retire le frontmatter : première ligne '---' jusqu'à la suivante
    if lignes and lignes[0].strip() == "---":
        for i in range(1, len(lignes)):
            if lignes[i].strip() == "---":
                lignes = lignes[i + 1:]
                break
    # Espaces de fin retirés ligne par ligne, lignes vides finales retirées
    lignes = [l.rstrip() for l in lignes]
    while lignes and lignes[-1] == "":
        lignes.pop()
    return "\n".join(lignes)

def sha(texte):
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()

# --- Lecture du manifeste : lignes de tableau « | nom | version | hash | ... »
attendu = {}      # nom -> (hash dépôt, hash compte)
plugin = {}       # nom -> hash (section plugin tiers)
section = None
with open(manifest, encoding="utf-8") as f:
    for ligne in f:
        if ligne.startswith("## "):
            section = ligne.strip()
        if not ligne.startswith("|"):
            continue
        c = [x.strip().strip("`") for x in ligne.strip().strip("|").split("|")]
        if len(c) < 6 or c[0] in ("nom", "") or set(c[0]) <= set("-: "):
            continue
        if section and "plugin" in section.lower():
            plugin[c[0]] = c[2]
        else:
            attendu[c[0]] = (c[2], c[4])

derives = 0
print(f"{'skill':32} {'état':14} détail")

# --- Skills du dépôt
presents = sorted(d for d in os.listdir(skills_dir)
                  if os.path.isfile(os.path.join(skills_dir, d, "SKILL.md")))
for nom in presents:
    h = sha(corps(os.path.join(skills_dir, nom, "SKILL.md")))
    if nom not in attendu:
        print(f"{nom:32} {'NON LISTÉ':14} absent du manifeste (hash {h[:12]})"); derives += 1
        continue
    h_man, h_compte = attendu[nom]
    if h != h_man:
        print(f"{nom:32} {'DÉRIVE':14} dépôt {h[:12]} ≠ manifeste {h_man[:12]}"); derives += 1
    elif h_compte not in ("", "—", "-", "à renseigner") and h_compte != h:
        print(f"{nom:32} {'COMPTE ≠':14} compte {h_compte[:12]} ≠ dépôt {h[:12]}"); derives += 1
    else:
        etat = "OK" if h_compte == h else "OK (compte ?)"
        print(f"{nom:32} {etat:14} {h[:12]}")
for nom in sorted(set(attendu) - set(presents)):
    print(f"{nom:32} {'MANQUANT':14} listé au manifeste, absent du dépôt"); derives += 1

# --- Skills du plugin tiers (superpowers), si le dossier est trouvé (glob, pas de chemin en dur)
base = os.path.expanduser("~/.claude/plugins/synced/*/*/skills")
for nom, h_man in sorted(plugin.items()):
    trouves = glob.glob(os.path.join(base, nom, "SKILL.md"))
    if not trouves:
        print(f"{'superpowers:'+nom:32} {'NON VÉRIFIÉ':14} plugin introuvable"); continue
    h = sha(corps(trouves[0]))
    if h != h_man:
        print(f"{'superpowers:'+nom:32} {'DÉRIVE':14} plugin {h[:12]} ≠ manifeste {h_man[:12]}"); derives += 1
    else:
        print(f"{'superpowers:'+nom:32} {'OK':14} {h[:12]}")

print(f"\n{len(presents)} skills du dépôt, {len(plugin)} du plugin ; dérives : {derives}")
sys.exit(1 if derives else 0)
PYEOF
