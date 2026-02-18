# CLAUDE.md - AI Assistant Tobee

## Project Overview

**Tobee** is a fully open source, local-first AI assistant with MCP (Model Context Protocol) and RAG (Retrieval-Augmented Generation) support. It runs completely offline with no external dependencies required after initial setup.

- **GitHub Org**: localai-community
- **License**: Apache 2.0
- **Status**: Under active development

## Architecture

Hybrid LLM integration: Direct Ollama API for core chat + LangChain for RAG workflows.

- **Backend**: FastAPI (Python 3.10+) with SQLAlchemy, Alembic, reasoning engines
- **Frontend (primary)**: Next.js 15 + React 19 + TypeScript (`frontend-nextjs/`)
- **Frontend (legacy)**: Streamlit (`frontend/`)
- **LLM**: Ollama (local-first), with optional cloud fallback (OpenAI, Anthropic, Google)
- **Vector DB**: Chroma (file-based, no server required)
- **Embeddings**: Sentence Transformers (local) / Ollama embeddings
- **Document Processing**: PyMuPDF (primary), Unstructured.io (fallback)
- **Database**: SQLite (local) / PostgreSQL (production)
- **Package Manager**: uv (backend Python), npm (frontend-nextjs)

## Directory Structure

```
backend/              # FastAPI backend
  app/
    api/              # API routes
    core/             # Core configurations
    services/         # Business logic (chat, RAG, file handling)
      rag/            # RAG components (document_processor, vector_store, retriever, embeddings)
    models/           # Data models
    mcp/              # MCP integration
    reasoning/        # Reasoning engines (mathematical, logical, causal, CoT, ToT)
    main.py           # FastAPI app entry
  alembic/            # Database migrations
  storage/            # File & vector DB storage
  pyproject.toml      # Python dependencies (managed with uv)
  uv.lock

frontend-nextjs/      # Next.js frontend (recommended)
  app/                # Next.js app router
  lib/                # Shared utilities
  package.json

frontend/             # Streamlit frontend (legacy)
mcp-servers/          # Custom MCP server implementations
docker/               # Docker Compose files
infrastructure/       # Terraform deployment
tests/                # Test suite
docs/                 # Project documentation
scripts/              # Utility scripts
```

## Development Setup

### Backend
```bash
cd backend
source .venv/bin/activate   # uv-managed venv
uv sync                     # Install dependencies
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Next.js)
```bash
cd frontend-nextjs
npm install
npm run dev                 # Runs on port 3000
```

### Frontend (Streamlit - legacy)
```bash
cd frontend
source venv/bin/activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Testing
```bash
cd backend
source .venv/bin/activate
python -m pytest ../tests/ -v
```

### Docker
```bash
docker-compose -f docker/docker-compose.yml up -d
```

## Git Workflow

### Commit Message Format
```
type: brief description
```
Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat: add Phase 4 multi-agent reasoning system`
- `fix: resolve streaming timeout in chat service`
- `docs: update RAG testing guide`

### Branch Strategy
- `main` - main branch
- Feature branches: `feature/description`
- Always create PRs for feature branches

## Coding Guidelines

- Always create tests for new features
- Update docs when adding features
- Provide meaningful error messages
- Use the correct venv for each component (backend vs frontend)
- Backend uses Python type hints and Pydantic models
- Frontend (Next.js) uses TypeScript strictly
- Follow existing code patterns in each directory

## Key APIs

- `POST /api/v1/chat/message` - Chat with MCP and RAG integration
- `GET /api/v1/conversations/{session_id}` - Conversation history
- `POST /api/v1/upload` - File upload for RAG processing
- `POST /api/v1/rag/documents` - Upload documents for RAG
- `GET /api/v1/rag/documents` - List processed documents
- `POST /api/v1/rag/query` - Direct RAG query

## Multi-Agent Reasoning System (Phase 4)

7 local agents: mathematical, logical, causal, cot, tot, prompt_engineering, general_reasoning. Uses local-first approach with A2A (Agent-to-Agent) fallback, confidence scoring, and result synthesis.
