# PROMPT Claude Code — exclure les `.bak` du dossier `.claude/skills` (`.gitignore` ligne 30)

> Préparé sur claude.ai (projet SITE ZETA) le 11/11/2026 à 23:40, d'après `claude/ETAT_SITE_ZETA_FIN_JOURNEE_20261111.md` (point ouvert n° 1). **Décision de hprzeta : OUI.** Rapport d'analyse joint : `RAPPORT_ANALYSE_GITIGNORE_SKILLS_20261111_2340.md`.

## Problème
`.gitignore` ligne 30 contient `!.claude/skills/**` : elle **ré-inclut** tout le dossier skills. Or les règles du `.gitignore` passent avant celles de `.git/info/exclude` (où la décision D3 a mis `*.bak*`). Donc un fichier `.claude/skills/…/SKILL.md.bak-AAAAMMJJ` **serait publié** par un `git add -A`.

## Correctif visé (1 ligne ajoutée, rien de supprimé)
Ajouter **juste après la ligne 30** (la dernière règle qui correspond gagne) :
```
.claude/skills/**/*.bak*
```

## Règles
1. **STOP avant commit**, **second STOP avant push** (attendre « go commit » puis « go push »). Jamais `--force`. Wiki non concerné.
2. Copie de sauvegarde avant modification : `pdf/archive/gitignore.bak-<AAAAMMJJ>` (exclue par D3, non suivie).
3. Aucune valeur identifiante dans les messages, captures et rapports (`[IP]`, `[MAC]`, `[EMAIL]`).
4. Tout montrer à l'écran dans Claude in Chrome : défiler jusqu'à la ligne, survoler, encadrer, capturer.
5. Ne toucher à aucun autre fichier (notamment `monitoring/Monitoring-Runs.md`, toujours « M »).

---

## Étape 0 — Ranger le prompt
```bash
mkdir -p /home/riemann/projet_zeta/src/ia/prompts
cd /home/riemann/projet_zeta/src/ia/prompts
unzip -o ~/Téléchargements/MAJ_GITIGNORE_SKILLS_20261111_2340.zip   # ou ~/Downloads/ selon la machine
```
Puis lire ce prompt depuis `src/ia/prompts/`.

## Étape 1 — Ouvrir Claude in Chrome, onglet « Mise à jour site » (état AVANT)
- Ouvrir un onglet nommé **« Mise à jour site »** sur `https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/.gitignore`.
- Défiler jusqu'à la ligne 30, la survoler et l'encadrer en rouge. Capture : `captures/gitignore_avant_ligne30.jpg`.

## Étape 2 — Dossier de mise à jour du jour
```bash
D=/home/riemann/projet_zeta/pdf/site/maj_site_$(date +%Y%m%d)
mkdir -p "$D/captures"
cp -p /home/riemann/projet_zeta/src/ia/prompts/RAPPORT_ANALYSE_GITIGNORE_SKILLS_20261111_2340.* "$D/"
cp -p /home/riemann/projet_zeta/src/ia/prompts/PROMPT_CORRECTION_GITIGNORE_SKILLS_20261111_2340.md "$D/"
```
(Le dossier est complété s'il existe déjà.)

## Étape 3 — Diagnostic (lecture seule) — montrer chaque sortie
```bash
cd /home/riemann/projet_zeta
git branch --show-current                           # attendu : Riemann_Lab_IA
sed -n '25,35p' .gitignore | cat -n                 # vérifier que la ligne 30 est bien !.claude/skills/**
git ls-files .claude/skills | wc -l                 # N_AVANT (à noter)
git ls-files .claude/skills | grep -c '\.bak' || true   # attendu : 0
# Test de la faille, sur un fichier temporaire jamais commité :
T=$(git ls-files .claude/skills | head -1 | xargs dirname)/zz_test.bak-test
touch "$T"; git check-ignore -v "$T" || echo "NON IGNORÉ → faille confirmée"; rm -f "$T"
```
Si la ligne 30 n'est pas celle attendue : **STOP**, décrire l'écart, ne rien modifier.

## Étape 4 — Correctif (sur `Riemann_Lab_IA`)
```bash
cp -p .gitignore pdf/archive/gitignore.bak-$(date +%Y%m%d)
sed -i '30a .claude/skills/**/*.bak*' .gitignore
git diff -U2 .gitignore                             # attendu : +1 ligne, 0 ligne retirée
# Contrôles :
touch "$T"; git check-ignore -v "$T"                # attendu : .gitignore:31:.claude/skills/**/*.bak*
rm -f "$T"
git ls-files .claude/skills | wc -l                 # = N_AVANT (aucun skill réel perdu)
git status --short                                  # seuls changements : .gitignore (+ Monitoring-Runs.md déjà M)
```
Mettre à jour le pied de page de date si le `.gitignore` en a un (sinon ne rien ajouter).

**STOP — attendre « go commit ».**
```bash
git add .gitignore
git commit -m "gitignore: exclure les .bak du dossier .claude/skills (la ligne 30 les ré-incluait)"
for b in Riemann_Lab_C main Riemann_Lab_Test; do git checkout "$b" && git cherry-pick -x Riemann_Lab_IA; done
git checkout Riemann_Lab_IA
```
Vérifier que le `.gitignore` est identique sur les 4 branches (`git show <b>:.gitignore | sha256sum`).

**STOP — attendre « go push ».** Puis `git push origin Riemann_Lab_IA Riemann_Lab_C main Riemann_Lab_Test` (sans `--force`) ; local = origin pour les 4.

## Étape 5 — Montrer et tester à l'écran (état APRÈS)
- Onglet « Mise à jour site » : recharger le `.gitignore` sur `main` puis sur `Riemann_Lab_IA` ; défiler jusqu'aux lignes 30-31, encadrer la nouvelle ligne 31 en vert. Captures : `captures/gitignore_apres_main_ligne31.jpg`, `captures/gitignore_apres_IA_ligne31.jpg`.
- Non-régression du site : ouvrir `https://hprzeta.github.io/Riemann_Lab/`, défiler de haut en bas, cliquer sur 2 animations. Vérifier : liens externes (curl -sIL, tous en 200), 0 `.katex-error`, 0 formule brute `\(` ou `$$`, console sans erreur, pied « mis à jour le … » inchangé (le site n'est pas modifié par ce correctif).
- Audit secrets du diff : 0 IP, MAC, clé, jeton, e-mail.

## Étape 6 — Rapport
Dans `pdf/site/maj_site_<AAAAMMJJ>/` : `RAPPORT_MAJ_GITIGNORE_SKILLS_<AAAAMMJJ>_<HHMM>.md` + `.pdf` avec :
- tableau de validation (🟢/🟡/🔴, preuve, reste à corriger) ;
- tableau `page | ligne in | ligne out | date heure` (ligne in en **vert**, ligne out en **rouge** dans le PDF) ;
- pied : nom du fichier · date et heure de MAJ · nombre de lignes.

Terminer par : **« hprzeta, donne maintenant le .md du rapport (seulement le .md) à claude.ai, projet SITE ZETA : il le range lui-même. »**

---
*PROMPT_CORRECTION_GITIGNORE_SKILLS_20261111_2340.md · projet SITE ZETA · hprzeta · MAJ 11 novembre 2026 23:40 · 95 lignes*
