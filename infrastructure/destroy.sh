#!/bin/bash

set -e

# Load environment variables from .env file
source ./load-env.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting destruction of ${PROJECT_NAME} infrastructure...${NC}"

# Check if OpenTofu is installed
if ! command -v tofu &> /dev/null; then
    echo -e "${RED}OpenTofu is not installed. Please install it first.${NC}"
    exit 1
fi

# Confirm destruction
read -p "Are you sure you want to destroy all infrastructure? This action cannot be undone. (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Destruction cancelled.${NC}"
    exit 1
fi

# Change to infrastructure directory
cd infrastructure

# Destroy the infrastructure
echo -e "${YELLOW}Destroying infrastructure with OpenTofu...${NC}"
tofu destroy -var="aws_region=${AWS_REGION}" -var="aws_profile=${AWS_PROFILE}" -var="project_name=${PROJECT_NAME}" -var="environment=${ENVIRONMENT}" -var="log_level=${LOG_LEVEL}" -var="backend_timeout=${BACKEND_TIMEOUT}" -var="frontend_timeout=${FRONTEND_TIMEOUT}" -var="backend_memory_size=${BACKEND_MEMORY_SIZE}" -var="frontend_memory_size=${FRONTEND_MEMORY_SIZE}" -auto-approve

echo -e "${GREEN}Infrastructure destruction completed successfully!${NC}" 