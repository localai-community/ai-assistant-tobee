# LocalAI Community - Your Private AI Assistant

A **fully open source**, **local-first** AI assistant with MCP (Model Context Protocol) and RAG (Retrieval-Augmented Generation) support. Runs completely offline with no external dependencies required.

## 🎯 Our Vision

We believe AI should be **transparent, private, and truly yours**. This AI assistant embodies complete digital sovereignty - every conversation, every document, every AI interaction happens on your hardware. No cloud dependencies, no data sharing, no vendor lock-in. Just pure, powerful AI that respects your privacy and independence.

[📖 **Read our full vision and philosophy →**](docs/INTRODUCTION.md)

## 📋 Documentation

- **[📚 Documentation Hub](docs/README.md)** - Complete documentation index and guides
- **[🏠 Introduction](docs/INTRODUCTION.md)** - Local-first approach, benefits, and philosophy
- **[🏗️ Architecture Overview](docs/ARCHITECTURE.md)** - Complete technical specification
- **[📋 Implementation Plan](docs/IMPLEMENTATION_PLAN.md)** - Step-by-step development guide
- **[🍎 GPU Setup Guide](docs/GPU_SETUP.md)** - GPU acceleration for M1/M2 Macs
- **[🛠️ Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[📊 System Diagram](docs/architecture-diagram.mmd)** - Visual architecture representation

## 🚀 Quick Start

**Choose your setup based on your system:**

```bash
# 1. Clone and enter directory
git clone https://github.com/leiarenee/localai.community.git
cd localai.community

# 2. Run the startup script and choose your option
./start.sh
```

**The script will detect your system and recommend the best option:**

- **🍎 macOS M1/M2**: GPU acceleration (recommended)
- **🔒 Other platforms**: Cross-platform Docker setup
- **📋 System info**: Check your setup requirements

### 🛑 Stopping Services

```bash
# Run the startup script and choose "Stop Services"
./start.sh
```

**✅ No API keys required for local setup!**

## 🏗️ Key Features

### 🔒 **Local-First & Privacy**
- **100% Open Source**: All components are open source and self-hostable
- **Offline Capable**: No internet required after initial setup
- **Local LLM**: Ollama integration for complete independence
- **Local Embeddings**: Sentence Transformers for document analysis
- **Air-Gapped**: Can run in completely isolated environments
- **GDPR Compliant**: Your data never leaves your infrastructure

### 🤖 **AI Capabilities**
- **Frontend**: Chainlit - Purpose-built for conversational AI
- **Backend**: FastAPI with full MCP (Model Context Protocol) integration
- **RAG System**: Upload and analyze documents with vector search
- **Document Support**: PDF, DOCX, TXT, MD, HTML with intelligent chunking
- **Local Tools**: File operations, code execution, data analysis (no external APIs)

### ⚙️ **Technical Stack**
- **Vector Database**: Chroma (file-based, no server required)
- **Database**: SQLite (zero-config) or PostgreSQL
- **Deployment**: Docker-ready for local development and cloud production
- **Real-time**: WebSocket streaming with typing indicators
- **Authentication**: Built-in user management and session handling

**🎯 Perfect for: Privacy-conscious users, enterprises, air-gapped environments, and anyone wanting full control over their AI assistant.**

![Architecture Preview](docs/architecture-diagram.svg)