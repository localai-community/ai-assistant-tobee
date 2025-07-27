#!/usr/bin/env python3
"""
Test script to simulate frontend Phase 2 streaming call
"""

import sys
import os

# Path is set by the test runner

# Mock streamlit for testing
import streamlit as st
from unittest.mock import MagicMock

# Mock streamlit components
st.chat_message = MagicMock()
st.empty = MagicMock()
st.info = MagicMock()
st.error = MagicMock()
st.markdown = MagicMock()

# Mock the message placeholder
mock_placeholder = MagicMock()
st.empty.return_value = mock_placeholder

# Mock the chat message context manager
mock_chat_message = MagicMock()
st.chat_message.return_value.__enter__ = MagicMock(return_value=mock_chat_message)
st.chat_message.return_value.__exit__ = MagicMock(return_value=None)

# Import the streaming function
from app import send_streaming_phase2_reasoning_chat

def test_frontend_streaming():
    """Test the frontend streaming function"""
    print("🧪 Testing frontend Phase 2 streaming function...")
    
    # Mock session state
    import app
    app.st.session_state = MagicMock()
    app.st.session_state.available_models = ["llama3:latest"]
    app.BACKEND_URL = "http://localhost:8000"
    
    try:
        # Test the streaming function
        result = send_streaming_phase2_reasoning_chat(
            message="What is 5 + 3?",
            engine_type="auto",
            conversation_id="test-conversation"
        )
        
        print(f"📊 Result: {result}")
        
        if result and isinstance(result, dict):
            print(f"✅ Function returned result")
            print(f"📝 Response length: {len(result.get('response', ''))}")
            print(f"🔧 Engine used: {result.get('engine_used', 'unknown')}")
            print(f"🧠 Reasoning type: {result.get('reasoning_type', 'unknown')}")
            print(f"📊 Steps count: {result.get('steps_count', 0)}")
            print(f"🎯 Confidence: {result.get('confidence', 0.0)}")
            return True
        else:
            print(f"❌ Function returned: {result}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_frontend_streaming()
    if success:
        print("✅ Frontend streaming test PASSED")
        sys.exit(0)
    else:
        print("❌ Frontend streaming test FAILED")
        sys.exit(1) 