#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up environment configuration...${NC}"

# Check if .env file already exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file already exists.${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# Copy example file
if [ -f ".env.example" ]; then
    cp .env.example .env
    echo -e "${GREEN}Created .env file from .env.example${NC}"
else
    echo -e "${YELLOW}Warning: .env.example not found. Creating basic .env file...${NC}"
    cat > .env << 'EOF'
# AWS Configuration
AWS_REGION=eu-central-1
AWS_PROFILE=default

# Project Configuration
PROJECT_NAME=ai-assistant
ENVIRONMENT=dev

# Lambda Configuration
LOG_LEVEL=INFO
BACKEND_TIMEOUT=900
FRONTEND_TIMEOUT=30
BACKEND_MEMORY_SIZE=2048
FRONTEND_MEMORY_SIZE=512

# Network Configuration
VPC_CIDR=10.0.0.0/16
PRIVATE_SUBNET_CIDRS=["10.0.1.0/24", "10.0.2.0/24"]
PUBLIC_SUBNET_CIDRS=["10.0.10.0/24", "10.0.11.0/24"]
EOF
    echo -e "${GREEN}Created basic .env file${NC}"
fi

echo -e "${GREEN}Environment setup completed!${NC}"
echo -e "${YELLOW}Please edit the .env file to configure your deployment settings.${NC}"
echo -e "${YELLOW}You can now run: ./deploy.sh${NC}" 