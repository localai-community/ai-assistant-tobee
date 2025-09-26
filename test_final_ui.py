#!/usr/bin/env python3
"""
Final test for the new streamlined PDF Summary UI
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
    AI Research Paper: Transformer Architectures in NLP
    
    Abstract:
    This comprehensive study evaluates transformer architectures including BERT, RoBERTa, and GPT models on various natural language processing benchmarks. Our results demonstrate significant improvements in performance across multiple tasks.
    
    Key Findings:
    1. RoBERTa achieves 94.2% accuracy on sentiment analysis
    2. BERT shows 96.8% performance on text classification
    3. GPT models excel in question answering with 89.1% F1 score
    
    Methodology:
    We conducted experiments on three datasets: IMDB movie reviews, AG News corpus, and SQuAD question answering dataset. All models were fine-tuned using the same hyperparameters for fair comparison.
    
    Results:
    The transformer architectures show remarkable improvements over traditional methods. RoBERTa consistently outperforms other models across most tasks, while BERT provides the best balance of performance and efficiency.
    
    Conclusion:
    Transformer architectures have revolutionized natural language processing. Future research should focus on efficiency improvements and domain-specific adaptations.
    """
    
    with open(TEST_DOCUMENT_PATH, 'w') as f:
        f.write(test_content)
    
    print(f"✅ Created test document: {TEST_DOCUMENT_PATH}")

def test_complete_workflow():
    """Test the complete new workflow."""
    print("🚀 Testing Complete New PDF Summary Workflow")
    print("=" * 60)
    
    # Create test document
    create_test_document()
    
    conversation_id = "test_conv_final"
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
    
    # Step 2: Generate summary first
    print("\n📝 Step 2: Generate Document Summary")
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
    
    # Step 3: Test natural language summary request
    print("\n💬 Step 3: Test Natural Language Summary Request")
    try:
        chat_data = {
            "message": "summarize this document",
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
            print("✅ Natural language summary request successful!")
            print(f"   Response length: {len(result.get('response', ''))}")
            print(f"   Response: {result.get('response', '')}")
        else:
            print(f"❌ Summary request failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Summary request error: {e}")
    
    # Step 4: Test document Q&A
    print("\n❓ Step 4: Test Document Q&A")
    try:
        chat_data = {
            "message": "What are the main findings of this research paper?",
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
            print("✅ Document Q&A successful!")
            print(f"   Response length: {len(result.get('response', ''))}")
            print(f"   Response: {result.get('response', '')}")
        else:
            print(f"❌ Q&A failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Q&A error: {e}")
    
    # Cleanup
    if os.path.exists(TEST_DOCUMENT_PATH):
        os.remove(TEST_DOCUMENT_PATH)
        print(f"\n🧹 Cleaned up test file: {TEST_DOCUMENT_PATH}")
    
    print("\n" + "=" * 60)
    print("🎉 Complete workflow test finished!")
    print("\n✨ New Features Implemented:")
    print("1. 📄 Floating upload button in main chat area")
    print("2. 🔄 Automatic document processing (no separate button)")
    print("3. 💬 Natural language summary requests")
    print("4. 📡 Direct streaming of summaries to chat")
    print("5. 🎯 Simplified sidebar (documents view only)")
    print("6. 🔗 Document context integration in chat responses")

if __name__ == "__main__":
    test_complete_workflow()
