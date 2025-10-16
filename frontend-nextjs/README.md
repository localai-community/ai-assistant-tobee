# Next.js Frontend

A modern Next.js 15 frontend with React 19 for the LocalAI Community chat interface, featuring App Router, Server Components, and real-time streaming chat.

## Features

- 🤖 **Modern Chat Interface** - Built with Next.js 15 and React 19
- 📄 **File Upload Support** - Upload PDF, DOCX, TXT, MD files for RAG
- 🔗 **Backend Integration** - Seamless communication with FastAPI backend
- 🛠️ **MCP Tools** - Model Context Protocol integration
- 📊 **Real-time Responses** - Server-Sent Events (SSE) streaming
- 🎨 **Modern UI** - CSS Modules with dark mode support
- 📱 **Responsive Design** - Mobile, tablet, and desktop optimized
- ⚡ **Type Safety** - Full TypeScript support

## Prerequisites

- Node.js 18+ and npm
- LocalAI Community Backend running on `http://localhost:8000`
- Ollama running locally (for AI model access)

## Quick Start

### 1. Setup Environment

```bash
# Navigate to frontend-nextjs directory
cd frontend-nextjs

# Install dependencies
npm install
```

### 2. Start Backend First

```bash
# In another terminal, start the backend
cd ../backend
./start_server.sh
```

### 3. Start Frontend

```bash
# Start the Next.js development server
./start.sh

# Or manually:
npm run dev
```

### 4. Access the Interface

Open your browser and go to:
- **Next.js Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **Backend Docs**: `http://localhost:8000/docs`

## Usage

### Basic Chat
1. Type your message in the chat input
2. Press Enter or click Send
3. Get AI responses from your local Ollama model
4. Conversation history is maintained automatically

### Document Upload
1. Click the file upload button (📎)
2. Select a supported file (PDF, DOCX, TXT, MD)
3. Wait for processing confirmation
4. Ask questions about your document

### Settings
- Access settings via the sidebar
- Configure model selection, temperature, RAG options
- Toggle reasoning modes and context awareness
- Clear conversation history

## Configuration

### Environment Variables

Create a `.env.local` file in the frontend-nextjs directory:

```env
# Backend URL
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# App settings
NEXT_PUBLIC_APP_NAME=LocalAI Community
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Next.js Configuration

The app is configured with:
- TypeScript support
- CSS Modules for styling
- App Router (Next.js 13+)
- Server Components
- API routes for SSE proxying

## Development

### Project Structure

```
frontend-nextjs/
├── app/
│   ├── layout.tsx                 # Root layout
│   ├── page.tsx                   # Home page
│   ├── api/
│   │   └── chat/
│   │       └── stream/route.ts    # SSE endpoint
│   ├── components/
│   │   ├── ChatInterface.tsx      # Main chat component
│   │   ├── MessageList.tsx        # Message display
│   │   ├── ChatInput.tsx          # Input component
│   │   ├── Sidebar.tsx            # Settings sidebar
│   │   ├── FileUpload.tsx         # File upload
│   │   └── ModelSelector.tsx      # Model selection
│   └── styles/
│       └── globals.css            # Global styles
├── lib/
│   ├── api.ts                     # Backend API client
│   ├── types.ts                   # TypeScript types
│   └── hooks/
│       ├── useChat.ts             # Chat functionality with streaming
│       └── useSettings.ts         # User settings
├── package.json
├── tsconfig.json
├── next.config.js
└── README.md
```

### Key Features

1. **SSE Streaming**: Real-time chat responses via Server-Sent Events
2. **Type Safety**: Full TypeScript integration with backend schemas
3. **Responsive Design**: Mobile-first approach with CSS Modules
4. **State Management**: Custom hooks for chat, settings, and SSE
5. **File Upload**: Drag-and-drop file upload with validation
6. **Dark Mode**: CSS variables for theme switching

### Adding Features

1. **New Components**: Add to `app/components/` with CSS Modules
2. **API Integration**: Extend `lib/api.ts` for new endpoints
3. **State Management**: Create custom hooks in `lib/hooks/`
4. **Styling**: Use CSS variables and modules for consistency

## API Integration

The frontend communicates with the backend via:

- **REST API**: For CRUD operations (conversations, settings, documents)
- **SSE**: For real-time chat streaming
- **File Upload**: Multipart form data for document processing

### Key Endpoints

- `POST /api/chat/stream` - Chat streaming (proxied via Next.js API route)
- `GET /api/v1/conversations` - Get conversations
- `POST /api/v1/documents/upload` - Upload documents
- `GET /api/v1/models` - Get available models

## Testing

```bash
# Test frontend dependencies
npm run build

# Test backend connectivity
curl http://localhost:8000/health

# Run development server
npm run dev
```

## Deployment

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

### Docker

```bash
# Build Docker image
docker build -t localai-community-frontend .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_BACKEND_URL=http://host.docker.internal:8000 \
  localai-community-frontend
```

## Migration from Streamlit

This Next.js frontend provides feature parity with the existing Streamlit frontend:

- ✅ Real-time streaming chat
- ✅ File upload and document Q&A
- ✅ Model selection and configuration
- ✅ User settings persistence
- ✅ Conversation history
- ✅ Responsive design
- ✅ Dark mode support

### Benefits of Migration

- **Performance**: Better rendering and state management
- **Developer Experience**: Modern tooling and TypeScript
- **User Experience**: More responsive and native-feeling UI
- **Maintainability**: Industry-standard React patterns
- **Extensibility**: Easier to add new features

## Troubleshooting

### Common Issues

**Frontend won't start:**
- Check Node.js version (18+ required)
- Verify dependencies: `npm install`
- Ensure port 3000 is available

**Backend connection failed:**
- Verify backend is running: `curl http://localhost:8000/health`
- Check `NEXT_PUBLIC_BACKEND_URL` in environment variables
- Ensure no firewall blocking localhost

**SSE streaming issues:**
- Check browser console for errors
- Verify backend SSE endpoint is working
- Test with curl: `curl -N http://localhost:8000/api/v1/chat/stream`

**File upload problems:**
- Check file size limits (50MB default)
- Verify supported file types (PDF, DOCX, TXT, MD)
- Ensure backend storage directory exists

### Logs

Check browser developer tools for detailed error information:
- Network tab for API requests
- Console for JavaScript errors
- Application tab for local storage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of LocalAI Community and follows the same license terms.
