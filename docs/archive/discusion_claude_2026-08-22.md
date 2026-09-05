# Discussion Claude Code — 22 août 2026

> Archive de session — mise à jour du diagnostic réseau WireGuard, fusion du
> guide de commandes, point projet. Extraits de code modifiés non reproduits
> ici — tableaux, rapports, conclusions et instructions transmises par
> hprzeta conservés intégralement.

---

## 1. Mise à jour du diagnostic WireGuard — incident récurrent

### Prompt de hprzeta

> Lis RAPPORT-SESSION-WIREGUARD-IPV6.md (session du 22/08/2026). Mets à jour
> Riemann_Lab.wiki/Diagnostic-WireGuard-Hotspot.md :
> 1. La page est marquée « RÉSOLU 05/07/2026 » mais la panne a récidivé le
>    22/08/2026. Restructure-la en incident récurrent : garde l'historique de
>    juillet, ajoute la session d'août.
> 2. Cause racine identifiée cette fois : règle IPv6 de la box pointant vers
>    une adresse PC4 périmée. À documenter en premier — se reproduira à
>    chaque changement de préfixe SFR.
> 3. Ajoute la 2e cause (net.inet.ip.forwarding=0 sur PC4), absente de la
>    version de juillet.
> 4. Supprime ou corrige toute mention d'un accès par IPv4
>    (192.168.1.54:51820, redirection de port IPv4) : le WAN de la box est
>    IPv6 seul, ce chemin est inopérant par conception.
> 5. Ajoute la section « faux positifs connus » (§3.2 du rapport) : nc -u,
>    ping6, nm-dispatcher.
> 6. Vérifie qu'aucun token DuckDNS n'apparaît dans le wiki ni dans
>    l'historique git.

### Alerte sécurité trouvée en cours de route — token DuckDNS exposé

En exécutant le point 6 (vérification), un **token DuckDNS réel** a été
trouvé exposé en clair — pas seulement dans l'historique git, mais dans le
contenu **actuel** de `Migration-PC4-Compaq-CQ58-20260816.md`, poussé sur
`origin/master` (commit `24cd459`). Le même token que celui encore utilisé en
production dans `duck.sh` sur PC4 au moment du rapport.

Trois options soumises à hprzeta : rédaction simple, rédaction + purge de
l'historique git (`filter-repo`, destructif), ou ne rien faire. **Choix de
hprzeta : rédaction seule** — l'historique git n'est pas réécrit (dépôt jugé
interne), cohérent avec la décision déjà prise dans le rapport de ne pas
régénérer le token (WireGuard authentifie par clé publique ; un détournement
DNS ne permettrait qu'un déni de service, pas une interception).

### Travail réalisé

- `Migration-PC4-Compaq-CQ58-20260816.md` — token remplacé par `<TOKEN>`
  (commit wiki `7ebf94c`).
- `Diagnostic-WireGuard-Hotspot.md` — restructuré en incident récurrent
  (158 → 397 lignes, commit wiki `2b3b57d`) : règle IPv6 de la box documentée
  en premier comme mode de défaillance structurel (se reproduit à chaque
  changement d'adresse IPv6 de PC4 — préfixe SFR ou changement d'interface,
  comme lors de la migration matérielle du 16/08), nouvelle cause
  `net.inet.ip.forwarding=0`, historique juillet conservé (`AllowedIPs` vide),
  faux positifs consolidés (`nc -u`, `ping6`, `nm-dispatcher`), mentions IPv4
  corrigées (WAN de la box IPv6 seul par conception, indépendamment de tout
  blocage opérateur mobile).

---

## 2. Fusion du guide de commandes réseau

### Prompt de hprzeta

> Intègre COMMANDES-SESSION-20260822.md au guide de commandes du projet.
> Priorité à la §7 (correspondance Linux/OpenBSD) : c'est la source d'erreur
> récurrente avec PC4 sous OpenBSD. Vérifie si un guide de commandes existe
> déjà dans le wiki — fusionne plutôt que de dupliquer.

### Travail réalisé

`Guide-Linux-Commandes.md` existait déjà (1393 lignes) — fusion plutôt que
duplication (commit wiki `68f2d6d`, 1393 → 1610 lignes) :

- Nouvelle table de correspondance Linux ↔ OpenBSD en tête de guide
  (référence rapide, priorité demandée par hprzeta).
- Nouvelle §27 : résolution DNS (`dig`), lecture des champs de `wg show`,
  table d'interprétation des erreurs SSH, faux positifs (`nc -u`, `ping6`),
  séquence de vérification complète après toute modification réseau.
- §1/§5/§6 existantes enrichies (TTL, `ip link`/`ip neigh`, syntaxe crochets
  IPv6, `pfctl -sn` obsolète) plutôt que dupliquées en nouvelles sections.
- 5 nouvelles lignes dans la table « Leçons importantes apprises ».

---

## 3. Push vers origin/master

### Prompt de hprzeta

> push origin master

### Résultat

3 commits locaux poussés : `7ebf94c` (rédaction token), `2b3b57d`
(restructuration diagnostic), `68f2d6d` (fusion guide de commandes).
`JOURNAL.md`, modifié par ailleurs (travail en cours de hprzeta sur le run
T5M, sans rapport avec cette session), volontairement laissé de côté — non
inclus dans les commits ni le push.

---

## 4. Point projet

### Prompt de hprzeta

> point projet

### Résultat

Bloc `PROMPT_REPRISE` de `~/riemann_handoff/Handoff.md` affiché tel quel
(mécanisme standard, rien exécuté). Résumé donné en 3 lignes :

1. **Pipeline** : v16 opérationnel (T=100k en 1,6 min, 20/20 LMFDB) ; mais le
   run T=5M v16 du 16-18/08 a perdu 31h37 de calcul (CSV jamais flushé avant
   le crash PC1 à 03h12) — un run de reprise (MARGE=10.0, segments 0-1) était
   en cours au moment de la clôture de session du 18/08.
2. **Dernier commit** avant cette session : code `36c7f77`
   (`Riemann_Lab_C`, poussé) ; wiki `841bf63` (poussé) — 4 branches
   désynchronisées depuis `65e64f4`.
3. **Prochaine action** (listée dans le Handoff, non traitée pendant cette
   session) : coller `smartctl -a /dev/sda` + `dmesg` (fiabilité PC1) et
   lancer le test v15 vs v16 sur T=100k (écart 177 vs 96 zéros manquants,
   toujours sans cause identifiée).

---

## 5. Points ouverts en fin de session

- Token DuckDNS rédigé du fichier actuel, mais **toujours présent en clair
  dans l'historique git** — décision assumée de ne pas purger.
- Régénération de la clé WireGuard PC4 et du token DuckDNS — action hprzeta,
  toujours pas faite (rappelée dans le Handoff depuis plusieurs sessions,
  antérieure à cette session).
- Écart 177 vs 96 zéros manquants (déficit T=5M v16 vs v13) — toujours sans
  cause identifiée, test v15/v16 sur T=100k non lancé pendant cette session.
- Fiabilité de PC1 pour un run long — toujours INDÉTERMINÉE (`smartctl`/
  `dmesg` en attente, action hprzeta).
- 4 branches du dépôt code (`Riemann_Lab_C`/`main`/`Riemann_Lab_IA`/
  `Riemann_Lab_Test`) désynchronisées depuis `65e64f4` — pas de cycle de sync
  effectué pendant cette session (hors périmètre, session centrée sur le
  wiki réseau).

---

*Document généré à la demande de hprzeta ("byby", 22/08/2026) — archive de
fin de session, Claude Code — Riemann_Lab, branche `Riemann_Lab_C`.*
