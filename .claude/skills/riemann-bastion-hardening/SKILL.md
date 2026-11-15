---
name: "riemann-bastion-hardening"
description: "Durcissement, allègement et maintenance du bastion OpenBSD PC4 (zeta-secure) du cluster Riemann_Lab. Utiliser dès qu'on met à jour, nettoie, sécurise, patche (syspatch) ou reboote PC4, ou avant toute intervention sur le VPN WireGuard, pf, sshd, le DDNS DuckDNS (duck.sh, enregistrements A/AAAA, journal, newsyslog) ou les services OpenBSD du bastion ; pour la rotation de la clé WireGuard de PC4 et l'hygiène des sorties (clés, PSK, jetons, captures). Une panne de tunnel qui ne monte pas relève du skill riemann-wireguard-diagnostic."
---

# Riemann Bastion Hardening — PC4 (zeta-secure, OpenBSD)

Skill de durcissement et de maintenance du **bastion Internet** du cluster Zêta. Il encode les
**incidents réels** rencontrés (boucle smtpd 34 j, `/var` saturé à 11,4 Go, cron DuckDNS spammant
root, rotation de la clé WireGuard du 15/11) pour qu'ils ne se reproduisent pas, et fixe les règles
de sécurité d'un bastion exposé.

> PC4 = `zeta-secure` · OpenBSD 7.9 · LAN `[IP_PC4]` · tunnel `[WG_PC4]` (valeurs réelles : `~/.ssh/config` et doc privée, jamais dans le dépôt) · `doas` (pas sudo).
> Rôle unique : router WireGuard (wg0) + filtrer (pf) + admin SSH. Tout le reste est superflu.
>
> **`doas` demande un mot de passe sur PC4 : Claude Code n'y lance AUCUNE commande.** Les commandes
> sont **données** à hprzeta, qui les lance lui-même et colle les sorties. Tout fait de PC4 issu
> d'une sortie collée est écrit « **rapporté** » : il n'a pas été revérifié par Claude Code.
>
> Auteur : hprzeta · Mise à jour : 15 novembre 2026

---

## 1. Règle d'or

**Un bastion ne fait que 3 choses : VPN (wg0), pare-feu (pf), admin (sshd).**
Tout service qui n'y contribue pas est une **surface d'attaque** à couper.
Et : **on audite AVANT de couper** (jamais l'inverse) — un `rcctl stop`/`disable` par service,
avec vérification à chaque fois.

---

## 2. À GARDER (ne jamais désactiver)

| Service | Rôle |
|---|---|
| `sshd` | seul accès admin (durci, cf. §5) |
| `pf` + `pflogd` | pare-feu + son log (traçabilité) |
| wg0 (via `/etc/hostname.wg0` + `/etc/wireguard/privatekey`) | le tunnel VPN lui-même (détail ci-dessous) |
| `ntpd` | horloge — **vital** pour VPN et cohérence des logs |
| `cron` | DuckDNS (DDNS) — cf. §7 |
| `slaacd` + `dhcpleased` | autoconf réseau ; **slaacd = IPv6, la porte d'entrée VPN** |
| `syslogd` | logs système |
| `library_aslr` | protection sécurité (randomisation) — c'est une défense, pas un extra |

**Comment wg0 est configuré sur ce PC4 (rapporté le 15/11/2026).** `/etc/hostname.wg0` ne contient
**pas** de ligne `wgkey` : la clé privée est dans le fichier séparé `/etc/wireguard/privatekey`
(600 root:wheel, 45 octets), chargé par une ligne de la forme
`!/usr/local/bin/wg set wg0 private-key /etc/wireguard/privatekey listen-port 51820 peer … allowed-ips …`
qui définit aussi le **1er pair**. Les **autres pairs** sont des lignes `wgpeer … [wgpsk …] wgaip …`.
`grep -c 'wgpeer '` ne compte donc **pas** le pair de la ligne `wg set`.

## 3. À COUPER (inutile au bastion)

Méthode : `doas rcctl stop <svc>` puis `doas rcctl disable <svc>` (persistant, survit au reboot ;
une MaJ ne réactive JAMAIS un service désarmé).

| Service | Pourquoi couper | Statut au 26/09/2026 |
|---|---|---|
| `smtpd` | serveur mail — cause de la boucle de bounces 34 j | ✅ coupé + masqué |
| `sndiod` | serveur audio — headless, aucun son | ✅ coupé |
| X11 / xenodm | pas d'interface graphique sur un bastion | absent (install propre) |
| paquets desktop (`desktop-file-utils`, etc.) | tirent pcre2/xz/python inutiles | à purger si présents |
| NFS / portmap, `vmd`, `iked` (si non utilisés) | services réseau non nécessaires | vérifier avant |

Vérifier la **surface d'attaque** après coupe :
```
doas netstat -na -f inet | grep LISTEN
doas netstat -na -f inet6 | grep LISTEN
```
→ Cible bastion sain : **seul le port 22 (SSH) en écoute TCP** ; wg0 = 51820/UDP (n'apparaît pas en LISTEN, normal).

---

## 4. À NE JAMAIS TOUCHER / NE JAMAIS METTRE À JOUR

| Élément | Pourquoi |
|---|---|
| **`sysupgrade`** (7.9 → 8.0) | change la VERSION d'OS → risque de casser pf/wg. Opération manuelle planifiée, JAMAIS via le script auto. Le `zeta-update` ne fait QUE `syspatch` + `pkg_add -u`. |
| **`/etc/pf.conf`** sans test | une règle cassée = plus d'accès. Toujours `doas pfctl -nf /etc/pf.conf` (test) AVANT `doas pfctl -f`. |
| **`/etc/hostname.wg0`** | config des pairs : la ligne `wg set` (1er pair) et les `wgpeer`, dont des **PSK** (`wgpsk`, secrets) ; toujours `doas cp -p` en `.bak` avant édition, **jamais `cat`/`diff`** (cf. §11). wg0 remonte au boot grâce à ce fichier. |
| **Clés WireGuard** : `/etc/wireguard/privatekey` (privée, 600), `publickey` (644) | changer la clé de PC4 change sa clé **publique** : il faut re-provisionner TOUS les pairs (PC1 + téléphone). Procédure complète : **§10**. |
| **Réseau/pf via le tunnel** | ne JAMAIS modifier pf/réseau à distance via wg0 → on se coupe l'accès. Interventions bastion = **en LAN, à la maison**. |
| `net.inet.ip.forwarding=1` (dans `/etc/sysctl.conf`) | routage VPN. Ne pas retirer — vérifier qu'il persiste. |

---

## 5. Durcissement SSH (le seul port ouvert)

Acquis au 26/09/2026 dans `/etc/ssh/sshd_config` :
```
PermitRootLogin no
PasswordAuthentication no          # clé UNIQUEMENT
KbdInteractiveAuthentication no
AllowUsers hprzeta
```

**Procédure filet de sécurité (ne jamais se verrouiller) :**
1. Vérifier d'abord que la clé marche : `ssh -v zeta-secure exit 2>&1 | grep "Authentication succeeded"` → doit dire **publickey**.
2. `doas cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak-$(date +%Y%m%d)`
3. Ajouter/éditer les 4 lignes ci-dessus.
4. **Tester la conf** : `doas sshd -t` → doit être silencieux (= valide). Si erreur, STOP.
5. `doas rcctl reload sshd` — **garder la session courante ouverte**.
6. Dans un **2ᵉ terminal**, tester une NOUVELLE connexion : `ssh zeta-secure "whoami"`.
7. OK → fermer l'ancienne. KO → restaurer le `.bak` depuis la session restée ouverte.

> La **console physique** de PC4 accepte toujours le mot de passe (voulu, pour l'urgence).
> Le durcissement ne concerne que l'accès réseau. L'écran affiche `login:` en permanence — normal, headless, on n'y touche pas.

---

## 6. Piège majeur — `/var` plein bloque syspatch (incident 26/09)

**Symptôme** : `syspatch` échoue avec `/var: write failed, file system is full` +
`Failed to create rollback patch`. La MaJ avorte **proprement** (rien d'installé à moitié),
mais aucun patch ne passe.

**Cause réelle** : `smtpd` en boucle 34 j → `syslogd` a gonflé `/var/log/maillog.1` à **11,4 Go**
(la rotation `newsyslog` n'a pas pu compresser faute de place → cercle vicieux).

**Réparation :**
```
df -h                                   # /var à 100%+ ?
doas du -sh /var/* | sort -rh | head    # coupable = /var/log
doas du -ah /var/log | sort -rh | head  # -> maillog.1 (ou messages)
doas rm -f /var/log/maillog.1           # supprimer le vieux log (sans valeur)
df -h /var                              # doit retomber ~1%
```

**Protection définitive** — plafonner la taille dans `/etc/newsyslog.conf` (4ᵉ colonne = Ko max,
remplace le `*` "illimité") :
```
/var/log/maillog          640  7   512  24  Z
```
⚠️ Éditer avec de VRAIS espaces/tabs — un `sed` avec `\t` a produit `maillogttt640` (ligne cassée).
Valider : `doas newsyslog -n` (dry-run, sans erreur).

### Disque et partitions de PC4 (inventaire du 11/11/2026)

- Disque **dur mécanique** (HDD Hitachi) : `rm -P` y est fiable (`man rm` : écrasement une fois, à
  condition que le support écrive « en place » ; **pas garanti sur SSD/flash** ; fichiers à liens
  multiples dissociés mais non écrasés).
- Partitions **séparées** : `/`, `/home`, `/tmp`, `/usr`, `/var` (+ `/usr/local`, `/usr/obj`, `/usr/src`).
  **`find / -xdev` ne traverse pas ces partitions** : nommer chaque point de montage
  (`doas find /tmp /var /home /root -xdev …`). Vérifier avec `df -h`.

---

## 7. Cron DuckDNS — état au 15/11/2026 (incident 26/09 : ne pas spammer root)

Cron root (rapporté) : `*/5 * * * * /etc/duckdns/duck.sh >> /var/log/duckdns.log 2>&1`. La sortie doit
être redirigée, sinon `ftp` affiche sa progression → mail à root → bounces (smtpd) → boucle.

**Ligne d'envoi de `/etc/duckdns/duck.sh`** (700 root:wheel, 279 octets, rapporté ; l'IPv6 est extraite de `re0`) :
```
ftp -V -o /var/log/duckdns.log "https://www.duckdns.org/update?domains=[DDNS_NOM]&token=TOKEN&ip=&ipv6=${IP6}" 2>/dev/null || echo "$(date) : echec ftp" >&2
```
- `-V` coupe la verbosité : sans elle, en cas d'erreur, `ftp` recopie l'**URL (donc le jeton)** sur la
  sortie d'erreur, que le cron ajoutait au journal. `2>/dev/null` masque ces messages ; en échec, une
  seule ligne propre `… : echec ftp`.
- **`ftp -o` n'écrase pas le fichier en cas d'échec** (constaté le 15/11) : un `OK` en fin de journal ne
  prouve pas que le **dernier** passage a réussi. Lire `echec ftp` et l'**heure** du fichier.
- Journal `/var/log/duckdns.log` en **600 root:wheel**, plafonné par `/etc/newsyslog.conf` :
  `/var/log/duckdns.log root:wheel 600 4 64 * Z` ; contrôle : `doas newsyslog -nv`
  (`size (KB): 0.04 [64] --> skipping` = sous le plafond).
- **Un 502 est un raté du serveur DuckDNS, pas un refus du jeton** (O8a).

**Le nom DDNS ne doit porter AUCUN enregistrement `A`.** La box n'accepte que l'IPv6 en entrée ; un `A`
périmé est **préféré par l'appli WireGuard Android** et envoie ses paquets dans le vide (mode n°6,
15/11 — voir `riemann-wireguard-diagnostic`).
```
# Contrôle (compte seulement, aucune adresse) — attendu : A: 0 et AAAA: 1
for t in A AAAA; do echo "$t: $(dig +short $t [DDNS_PC4] | grep -c .)"; done

# Effacer le A sans afficher le jeton : clear=true efface A ET AAAA -> enchaîner TOUT DE SUITE duck.sh
doas sh -c 'U=$(grep -o "token=[^&\"]*" /etc/duckdns/duck.sh | head -1); D=$(grep -o "domains=[^&\"]*" /etc/duckdns/duck.sh | head -1); ftp -V -o - "https://www.duckdns.org/update?${D}&${U}&clear=true" 2>/dev/null; echo; /etc/duckdns/duck.sh; tail -c 3 /var/log/duckdns.log'
# attendu : OK (effacement) puis OK (republication)
```
- Doc DuckDNS : la détection automatique de `ip` ne concerne que l'IPv4 ; `ipv6=` renseigné la
  désactive. **Non élucidé** : pourquoi un `A` existait le 15/11 alors qu'il avait été supprimé le 22/08.
- **`ftp -6` est inutilisable** : essayé le 15/11, échec ; `ping6` vers le serveur DuckDNS répond « no
  address associated with name » (le résolveur de PC4 ne renvoie pas d'`AAAA` pour lui). Cause non creusée.
- Contrôle de fin de journée : `doas grep -c 'echec ftp' /var/log/duckdns.log` et `doas ls -l /var/log/duckdns.log`.
- ⚠️ `duck.sh` contient le **jeton en clair** dans l'URL (visible brièvement dans `ps` à l'exécution).
  Ne jamais l'afficher ; s'il a fui, le régénérer sur le tableau de bord DuckDNS (le jeton ne passe jamais
  par Claude Code), puis le mettre à jour. Une sauvegarde `.bak` de `duck.sh` contient le jeton : `rm -P` après usage.

---

## 8. Mise à jour de PC4 — procédure sûre

1. **À la maison (LAN)** uniquement — accès direct garanti même si le tunnel tombe.
2. Vérifier la santé AVANT : `ssh -t zeta-secure "uptime; top -b -n1 | head -12"` — charge ~0 attendue ;
   une charge anormale = un service s'emballe (cf. §6) → régler d'abord.
3. Check : `zeta-update --only "PC4"` (n'installe rien ; liste syspatch + pkg_add -n).
4. Vérifier que `/var` a de la place (`df -h /var`) AVANT l'apply.
5. Apply : `zeta-update --apply --only "PC4"` → `syspatch` + `pkg_add -u` (JAMAIS sysupgrade).
6. Si `Relinking to create unique kernel... reboot to load` → **patch noyau, reboot requis**.
7. **Avant reboot**, vérifier que tout est persistant :
   ```
   doas pfctl -si | grep Status                 # Enabled
   doas sysctl net.inet.ip.forwarding            # =1
   doas grep forwarding /etc/sysctl.conf         # =1 (persistant)
   ls -l /etc/hostname.wg0                        # existe (wg0 au boot)
   doas wg show wg0                               # interface + peers
   doas ifconfig wg0 | grep -E 'wgpubkey|wgpeer'  # clé publique = contenu de /etc/wireguard/publickey ; nombre de pairs attendu
   ```
8. `ssh -t zeta-secure "doas reboot"` → attendre ~60 s.
9. **Vérif post-reboot** : `uptime` récent, pf `Enabled`, forwarding `=1`, wg0 up, **`doas ifconfig wg0 |
   grep -E 'wgpubkey|wgpeer'` identique à l'avant-reboot** (même clé publique, mêmes pairs — relevé le 15/11 après
   un redémarrage non planifié de PC4, rapporté ; durée d'activité non vérifiée), sshd durci, smtpd/sndiod `failed` (= off), `/var` ~1%,
   `sysctl kern.version` (nouveau noyau).

> `doas rcctl check <svc>` renvoie `failed` pour un service ARRÊTÉ — c'est le résultat attendu
> pour smtpd/sndiod désactivés, pas une erreur.

---

## 9. Format de sortie d'une intervention bastion

1. **Verdict** : 🟢 sain / 🟡 corriger d'abord / 🔴 accès ou VPN en danger → STOP.
2. **Findings** (service, charge, disque, port ouvert) — sans recopier de token/clé. **Chaque fait de PC4
   issu d'une sortie collée est marqué « rapporté »** ; un fait mesuré par Claude Code (PC1, wiki, fichiers
   locaux) est marqué « mesuré ».
3. **Actions ordonnées** : audit → coupe service par service → vérif → (reboot LAN si noyau).
4. **Commandes prêtes à coller** (vrais chemins/hôtes : zeta-secure, doas), avec le **filet SSH**
   pour toute modif de sshd, et jamais d'intervention réseau via le tunnel. Une commande à la fois, avec
   la machine indiquée (PC1 ou PC4) ; ce qui coupe le tunnel se donne « à la console ».

---

## 10. Rotation de la clé WireGuard de PC4 (procédure validée le 15/11/2026, O8b)

**Quand** : clé privée exposée ou restaurée d'ailleurs (elle venait du Dell via la migration du 16/08).
**Où** : LAN ou console de PC4 ; **jamais par le tunnel**. Les commandes qui le coupent (`ifconfig wg0
destroy`, `sh /etc/netstart wg0`) se lancent **à la console** (observé le 15/11 : une session SSH qui
passait par le tunnel s'est figée quand on a coupé un client). Toutes les sorties de PC4 sont « rapportées ».
Gabarit de clé publique : `DÉBUT_DE_LA_CLÉ` (8 caractères au plus) ; jamais une clé entière dans un rapport.

1. **Structure sans clé** (une ligne `wgkey` serait attendue dans `hostname.wg0` : **0 ici** ; si l'état réel diffère de ce skill, STOP et le décrire) :
   ```
   doas sed -E 's/(wgkey )[^ ]+/\1XXX/g; s/(wgpsk )[^ ]+/\1XXX/g; s/(wgendpoint )[^ ]+( [0-9]+)?/\1XXX/g; s/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/IP/g' /etc/hostname.wg0
   doas ifconfig wg0 | grep -E 'wgpubkey|wgpeer'
   ```
2. **Inventaire des pairs** : tableau `pair (8 car.) | machine | où coller la nouvelle clé`. PC1 : comparer au
   contenu de son `/etc/wireguard/publickey`. Téléphone : l'appli. Pair inconnu → demander à hprzeta. **STOP**,
   validation de hprzeta avant de continuer.
3. **Sauvegarde** : `doas cp -p /etc/wireguard/privatekey /etc/wireguard/privatekey.bak.AAAAMMJJ` (+ `hostname.wg0` si on le modifie).
4. **Nouvelle clé, jamais affichée** :
   `doas sh -c 'umask 077; /usr/local/bin/wg genkey > /etc/wireguard/privatekey.new && mv /etc/wireguard/privatekey.new /etc/wireguard/privatekey'`
5. **Clé publique** (la seule à afficher) :
   `doas sh -c '/usr/local/bin/wg pubkey < /etc/wireguard/privatekey > /etc/wireguard/publickey' && doas cat /etc/wireguard/publickey`
6. **Contrôles sans lecture** : `doas cmp -s /etc/wireguard/privatekey /etc/wireguard/privatekey.bak.AAAAMMJJ; echo $?`
   (attendu **1**), `doas wc -c /etc/wireguard/privatekey` (45), `doas ls -l /etc/wireguard/` (600 / 644).
7. **Retrait d'un pair inutile** (si décidé) : `doas sed -i '/^wgpeer DÉBUT_DE_LA_CLÉ/d' /etc/hostname.wg0` (la ligne
   porte aussi `wgpsk` et `wgaip`) ; contrôles : 1 ligne de moins, `doas grep -c wgpsk /etc/hostname.wg0`.
8. **À la console** : `doas ifconfig wg0 destroy` puis `doas sh /etc/netstart wg0` (le `destroy` est une précaution :
   `netstart` seul n'enlève pas un pair déjà actif, **non testé**), puis `doas ifconfig wg0 | grep -E 'wgpubkey|wgpeer'` :
   nouvelle clé publique **différente** de l'ancienne, pairs attendus.
9. **Clients, un par un.**
   - PC1 : `sudo cp -p /etc/wireguard/wg0.conf /etc/wireguard/wg0.conf.bak-AAAAMMJJ`, remplacer la ligne `PublicKey =`
     du bloc `[Peer]` de PC4 (`sudo sed -i 's|^PublicKey = ANCIENNE$|PublicKey = NOUVELLE|' …`), `sudo grep -c -F` pour
     contrôler (1 / 0), puis `sudo systemctl restart wg-quick@wg0` et `sudo wg show wg0 latest-handshakes`.
     ⚠️ Dans un dossier réservé à root, un joker `*.conf` est développé **sans** `sudo` (§11).
     ⚠️ **À la maison**, le hook `nm-dispatcher` de PC1 recoupe volontairement `wg0` : tester sur un autre réseau
     (partage de 4G), ne pas relancer `wg-quick` à la main.
   - Téléphone : champ « Clé publique » du pair PC4 (la clé de l'Interface et la PSK ne changent pas).
10. **Tests** : PC1 (handshake récent), téléphone en 4G (Rx > 0), et côté PC4
    `doas ifconfig wg0 | grep -A3 'wgpeer DÉBUT_DE_LA_CLÉ'` (tx/rx, `last handshake`).
11. **Nettoyage, après validation** : `doas rm -P /etc/wireguard/privatekey.bak.AAAAMMJJ` (et le `.bak` de
    `hostname.wg0` s'il contient une PSK) ; puis chercher les copies égarées **partition par partition** (§6) :
    `doas find / -xdev \( -name 'privatekey*' -o -name 'hostname.wg0*' -o -name 'duck.sh*' \) 2>/dev/null` et la
    même sur `/tmp /var /home /root`. Les `.bak` de `wg0.conf` de PC1 contiennent la clé privée de **PC1**
    (non exposée par cette rotation).

**Retour arrière tant que la sauvegarde existe (NON TESTÉ)** : à la console, `doas cp -p /etc/wireguard/privatekey.bak.AAAAMMJJ
/etc/wireguard/privatekey`, régénérer `publickey`, `ifconfig wg0 destroy` + `netstart wg0`, remettre l'ancienne clé
publique sur les clients. Dépannage seulement : l'ancienne clé reste exposée, il faudra recommencer.

---

## 11. Hygiène des sorties — ne jamais afficher un secret

- **Jamais** `cat` / `less` / `head` / `diff` / Read sur : une clé privée, une PSK, `duck.sh`, `hostname.wg0`
  (contient des PSK), une capture `tcpdump` ni une image de l'appli WireGuard (elle peut montrer une clé privée).
- **Vérifier sans lire** : `cmp -s` (code retour seul), `wc -c`, `grep -c`, `ls -l`.
- **`diff` interdit** entre une config WireGuard et sa sauvegarde : la ligne retirée contient la PSK.
- **Voir une structure** : un `sed` masquant (§10 étape 1 pour `hostname.wg0`, §7 pour `duck.sh` : `token=`, `domains=` et adresses remplacés).
- Une capture `tcpdump` contient les **adresses** : relire par un masque
  (`sed -E 's/([0-9a-f]{1,4}:){4,}[0-9a-f]{0,4}/IPV6/g'`), puis `rm -P` dès l'analyse finie.
- Dans un dossier réservé à root (`/etc/wireguard`), le **joker** est développé par **ton** shell, sans `sudo` :
  « Aucun fichier » à tort. `sudo ls dossier/` puis le nom explicite, ou `sudo sh -c '… dossier/*.conf'`.
- Un script qui finit par `echo` renvoie **0** même si `ftp` a échoué : lire le journal, pas `$?`.
- Côté Git (commits, historique, publication) : skill `riemann-security-review`. Un diagnostic abouti se range
  selon `riemann-zeta-diagnostic`.

---
*Skill du projet Riemann_Lab · bastion PC4 zeta-secure (OpenBSD) · Auteur : hprzeta · MAJ : 15/11/2026 · 298 lignes*
