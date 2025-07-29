#!/bin/bash

# AI Assistant Git Workflow Helper

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}AI Assistant Git Workflow Helper${NC}"
echo "================================"

case "$1" in
    "status")
        echo -e "${YELLOW}Git Status:${NC}"
        git status --short
        ;;
    "stage")
        if [ -z "$2" ]; then
            echo -e "${YELLOW}Staging all changes:${NC}"
            git add .
            echo -e "${GREEN}✅ Staged all changes${NC}"
        else
            echo -e "${YELLOW}Staging specific files:${NC}"
            shift
            for file in "$@"; do
                if [ -f "$file" ]; then
                    git add "$file"
                    echo -e "${GREEN}✅ Staged: $file${NC}"
                else
                    echo -e "${RED}❌ File not found: $file${NC}"
                fi
            done
        fi
        ;;
    "interactive")
        echo -e "${YELLOW}Interactive staging:${NC}"
        git add -p
        ;;
    "commit")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}Error: Please provide commit type and message${NC}"
            echo "Usage: $0 commit <type> <message>"
            echo "Types: feat, fix, docs, style, refactor, test, chore"
            echo "Example: $0 commit feat 'add comprehensive evaluation tests'"
            exit 1
        fi
        commit_type="$2"
        shift 2
        commit_message="$*"
        
        # Validate commit type
        valid_types=("feat" "fix" "docs" "style" "refactor" "test" "chore")
        valid=false
        for type in "${valid_types[@]}"; do
            if [ "$commit_type" = "$type" ]; then
                valid=true
                break
            fi
        done
        
        if [ "$valid" = false ]; then
            echo -e "${RED}Error: Invalid commit type '$commit_type'${NC}"
            echo "Valid types: ${valid_types[*]}"
            exit 1
        fi
        
        echo -e "${YELLOW}Committing:${NC}"
        git commit -m "$commit_type: $commit_message"
        echo -e "${GREEN}✅ Committed successfully${NC}"
        ;;
    "push")
        echo -e "${YELLOW}Pushing changes:${NC}"
        git push origin main
        echo -e "${GREEN}✅ Pushed successfully${NC}"
        ;;
    "workflow")
        echo -e "${YELLOW}Complete workflow example:${NC}"
        echo ""
        echo "1. Check status:"
        echo "   $0 status"
        echo ""
        echo "2. Stage all changes:"
        echo "   $0 stage"
        echo ""
        echo "   Or stage specific files:"
        echo "   $0 stage backend/app/api/phase4_reasoning.py"
        echo "   $0 stage tests/backend/test_phase4_evaluation.py"
        echo ""
        echo "3. Or use interactive staging:"
        echo "   $0 interactive"
        echo ""
        echo "4. Commit with proper message:"
        echo "   $0 commit feat 'add comprehensive evaluation tests'"
        echo ""
        echo "5. Push immediately:"
        echo "   $0 push"
        echo ""
        echo "Or do it all in one go:"
        echo "   $0 stage && $0 commit feat 'your message' && $0 push"
        ;;
    "check")
        echo -e "${YELLOW}Checking for common issues:${NC}"
        
        # Check for unstaged changes
        if [ -n "$(git status --porcelain)" ]; then
            echo -e "${RED}❌ You have unstaged changes${NC}"
            git status --short
        else
            echo -e "${GREEN}✅ No unstaged changes${NC}"
        fi
        
        # Check last commit message format
        last_commit=$(git log -1 --pretty=format:"%s")
        if [[ $last_commit =~ ^(feat|fix|docs|style|refactor|test|chore): ]]; then
            echo -e "${GREEN}✅ Last commit follows format: $last_commit${NC}"
        else
            echo -e "${RED}❌ Last commit doesn't follow format: $last_commit${NC}"
            echo "Should be: type: description"
        fi
        
        # Check if up to date with remote
        git fetch origin
        local_commit=$(git rev-parse HEAD)
        remote_commit=$(git rev-parse origin/main)
        if [ "$local_commit" = "$remote_commit" ]; then
            echo -e "${GREEN}✅ Up to date with remote${NC}"
        else
            echo -e "${YELLOW}⚠️  Not up to date with remote${NC}"
            echo "Consider: git pull origin main"
        fi
        ;;
    *)
        echo -e "${YELLOW}Usage:${NC}"
        echo "  $0 status                    - Show git status"
        echo "  $0 stage [file1] [file2] ... - Stage all changes (default) or specific files"
        echo "  $0 interactive               - Interactive staging"
        echo "  $0 commit <type> <message>   - Commit with proper format"
        echo "  $0 push                      - Push to remote"
        echo "  $0 workflow                  - Show complete workflow example"
        echo "  $0 check                     - Check for common issues"
        echo ""
        echo -e "${BLUE}Commit Types:${NC}"
        echo "  feat     - New feature"
        echo "  fix      - Bug fix"
        echo "  docs     - Documentation"
        echo "  style    - Formatting"
        echo "  refactor - Code refactoring"
        echo "  test     - Adding tests"
        echo "  chore    - Maintenance"
        echo ""
        echo -e "${BLUE}Examples:${NC}"
        echo "  $0 stage"
        echo "  $0 stage backend/app/api/phase4_reasoning.py"
        echo "  $0 commit feat 'add comprehensive evaluation tests'"
        echo "  $0 workflow"
        ;;
esac
