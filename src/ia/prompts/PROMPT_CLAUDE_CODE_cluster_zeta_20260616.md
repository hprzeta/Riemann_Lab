> **Fichier :** PROMPT_CLAUDE_CODE_cluster_zeta_20260616.md · **Dossier :** local (usage unique, coller dans Claude Code)
> **Branche :** — · **Auteur :** hprzeta · **MAJ :** 2026-06-16

---

> ⚠️ **ARCHIVE (2026-06-16)** — document historique. Les infos cluster (IP, hostnames,
> versions) peuvent être périmées. Source de vérité actuelle : Architecture-Cluster-Zeta.md

---

# PROMPT CLAUDE CODE — Session cluster Zeta 16 juin 2026

> Colle ce prompt dans Claude Code (terminal `~/projet_zeta/`).
> Les tâches sont ordonnées du plus facile au plus complexe.
> Exécute-les dans l'ordre. Entre chaque tâche, `git status` + commit avant de passer à la suivante.

---

## CONTEXTE À LIRE EN PREMIER

Tu travailles sur le projet `Riemann_Lab` de hprzeta.
- Repo principal : `~/projet_zeta/Riemann_Lab/`
- Wiki : `~/projet_zeta/Riemann_Lab.wiki/`
- Branche code courante : `Riemann_Lab_C`
- Wiki branche : `master`
- **Jamais `git add -A`** — toujours `git add` fichier par fichier
- **Jamais pousser `Handoff.md`** (gitignoré, local only)
- Tout `.md` produit porte un **en-tête ET un pied de page** avec date et auteur `hprzeta`

**Résumé de ce qui s'est passé les 14-15 juin (à connaître pour toutes les tâches) :**

Le cluster Zeta a été finalisé à 4 machines. PC4 (`zeta-secure`, Dell Dimension 4500, Pentium 4 i386)
a été installé sous OpenBSD 7.9, configuré comme bastion WireGuard. La box SFR est en CGNAT IPv4
(IP WAN = 10.153.18.138, privée), donc l'accès externe passe par IPv6. DuckDNS
`zeta-secure.duckdns.org` maintient A + AAAA. Le tunnel WireGuard téléphone (4G) ↔ PC4 est
fonctionnel via IPv6 depuis la nuit du 15/06.

---

## TABLE DE RÉFÉRENCE CLUSTER — ÉTAT OFFICIEL AU 16/06/2026

⚠️ UTILISE EXCLUSIVEMENT CETTE TABLE — elle corrige les noms anciens.

| # | Hostname OFFICIEL | Alias réseau | IP LAN | OS | CPU | Rôle | Statut |
|---|---|---|---|---|---|---|---|
| PC1 | `zeta-lab` | zeta-lab | 192.168.1.24 | Ubuntu Linux | Intel i7-7500U | Orchestrateur / calcul principal (WiFi wlp2s0) | ✅ |
| PC2 | `zeta-calc-second` | — | 192.168.1.52 | Debian 6.1 amd64 | Core2Duo E8400 @3.0GHz | Calcul secondaire | ✅ |
| PC3 | `zeta-backup` | — | 192.168.1.22 | Ubuntu 18.04 LTS | Pentium E2140 @1.6GHz | Backup + log-dns-moni (pending) | ✅ |
| PC4 | `zeta-secure` | zeta-del | 192.168.1.54 | OpenBSD 7.9 i386 | Pentium 4 @2.4GHz | Bastion VPN/pare-feu | ✅ COMPLET |

**Users SSH :**
- PC1 : `riemann@zeta-lab` (alias ssh : `zeta-hp` dans tmux)
- PC2 : `hprzeta@zeta-calc-second`
- PC3 : `hprzeta@zeta-backup`
- PC4 : `hprzeta@zeta-secure` (alias ssh : `zeta-secure`)

**Session tmux sur PC1 :** `[zeta] 0:ssh*M` — les connexions aux autres machines se font
depuis PC1 via tmux (visible dans le screenshot : fenêtre tmux verte = PC1 orchestrateur).

**Couleurs terminaux (pour documentation et SVG) :**
- PC1 zeta-lab : fond **cyan/vert clair** (Ubuntu, couleur distinctive)
- PC2 zeta-calc-second : fond **jaune/orange** (Debian)
- PC3 zeta-backup : fond **cyan clair** (Ubuntu 18.04)
- PC4 zeta-secure : fond **noir** (OpenBSD, sobre et sécurisé)
- Barre tmux : fond **vert foncé**

**WireGuard :**
- Réseau VPN : `10.10.0.0/24`
- PC4 serveur : `10.10.0.1/24`, clé pub `/IsrTt7DGhqvCoVr/pgcUuBBpVnNdzUsuUPkGGIwtzY=`
- PC1 client : `10.10.0.2/32`, clé pub `vRmxPmusiEIM2RegkvhKXpSTbLFAXFvQDYLl4KoFqmk=`
- Téléphone client : `10.10.0.3/24`, clé pub `6euaNc/uLQc/PYL2/CAWYR391gE7vRSF+CH3ueO+8yc=`
- DuckDNS : `zeta-secure.duckdns.org` → A=93.1.104.93 (CGNAT, inutilisable) / AAAA=2a02:8428:80a6:da01:ad39:37b9:a638:126c
- Cron PC4 : `*/5 * * * *` → `/etc/duckdns/duck.sh` (A + AAAA auto)

**Scripts cluster (PC1, `~/projet_zeta/`) :**
- `zeta_turbo_on.sh` — avant chaque run calcul (governor performance, swappiness=10, stoppe 7 services)
- `zeta_turbo_off.sh` — après run
- Scripts SSH couleurs tmux : changement de couleur de la barre tmux selon la machine connectée
  (à documenter dans la procédure cluster — voir Tâche 1)

---

## TÂCHE 1 — Mise à jour `Architecture-Cluster-Zeta.md` (wiki) [FACILE, FAIRE EN PREMIER]

**Fichier cible :** `~/projet_zeta/Riemann_Lab.wiki/Architecture-Cluster-Zeta.md`

**Ce que tu dois faire :**

1. Lire le fichier actuel (`cat` ou `view`).
2. Mettre à jour **toutes** les machines avec les hostnames officiels de la table ci-dessus.
   - PC2 = `zeta-calc-second` (PAS `zeta-hp3647h`)
   - PC3 = `zeta-backup` (PAS `zeta-livermore8`)
   - PC4 = `zeta-secure` ✅
3. Corriger l'OS de PC3 : Ubuntu 18.04 LTS (pas Linux Lite).
4. Mettre à jour le diagramme ASCII :

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
PC1 .24      PC2 .94        PC3 .22           [box SFR]
zeta-lab   zeta-calc-     zeta-backup         GR140IG
Ubuntu i7  second Debian  Ubuntu 18.04        CGNAT IPv4
Orchestr.  Core2Duo       backup+log          WAN=10.153.x
WG:10.10.0.2              (log pending)

Téléphone (10.10.0.3) ──WireGuard IPv6──▶ PC4 ──▶ tout le LAN
PC1 distant (10.10.0.2) ──WireGuard──▶ PC4 ──▶ tout le LAN
```

5. Ajouter ou mettre à jour la section **WireGuard** (peers, CGNAT, IPv6, DuckDNS AAAA).

6. Ajouter une section **"Procédure de connexion au cluster"** :

```markdown
## Procédure de connexion au cluster (depuis PC1)

### Prérequis
- Lancer tmux session `zeta` : `tmux new -s zeta` ou `tmux attach -t zeta`
- Les alias SSH sont définis dans `~/.ssh/config` sur PC1

### Connexions directes (LAN)
```bash
ssh zeta-hp          # → riemann@zeta-lab (PC1 lui-même, local)
ssh zeta-calc-second # → hprzeta@192.168.1.52 (PC2)
ssh zeta-backup      # → hprzeta@192.168.1.22 (PC3)
ssh zeta-secure      # → hprzeta@192.168.1.54 (PC4 OpenBSD)
```

### Connexion depuis l'extérieur (VPN WireGuard actif)
```bash
# 1. Activer WireGuard sur le device mobile/distant
#    Endpoint : zeta-secure.duckdns.org:51820
# 2. Depuis le device, accès direct au LAN :
ssh riemann@192.168.1.24   # PC1 zeta-lab
ssh hprzeta@192.168.1.52   # PC2 zeta-calc-second
ssh hprzeta@192.168.1.22   # PC3 zeta-backup
```

### Couleurs tmux par machine
Les scripts SSH changent la couleur de la barre tmux pour identifier visuellement la machine :
- **Cyan/vert** → PC1 zeta-lab (Ubuntu, machine principale)
- **Jaune/orange** → PC2 zeta-calc-second (Debian)
- **Cyan clair** → PC3 zeta-backup (Ubuntu 18.04)
- **Noir** → PC4 zeta-secure (OpenBSD — sobre, bastion)

Script type dans `~/.ssh/config` ou wrapper ssh :
```bash
# Changer couleur barre tmux à la connexion
tmux set-option -g status-bg colour<N>
ssh hprzeta@192.168.1.52
tmux set-option -g status-bg colour<DEFAULT>   # restaurer au retour
```

### Scripts pré-run obligatoires (PC1)
```bash
# Avant tout run de calcul zéros :
bash ~/projet_zeta/zeta_turbo_on.sh

# Lancer le run (exemple) :
cd ~/projet_zeta/src/
nohup python compute_zeros_v9.py ... &

# Après le run :
bash ~/projet_zeta/zeta_turbo_off.sh
```
```

7. Mettre à jour **en-tête ET pied de page** (date `2026-06-16`, recompter les lignes).

8. **Commit wiki :**
```bash
cd ~/projet_zeta/Riemann_Lab.wiki/
git add Architecture-Cluster-Zeta.md
git commit -m "docs(cluster): update hostnames zeta-calc-second/zeta-backup/zeta-secure, WireGuard IPv6, procédure connexion couleurs tmux"
git push origin master
```

---

## TÂCHE 2 — Mise à jour SVG `top_machine.svg` et `backup_cluster.svg` [MOYEN]

**Fichiers cibles :**
```bash
find ~/projet_zeta/Riemann_Lab/docs/ -name "*.svg" | head -20
```

**Ce que tu dois faire :**

1. Lire chaque SVG existant.
2. Mettre à jour les `<text>` de chaque machine avec les **hostnames officiels** :

| Machine | Hostname SVG | IP | OS | CPU | Couleur fond |
|---|---|---|---|---|---|
| PC1 | `zeta-lab` | 192.168.1.24 | Ubuntu Linux | Intel i7-7500U | #00CED1 (cyan) |
| PC2 | `zeta-calc-second` | 192.168.1.52 | Debian 6.1 | Core2Duo E8400 | #FFD700 (jaune) |
| PC3 | `zeta-backup` | 192.168.1.22 | Ubuntu 18.04 LTS | Pentium E2140 | #87CEEB (cyan clair) |
| PC4 | `zeta-secure` | 192.168.1.54 | OpenBSD 7.9 i386 | Pentium 4 @2.4GHz | #1a1a1a (noir) |

3. Pour `top_machine.svg` : ajouter **"Bastion VPN"** et **"WireGuard 10.10.0.1"** sur la case PC4.
4. Pour `backup_cluster.svg` : vérifier les flèches (PC1 → rsync SSH → PC3 01:50, PC3 → rclone → Proton Drive 02:00).
5. **Commit `Riemann_Lab_C` :**
```bash
cd ~/projet_zeta/Riemann_Lab/
git checkout Riemann_Lab_C
git add docs/top_machine.svg docs/backup_cluster.svg
git commit -m "docs(svg): correct hostnames zeta-calc-second/zeta-backup/zeta-secure, colors per terminal theme"
git push origin Riemann_Lab_C
```

---

## TÂCHE 3 — Mise à jour `Fichier-des-Prompts.md` (wiki) [MOYEN]

**Fichier cible :**
```bash
ls ~/projet_zeta/Riemann_Lab.wiki/ | grep -i prompt
```

**Ce que tu dois faire :**

1. Lire le fichier entier, repérer la **dernière entrée datée**.
2. **Ajouter à la fin** (append uniquement, ne jamais supprimer l'existant) :

```markdown
---

## Session 14-15 juin 2026 — Cluster Zeta : bastion PC4 zeta-secure + tunnel WireGuard externe

### Contexte
Sessions de nuit (14/06 ~22h → 15/06 ~02h45). Objectif : finaliser les hostnames du cluster,
déployer PC4 comme bastion WireGuard sous OpenBSD, rendre le cluster accessible de l'extérieur
(téléphone en 4G). Renommage définitif des machines :
- PC2 → `zeta-calc-second` (Debian 6.1 amd64, Core2Duo E8400)
- PC3 → `zeta-backup` (Ubuntu 18.04 LTS, Pentium E2140)
- PC4 → `zeta-secure` (OpenBSD 7.9 i386, Pentium 4, bastion VPN)

### Prompts clés utilisés

**[14/06] Architecture cluster — décision finale 4 nœuds + hostnames**
> "changement de plan final : on garde PC1-icore7-zeta-orchestrateur, PC2-hp-zeta-calc-second,
> PC3-acer-zeta-backup et PC4-delpentium4-zeta-secure. Le PC-i386-tinycore marche mais pas de
> carte réseau, et on vire le PC5 (pas de barrette mémoire)."
> Résultat : architecture 4 nœuds figée, hostnames renommés ✅

**[14/06] Installation OpenBSD PC4 zeta-secure**
> "Installe OpenBSD 7.9 sur PC4 Dell Dimension 4500 (i386). Configure doas, applique syspatch."
> Résultat : OpenBSD opérationnel, syspatch appliqué (002_smtpd), doas configuré ✅

**[14/06] WireGuard tunnel local PC1 ↔ PC4**
> "Configure WireGuard sur PC4 (serveur 10.10.0.1) et PC1 (client 10.10.0.2). Teste avec ping."
> Résultat : handshake OK, 0% perte, tunnel chiffré LAN ✅
> Incident : NBSP (\xc2\xa0) dans la PrivateKey → fix : `sed -i 's/\xc2\xa0/ /g' wg0.conf`

**[14/06] DuckDNS — zeta-secure.duckdns.org**
> "Configure DuckDNS. Script /etc/duckdns/duck.sh, cron */5 sur PC4."
> Résultat : A enregistré (93.1.104.93) ✅

**[14/06] Peer téléphone WireGuard — premier essai**
> "Génère config WireGuard téléphone Android. Endpoint = zeta-secure.duckdns.org:51820.
> Génère QR code pour import."
> Résultat : ❌ rx=0, tx croît (keepalive OK) mais rien ne revient — bloqué pour la nuit.

**[15/06] Diagnostic CGNAT — cause racine n°1**
> "Le téléphone envoie mais reçoit rien. Qu'est-ce qui bloque ?"
> IP WAN box = 10.153.18.138 (RFC1918) → CGNAT confirmé. Port forwarding IPv4 impossible.
> Décision : basculer sur IPv6 ✅

**[15/06] SLAAC OpenBSD — pf bloque les Router Advertisements**
> "PC4 n'obtient pas d'adresse IPv6 globale malgré inet6 autoconf."
> Cause : `block in` par défaut bloque ICMPv6 type 134 (routeradv).
> Fix pf.conf :
> `pass in on $ext_if inet6 proto icmp6 icmp6-type {routeradv, neighbradv, neighbrsol, redir}`
> Piège : `neighbrsolicit` invalide → nom correct = `neighbrsol`
> Résultat : adresse globale 2a02:8428:80a6:da01:ad39:37b9:a638:126c obtenue ✅

**[15/06] DuckDNS AAAA — enregistrement IPv6 séparé**
> "Enregistre l'IPv6 de PC4 dans le champ AAAA séparé du dashboard DuckDNS."
> Résultat : `host -t AAAA zeta-secure.duckdns.org` → correct ✅

**[15/06] Pare-feu IPv6 box SFR — cause racine n°2**
> "pf OK, IPv6 OK, AAAA OK, mobile a IPv6, mais toujours rx=0. Qu'est-ce qui reste ?"
> Section « Réseau v6 » de la box SFR = pare-feu IPv6 indépendant du NAT IPv4, liste blanche vide.
> Fix : règle WireGuard-IPv6 → dest 2a02:...126c / UDP 51820 / Activer=On
> Résultat : handshake 4G bidirectionnel ✅ SUCCÈS FINAL

**[15/06] Élargissement accès LAN téléphone**
> "Donne au peer téléphone accès 10.10.0.0/24 + 192.168.1.0/24."
> `doas wg set wg0 peer 6euaN... allowed-ips 10.10.0.0/24,192.168.1.0/24`
> Sur téléphone : éditer tunnel → Adresses IP autorisées : `10.10.0.0/24, 192.168.1.0/24` ✅

**[15/06] DuckDNS script v2 — A + AAAA auto (rotation SLAAC)**
> "Script duck.sh qui extrait l'IPv6 stable de re0 et met à jour AAAA dynamiquement."
> `IP6=$(ifconfig re0 | awk '/inet6/ && !/fe80/ && !/temporary/ {print $2; exit}')`
> Cron */5 déjà en place → maintient A et AAAA à jour ✅

### Leçons retenues (15 juin 2026)
1. `curl -4 ifconfig.me` depuis l'intérieur du réseau ne détecte pas le CGNAT.
2. Sous OpenBSD, `block in` bloque les RA → SLAAC échoue même avec `AUTOCONF6` actif.
3. `net.inet6.ip6.accept_rtadv` n'existe pas sous OpenBSD (FreeBSD/NetBSD seulement).
4. pf ICMPv6 : nom correct = `neighbrsol` (pas `neighbrsolicit`).
5. Box SFR GR140IG : pare-feu IPv6 **séparé** du NAT IPv4 — section « Réseau v6 ».
6. DuckDNS : champs A et AAAA distincts sur le dashboard et dans l'API (`&ipv6=ADDR`).
7. NBSP (\xc2\xa0) dans les fichiers de config WireGuard (copier-coller mobile) → erreur
   "wrong length or format". Fix : `sed -i 's/\xc2\xa0/ /g' fichier.conf`
```

3. Mettre à jour **en-tête ET pied de page** (date `2026-06-16`).
4. **Commit wiki :**
```bash
cd ~/projet_zeta/Riemann_Lab.wiki/
git add Fichier-des-Prompts.md
git commit -m "docs(prompts): add sessions 14-15 juin — zeta-secure, WireGuard IPv6, CGNAT, hostnames définitifs"
git push origin master
```

---

## TÂCHE 4 — PDF enrichi `doc_zeta_secure_cluster_enrichi.pdf` [COMPLEXE]

**Objectif :** Version enrichie et pédagogique du PDF sessions 14-15 juin, qui explique
**à quoi sert cette infrastructure dans le projet Riemann_Lab** (accès distant aux calculs,
supervision des runs), avec les captures d'écran intégrées.

**Fichier source :** cherche avec :
```bash
find ~/projet_zeta/ -name "doc_zeta_secure*" 2>/dev/null
```

**Fichier de sortie :** `~/projet_zeta/pdf/optimisation/doc_zeta_secure_cluster_enrichi.pdf`

**Captures d'écran disponibles** (dans `~/projet_zeta/pdf/optimisation/screens/` ou à demander) :

| Fichier screen | Contenu clé | Section PDF |
|---|---|---|
| screen_box_wan.jpg | Box GR140IG — IPv4 WAN = **10.153.18.138** (CGNAT proof) | §3 CGNAT |
| screen_wg_ipv4.jpg | Règle WireGuard IPv4 → 192.168.1.54:51820, On | §4 WireGuard |
| screen_wg_ipv6.jpg | Règle WireGuard-IPv6 → 2a02:...126c:51820, On | §7.8 cause racine n°2 |
| screen_duckdns.jpg | Dashboard DuckDNS — compte hprzeta@github, jeton, 14 juin | §5 DDNS |
| screen_lan_devices.jpg | Équipements LAN : zeta-livermore8 + 2 MAC off | §2.2 architecture |
| screen_zeta_backup.jpg | zeta-backup — IP 192.168.1.22, MAC 00:01:6C..., LAN 2 | §2.2 |
| screen_phonea.jpg | PhoneA — WiFi 5GHz, IP 192.168.1.111, IPv6 2a02:...fed5:50f6 | §6 peer téléphone |
| screen_terminal.jpg | tmux zeta-lab : 3 panneaux (zeta-calc-second jaune, zeta-backup cyan, zeta-secure noir) | §2 cluster |

> Si les screens ne sont pas encore dans ce dossier, crée le dossier et indique à l'utilisateur
> de les y copier depuis son téléphone avant de générer le PDF.

### Structure du PDF enrichi (en français)

```markdown
# Cluster Zeta — Infrastructure VPN et accès distant
## Pour le projet Riemann_Lab / Hypothèse de Riemann
### hprzeta — Sessions 14-15 juin 2026

---

## 1. Le cluster Zeta dans le projet Riemann_Lab

### 1.1 Pourquoi un cluster ?
- Calcul des 10 000+ premiers zéros non-triviaux de ζ(s) : intensif en CPU
- PC1 (zeta-lab, i7) = orchestrateur ; PC2 (zeta-calc-second) = calcul secondaire
- PC3 (zeta-backup) = sauvegarde des CSV précieux + futurs logs centralisés
- PC4 (zeta-secure) = accès sécurisé depuis l'extérieur → superviser les runs à distance

### 1.2 Utilité concrète du VPN pour Riemann_Lab
- Lancer `nohup python compute_zeros_v9.py ...` depuis le téléphone en 4G
- Surveiller les logs de run sans être devant PC1
- Déclencher `zeta_turbo_on.sh` / `zeta_turbo_off.sh` à distance
- Futur Objectif 2 : agent IA autonome qui tourne en permanence sur PC1,
  accessible depuis n'importe où via le tunnel

### 1.3 Architecture à 4 nœuds
[TABLE + DIAGRAMME ASCII + SCREENSHOT TERMINAL TMUX]

---

## 2. PC4 zeta-secure — Le bastion OpenBSD

### 2.1 Pourquoi OpenBSD ?
- Réputation de sécurité maximale (audit code, pf pare-feu natif)
- Très léger : parfait pour un Pentium 4 i386 (1 seul cœur, 32-bit)
- pf = pare-feu stateful puissant, syntaxe claire
- Seul nœud **exposé sur internet** → doit être le plus durci possible
- Si PC4 est compromis, les calculs et données sur PC1/PC2/PC3 survivent

### 2.2 Installation et durcissement
- Image cd79.iso, installation réseau
- syspatch : correctifs de sécurité appliqués
- doas (pas sudo) : `permit persist hprzeta`
- pf : politique default-deny en entrée, seuls SSH/WireGuard/ICMPv6-SLAAC autorisés

---

## 3. Le problème CGNAT et la stratégie IPv6

### 3.1 Qu'est-ce que le CGNAT ?
[Explication pédagogique + screenshot box GR140IG montrant IP WAN 10.153.18.138]
- Les FAI mutualisent une IP publique entre plusieurs abonnés
- La box voit une IP RFC1918 côté WAN → port forwarding IPv4 = impossible
- Erreur classique : `curl -4 ifconfig.me` depuis l'intérieur retourne 93.1.104.93
  (l'IP vue par les services externes), mais ce n'est PAS l'IP WAN de la box

### 3.2 La solution : IPv6 natif
- SFR alloue un préfixe /56 au LAN : 2a02:8428:80a6:da00::/56
- Chaque machine reçoit une adresse IPv6 globale directement routable
- PC4 obtient 2a02:8428:80a6:da01:ad39:37b9:a638:126c (via SLAAC)
- Problème SLAAC sous OpenBSD : pf bloquait les Router Advertisements → résolu

---

## 4. WireGuard — Le tunnel chiffré

### 4.1 Principe
[Schéma : Téléphone 4G ──IPv6 chiffré──▶ PC4 ──LAN──▶ PC1/PC2/PC3]
- Protocole VPN moderne, ultra-rapide, cryptographie Curve25519/ChaCha20
- Stateless : pas de handshake permanent, PersistentKeepalive=25s

### 4.2 Les 3 peers
[TABLE des peers avec IPs VPN et clés publiques]

### 4.3 Configuration box SFR
[SCREENSHOT règle WireGuard IPv4 + SCREENSHOT règle WireGuard-IPv6]
- Règle IPv4 (port forwarding) : inutile à cause du CGNAT, mais configurée
- Règle IPv6 indispensable : pare-feu IPv6 séparé de la box, liste blanche

---

## 5. DuckDNS — DNS dynamique pour IPv6 rotative

### 5.1 Problème : SLAAC renouvelle l'IPv6 toutes les ~12 min
### 5.2 Solution : cron + API DuckDNS
[SCREENSHOT dashboard DuckDNS]
- Domaine : zeta-secure.duckdns.org
- Script duck.sh : extrait l'IPv6 stable de re0, met à jour A + AAAA
- Cron */5 sur PC4

---

## 6. Procédure d'accès à distance (usage quotidien)

### 6.1 Depuis le téléphone en 4G
1. Ouvrir app WireGuard → activer tunnel `zeta-vpn`
2. Vérifier : `rx` doit augmenter → handshake établi
3. Dans Termux (ou app SSH) : `ssh riemann@192.168.1.24`
4. On est sur PC1 zeta-lab → accès complet au cluster

### 6.2 Supervision d'un run calcul
```bash
# Sur PC1 depuis le téléphone :
tmux attach -t zeta          # rejoindre la session tmux
tail -f ~/projet_zeta/logs/compute_zeros_v9_*.log  # suivre le run
```

---

## 7. Leçons apprises (synthèse technique)
[Reprendre les 7 leçons de la section 9 du PDF source]

---

## 8. État final au 15/06/2026 02h45
[Reprendre section 10 du PDF source]
```

### Génération du PDF

```bash
# 1. Créer le dossier screens si besoin
mkdir -p ~/projet_zeta/pdf/optimisation/screens/

# 2. Générer le .md source
# (Claude Code écrit le contenu complet dans /tmp/doc_enrichi.md)

# 3. Build PDF
pandoc /tmp/doc_enrichi.md \
  -o ~/projet_zeta/pdf/optimisation/doc_zeta_secure_cluster_enrichi.pdf \
  --pdf-engine=xelatex \
  --variable mainfont="DejaVu Serif" \
  --variable fontsize=11pt \
  --variable geometry:margin=2.5cm \
  --variable lang=fr \
  --variable colorlinks=true \
  2>&1

# Si build_pdf_riemann.sh disponible, l'utiliser à la place.

# 4. Push Proton Drive
rclone copy ~/projet_zeta/pdf/optimisation/doc_zeta_secure_cluster_enrichi.pdf \
  protondrive:hprzeta/Riemann_Lab/cours/ --progress
# 401 → rclone config reconnect protondrive:
# 422 = fichier déjà présent, normal
```

---

## TÂCHE 5 — Mise à jour `Handoff.md` [FINAL, 5 MIN]

**Fichier cible :** `~/projet_zeta/Handoff.md` (chercher aussi `~/riemann_handoff/Handoff.md`)

Réécrire complètement avec :

```markdown
> **Fichier :** Handoff.md · **Dossier :** local ~/projet_zeta/ (hors git, JAMAIS commit)
> **Branche :** — · **Auteur :** hprzeta · **MAJ :** 2026-06-16

# Handoff — État session 16 juin 2026

## Cluster Zeta — Hostnames officiels (DÉFINITIFS)

| PC | Hostname | IP LAN | OS | Rôle | État |
|---|---|---|---|---|---|
| PC1 | zeta-lab | 192.168.1.24 | Ubuntu Linux i7 | Orchestrateur + calcul | ✅ |
| PC2 | zeta-calc-second | 192.168.1.52 | Debian 6.1 amd64 | Calcul secondaire | ✅ |
| PC3 | zeta-backup | 192.168.1.22 | Ubuntu 18.04 LTS | Backup + log (pending) | ✅ |
| PC4 | zeta-secure | 192.168.1.54 | OpenBSD 7.9 i386 | Bastion VPN WireGuard | ✅ COMPLET |

## État calcul zéros
- 10 142 zéros calculés (T=9 998,85)
- v9 actif sur `Riemann_Lab_C` (brent_mpfr.c, prec_fast=64, prec_full=80)
- Validation Turing T=100k : COMPLÈTE, 0 zero manquant
- CSV de référence : `zeros_zeta_T10000_20260424_205325.csv` — NE PAS ÉCRASER

## WireGuard (PC4 zeta-secure)
- UDP 51820, réseau VPN 10.10.0.0/24
- Accès externe : IPv6 UNIQUEMENT (CGNAT confirmé, WAN box = 10.153.18.138)
- DuckDNS AAAA : zeta-secure.duckdns.org, cron */5 sur PC4

## Tâches faites cette session (16/06)
- [x] Architecture-Cluster-Zeta.md mis à jour wiki (hostnames + procédure cluster + couleurs tmux)
- [x] SVG top_machine + backup_cluster corrigés (hostnames officiels)
- [x] Fichier-des-Prompts.md — sessions 14-15 juin appendées
- [x] PDF doc_zeta_secure_cluster_enrichi.pdf généré + Proton Drive

## Prochaines actions
1. Tester ping/SSH depuis téléphone (Termux) → 192.168.1.24 via WireGuard actif en 4G
2. Vérifier rotation SLAAC PC4 : après ~12 min, AAAA DuckDNS se met à jour ?
3. PC3 zeta-backup → setup rôle log-dns-moni (dnsmasq, rsyslog, chrony, glances)
4. Reprendre calculs v9 T=100k → T=200k quand cluster stabilisé
5. Documenter scripts SSH couleurs tmux dans un fichier dédié `scripts-cluster.sh`
```

> ⚠️ **Ne jamais commit Handoff.md** — gitignoré sur toutes les branches.

---

## ORDRE D'EXÉCUTION

```
1. Tâche 1 — Architecture-Cluster-Zeta.md    [~20 min]  → git push wiki
2. Tâche 3 — Fichier-des-Prompts.md          [~20 min]  → git push wiki
3. Tâche 2 — SVG diagrams                    [~20 min]  → git push Riemann_Lab_C
4. Tâche 4 — PDF enrichi                     [~60 min]  → rclone Proton Drive
5. Tâche 5 — Handoff.md                      [~5 min]   → local only
```

**Entre chaque tâche :** `git status` pour vérifier qu'aucun fichier non voulu n'est staged.

---

*PROMPT_CLAUDE_CODE_cluster_zeta_20260616.md · local usage unique · hprzeta · MAJ 2026-06-16 · 320 lignes*
