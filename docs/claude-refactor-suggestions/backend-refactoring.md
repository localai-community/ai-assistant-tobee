# Backend Refactoring Suggestions

## Critical

### 1. No Authentication/Authorization

Every endpoint is completely open — anyone can create/delete users, access conversations, or read sensitive prompt data. There are no auth guards, no JWT/session validation, nothing.

**Files affected:**
- `backend/app/api/chat.py`
- `backend/app/api/users.py`
- `backend/app/api/user_sessions.py`
- `backend/app/api/user_settings.py`
- `backend/app/api/view_prompts_context.py`
- `backend/app/api/reasoning.py`

**Recommendation:** Implement JWT or session-based authentication middleware. Add dependency injection for authenticated user context (`Depends(get_current_user)`). At minimum, add API key validation for production deployments.

---

### 2. Exception Details Leaked to Clients

All error handlers do `raise HTTPException(status_code=500, detail=str(e))`, which exposes raw internal exception messages (DB errors, file paths, stack traces) to API consumers.

**Files affected:** All API route files under `backend/app/api/`

**Recommendation:** Return generic error messages to clients. Log the full exception server-side. Create custom exception classes and a global exception handler.

```python
# Instead of:
raise HTTPException(status_code=500, detail=str(e))

# Do:
logger.error(f"Operation failed: {e}", exc_info=True)
raise HTTPException(status_code=500, detail="Internal server error")
```

---

### 3. Zero Test Coverage

No pytest test files exist. The `pyproject.toml` has test dependencies (`pytest`, `pytest-asyncio`, `httpx`), but there's no `tests/` directory, no `conftest.py`, and no actual tests. The "tests" that exist (`test_handler.py`, `test_lambda_local.py`) are manual simulation scripts.

**Recommendation:**
- Create `backend/tests/` directory with `conftest.py`
- Add unit tests for all repository classes
- Add integration tests for API endpoints using `httpx.AsyncClient`
- Add service-level tests for `ChatService`, `DocumentManager`, etc.
- Target at least critical path coverage first (chat streaming, user CRUD, conversation CRUD)

---

## High

### 5. Security Misconfigurations

**CORS wildcard with credentials:**
```python
# backend/app/main.py
allow_origins=["*"]       # Allows any origin
allow_credentials=True    # Combined with wildcard = misconfiguration
```

**Hardcoded secret key:**
```python
# backend/app/core/config.py
secret_key: str = "your-secret-key-change-in-production"
```

**Hardcoded developer path:**
```json
// backend/mcp-config-local.json
"ALLOWED_PATHS": "/Users/leia/workspaces/llm/ai-assistant,/tmp"
```

**Recommendation:**
- Set explicit allowed origins from environment variable
- Require `SECRET_KEY` env var with no default (fail on startup if missing)
- Use relative or environment-variable-based paths in MCP config

---

### 6. Four Conflicting Requirements Files

`requirements.txt`, `requirements-simple.txt`, `requirements-advanced.txt`, and `requirements-updated.txt` all coexist alongside `pyproject.toml` with inconsistent content.

**Recommendation:** Remove all `requirements*.txt` files. Use `pyproject.toml` as the single source of truth with dependency groups for different install profiles. See [UV Migration Steps](./uv-migration-steps.md).

---

### 7. Pydantic v1 Patterns in a v2 Project

The project uses Pydantic v2 (`pydantic>=2.8.0`) but still uses v1 API patterns:
- `.dict(exclude_unset=True)` → should be `.model_dump(exclude_unset=True)`
- `.from_orm()` → should be `model_validate(orm_object)`
- `class Config: orm_mode = True` → should be `model_config = ConfigDict(from_attributes=True)`

**Files affected:**
- `backend/app/models/schemas.py`
- `backend/app/services/user_settings_repository.py`

**Recommendation:** Migrate to Pydantic v2 API. These deprecated aliases will be removed in Pydantic v3.

---

## Medium

### 8. ChatService Instantiated Per-Request

Every route handler creates `ChatService(ollama_url=..., db=db)` inline. No dependency injection, no singleton reuse. MCP manager initialization (with a 1-second sleep in `manager.py`) runs per-request.

**Files affected:** `backend/app/api/chat.py`

**Recommendation:** Use FastAPI dependency injection to create and cache service instances. Consider a `get_chat_service` dependency that reuses the MCP manager across requests.

```python
async def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(
        ollama_url=settings.ollama_base_url,
        db=db,
        mcp_manager=app.state.mcp_manager  # initialized at startup
    )
```

---

### 9. Inconsistent Configuration Access

`settings.ollama_base_url` exists in the Settings object, but routes use `os.getenv("OLLAMA_URL")` directly — two different env var names for the same purpose, and the Settings object is bypassed.

**Files affected:**
- `backend/app/core/config.py` (defines `ollama_base_url`)
- `backend/app/api/chat.py` (reads `os.getenv("OLLAMA_URL")`)

**Recommendation:** Use the `Settings` object consistently everywhere. Remove direct `os.getenv()` calls in route handlers.

---

### 10. Reasoning Router Missing API Prefix

All routers mount under `/api/v1/` except `reasoning_router` which mounts at `/reasoning`.

**Files affected:** `backend/app/main.py`

**Recommendation:** Mount reasoning router at `/api/v1/reasoning` for consistency.

---

### 11. Deprecated SQLAlchemy Patterns

`declarative_base()` from `sqlalchemy.ext.declarative` is deprecated in SQLAlchemy 2.x.

**Files affected:** `backend/app/core/database.py`

**Recommendation:**
```python
# Instead of:
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Use:
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass
```

---

### 12. Fragmented ORM Model Layout

`UserSettings` lives in `app/models/user_settings.py` separate from all other models in `app/models/database.py`, importing `Base` from a different path.

**Recommendation:** Consolidate all ORM models into `app/models/database.py` or create a proper `__init__.py` that re-exports everything from a single location.

---

## Low

### 13. Deprecated FastAPI `@app.on_event()`

`@app.on_event("startup")` and `@app.on_event("shutdown")` are deprecated.

**Files affected:** `backend/app/main.py`

**Recommendation:** Use the `lifespan` context manager pattern:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup logic
    yield
    # shutdown logic

app = FastAPI(lifespan=lifespan)
```

---

### 14. Module-Level Side Effects

`ensure_directories()` runs on import of `core/config.py`, causing filesystem side effects at import time.

**Recommendation:** Move directory creation to the application startup (lifespan), not module import.

---

### 15. Duplicate Logger Assignment

`document_processor.py` defines `logger = logging.getLogger(__name__)` twice.

**Recommendation:** Remove the duplicate.

---

### 16. Docker Issues

- Dockerfile uses Python 3.11, local dev uses 3.13 (version mismatch)
- No `.dockerignore` — venv, DB file, and cache get copied into the image
- Container runs as root (no `USER` instruction)
- Single uvicorn worker (no `--workers` flag)

**Recommendation:** See [UV Migration Steps](./uv-migration-steps.md) for the Dockerfile rewrite. Add a `.dockerignore`, a non-root user, and multi-worker configuration.
