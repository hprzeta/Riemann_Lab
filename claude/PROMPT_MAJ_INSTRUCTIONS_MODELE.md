# Modèle de procédure — « Mise à jour instructions » d'un projet claude.ai zêta

> Déjà appliquée à SKILLS ZETA (14/11), SECURITE ZETA (14/11) et ZETA FORMATION (21/11).
> Pour un nouveau projet, il suffit d'écrire dans ce projet : « Mise à jour instructions ». claude.ai suit la partie A, puis Claude Code exécute la partie B.
> Référence : `MODELE_INSTRUCTIONS_PROJET.md` (projet SKILLS ZETA, `claude/`).

## Leçons tirées des sessions précédentes

| N° | Problème constaté | Règle |
|---|---|---|
| L1 | Claude in Chrome produit des JPEG, alors que le prompt demandait `.png` (`.png.jpg`) | Toujours nommer les captures `*.jpg`, sans conversion |
| L2 | Une recherche `find` trop large a bloqué la session et a dû être arrêtée | `timeout 60`, `-maxdepth`, exclusion de `.git`, `calculs`, `venv*` ; jamais hors de `/home/riemann/projet_zeta` ; pas de tâche de fond |
| L3 | Claude Code ne peut pas lire les fichiers d'un projet claude.ai | Lister dans « Prérequis » les fichiers à télécharger (nom exact, dans `~/Téléchargements`), vérifiés à l'étape 0 : s'il en manque un, STOP. Quand c'est possible, claude.ai déclenche lui-même le téléchargement dans Chrome |
| L4 | Le tableau de diagnostic a été tronqué à l'écran | Écrire le diagnostic dans `etape3_diagnostic.md` au fur et à mesure, puis l'afficher |
| L5 | `MODELE_INSTRUCTIONS_PROJET.md` n'existe que dans SKILLS ZETA, pas dans le dépôt | Décision à prendre : version de référence dans le dépôt, copie dans SKILLS ZETA (comme D1 pour les skills) |

## A. Côté claude.ai, dans le projet concerné

1. Lire, avec Claude in Chrome (API du compte), les instructions du projet, la liste de ses documents, le modèle et un exemple déjà rempli (SECURITE ZETA).
2. Inventaire : nombre de documents par dossier et par extension, doublons exacts, `.bak`, `.log`, code, copie de skills (D9).
3. Valeurs sensibles par formats réels (D6) : IPv4, `fe80::`, MAC, nom DDNS, chaînes au format de clé, jetons, e-mails autres que l'adresse publique. **On note le nombre et le fichier, jamais la valeur.**
4. Produire un zip `audit_<préfixe>_<AAAAMMJJ>.zip` qui contient :
   - `A_DEPOSER/INSTRUCTIONS_<PROJET>_<date>.md` : sections 1 à 7 du modèle copiées à l'identique, `<<…>>` remplis, §8 propre au projet ;
   - `A_DEPOSER/audit_<préfixe>_<date>.md` : tableau 🟢/🟡/🔴, inventaire, décisions D… proposées ;
   - `A_DEPOSER/ETAT_<PROJET>_<date>.md` : fait, reste ouvert, décisions ;
   - `PROMPT_AUDIT_<PRÉFIXE>_<date>.md` : partie B ci-dessous, adaptée au projet ;
   - la liste des fichiers prérequis (L3).
5. Aucune suppression ni modification dans le projet sans accord de hprzeta.

## B. Côté Claude Code (PC1)

0. `unzip -n` dans `src/ia/prompts/` ; vérifier les prérequis (L3) ; STOP s'il en manque.
1. Créer `pdf/<dossier_domaine>/audit_<préfixe>_<AAAAMMJJ>/` avec `captures/`, `A_DEPOSER/` ; y copier les `.md`.
2. Capture « avant » de la page du projet, en `captures/avant_<projet>.jpg` (L1).
3. Diagnostic en lecture seule, borné (L2), écrit dans `etape3_diagnostic.md` (L4). STOP.
4. Correctif seulement sur « go », avec `.bak` avant toute modification. STOP avant « go commit » et avant « go push ».
5. Tests : test positif, puis `grep -c -F -f ~/.zeta_valeurs_sensibles` = 0 ; PDF et `pdfinfo`.
6. Rapport, un seul HANDOFF, uniquement les `.md` dans `A_DEPOSER/` ; phrase de fin.

## C. Côté hprzeta

1. Coller les instructions dans le projet.
2. Déposer les `.md` de `A_DEPOSER/` (l'ETAT va sous `claude/`).
3. Trancher les décisions proposées.

## Valeurs connues (à reporter dans le tableau du modèle)

| Projet | `<<dossier_domaine>>/<<préfixe>>` |
|---|---|
| SITE ZETA | `site/maj_site` |
| SKILLS ZETA | `audits_skills/audit_skills` |
| SECURITE ZETA | `secur/audit_securite` |
| ZETA FORMATION | `formation/audit_formation` |
| Autres | à fixer lors de leur migration |

---
<sub>Mis à jour le 2026-11-21 · 57 lignes</sub>
