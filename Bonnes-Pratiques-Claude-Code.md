# Bonnes Pratiques — Claude Code & Claude (app web)
> Auteur : hprzeta · Mis à jour : **2 juin 2026**
> Guide vivant — enrichi à chaque nouvelle leçon de session
> Fusion : version wiki 1ᵉʳ juin + leçons session 2 juin (529, crédits, modèle, capture)

---

## 🎯 Comprendre les DEUX compteurs de consommation

C'est la confusion n°1. Il y a deux choses **différentes** à surveiller :

### 1. Les fenêtres de plafond (5h / 7d)
Affichées en bas de Claude Code :
```
5h[█ 18%]⏱4h18m | 7d[█ 21%]⏱3d13h | Sonnet 4.6(26.0k/200.0k) | cache 1m46s
↳ Riemann_Lab ⑂ Riemann_Lab_C
```

| Segment | Ce que c'est | Quand agir |
|---|---|---|
| `5h[█ X%]⏱Yh` | Quota **fenêtre glissante 5h** — forfait Pro | Proche 100% → pause forcée |
| `7d[█ X%]⏱Yh` | Quota **semaine glissante 7j** | Rarement critique |
| `Sonnet 4.6(Xk/200k)` | **Contexte session** — mémoire de travail | ⚠️ Seuils tableau ci-dessous |
| `cache Xm Xs` | Cache prompt — expire en ~5 min | Relancer vite = plus rapide/moins cher |
| `cache COLD` | Cache expiré | Pas grave — Claude recharge au prochain appel |
| `↳ Repo ⑂ Branche` | Repère Git actif | Vérifier branche avant tout commit |

### 2. Le contexte / auto-compact (le plus important pour la qualité)
Affiché comme `XX% context used` (bas droite) ou `(XX.0k/200.0k)` à côté du modèle.
- C'est la **mémoire de travail** de Claude Code dans la session en cours
- À ~200k tokens, l'**auto-compact** se déclenche : Claude Code RÉSUME l'historique
  → il peut OUBLIER des contraintes ou RÉPÉTER du travail déjà fait
- C'est CE compteur qui dicte quand committer/pousser

| Compteur | Ce qu'il limite | Quand s'inquiéter |
|---|---|---|
| 5h / 7d | Volume de travail autorisé | Proche de 100% = pause forcée |
| Contexte (k/200k) | Qualité/cohérence de la session | > 70% = sécuriser le travail |

---

## 📊 Seuils d'action selon le contexte (% context used)

| Seuil contexte | Action OBLIGATOIRE |
|---|---|
| **< 50%** | Travail normal. On peut démarrer une grosse tâche. |
| **50%** | `git commit` checkpoint (wip). Tâche en cours = on continue. |
| **70%** | `git push origin <branche>`. NE PAS démarrer de nouvelle grosse tâche. |
| **80%** | STOP nouvelles tâches. Finir/sécuriser uniquement. |
| **85–90%** | URGENCE : commit + push IMMÉDIAT. Aucun nouveau test/run. |
| **> 90%** | Commit/push depuis le TERMINAL BASH (pas Claude Code) pour ne pas consommer plus de contexte. Puis fermer. |

### Leçon vécue (31 mai)
À 85–92% de contexte, Claude Code continuait à lancer des tests de diagnostic
au lieu de committer, malgré les STOP. **Solution qui a marché :** taper la
commande git directement dans le **TERMINAL BASH** (fond violet), pas dans
Claude Code. Le bash exécute instantanément SANS consommer de contexte Claude Code.

```bash
# Commande de sauvetage à 90%+ (terminal bash, PAS Claude Code) :
cd ~/projet_zeta && git add -A && git commit -m "wip: checkpoint" && git push origin Riemann_Lab_C
```

---

## 🛑 Points d'arrêt obligatoires — la pratique qui sauve les runs

C'est la leçon la plus rentable de la session v4.1.

**Principe :** avant tout run long (plusieurs minutes), insérer des POINTS D'ARRÊT
où Claude Code DOIT montrer ses chiffres et attendre un "OK continue" explicite.
```
- STOP ici. Montre-moi ces chiffres et attends mon "OK continue".
```

### Pourquoi ça vaut de l'or (preuve chiffrée)
Au point d'arrêt n°1 de v4.1, le test a révélé **359 désaccords** sur la
détection des changements de signe. Sans ce point d'arrêt, un run de plusieurs
heures aurait RATÉ des centaines de zéros sans alerte. Le test a tué le bug
en quelques minutes, avant le run long.

### Grille de décision à un point d'arrêt de détection
| Ce que tu vois | Décision |
|---|---|
| 0 désaccord + mêmes changements de signe partout | "OK continue" |
| Écart numérique ~1e-3 mais 0 désaccord | "OK continue" (normal = troncature RS) |
| Désaccords > 0, ou nb de changements de signe différent | STOP — diagnostiquer avant tout run |

---

## 🧠 Choix du modèle — Sonnet par défaut, pas Opus

| Modèle | Usage | Coût relatif | Verdict projet |
|---|---|---|---|
| Opus 4.x | Décisions d'architecture délicates, diagnostic complexe | ×5 à ×10 | Surdimensionné au quotidien — épuise les crédits vite |
| **Sonnet 4.6** | Code, math, documents, sessions longues | ×1 | ✅ **Modèle cible** |
| Haiku 4.x | Réponses courtes, classification simple | ×0.2 | Trop léger pour le raisonnement zêta |

Rester sur **Sonnet par défaut**. Basculer sur Opus (`/model`) uniquement pour
les vrais blocages d'architecture, puis repasser sur Sonnet.

**Deux endroits à configurer (une seule fois) :**
```bash
# 1. Claude Code — dans ~/.claude/CLAUDE.md (LOCAL, ne jamais committer)
## Modèle par défaut
# Utiliser Claude Sonnet 4.6. Ne pas basculer sur Opus sauf demande hprzeta.
```
```
2. App web claude.ai : Paramètres → Général → Modèle par défaut → Sonnet 4.6
```

**Changer en cours de session :**
```bash
/model claude-sonnet-4-6    # basculer sur Sonnet
/model                      # voir le modèle actuel
```

---

## ⚠️ Erreurs serveur — 529 Overloaded

```
API Error: 529 Overloaded. This is a server-side issue, usually temporary.
```
Pas un problème de ton code ou de ta machine.
Vérifier en temps réel : **https://status.claude.com**

| Statut | Signification | Action |
|---|---|---|
| 🟢 Opérationnel | Tout va bien | — |
| 🟡 Panne partielle | Dégradé | Réessayer toutes les 30–60 secondes |
| 🔴 Panne complète | Attendre | S'abonner aux mises à jour |

Le travail déjà écrit sur le disque n'est **pas perdu** — retaper la même commande.
Si l'incident touche Opus mais pas Sonnet (fréquent) : encore une raison de rester Sonnet.

**Bon réflexe :** vérifier `status.claude.com` avant toute longue session.

---

## 💳 Crédits et limite de dépenses — les deux chiffres

| Chiffre | Rôle | Que faire si atteint |
|---|---|---|
| **Solde de crédits** (ex. 17,58 €) | L'argent réellement disponible. Renouvellement mensuel. | Acheter des crédits si besoin |
| **Limite mensuelle** (ex. 25 €) | Frein **volontaire** — ne **jamais** supprimer | Augmenter modérément via le `+` |

**⚠️ Ne jamais cliquer « Supprimer la limite »** — tu perdrais tout garde-fou et
pourrais dépenser l'intégralité du solde sans alerte.

**Si la limite mensuelle bloque :**
1. Paramètres → Utilisation → Crédits d'utilisation.
2. Cliquer `+` → monter de quelques euros → Enregistrer. Déblocage immédiat.
3. Ne jamais monter la limite au-delà de ton solde réel (inutile).

**Lire la page Utilisation :**
```
Barre rouge  → quota session 5h de l'app WEB (≠ Claude Code)
Barre bleue  → quota 7 jours tous modèles
Barre jaune  → % du plafond mensuel consommé
Solde actuel → vrais euros disponibles
```
**Important :** app web (claude.ai) et Claude Code (terminal) ont des quotas
**séparés**. Barre rouge à 100% dans l'app web ne bloque **pas** Claude Code.

---

## 📹 Capturer une session Claude Code en fichier .md relisible

Pour relire tranquillement tout ce que Claude Code a affiché.

### Script `capture.sh`
```bash
#!/usr/bin/env bash
# capture.sh — session Claude Code → .log brut + .md propre — hprzeta
DOSSIER="$HOME/projet_zeta/claude-traitement-journalier"
mkdir -p "$DOSSIER"
HORODATAGE=$(date +%Y%m%d_%H%M)
BRUT="$DOSSIER/session_${HORODATAGE}.log"
PROPRE="$DOSSIER/session_${HORODATAGE}.md"
echo "📹 Enregistrement → $BRUT  (tape 'exit' pour arrêter)"
script -q -f "$BRUT"
sed 's/\x1b\[[0-9;]*[mGKHF]//g' "$BRUT" | sed 's/\r$//' > "$PROPRE"
echo "✅ Version lisible : $PROPRE"
```

```bash
# Installation (une seule fois)
mkdir -p ~/projet_zeta/scripts
nano ~/projet_zeta/scripts/capture.sh    # coller le script ci-dessus
chmod +x ~/projet_zeta/scripts/capture.sh
echo "claude-traitement-journalier/" >> ~/projet_zeta/.gitignore

# Utilisation quotidienne
~/projet_zeta/scripts/capture.sh    # AVANT de lancer Claude Code
claude
exit                                 # arrête l'enregistrement + génère le .md propre
```

> **Pourquoi `script` et pas `> fichier` ?** Claude Code est une TUI
> (interactive). Une redirection `>` lui retire le terminal et casse
> l'affichage. `script` crée un pseudo-TTY intermédiaire — tout fonctionne
> normalement à l'écran, et le flux est enregistré en parallèle. Les codes
> couleur ANSI sont nettoyés automatiquement ; les emojis (✅ ⚠️ 🛑) restent.

---

## 🖱️ Permissions d'édition — ne pas cliquer "allow all"

```
Do you want to make this edit?
1. Yes
2. Yes, allow all edits during this session (shift+tab)
3. No
```
- Choisir **1 (Yes)** — valider au cas par cas, tu gardes la visibilité
- ÉVITER **2 (allow all)** en phase de débogage délicat : tu perds le contrôle
- Les petits tests de diagnostic sont sûrs → Yes

---

## 📋 Coller un bloc de commandes généré par une IA

Les blocs contiennent parfois des **placeholders** à remplacer :
`~/chemin/vers/fichier.md`, `<branche>`, `FICHIER`. Collés tels quels,
ils provoquent une **chaîne de non-opérations silencieuse** :
```bash
cp ~/chemin/vers/Handoff.md .   # ÉCHOUE silencieusement
                                # → git add ne trouve rien
                                # → commit "aucune modification"
                                # → push "up-to-date" — rien n'a été poussé
```
Aucune erreur bloquante, mais **rien n'a été poussé.** (Vécu le 1ᵉʳ juin.)

**Réflexes :**
1. Lire le bloc avant de le coller — repérer tout placeholder.
2. Mettre le vrai chemin (`~/Téléchargements/...`).
3. Vérifier : `head -3 fichier.md` après un `cp` ; regarder la sortie de
   `git commit` (« 1 file changed » = OK ; « up-to-date » inattendu = échec amont).

> Détail des pièges Git (`git rm` vs `rm`, untracked ≠ page wiki) :
> voir `Guide-Git-GitHub.md` §21.

---

## 🔐 Sécurité Git — secrets

**Règle d'or :** un secret (token, mot de passe, clé) ne va JAMAIS dans
un fichier suivi par Git.

- Mettre les fichiers sensibles (`.mcp.json`) dans `.gitignore` AVANT le 1er commit.
- `.gitignore` ne purge PAS le passé : si un secret est commité, réécrire
  l'historique (`git filter-repo --path FICHIER --invert-paths`).
- Si GitHub Push Protection bloque (GH013) : **révoquer le token d'abord**,
  puis purger. NE JAMAIS cliquer "unblock-secret".
- Vérifier : `git check-ignore .mcp.json`
- Le `.gitignore` n'est **pas** synchronisé entre branches : vérifier sur CHAQUE branche.

---

## 💾 Fin de session propre

```bash
git add -A
git commit -m "wip: checkpoint [description courte]"
git push origin <branche>
```

Si la session a produit des résultats à transmettre :
- Créer `docs/session_checkpoint_YYYYMMDD.md` : état actuel, résultats validés,
  problème restant, prochaine étape.
- Mettre à jour **Handoff.md** (section « REPRENDRE ICI »).
- Ajouter un **pavé daté en haut de `JOURNAL.md`** (résumé de la session).

**Mémo de reprise :** toujours laisser dans `Handoff.md` un état exact → gain
de ~20 min au redémarrage.

---

## 🔀 Git — règles du projet

| Branche | Usage |
|---|---|
| `Riemann_Lab_IA` | Développement principal, docs, wiki |
| `Riemann_Lab_C` | Phase C — Illinois C/libmpfr |
| `main` | Stable uniquement |

- Tous les `.md` → wiki (`~/projet_zeta/Riemann_Lab.wiki/`, branche `master`).
- `Handoff.md` ne va **JAMAIS** dans le repo principal `Riemann_Lab_IA`.
- Convention commit : `feat(...)`, `fix(...)`, `docs(...)`, `chore: ...`, `wip: ...`

---

## ⚙️ ~/.claude/CLAUDE.md global — structure recommandée

Ce fichier est **LOCAL** — ne jamais committer dans un dépôt projet.

```markdown
# ~/.claude/CLAUDE.md — Instructions globales
## Modèle par défaut
Utiliser Claude Sonnet 4.6. Ne pas basculer sur Opus sauf demande hprzeta.
## Langue et style
- Toujours répondre en français
- Code commenté ligne par ligne
- Distinguer : théorème prouvé / conjecture / heuristique / intuition
- Formules en LaTeX
## Règles code
- plt.savefig() + plt.close() — jamais plt.show() en production
- Ne pas utiliser joblib avec mpmath (GMP non thread-safe)
## Sécurité
- git status AVANT tout git add -A
- .mcp.json ne doit JAMAIS être commité
- Un secret exposé = secret mort : révoquer, ne jamais suivre "unblock-secret"
```

| Fichier | Portée | Committer ? | Contenu |
|---|---|---|---|
| `~/.claude/CLAUDE.md` | Toute la machine | ❌ Jamais | Règles globales légères |
| `~/projet_zeta/CLAUDE.md` | Projet uniquement | ✅ Oui | Contexte complet, formules, état Phase C |

---

## 🔧 Commandes utiles du quotidien

```bash
# Modèle
/model                           # voir le modèle actif
/model claude-sonnet-4-6         # basculer sur Sonnet

# Checkpoint Git (règle 50% contexte)
git add -A && git commit -m "wip: checkpoint $(date +%Y%m%d_%H%M)"
git push origin Riemann_Lab_C

# Sauvetage à 90%+ (terminal bash, PAS Claude Code)
cd ~/projet_zeta && git add -A && git commit -m "wip: urgence" && git push origin Riemann_Lab_C

# Capture de session (lancer AVANT claude)
~/projet_zeta/scripts/capture.sh

# Vérifier les serveurs Anthropic
# → ouvrir https://status.claude.com dans le navigateur

# Vérifier l'usage des crédits
# → claude.ai → Paramètres → Utilisation
```

---

*Auteur : hprzeta · Mise à jour : 2 juin 2026 — $~418 lignes*

---

## 📹 Capture de session — comportement détaillé (leçon 2 juin)

### Ce que `capture.sh` enregistre exactement

Tout ce qui s'affiche dans le terminal Claude Code est capturé :
- Les messages de Claude Code (insights, analyses, décisions)
- Les sorties bash (workers, résultats, tableaux)
- Les erreurs et avertissements
- Les confirmations (1. Yes / 2. No)
- La barre de statut du bas

**Ce qui n'est PAS dans la capture :**
- Les onglets VS Code (éditeur, explorateur)
- Les autres terminaux
- L'app web claude.ai

### Quand le `.md` propre est généré

```
capture.sh lancé → .log brut créé IMMÉDIATEMENT (enregistrement en direct)
                 → .md propre créé SEULEMENT quand tu tapes 'exit'
```

| Moment | Fichier disponible | Lisible ? |
|---|---|---|
| Pendant la session | `.log` uniquement | ❌ Caractères bizarres |
| Après `exit` | `.log` + `.md` | ✅ `.md` propre dans VS Code |

### Lire en direct pendant que ça tourne (sans attendre exit)

Dans un **2ème terminal bash** (pas Claude Code) :

```bash
# Voir les 50 dernières lignes nettoyées
tail -50 ~/projet_zeta/claude-traitement-journalier/session_*.log \
  | sed 's/\x1b\[[0-9;]*[mGKHF]//g'

# Suivre en temps réel (comme un tail -f nettoyé)
tail -f ~/projet_zeta/claude-traitement-journalier/session_*.log \
  | sed 's/\x1b\[[0-9;]*[mGKHF]//g'
# Ctrl+C pour arrêter le suivi
```

### Où trouver les fichiers

```
~/projet_zeta/
└── claude-traitement-journalier/     ← dossier ignoré par Git (.gitignore)
    ├── session_20260602_1600.log     ← brut (illisible directement)
    └── session_20260602_1600.md      ← propre (généré à la fin, après exit)
```

### Ouvrir le `.md` dans VS Code après exit

```bash
# Depuis un terminal bash
code ~/projet_zeta/claude-traitement-journalier/session_20260602_1600.md

# Ou dans l'explorateur VS Code à gauche :
# projet_zeta → claude-traitement-journalier → session_*.md
```

### Problème connu : le `.log` s'ouvre avec des caractères bizarres

Si VS Code ouvre le `.log` directement → ferme-le, ouvre le `.md` à la place.
Le `.log` n'est pas fait pour être lu dans un éditeur — c'est une archive brute.
> **Fichier :** Bonnes-Pratiques-Claude-Code.md · **Dossier :** wiki racine
> **Branche :** master · **Auteur :** hprzeta · **MAJ :** 2026-06-10

---

---

## 🔄 Nouvelle conversation vs rouvrir une ancienne — quand choisir ?

Si tu fermes accidentellement une fenêtre Claude.ai :

| Situation | Action | Pourquoi |
|---|---|---|
| Conversation récente, peu de tokens | Rouvrir | Contexte encore léger |
| Conversation longue (>50k tokens) | **Nouvelle conversation** | Rouvrir = recharger TOUS les vieux tokens → coûteux |
| Tu changes de tâche | **Nouvelle conversation** | Contexte propre = moins cher et plus efficace |
| Tu es en milieu de tâche critique | Rouvrir | Ne pas perdre le fil |

**Règle simple :** si la conversation avait déjà beaucoup tourné → nouvelle conv + coller le Handoff.

---

## 📦 Workflow inbox-ia — lire des docs sans les uploader

Pour donner des documents à lire à Claude sans surcharger le projet :

```
1. Convertir PDF → MD (script pdf_to_md_voie_b5.sh)
   → résultat dans ~/projet_zeta/pdf/optimisation/Voie_b_5/md_to_claude/

2. Pousser sur inbox-ia :
   git checkout inbox-ia
   cp ~/projet_zeta/pdf/optimisation/Voie_b_5/md_to_claude/*.md .
   git add *.md
   git commit -m "inbox: ajout N pavés ($(date +%F))"
   git push origin inbox-ia
   git checkout Riemann_Lab_IA

3. Donner l'URL à Claude :
   "Lis les fichiers sur la branche inbox-ia de hprzeta/Riemann_Lab"

4. Archiver quand Claude a fini :
   git checkout inbox-ia && git rm FICHIER.md
   git commit -m "inbox: archive FICHIER ($(date +%F))"
   git push origin inbox-ia
   git checkout Riemann_Lab_IA
```

**Règles inbox-ia :**
- ✅ Fichiers `.md` légers uniquement (convertis depuis PDF)
- ❌ Jamais de secrets, tokens, chemins système
- ❌ Jamais de PDFs directement (trop lourds)
- Le dossier `.pdf_to_md/` est LOCAL et dans `.gitignore` — jamais pushé

---

## 🖥️ 2 terminaux en parallèle — sans conflit

Tu peux ouvrir un 2ème terminal VS Code (`Ctrl+Shift+\``) pendant que Claude Code tourne :

| Terminal 1 (Claude Code) | Terminal 2 (bash libre) |
|---|---|
| Claude Code bosse | Tu pousses des fichiers |
| Sur branche X | Sur branche Y différente |
| Ne pas interrompre | Aucun conflit possible |

**Condition :** travailler sur des **branches différentes**. Si même branche → risque de conflit.

---

## 📊 Règle des 50k tokens non cachés

Dans la barre de statut Claude Code :
```
~87k uncached · /clear to start fresh
```

| uncached | Action |
|---|---|
| < 30k | Normal, continuer |
| 30–50k | Surveiller |
| > 50k | `/clear` entre deux tâches |
| cache COLD | `/clear` recommandé avant grosse tâche |

**Après `/clear` :** Claude Code relit automatiquement les `CLAUDE.md` en cascade → pas besoin de tout ré-expliquer.

---

## ⚡ `high · effort` dans la barre de statut

```
Sonnet 4.6(36.0k/200.0k) | cache 4m13s · high · effort
```

`high · effort` = Claude Code est en mode raisonnement approfondi sur une tâche complexe (ex: git multi-branches, diagnostic algorithme). C'est **normal et attendu** — pas un problème. Consomme un peu plus de tokens mais produit une meilleure analyse.

---

## 📚 Recueil des prompts — ia_prompts/

Tous les prompts du projet sont documentés dans :
```
~/projet_zeta/scripts/ia_prompts/ia_prompts_riemann_lab_complet.md
```

Contient 14 sessions (mai → juin 2026) + 10 leçons sur les prompts.
Versionné sur `Riemann_Lab_IA`.

**Pour ajouter un nouveau prompt :**
```bash
# Éditer le fichier
code ~/projet_zeta/scripts/ia_prompts/ia_prompts_riemann_lab_complet.md
# Ajouter la nouvelle session avec date + contexte + prompt complet
git add scripts/ia_prompts/
git commit -m "docs: ajout prompt SESSION_DATE"
git push origin Riemann_Lab_IA
```

---

---

## 📋 Leçons sessions 09–10 juin 2026

### Runs de calcul

- **Toujours utiliser `nohup` + `printf "T\nO\n"`** pour les runs interactifs en arrière-plan.
  Sans nohup, SIGHUP tue le process dès déconnexion du terminal → 0 résultats.
  ```bash
  printf "100000\nO\n" | nohup python src/calculs/optimisation/compute_zeros_v4_1.py \
    > logs/run_T100000.log 2>&1 &
  ```
- **Ne jamais fermer VS Code** pendant un run sans nohup préalable.
- **`zeta_turbo_on.sh` obligatoire** avant tout run (règle `CLAUDE.md`) → +15–30 % calcul.
- **`zeta_turbo_off.sh` obligatoire** après tout run → restaure CPU governor + swappiness.

### Gestion du contexte Claude

- **`/clear`** quand le contexte > 50k tokens ou que le cache est COLD (ralentissement notable).
- **Vérifier quota 7j** avant session longue : `ccusage` (coût/session, limite API).
- Contexte > 40 % → ne pas lancer de runs T > 300.

### STEP adaptatif — règle obligatoire depuis 2026-06-10

Espacement moyen entre zéros ≈ $2\pi / \ln(t/2\pi)$ :

| Tranche t | Espacement moyen | STEP imposé |
|---|---|---|
| t < 10 000 | ~0.39 | 0.1 |
| 10 000 ≤ t < 50 000 | ~0.28 | 0.05 |
| t ≥ 50 000 | ~0.21 | 0.02 |

STEP=0.1 fixe à T=100 000 → 356 zéros manquants (0.26 %). Fix dans `step_pour_t()`.

### Segmentation 1/√t

Sans segmentation adaptative, Worker 3 ([75k, 100k]) traite ~2× plus de zéros que Worker 0
([14, 25k]) → déséquilibre de charge. Solution : `_partitionner_adaptatif()` dans
`compute_zeros_v4_1.py` (partition uniforme de l'axe √t).

### GPU nvrtc (GTX 960M / CUDA 12.x)

`nvrtc: error: invalid value for --gpu-architecture` → sm_50 déprécié dans CUDA 12.x.
Fix dans `riemann_siegel_batch.py` : détecter `cc_major < 6` → basculer automatiquement
sur CPU numpy. Aucune perte de performance (Z_batch numpy est déjà très rapide).

### Suivi de progression

- Log progression 1000 zéros par worker : `[Worker X] zéro #N à t=... — Xs`
- `tail -f logs/run_T*.log` toutes les 5 min pour vérifier l'avancement.
- `htop` → F4 + `compute_zeros` pour filtrer les processus.

---

---

## 🗂️ Gestion des sessions Claude Code

### Un seul fichier session ou plusieurs ?

- Un seul fichier `session_YYYYMMDD_HHMM.md` par session Claude Code (créé via `capture.sh`)
- Ne pas créer plusieurs fichiers pour la même session
- Ne pas confondre avec Handoff.md (état courant) et JOURNAL.md (historique)

### Règle des 3 fichiers de suivi

| Fichier | Rôle | Localisation |
|---|---|---|
| `Handoff.md` | État courant — "REPRENDRE ICI" | `handoff/` local, hors git |
| `JOURNAL.md` | Historique daté append-only | wiki master |
| `session_YYYYMMDD_HHMM.md` | Log automatique Claude Code | `claude-traitement-journalier/` local |

### Règles de session

- Toujours faire `/clear` entre deux sessions longues (évite l'auto-compact intempestif)
- Vérifier quota `ccusage` avant session longue (5h glissantes)
- Cache COLD = relancer depuis `~/projet_zeta/` avec `zeta` pour recharger les CLAUDE.md
- Un `/clear` ne supprime PAS les CLAUDE.md — ils sont relus automatiquement
- Ne pas lancer T > 300 si contexte > 40 % (règle `CLAUDE.md` racine)

### Règle STEP adaptatif — formule canonique

$$\text{STEP}(t) = \max\!\left(0.05,\; \min\!\left(0.5,\; \frac{2\pi}{3\ln(t/2\pi)}\right)\right)$$

Valeurs repères : 0.5 à $t=100$ · 0.33 à $t=10\,000$ · 0.22 à $t=100\,000$.
STEP fixe → zéros manquants dès que $\text{STEP} > \delta(t)/2$ (commit `d2f62c1`).
Ne pas revenir à un STEP fixe sans raison documentée.

### Règle estimation vitesse par tranche

Avant de lancer un run long, estimer la durée par worker :

$$T_{\text{worker}} \approx \frac{N(T_j) - N(T_{j-1})}{v_j} \quad \text{avec} \quad v_j \approx 40\,/\!\sqrt{T_j/10\,000} \;\text{z/s}$$

Vérifier la vitesse à 5 min — si $< 10$ z/s → reporter immédiatement (régresssion STEP).

### Surveiller un run long avec Monitor Claude Code

Pour les runs > 30 min, lancer Monitor sur le fichier log pour être notifié :

```bash
# Dans Claude Code, lancer Monitor sur le log du run :
# Monitor file = calculs/run_T100k_*.log
# Pattern : "Turing-Backlund"
# Timeout : 3600000 (1h max par tranche)
```

Si le Monitor se déclenche (pattern trouvé) → **stopper immédiatement toute autre tâche**
et traiter le résultat du run en priorité.

### /clear avant prompt v6

Toujours lancer `/clear` avant de démarrer un prompt de développement majeur (v6, nouveau levier).
Raison : les prompts v5/v4.1 génèrent ~200k tokens de contexte ; l'auto-compact à 80 %
peut supprimer des contraintes critiques (seuil Illinois, formule N(T), règle STEP).
Conséquence : erreurs silencieuses, pas de message d'erreur explicite.

---

## ⚡ Règle précision mpfr — leçon v7 (11 juin 2026)

**Contre-intuition prouvée :** `prec=64 bits` (1 limb machine) est **×16 plus rapide** que
`prec=116 bits` (2 limbs), parce qu'un seul limb active les routines SIMD spécialisées de
libmpfr (AVX2 sur x86_64). Deux limbs cassent le SIMD et multiplient le coût par 10 à 20.

| Précision | Limbs | SIMD | ms/appel t~5k |
|---|---|---|---|
| 32 bits | 1 | OUI — mais trop imprécis | ~0.7 ms |
| **64 bits** | **1** | **OUI — AVX2** | **~1.5 ms** |
| 116 bits | 2 | NON | ~23.5 ms |
| 128 bits | 2 | NON | ~24 ms |
| 170 bits | 3 | NON | ~35 ms |

$$N_{\text{limbs}} = \left\lceil\frac{\text{prec}}{64}\right\rceil \qquad t_{\text{appel}} \approx 1.47 \times N_{\text{limbs}}^2 \text{ ms}$$

**Règle :** ne jamais supposer que la précision « raisonnable » est optimale — **mesurer**.
La théorie (nombre de termes RS) prédisait ×4.6 pour v7 ; la réalité (précision) a donné ×16.

**Conséquence pour la v8 :** tester `prec_fast` ∈ {32, 48, 64, 80, 96} bits empiriquement
avant toute décision d'architecture.

---

## 📐 Règle benchmark avant implémentation (leçon v7)

**TÂCHE 0 obligatoire à chaque nouvelle version** : mesurer les paramètres clés sur T=5k
(run court) AVANT de modifier l'architecture.

```python
# Benchmark minimal : 1 appel illinois_refine pour chaque prec candidate
for prec in [32, 48, 64, 80, 96, 116, 128]:
    t0 = time.time()
    for _ in range(100):
        illinois_refine_adaptive(a, b, fa, fb, prec_fast=prec, ...)
    print(f"prec={prec:3d} bits : {(time.time()-t0)*10:.2f} ms/appel")
```

| Règle | Raison |
|---|---|
| Mesurer AVANT de modifier l'architecture | v7 : l'intuition théorique (termes RS) était fausse |
| Calibrer `iter_switch` empiriquement | Pas a priori — valeur optimale dépend du hardware |
| Séparer tests précision ET nombre de termes | Une seule variable à la fois |
| Ne pas confier à la théorie le rôle du benchmark | La théorie confirme, le benchmark décide |

**Leçon v7 chiffrée :** hypothèse = ×4.6 via N_termes, réalité = ×16 via prec_fast=64 bits.
Sans benchmark, v7 n'aurait jamais trouvé le bon levier.

---

## 🚦 Workflow de validation avant intégration en production (leçon v16, 08/08/2026)

**Contexte :** remplacement de `arb_fpwrap_cdouble_hardy_z` par `acb_dirichlet_hardy_z`
dans `illinois_arb.c` — un changement touchant le cœur du calcul de production. Le
déroulé de cette session illustre un protocole réutilisable pour tout changement
similaire (nouvelle dépendance, nouveau mécanisme, gain mesuré mais pas encore prouvé
à l'échelle réelle).

### Les étapes, dans l'ordre

1. **Chiffrer avant de proposer** — `perf record` réel, pas une intuition. Le vrai
   goulot (escalade de précision `arb_fpwrap` visant ~1e-16, surdimensionné vs le
   besoin réel 1e-12) n'apparaît qu'en lisant le code source de la dépendance, pas en
   devinant depuis la doc.
2. **Prototyper en isolation stricte** — nouveau fichier `.c`/`.so` distinct, nouveau
   script Python distinct, **jamais toucher au fichier de production** pendant cette
   phase. `git status` vérifié vide sur les fichiers de production à chaque étape.
3. **Valider sur un run réel modeste** avant de demander une décision — pas seulement
   des micro-benchmarks synthétiques (300 brackets isolés a *surestimé* le gain réel
   de ×5,75 à ×1,98 mesuré sur un vrai run T=10000 — la part relative de la phase
   optimisée n'est pas la même en isolation qu'en contexte réel).
4. **Poser explicitement la question de décision** à hprzeta (« décide si on intègre »)
   plutôt que d'intégrer unilatéralement dès qu'un gain est mesuré — un changement de
   dépendance (ici : headers FLINT vendorisés) engage le projet au-delà du gain de
   vitesse.
5. **Intégrer en suivant la convention établie du projet**, pas une convention
   inventée pour l'occasion — ici, fichier `.c` modifié en place + nouveau
   `compute_zeros_vN.py` (le pattern déjà utilisé pour v12→v15).
6. **Revalider au protocole standard AVANT de déclarer la version adoptée** — le
   critère d'acceptation d'une nouvelle version Phase C dans ce projet est fixe
   (T=100k, Turing COMPLET, LMFDB 20/20 — voir `STACK.md`), pas le run modeste de
   l'étape 3. Le gain mesuré à grande échelle a d'ailleurs été *meilleur* que celui du
   run modeste (×2,75 à T=100k vs ×1,98 à T=10000) — les deux sens d'écart sont
   possibles, d'où l'intérêt de ne jamais sauter cette étape.

**Pourquoi ça compte :** sans les étapes 2-3, un gain synthétique aurait pu être
intégré directement en production sans preuve qu'il tient à l'échelle réelle — dans
un sens comme dans l'autre. Le coût de ce protocole (deux runs de validation au lieu
d'un) est negligeable comparé au risque d'un remplacement de production non prouvé.

---

## ⚙️ OpenBSD/pf et réseau — Pièges et leçons (2026-06-15)

> Leçons tirées de la configuration du bastion VPN PC4 (`zeta-secure`, OpenBSD 7.9/i386).

### SLAAC IPv6 sous OpenBSD — ne pas confondre avec Linux

**`net.inet6.ip6.accept_rtadv` n'existe pas sous OpenBSD** (sysctl Linux uniquement).
Sous OpenBSD, SLAAC s'active dans `/etc/hostname.<interface>` :
```
inet6 autoconf
```
Relancer avec `sh /etc/netstart <interface>` (il n'y a pas d'`ifup` sous OpenBSD).

### Règle pf — types ICMPv6 corrects

```pf
pass in on $ext_if inet6 proto icmp6 icmp6-type {routeradv, neighbradv, neighbrsol, redir}
```

⚠️ Le type correct est **`neighbrsol`**, pas `neighbrsolicit` (nom long Linux, invalide sous pf).
Sans cette règle, `block in` par défaut bloque les Router Advertisements → aucune adresse
globale SLAAC ne s'obtient malgré `inet6 autoconf` dans `/etc/hostname.re0`.

### Diagnostic CGNAT — piège classique

**Ne pas tester depuis l'intérieur du réseau** avec `curl ifconfig.me` ou `curl ip6.me` :
le résultat peut être trafiqué par le routeur. Pour savoir si l'IP est derrière CGNAT :
→ Comparer avec l'**IP WAN affichée par la box** (interface admin `192.168.1.1`).
Si l'IP WAN de la box est en `10.x.x.x`, `100.64-127.x.x.x` ou autre RFC1918 : CGNAT.

### WireGuard mobile — config via QR code

```bash
# Générer un QR code lisible par l'app Android/iOS WireGuard
qrencode -t ansiutf8 < /etc/wireguard/peer_telephone.conf
```
Import direct dans l'app sans saisie manuelle. `qrencode` : `apt install qrencode` (Linux)
ou `pkg_add qrencode` (OpenBSD).

### WireGuard — diagnostic `rx=0` persistant côté client

`rx=0` persistant + `tx` croissant = les paquets partent du client mais n'arrivent pas.
Ne pas chercher du côté du client — le pare-feu intermédiaire bloque.
→ Vérifier **à la fois** :
1. Règles `pf` sur PC4 (port UDP 51820 en `pass in`).
2. Section **"Réseau v6"** de la box SFR (Sécurité → Accès → Réseau v6) : distincte
   du NAT/redirection IPv4, vide par défaut = tout trafic IPv6 entrant bloqué.

### SSH via agent — "Too many authentication failures"

Si `ssh` échoue avec "Too many authentication failures" : l'agent SSH propose trop de
clés au serveur avant la bonne. Forcer la clé correcte :
```bash
ssh -o IdentitiesOnly=yes -i ~/.ssh/zeta_cluster user@host
```
Ajouter dans `~/.ssh/config` pour l'alias concerné :
```
IdentityFile ~/.ssh/zeta_cluster
IdentitiesOnly yes
```

---

### Diagnostic cross-machine — bibliothèques partagées (.so)

Quand un `.so` se comporte différemment sur PC1 et PC2, utiliser ce protocole en 4 commandes :

```bash
# 1. Sources identiques ?
diff <(cat local/scan_arb.c) <(ssh pc2 "cat ~/projet_zeta/.../scan_arb.c")

# 2. Symboles exportés
nm -D scan_arb.so | grep " T "          # fonctions publiques uniquement

# 3. Dépendances réelles (bibliothèques liées)
ldd scan_arb.so | grep -E 'arb|flint|not found'

# 4. Paquets installés
dpkg -l | grep -E 'flint|arb'           # Debian/Ubuntu
# ou sur OpenBSD : pkg_info | grep flint
```

**Pièges courants :**
- `ldd | grep arb` retourne exit 1 si aucune correspondance → pas forcément une erreur, peut vouloir dire que la lib n'utilise pas arb (normal pour `scan_arb.so` qui est C pur).
- `nm -D` n'exporte pas `scan_arb_hardy_z` : normal si la fonction n'est pas dans le source.
- `python-flint` (pip) ≠ `libflint-arb2` (apt) : le wrapper Python cherche `python_flint.libs/libflint-*.so*` dans site-packages. Même si `libflint-arb2` est installé système, `ARB_DISPONIBLE=False` si python-flint est absent.

### Diagnostic ctypes — signature incorrecte silencieuse

En Python ctypes, passer trop peu d'arguments ne lève **pas** d'exception — comportement indéfini C (valeurs parasites sur la pile), résultat souvent 0 ou crash aléatoire.

```python
# ❌ Bug silencieux : 2 POINTER au lieu de 4 → retourne 0
lib.scan_zeros_arb.argtypes = [ctypes.c_double]*3 + [ctypes.POINTER(ctypes.c_double)]*2 + [ctypes.c_int]
n = lib.scan_zeros_arb(100.0, 200.0, 0.3, a, b, 200)  # fa, fb manquants !

# ✅ Correct : vérifier la signature dans le .c avant d'écrire argtypes
lib.scan_zeros_arb.argtypes = (
    [ctypes.c_double] * 3 +
    [ctypes.POINTER(ctypes.c_double)] * 4 +  # brackets_a, brackets_b, fa, fb
    [ctypes.c_int]
)
```

**Règle :** toujours compter les arguments dans le `.c` source et les comparer au `argtypes` Python avant tout test.

### Seuil T_SEUIL_PETIT_T — calibrage par N_RS

`scan_arb` (Z_double RS + C0+C1) est fiable seulement si N_RS ≥ 3. En-dessous, les brackets peuvent être décalés de 0.01-0.05 et provoquer des erreurs de convergence Illinois.

| Range t | N_RS | Comportement |
|---|---|---|
| [14, 20) | 1 | θ(t) asymptotique invalide → mpmath obligatoire |
| [20, 57) | 2 | Brackets scan_arb potentiellement décalés → mpmath |
| [57, 100) | 3 | Fiable à t ≥ 65 (confirmé empiriquement LMFDB T=1000) |
| [100, 157) | 3-4 | Fiable |
| ≥ 157 | ≥ 5 | Très fiable |

**v13 : `T_SEUIL_PETIT_T = 65`** — compromis validé : 20/20 LMFDB, 52 z/s sur PC2 (×8.1 vs v12).

**Piège re-évaluation fa/fb :** filtrer les brackets spurieux avec `if fa*fb >= 0: continue` élimine aussi les vrais zéros dont scan_arb a placé le bracket au mauvais endroit — le vrai bracket adjacent est lui aussi manqué. Ne pas re-évaluer après coup ; utiliser arb_hardy_z dès la détection (chemin mpmath_petit_t).

---

## Distribution calcul multi-machine (zeta_distribute.py)

*Leçon session 2026-06-17 — Distribution PC1+PC2 T=100k validée.*

- **pip3 install X --break-system-packages** (Debian 12, PEP 668) — pip3 système bloque l'install sans flag explicite. `--user` peut marcher mais les paquets vont dans `~/.local/lib/` qui peut ne pas être dans PYTHONPATH si le script est lancé via SSH sans shell interactif. Vérifier avec `python3 -c "import sys; print(sys.path)"`.
- **Toujours vérifier ARB_DISPONIBLE avant benchmark cross-machine** — un `ARB_DISPONIBLE=False` sur PC2 multiplie par ×100 le temps de la zone [14,65] (mpmath.siegelz au lieu de Arb).
- **Marge pivot PC2 : −15%** — compense overhead SSH (~5 s de setup) + CPU plus lent + swap potentiel. `N_pivot = N_total - int(N_pc2_eq * 0.85)`. Marge −5% trop faible (PC2 finissait 20% après PC1).
- **dry-run obligatoire avant vrai run** — `python scripts/zeta_distribute.py T --dry-run` affiche la segmentation et les durées prévues sans lancer le calcul.
- **Surplus zéros aux bords de segment = normal** — chevauchement de ±0.5 entre workers internes crée des doublons. Déduplication `tolerance=0.01` suffit. Turing COMPLET (0 manquant) est le vrai critère.
- **PC2 finit avant PC1 = bon signe** — signifie que la marge est efficace et que l'agrégation Turing peut démarrer dès que PC1 termine. Si PC2 finit après → augmenter la marge.
- **PYTHONPATH cross-machine** — sur PC2 sans venv, les modules sont à plat dans `src/calculs/optimisation/`. Passer `export PYTHONPATH=.../src/calculs/optimisation` dans la commande SSH, pas `src/`.
- **Nom CSV v13** — convention : dossier `v13_T{T_MIN:.0f}_{T_MAX:.0f}_{horodatage}/`, CSV `zeros_v13_T{T_MAX:.0f}_{horodatage}.csv` (T_MAX seul dans le nom du CSV, pas T_MIN).

---

## Maintenance périodique — tokens expirés / reconnexions (23 juin 2026)

### Reconnexion Claude Code (`/login`)

Quand la session Claude Code se déconnecte (token expiré), relancer l'authentification
depuis le terminal :

```
/login
```

Choisir **Claude account with subscription**, puis ouvrir `platform.claude.com` dans le
navigateur, récupérer le code affiché et le coller dans le terminal pour valider la
reconnexion.

> 💡 Comme pour `gh auth status` (Guide-Git-GitHub.md §23), si Claude Code répond de façon
> anormale en début de session (erreurs d'auth, refus d'outil), vérifier d'abord l'état de
> connexion via `/login` avant de chercher un autre bug.

### Mise à jour des userPreferences (claude.ai)

Les instructions personnalisées du compte web claude.ai (distinctes de `~/.claude/CLAUDE.md`,
qui ne s'applique qu'à Claude Code) se gèrent depuis :

```
claude.ai → Settings → Général → Instructions pour Claude
```

Le 23 juin 2026, l'ancien prompt présent dans ce champ était devenu obsolète (référençait
un contexte de session périmé) et a été remplacé par une version courte et à jour. À
recontrôler périodiquement — ce champ n'est pas synchronisé avec `~/.claude/CLAUDE.md` et
peut diverger silencieusement si l'un des deux est mis à jour sans l'autre.

---

*Auteur : hprzeta · Mise à jour : 11 juin 2026 · 15 juin 2026 (§ OpenBSD/pf) · 17 juin 2026 (§ diagnostic cross-machine, ctypes, T_SEUIL) · 23 juin 2026 (§ Maintenance périodique — tokens expirés) · 8 août 2026 (§ Workflow de validation avant intégration production — leçon v16) · ~925 lignes*
