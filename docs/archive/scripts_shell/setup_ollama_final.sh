#!/bin/bash

# ============================================================================
# Script d'installation d'Ollama - Version ultra robuste pour le projet Zêta
# Version sans set -e - continue même en cas d'erreur
# AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
# DATE : 2026
# ============================================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Fonction qui ne s'arrête jamais même en cas d'erreur
run_safe() {
    "$@" 2>/dev/null || true
}

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Installation d'Ollama pour projet Zêta${NC}"
echo -e "${BLUE}========================================${NC}"

# Étape 1 : Nettoyage (ignore toutes les erreurs)
echo -e "\n${YELLOW}Étape 1: Nettoyage des anciennes installations...${NC}"
run_safe sudo systemctl stop ollama
run_safe sudo systemctl disable ollama
run_safe sudo pkill -9 ollama
run_safe sudo rm -f /usr/local/bin/ollama
run_safe rm -rf ~/.ollama
run_safe sudo rm -rf /mnt/data/models_ia/ollama
run_safe sudo rm -f /etc/systemd/system/ollama.service
run_safe sudo rm -rf /etc/systemd/system/ollama.service.d
run_safe sudo systemctl daemon-reload
echo -e "${GREEN}✓ Nettoyage terminé${NC}"

# Étape 2 : Création du dossier
echo -e "\n${YELLOW}Étape 2: Création du dossier...${NC}"
run_safe sudo mkdir -p /mnt/data/models_ia/ollama
run_safe sudo chown -R $USER:$USER /mnt/data/models_ia/ollama
echo -e "${GREEN}✓ Dossier créé : /mnt/data/models_ia/ollama${NC}"

# Étape 3 : Configuration
echo -e "\n${YELLOW}Étape 3: Configuration de l'environnement...${NC}"
run_safe sed -i '/OLLAMA_MODELS/d' ~/.bashrc
echo 'export OLLAMA_MODELS=/mnt/data/models_ia/ollama' >> ~/.bashrc
export OLLAMA_MODELS=/mnt/data/models_ia/ollama
echo -e "${GREEN}✓ Variable OLLAMA_MODELS définie${NC}"

# Étape 4 : Installation d'Ollama
echo -e "\n${YELLOW}Étape 4: Installation d'Ollama...${NC}"
if curl -fsSL https://ollama.com/install.sh | sh; then
    echo -e "${GREEN}✓ Ollama installé${NC}"
else
    echo -e "${RED}✗ Erreur lors de l'installation d'Ollama${NC}"
    exit 1
fi

# Étape 5 : Service systemd
echo -e "\n${YELLOW}Étape 5: Configuration du service...${NC}"
sudo tee /etc/systemd/system/ollama.service > /dev/null << 'EOF'
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
Type=simple
User=riemann
Group=riemann
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3
Environment="HOME=/home/riemann"
Environment="OLLAMA_MODELS=/mnt/data/models_ia/ollama"

[Install]
WantedBy=multi-user.target
EOF

run_safe sudo systemctl daemon-reload
run_safe sudo systemctl enable ollama
run_safe sudo systemctl start ollama
sleep 3
echo -e "${GREEN}✓ Service configuré${NC}"

# Étape 6 : Vérification
echo -e "\n${YELLOW}Étape 6: Vérification...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama répond correctement${NC}"
else
    echo -e "${RED}✗ Ollama ne répond pas, tentative de démarrage manuel...${NC}"
    run_safe ollama serve &
    sleep 3
fi

# Étape 7 : Alias
echo -e "\n${YELLOW}Étape 7: Création de l'alias...${NC}"
run_safe sed -i '/ollama-serve/d' ~/.bashrc
echo 'alias ollama-serve="OLLAMA_MODELS=/mnt/data/models_ia/ollama ollama serve"' >> ~/.bashrc
run_safe source ~/.bashrc
echo -e "${GREEN}✓ Alias ollama-serve créé${NC}"

# Étape 8 : Installation des modèles
echo -e "\n${YELLOW}Étape 8: Installation des modèles...${NC}"
echo -e "${YELLOW}Téléchargement de deepseek-coder:6.7b (peut prendre du temps)...${NC}"
ollama pull deepseek-coder:6.7b

echo -e "\n${YELLOW}Téléchargement de llama3.2:3b...${NC}"
ollama pull llama3.2:3b

# Étape 9 : Récapitulatif
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}RÉCAPITULATIF FINAL${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
ollama list
echo ""
echo -e "${GREEN}Espace disque :${NC}"
df -h /mnt/data | tail -1
echo ""
echo -e "${GREEN}✓ Installation terminée !${NC}"
echo ""
echo -e "${YELLOW}Commandes utiles :${NC}"
echo "  ollama run deepseek-coder:6.7b    # Lancer DeepSeek"
echo "  ollama run llama3.2:3b            # Lancer Llama"
echo "  ollama list                       # Voir les modèles"
echo "  sudo systemctl status ollama      # Statut du service"
