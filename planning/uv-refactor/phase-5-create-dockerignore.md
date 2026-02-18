# Phase 5: Create `.dockerignore`

## Current State

No `.dockerignore` exists. The current `COPY . .` in Dockerfile copies everything including `.venv/`, `venv/`, `*.db`, `storage/`, and utility scripts into the image.

## Target State

Create `backend/.dockerignore`:

```
# Virtual environments
.venv/
venv/

# Python cache
__pycache__/
*.pyc
*.pyo

# Database files
*.db
*.sqlite
*.sqlite3

# Storage (runtime data)
storage/

# Git
.git/
.gitignore

# IDE
.vscode/

# Documentation
*.md

# Test and utility scripts
tests/
test_*.py
cleanup_conversations.py
delete_user.py
migrate_db.py
invoke_lambda.py
Makefile

# Old requirements files (if any remain)
requirements*.txt

# Docker
Dockerfile
.dockerignore
docker-compose*.yml
```

## File Created
- `backend/.dockerignore`
