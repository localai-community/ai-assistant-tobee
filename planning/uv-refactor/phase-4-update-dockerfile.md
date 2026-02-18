# Phase 4: Update `Dockerfile`

## Current State

```dockerfile
FROM python:3.11-bullseye
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ curl libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    && rm -rf /var/lib/apt/lists/* && apt-get clean
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p storage/uploads storage/vector_db
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Target State

```dockerfile
FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy dependency files first (layer caching)
COPY pyproject.toml uv.lock ./

# Install Python dependencies using lockfile
RUN uv sync --frozen --no-dev

# Copy application code (selective, not COPY . .)
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
COPY lambda_handler.py .

# Create storage directories
RUN mkdir -p storage/uploads storage/vector_db

# Non-root user
RUN useradd -m appuser
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Changes
- `python:3.11-bullseye` → `python:3.13-slim` (match local dev)
- Install `uv` from official image
- `pip install -r requirements.txt` → `uv sync --frozen --no-dev`
- `COPY . .` → selective COPY of only app code
- Add non-root `appuser`
- `CMD uvicorn` → `CMD uv run uvicorn`

## File Modified
- `backend/Dockerfile`
