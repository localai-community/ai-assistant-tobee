# Phase 6: Update `README.md`

## Changes

### Prerequisites section (line 17-19)
```
Before:  - Python 3.11+
After:   - Python 3.10+
         - uv (install: https://docs.astral.sh/uv/getting-started/installation/)
```

### Installation section (lines 23-26)
```
Before:  pip install -r requirements.txt
After:   uv sync
```

### Run commands (lines 34-41)
```
Before:  uvicorn app.main:app --reload
         uvicorn app.main:app --host 0.0.0.0 --port 8000
After:   uv run uvicorn app.main:app --reload
         uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Project structure (lines 74-89)
```
Before:  ├── requirements.txt
After:   ├── pyproject.toml
         ├── uv.lock
```

### Testing section (lines 96-101)
```
Before:  python test_chat.py
         python -c "from app.services.chat ..."
After:   uv run python test_chat.py
         uv run python -c "from app.services.chat ..."
```

## File Modified
- `backend/README.md`
