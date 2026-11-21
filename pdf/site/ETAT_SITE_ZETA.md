# État du site zêta — 21/11/2026

## État en bref
- **Dernière action :** 21/11/2026 : instructions au modèle commun ; procédures « Test site » et « Vérification site » portées par le skill `riemann-site-check` ; 2 valeurs réelles masquées (D32).
- **Chiffres clés :** Projet : 62 documents `.md` (43 dans `claude/`, 19 à la racine) ; 0 doublon ; décisions D1 à D32.
- **Point bloquant :** Rien de commité côté site : `pdf/site/maj_site_20261121/` et archives du jour ; `.md` de `maj_site_20261114/A_DEPOSER/` à recevoir.
- **Prochaine action :** règle `.claude/rules/site.md` créée ; reprendre les points 🟡 Y1 à Y3 et les formules des 10 pages du diagnostic.

> Rédigé sur claude.ai (projet SITE ZETA). Fait suite à `claude/ETAT_SITE_ZETA_20261114.md` (détail des décisions D1 à D29 dans les ETAT du 12/11 et du 14/11).

## Fait
- 21/11 : instructions du projet mises au modèle commun (`claude/MODELE_INSTRUCTIONS_PROJET.md`, commit `db3a22d`) : sections 1 à 7 communes, §8 propre au site. Les procédures « Test site » et « Vérification site » sont désormais portées par le skill `riemann-site-check` (contenu vérifié identique, avec en plus le contrôle mobile et SHA déployé / HEAD) ; « Mise à jour site » par `riemann-site-update`.
- 21/11 : ancienne version des instructions sauvegardée dans `claude/INSTRUCTIONS_SITE_ZETA_avant_20261121.md`.
- 21/11 : inventaire du projet : 62 `.md` (43 dans `claude/`, 19 à la racine), 0 doublon, 0 `.bak`. Contrôle par formats réels : aucune IPv4, aucune clé, aucune adresse `fe80::` réelle (21 mentions = motifs de contrôle) ; **2 valeurs réelles** (1 nom DDNS, 1 e-mail personnel) dans 2 documents du 11/11, non recopiées ici.

## Décisions (nouvelles)
| # | Décision | Statut |
|---|---|---|
| D30 | Instructions au modèle commun ; procédures répétitives dans les skills `riemann-site-check` et `riemann-site-update` | adoptée 21/11 |
| D31 | Côté Claude Code : règle `.claude/rules/site.md` (chemins `pdf/site/**`, `md/site/**`, `docs/**`, wiki) | proposée |
| D32 | Masquer les 2 valeurs réelles (`[DDNS_PC4]`, `[E-MAIL]`) dans `RAPPORT_TEST_MAJ_SITE_20261111_2049.md` et `PROMPT_CORRECTIONS_SITE_20261111.md` | 🟢 fait le 21/11 (0 document sensible restant) |

Rappel des décisions toujours en vigueur : D5 (jamais de mise à jour automatique du site), D23 (liens issues/Kanban du README gardés), D26 (pages renommées, renvois gardés), D28 (test automatique V2), D29 (commandes « Test site » et « Vérification site »).

## Reste ouvert
- Repris du 14/11 : `.md` de `pdf/site/maj_site_20261114/A_DEPOSER/` à recevoir ; formules des 10 pages nouvelles du diagnostic et points 🟡 Y1 à Y3 ; zip `TEST_AUTO_V2_20261114_1257.zip` si le test reste partiel ; restes acceptés (Plotly, liens privés du README, DOI Turing 1953) ; pages de renvoi du wiki ; rapports du 12/11 non commités.
- D31 : règle Claude Code `site.md` (prompt commun à tous les projets, en fin de migration).

---
<sub>Mis à jour le 2026-11-21 · 30 lignes</sub>
