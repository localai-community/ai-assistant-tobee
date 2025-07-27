#!/bin/bash

set -e

# Load environment variables from .env file
source ./load-env.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting deployment of ${PROJECT_NAME} to AWS Lambda...${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install it first.${NC}"
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
tofu plan -var="aws_region=${AWS_REGION}" -var="aws_profile=${AWS_PROFILE}" -var="project_name=${PROJECT_NAME}" -var="environment=${ENVIRONMENT}" -var="log_level=${LOG_LEVEL}" -var="backend_timeout=${BACKEND_TIMEOUT}" -var="frontend_timeout=${FRONTEND_TIMEOUT}" -var="backend_memory_size=${BACKEND_MEMORY_SIZE}" -var="frontend_memory_size=${FRONTEND_MEMORY_SIZE}"

# Ask for user approval
echo -e "${YELLOW}Do you want to apply these changes? (y/N)${NC}"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled by user.${NC}"
    exit 0
fi

# Apply the infrastructure
echo -e "${YELLOW}Applying OpenTofu configuration...${NC}"
tofu apply -var="aws_region=${AWS_REGION}" -var="aws_profile=${AWS_PROFILE}" -var="project_name=${PROJECT_NAME}" -var="environment=${ENVIRONMENT}" -var="log_level=${LOG_LEVEL}" -var="backend_timeout=${BACKEND_TIMEOUT}" -var="frontend_timeout=${FRONTEND_TIMEOUT}" -var="backend_memory_size=${BACKEND_MEMORY_SIZE}" -var="frontend_memory_size=${FRONTEND_MEMORY_SIZE}"

# Get ECR repository URLs
BACKEND_ECR_URL=$(tofu output -raw backend_ecr_repository_url)
FRONTEND_ECR_URL=$(tofu output -raw frontend_ecr_repository_url)

echo -e "${YELLOW}Backend ECR URL: ${BACKEND_ECR_URL}${NC}"
echo -e "${YELLOW}Frontend ECR URL: ${FRONTEND_ECR_URL}${NC}"

# Login to ECR
echo -e "${YELLOW}Logging in to ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build and push backend image
echo -e "${YELLOW}Building backend Docker image...${NC}"
# Navigate to project root for Docker build
if [ -d "../backend" ] || [ -d "../frontend" ]; then
    cd ..
    DOCKERFILE_PATH="infrastructure/Dockerfile.backend"
else
    DOCKERFILE_PATH="Dockerfile.backend"
fi
docker build -f ${DOCKERFILE_PATH} -t ${BACKEND_ECR_URL}:latest .

echo -e "${YELLOW}Pushing backend image to ECR...${NC}"
docker push ${BACKEND_ECR_URL}:latest

# Build and push frontend image
echo -e "${YELLOW}Building frontend Docker image...${NC}"
if [ -d "../backend" ] || [ -d "../frontend" ]; then
    DOCKERFILE_PATH="infrastructure/Dockerfile.frontend"
else
    DOCKERFILE_PATH="Dockerfile.frontend"
fi
docker build -f ${DOCKERFILE_PATH} -t ${FRONTEND_ECR_URL}:latest .

echo -e "${YELLOW}Pushing frontend image to ECR...${NC}"
docker push ${FRONTEND_ECR_URL}:latest

# Update Lambda functions with new images
echo -e "${YELLOW}Updating Lambda functions with new container images...${NC}"
# Navigate back to infrastructure directory for OpenTofu
if [ ! -f "main.tf" ]; then
    if [ -d "infrastructure" ]; then
        cd infrastructure
    else
        echo -e "${RED}Could not find infrastructure directory. Please run from project root or infrastructure directory.${NC}"
        exit 1
    fi
fi

# Plan the update
echo -e "${YELLOW}Planning Lambda function updates...${NC}"
tofu plan -var="aws_region=${AWS_REGION}" -var="aws_profile=${AWS_PROFILE}" -var="project_name=${PROJECT_NAME}" -var="environment=${ENVIRONMENT}" -var="log_level=${LOG_LEVEL}" -var="backend_timeout=${BACKEND_TIMEOUT}" -var="frontend_timeout=${FRONTEND_TIMEOUT}" -var="backend_memory_size=${BACKEND_MEMORY_SIZE}" -var="frontend_memory_size=${FRONTEND_MEMORY_SIZE}"

# Ask for user approval for Lambda updates
echo -e "${YELLOW}Do you want to update the Lambda functions with new container images? (y/N)${NC}"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Lambda function update cancelled by user.${NC}"
    exit 0
fi

tofu apply -var="aws_region=${AWS_REGION}" -var="aws_profile=${AWS_PROFILE}" -var="project_name=${PROJECT_NAME}" -var="environment=${ENVIRONMENT}" -var="log_level=${LOG_LEVEL}" -var="backend_timeout=${BACKEND_TIMEOUT}" -var="frontend_timeout=${FRONTEND_TIMEOUT}" -var="backend_memory_size=${BACKEND_MEMORY_SIZE}" -var="frontend_memory_size=${FRONTEND_MEMORY_SIZE}"

# Get API Gateway URL
API_URL=$(tofu output -raw api_gateway_url)
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}API Gateway URL: ${API_URL}${NC}"
echo -e "${GREEN}Backend endpoint: ${API_URL}/backend${NC}"
echo -e "${GREEN}Frontend endpoint: ${API_URL}/frontend${NC}" 