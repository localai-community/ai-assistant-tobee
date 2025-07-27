#!/bin/bash

# Load environment variables from .env file if it exists
ENV_FILE="${ENV_FILE:-.env}"
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from $ENV_FILE file..."
    # Load variables line by line, excluding comments and JSON arrays
    while IFS= read -r line; do
        # Skip comments and empty lines
        if [[ ! "$line" =~ ^[[:space:]]*# ]] && [[ -n "$line" ]]; then
            # Skip JSON array variables (they contain square brackets)
            if [[ ! "$line" =~ \[.*\] ]]; then
                export "$line"
            fi
        fi
    done < "$ENV_FILE"
else
    echo "No $ENV_FILE file found, using default values..."
fi

# Set default values if not provided
export AWS_REGION="${AWS_REGION:-us-east-1}"
export AWS_PROFILE="${AWS_PROFILE:-default}"
export PROJECT_NAME="${PROJECT_NAME:-ai-assistant}"
export ENVIRONMENT="${ENVIRONMENT:-dev}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export BACKEND_TIMEOUT="${BACKEND_TIMEOUT:-900}"
export FRONTEND_TIMEOUT="${FRONTEND_TIMEOUT:-30}"
export BACKEND_MEMORY_SIZE="${BACKEND_MEMORY_SIZE:-2048}"
export FRONTEND_MEMORY_SIZE="${FRONTEND_MEMORY_SIZE:-512}"
export VPC_CIDR="${VPC_CIDR:-10.0.0.0/16}"
# Note: JSON arrays are handled separately in OpenTofu configuration

# AWS SSO Configuration (optional)
export SSO_START_URL="${SSO_START_URL:-}"
export SSO_REGION="${SSO_REGION:-}"
export SSO_ACCOUNT_ID="${SSO_ACCOUNT_ID:-}"
export SSO_ROLE_NAME="${SSO_ROLE_NAME:-}"

echo "Environment configuration:"
echo "  AWS_REGION: $AWS_REGION"
echo "  AWS_PROFILE: $AWS_PROFILE"
echo "  PROJECT_NAME: $PROJECT_NAME"
echo "  ENVIRONMENT: $ENVIRONMENT"
echo "  LOG_LEVEL: $LOG_LEVEL"
echo "  BACKEND_TIMEOUT: $BACKEND_TIMEOUT"
echo "  FRONTEND_TIMEOUT: $FRONTEND_TIMEOUT"
echo "  BACKEND_MEMORY_SIZE: $BACKEND_MEMORY_SIZE"
echo "  FRONTEND_MEMORY_SIZE: $FRONTEND_MEMORY_SIZE"
echo "  SSO_START_URL: ${SSO_START_URL:-not set}"
echo "  SSO_REGION: ${SSO_REGION:-not set}"
echo "  SSO_ACCOUNT_ID: ${SSO_ACCOUNT_ID:-not set}"
echo "  SSO_ROLE_NAME: ${SSO_ROLE_NAME:-not set}" 