#!/bin/bash

# ============================================================================
# Script d'installation complet pour le projet Zêta
# Version sans set -e - continue même en cas d'erreur
# AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
# DATE : 2026
# ============================================================================

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions d'affichage
print_step() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${GREEN}ÉTAPE $1 : $2${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   Installation Projet ZÊTA                      ║"
echo "║                     par riemann                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================================
# ÉTAPE 1 : Création de l'environnement virtuel
# ============================================================================
print_step "1" "Création de l'environnement virtuel"

cd ~
mkdir -p projet_zeta
cd projet_zeta

if [ -d "zeta_env" ]; then
    print_info "L'environnement existe déjà, suppression..."
    rm -rf zeta_env
fi

python3 -m venv zeta_env
source zeta_env/bin/activate
print_success "Environnement virtuel créé et activé"

# ============================================================================
# ÉTAPE 2 : Création de l'arborescence complète du projet
# ============================================================================
print_step "2" "Création de l'arborescence du projet"

# Structure sur ~/projet_zeta
mkdir -p src/{calculs,ia,utils,tests,visualisation,monitoring} 2>/dev/null
mkdir -p scripts 2>/dev/null
mkdir -p notebooks 2>/dev/null
mkdir -p config 2>/dev/null
mkdir -p docs 2>/dev/null

# Fichiers __init__.py
touch src/__init__.py 2>/dev/null
touch src/calculs/__init__.py 2>/dev/null
touch src/ia/__init__.py 2>/dev/null
touch src/utils/__init__.py 2>/dev/null

print_success "Arborescence ~/projet_zeta créée"

# Structure sur /mnt/data
print_info "Création de la structure sur /mnt/data..."
sudo mkdir -p /mnt/data/datasets/zeros 2>/dev/null
sudo mkdir -p /mnt/data/datasets/calculs 2>/dev/null
sudo mkdir -p /mnt/data/datasets/references 2>/dev/null
sudo mkdir -p /mnt/data/models_ia 2>/dev/null
sudo mkdir -p /mnt/data/rapports/pdf 2>/dev/null
sudo mkdir -p /mnt/data/rapports/doc 2>/dev/null
sudo mkdir -p /mnt/data/rapports/markdown 2>/dev/null
sudo mkdir -p /mnt/data/logs/calculs 2>/dev/null
sudo mkdir -p /mnt/data/logs/ia 2>/dev/null
sudo mkdir -p /mnt/data/logs/monitoring 2>/dev/null
sudo mkdir -p /mnt/data/monitoring/cpu 2>/dev/null
sudo mkdir -p /mnt/data/monitoring/gpu 2>/dev/null
sudo mkdir -p /mnt/data/monitoring/ram 2>/dev/null
sudo mkdir -p /mnt/data/monitoring/graphs 2>/dev/null
sudo mkdir -p /mnt/data/exports/csv 2>/dev/null
sudo mkdir -p /mnt/data/exports/json 2>/dev/null
sudo mkdir -p /mnt/data/exports/figures 2>/dev/null

sudo chown -R $USER:$USER /mnt/data 2>/dev/null

print_success "Arborescence /mnt/data créée"

# ============================================================================
# ÉTAPE 3 : Installation du système de base
# ============================================================================
print_step "3" "Installation du système de base"

sudo apt update 2>/dev/null
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential 2>/dev/null
sudo apt install -y curl wget git 2>/dev/null
sudo apt install -y libopenblas-dev liblapack-dev 2>/dev/null
sudo apt install -y pari-gp 2>/dev/null
sudo apt install -y htop nvtop lm-sensors 2>/dev/null

print_success "Système de base installé"

# ============================================================================
# ÉTAPE 4 : Bibliothèques scientifiques optimisées
# ============================================================================
print_step "4" "Installation des bibliothèques scientifiques"

pip install --upgrade pip 2>/dev/null
pip install numpy scipy matplotlib numba sympy mpmath 2>/dev/null

print_success "Bibliothèques scientifiques installées"

# ============================================================================
# ÉTAPE 5 : Gestion des données et logs
# ============================================================================
print_step "5" "Installation des outils de gestion de données"

pip install pandas pyarrow loguru 2>/dev/null

print_success "Outils de données installés"

# ============================================================================
# ÉTAPE 6 : Monitoring et débogage
# ============================================================================
print_step "6" "Installation des outils de monitoring"

pip install tqdm memory_profiler line_profiler 2>/dev/null

print_success "Outils de monitoring installés"

# ============================================================================
# ÉTAPE 7 : IA et Machine Learning
# ============================================================================
print_step "7" "Installation des outils IA (hors Ollama)"

pip install transformers sentence-transformers 2>/dev/null

# PyTorch avec détection GPU
if command -v nvidia-smi &> /dev/null; then
    print_info "GPU NVIDIA détecté, installation de PyTorch avec CUDA"
    pip install torch 2>/dev/null
else
    print_info "GPU non détecté, installation de PyTorch CPU"
    pip install torch --index-url https://download.pytorch.org/whl/cpu 2>/dev/null
fi

print_success "Outils IA installés"

# ============================================================================
# ÉTAPE 8 : Visualisation avancée
# ============================================================================
print_step "8" "Installation des outils de visualisation"

pip install seaborn bokeh 2>/dev/null

print_success "Outils de visualisation installés"

# ============================================================================
# ÉTAPE 9 : Calcul parallèle distribué
# ============================================================================
print_step "9" "Installation des outils de calcul parallèle"

pip install dask ray 2>/dev/null

print_success "Outils parallèles installés"

# ============================================================================
# ÉTAPE 10 : Vérification de preuves formelles (Lean 4)
# ============================================================================
print_step "10" "Installation de Lean 4 pour les preuves formelles"

if ! command -v lean &> /dev/null; then
    curl -sSfL https://github.com/leanprover/elan/releases/download/v3.0.0/elan-x86_64-unknown-linux-gnu.tar.gz | tar xz 2>/dev/null
    ./elan-init -y --default-toolchain stable 2>/dev/null
    source ~/.profile 2>/dev/null
    print_success "Lean 4 installé"
else
    print_info "Lean 4 déjà installé"
fi

# ============================================================================
# ÉTAPE 11 : Installer des IDE (Spyder, Jupiter & JupyterLab, Vscode)
# ============================================================================
print_step "11" "Installation des IDE  (Spyder, Jupiter & JupyterLab, Vscode) "

pip install spyder jupyter jupyterlab  2>/dev/null
sudo apt update
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
rm -f packages.microsoft.gpg
sudo apt update
sudo apt install code



# ============================================================================
# ÉTAPE 12 : Vérification finale et alias
# ============================================================================
print_step "12" "Configuration finale"

# Ajouter un alias pour activer l'environnement
grep -q "alias zeta=" ~/.bashrc || echo 'alias zeta="cd ~/projet_zeta && source zeta_env/bin/activate"' >> ~/.bashrc

# Vérifier les installations principales
echo -e "\n${GREEN}=== VÉRIFICATION DES INSTALLATIONS ===${NC}"

# Python et pip
echo -n "Python : "
python3 --version 2>/dev/null || echo "non installé"

echo -n "Pip : "
pip --version 2>/dev/null || echo "non installé"

# Bibliothèques principales
python3 -c "import numpy; print(f'NumPy : {numpy.__version__}')" 2>/dev/null || print_error "NumPy non installé"
python3 -c "import pandas; print(f'Pandas : {pandas.__version__}')" 2>/dev/null || print_error "Pandas non installé"
python3 -c "import torch; print(f'PyTorch : {torch.__version__}')" 2>/dev/null || print_error "PyTorch non installé"

# Ollama
if command -v ollama &> /dev/null; then
    echo -n "Ollama : "
    ollama --version 2>&1 | head -1
else
    print_info "Ollama non installé (déjà fait précédemment)"
fi



# Affichage final
echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                INSTALLATION TERMINÉE AVEC SUCCÈS !              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${YELLOW}📁 Structure du projet :${NC}"
echo "   ~/projet_zeta/          # Code source"
echo "   /mnt/data/              # Données et modèles"

echo -e "\n${YELLOW}🚀 Pour activer l'environnement :${NC}"
echo "   zeta                    # Alias"
echo "   # ou"
echo "   cd ~/projet_zeta && source zeta_env/bin/activate"

echo -e "\n${YELLOW}📦 Modèles Ollama disponibles :${NC}"
ollama list 2>/dev/null || echo "   Aucun modèle installé (faites ollama run ...)"

echo -e "\n${YELLOW}🎯 Pour lancer tmux :${NC}"
echo "   tmux attach -t zeta"

echo -e "\n${GREEN}Bonne continuation avec le projet ZETA ! 🚀${NC}"
