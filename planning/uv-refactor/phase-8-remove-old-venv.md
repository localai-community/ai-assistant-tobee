# Phase 8: Remove Old `venv/` Directory

## Current State

Two virtual environments exist side by side:
- `backend/venv/` — old pip-managed venv (Python 3.13, created manually)
- `backend/.venv/` — uv-managed venv (Python 3.13, created by `uv sync`)

## Action

```bash
rm -rf backend/venv/
```

## Pre-check
- Confirm `.venv/` exists and is functional: `uv run python --version`
- Confirm `venv/` is not referenced by any remaining scripts (should be clean after phases 2-3)

## Post-check
- Only `.venv/` remains
- `.gitignore` already covers both `venv/` and `.venv/`
- `uv sync` and `uv run uvicorn app.main:app --reload` still work

## File Deleted
- `backend/venv/` (entire directory)
