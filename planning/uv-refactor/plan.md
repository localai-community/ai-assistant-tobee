# Plan: Complete UV Migration for Backend

## Context

PR #21 introduced `uv` as the package manager, adding `pyproject.toml`, `uv.lock`, and `.venv/`. However, several artifacts still reference the old `pip`/`venv` workflow — shell scripts, Dockerfile, docs, and redundant requirements files. This plan completes the migration so `uv` is the single, consistent tool for dependency management.

## Steps

### Step 1: Delete old requirements files
Remove these 4 files (source of truth is now `pyproject.toml`):
- `backend/requirements.txt`
- `backend/requirements-simple.txt`
- `backend/requirements-advanced.txt`
- `backend/requirements-updated.txt`

### Step 2: Update `backend/start_server.sh`
Replace the `venv/` + `pip install` logic with `uv sync` + `uv run`. Keep the echo messages for UX.

### Step 3: Update `backend/activate_venv.sh`
Rewrite to use `.venv/` (uv-managed) instead of `venv/`. Replace `pip` references with `uv`. Check for `pyproject.toml` instead of `requirements.txt` as the directory marker.

### Step 4: Update `backend/Dockerfile`
- Base image: `python:3.13-slim` (match local dev)
- Install `uv` via `COPY --from=ghcr.io/astral-sh/uv:latest`
- Use `uv sync --frozen --no-dev` instead of `pip install`
- Copy only needed files (not `COPY . .`)
- Add non-root user
- Keep existing healthcheck

### Step 5: Create `backend/.dockerignore`
Exclude `.venv/`, `venv/`, `__pycache__/`, `*.db`, `storage/`, `.git/`, `.vscode/`, test/utility scripts, and old requirements files.

### Step 6: Update `backend/README.md`
- Prerequisites: mention `uv` instead of `pip`
- Installation: `uv sync` instead of `pip install -r requirements.txt`
- Running: `uv run uvicorn ...`
- Project structure: remove `requirements.txt` line
- Testing: replace `python -m pytest` with `uv run pytest`

### Step 7: Update `backend/MIGRATIONS.md`
- Replace `source venv/bin/activate` → `source .venv/bin/activate`
- Replace bare `alembic` commands → `uv run alembic`
- Replace `python migrate_db.py` → `uv run python migrate_db.py`

### Step 8: Remove old `backend/venv/` directory
Delete the old pip-managed virtualenv. Only `.venv/` (uv-managed) should remain.

## Files Modified
- `backend/start_server.sh` (edit)
- `backend/activate_venv.sh` (edit)
- `backend/Dockerfile` (edit)
- `backend/.dockerignore` (create)
- `backend/README.md` (edit)
- `backend/MIGRATIONS.md` (edit)

## Files Deleted
- `backend/requirements.txt`
- `backend/requirements-simple.txt`
- `backend/requirements-advanced.txt`
- `backend/requirements-updated.txt`
- `backend/venv/` (directory)

## Verification
1. `cd backend && uv sync` — should install all deps from lockfile
2. `uv run uvicorn app.main:app --reload` — server should start
3. `uv run alembic current` — should show migration state
4. `docker build -t localai-backend .` — Docker build should succeed (if Docker available)
