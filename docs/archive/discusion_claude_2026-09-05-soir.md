# Discussion Claude Code — 5 septembre 2026 (soirée)

> Archive complète de la session du soir du 05/09/2026 — accès distant WireGuard
> injoignable en déplacement, diagnostic complet (fausse piste opérateur mobile,
> cause réelle Proton VPN), correctif `wg_auto.sh` v2, intégration wiki, et
> nettoyage des fichiers locaux non commités. Session distincte de celle de
> l'après-midi (diagnostic MARGE=10.0, déjà archivée dans
> `discusion_claude_2026-09-05.md`). Les extraits de code modifiés ne sont pas
> reproduits ici ; seuls les tableaux, rapports, conclusions et les instructions
> transmises par hprzeta sont conservés.

---

## 1. Demande initiale — retour à l'état manuel du 30/08

**Contexte donné par hprzeta :** la session du 30/08 avait rendu `zeta_tmux.sh`/
`wg_auto.sh` automatiques (bascule maison/déplacement + auto-réparation du
tunnel + `notify-send` en boucle). Avant cette modification, hprzeta montait le
tunnel lui-même et ça fonctionnait des deux côtés, y compris depuis le même
téléphone en partage de connexion. Demande : revenir exactement à l'état manuel
d'avant, faire cesser le spam de notifications, en procédant étape par étape
avec diff montré avant chaque action, backup horodaté avant toute modification.

### Diagnostic réseau initial (lecture seule)

| Vérification | Résultat |
|---|---|
| `ip -6 addr` / `ip -6 route` | Aucune IPv6 globale (uniquement `fe80::` lien-local sur `wlp2s0`), aucune route par défaut IPv6 |
| `ping6 2001:4860:4860::8888` | "Réseau non accessible" |
| `dig AAAA zeta-secure.duckdns.org` | Résolution correcte, préfixe cohérent avec l'historique connu |
| `sudo wg show` | Interface `wg0` présente avec une IP mais sans handshake |
| Journal `NetworkManager-dispatcher` | Cycles répétés de réparation automatique toutes les ~10 secondes |

**Découverte en creusant** : deux déclencheurs automatiques en dehors des deux
scripts du projet — le dispatcher NetworkManager `/etc/NetworkManager/
dispatcher.d/99-wg-auto` (root, appelle `wg_auto.sh --quiet` à chaque event
réseau) et le service systemd `wg-quick@wg0.service` activé au démarrage.

**Verdict donné à ce stade** : réseau local sans IPv6 globale confirmée ;
endpoint DuckDNS cohérent, pas de cause côté PC4. Hypothèse retenue (qui se
révélera fausse plus tard dans la soirée) : absence d'IPv6 côté opérateur
mobile.

### Restauration manuelle appliquée

Sur validation explicite de hprzeta après présentation des diffs :
- `wg_auto.sh` neutralisé (backup `wg_auto.sh.bak-20260905` créé avant).
- `wg-quick@wg0.service` désactivé (`systemctl disable`).
- Dispatcher `99-wg-auto` rendu non exécutable (`chmod -x`).
- `zeta_tmux.sh` et `wg0.conf` volontairement non touchés (jump-host SSH et
  config réseau du 30/08 préservés).

---

## 2. Revirement — retour à l'état AUTO du 30/08

**Instruction de hprzeta :** revenir sur la décision du matin — l'accès
distant automatique fonctionnait depuis le portable au travail et devait être
conservé.

Restauration complète effectuée et vérifiée :

| Élément | État restauré |
|---|---|
| `wg_auto.sh` | Identique au backup `wg_auto.sh.bak-20260905` (bascule auto + réparation handshake + notify-send) |
| `wg-quick@wg0.service` | `enabled` (confirmé par `systemctl is-enabled`) |
| Dispatcher `99-wg-auto` | `rwxr-xr-x` (exécutable, confirmé) |

**Test du tunnel depuis le portable, sur demande de hprzeta :** `ping 10.10.0.1`
→ 100 % de perte. Un redémarrage complet du partage de connexion (déconnexion/
reconnexion Wi-Fi confirmée dans les logs noyau, nouveau bail IPv4 obtenu) n'a
rien changé — toujours aucune IPv6 globale ensuite. Effet de bord observé :
`logs/wg_auto.log` montrait un cycle complet de réparation (tentative → échec)
toutes les 9-10 secondes en continu.

---

## 3. Lecture des guides projet avant nouveau diagnostic

**Demande explicite de hprzeta :** lire les guides/docs réseau existants avant
d'agir, puis re-vérifier précisément si le réseau actuel fournit de l'IPv6, en
distinguant bien « hotspot téléphone » et « Port\_Armel » (potentiellement deux
réseaux différents).

**Résumé des guides lus :**
- `Diagnostic-WireGuard-Hotspot.md` (wiki) : confirme explicitement en §4.1 que
  **« Port\_Armel » est le nom du hotspot mobile du téléphone**, pas un réseau
  distinct — déjà testé avec succès par le passé (IPv6 disponible). Procédure
  standard de vérification documentée (§6), pièges connus (§7) : notamment,
  aucun test de tunnel n'est possible depuis le réseau domestique, et PC4 ne
  répond jamais à un `ping6` direct (echoreq bloqué côté `pf`).
- `BOX-SFR-GR140IG-Addendum-20260823.md` : confirme que le WAN de la box SFR
  est IPv6 seul — l'IPv4 ne fonctionnera jamais pour l'accès distant.

**Nouveau diagnostic précis (commandes demandées) :** mêmes résultats que
précédemment — aucune IPv6 globale, `ping6` en échec, DNS `AAAA` toujours
correct. Réseau confirmé identique au hotspot documenté comme fonctionnel par
le passé — pas un réseau différent.

---

## 4. Fausse piste écartée par hprzeta — la vraie cause était Proton VPN

**Message de hprzeta :** correction du diagnostic précédent — le blocage IPv6
venait de **Proton VPN**, pas de l'opérateur mobile. Preuve donnée : coupure de
Proton VPN → IPv6 globale revenue immédiatement (`2a02:8440:...`), `wg0` a
handshaké, `ping 10.10.0.1` répond (58 ms, 0 % perte). L'accès distant
fonctionne, Proton coupé.

**Deux consignes données pour la suite :**
1. Ne pas remettre `wg_auto.sh` en pause — le script fonctionne correctement,
   le spam de la soirée venait uniquement de l'absence d'IPv6 (causée par
   Proton), pas d'un bug du script.
2. Améliorer `wg_auto.sh` (v2) pour qu'il ne spamme plus quand il n'y a pas
   d'IPv6 : garde à ajouter avant toute tentative de réparation/notification.

---

## 5. Correctif `wg_auto.sh` v2 — garde IPv6

Diff montré et validé avant application (backup `wg_auto.sh.bak-20260905-
avant-v2` créé). Principe : en déplacement, avant toute action, vérifier la
présence d'une IPv6 globale (`ip -6 addr show scope global`). Si absente :
sortie silencieuse (aucun `wg-quick`, aucun `notify-send`, une seule ligne de
log). Si présente : comportement identique au 30/08.

**Vérifications effectuées après application :**

| Test | Résultat |
|---|---|
| `wg_auto.sh --quiet`, tunnel déjà OK | Silencieux, log inchangé |
| `wg_auto.sh` (normal), tunnel déjà OK | Une seule notification « WireGuard OK », pas de réparation |
| Tunnel avant/après les tests | Stable, 0 % perte, ~42-45 ms |

**Committé** (`23dce34`, "auto-réparation handshake + garde IPv6 avant
notif/action"), poussé sur `Riemann_Lab_C`.

---

## 6. Intégration wiki — nouveau guide fourni par hprzeta

hprzeta a fourni un guide rédigé (`Guide-WireGuard-Acces-Distant-20260905.md`,
TL;DR + niveaux débutant→expert + procédure de dépannage + commandes +
checklist), avec instruction d'intégration dans le wiki : créer le guide en
page publique (placeholders `<...>`, zéro secret), fusionner avec
`Diagnostic-WireGuard-Hotspot.md` si doublon, enrichir `Guide-Linux-
Commandes.md` et `STACK.md`, montrer chaque diff avant push.

**Travail réalisé (diffs montrés avant application) :**

| Fichier | Action |
|---|---|
| `Guide-WireGuard-Acces-Distant.md` | Créé (nouveau), page publique, §0-§6 |
| `Diagnostic-WireGuard-Hotspot.md` | §9 ajouté (incident Proton), renvoi croisé vers le nouveau guide plutôt que duplication |
| `Guide-Linux-Commandes.md` | §28 ajouté (commandes de diagnostic IPv6 vs VPN tiers) |
| `STACK.md` | Avertissement Proton VPN ajouté à la fiche cluster |
| `JOURNAL.md` | Nouvelle entrée datée, chronologie complète de la session (y compris la fausse piste) |
| `Architecture-Cluster-Zeta.md` | Modifications du 30/08, trouvées déjà présentes non commitées, incluses au même commit |

**Point de transparence signalé à hprzeta** : le dépôt wiki contenait déjà des
modifications non commitées depuis le 30/08 (mêlées aux fichiers touchés ce
soir) — un seul commit couvrant les deux dates a été proposé et validé plutôt
qu'un découpage artificiel par `git add -p`.

Vérification anti-secret effectuée avant publication (aucun hostname réel,
aucune clé, aucun token dans le nouveau guide public). **Committé**
(`a73ed56`), poussé sur le wiki `master`.

---

## 7. Nettoyage des fichiers locaux non commités sur `Riemann_Lab_C`

**Demande de hprzeta :** lister les documents locaux importants non commités.

**Catégorisation présentée** (backups, archives `.zip`, archives de session,
images, logs, scripts fonctionnels, rapports PDF, documents marqués privés) —
détail complet dans la réponse à l'écran, non reproduit ici.

**Commit 1** (`de2ac31`, poussé) — scripts fonctionnels + rapport PDF + images
+ logs de suivi : `scripts/zeta_point_maj.sh`, `scripts/zeta_temp_monitor.py`,
`pdf/clone/generate_pdf_maj.py` + `MAJ_clone_ubuntu_20260824.{md,pdf}`,
`docs/images/flux_local_vs_cloud.svg` + `monitoring_3_outils.svg`,
`logs/suivi_run_T5M.md` + `suivi_run_T5M_v16_20260816.md`.

**Commit 2** (`0f5ad17`, poussé) — les 6 archives de discussion Claude Code
(`.md`+`.pdf`, 08-19/08-22/08-23/08-30/09-02/09-05). Contrôle anti-secret
effectué avant commit (recherche de tokens/clés/mots de passe dans les 6
transcripts) : uniquement des mentions narratives d'incidents déjà connus et
déjà corrigés, aucune valeur réelle exposée.

**Exclus volontairement, laissés non commités :**
- `BOX-SFR-GR140IG-Addendum-20260823.md` et `RAPPORT-SESSION-RESEAU-20260823-
  v2.md` — marqués usage privé (données réseau sensibles).
- Archives `.zip` et fichiers `.bak*` — suppression proposée puis **refusée
  par hprzeta** (« ne supprime pas »), rien touché.

---

## 8. Point projet et mise à jour du Handoff

**Demande de hprzeta :** « point projet », puis mise à jour du Handoff avec le
volet réseau et ce qui a été corrigé/restauré.

Le bloc `PROMPT_REPRISE` de `~/riemann_handoff/Handoff.md` a été affiché tel
quel (mécanisme standard), résumé en 3 lignes, puis mis à jour : un nouveau
bloc daté a été ajouté en tête, couvrant l'intégralité du volet réseau de la
soirée (fausse piste, cause réelle, correctif v2, wiki, nettoyage des
fichiers, éléments toujours non commités) — l'ancien bloc MARGE=10.0 (volet
calcul, session de l'après-midi) reste inchangé juste en dessous.

---

## 9. Vérification du fichier `Pass-20260819...zip`

**Demande de hprzeta :** vérifier moi-même le contenu de ce zip avant toute
décision, suspecté de contenir un export de mots de passe.

**Analyse effectuée** (extraction dans un dossier temporaire isolé, supprimé
immédiatement après inspection) :
- Le zip contient 12 captures d'écran datées du 27-28/06/2026 (apps WireGuard,
  ConnectBot, Termius, Samsung Notes) et un fichier texte à un seul champ.
- Ce fichier s'est révélé être au **format exact d'une clé WireGuard** (44
  caractères base64, padding correct) — vérifié différent de la clé publique
  déjà connue de PC1.
- Sur demande explicite de hprzeta de vérifier si cette clé est encore active :
  la clé publique dérivée localement correspond exactement au peer téléphone
  (`10.10.0.3`) documenté dans le wiki. Vérification en direct sur PC4 (`doas
  wg show wg0`, lancé par hprzeta lui-même car nécessitant un mot de passe
  interactif) : **le peer est toujours configuré**, mais sans aucun handshake
  récent enregistré.

**Décision de hprzeta :** ne rien changer sur PC4 ni régénérer la clé pour
l'instant (contexte : instabilité constatée sur PC4/zeta-cluster). Ne jamais
committer ce zip.

**Protection ajoutée** : règle `.gitignore` pour
`docs/archive/Pass-20260819T194523Z-1-001.zip`, committée (`b997445`) et
poussée sur `Riemann_Lab_C`.

---

## 10. Clôture de session

**Demande de hprzeta :** « bye bye »

**Résumé des hash de fin de session :**

| Dépôt | HEAD |
|---|---|
| `Riemann_Lab_C` | `b997445` (poussé) |
| Wiki `master` | `a73ed56` (poussé) |

**Fichiers mis à jour cette session :** `scripts/wg_auto.sh` (v2, `23dce34`),
6 fichiers wiki (`a73ed56`), 21 fichiers locaux triés/commités (`de2ac31`,
`0f5ad17`), `.gitignore` (`b997445`), `~/riemann_handoff/Handoff.md` (local,
hors dépôt), cette archive.

**Volontairement non touché** : `wg0.conf` (Endpoint DuckDNS + `AllowedIPs=
10.10.0.0/24`, état du 30/08), toutes les clés WireGuard, le token DuckDNS, le
peer téléphone sur PC4, les archives `.zip`/`.bak*` restantes,
`scripts/zeta_monitor.py`/`zeta_tmux.sh` (modifications jump-host antérieures,
non retouchées).

**Reste ouvert pour la prochaine session :**
- Décider du sort des `.zip` perso/CV et des `.bak*` restants (16 fichiers).
- Décider si la clé WireGuard du peer téléphone doit être régénérée.
- Committer ou nettoyer `scripts/zeta_monitor.py`/`zeta_tmux.sh`.
- Item hérité : régénération clé WireGuard PC4 + token DuckDNS (action
  hprzeta).
- Volet calcul (Objectif 1) : décider si le test A/B `scan_arb.c` doit être
  lancé (voir archive de l'après-midi, `discusion_claude_2026-09-05.md`).

---

*Document généré à la demande de hprzeta le 05/09/2026 (soirée) — archive de
session, Claude Code — Riemann_Lab, branche `Riemann_Lab_C`.*
