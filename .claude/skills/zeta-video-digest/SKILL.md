---
name: zeta-video-digest
description: "Transformer une vidéo (YouTube, TikTok) ou des captures d'écran en fiche d'idée exploitable pour la boîte à idées du projet Riemann_Lab : transcript, traduction en français, affirmations clés horodatées, statut, projet de destination. Utiliser quand hprzeta envoie un lien vidéo, un transcript ou des captures et demande de résumer, classer ou archiver l'idée. Toute annonce de preuve de l'hypothèse de Riemann passe par riemann-proof-status. Contrôle des secrets visibles dans les captures avant classement. Ne pas utiliser pour calculer des zéros ni pour résumer un article écrit."
---

# zeta-video-digest

Version : 1.0 · MAJ : 2026-11-28

## Chaîne

transcript → traduction en français → affirmations clés avec horodatage → statut → projet de destination.

## Deux modes

**(a) claude.ai** : skills `tubealfred-youtube` (`youtube-transcript`, `youtube-video`) pour obtenir transcript et métadonnées.

**(b) PC1, sans ces skills** : procédure manuelle ou locale. hprzeta fournit le transcript (copié-collé ou fichier de sous-titres). Outils locaux possibles, **candidats « à auditer » seulement, rien d'installé** (idée 81) : extracteur de sous-titres, transcription audio locale. Passer par `skill-install-audit` avant tout essai. Pour des captures : les lire visuellement, une par une.

## Étapes

1. **Contrôle de sécurité d'abord** (idées 64, 65, 73) : dans les captures et le transcript, repérer jetons, mots de passe, clés, adresses IP/MAC, e-mails, noms d'hôtes internes. S'il y en a : masquer par `***` ou un marqueur du projet, signaler `Sensible : oui`, ne pas recopier la valeur.
2. **Transcript** → traduction en français fidèle (ne pas embellir).
3. **Affirmations clés** : liste courte, chacune avec horodatage `[mm:ss]` et citation brève. Distinguer ce que dit la vidéo de ce que le skill en déduit.
4. **Statut** de chaque affirmation : `intuition`, `à vérifier` ou `piste`. **Jamais « établi »** : une vidéo n'établit rien.
5. **Garde-fou HR** : toute annonce de « preuve de l'hypothèse de Riemann » ou résultat spectaculaire → appliquer `riemann-proof-status` ; par défaut : non vérifié, source non primaire.
6. **Projets de destination** et certitude du rattachement (haute / moyenne / faible, avec la raison).

## Format de sortie (boîte à idées)

```
Idée N
Texte : (résumé en 2-5 lignes, en français)
Statut : intuition | à vérifier | piste
Projets de destination : (liste)
Médias : (lien, nom de capture ; jamais de valeur sensible)
Sensible : oui | non
Certitude du rattachement : haute | moyenne | faible — raison
```

Puis, en pied de fichier : date de mise à jour et nombre de lignes. Le numéro `N` : lire le dernier numéro dans la boîte à idées du projet ; ne pas le deviner (poser la question s'il est introuvable).

## Règles

- Ne rien classer en « établi » ; ne rien exécuter ; ne rien installer.
- Source = vidéo, donc secondaire : le dire.
- Pas de jugement sur les personnes ; décrire les affirmations.
