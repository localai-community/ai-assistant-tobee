# Phase 7: Update `MIGRATIONS.md`

## Changes

All changes are `venv` → `.venv` and bare commands → `uv run` prefixed.

### Option 1: Auto migration (line 18)
```
Before:  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
After:   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Option 2: Python script (lines 41, 50, 55, 60)
```
Before:  python migrate_db.py
         python migrate_db.py --check-pending
         python migrate_db.py --check
         python migrate_db.py --history
After:   uv run python migrate_db.py
         uv run python migrate_db.py --check-pending
         uv run python migrate_db.py --check
         uv run python migrate_db.py --history
```

### Option 3: Alembic directly (lines 70-71)
```
Before:  source venv/bin/activate  # On Windows: venv\Scripts\activate
         alembic upgrade head
After:   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
         uv run alembic upgrade head
```

### Create migration (lines 92-94)
```
Before:  source venv/bin/activate
         alembic revision -m "add_new_field_to_user_settings"
After:   uv run alembic revision -m "add_new_field_to_user_settings"
```

### Test migration (lines 117-125)
```
Before:  alembic upgrade head / alembic downgrade -1
After:   uv run alembic upgrade head / uv run alembic downgrade -1
```

### Common commands section (lines 137-158)
Prefix all bare `alembic` commands with `uv run`.

### Troubleshooting (lines 174, 181-191)
```
Before:  python migrate_db.py --check
         alembic upgrade head
After:   uv run python migrate_db.py --check
         uv run alembic upgrade head
```

### Auto-generate (lines 197-198)
```
Before:  alembic revision --autogenerate -m "auto detected changes"
After:   uv run alembic revision --autogenerate -m "auto detected changes"
```

### Recent migrations (line 223) and Need Help (lines 228-230)
```
Before:  python migrate_db.py
         alembic history
         python migrate_db.py --check
After:   uv run python migrate_db.py
         uv run alembic history
         uv run python migrate_db.py --check
```

## File Modified
- `backend/MIGRATIONS.md`
