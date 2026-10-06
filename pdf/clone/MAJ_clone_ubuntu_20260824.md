# Mise à jour clone Ubuntu — Toshiba sdb
## Session du 24 août 2026 — riemann@zeta-lab

---

## 1. Contexte

Mise à jour incrémentale du clone Ubuntu bootable (Toshiba MQ04ABD200, `/dev/sdb`) depuis le système principal (`sda` — Seagate ST1000LM035).

Dernier clonage complet : **21 juin 2026**.  
Évolutions depuis : v15 Projet Zêta validé, nouveau noyau 7.0.0-30, paquets mis à jour, vault_rag monté, fichiers SAP importés.

---

## 2. Architecture disques

| Disque | Modèle | Taille | Rôle | Lettre |
|--------|--------|--------|------|--------|
| Interne | Seagate ST1000LM035 | 931,5G | Ubuntu principal (source) | `sda` |
| USB3 externe | Toshiba MQ04ABD200 | 1,8T | Clone Ubuntu bootable (cible) | `sdb` |

### Partitions sda (source)

| Partition | UUID | Point de montage |
|-----------|------|-----------------|
| `sda1` | `[UUID_DISQUE]` | `/` |
| `sda2` | `[UUID_DISQUE]` | `/boot/efi` |
| `sda3` | `[UUID_DISQUE]` | `/home` |
| `sda4` | `[UUID_DISQUE]` | `/mnt/data` |
| `sda5` | `[UUID_DISQUE]` | swap |

### Partitions sdb (clone)

| Partition | Label | UUID | Point de montage clone |
|-----------|-------|------|----------------------|
| `sdb1` | EFI | `[UUID_DISQUE]` | `/boot/efi` |
| `sdb2` | root-clone | `[UUID_DISQUE]` | `/` |
| `sdb3` | home-clone | `[UUID_DISQUE]` | `/home` |
| `sdb4` | data-clone | `[UUID_DISQUE]` | `/mnt/data` |
| `sdb5` | swap-clone | `[UUID_DISQUE]` | swap |

---

## 3. Étapes réalisées

### 3.1 Identification et contrôle

```bash
lsblk /dev/sd* -o NAME,MODEL,SIZE,LABEL,UUID,MOUNTPOINT
sudo smartctl -H /dev/sdb
```

**Résultat SMART :** `PASSED` (warning "Incomplete response" bénin — limitation bridge USB/SATA).

---

### 3.2 rsync incrémental — 3 partitions

Commande type utilisée (une par partition) :

```bash
sudo rsync -avh --progress --delete --one-file-system \
  --exclude='/proc/*' --exclude='/sys/*' --exclude='/dev/*' \
  --exclude='/run/*' --exclude='/tmp/*' --exclude='/lost+found' \
  --exclude='/media/*' --exclude='/mnt/*' \
  --log-file=/home/riemann/rsync_root_YYYYMMDD.log \
  <source>/ <destination>/
```

| Partition | Source | Destination | Taille totale | Transféré | Vitesse |
|-----------|--------|-------------|--------------|-----------|---------|
| root `/` | `/` | `/media/riemann/root-clone/` | 45,13G | 13,61G | 21,59 MB/s |
| home `/home` | `/home/` | `/media/riemann/home-clone/` | 132,55G | 16,50G | 9,00 MB/s |
| data `/mnt/data` | `/mnt/data/` | `/media/riemann/data-clone/` | 29,90G | 17,18G | 93,65 MB/s |

> **Warning rsync code 24 sur /home** : bénin — fichiers temporaires disparus pendant le transfert.

---

### 3.3 Correction fstab du clone

⚠️ **Problème rencontré** : le rsync a écrasé le fstab du clone avec celui de `sda` (pointant vers les UUID sda). Correction obligatoire après chaque mise à jour rsync.

**Méthode retenue** (tee a échoué silencieusement → utiliser cp depuis fichier tmp) :

```bash
cat > /tmp/fstab_clone << 'EOF'
# /etc/fstab — clone Ubuntu bootable (Toshiba sdb)
UUID=[UUID_DISQUE] / ext4 defaults,noatime 0 1
UUID=[UUID_DISQUE] /boot/efi vfat defaults,noatime 0 0
UUID=[UUID_DISQUE] /home ext4 defaults,noatime 0 2
UUID=[UUID_DISQUE] /mnt/data ext4 defaults,noatime 0 2
/mnt/data/swapfile none swap sw 0 0
UUID=[UUID_DISQUE] /mnt/vault_rag ext4 defaults,noatime,nofail 0 2
EOF

cat /tmp/fstab_clone   # vérifier avant de copier
sudo cp /tmp/fstab_clone /media/riemann/root-clone/etc/fstab
cat /media/riemann/root-clone/etc/fstab   # confirmer
```

> **Correction supplémentaire** : suppression de la double entrée `vault_rag` présente dans l'ancien fstab.

---

### 3.4 Chroot — GRUB + initramfs

```bash
# Monter EFI et systèmes virtuels
sudo mount /dev/sdb1 /media/riemann/root-clone/boot/efi
sudo mount --bind /dev  /media/riemann/root-clone/dev
sudo mount --bind /proc /media/riemann/root-clone/proc
sudo mount --bind /sys  /media/riemann/root-clone/sys
sudo mount --bind /run  /media/riemann/root-clone/run

# Entrer dans le chroot
sudo chroot /media/riemann/root-clone
```

**Dans le chroot :**

```bash
grub-install --target=x86_64-efi --efi-directory=/boot/efi \
  --bootloader-id=ubuntu --recheck
update-grub
update-initramfs -u -k all
```

**Résultats :**
- GRUB installé sans erreur (warning EFI variables bénin en chroot)
- `update-grub` a détecté : `vmlinuz-7.0.0-30-generic` ✅ et `vmlinuz-7.0.0-29-generic` ✅
- initramfs régénéré pour les 2 noyaux sans warning swap

**Vérification fallback EFI :**
```bash
ls /boot/efi/EFI/boot/
# → BOOTX64.EFI  fbx64.efi  mmx64.efi  ✅
```

---

### 3.5 Sortie chroot et démontage

```bash
exit

sudo umount /media/riemann/root-clone/boot/efi
sudo umount /media/riemann/root-clone/dev
sudo umount /media/riemann/root-clone/proc
sudo umount /media/riemann/root-clone/sys
sudo umount /media/riemann/root-clone/run
```

---

## 4. Tableau d'avancement final

| # | Étape | Statut |
|---|-------|--------|
| 1 | Identification sdb = Toshiba | ✅ |
| 2 | Contrôle SMART | ✅ PASSED |
| 3 | rsync `/` → sdb2 | ✅ 45,13G |
| 4 | rsync `/home` → sdb3 | ✅ 132,55G |
| 5 | rsync `/mnt/data` → sdb4 | ✅ 29,90G |
| 6 | fstab clone corrigé (UUID sdb) | ✅ |
| 7 | GRUB mis à jour (chroot) | ✅ noyau 7.0.0-30 |
| 8 | initramfs régénéré (chroot) | ✅ 2 noyaux |
| 9 | Fallback EFI vérifié | ✅ BOOTX64.EFI présent |
| 10 | Démontage propre sdb | ✅ |

---

## 5. Problèmes rencontrés et corrections

| # | Problème | Cause | Correction |
|---|----------|-------|------------|
| 1 | fstab clone écrasé par rsync | rsync copie `/etc/fstab` de sda | Réécriture manuelle via `/tmp/fstab_clone` + `cp` |
| 2 | `tee` n'a pas écrasé le fstab | Comportement inattendu du `tee` sur partition montée | Utiliser `cp` depuis fichier tmp — méthode retenue pour la suite |
| 3 | Double entrée vault_rag dans fstab | Entrée dupliquée lors d'une session précédente | Nettoyé dans le nouveau fstab |

---

## 6. Règles à retenir pour les prochaines MAJ

1. **Toujours re-corriger le fstab après rsync** — le rsync écrase `/etc/fstab` du clone avec celui de sda.
2. **Utiliser `cp` depuis `/tmp/`** pour écrire le fstab clone, pas `tee` (comportement instable).
3. **UUID sdb stables** — pas de reformatage donc les UUID du clone ne changent pas entre sessions.
4. **`/dev/sdX` instable** — toujours vérifier avec `lsblk` en début de session avant toute opération.
5. **Fallback EFI** — vérifier `BOOTX64.EFI` présent après chaque `grub-install` (requis firmware ASUS).
6. **Warning "EFI variables cannot be set"** en chroot = bénin, non bloquant.
7. **Warning rsync code 24** = bénin (fichiers tmp disparus pendant transfert).

---

## 7. État du clone au 24/08/2026

| Élément | Version/État |
|---------|-------------|
| OS cloné | Ubuntu 24.04 LTS |
| Noyaux présents | 7.0.0-30-generic, 7.0.0-29-generic |
| GRUB | Installé, à jour |
| initramfs | Régénéré pour les 2 noyaux |
| fstab | Corrigé — UUID sdb |
| Fallback EFI | `BOOTX64.EFI` présent |
| vault_rag | Entrée `nofail` présente (montage optionnel) |
| Projet Zêta | v15 synchronisé (45G root + 132G home + 30G data) |

---

*Mise à jour : 24 août 2026 — 7 lignes de règles, 10 étapes validées*  
*Auteur : riemann@zeta-lab — Projet Zêta / Riemann Lab*
