## 5 Pilier1  **Résumé récupération projet Git & système Linux** 

Instructions avant réinstallation propre — hprzeta / Riemann_Lab / Recovery / Brain Vault 

## Auteur : hprzeta — Préparé le 26 mai 2026 

Objectif : rentrer à la maison, rester connecté si possible, exporter le dépôt, le wiki et l’ancien système Linux, puis réinstaller proprement Ubuntu en gardant une base complète d’analyse pour reprendre la conversion du projet. 

Règle absolue : avant de casser ou réinstaller le système, générer et sauvegarder hors du PC les deux archives : export dépôt/wiki et audit système. Sans ces archives, on perdra des éléments précieux de ta méthode de travail. 

## **1. Ce que nous avons décidé** 

- Repartir sur une installation propre, idéalement Ubuntu 24.04 LTS. 

- Conserver et analyser l’ancien projet Riemann_Lab et son Wiki GitHub. 

- Extraire les Markdown, docs, scripts, config, requirements, skills Claude, inventaires Git et fichiers utiles. 

- Auditer l’ancien Linux avant suppression : paquets, partitions, GPU, swap, bashrc, services, venvs, Ollama, dépôts locaux. 

- Migrer ensuite vers une architecture robuste : hprzeta-lab, Recovery Zeta, Brain Vault, RAG, sauvegardes et reprise catastrophe. 

- Utiliser des modèles locaux légers : qwen2.5-coder:1.5b, qwen2.5-coder:3b, llama3.2:3b. 

- Garder OpenHands seulement en usage ponctuel ; privilégier Aider + Ollama + scripts shell/Python sur PC léger. 

## **2. Fichiers/outils que je t’ai préparés** 

|**Fichier**|**Usage**|**Résultat attendu**|
|---|---|---|
|export_riemann_lab_context.sh|Clone ou met à jour le dépôt GitHub et le wiki, extrait<br>Markdown, docs, scripts, config, skills, inventaires.|riemann_lab_context_export_latest.tar.gz|
|riemann_lab_export_tools.zip|Pack contenant le script d’export dépôt/wiki et le prompt<br>de reprise.|À télécharger et dézipper chez toi.|
|audit_systeme_hprzeta_avant_reinstal<br>l.sh|Analyse l’ancien Linux avant réinstallation : matériel,<br>paquets, partitions, bashrc, services, Python, Git, projets<br>locaux.|hprzeta_system_audit_latest.tar.gz|
|hprzeta_system_audit_tools.zip|Pack contenant le script d’audit système et le prompt<br>d’analyse.|À télécharger et dézipper chez toi.|
|prompt_reprise_hprzeta.md|Prompt de rappel si la conversation se coupe.|À copier-coller pour reprendre.|
|prompt_analyse_systeme_hprzeta.md|Prompt pour analyser l’audit de l’ancien système.|Inclus dans archive audit.|



## **3. Ordre exact à faire avant réinstallation** 

À faire chez toi, avant de formater ou réinstaller. 

```
# 0. Créer un dossier de travail temporaire
mkdir -p ~/hprzeta-pre-reinstall
cd ~/hprzeta-pre-reinstall
```

```
# 1. Dézipper les outils déjà téléchargés
unzip ~/Téléchargements/riemann_lab_export_tools.zip -d ./repo_export_tools
unzip ~/Téléchargements/hprzeta_system_audit_tools.zip -d ./system_audit_tools
```

```
# 2. Exporter le dépôt GitHub + Wiki
cd ~/hprzeta-pre-reinstall/repo_export_tools
chmod +x export_riemann_lab_context.sh
```

```
./export_riemann_lab_context.sh
```

```
# 3. Auditer l’ancien système Linux
cd ~/hprzeta-pre-reinstall/system_audit_tools
chmod +x audit_systeme_hprzeta_avant_reinstall.sh
./audit_systeme_hprzeta_avant_reinstall.sh
```

```
# 4. Les deux archives à conserver et à me transmettre
ls -lh ~/hprzeta-import/riemann_lab_context_export_latest.tar.gz
ls -lh ~/hprzeta-system-audit/hprzeta_system_audit_latest.tar.gz
```

## **4. Ce que contient l’export dépôt/wiki** 

L’export dépôt/wiki récupère le dépôt principal https://github.com/hprzeta/Riemann_Lab et le wiki https://github.com/hprzeta/Riemann_Lab.wiki.git. Il extrait les fichiers Markdown, docs, scripts, config, requirements, .claude, src, notebooks, images, inventaires et informations Git utiles. 

```
Archive à envoyer :
~/hprzeta-import/riemann_lab_context_export_latest.tar.gz
```

```
Contenu typique :
- repo_markdown/
- repo_selected/
- wiki/
```

- `git_info/` 

- `inventories/` 

Résumé récupération Git & système Linux — hprzeta — 26/05/2026 

Page 1 

```
- manifests/export_manifest.md
```

- `manifests/prompt_reprise_hprzeta.md` 

- `checksums/SHA256SUMS.txt` 

## **5. Ce que contient l’audit système Linux** 

L’audit système sert à reproduire ce qui était utile dans ton ancienne méthode de travail, mais sans recopier aveuglément un système potentiellement désorganisé. 

```
Archive à envoyer :
```

```
~/hprzeta-system-audit/hprzeta_system_audit_latest.tar.gz
```

```
Contenu typique :
```

- `system/ : OS, hostname, locale, date` 

- `hardware/ : CPU, RAM, swap, disque, partitions, GPU, NVIDIA` 

- `packages/ : apt, paquets manuels, snap, flatpak, sources apt` 

- `python/ : versions Python, pip freeze, venvs détectés` 

- `git/ : dépôts locaux, remotes, commits, statuts` 

- `projects/ : inventaire Markdown, requirements, scripts, snapshots légers` 

- `configs/ : bashrc/profile/aliases/env nettoyés` 

- `services/ : systemd filtré zeta, ollama, docker, syncthing, restic` 

- `manifests/ : prompt d’analyse et manifest - security_notes/ : consignes sécurité` 

## **6. Vérification sécurité avant de m’envoyer les archives** 

Les scripts nettoient déjà beaucoup de secrets, mais il faut vérifier avant partage. 

```
# Vérifier la liste des fichiers de l’archive système
```

```
tar -tzf ~/hprzeta-system-audit/hprzeta_system_audit_latest.tar.gz | less
```

```
# Décompresser dans /tmp et chercher des secrets éventuels
mkdir -p /tmp/hprzeta_audit_check
```

```
tar -xzf ~/hprzeta-system-audit/hprzeta_system_audit_latest.tar.gz -C /tmp/hprzeta_audit_check
```

```
grep -RniE 'token|secret|password|api_key|private key' /tmp/hprzeta_audit_check || true
```

```
# Faire pareil pour l’archive dépôt/wiki si besoin
mkdir -p /tmp/riemann_export_check
tar -xzf ~/hprzeta-import/riemann_lab_context_export_latest.tar.gz -C /tmp/riemann_export_check
grep -RniE 'token|secret|password|api_key|private key' /tmp/riemann_export_check || true
```

Ne jamais partager : clés privées SSH, tokens GitHub, fichiers .env réels, mots de passe, clés API. 

## **7. Sauvegarde hors PC avant formatage** 

Avant de réinstaller, copier les deux archives sur au moins un support externe. 

- `# Exemple avec une clé USB montée dans /media/$USER/USB` 

```
cp ~/hprzeta-import/riemann_lab_context_export_latest.tar.gz /media/$USER/USB/
```

```
cp ~/hprzeta-system-audit/hprzeta_system_audit_latest.tar.gz /media/$USER/USB/
```

- `# Copier aussi les checksums si présents` 

```
cp ~/hprzeta-import/*.sha256 /media/$USER/USB/ 2>/dev/null || true
cp ~/hprzeta-system-audit/*.sha256 /media/$USER/USB/ 2>/dev/null || true
```

- `# Vérifier` 

```
ls -lh /media/$USER/USB/*hprzeta* /media/$USER/USB/*riemann* 2>/dev/null || true
```

Idéalement : clé USB + cloud privé/dépôt distant + disque externe. Ne réinstalle pas avant d’avoir validé que les archives sont lisibles. 

## **8. Installation Linux recommandée** 

Version recommandée : Ubuntu 24.04 LTS. Objectif : stabilité, compatibilité scientifique, support NVIDIA, Python, Git, Ollama, Sage/PARI/FLINT, Docker éventuel et outils de sauvegarde. 

Si possible, choisir une installation minimale puis ajouter les paquets nécessaires proprement avec un bootstrap hprzeta. 

## **9. Partitionnement conseillé pour disque 1 To** 

|**Partition**|**Taille**|**Format**|**Usage**|
|---|---|---|---|
|EFI|1 Go|FAT32|/boot/efi|
|/|80 à 120 Go|ext4|Ubuntu + paquets|
|/home|250 à 350 Go|ext4|profil utilisateur + projets courants|
|/data|reste du disque|ext4|modèles IA, résultats, datasets, backups locaux|
|/swapfile|16 Go|fichier swap|stabilité mémoire|



Alternative simple : EFI 1 Go + une grande partition / + swapfile 16 Go. Mais pour hprzeta, séparer /data est préférable. 

## **10. Swap recommandé** 

```
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

```
echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-hprzeta.conf
sudo sysctl --system
```

Résumé récupération Git & système Linux — hprzeta — 26/05/2026 

Page 2 

```
free -h
swapon --show
```

## **11. GPU NVIDIA GTX 960/960M** 

Après installation Ubuntu, installer le driver recommandé par Ubuntu. Ne pas chercher à forcer une pile CUDA trop lourde au départ. 

```
sudo apt update
sudo ubuntu-drivers devices
sudo ubuntu-drivers autoinstall
sudo reboot
```

```
# Après reboot
nvidia-smi
lsmod | grep -Ei 'nvidia|nouveau' || true
```

Avec 4 Go VRAM, éviter les modèles IA lourds. Utiliser qwen2.5-coder:1.5b, qwen2.5-coder:3b et llama3.2:3b. 

## **12. Paquets système de base après réinstallation** 

```
sudo apt update
sudo apt install -y   git curl wget build-essential cmake pkg-config   python3 python3-pip python3-venv
python3-dev   htop btop nvtop tmux tree unzip zip   pari-gp libgmp-dev libmpfr-dev libmpc-dev libflint-dev
ffmpeg pandoc texlive-latex-base   sqlite3 jq ripgrep fd-find   restic syncthing
```

## **13. Arborescence cible hprzeta-lab** 

```
~/hprzeta-lab/
  01_env/              # scripts setup, notes installation, audit ancien système
  02_models/           # notes modèles IA, pointeurs Ollama
  03_rag/              # sources et index RAG
  04_projects/         # dépôt Riemann_Lab cloné ici
  05_data_reference/   # petites références versionnables
  06_results/          # résultats expérimentaux
  07_reports/          # rapports PDF/Markdown/JSON
  08_backups/          # backups locaux
  09_tmp/              # temporaire nettoyable
  10_docker/           # Docker/OpenHands optionnel
  11_recovery/         # checkpoints, crash reports, error_memory
  12_brain_vault/      # Obsidian/Markdown knowledge brain
  13_heartbeat/        # statut machine et monitoring
```

## **14. Bashrc et alias à reconstruire proprement** 

Ne pas recopier tout l’ancien .bashrc. On va l’analyser avec l’audit puis reconstruire proprement. 

```
# hprzeta aliases
alias zlab='cd ~/hprzeta-lab'
alias zrepo='cd ~/hprzeta-lab/04_projects/Riemann_Lab'
alias zdata='cd /data'
alias zrec='cd ~/hprzeta-lab/11_recovery'
alias zbrain='cd ~/hprzeta-lab/12_brain_vault'
alias zstatus='free -h && swapon --show && df -h'
```

```
# Ollama models
export OLLAMA_MODELS=/data/models_ia/ollama
```

## **15. Ollama après réinstallation** 

```
curl -fsSL https://ollama.com/install.sh | sh
```

```
sudo mkdir -p /data/models_ia/ollama
sudo chown -R $USER:$USER /data/models_ia/ollama
echo 'export OLLAMA_MODELS=/data/models_ia/ollama' >> ~/.bashrc
source ~/.bashrc
ollama pull qwen2.5-coder:1.5b
ollama pull qwen2.5-coder:3b
ollama pull llama3.2:3b
ollama list
```

## **16. Git après réinstallation** 

```
git config --global user.name "hprzeta"
git config --global user.email "ton-email-github"
git config --global init.defaultBranch main
git config --global pull.rebase false
```

```
# Cloner le projet
mkdir -p ~/hprzeta-lab/04_projects
cd ~/hprzeta-lab/04_projects
git clone https://github.com/hprzeta/Riemann_Lab.git
```

```
git clone https://github.com/hprzeta/Riemann_Lab.wiki.git Riemann_Lab.wiki || true
```

Si tu utilises SSH GitHub, régénérer ou restaurer une clé SSH proprement. Ne jamais partager la clé privée. 

## **17. Python projet** 

```
cd ~/hprzeta-lab/04_projects/Riemann_Lab
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip wheel setuptools
```

- `# Installer seulement après analyse des requirements réels` 

- `# Exemple minimal plus tard :` 

- `# pip install numpy scipy mpmath sympy pandas matplotlib pytest ruff mypy reportlab pypdf` 

Résumé récupération Git & système Linux — hprzeta — 26/05/2026 

Page 3 

## **18. Ce que tu m’enverras après les exports** 

Quand la connexion est stable, envoie-moi les deux fichiers suivants : 

```
~/hprzeta-import/riemann_lab_context_export_latest.tar.gz
```

```
~/hprzeta-system-audit/hprzeta_system_audit_latest.tar.gz
```

Avec ces deux archives, je préparerai : plan de reconfiguration, partitionnement final, bootstrap Ubuntu 24.04, migration Riemann_Lab, reconstruction /data, configuration Ollama, Brain Vault, Recovery Zeta, README_RESTORE.md et checklist complète. 

## **19. Prompt de rappel si la conversation se coupe** 

```
Nous reprenons le projet hprzeta/Riemann_Lab.
```

```
J’ai préparé deux archives avant réinstallation :
```

`1. riemann_lab_context_export_latest.tar.gz : dépôt GitHub + wiki + markdown + docs + scripts + skills.` 

`2. hprzeta_system_audit_latest.tar.gz : audit de l’ancien Linux avant réinstallation.` 

```
Contexte : PC ASUS Ubuntu 24.04 LTS cible, Intel i7, 8 Go RAM, 16 Go swap, disque 1 To, NVIDIA GTX 960/960M 4 Go
 VRAM.
```

```
Objectif : repartir proprement avec hprzeta-lab, Recovery Zeta, Brain Vault, RAG, sauvegardes, reprise
catastrophe et modèles IA légers.
```

```
Documents déjà produits :
```

- `solution_experimental_zeta.pdf` 

- `solution_experimental_zeta_pc_asus.pdf` 

- `recovery_zeta.pdf` 

- `cerveau_autonome_zeta_23_points.pdf` 

```
Travail demandé : analyser les archives, cartographier l’existant, proposer migration douce, générer bootstrap
Ubuntu 24.04, README_RESTORE.md, RESTORE_CHECKLIST.md, architecture Obsidian Brain Vault, intégration Recovery
Zeta et plan RAG initial.
```

```
Ne jamais prétendre prouver l’hypothèse de Riemann ; distinguer expérimentation, preuve formelle, conjecture et
documentation.
```

## **20. Checklist très courte avant formatage** 

- Lancer export_riemann_lab_context.sh. 

- Lancer audit_systeme_hprzeta_avant_reinstall.sh. 

- Vérifier que les deux archives .tar.gz existent. 

- Copier les deux archives sur clé USB/disque externe/cloud. 

- Vérifier rapidement qu’il n’y a pas de secrets dans les archives. 

- Noter le partitionnement actuel si besoin. 

- Noter si nvidia-smi fonctionne actuellement. 

- Seulement après cela : réinstaller Ubuntu proprement. 

Résumé récupération Git & système Linux — hprzeta — 26/05/2026 

Page 4 

