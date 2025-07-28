#!/bin/bash

set -e

# Parse command line arguments
AUTO_APPROVE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --auto-approve|-y)
            AUTO_APPROVE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --auto-approve, -y    Auto-approve all prompts (non-interactive)"
            echo "  --help, -h           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

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
if [ "$AUTO_APPROVE" = true ]; then
    echo -e "${YELLOW}Auto-approving infrastructure changes...${NC}"
else
    echo -e "${YELLOW}Do you want to apply these changes? (y/N)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Deployment cancelled by user.${NC}"
        exit 0
    fi
fi

# Apply the infrastructure
echo -e "${YELLOW}Applying OpenTofu configuration...${NC}"
tofu apply -var="aws_region=${AWS_REGION}" -var="aws_profile=${AWS_PROFILE}" -var="project_name=${PROJECT_NAME}" -var="environment=${ENVIRONMENT}" -var="log_level=${LOG_LEVEL}" -var="backend_timeout=${BACKEND_TIMEOUT}" -var="frontend_timeout=${FRONTEND_TIMEOUT}" -var="backend_memory_size=${BACKEND_MEMORY_SIZE}" -var="frontend_memory_size=${FRONTEND_MEMORY_SIZE}"

# Docker images will be built and pushed automatically by OpenTofu
echo -e "${YELLOW}Docker images will be built and pushed automatically during infrastructure deployment${NC}"
echo -e "${BLUE}Note: Docker builds are now handled by OpenTofu with proper dependency management${NC}"


# Get API Gateway URL
API_URL=$(tofu output -raw api_gateway_url 2>/dev/null || echo "Not available yet")
echo -e "${GREEN}Deployment completed successfully!${NC}"
if [ -n "$API_URL" ] && [ "$API_URL" != "Not available yet" ]; then
    echo -e "${GREEN}API Gateway URL: ${API_URL}${NC}"
    echo -e "${GREEN}Backend endpoint: ${API_URL}/backend${NC}"
    echo -e "${GREEN}Frontend endpoint: ${API_URL}/frontend${NC}"
else
    echo -e "${YELLOW}API Gateway URL not available yet. Run 'tofu output api_gateway_url' after deployment completes.${NC}"
fi 