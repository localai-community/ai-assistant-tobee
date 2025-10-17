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
import time
import threading
from functools import lru_cache

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Performance optimization: Create a global HTTP client with connection pooling
@st.cache_resource
def get_http_client():
    """Get a cached HTTP client with connection pooling for better performance."""
    return httpx.Client(
        timeout=httpx.Timeout(5.0),
        limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        http2=False  # Disable HTTP/2 to avoid dependency issues
    )

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
        .advanced-rag-info {
            background-color: #f0f8ff;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #0066cc;
            margin: 10px 0;
        }
        .strategy-badge {
            display: inline-block;
            background-color: #e6f3ff;
            color: #0066cc;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin: 2px;
        }
        .sample-button {
            background-color: #f0f8ff;
            border: 1px solid #0066cc;
            color: #0066cc;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 2px;
            font-size: 0.9em;
        }
        .sample-button:hover {
            background-color: #0066cc;
            color: white;
        }
        .stop-button {
            background-color: #dc3545;
            border: 1px solid #dc3545;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9em;
            font-weight: bold;
        }
        .stop-button:hover {
            background-color: #c82333;
            border-color: #c82333;
        }
        .stop-button:disabled {
            background-color: #6c757d;
            border-color: #6c757d;
            cursor: not-allowed;
        }
        
        /* Fixed chatbox at bottom */
        .stChatInput {
            position: fixed !important;
            bottom: 0 !important;
            left: 21rem !important; /* Account for sidebar width */
            right: 0 !important;
            z-index: 999 !important;
            background-color: transparent !important;
            border: none !important;
            padding: 1rem !important;
            box-shadow: none !important;
        }
        
        /* For mobile/smaller screens, adjust positioning */
        @media (max-width: 768px) {
            .stChatInput {
                left: 0 !important;
            }
        }
        
        /* Add bottom padding to main content to prevent overlap */
        .main .block-container {
            padding-bottom: 120px !important;
        }
        
        /* Ensure chat messages have proper spacing */
        .stChatMessage {
            margin-bottom: 1rem !important;
        }
        
        /* Style for button container - compact and right-aligned */
        .button-container {
            position: fixed !important;
            bottom: 1rem !important;
            right: 1rem !important;
            z-index: 1000 !important;
            width: auto !important;
            max-width: 300px !important;
        }
        
        /* Style for button columns to be compact */
        .button-container .stColumns {
            gap: 0.3rem !important;
        }
        
        .button-container .stColumn {
            padding: 0 !important;
        }
        
        /* Style buttons within the container to be compact */
        .button-container button {
            width: 100% !important;
            padding: 6px 10px !important;
            font-size: 0.8em !important;
            margin: 0 !important;
            min-width: auto !important;
        }
        
        /* Make the spacer column invisible */
        .button-container .stColumn:last-child {
            display: none !important;
        }
        
        /* Style for stop button container */
        .stop-button-container {
            position: relative !important;
            bottom: auto !important;
            right: auto !important;
        }
        
        /* Style for upload button container */
        .upload-button-container {
            position: relative !important;
            bottom: auto !important;
            right: auto !important;
        }
        
        /* Style for upload button */
        .upload-button-container button {
            background-color: #4CAF50 !important;
            border: 1px solid #4CAF50 !important;
            color: white !important;
            padding: 8px 16px !important;
            border-radius: 6px !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            font-size: 0.9em !important;
            font-weight: bold !important;
        }
        
        .upload-button-container button:hover {
            background-color: #45a049 !important;
            border-color: #45a049 !important;
        }
        
        /* Hidden file uploader */
        .hidden-file-uploader {
            display: none !important;
        }
        
        /* For mobile/smaller screens, adjust stop button positioning */
        @media (max-width: 768px) {
            .stop-button-container {
                right: 1rem !important;
            }
        }
        
        /* Style for stop button */
        .stop-button-container button {
            background-color: #dc3545 !important;
            border: 1px solid #dc3545 !important;
            color: white !important;
            padding: 8px 16px !important;
            border-radius: 6px !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            font-size: 0.9em !important;
            font-weight: bold !important;
        }
        
        .stop-button-container button:hover {
            background-color: #c82333 !important;
            border-color: #c82333 !important;
        }
        
        .stop-button-container button:disabled {
            background-color: #6c757d !important;
            border-color: #6c757d !important;
            cursor: not-allowed !important;
        }
    </style>
    """

def get_default_user_settings():
    """Get default user settings."""
    return {
        "enable_context_awareness": True,
        "include_memory": False,
        "context_strategy": "conversation_only",
        "user_id": "leia",
        "selected_model": "llama3:latest",
        "use_rag": False,
        "use_advanced_rag": False,
        "use_phase2_reasoning": False,
        "use_reasoning_chat": False,
        "use_phase3_reasoning": False,
        "selected_phase2_engine": "auto",
        "selected_phase3_strategy": "auto",
        "use_unified_reasoning": False,
        "selected_reasoning_mode": "auto",
        "temperature": 0.7
    }

def save_user_settings():
    """Save current user settings to database."""
    try:
        # Sync user_id to URL for persistence across page refreshes
        sync_user_id_to_url()
        
        settings = {
            "enable_context_awareness": st.session_state.enable_context_awareness,
            "include_memory": st.session_state.include_memory,
            "context_strategy": st.session_state.context_strategy,
            "selected_model": st.session_state.selected_model,
            "use_rag": st.session_state.use_rag,
            "use_advanced_rag": st.session_state.use_advanced_rag,
            "use_phase2_reasoning": st.session_state.use_phase2_reasoning,
            "use_reasoning_chat": st.session_state.use_reasoning_chat,
            "use_phase3_reasoning": st.session_state.use_phase3_reasoning,
            "selected_phase2_engine": st.session_state.selected_phase2_engine,
            "selected_phase3_strategy": st.session_state.selected_phase3_strategy,
            "use_unified_reasoning": st.session_state.use_unified_reasoning,
            "selected_reasoning_mode": st.session_state.selected_reasoning_mode,
            "temperature": st.session_state.temperature
        }
        
        # Make API call to save settings
        import httpx
        with httpx.Client() as client:
            response = client.post(
                f"{BACKEND_URL}/api/v1/user-settings/{st.session_state.user_id}/upsert",
                json=settings,
                timeout=10.0
            )
            
            if response.status_code == 200:
                # Settings saved successfully
                pass
            else:
                st.error(f"Failed to save settings: {response.status_code}")
                
    except Exception as e:
        st.error(f"Error saving settings: {str(e)}")

def load_user_settings_from_database(user_id: str):
    """Load user settings from database."""
    try:
        import httpx
        with httpx.Client() as client:
            response = client.get(
                f"{BACKEND_URL}/api/v1/user-settings/{user_id}",
                timeout=10.0
            )
            
            if response.status_code == 200:
                settings = response.json()
                return settings
            else:
                # Return default settings if not found
                return get_default_user_settings()
                
    except Exception as e:
        st.error(f"Error loading settings: {str(e)}")
        return get_default_user_settings()

def sync_user_id_to_url():
    """Sync user_id to URL query params for persistence across refreshes."""
    if "user_id" in st.session_state and st.session_state.user_id:
        # Update URL to include user_id
        current_params = dict(st.query_params)
        if current_params.get("uid") != st.session_state.user_id:
            current_params["uid"] = st.session_state.user_id
            st.query_params.update(current_params)

def init_session_state():
    """Initialize session state variables with persistent settings."""
    default_settings = get_default_user_settings()
    
    # Initialize basic session state (non-persistent)
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
    if "mcp_tools" not in st.session_state:
        st.session_state.mcp_tools = []
    if "mcp_health" not in st.session_state:
        st.session_state.mcp_health = {}
    if "advanced_rag_strategies" not in st.session_state:
        st.session_state.advanced_rag_strategies = []
    if "sample_question" not in st.session_state:
        st.session_state.sample_question = None
    if "chat_input_key" not in st.session_state:
        st.session_state.chat_input_key = 0
    if "temp_phase_override" not in st.session_state:
        st.session_state.temp_phase_override = None
    if "context_info" not in st.session_state:
        st.session_state.context_info = {}
    
    # Initialize user_id from URL query params if available
    # This needs to happen before loading other settings
    query_params = st.query_params
    stored_user_id = query_params.get("uid", None)
    
    # Initialize user settings with defaults first, but use stored_user_id if available
    for key, default_value in default_settings.items():
        if key not in st.session_state:
            # Use stored user_id from URL if available, otherwise use default
            if key == "user_id" and stored_user_id:
                st.session_state[key] = stored_user_id
            else:
                st.session_state[key] = default_value
    
    # Load settings from database if not already loaded
    if "settings_loaded" not in st.session_state:
        st.session_state.settings_loaded = True
        # Load settings from database
        db_settings = load_user_settings_from_database(st.session_state.user_id)
        # Apply database settings to session state
        for key, value in db_settings.items():
            if key != "user_id" and key in st.session_state:  # Don't override user_id
                st.session_state[key] = value
    
    # Check URL parameters for settings override (for sharing settings via URL)
    query_params = st.query_params
    for key in default_settings.keys():
        if key in query_params:
            value = query_params[key]
            if key in ["enable_context_awareness", "include_memory", "use_rag", "use_advanced_rag", "use_phase2_reasoning", "use_reasoning_chat", "use_phase3_reasoning"]:
                st.session_state[key] = value.lower() in ['true', '1', 'yes']
            elif key == "temperature":
                try:
                    st.session_state[key] = float(value)
                except ValueError:
                    st.session_state[key] = default_settings[key]
            else:
                st.session_state[key] = value
    
    # Add stop button state variable
    if "stop_generation" not in st.session_state:
        st.session_state.stop_generation = False
    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False
    # Add Phase 2 reasoning engine state variables
    # Force disable reasoning by default to prevent interference with context awareness
    st.session_state.use_phase2_reasoning = False
    if "selected_phase2_engine" not in st.session_state:
        st.session_state.selected_phase2_engine = "auto"
    if "phase2_engine_status" not in st.session_state:
        st.session_state.phase2_engine_status = {}
    if "phase2_sample_questions" not in st.session_state:
        st.session_state.phase2_sample_questions = {
            "mathematical": [
                "Solve 2x + 3 = 7",
                "Calculate the area of a circle with radius 5",
                "Find the derivative of x² + 3x + 1",
                "Solve the quadratic equation x² - 4x + 3 = 0"
            ],
            "logical": [
                "All A are B. Some B are C. What can we conclude?",
                "If P then Q. P is true. Is Q necessarily true?",
                "Evaluate the logical expression: (A AND B) OR (NOT A)",
                "Prove that if x > 0 and y > 0, then x + y > 0"
            ],
            "causal": [
                "Does smoking cause lung cancer? Assume S = smoking, L = lung cancer",
                "What is the causal effect of education on income?",
                "Does exercise cause better health outcomes?",
                "Analyze the causal relationship between diet and weight loss"
            ]
        }
    
    # Phase 3 Advanced Reasoning Strategies
    # Force disable phase 3 reasoning by default
    st.session_state.use_phase3_reasoning = False
    if "selected_phase3_strategy" not in st.session_state:
        st.session_state.selected_phase3_strategy = "auto"
    if "phase3_health" not in st.session_state:
        st.session_state.phase3_health = {}
    if "phase3_sample_questions" not in st.session_state:
        st.session_state.phase3_sample_questions = {
            "chain_of_thought": [
                "What is 15 + 27? Show your work step by step.",
                "If a train travels 60 mph for 2 hours, how far does it go?",
                "Calculate the perimeter of a rectangle with length 8 and width 5",
                "Solve: 3x + 4 = 16"
            ],
            "tree_of_thoughts": [
                "How can I design a scalable microservices architecture?",
                "What are the best strategies for implementing user authentication?",
                "How should I approach building a recommendation system?",
                "What's the optimal way to structure a database for an e-commerce site?"
            ],
            "prompt_engineering": [
                "Create a prompt for explaining quantum computing to a high school student",
                "Design a prompt for analyzing customer feedback sentiment",
                "Write a prompt for generating creative writing ideas",
                "Craft a prompt for debugging code issues"
            ]
        }
    
    # Unified Reasoning System
    # Initialize unified reasoning system state variables
    if "use_unified_reasoning" not in st.session_state:
        st.session_state.use_unified_reasoning = False
    if "selected_reasoning_mode" not in st.session_state:
        st.session_state.selected_reasoning_mode = "auto"
    if "unified_reasoning_status" not in st.session_state:
        st.session_state.unified_reasoning_status = {}
    if "temp_reasoning_override" not in st.session_state:
        st.session_state.temp_reasoning_override = None


@st.cache_data(ttl=30)  # Cache for 30 seconds
def check_backend_health() -> bool:
    """Check if the backend is healthy."""
    try:
        client = get_http_client()
        response = client.get(f"{BACKEND_URL}/health")
        return response.status_code == 200
    except:
        return False

def get_selected_model() -> str:
    """Get the currently selected model or fallback to first available."""
    if st.session_state.selected_model:
        return st.session_state.selected_model
    elif st.session_state.available_models:
        return st.session_state.available_models[0]
    else:
        return "llama3:latest"

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_available_models() -> List[str]:
    """Get available models from backend with llama3:latest prioritized."""
    try:
        client = get_http_client()
        response = client.get(f"{BACKEND_URL}/api/v1/chat/models")
        if response.status_code == 200:
            models = response.json()
            # Prioritize llama3:latest as the first model
            if "llama3:latest" in models:
                models.remove("llama3:latest")
                models.insert(0, "llama3:latest")
            return models
    except:
        pass
    return []

@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_conversations() -> List[Dict]:
    """Get conversations from backend."""
    try:
        client = get_http_client()
        response = client.get(f"{BACKEND_URL}/api/v1/chat/conversations")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def get_rag_stats() -> Dict:
    """Get RAG statistics from backend - simplified version."""
    # RAG service removed, return empty stats
    return {}

def get_advanced_rag_strategies() -> List[Dict]:
    """Get available advanced RAG strategies from backend - simplified version."""
    # Advanced RAG service removed, return empty strategies
    return {}

def get_advanced_rag_health() -> Dict:
    """Get advanced RAG health status - simplified version."""
    # Advanced RAG service removed, return unhealthy status
    return {"status": "unhealthy", "error": "Service removed"}

def get_mcp_tools() -> List[Dict]:
    """Get MCP tools from backend."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/chat/tools", timeout=5.0)
            if response.status_code == 200:
                return response.json()
    except:
        pass
    return []

def get_mcp_health() -> Dict:
    """Get MCP health status."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/chat/tools/health", timeout=5.0)
            if response.status_code == 200:
                return response.json()
    except:
        pass
    return {}


def get_reasoning_health() -> Dict:
    """Get reasoning system health status."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/reasoning/health", timeout=5.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def parse_problem(problem_statement: str) -> Dict:
    """Parse a problem statement using the reasoning system."""
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{BACKEND_URL}/reasoning/parse-problem",
                json={"problem_statement": problem_statement},
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_steps(step_output: str) -> Dict:
    """Parse step-by-step reasoning output."""
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{BACKEND_URL}/reasoning/parse-steps",
                json={"step_output": step_output},
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def validate_reasoning(problem_statement: str, steps: List[Dict], final_answer: str = None, confidence: float = 0.0) -> Dict:
    """Validate reasoning using the reasoning system."""
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{BACKEND_URL}/reasoning/validate",
                json={
                    "problem_statement": problem_statement,
                    "steps": steps,
                    "final_answer": final_answer,
                    "confidence": confidence
                },
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def format_reasoning(problem_statement: str, steps: List[Dict], final_answer: str = None, 
                    confidence: float = 0.0, format_type: str = "json") -> Dict:
    """Format reasoning result in the specified format."""
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{BACKEND_URL}/reasoning/format",
                json={
                    "problem_statement": problem_statement,
                    "steps": steps,
                    "final_answer": final_answer,
                    "confidence": confidence,
                    "format_type": format_type
                },
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def test_reasoning_workflow(problem_statement: str, format_type: str = "json") -> Dict:
    """Test the complete reasoning workflow."""
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{BACKEND_URL}/reasoning/test-workflow",
                json={
                    "problem_statement": problem_statement,
                    "format_type": format_type
                },
                timeout=15.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_reasoning_chat(message: str, conversation_id: Optional[str] = None, use_streaming: bool = False) -> Optional[Dict]:
    """Send message to backend with reasoning enhancement."""
    try:
        with httpx.Client() as client:
            # Use the first available model or fallback to llama3:latest
            model = get_selected_model()
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "use_reasoning": True,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True,
                "enable_context_awareness": st.session_state.enable_context_awareness,
                "include_memory": st.session_state.include_memory,
                "context_strategy": st.session_state.context_strategy
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            # Use regular endpoint (streaming will be handled separately)
            response = client.post(
                f"{BACKEND_URL}/api/v1/reasoning-chat/",
                json=payload,
                timeout=120.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "response": data.get("response", "No response from backend"),
                    "conversation_id": data.get("conversation_id"),
                    "reasoning_used": data.get("reasoning_used", False),
                    "steps_count": data.get("steps_count"),
                    "validation_summary": data.get("validation_summary")
                }
            elif response.status_code == 503:
                return {"response": "❌ Ollama service is not available. Please make sure Ollama is running."}
            else:
                return {"response": f"Backend error: {response.status_code}"}
                    
    except httpx.TimeoutException:
        return {"response": "Request timed out. Please try again."}
    except Exception as e:
        return {"response": f"Communication error: {str(e)}"}


def send_streaming_reasoning_chat(message: str, conversation_id: Optional[str] = None):
    """Send message to backend with reasoning enhancement using streaming."""
    try:
        with httpx.Client() as client:
            # Use the first available model or fallback to llama3:latest
            model = get_selected_model()
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "use_reasoning": True,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True,
                "enable_context_awareness": st.session_state.enable_context_awareness,
                "include_memory": st.session_state.include_memory,
                "context_strategy": st.session_state.context_strategy
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            # Use streaming endpoint
            with client.stream(
                "POST",
                f"{BACKEND_URL}/api/v1/reasoning-chat/stream",
                json=payload,
                timeout=120.0
            ) as response:
                if response.status_code == 200:
                    # Handle streaming response
                    full_response = ""
                    
                    for line in response.iter_lines():
                        if line:
                            # Handle SSE format
                            if line.startswith('data: '):
                                try:
                                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                                    content = data.get('content', '')
                                    full_response += content
                                    yield content
                                except json.JSONDecodeError:
                                    continue
                            else:
                                # Direct text response (fallback)
                                full_response += line
                                yield line
                    
                    # Return final response data
                    yield {
                        "response": full_response,
                        "conversation_id": conversation_id,
                        "reasoning_used": True
                    }
                else:
                    yield {"response": f"Backend error: {response.status_code}"}
                    
    except httpx.TimeoutException:
        yield {"response": "Request timed out. Please try again."}
    except Exception as e:
        yield {"response": f"Communication error: {str(e)}"}

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

def upload_document_for_rag(uploaded_file, conversation_id: Optional[str] = None, user_id: Optional[str] = None) -> Dict:
    """Upload a document for RAG processing with conversation-scoped storage."""
    try:
        with httpx.Client() as client:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            data = {}
            
            # Add conversation and user context if available
            if conversation_id:
                data["conversation_id"] = conversation_id
            if user_id:
                data["user_id"] = user_id
            
            response = client.post(
                f"{BACKEND_URL}/api/v1/chat/upload", 
                files=files, 
                data=data,
                timeout=60.0
            )
            if response.status_code == 200:
                result = response.json()
                return {"success": True, "data": result}
            else:
                return {"success": False, "error": f"Upload failed: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"success": False, "error": f"Upload error: {str(e)}"}

def generate_upload_response(filename: str, conversation_id: Optional[str]) -> Optional[str]:
    """Generate automatic LLM response for uploaded document."""
    try:
        # Create a message that will trigger document context inclusion
        message = f"Please analyze the document I just uploaded ({filename}) and provide a brief overview of its contents. What are the main topics or key points covered in this document?"
        
        # Use the backend chat API with context awareness enabled
        payload = {
            "message": message,
            "model": get_selected_model(),
            "temperature": 0.7,
            "enable_context_awareness": True,
            "include_memory": False,
            "context_strategy": "conversation_only"
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        # Get user_id safely
        user_id = getattr(st.session_state, 'user_id', None)
        if user_id:
            payload["user_id"] = user_id
        
        with httpx.Client() as client:
            response = client.post(
                f"{BACKEND_URL}/api/v1/chat/stream",
                json=payload,
                timeout=60.0  # Increased timeout for document analysis
            )
            
            if response.status_code == 200:
                # For streaming response, we need to collect all chunks
                full_response = ""
                for line in response.iter_lines():
                    if line.strip():
                        try:
                            # Parse SSE format
                            if line.startswith("data: "):
                                data_str = line[6:]  # Remove "data: " prefix
                                data = json.loads(data_str)
                                if data.get("type") == "content":
                                    full_response += data.get("content", "")
                        except json.JSONDecodeError:
                            continue
                
                # If we got a meaningful response, return it
                if full_response and len(full_response.strip()) > 50:
                    return full_response
                else:
                    # Fallback response with more detail
                    return f"📄 **Document Analysis Complete**\n\n✅ **{filename}** has been successfully processed and is now available for questions!\n\n🔍 **What I can help you with:**\n- Ask specific questions about the document content\n- Request summaries of key sections\n- Get insights and analysis from the document\n- Find specific information or topics\n\n💡 **Try asking:**\n- \"What are the main topics in this document?\"\n- \"Summarize the key points\"\n- \"What does this document say about [specific topic]?\""
            else:
                print(f"🔍 DEBUG: Upload response generation failed: {response.status_code}")
                return f"📄 **Document Analysis Complete**\n\n✅ **{filename}** has been successfully processed and is now available for questions!\n\n🔍 **What I can help you with:**\n- Ask specific questions about the document content\n- Request summaries of key sections\n- Get insights and analysis from the document\n- Find specific information or topics\n\n💡 **Try asking:**\n- \"What are the main topics in this document?\"\n- \"Summarize the key points\"\n- \"What does this document say about [specific topic]?\""
                
    except Exception as e:
        print(f"🔍 DEBUG: Error generating upload response: {e}")
        return f"📄 **Document Analysis Complete**\n\n✅ **{filename}** has been successfully processed and is now available for questions!\n\n🔍 **What I can help you with:**\n- Ask specific questions about the document content\n- Request summaries of key sections\n- Get insights and analysis from the document\n- Find specific information or topics\n\n💡 **Try asking:**\n- \"What are the main topics in this document?\"\n- \"Summarize the key points\"\n- \"What does this document say about [specific topic]?\""

def get_conversation_documents(conversation_id: str) -> Dict:
    """Get all documents for a conversation."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/chat/documents/{conversation_id}")
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to get documents: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"success": False, "error": f"Error getting documents: {str(e)}"}

def send_advanced_rag_chat(message: str, conversation_id: Optional[str] = None) -> Optional[Dict]:
    """Send message to backend with advanced RAG enhancement - simplified version."""
    # Advanced RAG service removed, use regular streaming chat instead
    return send_streaming_chat(message, conversation_id)

def send_rag_chat(message: str, conversation_id: Optional[str] = None) -> Optional[Dict]:
    """Send message to backend with RAG enhancement - simplified version."""
    # RAG service removed, use regular streaming chat instead
    return send_streaming_chat(message, conversation_id)

def send_streaming_rag_chat(message: str, conversation_id: Optional[str] = None) -> Optional[Dict]:
    """Send message to backend with RAG enhancement and streaming response - simplified version."""
    # RAG service removed, use regular streaming chat instead
    return send_streaming_chat(message, conversation_id)

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
    print(f"🔍 DEBUG: Starting basic streaming chat function")
    try:
        with httpx.Client() as client:
            # Use the first available model or fallback to llama3:latest
            model = get_selected_model()
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "stream": True,
                "enable_context_awareness": st.session_state.enable_context_awareness,
                "include_memory": st.session_state.include_memory,
                "context_strategy": st.session_state.context_strategy
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            if st.session_state.user_id:
                payload["user_id"] = st.session_state.user_id
            
            # Create assistant message container for streaming
            with st.chat_message("assistant"):
                # Create containers for thinking and answer in the correct order
                thinking_container = st.empty()  # This will hold the expandable thinking box
                answer_placeholder = st.empty()  # This will hold the final answer
                full_response = ""
                thinking_content = ""
                answer_content = ""
                is_deepseek_format = False
                in_thinking_phase = False
                thinking_stream_placeholder = None
                
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
                            # Check for stop signal
                            if st.session_state.stop_generation:
                                print(f"🔍 DEBUG: Stop signal detected in basic streaming chat!")
                                if is_deepseek_format:
                                    display_deepseek_response(thinking_content, answer_content, answer_placeholder, create_expander=False)
                                else:
                                    answer_placeholder.markdown(full_response + "\n\n*Generation stopped by user.*")
                                return {"response": full_response + "\n\n*Generation stopped by user.*", "stopped": True}
                            
                            if line:
                                # httpx.iter_lines() returns strings, not bytes
                                if line.startswith('data: '):
                                    try:
                                        data = json.loads(line[6:])  # Remove 'data: ' prefix
                                        chunk = data.get('content', '')
                                        chunk_type = data.get('type', 'content')
                                        
                                        if chunk_type == 'metadata':
                                            # Extract conversation ID from metadata chunk
                                            if 'conversation_id' in data:
                                                conversation_id = data['conversation_id']
                                                print(f"🔍 DEBUG: Received conversation_id from stream: {conversation_id}")
                                        
                                        full_response += chunk
                                        
                                        # Check for DeepSeek reasoning format
                                        if '<think>' in full_response and not is_deepseek_format:
                                            is_deepseek_format = True
                                            in_thinking_phase = True
                                            # Create expandable thinking section immediately in the thinking container
                                            with thinking_container.container():
                                                with st.expander("🧠 View Reasoning Process", expanded=False):
                                                    thinking_stream_placeholder = st.empty()
                                        
                                        if is_deepseek_format:
                                            # Extract current thinking content for streaming
                                            if '<think>' in full_response:
                                                # Get the thinking content up to the current point
                                                think_start = full_response.find('<think>')
                                                if '</think>' in full_response:
                                                    # Complete thinking section
                                                    think_end = full_response.find('</think>')
                                                    current_thinking = full_response[think_start + 7:think_end].strip()
                                                    
                                                    # Update thinking content in expandable section
                                                    if thinking_stream_placeholder and current_thinking:
                                                        thinking_stream_placeholder.markdown(f'<div style="color: #888888;">{current_thinking}</div>', unsafe_allow_html=True)
                                                    
                                                    # Parse and show answer content
                                                    parsed = parse_deepseek_reasoning(full_response)
                                                    if parsed['is_deepseek_format']:
                                                        thinking_content = parsed['thinking']
                                                        answer_content = parsed['answer']
                                                        
                                                        # Show answer content (or partial if still streaming)
                                                        if answer_content:
                                                            answer_placeholder.markdown(answer_content + "▌")
                                                        else:
                                                            answer_placeholder.markdown("🧠 *Thinking...*")
                                                    else:
                                                        answer_placeholder.markdown(full_response + "▌")
                                                else:
                                                    # Still in thinking phase, stream the thinking content
                                                    current_thinking = full_response[think_start + 7:].strip()
                                                    
                                                    # Update thinking content in expandable section
                                                    if thinking_stream_placeholder and current_thinking:
                                                        thinking_stream_placeholder.markdown(f'<div style="color: #888888;">{current_thinking}▌</div>', unsafe_allow_html=True)
                                                    
                                                    # Show thinking indicator in answer area
                                                    answer_placeholder.markdown("🧠 *Thinking...*")
                                            else:
                                                # Not yet in DeepSeek format, show regular streaming
                                                answer_placeholder.markdown(full_response + "▌")
                                        else:
                                            # Regular response, show normal streaming
                                            answer_placeholder.markdown(full_response + "▌")
                                            
                                    except json.JSONDecodeError:
                                        continue
                                elif line.strip() == '':  # Empty line indicates end of SSE
                                    continue
                        
                        # Final update without cursor
                        if is_deepseek_format:
                            # Parse final response and display properly
                            parsed = parse_deepseek_reasoning(full_response)
                            if parsed['is_deepseek_format']:
                                # Just show the final answer, thinking is already displayed in expandable box
                                if parsed['answer'].strip():
                                    answer_placeholder.markdown(parsed['answer'])
                                else:
                                    answer_placeholder.markdown(parsed['thinking'])
                            else:
                                answer_placeholder.markdown(full_response)
                        else:
                            answer_placeholder.markdown(full_response)
                        
                        return {
                            "response": full_response,
                            "conversation_id": conversation_id
                        }
                    elif response.status_code == 503:
                        error_msg = "❌ Ollama service is not available. Please make sure Ollama is running."
                        answer_placeholder.error(error_msg)
                        return {"response": error_msg}
                    else:
                        error_msg = f"Backend error: {response.status_code}"
                        answer_placeholder.error(error_msg)
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
            model = get_selected_model()
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "stream": False,
                "enable_context_awareness": st.session_state.enable_context_awareness,
                "include_memory": st.session_state.include_memory,
                "context_strategy": st.session_state.context_strategy
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            if st.session_state.user_id:
                payload["user_id"] = st.session_state.user_id
            
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

def parse_deepseek_reasoning(response_text: str) -> dict:
    """
    Parse DeepSeek reasoning format with <think>...</think> tags.
    
    Args:
        response_text: The full response text from DeepSeek
        
    Returns:
        dict: Contains 'thinking', 'answer', and 'is_deepseek_format' keys
    """
    import re
    
    # Check if response contains DeepSeek reasoning format
    think_pattern = r'<think>(.*?)</think>'
    matches = re.findall(think_pattern, response_text, re.DOTALL)
    
    if matches:
        # Extract thinking content
        thinking_content = matches[0].strip()
        
        # Extract answer content (everything after </think>)
        answer_pattern = r'</think>(.*)'
        answer_match = re.search(answer_pattern, response_text, re.DOTALL)
        answer_content = answer_match.group(1).strip() if answer_match else ""
        
        return {
            'thinking': thinking_content,
            'answer': answer_content,
            'is_deepseek_format': True
        }
    else:
        # Not DeepSeek format, return as regular response
        return {
            'thinking': "",
            'answer': response_text,
            'is_deepseek_format': False
        }

def display_deepseek_response(thinking_content: str, answer_content: str, message_placeholder, create_expander=True):
    """
    Display DeepSeek response with expandable thinking section.
    
    Args:
        thinking_content: The thinking/reasoning content
        answer_content: The final answer content
        message_placeholder: Streamlit placeholder for the message
        create_expander: Whether to create the expandable thinking section (True for history, False for streaming)
    """
    if create_expander and thinking_content.strip():
        # Create expandable thinking section for conversation history
        with st.expander("🧠 View Reasoning Process", expanded=False):
            st.markdown(f'<div style="color: #888888;">{thinking_content}</div>', unsafe_allow_html=True)
    
    # Display the final answer
    if answer_content.strip():
        message_placeholder.markdown(answer_content)
    else:
        # If no answer content, show the full response (fallback)
        message_placeholder.markdown(thinking_content)

def test_deepseek_parsing():
    """Test function to verify DeepSeek reasoning format parsing works correctly."""
    # Test case 1: Normal DeepSeek response
    test_response_1 = """<think>
I need to solve this math problem step by step.
First, I'll identify what's being asked.
The problem is asking for the area of a circle with radius 5.
The formula for area of a circle is A = πr².
So A = π × 5² = π × 25 = 25π.
</think>

The area of a circle with radius 5 is **25π** square units.

To calculate this:
1. Use the formula: A = πr²
2. Substitute r = 5: A = π × 5²
3. Calculate: A = π × 25 = 25π

Therefore, the answer is 25π square units."""

    # Test case 2: Regular response (not DeepSeek format)
    test_response_2 = "This is a regular response without thinking tags."

    # Test case 3: Empty thinking section
    test_response_3 = """<think></think>
This is the answer without any thinking process."""

    # Test case 4: Streaming simulation - partial response
    test_response_4 = """<think>
First, the user asked "What is 2+2? Show your thinking process."
I need to solve this step by step."""

    print("Testing DeepSeek parsing...")
    
    # Test case 1
    result_1 = parse_deepseek_reasoning(test_response_1)
    print(f"Test 1 - Is DeepSeek format: {result_1['is_deepseek_format']}")
    print(f"Test 1 - Thinking length: {len(result_1['thinking'])}")
    print(f"Test 1 - Answer length: {len(result_1['answer'])}")
    
    # Test case 2
    result_2 = parse_deepseek_reasoning(test_response_2)
    print(f"Test 2 - Is DeepSeek format: {result_2['is_deepseek_format']}")
    print(f"Test 2 - Answer: {result_2['answer'][:50]}...")
    
    # Test case 3
    result_3 = parse_deepseek_reasoning(test_response_3)
    print(f"Test 3 - Is DeepSeek format: {result_3['is_deepseek_format']}")
    print(f"Test 3 - Thinking empty: {not result_3['thinking'].strip()}")
    print(f"Test 3 - Answer: {result_3['answer'][:50]}...")
    
    # Test case 4 - partial response (should not be detected as DeepSeek format yet)
    result_4 = parse_deepseek_reasoning(test_response_4)
    print(f"Test 4 - Is DeepSeek format: {result_4['is_deepseek_format']}")
    print(f"Test 4 - Answer: {result_4['answer'][:50]}...")
    
    print("DeepSeek parsing tests completed!")

def test_streaming_simulation():
    """Test function to simulate streaming chunks and verify the logic works."""
    print("\nTesting streaming simulation...")
    
    # Simulate streaming chunks
    chunks = [
        '<think>',
        '\nFirst, the user asked "What is 2+2? Show your thinking process."\n',
        'I need to solve this step by step.\n',
        '2 + 2 = 4\n',
        '</think>\n\n',
        'The answer is **4**.\n\n',
        'Here\'s the step-by-step solution:\n',
        '1. Start with 2\n',
        '2. Add 2 to it\n',
        '3. Result is 4'
    ]
    
    full_response = ""
    is_deepseek_format = False
    
    for i, chunk in enumerate(chunks):
        full_response += chunk
        print(f"Chunk {i+1}: '{chunk}'")
        print(f"Full response so far: '{full_response[:50]}...'")
        
        # Check for DeepSeek reasoning format
        if '<think>' in full_response and not is_deepseek_format:
            is_deepseek_format = True
            print(f"  -> DeepSeek format detected!")
        
        if is_deepseek_format:
            if '</think>' in full_response:
                print(f"  -> Complete thinking section found!")
                parsed = parse_deepseek_reasoning(full_response)
                if parsed['is_deepseek_format']:
                    print(f"  -> Parsed successfully!")
                    print(f"  -> Thinking: '{parsed['thinking'][:50]}...'")
                    print(f"  -> Answer: '{parsed['answer'][:50]}...'")
                else:
                    print(f"  -> Parsing failed!")
            else:
                print(f"  -> Still in thinking phase...")
        else:
            print(f"  -> Regular response...")
        print()
    
    print("Streaming simulation completed!")

def display_welcome_message():
    """Display welcome message and status information."""
    st.markdown('<h1 class="main-header">LocalAI - Ask Tobee</h1>', unsafe_allow_html=True)
    
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
    



def extract_rag_context_from_content(content: str) -> str:
    """Extract RAG context from response content by looking for document references."""
    import re
    
    # Look for specific document references like "Document 1:", "Document 2:", etc.
    doc_pattern = r'Document \d+:[^.!?]*[.!?]'
    matches = re.findall(doc_pattern, content)
    
    if matches:
        return " ".join(matches)
    
    # Look for document references with quotes (like "Sequence to Sequence Learning")
    quoted_doc_pattern = r'Document \d+:\s*["\']([^"\']+)["\']'
    quoted_matches = re.findall(quoted_doc_pattern, content)
    
    if quoted_matches:
        return f"Document references: {', '.join(quoted_matches)}"
    
    # Look for any mention of "Document" followed by content
    any_doc_pattern = r'Document \d+[^.!?]*[.!?]'
    any_matches = re.findall(any_doc_pattern, content)
    
    if any_matches:
        return " ".join(any_matches)
    
    # Look for specific document titles or names in quotes
    doc_title_pattern = r'["\']([^"\']+(?:attention|transformer|neural|machine|learning)[^"\']*)["\']'
    title_matches = re.findall(doc_title_pattern, content, re.IGNORECASE)
    
    if title_matches:
        return f"Referenced documents: {', '.join(title_matches)}"
    
    # If no specific references found, don't extract general content
    return ""

def process_chat_response(response_data, question):
    """Process chat response and add to session state."""
    if response_data and isinstance(response_data, dict) and not response_data.get("response", "").startswith("❌"):
        # Update conversation ID if provided
        if response_data.get("conversation_id"):
            st.session_state.conversation_id = response_data["conversation_id"]
        
        # Add assistant response to chat history
        message_data = {"role": "assistant", "content": response_data["response"]}
        
        # Handle advanced RAG information
        if st.session_state.use_advanced_rag and response_data.get("strategies_used"):
            strategies_used = response_data.get("strategies_used", [])
            results_count = response_data.get("results_count", 0)
            
            # Add advanced RAG info to the message
            advanced_info = f"\n\n🚀 **Advanced RAG Info:**\n"
            advanced_info += f"• Strategies used: {', '.join(strategies_used)}\n"
            advanced_info += f"• Results retrieved: {results_count}\n"
            
            if response_data.get("has_context"):
                advanced_info += "• Context-aware retrieval: ✅\n"
            else:
                advanced_info += "• Context-aware retrieval: ❌\n"
            
            # Add document references from results
            if response_data.get("results"):
                doc_references = []
                for i, result in enumerate(response_data["results"][:3]):  # Show first 3 results
                    filename = result.get("filename", f"Document {i+1}")
                    strategy = result.get("strategy", "unknown")
                    score = result.get("relevance_score", 0)
                    doc_references.append(f"{filename} ({strategy}, score: {score:.2f})")
                
                if doc_references:
                    advanced_info += f"• Documents used: {', '.join(doc_references)}\n"
            
            message_data["content"] += advanced_info
            message_data["advanced_rag"] = True
            message_data["strategies_used"] = strategies_used
            message_data["results_count"] = results_count
        
        # Add RAG context if available (for basic RAG)
        if not st.session_state.use_advanced_rag and response_data.get("rag_context") and response_data.get("has_context"):
            message_data["rag_context"] = response_data["rag_context"]
            message_data["has_context"] = response_data["has_context"]
        
        # Add reasoning metadata
        if response_data.get("reasoning_used"):
            message_data["reasoning_used"] = True
            message_data["steps_count"] = response_data.get("steps_count")
            message_data["validation_summary"] = response_data.get("validation_summary")
        
        # Add Phase 2 engine information
        if st.session_state.use_phase2_reasoning and response_data.get("engine_used"):
            engine_used = response_data.get("engine_used", "unknown")
            reasoning_type = response_data.get("reasoning_type", "unknown")
            confidence = response_data.get("confidence", 0.0)
            
            # Add Phase 2 engine info to the message
            phase2_info = f"\n\n🚀 **Phase 2 Engine Info:**\n"
            phase2_info += f"• Engine used: {engine_used.title()}\n"
            phase2_info += f"• Reasoning type: {reasoning_type.title()}\n"
            phase2_info += f"• Confidence: {confidence:.2f}\n"
            
            if response_data.get("steps_count"):
                phase2_info += f"• Steps generated: {response_data['steps_count']}\n"
            
            if response_data.get("validation_summary"):
                phase2_info += f"• Validation: {response_data['validation_summary']}\n"
            
            message_data["content"] += phase2_info
            message_data["phase2_engine"] = True
            message_data["engine_used"] = engine_used
            message_data["reasoning_type"] = reasoning_type
            message_data["confidence"] = confidence
        
        # Add Phase 3 strategy information
        if st.session_state.use_phase3_reasoning and response_data.get("strategy_used"):
            strategy_used = response_data.get("strategy_used", "unknown")
            reasoning_type = response_data.get("reasoning_type", "unknown")
            confidence = response_data.get("confidence", 0.0)
            
            # Add Phase 3 strategy info to the message
            phase3_info = f"\n\n🚀 **Phase 3 Strategy Info:**\n"
            phase3_info += f"• Strategy used: {strategy_used.title()}\n"
            phase3_info += f"• Reasoning type: {reasoning_type.title()}\n"
            phase3_info += f"• Confidence: {confidence:.2f}\n"
            
            if response_data.get("steps_count"):
                phase3_info += f"• Steps generated: {response_data['steps_count']}\n"
            
            if response_data.get("validation_summary"):
                phase3_info += f"• Validation: {response_data['validation_summary']}\n"
            
            message_data["content"] += phase3_info
            message_data["phase3_strategy"] = True
            message_data["strategy_used"] = strategy_used
            message_data["reasoning_type"] = reasoning_type
            message_data["confidence"] = confidence
        
        st.session_state.messages.append(message_data)
        
        # Refresh conversation list to include the new conversation
        st.session_state.conversations = get_conversations()
        
        return True
    else:
        if response_data and isinstance(response_data, dict):
            error_msg = response_data.get("response", "❌ Unknown error from backend")
        else:
            error_msg = "❌ Unable to get response from backend. Please try again or check the backend logs."
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        with st.chat_message("assistant"):
            st.error(error_msg)
        return False

def handle_sample_question(question):
    """Handle sample question processing."""
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(question)
    
    # Process the question immediately
    if not st.session_state.backend_health:
        error_msg = f"❌ Backend service is not available. Please make sure the backend server is running on {BACKEND_URL}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        with st.chat_message("assistant"):
            st.error(error_msg)
    else:
        # Send message to backend (with reasoning, RAG, or regular chat)
        if st.session_state.use_reasoning_chat:
            # Use reasoning chat for step-by-step solutions (always streaming)
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                # Stream the response chunks
                for chunk in send_streaming_reasoning_chat(question, st.session_state.conversation_id):
                    if isinstance(chunk, str):
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                    elif isinstance(chunk, dict):
                        # This is the final response data
                        if chunk.get("response", "").startswith("❌"):
                            error_msg = chunk["response"]
                            message_placeholder.error(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
                            break
                        else:
                            # Update conversation ID if provided
                            if chunk.get("conversation_id"):
                                st.session_state.conversation_id = chunk["conversation_id"]
                            
                            # Update the final message
                            final_response = chunk.get("response", full_response)
                            message_placeholder.markdown(final_response)
                            
                            # Add to chat history
                            message_data = {
                                "role": "assistant", 
                                "content": final_response,
                                "reasoning_used": chunk.get("reasoning_used", False),
                                "steps_count": chunk.get("steps_count"),
                                "validation_summary": chunk.get("validation_summary")
                            }
                            st.session_state.messages.append(message_data)
                            break
                
                # Refresh conversation list to include the new conversation
                st.session_state.conversations = get_conversations()
        elif st.session_state.use_rag and st.session_state.rag_stats.get("total_documents", 0) > 0:
            # Check if advanced RAG is enabled
            if st.session_state.use_advanced_rag:
                # Use advanced RAG
                with st.spinner("🚀 Thinking with Advanced RAG..."):
                    response_data = send_advanced_rag_chat(question, st.session_state.conversation_id)
                    process_chat_response(response_data, question)
            else:
                # Use basic RAG (always streaming)
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    # Stream the response chunks
                    for chunk in send_streaming_rag_chat(question, st.session_state.conversation_id):
                        if isinstance(chunk, str):
                            full_response += chunk
                            message_placeholder.markdown(full_response + "▌")
                        elif isinstance(chunk, dict):
                            # This is the final response data
                            if chunk.get("response", "").startswith("❌"):
                                error_msg = chunk["response"]
                                message_placeholder.error(error_msg)
                                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                                break
                            else:
                                # Update conversation ID if provided
                                if chunk.get("conversation_id"):
                                    st.session_state.conversation_id = chunk["conversation_id"]
                                
                                # Update the final message
                                final_response = chunk.get("response", full_response)
                                message_placeholder.markdown(final_response)
                                
                                # Add to chat history
                                message_data = {
                                    "role": "assistant", 
                                    "content": final_response,
                                    "rag_context": chunk.get("rag_context", ""),
                                    "has_context": chunk.get("has_context", False),
                                    "context_awareness_enabled": chunk.get("context_awareness_enabled", False),
                                    "context_strategy_used": chunk.get("context_strategy_used"),
                                    "context_entities": chunk.get("context_entities", []),
                                    "context_topics": chunk.get("context_topics", []),
                                    "memory_chunks_used": chunk.get("memory_chunks_used", 0),
                                    "user_preferences_applied": chunk.get("user_preferences_applied", {})
                                }
                                st.session_state.messages.append(message_data)
                                break
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
        else:
            # Use streaming chat (always enabled)
            response_data = send_to_backend(question, st.session_state.conversation_id, use_streaming=True)
            
            # Handle streaming responses differently since they're already displayed
            if st.session_state.use_phase2_reasoning:
                # For streaming Phase 2 reasoning, the response is already displayed in real-time
                if response_data and not response_data.get("response", "").startswith("❌"):
                    # Update conversation ID if provided
                    if response_data.get("conversation_id"):
                        st.session_state.conversation_id = response_data["conversation_id"]
                    
                    # Add assistant response to chat history
                    message_data = {"role": "assistant", "content": response_data["response"]}
                    
                    # Add Phase 2 engine information
                    if response_data.get("engine_used"):
                        message_data["phase2_engine"] = True
                        message_data["engine_used"] = response_data.get("engine_used", "unknown")
                        message_data["reasoning_type"] = response_data.get("reasoning_type", "unknown")
                        message_data["confidence"] = response_data.get("confidence", 0.0)
                        message_data["steps_count"] = response_data.get("steps_count", 0)
                        message_data["validation_summary"] = response_data.get("validation_summary")
                    
                    # Add Phase 3 strategy information
                    if st.session_state.use_phase3_reasoning and response_data.get("strategy_used"):
                        strategy_used = response_data.get("strategy_used", "unknown")
                        reasoning_type = response_data.get("reasoning_type", "unknown")
                        confidence = response_data.get("confidence", 0.0)
                        
                        # Add Phase 3 strategy info to the message
                        phase3_info = f"\n\n🚀 **Phase 3 Strategy Info:**\n"
                        phase3_info += f"• Strategy used: {strategy_used.title()}\n"
                        phase3_info += f"• Reasoning type: {reasoning_type.title()}\n"
                        phase3_info += f"• Confidence: {confidence:.2f}\n"
                        
                        if response_data.get("steps_count"):
                            phase3_info += f"• Steps generated: {response_data['steps_count']}\n"
                        
                        if response_data.get("validation_summary"):
                            phase3_info += f"• Validation: {response_data['validation_summary']}\n"
                        
                        message_data["content"] += phase3_info
                        message_data["phase3_strategy"] = True
                        message_data["strategy_used"] = strategy_used
                        message_data["reasoning_type"] = reasoning_type
                        message_data["confidence"] = confidence
                    
                    st.session_state.messages.append(message_data)
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Force rerun to update sidebar
                    st.rerun()
                else:
                    error_msg = response_data["response"] if response_data else "❌ Unable to get response from backend. Please try again or check the backend logs."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.error(error_msg)
            elif st.session_state.use_rag and st.session_state.rag_stats.get("total_documents", 0) > 0:
                # For streaming RAG, the response is already displayed in real-time
                if response_data and not response_data.get("response", "").startswith("❌"):
                    # Update conversation ID if provided
                    if response_data.get("conversation_id"):
                        st.session_state.conversation_id = response_data["conversation_id"]
                    
                    # Add assistant response to chat history (preserve content even if stopped)
                    message_data = {"role": "assistant", "content": response_data["response"]}
                    if response_data.get("stopped"):
                        message_data["stopped"] = True
                        print(f"🔍 DEBUG: Saving stopped RAG streaming response to chat history (first instance)")
                    
                    # Handle advanced RAG information
                    if st.session_state.use_advanced_rag and response_data.get("strategies_used"):
                        strategies_used = response_data.get("strategies_used", [])
                        results_count = response_data.get("results_count", 0)
                        
                        # Add advanced RAG info to the message
                        advanced_info = f"\n\n🚀 **Advanced RAG Info:**\n"
                        advanced_info += f"• Strategies used: {', '.join(strategies_used)}\n"
                        advanced_info += f"• Results retrieved: {results_count}\n"
                        
                        if response_data.get("has_context"):
                            advanced_info += "• Context-aware retrieval: ✅\n"
                        else:
                            advanced_info += "• Context-aware retrieval: ❌\n"
                        
                        # Add document references from results
                        if response_data.get("results"):
                            doc_references = []
                            for i, result in enumerate(response_data["results"][:3]):  # Show first 3 results
                                filename = result.get("filename", f"Document {i+1}")
                                strategy = result.get("strategy", "unknown")
                                score = result.get("relevance_score", 0)
                                doc_references.append(f"{filename} ({strategy}, score: {score:.2f})")
                            
                            if doc_references:
                                advanced_info += f"• Documents used: {', '.join(doc_references)}\n"
                        
                        message_data["content"] += advanced_info
                        message_data["advanced_rag"] = True
                        message_data["strategies_used"] = strategies_used
                        message_data["results_count"] = results_count
                    
                    # For advanced RAG, document references are already included in the advanced info above
                    # For basic RAG, check if backend provided RAG context directly
                    if not st.session_state.use_advanced_rag and response_data.get("rag_context") and response_data.get("has_context") == True:
                        message_data["rag_context"] = response_data["rag_context"]
                        message_data["has_context"] = response_data["has_context"]
                        # Add RAG reference to the message content
                        message_data["content"] += f"\n\n📚 **RAG Reference:** {response_data.get('rag_context', '')}"
                    elif not st.session_state.use_advanced_rag:
                        # Try to extract RAG context from the content itself for basic RAG
                        extracted_rag_context = extract_rag_context_from_content(response_data["response"])
                        
                        if extracted_rag_context:
                            message_data["rag_context"] = extracted_rag_context
                            message_data["has_context"] = True
                            # Add RAG reference to the message content
                            message_data["content"] += f"\n\n📚 **RAG Reference:** {extracted_rag_context}"
                        else:
                            # Add note if no RAG context was found
                            message_data["content"] += f"\n\nℹ️ *No relevant documents found in RAG database.*"
                    
                    st.session_state.messages.append(message_data)
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Force rerun to update sidebar
                    st.rerun()
                else:
                    error_msg = response_data["response"] if response_data else "❌ Unable to get response from backend. Please try again or check the backend logs."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.error(error_msg)
            elif st.session_state.use_reasoning_chat:
                # Handle streaming reasoning responses
                # Create a placeholder for the assistant message
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    # Stream the response chunks
                    for chunk in response_data:
                        if isinstance(chunk, str):
                            full_response += chunk
                            message_placeholder.markdown(full_response + "▌")
                        elif isinstance(chunk, dict):
                            # This is the final response data
                            if chunk.get("response", "").startswith("❌"):
                                error_msg = chunk["response"]
                                message_placeholder.error(error_msg)
                                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                                break
                            else:
                                # Update conversation ID if provided
                                if chunk.get("conversation_id"):
                                    st.session_state.conversation_id = chunk["conversation_id"]
                                
                                # Update the final message (no reasoning info needed)
                                final_response = chunk.get("response", full_response)
                                message_placeholder.markdown(final_response)
                                
                                # Add to chat history
                                message_data = {
                                    "role": "assistant", 
                                    "content": final_response,
                                    "reasoning_used": chunk.get("reasoning_used", False),
                                    "steps_count": chunk.get("steps_count"),
                                    "validation_summary": chunk.get("validation_summary")
                                }
                                st.session_state.messages.append(message_data)
                                break
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Force rerun to update sidebar
                    st.rerun()
            else:
                # Handle regular responses (non-streaming or non-RAG)
                if response_data and not response_data["response"].startswith("❌"):
                    # Update conversation ID if provided
                    if response_data.get("conversation_id"):
                        st.session_state.conversation_id = response_data["conversation_id"]
                    
                    # For streaming responses, the message is already displayed and stored by the streaming function
                    # Add to session state (streaming responses are handled separately)
                    if False:  # This block is no longer needed since streaming is always enabled
                        # Add assistant response to chat history
                        message_data = {"role": "assistant", "content": response_data["response"]}
                    
                    # Handle advanced RAG information for regular responses
                    if st.session_state.use_advanced_rag and response_data.get("strategies_used"):
                        strategies_used = response_data.get("strategies_used", [])
                        results_count = response_data.get("results_count", 0)
                        
                        # Add advanced RAG info to the message
                        advanced_info = f"\n\n🚀 **Advanced RAG Info:**\n"
                        advanced_info += f"• Strategies used: {', '.join(strategies_used)}\n"
                        advanced_info += f"• Results retrieved: {results_count}\n"
                        
                        if response_data.get("has_context"):
                            advanced_info += "• Context-aware retrieval: ✅\n"
                        else:
                            advanced_info += "• Context-aware retrieval: ❌\n"
                        
                        # Add document references from results
                        if response_data.get("results"):
                            doc_references = []
                            for i, result in enumerate(response_data["results"][:3]):  # Show first 3 results
                                filename = result.get("filename", f"Document {i+1}")
                                strategy = result.get("strategy", "unknown")
                                score = result.get("relevance_score", 0)
                                doc_references.append(f"{filename} ({strategy}, score: {score:.2f})")
                            
                            if doc_references:
                                advanced_info += f"• Documents used: {', '.join(doc_references)}\n"
                        
                        message_data["content"] += advanced_info
                        message_data["advanced_rag"] = True
                        message_data["strategies_used"] = strategies_used
                        message_data["results_count"] = results_count
                    
                    # Add RAG context if available (for basic RAG)
                    if not st.session_state.use_advanced_rag and response_data.get("rag_context") and response_data.get("has_context"):
                        message_data["rag_context"] = response_data["rag_context"]
                        message_data["has_context"] = response_data["has_context"]
                    
                    # Add reasoning metadata for regular responses (no display needed)
                    if response_data.get("reasoning_used"):
                        message_data["reasoning_used"] = True
                        message_data["steps_count"] = response_data.get("steps_count")
                        message_data["validation_summary"] = response_data.get("validation_summary")
                    
                    # Add Phase 2 engine information
                    if st.session_state.use_phase2_reasoning and response_data.get("engine_used"):
                        engine_used = response_data.get("engine_used", "unknown")
                        reasoning_type = response_data.get("reasoning_type", "unknown")
                        confidence = response_data.get("confidence", 0.0)
                        
                        # Add Phase 2 engine info to the message
                        phase2_info = f"\n\n🚀 **Phase 2 Engine Info:**\n"
                        phase2_info += f"• Engine used: {engine_used.title()}\n"
                        phase2_info += f"• Reasoning type: {reasoning_type.title()}\n"
                        phase2_info += f"• Confidence: {confidence:.2f}\n"
                        
                        if response_data.get("steps_count"):
                            phase2_info += f"• Steps generated: {response_data['steps_count']}\n"
                        
                        if response_data.get("validation_summary"):
                            phase2_info += f"• Validation: {response_data['validation_summary']}\n"
                        
                        message_data["content"] += phase2_info
                        message_data["phase2_engine"] = True
                        message_data["engine_used"] = engine_used
                        message_data["reasoning_type"] = reasoning_type
                        message_data["confidence"] = confidence
                    
                    # Add Phase 3 strategy information
                    if st.session_state.use_phase3_reasoning and response_data.get("strategy_used"):
                        strategy_used = response_data.get("strategy_used", "unknown")
                        reasoning_type = response_data.get("reasoning_type", "unknown")
                        confidence = response_data.get("confidence", 0.0)
                        
                        # Add Phase 3 strategy info to the message
                        phase3_info = f"\n\n🚀 **Phase 3 Strategy Info:**\n"
                        phase3_info += f"• Strategy used: {strategy_used.title()}\n"
                        phase3_info += f"• Reasoning type: {reasoning_type.title()}\n"
                        phase3_info += f"• Confidence: {confidence:.2f}\n"
                        
                        if response_data.get("steps_count"):
                            phase3_info += f"• Steps generated: {response_data['steps_count']}\n"
                        
                        if response_data.get("validation_summary"):
                            phase3_info += f"• Validation: {response_data['validation_summary']}\n"
                        
                        message_data["content"] += phase3_info
                        message_data["phase3_strategy"] = True
                        message_data["strategy_used"] = strategy_used
                        message_data["reasoning_type"] = reasoning_type
                        message_data["confidence"] = confidence
                    
                    # Add to session state (streaming responses are handled separately)
                    if False:  # This block is no longer needed since streaming is always enabled
                        st.session_state.messages.append(message_data)
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Display assistant response (streaming responses are handled separately)
                    if False:  # This block is no longer needed since streaming is always enabled
                        with st.chat_message("assistant"):
                            st.markdown(response_data["response"])
                    
                    # Force rerun to update sidebar
                    st.rerun()
                else:
                    error_msg = response_data["response"] if response_data else "❌ Unable to get response from backend. Please try again or check the backend logs."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.error(error_msg)

def display_chat_messages():
    """Display chat messages with context awareness information."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            content = message["content"]
            
            # Check if this is a DeepSeek format response
            parsed = parse_deepseek_reasoning(content)
            
            # Show visual indicator if message was stopped
            if message.get("stopped"):
                if parsed['is_deepseek_format']:
                    display_deepseek_response(parsed['thinking'], parsed['answer'], st)
                else:
                    st.markdown(content)
                st.info("⏹️ Generation stopped by user - content preserved!")
            else:
                if parsed['is_deepseek_format']:
                    # Display DeepSeek response with expandable thinking section
                    display_deepseek_response(parsed['thinking'], parsed['answer'], st)
                else:
                    st.markdown(content)
                
                # Display context awareness information for assistant messages
                if message["role"] == "assistant" and message.get("context_awareness_enabled"):
                    with st.expander("🧠 Context Information"):
                        context_info = []
                        
                        if message.get("context_strategy_used"):
                            context_info.append(f"**Strategy:** {message['context_strategy_used']}")
                        
                        if message.get("context_entities"):
                            entities = message["context_entities"][:5]  # Show top 5
                            if entities:
                                context_info.append(f"**Key Entities:** {', '.join(entities)}")
                        
                        if message.get("context_topics"):
                            topics = message["context_topics"][:3]  # Show top 3
                            if topics:
                                context_info.append(f"**Topics:** {', '.join(topics)}")
                        
                        if message.get("memory_chunks_used", 0) > 0:
                            context_info.append(f"**Memory Chunks Used:** {message['memory_chunks_used']}")
                        
                        if message.get("user_preferences_applied"):
                            prefs = message["user_preferences_applied"]
                            if prefs:
                                context_info.append(f"**User Preferences Applied:** {str(prefs)}")
                        
                        if context_info:
                            st.markdown("\n".join(context_info))
                        else:
                            st.write("No specific context information available")

def get_phase2_engine_status() -> Dict:
    """Get Phase 2 reasoning engine status."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/phase2-reasoning/status", timeout=5.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "unavailable",
                    "engines": {
                        "mathematical": {"status": "unknown", "error": f"HTTP {response.status_code}"},
                        "logical": {"status": "unknown", "error": f"HTTP {response.status_code}"},
                        "causal": {"status": "unknown", "error": f"HTTP {response.status_code}"}
                    }
                }
    except Exception as e:
        return {
            "status": "unavailable",
            "engines": {
                "mathematical": {"status": "unknown", "error": str(e)},
                "logical": {"status": "unknown", "error": str(e)},
                "causal": {"status": "unknown", "error": str(e)}
            }
        }


def get_phase3_health() -> Dict:
    """Get Phase 3 advanced reasoning strategies health from backend."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/phase3-reasoning/health", timeout=5.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "unavailable",
                    "strategies": {
                        "chain_of_thought": {"status": "unknown", "error": f"HTTP {response.status_code}"},
                        "tree_of_thoughts": {"status": "unknown", "error": f"HTTP {response.status_code}"},
                        "prompt_engineering": {"status": "unknown", "error": f"HTTP {response.status_code}"}
                    }
                }
    except Exception as e:
        return {
            "status": "unavailable",
            "strategies": {
                "chain_of_thought": {"status": "unknown", "error": str(e)},
                "tree_of_thoughts": {"status": "unknown", "error": str(e)},
                "prompt_engineering": {"status": "unknown", "error": str(e)}
            }
        }


def get_unified_reasoning_status() -> Dict:
    """Get unified reasoning system status from backend."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/unified-reasoning/status", timeout=5.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "unavailable",
                    "error": f"HTTP {response.status_code}",
                    "components": {
                        "core": {"status": "unknown", "error": f"HTTP {response.status_code}"},
                        "engines": {
                            "mathematical": {"status": "unknown", "error": f"HTTP {response.status_code}"},
                            "logical": {"status": "unknown", "error": f"HTTP {response.status_code}"},
                            "causal": {"status": "unknown", "error": f"HTTP {response.status_code}"}
                        },
                        "strategies": {
                            "chain_of_thought": {"status": "unknown", "error": f"HTTP {response.status_code}"},
                            "tree_of_thoughts": {"status": "unknown", "error": f"HTTP {response.status_code}"}
                        }
                    }
                }
    except Exception as e:
        return {
            "status": "unavailable",
            "error": str(e),
            "components": {
                "core": {"status": "unknown", "error": str(e)},
                "engines": {
                    "mathematical": {"status": "unknown", "error": str(e)},
                    "logical": {"status": "unknown", "error": str(e)},
                    "causal": {"status": "unknown", "error": str(e)}
                },
                "strategies": {
                    "chain_of_thought": {"status": "unknown", "error": str(e)},
                    "tree_of_thoughts": {"status": "unknown", "error": str(e)}
                }
            }
        }


def get_phase3_strategies() -> Dict:
    """Get available Phase 3 strategies from backend."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/phase3-reasoning/strategies", timeout=5.0)
            if response.status_code == 200:
                return response.json()
    except:
        pass
    return {"strategies": {}, "error": "Backend not available"}


def send_phase2_reasoning_chat(message: str, engine_type: str = "auto", conversation_id: Optional[str] = None, use_streaming: bool = False) -> Optional[Dict]:
    """Send message to backend with Phase 2 reasoning engine."""
    if use_streaming:
        # Use streaming version
        for response in send_streaming_phase2_reasoning_chat(message, engine_type, conversation_id):
            if isinstance(response, dict):
                return response
        return {"response": "❌ Streaming failed"}
    
    # Non-streaming version
    try:
        with httpx.Client() as client:
            # Use the first available model or fallback to llama3:latest
            model = get_selected_model()
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "use_phase2_reasoning": True,
                "engine_type": engine_type,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True,
                "enable_context_awareness": st.session_state.enable_context_awareness,
                "include_memory": st.session_state.include_memory,
                "context_strategy": st.session_state.context_strategy
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            # Use Phase 2 reasoning endpoint
            response = client.post(
                f"{BACKEND_URL}/api/v1/phase2-reasoning/",
                json=payload,
                timeout=120.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "response": data.get("response", "No response from backend"),
                    "conversation_id": data.get("conversation_id"),
                    "engine_used": data.get("engine_used", "unknown"),
                    "reasoning_type": data.get("reasoning_type", "unknown"),
                    "steps_count": data.get("steps_count"),
                    "confidence": data.get("confidence", 0.0),
                    "validation_summary": data.get("validation_summary")
                }
            elif response.status_code == 503:
                return {"response": "❌ Ollama service is not available. Please make sure Ollama is running."}
            else:
                return {"response": f"Backend error: {response.status_code}"}
                    
    except httpx.TimeoutException:
        return {"response": "Request timed out. Please try again."}
    except Exception as e:
        return {"response": f"Communication error: {str(e)}"}

def send_streaming_phase2_reasoning_chat(message: str, engine_type: str = "auto", conversation_id: Optional[str] = None):
    """Send message to backend with Phase 2 reasoning engine using streaming."""
    st.info("🚀 Starting Phase 2 reasoning streaming...")
    print(f"🔍 Phase 2 streaming started for message: {message[:50]}...")
    try:
        with httpx.Client() as client:
            # Use the first available model or fallback to llama3:latest
            model = get_selected_model()
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "use_phase2_reasoning": True,
                "engine_type": engine_type,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True,
                "enable_context_awareness": st.session_state.enable_context_awareness,
                "include_memory": st.session_state.include_memory,
                "context_strategy": st.session_state.context_strategy
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            print(f"🔍 Sending request to: {BACKEND_URL}/api/v1/phase2-reasoning/stream")
            print(f"🔍 Payload: {payload}")
            
            # Create assistant message container for streaming
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                # Store in session state so stop button can access it
                st.session_state.current_response = ""
                engine_used = "auto"
                reasoning_type = "unknown"
                steps_count = 0
                confidence = 0.0
                validation_summary = None
                
                # Stream the response
                with client.stream(
                    "POST",
                    f"{BACKEND_URL}/api/v1/phase2-reasoning/stream",
                    json=payload,
                    timeout=300.0,  # Increased timeout for reasoning processing
                    headers={"Accept": "text/event-stream", "Connection": "keep-alive"}
                ) as response:
                    print(f"🔍 Response status: {response.status_code}")
                    if response.status_code == 200:
                        # Process Server-Sent Events
                        for line in response.iter_lines():
                            # Check for stop signal
                            if st.session_state.stop_generation:
                                message_placeholder.markdown(full_response + "\n\n*Generation stopped by user.*")
                                return {"response": full_response + "\n\n*Generation stopped by user.*", "stopped": True}
                            
                            if line:
                                print(f"🔍 Received line: {line[:100]}...")
                                # httpx.iter_lines() returns strings, not bytes
                                if line.startswith('data: '):
                                    data_str = line[6:]  # Remove 'data: ' prefix
                                    try:
                                        data = json.loads(data_str)
                                        print(f"🔍 Parsed data: {data}")
                                        
                                        if data.get("error"):
                                            print(f"🔍 Error in data: {data.get('error')}")
                                            return {"response": f"Error: {data.get('error', 'Unknown error')}"}
                                        
                                        # Handle different response types
                                        if "content" in data:
                                            chunk = data["content"]
                                            full_response += chunk
                                            # Update session state so stop button can access current content
                                            st.session_state.current_response = full_response
                                            message_placeholder.markdown(full_response + "▌")
                                            print(f"🔍 Added chunk: {chunk[:50]}...")
                                            
                                            # Add artificial delay to see streaming effect (optional)
                                            # Uncomment the next line to slow down streaming for testing
                                            # time.sleep(0.2)  # 200ms delay
                                        
                                        # Update metadata
                                        if "engine_used" in data:
                                            engine_used = data["engine_used"]
                                        if "reasoning_type" in data:
                                            reasoning_type = data["reasoning_type"]
                                        if "steps_count" in data:
                                            steps_count = data["steps_count"]
                                        if "confidence" in data:
                                            confidence = data["confidence"]
                                        if "validation_summary" in data:
                                            validation_summary = data["validation_summary"]
                                        
                                        # Check if this is the final message
                                        if data.get("final"):
                                            print(f"🔍 Final message received")
                                            message_placeholder.markdown(full_response)
                                            
                                            # Add Phase 2 engine info to the response
                                            phase2_info = f"\n\n🚀 **Phase 2 Engine Info:**\n"
                                            phase2_info += f"• Engine used: {engine_used.title()}\n"
                                            phase2_info += f"• Reasoning type: {reasoning_type.title()}\n"
                                            phase2_info += f"• Confidence: {confidence:.2f}\n"
                                            phase2_info += f"• Steps generated: {steps_count}\n"
                                            
                                            if validation_summary:
                                                phase2_info += f"• Validation: {validation_summary}\n"
                                            
                                            full_response += phase2_info
                                            message_placeholder.markdown(full_response)
                                            
                                            # Clear current response since generation is complete
                                            st.session_state.current_response = ""
                                            return {
                                                "response": full_response,
                                                "conversation_id": data.get("conversation_id") or conversation_id,
                                                "engine_used": engine_used,
                                                "reasoning_type": reasoning_type,
                                                "steps_count": steps_count,
                                                "confidence": confidence,
                                                "validation_summary": validation_summary
                                            }
                                            
                                    except json.JSONDecodeError as e:
                                        print(f"🔍 JSON decode error: {e}")
                                        continue
                        
                        print(f"🔍 Streaming ended, full_response length: {len(full_response)}")
                        # If we get here without returning, the streaming ended without content
                        if not full_response:
                            print("🔍 No response generated")
                            return {"response": "No response generated. Please try again."}
                        else:
                            # If we have content but no final message, return what we have
                            print("🔍 Returning fallback response")
                            message_placeholder.markdown(full_response)
                            
                            # Add Phase 2 engine info to the response
                            phase2_info = f"\n\n🚀 **Phase 2 Engine Info:**\n"
                            phase2_info += f"• Engine used: {engine_used.title()}\n"
                            phase2_info += f"• Reasoning type: {reasoning_type.title()}\n"
                            phase2_info += f"• Confidence: {confidence:.2f}\n"
                            phase2_info += f"• Steps generated: {steps_count}\n"
                            
                            if validation_summary:
                                phase2_info += f"• Validation: {validation_summary}\n"
                            
                            full_response += phase2_info
                            message_placeholder.markdown(full_response)
                            
                            # Clear current response in case of any exit path
                            st.session_state.current_response = ""
                            return {
                                "response": full_response,
                                "conversation_id": conversation_id,
                                "engine_used": engine_used,
                                "reasoning_type": reasoning_type,
                                "steps_count": steps_count,
                                "confidence": confidence,
                                "validation_summary": validation_summary
                            }
                    else:
                        print(f"🔍 Backend error: {response.status_code}")
                        return {"response": f"Backend error: {response.status_code}"}
                        
    except httpx.TimeoutException:
        print("🔍 Timeout exception")
        st.error("⏰ Phase 2 reasoning streaming timed out")
        return {"response": "Request timed out. Please try again."}
    except Exception as e:
        print(f"🔍 Exception: {e}")
        st.error(f"💥 Phase 2 reasoning streaming error: {str(e)}")
        return {"response": f"Communication error: {str(e)}"}
    
    print("🔍 Function completed without returning")
    st.error("🔚 Phase 2 reasoning streaming function completed without returning anything")
    return None

def send_phase3_reasoning_chat(message: str, strategy_type: str = "auto", conversation_id: Optional[str] = None, use_streaming: bool = False) -> Optional[Dict]:
    """Send message to backend with Phase 3 advanced reasoning strategies."""
    # For now, use a simple implementation without streaming
    try:
        with httpx.Client() as client:
            # Use the first available model or fallback to llama3:latest
            model = get_selected_model()
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "use_phase3_reasoning": True,
                "strategy_type": strategy_type,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True,
                "enable_context_awareness": st.session_state.enable_context_awareness,
                "include_memory": st.session_state.include_memory,
                "context_strategy": st.session_state.context_strategy
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            # Use Phase 3 reasoning endpoint
            response = client.post(
                f"{BACKEND_URL}/api/v1/phase3-reasoning/",
                json=payload,
                timeout=120.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "response": data.get("response", "No response from backend"),
                    "conversation_id": data.get("conversation_id"),
                    "strategy_used": data.get("strategy_used", "unknown"),
                    "reasoning_type": data.get("reasoning_type", "unknown"),
                    "steps_count": data.get("steps_count"),
                    "confidence": data.get("confidence", 0.0),
                    "validation_summary": data.get("validation_summary")
                }
            elif response.status_code == 503:
                return {"response": "❌ Ollama service is not available. Please make sure Ollama is running."}
            else:
                return {"response": f"Backend error: {response.status_code}"}
                    
    except httpx.TimeoutException:
        return {"response": "Request timed out. Please try again."}
    except Exception as e:
        return {"response": f"Communication error: {str(e)}"}

def send_unified_reasoning_chat(message: str, reasoning_mode: str = "auto", conversation_id: Optional[str] = None) -> Optional[Dict]:
    """Send message to backend with unified reasoning system."""
    try:
        with httpx.Client() as client:
            # Use the first available model or fallback to llama3:latest
            model = get_selected_model()
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "reasoning_mode": reasoning_mode,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True,
                "enable_context_awareness": st.session_state.enable_context_awareness,
                "include_memory": st.session_state.include_memory,
                "context_strategy": st.session_state.context_strategy
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            print(f"🔍 Sending unified reasoning request to: {BACKEND_URL}/api/v1/unified-reasoning/chat")
            print(f"🔍 Payload: {payload}")
            
            response = client.post(
                f"{BACKEND_URL}/api/v1/unified-reasoning/chat",
                json=payload,
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"🔍 Unified reasoning response received: {result.get('response', '')[:100]}...")
                return result
            else:
                print(f"🔍 Unified reasoning request failed with status: {response.status_code}")
                return {"response": f"❌ Unified reasoning request failed: {response.status_code}"}
                
    except Exception as e:
        print(f"🔍 Unified reasoning error: {str(e)}")
        return {"response": f"Communication error: {str(e)}"}

def send_streaming_phase3_reasoning_chat(message: str, strategy_type: str = "auto", conversation_id: Optional[str] = None):
    """Send message to backend with Phase 3 reasoning strategies using streaming."""
    st.info("🧠 Starting Phase 3 advanced reasoning streaming...")
    print(f"🔍 Phase 3 streaming started for message: {message[:50]}...")
    try:
        with httpx.Client() as client:
            # Use the first available model or fallback to llama3:latest
            model = get_selected_model()
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "use_phase3_reasoning": True,
                "strategy_type": strategy_type,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True,
                "enable_context_awareness": st.session_state.enable_context_awareness,
                "include_memory": st.session_state.include_memory,
                "context_strategy": st.session_state.context_strategy
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            print(f"🔍 Sending request to: {BACKEND_URL}/api/v1/phase3-reasoning/stream")
            print(f"🔍 Payload: {payload}")
            
            # Create assistant message container for streaming
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                # Store in session state so stop button can access it
                st.session_state.current_response = ""
                strategy_used = "auto"
                reasoning_type = "unknown"
                steps_count = 0
                confidence = 0.0
                validation_summary = None
                
                # Stream the response
                with client.stream(
                    "POST",
                    f"{BACKEND_URL}/api/v1/phase3-reasoning/stream",
                    json=payload,
                    timeout=300.0,  # Increased timeout for reasoning processing
                    headers={"Accept": "text/event-stream", "Connection": "keep-alive"}
                ) as response:
                    print(f"🔍 Response status: {response.status_code}")
                    if response.status_code == 200:
                        # Process Server-Sent Events
                        for line in response.iter_lines():
                            # Check for stop signal
                            if st.session_state.stop_generation:
                                print(f"🔍 DEBUG: Stop signal detected in Phase 3 streaming! full_response length: {len(full_response)}")
                                message_placeholder.markdown(full_response + "\n\n*Generation stopped by user.*")
                                stopped_response = {"response": full_response + "\n\n*Generation stopped by user.*", "stopped": True, "strategy_used": strategy_used, "reasoning_type": reasoning_type, "steps_count": steps_count, "confidence": confidence, "validation_summary": validation_summary}
                                print(f"🔍 DEBUG: Returning stopped response: {stopped_response}")
                                return stopped_response
                            
                            if line:
                                print(f"🔍 Received line: {line[:100]}...")
                                # httpx.iter_lines() returns strings, not bytes
                                if line.startswith('data: '):
                                    data_str = line[6:]  # Remove 'data: ' prefix
                                    try:
                                        data = json.loads(data_str)
                                        print(f"🔍 Parsed data: {data}")
                                        
                                        if data.get("error"):
                                            print(f"🔍 Error in data: {data.get('error')}")
                                            return {"response": f"Error: {data.get('error', 'Unknown error')}"}
                                        
                                        # Handle different response types
                                        if "content" in data:
                                            chunk = data["content"]
                                            full_response += chunk
                                            # Update session state so stop button can access current content
                                            st.session_state.current_response = full_response
                                            message_placeholder.markdown(full_response + "▌")
                                            print(f"🔍 Added chunk: {chunk[:50]}...")
                                            
                                            # Add artificial delay to see streaming effect (optional)
                                            # Uncomment the next line to slow down streaming for testing
                                            # time.sleep(0.2)  # 200ms delay
                                        
                                        # Update metadata
                                        if "strategy_used" in data:
                                            strategy_used = data["strategy_used"]
                                        if "reasoning_type" in data:
                                            reasoning_type = data["reasoning_type"]
                                        if "steps_count" in data:
                                            steps_count = data["steps_count"]
                                        if "confidence" in data:
                                            confidence = data["confidence"]
                                        if "validation_summary" in data:
                                            validation_summary = data["validation_summary"]
                                        
                                        # Check if this is the final message
                                        if data.get("final"):
                                            print(f"🔍 Final message received")
                                            message_placeholder.markdown(full_response)
                                            
                                            # Clear current response since generation is complete
                                            st.session_state.current_response = ""
                                            return {"response": full_response, "conversation_id": conversation_id, "strategy_used": strategy_used, "reasoning_type": reasoning_type, "steps_count": steps_count, "confidence": confidence, "validation_summary": validation_summary}
                                    except json.JSONDecodeError as e:
                                        print(f"🔍 JSON decode error: {e}")
                                        continue
                    else:
                        print(f"🔍 Error response: {response.status_code}")
                        return {"response": f"Backend error: {response.status_code}"}
                        
    except Exception as e:
        print(f"🔍 Exception in Phase 3 streaming: {e}")
        return {"response": f"Communication error: {str(e)}"}

def main():
    """Main application function."""
    init_session_state()
    
    # Apply simple CSS
    st.markdown(get_css(), unsafe_allow_html=True)
    
    # Performance optimization: Load data asynchronously to improve startup time
    if not st.session_state.auto_loaded:
        with st.spinner("🚀 Initializing..."):
            # Check backend health and get models in parallel
            st.session_state.backend_health = check_backend_health()
            if st.session_state.backend_health:
                # Load essential data first
                st.session_state.available_models = get_available_models()
                st.session_state.conversations = get_conversations()
                
                # Set default selected model if none selected
                if not st.session_state.selected_model and st.session_state.available_models:
                    st.session_state.selected_model = st.session_state.available_models[0]
                
                # Load secondary data in background - RAG service removed
                st.session_state.rag_stats = {}
                    
        st.session_state.auto_loaded = True
    else:
        # Use cached data for faster subsequent loads
        if st.session_state.backend_health:
            if not st.session_state.available_models:
                st.session_state.available_models = get_available_models()
            if not st.session_state.conversations:
                st.session_state.conversations = get_conversations()
        
        # Debug output
        print(f"🔍 Main function - RAG Stats loaded: {st.session_state.rag_stats}")
        print(f"🔍 Total documents: {st.session_state.rag_stats.get('total_documents', 0)}")
    
    # Sidebar for conversations and settings
    with st.sidebar:
        # Force refresh button for debugging
        if st.button("🔄 Force Refresh All Data"):
            # Store current selected model
            current_model = st.session_state.selected_model
            
            st.session_state.rag_stats = {}  # RAG service removed
            st.session_state.conversations = get_conversations()
            st.session_state.available_models = get_available_models()
            
            # Restore selected model if it still exists, otherwise use first available
            if current_model and current_model in st.session_state.available_models:
                st.session_state.selected_model = current_model
            elif st.session_state.available_models:
                st.session_state.selected_model = st.session_state.available_models[0]
            
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
        
        # User ID Input - at the top for easy access
        st.markdown("---")
        st.markdown("### 👤 User ID")
        user_id = st.text_input(
            "Enter your User ID:",
            value=st.session_state.user_id or "",
            help="Your user ID for personalized settings and context across conversations",
            key="navbar_user_id"
        )
        if st.session_state.user_id != (user_id if user_id else None):
            # User ID changed - load the new user's settings
            old_user_id = st.session_state.user_id
            st.session_state.user_id = user_id if user_id else None
            
            # Sync to URL
            sync_user_id_to_url()
            
            # Load settings for the new user from database
            db_settings = load_user_settings_from_database(st.session_state.user_id)
            
            # Apply the new user's settings to session state
            for key, value in db_settings.items():
                if key != "user_id" and key in st.session_state:
                    st.session_state[key] = value
            
            st.success(f"✅ Switched to user: {st.session_state.user_id}")
            st.rerun()
        
        # Model Selection at the top
        st.markdown("---")
        st.markdown("### 🤖 Model Selection")
        
        if st.session_state.available_models:
            # Set default model if none selected
            if not st.session_state.selected_model:
                st.session_state.selected_model = st.session_state.available_models[0]
            
            # Find the index of the currently selected model
            try:
                current_index = st.session_state.available_models.index(st.session_state.selected_model)
            except ValueError:
                current_index = 0
                st.session_state.selected_model = st.session_state.available_models[0]
            
            selected_model = st.selectbox(
                "Choose your AI model:",
                st.session_state.available_models,
                index=current_index,
                help="Select from your locally downloaded Ollama models"
            )
            
            # Update session state if model changed
            if selected_model != st.session_state.selected_model:
                st.session_state.selected_model = selected_model
                save_user_settings()  # Save settings when changed
                st.success(f"✅ Switched to {selected_model}")
                st.rerun()
            
            # Display model info
            st.info(f"**Active Model:** {selected_model}")
        else:
            st.warning("⚠️ No models available")
            st.info("Make sure Ollama is running and models are downloaded")
        
        st.markdown("---")
        
        # RAG Section (Collapsible) - Simplified for document viewing only
        with st.expander("📚 Documents", expanded=False):
            st.markdown('<div class="section-header">Uploaded Documents</div>', unsafe_allow_html=True)
            st.info("💡 Use the 📄 Upload button in the main chat area to upload documents")
            
            if st.session_state.backend_health:
                # Show conversation documents if we have a current conversation
                if getattr(st.session_state, 'conversation_id', None):
                    if st.button("🔄 Refresh Documents"):
                        st.session_state.conversation_documents = None
                        st.rerun()
                    
                    # Get conversation documents
                    if not hasattr(st.session_state, 'conversation_documents') or st.session_state.conversation_documents is None:
                        with st.spinner("Loading conversation documents..."):
                            docs_result = get_conversation_documents(getattr(st.session_state, 'conversation_id', None))
                            if docs_result.get("success"):
                                st.session_state.conversation_documents = docs_result.get("data", {})
                            else:
                                st.session_state.conversation_documents = {"documents": []}
                    
                    # Display conversation documents
                    if st.session_state.conversation_documents.get("documents"):
                        for doc in st.session_state.conversation_documents["documents"]:
                            with st.expander(f"📄 {doc['filename']} ({doc['file_type']})"):
                                st.write(f"**Size:** {doc['file_size']} bytes")
                                st.write(f"**Uploaded:** {doc['upload_timestamp']}")
                                st.write(f"**Status:** {doc['processing_status']}")
                                
                                if doc.get('summary_text'):
                                    st.write(f"**Summary:** {doc['summary_text']}")
                                else:
                                    st.info("💡 Ask 'summarize this document' in chat to generate a summary")
                    else:
                        st.info("No documents uploaded to this conversation yet.")
                else:
                    st.info("Start a conversation to see uploaded documents here.")
                
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
                        # RAG service removed
                        st.session_state.rag_stats = {}
                        st.success("RAG service has been removed - stats cleared")
                        st.rerun()
            else:
                st.warning("Backend not available for document upload")
            
            st.markdown('<div class="section-header">Context Awareness</div>', unsafe_allow_html=True)
            
            # Context Awareness Toggle
            enable_context_awareness = st.checkbox(
                "🧠 Enable Context Awareness",
                value=st.session_state.enable_context_awareness,
                help="Enable advanced context awareness features including conversation memory and user preferences"
            )
            if st.session_state.enable_context_awareness != enable_context_awareness:
                st.session_state.enable_context_awareness = enable_context_awareness
                save_user_settings()  # Save settings when changed
            
            if enable_context_awareness:
                # Context Strategy Selection
                context_strategy = st.selectbox(
                    "🎯 Context Strategy",
                    options=["auto", "conversation_only", "memory_only", "hybrid"],
                    index=["auto", "conversation_only", "memory_only", "hybrid"].index(st.session_state.context_strategy),
                    help="Choose how context should be retrieved and used"
                )
                if st.session_state.context_strategy != context_strategy:
                    st.session_state.context_strategy = context_strategy
                    save_user_settings()  # Save settings when changed
                
                # Include Memory Toggle
                include_memory = st.checkbox(
                    "💾 Include Long-term Memory",
                    value=st.session_state.include_memory,
                    help="Include relevant information from past conversations"
                )
                if st.session_state.include_memory != include_memory:
                    st.session_state.include_memory = include_memory
                    save_user_settings()  # Save settings when changed
                
                # Settings Status (for testing)
                with st.expander("🔧 Settings Status", expanded=False):
                    st.json({
                        "Context Awareness": st.session_state.enable_context_awareness,
                        "Include Memory": st.session_state.include_memory,
                        "Context Strategy": st.session_state.context_strategy,
                        "User ID": st.session_state.user_id,
                        "Selected Model": st.session_state.selected_model,
                        "Temperature": st.session_state.temperature,
                        "Use RAG": st.session_state.use_rag,
                        "Phase 1 Reasoning": st.session_state.use_reasoning_chat,
                        "Phase 2 Reasoning": st.session_state.use_phase2_reasoning,
                        "Phase 2 Engine": st.session_state.selected_phase2_engine,
                        "Phase 3 Reasoning": st.session_state.use_phase3_reasoning,
                        "Phase 3 Strategy": st.session_state.selected_phase3_strategy,
                        "Unified Reasoning": st.session_state.use_unified_reasoning,
                        "Reasoning Mode": st.session_state.selected_reasoning_mode
                    })
                
                # Context Information Display
                if st.session_state.context_info:
                    with st.expander("📊 Context Information"):
                        context = st.session_state.context_info
                        if context.get("topics"):
                            st.write("**Topics:**", ", ".join(context["topics"][:5]))
                        if context.get("entities"):
                            st.write("**Key Entities:**", ", ".join([e["text"] for e in context["entities"][:5]]))
                        if context.get("user_preferences"):
                            st.write("**User Preferences:**", str(context["user_preferences"]))
            
            st.markdown('<div class="section-header">RAG Mode</div>', unsafe_allow_html=True)
            use_rag = st.checkbox(
                "Enable RAG for responses",
                value=st.session_state.use_rag,
                help="When enabled, responses will use document context from uploaded files"
            )
            if st.session_state.use_rag != use_rag:
                st.session_state.use_rag = use_rag
                save_user_settings()  # Save settings when changed
            
            if use_rag:
                if st.session_state.rag_stats.get("total_documents", 0) == 0:
                    st.warning("⚠️ No documents uploaded. Upload documents to use RAG mode.")
                else:
                    st.success("✅ RAG mode enabled - responses will use document context")
            
            # Advanced RAG Section
            st.markdown('<div class="section-header">🚀 Advanced RAG</div>', unsafe_allow_html=True)
            
            # Advanced RAG service removed
            if st.session_state.backend_health:
                st.info("ℹ️ Advanced RAG service has been removed - using simplified streaming chat only")
        
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
        with st.expander("💬 Conversations", expanded=False):
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
        
        # Unified Reasoning System Section (Collapsible)
        with st.expander("🧠 Reasoning", expanded=False):
            st.markdown('<div class="section-header">Reasoning Configuration</div>', unsafe_allow_html=True)
            
            # Unified Reasoning Toggle
            use_unified_reasoning = st.checkbox(
                "Enable Unified Reasoning System",
                value=st.session_state.use_unified_reasoning,
                help="When enabled, uses the unified reasoning system that automatically selects the best approach for your problem"
            )
            if st.session_state.use_unified_reasoning != use_unified_reasoning:
                st.session_state.use_unified_reasoning = use_unified_reasoning
                save_user_settings()  # Save settings when changed
            
            if use_unified_reasoning:
                st.success("✅ Unified reasoning enabled - intelligent problem-solving with automatic mode selection")
                
                # Reasoning Mode Selection
                current_index = 0
                mode_options = [
                    ("auto", "🔄 Auto-detect (Recommended)"),
                    ("mathematical", "🔢 Mathematical"),
                    ("logical", "🧮 Logical"),
                    ("causal", "🔗 Causal"),
                    ("chain_of_thought", "🔗 Chain-of-Thought"),
                    ("tree_of_thoughts", "🌳 Tree-of-Thoughts"),
                    ("hybrid", "🔀 Hybrid (Multi-mode)")
                ]
                for i, (key, _) in enumerate(mode_options):
                    if key == st.session_state.selected_reasoning_mode:
                        current_index = i
                        break
                
                selected_mode = st.selectbox(
                    "Select Reasoning Mode",
                    options=mode_options,
                    format_func=lambda x: x[1],
                    index=current_index,
                    key="unified_reasoning_mode_select"
                )
                if st.session_state.selected_reasoning_mode != selected_mode[0]:
                    st.session_state.selected_reasoning_mode = selected_mode[0]
                    save_user_settings()  # Save settings when changed
                
                st.info(f"💡 Selected: {selected_mode[1]}")
                
                # System Status
                if st.session_state.backend_health:
                    st.markdown('<div class="section-header">System Status</div>', unsafe_allow_html=True)
                    
                    # Get unified reasoning system status
                    unified_status = get_unified_reasoning_status()
                    
                    if unified_status.get("status") == "available":
                        st.success("✅ Unified Reasoning System: Available")
                        
                        # Show available components
                        components = unified_status.get("components", {})
                        
                        # Core Components
                        if components.get("core", {}).get("status") == "available":
                            st.success("✅ Core Components: Available")
                        else:
                            st.warning("⚠️ Core Components: Limited")
                        
                        # Reasoning Engines
                        engines = components.get("engines", {})
                        if engines.get("mathematical", {}).get("status") == "available":
                            st.success("✅ Mathematical Engine: Available")
                        else:
                            st.warning("⚠️ Mathematical Engine: Limited")
                        
                        if engines.get("logical", {}).get("status") == "available":
                            st.success("✅ Logical Engine: Available")
                        else:
                            st.warning("⚠️ Logical Engine: Limited")
                        
                        if engines.get("causal", {}).get("status") == "available":
                            st.success("✅ Causal Engine: Available")
                        else:
                            st.warning("⚠️ Causal Engine: Limited")
                        
                        # Advanced Strategies
                        strategies = components.get("strategies", {})
                        if strategies.get("chain_of_thought", {}).get("status") == "available":
                            st.success("✅ Chain-of-Thought: Available")
                        else:
                            st.warning("⚠️ Chain-of-Thought: Limited")
                        
                        if strategies.get("tree_of_thoughts", {}).get("status") == "available":
                            st.success("✅ Tree-of-Thoughts: Available")
                        else:
                            st.warning("⚠️ Tree-of-Thoughts: Limited")
                        
                        # Refresh button
                        if st.button("🔄 Refresh System Status", key="refresh_unified_status"):
                            st.session_state.unified_reasoning_status = get_unified_reasoning_status()
                            st.rerun()
                    else:
                        st.warning("⚠️ Unified Reasoning System not available")
                        if unified_status.get("error"):
                            st.error(f"Error: {unified_status['error']}")
                else:
                    st.warning("Backend not available for unified reasoning system")
                
                # Sample Questions
                st.markdown('<div class="section-header">Sample Questions</div>', unsafe_allow_html=True)
                
                # Mathematical Problems
                st.markdown("**🔢 Mathematical Problems:**")
                math_questions = [
                    "What is 15 * 23 + 45?",
                    "Solve for x: 2x + 5 = 13",
                    "Calculate the area of a circle with radius 7",
                    "What is the derivative of x² + 3x + 2?"
                ]
                for i, question in enumerate(math_questions):
                    if st.button(f"📝 {question[:40]}...", key=f"unified_math_{i}_{st.session_state.chat_input_key}"):
                        st.session_state.sample_question = question
                        st.session_state.temp_reasoning_override = "unified"
                        st.session_state.chat_input_key += 1
                        st.rerun()
                
                # Logical Problems
                st.markdown("**🧮 Logical Problems:**")
                logic_questions = [
                    "If all birds can fly and penguins are birds, can penguins fly?",
                    "What is the logical conclusion: All A are B, All B are C, therefore...",
                    "Analyze this argument: If it rains, the ground gets wet. The ground is wet. Therefore, it rained."
                ]
                for i, question in enumerate(logic_questions):
                    if st.button(f"📝 {question[:40]}...", key=f"unified_logic_{i}_{st.session_state.chat_input_key}"):
                        st.session_state.sample_question = question
                        st.session_state.temp_reasoning_override = "unified"
                        st.session_state.chat_input_key += 1
                        st.rerun()
                
                # Causal Problems
                st.markdown("**🔗 Causal Problems:**")
                causal_questions = [
                    "Does exercise cause better health outcomes?",
                    "What causes seasonal changes in weather?",
                    "Analyze the causal relationship between diet and weight loss"
                ]
                for i, question in enumerate(causal_questions):
                    if st.button(f"📝 {question[:40]}...", key=f"unified_causal_{i}_{st.session_state.chat_input_key}"):
                        st.session_state.sample_question = question
                        st.session_state.temp_reasoning_override = "unified"
                        st.session_state.chat_input_key += 1
                        st.rerun()
                
                # Complex Problems
                st.markdown("**🔀 Complex Multi-faceted Problems:**")
                complex_questions = [
                    "A store sells apples for $2.50 per pound and oranges for $3.00 per pound. If a customer buys 2.5 pounds of apples and 1.8 pounds of oranges, and there's a 10% discount on the total, what is the final price? Also, explain the reasoning behind the calculation.",
                    "Design a study to test whether a new drug is effective. What are the key considerations for ensuring valid results?",
                    "Explain how a computer processes information from input to output, including the role of memory, CPU, and storage."
                ]
                for i, question in enumerate(complex_questions):
                    if st.button(f"📝 {question[:40]}...", key=f"unified_complex_{i}_{st.session_state.chat_input_key}"):
                        st.session_state.sample_question = question
                        st.session_state.temp_reasoning_override = "unified"
                        st.session_state.chat_input_key += 1
                        st.rerun()
                
                st.divider()
                st.info("💡 The unified reasoning system automatically selects the best approach for your problem, combining mathematical, logical, causal, and advanced reasoning strategies as needed.")
            else:
                st.info("💡 Enable unified reasoning for intelligent problem-solving with automatic mode selection")
        
        # Settings Section (Collapsible)
        with st.expander("⚙️ Settings", expanded=False):
            # Temperature slider
            temperature = st.slider("Temperature", 0.0, 1.0, st.session_state.temperature, 0.1)
            if st.session_state.temperature != temperature:
                st.session_state.temperature = temperature
                save_user_settings()  # Save settings when changed
            
            # Chat settings
            st.markdown('<div class="section-header">Chat Settings</div>', unsafe_allow_html=True)
            st.success("✅ Streaming enabled - responses appear in real-time")
            st.info("💡 All responses use streaming for optimal user experience")
            
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
    
    # Chat input (now fixed at bottom via CSS)
    prompt = st.chat_input("Ask me anything...", key=f"chat_input_{st.session_state.chat_input_key}")
    
    
    # Hidden file uploader that appears when upload button is clicked
    if st.session_state.get("show_uploader", False):
        with st.container():
            st.markdown("### 📄 Upload Document")
            uploaded_file = st.file_uploader(
                "Choose a document",
                type=['pdf', 'docx', 'txt', 'md', 'doc'],
                help="Upload PDF, DOCX, TXT, MD, or DOC files",
                key="main_uploader"
            )
            
            if uploaded_file is not None:
                # Automatic processing - no separate button needed
                with st.spinner("🔄 Processing document..."):
                    # Get current conversation ID and user ID
                    conversation_id = getattr(st.session_state, 'conversation_id', None)
                    user_id = st.session_state.get("user_id", "default_user")
                    
                    # Create a new conversation if none exists
                    if not conversation_id:
                        import uuid
                        conversation_id = str(uuid.uuid4())
                        st.session_state.conversation_id = conversation_id
                        print(f"🔍 DEBUG: Created new conversation for document upload: {conversation_id}")
                        
                        # Initialize empty messages list for the new conversation
                        if "messages" not in st.session_state or not st.session_state.messages:
                            st.session_state.messages = []
                    
                    result = upload_document_for_rag(
                        uploaded_file, 
                        conversation_id=conversation_id,
                        user_id=user_id
                    )
                    
                    if result.get("success"):
                        data = result.get("data", {})
                        document_id = data.get("document_id")
                        filename = uploaded_file.name
                        chunks_created = data.get("chunks_created", 0)
                        
                        # Store document info for potential summary
                        st.session_state.last_uploaded_document_id = document_id
                        st.session_state.last_uploaded_filename = filename
                        
                        # Add user message about the upload with file details
                        upload_message = f"📄 **Uploaded Document:** {filename}\n\n📊 **File Details:**\n- File Type: {data.get('file_type', 'Unknown')}\n- File Size: {data.get('file_size', 0)} bytes\n- Chunks Created: {chunks_created}\n- Document ID: {document_id}"
                        
                        st.session_state.messages.append({
                            "role": "user",
                            "content": upload_message
                        })
                        
                        # Hide uploader immediately
                        st.session_state.show_uploader = False
                        
                        # Generate automatic LLM response with document summary
                        with st.chat_message("assistant"):
                            response_container = st.empty()
                            
                            # Generate automatic response about the uploaded document
                            with st.spinner("📝 Analyzing uploaded document..."):
                                # Get conversation ID safely
                                conversation_id = getattr(st.session_state, 'conversation_id', None)
                                auto_response = generate_upload_response(filename, conversation_id)
                                
                                if auto_response:
                                    # Stream the response to chat
                                    response_container.markdown(auto_response)
                                    
                                    # Add assistant message to session state
                                    st.session_state.messages.append({
                                        "role": "assistant", 
                                        "content": auto_response
                                    })
                                    
                                    print(f"🔍 DEBUG: ✅ Auto-response generated for uploaded document")
                                else:
                                    fallback_msg = f"📄 **Document Analysis Complete**\n\n✅ **{filename}** has been successfully processed and added to our knowledge base!\n\n📊 **Processing Summary:**\n- Created {chunks_created} searchable chunks\n- Document is now available for questions\n- Context awareness is enabled for this conversation\n\n💡 **What you can do now:**\n- Ask specific questions about the document content\n- Request a summary of key points\n- Ask for analysis or insights from the document\n- Reference specific sections or topics"
                                    
                                    response_container.markdown(fallback_msg)
                                    
                                    # Add assistant message to session state
                                    st.session_state.messages.append({
                                        "role": "assistant", 
                                        "content": fallback_msg
                                    })
                        
                        st.rerun()
                    else:
                        st.error(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
            
            # Cancel button
            if st.button("❌ Cancel", key="cancel_upload"):
                st.session_state.show_uploader = False
                st.rerun()
    
    # Floating Buttons Container (fixed position via CSS)
    print(f"🔍 DEBUG: Stop button state - is_generating: {st.session_state.is_generating}, stop_generation: {st.session_state.stop_generation}")
    with st.container():
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        
        # Use columns with custom ratios to keep buttons compact and close together
        col1, col2, col3 = st.columns([1, 1, 8])  # Small buttons, large spacer
        
        with col1:
            if st.button("📄 Upload", key="upload_button", help="Upload a document"):
                st.session_state.show_uploader = True
                st.rerun()
        
        with col2:
            if st.button("🛑 Stop", key="stop_button", help="Stop the current generation"):
                print(f"🔍 DEBUG: Stop button clicked! Setting stop_generation = True")
                st.session_state.stop_generation = True
                st.session_state.is_generating = False
                
                # Save any accumulated content immediately
                if hasattr(st.session_state, 'current_response') and st.session_state.current_response:
                    print(f"🔍 DEBUG: Saving accumulated content from stop button: {len(st.session_state.current_response)} chars")
                    stopped_content = st.session_state.current_response + "\n\n*Generation stopped by user.*"
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": stopped_content,
                        "stopped": True
                    })
                    # Clear the current response
                    st.session_state.current_response = ""
                    print(f"🔍 DEBUG: ✅ SAVED stopped content to chat history from stop button")
                    # Force UI refresh to show the saved content immediately
                    st.rerun()
        
        with col3:
            st.empty()  # Empty column to push buttons to the right
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle sample question if selected (moved here to be part of the main chat flow)
    if st.session_state.sample_question:
        prompt = st.session_state.sample_question
        st.session_state.sample_question = None  # Clear the sample question
        st.session_state.chat_input_key += 1  # Force chat input refresh
    
    # Handle document summary to add to chat
    if hasattr(st.session_state, 'summary_to_add') and st.session_state.summary_to_add:
        # Add summary as assistant message
        st.session_state.messages.append({
            "role": "assistant", 
            "content": st.session_state.summary_to_add
        })
        # Clear the summary to add
        st.session_state.summary_to_add = None
        st.rerun()
    
    if prompt:
        # Reset stop generation flag and set generating state
        st.session_state.stop_generation = False
        st.session_state.is_generating = True
        print(f"🔍 DEBUG: Set is_generating = True, stop_generation = False")
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Document context is now automatically included in all chat requests
        # No need for separate summary handling - all prompts go through normal chat flow
        
        # Check backend health before sending
        if not st.session_state.backend_health:
            error_msg = f"❌ Backend service is not available. Please make sure the backend server is running on {BACKEND_URL}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.error(error_msg)
        else:
            # Check for temporary phase override from sample question buttons
            temp_override = st.session_state.get("temp_phase_override")
            temp_reasoning_override = st.session_state.get("temp_reasoning_override")
            
            # Debug: Print the override status
            if temp_override:
                print(f"🔍 DEBUG: Using temp_phase_override: {temp_override}")
                print(f"🔍 DEBUG: Current settings - Phase3: {st.session_state.use_phase3_reasoning}, Phase2: {st.session_state.use_phase2_reasoning}, Phase1: {st.session_state.use_reasoning_chat}")
            if temp_reasoning_override:
                print(f"🔍 DEBUG: Using temp_reasoning_override: {temp_reasoning_override}")
                print(f"🔍 DEBUG: Current settings - Unified: {st.session_state.use_unified_reasoning}, Mode: {st.session_state.selected_reasoning_mode}")
            
            # Send message to backend (with unified reasoning, Phase 3, Phase 2 reasoning, reasoning, RAG, or regular chat)
            if temp_reasoning_override == "unified":
                # Force unified reasoning for sample question
                print(f"🔍 DEBUG: FORCING unified reasoning for sample question")
                with st.spinner("🧠 Using unified reasoning system..."):
                    response_data = send_unified_reasoning_chat(
                        prompt, 
                        st.session_state.selected_reasoning_mode, 
                        st.session_state.conversation_id
                    )
            elif temp_override == "phase3":
                # Force Phase 3 for sample question
                print(f"🔍 DEBUG: FORCING Phase 3 reasoning for sample question")
                # Always use streaming
                if True:
                    # Use streaming Phase 3 reasoning response
                    response_data = send_streaming_phase3_reasoning_chat(
                        prompt, 
                        st.session_state.selected_phase3_strategy, 
                        st.session_state.conversation_id
                    )
                else:
                    # Use regular Phase 3 reasoning response
                    with st.spinner("🧠 Using Phase 3 advanced reasoning strategies..."):
                        response_data = send_phase3_reasoning_chat(
                            prompt, 
                            st.session_state.selected_phase3_strategy, 
                            st.session_state.conversation_id, 
                            use_streaming=False
                        )
            elif temp_override == "phase2":
                # Force Phase 2 for sample question
                print(f"🔍 DEBUG: FORCING Phase 2 reasoning for sample question")
                # Always use streaming
                if True:
                    # Use streaming Phase 2 reasoning response
                    response_data = send_streaming_phase2_reasoning_chat(
                        prompt, 
                        st.session_state.selected_phase2_engine, 
                        st.session_state.conversation_id
                    )
                else:
                    # Use regular Phase 2 reasoning response
                    with st.spinner("🚀 Using Phase 2 reasoning engine..."):
                        response_data = send_phase2_reasoning_chat(
                            prompt, 
                            st.session_state.selected_phase2_engine, 
                            st.session_state.conversation_id, 
                            use_streaming=False
                        )
            elif temp_override == "phase1":
                # Force Phase 1 for sample question
                print(f"🔍 DEBUG: FORCING Phase 1 reasoning for sample question")
                print(f"🔍 DEBUG: streaming always enabled")
                # Always use streaming
                if True:
                    # Use streaming reasoning response
                    print(f"🔍 DEBUG: Calling send_streaming_reasoning_chat for Phase 1")
                    with st.spinner("🧠 Thinking step by step..."):
                        response_data = send_streaming_reasoning_chat(prompt, st.session_state.conversation_id)
                    print(f"🔍 DEBUG: send_streaming_reasoning_chat returned: {type(response_data)}")
                else:
                    # Use regular reasoning response
                    print(f"🔍 DEBUG: Using non-streaming Phase 1")
                    with st.spinner("🧠 Thinking step by step..."):
                        response_data = send_reasoning_chat(prompt, st.session_state.conversation_id, use_streaming=False)
            elif st.session_state.use_unified_reasoning:
                # Use unified reasoning system for intelligent problem-solving
                with st.spinner("🧠 Using unified reasoning system..."):
                    response_data = send_unified_reasoning_chat(
                        prompt, 
                        st.session_state.selected_reasoning_mode, 
                        st.session_state.conversation_id
                    )
            elif st.session_state.use_phase3_reasoning:
                # Use Phase 3 advanced reasoning strategies for complex problem solving
                # Always use streaming
                if True:
                    # Use streaming Phase 3 reasoning response
                    response_data = send_streaming_phase3_reasoning_chat(
                        prompt, 
                        st.session_state.selected_phase3_strategy, 
                        st.session_state.conversation_id
                    )
                else:
                    # Use regular Phase 3 reasoning response
                    with st.spinner("🧠 Using Phase 3 advanced reasoning strategies..."):
                        response_data = send_phase3_reasoning_chat(
                            prompt, 
                            st.session_state.selected_phase3_strategy, 
                            st.session_state.conversation_id, 
                            use_streaming=False
                        )
            elif st.session_state.use_phase2_reasoning:
                # Use Phase 2 reasoning engines for specialized problem solving
                # Always use streaming
                if True:
                    # Use streaming Phase 2 reasoning response
                    response_data = send_streaming_phase2_reasoning_chat(
                        prompt, 
                        st.session_state.selected_phase2_engine, 
                        st.session_state.conversation_id
                    )
                else:
                    # Use regular Phase 2 reasoning response
                    with st.spinner("🚀 Using Phase 2 reasoning engine..."):
                        response_data = send_phase2_reasoning_chat(
                            prompt, 
                            st.session_state.selected_phase2_engine, 
                            st.session_state.conversation_id, 
                            use_streaming=False
                        )
            elif st.session_state.use_reasoning_chat:
                # Use reasoning chat for step-by-step solutions
                # Always use streaming
                if True:
                    # Use streaming reasoning response
                    with st.spinner("🧠 Thinking step by step..."):
                        response_data = send_streaming_reasoning_chat(prompt, st.session_state.conversation_id)
                else:
                    # Use regular reasoning response
                    with st.spinner("🧠 Thinking step by step..."):
                        response_data = send_reasoning_chat(prompt, st.session_state.conversation_id, use_streaming=False)
            elif st.session_state.use_rag and st.session_state.rag_stats.get("total_documents", 0) > 0:
                # Check if advanced RAG is enabled
                if st.session_state.use_advanced_rag:
                    # Use advanced RAG
                    with st.spinner("🚀 Thinking with Advanced RAG..."):
                        response_data = send_advanced_rag_chat(prompt, st.session_state.conversation_id)
                else:
                    # Use basic RAG (always streaming)
                    with st.spinner("Thinking with RAG..."):
                        response_data = send_streaming_rag_chat(prompt, st.session_state.conversation_id)
            else:
                # Use streaming chat (always enabled)
                response_data = send_to_backend(prompt, st.session_state.conversation_id, use_streaming=True)
            
            # Handle streaming responses differently since they're already displayed
            if temp_reasoning_override == "unified":
                # Handle unified reasoning response
                if response_data and not response_data.get("response", "").startswith("❌"):
                    # Update conversation ID if provided
                    if response_data.get("conversation_id"):
                        st.session_state.conversation_id = response_data["conversation_id"]
                    
                    # Create message data
                    message_data = {
                        "role": "assistant", 
                        "content": response_data["response"],
                        "unified_reasoning_used": True,
                        "reasoning_mode": response_data.get("reasoning_mode", "auto"),
                        "reasoning_type": response_data.get("reasoning_type", "unknown")
                    }
                    
                    # Add validation summary if available
                    if response_data.get("validation_summary"):
                        message_data["validation_summary"] = response_data.get("validation_summary")
                    
                    # Add unified reasoning information
                    if response_data.get("mode_used"):
                        mode_used = response_data.get("mode_used", "unknown")
                        confidence = response_data.get("confidence", 0.0)
                        steps_count = response_data.get("steps_count", 0)
                        
                        message_data["mode_used"] = mode_used
                        message_data["confidence"] = confidence
                        message_data["steps_count"] = steps_count
                    
                    st.session_state.messages.append(message_data)
                    st.session_state.conversations = get_conversations()
                    
                    # Clear temporary reasoning override after processing
                    if "temp_reasoning_override" in st.session_state:
                        print(f"🔍 DEBUG: Clearing temp_reasoning_override: {st.session_state.temp_reasoning_override}")
                        del st.session_state.temp_reasoning_override
                    
                    # Reset generating state
                    st.session_state.is_generating = False
                else:
                    error_msg = response_data["response"] if response_data else "❌ Unable to get response from unified reasoning system. Please try again or check the backend logs."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.error(error_msg)
            elif temp_override == "phase1":
                # For streaming Phase 1 reasoning, handle the generator response
                print(f"🔍 DEBUG: Handling Phase 1 streaming response")
                print(f"🔍 DEBUG: response_data type: {type(response_data)}")
                # Create a placeholder for the assistant message
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    # Store in session state so stop button can access it
                    st.session_state.current_response = ""
                    
                    # Stream the response chunks
                    chunk_count = 0
                    for chunk in response_data:
                        # Check for stop signal and save content immediately
                        print(f"🔍 DEBUG: Checking stop signal - stop_generation: {st.session_state.stop_generation}")
                        if st.session_state.stop_generation:
                            print(f"🔍 DEBUG: ✅ STOP SIGNAL DETECTED! Saving current content...")
                            if full_response:
                                final_content = full_response + "\n\n*Generation stopped by user.*"
                                message_placeholder.markdown(final_content)
                                message_data = {
                                    "role": "assistant", 
                                    "content": final_content,
                                    "stopped": True,
                                    "reasoning_used": True
                                }
                                st.session_state.messages.append(message_data)
                                print(f"🔍 DEBUG: ✅ SUCCESSFULLY SAVED stopped content to chat history")
                            else:
                                print(f"🔍 DEBUG: ⚠️ No content to save")
                            break
                        
                        chunk_count += 1
                        print(f"🔍 DEBUG: Processing chunk {chunk_count}: {type(chunk)} - {str(chunk)[:100]}...")
                        
                        if isinstance(chunk, str):
                            full_response += chunk
                            # Update session state so stop button can access current content
                            st.session_state.current_response = full_response
                            message_placeholder.markdown(full_response + "▌")
                        elif isinstance(chunk, dict):
                            print(f"🔍 DEBUG: Got dict chunk: {chunk}")
                            # This is the final response data
                            if chunk.get("response", "").startswith("❌"):
                                error_msg = chunk["response"]
                                message_placeholder.error(error_msg)
                                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                                print(f"🔍 DEBUG: Saved Phase 1 error message")
                                break
                            else:
                                # Update conversation ID if provided
                                if chunk.get("conversation_id"):
                                    st.session_state.conversation_id = chunk["conversation_id"]
                                
                                # Update the final message
                                final_response = chunk.get("response", full_response)
                                message_placeholder.markdown(final_response)
                                
                                # Add to chat history
                                message_data = {
                                    "role": "assistant", 
                                    "content": final_response,
                                    "reasoning_used": chunk.get("reasoning_used", False),
                                    "steps_count": chunk.get("steps_count"),
                                    "validation_summary": chunk.get("validation_summary")
                                }
                                if chunk.get("stopped"):
                                    message_data["stopped"] = True
                                st.session_state.messages.append(message_data)
                                print(f"🔍 DEBUG: Phase 1 message added to chat history")
                                # Clear current response since generation is complete
                                st.session_state.current_response = ""
                                break
                    print(f"🔍 DEBUG: Phase 1 streaming completed, processed {chunk_count} chunks")
                    # Clear current response in case of any exit path
                    st.session_state.current_response = ""
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Clear temporary phase override after processing
                    if "temp_phase_override" in st.session_state:
                        print(f"🔍 DEBUG: Clearing temp_phase_override: {st.session_state.temp_phase_override}")
                        del st.session_state.temp_phase_override
                    
                    # Reset generating state
                    st.session_state.is_generating = False
            elif st.session_state.use_unified_reasoning:
                # Handle unified reasoning response
                if response_data and not response_data.get("response", "").startswith("❌"):
                    # Update conversation ID if provided
                    if response_data.get("conversation_id"):
                        st.session_state.conversation_id = response_data["conversation_id"]
                    
                    # Create message data
                    message_data = {
                        "role": "assistant", 
                        "content": response_data["response"],
                        "unified_reasoning_used": True,
                        "reasoning_mode": response_data.get("reasoning_mode", "auto"),
                        "reasoning_type": response_data.get("reasoning_type", "unknown")
                    }
                    
                    # Add validation summary if available
                    if response_data.get("validation_summary"):
                        message_data["validation_summary"] = response_data.get("validation_summary")
                    
                    # Add unified reasoning information
                    if response_data.get("mode_used"):
                        mode_used = response_data.get("mode_used", "unknown")
                        confidence = response_data.get("confidence", 0.0)
                        steps_count = response_data.get("steps_count", 0)
                        
                        message_data["mode_used"] = mode_used
                        message_data["confidence"] = confidence
                        message_data["steps_count"] = steps_count
                    
                    st.session_state.messages.append(message_data)
                    st.session_state.conversations = get_conversations()
                    
                    # Reset generating state
                    st.session_state.is_generating = False
                else:
                    error_msg = response_data["response"] if response_data else "❌ Unable to get response from unified reasoning system. Please try again or check the backend logs."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.error(error_msg)
            elif not st.session_state.use_reasoning_chat and not st.session_state.use_rag:
                # Handle basic streaming chat response
                print(f"🔍 DEBUG: Handling basic streaming chat response")
                if response_data and not response_data.get("response", "").startswith("❌"):
                    # Update conversation ID if provided
                    if response_data.get("conversation_id"):
                        st.session_state.conversation_id = response_data["conversation_id"]
                    
                    # Add assistant response to chat history (preserve content even if stopped)
                    message_data = {"role": "assistant", "content": response_data["response"]}
                    if response_data.get("stopped"):
                        message_data["stopped"] = True
                        print(f"🔍 DEBUG: Saving stopped basic streaming response to chat history")
                    st.session_state.messages.append(message_data)
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Reset generating state
                    st.session_state.is_generating = False
                else:
                    error_msg = response_data["response"] if response_data else "❌ Unable to get response from backend. Please try again or check the backend logs."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.error(error_msg)
                    
                    # Reset generating state on error
                    st.session_state.is_generating = False
            elif temp_override == "phase2":
                # For streaming Phase 2 reasoning, the function handles its own display
                print(f"🔍 DEBUG: Handling Phase 2 streaming response")
                
                # response_data is a dict returned from the streaming function
                if response_data:
                    if response_data.get("response", "").startswith("❌"):
                        error_msg = response_data["response"]
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    else:
                        # Update conversation ID if provided
                        if response_data.get("conversation_id"):
                            st.session_state.conversation_id = response_data["conversation_id"]
                        
                        # Add to chat history with Phase 2 metadata (preserve content even if stopped)
                        message_data = {
                            "role": "assistant", 
                            "content": response_data["response"],
                            "phase2_engine": True,
                            "engine_used": response_data.get("engine_used", "unknown"),
                            "reasoning_type": response_data.get("reasoning_type", "unknown"),
                            "confidence": response_data.get("confidence", 0.0),
                            "steps_count": response_data.get("steps_count"),
                            "validation_summary": response_data.get("validation_summary")
                        }
                        if response_data.get("stopped"):
                            message_data["stopped"] = True
                            print(f"🔍 DEBUG: Saving stopped Phase 2 response to chat history")
                        st.session_state.messages.append(message_data)
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Clear temporary phase override after processing
                    if "temp_phase_override" in st.session_state:
                        print(f"🔍 DEBUG: Clearing temp_phase_override: {st.session_state.temp_phase_override}")
                        del st.session_state.temp_phase_override
                    
                    # Reset generating state
                    st.session_state.is_generating = False
                    
                    # Force rerun to update sidebar
                    st.rerun()
            elif temp_override == "phase3":
                # For streaming Phase 3 reasoning, the function handles its own display
                print(f"🔍 DEBUG: Handling Phase 3 streaming response")
                print(f"🔍 DEBUG: response_data = {response_data}")
                print(f"🔍 DEBUG: response_data type = {type(response_data)}")
                
                # response_data is a dict returned from the streaming function
                if response_data:
                    print(f"🔍 DEBUG: response_data exists, checking content...")
                    if response_data.get("response", "").startswith("❌"):
                        error_msg = response_data["response"]
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        print(f"🔍 DEBUG: Saved error message to chat history")
                    else:
                        print(f"🔍 DEBUG: Processing normal response...")
                        # Update conversation ID if provided
                        if response_data.get("conversation_id"):
                            st.session_state.conversation_id = response_data["conversation_id"]
                        
                        # Add to chat history with Phase 3 metadata (preserve content even if stopped)
                        message_data = {
                            "role": "assistant", 
                            "content": response_data["response"],
                            "phase3_strategy": True,
                            "strategy_used": response_data.get("strategy_used", "unknown"),
                            "reasoning_type": response_data.get("reasoning_type", "unknown"),
                            "confidence": response_data.get("confidence", 0.0),
                            "steps_count": response_data.get("steps_count"),
                            "validation_summary": response_data.get("validation_summary")
                        }
                        print(f"🔍 DEBUG: Checking if stopped: {response_data.get('stopped')}")
                        if response_data.get("stopped"):
                            message_data["stopped"] = True
                            print(f"🔍 DEBUG: Saving stopped Phase 3 response to chat history")
                        else:
                            print(f"🔍 DEBUG: Saving normal Phase 3 response to chat history")
                        st.session_state.messages.append(message_data)
                        print(f"🔍 DEBUG: Message added to chat history")
                else:
                    print(f"🔍 DEBUG: response_data is None or empty!")
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Clear temporary phase override after processing
                    if "temp_phase_override" in st.session_state:
                        print(f"🔍 DEBUG: Clearing temp_phase_override: {st.session_state.temp_phase_override}")
                        del st.session_state.temp_phase_override
                    
                    # Reset generating state
                    st.session_state.is_generating = False
            elif st.session_state.use_phase2_reasoning:
                # For streaming Phase 2 reasoning, the response is already displayed in real-time
                if response_data and not response_data.get("response", "").startswith("❌"):
                    # Update conversation ID if provided
                    if response_data.get("conversation_id"):
                        st.session_state.conversation_id = response_data["conversation_id"]
                    
                    # Add assistant response to chat history
                    message_data = {"role": "assistant", "content": response_data["response"]}
                    
                    # Add Phase 2 engine information
                    if response_data.get("engine_used"):
                        message_data["phase2_engine"] = True
                        message_data["engine_used"] = response_data.get("engine_used", "unknown")
                        message_data["reasoning_type"] = response_data.get("reasoning_type", "unknown")
                        message_data["confidence"] = response_data.get("confidence", 0.0)
                        message_data["steps_count"] = response_data.get("steps_count", 0)
                        message_data["validation_summary"] = response_data.get("validation_summary")
                    
                    # Add Phase 3 strategy information
                    if st.session_state.use_phase3_reasoning and response_data.get("strategy_used"):
                        strategy_used = response_data.get("strategy_used", "unknown")
                        reasoning_type = response_data.get("reasoning_type", "unknown")
                        confidence = response_data.get("confidence", 0.0)
                        
                        # Add Phase 3 strategy info to the message
                        phase3_info = f"\n\n🚀 **Phase 3 Strategy Info:**\n"
                        phase3_info += f"• Strategy used: {strategy_used.title()}\n"
                        phase3_info += f"• Reasoning type: {reasoning_type.title()}\n"
                        phase3_info += f"• Confidence: {confidence:.2f}\n"
                        
                        if response_data.get("steps_count"):
                            phase3_info += f"• Steps generated: {response_data['steps_count']}\n"
                        
                        if response_data.get("validation_summary"):
                            phase3_info += f"• Validation: {response_data['validation_summary']}\n"
                        
                        message_data["content"] += phase3_info
                        message_data["phase3_strategy"] = True
                        message_data["strategy_used"] = strategy_used
                        message_data["reasoning_type"] = reasoning_type
                        message_data["confidence"] = confidence
                    
                    st.session_state.messages.append(message_data)
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Force rerun to update sidebar
                    st.rerun()
                else:
                    error_msg = response_data["response"] if response_data else "❌ Unable to get response from backend. Please try again or check the backend logs."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.error(error_msg)
                    
                    # Reset generating state on error
                    st.session_state.is_generating = False
            elif st.session_state.use_rag and st.session_state.rag_stats.get("total_documents", 0) > 0:
                # For streaming RAG, the response is already displayed in real-time
                if response_data and not response_data.get("response", "").startswith("❌"):
                    # Update conversation ID if provided
                    if response_data.get("conversation_id"):
                        st.session_state.conversation_id = response_data["conversation_id"]
                    
                    # Add assistant response to chat history (preserve content even if stopped)
                    message_data = {"role": "assistant", "content": response_data["response"]}
                    if response_data.get("stopped"):
                        message_data["stopped"] = True
                        print(f"🔍 DEBUG: Saving stopped RAG streaming response to chat history (second instance)")
                    
                    # Handle advanced RAG information
                    if st.session_state.use_advanced_rag and response_data.get("strategies_used"):
                        strategies_used = response_data.get("strategies_used", [])
                        results_count = response_data.get("results_count", 0)
                        
                        # Add advanced RAG info to the message
                        advanced_info = f"\n\n🚀 **Advanced RAG Info:**\n"
                        advanced_info += f"• Strategies used: {', '.join(strategies_used)}\n"
                        advanced_info += f"• Results retrieved: {results_count}\n"
                        
                        if response_data.get("has_context"):
                            advanced_info += "• Context-aware retrieval: ✅\n"
                        else:
                            advanced_info += "• Context-aware retrieval: ❌\n"
                        
                        # Add document references from results
                        if response_data.get("results"):
                            doc_references = []
                            for i, result in enumerate(response_data["results"][:3]):  # Show first 3 results
                                filename = result.get("filename", f"Document {i+1}")
                                strategy = result.get("strategy", "unknown")
                                score = result.get("relevance_score", 0)
                                doc_references.append(f"{filename} ({strategy}, score: {score:.2f})")
                            
                            if doc_references:
                                advanced_info += f"• Documents used: {', '.join(doc_references)}\n"
                        
                        message_data["content"] += advanced_info
                        message_data["advanced_rag"] = True
                        message_data["strategies_used"] = strategies_used
                        message_data["results_count"] = results_count
                    
                    # For advanced RAG, document references are already included in the advanced info above
                    # For basic RAG, check if backend provided RAG context directly
                    if not st.session_state.use_advanced_rag and response_data.get("rag_context") and response_data.get("has_context") == True:
                        message_data["rag_context"] = response_data["rag_context"]
                        message_data["has_context"] = response_data["has_context"]
                        # Add RAG reference to the message content
                        message_data["content"] += f"\n\n📚 **RAG Reference:** {response_data.get('rag_context', '')}"
                    elif not st.session_state.use_advanced_rag:
                        # Try to extract RAG context from the content itself for basic RAG
                        extracted_rag_context = extract_rag_context_from_content(response_data["response"])
                        
                        if extracted_rag_context:
                            message_data["rag_context"] = extracted_rag_context
                            message_data["has_context"] = True
                            # Add RAG reference to the message content
                            message_data["content"] += f"\n\n📚 **RAG Reference:** {extracted_rag_context}"
                        else:
                            # Add note if no RAG context was found
                            message_data["content"] += f"\n\nℹ️ *No relevant documents found in RAG database.*"
                    
                    st.session_state.messages.append(message_data)
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Reset generating state
                    st.session_state.is_generating = False
                else:
                    error_msg = response_data["response"] if response_data else "❌ Unable to get response from backend. Please try again or check the backend logs."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.error(error_msg)
                    
                    # Reset generating state on error
                    st.session_state.is_generating = False
            elif st.session_state.use_reasoning_chat:
                # Handle streaming reasoning responses
                # Create a placeholder for the assistant message
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    # Stream the response chunks
                    for chunk in response_data:
                        if isinstance(chunk, str):
                            full_response += chunk
                            message_placeholder.markdown(full_response + "▌")
                        elif isinstance(chunk, dict):
                            # This is the final response data
                            if chunk.get("response", "").startswith("❌"):
                                error_msg = chunk["response"]
                                message_placeholder.error(error_msg)
                                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                                break
                            else:
                                # Update conversation ID if provided
                                if chunk.get("conversation_id"):
                                    st.session_state.conversation_id = chunk["conversation_id"]
                                
                                # Update the final message (no reasoning info needed)
                                final_response = chunk.get("response", full_response)
                                message_placeholder.markdown(final_response)
                                
                                # Add to chat history (preserve content even if stopped)
                                message_data = {
                                    "role": "assistant", 
                                    "content": final_response,
                                    "reasoning_used": chunk.get("reasoning_used", False),
                                    "steps_count": chunk.get("steps_count"),
                                    "validation_summary": chunk.get("validation_summary")
                                }
                                if chunk.get("stopped"):
                                    message_data["stopped"] = True
                                st.session_state.messages.append(message_data)
                                break
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Reset generating state
                    st.session_state.is_generating = False
            else:
                # Handle regular responses (non-streaming or non-RAG)
                if response_data and not response_data["response"].startswith("❌"):
                    # Update conversation ID if provided
                    if response_data.get("conversation_id"):
                        st.session_state.conversation_id = response_data["conversation_id"]
                    
                    # Add assistant response to chat history (preserve content even if stopped)
                    message_data = {"role": "assistant", "content": response_data["response"]}
                    if response_data.get("stopped"):
                        message_data["stopped"] = True
                    
                    # Handle advanced RAG information for regular responses
                    if st.session_state.use_advanced_rag and response_data.get("strategies_used"):
                        strategies_used = response_data.get("strategies_used", [])
                        results_count = response_data.get("results_count", 0)
                        
                        # Add advanced RAG info to the message
                        advanced_info = f"\n\n🚀 **Advanced RAG Info:**\n"
                        advanced_info += f"• Strategies used: {', '.join(strategies_used)}\n"
                        advanced_info += f"• Results retrieved: {results_count}\n"
                        
                        if response_data.get("has_context"):
                            advanced_info += "• Context-aware retrieval: ✅\n"
                        else:
                            advanced_info += "• Context-aware retrieval: ❌\n"
                        
                        # Add document references from results
                        if response_data.get("results"):
                            doc_references = []
                            for i, result in enumerate(response_data["results"][:3]):  # Show first 3 results
                                filename = result.get("filename", f"Document {i+1}")
                                strategy = result.get("strategy", "unknown")
                                score = result.get("relevance_score", 0)
                                doc_references.append(f"{filename} ({strategy}, score: {score:.2f})")
                            
                            if doc_references:
                                advanced_info += f"• Documents used: {', '.join(doc_references)}\n"
                        
                        message_data["content"] += advanced_info
                        message_data["advanced_rag"] = True
                        message_data["strategies_used"] = strategies_used
                        message_data["results_count"] = results_count
                    
                    # Add RAG context if available (for basic RAG)
                    if not st.session_state.use_advanced_rag and response_data.get("rag_context") and response_data.get("has_context"):
                        message_data["rag_context"] = response_data["rag_context"]
                        message_data["has_context"] = response_data["has_context"]
                    
                    # Add reasoning metadata for regular responses (no display needed)
                    if response_data.get("reasoning_used"):
                        message_data["reasoning_used"] = True
                        message_data["steps_count"] = response_data.get("steps_count")
                        message_data["validation_summary"] = response_data.get("validation_summary")
                    
                    # Add Phase 2 engine information
                    if st.session_state.use_phase2_reasoning and response_data.get("engine_used"):
                        engine_used = response_data.get("engine_used", "unknown")
                        reasoning_type = response_data.get("reasoning_type", "unknown")
                        confidence = response_data.get("confidence", 0.0)
                        
                        # Add Phase 2 engine info to the message
                        phase2_info = f"\n\n🚀 **Phase 2 Engine Info:**\n"
                        phase2_info += f"• Engine used: {engine_used.title()}\n"
                        phase2_info += f"• Reasoning type: {reasoning_type.title()}\n"
                        phase2_info += f"• Confidence: {confidence:.2f}\n"
                        
                        if response_data.get("steps_count"):
                            phase2_info += f"• Steps generated: {response_data['steps_count']}\n"
                        
                        if response_data.get("validation_summary"):
                            phase2_info += f"• Validation: {response_data['validation_summary']}\n"
                        
                        message_data["content"] += phase2_info
                        message_data["phase2_engine"] = True
                        message_data["engine_used"] = engine_used
                        message_data["reasoning_type"] = reasoning_type
                        message_data["confidence"] = confidence
                    
                    # Add Phase 3 strategy information
                    if st.session_state.use_phase3_reasoning and response_data.get("strategy_used"):
                        strategy_used = response_data.get("strategy_used", "unknown")
                        reasoning_type = response_data.get("reasoning_type", "unknown")
                        confidence = response_data.get("confidence", 0.0)
                        
                        # Add Phase 3 strategy info to the message
                        phase3_info = f"\n\n🚀 **Phase 3 Strategy Info:**\n"
                        phase3_info += f"• Strategy used: {strategy_used.title()}\n"
                        phase3_info += f"• Reasoning type: {reasoning_type.title()}\n"
                        phase3_info += f"• Confidence: {confidence:.2f}\n"
                        
                        if response_data.get("steps_count"):
                            phase3_info += f"• Steps generated: {response_data['steps_count']}\n"
                        
                        if response_data.get("validation_summary"):
                            phase3_info += f"• Validation: {response_data['validation_summary']}\n"
                        
                        message_data["content"] += phase3_info
                        message_data["phase3_strategy"] = True
                        message_data["strategy_used"] = strategy_used
                        message_data["reasoning_type"] = reasoning_type
                        message_data["confidence"] = confidence
                    
                    st.session_state.messages.append(message_data)
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Display assistant response (streaming responses are handled separately)
                    if False:  # This block is no longer needed since streaming is always enabled
                        with st.chat_message("assistant"):
                            st.markdown(response_data["response"])
                    
                    # Reset generating state
                    st.session_state.is_generating = False
                else:
                    error_msg = response_data["response"] if response_data else "❌ Unable to get response from backend. Please try again or check the backend logs."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.error(error_msg)
                    
                    # Reset generating state on error
                    st.session_state.is_generating = False
    
if __name__ == "__main__":
    main() 