# Rapport — PasswordAuthentication (wiki) et faux positif STACK (14/11/2026)

> Wiki `Riemann_Lab.wiki`, branche `master`, commit `5da032d` (14/11/2026 14:20), poussé sans `--force` (`85daa59..5da032d`). **Aucune modification de PC4.** Aucune adresse ni nom d'hôte dans ce rapport.

## 1. Tableau de validation

| Élément | Statut | Preuve | Reste à corriger |
|---|---|---|---|
| Contexte de `Architecture-Cluster-Zeta.md:200` | 🟢 | Ligne 200 = dernière ligne de la commande de dépannage « Problème 3 : sshd_config manquant » (journal du HP Debian = PC2), recréant un `sshd_config` minimal. Non marquée provisoire. PC4 (OpenBSD) n'est pas concerné. | Rien. |
| Note « Provisoire » | 🟢 | Visible en ligne, juste avant « Problème 4 » ; console sans erreur ; `.katex-error` 0. | Rien. |
| Autres occurrences (`PasswordAuthentication`, `PermitRootLogin`, `KbdInteractiveAuthentication`) | 🟢 | Wiki : seules les lignes 197 et 200 du même bloc. Dépôt : seul le diagnostic publié du 03/10 (PC2, PC3, PC5 en `no`) et mes rapports du jour. | Rien. |
| État réel de PC4 | 🟢 | Fichier de configuration : `PermitRootLogin no`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `AllowUsers` restreint. Requête d'authentification « none » : seule la méthode clé publique est acceptée (mesuré). | Aucune action sur PC4. |
| `sshd -T` sur PC4 | 🟡 | Impossible sans droits root (« no hostkeys available » ; `doas` demande un mot de passe). Le fichier peut différer de la configuration chargée si sshd n'a pas été rechargé ; le comportement mesuré confirme l'état actif. | Si besoin : contrôle avec le skill `riemann-bastion-hardening`, sur décision de hprzeta. |
| État réel de PC2 | 🟡 | Non mesuré. Le wiki montrait `yes` (dépannage) ; le diagnostic publié du 03/10 indique `no`. | À vérifier si souhaité. |
| STACK, phrase du 12/09 (ligne 695, ex-693) | 🟢 | `$$` et `$` en code. En ligne : 0 zone rouge (était 1), 26 formules rendues, `.katex-error` 0, console sans erreur. | Rien. |
| Pieds de page | 🟢 | `Architecture-Cluster-Zeta` 789 lignes (`wc -l` 789) ; `STACK` 708 lignes (`wc -l` 708) ; date du 14/11/2026. | Rien. |
| Audit avant commit | 🟢 | Lignes ajoutées : 0 IP, MAC, clé, jeton, e-mail. | Rien. |

## 2. Fichiers modifiés (page | ligne in | ligne out | date heure)

« in » = texte publié, « out » = texte remplacé. Heure : commit `5da032d`.

| page | ligne in | ligne out | date heure |
|---|---|---|---|
| Architecture-Cluster-Zeta | 203 : « > **Provisoire :** passer à `PasswordAuthentication no` une fois la clé publique installée et testée. » (+ ligne vide) | aucune (la ligne 200 `yes` est inchangée) | 14/11/2026 14:20 |
| Architecture-Cluster-Zeta | 789 (pied : date, 789 lignes) | 787 (787 lignes) | 14/11/2026 14:20 |
| STACK | 695 : les symboles `$$` et `$` de la phrase du 12/09 sont mis entre accents graves | les mêmes symboles en texte brut | 14/11/2026 14:20 |
| STACK | 708 (pied : date, 708 lignes) | 708 (708 lignes) | 14/11/2026 14:20 |

## 3. Points ouverts
- État réel de PC2 : non mesuré.
- Formules `\|…\|` de `Formules_zeta.md` : non traitées dans ce lot.

---
*RAPPORT_SSH_STACK_20261114.md · projet SITE ZETA · hprzeta · mis à jour le 14 novembre 2026 · 35 lignes*
