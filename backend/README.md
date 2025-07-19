# LocalAI Community Backend

A FastAPI-based backend for the LocalAI Community AI assistant with MCP and RAG capabilities.

## Features

- Direct Ollama API integration
- RAG (Retrieval-Augmented Generation) system
- MCP (Model Context Protocol) integration
- Document processing (PDF, DOCX, TXT, MD)
- Vector database storage
- File upload handling

## Setup

### Prerequisites

- Python 3.11+
- Ollama running locally (default: http://localhost:11434)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file (optional):
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the application:
```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build image
docker build -t localai-community-backend .

# Run container
docker run -p 8000:8000 localai-community-backend
```

## API Endpoints

### Core Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/v1/status` - API status

### Chat Endpoints
- `POST /api/v1/chat/` - Send message and get response
- `POST /api/v1/chat/stream` - Get streaming response
- `GET /api/v1/chat/models` - List available Ollama models
- `GET /api/v1/chat/health` - Chat service health check
- `GET /api/v1/chat/conversations` - List all conversations
- `GET /api/v1/chat/conversations/{id}` - Get specific conversation
- `DELETE /api/v1/chat/conversations/{id}` - Delete conversation
- `DELETE /api/v1/chat/conversations` - Clear all conversations

## Project Structure

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Configuration
│   ├── models/       # Database models
│   ├── services/     # Business logic
│   │   └── rag/      # RAG services
│   └── mcp/          # MCP integration
├── storage/
│   ├── uploads/      # File uploads
│   └── vector_db/    # Vector database
├── requirements.txt
├── Dockerfile
└── README.md
```

## Testing

### Chat Service Test
Test the chat functionality and Ollama integration:

```bash
# Test chat service and API
python test_chat.py

# Or run individual tests
python -c "from app.services.chat import ChatService; print('Chat service imported successfully')"
```

### Prerequisites for Testing
1. Start Ollama:
```bash
ollama serve
```

2. Pull a model:
```bash
ollama pull llama3.2
```

3. Start the backend:
```bash
./start_server.sh
```

## Configuration

Key configuration options in `app/core/config.py`:

- `ollama_base_url`: Ollama server URL (default: http://localhost:11434)
- `ollama_model`: Default model to use (default: llama3.2)
- `vector_db_path`: Vector database storage path
- `upload_dir`: File upload directory
- `max_file_size`: Maximum file upload size
- `allowed_file_types`: Supported file types 