# Rapport — état SSH de PC2 et rendu de 3 formules de Formules_zeta (14/11/2026)

> Lecture seule, **aucune modification de PC2 ni de PC4, aucun commit** (le wiki est resté sur `5da032d`). Aucune adresse ni nom d'hôte dans ce rapport. Mesures du 14/11/2026 à partir de 14:25.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| PC2 : `PasswordAuthentication` | 🟢 | `sshd_config.d/10-zeta-keyonly.conf` contient `PasswordAuthentication no`. | Rien. |
| PC2 : `KbdInteractiveAuthentication` | 🟢 | `no` dans `sshd_config` (ligne 62). | Rien. |
| PC2 : `PermitRootLogin`, `PubkeyAuthentication` | 🟢 | Aucune directive active : valeurs par défaut (déduites, non lues par `sshd -T`). | Rien. |
| PC2 : méthodes réellement acceptées | 🟢 | Requête d'authentification « none » : « Authentications that can continue: publickey ». | Rien. |
| `sshd -T` sur PC2 | 🟡 | Commande introuvable pour l'utilisateur (hors du chemin) et droits root requis ; non lancée en élévation. | Contrôle par le skill `riemann-bastion-hardening`, seulement sur décision de hprzeta. |
| `Formules_zeta` ligne 707 | 🟢 | Rendue (`| π(x) − li(x) | = O(√x ln x)`), `.katex-error` 0, pas de LaTeX brut ; capture `formules_zeta_l707_apres.jpg`. | Rien. |
| `Formules_zeta` ligne 748 | 🟢 | Rendue, 0 erreur, pas de LaTeX brut ; capture `formules_zeta_l748_apres.jpg`. | Rien. |
| `Formules_zeta` ligne 1591 | 🟢 | Rendue, 0 erreur, pas de LaTeX brut ; capture `formules_zeta_l1591_apres.jpg`. | Rien. |
| `Formules_zeta`, page entière | 🟢 | 630 formules rendues, 0 non rendue, `.katex-error` 0, console sans erreur. | Rien. |
| Correction du wiki (étape 2) | ⚪ | Sans objet : aucun rendu cassé. Aucun commit. | Point clos. |

Remarque : les 3 formules sont des blocs `$$` sur plusieurs lignes, pas des cellules de tableau ; les barres `|` y sont sans effet. Le détecteur les signalait à tort.

## 2. Fichiers créés ou modifiés (page | ligne in | ligne out | date heure)

Aucun fichier du wiki ni du dépôt de code n'est modifié. Fichiers locaux de `pdf/site/maj_site_20261114/` :

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| captures/formules_zeta_l707_apres.jpg, l748, l1591 | 3 captures créées (JPEG) | — | 14/11/2026 14:27 |
| RAPPORT_SSH_STACK_20261114.md | pied : « 35 lignes » | « NN35 lignes » | 14/11/2026 14:28 |
| HANDOFF_SITE_20261114.md | lignes 10, 14, 17, 24 réécrites ; section « PC2 et Formules_zeta » ajoutée ; pied mis à jour | version précédente (27 lignes) | 14/11/2026 14:28 |
| RAPPORT_PC2_FORMULES_20261114.md et .pdf | ce rapport | — | 14/11/2026 14:28 |

## 3. Points ouverts
Aucun sur SSH (PC2 et PC4 en clé seule) ni sur les formules du wiki.

---
*RAPPORT_PC2_FORMULES_20261114.md · projet SITE ZETA · hprzeta · mis à jour le 14 novembre 2026 · 37 lignes*
