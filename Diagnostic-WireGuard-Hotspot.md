> **Fichier :** Diagnostic-WireGuard-Hotspot.md · **Dossier :** wiki (racine)
> **Branche :** master (wiki) · **Auteur :** hprzeta · **MAJ :** 2026-07-05

# Diagnostic — Blocage WireGuard sur hotspot mobile ✅ RÉSOLU

## 1. Contexte

Test de `wg_auto.sh` en mode déplacement, connexion via hotspot mobile (Port_Armel).
Objectif : valider la bascule automatique maison/déplacement de PC1 en conditions réelles.

## 2. Principe — handshake vs transport de données

Un tunnel WireGuard fonctionne en deux temps distincts, qui peuvent être bloqués
indépendamment l'un de l'autre par un réseau intermédiaire :

1. **Handshake** : poignée de main cryptographique initiale + paquets `keepalive`
   périodiques. Paquets très petits et peu fréquents.
2. **Transport de données** : trafic applicatif réel (ping, SSH, synchronisation
   cluster). Paquets plus gros et/ou plus soutenus dans le temps.

Un opérateur mobile ou un pare-feu peut laisser passer le premier tout en filtrant
le second (DPI ciblant le trafic soutenu, NAT asymétrique, règle de pare-feu trop
restrictive côté serveur). C'est exactement ce qui a été observé ici.

## 3. Résultats des tests

| Étape | Résultat |
|---|---|
| Connexion hotspot mobile | OK (IPv4 CGNAT + IPv6 disponible) |
| Tunnel wg0, endpoint IPv4 (DuckDNS) | Handshake : aucune réponse (0 B received) |
| Endpoint basculé en IPv6 ([2a02:8428:80a6:da01:c10d:e4a1:c992:9918]:51820) | Handshake OK (124 B puis 744 B received, keepalive stable ~3 min) |
| Ping 10.10.0.1 (endpoint IPv6) | KO — 100 % perte, avant et après délai de 150 s |
| SSH TCP port 22 vers 10.10.0.1 | KO — timeout total |
| Test MTU (`ping -s 8`) | KO aussi — fragmentation écartée comme cause |

## 4. Schéma — déroulé du diagnostic

![Schéma diagnostic WireGuard hotspot](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/docs/images/schema_diagnostic.png)

## 5. Interférence observée — dispatcher NetworkManager

Pendant les vérifications manuelles, le dispatcher `/etc/NetworkManager/dispatcher.d/99-wg-auto`
s'est redéclenché seul suite à un renouvellement DHCP sur le hotspot, remontant `wg0`
automatiquement. Comportement correct du script en soi, mais source de confusion pour
du débogage manuel pas-à-pas.

**Bonne pratique retenue** : désactiver temporairement le dispatcher pendant une session
de diagnostic manuel :
```bash
sudo chmod -x /etc/NetworkManager/dispatcher.d/99-wg-auto
# ... tests manuels ...
sudo chmod +x /etc/NetworkManager/dispatcher.d/99-wg-auto
```

## 6. Conclusion (état initial du diagnostic)

- **IPv4** : le hotspot bloque le handshake (CGNAT/DPI) → confirmé, non résolu
  (contournable en IPv6, voir §2).
- **IPv6** : handshake + keepalive OK, stables dans le temps, mais **aucune donnée
  applicative** ne traverse (ni ICMP ni TCP), même après attente et à taille de
  paquet minimale.
- **Cause envisagée à ce stade** : filtrage `pf` sur PC4 (OpenBSD) au niveau du
  forwarding vers `10.10.0.0/24`, ou DPI/NAT plus fin de l'opérateur mobile bloquant
  spécifiquement le trafic de données soutenu au-delà du handshake.
- **Non résolu à distance à ce stade** : PC4 n'est joignable que via ce tunnel, donc
  logs `pf` inaccessibles depuis le hotspot.

> ✅ **Cause réelle trouvée et corrigée depuis** — voir §9 « Résolution confirmée ».
> Ce n'était ni `pf`, ni un DPI mobile : `AllowedIPs` était vide pour le peer PC1 sur PC4.

## 7. Vue globale — automatisation maison / déplacement

Indépendamment de ce blocage réseau ponctuel, l'automatisation de `wg_auto.sh`
elle-même fonctionne correctement dans les deux contextes (maison et déplacement),
déclenchée soit par le dispatcher réseau, soit par `zeta_tmux.sh` au lancement du
cluster.

![Schéma automatisation wg_auto.sh](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/docs/images/schema_automatisation.png)

**Point de vigilance** : un handshake réussi ne garantit pas que le tunnel transporte
des données — c'est une limite réseau externe, pas un défaut du script.

## 8. Étape suivante à l'époque

Vérifier les logs et règles `pf` sur PC4 en LAN maison (comparer avec §7 du wiki
réseau). Endpoint `wg0.conf` restauré en IPv4 (`zeta-secure.duckdns.org:51820`)
après le test.

## 9. Résolution confirmée (05/07/2026)

### 🎯 Cause racine — `AllowedIPs` vide pour le peer PC1 sur PC4

En LAN maison, `doas pfctl -sr` sur PC4 n'a montré **aucune règle bloquante** — le
trafic sur `wg0` (ping et TCP) est bien autorisé par `pf`. Le vrai coupable :
`doas wg show wg0` a révélé deux peers :

```
peer: 6euaNc/uLQc/PYL2/CAWYR391gE7vRSF+CH3ueO+8yc=
  allowed ips: 10.10.0.2/32, 10.10.0.3/32   ← doublon, 10.10.0.2/32 ne devrait pas être ici

peer: vRmxPmusiEIM2RegkvhKXpSTbLFAXFvQDYLl4KoFqmk=   ← PC1
  allowed ips: (none)                       ← rien n'est autorisé pour PC1 !
```

Un `/32` WireGuard ne peut appartenir qu'à un seul peer dans la table de routage du
noyau. `/etc/hostname.wg0` contenait une ligne `wgaip 10.10.0.2/32` en trop sous le
bloc `wgpeer 6euaNc/...`, ce qui volait l'IP `10.10.0.2/32` au peer PC1 — pourtant
bien déclarée pour lui via la ligne `!wg set ... allowed-ips 10.10.0.2/32` plus haut
dans le même fichier.

**Pourquoi le handshake/keepalive fonctionnaient quand même :** ces paquets de
contrôle n'ont pas de charge IP interne, donc ils ne sont pas soumis au filtrage
`AllowedIPs` — seul le trafic de données réel (ping, SSH...) est concerné, d'où le
symptôme trompeur « tunnel qui a l'air OK mais rien ne passe ».

### Correctif appliqué (live + persistant, sans coupure du tunnel de l'autre peer)

```bash
# Live — via wg set (remplace la liste allowed-ips de chaque peer)
doas wg set wg0 peer 6euaNc/uLQc/PYL2/CAWYR391gE7vRSF+CH3ueO+8yc= allowed-ips 10.10.0.3/32
doas wg set wg0 peer vRmxPmusiEIM2RegkvhKXpSTbLFAXFvQDYLl4KoFqmk= allowed-ips 10.10.0.2/32

# Persistant — retire la ligne wgaip en trop dans /etc/hostname.wg0
doas sed -i '/^wgaip 10.10.0.2\/32$/d' /etc/hostname.wg0
```

### ✅ Retest hotspot mobile — confirmation

Retest depuis le même hotspot mobile (`Port_Armel`), endpoint IPv6 :

| Test | Résultat |
|---|---|
| Handshake WireGuard (IPv6) | OK — 6 secondes, 604 B received |
| `ping 10.10.0.1` (PC4, gateway VPN) | ✅ 0% perte, RTT 42-52 ms |
| SSH TCP port 22 → `10.10.0.1` | ✅ succeeded |
| `ping 192.168.1.52` (PC2, via tunnel) | ✅ 0% perte, RTT 40-55 ms |
| `ping 192.168.1.22` (PC3, via tunnel) | ✅ 0% perte, RTT 36-55 ms |

Le tunnel transporte désormais les données réelles, et l'accès à l'ensemble du
cluster LAN (PC2/PC3) fonctionne en déplacement via l'endpoint IPv6. Endpoint
`wg0.conf` sur PC1 remis en IPv4/hostname après le test. Le blocage du handshake
en IPv4 par ce forfait mobile reste, lui, non résolu (contournement : endpoint IPv6
à chaque déplacement avec ce forfait précis).

## Voir aussi

- [[JOURNAL]] — historique daté, append-only
- [[STACK]] — outils, roadmap, matériel, formation
- [[Guide-Linux-Commandes]] — §18, commandes réseau

---
*Diagnostic-WireGuard-Hotspot.md · wiki racine · branche master · hprzeta · MAJ 2026-07-05 · 152 lignes*
