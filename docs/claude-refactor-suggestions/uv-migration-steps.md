# UV Migration Steps

The recent PR #21 introduced `uv` as the package manager, but the migration is **incomplete**. Here are the steps to fully adopt `uv`.

## Current State

**What's done:**
- `pyproject.toml` uses `[dependency-groups]` (uv syntax)
- `uv.lock` is present and tracked (1.2MB, full transitive dep tree)
- `.venv/` is managed by uv (Python 3.13)

**What's not done:**
- Shell scripts still reference old `venv/` and `pip install`
- Dockerfile still uses `pip`
- Documentation still references `pip` and `venv`
- Old `venv/` directory still exists alongside `.venv/`
- Four `requirements*.txt` files still exist

---

## Step 1: Clean Up Old Requirements Files

Remove redundant files — `pyproject.toml` is the single source of truth now.

```bash
cd backend
rm requirements.txt
rm requirements-simple.txt
rm requirements-advanced.txt
rm requirements-updated.txt
```

If you need "simple" vs "advanced" install profiles, use uv's dependency groups in `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.28.0",
]
rag = [
    "langchain>=0.3.0",
    "langchain-community>=0.3.0",
    "chromadb>=0.5.0",
    "sentence-transformers>=2.2.0",
]
ml = [
    "torch",
    "transformers",
    "accelerate",
    "scikit-learn",
    "spacy",
]
```

Then install selectively:
```bash
uv sync                    # core deps only
uv sync --group dev        # core + dev
uv sync --group rag        # core + RAG
uv sync --all-groups       # everything
```

---

## Step 2: Update Shell Scripts

### `start_server.sh`

Replace the current pip/venv logic:

```bash
#!/bin/bash
set -e

# Sync dependencies using uv
uv sync

# Start the server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### `activate_venv.sh`

```bash
#!/bin/bash
# Activate the uv-managed virtual environment
source .venv/bin/activate
```

---

## Step 3: Remove Old venv

```bash
rm -rf backend/venv/
```

Only `.venv/` (uv-managed) should remain. Ensure `.gitignore` includes:

```
.venv/
venv/
```

---

## Step 4: Update Dockerfile

```dockerfile
FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# System dependencies (for ML/RAG packages if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies using lockfile (frozen = exact lockfile versions)
RUN uv sync --frozen --no-dev

# Copy application code
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
COPY lambda_handler.py .

# Create storage directories
RUN mkdir -p storage/uploads storage/vector_db

# Non-root user
RUN useradd -m appuser
USER appuser

EXPOSE 8000

HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

Key changes:
- Uses `python:3.13-slim` (matches local dev)
- Installs `uv` from the official image
- Uses `uv sync --frozen` instead of `pip install`
- Copies only necessary files (not the entire directory)
- Adds non-root user
- Adds `--workers 2` for production

---

## Step 5: Add `.dockerignore`

Create `backend/.dockerignore`:

```
.venv/
venv/
__pycache__/
*.pyc
*.pyo
localai_community.db
storage/
*.egg-info/
.git/
.gitignore
.vscode/
*.md
tests/
requirements*.txt
Makefile
invoke_lambda.py
test_*.py
cleanup_conversations.py
delete_user.py
migrate_db.py
```

---

## Step 6: Update Documentation

### README.md

Replace all occurrences of:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

With:
```bash
uv sync
source .venv/bin/activate
# Or simply:
uv run uvicorn app.main:app --reload
```

### MIGRATIONS.md

Same replacements. Also update any migration commands:
```bash
# Old
alembic upgrade head

# New
uv run alembic upgrade head
```

---

## Step 7: CI/CD Integration (Future)

When CI is set up, use the official `setup-uv` action:

```yaml
name: Backend CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Install dependencies
        run: uv sync --frozen --group dev

      - name: Run linter
        run: uv run ruff check .

      - name: Run tests
        run: uv run pytest

      - name: Type check
        run: uv run mypy app/
```

---

## Verification Checklist

After completing all steps, verify:

- [ ] `uv sync` installs all dependencies correctly
- [ ] `uv run uvicorn app.main:app --reload` starts the server
- [ ] `uv run alembic upgrade head` runs migrations
- [ ] `uv run pytest` runs tests (once tests exist)
- [ ] No `requirements*.txt` files remain
- [ ] No `venv/` directory remains (only `.venv/`)
- [ ] Docker build succeeds with the new Dockerfile
- [ ] All documentation references `uv` instead of `pip`
