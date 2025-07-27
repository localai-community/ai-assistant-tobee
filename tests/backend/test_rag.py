#!/usr/bin/env python3
"""
Test script for RAG system functionality.
"""

import os
import sys
import logging
from pathlib import Path

# Path is set by the test runner

from app.services.rag import RAGRetriever, DocumentProcessor, VectorStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_document_processing():
    """Test document processing functionality"""
    print("🧪 Testing Document Processing...")
    
    # Create a test document
    test_content = """
    This is a test document about artificial intelligence.
    AI is a field of computer science that aims to create intelligent machines.
    Machine learning is a subset of AI that focuses on algorithms that can learn from data.
    Deep learning is a type of machine learning that uses neural networks.
    Natural language processing is another important area of AI.
    """
    
    test_file_path = "test_document.txt"
    with open(test_file_path, "w") as f:
        f.write(test_content)
    
    try:
        # Test document processor
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        documents = processor.process_file(test_file_path)
        
        print(f"✅ Document processed successfully: {len(documents)} chunks created")
        
        # Test stats
        stats = processor.get_processing_stats(documents)
        print(f"📊 Processing stats: {stats}")
        
        return documents
        
    except Exception as e:
        print(f"❌ Document processing failed: {e}")
        return None
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_vector_store():
    """Test vector store functionality"""
    print("\n🧪 Testing Vector Store...")
    
    try:
        # Initialize vector store
        vector_store = VectorStore(persist_directory="test_vector_db")
        
        # Test health check
        health = vector_store.health_check()
        print(f"🏥 Vector store health: {health['status']}")
        
        # Test embeddings
        test_text = "This is a test query"
        results = vector_store.similarity_search(test_text, k=1)
        print(f"🔍 Similarity search test: {len(results)} results")
        
        return vector_store
        
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return None

def test_rag_integration():
    """Test full RAG integration"""
    print("\n🧪 Testing RAG Integration...")
    
    try:
        # Initialize RAG retriever
        rag = RAGRetriever()
        
        # Test health check
        health = rag.health_check()
        print(f"🏥 RAG system health: {health['overall_status']}")
        
        # Test system stats
        stats = rag.get_system_stats()
        print(f"📊 RAG system stats: {stats}")
        
        return rag
        
    except Exception as e:
        print(f"❌ RAG integration test failed: {e}")
        return None

def test_full_workflow():
    """Test complete RAG workflow"""
    print("\n🧪 Testing Complete RAG Workflow...")
    
    try:
        # Create test document
        test_content = """
        Python is a high-level programming language known for its simplicity and readability.
        It was created by Guido van Rossum and first released in 1991.
        Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.
        It has a large standard library and extensive third-party packages available through PyPI.
        Python is widely used in web development, data science, artificial intelligence, and automation.
        """
        
        test_file_path = "python_info.txt"
        with open(test_file_path, "w") as f:
            f.write(test_content)
        
        # Initialize RAG system
        rag = RAGRetriever()
        
        # Add document
        result = rag.add_document(test_file_path)
        print(f"📄 Document addition result: {result['success']}")
        
        if result['success']:
            # Test search
            query = "What is Python used for?"
            search_results = rag.search_documents(query, k=3)
            print(f"🔍 Search results for '{query}': {len(search_results)} found")
            
            # Test RAG prompt creation
            rag_prompt = rag.create_rag_prompt(query, k=2)
            print(f"📝 RAG prompt created (length: {len(rag_prompt)} chars)")
            
            # Test context retrieval
            context = rag.get_context_for_query(query, k=2)
            print(f"📚 Context retrieved (length: {len(context)} chars)")
        
        # Clean up
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Full workflow test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting RAG System Tests...\n")
    
    # Test individual components
    test_document_processing()
    test_vector_store()
    test_rag_integration()
    
    # Test complete workflow
    success = test_full_workflow()
    
    print("\n" + "="*50)
    if success:
        print("✅ All RAG tests completed successfully!")
    else:
        print("❌ Some tests failed. Check the output above.")
    print("="*50)

if __name__ == "__main__":
    main() 