# AI Assistant API Documentation

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Core API Endpoints](#core-api-endpoints)
  - [Root & Health Endpoints](#root--health-endpoints)
- [Chat Service](#chat-service-apiv1chat)
  - [POST / - Send Chat Message](#post----send-chat-message)
  - [POST /stream - Streaming Chat](#post-stream---streaming-chat)
  - [GET /models - Available Models](#get-models---available-models)
  - [GET /health - Chat Health](#get-health---chat-health)
  - [GET /conversations - List Conversations](#get-conversations---list-conversations)
  - [GET /conversations/{conversation_id} - Get Conversation](#get-conversationsconversation_id---get-conversation)
  - [DELETE /conversations/{conversation_id} - Delete Conversation](#delete-conversationsconversation_id---delete-conversation)
  - [DELETE /conversations - Clear All Conversations](#delete-conversations---clear-all-conversations)
  - [GET /tools - List MCP Tools](#get-tools---list-mcp-tools)
  - [POST /tools/{tool_name}/call - Call MCP Tool](#post-toolstool_namecall---call-mcp-tool)
  - [GET /tools/health - MCP Health](#get-toolshealth---mcp-health)
  - [GET /context/{conversation_id} - Get Conversation Context](#get-contextconversation_id---get-conversation-context)
  - [GET /context/user/{user_id} - Get User Context](#get-contextuseruser_id---get-user-context)
  - [POST /context/{conversation_id}/memory - Store Memory](#post-contextconversation_idmemory---store-memory)
- [RAG Service](#rag-service-apiv1rag)
  - [POST /stream - RAG Streaming Chat](#post-stream---rag-streaming-chat)
  - [POST /upload - Upload Document](#post-upload---upload-document)
  - [GET /documents/{conversation_id} - Get Conversation Documents](#get-documentsconversation_id---get-conversation-documents)
  - [DELETE /documents/{document_id} - Delete Document](#delete-documentsdocument_id---delete-document)
  - [POST /summarize/{document_id} - Summarize Document](#post-summarizedocument_id---summarize-document)
  - [POST /summarize/{document_id}/multi - Multi-Level Summary](#post-summarizedocument_idmulti---multi-level-summary)
  - [GET /document/{document_id}/summary - Get Document Summary](#get-documentdocument_idsummary---get-document-summary)
  - [GET /documents/analytics/{user_id} - Document Analytics](#get-documentsanalyticsuser_id---document-analytics)
  - [GET /documents/health - Document Health](#get-documentshealth---document-health)
  - [POST /documents/cleanup/{conversation_id} - Cleanup Documents](#post-documentscleanupconversation_id---cleanup-documents)
  - [POST /documents/archive/{document_id} - Archive Document](#post-documentsarchivedocument_id---archive-document)
  - [POST /documents/restore/{document_id} - Restore Document](#post-documentsrestoredocument_id---restore-document)
  - [POST /documents/cleanup-old - Cleanup Old Documents](#post-documentscleanup-old---cleanup-old-documents)
  - [POST /upload-directory - Upload Directory](#post-upload-directory---upload-directory)
  - [POST /search - Search Documents](#post-search---search-documents)
  - [POST /chat-with-rag - Chat with RAG Context](#post-chat-with-rag---chat-with-rag-context)
  - [GET /stats - RAG Statistics](#get-stats---rag-statistics)
  - [GET /health - RAG Health](#get-health---rag-health)
  - [DELETE /documents - Clear All Documents](#delete-documents---clear-all-documents)
  - [DELETE /documents/by-metadata - Delete by Metadata](#delete-documentsby-metadata---delete-by-metadata)
- [Advanced RAG Service](#advanced-rag-service-apiv1advanced-rag)
  - [POST /chat - Advanced RAG Chat](#post-chat---advanced-rag-chat)
  - [POST /stream - Advanced RAG Streaming](#post-stream---advanced-rag-streaming)
  - [POST /search - Advanced Document Search](#post-search---advanced-document-search)
  - [GET /strategies - Available Strategies](#get-strategies---available-strategies)
  - [GET /health - Advanced RAG Health](#get-health---advanced-rag-health)
- [Reasoning Service](#reasoning-service-reasoning)
  - [POST /parse-problem - Parse Problem Statement](#post-parse-problem---parse-problem-statement)
  - [POST /parse-steps - Parse Step Output](#post-parse-steps---parse-step-output)
  - [POST /validate - Validate Reasoning](#post-validate---validate-reasoning)
  - [POST /format - Format Reasoning](#post-format---format-reasoning)
  - [POST /test-workflow - Test Complete Workflow](#post-test-workflow---test-complete-workflow)
  - [GET /health - Reasoning Health](#get-health---reasoning-health)
  - [GET /available-formats - Available Formats](#get-available-formats---available-formats)
  - [GET /available-parsers - Available Parsers](#get-available-parsers---available-parsers)
- [Reasoning Chat Service](#reasoning-chat-service-apiv1reasoning-chat)
  - [POST / - Reasoning Chat](#post----reasoning-chat)
  - [POST /stream - Reasoning Chat Stream](#post-stream---reasoning-chat-stream)
  - [GET /health - Reasoning Chat Health](#get-health---reasoning-chat-health)
- [Phase 2 Reasoning Service](#phase-2-reasoning-service-apiv1phase2-reasoning)
  - [POST / - Phase 2 Reasoning Chat](#post----phase-2-reasoning-chat)
  - [POST /stream - Phase 2 Reasoning Stream](#post-stream---phase-2-reasoning-stream)
  - [GET /status - Phase 2 Status](#get-status---phase-2-status)
  - [GET /health - Phase 2 Health](#get-health---phase-2-health)
- [Phase 3 Reasoning Service](#phase-3-reasoning-service-apiv1phase3-reasoning)
  - [POST / - Phase 3 Reasoning Chat](#post----phase-3-reasoning-chat)
  - [POST /stream - Phase 3 Reasoning Stream](#post-stream---phase-3-reasoning-stream)
  - [GET /health - Phase 3 Health](#get-health---phase-3-health)
  - [GET /strategies - Phase 3 Strategies](#get-strategies---phase-3-strategies)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Quick Start Examples](#quick-start-examples)
- [Integration Notes](#integration-notes)

---

## Overview

This document provides comprehensive documentation for all available API endpoints in the AI Assistant project. The API is built with FastAPI and provides advanced chat, reasoning, and document processing capabilities.

## Base URL

- **Local Development**: `http://localhost:8000`
- **Production**: Configure based on deployment

## Authentication

Currently, the API does not require authentication for local development. In production, implement appropriate authentication mechanisms.

---

## **Core API Endpoints**

### **Root & Health Endpoints**

#### **GET /** - Root Endpoint
- **Purpose**: API root information
- **Response**: API version and status

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/"
```
</details>

**Example Response**:
```json
{
  "message": "LocalAI Community API",
  "version": "1.0.0",
  "status": "running"
}
```

#### **GET /health** - Health Check
- **Purpose**: System health status
- **Response**: Service health information

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/health"
```
</details>

**Example Response**:
```json
{
  "status": "healthy",
  "service": "localai-community-backend"
}
```

#### **GET /api/v1/status** - API Status
- **Purpose**: Detailed API status with feature flags
- **Response**: Available features and operational status

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/status"
```
</details>

**Example Response**:
```json
{
  "api_version": "v1",
  "status": "operational",
  "features": {
    "chat": "enabled",
    "rag": "enabled",
    "advanced_rag": "enabled",
    "mcp": "enabled",
    "reasoning": "enabled",
    "reasoning_chat": "enabled",
    "phase2_reasoning": "enabled",
    "phase3_reasoning": "enabled"
  }
}
```

---

## **Chat Service (`/api/v1/chat`)**

The Chat Service provides core conversational AI capabilities with Ollama integration, streaming responses, and MCP tool support.

### **POST /** - Send Chat Message
**Purpose**: Send a message and get AI response

**POST Parameters:**
```json
{
  "message": "string (required)",
  "model": "string (default: llama3:latest)",
  "temperature": "float (default: 0.7, range: 0.0-1.0)",
  "max_tokens": "integer (optional)",
  "conversation_id": "string (optional)",
  "user_id": "string (default: leia)",
  "k": "integer (optional - RAG documents to retrieve)",
  "filter_dict": "object (optional - RAG metadata filter)",
  "enable_context_awareness": "boolean (default: true)",
  "include_memory": "boolean (default: false)",
  "context_strategy": "string (default: conversation_only, options: auto, conversation_only, memory_only, hybrid)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain quantum computing in simple terms",
    "model": "llama3:latest",
    "temperature": 0.7,
    "conversation_id": "conv_123",
    "enable_context_awareness": true,
    "include_memory": false,
    "context_strategy": "conversation_only"
  }'
```
</details>

**Example Request:**
```json
{
  "message": "Explain quantum computing in simple terms",
  "model": "llama3:latest",
  "temperature": 0.7,
  "conversation_id": "conv_123",
  "enable_context_awareness": true
}
```

**Example Response:**
```json
{
  "response": "Quantum computing is a revolutionary approach to computation...",
  "model": "llama3:latest",
  "conversation_id": "conv_123",
  "user_id": "leia",
  "timestamp": "2024-01-15T10:30:00Z",
  "context_awareness_enabled": true,
  "context_strategy_used": "conversation_only"
}
```

### **POST /stream** - Streaming Chat
**Purpose**: Get streaming AI response
**Parameters**: Same as above
**Response**: Server-sent events stream

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me a story about space exploration",
    "model": "llama3:latest",
    "temperature": 0.8,
    "conversation_id": "conv_123"
  }'
```
</details>

### **GET /models** - Available Models
**Purpose**: List available Ollama models

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/chat/models"
```
</details>

**Example Response**:
```json
["llama3:latest", "codellama:latest", "mistral:latest"]
```

### **GET /health** - Chat Health
**Purpose**: Check chat service and Ollama availability

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/chat/health"
```
</details>

**Example Response**:
```json
{
  "status": "healthy",
  "ollama_available": true,
  "available_models": ["llama3:latest"],
  "conversation_count": 5
}
```

### **GET /conversations** - List Conversations
**Purpose**: Get all conversations

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/chat/conversations"
```
</details>

**Example Response**:
```json
[
  {
    "id": "conv_123",
    "title": "Quantum Computing Discussion",
    "model": "llama3:latest",
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### **GET /conversations/{conversation_id}** - Get Conversation
**Purpose**: Get specific conversation by ID
**Path Parameters**:
- `conversation_id`: string (required) - Unique conversation identifier

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/chat/conversations/conv_123"
```
</details>

### **DELETE /conversations/{conversation_id}** - Delete Conversation
**Purpose**: Delete specific conversation
**Path Parameters**:
- `conversation_id`: string (required) - Unique conversation identifier

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X DELETE "http://localhost:8000/api/v1/chat/conversations/conv_123"
```
</details>

### **DELETE /conversations** - Clear All Conversations
**Purpose**: Clear all conversations

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X DELETE "http://localhost:8000/api/v1/chat/conversations"
```
</details>

**Example Response**:
```json
{
  "message": "Cleared 5 conversations successfully",
  "deleted_count": 5
}
```

### **GET /tools** - List MCP Tools
**Purpose**: List available MCP tools

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/chat/tools"
```
</details>

**Example Response**:
```json
[
  {
    "name": "filesystem.read_file",
    "description": "Read contents of a file",
    "input_schema": {...}
  }
]
```

### **POST /tools/{tool_name}/call** - Call MCP Tool
**Purpose**: Execute specific MCP tool
**Path Parameters**:
- `tool_name`: string (required) - Tool name in format "server.tool"

**POST Parameters:**
```json
{
  "arguments": "object (required - tool-specific arguments)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/chat/tools/filesystem.read_file/call" \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "path": "/path/to/file.txt"
    }
  }'
```
</details>

### **GET /tools/health** - MCP Health
**Purpose**: Check MCP tools health

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/chat/tools/health"
```
</details>

**Example Response**:
```json
{
  "mcp_enabled": true,
  "servers": {
    "filesystem": {"status": "healthy"},
    "code-execution": {"status": "healthy"}
  },
  "tools_count": 8,
  "overall_healthy": true
}
```

### **GET /context/{conversation_id}** - Get Conversation Context
**Purpose**: Get comprehensive context for conversation
**Path Parameters**:
- `conversation_id`: string (required) - Conversation identifier

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/chat/context/conv_123"
```
</details>

### **GET /context/user/{user_id}** - Get User Context
**Purpose**: Get user context across conversations
**Path Parameters**:
- `user_id`: string (required) - User identifier

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/chat/context/user/leia"
```
</details>

### **POST /context/{conversation_id}/memory** - Store Memory
**Purpose**: Store conversation as memory chunks
**Path Parameters**:
- `conversation_id`: string (required) - Conversation identifier

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/chat/context/conv_123/memory"
```
</details>

---

## **RAG Service (`/api/v1/rag`)**

The RAG (Retrieval-Augmented Generation) Service provides document processing, vector search, and context-enhanced responses.

### **POST /stream** - RAG Streaming Chat
**Purpose**: Stream RAG-enhanced chat response
**POST Parameters:**
```json
{
  "message": "string (required)",
  "model": "string (default: llama3:latest)",
  "temperature": "float (default: 0.7)",
  "conversation_id": "string (optional)",
  "k": "integer (default: 4 - documents to retrieve)",
  "filter_dict": "object (optional - metadata filter)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/rag/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Summarize the key findings from the uploaded documents",
    "model": "llama3:latest",
    "temperature": 0.7,
    "conversation_id": "conv_123",
    "k": 5
  }'
```
</details>

### **POST /upload** - Upload Document
**Purpose**: Upload and process document for RAG
**Content-Type**: `multipart/form-data`

**POST Parameters**:
- `file`: File (required) - Supported formats: .pdf, .docx, .txt, .md, .doc
- `conversation_id`: string (optional) - Associate with conversation
- `user_id`: string (optional) - Document owner

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/rag/upload" \
  -F "file=@/path/to/document.pdf" \
  -F "conversation_id=conv_123" \
  -F "user_id=leia"
```
</details>

**Example Response:**
```json
{
  "success": true,
  "document_id": "doc_123",
  "filename": "research_paper.pdf",
  "file_size": 1024000,
  "conversation_id": "conv_123",
  "chunks_created": 45,
  "message": "Document 'research_paper.pdf' processed successfully"
}
```

### **GET /documents/{conversation_id}** - Get Conversation Documents
**Purpose**: Get all documents for specific conversation
**Path Parameters**:
- `conversation_id`: string (required) - Conversation identifier

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/rag/documents/conv_123"
```
</details>

### **DELETE /documents/{document_id}** - Delete Document
**Purpose**: Delete document from system
**Path Parameters**:
- `document_id`: string (required) - Document identifier

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X DELETE "http://localhost:8000/api/v1/rag/documents/doc_123"
```
</details>

### **POST /summarize/{document_id}** - Summarize Document
**Purpose**: Generate document summary
**Path Parameters**:
- `document_id`: string (required) - Document identifier

**POST Parameters:**
```json
{
  "summary_type": "string (default: brief, options: brief, detailed, key_points, executive)",
  "conversation_context": "string (optional)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/rag/summarize/doc_123" \
  -H "Content-Type: application/json" \
  -d '{
    "summary_type": "detailed",
    "conversation_context": "Research paper analysis"
  }'
```
</details>

### **POST /summarize/{document_id}/multi** - Multi-Level Summary
**Purpose**: Generate multiple summary types
**Path Parameters**:
- `document_id`: string (required) - Document identifier

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/rag/summarize/doc_123/multi"
```
</details>

### **GET /document/{document_id}/summary** - Get Document Summary
**Purpose**: Get existing document summary
**Path Parameters**:
- `document_id`: string (required) - Document identifier

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/rag/document/doc_123/summary"
```
</details>

### **GET /documents/analytics/{user_id}** - Document Analytics
**Purpose**: Get document usage analytics
**Path Parameters**:
- `user_id`: string (required) - User identifier

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/rag/documents/analytics/leia"
```
</details>

### **GET /documents/health** - Document Health
**Purpose**: Get document system health

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/rag/documents/health"
```
</details>

### **POST /documents/cleanup/{conversation_id}** - Cleanup Documents
**Purpose**: Clean up conversation documents
**Path Parameters**:
- `conversation_id`: string (required) - Conversation identifier

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/rag/documents/cleanup/conv_123"
```
</details>

### **POST /documents/archive/{document_id}** - Archive Document
**Purpose**: Archive document for long-term storage
**Path Parameters**:
- `document_id`: string (required) - Document identifier

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/rag/documents/archive/doc_123"
```
</details>

### **POST /documents/restore/{document_id}** - Restore Document
**Purpose**: Restore archived document
**Path Parameters**:
- `document_id`: string (required) - Document identifier

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/rag/documents/restore/doc_123"
```
</details>

### **POST /documents/cleanup-old** - Cleanup Old Documents
**Purpose**: Clean up old documents
**POST Parameters:**
```json
{
  "days_old": "integer (default: 30)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/rag/documents/cleanup-old" \
  -H "Content-Type: application/json" \
  -d '{
    "days_old": 30
  }'
```
</details>

### **POST /upload-directory** - Upload Directory
**Purpose**: Process all documents in directory
**POST Parameters:**
```json
{
  "directory_path": "string (required)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/rag/upload-directory" \
  -F "directory_path=/path/to/documents"
```
</details>

### **POST /search** - Search Documents
**Purpose**: Search documents in RAG system
**POST Parameters:**
```json
{
  "query": "string (required)",
  "k": "integer (default: 10)",
  "filter_dict": "object (optional)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/rag/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning algorithms",
    "k": 10
  }'
```
</details>

### **POST /chat-with-rag** - Chat with RAG Context
**Purpose**: Get RAG-enhanced context for message
**POST Parameters:**
```json
{
  "message": "string (required)",
  "k": "integer (default: 4)",
  "filter_dict": "object (optional)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/rag/chat-with-rag" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the key findings in the research papers?",
    "k": 5
  }'
```
</details>

### **GET /stats** - RAG Statistics
**Purpose**: Get RAG system statistics

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/rag/stats"
```
</details>

### **GET /health** - RAG Health
**Purpose**: Check RAG system health

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/rag/health"
```
</details>

### **DELETE /documents** - Clear All Documents
**Purpose**: Clear all documents from RAG system

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X DELETE "http://localhost:8000/api/v1/rag/documents"
```
</details>

### **DELETE /documents/by-metadata** - Delete by Metadata
**Purpose**: Delete documents by metadata filter
**POST Parameters:**
```json
{
  "metadata_filter": "object (required)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X DELETE "http://localhost:8000/api/v1/rag/documents/by-metadata" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata_filter": {
      "conversation_id": "conv_123"
    }
  }'
```
</details>

---

## **Advanced RAG Service (`/api/v1/advanced-rag`)**

The Advanced RAG Service provides sophisticated retrieval strategies and multi-strategy document search.

### **POST /chat** - Advanced RAG Chat
**Purpose**: Advanced RAG with multiple retrieval strategies
**POST Parameters:**
```json
{
  "message": "string (required)",
  "model": "string (default: llama3:latest)",
  "temperature": "float (default: 0.7)",
  "conversation_id": "string (optional)",
  "conversation_history": "array (optional)",
  "k": "integer (default: 4)",
  "use_advanced_strategies": "boolean (default: true)"
}
```

**Example Response:**
```json
{
  "success": true,
  "response": "Based on the retrieved documents...",
  "conversation_id": "conv_123",
  "has_context": true,
  "strategies_used": ["dense", "sparse", "contextual"],
  "results_count": 8,
  "results": [...]
}
```

### **POST /stream** - Advanced RAG Streaming
**Purpose**: Stream advanced RAG response
**Parameters**: Same as above

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/advanced-rag/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Compare different machine learning approaches",
    "use_advanced_strategies": true,
    "k": 8
  }'
```
</details>

### **POST /search** - Advanced Document Search
**Purpose**: Search using advanced retrieval strategies
**POST Parameters:**
```json
{
  "query": "string (required)",
  "conversation_history": "array (optional)",
  "k": "integer (default: 10)",
  "use_advanced_strategies": "boolean (default: true)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/advanced-rag/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "neural network architectures",
    "k": 15,
    "use_advanced_strategies": true
  }'
```
</details>

### **GET /strategies** - Available Strategies
**Purpose**: Get information about retrieval strategies

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/advanced-rag/strategies"
```
</details>

**Example Response:**
```json
{
  "success": true,
  "strategies": {
    "dense": {
      "name": "Dense Vector Similarity",
      "description": "Traditional embedding-based similarity search",
      "strengths": ["Semantic understanding", "Fast retrieval"],
      "weaknesses": ["May miss exact keyword matches"]
    },
    "sparse": {
      "name": "Sparse TF-IDF Retrieval",
      "description": "Keyword-based retrieval using TF-IDF",
      "strengths": ["Exact keyword matching"],
      "weaknesses": ["No semantic understanding"]
    }
  }
}
```

### **GET /health** - Advanced RAG Health
**Purpose**: Health check for advanced RAG system

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/advanced-rag/health"
```
</details>

---

## **Reasoning Service (`/reasoning`)**

The Reasoning Service provides structured problem analysis, step-by-step reasoning, and validation capabilities.

### **POST /parse-problem** - Parse Problem Statement
**Purpose**: Parse and analyze problem statement
**POST Parameters:**
```json
{
  "problem_statement": "string (required)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/reasoning/parse-problem" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_statement": "Solve the equation 2x + 3 = 7"
  }'
```
</details>

**Example Request:**
```json
{
  "problem_statement": "Solve the equation 2x + 3 = 7"
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "problem_type": "mathematical",
    "variables": ["x"],
    "operations": ["addition", "multiplication", "equality"],
    "complexity": "simple"
  },
  "warnings": []
}
```

### **POST /parse-steps** - Parse Step Output
**Purpose**: Parse step-by-step reasoning output
**POST Parameters:**
```json
{
  "step_output": "string (required)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/reasoning/parse-steps" \
  -H "Content-Type: application/json" \
  -d '{
    "step_output": "Step 1: Identify the equation\nStep 2: Isolate the variable\nStep 3: Solve"
  }'
```
</details>

### **POST /validate** - Validate Reasoning
**Purpose**: Validate reasoning input, steps, and result
**POST Parameters:**
```json
{
  "problem_statement": "string (required)",
  "steps": [
    {
      "description": "string",
      "reasoning": "string",
      "confidence": "float"
    }
  ],
  "final_answer": "any (optional)",
  "confidence": "float (default: 0.0)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/reasoning/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_statement": "Solve 2x + 3 = 7",
    "steps": [
      {
        "description": "Subtract 3 from both sides",
        "reasoning": "To isolate the term with x",
        "confidence": 0.9
      }
    ],
    "final_answer": "x = 2",
    "confidence": 0.95
  }'
```
</details>

### **POST /format** - Format Reasoning
**Purpose**: Format reasoning result in specified format
**POST Parameters:**
```json
{
  "problem_statement": "string (required)",
  "steps": "array (required)",
  "final_answer": "any (optional)",
  "confidence": "float (default: 0.0)",
  "format_type": "string (default: json, options: json, text, markdown, html, structured)",
  "include_metadata": "boolean (default: true)",
  "include_validation": "boolean (default: true)",
  "include_timestamps": "boolean (default: true)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/reasoning/format" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_statement": "Solve 2x + 3 = 7",
    "steps": [
      {
        "description": "Subtract 3 from both sides",
        "reasoning": "To isolate the term with x",
        "confidence": 0.9
      }
    ],
    "final_answer": "x = 2",
    "format_type": "markdown",
    "include_metadata": true
  }'
```
</details>

### **POST /test-workflow** - Test Complete Workflow
**Purpose**: Test complete reasoning workflow
**POST Parameters:**
```json
{
  "problem_statement": "string (required)",
  "format_type": "string (default: json)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/reasoning/test-workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_statement": "What is the capital of France?",
    "format_type": "markdown"
  }'
```
</details>

### **GET /health** - Reasoning Health
**Purpose**: Health check for reasoning system

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/reasoning/health"
```
</details>

### **GET /available-formats** - Available Formats
**Purpose**: Get list of available output formats

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/reasoning/available-formats"
```
</details>

### **GET /available-parsers** - Available Parsers
**Purpose**: Get list of available parsers

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/reasoning/available-parsers"
```
</details>

---

## **Reasoning Chat Service (`/api/v1/reasoning-chat`)**

The Reasoning Chat Service integrates structured reasoning with conversational AI.

### **POST /** - Reasoning Chat
**Purpose**: Chat with step-by-step reasoning
**POST Parameters:**
```json
{
  "message": "string (required)",
  "model": "string (default: llama3:latest)",
  "temperature": "float (default: 0.7)",
  "max_tokens": "integer (optional)",
  "conversation_id": "string (optional)",
  "user_id": "string (default: leia)",
  "k": "integer (optional)",
  "filter_dict": "object (optional)",
  "use_reasoning": "boolean (default: true)",
  "show_steps": "boolean (default: true)",
  "output_format": "string (default: markdown)",
  "include_validation": "boolean (default: true)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/reasoning-chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Solve 2x + 3 = 7",
    "use_reasoning": true,
    "show_steps": true,
    "output_format": "markdown",
    "include_validation": true
  }'
```
</details>

**Example Response:**
```json
{
  "response": "## Step-by-Step Reasoning\n\n**Step 1:** Isolate the variable...",
  "conversation_id": "conv_123",
  "reasoning_result": {...},
  "steps_count": 3,
  "validation_summary": {...},
  "reasoning_used": true
}
```

### **POST /stream** - Reasoning Chat Stream
**Purpose**: Stream reasoning-enhanced response
**Parameters**: Same as above

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/reasoning-chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain the steps to solve 3x - 5 = 10",
    "use_reasoning": true,
    "show_steps": true
  }'
```
</details>

### **GET /health** - Reasoning Chat Health
**Purpose**: Health check for reasoning chat service

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/reasoning-chat/health"
```
</details>

---

## **Phase 2 Reasoning Service (`/api/v1/phase2-reasoning`)**

The Phase 2 Reasoning Service provides specialized reasoning engines for different problem types.

### **POST /** - Phase 2 Reasoning Chat
**Purpose**: Chat using specialized reasoning engines
**POST Parameters:**
```json
{
  "message": "string (required)",
  "model": "string (default: llama3:latest)",
  "temperature": "float (default: 0.7)",
  "max_tokens": "integer (optional)",
  "conversation_id": "string (optional)",
  "user_id": "string (default: leia)",
  "k": "integer (optional)",
  "filter_dict": "object (optional)",
  "use_phase2_reasoning": "boolean (default: true)",
  "engine_type": "string (default: auto, options: auto, mathematical, logical, causal)",
  "show_steps": "boolean (default: true)",
  "output_format": "string (default: markdown)",
  "include_validation": "boolean (default: true)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/phase2-reasoning/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "If all A are B and all B are C, then all A are C. Is this valid?",
    "engine_type": "logical",
    "show_steps": true,
    "include_validation": true
  }'
```
</details>

**Example Response:**
```json
{
  "response": "Using mathematical reasoning engine...",
  "model": "llama3:latest",
  "conversation_id": "conv_123",
  "engine_used": "mathematical",
  "reasoning_type": "mathematical",
  "steps_count": 4,
  "confidence": 0.95,
  "validation_summary": "Validated"
}
```

### **POST /stream** - Phase 2 Reasoning Stream
**Purpose**: Stream Phase 2 reasoning response
**Parameters**: Same as above

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/phase2-reasoning/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze the logical validity of: All birds can fly. Penguins are birds. Therefore, penguins can fly.",
    "engine_type": "logical",
    "show_steps": true
  }'
```
</details>

### **GET /status** - Phase 2 Status
**Purpose**: Get status of Phase 2 reasoning engines

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/phase2-reasoning/status"
```
</details>

### **GET /health** - Phase 2 Health
**Purpose**: Health check for Phase 2 reasoning engines

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/phase2-reasoning/health"
```
</details>

---

## **Phase 3 Reasoning Service (`/api/v1/phase3-reasoning`)**

The Phase 3 Reasoning Service provides advanced reasoning strategies like Chain-of-Thought and Tree-of-Thoughts.

### **POST /** - Phase 3 Reasoning Chat
**Purpose**: Chat using advanced reasoning strategies
**POST Parameters:**
```json
{
  "message": "string (required)",
  "model": "string (default: llama3:latest)",
  "temperature": "float (default: 0.7)",
  "max_tokens": "integer (optional)",
  "conversation_id": "string (optional)",
  "user_id": "string (default: leia)",
  "k": "integer (optional)",
  "filter_dict": "object (optional)",
  "use_phase3_reasoning": "boolean (default: true)",
  "strategy_type": "string (default: auto, options: auto, chain_of_thought, tree_of_thoughts, prompt_engineering)",
  "show_steps": "boolean (default: true)",
  "output_format": "string (default: markdown)",
  "include_validation": "boolean (default: true)"
}
```

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/phase3-reasoning/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Design a scalable microservices architecture for an e-commerce platform",
    "strategy_type": "tree_of_thoughts",
    "show_steps": true,
    "include_validation": true
  }'
```
</details>

**Example Response:**
```json
{
  "response": "Using Chain-of-Thought strategy...",
  "model": "llama3:latest",
  "conversation_id": "conv_123",
  "strategy_used": "chain_of_thought",
  "reasoning_type": "advanced",
  "steps_count": 5,
  "confidence": 0.88,
  "validation_summary": "Validated"
}
```

### **POST /stream** - Phase 3 Reasoning Stream
**Purpose**: Stream Phase 3 reasoning response
**Parameters**: Same as above

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/phase3-reasoning/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Design a distributed system architecture for handling 1 million concurrent users",
    "strategy_type": "tree_of_thoughts",
    "show_steps": true
  }'
```
</details>

### **GET /health** - Phase 3 Health
**Purpose**: Health check for Phase 3 reasoning strategies

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/phase3-reasoning/health"
```
</details>

### **GET /strategies** - Phase 3 Strategies
**Purpose**: Get available Phase 3 strategies

<details>
<summary><strong>📋 cURL Command</strong></summary>

```bash
curl -X GET "http://localhost:8000/api/v1/phase3-reasoning/strategies"
```
</details>

---

## **Error Handling**

All endpoints return appropriate HTTP status codes and error messages:

- **200**: Success
- **400**: Bad Request (invalid parameters)
- **404**: Not Found (resource doesn't exist)
- **500**: Internal Server Error
- **503**: Service Unavailable (Ollama not running)

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## **Rate Limiting**

Currently, no rate limiting is implemented. Consider implementing rate limiting for production deployments.

---

## **Quick Start Examples**

<details>
<summary><strong>🚀 Basic Chat Example</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?",
    "model": "llama3:latest",
    "temperature": 0.7
  }'
```
</details>

<details>
<summary><strong>📄 Document Upload Example</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/rag/upload" \
  -F "file=@document.pdf" \
  -F "conversation_id=conv_123"
```
</details>

<details>
<summary><strong>🔍 RAG-Enhanced Chat Example</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/rag/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Summarize the uploaded document",
    "k": 5,
    "conversation_id": "conv_123"
  }'
```
</details>

<details>
<summary><strong>🧠 Reasoning Chat Example</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/reasoning-chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Solve 2x + 3 = 7",
    "use_reasoning": true,
    "show_steps": true
  }'
```
</details>

<details>
<summary><strong>⚡ Advanced RAG Example</strong></summary>

```bash
curl -X POST "http://localhost:8000/api/v1/advanced-rag/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Compare different approaches to machine learning",
    "use_advanced_strategies": true,
    "k": 8
  }'
```
</details>

---

## **Integration Notes**

### **Ollama Requirements**
- Ollama must be running on `http://localhost:11434` (configurable via `OLLAMA_URL` environment variable)
- Required models should be pulled using `ollama pull model_name`

### **Database Requirements**
- SQLite database is used by default
- Database is automatically initialized on startup
- All conversation and message data is persisted

### **MCP Integration**
- MCP (Model Context Protocol) tools are automatically loaded from configuration
- Tools provide filesystem access, code execution, and other capabilities
- Tool health is monitored and reported

### **Vector Storage**
- ChromaDB is used for vector storage
- Documents are automatically chunked and embedded
- Conversation-scoped collections are supported

---

This API provides a comprehensive foundation for building advanced AI applications with reasoning, document processing, and conversational capabilities.
