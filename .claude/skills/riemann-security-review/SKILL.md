---
name: riemann-security-review
description: |
  Revue de sécurité pour le projet `Riemann_Lab` de hprzeta — secrets, `.mcp.json`, serveurs MCP, binaires `.so`, hygiène Git et historique.

  Utiliser ce skill dès que l'utilisateur :
  - Va committer / pousser et veut éviter d'exposer un secret (token GitHub, clé, mot de passe)
  - Manipule `.mcp.json`, `.mcp.json.example`, des variables d'environnement, ou un PAT
  - Configure ou audite un serveur MCP (github, filesystem, ou tout serveur futur nécessitant une clé API)
  - Configure ou audite `.gitignore` (notamment entre branches)
  - Compile ou intègre un binaire `.so` (provenance, recompilation)
  - Vient de subir un blocage GitHub Push Protection (GH013) ou suspecte une fuite
  - Fait du ménage multi-branches et veut vérifier qu'aucun secret ne traîne

  Déclencher aussi pour : purge d'historique (git filter-repo), révocation de token, vérification avant publication wiki/site, audit des chemins exposés par le serveur MCP filesystem.
---

# Riemann Security Review Skill

Skill de revue de sécurité spécialisé pour `Riemann_Lab`. Il encode les **incidents réels**
du projet (token dans `.mcp.json`, `.gitignore` désynchronisé entre branches) pour qu'ils ne
se reproduisent pas. À passer **avant tout push** touchant la config ou des fichiers sensibles.

> Auteur : hprzeta · Mise à jour : 27 septembre 2026 (ajout de la section MCP, voir §8)

---

## 1. Règle d'or

**Un secret (token, clé, mot de passe) ne va JAMAIS dans un fichier suivi par Git.**
Et : **un secret exposé = secret mort** → on le **révoque toujours**, on ne suit jamais
le lien « unblock-secret » de GitHub.

---

## 2. Checklist secrets — avant chaque push

1. **Scan rapide des fichiers touchés** :
```bash
   grep -rInE "token|secret|key|password|ghp_|github_pat" <fichiers à committer>
```
   Vide = OK. Une occurrence = traiter avant de committer.
2. **`.mcp.json` doit être ignoré** sur la branche courante :
```bash
   git check-ignore .mcp.json     # doit renvoyer ".mcp.json"
```
3. **`git status` AVANT `git add -A`** : ne jamais ajouter en aveugle.
4. **Vérifier qu'aucun secret n'est déjà suivi** :
```bash
   git ls-files | grep -i mcp     # ne doit renvoyer que .mcp.json.example
```

---

## 3. Piège majeur — `.gitignore` désynchronisé entre branches

**Leçon réelle (1ᵉʳ juin)** : `.gitignore` n'est PAS synchronisé entre branches. `.mcp.json`
était ignoré sur `Riemann_Lab_C`/`Riemann_Lab_IA` mais PAS sur `main` ni `Riemann_Lab_Test`.

→ Après toute manip multi-branches, vérifier sur **chaque** branche :
```bash
for b in Riemann_Lab_IA Riemann_Lab_C Riemann_Lab_Test main; do
  git checkout "$b" >/dev/null 2>&1
  echo -n "$b : "; git check-ignore .mcp.json || echo "NON IGNORÉ ⚠️"
done
```

---

## 4. Si un secret a déjà été commité

L'ordre compte — le geste n°1 est la révocation, pas la purge :

1. **Révoquer le token** sur GitHub (immédiat — le secret est déjà mort).
2. Purger l'historique :
```bash
   git filter-repo --path .mcp.json --invert-paths
```
3. Vérifier la purge :
```bash
   git log --all --oneline -- .mcp.json     # doit être VIDE
```
4. `git push --force` (le blocage GH013 se lève).
5. Vérifier les **autres branches** (le secret peut y survivre).
6. Régénérer un token, le remettre dans `.mcp.json` **local** (ignoré).

> Rappel : `.gitignore` empêche les futurs commits mais **ne purge pas le passé**.

---

## 5. Suppression de fichiers — `git rm` ≠ `rm`

- Fichier **suivi** (committé) → `git rm fichier` puis commit.
- Fichier **non suivi** → `git rm` échoue (`fatal: ... ne correspond à aucun fichier`) → `rm fichier`.
- **Un fichier non suivi n'est jamais une page wiki / jamais publié** : seul ce qui est
  committé ET poussé est servi. Pas de panique « public » pour un untracked.

---

## 6. Binaires `.so` — provenance & intégrité

- Recompiler depuis la source du dépôt (`make clean && make`), jamais récupérer un `.so` opaque.
- Ne PAS committer les `.so` compilés (les ignorer) — ils se régénèrent.
- Le code doit **refuser de tourner** si le `.so` attendu est absent (pas de fallback silencieux).
- Headers vendorisés (ex. Flint 3.3.1, voir skill `riemann-code-review` §8) : vérifier leur
  provenance avant intégration, ne pas les mélanger avec les headers système.

---

## 7. Avant publication (wiki / GitHub Pages / mail)

- Aucun chemin/identifiant sensible en clair au-delà de ce qui est déjà public (`hprzeta@protonmail.com` est connu, OK).
- Pas de token dans les exemples de commandes, prompts, ou captures.
- Vérifier après push : `git log --oneline -1` + relecture du fichier en ligne.

---

## 8. Sécurité MCP — tokens transportés par les serveurs

Depuis la Vague V1 (`.mcp.json.example`, commit `df46f82`), le projet utilise des serveurs MCP
(`github`, `filesystem`) qui manipulent des secrets et des chemins sensibles. Points de
vigilance spécifiques, à recouper avec la Règle d'or (§1) :

1. **Token GitHub transporté par variable d'environnement uniquement** (`${GITHUB_TOKEN}` dans
   `.mcp.json`, jamais en clair — cf. §2-3). Vérifier que le token utilisé a le **scope
   minimal** nécessaire (accès au dépôt seul, jamais `admin:org` ou équivalent).
2. **`.mcp.json` réel reste local et ignoré** (`.gitignore:40`) — ne jamais le committer, même
   « temporairement pour tester ». Seul `.mcp.json.example` (placeholder `${GITHUB_TOKEN}`,
   jamais de valeur réelle) est suivi par Git.
3. **Serveur `filesystem` : restreindre les chemins exposés.** Le gabarit actuel expose
   `/home/riemann/projet_zeta`, `/mnt/data`, `/mnt/vault_rag` — ne jamais élargir à `/` ou
   `$HOME` entier sans nécessité explicite (la surface d'attaque = tout fichier lisible par
   l'agent via ce serveur).
4. **Rotation du token** : si un agent (Claude Code, Codex) a eu un accès prolongé au token,
   envisager une rotation périodique, en particulier après une session de debug qui a pu
   afficher des variables d'environnement à l'écran ou dans des logs.
5. **Secrets dans les logs/CSV** : les logs structurés (`loguru`, voir skill
   `riemann-code-review` §7) et les exports CSV ne doivent jamais contenir de valeur issue de
   `os.environ`. Vérifier qu'aucun handler d'exception ne dumpe l'environnement complet en cas
   de crash (un traceback par défaut peut exposer des variables locales selon la configuration
   du logger).
6. **MCP futur nécessitant une clé API (ex. `arxiv-mcp-server`, non activé à ce jour)** :
   appliquer strictement les mêmes règles — variable d'environnement uniquement, jamais de
   valeur réelle dans `.mcp.json.example`, scope minimal.

---

## 9. Format de sortie d'une revue de sécurité

1. **Verdict** : 🟢 sûr à pousser / 🟡 corriger d'abord / 🔴 secret exposé → révoquer MAINTENANT.
2. **Findings** (fichier, ligne, type de secret) — sans recopier le secret en entier.
3. **Actions ordonnées** (révocation d'abord, purge ensuite).
4. **Commandes git de vérification + push** prêtes à coller (avec vrais chemins, pas de placeholder).

---
*Skill du projet Riemann_Lab · Auteur : hprzeta · Mise à jour : 27/09/2026 (Vague V3 — ajout section MCP, voir `synthese_skills_zeta.md` §4.1).*
