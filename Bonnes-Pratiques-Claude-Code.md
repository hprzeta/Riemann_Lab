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

## ⚠️ Claude Code modifie les fichiers sans permission (leçon 3 juin 2026)

### Ce qui s'est passé
Claude Code a modifié `compute_zeros_v4_1.py` de sa propre initiative pendant un run,
sans demander : remplacement `Z_batch` → `Z_vect_correct`, refactoring `findroot` bracketé.
Les changements étaient mathématiquement corrects, mais non demandés. Il allait ensuite
committer directement (`git commit`) — on a stoppé avec **`2. No`**.

### Règle obligatoire — ajouter dans tous les `CLAUDE.md`
```markdown
## ⛔ RÈGLE ABSOLUE — ne jamais modifier le code sans permission explicite
- NE PAS éditer, "corriger" ou "améliorer" un fichier .py de ta propre initiative.
- Si tu penses qu'un fix est nécessaire : DÉCRIS-le et DEMANDE avant d'éditer.
- Pour les tâches d'exécution : exécuter UNIQUEMENT, sortie brute, zéro modification.
- Toute modification → annoncer + montrer le diff → attendre validation avant commit.
- NE PAS committer sans validation explicite de l'utilisateur.
```
→ À placer dans : `~/.claude/CLAUDE.md` (global) ET `~/projet_zeta/CLAUDE.md` (projet)
ET `src/calculs/optimisation/CLAUDE.md` (local Phase C).

### Comment réagir si Claude Code a déjà modifié
1. **Ne pas committer** → répondre `2. No` au prompt git.
2. `git diff src/...fichier.py` → lire tous les changements.
3. Évaluer chaque modif : justifiée ? → garder. Injustifiée ? → `git checkout -- fichier`.
4. Committer manuellement avec un message explicite.

### Timeout 5 min sur les runs longs
L'agent Claude Code coupe les process après **5 min**. Pour les runs T≥1000 (~10 min) :
```bash
# Lancer HORS agent Claude Code, dans un vrai terminal :
printf "1000\nO\n" | python compute_zeros_v4_1.py 2>&1 | tee /tmp/run.log
grep -A 8 "PROFIL PHASES" /tmp/run.log
```
- `printf` alimente les `input()` automatiquement.
- `tee` sauvegarde la sortie complète (y compris `[PROFIL PHASES]`).
- En cas de timeout agent : le log sur disque (`calculs/*/execution_*.log`) existe,
  mais `[PROFIL PHASES]` est console-only → relancer avec `tee`.

### Claude Code lit le mauvais Handoff
Claude Code lit `Riemann_Lab.wiki/Handoff.md` (ancien), pas la branche `session`.
→ Son contexte est potentiellement périmé. Toujours lui dire explicitement :
*« Lis le Handoff depuis la branche session : `git show session:Handoff.md` »*
ou colle le contenu directement dans le prompt.

### Rapport de vitesse sans run réel = fabrication
Si Claude Code annonce une vitesse (ex. « 62.91 z/s ») sans avoir vu le `[PROFIL PHASES]`
ou sans run complet → c'est une **estimation basée sur le code**, pas une mesure.
**Ne jamais committer sur la foi d'un chiffre annoncé par l'agent sans capture d'écran.**

---

*Auteur : hprzeta · Mise à jour : 3 juin 2026 — ~410 lignes*
