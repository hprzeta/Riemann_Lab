# 🖥️ Guide VS Code & Codespaces — Bonnes pratiques

> Référence rapide pour le projet **Riemann_Lab**
> Environnement : GitHub Codespaces · VS Code · Python 3.12 · zeta_env

---

## 🎨 Couleurs des fichiers dans l'Explorateur

| Couleur | Signification | Action |
|---------|--------------|--------|
| ⬜ **Blanc** | Fichier propre — synchronisé avec Git | Rien à faire ✅ |
| 🟡 **Jaune** | Fichier **modifié** — changements non committés | `git add` + `git commit` |
| 🟢 **Vert** | Fichier **nouveau** — jamais commité | `git add` + `git commit` |
| 🔴 **Rouge** | Fichier **en conflit** — merge raté | Résoudre le conflit |
| ⚫ **Grisé** | Fichier ignoré par `.gitignore` | Normal, Git ne le suit pas |

---

## 🗂️ Les panneaux principaux

### Barre d'activité (colonne gauche)

| Icône | Panneau | Raccourci |
|-------|---------|-----------|
| 📄 | **Explorateur** — arbre des fichiers | `Ctrl+Shift+E` |
| 🔍 | **Recherche** — dans tout le code | `Ctrl+Shift+F` |
| 🌿 | **Source Control** — Git | `Ctrl+Shift+G` |
| 🧩 | **Extensions** | `Ctrl+Shift+X` |
| 🐛 | **Débogueur** | `Ctrl+Shift+D` |

### Panneau bas

| Onglet | Rôle |
|--------|------|
| **TERMINAL** | Terminal Linux — commandes bash/python |
| **PROBLÈMES** | Erreurs et warnings du code |
| **SORTIE** | Logs des extensions |
| **PORTS** | Serveurs locaux tunnelisés vers HTTPS |

---

## 🌿 Branches — réflexe de début de session

```bash
# 1. Vérifier sur quelle branche tu es
git branch          # l'étoile * = branche active

# 2. Basculer si besoin
git checkout Riemann_Lab_IA     # travail principal
git checkout Riemann_Lab_Test   # tests et expériences

# 3. Récupérer les derniers changements
git pull origin Riemann_Lab_IA
```

### Règle des 3 branches Riemann_Lab

| Branche | Quand l'utiliser |
|---------|-----------------|
| `Riemann_Lab_IA` ⭐ | Travail principal — code stable |
| `Riemann_Lab_Test` | Tests risqués — tu peux casser |
| `main` | Référence — touche peu |

---

## 🐍 Environnement virtuel zeta_env

```bash
# Activer à chaque session
source zeta_env/bin/activate
# Le prompt devient : (zeta_env) @hprzeta → ... ✅

# Installer les dépendances
pip install -r requirements/requirements_workspace.txt

# Vérifier que tout fonctionne
python -c "import numpy, scipy, mpmath, torch, matplotlib; print('✅ OK')"

# Désactiver en fin de session
deactivate
```

> ⚠️ **Toujours activer `zeta_env` avant de lancer un script Python !**

---

## ⚡ Raccourcis clavier essentiels

| Raccourci | Action |
|-----------|--------|
| `` Ctrl+` `` | Ouvrir / fermer le terminal |
| `Ctrl+Shift+P` | Palette de commandes (tout faire depuis ici) |
| `Ctrl+P` | Ouvrir un fichier rapidement |
| `Ctrl+/` | Commenter / décommenter une ligne |
| `Shift+Alt+F` | Formater le fichier (black) |
| `F5` | Lancer le débogueur |
| `Ctrl+S` | Sauvegarder |
| `Ctrl+Z` | Annuler |
| `Ctrl+W` | Fermer l'onglet actif |

---

## 📤 Workflow Git quotidien

```bash
# Début de session
git checkout Riemann_Lab_IA
git pull origin Riemann_Lab_IA
source zeta_env/bin/activate

# ... tu travailles ...

# Fin de session
git status                          # voir ce qui a changé (jaune → ?)
git add .                           # ajouter tous les changements
git commit -m "feat: description"   # committer
git push origin Riemann_Lab_IA      # pousser vers GitHub
```

### Tags de commit recommandés

| Tag | Exemple |
|-----|---------|
| `feat` | `feat: ajout FrobeniusLearner` |
| `fix` | `fix: overflow à t≈432` |
| `docs` | `docs: mise à jour wiki` |
| `test` | `test: validation zéros T500` |
| `chore` | `chore: mise à jour requirements` |

---

## 🔌 Panneau PORTS — lancer une animation

```bash
# Lancer un serveur pour tes animations HTML
cd docs/
python -m http.server 8080
# → Codespaces crée une URL dans l'onglet PORTS
# → cliquer sur l'URL → ouvre animation_theta.html dans le navigateur
```

> 💡 Passe la visibilité en **Public** pour partager l'URL avec quelqu'un.

---

## 🐛 Débogage Python dans VS Code

```python
# Ajouter un point d'arrêt dans le code
import pdb; pdb.set_trace()   # méthode classique

# Ou cliquer dans la marge gauche de l'éditeur
# → point rouge = breakpoint
# → F5 pour lancer en mode debug
```

---

## ⚠️ Erreurs fréquentes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `ModuleNotFoundError` | zeta_env pas activé | `source zeta_env/bin/activate` |
| Fichier jaune qui reste | Changements non sauvegardés | `Ctrl+S` puis `git add` + `git commit` |
| Port déjà utilisé | Serveur déjà lancé | `lsof -i :8080` puis `kill <PID>` |
| Push refusé | GitHub en avance sur local | `git pull --rebase` puis `git push` |
| Mauvaise branche | Oubli du checkout | `git branch` pour vérifier, `git checkout` pour corriger |

---

## 🗒️ Wiki — pousser une page

```bash
cd ~/projet_zeta/Riemann_Lab.wiki

git add "nom-de-la-page.md"
git commit -m "docs: ajout/mise à jour page"
git push origin master
```

---

## 📋 Leçons sessions 09–10 juin 2026

### Extension PDF

```bash
# Installer l'extension PDF si les PDF n'affichent rien
code --install-extension tomoki1207.pdf
# Puis : Ctrl+Shift+P → "Reload Window"
```

### PNG/images

Les PNG s'affichent nativement dans VS Code. Si l'affichage est blanc : fichier corrompu
(vérifier `file image.png` ou régénérer).

### Raccourcis essentiels

| Raccourci | Action |
|---|---|
| `F11` | Plein écran toggle |
| `Ctrl+Shift+P` → "Reload Window" | Recharger VS Code après installation d'extension |
| `Super+H` | Minimiser la fenêtre Ubuntu |
| `F4` (dans htop) | Filtrer par nom de processus (ex: `compute_zeros`) |

### tmux — raccourcis utiles

| Raccourci | Action |
|---|---|
| `Ctrl+b d` | Détacher le panneau (run continue en arrière-plan) |
| `Ctrl+b [` | Mode scroll — `q` pour quitter |
| `Ctrl+b z` | Zoom sur le panneau actif |
| `Ctrl+b [` → `Espace` → sélection → `Entrée` | Copier du texte dans tmux |
| `Ctrl+b ]` | Coller le texte copié |

```bash
# Activer la souris dans tmux (scroll + clic)
echo "set -g mouse on" >> ~/.tmux.conf
tmux source-file ~/.tmux.conf
```

---
*Dernière mise à jour : 22 mai 2026 · 10 juin 2026 (leçons sessions 09-10 — PDF, tmux, raccourcis) — ~220 lignes*
