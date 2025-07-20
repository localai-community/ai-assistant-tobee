# LocalAI Community Frontend

A Chainlit-based chat interface for the LocalAI Community backend with MCP and RAG capabilities.

## Features

- 🤖 **Interactive Chat Interface** - Beautiful Chainlit-based UI
- 📄 **File Upload Support** - Upload PDF, DOCX, TXT, MD files for RAG
- 🔗 **Backend Integration** - Seamless communication with FastAPI backend
- 🛠️ **MCP Tools** - Model Context Protocol integration
- 📊 **Real-time Responses** - Streaming chat responses
- 🎨 **Modern UI** - Clean, responsive design

## Prerequisites

- Python 3.11+
- LocalAI Community Backend running on `http://localhost:8000`
- Ollama running locally (for AI model access)
- At least one Ollama model installed (e.g., `ollama pull llama3.2`)

## Quick Start

### 1. Setup Environment

```bash
# Navigate to frontend directory
cd frontend

# Activate virtual environment (creates if not exists)
./activate_venv.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Backend First

```bash
# In another terminal, start the backend
cd backend
./start_server.sh
```

### 3. Start Frontend

```bash
# Start the frontend server
./start_frontend.sh

# Or manually:
chainlit run app.py --host 0.0.0.0 --port 8001
```

### 4. Access the Interface

Open your browser and go to:
- **Frontend**: `http://localhost:8001`
- **Backend API**: `http://localhost:8000`
- **Backend Docs**: `http://localhost:8000/docs`

## Usage

### Basic Chat
1. Type your message in the chat input
2. Press Enter or click Send
3. Get AI responses from your local Ollama model
4. Conversation history is maintained automatically
5. Available models are displayed on startup

### Document Upload
1. Click the file upload button
2. Select a supported file (PDF, DOCX, TXT, MD)
3. Wait for processing confirmation
4. Ask questions about your document

### MCP Tools
- Use file system operations
- Execute code safely
- Access system information

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
# Backend URL
BACKEND_URL=http://localhost:8000

# Chainlit settings
CHAINLIT_HOST=0.0.0.0
CHAINLIT_PORT=8001
```

### Chainlit Configuration

Edit `.chainlit/config.toml` to customize:
- UI theme and appearance
- File upload settings
- Security options
- Server configuration

## Development

### Project Structure
```
frontend/
├── app.py                 # Main Chainlit application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── .chainlit/
│   └── config.toml       # Chainlit configuration
├── start_frontend.sh     # Startup script
├── stop_frontend.sh      # Shutdown script
├── activate_venv.sh      # Environment activation
└── README.md             # This file
```

### Adding Features

1. **New Chat Handlers**: Add functions with `@cl.on_message`
2. **File Processing**: Extend `@cl.on_file_upload`
3. **UI Customization**: Modify `.chainlit/config.toml`
4. **Backend Integration**: Update API calls in `app.py`

### Testing

```bash
# Test frontend dependencies
python -c "import chainlit, httpx; print('✅ Dependencies OK')"

# Test backend connectivity
curl http://localhost:8000/health

# Test frontend chat API integration
python test_frontend_chat.py
```

## Troubleshooting

### Common Issues

**Frontend won't start:**
- Check if virtual environment is activated
- Verify dependencies are installed: `pip install -r requirements.txt`
- Ensure port 8001 is available

**Backend connection failed:**
- Verify backend is running: `curl http://localhost:8000/health`
- Check BACKEND_URL in environment variables
- Ensure no firewall blocking localhost

**File upload issues:**
- Check file size limits in `.chainlit/config.toml`
- Verify supported file types
- Ensure backend storage directory exists

### Logs

Check logs for detailed error information:
```bash
# Frontend logs
chainlit run app.py --host 0.0.0.0 --port 8001 --debug

# Backend logs
cd backend && uvicorn app.main:app --reload --log-level debug
```

## Docker

### Build and Run

```bash
# Build image
docker build -t localai-community-frontend .

# Run container
docker run -p 8001:8001 \
  -e BACKEND_URL=http://host.docker.internal:8000 \
  localai-community-frontend
```

### Docker Compose

Use the main `docker/docker-compose.yml` in the project root to run both frontend and backend together.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of LocalAI Community and follows the same license terms. 