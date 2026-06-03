# 🧭 Guide Git & GitHub — projet_zeta

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
*Guide personnel — hprzeta / projet_zeta — mis à jour le 1ᵉʳ juin 2026*

---

## 🌿 Branche orpheline `session` — versionner Handoff sans polluer le code (3 juin 2026)

### Pourquoi
`Handoff.md` est un doc de session (état courant, remplacé à chaque fin de session).
Il ne doit **jamais** être sur les branches de code (IA/C/main/Test) — risque d'être
committé par accident avec `git add -A`. Mais on veut quand même un historique Git.
Solution : **branche orpheline** (aucun ancêtre commun → jamais mergeable par erreur).

### Créer la branche `session` (une seule fois — déjà fait)
```bash
cd ~/projet_zeta/
git checkout --orphan session
git rm -rf . >/dev/null 2>&1          # vide l'index, garde le working dir
cp ~/Téléchargements/Handoff.md Handoff.md
git add Handoff.md
git commit -m "session: handoff <date>"
git push origin session
git checkout Riemann_Lab_C
```

### Mettre à jour le Handoff en fin de session
```bash
git checkout session
cp ~/Téléchargements/Handoff.md Handoff.md    # ou git show session:Handoff.md > ... puis éditer
git add Handoff.md && git commit -m "session: handoff $(date +%Y-%m-%d)"
git push origin session
git checkout Riemann_Lab_C
```

### Ignorer Handoff.md sur toutes les branches de code
```bash
# Vérifier le chemin exact (avant tout git rm --cached) :
git ls-files | grep -i handoff    # retourne le chemin EXACT avec casse

# Puis pour chaque branche :
for br in Riemann_Lab_C Riemann_Lab_IA main Riemann_Lab_Test; do
  git checkout "$br"
  git rm --cached "chemin/exact/vu/ci-dessus"
  grep -qxF "**/Handoff.md" .gitignore || echo "**/Handoff.md" >> .gitignore
  git add .gitignore
  git commit -m "chore: Handoff.md hors suivi (canonique = branche 'session')"
  git push origin "$br"
done
git checkout Riemann_Lab_C
```

### ⚠️ Pièges rencontrés
- **`git rm --cached Handoff.md` (nom seul) ne trouve rien** si le fichier est dans
  un sous-dossier. Utiliser `git ls-files | grep -i handoff` pour voir le chemin exact.
- **`2>/dev/null` masque les erreurs** → ne pas l'utiliser dans les boucles de diagnostic.
- **`**/Handoff.md`** ignore le fichier à tous les niveaux (racine + sous-dossiers).
  Préférer ce motif à `Handoff.md` (racine seulement).

### Vérification
```bash
git checkout Riemann_Lab_C >/dev/null 2>&1; echo -n "C      : "; git ls-files | grep -ci handoff
git checkout session       >/dev/null 2>&1; echo -n "session: "; git ls-files | grep -ci handoff
git checkout Riemann_Lab_C >/dev/null 2>&1
# Attendu : C : 0 / session : 1
```

### Lire le Handoff sans changer de branche
```bash
git show session:Handoff.md                    # affiche dans le terminal
git show session:Handoff.md > Handoff.md       # récupère dans le working dir
```

---
*Guide personnel — hprzeta / projet_zeta — mis à jour le 3 juin 2026 — ~520 lignes*
