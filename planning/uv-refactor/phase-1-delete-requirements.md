# Phase 1: Delete Old Requirements Files

## Pre-check

Verify all dependencies from the 4 files exist in `pyproject.toml`.

**Already verified** — only gap was `pdfplumber>=0.9.0`, which has been added.

## Actions

```bash
cd backend
rm requirements.txt
rm requirements-simple.txt
rm requirements-advanced.txt
rm requirements-updated.txt
```

## Files Deleted
- `backend/requirements.txt` (40 lines — core + RAG + doc processing deps)
- `backend/requirements-simple.txt` (22 lines — minimal FastAPI + SQLAlchemy + MCP)
- `backend/requirements-advanced.txt` (29 lines — ML/RAG deps only)
- `backend/requirements-updated.txt` (39 lines — older iteration with different pins)

## Verification
- `pyproject.toml` remains the single source of truth
- `uv sync` still resolves and installs all deps
