#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}AWS SSO Login Setup${NC}"
echo "======================"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Function to configure SSO
configure_sso() {
    echo -e "${YELLOW}Configuring AWS SSO...${NC}"
    
    # Load environment variables from .env file
    if [ -f ".env" ]; then
        echo -e "${YELLOW}Loading SSO configuration from .env file...${NC}"
        source ./load-env.sh
    else
        echo -e "${RED}No .env file found. Please run setup-env.sh first.${NC}"
        exit 1
    fi
    
    # Check if SSO variables are set
    if [ -z "$SSO_START_URL" ] || [ -z "$SSO_REGION" ] || [ -z "$SSO_ACCOUNT_ID" ] || [ -z "$SSO_ROLE_NAME" ]; then
        echo -e "${RED}Missing SSO configuration in .env file.${NC}"
        echo -e "${YELLOW}Please add the following variables to your .env file:${NC}"
        echo "SSO_START_URL=https://your-sso-portal.awsapps.com/start"
        echo "SSO_REGION=eu-central-1"
        echo "SSO_ACCOUNT_ID=123456789012"
        echo "SSO_ROLE_NAME=YourRoleName"
        exit 1
    fi
    
    echo -e "${GREEN}Using SSO configuration:${NC}"
    echo "  Start URL: $SSO_START_URL"
    echo "  Region: $SSO_REGION"
    echo "  Account ID: $SSO_ACCOUNT_ID"
    echo "  Role Name: $SSO_ROLE_NAME"
    
    # Create AWS config entries manually
    AWS_CONFIG_FILE="$HOME/.aws/config"
    AWS_CREDENTIALS_FILE="$HOME/.aws/credentials"
    
    # Create .aws directory if it doesn't exist
    mkdir -p "$HOME/.aws"
    
    # Check if profile already exists
    if grep -q "\[profile ai-assistant-sso\]" "$AWS_CONFIG_FILE" 2>/dev/null; then
        echo -e "${YELLOW}Profile 'ai-assistant-sso' already exists, updating...${NC}"
        # Remove existing profile section (macOS compatible)
        awk '/\[profile ai-assistant-sso\]/{flag=1; next} /^\[/{flag=0} !flag' "$AWS_CONFIG_FILE" > "$AWS_CONFIG_FILE.tmp" && mv "$AWS_CONFIG_FILE.tmp" "$AWS_CONFIG_FILE"
    else
        echo -e "${GREEN}Creating new profile 'ai-assistant-sso'...${NC}"
    fi
    
    # Add SSO profile configuration with integrated session parameters
    cat >> "$AWS_CONFIG_FILE" << EOF

[profile ai-assistant-sso]
sso_start_url = $SSO_START_URL
sso_region = $SSO_REGION
sso_registration_scopes = sso:account:access
sso_account_id = $SSO_ACCOUNT_ID
sso_role_name = $SSO_ROLE_NAME
region = $SSO_REGION
output = json
cli_pager = cat
cli_auto_prompt = off
EOF
    
    echo -e "${GREEN}AWS SSO profile 'ai-assistant-sso' created successfully!${NC}"
}

# Function to login to SSO
login_sso() {
    echo -e "${YELLOW}Logging in to AWS SSO...${NC}"
    
    # Check if SSO profile exists
    if ! aws configure list-profiles | grep -q "ai-assistant-sso"; then
        echo -e "${RED}SSO profile 'ai-assistant-sso' not found.${NC}"
        echo -e "${YELLOW}Please run the setup first:${NC}"
        echo -e "${BLUE}./aws-sso-login.sh setup${NC}"
        exit 1
    fi
    
    # Login to SSO
    aws sso login --profile ai-assistant-sso
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully logged in to AWS SSO!${NC}"
        echo -e "${YELLOW}You can now use the profile 'ai-assistant-sso' for deployment.${NC}"
        echo -e "${BLUE}Update your .env file to use: AWS_PROFILE=ai-assistant-sso${NC}"
    else
        echo -e "${RED}Failed to login to AWS SSO.${NC}"
        exit 1
    fi
}

# Function to check SSO status
check_sso() {
    echo -e "${YELLOW}Checking AWS SSO status...${NC}"
    
    # Check if SSO profile exists
    if aws configure list-profiles | grep -q "ai-assistant-sso"; then
        echo -e "${GREEN}SSO profile 'ai-assistant-sso' found.${NC}"
        
        # Check if logged in
        if aws sts get-caller-identity --profile ai-assistant-sso &>/dev/null; then
            echo -e "${GREEN}✓ Currently logged in to AWS SSO${NC}"
            aws sts get-caller-identity --profile ai-assistant-sso
        else
            echo -e "${YELLOW}⚠ Not logged in to AWS SSO${NC}"
            echo -e "${BLUE}Run: ./aws-sso-login.sh login${NC}"
        fi
    else
        echo -e "${RED}SSO profile 'ai-assistant-sso' not found.${NC}"
        echo -e "${BLUE}Run: ./aws-sso-login.sh setup${NC}"
    fi
}

# Function to show AWS config
show_config() {
    echo -e "${YELLOW}Current AWS config for ai-assistant-sso profile:${NC}"
    if [ -f "$HOME/.aws/config" ]; then
        echo ""
        # Extract the profile section with integrated SSO parameters
        sed -n '/\[profile ai-assistant-sso\]/,/^$/p' "$HOME/.aws/config" 2>/dev/null || echo "Profile not found in config"
    else
        echo -e "${RED}AWS config file not found.${NC}"
    fi
}

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage:${NC}"
    echo "  $0 setup    - Configure AWS SSO profile"
    echo "  $0 login    - Login to AWS SSO"
    echo "  $0 check    - Check SSO status"
    echo "  $0 config   - Show AWS config"
    echo "  $0 help     - Show this help"
    echo ""
    echo -e "${YELLOW}After setup, update your .env file:${NC}"
    echo "  AWS_PROFILE=ai-assistant-sso"
    echo ""
}

# Main script logic
case "${1:-help}" in
    "setup")
        configure_sso
        ;;
    "login")
        login_sso
        ;;
    "check")
        check_sso
        ;;
    "config")
        show_config
        ;;
    "help"|*)
        show_usage
        ;;
esac 