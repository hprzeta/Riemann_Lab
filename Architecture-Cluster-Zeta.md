> **Fichier :** Architecture-Cluster-Zeta.md · **Dossier :** wiki (racine)
> **Branche :** master (wiki) · **Auteur :** hprzeta · **MAJ :** 2026-07-04

# 🖥️ Architecture Cluster Zêta — 4 machines en réseau local

> Réseau local domestique · 4 machines Ubuntu/Debian/OpenBSD
> Interconnexion SSH sans mot de passe · PC4 = bastion WireGuard accès externe IPv6
> **Statut : MONITOR 4/4 ✅ + TMUX CLUSTER ✅ + ACCÈS DISTANT PC1 VALIDÉ ✅ — 23 juin 2026**

---

## 1. Vue d'ensemble

```
Internet (4G / WiFi externe)
      │
      ▼ UDP 51820 IPv6 — zeta-secure.duckdns.org
┌─────────────────────────────────────┐
│  PC4 — zeta-secure (192.168.1.54)  │
│  OpenBSD 7.9 i386 — Bastion VPN    │
│  WireGuard wg0 : 10.10.0.1/24      │
└──────────────┬──────────────────────┘
               │ LAN 192.168.1.0/24
               │ + VPN 10.10.0.0/24
   ┌───────────┼───────────────┬──────────────────┐
   │           │               │                  │
PC1 .24      PC2 .52        PC3 .22           [box SFR]
zeta-lab   zeta-calc-     zeta-backup         GR140IG
Ubuntu i7  second Debian  Ubuntu 14.04 i686   CGNAT IPv4
Orchestr.  Core2Duo       backup+log          WAN=10.153.x
WG:10.10.0.2              (log pending)

Téléphone (10.10.0.3) ──WireGuard IPv6──▶ PC4 ──▶ tout le LAN
PC1 distant (10.10.0.2) ──WireGuard──▶ PC4 ──▶ tout le LAN
```

---

## 2. Fiche technique des 3 machines

### 🔵 Node 1 — Portable i7 (machine principale)

| Composant | Détail |
|-----------|--------|
| OS | Ubuntu 24.04 LTS |
| CPU | Intel Core i7-7500U · 2C/4T HT · 2.7–3.5 GHz |
| RAM | 8 Go DDR4 + 16 Go swap `/mnt/data` |
| GPU | NVIDIA GTX 960M · 4 Go VRAM · CUDA 12.2 |
| IP locale | **192.168.1.24** ✅ |
| User | `riemann` |
| Hostname | `zeta-lab` |
| Alias SSH | `zeta-lab` (depuis les autres nodes) |
| Rôle | Calcul principal · orchestration · git · wiki |
| Pipeline | v12 · 8 workers · 8.8 min T=100k ✅ |

### 🟢 Node 2 — HP Compaq 8000 Elite (calcul secondaire)

| Composant | Détail |
|-----------|--------|
| Modèle | HP Compaq 8000 Elite · carte mère HP 3647h |
| OS | Debian 6.1 (Bookworm) · kernel 6.1.158-1 amd64 |
| CPU | Intel Core2Duo E8400 · **2C/2T** · 3.0 GHz · 64 bits |
| RAM | DDR3 1333 MHz · jusqu'à **16 Go** (4 slots) |
| DD | SATA 80 Go + IDE 500 Go |
| Réseau | Intel 82567LM-3 · **1 Gbit/s** filaire · `enp0s25` |
| IP locale | **192.168.1.52** ✅ |
| User | `hprzeta` |
| Hostname | `zeta-calc-second` |
| Alias SSH | `zeta-calc-second` |
| Rôle | Calcul secondaire · Gigabit ethernet stable |
| Statut SSH | ✅ Connecté depuis PC1 |

### 🟡 Node 3 — Compaq Presario SG3210FR (backup)

| Composant | Détail |
|-----------|--------|
| Modèle | Compaq Presario SG3210FR · carte mère ECS Livermore8 |
| OS | Ubuntu 14.04 LTS — kernel 4.4.0-210 i686 32-bit |
| CPU | Intel Pentium E2140 · 2C · 1.6 GHz · 64 bits |
| RAM | 3 Go DDR2 667 MHz · 2 slots pleins · pas d'upgrade |
| DD | 250 Go Hitachi |
| Réseau | Realtek RTL810xE · **100 Mbit/s** · `enp1s0` |
| IP locale | **192.168.1.22** ✅ |
| User | `hprzeta` |
| Hostname | `zeta-backup` |
| Alias SSH | `zeta-backup` |
| Rôle | Backup nocturne (rsync+rclone) · monitor cluster |
| Statut SSH | ✅ Connecté depuis PC1 |
| Python | **3.5.2** (Ubuntu 14.04 LTS) — f-strings interdits, `.format()` obligatoire |
| Monitor | ✅ `zeta_monitor.py` opérationnel (PYTHONNOUSERSITE=1 dans CMD_LINUX) |

---

## 3. Configuration SSH complète

### Clé SSH (générée sur i7 le 2026-06-13)

```bash
ssh-keygen -t ed25519 -C "hprzeta-zeta-cluster" -f ~/.ssh/zeta_cluster
# Clé publique :
# ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFxG2BALVzYBqNDbcCgBSYeeeC//EKe5Q9+tt2wqwk26 hprzeta-zeta-cluster
```

### Config `~/.ssh/config` sur PC1 (opérationnelle)

```
Host zeta-calc-second
    HostName 192.168.1.52
    User hprzeta
    IdentityFile ~/.ssh/zeta_cluster

Host zeta-backup
    HostName 192.168.1.22
    User hprzeta
    IdentityFile ~/.ssh/zeta_cluster

Host zeta-secure
    HostName 192.168.1.54
    User hprzeta
    IdentityFile ~/.ssh/zeta_cluster
```

### Statut connexions SSH ✅

| Connexion | Commande | Statut |
|-----------|----------|--------|
| PC1 → PC2 | `ssh zeta-calc-second` | ✅ Opérationnel |
| PC1 → PC3 | `ssh zeta-backup` | ✅ Opérationnel |
| PC1 → PC4 | `ssh zeta-secure` | ✅ Opérationnel |

---

## 4. Procédure d'installation SSH (étapes + problèmes rencontrés)

### Sur chaque node (procédure standard)

```bash
# 1. Installer openssh-server
sudo apt update && sudo apt install -y openssh-server
sudo systemctl enable ssh && sudo systemctl start ssh

# 2. Autoriser la clé publique i7
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFxG2BALVzYBqNDbcCgBSYeeeC//EKe5Q9+tt2wqwk26 hprzeta-zeta-cluster" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 3. Vérifier l'IP
hostname -I
```

### Problèmes rencontrés sur le HP Debian — journal

#### Problème 1 : Lock dpkg
```
E: dpkg a été interrompu — sudo dpkg --configure -a nécessaire
Could not get lock /var/lib/dpkg/lock-frontend
```
**Cause** : MAJ interrompue, processus dpkg bloqué.
**Solution** :
```bash
sudo rm /var/lib/dpkg/lock-frontend
sudo rm /var/lib/dpkg/lock
sudo rm /var/cache/apt/archives/lock
sudo dpkg --configure -a
```

#### Problème 2 : debconf.dat locked
```
debconf: DbDriver "config": /var/cache/debconf/config.dat is locked
```
**Cause** : processus debconf zombie après interruption MAJ.
**Solution** :
```bash
sudo kill $(lsof /var/cache/debconf/config.dat 2>/dev/null | awk 'NR>1{print $2}')
sudo DEBIAN_FRONTEND=noninteractive dpkg --configure -a
```

#### Problème 3 : sshd_config manquant
```
/etc/ssh/sshd_config: No such file or directory
```
**Cause** : openssh-server installé mais post-install script échoué.
**Solution** :
```bash
sudo ssh-keygen -A   # Régénère les clés hôte
sudo bash -c 'echo "Port 22
PermitRootLogin no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PasswordAuthentication yes" > /etc/ssh/sshd_config'
```

#### Problème 4 : Privilege separation user sshd manquant
```
Privilege separation user sshd does not exist
```
**Cause** : utilisateur système `sshd` absent (non créé par dpkg échoué).
**Solution** :
```bash
sudo useradd -r -s /usr/sbin/nologin -d /run/sshd sshd
sudo mkdir -p /run/sshd
sudo systemctl start ssh
```
✅ **SSH actif après cette étape.**

---

## 4b. Connexion bidirectionnelle — PC2/PC3 → PC1 (zeta-lab)

### Clés générées sur chaque node fixe

```bash
# Sur PC2 et sur PC3 (même commande) :
ssh-keygen -t ed25519 -C "zeta-calc-second" -f ~/.ssh/id_ed25519  # sur PC2
ssh-keygen -t ed25519 -C "zeta-backup"      -f ~/.ssh/id_ed25519  # sur PC3
# Enter 2 fois — pas de passphrase
```

### Clés publiques des nodes (à ajouter sur PC1)

```bash
# Sur PC1 — autoriser PC2 et PC3 à se connecter :
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBD9slNvgHnVlcbEzgJV+guBcwVAM14XQnJhZOd7UnhN zeta-calc-second" >> ~/.ssh/authorized_keys
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE2UfOjfgkRGJAGxOLxAMdHumveEbXOn3uLMBKT8CrNO zeta-backup" >> ~/.ssh/authorized_keys
```

### Alias SSH `zeta-lab` sur PC2 et PC3

```bash
# Sur PC2 ET sur PC3 (même config) :
cat >> ~/.ssh/config << 'EOF'
Host zeta-lab
    HostName 192.168.1.24
    User riemann
    IdentityFile ~/.ssh/id_ed25519
EOF
```

### Tableau complet des connexions SSH ✅

| De → Vers | Commande | Statut |
|-----------|----------|--------|
| PC1 → PC2 | `ssh zeta-calc-second` | ✅ |
| PC1 → PC3 | `ssh zeta-backup` | ✅ |
| PC1 → PC4 | `ssh zeta-secure` | ✅ |
| PC2 → PC1 | `ssh zeta-lab` | ✅ |
| PC3 → PC1 | `ssh zeta-lab` | ✅ |
| PC2 → PC3 | `ssh hprzeta@192.168.1.22` | *(non configuré)* |
| PC3 → PC2 | `ssh hprzeta@192.168.1.52` | *(non configuré)* |

---

## 5. Commandes utiles depuis PC1 (zeta-lab)

### Connexion

```bash
ssh zeta-calc-second   # → hprzeta@zeta-calc-second (PC2)
ssh zeta-backup        # → hprzeta@zeta-backup (PC3)
ssh zeta-secure        # → hprzeta@zeta-secure (PC4 OpenBSD)
exit                   # Quitter la session SSH
```

### Transfert de fichiers

```bash
# Envoyer code vers PC2
scp ~/projet_zeta/src/calculs/optimisation/compute_zeros_v12.py \
    zeta-calc-second:~/projet_zeta/src/

# Récupérer résultats de PC2
scp zeta-calc-second:~/projet_zeta/calculs/zeros_*.csv ~/projet_zeta/calculs/

# Backup calculs vers PC3 (zeta-backup)
rsync -avz ~/projet_zeta/calculs/ zeta-backup:~/backup/calculs/
rsync -avz ~/projet_zeta/logs/    zeta-backup:~/backup/logs/
rsync -avz ~/projet_zeta/pdf/     zeta-backup:~/backup/pdf/
```

### Monitoring à distance

```bash
# Suivre un run sur PC2
ssh zeta-calc-second "tail -f ~/projet_zeta/logs/run_current.log"

# Charge CPU sur chaque node
ssh zeta-calc-second "uptime && free -h"
ssh zeta-backup      "uptime && df -h"

# Lancer un calcul sur PC2 en arrière-plan
ssh zeta-calc-second "cd ~/projet_zeta && source zeta_env/bin/activate && \
  nohup python src/calculs/optimisation/compute_zeros_v12.py \
  2>&1 | tee logs/run_pc2_\$(date +%Y%m%d_%H%M%S).log &"
```

---

## 6. Prochaines étapes — PC2 zeta-calc-second (installation calcul)

```bash
# Depuis PC1 via SSH :
ssh zeta-calc-second

# Installer Python + libs calcul
sudo apt install -y python3 python3-pip python3-venv \
  libmpfr-dev libgmp-dev libflint-dev build-essential rsync

# Créer venv
mkdir -p ~/projet_zeta && cd ~/projet_zeta
python3 -m venv zeta_env
source zeta_env/bin/activate
pip install mpmath numpy

# Copier le code depuis PC1 :
rsync -avz ~/projet_zeta/src/     zeta-calc-second:~/projet_zeta/src/
rsync -avz ~/projet_zeta/scripts/ zeta-calc-second:~/projet_zeta/scripts/
rsync -avz ~/projet_zeta/config/  zeta-calc-second:~/projet_zeta/config/
```

---

## 7. Prochaines étapes — PC3 zeta-backup (log-dns-moni)

```bash
# Services déjà déployés sur zeta-backup (session 15/06) :
# chrony (NTP), rsyslog, dnsmasq (.lan), zeta_monitor.sh

# Installer rclone (si pas encore fait)
curl https://rclone.org/install.sh | sudo bash

# Configurer Proton Drive
rclone config

# Cron backup quotidien à 2h
echo '0 2 * * * rclone copy ~/backup/ protondrive:hprzeta/Riemann_Lab/backup/ --include "*.csv" --include "*.pdf"' | crontab -
```

---

## 8. Pipeline distribué futur (v13 OS)

```
┌──────────────────────────────────────────────────────┐
│           Pipeline distribué T=1 000 000              │
├──────────────────────────────────────────────────────┤
│  zeta-lab 192.168.1.24 — orchestrateur               │
│  ├── Segments [14, 500k]     → calcul local (8W)     │
│  └── Segments [500k, 1000k] → ssh zeta-calc-second   │
│                                                       │
│  zeta-calc-second 192.168.1.52 — worker              │
│  ├── 2 workers Illinois/Arb                          │
│  └── Résultats → rsync → zeta-backup                 │
│                                                       │
│  zeta-backup 192.168.1.22 — collecteur               │
│  ├── Agrège les CSV des 2 nodes                      │
│  └── rclone → Proton Drive (backup auto)             │
│                                                       │
│  Total : 8W (zeta-lab) + 2W (zeta-calc-second)       │
│  T=100k : ~7 min · T=1M v12 : ~30h · T=1M OS : ~3h  │
└──────────────────────────────────────────────────────┘
```

---

## 9. Estimation gain cluster

| Config | Workers | T=100k | T=1M v12 | T=1M OS |
|--------|---------|--------|---------|--------|
| zeta-lab seul | 8 HT | **8.8 min** ✅ | ~37–47 h | ~2–4 h |
| zeta-lab + zeta-calc-second | 8+2=10 | ~7 min | ~30–35 h | ~2–3 h |
| + zeta-backup stockage | — | — | — | — |

---

---

## 10. PC4 — zeta-secure (bastion VPN / pare-feu OpenBSD)

> Ajouté le 2026-06-15 — PC4 n'est pas un nœud de calcul mais le gardien du périmètre réseau.

| Composant | Détail |
|-----------|--------|
| Modèle | Dell Dimension 4500 · i386 |
| OS | OpenBSD 7.9 / i386 |
| CPU | Intel Pentium 4 @2.4GHz · 32 bits |
| IP locale | **192.168.1.54** (`re0`) ✅ |
| IP VPN | **10.10.0.1** (concentrateur WireGuard `wg0`) |
| User | `hprzeta` |
| Hostname | `zeta-secure` |
| Alias SSH | `zeta-secure` |
| DDNS | `zeta-secure.duckdns.org` (AAAA mis à jour toutes les 5 min) |
| Rôle | Bastion VPN · pare-feu pf · point d'entrée externe |
| Statut | ✅ Opérationnel depuis 2026-06-15 |

---

## 11. Accès VPN externe — Architecture et chemin réseau

### Schéma — téléphone 4G → cluster via IPv6

```
                         Internet (4G)
                              │
                    [Téléphone Android]
                    WireGuard "zeta-vpn"
                    10.10.0.3/32
                    Endpoint: zeta-secure.duckdns.org:51820
                              │
                              │ IPv6 (2a02:8428:80a6:da01:.../51820 UDP)
                              │
                    [Box SFR GR140IG]
                    Préfixe délégué /56 : 2a02:8428:80a6:da00::/56
                    LAN : 2a02:8428:80a6:da01::/64
                    Règle "Réseau v6" : UDP 51820 → PC4 activée
                              │
                    [PC4 — zeta-secure 192.168.1.54]
                    OpenBSD 7.9 · re0 (IPv6 SLAAC global)
                    WireGuard wg0 · 10.10.0.1/24
                    pf : block in / pass WireGuard + ICMPv6
                              │
                       ┌──────┴──────┐
                       │  LAN local  │  192.168.1.0/24
              ┌────────▼────┐   ┌────────────────────┐   ┌────▼───────────┐
              │PC1 zeta-lab │   │PC2 zeta-calc-second│   │PC3 zeta-backup │
              │192.168.1.24 │   │192.168.1.52        │   │192.168.1.22    │
              │10.10.0.2/24 │   │ (futur pair        │   │ (futur pair    │
              └─────────────┘   │  WireGuard)        │   │  WireGuard)    │
                                └────────────────────┘   └────────────────┘
```

### Adresse IPv6 de PC4

| Type | Adresse | Usage |
|------|---------|-------|
| Locale-lien | `fe80::240:f4ff:fecc:36a0` | Interne uniquement |
| Globale SLAAC | `2a02:8428:80a6:da01:ad39:37b9:a638:126c` | Endpoint public ✅ |
| Temporary | (ignorée) | Ignorer pour un usage serveur |

> L'adresse globale SLAAC se renouvelle périodiquement (~12 min `pltime`, ~2 h `vltime`).
> `duck.sh` extrait en temps réel l'adresse non-temporary et met à jour le DDNS toutes les 5 min.

---

## 12. Peers WireGuard — table de référence (PC4 concentrateur)

| Pair | IP VPN | Clé publique (tronquée) | allowed-ips | Statut |
|------|--------|------------------------|-------------|--------|
| PC4 (serveur) | `10.10.0.1/24` | — | — | ✅ concentrateur |
| PC1 zeta-lab | `10.10.0.2/24` | `...` (i7) | `10.10.0.0/24` | ✅ handshake OK |
| Téléphone Android | `10.10.0.3/24` | `6euaNc/uLQc/PYL2/CAWYR391...` | `10.10.0.0/24, 192.168.1.0/24` | ✅ testé 2026-06-15 |

> `allowed-ips` du téléphone inclut `192.168.1.0/24` pour accès complet au LAN via le tunnel.
> Test ping LAN depuis téléphone → reporté à la prochaine session.

### Extrait configuration `/etc/wireguard/wg0.conf` (PC4, OpenBSD)

```ini
[Interface]
Address = 10.10.0.1/24
ListenPort = 51820
PrivateKey = <clé privée PC4>

[Peer]
# PC1 — zeta-lab (i7)
PublicKey = <clé publique PC1>
AllowedIPs = 10.10.0.2/32

[Peer]
# Téléphone Android
PublicKey = 6euaNc/uLQc/PYL2/CAWYR391...
AllowedIPs = 10.10.0.3/32
```

### Correction PC1 — accès distant validé (2026-06-23)

> Config PC1 créée le 14/06 mais jamais testée hors LAN : deux erreurs bloquaient
> l'accès complet au cluster depuis l'extérieur (ex. Paris/Free, hors du LAN SFR de PC4).

| Champ `wg0.conf` (PC1) | Avant (cassé) | Après (corrigé) |
|---|---|---|
| `Endpoint` | `192.168.1.54:51820` (IP LAN — injoignable hors réseau SFR) | `zeta-secure.duckdns.org:51820` |
| `AllowedIPs` | `10.10.0.1/32` (route uniquement PC4) | `10.10.0.0/24, 192.168.1.0/24` (route tout le LAN via le tunnel) |

```bash
# Correctifs appliqués sur PC1
sudo cp /etc/wireguard/wg0.conf /etc/wireguard/wg0.conf.bak
sudo sed -i 's|Endpoint = 192.168.1.54:51820|Endpoint = zeta-secure.duckdns.org:51820|' /etc/wireguard/wg0.conf
sudo sed -i 's|AllowedIPs = 10.10.0.1/32|AllowedIPs = 10.10.0.0/24, 192.168.1.0/24|' /etc/wireguard/wg0.conf
sudo wg-quick up wg0
sudo systemctl enable wg-quick@wg0   # persistance au démarrage
```

**Validation depuis PC1, hors LAN SFR (Paris/Free, 2026-06-23) :**

| Cible | Résultat |
|---|---|
| `ping 10.10.0.1` (PC4 tunnel) | ✅ 0 % perte, 13 ms |
| `ping 192.168.1.52` (PC2 via PC4) | ✅ 0 % perte, 11 ms |
| `ping 192.168.1.22` (PC3 via PC4) | ✅ 0 % perte, 15 ms |
| `ssh -i ~/.ssh/id_acer hprzeta@192.168.1.52` | ✅ connexion OK |

> Le routage IPv4 LAN via le tunnel (point resté « reporté » pour le téléphone, voir
> tableau ci-dessus) fonctionnait déjà côté PC4 (`net.inet.ip.forwarding` actif) —
> aucune modification nécessaire côté PC4 pour ce test.
> PC1 est donc maintenant un client WireGuard pleinement opérationnel, accessible
> à distance (4G, autre box) avec accès complet au LAN 192.168.1.0/24.

---

## 13. Configuration pf (PC4) — règles critiques IPv6

```pf
# Variables
ext_if = "re0"

# Politique par défaut
block in all
pass out all

# WireGuard — entrant IPv4 et IPv6
pass in on $ext_if proto udp from any to any port 51820
pass in on wg0 all

# ICMPv6 — INDISPENSABLE pour SLAAC (RA, NDP)
pass in on $ext_if inet6 proto icmp6 icmp6-type {routeradv, neighbradv, neighbrsol, redir}
pass out on $ext_if inet6 proto icmp6 all
```

> ⚠️ **Sans la règle `icmp6-type {routeradv,...}`**, `inet6 autoconf` dans `/etc/hostname.re0`
> reste sans effet : les Router Advertisements sont bloqués avant que la pile TCP/IP les traite.
> Le type correct sous OpenBSD est `neighbrsol` (pas `neighbrsolicit`).

### `/etc/hostname.re0` — ligne ajoutée

```
inet6 autoconf
```

---

## 14. DuckDNS — `duck.sh` (mise à jour AAAA automatique)

```sh
#!/bin/sh
# Extraire l'adresse IPv6 globale non-temporary de re0
IP6=$(ifconfig re0 | awk '/inet6/ && !/fe80/ && !/temporary/ {print $2; exit}')
TOKEN="<token_duckdns>"
DOMAIN="zeta-secure"

# Pousser A (IPv4 vide si CGNAT) et AAAA
curl -s "https://www.duckdns.org/update?domains=${DOMAIN}&token=${TOKEN}&ip=&ipv6=${IP6}" >> /var/log/duck.log 2>&1
```

Cron : `*/5 * * * * /etc/duckdns/duck.sh` — vérifié avec `crontab -l`.

---

## 15. Leçons apprises — IPv6, pf, box SFR, WireGuard

| Piège | Symptôme | Solution |
|-------|----------|----------|
| CGNAT IPv4 | `curl ifconfig.me` renvoie une IP "publique" mais la box en affiche une RFC1918 | Comparer avec l'IP WAN dans l'interface box, pas depuis l'intérieur du réseau |
| Pare-feu IPv6 box SFR distinct du NAT | Règle UDP 51820 en NAT/redirection créée, mais trafic IPv6 entrant quand même bloqué | Ouvrir la section "Réseau v6 → Sécurité → Accès" de l'interface box |
| SLAAC OpenBSD bloqué par pf | `inet6 autoconf` dans `/etc/hostname.re0` mais aucune adresse globale | Ajouter `pass in ... icmp6-type {routeradv,...}` dans `pf.conf` |
| `rx=0` persistant WireGuard Android | Le paquet part (tx croissant) mais n'arrive jamais | Chercher du côté des pare-feu intermédiaires (box), pas du client |
| Adresse SLAAC temporary | DDNS pointe sur une adresse qui change toutes les quelques minutes | Filtrer avec `awk '!/temporary/'` dans `duck.sh` |

---

## 16. Procédure de connexion au cluster (depuis PC1)

### Prérequis
- Lancer tmux session `zeta` : `tmux new -s zeta` ou `tmux attach -t zeta`
- Les alias SSH sont définis dans `~/.ssh/config` sur PC1

### Connexions directes (LAN)

```bash
ssh zeta-calc-second   # → hprzeta@192.168.1.52 (PC2 Debian)
ssh zeta-backup        # → hprzeta@192.168.1.22 (PC3 Ubuntu 14.04 i686)
ssh zeta-secure        # → hprzeta@192.168.1.54 (PC4 OpenBSD)
```

> ⚠️ PC4 OpenBSD : si sudo nécessite un TTY interactif, utiliser `ssh -t zeta-secure doas commande`

### Connexion depuis l'extérieur (VPN WireGuard actif)

```bash
# 1. Activer WireGuard sur le device mobile/distant
#    Endpoint : zeta-secure.duckdns.org:51820 (IPv6 AAAA)
# 2. Depuis le device, accès direct au LAN :
ssh riemann@192.168.1.24    # PC1 zeta-lab
ssh hprzeta@192.168.1.52    # PC2 zeta-calc-second
ssh hprzeta@192.168.1.22    # PC3 zeta-backup
```

### Couleurs tmux par machine

Les scripts SSH changent la couleur de la barre tmux pour identifier visuellement la machine :
- **Cyan/vert clair** → PC1 zeta-lab (Ubuntu, machine principale)
- **Jaune/orange** → PC2 zeta-calc-second (Debian)
- **Cyan clair** → PC3 zeta-backup (Ubuntu 14.04 i686)
- **Noir** → PC4 zeta-secure (OpenBSD — sobre, bastion)

Exemple de wrapper SSH avec changement de couleur :

```bash
# Changer couleur barre tmux à la connexion
tmux set-option -g status-bg colour214   # jaune → PC2
ssh hprzeta@192.168.1.52
tmux set-option -g status-bg colour28    # restaurer vert foncé par défaut
```

### Scripts pré-run obligatoires (PC1)

```bash
# Avant tout run de calcul zéros :
bash ~/projet_zeta/scripts/zeta_turbo_on.sh

# Lancer le run (exemple) :
cd ~/projet_zeta
nohup python src/calculs/optimisation/compute_zeros_v12.py ... &

# Après le run :
bash ~/projet_zeta/scripts/zeta_turbo_off.sh
```

---

## 17. Monitoring cluster — zeta_monitor.py + zeta_tmux.sh

> Ajouté le 2026-06-16 — monitor 4/4 opérationnel, session tmux colorée opérationnelle.

### zeta_monitor.py — état global 4/4

Script Python sur PC1 (`scripts/zeta_monitor.py`) qui interroge les 4 machines en parallèle via SSH.

| Machine | OS | Méthode CPU | Fix appliqué | Statut |
|---|---|---|---|---|
| PC1 `zeta-lab` | Ubuntu 24.04 | `/proc/stat` natif | — | ✅ |
| PC2 `zeta-calc-second` | Debian 12 | `/proc/stat` natif | — | ✅ |
| PC3 `zeta-backup` | Ubuntu 14.04 (Python 3.5.2) | `/proc/stat` via `top` batch | `PYTHONNOUSERSITE=1` + `.format()` | ✅ |
| PC4 `zeta-secure` | OpenBSD 7.9 i386 | `top -b -n 1` (awk NF-1) | `len(p) >= 5`, idle=`p[-1]` | ✅ |

**Fixes appliqués dans `zeta_monitor.py` (session 2026-06-16) :**
- PC3 : f-strings remplacés par `.format()` (Python 3.5 ne supporte pas f-strings)
- PC3 : `PYTHONNOUSERSITE=1` préfixé dans `CMD_LINUX` (contourne `distutils-precedence.pth`)
- PC4 : CPU extrait via `top -b -n 1` (pas `/proc/stat` — absent sous OpenBSD)
- PC4 : `len(p) >= 5` au lieu de `>= 7` (OpenBSD top produit moins de colonnes)

```python
# Extrait zeta_monitor.py — commande SSH pour PC3 (Python 3.5)
CMD_LINUX = "PYTHONNOUSERSITE=1 python3 /home/hprzeta/proj/monitor_agent.py"

# Extrait — parsing CPU OpenBSD (top -b -n 1)
# Ligne : "CPU:  2.3% user, ... 96.2% idle"
p = line.split()
if len(p) >= 5 and p[0] == 'CPU:':
    idle = float(p[-1].replace('%', ''))
    cpu  = 100.0 - idle
```

### zeta_tmux.sh — session cluster 4 panneaux

Script `scripts/zeta_tmux.sh` — crée (ou reprend) la session tmux `zeta-cluster` :

```bash
# Lancer la session cluster
zeta-cluster       # alias ~/.bashrc PC1

# Disposition des panneaux :
# ┌─────────────────────┬─────────────────────┐
# │ PC2 zeta-calc-second│ PC4 zeta-secure      │
# │ fond JAUNE (colour3)│ fond NOIR (colour0)  │
# ├─────────────────────┼─────────────────────┤
# │ PC3 zeta-backup     │ PC1 local + monitor  │
# │ fond CYAN (colour6) │ fond MAGENTA (colour5│
# └─────────────────────┴─────────────────────┘
```

Les couleurs utilisent `tmux select-pane -P 'bg=colourX,fg=colourY'` — chaque panneau SSH
change de couleur dès l'ouverture de la connexion, permettant d'identifier la machine au premier coup d'œil.

### Alias ~/.bashrc sur PC1

```bash
alias zeta-cluster='bash ~/projet_zeta/scripts/zeta_tmux.sh'
```

---

## Voir aussi

- [[Plancher-Hardware-Architecture]] — limites hardware, mur de latence
- [[Etape-1-Calcul-des-zéros-non-triviaux]] — pipeline v12
- [[STACK]] — roadmap, outils, matériel
- [[Guide-Linux-Commandes]] — §12 tmux, §15 Python 3.5 compat
- [[JOURNAL]] — entrée 2026-06-16 : monitor 4/4 + zeta_tmux.sh

---

> **Fichier :** Architecture-Cluster-Zeta.md · **Dossier :** wiki (racine)
> **Branche :** master (wiki) · **Auteur :** hprzeta · **MAJ :** 2026-07-04 (correction IP PC2 .94 → .52)

*Architecture-Cluster-Zeta.md · wiki racine · branche master · hprzeta · MAJ 2026-07-04 · ~705 lignes*
