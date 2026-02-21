# Backend Codebase Catalog

Generated from exploration of `/Users/leia/workspaces/llm/ai-assistant/backend/app/`

---

## Table of Contents

1. [Database Queries](#1-database-queries)
2. [API Routes](#2-api-routes)
3. [Error Handling Patterns](#3-error-handling-patterns)

---

## 1. Database Queries

### 1.1 SQLAlchemy Model Definitions

All database models are defined in:
- `/backend/app/models/database.py` (lines 1-194)
- `/backend/app/models/user_settings.py`

#### Core Models

| Model | File | Lines | Table Name |
|-------|------|-------|------------|
| User | `app/models/database.py` | 18-33 | `users` |
| Conversation | `app/models/database.py` | 35-52 | `conversations` |
| Message | `app/models/database.py` | 54-70 | `messages` |
| ChatDocument | `app/models/database.py` | 72-95 | `chat_documents` |
| DocumentChunk | `app/models/database.py` | 97-112 | `document_chunks` |
| UserSession | `app/models/database.py` | 114-128 | `user_sessions` |
| UserQuestion | `app/models/database.py` | 130-149 | `user_questions` |
| AIPrompt | `app/models/database.py` | 151-172 | `ai_prompts` |
| ContextAwarenessData | `app/models/database.py` | 174-194 | `context_awareness_data` |
| UserSettings | `app/models/user_settings.py` | 5-50 | `user_settings` |

---

### 1.2 Database Connection Management

**File:** `app/core/database.py`

| Function | Lines | Description |
|----------|-------|-------------|
| `create_engine()` | 17-30 | Creates SQLAlchemy engine (SQLite for dev, PostgreSQL for prod) |
| `SessionLocal` | 33 | Session factory |
| `create_tables()` | 35-42 | Creates all database tables |
| `get_db()` | 44-50 | FastAPI dependency for session injection |
| `init_db()` | 52-62 | Initializes database with tables |

---

### 1.3 Repository Pattern - Query Operations

All repository classes are in `app/services/repository.py`.

#### ConversationRepository (lines 16-90)

| Method | Lines | Query Type | Operation |
|--------|-------|------------|-----------|
| `create_conversation()` | 22-37 | INSERT | Creates new conversation |
| `get_conversation()` | 39-44 | SELECT | Get conversation by ID |
| `get_conversations()` | 46-53 | SELECT | List conversations (with optional user filter) |
| `update_conversation()` | 55-68 | UPDATE | Update conversation fields |
| `delete_conversation()` | 70-78 | UPDATE | Soft delete (sets `is_active=False`) |
| `clear_conversations()` | 80-90 | UPDATE | Batch soft delete all conversations |

#### MessageRepository (lines 92-130)

| Method | Lines | Query Type | Operation |
|--------|-------|------------|-----------|
| `create_message()` | 98-110 | INSERT | Create new message |
| `get_messages()` | 112-116 | SELECT | Get messages for conversation |
| `get_message()` | 118-120 | SELECT | Get single message by ID |
| `delete_message()` | 122-130 | DELETE | Hard delete message |

#### UserRepository (lines 132-206)

| Method | Lines | Query Type | Operation |
|--------|-------|------------|-----------|
| `create_user()` | 138-147 | INSERT | Create new user |
| `get_user()` | 149-154 | SELECT | Get user by ID |
| `get_user_by_username()` | 156-161 | SELECT | Get user by username |
| `get_users()` | 163-167 | SELECT | List all active users |
| `delete_user()` | 169-189 | DELETE | Hard delete user (cascade) |
| `delete_user_by_username()` | 191-206 | DELETE | Hard delete user by username |

#### ChatDocumentRepository (lines 208-293)

| Method | Lines | Query Type | Operation |
|--------|-------|------------|-----------|
| `create_document()` | 214-226 | INSERT | Create chat document |
| `get_document()` | 228-230 | SELECT | Get document by ID |
| `get_conversation_documents()` | 232-236 | SELECT | Get documents for conversation |
| `get_user_documents()` | 238-242 | SELECT | Get documents for user |
| `update_document()` | 244-263 | UPDATE | Update document fields |
| `delete_document()` | 265-279 | DELETE | Hard delete document |
| `cleanup_conversation_documents()` | 281-293 | DELETE | Batch delete documents for conversation |

#### DocumentChunkRepository (lines 295-333)

| Method | Lines | Query Type | Operation |
|--------|-------|------------|-----------|
| `create_chunk()` | 301-313 | INSERT | Create document chunk |
| `get_document_chunks()` | 315-319 | SELECT | Get chunks for document |
| `delete_document_chunks()` | 321-333 | DELETE | Batch delete chunks for document |

#### UserSessionRepository (lines 335-401)

| Method | Lines | Query Type | Operation |
|--------|-------|------------|-----------|
| `create_session()` | 341-350 | INSERT | Create new session |
| `get_session()` | 352-356 | SELECT | Get session by key |
| `update_session()` | 358-375 | UPDATE | Update session |
| `upsert_session()` | 377-401 | INSERT/UPDATE | Create or update session |

#### UserQuestionRepository (lines 403-445)

| Method | Lines | Query Type | Operation |
|--------|-------|------------|-----------|
| `create_question()` | 409-419 | INSERT | Create user question |
| `get_question()` | 421-423 | SELECT | Get question by ID |
| `get_questions_by_conversation()` | 425-429 | SELECT | Get questions for conversation |
| `get_questions_by_user()` | 431-435 | SELECT | Get questions for user |
| `delete_question()` | 437-445 | DELETE | Delete question |

#### AIPromptRepository (lines 447-493)

| Method | Lines | Query Type | Operation |
|--------|-------|------------|-----------|
| `create_prompt()` | 453-467 | INSERT | Create AI prompt |
| `get_prompt_by_question()` | 469-471 | SELECT | Get prompt for question |
| `get_prompts_by_conversation()` | 473-477 | SELECT | Get prompts for conversation |
| `get_prompts_by_user()` | 479-483 | SELECT | Get prompts for user |
| `delete_prompt()` | 485-493 | DELETE | Delete prompt |

#### ContextAwarenessRepository (lines 495-551)

| Method | Lines | Query Type | Operation |
|--------|-------|------------|-----------|
| `create_context_data()` | 501-514 | INSERT | Create context awareness data |
| `get_context_by_question()` | 516-520 | SELECT | Get all context for question |
| `get_context_by_type()` | 522-529 | SELECT | Get context by type for question |
| `get_context_by_conversation()` | 531-535 | SELECT | Get context for conversation |
| `get_context_by_user()` | 537-541 | SELECT | Get context for user |
| `delete_context_data()` | 543-550 | DELETE | Delete context data |

---

### 1.4 UserSettingsRepository

**File:** `app/services/user_settings_repository.py`

| Method | Lines | Query Type | Operation |
|--------|-------|------------|-----------|
| `get_user_settings()` | 13-19 | SELECT | Get user settings by user_id |
| `create_user_settings()` | 21-33 | INSERT | Create user settings |
| `update_user_settings()` | 35-54 | UPDATE | Update existing settings |
| `upsert_user_settings()` | 56-69 | INSERT/UPDATE | Create or update settings |

---

### 1.5 Query Patterns Summary

All queries follow SQLAlchemy ORM patterns:

| Pattern | Count | Locations |
|---------|-------|-----------|
| `.query(Model).filter()` | ~40 | repository.py, user_settings_repository.py |
| `.query(Model).filter().first()` | ~25 | repository.py |
| `.query(Model).filter().all()` | ~15 | repository.py |
| `.query(Model).filter().order_by().limit().all()` | ~10 | repository.py |
| `.query(Model).delete()` | ~8 | repository.py |
| `.query(Model).update()` | ~1 | repository.py |
| `.add()` | ~15 | repository.py, user_settings_repository.py |
| `.commit()` | ~40 | All repository methods |
| `.refresh()` | ~20 | All create/update methods |
| `.delete()` | ~10 | repository.py |
| `.rollback()` | ~12 | repository.py, user_settings_repository.py |

### 1.6 Raw SQL

The codebase uses **no raw SQL** - pure SQLAlchemy ORM throughout.

---

## 2. API Routes

### 2.1 Root Level Endpoints (main.py)

**File:** `app/main.py`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Root endpoint - returns API info |
| GET | `/health` | Health check endpoint |
| GET | `/api/v1/status` | API status with feature flags |

---

### 2.2 Chat API Routes

**File:** `app/api/chat.py`
**Prefix:** `/api/v1/chat`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/chat/stream` | Streaming chat with Ollama |
| GET | `/api/v1/chat/models` | Get available Ollama models |
| GET | `/api/v1/chat/health` | Chat service and Ollama health |
| GET | `/api/v1/chat/conversations` | List conversations (optional user_id filter) |
| GET | `/api/v1/chat/conversations/{conversation_id}` | Get specific conversation |
| GET | `/api/v1/chat/conversations/{conversation_id}/messages` | Get conversation messages |
| DELETE | `/api/v1/chat/conversations/{conversation_id}` | Delete conversation |
| DELETE | `/api/v1/chat/conversations` | Clear all conversations |
| GET | `/api/v1/chat/tools` | List available MCP tools |
| POST | `/api/v1/chat/tools/{tool_name}/call` | Call MCP tool |
| GET | `/api/v1/chat/tools/health` | MCP tools health check |
| GET | `/api/v1/chat/context/{conversation_id}` | Get conversation context |
| GET | `/api/v1/chat/context/user/{user_id}` | Get user context across conversations |
| POST | `/api/v1/chat/context/{conversation_id}/memory` | Store conversation as memory |
| POST | `/api/v1/chat/upload` | Upload document for RAG processing |
| GET | `/api/v1/chat/documents/{conversation_id}` | Get documents for conversation |

---

### 2.3 Users API Routes

**File:** `app/api/users.py`
**Prefix:** `/api/v1/users`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/users/` | Get all active users |
| GET | `/api/v1/users/{user_id}` | Get user by ID |
| GET | `/api/v1/users/check-username/{username}` | Check if username exists |
| POST | `/api/v1/users/` | Create new user |
| DELETE | `/api/v1/users/{user_id}` | Delete user by ID |
| DELETE | `/api/v1/users/username/{username}` | Delete user by username |

---

### 2.4 User Sessions API Routes

**File:** `app/api/user_sessions.py`
**Prefix:** `/api/v1/user-sessions`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/user-sessions/{session_key}` | Get session by key |
| POST | `/api/v1/user-sessions/{session_key}` | Create new session |
| PUT | `/api/v1/user-sessions/{session_key}` | Update session |
| POST | `/api/v1/user-sessions/{session_key}/set-user/{user_id}` | Set current user for session |

---

### 2.5 User Settings API Routes

**File:** `app/api/user_settings.py`
**Prefix:** `/api/v1/user-settings`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/user-settings/{user_id}` | Get user settings |
| POST | `/api/v1/user-settings/` | Create user settings |
| PUT | `/api/v1/user-settings/{user_id}` | Update user settings |
| POST | `/api/v1/user-settings/{user_id}/upsert` | Create or update user settings |

---

### 2.6 View Prompts Context API Routes

**File:** `app/api/view_prompts_context.py`
**Prefix:** `/api/v1/view-prompts-context`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/view-prompts-context/questions/{question_id}/prompt` | Get AI prompt for question |
| GET | `/api/v1/view-prompts-context/questions/{question_id}/context` | Get context for question |
| GET | `/api/v1/view-prompts-context/questions/{question_id}/details` | Get complete question details |
| GET | `/api/v1/view-prompts-context/conversations/{conversation_id}/questions` | Get conversation questions |
| GET | `/api/v1/view-prompts-context/conversations/{conversation_id}/prompts` | Get conversation prompts |
| GET | `/api/v1/view-prompts-context/conversations/{conversation_id}/context` | Get conversation context |
| GET | `/api/v1/view-prompts-context/users/{user_id}/questions` | Get user questions |
| GET | `/api/v1/view-prompts-context/users/{user_id}/prompts` | Get user prompts |
| GET | `/api/v1/view-prompts-context/users/{user_id}/context` | Get user context |

---

### 2.7 Reasoning API Routes

**File:** `app/api/reasoning.py`
**Prefix:** `/reasoning`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/reasoning/parse-problem` | Parse and analyze problem statement |
| POST | `/reasoning/parse-steps` | Parse step-by-step reasoning output |
| POST | `/reasoning/validate` | Validate reasoning input, steps, and result |
| POST | `/reasoning/format` | Format reasoning result |
| POST | `/reasoning/test-workflow` | Test complete reasoning workflow |
| GET | `/reasoning/health` | Reasoning system health check |
| GET | `/reasoning/available-formats` | Get available output formats |
| GET | `/reasoning/available-parsers` | Get available parsers |

---

### 2.8 API Routes Summary

| Router | Prefix | Endpoints |
|--------|--------|-----------|
| Root (main.py) | - | 3 |
| Chat | `/api/v1/chat` | 16 |
| Users | `/api/v1/users` | 6 |
| User Sessions | `/api/v1/user-sessions` | 4 |
| User Settings | `/api/v1/user-settings` | 4 |
| View Prompts Context | `/api/v1/view-prompts-context` | 9 |
| Reasoning | `/reasoning` | 8 |

**Total: 50 API endpoints**

---

## 3. Error Handling Patterns

### 3.1 Custom Exception Classes

The codebase does **not** have dedicated custom exception classes. Instead, it relies on standard Python exceptions:

| File | Line | Exception | Purpose |
|------|------|-----------|---------|
| `app/services/repository.py` | 26 | `ValueError` | "Cannot create conversations for guest users" |
| `app/services/rag/document_processor.py` | 63 | `FileNotFoundError` | "File not found: {file_path}" |
| `app/services/rag/document_processor.py` | 147 | `ValueError` | "No PDF processing library available" |
| `app/services/rag/document_processor.py` | 165 | `ValueError` | "No DOCX processing library available" |
| `app/services/rag/document_processor.py` | 188 | `ValueError` | "Could not extract text from {file_path}" |
| `app/services/rag/document_processor.py` | 194 | `FileNotFoundError` | "Directory not found: {directory_path}" |
| `app/mcp/client.py` | 85 | `RuntimeError` | "MCP server {server_name} is not running" |
| `app/mcp/client.py` | 105 | `RuntimeError` | "No response from MCP server" |
| `app/reasoning/unified.py` | 391 | `ValueError` | "Cannot configure unknown mode: {mode}" |
| `app/reasoning/unified.py` | 424 | `ValueError` | "Cannot create reasoner for unknown mode: {mode}" |

---

### 3.2 Error Response Models

**File:** `app/core/models.py` (lines 21-25)

```python
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    status_code: int
```

This is imported in `app/api/chat.py` but not extensively used - most endpoints use `HTTPException` with `detail` parameter directly.

---

### 3.3 Exception Handlers

**There are no custom FastAPI exception handlers** (`@app.exception_handler`) defined in the codebase. The app relies entirely on FastAPI's default exception handling and direct `HTTPException` raises.

---

### 3.4 Try/Except Patterns

#### Pattern 1: Simple Catch-All with Logging (Most Common)

```python
try:
    # business logic
except Exception as e:
    logger.error(f"Failed to do something: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

Found in:
- `app/api/chat.py` lines 51-111, 197-203, 217-228
- `app/api/users.py` lines 32-38

#### Pattern 2: Re-raise HTTPException

```python
try:
    # business logic that may raise HTTPException
except HTTPException:
    raise  # Re-raise HTTPException
except Exception as e:
    logger.error(...)
    raise HTTPException(status_code=500, detail=str(e))
```

Found in:
- `app/api/chat.py` lines 224-228
- `app/api/users.py` lines 60-64

#### Pattern 3: Nested Try/Except with Fallback (RAG/Services)

```python
try:
    # Primary approach
    result = primary_method()
except Exception as primary_error:
    try:
        # Fallback approach
        result = fallback_method()
    except Exception as fallback_error:
        logger.error(f"Both primary and fallback failed: {primary_error}, {fallback_error}")
        raise
```

Found in:
- `app/services/rag/vector_store.py` lines 57-71
- `app/services/rag/advanced_retriever.py` lines 385-500

#### Pattern 4: ImportError Handling (Document Processing)

```python
try:
    from pymupdf import fitz
except ImportError:
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise ImportError("Neither PyMuPDF nor pdf2image is available")
```

Found in `app/services/rag/document_processor.py` lines 7-33

#### Pattern 5: Database Session Management

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Found in `app/core/database.py` lines 44-50

#### Pattern 6: Graceful Degradation with Error Dictionary

```python
except Exception as e:
    logger.error(f"Error: {e}")
    return {
        "status": "error",
        "mcp_enabled": False,
        "servers": {},
        "tools_count": 0,
        "overall_healthy": False,
        "error": str(e)
    }
```

Found in `app/api/chat.py` lines 175-183, 385-393

#### Pattern 7: Non-Fatal Error Logging

```python
try:
    # Optional feature
    summary_result = await summary_service.generate_summary(...)
except Exception as e:
    logger.error(f"Error generating summary: {e}")
    # Don't fail the main operation
```

Found in `app/api/chat.py` lines 597-614

---

### 3.5 HTTP Status Code Usage

| Status Code | Usage | Count |
|-------------|-------|-------|
| **500** | Internal server error (general exceptions) | ~40+ |
| **404** | Resource not found | ~10 |
| **400** | Bad request / validation error | ~6 |
| **503** | Service unavailable (Ollama down) | ~1 |

#### 500 - Internal Server Error

```python
raise HTTPException(status_code=500, detail=str(e))
```

Used in:
- `app/api/chat.py` lines 111, 149, 203, 228, 262, 287, 310, 332, 355, 441, 469, 516, 631, 670
- `app/api/users.py` lines 38, 64, 89, 117, 143, 169
- `app/api/user_sessions.py` lines 44, 77, 108, 133
- `app/api/user_settings.py` lines 28, 43, 58, 80, 85
- `app/api/reasoning.py` lines 136, 158, 210, 261, 332

#### 404 - Not Found

```python
raise HTTPException(status_code=404, detail="Resource not found")
```

Used in:
- `app/api/chat.py` lines 222, 249, 281, 490
- `app/api/users.py` lines 57, 136, 162

#### 400 - Bad Request

```python
raise HTTPException(status_code=400, detail="Validation message")
```

Used in:
- `app/api/chat.py` lines 543-544, 572-573 (file type validation)
- `app/api/users.py` line 109 (username exists)

#### 503 - Service Unavailable

```python
raise HTTPException(status_code=503, detail="Ollama service is not available")
```

Used in `app/api/chat.py` lines 58-60

---

### 3.6 Error Handling Summary

| Category | Finding |
|----------|---------|
| Custom Exception Classes | None defined |
| Error Response Models | `ErrorResponse` defined but minimally used |
| FastAPI Exception Handlers | None defined |
| Try/Except Patterns | 7 distinct patterns identified |
| HTTP Status Codes | Primarily 500, with selective 404, 400, 503 |
| Logging | Used consistently via `logger.error()` |

---

*Generated on 2026-02-21*
