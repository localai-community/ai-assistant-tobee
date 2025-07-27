#!/usr/bin/env python3
"""
Test script to compare LLM-based vs heuristic context detection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.rag.advanced_retriever import AdvancedRAGRetriever

def test_context_detection_comparison():
    """Compare LLM-based vs heuristic context detection."""
    
    # Initialize the retriever
    retriever = AdvancedRAGRetriever()
    
    # Sample conversation history about neural networks
    conversation_history = [
        {"role": "user", "content": "What is a transformer?"},
        {"role": "assistant", "content": "A transformer is a neural network architecture that uses attention mechanisms to process sequential data. It was introduced in the 'Attention Is All You Need' paper and has become the foundation for many modern language models."},
        {"role": "user", "content": "How does attention work?"},
        {"role": "assistant", "content": "Attention allows the model to focus on different parts of the input sequence when processing each element. It computes attention scores between all pairs of positions and uses these scores to weight the importance of each position."}
    ]
    
    # Test cases with expected results
    test_cases = [
        # General knowledge questions
        ("What is the capital of France?", False, "Geography question"),
        ("What is photosynthesis?", False, "Science definition"),
        ("Who is Albert Einstein?", False, "Person question"),
        ("What year was World War II?", False, "Historical date"),
        
        # Context-dependent questions
        ("What about the second part?", True, "Follow-up with pronoun"),
        ("How does it work?", True, "Follow-up with pronoun"),
        ("Can you explain that further?", True, "Follow-up with pronoun"),
        ("What's the difference between them?", True, "Comparative with pronoun"),
        ("Tell me more about attention", True, "Specific reference to conversation topic"),
        ("How does this relate to transformers?", True, "Contextual reference"),
        
        # Edge cases
        ("What is it?", True, "Very short with pronoun"),
        ("What is a transformer?", False, "Specific question, no context needed"),
        ("How does attention work?", False, "Specific question, no context needed"),
        
        # Nuanced cases
        ("What are the advantages?", True, "Implied reference to previous topic"),
        ("Can you give me an example?", True, "Follow-up question"),
        ("What about the implementation?", True, "Follow-up about previous topic"),
        ("What is machine learning?", False, "General definition question")
    ]
    
    print("🧪 Testing LLM vs Heuristic Context Detection")
    print("=" * 70)
    
    llm_correct = 0
    heuristic_correct = 0
    total = len(test_cases)
    
    for query, expected, description in test_cases:
        print(f"\n🔍 Testing: '{query}'")
        print(f"   Expected: {expected} ({description})")
        
        # Test heuristic approach
        try:
            heuristic_result = retriever._llm_context_detection_heuristic(query, conversation_history)
            heuristic_status = "✅" if heuristic_result == expected else "❌"
            print(f"   Heuristic: {heuristic_result} {heuristic_status}")
            if heuristic_result == expected:
                heuristic_correct += 1
        except Exception as e:
            print(f"   Heuristic: ERROR - {e}")
        
        # Test LLM approach
        try:
            context_summary = retriever._create_conversation_summary(conversation_history)
            llm_result = retriever._llm_context_detection(query, context_summary)
            llm_status = "✅" if llm_result == expected else "❌"
            print(f"   LLM:      {llm_result} {llm_status}")
            if llm_result == expected:
                llm_correct += 1
        except Exception as e:
            print(f"   LLM:      ERROR - {e}")
    
    print(f"\n📊 Results Summary:")
    print(f"   Heuristic: {heuristic_correct}/{total} correct ({heuristic_correct/total*100:.1f}%)")
    print(f"   LLM:       {llm_correct}/{total} correct ({llm_correct/total*100:.1f}%)")
    
    if llm_correct > heuristic_correct:
        print("🎉 LLM-based detection performed better!")
    elif heuristic_correct > llm_correct:
        print("🎉 Heuristic detection performed better!")
    else:
        print("🤝 Both approaches performed equally well!")
    
    return llm_correct, heuristic_correct, total

if __name__ == "__main__":
    test_context_detection_comparison() 