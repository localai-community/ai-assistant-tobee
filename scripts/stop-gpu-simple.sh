#!/bin/bash

# LocalAI Community - Stop GPU Services Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "🛑 Stopping LocalAI Community GPU Services..."

# Stop backend
print_info "Stopping backend..."
pkill -f "uvicorn.*app.main:app" 2>/dev/null || true

# Stop frontend
print_info "Stopping frontend..."
pkill -f "streamlit.*app.py" 2>/dev/null || true

# Check Ollama status (don't stop it)
print_info "Checking Ollama status..."
if pgrep -x "ollama" > /dev/null; then
    print_info "Ollama is still running (user-managed)"
else
    print_info "Ollama is not running"
fi

# Clean up PID files
rm -f /tmp/ollama.pid /tmp/backend.pid /tmp/frontend.pid

print_success "All services stopped!"
echo ""
print_info "To start services again, run: ./start.sh gpu" 