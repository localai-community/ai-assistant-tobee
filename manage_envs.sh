#!/bin/bash

# AI Assistant Environment Management Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}AI Assistant Environment Management${NC}"
echo "======================================"

case "$1" in
    "backend")
        echo -e "${YELLOW}Activating Backend Environment${NC}"
        cd backend
        source venv/bin/activate
        echo -e "${GREEN}✅ Backend environment activated${NC}"
        echo -e "${BLUE}Available commands:${NC}"
        echo "  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
        echo "  python -m pytest ../tests/ -v"
        echo "  python -c 'import app; print(\"✅ Backend imports OK\")'"
        ;;
    "frontend")
        echo -e "${YELLOW}Activating Frontend Environment${NC}"
        cd frontend
        source venv/bin/activate
        echo -e "${GREEN}✅ Frontend environment activated${NC}"
        echo -e "${BLUE}Available commands:${NC}"
        echo "  streamlit run app.py --server.port 8501 --server.address 0.0.0.0"
        echo "  python -c 'import streamlit; print(\"✅ Frontend imports OK\")'"
        ;;
    "setup")
        echo -e "${YELLOW}Setting up both environments${NC}"
        
        # Backend setup
        echo -e "${BLUE}Setting up Backend...${NC}"
        cd backend
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Backend environment ready${NC}"
        
        # Frontend setup
        echo -e "${BLUE}Setting up Frontend...${NC}"
        cd ../frontend
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Frontend environment ready${NC}"
        
        cd ..
        echo -e "${GREEN}✅ Both environments are ready!${NC}"
        ;;
    "test")
        echo -e "${YELLOW}Testing both environments${NC}"
        
        # Test backend
        echo -e "${BLUE}Testing Backend...${NC}"
        cd backend
        source venv/bin/activate
        python -c "import app; print('✅ Backend imports OK')"
        
        # Test frontend
        echo -e "${BLUE}Testing Frontend...${NC}"
        cd ../frontend
        source venv/bin/activate
        python -c "import streamlit; print('✅ Frontend imports OK')"
        
        cd ..
        echo -e "${GREEN}✅ Both environments tested successfully!${NC}"
        ;;
    *)
        echo -e "${YELLOW}Usage:${NC}"
        echo "  $0 backend   - Activate backend environment"
        echo "  $0 frontend  - Activate frontend environment"
        echo "  $0 setup     - Set up both environments"
        echo "  $0 test      - Test both environments"
        echo ""
        echo -e "${BLUE}Examples:${NC}"
        echo "  source manage_envs.sh backend"
        echo "  source manage_envs.sh frontend"
        echo "  ./manage_envs.sh setup"
        echo "  ./manage_envs.sh test"
        ;;
esac
