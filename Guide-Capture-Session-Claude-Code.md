# Guide — Capture de session Claude Code
> Auteur : hprzeta · Créé le : 2 juin 2026
> Enregistrer, relire et archiver les sessions Claude Code en fichier `.md` propre

---

## 🎯 Principe général

`capture.sh` enregistre **tout ce qui s'affiche dans le terminal Claude Code**
pendant que tu travailles normalement — exactement comme si quelqu'un prenait
des notes pour toi en temps réel.

```
Tu lances capture.sh
      ↓
Tu lances claude (dans le terminal enregistré)
      ↓
Tu travailles normalement — tout est capturé en arrière-plan
      ↓
Tu tapes exit → .md propre généré automatiquement
```

---

## 📁 Fichiers produits

```
~/projet_zeta/
└── claude-traitement-journalier/          ← ignoré par Git (.gitignore ✅)
    ├── session_20260602_1600.log          ← brut (illisible — archive)
    └── session_20260602_1600.md           ← propre (à lire dans VS Code)
```

| Fichier | Créé quand | Lisible ? | Usage |
|---|---|---|---|
| `.log` | Immédiatement au démarrage | ❌ Caractères bizarres | Archive brute, ne pas ouvrir |
| `.md` | Seulement après `exit` | ✅ Propre dans VS Code | Relecture tranquille |

---

## 🚀 Utilisation quotidienne

```bash
# 1. Lancer la capture (AVANT claude)
~/projet_zeta/scripts/capture.sh

# 2. Dans le terminal enregistré, lancer Claude Code
claude

# 3. Travailler normalement...

# 4. À la fin de la journée, arrêter
exit
# → Le .md propre est généré automatiquement
# → Message : ✅ Version lisible : .../session_YYYYMMDD_HHMM.md
```

---

## 👁️ Lire en direct pendant que ça tourne

Le `.log` est disponible **immédiatement** pendant la session.
Dans un **2ème terminal bash** (pas Claude Code) :

```bash
# Les 50 dernières lignes nettoyées
tail -50 ~/projet_zeta/claude-traitement-journalier/session_*.log \
  | sed 's/\x1b\[[0-9;]*[mGKHF]//g'

# Suivi en temps réel (comme tail -f, mais propre)
tail -f ~/projet_zeta/claude-traitement-journalier/session_*.log \
  | sed 's/\x1b\[[0-9;]*[mGKHF]//g'
# Ctrl+C pour arrêter le suivi
```

---

## 📖 Ouvrir le `.md` après exit

```bash
# Dans un terminal bash
code ~/projet_zeta/claude-traitement-journalier/session_20260602_1600.md

# Ou dans l'explorateur VS Code :
# projet_zeta → claude-traitement-journalier → session_*.md (clic)
```

---

## ✅ Ce que `capture.sh` enregistre

| Contenu | Capturé ? |
|---|---|
| Messages de Claude Code (insights, analyses, décisions) | ✅ |
| Sorties bash (workers, résultats, tableaux de zéros) | ✅ |
| Erreurs et avertissements | ✅ |
| Confirmations (1. Yes / 2. No et réponse choisie) | ✅ |
| Barre de statut du bas (tokens, cache, branche) | ✅ |
| Onglets VS Code (éditeur, explorateur) | ❌ Terminal uniquement |
| Autres terminaux ouverts | ❌ Ce terminal uniquement |
| App web claude.ai | ❌ Navigateur uniquement |

---

## ⚠️ Pièges connus

### Le `.log` s'ouvre avec des caractères bizarres dans VS Code
**Cause :** VS Code ouvre le `.log` brut qui contient les codes couleur ANSI.
**Solution :** ferme cet onglet, ouvre le `.md` à la place.
Le `.log` n'est pas fait pour être lu dans un éditeur.

### Le `.md` n'apparaît pas dans l'explorateur VS Code
**Cause :** la session est encore en cours — le `.md` n'existe pas encore.
**Solution :** tape `exit` dans le terminal Claude Code pour générer le `.md`.

### `exit` a fermé Claude Code en plein milieu d'un run
**Cause :** `exit` arrête `script` ET le shell — donc Claude Code aussi.
**Règle :** ne taper `exit` qu'à la **fin de la journée**, jamais pendant un run.

### Deux terminaux ouverts — lequel enregistre ?
Seul le terminal lancé par `capture.sh` est enregistré.
Le terminal bash séparé (2ème terminal) n'est **pas** dans la capture.

---

## 🗂️ Nommage et archivage

Les fichiers sont nommés automatiquement :
```
session_YYYYMMDD_HHMM.log   →   session_20260602_1600.log
session_YYYYMMDD_HHMM.md    →   session_20260602_1600.md
```

Pour retrouver une session passée :
```bash
# Lister toutes les sessions
ls -lh ~/projet_zeta/claude-traitement-journalier/

# Chercher une session par date
ls ~/projet_zeta/claude-traitement-journalier/ | grep 20260602

# Chercher un mot-clé dans les sessions passées
grep -l "Vérif A" ~/projet_zeta/claude-traitement-journalier/*.md
```

---

## 🔧 Script `capture.sh` — code complet

```bash
#!/usr/bin/env bash
# capture.sh — Enregistre une session Claude Code
# Auteur : hprzeta · Projet : Riemann_Lab · 2 juin 2026
DOSSIER="$HOME/projet_zeta/claude-traitement-journalier"
HORODATAGE=$(date +%Y%m%d_%H%M)
BRUT="$DOSSIER/session_${HORODATAGE}.log"
PROPRE="$DOSSIER/session_${HORODATAGE}.md"
mkdir -p "$DOSSIER"
echo "============================================================"
echo "  📹  Capture de session Claude Code — Riemann_Lab"
echo "  Fichier brut  : $BRUT"
echo "  Fichier propre: $PROPRE"
echo "  → Lance 'claude', puis 'exit' pour arrêter"
echo "============================================================"
script -q -f "$BRUT"
echo "⏳ Nettoyage des codes couleur ANSI..."
sed 's/\x1b\[[0-9;]*[mGKHF]//g' "$BRUT" \
  | sed 's/\r$//' | sed '/^$/N;/^\n$/d' > "$PROPRE"
echo "✅ Session enregistrée :"
echo "   Brut  : $BRUT  ($(wc -l < "$BRUT") lignes)"
echo "   Propre: $PROPRE  ($(wc -l < "$PROPRE") lignes)"
echo "💡 Pour relire : code '$PROPRE'"
```

**Emplacement :** `~/projet_zeta/scripts/capture.sh`
**Permissions :** `chmod +x ~/projet_zeta/scripts/capture.sh`

---

## 📋 Pourquoi `script` et pas `> fichier` ?

Claude Code est une **application interactive** (TUI). Une redirection `>`
lui retire le terminal → l'affichage casse et tu ne peux plus taper.

`script` crée un **pseudo-TTY intermédiaire** : Claude Code croit parler à
un vrai terminal (tout fonctionne normalement), mais `script` enregistre
le flux en parallèle. C'est le seul mécanisme propre pour capturer une
application interactive sous Linux.

---

*Auteur : hprzeta · Créé le : 2 juin 2026 — ~192 lignes*
