#!/bin/bash

# LocalAI Community - GPU Setup Debug Script
# This script helps debug issues with the GPU setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo -e "${CYAN}🔍 $1${NC}"
}

print_header "LocalAI Community - GPU Setup Debug"
echo ""

# Check system information
print_header "System Information"
echo "OS: $OSTYPE"
echo "Architecture: $(uname -m)"
echo "Docker version: $(docker --version 2>/dev/null || echo 'Docker not installed')"
echo "Docker Compose version: $(docker-compose --version 2>/dev/null || echo 'Docker Compose not installed')"
echo ""

# Check if Ollama is installed and running
print_header "Ollama Status"
if command -v ollama &> /dev/null; then
    print_status "Ollama is installed: $(ollama --version)"
    if pgrep -x "ollama" > /dev/null; then
        print_status "Ollama is running"
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_status "Ollama API is responding"
            MODELS=$(curl -s http://localhost:11434/api/tags 2>/dev/null | jq -r '.models[].name' 2>/dev/null || echo "")
            if [ -n "$MODELS" ]; then
                print_status "Available models:"
                echo "$MODELS" | while read -r model; do
                    echo "   • $model"
                done
            else
                print_warning "No models found"
            fi
        else
            print_error "Ollama API is not responding"
        fi
    else
        print_warning "Ollama is not running"
    fi
else
    print_error "Ollama is not installed"
fi
echo ""

# Check Docker status
print_header "Docker Status"
if docker info &> /dev/null; then
    print_status "Docker is running"
    print_info "Docker containers:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    print_error "Docker is not running"
fi
echo ""

# Check if ports are in use
print_header "Port Status"
for port in 8000 8501 11434; do
    if lsof -i :$port > /dev/null 2>&1; then
        print_warning "Port $port is in use:"
        lsof -i :$port
    else
        print_status "Port $port is available"
    fi
done
echo ""

# Check Docker Compose files
print_header "Docker Compose Files"
if [ -f "docker/docker-compose.host-ollama.yml" ]; then
    print_status "host-ollama.yml exists"
    if docker-compose -f docker/docker-compose.host-ollama.yml config > /dev/null 2>&1; then
        print_status "host-ollama.yml is valid"
    else
        print_error "host-ollama.yml has configuration errors"
    fi
else
    print_error "host-ollama.yml not found"
fi

if [ -f "docker/docker-compose.yml" ]; then
    print_status "docker-compose.yml exists"
    if docker-compose -f docker/docker-compose.yml config > /dev/null 2>&1; then
        print_status "docker-compose.yml is valid"
    else
        print_error "docker-compose.yml has configuration errors"
    fi
else
    print_error "docker-compose.yml not found"
fi
echo ""

# Check if services are currently running
print_header "Current Service Status"
if docker ps | grep -q "localaicommunity"; then
    print_info "LocalAI Community services are running:"
    docker ps --filter "name=localaicommunity" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    print_info "Service logs (last 10 lines each):"
    for service in backend frontend; do
        if docker ps | grep -q "localaicommunity-$service"; then
            echo "--- $service logs ---"
            docker logs localaicommunity-$service-1 --tail=10 2>/dev/null || echo "No logs available"
            echo ""
        fi
    done
else
    print_info "No LocalAI Community services are currently running"
fi
echo ""

# Test individual components
print_header "Component Tests"

# Test Ollama connectivity
print_info "Testing Ollama connectivity..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_status "Ollama API is accessible"
else
    print_error "Ollama API is not accessible"
fi

# Test backend health (if running)
print_info "Testing backend health..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Backend health endpoint is accessible"
    BACKEND_HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo "unknown")
    print_info "Backend status: $BACKEND_HEALTH"
else
    print_error "Backend health endpoint is not accessible"
fi

# Test frontend health (if running)
print_info "Testing frontend health..."
if curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    print_status "Frontend health endpoint is accessible"
else
    print_error "Frontend health endpoint is not accessible"
fi
echo ""

# Recommendations
print_header "Recommendations"
echo "If the GPU setup is getting stuck, try these steps:"
echo ""
echo "1. Stop all services:"
echo "   docker-compose -f docker/docker-compose.host-ollama.yml down"
echo "   pkill ollama"
echo ""
echo "2. Check Docker resources:"
echo "   docker system df"
echo "   docker system prune -f"
echo ""
echo "3. Restart Docker Desktop (if on macOS/Windows)"
echo ""
echo "4. Try the no-GPU setup first:"
echo "   ./scripts/run-no-gpu.sh"
echo ""
echo "5. Check system resources:"
echo "   top"
echo "   df -h"
echo ""

print_header "Debug Complete" 