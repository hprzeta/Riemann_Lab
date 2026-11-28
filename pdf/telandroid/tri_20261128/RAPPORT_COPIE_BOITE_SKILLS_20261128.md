# Rapport — copie des fiches de la boîte à idées (.md seuls) pour SKILLS ZETA — 28/11/2026

> Local uniquement. Machine : PC1. Aucun nom de média, aucun secret dans ce document. Source en lecture seule, aucun commit, aucun push, aucun `--delete`.

## Résumé

Les 83 fichiers `.md` de `boite_a_idee/` (82 fiches `idee_NN.md` et `index.md`) ont été copiés avec le rangement de la boîte (un dossier par idée) dans `pdf/telandroid/tri_20261128/SKILLS_ZETA_boite_a_idee_md_20261128/`, puis archivés dans `SKILLS_ZETA_boite_a_idee_md_20261128.zip`. Aucun média, aucune sauvegarde `.bak`, aucun `.tsv` n'a été copié. La source n'a pas été modifiée. Le contrôle de confidentialité a signalé 6 fichiers (mots seulement) ; sur décision de hprzeta (option 1), les 83 `.md` ont été copiés.

## Tableau de validation

| Étape | Contrôle | Résultat | Verdict |
|---|---|---|---|
| 0 | Prompt extrait dans `src/ia/prompts/tel_copie_boite_20261128/` | 1 fichier, sans écrasement | 🟢 |
| 1 | Source et destination | source présente avec `index.md` ; destination et archive absentes avant la copie | 🟢 |
| 1 | Comptages de la source | 82 dossiers d'idées, 82 `idee_NN.md`, 83 `.md` ; hors `.md` : 483 fichiers (374 `.jpg`, 86 `.mp4`, 23 sauvegardes `.bak`) ; 86 Ko de `.md` | 🟢 |
| 2.1 | Liens symboliques dans la source | 0 | 🟢 |
| 2.2 | IP, MAC, adresses e-mail, chemins `/home/` | 0 occurrence dans les 83 `.md` | 🟢 |
| 2.2 | Mots « clé », « jeton », « mot de passe » | **6 fichiers** (`idee_23`, `idee_29`, `idee_30`, `idee_64`, `idee_65` et `index.md`), 1 à 3 lignes chacun ; aucune valeur détectée (0 longue chaîne sur les lignes touchées des fiches ; les 2 candidats de l'`index.md` sont des noms de dossiers d'idées) ; contenu non relu un par un | 🟡 |
| 2.2 | STOP sur motif sensible | appliqué ; **décision de hprzeta : option 1, copier les 83 `.md`** | 🟢 |
| 3 | Copie `rsync -a` (`.md` seuls, rangement identique, sans `--delete`, sans `-L`) | code 0 ; 83 fichiers, 82 dossiers recréés | 🟢 |
| 4.1 | `.md` source contre destination | 83 / 83, mêmes chemins relatifs | 🟢 |
| 4.2 | Fichiers non `.md` dans la destination | 0 | 🟢 |
| 4.3 | sha256 source contre destination | 83 comparés, 0 écart | 🟢 |
| 4.4 | Archive `SKILLS_ZETA_boite_a_idee_md_20261128.zip` | 84 346 octets ; 166 entrées = 83 fichiers + 83 dossiers ; 0 non `.md`, 0 `.bak`, 0 média ; test d'intégrité sans erreur ; sha256 du contenu = source (83 comparés, 0 écart) | 🟢 |
| — | Source intacte | 83 `.md`, 566 fichiers au total comme avant ; registre inchangé | 🟢 |
| — | Destination dans l'arborescence du dépôt | `pdf/telandroid/tri_20261128/` : fichiers non suivis par git ; ne pas les inclure dans un `git add -A` sans contrôle | 🟡 |
| — | Commit, push, `--force`, suppression | aucun | 🟢 |

## Tableau horodaté des changements (28/11/2026)

| Heure | Machine | Changement | Périmètre |
|---|---|---|---|
| 14:50 | PC1 | Extraction du prompt (sans écraser) | `src/ia/prompts/tel_copie_boite_20261128/` |
| ≈14:51 | PC1 | Étape 1 : comptages de la source (lecture seule) | `boite_a_idee/` |
| ≈14:52 | PC1 | Étape 2 : liens symboliques et contrôle de confidentialité (comptes seulement) | 83 `.md` |
| 14:53 | PC1 | Étape 3 : création de la destination et copie des 83 `.md` | `tri_20261128/SKILLS_ZETA_boite_a_idee_md_20261128/` |
| ≈14:53 | PC1 | Étape 4 : contrôles 4.1 à 4.3 (lecture seule) | source et destination |
| 14:54 | PC1 | Création de l'archive et vérification de son contenu | `tri_20261128/SKILLS_ZETA_boite_a_idee_md_20261128.zip` |
| 14:54 | PC1 | Rédaction du rapport et du handoff, copie dans `A_DEPOSER/` | `tri_20261128/`, `A_DEPOSER/` |

## Ce qui est livré

- Dossier : `pdf/telandroid/tri_20261128/SKILLS_ZETA_boite_a_idee_md_20261128/` (83 `.md`, rangement de la boîte).
- Archive : `pdf/telandroid/tri_20261128/SKILLS_ZETA_boite_a_idee_md_20261128.zip` (83 fichiers `.md`).
- Aucune sauvegarde nécessaire : aucun fichier existant n'a été modifié.

## Suite proposée (rien ne s'exécute sans « go »)

- Relire les 6 fichiers signalés par le contrôle de confidentialité avant de transmettre l'archive à SKILLS ZETA, si vous voulez une certitude (par exemple avec `grep -n -i -E 'clé|jeton|mot de passe'`).
- Rappel : les statuts et rattachements des idées 75 à 82 restent à relire (certitude `a_verifier`), et l'ETAT peut recevoir une ligne sur cette copie sur demande.
- Rien n'est commité ni poussé ; l'archive et le dossier copié ne doivent pas être ajoutés à git sans « go commit ».

---
<sub>Mis à jour le 2026-11-28 · 54 lignes</sub>
