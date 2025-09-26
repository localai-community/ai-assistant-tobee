#!/usr/bin/env python3
"""
Test script for PDF Summary functionality
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_DOCUMENT_PATH = "test_document.txt"  # We'll create this

def create_test_document():
    """Create a test document for testing."""
    test_content = """
    Artificial Intelligence and Machine Learning Report
    
    Executive Summary:
    This report provides an overview of current trends in artificial intelligence and machine learning technologies.
    
    Key Findings:
    1. AI adoption has increased by 300% in the past two years
    2. Machine learning models are becoming more efficient and accurate
    3. Natural language processing capabilities have significantly improved
    4. Computer vision applications are expanding across industries
    
    Technical Details:
    - Deep learning architectures like transformers are revolutionizing NLP
    - GPU acceleration is enabling faster model training
    - Edge computing is bringing AI to mobile and IoT devices
    - Federated learning is addressing privacy concerns
    
    Recommendations:
    1. Invest in AI talent and training programs
    2. Implement robust data governance frameworks
    3. Focus on ethical AI development practices
    4. Consider hybrid cloud architectures for AI workloads
    
    Conclusion:
    The future of AI looks promising with continued innovation in algorithms, hardware, and applications.
    Organizations should prepare for the AI-driven transformation of their industries.
    """
    
    with open(TEST_DOCUMENT_PATH, 'w') as f:
        f.write(test_content)
    
    print(f"✅ Created test document: {TEST_DOCUMENT_PATH}")

def test_backend_health():
    """Test if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend is not accessible: {e}")
        return False

def test_document_upload():
    """Test document upload functionality."""
    print("\n🧪 Testing Document Upload...")
    
    if not os.path.exists(TEST_DOCUMENT_PATH):
        create_test_document()
    
    try:
        with open(TEST_DOCUMENT_PATH, 'rb') as f:
            files = {'file': (TEST_DOCUMENT_PATH, f, 'text/plain')}
            data = {
                'conversation_id': 'test_conv_123',
                'user_id': 'test_user'
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/v1/rag/upload",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document upload successful!")
            print(f"   Document ID: {result.get('document_id')}")
            print(f"   Chunks created: {result.get('chunks_created')}")
            return result.get('document_id')
        else:
            print(f"❌ Document upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Document upload error: {e}")
        return None

def test_document_summary(document_id):
    """Test document summarization."""
    print(f"\n🧪 Testing Document Summary for {document_id}...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/rag/summarize/{document_id}",
            params={'summary_type': 'brief'},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document summary generated!")
            print(f"   Summary: {result.get('summary', '')[:200]}...")
            return True
        else:
            print(f"❌ Document summary failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document summary error: {e}")
        return False

def test_conversation_documents():
    """Test getting conversation documents."""
    print("\n🧪 Testing Conversation Documents...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/rag/documents/test_conv_123"
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Conversation documents retrieved!")
            print(f"   Documents count: {result.get('count', 0)}")
            return True
        else:
            print(f"❌ Get conversation documents failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Get conversation documents error: {e}")
        return False

def test_document_health():
    """Test document system health."""
    print("\n🧪 Testing Document System Health...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/rag/documents/health")
        
        if response.status_code == 200:
            result = response.json()
            health = result.get('health', {})
            print("✅ Document system health check passed!")
            print(f"   Total documents: {health.get('total_documents', 0)}")
            print(f"   Health score: {health.get('health_score', 0)}")
            return True
        else:
            print(f"❌ Document health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Document health check error: {e}")
        return False

def test_chat_with_document():
    """Test chat functionality with document context."""
    print("\n🧪 Testing Chat with Document Context...")
    
    try:
        chat_data = {
            "message": "What is this document about?",
            "model": "llama3:latest",
            "conversation_id": "test_conv_123",
            "user_id": "test_user",
            "enable_context_awareness": True
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat/",
            json=chat_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat with document context successful!")
            print(f"   Response: {result.get('response', '')[:200]}...")
            return True
        else:
            print(f"❌ Chat with document context failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat with document context error: {e}")
        return False

def cleanup_test_files():
    """Clean up test files."""
    if os.path.exists(TEST_DOCUMENT_PATH):
        os.remove(TEST_DOCUMENT_PATH)
        print(f"🧹 Cleaned up test file: {TEST_DOCUMENT_PATH}")

def main():
    """Run all tests."""
    print("🚀 Starting PDF Summary Functionality Tests")
    print("=" * 50)
    
    # Test backend health
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start the backend first.")
        return
    
    # Test document upload
    document_id = test_document_upload()
    if not document_id:
        print("\n❌ Document upload failed. Cannot continue with other tests.")
        return
    
    # Test document summary
    test_document_summary(document_id)
    
    # Test conversation documents
    test_conversation_documents()
    
    # Test document health
    test_document_health()
    
    # Test chat with document context
    test_chat_with_document()
    
    # Cleanup
    cleanup_test_files()
    
    print("\n" + "=" * 50)
    print("🎉 PDF Summary functionality tests completed!")
    print("\nNext steps:")
    print("1. Test the frontend interface at http://localhost:8501")
    print("2. Upload a real PDF document and test summarization")
    print("3. Try asking questions about the uploaded document")

if __name__ == "__main__":
    main()
