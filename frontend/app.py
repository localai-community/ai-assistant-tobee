"""
LocalAI Community Frontend
A Streamlit-based chat interface for the LocalAI Community backend.
"""

import streamlit as st
import httpx
import os
import asyncio
import json
from typing import Optional, List, Dict
from dotenv import load_dotenv
import tempfile
from pathlib import Path

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
# Note: Streamlit has built-in dark mode support - users can toggle it in the hamburger menu
st.set_page_config(
    page_title="LocalAI Community",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple CSS for better styling
def get_css():
    return """
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 2rem;
        }
        .section-header {
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
    </style>
    """

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
    if "rag_stats" not in st.session_state:
        st.session_state.rag_stats = {}
    if "use_rag" not in st.session_state:
        st.session_state.use_rag = False
    if "mcp_tools" not in st.session_state:
        st.session_state.mcp_tools = []
    if "mcp_health" not in st.session_state:
        st.session_state.mcp_health = {}
    if "use_streaming" not in st.session_state:
        st.session_state.use_streaming = True

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

def get_rag_stats() -> Dict:
    """Get RAG system statistics."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/rag/stats", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                # Extract stats from the nested structure
                if "stats" in data and "vector_store" in data["stats"]:
                    vector_stats = data["stats"]["vector_store"]["stats"]
                    stats = {
                        "total_documents": vector_stats.get("total_documents", 0),
                        "total_chunks": vector_stats.get("total_documents", 0),  # Same as total_documents
                        "vector_db_size_mb": vector_stats.get("storage_size_mb", 0.0),  # Use actual size from backend
                        "collection_name": vector_stats.get("collection_name", ""),
                        "persist_directory": vector_stats.get("persist_directory", "")
                    }
                    # Debug output
                    print(f"🔍 RAG Stats from API: {stats}")
                    return stats
                return {}
    except Exception as e:
        print(f"Error getting RAG stats: {e}")
        pass
    return {}

def get_mcp_tools() -> List[Dict]:
    """Get available MCP tools from backend."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/chat/tools", timeout=5.0)
            if response.status_code == 200:
                return response.json()
    except:
        pass
    return []

def get_mcp_health() -> Dict:
    """Get MCP health status from backend."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/chat/tools/health", timeout=5.0)
            if response.status_code == 200:
                return response.json()
    except:
        pass
    return {}

def call_mcp_tool(tool_name: str, arguments: Dict) -> Dict:
    """Call an MCP tool."""
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{BACKEND_URL}/api/v1/chat/tools/{tool_name}/call",
                json=arguments,
                timeout=30.0
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Tool call failed: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"success": False, "error": f"Tool call error: {str(e)}"}

def upload_document_for_rag(uploaded_file) -> Dict:
    """Upload a document for RAG processing."""
    try:
        with httpx.Client() as client:
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = client.post(f"{BACKEND_URL}/api/v1/rag/upload", files=files, timeout=30.0)
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Upload failed: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"success": False, "error": f"Upload error: {str(e)}"}

def send_rag_chat(message: str, conversation_id: Optional[str] = None) -> Optional[Dict]:
    """Send message to backend with RAG enhancement."""
    try:
        with httpx.Client() as client:
            # Use the first available model or fallback to llama3:latest
            model = st.session_state.available_models[0] if st.session_state.available_models else "llama3:latest"
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "k": 4
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            response = client.post(
                f"{BACKEND_URL}/api/v1/chat/",
                json=payload,
                timeout=120.0  # Increased timeout for RAG processing (2 minutes)
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "response": data.get("response", "No response from backend"),
                    "conversation_id": data.get("conversation_id"),
                    "rag_context": data.get("rag_context", ""),
                    "has_context": data.get("has_context", False)
                }
            elif response.status_code == 503:
                return {"response": "❌ Ollama service is not available. Please make sure Ollama is running."}
            else:
                return {"response": f"Backend error: {response.status_code}"}
                
    except httpx.TimeoutException:
        return {"response": "Request timed out. Please try again."}
    except Exception as e:
        return {"response": f"Communication error: {str(e)}"}

def send_streaming_rag_chat(message: str, conversation_id: Optional[str] = None) -> Optional[Dict]:
    """Send message to backend with RAG enhancement and streaming response."""
    st.info("🚀 Starting RAG streaming function...")
    try:
        with httpx.Client() as client:
            # Use the first available model or fallback to llama3:latest
            model = st.session_state.available_models[0] if st.session_state.available_models else "llama3:latest"
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "k": 4
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            # Create assistant message container for streaming
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                # Stream the response
                with client.stream(
                    "POST",
                    f"{BACKEND_URL}/api/v1/rag/stream",
                    json=payload,
                    timeout=300.0,  # Increased timeout for RAG processing (5 minutes)
                    headers={"Accept": "text/event-stream", "Connection": "keep-alive"}
                ) as response:
                    if response.status_code == 200:
                        # Process Server-Sent Events
                        line_count = 0
                        rag_context_found = False
                        last_few_lines = []
                        for line in response.iter_lines():
                            if line:
                                # httpx.iter_lines() returns strings, not bytes
                                if line.startswith('data: '):
                                    line_count += 1
                                    # Keep track of last few lines for debugging
                                    last_few_lines.append(line)
                                    if len(last_few_lines) > 5:
                                        last_few_lines.pop(0)
                                    data_str = line[6:]  # Remove 'data: ' prefix
                                    try:
                                        data = json.loads(data_str)
                                        
                                        # Debug: Log any data containing rag_context
                                        if "rag_context" in data:
                                            st.info(f"🔍 FOUND DATA WITH RAG_CONTEXT: {data}")
                                        
                                        if data.get("type") == "error":
                                            return {"response": f"Error: {data.get('error', 'Unknown error')}"}
                                        
                                        # Handle different response types
                                        if "content" in data:
                                            chunk = data["content"]
                                            full_response += chunk
                                            message_placeholder.markdown(full_response + "▌")
                                        
                                        elif "conversation_id" in data:
                                            # Update conversation ID
                                            st.session_state.conversation_id = data["conversation_id"]
                                        
                                        elif "rag_context" in data:
                                            # Found rag_context - check if it's the final line
                                            message_placeholder.markdown(full_response)
                                            st.success(f"🎯 RAG CONTEXT FOUND: {data.get('rag_context', '')[:100]}...")
                                            st.info(f"Has context: {data.get('has_context', False)}")
                                            # Add debug info to the response
                                            debug_response = full_response + f"\n\n🔍 DEBUG: RAG context found after processing {line_count} lines."
                                            return {
                                                "response": debug_response,
                                                "conversation_id": st.session_state.conversation_id,
                                                "rag_context": data.get("rag_context", ""),
                                                "has_context": data.get("has_context", True)  # Assume True if rag_context is present
                                            }

                                            
                                    except json.JSONDecodeError:
                                        st.error(f"❌ JSON decode error for line: {line}")
                                        continue
                        
                        # If we get here without returning, the streaming ended without content
                        st.warning(f"⚠️ STREAMING ENDED - Response length: {len(full_response)}")
                        if not full_response:
                            return {"response": "No response generated. Please try again."}
                        else:
                            # If we have content but no rag_context line, return what we have
                            st.error("❌ NO RAG CONTEXT FOUND - Function completed without rag_context line")
                            # Add debug info to the response
                            debug_response = full_response + f"\n\n🔍 DEBUG: Function completed without finding rag_context line. Processed {line_count} lines."
                            debug_response += f"\n🔍 DEBUG: Last 5 lines received:"
                            for i, line in enumerate(last_few_lines):
                                debug_response += f"\n  {i+1}: {line[:100]}..."
                            return {
                                "response": debug_response,
                                "conversation_id": st.session_state.conversation_id,
                                "rag_context": "",
                                "has_context": False
                            }
                    else:
                        return {"response": f"Backend error: {response.status_code}"}
                        
    except httpx.TimeoutException:
        st.error("⏰ RAG streaming timed out")
        return {"response": "Request timed out. Please try again."}
    except Exception as e:
        st.error(f"💥 RAG streaming error: {str(e)}")
        return {"response": f"Communication error: {str(e)}"}
    
    st.error("🔚 RAG streaming function completed without returning anything")
    return None

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

def send_streaming_chat(message: str, conversation_id: Optional[str] = None) -> Optional[Dict]:
    """Send message to backend and get streaming response with real-time display."""
    try:
        with httpx.Client() as client:
            # Use the first available model or fallback to llama3:latest
            model = st.session_state.available_models[0] if st.session_state.available_models else "llama3:latest"
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "stream": True
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            # Create assistant message container for streaming
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                # Stream the response
                with client.stream(
                    "POST",
                    f"{BACKEND_URL}/api/v1/chat/stream",
                    json=payload,
                    timeout=300.0,  # Increased timeout (5 minutes)
                    headers={"Accept": "text/event-stream", "Connection": "keep-alive"}
                ) as response:
                    if response.status_code == 200:
                        # Process Server-Sent Events
                        for line in response.iter_lines():
                            if line:
                                # httpx.iter_lines() returns strings, not bytes
                                if line.startswith('data: '):
                                    try:
                                        data = json.loads(line[6:])  # Remove 'data: ' prefix
                                        chunk = data.get('content', '')
                                        full_response += chunk
                                        
                                        # Update the message placeholder with accumulated response
                                        message_placeholder.markdown(full_response + "▌")
                                    except json.JSONDecodeError:
                                        continue
                                elif line.strip() == '':  # Empty line indicates end of SSE
                                    continue
                        
                        # Final update without cursor
                        message_placeholder.markdown(full_response)
                        
                        return {
                            "response": full_response,
                            "conversation_id": conversation_id
                        }
                    elif response.status_code == 503:
                        error_msg = "❌ Ollama service is not available. Please make sure Ollama is running."
                        message_placeholder.error(error_msg)
                        return {"response": error_msg}
                    else:
                        error_msg = f"Backend error: {response.status_code}"
                        message_placeholder.error(error_msg)
                        return {"response": error_msg}
                    
    except httpx.TimeoutException:
        error_msg = "Request timed out. Please try again."
        with st.chat_message("assistant"):
            st.error(error_msg)
        return {"response": error_msg}
    except httpx.ConnectError:
        error_msg = "❌ Cannot connect to backend server. Please make sure the backend is running."
        with st.chat_message("assistant"):
            st.error(error_msg)
        return {"response": error_msg}
    except Exception as e:
        error_msg = f"Communication error: {str(e)}"
        with st.chat_message("assistant"):
            st.error(error_msg)
        return {"response": error_msg}

def send_to_backend(message: str, conversation_id: Optional[str] = None, use_streaming: bool = False) -> Optional[Dict]:
    """Send message to backend and get response."""
    if use_streaming:
        return send_streaming_chat(message, conversation_id)
    
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
                timeout=120.0  # Increased timeout (2 minutes)
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
    col1, col2, col3, col4 = st.columns(4)
    
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
    
    with col4:
        if st.session_state.rag_stats.get("total_documents", 0) > 0:
            st.success(f"📚 {st.session_state.rag_stats.get('total_documents', 0)} Documents Loaded")
        else:
            st.info("📚 No Documents Loaded")
    
    # Welcome message
    if not st.session_state.messages:
        welcome_msg = """
        **Welcome to LocalAI Community!**
        
        I'm your local-first AI assistant with MCP and RAG capabilities.
        
        **Features:**
        • Direct Ollama integration
        • Document processing (PDF, DOCX, TXT, MD)
        • RAG (Retrieval-Augmented Generation)
        • MCP (Model Context Protocol) tools
        
        **Getting Started:**
        1. Upload documents using the sidebar
        2. Enable RAG mode for document-based responses
        3. Ask questions about your documents
        4. Use MCP tools for file operations
        
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
            
            # Show RAG context if available
            if message.get("rag_context") and message.get("has_context"):
                st.markdown(f"""
                <div class="rag-context">
                    <strong>📚 RAG Context Found:</strong><br>
                    {message["rag_context"][:300]}{"..." if len(message["rag_context"]) > 300 else ""}
                </div>
                """, unsafe_allow_html=True)

def main():
    """Main application function."""
    init_session_state()
    
    # Apply simple CSS
    st.markdown(get_css(), unsafe_allow_html=True)
    
    # Check backend health and get models
    st.session_state.backend_health = check_backend_health()
    if st.session_state.backend_health:
        st.session_state.available_models = get_available_models()
        st.session_state.conversations = get_conversations()
        st.session_state.rag_stats = get_rag_stats()
        
        # Debug output
        print(f"🔍 Main function - RAG Stats loaded: {st.session_state.rag_stats}")
    
    # Sidebar for conversations and settings
    with st.sidebar:
        # Force refresh button for debugging
        if st.button("🔄 Force Refresh All Data"):
            st.session_state.rag_stats = get_rag_stats()
            st.session_state.conversations = get_conversations()
            st.session_state.available_models = get_available_models()
            st.success("✅ All data refreshed!")
            st.rerun()
        
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
        
        # RAG Section (Collapsible)
        with st.expander("📚 RAG System", expanded=False):
            st.markdown('<div class="section-header">Document Upload</div>', unsafe_allow_html=True)
            
            if st.session_state.backend_health:
                uploaded_file = st.file_uploader(
                    "Upload a document for RAG",
                    type=['pdf', 'docx', 'txt', 'md'],
                    help="Upload PDF, DOCX, TXT, or MD files to enable RAG functionality"
                )
                
                if uploaded_file is not None:
                    if st.button("📤 Process Document"):
                        with st.spinner("Processing document..."):
                            result = upload_document_for_rag(uploaded_file)
                            
                            if result["success"]:
                                data = result["data"]
                                st.success(f"✅ {data.get('message', 'Document processed successfully')}")
                                st.info(f"📊 Created {data.get('chunks_created', 0)} chunks")
                                
                                # Wait a moment for the backend to update, then refresh stats
                                import time
                                time.sleep(1)
                                
                                # Refresh RAG stats
                                new_stats = get_rag_stats()
                                st.session_state.rag_stats = new_stats
                                
                                # Show updated stats immediately
                                if new_stats.get("total_documents", 0) > 0:
                                    st.success(f"📚 Updated: {new_stats['total_documents']} documents in RAG system")
                                
                                st.rerun()
                            else:
                                st.error(f"❌ {result['error']}")
                
                # RAG Statistics
                if st.session_state.rag_stats:
                    st.markdown('<div class="section-header">Statistics</div>', unsafe_allow_html=True)
                    stats = st.session_state.rag_stats
                    st.metric("Total Documents", stats.get("total_documents", 0))
                    st.metric("Total Chunks", stats.get("total_chunks", 0))
                    st.metric("Vector DB Size", f"{stats.get('vector_db_size_mb', 0):.1f} MB")
                    
                    # Debug info (can be removed later)
                    if st.checkbox("🔍 Show Debug Info"):
                        st.json(stats)
                    
                    if st.button("🔄 Refresh RAG Stats"):
                        new_stats = get_rag_stats()
                        st.session_state.rag_stats = new_stats
                        st.success(f"Stats refreshed: {new_stats.get('total_documents', 0)} documents")
                        st.rerun()
            else:
                st.warning("Backend not available for document upload")
            
            st.markdown('<div class="section-header">RAG Mode</div>', unsafe_allow_html=True)
            use_rag = st.checkbox(
                "Enable RAG for responses",
                value=st.session_state.use_rag,
                help="When enabled, responses will use document context from uploaded files"
            )
            st.session_state.use_rag = use_rag
            
            if use_rag:
                if st.session_state.rag_stats.get("total_documents", 0) == 0:
                    st.warning("⚠️ No documents uploaded. Upload documents to use RAG mode.")
                else:
                    st.success("✅ RAG mode enabled - responses will use document context")
        
        # MCP Tools Section (Collapsible)
        with st.expander("🛠️ MCP Tools", expanded=False):
            # Get MCP tools and health
            if st.session_state.backend_health:
                mcp_tools = get_mcp_tools()
                mcp_health = get_mcp_health()
                
                if mcp_health.get("mcp_enabled", False):
                    st.success("✅ MCP Tools Available")
                    
                    # Show available tools
                    if mcp_tools:
                        st.markdown('<div class="section-header">Available Tools</div>', unsafe_allow_html=True)
                        for tool in mcp_tools:
                            st.text(f"• {tool.get('name', 'Unknown')}")
                            st.caption(f"  {tool.get('description', 'No description')}")
                    
                    # Show server status
                    servers = mcp_health.get("servers", {})
                    if servers:
                        st.markdown('<div class="section-header">Server Status</div>', unsafe_allow_html=True)
                        for server_name, status in servers.items():
                            if status.get("running", False):
                                st.success(f"✅ {server_name}")
                            else:
                                st.error(f"❌ {server_name}")
                    
                    # Tool count
                    st.metric("Total Tools", mcp_health.get("tools_count", 0))
                    
                    # Refresh button
                    if st.button("🔄 Refresh MCP Status"):
                        st.session_state.mcp_tools = get_mcp_tools()
                        st.session_state.mcp_health = get_mcp_health()
                        st.rerun()
                else:
                    st.warning("⚠️ MCP Tools not available")
                    if st.button("🔄 Check MCP Status"):
                        st.session_state.mcp_health = get_mcp_health()
                        st.rerun()
            else:
                st.warning("Backend not available for MCP tools")
        
        # Conversations Section (Collapsible)
        with st.expander("💬 Conversations", expanded=True):
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
                st.markdown('<div class="section-header">Recent Conversations</div>', unsafe_allow_html=True)
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
        
        # Settings Section (Collapsible)
        with st.expander("⚙️ Settings", expanded=False):
            # Model selection
            if st.session_state.available_models:
                st.markdown('<div class="section-header">Model Configuration</div>', unsafe_allow_html=True)
                selected_model = st.selectbox(
                    "Select Model",
                    st.session_state.available_models,
                    index=0
                )
                
                # Temperature slider
                temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
            else:
                st.warning("No models available")
            
            # Chat settings
            st.markdown('<div class="section-header">Chat Settings</div>', unsafe_allow_html=True)
            use_streaming = st.checkbox(
                "Enable Streaming Responses",
                value=st.session_state.use_streaming,
                help="When enabled, responses will stream in real-time as they're generated"
            )
            st.session_state.use_streaming = use_streaming
            
            if use_streaming:
                st.success("✅ Streaming enabled - responses will appear in real-time")
            else:
                st.info("⏳ Streaming disabled - responses will appear all at once")
            
            # Backend status
            st.markdown('<div class="section-header">Backend Status</div>', unsafe_allow_html=True)
            if st.session_state.backend_health:
                st.success("✅ Connected")
            else:
                st.error("❌ Disconnected")
                st.info(f"Backend URL: {BACKEND_URL}")
            
            # Available models
            if st.session_state.available_models:
                st.markdown('<div class="section-header">Available Models</div>', unsafe_allow_html=True)
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
            # Send message to backend (with or without RAG)
            if st.session_state.use_rag and st.session_state.rag_stats.get("total_documents", 0) > 0:
                # Use streaming or regular RAG response based on setting
                if st.session_state.use_streaming:
                    # Use streaming RAG response
                    with st.spinner("Thinking with RAG..."):
                        response_data = send_streaming_rag_chat(prompt, st.session_state.conversation_id)
                else:
                    # Use regular non-streaming RAG response
                    with st.spinner("Thinking with RAG..."):
                        response_data = send_rag_chat(prompt, st.session_state.conversation_id)
            else:
                # Use streaming or regular response based on setting
                if st.session_state.use_streaming:
                    # Use streaming response
                    response_data = send_to_backend(prompt, st.session_state.conversation_id, use_streaming=True)
                else:
                    # Use regular non-streaming response
                    with st.spinner("Thinking..."):
                        response_data = send_to_backend(prompt, st.session_state.conversation_id, use_streaming=False)
            
            # Handle streaming RAG responses differently since they're already displayed
            if st.session_state.use_rag and st.session_state.use_streaming and st.session_state.rag_stats.get("total_documents", 0) > 0:
                # For streaming RAG, the response is already displayed in real-time
                if response_data and not response_data.get("response", "").startswith("❌"):
                    # Update conversation ID if provided
                    if response_data.get("conversation_id"):
                        st.session_state.conversation_id = response_data["conversation_id"]
                    
                    # Add assistant response to chat history
                    message_data = {"role": "assistant", "content": response_data["response"]}
                    
                    # Add RAG context if available (check for non-empty rag_context and has_context=True)
                    if response_data.get("rag_context") and response_data.get("has_context") == True:
                        message_data["rag_context"] = response_data["rag_context"]
                        message_data["has_context"] = response_data["has_context"]
                        # Add debug info to the message content
                        message_data["content"] += f"\n\n🔍 DEBUG: RAG context found: {response_data.get('rag_context', '')[:100]}..."
                    else:
                        # Add debug info if no RAG context
                        message_data["content"] += f"\n\n🔍 DEBUG: No RAG context found. response_data keys: {list(response_data.keys()) if response_data else 'None'}"
                        message_data["content"] += f"\n🔍 DEBUG: rag_context value: '{response_data.get('rag_context', 'None')}'"
                        message_data["content"] += f"\n🔍 DEBUG: has_context value: {response_data.get('has_context', 'None')}"
                    
                    st.session_state.messages.append(message_data)
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Force rerun to update sidebar
                    st.rerun()
                else:
                    error_msg = response_data["response"] if response_data else "❌ Unable to get response from backend. Please try again or check the backend logs."
                    # Add debug info to error message
                    error_msg += f"\n\n🔍 DEBUG: Error branch taken. response_data: {response_data}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.error(error_msg)
            else:
                # Handle regular responses (non-streaming or non-RAG)
                if response_data and not response_data["response"].startswith("❌"):
                    # Update conversation ID if provided
                    if response_data.get("conversation_id"):
                        st.session_state.conversation_id = response_data["conversation_id"]
                    
                    # Add assistant response to chat history
                    message_data = {"role": "assistant", "content": response_data["response"]}
                    
                    # Add RAG context if available
                    if response_data.get("rag_context") and response_data.get("has_context"):
                        message_data["rag_context"] = response_data["rag_context"]
                        message_data["has_context"] = response_data["has_context"]
                    
                    st.session_state.messages.append(message_data)
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Display assistant response (if not already displayed via streaming)
                    if not st.session_state.use_streaming:
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