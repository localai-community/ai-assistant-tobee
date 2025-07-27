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

echo -e "${GREEN}Importing existing ECR repositories into OpenTofu state...${NC}"

# Check if OpenTofu is installed
if ! command -v tofu &> /dev/null; then
    echo -e "${RED}OpenTofu is not installed. Please install it first.${NC}"
    exit 1
fi

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

# Initialize OpenTofu if not already initialized
if [ ! -d ".terraform" ]; then
    echo -e "${YELLOW}Initializing OpenTofu...${NC}"
    tofu init
fi

# Function to check if repository exists
check_repository() {
    local repo_name="$1"
    local region="$2"
    
    if aws ecr describe-repositories --repository-names "$repo_name" --region "$region" &>/dev/null; then
        echo -e "${GREEN}✓ Repository $repo_name exists${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Repository $repo_name does not exist${NC}"
        return 1
    fi
}

# Function to import repository
import_repository() {
    local repo_name="$1"
    local region="$2"
    local resource_name="$3"
    
    echo -e "${YELLOW}Importing repository $repo_name...${NC}"
    
    # Get repository ARN
    local repo_arn=$(aws ecr describe-repositories --repository-names "$repo_name" --region "$region" --query 'repositories[0].repositoryArn' --output text)
    
    if [ "$repo_arn" != "None" ] && [ -n "$repo_arn" ]; then
        echo -e "${BLUE}Repository ARN: $repo_arn${NC}"
        
        # Import the repository
        tofu import "aws_ecr_repository.$resource_name" "$repo_arn"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Successfully imported $repo_name${NC}"
        else
            echo -e "${RED}✗ Failed to import $repo_name${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ Could not get ARN for repository $repo_name${NC}"
        return 1
    fi
}

# Check and import backend repository
BACKEND_REPO_NAME="${PROJECT_NAME}-backend"
echo -e "${YELLOW}Checking backend repository: $BACKEND_REPO_NAME${NC}"

if check_repository "$BACKEND_REPO_NAME" "$AWS_REGION"; then
    echo -e "${YELLOW}Do you want to import the backend repository? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        import_repository "$BACKEND_REPO_NAME" "$AWS_REGION" "backend"
    else
        echo -e "${YELLOW}Skipping backend repository import${NC}"
    fi
else
    echo -e "${YELLOW}Backend repository does not exist, will be created during deployment${NC}"
fi

echo ""

# Check and import frontend repository
FRONTEND_REPO_NAME="${PROJECT_NAME}-frontend"
echo -e "${YELLOW}Checking frontend repository: $FRONTEND_REPO_NAME${NC}"

if check_repository "$FRONTEND_REPO_NAME" "$AWS_REGION"; then
    echo -e "${YELLOW}Do you want to import the frontend repository? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        import_repository "$FRONTEND_REPO_NAME" "$AWS_REGION" "frontend"
    else
        echo -e "${YELLOW}Skipping frontend repository import${NC}"
    fi
else
    echo -e "${YELLOW}Frontend repository does not exist, will be created during deployment${NC}"
fi

echo ""
echo -e "${GREEN}Import process completed!${NC}"
echo -e "${BLUE}You can now run 'tofu plan' to see what other resources need to be created.${NC}" 