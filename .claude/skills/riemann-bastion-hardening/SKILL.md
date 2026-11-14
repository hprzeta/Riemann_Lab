---
name: "riemann-bastion-hardening"
description: "Durcissement, allègement et maintenance du bastion OpenBSD PC4 (zeta-secure) du cluster Riemann_Lab. Utiliser dès qu'on met à jour, nettoie, sécurise, patche (syspatch) ou reboote PC4, ou avant toute intervention sur le VPN WireGuard, pf, sshd ou les services OpenBSD du bastion."
---

# Riemann Bastion Hardening — PC4 (zeta-secure, OpenBSD)

Skill de durcissement et de maintenance du **bastion Internet** du cluster Zêta. Il encode les
**incidents réels** rencontrés (boucle smtpd 34 j, `/var` saturé à 11,4 Go, cron DuckDNS spammant
root) pour qu'ils ne se reproduisent pas, et fixe les règles de sécurité d'un bastion exposé.

> PC4 = `zeta-secure` · OpenBSD 7.9 · LAN `[IP-LAN-PC4]` · tunnel `[IP-TUNNEL-PC4]` (valeurs réelles : `~/.ssh/config` et doc privée, jamais dans le dépôt) · `doas` (pas sudo).
> Rôle unique : router WireGuard (wg0) + filtrer (pf) + admin SSH. Tout le reste est superflu.
> Auteur : hprzeta · Mise à jour : 26 septembre 2026

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
| wg0 (via `/etc/hostname.wg0`) | le tunnel VPN lui-même |
| `ntpd` | horloge — **vital** pour VPN et cohérence des logs |
| `cron` | DuckDNS (DDNS) — cf. §7 |
| `slaacd` + `dhcpleased` | autoconf réseau ; **slaacd = IPv6, la porte d'entrée VPN** |
| `syslogd` | logs système |
| `library_aslr` | protection sécurité (randomisation) — c'est une défense, pas un extra |

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
| **`/etc/hostname.wg0`** | contient la config peer wg0 ; toujours `doas cp` en `.bak` avant edit. wg0 remonte au boot grâce à ce fichier. |
| **Clés WireGuard** (`/etc/wireguard/`, clés dans hostname.wg0) | les régénérer = re-provisionner TOUS les peers (PC1 + téléphone). |
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

---

## 7. Cron DuckDNS — ne pas spammer root (incident 26/09)

Le cron `*/5 * * * * /etc/duckdns/duck.sh` (dans `/var/cron/tabs/root`) doit **rediriger sa sortie**,
sinon `ftp` affiche sa progression → cron l'envoie par mail à root → bounces (smtpd) → boucle.
Ligne correcte :
```
*/5 * * * * /etc/duckdns/duck.sh >> /var/log/duckdns.log 2>&1
```
> ⚠️ `duck.sh` contient le **token DuckDNS en clair** dans l'URL. Ne jamais l'afficher en session
> partagée ; s'il a fui, le régénérer sur le dashboard DuckDNS puis mettre à jour `duck.sh`.

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
   ```
8. `ssh -t zeta-secure "doas reboot"` → attendre ~60 s.
9. **Vérif post-reboot** : `uptime` récent, pf `Enabled`, forwarding `=1`, wg0 up,
   sshd durci, smtpd/sndiod `failed` (= off), `/var` ~1%, `sysctl kern.version` (nouveau noyau).

> `doas rcctl check <svc>` renvoie `failed` pour un service ARRÊTÉ — c'est le résultat attendu
> pour smtpd/sndiod désactivés, pas une erreur.

---

## 9. Format de sortie d'une intervention bastion

1. **Verdict** : 🟢 sain / 🟡 corriger d'abord / 🔴 accès ou VPN en danger → STOP.
2. **Findings** (service, charge, disque, port ouvert) — sans recopier de token/clé.
3. **Actions ordonnées** : audit → coupe service par service → vérif → (reboot LAN si noyau).
4. **Commandes prêtes à coller** (vrais chemins/hôtes : zeta-secure, doas), avec le **filet SSH**
   pour toute modif de sshd, et jamais d'intervention réseau via le tunnel.

---
*Skill du projet Riemann_Lab · bastion PC4 zeta-secure (OpenBSD) · Auteur : hprzeta · MAJ : 26/09/2026*