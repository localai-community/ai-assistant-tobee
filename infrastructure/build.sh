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

echo -e "${GREEN}Building and pushing Docker images for ${PROJECT_NAME}...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${YELLOW}AWS Account ID: ${AWS_ACCOUNT_ID}${NC}"

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

# Login to ECR
echo -e "${YELLOW}Logging in to ECR...${NC}"
if ! aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com; then
    echo -e "${RED}Failed to login to ECR. Please check your AWS credentials.${NC}"
    exit 1
fi

# Build and push backend image
echo -e "${YELLOW}Building backend Docker image...${NC}"

# Navigate to project root for Docker build
if [ -d "../backend" ] || [ -d "../frontend" ]; then
    cd ..
    DOCKERFILE_PATH="infrastructure/Dockerfile.backend"
else
    DOCKERFILE_PATH="Dockerfile.backend"
fi

BACKEND_ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-backend"

if ! docker build -f ${DOCKERFILE_PATH} -t ${BACKEND_ECR_URL}:latest .; then
    echo -e "${RED}Failed to build backend Docker image.${NC}"
    exit 1
fi

echo -e "${YELLOW}Pushing backend image to ECR...${NC}"
if ! docker push ${BACKEND_ECR_URL}:latest; then
    echo -e "${RED}Failed to push backend image to ECR.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Backend image built and pushed successfully${NC}"

# Build and push frontend image
echo -e "${YELLOW}Building frontend Docker image...${NC}"

if [ -d "backend" ] || [ -d "frontend" ]; then
    DOCKERFILE_PATH="infrastructure/Dockerfile.frontend"
else
    DOCKERFILE_PATH="Dockerfile.frontend"
fi

FRONTEND_ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-frontend"

if ! docker build -f ${DOCKERFILE_PATH} -t ${FRONTEND_ECR_URL}:latest .; then
    echo -e "${RED}Failed to build frontend Docker image.${NC}"
    exit 1
fi

echo -e "${YELLOW}Pushing frontend image to ECR...${NC}"
if ! docker push ${FRONTEND_ECR_URL}:latest; then
    echo -e "${RED}Failed to push frontend image to ECR.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Frontend image built and pushed successfully${NC}"

echo -e "${GREEN}Successfully built and pushed all Docker images to ECR!${NC}"
echo -e "${BLUE}Backend ECR URL: ${BACKEND_ECR_URL}${NC}"
echo -e "${BLUE}Frontend ECR URL: ${FRONTEND_ECR_URL}${NC}"
echo ""
echo -e "${YELLOW}To update Lambda functions with new images, run:${NC}"
echo -e "${BLUE}aws lambda update-function-code --function-name ${PROJECT_NAME}-backend-container --image-uri ${BACKEND_ECR_URL}:latest --region ${AWS_REGION}${NC}"
echo -e "${BLUE}aws lambda update-function-code --function-name ${PROJECT_NAME}-frontend-container --image-uri ${FRONTEND_ECR_URL}:latest --region ${AWS_REGION}${NC}" 