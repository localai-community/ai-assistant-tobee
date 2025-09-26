#!/usr/bin/env python3
"""
Test script for the new streamlined PDF Summary UI
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

def test_new_workflow():
    """Test the new streamlined workflow."""
    print("🚀 Testing New Streamlined PDF Summary Workflow")
    print("=" * 60)
    
    # Create test document
    create_test_document()
    
    # Test 1: Upload document
    print("\n📤 Test 1: Upload Document")
    try:
        with open(TEST_DOCUMENT_PATH, 'rb') as f:
            files = {'file': (TEST_DOCUMENT_PATH, f, 'text/plain')}
            data = {
                'conversation_id': 'test_conv_new_ui',
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
            document_id = result.get('document_id')
            print(f"✅ Document uploaded successfully!")
            print(f"   Document ID: {document_id}")
            print(f"   Chunks created: {result.get('chunks_created')}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # Test 2: Natural language summary request
    print("\n📝 Test 2: Natural Language Summary Request")
    try:
        chat_data = {
            "message": "summarize this document",
            "model": "llama3:latest",
            "conversation_id": "test_conv_new_ui",
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
            print("✅ Natural language summary request successful!")
            print(f"   Response length: {len(result.get('response', ''))}")
            print(f"   Response preview: {result.get('response', '')[:200]}...")
        else:
            print(f"❌ Summary request failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Summary request error: {e}")
    
    # Test 3: Document Q&A
    print("\n❓ Test 3: Document Q&A")
    try:
        chat_data = {
            "message": "What are the main findings of this research?",
            "model": "llama3:latest",
            "conversation_id": "test_conv_new_ui",
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
            print("✅ Document Q&A successful!")
            print(f"   Response length: {len(result.get('response', ''))}")
            print(f"   Response preview: {result.get('response', '')[:200]}...")
        else:
            print(f"❌ Q&A failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Q&A error: {e}")
    
    # Cleanup
    if os.path.exists(TEST_DOCUMENT_PATH):
        os.remove(TEST_DOCUMENT_PATH)
        print(f"\n🧹 Cleaned up test file: {TEST_DOCUMENT_PATH}")
    
    print("\n" + "=" * 60)
    print("🎉 New UI workflow tests completed!")
    print("\n✨ New Features:")
    print("1. 📄 Floating upload button in main chat area")
    print("2. 🔄 Automatic document processing (no separate button)")
    print("3. 💬 Natural language summary requests")
    print("4. 📡 Direct streaming of summaries to chat")
    print("5. 🎯 Simplified sidebar (documents view only)")

if __name__ == "__main__":
    test_new_workflow()
