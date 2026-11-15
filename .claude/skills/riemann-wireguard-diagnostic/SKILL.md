---
name: "riemann-wireguard-diagnostic"
description: "Diagnostic du tunnel WireGuard du cluster Riemann_Lab (PC4 bastion, PC1, téléphone). Utiliser dès qu'un tunnel ne monte pas, qu'il n'y a pas de handshake, que le Tx monte et le Rx reste à 0, qu'un client seul (téléphone, PC1) échoue alors qu'un autre fonctionne, que l'accès distant est impossible en déplacement ou sur partage 4G, que PC1 affiche « No such device », ou après une rotation de clé, un changement de box, d'IPv6 ou de DDNS. Diagnostic seulement : toute modification de PC4 relève du skill riemann-bastion-hardening."
---

# Diagnostic du tunnel WireGuard du cluster Zêta

Skill de **diagnostic** : trouver la cause d'un tunnel qui ne monte pas, sans rien modifier. Le détail et
l'historique des incidents sont dans le wiki (ne pas les recopier) :
`Diagnostic-WireGuard-Hotspot` (§1 à §10), `Guide-WireGuard-Acces-Distant` (§4),
`Guide-Linux-Commandes` (§5, §6, §8, « Leçons importantes »).

**Règles.**
- **Claude Code ne lance aucune commande sur PC4** (`doas` demande un mot de passe) : il **donne** les commandes,
  hprzeta les lance et colle les sorties. Tout fait de PC4 issu d'une sortie collée est « **rapporté** » ; ce que
  Claude Code mesure lui-même (PC1, wiki, fichiers locaux) est « **mesuré** ».
- **Aucune valeur sensible** : gabarits `[DDNS_PC4]`, `[IP_PC4]`, `[WG_PC4]`, `DÉBUT_DE_LA_CLÉ` (8 caractères au plus) ;
  jamais une clé entière, une PSK, un jeton, une adresse ni un nom DDNS. Voir l'hygiène des sorties dans
  `riemann-bastion-hardening` §11.
- **STOP avant toute modification.** Les modifications de PC4 se font avec `riemann-bastion-hardening`.
- Les commandes qui **coupent un tunnel** se donnent « à la console » ou par le LAN, jamais par le tunnel
  (observé le 15/11 : la session SSH qui passait par le tunnel s'est figée quand on a coupé le client).

---

## 1. Première question : tous les clients échouent, ou un seul ?

| Constat | Où chercher | Modes |
|---|---|---|
| **Tous** les clients échouent (PC1 et téléphone) | PC4, box, DDNS, pare-feu | n°1, n°2 |
| **Un seul** client échoue alors qu'un autre passe par le même chemin et la même clé de PC4 | **ce client** (sa config, sa résolution de nom, un VPN tiers, son script) | n°4, n°5, n°6 |
| Un **pair** précis n'a pas de données mais un handshake | config de ce pair sur PC4 (`AllowedIPs`) | n°3 |

**Exceptions à noter** (la dichotomie n'est pas étanche) :
- **n°3** est une config de **PC4**, mais elle ne touche qu'**un pair** : « un seul client échoue » ne suffit pas à
  exclure PC4, il faut lire `wg show` côté PC4.
- **n°4** est côté **PC1** (script de reprise, démarrage avant le réseau) même quand « tous les nœuds distants »
  sont injoignables **depuis PC1**.
- **n°5** est côté client mais touche **tous** les tunnels de ce client.

## 2. Les 6 modes de panne du wiki

| n° | Mode (wiki) | Symptôme | Test qui tranche | Correctif |
|---|---|---|---|---|
| 1 | Règle IPv6 de la box périmée (§2) | aucun handshake, tous clients, DNS correct | `dig +short AAAA [DDNS_PC4]` comparé à la destination de la règle « Réseau v6 » de la box | mettre la règle de la box à jour (depuis le **LAN**) ; structurel dès que l'IPv6 de PC4 change |
| 2 | Routage désactivé sur PC4 (§3) | handshake OK, PC4 répond, PC2/PC3 injoignables | `doas sysctl net.inet.ip.forwarding` (=0) | `net.inet.ip.forwarding=1` persistant dans `/etc/sysctl.conf` ; à revérifier après réinstallation |
| 3 | `AllowedIPs` vide ou doublon (§4, juillet) | handshake OK, **aucune donnée** pour un pair | `doas wg show wg0` : `allowed ips: (none)` ou une IP en doublon | retirer la ligne `wgaip` en trop de `hostname.wg0` ; handshake ≠ transport |
| 4 | Tunnel non résilient en déplacement (§8, **PC1**) | `wg0` monté sans IP, nœuds fixes en `No route to host` | `ping -c2 [WG_PC4]` (pas `wg show`) | ping de santé, `AllowedIPs` réduit au réseau WG, `ProxyJump`, `After=network-online.target` |
| 5 | VPN tiers (Proton) (§9) | en déplacement, aucune IPv6 globale (`fe80::` seul), pas de handshake | `ip -6 addr show \| grep -v fe80` (doit montrer une globale) | couper le VPN tiers |
| 6 | **Enregistrement `A` périmé** préféré par WireGuard Android (§10, 15/11) | téléphone : **Tx monte, Rx à 0** ; PC4 : pair du téléphone `tx: 0, rx: 0` ; PC1 fonctionne | `dig` compté : `A: 1` (devrait être 0) ; endpoint en **IPv6 littérale** : le tunnel monte | effacer le `A` (`riemann-bastion-hardening` §7), endpoint du téléphone sur le **nom** |

Notes :
- Mode 6 : cause **retenue par recoupement**, pas prouvée dans le code de l'appli. **Non élucidé** : pourquoi un `A`
  existait le 15/11 alors qu'il avait été supprimé le 22/08.
- Mode 4 / démarrage : `wg-quick@wg0` de PC1 est **`failed` au démarrage de 11:32 le 15/11**, cause **non élucidée** ;
  le wiki décrit un cas voisin (§8 E1, démarrage avant le réseau) : piste **non vérifiée** pour le 15/11.
- Un pair inutile ou inconnu : ne pas le laisser (surface) ; voir la rotation dans `riemann-bastion-hardening` §10.

## 3. Ordre de diagnostic (wiki §6, Guide §4)

1. **Santé réelle du tunnel** : `ping -c2 [WG_PC4]` depuis le client. Un `wg show` sain ne prouve rien (handshake
   ≠ transport, wiki §7d, §7f).
2. **Un seul client ?** (§1 ci-dessus) puis le test du mode soupçonné.
3. **DNS et règle box** (mode 1), **forwarding** (mode 2), **`AllowedIPs`** (mode 3).
4. **Tester depuis l'extérieur** : jamais depuis le réseau domestique (le hook de PC1 coupe `wg0` à la maison).
   Ordre à respecter : modifier la box (sur le LAN) → basculer sur un partage de 4G → monter le tunnel.

## 4. Tests sans valeur sensible

| Test | Machine | Ce qu'on lit | État |
|---|---|---|---|
| `doas ifconfig wg0 \| grep -A3 'wgpeer DÉBUT_DE_LA_CLÉ'` | PC4 | `tx`/`rx` et `last handshake` d'un pair ; `tx: 0, rx: 0` sans `last handshake` = **aucun paquet valide reçu** de ce pair | testé le 15/11 (rapporté) |
| `sudo wg show wg0 latest-handshakes` | PC1 | clé publique et heure du handshake (époque Unix) ; `date -d @N` pour la lire ; **pas d'endpoint** | testé le 15/11 (mesuré) |
| `for t in A AAAA; do echo "$t: $(dig +short $t [DDNS_PC4] \| grep -c .)"; done` | PC1 ou PC4 | nombre d'enregistrements, **aucune adresse** (attendu `A: 0`, `AAAA: 1`) | testé le 15/11 |
| **Endpoint en IPv6 littérale** entre crochets `[…]:51820` (téléphone : champ « Point de terminaison » ; PC1 : `sudo wg set wg0 peer … endpoint […]:51820`, test temporaire) | client | si le tunnel **monte**, le problème est la résolution du nom ; crochets obligatoires (le `:` est ambigu) | téléphone : testé le 15/11 (rapporté) ; PC1 : wiki Guide §5 |
| `ip -6 addr show \| grep -v fe80` | client | présence d'une IPv6 **globale** (mode 5) | wiki §9 |

**Capture réseau sur PC4** (à donner à hprzeta ; le fichier contient des **adresses**) :
```
# Lancement, en arrière-plan (re0 = interface Ethernet de PC4) — testé le 15/11 (rapporté)
doas sh -c 'nohup tcpdump -n -i re0 -w /tmp/wg_test.pcap udp port 51820 >/dev/null 2>&1 & echo $! > /tmp/wg_test.pid'
pgrep -l tcpdump          # vérifier ; arrêt : doas kill $(cat /tmp/wg_test.pid)

# Relecture SANS afficher d'adresse : le masque remplace chaque IPv6 par IPV6
F=/tmp/wg_test.pcap
doas tcpdump -n -r $F 2>/dev/null | sed -E 's/([0-9a-f]{1,4}:){4,}[0-9a-f]{0,4}/IPV6/g' | head -8

# Paquets REÇUS par PC4 (le client est la source, PC4 la destination = port 51820) / ENVOYÉS
doas tcpdump -n -r $F 2>/dev/null | grep -c '\.51820: '
doas tcpdump -n -r $F 2>/dev/null | grep -c '\.51820 > '

# Par minute, PORT SOURCE et TYPE [wg], paquets reçus seulement (aucune adresse dans la sortie)
doas tcpdump -n -r $F 2>/dev/null | grep '\.51820: ' | awk '{split($2,a,"."); print substr($1,1,5), a[2], $6}' | sort | uniq -c
```
- **Format de sortie testé le 15/11** (rapporté) : `351 16:11 40272 data`, `1 16:15 34442 initiation`,
  `1 16:15 34442 keepalive`, `700 16:16 34442 data`. Types **observés** : `data`, `initiation`, `keepalive` ;
  `response` n'a pas été vu. L'écriture de la commande ci-dessus a été vérifiée sur des lignes d'exemple.
- Les paquets **reçus** portent `[class 0x20]` (observé le 15/11). **Un port source = une session** : nouveau
  port et nouveaux identifiants `0x…` = nouveau handshake ; un `nonce` croissant = session déjà établie.
- **Couper les autres clients pendant la capture**, par le **LAN** ou la console de PC4, pas par le tunnel. Sinon
  le trafic de PC1 noie celui du téléphone et la session SSH qui passait par le tunnel se fige.
- **Lecture** : aucun paquet du client → ils n'atteignent pas PC4 (**vu le 15/11, rapporté** : entre 16:12 et 16:14,
  aucun paquet du téléphone, seul PC1 apparaissait ; ce constat a orienté vers le mode n°6) ; des `initiation` sans
  `response` → clé ou PSK refusées (**non vu en cas réel**).
- **Effacer** dès l'analyse : `doas rm -P /tmp/wg_test.pcap /tmp/wg_test.pid` (HDD : fiable).

## 5. Faux positifs connus (ne pas conclure à une panne)

| Piège | Pourquoi |
|---|---|
| `wg show` : **« No such device »** sur PC1 à la maison | un hook `nm-dispatcher` coupe **volontairement** `wg0` sur le Wi-Fi de la box (« MAISON — WireGuard DÉSACTIVÉ »). Le service reste `active (exited)` : état **périmé** par construction. Ne pas relancer `wg-quick` à la main (wiki §7c) |
| Icône **clé** d'Android affichée | elle indique que le VPN du système est actif, **pas** que le tunnel est monté (observé le 15/11 : icône présente avec Rx à 0) |
| `code=$?` d'un script | un script qui finit par `echo` renvoie 0 même si `ftp` a échoué : lire le journal |
| `tcpdump -tttt` | **OpenBSD : écart entre paquets** (`man tcpdump`) ; Linux : date complète |
| `grep udp` sur une capture WireGuard | `tcpdump` affiche `[wg] data` : le compte vaut 0 à tort |
| Handshake récent | ne prouve pas que les données passent (wiki §7d, §7f) : tester `ping [WG_PC4]`, SSH |
| `ping6` vers PC4 silencieux | `pf` n'autorise pas `echoreq` (wiki §7b) |
| `nc -u … succeeded` | UDP : « succeeded » dès qu'aucun ICMP d'erreur ne revient (wiki §7a) |
| `No route to host` sur `192.168.1.x` en déplacement | PC1 est hors du LAN maison, pas une panne du cluster (wiki §7e) |
| `diff` entre une config WireGuard et sa sauvegarde | afficherait une PSK : interdit |
| `find / -xdev` pour chercher une capture | ne traverse pas `/tmp`, `/var`, `/home` (partitions séparées) |

## 6. Format de sortie

1. **Verdict** : 🟢 tunnel sain / 🟡 cause probable à confirmer / 🔴 accès en danger → STOP.
2. **Tableau des tests** : `test | résultat | rapporté ou mesuré | lecture`.
3. **Cause** : **prouvée**, **retenue par recoupement** (avec ce qui manque pour la prouver) ou **non élucidée**.
   Ne jamais inventer : une observation non testée s'écrit « non testé ».
4. **STOP** avant toute modification ; renvoi vers `riemann-bastion-hardening` pour PC4 (rotation de clé §10,
   DuckDNS §7).
5. Un diagnostic abouti se range et se publie selon `riemann-zeta-diagnostic` (dossier privé, gabarit, index,
   copie publiable sans IP) ; les causes passent au wiki (`Diagnostic-WireGuard-Hotspot`).

---
*Skill du projet Riemann_Lab · diagnostic du tunnel WireGuard du cluster · Auteur : hprzeta · MAJ : 15/11/2026 · 135 lignes*
