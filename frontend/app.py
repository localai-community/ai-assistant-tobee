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
    if "conversations" not in st.session_state:
        st.session_state.conversations = []
    if "auto_loaded" not in st.session_state:
        st.session_state.auto_loaded = False

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

def get_conversations() -> List[Dict]:
    """Get conversations from backend."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/chat/conversations", timeout=5.0)
            if response.status_code == 200:
                return response.json()
    except:
        pass
    return []

def load_conversation_messages(conversation_id: str) -> List[Dict]:
    """Load messages for a specific conversation."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/chat/conversations/{conversation_id}", timeout=5.0)
            if response.status_code == 200:
                conversation = response.json()
                return conversation.get("messages", [])
    except:
        pass
    return []

def send_to_backend(message: str, conversation_id: Optional[str] = None) -> Optional[Dict]:
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
                return {
                    "response": data.get("response", "No response from backend"),
                    "conversation_id": data.get("conversation_id")
                }
            elif response.status_code == 503:
                return {"response": "❌ Ollama service is not available. Please make sure Ollama is running."}
            else:
                return {"response": f"Backend error: {response.status_code}"}
                
    except httpx.TimeoutException:
        return {"response": "Request timed out. Please try again."}
    except Exception as e:
        return {"response": f"Communication error: {str(e)}"}

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
        
        # Always load conversations to ensure they're fresh
        st.session_state.conversations = get_conversations()
        

        
        # Auto-load the most recent conversation if not already auto-loaded
        # Commented out to start with empty chat on page refresh
        # if (not st.session_state.auto_loaded and 
        #     st.session_state.conversations and 
        #     len(st.session_state.conversations) > 0 and 
        #     not st.session_state.messages):
        #     # Get the most recent conversation (last in the list)
        #     latest_conversation = st.session_state.conversations[-1]
        #     st.session_state.conversation_id = latest_conversation["id"]
        #     st.session_state.messages = latest_conversation["messages"]
        #     st.session_state.auto_loaded = True
        #     st.sidebar.info(f"🔄 Auto-loaded conversation: {latest_conversation['id'][:8]}...")
    
    # Sidebar for conversations and settings
    with st.sidebar:
        # Logo at the top
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
            <span style="font-size: 80px;">🦥</span>
            <div style="font-size: 24px; margin-left: 10px;">
                <div>Assistant</div>
                <div style="font-weight: bold;">Tobee</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Conversation selection
        st.markdown("**Conversations**")
        
        if st.session_state.backend_health and st.session_state.conversations:
            # Show "New Chat" option
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💬 New Chat", key="new_chat_sidebar"):
                    st.session_state.messages = []
                    st.session_state.conversation_id = None
                    st.session_state.auto_loaded = True  # Prevent auto-loading after manual new chat
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete All", key="delete_all"):
                    # Clear all conversations from backend
                    try:
                        with httpx.Client() as client:
                            response = client.delete(f"{BACKEND_URL}/api/v1/chat/conversations", timeout=5.0)
                            if response.status_code == 200:
                                data = response.json()
                                st.session_state.conversations = []
                                st.session_state.messages = []
                                st.session_state.conversation_id = None
                                st.session_state.auto_loaded = True
                                st.success(f"✅ {data.get('message', 'All conversations deleted')}")
                                st.rerun()
                            else:
                                st.error(f"Failed to delete conversations: {response.status_code}")
                    except Exception as e:
                        st.error(f"Failed to delete conversations: {str(e)}")
            
            # Show conversation list
            st.markdown("**Recent Conversations:**")
            for i, conv in enumerate(st.session_state.conversations):
                # Create a short title from the first message
                first_message = conv['messages'][0]['content'] if conv['messages'] else "Empty conversation"
                short_title = first_message[:30] + "..." if len(first_message) > 30 else first_message
                
                # Highlight current conversation
                is_current = (st.session_state.conversation_id == conv['id'])
                
                # Create clickable text with different styling for current conversation
                if is_current:
                    st.markdown(f"**👈 {short_title}** *(current)*")
                else:
                    # Use a small, minimal button that looks like a link
                    if st.button(f"📝 {short_title}", key=f"conv_{i}", use_container_width=True):
                        st.session_state.conversation_id = conv["id"]
                        st.session_state.messages = conv["messages"]
                        st.session_state.auto_loaded = True
                        st.rerun()
        else:
            st.info("No conversations available")
        
        # Settings section at the bottom
        st.markdown("---")  # Separator
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
                response_data = send_to_backend(prompt, st.session_state.conversation_id)
                
                if response_data and not response_data["response"].startswith("❌"):
                    # Update conversation ID if provided
                    if response_data.get("conversation_id"):
                        st.session_state.conversation_id = response_data["conversation_id"]
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response_data["response"]})
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Display assistant response
                    with st.chat_message("assistant"):
                        st.markdown(response_data["response"])
                    
                    # Force rerun to update sidebar
                    st.rerun()
                else:
                    error_msg = response_data["response"] if response_data else "❌ Unable to get response from backend. Please try again or check the backend logs."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.error(error_msg)

if __name__ == "__main__":
    main() 