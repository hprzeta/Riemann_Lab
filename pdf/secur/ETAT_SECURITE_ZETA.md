# ÉTAT SÉCURITÉ ZETA — 21/11/2026

> Suite de `claude/ETAT_SECURITE_ZETA_20261114.md` et de `HANDOFF_SECURITE_20261115.md`. Aucune valeur sensible.

## Nouveau : O12 — accès distant au cluster coupé (ouvert, 🔴)

| Mesure (21/11, hprzeta à distance) | Résultat | État |
|---|---|---|
| `wg_auto.sh` | boucle « tunnel MORT » / « échec réparation » | 🔴 |
| PC1 : `apt` depuis le 14/11 | rien touché côté WireGuard / réseau | 🟢 |
| PC1 : IPv6 sortant sur le réseau distant | oui | 🟢 |
| PC1 : pair WireGuard | `bikedJC3…` (bonne clé de PC4) | 🟢 |
| PC1 : endpoint utilisé | IPv6, égal à l'AAAA publié | 🟢 |
| PC1 : handshake | jamais ; rx 0, tx 148 (une initiation sans réponse) | 🔴 |
| DuckDNS | A : 0, AAAA : 1 | 🟢 |
| Ping IPv6 vers l'AAAA | 100 % de perte, **non concluant** (pf de PC4 n'autorise pas l'écho ICMPv6, config de juin) | ⚪ |
| Téléphone `zeta-vpn` en 4G | Rx 0, puis éteint | 🔴 |
| Page DuckDNS (vue dans Chrome, 21/11) | champ IPv4 vide (voulu, O10) ; « mise à jour IPv6 : il y a 5 jours » (≈ 16/11) ; jeton généré il y a 6 jours (O8a) | ⚪ |

**Conclusion (probable).** PC1 et DuckDNS sont hors de cause, et le réseau distant aussi (même échec en 4G). La panne est **côté maison** :
1. adresse IPv6 de PC4 (ou préfixe de la box) changée depuis le 15/11 au soir → la règle du pare-feu IPv6 de la box ne vise plus PC4 ;
2. `wg0` absent sur PC4, ou PC4 arrêté ou bloqué ;
3. pare-feu IPv6 de la box remis à zéro.

Âge de « changed » lu le 21/11 : l'AAAA n'a pas bougé depuis ≈ 16/11. **Non tranché** : on ne sait pas (non vérifié) si DuckDNS date le dernier appel ou le dernier changement d'adresse, ni si `duck.sh` lit l'IPv6 de PC4 dynamiquement. Le contrôle de `/var/log/duckdns.log` sur place (heure de modification) départagera.

## À faire sur place (console PC4, puis box)

0. `ls -l /var/log/duckdns.log` : heure de modification récente (< 5 min) = PC4 et cron vivants.
1. PC4 allumé ? Console : `ifconfig wg0` (interface présente, 2 pairs), `doas wg show` (clé publique `bikedJC3…`).
2. `ifconfig re0 | grep inet6` : relever l'adresse globale non temporaire et la comparer **à l'écran** à l'AAAA de DuckDNS et à la cible de la règle WireGuard du pare-feu IPv6 de la box.
3. Si l'adresse diffère : corriger la règle de la box (une seule modification), puis tester avec le téléphone en 4G.
4. `doas pfctl -sr | grep 51820` : règle UDP toujours présente.
5. Chercher la cause du changement (redémarrage de PC4 ou de la box, durée de vie SLAAC) avant de refermer O12.

## Décisions

- **S5** (proposée) : à distance, aucune commande sur PC4 ni sur la box ; seuls les correctifs côté PC1 sont autorisés.
- **S6** (proposée) : mise à jour ou redémarrage de PC4 uniquement sur place, console disponible.
- **S7** (proposée) : ne pas redémarrer la box à distance, car le préfixe IPv6 délégué peut changer.

## Reste ouvert (inchangé)

O1, O2, O3, O4, O5, O7, O9 (IP fixe box, à relier à O12), S4 (wiki), dossier `Pass/`, archive du 14/11 : voir `HANDOFF_SECURITE_20261115.md`. O11 (protection de PC1) proposé le 15/11, non confirmé.

---
*claude/ETAT_SECURITE_ZETA_20261121.md · MAJ 2026-11-21 · 54 lignes*
