#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing AI Assistant deployment...${NC}"

# Get API Gateway URL from OpenTofu output
cd infrastructure
API_URL=$(tofu output -raw api_gateway_url 2>/dev/null || echo "")

if [ -z "$API_URL" ]; then
    echo -e "${RED}Could not get API Gateway URL. Make sure deployment is complete.${NC}"
    exit 1
fi

echo -e "${YELLOW}API Gateway URL: ${API_URL}${NC}"

# Test backend health endpoint
echo -e "${YELLOW}Testing backend health endpoint...${NC}"
BACKEND_HEALTH_RESPONSE=$(curl -s -w "%{http_code}" -X POST "${API_URL}/backend/health" -H "Content-Type: application/json" -d '{}' || echo "000")

HTTP_CODE=${BACKEND_HEALTH_RESPONSE: -3}
RESPONSE_BODY=${BACKEND_HEALTH_RESPONSE%???}

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${RED}✗ Backend health check failed (HTTP ${HTTP_CODE})${NC}"
    echo -e "${YELLOW}Response: ${RESPONSE_BODY}${NC}"
fi

# Test frontend endpoint
echo -e "${YELLOW}Testing frontend endpoint...${NC}"
FRONTEND_RESPONSE=$(curl -s -w "%{http_code}" -X POST "${API_URL}/frontend" -H "Content-Type: application/json" -d '{"message": "test"}' || echo "000")

HTTP_CODE=${FRONTEND_RESPONSE: -3}
RESPONSE_BODY=${FRONTEND_RESPONSE%???}

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Frontend endpoint test passed${NC}"
else
    echo -e "${RED}✗ Frontend endpoint test failed (HTTP ${HTTP_CODE})${NC}"
    echo -e "${YELLOW}Response: ${RESPONSE_BODY}${NC}"
fi

# Test chat endpoint
echo -e "${YELLOW}Testing chat endpoint...${NC}"
CHAT_RESPONSE=$(curl -s -w "%{http_code}" -X POST "${API_URL}/backend/chat" -H "Content-Type: application/json" -d '{"message": "Hello, how are you?"}' || echo "000")

HTTP_CODE=${CHAT_RESPONSE: -3}
RESPONSE_BODY=${CHAT_RESPONSE%???}

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Chat endpoint test passed${NC}"
else
    echo -e "${RED}✗ Chat endpoint test failed (HTTP ${HTTP_CODE})${NC}"
    echo -e "${YELLOW}Response: ${RESPONSE_BODY}${NC}"
fi

echo -e "${GREEN}Deployment test completed!${NC}"
echo -e "${YELLOW}You can now access your AI Assistant at:${NC}"
echo -e "${GREEN}Backend: ${API_URL}/backend${NC}"
echo -e "${GREEN}Frontend: ${API_URL}/frontend${NC}" 