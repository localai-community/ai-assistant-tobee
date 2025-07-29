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
    if "use_advanced_rag" not in st.session_state:
        st.session_state.use_advanced_rag = False
    if "use_phase2_reasoning" not in st.session_state:
        st.session_state.use_phase2_reasoning = True
    if "selected_phase2_engine" not in st.session_state:
        st.session_state.selected_phase2_engine = "auto"
    if "mcp_tools" not in st.session_state:
        st.session_state.mcp_tools = []
    if "mcp_health" not in st.session_state:
        st.session_state.mcp_health = {}
    if "use_streaming" not in st.session_state:
        st.session_state.use_streaming = True
    if "advanced_rag_strategies" not in st.session_state:
        st.session_state.advanced_rag_strategies = []
    if "use_reasoning_chat" not in st.session_state:
        st.session_state.use_reasoning_chat = True
    if "sample_question" not in st.session_state:
        st.session_state.sample_question = None
    if "chat_input_key" not in st.session_state:
        st.session_state.chat_input_key = 0
    if "temp_phase_override" not in st.session_state:
        st.session_state.temp_phase_override = None
    # Add stop button state variable
    if "stop_generation" not in st.session_state:
        st.session_state.stop_generation = False
    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False
    # Add Phase 2 reasoning engine state variables
    if "use_phase2_reasoning" not in st.session_state:
        st.session_state.use_phase2_reasoning = True
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
    if "use_phase3_reasoning" not in st.session_state:
        st.session_state.use_phase3_reasoning = True
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
    """Get RAG statistics from backend."""
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
                        "vector_db_size_mb": vector_stats.get("storage_size_mb", 0.0),
                        "collection_name": vector_stats.get("collection_name", ""),
                        "persist_directory": vector_stats.get("persist_directory", "")
                    }
                    return stats
                return {}
    except Exception as e:
        print(f"Error getting RAG stats: {e}")
        pass
    return {}

def get_advanced_rag_strategies() -> List[Dict]:
    """Get available advanced RAG strategies from backend."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/advanced-rag/strategies", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return data.get('strategies', {})
    except:
        pass
    return {}

def get_advanced_rag_health() -> Dict:
    """Get advanced RAG health status."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/api/v1/advanced-rag/health", timeout=5.0)
            if response.status_code == 200:
                return response.json()
    except:
        pass
    return {"status": "unhealthy", "error": "Connection failed"}

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
            model = st.session_state.available_models[0] if st.session_state.available_models else "llama3:latest"
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "use_reasoning": True,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True
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
            model = st.session_state.available_models[0] if st.session_state.available_models else "llama3:latest"
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "use_reasoning": True,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            # Use streaming endpoint with proper httpx streaming
            with client.stream(
                "POST",
                f"{BACKEND_URL}/api/v1/reasoning-chat/stream",
                json=payload,
                timeout=120.0
            ) as response:
                if response.status_code == 200:
                    # Handle streaming response
                    full_response = ""
                    for chunk in response.iter_text():
                        # Check for stop signal
                        if st.session_state.stop_generation:
                            yield {"response": full_response + "\n\n*Generation stopped by user.*", "stopped": True}
                            return
                        
                        if chunk:
                            # Handle different response formats
                            if chunk.startswith('data: '):
                                try:
                                    data = json.loads(chunk[6:])  # Remove 'data: ' prefix
                                    content = data.get('content', '')
                                    full_response += content
                                    yield content
                                except json.JSONDecodeError:
                                    continue
                            else:
                                # Direct text response
                                full_response += chunk
                                yield chunk
                    
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

def upload_document_for_rag(uploaded_file) -> Dict:
    """Upload a document for RAG processing."""
    try:
        with httpx.Client() as client:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            response = client.post(f"{BACKEND_URL}/api/v1/rag/upload", files=files, timeout=60.0)
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data}
            else:
                return {"success": False, "error": f"Upload failed: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"success": False, "error": f"Upload error: {str(e)}"}

def send_advanced_rag_chat(message: str, conversation_id: Optional[str] = None) -> Optional[Dict]:
    """Send message to backend with advanced RAG enhancement."""
    try:
        with httpx.Client() as client:
            # Use the first available model or fallback to llama3:latest
            model = st.session_state.available_models[0] if st.session_state.available_models else "llama3:latest"
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "k": 4,
                "use_advanced_strategies": True,
                "conversation_history": st.session_state.messages if st.session_state.messages else []
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            response = client.post(
                f"{BACKEND_URL}/api/v1/advanced-rag/chat",
                json=payload,
                timeout=120.0  # Increased timeout for advanced RAG processing
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "response": data.get("response", "No response from backend"),
                    "conversation_id": data.get("conversation_id"),
                    "strategies_used": data.get("strategies_used", []),
                    "results_count": data.get("results_count", 0),
                    "has_context": data.get("has_context", False),
                    "results": data.get("results", [])
                }
            elif response.status_code == 503:
                return {"response": "❌ Ollama service is not available. Please make sure Ollama is running."}
            else:
                return {"response": f"Backend error: {response.status_code}"}
                
    except httpx.TimeoutException:
        return {"response": "Request timed out. Please try again."}
    except Exception as e:
        return {"response": f"Communication error: {str(e)}"}

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
                        for line in response.iter_lines():
                            # Check for stop signal
                            if st.session_state.stop_generation:
                                message_placeholder.markdown(full_response + "\n\n*Generation stopped by user.*")
                                return {"response": full_response + "\n\n*Generation stopped by user.*", "stopped": True}
                            
                            if line:
                                # httpx.iter_lines() returns strings, not bytes
                                if line.startswith('data: '):
                                    data_str = line[6:]  # Remove 'data: ' prefix
                                    try:
                                        data = json.loads(data_str)
                                        
                                        if data.get("type") == "error":
                                            return {"response": f"Error: {data.get('error', 'Unknown error')}"}
                                        
                                        # Handle different response types
                                        if "content" in data:
                                            chunk = data["content"]
                                            full_response += chunk
                                            message_placeholder.markdown(full_response + "▌")
                                            print(f"🔍 Added chunk: {chunk[:50]}...")
                                            
                                            # Add artificial delay to see streaming effect (optional)
                                            # Uncomment the next line to slow down streaming for testing
                                            # time.sleep(0.2)  # 200ms delay
                                        
                                        elif "conversation_id" in data:
                                            # Update conversation ID
                                            st.session_state.conversation_id = data["conversation_id"]
                                        
                                        elif "rag_context" in data:
                                            # Found rag_context - this is the final line
                                            message_placeholder.markdown(full_response)
                                            # Debug: Log what we found
                                            print(f"🔍 RAG CONTEXT FOUND: {data.get('rag_context', '')}")
                                            print(f"🔍 HAS CONTEXT: {data.get('has_context', False)}")
                                            return {
                                                "response": full_response,
                                                "conversation_id": st.session_state.conversation_id,
                                                "rag_context": data.get("rag_context", ""),
                                                "has_context": data.get("has_context", True)  # Assume True if rag_context is present
                                            }

                                            
                                    except json.JSONDecodeError as e:
                                        continue
                        
                        # If we get here without returning, the streaming ended without content
                        if not full_response:
                            return {"response": "No response generated. Please try again."}
                        else:
                            # If we have content but no rag_context line, return what we have
                            return {
                                "response": full_response,
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
                            # Check for stop signal
                            if st.session_state.stop_generation:
                                message_placeholder.markdown(full_response + "\n\n*Generation stopped by user.*")
                                return {"response": full_response + "\n\n*Generation stopped by user.*", "stopped": True}
                            
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
            # Use reasoning chat for step-by-step solutions
            if st.session_state.use_streaming:
                # Use streaming reasoning response with real-time display
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
            else:
                # Use regular reasoning response
                with st.spinner("🧠 Thinking step by step..."):
                    response_data = send_reasoning_chat(question, st.session_state.conversation_id, use_streaming=False)
                    process_chat_response(response_data, question)
        elif st.session_state.use_rag and st.session_state.rag_stats.get("total_documents", 0) > 0:
            # Check if advanced RAG is enabled
            if st.session_state.use_advanced_rag:
                # Use advanced RAG
                with st.spinner("🚀 Thinking with Advanced RAG..."):
                    response_data = send_advanced_rag_chat(question, st.session_state.conversation_id)
                    process_chat_response(response_data, question)
            else:
                # Use basic RAG
                if st.session_state.use_streaming:
                    # Use streaming RAG response with real-time display
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
                                        "has_context": chunk.get("has_context", False)
                                    }
                                    st.session_state.messages.append(message_data)
                                    break
                        
                        # Refresh conversation list to include the new conversation
                        st.session_state.conversations = get_conversations()
                else:
                    # Use regular non-streaming RAG response
                    with st.spinner("Thinking with RAG..."):
                        response_data = send_rag_chat(question, st.session_state.conversation_id)
                        process_chat_response(response_data, question)
        else:
            # Use streaming or regular response based on setting
            if st.session_state.use_reasoning_chat:
                # Use reasoning chat
                if st.session_state.use_streaming:
                    # Use streaming reasoning response
                    response_data = send_streaming_reasoning_chat(question, st.session_state.conversation_id)
                else:
                    # Use regular non-streaming reasoning response
                    with st.spinner("Thinking with reasoning..."):
                        response_data = send_reasoning_chat(question, st.session_state.conversation_id, use_streaming=False)
            else:
                # Use regular chat
                if st.session_state.use_streaming:
                    # Use streaming response
                    response_data = send_to_backend(question, st.session_state.conversation_id, use_streaming=True)
                else:
                    # Use regular non-streaming response
                    with st.spinner("Thinking..."):
                        response_data = send_to_backend(question, st.session_state.conversation_id, use_streaming=False)
            
            # Handle streaming RAG responses differently since they're already displayed
            if st.session_state.use_phase2_reasoning and st.session_state.use_streaming:
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
            elif st.session_state.use_rag and st.session_state.use_streaming and st.session_state.rag_stats.get("total_documents", 0) > 0:
                # For streaming RAG, the response is already displayed in real-time
                if response_data and not response_data.get("response", "").startswith("❌"):
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
            elif st.session_state.use_reasoning_chat and st.session_state.use_streaming:
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

def display_chat_messages():
    """Display chat messages."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

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
            model = st.session_state.available_models[0] if st.session_state.available_models else "llama3:latest"
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "use_phase2_reasoning": True,
                "engine_type": engine_type,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True
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
            model = st.session_state.available_models[0] if st.session_state.available_models else "llama3:latest"
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "use_phase2_reasoning": True,
                "engine_type": engine_type,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            print(f"🔍 Sending request to: {BACKEND_URL}/api/v1/phase2-reasoning/stream")
            print(f"🔍 Payload: {payload}")
            
            # Create assistant message container for streaming
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
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
            model = st.session_state.available_models[0] if st.session_state.available_models else "llama3:latest"
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "use_phase3_reasoning": True,
                "strategy_type": strategy_type,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True
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

def send_streaming_phase3_reasoning_chat(message: str, strategy_type: str = "auto", conversation_id: Optional[str] = None):
    """Send message to backend with Phase 3 reasoning strategies using streaming."""
    st.info("🧠 Starting Phase 3 advanced reasoning streaming...")
    print(f"🔍 Phase 3 streaming started for message: {message[:50]}...")
    try:
        with httpx.Client() as client:
            # Use the first available model or fallback to llama3:latest
            model = st.session_state.available_models[0] if st.session_state.available_models else "llama3:latest"
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "use_phase3_reasoning": True,
                "strategy_type": strategy_type,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            print(f"🔍 Sending request to: {BACKEND_URL}/api/v1/phase3-reasoning/stream")
            print(f"🔍 Payload: {payload}")
            
            # Create assistant message container for streaming
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
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
    
    # Check backend health and get models
    st.session_state.backend_health = check_backend_health()
    if st.session_state.backend_health:
        st.session_state.available_models = get_available_models()
        st.session_state.conversations = get_conversations()
        st.session_state.rag_stats = get_rag_stats()
        
        # Debug output
        print(f"🔍 Main function - RAG Stats loaded: {st.session_state.rag_stats}")
        print(f"🔍 Total documents: {st.session_state.rag_stats.get('total_documents', 0)}")
    
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
        
        # Reasoning System Section (Collapsible)
        with st.expander("🧠 Phase 1: Reasoning System", expanded=False):
            # Reasoning Chat Toggle (Always visible within the expander)
            use_reasoning_chat = st.checkbox(
                "Enable Phase 1: Basic Step-by-Step Reasoning",
                value=st.session_state.use_reasoning_chat,
                help="When enabled, responses will show basic step-by-step reasoning for general problems"
            )
            st.session_state.use_reasoning_chat = use_reasoning_chat
            
            if use_reasoning_chat:
                st.success("✅ Phase 1 reasoning enabled - responses will show basic step-by-step solutions")
                st.info("💡 Works best with general analytical questions")
            else:
                st.info("💡 Enable Phase 1 reasoning for basic step-by-step solutions")
            
            st.divider()
            
            if st.session_state.backend_health:
                # Get reasoning health
                reasoning_health = get_reasoning_health()
                
                if reasoning_health.get("status") == "healthy":
                    st.success("✅ Reasoning System Available")
                else:
                    st.warning("⚠️ Reasoning System not available")
                    if reasoning_health.get("error"):
                        st.error(f"Error: {reasoning_health['error']}")
            else:
                st.warning("Backend not available for reasoning system")
            
            # Sample Questions
            if use_reasoning_chat:
                st.markdown('<div class="section-header">Sample Questions</div>', unsafe_allow_html=True)
                
                # General analytical questions for Phase 1
                phase1_sample_questions = [
                    "Explain how photosynthesis works step by step",
                    "What are the steps to make a sandwich?",
                    "How does a computer process information?",
                    "Explain the water cycle in detail",
                    "What is the process of making coffee?",
                    "How do plants grow from seeds?"
                ]
                
                for i, question in enumerate(phase1_sample_questions):
                    if st.button(f"📝 {question[:40]}...", key=f"phase1_general_{i}_{st.session_state.chat_input_key}"):
                        st.session_state.sample_question = question
                        st.session_state.temp_phase_override = "phase1"
                        print(f"🔍 DEBUG: Phase 1 button clicked, set temp_phase_override to: {st.session_state.temp_phase_override}")
                        st.session_state.chat_input_key += 1
                        st.rerun()
                
                st.divider()
                st.info("💡 Phase 1 reasoning provides basic step-by-step solutions for general analytical questions.")
        
        # Phase 2 Reasoning Engines Section (Collapsible)
        with st.expander("🚀 Phase 2: Advanced Reasoning Engines", expanded=False):
            st.markdown('<div class="section-header">Engine Selection</div>', unsafe_allow_html=True)
            
            # Phase 2 Reasoning Toggle
            use_phase2_reasoning = st.checkbox(
                "Enable Phase 2 Reasoning Engines",
                value=st.session_state.use_phase2_reasoning,
                help="When enabled, uses specialized reasoning engines for mathematical, logical, and causal problems"
            )
            st.session_state.use_phase2_reasoning = use_phase2_reasoning
            
            if use_phase2_reasoning:
                st.success("✅ Phase 2 engines enabled - specialized reasoning for complex problems")
                
                # Engine Selection
                selected_engine = st.selectbox(
                    "Select Reasoning Engine",
                    options=[
                        ("auto", "🔄 Auto-detect (Recommended)"),
                        ("mathematical", "🔢 Mathematical Engine"),
                        ("logical", "🧮 Logical Engine"),
                        ("causal", "🔗 Causal Engine")
                    ],
                    format_func=lambda x: x[1],
                    index=0,
                    key="phase2_engine_select"
                )
                st.session_state.selected_phase2_engine = selected_engine[0]
                
                st.info(f"💡 Selected: {selected_engine[1]}")
                
                # Engine Status
                if st.session_state.backend_health:
                    st.markdown('<div class="section-header">Engine Status</div>', unsafe_allow_html=True)
                    
                    # Get Phase 2 engine status
                    phase2_status = get_phase2_engine_status()
                    
                    if phase2_status.get("status") == "available":
                        engines = phase2_status.get("engines", {})
                        
                        # Mathematical Engine Status
                        math_status = engines.get("mathematical", {})
                        if math_status.get("status") == "available":
                            st.success("✅ Mathematical Engine: Available")
                            if math_status.get("features"):
                                st.caption(f"Features: {', '.join(math_status['features'])}")
                        else:
                            st.warning("⚠️ Mathematical Engine: Limited")
                            if math_status.get("error"):
                                st.caption(f"Error: {math_status['error']}")
                        
                        # Logical Engine Status
                        logic_status = engines.get("logical", {})
                        if logic_status.get("status") == "available":
                            st.success("✅ Logical Engine: Available")
                            if logic_status.get("features"):
                                st.caption(f"Features: {', '.join(logic_status['features'])}")
                        else:
                            st.warning("⚠️ Logical Engine: Limited")
                            if logic_status.get("error"):
                                st.caption(f"Error: {logic_status['error']}")
                        
                        # Causal Engine Status
                        causal_status = engines.get("causal", {})
                        if causal_status.get("status") == "available":
                            st.success("✅ Causal Engine: Available")
                            if causal_status.get("features"):
                                st.caption(f"Features: {', '.join(causal_status['features'])}")
                        else:
                            st.warning("⚠️ Causal Engine: Limited")
                            if causal_status.get("error"):
                                st.caption(f"Error: {causal_status['error']}")
                        
                        # Refresh button
                        if st.button("🔄 Refresh Engine Status", key="refresh_phase2_status"):
                            st.session_state.phase2_engine_status = get_phase2_engine_status()
                            st.rerun()
                    else:
                        st.warning("⚠️ Phase 2 engines not available")
                        if phase2_status.get("error"):
                            st.error(f"Error: {phase2_status['error']}")
                else:
                    st.warning("Backend not available for Phase 2 engines")
                
                # Sample Questions
                st.markdown('<div class="section-header">Sample Questions</div>', unsafe_allow_html=True)
                
                # Mathematical Sample Questions
                st.markdown("**🔢 Mathematical Problems:**")
                for i, question in enumerate(st.session_state.phase2_sample_questions["mathematical"]):
                    if st.button(f"📝 {question[:40]}...", key=f"phase2_math_{i}_{st.session_state.chat_input_key}"):
                        st.session_state.sample_question = question
                        st.session_state.temp_phase_override = "phase2"
                        print(f"🔍 DEBUG: Phase 2 math button clicked, set temp_phase_override to: {st.session_state.temp_phase_override}")
                        st.session_state.chat_input_key += 1
                        st.rerun()
                
                # Logical Sample Questions
                st.markdown("**🧮 Logical Problems:**")
                for i, question in enumerate(st.session_state.phase2_sample_questions["logical"]):
                    if st.button(f"📝 {question[:40]}...", key=f"phase2_logic_{i}_{st.session_state.chat_input_key}"):
                        st.session_state.sample_question = question
                        st.session_state.temp_phase_override = "phase2"
                        st.session_state.chat_input_key += 1
                        st.rerun()
                
                # Causal Sample Questions
                st.markdown("**🔗 Causal Problems:**")
                for i, question in enumerate(st.session_state.phase2_sample_questions["causal"]):
                    if st.button(f"📝 {question[:40]}...", key=f"phase2_causal_{i}_{st.session_state.chat_input_key}"):
                        st.session_state.sample_question = question
                        st.session_state.temp_phase_override = "phase2"
                        st.session_state.chat_input_key += 1
                        st.rerun()
                
                st.divider()
                st.info("💡 Phase 2 engines provide specialized reasoning for complex mathematical, logical, and causal problems with step-by-step solutions.")
            else:
                st.info("💡 Enable Phase 2 engines for specialized reasoning capabilities")
        
        # Phase 3 Advanced Reasoning Strategies Section (Collapsible)
        with st.expander("🧠 Phase 3: Advanced Reasoning Strategies", expanded=False):
            st.markdown('<div class="section-header">Strategy Selection</div>', unsafe_allow_html=True)
            
            # Phase 3 Reasoning Toggle
            use_phase3_reasoning = st.checkbox(
                "Enable Phase 3 Advanced Reasoning Strategies",
                value=st.session_state.use_phase3_reasoning,
                help="When enabled, uses advanced reasoning strategies for complex problem solving"
            )
            st.session_state.use_phase3_reasoning = use_phase3_reasoning
            
            if use_phase3_reasoning:
                st.success("✅ Phase 3 strategies enabled - advanced reasoning for complex problems")
                
                # Strategy Selection
                selected_strategy = st.selectbox(
                    "Select Reasoning Strategy",
                    options=[
                        ("auto", "🔄 Auto-detect (Recommended)"),
                        ("chain_of_thought", "🔗 Chain-of-Thought"),
                        ("tree_of_thoughts", "🌳 Tree-of-Thoughts"),
                        ("prompt_engineering", "📝 Prompt Engineering")
                    ],
                    format_func=lambda x: x[1],
                    index=0,
                    key="phase3_strategy_select"
                )
                st.session_state.selected_phase3_strategy = selected_strategy[0]
                
                st.info(f"💡 Selected: {selected_strategy[1]}")
                
                # Strategy Status
                if st.session_state.backend_health:
                    st.markdown('<div class="section-header">Strategy Status</div>', unsafe_allow_html=True)
                    
                    # Get Phase 3 strategy status
                    phase3_status = get_phase3_health()
                    
                    if phase3_status.get("status") == "available":
                        strategies = phase3_status.get("strategies", {})
                        
                        # Chain-of-Thought Strategy Status
                        cot_status = strategies.get("chain_of_thought", {})
                        if cot_status.get("status") == "available":
                            st.success("✅ Chain-of-Thought: Available")
                            if cot_status.get("features"):
                                st.caption(f"Features: {', '.join(cot_status['features'])}")
                        else:
                            st.warning("⚠️ Chain-of-Thought: Limited")
                            if cot_status.get("error"):
                                st.caption(f"Error: {cot_status['error']}")
                        
                        # Tree-of-Thoughts Strategy Status
                        tot_status = strategies.get("tree_of_thoughts", {})
                        if tot_status.get("status") == "available":
                            st.success("✅ Tree-of-Thoughts: Available")
                            if tot_status.get("features"):
                                st.caption(f"Features: {', '.join(tot_status['features'])}")
                        else:
                            st.warning("⚠️ Tree-of-Thoughts: Limited")
                            if tot_status.get("error"):
                                st.caption(f"Error: {tot_status['error']}")
                        
                        # Prompt Engineering Strategy Status
                        pe_status = strategies.get("prompt_engineering", {})
                        if pe_status.get("status") == "available":
                            st.success("✅ Prompt Engineering: Available")
                            if pe_status.get("features"):
                                st.caption(f"Features: {', '.join(pe_status['features'])}")
                        else:
                            st.warning("⚠️ Prompt Engineering: Limited")
                            if pe_status.get("error"):
                                st.caption(f"Error: {pe_status['error']}")
                        
                        # Refresh button
                        if st.button("🔄 Refresh Strategy Status", key="refresh_phase3_status"):
                            st.session_state.phase3_health = get_phase3_health()
                            st.rerun()
                    else:
                        st.warning("⚠️ Phase 3 strategies not available")
                        if phase3_status.get("error"):
                            st.error(f"Error: {phase3_status['error']}")
                else:
                    st.warning("Backend not available for Phase 3 strategies")
                
                # Sample Questions
                st.markdown('<div class="section-header">Sample Questions</div>', unsafe_allow_html=True)
                
                # Chain-of-Thought Sample Questions
                st.markdown("**🔗 Chain-of-Thought Problems:**")
                for i, question in enumerate(st.session_state.phase3_sample_questions["chain_of_thought"]):
                    if st.button(f"📝 {question[:40]}...", key=f"phase3_cot_{i}_{st.session_state.chat_input_key}"):
                        st.session_state.sample_question = question
                        st.session_state.temp_phase_override = "phase3"
                        st.session_state.chat_input_key += 1
                        st.rerun()
                
                # Tree-of-Thoughts Sample Questions
                st.markdown("**🌳 Tree-of-Thoughts Problems:**")
                for i, question in enumerate(st.session_state.phase3_sample_questions["tree_of_thoughts"]):
                    if st.button(f"📝 {question[:40]}...", key=f"phase3_tot_{i}_{st.session_state.chat_input_key}"):
                        st.session_state.sample_question = question
                        st.session_state.temp_phase_override = "phase3"
                        st.session_state.chat_input_key += 1
                        st.rerun()
                
                # Prompt Engineering Sample Questions
                st.markdown("**📝 Prompt Engineering Problems:**")
                for i, question in enumerate(st.session_state.phase3_sample_questions["prompt_engineering"]):
                    if st.button(f"📝 {question[:40]}...", key=f"phase3_pe_{i}_{st.session_state.chat_input_key}"):
                        st.session_state.sample_question = question
                        st.session_state.temp_phase_override = "phase3"
                        st.session_state.chat_input_key += 1
                        st.rerun()
                
                st.divider()
                st.info("💡 Phase 3 strategies provide advanced reasoning capabilities including Chain-of-Thought, Tree-of-Thoughts, and Prompt Engineering for complex problem solving.")
            else:
                st.info("💡 Enable Phase 3 strategies for advanced reasoning capabilities")
        
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
                            
                            if result.get("success"):
                                data = result.get("data", {})
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
                                st.error(f"❌ {result.get('error', 'Unknown error')}")
                
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
            
            # Advanced RAG Section
            st.markdown('<div class="section-header">🚀 Advanced RAG</div>', unsafe_allow_html=True)
            
            # Get advanced RAG health and strategies
            if st.session_state.backend_health:
                advanced_rag_health = get_advanced_rag_health()
                advanced_rag_strategies = get_advanced_rag_strategies()
                
                if advanced_rag_health.get("status") == "healthy":
                    st.success("✅ Advanced RAG Available")
                    
                    use_advanced_rag = st.checkbox(
                        "Enable Advanced RAG",
                        value=st.session_state.use_advanced_rag,
                        help="Use multiple retrieval strategies for better results"
                    )
                    st.session_state.use_advanced_rag = use_advanced_rag
                    
                    if use_advanced_rag:
                        st.info("🚀 Advanced RAG enabled - using multiple retrieval strategies")
                        
                        # Show available strategies
                        if advanced_rag_strategies:
                            st.markdown('<div class="section-header">Available Strategies</div>', unsafe_allow_html=True)
                            for strategy_name, strategy_info in advanced_rag_strategies.items():
                                st.markdown(f"""
                                <div class="strategy-badge">{strategy_name.upper()}</div>
                                <small>{strategy_info.get('description', 'No description')}</small>
                                """, unsafe_allow_html=True)
                        
                        # Show components status
                        components = advanced_rag_health.get("components", {})
                        if components:
                            st.markdown('<div class="section-header">Components</div>', unsafe_allow_html=True)
                            for component, status in components.items():
                                if status:
                                    st.success(f"✅ {component}")
                                else:
                                    st.error(f"❌ {component}")
                    else:
                        st.info("💡 Enable Advanced RAG for multi-strategy retrieval")
                else:
                    st.warning("⚠️ Advanced RAG not available")
                    if advanced_rag_health.get("error"):
                        st.error(f"Error: {advanced_rag_health['error']}")
            else:
                st.warning("Backend not available for Advanced RAG")
        
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
    
    # Chat input and stop button row
    col1, col2 = st.columns([4, 1])
    
    with col1:
        prompt = st.chat_input("Ask me anything...", key=f"chat_input_{st.session_state.chat_input_key}")
    
    with col2:
        # Stop button - always show but enable/disable based on state
        if st.button("🛑 Stop", key="stop_button", disabled=not st.session_state.is_generating, help="Stop the current generation" if st.session_state.is_generating else "No generation in progress"):
            print(f"🔍 DEBUG: Stop button clicked! Setting stop_generation = True")
            st.session_state.stop_generation = True
            st.session_state.is_generating = False
            st.rerun()
    
    # Handle sample question if selected (moved here to be part of the main chat flow)
    if st.session_state.sample_question:
        prompt = st.session_state.sample_question
        st.session_state.sample_question = None  # Clear the sample question
        st.session_state.chat_input_key += 1  # Force chat input refresh
    
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
        
        # Check backend health before sending
        if not st.session_state.backend_health:
            error_msg = f"❌ Backend service is not available. Please make sure the backend server is running on {BACKEND_URL}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.error(error_msg)
        else:
            # Check for temporary phase override from sample question buttons
            temp_override = st.session_state.get("temp_phase_override")
            
            # Debug: Print the override status
            if temp_override:
                print(f"🔍 DEBUG: Using temp_phase_override: {temp_override}")
                print(f"🔍 DEBUG: Current settings - Phase3: {st.session_state.use_phase3_reasoning}, Phase2: {st.session_state.use_phase2_reasoning}, Phase1: {st.session_state.use_reasoning_chat}")
            
            # Send message to backend (with Phase 3, Phase 2 reasoning, reasoning, RAG, or regular chat)
            if temp_override == "phase3":
                # Force Phase 3 for sample question
                print(f"🔍 DEBUG: FORCING Phase 3 reasoning for sample question")
                if st.session_state.use_streaming:
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
                if st.session_state.use_streaming:
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
                if st.session_state.use_streaming:
                    # Use streaming reasoning response
                    with st.spinner("🧠 Thinking step by step..."):
                        response_data = send_streaming_reasoning_chat(prompt, st.session_state.conversation_id)
                else:
                    # Use regular reasoning response
                    with st.spinner("🧠 Thinking step by step..."):
                        response_data = send_reasoning_chat(prompt, st.session_state.conversation_id, use_streaming=False)
            elif st.session_state.use_phase3_reasoning:
                # Use Phase 3 advanced reasoning strategies for complex problem solving
                if st.session_state.use_streaming:
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
                if st.session_state.use_streaming:
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
                if st.session_state.use_streaming:
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
                    # Use basic RAG
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
                if st.session_state.use_reasoning_chat:
                    # Use reasoning chat
                    if st.session_state.use_streaming:
                        # Use streaming reasoning response
                        response_data = send_streaming_reasoning_chat(prompt, st.session_state.conversation_id)
                    else:
                        # Use regular non-streaming reasoning response
                        with st.spinner("Thinking with reasoning..."):
                            response_data = send_reasoning_chat(prompt, st.session_state.conversation_id, use_streaming=False)
                else:
                    # Use regular chat
                    if st.session_state.use_streaming:
                        # Use streaming response
                        response_data = send_to_backend(prompt, st.session_state.conversation_id, use_streaming=True)
                    else:
                        # Use regular non-streaming response
                        with st.spinner("Thinking..."):
                            response_data = send_to_backend(prompt, st.session_state.conversation_id, use_streaming=False)
            
            # Handle streaming responses differently since they're already displayed
            if temp_override == "phase1" and st.session_state.use_streaming:
                # For streaming Phase 1 reasoning, handle the generator response
                print(f"🔍 DEBUG: Handling Phase 1 streaming response")
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
                    
                    # Clear temporary phase override after processing
                    if "temp_phase_override" in st.session_state:
                        print(f"🔍 DEBUG: Clearing temp_phase_override: {st.session_state.temp_phase_override}")
                        del st.session_state.temp_phase_override
                    
                    # Reset generating state
                    st.session_state.is_generating = False
            elif temp_override == "phase2" and st.session_state.use_streaming:
                # For streaming Phase 2 reasoning, handle the generator response
                print(f"🔍 DEBUG: Handling Phase 2 streaming response")
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
                                
                                # Update the final message with Phase 2 info
                                final_response = chunk.get("response", full_response)
                                message_placeholder.markdown(final_response)
                                
                                # Add to chat history with Phase 2 metadata
                                message_data = {
                                    "role": "assistant", 
                                    "content": final_response,
                                    "phase2_engine": True,
                                    "engine_used": chunk.get("engine_used", "unknown"),
                                    "reasoning_type": chunk.get("reasoning_type", "unknown"),
                                    "confidence": chunk.get("confidence", 0.0),
                                    "steps_count": chunk.get("steps_count"),
                                    "validation_summary": chunk.get("validation_summary")
                                }
                                st.session_state.messages.append(message_data)
                                break
                    
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
            elif temp_override == "phase3" and st.session_state.use_streaming:
                # For streaming Phase 3 reasoning, handle the generator response
                print(f"🔍 DEBUG: Handling Phase 3 streaming response")
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
                                
                                # Update the final message with Phase 3 info
                                final_response = chunk.get("response", full_response)
                                message_placeholder.markdown(final_response)
                                
                                # Add to chat history with Phase 3 metadata
                                message_data = {
                                    "role": "assistant", 
                                    "content": final_response,
                                    "phase3_strategy": True,
                                    "strategy_used": chunk.get("strategy_used", "unknown"),
                                    "reasoning_type": chunk.get("reasoning_type", "unknown"),
                                    "confidence": chunk.get("confidence", 0.0),
                                    "steps_count": chunk.get("steps_count"),
                                    "validation_summary": chunk.get("validation_summary")
                                }
                                st.session_state.messages.append(message_data)
                                break
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Clear temporary phase override after processing
                    if "temp_phase_override" in st.session_state:
                        print(f"🔍 DEBUG: Clearing temp_phase_override: {st.session_state.temp_phase_override}")
                        del st.session_state.temp_phase_override
                    
                    # Reset generating state
                    st.session_state.is_generating = False
            elif st.session_state.use_phase2_reasoning and st.session_state.use_streaming:
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
            elif st.session_state.use_rag and st.session_state.use_streaming and st.session_state.rag_stats.get("total_documents", 0) > 0:
                # For streaming RAG, the response is already displayed in real-time
                if response_data and not response_data.get("response", "").startswith("❌"):
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
            elif st.session_state.use_reasoning_chat and st.session_state.use_streaming:
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
                    
                    # Reset generating state
                    st.session_state.is_generating = False
            else:
                # Handle regular responses (non-streaming or non-RAG)
                if response_data and not response_data["response"].startswith("❌"):
                    # Update conversation ID if provided
                    if response_data.get("conversation_id"):
                        st.session_state.conversation_id = response_data["conversation_id"]
                    
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
                    
                    st.session_state.messages.append(message_data)
                    
                    # Refresh conversation list to include the new conversation
                    st.session_state.conversations = get_conversations()
                    
                    # Display assistant response (if not already displayed via streaming)
                    if not st.session_state.use_streaming:
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