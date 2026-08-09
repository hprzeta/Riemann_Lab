# 🧭 Guide Git & GitHub — projet_zeta

> **Fichier :** Guide-Git-GitHub.md · **Dossier :** wiki racine (`~/projet_zeta/Riemann_Lab.wiki/`)
> **Branche :** master · **Auteur :** hprzeta · **MAJ :** 2026-06-21

> Principe fondamental : **tout se fait en LOCAL, puis on pousse vers GitHub.**
> Ne jamais modifier directement sur GitHub (sauf urgence).

---

## 🎨 Tableau d'icônes pour tes titres

| Icône | Idée d'usage |
|-------|-------------|
| 🧭 | Navigation, guide, workflow |
| 🔬 | Tests, résultats, analyse |
| 📐 | Théorie, mathématiques |
| 📊 | Graphiques, données, stats |
| 🧮 | Calculs, scripts |
| 📝 | Notes, documentation |
| 🗂️ | Organisation, structure |
| 🚀 | Lancement, déploiement |
| 🔧 | Configuration, maintenance |
| 🐛 | Bug, correction |
| ✅ | Validation, succès |
| ⚠️ | Avertissement |
| 📦 | Dépendances, packages |
| 🌿 | Branche Git |
| 🏷️ | Tag, version |
| 📌 | Point important |
| 🔗 | Lien, référence |
| 💡 | Idée, astuce |
| 🗒️ | Wiki, page |
| 🐙 | GitHub |

---

## 📋 Workflow de travail

```
Fichiers locaux  →  git add  →  git commit  →  git push  →  GitHub
git pull   →   tu travailles   →   git add   →   git commit   →   git push
```

---

## 1. 🚀 Créer un nouveau dépôt

### Sur GitHub d'abord
1. Aller sur [github.com](https://github.com) → **New repository**
2. Nommer le dépôt (ex: `projet_zeta`)
3. Cocher **Add a README**
4. Cliquer **Create repository**

### Puis cloner en local
```bash
cd ~/
git clone https://github.com/hprzeta/projet_zeta.git
cd projet_zeta
```

---

## 2. 📥 Cloner un dépôt existant

```bash
# Dépôt principal
git clone https://github.com/hprzeta/projet_zeta.git

# Wiki du dépôt
git clone https://github.com/hprzeta/projet_zeta.wiki.git
```

---

## 3. 📤 Pousser des fichiers

### Un dossier du projet (dépôt général)
```bash
cd ~/projet_zeta
git add src/tests/
git commit -m "docs: ajout interprétation test T40 — zéros ζ(s)"
git push
```

### Un fichier spécifique
```bash
cd ~/projet_zeta
git add src/tests/interpreation_test/T40zero/compute_zeros_zeta.py
git commit -m "feat: script calcul zéros ζ(s) T40"
git push
```

### Tout ce qui a changé
```bash
cd ~/projet_zeta
git add .
git commit -m "chore: mise à jour générale"
git push
```

### Page Wiki
```bash
cd ~/projet_zeta/Riemann_Lab.wiki
git add "🔬-Interprétation-des-résultats-de-tests.md"
git commit -m "docs: ajout interprétation des résultats de tests T40 ζ(s)"
git push origin master
```

---

## 4. 🔍 Contrôler l'état du dépôt

```bash
# Voir ce qui a changé / ce qui est prêt à committer
git status

# Voir l'historique des commits
git log --oneline

# Voir les différences avant d'ajouter
git diff

# Voir les branches existantes
git branch -a
```

---

## 5. 🌿 Travailler avec les branches

```bash
# Créer une nouvelle branche et basculer dessus
git checkout -b T500-zeros

# Voir sur quelle branche on est
git branch

# Basculer sur une branche existante
git checkout master

# Pousser une nouvelle branche vers GitHub
git push origin T500-zeros

# Fusionner une branche dans master (depuis master)
git checkout master
git merge T500-zeros

# Supprimer une branche locale après fusion
git branch -d T500-zeros
```

> 💡 **Bonne pratique :** une branche par expérience (ex: `T500-zeros`, `T1000-gue`, `refactor-illinois`)

---

## 6. ✏️ Renommer un fichier

```bash
cd ~/projet_zeta
git mv ancien_nom.py nouveau_nom.py
git commit -m "refactor: renommage ancien_nom → nouveau_nom"
git push
```

> ⚠️ Toujours utiliser `git mv` plutôt que `mv` seul — Git garde ainsi l'historique du fichier.

---

## 7. 🔙 Retrouver / Annuler

```bash
# Annuler les modifications d'un fichier non encore commité
git checkout -- nom_du_fichier.py

# Annuler le dernier commit (en gardant les fichiers)
git reset --soft HEAD~1

# Voir un ancien commit
git show abc1234

# Revenir à une version antérieure d'un fichier
git checkout abc1234 -- nom_du_fichier.py
```

---

## 8. 🏷️ Créer une version (tag)

```bash
# Créer un tag pour marquer une étape importante
git tag v0.1.0 -m "Première version — zéros T40 validés"

# Pousser le tag vers GitHub
git push origin v0.1.0
```

> 💡 **Suggestion pour projet_zeta :** tagger chaque palier validé (`v0.1-T40`, `v0.2-T500`, etc.)

---

## 9. 🗒️ Créer une nouvelle page Wiki

```bash
cd ~/projet_zeta/Riemann_Lab.wiki

# Créer le fichier en local
touch "📐-Partie-2-Méthode-Illinois.md"
# … éditer le fichier …

git add "📐-Partie-2-Méthode-Illinois.md"
git commit -m "docs: ajout page méthode Illinois"
git push origin master
```

---

## 10. 🐛 Créer un Issue (ticket)

Les Issues se créent directement sur GitHub :

1. Aller sur `github.com/hprzeta/projet_zeta` → onglet **Issues**
2. Cliquer **New issue**
3. Titre : ex. `Zéro manqué quand STEP=0.1 et T_MAX=100`
4. Description : reproduire le problème, coller le log
5. Assigner un label : `bug`, `enhancement`, `documentation`...

> 💡 Dans un commit, écrire `fix #12` fermera automatiquement l'issue n°12.

---

## 11. 🔄 Mettre à jour le dépôt local (récupérer les changements GitHub)

```bash
cd ~/projet_zeta
git pull

# Pour le wiki
cd ~/projet_zeta/Riemann_Lab.wiki
git pull origin master
```

---

## 12. 📦 Tags de commit (Conventional Commits)

| Tag | Signification | Exemple |
|-----|--------------|---------|
| `feat` | Nouvelle fonctionnalité | `feat: calcul zéros jusqu'à T500` |
| `fix` | Correction de bug | `fix: zéro manqué STEP trop grand` |
| `docs` | Documentation | `docs: ajout interprétation T40 ζ(s)` |
| `refactor` | Réécriture sans changer le comportement | `refactor: simplification Illinois` |
| `test` | Ajout/modification de tests | `test: vérification T40 vs LMFDB` |
| `chore` | Maintenance, config | `chore: mise à jour mpmath` |
| `style` | Mise en forme uniquement | `style: reformatage compute_zeros.py` |
| `perf` | Amélioration des performances | `perf: réduction temps de balayage` |
| `revert` | Annulation d'un commit | `revert: annulation refactor Illinois` |

---

## 13. 🆘 Commandes de secours

```bash
# Voir ce que Git sait de mes dépôts distants
git remote -v

# Réparer un push refusé (si GitHub est en avance sur local)
git pull --rebase
git push

# Vider le cache Git (si un fichier ignoré persiste)
git rm -r --cached .
git add .
git commit -m "chore: nettoyage cache Git"
```

---

## 14. 🎯 Flux de travail concret pour tester

```bash
# 1. Basculer sur la branche de test
git checkout Riemann_Lab_Test

# 2. Récupérer le code actuel de Riemann_Lab_IA
git merge Riemann_Lab_IA

# 3. Tu testes, tu modifies, tu casses...
python zeta_test.py

# 4. Si ça marche → tu ramènes dans Riemann_Lab_IA
git checkout Riemann_Lab_IA
git merge Riemann_Lab_Test

# 5. Si ça ne marche pas → aucun problème
# Riemann_Lab_IA est intact, tu recommences
```
---

## 15. Réflexe à avoir — début de chaque session
```
bash
# 1. Aller dans ton projet
cd ~/projet_zeta

# 2. Vérifier où tu es
git branch          # l'étoile * = branche active

# 3. Basculer si besoin
git checkout Riemann_Lab_IA

# 4. Récupérer les derniers changements
git pull origin Riemann_Lab_IA

# 5. Tu travailles...

# 6. Fin de session → pousser
git add .
git commit -m "feat: ..."
git push origin Riemann_Lab_IA
```
---

## 16. Synchroniser wiki distant ↔ local
```
bash

cd ~/projet_zeta/Riemann_Lab.wiki

# Voir ce qui diffère entre local et distant
git status
git log --oneline -5

```
---

## 17. Récupérer le distant vers le local (GitHub → local)
```
bash

cd ~/projet_zeta/Riemann_Lab.wiki

# Télécharger et fusionner les changements distants
git pull origin master

```
---

## 18. Envoyer le local vers GitHub (local → GitHub)
```
bash

cd ~/projet_zeta/Riemann_Lab.wiki

# Voir ce qui a changé
git status

# Ajouter tout
git add .

# Committer
git commit -m "docs: synchronisation wiki"

# Pousser
git push origin master

```
---

## 19. Copier main sur Riemann_Lab_IA :
```
bash
git checkout Riemann_Lab_IA
git reset --hard origin/main
git push origin Riemann_Lab_IA --force

```
---


## 20. Renommer Riemann_Test → Riemann_Lab_Test
```
bash
git branch -m Riemann_Test Riemann_Lab_Test
git push origin --delete Riemann_Test
git push origin Riemann_Lab_Test
git branch --set-upstream-to=origin/Riemann_Lab_Test Riemann_Lab_Test

# Basculer sur Riemann_Lab_IA
git checkout Riemann_Lab_IA
```
---

## 20. Créer la branche locale manuellement

```
bash
# Créer Riemann_Test localement depuis main
git checkout main
git checkout -b Riemann_Test

# La pousser sur GitHub avec un premier commit
git push -u origin Riemann_Test

# Vérifier
git branch -a

```
---

## 21. ⚠️ Pièges vécus — réflexes de vérification (session 1ᵉʳ juin 2026)

### 🐛 Le piège du placeholder dans une commande copiée
Quand tu colles un bloc de commandes fourni par une IA, repère les **placeholders**
du type `~/chemin/vers/fichier.md`. Collé tel quel :
```bash
cp ~/chemin/vers/Handoff.md .     # ÉCHOUE : "Aucun fichier ou dossier de ce nom"
```
Le piège est que la suite devient une **chaîne de non-opérations silencieuse** :
`cp` échoue → `git add` ne trouve rien de neuf → `git commit` répond *« aucune
modification »* → `git push` répond *« Everything up-to-date »*. Aucune erreur
bloquante, mais **rien n'a été poussé.**

Réflexe : remplacer le placeholder par le **vrai dossier** (`~/Téléchargements/`),
puis vérifier juste après le `cp` :
```bash
cp ~/Téléchargements/Handoff.md .
head -3 Handoff.md          # confirme que la BONNE version est bien là
```

### 🗑️ `git rm` ≠ `rm`
- `git rm fichier` ne marche **que sur un fichier suivi** (déjà committé).
  Sur un fichier non suivi → `fatal: ... ne correspond à aucun fichier`.
- Pour supprimer un fichier **non suivi** (jamais committé) : `rm fichier` tout court.

### 🔒 Un fichier non suivi n'est JAMAIS une page wiki
Le wiki GitHub ne sert que les fichiers **committés ET poussés** à la racine du
repo wiki. Un fichier listé en rouge sous *« Fichiers non suivis »* n'a jamais
quitté ta machine → **aucun risque « public »**, même s'il traîne dans le dossier wiki.

### 🔍 Vérifier AVANT de s'inquiéter d'un secret
Avant de paniquer sur un fichier « public », chercher d'abord un éventuel secret :
```bash
grep -iE "token|secret|key|password|ghp_|github_pat" fichier.md
```
Vide = aucun danger. Sinon → **secret exposé = secret mort → révocation immédiate**
(voir `Bonnes-Pratiques-Claude-Code.md`, section Sécurité).

### ✅ Toujours vérifier APRÈS un push
```bash
head -3 Handoff.md                      # la bonne version est-elle en place ?
git log --oneline -2 -- Handoff.md      # le commit attendu touche-t-il bien ce fichier ?
```

---

## 📋 Leçons sessions 09–10 juin 2026

### Handoff.md — local uniquement

`Handoff.md` est **local uniquement** (`~/projet_zeta/handoff/`), jamais dans le wiki,
jamais dans `docs/`. Vérifier l'absence de doublon :

```bash
ls ~/projet_zeta/docs/handoff/Handoff.md 2>/dev/null  # ne doit PAS exister
ls ~/projet_zeta/Riemann_Lab.wiki/Handoff.md 2>/dev/null  # ne doit PAS exister
```

### Lister fichiers modifiés par date

```bash
find . -name "*.md" -printf "%TY-%Tm-%Td %TH:%TM  %p\n" | sort -r | head -20
```

### Vérifier .gitignore sur CHAQUE branche

```bash
git check-ignore -v logs/*.log   # vérifier avant tout git add -A
```

Un fichier ignoré sur `main` peut ne pas l'être sur `Riemann_Lab_C`. Toujours vérifier
sur la branche active.

### Après un run : archiver immédiatement

```bash
# Créer dossier de résultat
mkdir -p calculs/vX_TYYY_YYYYMMDD_HHMMSS/
cp logs/run_T*.log calculs/vX_TYYY_YYYYMMDD_HHMMSS/
cp calculs/vX_TYYY_YYYYMMDD_HHMMSS/*.csv .  # copie de sécurité
```

---

### Surveiller un run long

Pour un run > 30 min, surveiller le processus et estimer la durée avant de lancer :

```bash
# Vérifier que le run est actif (toutes les 5–10 min)
ps aux | grep compute_zeros | grep -v grep

# Suivre les logs en direct
tail -f calculs/run_T100k_step_delta3_*.log | grep -E "Worker|Turing|zéros"

# Estimation durée restante par worker j (formule approximée)
# v_j ≈ 40 / √(T_j / 10000)  z/s
# durée ≈ (N(T_j) - N(T_{j-1})) / v_j   secondes
```

**Règle vitesse :** vérifier à 5 min après lancement. Si vitesse < 10 z/s → régression
STEP probable → tuer le run et diagnostiquer.

**Monitor Claude Code :** lancer Monitor sur le fichier log avec pattern `"Turing-Backlund"`.
Timeout max : 3 600 000 ms (1h). Si Monitor se déclenche → stopper toute tâche courante
et traiter le résultat du run en priorité.

```bash
# Exemple : run actif PID 328675, log run_T100k_step_delta3_20260610_1717.log
# Monitor déclenché → tail du log + validation Turing-Backlund :
tail -50 calculs/run_T100k_step_delta3_20260610_1717.log
```

---

## 22. 🔐 Authentification GitHub CLI (`gh`) et création de pull requests (session 21 juin 2026)

### Pourquoi authentifier `gh`

`gh` (GitHub CLI) permet de piloter GitHub depuis le terminal — créer des pull requests, gérer des issues, etc. — sans manipuler de token manuellement. C'est ce qui permet à Claude Code d'agir directement sur GitHub (ex. `gh pr create`) plutôt que de te renvoyer vers le site web.

### Authentification via device login

```bash
gh auth login
```

Répondre aux questions interactives :
1. `What account do you want to log into?` → **GitHub.com**
2. `What is your preferred protocol for Git operations?` → **HTTPS**
3. `Authenticate Git with your GitHub credentials?` → **Yes**
4. `How would you like to authenticate GitHub CLI?` → **Login with a web browser**

Le terminal affiche alors un **code à 8 caractères** (ex. `1272-E323`) et une URL :
```
https://github.com/login/device
```

Étapes côté navigateur :
1. Ouvrir cette URL
2. Se connecter au compte `hprzeta`
3. Entrer le code affiché dans le terminal
4. Sur la page **« Authorize GitHub CLI »**, vérifier les permissions demandées :
   - **Gists**
   - **Organizations** (lecture seule)
   - **Repositories** (publics + privés) ← **permission essentielle pour créer des PR**
5. Cliquer **Authorize github**

Le terminal se débloque automatiquement dès l'autorisation validée. Vérifier le résultat :
```bash
gh auth status
# ✓ Logged in to github.com account hprzeta (keyring)
# - Token scopes: 'gist', 'read:org', 'repo'
```

> ⚠️ **Le code expire après 1 minute.** S'il expire avant la validation côté navigateur, relancer simplement `gh auth login`.

### Créer une pull request avec `gh pr create`

Une fois authentifié, créer une PR directement depuis le terminal (sans passer par le formulaire web) :

```bash
gh pr create --base <branche_cible> --head <branche_source> \
  --title "docs(ops): titre court" \
  --body "Description de la PR"
```

**Prérequis :** la branche source (`--head`) doit déjà être poussée sur GitHub (`git push -u origin <branche>`).

`gh` signale au passage les fichiers non commités/untracked présents dans le répertoire de travail (`Warning: N uncommitted changes`) — c'est informatif, ça **n'empêche pas** la création de la PR.

Résultat : l'URL de la PR créée s'affiche directement, par exemple :
```
https://github.com/hprzeta/Riemann_Lab/pull/6
```

### Alternative manuelle (sans authentification `gh`)

Si `gh` n'est pas authentifié, `git push` d'une nouvelle branche affiche déjà un lien direct vers le formulaire de création de PR :

```
remote: Create a pull request for 'ma-branche' on GitHub by visiting:
remote:      https://github.com/hprzeta/Riemann_Lab/pull/new/ma-branche
```

Ouvrir ce lien dans un navigateur et remplir le formulaire GitHub manuellement (titre, description, branche cible).

---

## 23. 🔄 Maintenance périodique — tokens expirés (23 juin 2026)

### Symptôme

`gh` refuse une opération (push, `gh pr create`, etc.) en signalant que le token est expiré
ou invalide. Le token GitHub CLI a une durée de vie limitée et doit être renouvelé
périodiquement — ce n'est pas une anomalie, c'est attendu.

### Procédure de reconnexion

```bash
gh auth login
```

Répondre aux questions interactives (identique à la procédure §22) :
1. `What account do you want to log into?` → **GitHub.com**
2. `What is your preferred protocol for Git operations?` → **HTTPS**
3. `How would you like to authenticate GitHub CLI?` → **Login with a web browser**

Ouvrir l'URL affichée (`https://github.com/login/device`), entrer le code à 8 caractères,
se connecter au compte `hprzeta`, puis **Authorize github**.

Vérifier le résultat :
```bash
gh auth status
```

> 💡 **Réflexe avant toute session Git/GitHub :** si une commande `gh` échoue de façon
> inattendue, vérifier d'abord `gh auth status` avant de chercher un autre bug — un token
> expiré est la cause la plus fréquente et la plus rapide à corriger.

---
*Guide-Git-GitHub.md · wiki racine · branche master · hprzeta · MAJ 2026-06-23 · 632 lignes*
