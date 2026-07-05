> **Fichier :** Guide-Linux-Commandes.md · **Dossier :** wiki racine
> **Branche :** master (wiki) · **Auteur :** hprzeta · **MAJ :** 2026-07-04 (wg_auto.sh — bascule WireGuard maison/déplacement)

# Guide Linux/BSD — Commandes du projet Riemann_Lab

> 📖 **Guide vivant.** Chaque nouvelle commande utilisée dans le projet est ajoutée ici.
> Couvre Linux (Ubuntu/Debian) et OpenBSD (PC4 zeta-secure).
> Mis à jour à chaque session où de nouvelles commandes sont découvertes.

---

## 1. Réseau — Voir les adresses IP

### Linux (Ubuntu/Debian)
```bash
# Voir toutes les interfaces et IPs
ip addr show

# Voir seulement les IPv4
ip addr show | grep "inet "
ip -4 addr

# Voir une interface spécifique
ip addr show wlp2s0    # WiFi PC1
ip addr show enp0s25   # Ethernet PC2
ip addr show enp2s0    # Ethernet PC3

# Voir les routes
ip route

# Voir les IPs + interfaces en une ligne
ip -4 addr | grep inet | awk '{print $2, $NF}'
```

### OpenBSD (PC4 zeta-secure)
```bash
# Voir toutes les interfaces
ifconfig

# Voir une interface spécifique
ifconfig re0           # carte réseau principale
ifconfig wg0           # interface WireGuard

# Voir seulement IPv4
ifconfig re0 | grep "inet "

# Voir IPv6 (sauf lien-local fe80 et temporary)
ifconfig re0 | grep "inet6" | grep -v "fe80\|temporary"

# Voir les routes
netstat -rn
```

---

## 2. Système — Voir l'OS et la version

### Linux
```bash
uname -a               # noyau complet
uname -sr              # OS + version courte
cat /etc/os-release    # distribution (Ubuntu, Debian...)
lsb_release -a         # infos distribution (si installé)
```

### OpenBSD
```bash
uname -a               # seule commande nécessaire
# Exemple : OpenBSD zeta-secure 7.9 GENERIC#329 i386
# /etc/os-release n'existe pas sous OpenBSD
```

---

## 3. Système — Ressources et performances

```bash
# Charge CPU et mémoire
top                    # interactif (Linux et OpenBSD)
top -b -n 1            # une seule capture (Linux)
uptime                 # charge moyenne 1/5/15 min

# Mémoire
free -h                # Linux seulement
# OpenBSD : voir top

# Espace disque
df -h                  # tous les systèmes de fichiers
df -h /home            # dossier spécifique
du -sh ~/dossier/      # taille d'un dossier
du -sh ~/*/ | sort -h  # trier par taille

# Processus
ps aux                 # tous les processus (Linux + OpenBSD)
ps aux | grep python   # filtrer
kill -SIGTERM PID      # arrêter proprement
kill -9 PID            # forcer (dernier recours)

# Gouverneur CPU (Linux)
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# performance = mode calcul, powersave = mode économie
```

---

## 4. SSH — Connexions entre machines

```bash
# Connexion simple
ssh user@ip
ssh hprzeta@192.168.1.52    # PC2
ssh hprzeta@192.168.1.22    # PC3
ssh hprzeta@192.168.1.54    # PC4 (OpenBSD)

# Via alias (définis dans ~/.ssh/config sur PC1)
ssh zeta-calc-second
ssh zeta-backup
ssh zeta-secure

# Connexion avec clé SSH spécifique
ssh -i ~/.ssh/id_acer hprzeta@192.168.1.22

# Mode verbose (debug)
ssh -v hprzeta@192.168.1.52

# Copier un fichier vers une machine distante
scp fichier.txt hprzeta@192.168.1.22:~/destination/

# Copier depuis une machine distante
scp hprzeta@192.168.1.22:~/fichier.txt ./local/
```

---

## 5. WireGuard

### Linux (PC1 zeta-lab)
```bash
# Démarrer le tunnel
sudo wg-quick up wg0

# Arrêter le tunnel
sudo wg-quick down wg0

# Voir l'état du tunnel
sudo wg show

# Corriger un fichier de config corrompu (NBSP mobiles)
sudo sed -i 's/\xc2\xa0/ /g' /etc/wireguard/wg0.conf
```

### OpenBSD (PC4 zeta-secure)
```bash
# Démarrer l'interface WireGuard
doas ifconfig wg0 up
doas sh /etc/netstart wg0

# Arrêter l'interface
doas ifconfig wg0 down

# Voir l'état WireGuard
doas wg show

# Ajouter/modifier un peer à chaud
doas wg set wg0 peer CLE_PUBLIQUE \
  allowed-ips 10.10.0.3/32

# Modifier les AllowedIPs d'un peer
doas wg set wg0 peer CLE_PUBLIQUE \
  allowed-ips 10.10.0.0/24,192.168.1.0/24
```

---

## 6. OpenBSD — Commandes spécifiques

### Droits et sudo
```bash
# OpenBSD utilise doas (pas sudo)
doas commande              # exécuter en root
doas whoami                # vérifier → doit afficher "root"

# Configurer doas
echo 'permit persist hprzeta' > /etc/doas.conf
# persist = pas de re-demande pendant un moment
```

### Patches de sécurité
```bash
# Lister les patches disponibles
doas syspatch -c

# Appliquer les patches
doas syspatch

# Si patch noyau → reboot obligatoire
doas reboot
```

### Paquets
```bash
# Installer un paquet
doas pkg_add nom_paquet

# Chercher un paquet
pkg_info -Q mot_cle

# Lister les paquets installés
pkg_info
```

### Pare-feu pf
```bash
# Voir les règles actives
doas pfctl -sr

# Vérifier syntaxe avant chargement
doas pfctl -nf /etc/pf.conf

# Charger les règles
doas pfctl -f /etc/pf.conf

# Statistiques
doas pfctl -s info

# Activer/désactiver pf
doas pfctl -e    # enable
doas pfctl -d    # disable (ATTENTION : plus de pare-feu !)
```

### Réseau OpenBSD
```bash
# Reconfigurer une interface (relit /etc/hostname.re0)
doas sh /etc/netstart re0

# Voir la config d'une interface
cat /etc/hostname.re0
cat /etc/hostname.wg0

# Voir la passerelle par défaut
cat /etc/mygate
netstat -rn | grep default

# Tester la connectivité
ping -c 2 1.1.1.1
ping6 -c 2 2606:4700:4700::1111   # ping IPv6

# Vérifier la résolution DNS
host google.com
host -t AAAA zeta-secure.duckdns.org   # enregistrement IPv6
```

### sysctl OpenBSD
```bash
# Voir tous les sysctls
sysctl -a

# IP forwarding (pour WireGuard NAT)
doas sysctl net.inet.ip.forwarding=1

# ⚠️ net.inet6.ip6.accept_rtadv n'existe PAS sous OpenBSD
# (c'est FreeBSD/NetBSD) — SLAAC est géré nativement
```

---

## 7. Pare-feu pf — Règles types (OpenBSD PC4)

```bash
# Voir /etc/pf.conf actuel
doas cat /etc/pf.conf
```

Exemple de règles clés pour le bastion WireGuard :
```
# Bloquer tout en entrée par défaut
block in

# Autoriser tout en sortie
pass out

# SSH
pass in on $ext_if proto tcp to port 22

# WireGuard UDP (IPv4 et IPv6)
pass in on $ext_if proto udp to port 51820

# ICMPv6 nécessaire pour SLAAC (Router Advertisements)
pass in on $ext_if inet6 proto icmp6 \
  icmp6-type {routeradv, neighbradv, neighbrsol, redir}
# ⚠️ neighbrsol (pas neighbrsolicit — invalide sous pf)

# Trafic depuis le VPN vers le LAN
pass in on $wg_if
```

---

## 8. DuckDNS — DNS dynamique

```bash
# Mise à jour manuelle (depuis PC4 OpenBSD)
# ftp = équivalent de curl sous OpenBSD base
doas ftp -o /var/log/duckdns.log \
  "https://www.duckdns.org/update?domains=zeta-secure&token=TOKEN&ip=&ipv6=ADRESSE_IPv6"

# Script automatique /etc/duckdns/duck.sh
# Extrait l'IPv6 stable de re0 (pas fe80, pas temporary)
IP6=$(ifconfig re0 | awk '/inet6/ && !/fe80/ && !/temporary/ {print $2; exit}')

# Voir le résultat du dernier update
doas cat /var/log/duckdns.log
# → "OK" = succès, "KO" = échec

# Vérifier la résolution DNS (depuis n'importe quelle machine)
host -t A zeta-secure.duckdns.org     # IPv4 (inutile car CGNAT)
host -t AAAA zeta-secure.duckdns.org  # IPv6 (celle utilisée)
```

---

## 9. Cron — Tâches automatiques

### Linux (PC1, PC3)
```bash
# Voir les crons de l'utilisateur courant
crontab -l

# Éditer les crons
crontab -e

# Workaround si crontab -e cassé (ex: PC3 Python 3.5)
(crontab -l; echo "*/5 * * * * /chemin/script.sh") | crontab -
```

### OpenBSD (PC4)
```bash
# Voir les crons
doas crontab -l

# Éditer sans vi (OpenBSD n'a pas nano par défaut)
doas crontab -l > /tmp/cron.txt
echo '*/5 * * * * /etc/duckdns/duck.sh' >> /tmp/cron.txt
doas crontab /tmp/cron.txt
rm /tmp/cron.txt
```

### Syntaxe cron
```
# ┌──── minute (0-59)
# │ ┌── heure (0-23)
# │ │ ┌─ jour du mois (1-31)
# │ │ │ ┌ mois (1-12)
# │ │ │ │ ┌ jour semaine (0=dim)
# │ │ │ │ │
  * * * * *  commande

*/5 * * * *        # toutes les 5 minutes
0 2 * * *          # tous les jours à 02h00
50 1 * * *         # tous les jours à 01h50
```

---

## 10. rsync — Synchronisation entre machines

```bash
# Sync logs de PC1 vers PC3 (backup nocturne 01h50)
rsync -avz --progress \
  ~/projet_zeta/logs/ \
  hprzeta@192.168.1.22:~/backup/logs/

# Sync wiki
rsync -avz \
  ~/projet_zeta/Riemann_Lab.wiki/ \
  hprzeta@192.168.1.22:~/backup/Riemann_Lab.wiki/

# Options utiles
# -a  : archive (préserve permissions, dates, liens)
# -v  : verbose
# -z  : compression
# -n  : dry-run (simuler sans modifier)
# --delete : supprimer les fichiers absents de la source
# --progress : afficher la progression
```

---

## 11. rclone — Sync vers Proton Drive

```bash
# Copier vers Proton Drive
rclone copy ~/projet_zeta/pdf/cours/ \
  protondrive:hprzeta/Riemann_Lab/cours/ --progress

# Lister les fichiers sur Proton Drive
rclone ls protondrive:hprzeta/Riemann_Lab/

# Re-authentifier si erreur 401
rclone config reconnect protondrive:

# Erreur 422 = fichier déjà présent → normal, ignoré
```

---

## 12. tmux — Gestion de sessions multi-panneaux

### Commandes de base

```bash
# Créer une nouvelle session nommée
tmux new-session -s zeta
tmux new -s zeta-cluster        # forme courte

# Rejoindre une session existante
tmux attach -t zeta
tmux attach-session -t zeta-cluster

# Lister les sessions actives
tmux ls

# Tuer une session depuis l'extérieur
tmux kill-session -t zeta-cluster
```

### Raccourcis clavier (préfixe = Ctrl+B)

```
Ctrl+B  d         Détacher (quitter sans fermer la session)
Ctrl+B  &         Tuer la fenêtre courante (avec confirmation)
Ctrl+B  "         Diviser horizontalement (nouveau panneau en bas)
Ctrl+B  %         Diviser verticalement (nouveau panneau à droite)
Ctrl+B  ←→↑↓     Naviguer entre les panneaux
Ctrl+B  z         Zoom sur le panneau courant (toggle)
Ctrl+B  q         Afficher les numéros des panneaux
```

### split-window et layout

```bash
# Diviser horizontalement (panneau en bas)
tmux split-window -v

# Diviser verticalement (panneau à droite)
tmux split-window -h

# Sélectionner un panneau par numéro
tmux select-pane -t 0
tmux select-pane -t 3

# Agrandir un panneau
tmux resize-pane -D 5     # vers le bas de 5 lignes
tmux resize-pane -R 10    # vers la droite de 10 colonnes
```

### Couleurs des panneaux — identifier la machine (select-pane -P)

```bash
# -P 'bg=couleur,fg=couleur' colorie le fond ET le texte du panneau
tmux select-pane -t 0 -P 'bg=colour3,fg=colour0'    # jaune texte noir  → PC2 Debian
tmux select-pane -t 1 -P 'bg=colour6,fg=colour0'    # cyan texte noir   → PC3 backup
tmux select-pane -t 2 -P 'bg=colour0,fg=colour2'    # noir texte vert   → PC4 OpenBSD
tmux select-pane -t 3 -P 'bg=colour5,fg=colour15'   # magenta texte blanc → PC1 local

# Changer la barre de statut globale (toute la session)
tmux set-option -g status-bg colour3    # jaune (PC2 Debian)
tmux set-option -g status-bg colour6    # cyan (PC3 backup)
tmux set-option -g status-bg colour0    # noir (PC4 OpenBSD)
```

### send-keys — envoyer des commandes dans un panneau

```bash
# Envoyer une commande dans un panneau sans y accéder
# Format : session:fenêtre.panneau
tmux send-keys -t zeta-cluster:0.0 "ssh zeta-calc-second" Enter
tmux send-keys -t zeta-cluster:0.1 "ssh hprzeta@192.168.1.22" Enter
tmux send-keys -t zeta-cluster:0.2 "ssh zeta-secure" Enter

# Envoyer sans Enter (pour préparer une commande)
tmux send-keys -t zeta-cluster:0.3 "python3 zeta_monitor.py" ""
```

### Script zeta_tmux.sh — session cluster automatique

```bash
# Lancer la session cluster (4 panneaux colorés + monitor)
zeta-cluster              # alias dans ~/.bashrc

# Ou directement :
bash ~/projet_zeta/scripts/zeta_tmux.sh
```

Le script `scripts/zeta_tmux.sh` crée la session `zeta-cluster` avec :
- Panneau haut-gauche : PC2 `zeta-calc-second` — fond **jaune** (`colour3`)
- Panneau bas-gauche : PC3 `zeta-backup` — fond **cyan** (`colour6`)
- Panneau haut-droite : PC4 `zeta-secure` (OpenBSD) — fond **noir** (`colour0`)
- Panneau bas-droite : PC1 local + `zeta_monitor.py` — fond **magenta** (`colour5`)

### Alias ~/.bashrc

```bash
# Alias cluster — à ajouter dans ~/.bashrc sur PC1
alias zeta-cluster='bash ~/projet_zeta/scripts/zeta_tmux.sh'
```

---

## 13. Sed — Édition rapide de fichiers

```bash
# Remplacer une chaîne dans un fichier (Linux GNU sed)
sed -i 's/ancien/nouveau/g' fichier.txt

# Remplacer avec séparateur alternatif (si / dans les chemins)
sed -i 's|/ancien/chemin|/nouveau/chemin|g' fichier.txt

# ⚠️ OpenBSD/macOS (BSD sed) : -i nécessite une extension
sed -i '' 's/ancien/nouveau/g' fichier.txt

# Supprimer les caractères NBSP (espace insécable, fréquent en copier-coller mobile)
sed -i 's/\xc2\xa0/ /g' fichier.conf
# ⚠️ Cause l'erreur "wrong length or format" dans les clés WireGuard
```

---

## 14. Divers utiles

```bash
# Voir les connexions réseau actives
ss -tlnp          # Linux
netstat -an       # Linux + OpenBSD

# Tester un port distant
nc -zv 192.168.1.54 51820    # test UDP WireGuard
nc -zv 192.168.1.54 22       # test SSH

# Voir les logs système
journalctl -f                   # Linux systemd (temps réel)
doas tail -f /var/log/messages  # OpenBSD

# Générer un QR code (pour WireGuard Android)
qrencode -t ansiutf8 < /tmp/phone_wg0.conf

# Voir l'IP publique vue depuis internet
curl -4 -s ifconfig.me    # IPv4 (attention : ne détecte pas CGNAT depuis l'intérieur)
curl -6 -s ifconfig.me    # IPv6

# ⚠️ CGNAT : curl -4 ifconfig.me depuis l'intérieur du réseau retourne l'IP
# vue par les services externes, pas l'IP WAN de la box.
# Pour voir la vraie IP WAN : admin box → 192.168.1.1 → WAN → Caractéristiques
```

---

## 15. Python 3.5 — Compatibilité (PC3 zeta-backup Ubuntu 14.04)

> PC3 tourne Ubuntu 14.04 LTS avec **Python 3.5.2** (fin de vie 2017).
> Les adaptations ci-dessous sont obligatoires pour les scripts déployés sur PC3.

### f-strings → .format() (Python < 3.6)

```python
# ❌ INTERDIT sous Python 3.5 — SyntaxError immédiate
msg = f"CPU: {cpu_percent}%"

# ✅ CORRECT — .format() valide depuis Python 2
msg = "CPU: {}%".format(cpu_percent)
msg = "CPU: {cpu}%".format(cpu=cpu_percent)
msg = "Host {h} — CPU {c:.1f}%".format(h=hostname, c=cpu_pct)
```

### PYTHONNOUSERSITE=1 — contourner distutils-precedence.pth

```bash
# Symptôme : ImportError bizarre ou exception au démarrage Python
# Cause : distutils-precedence.pth (présent sur certains Ubuntu 14.04 mis à jour)
#         modifie sys.path dès le démarrage → conflits de versions de setuptools

# Solution : désactiver le site-packages utilisateur
PYTHONNOUSERSITE=1 python3 script.py

# Dans un script SSH lancé depuis PC1 (CMD_LINUX dans zeta_monitor.py) :
CMD_LINUX = "PYTHONNOUSERSITE=1 python3 /home/hprzeta/projet_zeta/scripts/mon_script.py"
```

### OpenBSD — CPU via top (pas /proc/stat)

```bash
# ❌ INTERDIT sous OpenBSD — /proc n'existe pas (kernel OpenBSD)
with open('/proc/stat') as f:
    ...

# ✅ CORRECT sous OpenBSD — lire top en mode batch (-b -n 1 = une seule capture)
top -b -n 1

# Extraire le % idle puis calculer cpu = 100 - idle
# Ligne typique de top OpenBSD :
# CPU:  2.3% user,  0.0% nice,  1.5% sys,  0.0% interrupt, 96.2% idle
# NF-1 = avant-dernier champ = valeur idle sans le symbole "%"
top -b -n 1 | awk '/^CPU/{gsub(/%/,"",$NF); idle=$NF; print 100-idle; exit}'

# Parser en Python (len(p) >= 5 suffit pour OpenBSD — NF ~ 10 champs)
p = line.split()           # ['CPU:', '2.3%', 'user,', ...]
if len(p) >= 5:
    idle = float(p[-1].replace('%',''))   # dernier champ = idle%
    cpu  = 100.0 - idle
```

### Tableau de compatibilité Python

| Fonctionnalité | Python 3.5 | Python 3.6+ | Solution |
|---|---|---|---|
| f-strings `f"..."` | ❌ SyntaxError | ✅ | `.format()` ou `%` |
| `asyncio.run()` | ❌ | ✅ 3.7+ | `loop.run_until_complete()` |
| Walrus operator `:=` | ❌ | ✅ 3.8+ | Variable intermédiaire |
| `dict` ordonné garanti | ❌ | ✅ 3.7+ | `collections.OrderedDict` |
| `PYTHONNOUSERSITE` | ✅ (contournement) | souvent inutile | Utiliser si erreur import |

---

## Leçons importantes apprises (pièges à éviter)

| Piège | Explication | Solution |
|---|---|---|
| `net.inet6.ip6.accept_rtadv` | N'existe pas sous OpenBSD (FreeBSD/NetBSD seulement) | SLAAC natif, juste passer les RA dans pf |
| `neighbrsolicit` dans pf | Nom invalide sous OpenBSD | Utiliser `neighbrsol` |
| NBSP dans config WireGuard | Copier-coller depuis mobile insère `\xc2\xa0` | `sed -i 's/\xc2\xa0/ /g' fichier` |
| `curl -4 ifconfig.me` pour détecter CGNAT | Teste depuis l'intérieur = résultat trompeur | Comparer avec IP WAN de la box (admin 192.168.1.1) |
| `crontab -e` cassé sur vieille machine | Python 3.5 / distutils absent | `(crontab -l; echo "...") \| crontab -` |
| `sed -i 's\|...\|'` sous BSD | BSD sed n'accepte pas `\|` comme séparateur | Utiliser `-i ''` et `/` ou `#` |
| SVG dans `scripts/` | Scripts .sh → `scripts/`, SVG → `docs/images/` | Toujours vérifier le bon dossier |
| IPv6 DuckDNS champ séparé | Dashboard DuckDNS : champ A ≠ champ AAAA | Remplir le champ "adresse ipv6" séparément |
| pf bloque SLAAC | `block in` bloque les Router Advertisements ICMPv6 | Ajouter `pass in ... icmp6-type {routeradv,...}` |
| f-string sur PC3 Python 3.5 | `SyntaxError: invalid syntax` à l'exécution | Remplacer tous les `f"..."` par `.format()` |
| `PYTHONNOUSERSITE` absent | PC3 Ubuntu 14.04 : `distutils-precedence.pth` corrompt le path | Préfixer : `PYTHONNOUSERSITE=1 python3 ...` |
| CPU OpenBSD via `/proc/stat` | `/proc` n'existe pas sous OpenBSD → `FileNotFoundError` | Utiliser `top -b -n 1` + awk, `len(p) >= 5` pour parser |
| `len(p) >= 7` pour parser `top` OpenBSD | OpenBSD `top -b -n 1` produit ~10 champs (moins que Linux) | Utiliser `len(p) >= 5` ; idle = dernier champ (`p[-1]`) |

---

## 16. nm / ldd / dpkg — Diagnostic bibliothèques partagées (.so)

Protocole de diagnostic quand un `.so` ne fonctionne pas ou produit des résultats suspects entre deux machines.

### nm — Symboles exportés par un .so

```bash
# Lister toutes les fonctions publiques (T = text, symbole global)
nm -D scan_arb.so | grep " T "

# Exemples de sortie :
# 00000000000014c0 T scan_zeros_arb    ← fonction exportée ✅
# (rien)                               ← fonction introuvable → .so mal compilé ou mauvais fichier

# Comparer les exports entre deux machines
nm -D local/scan_arb.so | grep " T "
ssh -i ~/.ssh/id_acer hprzeta@192.168.1.52 "nm -D ~/projet_zeta/.../scan_arb.so | grep ' T '"
```

### ldd — Dépendances d'un .so (bibliothèques liées)

```bash
# Voir toutes les dépendances
ldd scan_arb.so

# Chercher une lib spécifique ou les libs manquantes
ldd illinois_arb.so | grep -E 'arb|flint|not found'

# Sortie typique :
# libflint-arb.so.2 => /lib/x86_64-linux-gnu/libflint-arb.so.2  ← trouvé ✅
# libflint-arb.so.2 => not found                                 ← manquant ❌

# Sur une machine distante
ssh -i ~/.ssh/id_acer hprzeta@192.168.1.52 "ldd ~/projet_zeta/.../illinois_arb.so"
```

**Note :** `ldd | grep arb` retourne exit code 1 si aucune correspondance (comportement grep normal). Ce n'est pas une erreur si la lib utilise volontairement libm uniquement (ex: `scan_arb.so` = C pur sans arb).

### dpkg — Paquets installés (Debian/Ubuntu)

```bash
# Chercher un paquet par nom
dpkg -l | grep -E 'flint|arb'

# Sortie typique :
# ii  libflint-arb2:amd64  1:2.23.0-1+b1  amd64  C library for arbitrary-precision ball arithmetic
# ii  libflint-arb-dev     1:2.23.0-1+b1  amd64  development files

# Installer si manquant
sudo apt install libflint-arb-dev libflint-arb2

# OpenBSD (PC4) — équivalent
pkg_info | grep flint
pkg_add flint
```

### Distinction python-flint vs libflint-arb2

| Paquet | Source | Usage |
|---|---|---|
| `libflint-arb2` (apt) | Bibliothèque système | Liée par les `.so` C (illinois_arb.so) |
| `python-flint` (pip) | Package Python | `arb_wrapper.py` → `arb_hardy_z()` en Python |

`libflint-arb2` présent + `python-flint` absent → `illinois_arb.so` fonctionne (C) mais `ARB_DISPONIBLE=False` en Python → fallback `mpmath.siegelz`. Installer séparément :

```bash
# Sur PC2 (système Python3) — si pip3 disponible
pip3 install python-flint

# Vérifier
python3 -c "from arb_wrapper import ARB_DISPONIBLE; print(ARB_DISPONIBLE)"
```

---

## pip sur Debian externally-managed (Python 3.11+, PEP 668)

Debian 12 et Ubuntu 23.04+ bloquent `pip install` système par défaut (PEP 668).

```bash
# Option 1 — install utilisateur (sans sudo, packages dans ~/.local/)
pip3 install paquet --user

# Option 2 — forcer install système (machines dédiées calcul, pas de serveur de prod)
pip3 install paquet --break-system-packages

# Option 3 — venv (isolation propre, recommandé pour projets)
python3 -m venv ~/mon_venv
source ~/mon_venv/bin/activate
pip install paquet
```

**Attention PYTHONPATH en SSH :** un package installé `--user` est dans `~/.local/lib/pythonX.Y/site-packages/`.
Si le script est lancé via `ssh host "python3 script.py"` (shell non-interactif), ce chemin peut être absent.
Vérifier : `ssh host "python3 -c 'import sys; print([p for p in sys.path if \".local\" in p])'"`.
Si vide : passer `PYTHONUSERSITE=1` dans la commande SSH, ou utiliser `--break-system-packages`.

*Leçon session 2026-06-17 — python-flint 0.8.0 installé sur PC2 (Debian 12, Python 3.11).*

---

## 17. Alias Riemann_Lab — distribution PC1+PC2

Alias ajoutés au `~/.bashrc` de PC1 (session 2026-06-17) pour lancer la distribution
PC1+PC2 sans passer par Claude Code — script autonome `scripts/zeta_distribute_run.sh`.

```bash
zeta-distribute 500000          # lance T=500k distribué PC1+PC2 + dashboard
zeta-distribute 1000000         # lance T=1M
zeta-distribute 500000 --no-dashboard  # sans dashboard tmux
zeta-progress                   # s'attacher au dashboard en cours
zeta-pid                        # voir PID du run actif
zeta-log                        # suivre le log en temps réel
```

**Détail du script `zeta_distribute_run.sh` :**
- Active le turbo (`sudo scripts/zeta_turbo_on.sh` — sudoers NOPASSWD, non interactif).
- Lance `zeta_run_progress.py` dans une session tmux `zeta-progress` (sauf `--no-dashboard`).
- Lance `zeta_distribute.py $T_MAX` en `nohup`, détaché, avec confirmation auto-répondue
  (`printf "O\n" |`) — sans quoi le script plante en `EOFError` (pas de TTY pour `input()`).
- PID écrit dans `/tmp/zeta_distribute.pid`, log dans `logs/distribute_T<T_MAX>_nohup_<horodatage>.log`.

**Limites connues :**
- `--help` n'est pas géré : `zeta-distribute --help` lancerait un vrai run avec
  `T_MAX="--help"` (ne pas l'utiliser ; pas de validation d'argument dans le script).
- `zeta-log` (`tail -f ... | tail -1`) ne s'arrête jamais tout seul (`tail -f` est bloquant) —
  utile pour suivre en direct, mais ne convient pas à un usage scripté/non interactif.

---

## 18. wg_auto.sh — Bascule WireGuard automatique maison/déplacement (PC1)

### Règle maison / déplacement

| Situation | Test | Action |
|---|---|---|
| 🏠 **Maison** | PC4 (`192.168.1.54`) joignable en ping direct sur l'interface physique | `wg0` **DOWN** (LAN direct, plus rapide) |
| 🧳 **Déplacement** | PC4 injoignable en LAN | `wg0` **UP** (tunnel via DuckDNS) |

**Cause du besoin :** les `AllowedIPs` du tunnel incluent `192.168.1.0/24` (LAN maison).
Si `wg0` reste monté à la maison, le routage tente de passer par le tunnel au lieu du
LAN direct — or la box SFR ne fait pas de NAT loopback (pas de hairpinning), donc le
trafic vers l'IP publique/DuckDNS depuis l'intérieur du LAN échoue ou boucle. Il faut
donc désactiver `wg0` quand PC4 est joignable en direct, et l'activer sinon.

### Le script

`scripts/wg_auto.sh` :
- Ping `192.168.1.54` (PC4) en forçant l'interface physique (`ip route ... | grep -v wg0`,
  jamais `wg0` lui-même, sinon le test est faussé par le tunnel en cours).
- **Maison** (ping OK) → si `wg0` actif : `sudo wg-quick down wg0`.
- **Déplacement** (ping KO) → si `wg0` inactif : `sudo wg-quick up wg0`, puis vérifie le
  tunnel avec un ping sur `10.10.0.1` (passerelle VPN côté PC4).
- Log dans `logs/wg_auto.log` (append) + notification bureau (`notify-send`) systématique.

### Les 3 messages possibles

```
🏠 MAISON — WireGuard DÉSACTIVÉ                          # wg0 était up, vient d'être coupé
🏠 MAISON — WireGuard déjà désactivé                      # rien à faire (mode --quiet : silencieux)
🧳 DÉPLACEMENT — WireGuard ACTIVÉ                         # wg0 monté, tunnel 10.10.0.1 répond
🧳 DÉPLACEMENT — WireGuard déjà activé                    # rien à faire (mode --quiet : silencieux)
⚠️ DÉPLACEMENT — WireGuard activé mais tunnel NE RÉPOND PAS  # wg0 up mais 10.10.0.1 ne répond pas
                                                            # → vérifier connexion internet / DuckDNS
```

### Utilisation

```bash
wg-auto                       # alias ~/.bashrc — affiche le message dans le terminal
bash scripts/wg_auto.sh       # équivalent direct
bash scripts/wg_auto.sh --quiet   # pas d'affichage terminal si déjà dans le bon état
                                   # (utilisé par le dispatcher NetworkManager)

zeta-cluster                  # scripts/zeta_tmux.sh appelle wg_auto.sh (sans --quiet)
                               # avant de monter la session tmux du cluster
```

### Intégration NetworkManager (automatique à chaque connexion réseau)

`/etc/NetworkManager/dispatcher.d/99-wg-auto` appelle `wg_auto.sh --quiet` à chaque
événement `up`/`vpn-up` — la notification bureau prévient du basculement sans action
manuelle. Nécessite `sudo -u riemann` (le dispatcher tourne en root) et une entrée
`sudoers` `NOPASSWD` ciblée pour `wg-quick`/`wg show` (sinon `sudo` bloque en
non-interactif, faute de TTY).
