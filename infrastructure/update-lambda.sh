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

echo -e "${GREEN}Updating Lambda functions with new Docker images...${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${YELLOW}AWS Account ID: ${AWS_ACCOUNT_ID}${NC}"

# ECR URLs
BACKEND_ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-backend"
FRONTEND_ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-frontend"

# Update backend Lambda function
echo -e "${YELLOW}Updating backend Lambda function...${NC}"
if ! aws lambda update-function-code --function-name ${PROJECT_NAME}-backend-container --image-uri ${BACKEND_ECR_URL}:latest --region ${AWS_REGION}; then
    echo -e "${RED}Failed to update backend Lambda function.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Backend Lambda function updated successfully${NC}"

# Update frontend Lambda function
echo -e "${YELLOW}Updating frontend Lambda function...${NC}"
if ! aws lambda update-function-code --function-name ${PROJECT_NAME}-frontend-container --image-uri ${FRONTEND_ECR_URL}:latest --region ${AWS_REGION}; then
    echo -e "${RED}Failed to update frontend Lambda function.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Frontend Lambda function updated successfully${NC}"

echo -e "${GREEN}Successfully updated all Lambda functions!${NC}"
echo -e "${BLUE}Backend ECR URL: ${BACKEND_ECR_URL}${NC}"
echo -e "${BLUE}Frontend ECR URL: ${FRONTEND_ECR_URL}${NC}"
echo ""
echo -e "${YELLOW}Lambda functions are being updated. Wait a few minutes for the changes to take effect.${NC}" 