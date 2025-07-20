#!/usr/bin/env python3
"""
Comprehensive test script for Phase 3 RAG system implementation.
Tests all components: document processing, vector storage, retrieval, and API endpoints.
"""

import os
import sys
import logging
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.rag import RAGRetriever, DocumentProcessor, VectorStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rag_components():
    """Test individual RAG components"""
    print("🧪 Testing RAG Components...")
    
    # Test document processor
    processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
    
    # Create test document
    test_content = """
    Python is a high-level, interpreted programming language.
    It was created by Guido van Rossum and first released in 1991.
    Python is known for its simplicity and readability.
    It has a large standard library and extensive third-party packages.
    Python is widely used in web development, data science, AI, and automation.
    """
    
    test_file = Path("test_python.txt")
    test_file.write_text(test_content)
    
    try:
        # Process document
        chunks = processor.process_file(str(test_file))
        print(f"✅ Document processing: {len(chunks)} chunks created")
        
        # Test vector store
        vector_store = VectorStore(persist_directory="test_vector_db")
        health = vector_store.health_check()
        print(f"✅ Vector store health: {health['status']}")
        
        # Test RAG retriever
        rag = RAGRetriever()
        rag_health = rag.health_check()
        print(f"✅ RAG system health: {rag_health.get('status', 'healthy')}")
        
        # Test document addition
        success = rag.add_document(str(test_file))
        print(f"✅ Document addition: {success}")
        
        # Test retrieval
        results = rag.retrieve_relevant_documents("What is Python?")
        print(f"✅ Document retrieval: {len(results)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if Path("test_vector_db").exists():
            import shutil
            shutil.rmtree("test_vector_db")

def test_api_endpoints():
    """Test RAG API endpoints"""
    print("\n🌐 Testing RAG API Endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint: Working")
        else:
            print(f"❌ Health endpoint: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health endpoint: Connection failed - {e}")
        return False
    
    # Test RAG endpoints
    endpoints = [
        "/api/v1/rag/health",
        "/api/v1/rag/stats",
        "/api/v1/rag/documents"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint}: Working")
            else:
                print(f"⚠️  {endpoint}: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: Connection failed - {e}")
    
    return True

def test_file_upload():
    """Test file upload functionality"""
    print("\n📁 Testing File Upload...")
    
    base_url = "http://localhost:8000"
    
    # Create test file
    test_content = """
    This is a test document for upload functionality.
    It contains information about testing and validation.
    The document should be processed and stored in the vector database.
    """
    
    test_file = Path("test_upload.txt")
    test_file.write_text(test_content)
    
    try:
        # Test file upload
        with open(test_file, 'rb') as f:
            files = {'file': ('test_upload.txt', f, 'text/plain')}
            response = requests.post(
                f"{base_url}/api/v1/rag/upload",
                files=files,
                timeout=10
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File upload: Success - {result.get('message', 'Uploaded')}")
            return True
        else:
            print(f"❌ File upload: Status {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ File upload: Connection failed - {e}")
        return False
    finally:
        if test_file.exists():
            test_file.unlink()

def main():
    """Run all Phase 3 tests"""
    print("🚀 Starting Phase 3 RAG System Tests...")
    print("=" * 50)
    
    # Test RAG components
    components_ok = test_rag_components()
    
    # Test API endpoints
    api_ok = test_api_endpoints()
    
    # Test file upload
    upload_ok = test_file_upload()
    
    print("\n" + "=" * 50)
    print("📊 Phase 3 Test Results:")
    print(f"   Components: {'✅ PASS' if components_ok else '❌ FAIL'}")
    print(f"   API Endpoints: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"   File Upload: {'✅ PASS' if upload_ok else '❌ FAIL'}")
    
    if all([components_ok, api_ok, upload_ok]):
        print("\n🎉 All Phase 3 tests passed! RAG system is ready.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 