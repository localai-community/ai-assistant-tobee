# Backend Codebase Catalog

## 1. Database Queries

### SQLAlchemy Models

All models defined in `backend/app/models/database.py` and `backend/app/models/user_settings.py`:

| Model | File | Table Name |
|-------|------|------------|
| User | `app/models/database.py` | `users` |
| Conversation | `app/models/database.py` | `conversations` |
| Message | `app/models/database.py` | `messages` |
| ChatDocument | `app/models/database.py` | `chat_documents` |
| DocumentChunk | `app/models/database.py` | `document_chunks` |
| UserSession | `app/models/database.py` | `user_sessions` |
| UserQuestion | `app/models/database.py` | `user_questions` |
| AIPrompt | `app/models/database.py` | `ai_prompts` |
| ContextAwarenessData | `app/models/database.py` | `context_awareness_data` |
| UserSettings | `app/models/user_settings.py` | `user_settings` |

### Repository Pattern

Two main repository files handle all database operations:

**`backend/app/services/repository.py`** (551 lines):
- `ConversationRepository` - create, get, update, delete conversations
- `MessageRepository` - create, get, delete messages
- `UserRepository` - create, get, delete users
- `ChatDocumentRepository` - CRUD for documents
- `DocumentChunkRepository` - chunk management
- `UserSessionRepository` - session management
- `UserQuestionRepository` - question management
- `AIPromptRepository` - prompt management
- `ContextAwarenessRepository` - context data management

**`backend/app/services/user_settings_repository.py`** (90 lines):
- User settings CRUD operations

### Query Patterns

All queries use SQLAlchemy ORM:
- `.query(Model).filter()` - ~40 locations
- `.query(Model).filter().first()` - ~25 locations
- `.query(Model).filter().all()` - ~15 locations
- `.add()` / `.commit()` / `.refresh()` - throughout
- `.delete()` - ~10 locations
- `.rollback()` - ~12 locations

**No raw SQL queries** - pure SQLAlchemy ORM throughout.

---

## 2. API Routes

Total: **50 endpoints** across 7 routers

### Chat API (`/api/v1/chat`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/chat/stream` | Streaming chat with Ollama |
| GET | `/api/v1/chat/models` | Get available Ollama models |
| GET | `/api/v1/chat/health` | Chat service and Ollama health |
| GET | `/api/v1/chat/conversations` | List conversations |
| GET | `/api/v1/chat/conversations/{id}` | Get conversation |
api/v1/| GET | `/chat/conversations/{id}/messages` | Get messages |
| DELETE | `/api/v1/chat/conversations/{id}` | Delete conversation |
| DELETE | `/api/v1/chat/conversations` | Clear all conversations |
| GET | `/api/v1/chat/tools` | List MCP tools |
| POST | `/api/v1/chat/tools/{tool_name}/call` | Call MCP tool |
| GET | `/api/v1/chat/tools/health` | MCP health check |
| GET | `/api/v1/chat/context/{id}` | Get conversation context |
| GET | `/api/v1/chat/context/user/{user_id}` | Get user context |
| POST | `/api/v1/chat/context/{id}/memory` | Store as memory |
| POST | `/api/v1/chat/upload` | Upload for RAG |
| GET | `/api/v1/chat/documents/{conversation_id}` | Get documents |

### Users API (`/api/v1/users`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/users/` | List all users |
| GET | `/api/v1/users/{user_id}` | Get user by ID |
| GET | `/api/v1/users/check-username/{username}` | Check username |
| POST | `/api/v1/users/` | Create user |
| DELETE | `/api/v1/users/{user_id}` | Delete user |
| DELETE | `/api/v1/users/username/{username}` | Delete by username |

### User Sessions API (`/api/v1/user-sessions`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/user-sessions/{session_key}` | Get session |
| POST | `/api/v1/user-sessions/{session_key}` | Create session |
| PUT | `/api/v1/user-sessions/{session_key}` | Update session |
| POST | `/api/v1/user-sessions/{session_key}/set-user/{user_id}` | Set user |

### User Settings API (`/api/v1/user-settings`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/user-settings/{user_id}` | Get settings |
| POST | `/api/v1/user-settings/` | Create settings |
| PUT | `/api/v1/user-settings/{user_id}` | Update settings |
| POST | `/api/v1/user-settings/{user_id}/upsert` | Upsert settings |

### View Prompts Context API (`/api/v1/view-prompts-context`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/view-prompts-context/questions/{id}/prompt` | Get prompt |
| GET | `/view-prompts-context/questions/{id}/context` | Get context |
| GET | `/view-prompts-context/questions/{id}/details` | Get details |
| GET | `/view-prompts-context/conversations/{id}/questions` | Get questions |
| GET | `/view-prompts-context/conversations/{id}/prompts` | Get prompts |
| GET | `/view-prompts-context/conversations/{id}/context` | Get context |
| GET | `/view-prompts-context/users/{user_id}/questions` | Get questions |
| GET | `/view-prompts-context/users/{user_id}/prompts` | Get prompts |
| GET | `/view-prompts-context/users/{user_id}/context` | Get context |

### Reasoning API (`/reasoning`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/reasoning/parse-problem` | Parse problem |
| POST | `/reasoning/parse-steps` | Parse reasoning |
| POST | `/reasoning/validate` | Validate |
| POST | `/reasoning/format` | Format result |
| POST | `/reasoning/test-workflow` | Test workflow |
| GET | `/reasoning/health` | Health check |
| GET | `/reasoning/available-formats` | List formats |
| GET | `/reasoning/available-parsers` | List parsers |

---

## 3. Error Handling Patterns

### Custom Exceptions
**None defined** - uses standard Python exceptions directly (ValueError, RuntimeError, FileNotFoundError, ImportError).

### Error Response Model
Defined in `backend/app/core/models.py`:
```python
class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int
```
Minimally used - most endpoints use `HTTPException` with `detail`.

### FastAPI Exception Handlers
**None defined** - relies on FastAPI defaults.

### Try/Except Patterns

**Pattern 1: Simple Catch-All** (most common)
```python
try:
    # business logic
except Exception as e:
    logger.error(f"Failed: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

**Pattern 2: Re-raise HTTPException**
```python
try:
    # may raise HTTPException
except HTTPException:
    raise
except Exception as e:
    logger.error(...)
    raise HTTPException(status_code=500, detail=str(e))
```

**Pattern 3: Nested with Fallback** (RAG/services)
```python
try:
    result = primary_method()
except Exception as primary_error:
    try:
        result = fallback_method()
    except Exception as fallback_error:
        logger.error(f"Both failed: {primary_error}, {fallback_error}")
        raise
```

**Pattern 4: ImportError Handling**
```python
try:
    from pymupdf import fitz
except ImportError:
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise ImportError("Neither available")
```

**Pattern 5: Session Management**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Pattern 6: Graceful Degradation**
```python
except Exception as e:
    return {"status": "error", "healthy": False, "error": str(e)}
```

**Pattern 7: Non-Fatal Error Logging**
```python
try:
    optional_feature()
except Exception as e:
    logger.error(f"Error: {e}")
    # Don't fail main operation
```

### HTTP Status Codes

| Code | Usage | Count |
|------|-------|-------|
| 500 | Internal server error | ~40+ |
| 404 | Not found | ~10 |
| 400 | Bad request | ~6 |
| 503 | Service unavailable | ~1 |

---

*Generated from codebase exploration*
