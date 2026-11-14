# Rapport — inventaire des skills : compte Claude contre dépôt — 14/11/2026

> Rédigé sur claude.ai (projet SKILLS ZETA), en lecture seule. Sources : skills du compte (copie synchronisée de la session) et branche `Riemann_Lab_IA` lue sur GitHub (arbre public et fichiers bruts), présence vérifiée sur les 4 branches.

## 1. Réponse directe

Sur 12 skills Riemann_Lab, **2 seulement ont leurs deux copies** (`riemann-lab`, `riemann-site-update`), et les deux copies de `riemann-lab` diffèrent. **3** skills n'existent que dans le compte, **7** que dans le dépôt. Une contradiction 🔴 entre `riemann-lab` (dépôt) et `riemann-site-update` sur l'échappement KaTeX doit être tranchée.

## 2. Tableau de validation

| Skill | Compte | Dépôt (4 branches) | Statut | Comment vérifié | Action |
|---|---|---|---|---|---|
| `riemann-site-update` | 130 l. (v2) | 141 l. (v3) | 🟡 | `diff` des deux copies | Valider la carte v3 (R1) |
| `riemann-lab` | 241 l. | 354 l. (mise à jour 08/08/2026) | 🔴 | `diff` : 114 lignes du dépôt absentes du compte ; voir §3 | Trancher §3, puis aligner le compte sur le dépôt |
| `riemann-site-check` | 69 l. | absent (404 ×4) | 🟡 | lecture brute des 4 branches | Zip R4 |
| `zeta-diagnostic` | 42 l. | absent (404 ×4) | 🟡 | idem | Zip R4 |
| `riemann-bastion-hardening` | 174 l. | absent (404 ×4) | 🟡 | idem ; 2 IP privées en ligne 12 | Zip R4 avec IP masquées (D7) |
| `phase-c-illinois` | absent | 466 l. | 🟡 | arbre `.claude/skills/` de `Riemann_Lab_IA` | Carte pour le compte, si utile hors Claude Code |
| `riemann-agent-bridge` | absent | 137 l. | 🟡 | idem | idem |
| `riemann-code-review` | absent | 162 l. | 🟡 | idem | idem |
| `riemann-literature-scout` | absent | 85 l. | 🟡 | idem | idem |
| `riemann-proof-status` | absent | 107 l. | 🟡 | idem (aussi `skill_riemann-proof-status.md` dans ce projet) | idem |
| `riemann-security-review` | absent | 162 l. | 🟡 | idem | idem |
| `riemann-statistics-gue` | absent | 120 l. | 🟡 | idem | idem |

## 3. Contradiction KaTeX 🔴

| Source | Règle écrite |
|---|---|
| `riemann-lab` (dépôt, « audit 05/07/2026 ») | Underscore dans `\text{…}` → **toujours `\_`** ; `%` en mode math → **toujours `\%`** |
| `riemann-site-update` (rapport `corrections_wiki_katex_2026-09-12.md`, cause « prouvée en local avec KaTeX ») | GitHub retire le `\` devant la ponctuation ASCII en mode math : **jamais** `\_ \# \, \; \! \%` ; écrire `\text{a-b}` |

La règle du 12/09 est postérieure et mesurée sur le wiki GitHub. La règle du 05/07 peut rester juste **pour `index.html`** (KaTeX dans le navigateur, sans passage par GitHub Markdown), mais ce point n'est pas vérifié. Proposition (D8) : dans `riemann-lab`, séparer « wiki GitHub » (règle du 12/09) et « HTML du site » (règle du 05/07, à confirmer par un test), puis aligner la copie du compte.

## 4. Fichiers du zip `SKILLS_R4_R5_20261114.zip`

| Fichier | Rôle |
|---|---|
| `PROMPT_INSTALL_SKILLS_R4_R5_20261114.md` | Ajout des 3 skills dans le dépôt, contrôle R3 (`.gitignore` sur 4 branches) et R2 (nouvelle session) |
| `skills/<nom>/SKILL.md` ×3 | Copies du compte ; `riemann-bastion-hardening` avec `[IP-LAN-PC4]` et `[IP-TUNNEL-PC4]` |
| `RAPPORT_INVENTAIRE_SKILLS_20261114.md` | Ce rapport |

## 5. Lignes modifiées (page · ligne in · ligne out · date heure)

| Fichier | Ligne in (nouveau) | Ligne out (actuel) | Date heure |
|---|---|---|---|
| `riemann-bastion-hardening/SKILL.md` l. 12 | `LAN [IP-LAN-PC4] · tunnel [IP-TUNNEL-PC4] (valeurs réelles : ~/.ssh/config et doc privée…)` | `LAN <IP privée> · tunnel <IP privée>` | 14/11/2026 |

---
*RAPPORT_INVENTAIRE_SKILLS_20261114.md · projet SKILLS ZETA · hprzeta · MAJ 14 novembre 2026 · 50 lignes*
