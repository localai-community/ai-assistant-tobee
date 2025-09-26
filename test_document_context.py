#!/usr/bin/env python3
"""
Test script to debug document context integration
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_DOCUMENT_PATH = "test_document.txt"

def create_test_document():
    """Create a test document for testing."""
    test_content = """
    Machine Learning Research Paper
    
    Abstract:
    This paper presents a comprehensive study on the application of machine learning algorithms in natural language processing tasks. We evaluate the performance of various transformer architectures on sentiment analysis, text classification, and question answering benchmarks.
    
    Introduction:
    Natural language processing has seen remarkable progress with the advent of transformer architectures. The ability to process sequential data and capture long-range dependencies has revolutionized the field.
    
    Methodology:
    We conducted experiments on three datasets: IMDB movie reviews for sentiment analysis, AG News for text classification, and SQuAD for question answering. We compared BERT, RoBERTa, and GPT models.
    
    Results:
    Our experiments show that RoBERTa achieves the best performance across all tasks, with 94.2% accuracy on sentiment analysis, 96.8% on text classification, and 89.1% F1 score on question answering.
    
    Conclusion:
    Transformer architectures continue to push the boundaries of NLP performance. Future work should focus on efficiency improvements and domain adaptation.
    """
    
    with open(TEST_DOCUMENT_PATH, 'w') as f:
        f.write(test_content)
    
    print(f"✅ Created test document: {TEST_DOCUMENT_PATH}")

def test_document_context_debug():
    """Debug document context integration."""
    print("🔍 Debugging Document Context Integration")
    print("=" * 50)
    
    # Create test document
    create_test_document()
    
    conversation_id = "test_conv_debug"
    user_id = "test_user"
    
    # Step 1: Upload document
    print("\n📤 Step 1: Upload Document")
    try:
        with open(TEST_DOCUMENT_PATH, 'rb') as f:
            files = {'file': (TEST_DOCUMENT_PATH, f, 'text/plain')}
            data = {
                'conversation_id': conversation_id,
                'user_id': user_id
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/v1/rag/upload",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            document_id = result.get('document_id')
            print(f"✅ Document uploaded successfully!")
            print(f"   Document ID: {document_id}")
            print(f"   Conversation ID: {conversation_id}")
            print(f"   Chunks created: {result.get('chunks_created')}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # Step 2: Check conversation documents
    print("\n📋 Step 2: Check Conversation Documents")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/rag/documents/{conversation_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Conversation documents retrieved!")
            print(f"   Documents count: {result.get('count', 0)}")
            documents = result.get('documents', [])
            for doc in documents:
                print(f"   - {doc['filename']} (ID: {doc['id']})")
        else:
            print(f"❌ Failed to get conversation documents: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting conversation documents: {e}")
    
    # Step 3: Test document summary
    print("\n📝 Step 3: Test Document Summary")
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
        else:
            print(f"❌ Document summary failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Document summary error: {e}")
    
    # Step 4: Test chat with explicit document context
    print("\n💬 Step 4: Test Chat with Document Context")
    try:
        chat_data = {
            "message": "What is this document about? Please reference the uploaded document.",
            "model": "llama3:latest",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "enable_context_awareness": True,
            "include_memory": True
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat/",
            json=chat_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat with document context successful!")
            print(f"   Response length: {len(result.get('response', ''))}")
            print(f"   Response: {result.get('response', '')}")
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Chat error: {e}")
    
    # Cleanup
    if os.path.exists(TEST_DOCUMENT_PATH):
        os.remove(TEST_DOCUMENT_PATH)
        print(f"\n🧹 Cleaned up test file: {TEST_DOCUMENT_PATH}")

if __name__ == "__main__":
    test_document_context_debug()
