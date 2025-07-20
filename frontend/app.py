"""
LocalAI Community Frontend
A Streamlit-based chat interface for the LocalAI Community backend.
"""

import streamlit as st
import httpx
import os
import asyncio
from typing import Optional, List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="LocalAI Community",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .error-message {
        background-color: #ffebee;
        border-left-color: #f44336;
    }
    .success-message {
        background-color: #e8f5e8;
        border-left-color: #4caf50;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "available_models" not in st.session_state:
        st.session_state.available_models = []
    if "backend_health" not in st.session_state:
        st.session_state.backend_health = False

def check_backend_health() -> bool:
    """Check if the backend is healthy."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/health", timeout=5.0)
            return response.status_code == 200
    except:
        return False

def get_available_models() -> List[str]:
    """Get available models from backend."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/chat/models", timeout=5.0)
            if response.status_code == 200:
                return response.json()
    except:
        pass
    return []

def send_to_backend(message: str, conversation_id: Optional[str] = None) -> Optional[str]:
    """Send message to backend and get response."""
    try:
        with httpx.Client() as client:
            # Use the first available model or fallback to llama3:latest
            model = st.session_state.available_models[0] if st.session_state.available_models else "llama3:latest"
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "stream": False
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            response = client.post(
                f"{BACKEND_URL}/api/v1/chat/",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response from backend")
            elif response.status_code == 503:
                return "❌ Ollama service is not available. Please make sure Ollama is running."
            else:
                return f"Backend error: {response.status_code}"
                
    except httpx.TimeoutException:
        return "Request timed out. Please try again."
    except Exception as e:
        return f"Communication error: {str(e)}"

def display_welcome_message():
    """Display welcome message and status information."""
    st.markdown('<h1 class="main-header">🤖 LocalAI Community</h1>', unsafe_allow_html=True)
    
    # Status indicators
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.backend_health:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Disconnected")
    
    with col2:
        if st.session_state.available_models:
            st.success(f"✅ {len(st.session_state.available_models)} Models Available")
        else:
            st.warning("⚠️ No Models Available")
    
    with col3:
        if st.session_state.conversation_id:
            st.info(f"💬 Conversation Active")
        else:
            st.info("💬 New Conversation")
    
    # Welcome message
    if not st.session_state.messages:
        welcome_msg = """
        **Welcome to LocalAI Community!**
        
        I'm your local-first AI assistant with MCP and RAG capabilities.
        
        **Features:**
        • Direct Ollama integration
        • Document processing (PDF, DOCX, TXT)
        • RAG (Retrieval-Augmented Generation)
        • MCP (Model Context Protocol) tools
        
        **Getting Started:**
        1. Ask questions and get AI responses
        2. Use MCP tools for file operations
        3. Upload documents via the backend API
        
        How can I help you today?
        """
        
        st.markdown(welcome_msg)
        
        if st.session_state.available_models:
            st.info(f"**Available Models:** {', '.join(st.session_state.available_models)}")
        else:
            st.warning("**⚠️ No models available** - Please make sure Ollama is running and models are installed.")

def display_chat_messages():
    """Display chat messages."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def main():
    """Main application function."""
    init_session_state()
    
    # Check backend health and get models
    st.session_state.backend_health = check_backend_health()
    if st.session_state.backend_health:
        st.session_state.available_models = get_available_models()
    
    # Sidebar for settings and info
    with st.sidebar:
        st.header("Settings")
        
        # Model selection
        if st.session_state.available_models:
            selected_model = st.selectbox(
                "Select Model",
                st.session_state.available_models,
                index=0
            )
        else:
            st.warning("No models available")
        
        # Temperature slider
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        
        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.rerun()
        
        # Backend status
        st.header("Backend Status")
        if st.session_state.backend_health:
            st.success("✅ Connected")
        else:
            st.error("❌ Disconnected")
            st.info(f"Backend URL: {BACKEND_URL}")
        
        # Available models
        if st.session_state.available_models:
            st.header("Available Models")
            for model in st.session_state.available_models:
                st.text(f"• {model}")
    
    # Main chat interface
    display_welcome_message()
    
    # Display chat messages
    display_chat_messages()
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Check backend health before sending
        if not st.session_state.backend_health:
            error_msg = f"❌ Backend service is not available. Please make sure the backend server is running on {BACKEND_URL}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.error(error_msg)
        else:
            # Show spinner while processing
            with st.spinner("Thinking..."):
                # Send message to backend
                response = send_to_backend(prompt, st.session_state.conversation_id)
                
                if response and not response.startswith("❌"):
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Display assistant response
                    with st.chat_message("assistant"):
                        st.markdown(response)
                else:
                    error_msg = response or "❌ Unable to get response from backend. Please try again or check the backend logs."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.error(error_msg)

if __name__ == "__main__":
    main() 