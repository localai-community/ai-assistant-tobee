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

echo -e "${GREEN}Importing existing AWS resources into OpenTofu state...${NC}"

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

# Function to check if resource exists
check_resource() {
    local resource_type="$1"
    local resource_name="$2"
    local region="$3"
    
    case "$resource_type" in
        "ecr")
            if aws ecr describe-repositories --repository-names "$resource_name" --region "$region" &>/dev/null; then
                echo -e "${GREEN}✓ ECR Repository $resource_name exists${NC}"
                return 0
            else
                echo -e "${YELLOW}⚠ ECR Repository $resource_name does not exist${NC}"
                return 1
            fi
            ;;
        "lambda")
            if aws lambda get-function --function-name "$resource_name" --region "$region" &>/dev/null; then
                echo -e "${GREEN}✓ Lambda Function $resource_name exists${NC}"
                return 0
            else
                echo -e "${YELLOW}⚠ Lambda Function $resource_name does not exist${NC}"
                return 1
            fi
            ;;
        "apigateway")
            if aws apigateway get-rest-api --rest-api-id "$resource_name" --region "$region" &>/dev/null; then
                echo -e "${GREEN}✓ API Gateway $resource_name exists${NC}"
                return 0
            else
                echo -e "${YELLOW}⚠ API Gateway $resource_name does not exist${NC}"
                return 1
            fi
            ;;
        "iam-role")
            if aws iam get-role --role-name "$resource_name" &>/dev/null; then
                echo -e "${GREEN}✓ IAM Role $resource_name exists${NC}"
                return 0
            else
                echo -e "${YELLOW}⚠ IAM Role $resource_name does not exist${NC}"
                return 1
            fi
            ;;
        "security-group")
            if aws ec2 describe-security-groups --group-names "$resource_name" --region "$region" &>/dev/null; then
                echo -e "${GREEN}✓ Security Group $resource_name exists${NC}"
                return 0
            else
                echo -e "${YELLOW}⚠ Security Group $resource_name does not exist${NC}"
                return 1
            fi
            ;;
        *)
            echo -e "${RED}Unknown resource type: $resource_type${NC}"
            return 1
            ;;
    esac
}

# Function to import resource
import_resource() {
    local resource_type="$1"
    local resource_name="$2"
    local region="$3"
    local terraform_resource="$4"
    local resource_id="$5"
    
    echo -e "${YELLOW}Importing $resource_type: $resource_name...${NC}"
    
    if [ -n "$resource_id" ]; then
        echo -e "${BLUE}Resource ID: $resource_id${NC}"
        
        # Import the resource
        tofu import "$terraform_resource" "$resource_id"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Successfully imported $resource_name${NC}"
        else
            echo -e "${RED}✗ Failed to import $resource_name${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ Could not get ID for resource $resource_name${NC}"
        return 1
    fi
}

# Check and import ECR repositories
echo -e "${BLUE}=== ECR Repositories ===${NC}"

BACKEND_REPO_NAME="${PROJECT_NAME}-backend"
FRONTEND_REPO_NAME="${PROJECT_NAME}-frontend"

if check_resource "ecr" "$BACKEND_REPO_NAME" "$AWS_REGION"; then
    echo -e "${YELLOW}Do you want to import the backend ECR repository? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        repo_arn=$(aws ecr describe-repositories --repository-names "$BACKEND_REPO_NAME" --region "$AWS_REGION" --query 'repositories[0].repositoryArn' --output text)
        import_resource "ecr" "$BACKEND_REPO_NAME" "$AWS_REGION" "aws_ecr_repository.backend" "$repo_arn"
    fi
fi

if check_resource "ecr" "$FRONTEND_REPO_NAME" "$AWS_REGION"; then
    echo -e "${YELLOW}Do you want to import the frontend ECR repository? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        repo_arn=$(aws ecr describe-repositories --repository-names "$FRONTEND_REPO_NAME" --region "$AWS_REGION" --query 'repositories[0].repositoryArn' --output text)
        import_resource "ecr" "$FRONTEND_REPO_NAME" "$AWS_REGION" "aws_ecr_repository.frontend" "$repo_arn"
    fi
fi

echo ""

# Check and import Lambda functions
echo -e "${BLUE}=== Lambda Functions ===${NC}"

BACKEND_LAMBDA_NAME="${PROJECT_NAME}-backend-container"
FRONTEND_LAMBDA_NAME="${PROJECT_NAME}-frontend-container"

if check_resource "lambda" "$BACKEND_LAMBDA_NAME" "$AWS_REGION"; then
    echo -e "${YELLOW}Do you want to import the backend Lambda function? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        import_resource "lambda" "$BACKEND_LAMBDA_NAME" "$AWS_REGION" "aws_lambda_function.backend_container" "$BACKEND_LAMBDA_NAME"
    fi
fi

if check_resource "lambda" "$FRONTEND_LAMBDA_NAME" "$AWS_REGION"; then
    echo -e "${YELLOW}Do you want to import the frontend Lambda function? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        import_resource "lambda" "$FRONTEND_LAMBDA_NAME" "$AWS_REGION" "aws_lambda_function.frontend_container" "$FRONTEND_LAMBDA_NAME"
    fi
fi

echo ""

# Check and import IAM roles
echo -e "${BLUE}=== IAM Roles ===${NC}"

BACKEND_ROLE_NAME="${PROJECT_NAME}-backend-lambda-role"
FRONTEND_ROLE_NAME="${PROJECT_NAME}-frontend-lambda-role"

if check_resource "iam-role" "$BACKEND_ROLE_NAME"; then
    echo -e "${YELLOW}Do you want to import the backend IAM role? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        import_resource "iam-role" "$BACKEND_ROLE_NAME" "$AWS_REGION" "aws_iam_role.lambda_backend" "$BACKEND_ROLE_NAME"
    fi
fi

if check_resource "iam-role" "$FRONTEND_ROLE_NAME"; then
    echo -e "${YELLOW}Do you want to import the frontend IAM role? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        import_resource "iam-role" "$FRONTEND_ROLE_NAME" "$AWS_REGION" "aws_iam_role.lambda_frontend" "$FRONTEND_ROLE_NAME"
    fi
fi

echo ""
echo -e "${GREEN}Import process completed!${NC}"
echo -e "${BLUE}You can now run 'tofu plan' to see what other resources need to be created.${NC}"
echo -e "${YELLOW}Note: Some resources like API Gateway and Security Groups may need manual import due to complex configurations.${NC}" 