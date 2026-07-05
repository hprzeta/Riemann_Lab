> **Fichier :** Prompts-Claude-Code.md · **Dossier :** wiki racine
> **Branche :** master · **Auteur :** hprzeta · **MAJ :** 2026-06-16

# 📚 Prompts Claude Code — Riemann_Lab

> Page index des prompts utilisés depuis le début du projet.
> Source complète (prompts + résultats + leçons) :
> [`scripts/ia_prompts/ia_prompts_riemann_lab_complet.md`](https://github.com/hprzeta/Riemann_Lab/blob/Riemann_Lab_IA/scripts/ia_prompts/ia_prompts_riemann_lab_complet.md)

---

## Sessions et prompts

| # | Date | Prompt | Résultat clé |
|---|---|---|---|
| S01 | 9 mai 2026 | Démarrage projet zêta | Contexte initial, pile Ubuntu |
| S02 | 17 mai 2026 | v2 → v3 (10 problèmes) | compute_zeros_v3.py · ×7.6 vs v2 |
| S03 | 19 mai 2026 | Handoff + Second Cerveau IA | Architecture RAG définie |
| S04 | 21 mai 2026 | Enrichissement Formules_zeta | 10 142 zéros · Phase 0 validée |
| S05 | 22 mai 2026 | Réparation liens MD | Footer avec nb lignes |
| S06 | 23 mai 2026 | KaTeX + audit Formules_zeta | Bugs `%` documentés · 563 lignes |
| S07 | 23 mai 2026 | SKILL.md + CLAUDE.md cascade | 4 CLAUDE.md + 2 skills |
| S08 | 24 mai 2026 | **Phase C Illinois C/libmpfr** | `illinois_mpfr.so` compilé |
| S09 | 24 mai 2026 | Connexion MCP GitHub | 26 tools connectés |
| S10 | 25 mai 2026 | Fix liens wiki 404 | Fichiers à la racine wiki |
| S11 | 30 mai 2026 | Point d'état + priorité | Prompt reprise session |
| S12 | 30 mai 2026 | Validation Phase C Voie B v5 | Illinois C pur 100% · biais <1e-13 |
| S13 | 31 mai 2026 | Versionner les skills | 4 skills dans `.claude/skills/` |
| S14 | 3 juin 2026 | Maintenance dépôts (4 prompts) | gitignore · inbox-ia · CLAUDE.md sync |
| **S15** | **3 juin 2026** | **Option B — Fix Illinois** | **18.65 z/s · T=10000 en 9.1 min · ×18 ✅** |
| S16 | 13 juin 2026 | Documentation complète v12 | 2 rapports créés · 9 pages wiki mises à jour · site mis à jour · 0 manquant |

---

## 10 leçons clés sur les prompts

1. **Structure obligatoire** : Tâche 1, 2, 3... — Claude suit l'ordre
2. **Critères chiffrés** : `< 1e-12`, `> 15 z/s`, `19/20`
3. **Une tâche = un commit**
4. **Mentionner la branche** dès la première ligne
5. **`/clear` entre prompts** — économise les tokens
6. **Taille idéale** : 20–50 lignes
7. **`git check-ignore -v .mcp.json`** avant tout push
8. **`cp` avant `mv`** — commit = filet de sécurité
9. **`/clear` dès que `uncached > 50k`** ou cache COLD
10. **Points d'arrêt** : `STOP ici. Montre les chiffres et attends mon OK`

---

## Voir aussi

- [[Bonnes-Pratiques-Claude-Code]] — règles tokens, modèles, permissions
- [[Guide-Git-GitHub]] — workflow git détaillé
- [[STACK]] — outils, roadmap, formation

---

---

## Session 2026-06-13 — Documentation complète v12

### Contexte
Run v12 terminé : ~138 080 zéros · 0 manquant · 8.8 min · ×16.9 vs v10 · Turing COMPLET ✅

### Résultat
15 tâches exécutées : 2 rapports d'analyse créés (`analyse_problemes_v9_v10.md`, `analyse_problemes_v10_v12.md`),
9 pages wiki mises à jour (Home, Etape-1, STACK, Bibliotheques, Formules_zeta, JOURNAL, Plancher-Hardware-Architecture, Prompts-Claude-Code),
site `docs/index.html` mis à jour (v12 en surbrillance dorée), Handoff réécrit.

---

---

## Session 14-15 juin 2026 — Cluster Zeta : bastion PC4 zeta-secure + tunnel WireGuard externe

### Contexte
Sessions de nuit (14/06 ~22h → 15/06 ~02h45). Objectif : finaliser les hostnames du cluster,
déployer PC4 comme bastion WireGuard sous OpenBSD, rendre le cluster accessible de l'extérieur
(téléphone en 4G). Renommage définitif des machines :
- PC2 → `zeta-calc-second` (Debian 6.1 amd64, Core2Duo E8400)
- PC3 → `zeta-backup` (Ubuntu 14.04 LTS — kernel 4.4.0-210 i686 32-bit, Pentium E2140)
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

---

*Prompts-Claude-Code.md · wiki racine · master · hprzeta · MAJ 2026-06-16 · ~145 lignes*
