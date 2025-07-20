# RAG Testing Guide

This guide explains how to test the RAG (Retrieval-Augmented Generation) functionality in the LocalAI Community UI.

## 🚀 Quick Start

### Prerequisites
1. **Backend Running**: Make sure the backend server is running on `http://localhost:8000`
2. **Frontend Running**: Make sure the frontend is running on `http://localhost:8501`
3. **Ollama Running**: Ensure Ollama is running with at least one model installed

### Step 1: Access the UI
Open your browser and go to: `http://localhost:8501`

## 📚 Testing RAG Functionality

### 1. Upload Documents

#### Using the UI
1. **Navigate to the sidebar** - Look for the "📚 RAG Document Upload" section
2. **Upload a document** - Click "Browse files" and select a supported file:
   - PDF files (`.pdf`)
   - Word documents (`.docx`)
   - Text files (`.txt`)
   - Markdown files (`.md`)
3. **Process the document** - Click "📤 Process Document"
4. **Wait for processing** - You'll see a spinner and then success/error messages

#### Test Document
We've provided a test document: `test_document.txt` in the project root. You can use this to test RAG functionality.

#### Expected Results
- ✅ Success message: "Document processed successfully"
- 📊 Statistics: Number of chunks created
- 📈 Updated RAG statistics in the sidebar

### 2. Enable RAG Mode

1. **Find RAG Mode section** - In the sidebar, look for "🔍 RAG Mode"
2. **Enable RAG** - Check the "Enable RAG for responses" checkbox
3. **Verify status** - You should see "✅ RAG mode enabled - responses will use document context"

### 3. Test RAG Responses

#### Basic Questions
Try asking questions about your uploaded documents:

**Example questions for the test document:**
- "What is the LocalAI Community project?"
- "What are the key features of this system?"
- "How does the RAG system work?"
- "What models does it support?"
- "What is the technical architecture?"

#### Expected Behavior
- **With RAG enabled**: Responses will include information from your uploaded documents
- **RAG Context display**: You'll see an orange box showing the retrieved context
- **More accurate responses**: Answers will be specific to your documents

#### Without RAG
- **With RAG disabled**: Responses will use only the model's pre-trained knowledge
- **No context box**: No orange context display
- **Generic responses**: May not be specific to your documents

### 4. Monitor RAG Statistics

In the sidebar, you can monitor:

- **Total Documents**: Number of uploaded documents
- **Total Chunks**: Number of text chunks created
- **Vector DB Size**: Size of the vector database in MB

## 🔍 Advanced Testing

### Testing Different File Types

#### PDF Documents
1. Upload a PDF file
2. Ask questions about the PDF content
3. Verify responses reference the PDF information

#### Word Documents (.docx)
1. Upload a Word document
2. Test with complex formatting
3. Check if tables and structured content are preserved

#### Text Files
1. Upload plain text files
2. Test with large documents
3. Verify chunking works correctly

#### Markdown Files
1. Upload markdown files
2. Test with formatted text
3. Check if markdown formatting is handled

### Testing RAG Performance

#### Multiple Documents
1. Upload several documents
2. Ask questions that span multiple documents
3. Verify the system retrieves from all relevant documents

#### Large Documents
1. Upload large documents (10+ pages)
2. Test response time
3. Verify all content is accessible

#### Specific Queries
1. Ask very specific questions
2. Test semantic search accuracy
3. Verify context relevance

## 🐛 Troubleshooting

### Common Issues

#### "Backend not available for document upload"
- **Solution**: Make sure the backend server is running on port 8000
- **Check**: Run `curl http://localhost:8000/health`

#### "Upload failed" errors
- **Check file type**: Ensure it's PDF, DOCX, TXT, or MD
- **Check file size**: Very large files may timeout
- **Check backend logs**: Look for processing errors

#### "No relevant documents found"
- **Check RAG mode**: Make sure RAG is enabled
- **Check documents**: Verify documents were uploaded successfully
- **Try different queries**: Some queries may not match document content

#### "RAG error" responses
- **Check backend health**: Verify all services are running
- **Check vector database**: Ensure ChromaDB is working
- **Restart services**: Try restarting backend and frontend

### Debugging Steps

1. **Check Backend Health**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check RAG Health**
   ```bash
   curl http://localhost:8000/api/v1/rag/health
   ```

3. **Check RAG Statistics**
   ```bash
   curl http://localhost:8000/api/v1/rag/stats
   ```

4. **Check Backend Logs**
   ```bash
   tail -f backend/logs/app.log
   ```

## 📊 Expected Results

### Successful RAG Test

When RAG is working correctly, you should see:

1. **Document Upload**
   - ✅ Success message
   - 📊 Chunks created
   - 📈 Updated statistics

2. **RAG Mode**
   - ✅ RAG mode enabled
   - 📚 Documents loaded indicator

3. **Responses**
   - 📚 Orange context box with retrieved information
   - 🎯 Accurate, document-specific answers
   - ⚡ Reasonable response times

### Performance Benchmarks

- **Document Processing**: 1-5 seconds per document
- **RAG Response Time**: 2-10 seconds (depending on model)
- **Context Retrieval**: <1 second
- **Vector Search**: <100ms

## 🎯 Test Scenarios

### Scenario 1: Basic RAG Test
1. Upload `test_document.txt`
2. Enable RAG mode
3. Ask: "What is the LocalAI Community project?"
4. Verify response includes project information

### Scenario 2: Multi-Document Test
1. Upload multiple documents
2. Ask questions spanning multiple documents
3. Verify responses combine information from all sources

### Scenario 3: Specific Query Test
1. Upload technical documentation
2. Ask very specific technical questions
3. Verify accurate, detailed responses

### Scenario 4: Performance Test
1. Upload large documents
2. Ask multiple questions rapidly
3. Verify consistent performance

## 🔧 Advanced Features

### Custom RAG Parameters
The RAG system supports custom parameters:
- **k**: Number of relevant chunks to retrieve (default: 4)
- **Filtering**: Metadata-based document filtering
- **Chunk size**: Configurable text chunking

### RAG API Endpoints
You can also test RAG directly via API:

```bash
# Upload document
curl -X POST -F "file=@test_document.txt" http://localhost:8000/api/v1/rag/upload

# Get RAG context
curl -X POST -F "message=What is this project about?" http://localhost:8000/api/v1/rag/chat-with-rag

# Get statistics
curl http://localhost:8000/api/v1/rag/stats
```

## 📝 Notes

- **Document Processing**: Documents are processed into semantic chunks for better retrieval
- **Vector Storage**: Uses ChromaDB for efficient similarity search
- **Embeddings**: Uses sentence-transformers for high-quality embeddings
- **Context Window**: Limited by the LLM's context window size
- **Privacy**: All processing happens locally, no data leaves your machine

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs**: Look at backend and frontend logs
2. **Verify services**: Ensure all components are running
3. **Test API directly**: Use curl commands to test backend endpoints
4. **Check documentation**: Review the main documentation
5. **Report issues**: Create an issue on the project repository

---

**Happy RAG Testing! 🚀** 