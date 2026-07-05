# 🛠️ Rapport de Maintenance Système — 23 juin 2026

## Contexte

Maintenance préventive sur **PC1 (`riemann@zeta-lab`)** suite à l'apparition d'un écran
**Emergency Mode** au démarrage Ubuntu, accompagné d'un bruit de disque inhabituel.

## 1. Symptômes observés

| Symptôme | Description |
|----------|-------------|
| Emergency Mode au boot | Ubuntu bascule en mode urgence avant le login |
| Bruit disque | Son inhabituel pendant la phase de démarrage |
| Boot normal ensuite | Ctrl+D → login normal, système fonctionnel |

## 2. Cause racine identifiée

Entrée `/etc/fstab` **bloquante** pour le SSD Micron 1100 (`/mnt/vault_rag`) :
systemd cherche l'UUID du SSD, timeout, bascule en Emergency Mode.
Le bruit = HDD `sda` en retry pendant le timeout de montage.

## 3. Diagnostic disque système (`sda`)

- **Modèle** : Seagate BarraCuda ST1000LM035-1RK172 — 1 To — SATA
- **SMART overall** : ✅ PASSED
- **Reallocated/Pending/Uncorrectable** : ✅ 0 / 0 / 0
- **Power_On_Hours** : 3 547 h (~148 jours)
- **Température** : 37 °C
- **Self-test court** : ✅ Completed without error

## 4. Correction appliquée

Ajout de `nofail` dans `/etc/fstab` :

```
UUID=9476fad5-8512-4e0d-8cd4-50c9acae01c2  /mnt/vault_rag  ext4  defaults,noatime,nofail  0  2
```

`nofail` indique à systemd de ne pas bloquer le boot si ce point de montage est
indisponible ou lent à apparaître — l'éventuel échec du SSD au démarrage ne déclenchera
plus l'Emergency Mode (le montage sera simplement retenté/ignoré, sans interrompre la
séquence de boot).

## 5. Validation

Ligne confirmée présente dans `/etc/fstab` sur PC1 (vérifié par lecture directe du fichier,
23 juin 2026). Aucun test de reboot complet effectué depuis l'ajout de `nofail` — à
confirmer lors du prochain redémarrage de PC1.

