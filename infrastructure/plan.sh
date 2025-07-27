#!/bin/bash

set -e

# Load environment variables from .env file
source ./load-env.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Planning deployment of ${PROJECT_NAME} to AWS Lambda...${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if OpenTofu is installed
if ! command -v tofu &> /dev/null; then
    echo -e "${RED}OpenTofu is not installed. Please install it first.${NC}"
    exit 1
fi

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${YELLOW}AWS Account ID: ${AWS_ACCOUNT_ID}${NC}"

# Initialize OpenTofu
echo -e "${YELLOW}Initializing OpenTofu...${NC}"
# Check if we're in the infrastructure directory or need to navigate to it
if [ -f "main.tf" ]; then
    echo -e "${GREEN}Already in infrastructure directory${NC}"
else
    if [ -d "infrastructure" ]; then
        cd infrastructure
    else
        echo -e "${RED}Could not find infrastructure directory. Please run from project root or infrastructure directory.${NC}"
        exit 1
    fi
fi
tofu init

# Plan the deployment
echo -e "${YELLOW}Planning OpenTofu deployment...${NC}"
echo -e "${BLUE}This will show what changes would be made without applying them.${NC}"
echo ""

tofu plan -var="aws_region=${AWS_REGION}" -var="aws_profile=${AWS_PROFILE}" -var="project_name=${PROJECT_NAME}" -var="environment=${ENVIRONMENT}" -var="log_level=${LOG_LEVEL}" -var="backend_timeout=${BACKEND_TIMEOUT}" -var="frontend_timeout=${FRONTEND_TIMEOUT}" -var="backend_memory_size=${BACKEND_MEMORY_SIZE}" -var="frontend_memory_size=${FRONTEND_MEMORY_SIZE}"

echo ""
echo -e "${GREEN}Plan completed. Run ./deploy.sh to apply these changes.${NC}" 