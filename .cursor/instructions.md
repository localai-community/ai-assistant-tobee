# AI Assistant Project Instructions

## Project Overview
This is a multi-phase AI reasoning system with:
- Phase 1: Core infrastructure
- Phase 2: Basic reasoning engines (mathematical, logical, causal)
- Phase 3: Advanced reasoning strategies (CoT, ToT, prompt engineering)
- Phase 4: Multi-agent system with local-first + A2A fallback

## Key Directories
- `backend/` - FastAPI backend with reasoning engines
- `frontend/` - Streamlit frontend
- `tests/` - Comprehensive test suite
- `docs/` - Project documentation
- `infrastructure/` - Terraform deployment

## Virtual Environment Setup
Each component has its own virtual environment:

### Backend Environment
```bash
cd backend
source venv/bin/activate  # or ./activate_venv.sh
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Environment
```bash
cd frontend
source venv/bin/activate  # or ./activate_venv.sh
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## Git Workflow
Follow these rules for all Git operations:

### Commit Message Format
```
type: brief description

- feat: new feature
- fix: bug fix
- docs: documentation changes
- style: formatting, missing semicolons, etc.
- refactor: code refactoring
- test: adding or updating tests
- chore: maintenance tasks
```

### Git Commands
```bash
# Good - Add all changes
git add .

# Good - Add specific files
git add backend/app/api/phase4_reasoning.py
git add frontend/app.py

# Good - Interactive staging
git add -p

# Good - Add all changes in specific directory
git add backend/app/

# Commit with proper message
git commit -m "feat: add Phase 4 multi-agent reasoning system"

# Push immediately
git push origin main
```

### Development Workflow
```bash
# 1. Create feature branch
git checkout -b feature/phase4-evaluation

# 2. Make changes and test
./manage_envs.sh test

# 3. Stage all changes
git add .

# 4. Commit with descriptive message
git commit -m "feat: implement comprehensive Phase 4 evaluation tests"

# 5. Push immediately
git push origin feature/phase4-evaluation
```

## Development Guidelines
1. **Testing**: Always create tests for new features
2. **Documentation**: Update docs when adding features
3. **Error Handling**: Provide meaningful error messages
4. **Performance**: Consider scalability and efficiency
5. **Environment Management**: Always use the correct venv for each component
6. **Git Hygiene**: Use `git add .` for staging all changes (as preferred)
7. **Cursor Files**: Both `.cursorrules` and `.cursor/instructions.md` are tracked in git for team consistency

## Common Commands

### Backend Development
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
python -m pytest ../tests/ -v
```

### Frontend Development
```bash
cd frontend
source venv/bin/activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Testing
```bash
# Backend tests
cd backend
source venv/bin/activate
python -m pytest ../tests/ -v

# Frontend tests
cd frontend
source venv/bin/activate
python -m pytest tests/ -v
```

### Git Operations
```bash
# Check status
git status

# See what files are changed
git diff

# Stage specific files
git add backend/app/api/phase4_reasoning.py

# Interactive staging
git add -p

# Commit with proper message
git commit -m "feat: add comprehensive evaluation tests"

# Push immediately
git push origin main
```

## Phase 4 Multi-Agent System
- Uses 7 local agents: mathematical, logical, causal, cot, tot, prompt_engineering, general_reasoning
- Local-first approach with A2A fallback
- Agent selection based on task type
- Confidence scoring and result synthesis

## Environment-Specific Notes
- Backend: FastAPI with SQLAlchemy, Alembic, and reasoning engines
- Frontend: Streamlit with chat interface and file upload
- Each has separate requirements.txt and venv
- VS Code settings are configured per directory
- Git workflow enforces clean, atomic commits
