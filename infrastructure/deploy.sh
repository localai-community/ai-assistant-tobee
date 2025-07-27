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

# Check for existing ECR repositories
echo -e "${YELLOW}Checking for existing ECR repositories...${NC}"
BACKEND_REPO_NAME="${PROJECT_NAME}-backend"
FRONTEND_REPO_NAME="${PROJECT_NAME}-frontend"

if aws ecr describe-repositories --repository-names "$BACKEND_REPO_NAME" --region "$AWS_REGION" &>/dev/null || aws ecr describe-repositories --repository-names "$FRONTEND_REPO_NAME" --region "$AWS_REGION" &>/dev/null; then
    if [ "$AUTO_APPROVE" = true ]; then
        echo -e "${YELLOW}Found existing ECR repositories. Auto-importing...${NC}"
        if ./import-ecr.sh --auto-approve; then
            echo -e "${GREEN}Successfully imported ECR repositories${NC}"
        else
            echo -e "${YELLOW}Import failed, continuing with deployment (repositories will be created if needed)${NC}"
        fi
    else
        echo -e "${YELLOW}Found existing ECR repositories. Do you want to import them into OpenTofu state? (y/N)${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Running import script...${NC}"
            if ./import-ecr.sh; then
                echo -e "${GREEN}Successfully imported ECR repositories${NC}"
            else
                echo -e "${YELLOW}Import failed, continuing with deployment (repositories will be created if needed)${NC}"
            fi
        fi
    fi
fi

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

# Get ECR repository URLs
echo -e "${YELLOW}Getting ECR repository URLs...${NC}"
BACKEND_ECR_URL=$(tofu output -raw backend_ecr_repository_url 2>/dev/null || echo "")
FRONTEND_ECR_URL=$(tofu output -raw frontend_ecr_repository_url 2>/dev/null || echo "")

# If ECR URLs are not available from OpenTofu, construct them manually
if [ -z "$BACKEND_ECR_URL" ]; then
    BACKEND_ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-backend"
    echo -e "${YELLOW}Constructed backend ECR URL: ${BACKEND_ECR_URL}${NC}"
else
    echo -e "${YELLOW}Backend ECR URL: ${BACKEND_ECR_URL}${NC}"
fi

if [ -z "$FRONTEND_ECR_URL" ]; then
    FRONTEND_ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-frontend"
    echo -e "${YELLOW}Constructed frontend ECR URL: ${FRONTEND_ECR_URL}${NC}"
else
    echo -e "${YELLOW}Frontend ECR URL: ${FRONTEND_ECR_URL}${NC}"
fi

# Login to ECR
echo -e "${YELLOW}Logging in to ECR...${NC}"
if ! aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com; then
    echo -e "${RED}Failed to login to ECR. Please check your AWS credentials.${NC}"
    exit 1
fi

# Build and push backend image
echo -e "${YELLOW}Building backend Docker image...${NC}"

# Check if backend image needs to be rebuilt
if check_image_needs_rebuild "$BACKEND_ECR_URL" "backend"; then
    if [ "$AUTO_APPROVE" = true ]; then
        echo -e "${YELLOW}Auto-rebuilding backend image...${NC}"
        REBUILD_BACKEND=true
    else
        echo -e "${YELLOW}Backend image exists. Do you want to rebuild it? (y/N)${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            REBUILD_BACKEND=true
        else
            REBUILD_BACKEND=false
        fi
    fi
else
    REBUILD_BACKEND=true
fi

if [ "$REBUILD_BACKEND" = true ]; then
    # Navigate to project root for Docker build
    if [ -d "../backend" ] || [ -d "../frontend" ]; then
        cd ..
        DOCKERFILE_PATH="infrastructure/Dockerfile.backend"
    else
        DOCKERFILE_PATH="Dockerfile.backend"
    fi

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
else
    echo -e "${YELLOW}Skipping backend image rebuild${NC}"
fi

echo -e "${YELLOW}Pushing backend image to ECR...${NC}"
if ! docker push ${BACKEND_ECR_URL}:latest; then
    echo -e "${RED}Failed to push backend image to ECR.${NC}"
    exit 1
fi

# Build and push frontend image
echo -e "${YELLOW}Building frontend Docker image...${NC}"

# Check if frontend image needs to be rebuilt
if check_image_needs_rebuild "$FRONTEND_ECR_URL" "frontend"; then
    if [ "$AUTO_APPROVE" = true ]; then
        echo -e "${YELLOW}Auto-rebuilding frontend image...${NC}"
        REBUILD_FRONTEND=true
    else
        echo -e "${YELLOW}Frontend image exists. Do you want to rebuild it? (y/N)${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            REBUILD_FRONTEND=true
        else
            REBUILD_FRONTEND=false
        fi
    fi
else
    REBUILD_FRONTEND=true
fi

if [ "$REBUILD_FRONTEND" = true ]; then
    if [ -d "../backend" ] || [ -d "../frontend" ]; then
        DOCKERFILE_PATH="infrastructure/Dockerfile.frontend"
    else
        DOCKERFILE_PATH="Dockerfile.frontend"
    fi

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
else
    echo -e "${YELLOW}Skipping frontend image rebuild${NC}"
fi

echo -e "${GREEN}Successfully built and pushed Docker images to ECR${NC}"

# Function to check if Docker image needs to be rebuilt
check_image_needs_rebuild() {
    local image_url="$1"
    local image_name="$2"
    
    echo -e "${YELLOW}Checking if $image_name image needs to be rebuilt...${NC}"
    
    # Check if image exists in ECR
    if aws ecr describe-images --repository-name "$(echo $image_url | cut -d'/' -f2)" --image-ids imageTag=latest --region "$AWS_REGION" &>/dev/null; then
        echo -e "${GREEN}✓ $image_name image exists in ECR${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ $image_name image not found in ECR, will be built${NC}"
        return 1
    fi
}

# Check if we need to update Lambda functions
echo -e "${YELLOW}Checking if Lambda functions need updates...${NC}"
if [ "$AUTO_APPROVE" = true ]; then
    echo -e "${YELLOW}Auto-updating Lambda functions with new container images...${NC}"
    UPDATE_LAMBDAS=true
else
    echo -e "${YELLOW}Do you want to update the Lambda functions with new container images? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        UPDATE_LAMBDAS=true
    else
        echo -e "${YELLOW}Skipping Lambda function updates${NC}"
        UPDATE_LAMBDAS=false
    fi
fi

if [ "$UPDATE_LAMBDAS" = true ]; then
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
    if [ "$AUTO_APPROVE" = true ]; then
        echo -e "${YELLOW}Auto-approving Lambda function updates...${NC}"
    else
        echo -e "${YELLOW}Do you want to apply the Lambda function updates? (y/N)${NC}"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Lambda function update cancelled by user.${NC}"
            exit 0
        fi
    fi

    tofu apply -var="aws_region=${AWS_REGION}" -var="aws_profile=${AWS_PROFILE}" -var="project_name=${PROJECT_NAME}" -var="environment=${ENVIRONMENT}" -var="log_level=${LOG_LEVEL}" -var="backend_timeout=${BACKEND_TIMEOUT}" -var="frontend_timeout=${FRONTEND_TIMEOUT}" -var="backend_memory_size=${BACKEND_MEMORY_SIZE}" -var="frontend_memory_size=${FRONTEND_MEMORY_SIZE}"
    
    echo -e "${GREEN}Lambda functions updated successfully!${NC}"
fi

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