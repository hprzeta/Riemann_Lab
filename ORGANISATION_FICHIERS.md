# 🗂️ Organisation des fichiers — Riemann_Lab

> **Fichier :** ORGANISATION_FICHIERS.md · **Dossier :** wiki (racine)
> **Branche :** master (wiki) · **Auteur :** hprzeta · **MAJ :** 2026-06-03

> 🧭 **Rôle de cette page.** C'est la *carte de contexte* du projet : elle dit **où vit quoi**,
> ce qui est **versionné**, ce qui est **secret**, et **comment Claude récupère le contexte**.
> Page **stable** — elle ne contient aucun état de session (celui-ci vit dans `Handoff.md` local
> et dans [[JOURNAL]] / [[STACK]]). À lire en début de session avant d'aller chercher le reste sur GitHub.

---

## 1. Les 6 lieux

Il n'y a pas 3 endroits où ranger les fichiers, mais **6**, qu'il ne faut jamais confondre :

| # | Lieu | Versionné | Public | Pour qui / contenu type |
|---|---|---|---|---|
| 1 | **Disque local** `~/projet_zeta/` (hors git) | ❌ | non | état de travail volatil : `Handoff.md`, brouillons, logs de run |
| 2 | **Repo principal** `hprzeta/Riemann_Lab` (4 branches) | ✅ | oui | code (`src/`), site (`docs/`), config (`CLAUDE.md`, `.gitignore`), skills versionnés (`.claude/skills/`) |
| 3 | **Repo wiki** `Riemann_Lab.wiki` (`master`) | ✅ (dépôt séparé) | oui | doc lisible : cours, formulaires, guides, [[JOURNAL]], [[STACK]], rapports |
| 4 | **Skills Claude Code** `~/.claude/skills/` → versionnés vers `.claude/skills/` du repo | local → ✅ | — | skills exécutés par l'IA en terminal |
| 5 | **Skill Claude.ai web** `/mnt/skills/user/riemann-lab/` | géré à part (read-only) | — | skill exécuté par l'IA web ; édité via copie puis déployé |
| 6 | **Fichiers du projet Claude.ai** | ❌ (snapshot RAG) | non | copie *cherchable* pour une conversation — **pas une source de vérité** |

> ⚠️ **Wiki = fichiers à plat uniquement.** GitHub Wiki ne sert pas les pages depuis un sous-dossier.
> Toute page doit être à la **racine** du dépôt wiki (`niveau-0-prerequis.md`, jamais `cours/niveau-0…`).

---

## 2. Règle de décision (2 questions)

Pour n'importe quel fichier, se poser dans l'ordre :

1. **Un humain le lit, ou une machine l'exécute / le configure ?**
   - *lit* → **documentation → wiki** (lieu 3) — ou `docs/` (lieu 2) si c'est le site.
   - *exécute / configure* → **code ou skill → repo** (lieu 2) : `src/`, `.claude/`, `CLAUDE.md`.
2. **Stable / partageable, ou état de session volatil ?**
   - *stable* → **versionné**.
   - *volatil* → **local seulement** (lieu 1).

Et une garde permanente : **secret → nulle part** (ni repo, ni wiki, ni chat, ni fichiers projet).

---

## 3. Où vit quoi

| Type de fichier | Lieu | Note |
|---|---|---|
| Code `.py`, `.c`, `.h`, `Makefile` | repo `src/` | versionné |
| Site `index.html`, `animation_*.html` | repo `docs/` | GitHub Pages |
| `CLAUDE.md` (racine + cascade) | repo, à chaque niveau | **synchroniser la racine sur les 4 branches** ; cascade = branche du code concerné |
| Skills (`SKILL.md`…) | repo `.claude/skills/` | **jamais dans le wiki** |
| Cours, lexiques, formulaires, [[Formules_zeta]], [[Bibliotheques]], guides | wiki | doc lisible |
| [[JOURNAL]] (historique daté, append-only) | wiki | mémoire long terme |
| [[STACK]] (outils, roadmap, formation, matériel) | wiki | référence stable |
| Rapports / analyses (`analyse_problemes_vN_vN+1`, validations) | wiki ou repo `docs/`/`pdf/` | livrables datés |
| `analyse_problemes_v5_v6.md` | wiki | doc technique v5→v6 |
| `analyse_problemes_v4_1_v6_synthese.md` | wiki | synthèse globale v4.1→v6 |
| `compute_zeros_v6.py` | repo `src/calculs/optimisation/` | script actif v6 |
| `scan_arb.c` | repo `src/calculs/optimisation/c_modules/` | détection C v6 (Z_double) |
| `animation_gaps_gue.html` | repo `docs/` | site v6 — GUE vs STEP |
| `animation_ntermes_rs.html` | repo `docs/` | site v6 — N_termes et bottleneck |
| `recap_session_20260610_11.pdf` | local `claude-traitement-journalier/` | RAG BrainVault |
| `Handoff.md` (état courant + prochaine action) | **local** (`~/riemann_handoff/`) | volatil, réécrit chaque session — **hors git** (`Handoff.md` est dans `.gitignore`) |
| Logs de run `*.log` | local | bruit — ignoré par `.gitignore` (`*.log`) |
| Gros CSV (T=10000…) | local `/mnt/data` ou Git LFS | ne pas gonfler git ; petits CSV → repo `data/` |
| Secrets `.mcp.json`, tokens, clés | **nulle part** | ignoré par `.gitignore` sur les 4 branches |

---

## 4. Format d'en-tête et de pied de page (standard projet)

Tout fichier `.md` / `.pdf` porte un **en-tête** et un **pied de page** identifiant **fichier · dossier · branche · auteur · date**. Ce format rend la dérive visible d'un coup d'œil (un fichier daté de 6 semaines sur la mauvaise branche saute aux yeux).

**En-tête :**
```markdown
> **Fichier :** NOM.md · **Dossier :** chemin (`~/projet_zeta/...` ou « wiki racine »)
> **Branche :** NOM_BRANCHE · **Auteur :** hprzeta · **MAJ :** AAAA-MM-JJ
```

**Pied de page :**
```markdown
*NOM.md · dossier · branche NOM_BRANCHE · hprzeta · MAJ AAAA-MM-JJ · N lignes*
```

> ⚠️ **Champ « Branche » pour un fichier synchronisé** (ex. `CLAUDE.md` racine présent sur 4 branches) :
> indiquer la **branche source canonique**, pas un verrou — par exemple
> `Branche : Riemann_Lab_C (source) → sync main · IA · Test`.
> Pour un fichier propre à une seule branche (cascade `c_modules`), mettre la vraie branche unique.
>
> Le `.gitignore` n'est **pas** un `.md` : il ne porte **pas** d'en-tête/pied de page.

---

## 5. Comment Claude récupère le contexte (fin du copier-coller manuel)

L'auto-push « Claude Code → fichiers du projet Claude.ai » **n'existe pas** : ce sont deux systèmes séparés. Mais ce n'est pas nécessaire, car **Claude.ai web peut lire le GitHub public directement** (`git clone` / `fetch`). Le vrai relais est donc :

> **Claude Code pousse sur GitHub → Claude tire depuis GitHub.**

Conséquences pratiques :

- **Public & poussé** (code, site, pages wiki, rapports publics, [[JOURNAL]], [[STACK]]) → **ne pas uploader** dans le projet Claude.ai. Donner la **branche + dernier commit**, Claude va chercher l'état courant lui-même.
- **Non-public & utile ponctuellement** (Handoff local, log d'un run qu'on débogue, brouillon pas encore poussé) → **coller dans le chat** au moment où on en a besoin.
- **Secret** → **jamais**, nulle part.
- Le dossier de fichiers du projet Claude.ai peut rester **quasi vide** : au mieux, **cette page** comme carte de contexte, et le reste se récupère sur GitHub.

> 💡 Coût token : la simple *présence* d'un fichier dans le projet ne coûte presque rien (récupération à la demande, par recherche) ; c'est la *lecture* d'un gros fichier qui coûte. Donc on évite d'y laisser de gros CSV / logs.

### Inbox IA — staging public (branche `inbox-ia`)

Pour un fichier **pas encore poussé** ou un **lot** pénible à coller : plutôt qu'encombrer le projet Claude.ai, on utilise une **branche orpheline** dédiée `inbox-ia` (isolée du graphe de merge). On y dépose, Claude lit la branche, puis on **archive en local daté** (`~/archive_ia/AAAAMMJJ/`) et on vide la branche.

- ⚠️ **Public + historique permanent** : l'inbox ne contient **QUE du safe-pour-toujours**. Jamais un secret, jamais un log à chemins/identifiants sensibles → ceux-là se collent **dans le chat** (zéro trace).
- Le `git rm` + archive = **rangement**, **pas** confidentialité (l'historique git garde tout).
- Nom volontairement **distinct** des branches de code (`Riemann_Lab_IA`) pour éviter la confusion.
- Brique réutilisable pour l'**Objectif 2** : l'agent autonome pourra y déposer / lire automatiquement.

Workflow : `git checkout inbox-ia` → déposer les fichiers → `commit` + `push` → « lis la branche `inbox-ia` » → une fois traité : archive locale datée + `git rm` + `push` + retour sur la branche de travail.

---

## 6. Ce qui ne va JAMAIS nulle part

`.mcp.json`, tokens GitHub (PAT), clés SSH privées, mots de passe, identifiants d'API.

- Ignorés par `.gitignore` (motif `.mcp.json`) sur les **4 branches** — vérifier avec
  `git check-ignore -v .mcp.json` sur **chaque** branche (sortie vide = NON protégé).
- Un secret exposé = **secret mort** : on le **révoque** toujours, on ne suit jamais le lien
  « unblock-secret » de GitHub.
- `.gitignore` n'est **pas** synchronisé automatiquement entre branches → après toute manip
  multi-branches, revérifier `git check-ignore` partout.

---

## Voir aussi

- [[JOURNAL]] — historique daté, append-only
- [[STACK]] — outils, roadmap, matériel, formation
- [[Guide-Git-GitHub]] — workflow git détaillé
- [[Bonnes-Pratiques-Claude-Code]] — gestion du contexte / tokens

---
*ORGANISATION_FICHIERS.md · wiki racine · branche master · hprzeta · MAJ 2026-06-11 · 146 lignes*
