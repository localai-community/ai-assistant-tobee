"""
Advanced RAG API Endpoints
API routes for advanced RAG functionality with multiple retrieval strategies.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import os
import logging
from pathlib import Path
import json
import asyncio
from pydantic import BaseModel

from ..services.rag.advanced_retriever import AdvancedRAGRetriever
from ..services.chat import ChatService
from ..core.database import get_db
from ..core.models import ErrorResponse

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/advanced-rag", tags=["advanced-rag"])

# Initialize services
advanced_rag_retriever = AdvancedRAGRetriever()
chat_service = ChatService()

class AdvancedRAGRequest(BaseModel):
    message: str
    model: str = "llama3:latest"
    temperature: float = 0.7
    conversation_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None
    k: int = 4
    use_advanced_strategies: bool = True

class AdvancedRAGStreamRequest(BaseModel):
    message: str
    model: str = "llama3:latest"
    temperature: float = 0.7
    conversation_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None
    k: int = 4
    use_advanced_strategies: bool = True

@router.post("/chat")
async def advanced_rag_chat(request: AdvancedRAGRequest, db: Session = Depends(get_db)):
    """
    Get advanced RAG-enhanced response with multiple retrieval strategies.
    
    Args:
        request: Advanced RAG request with message and parameters
        db: Database session
        
    Returns:
        dict: Advanced RAG response with strategy information
    """
    try:
        if request.use_advanced_strategies:
            # Use advanced multi-strategy retrieval
            results = advanced_rag_retriever.retrieve_with_multiple_strategies(
                request.message, 
                request.conversation_history, 
                request.k
            )
            
            # Create advanced prompt
            enhanced_prompt = advanced_rag_retriever.create_advanced_rag_prompt(
                request.message, 
                request.conversation_history, 
                request.k
            )
            
            # Format results with strategy information
            strategy_results = []
            for doc, score, strategy in results:
                strategy_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": score,
                    "strategy": strategy,
                    "filename": doc.metadata.get('filename', 'Unknown'),
                    "source": doc.metadata.get('source', 'Unknown')
                })
            
            # Generate response using chat service
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            rag_chat_service = ChatService(ollama_url=ollama_url, db=db)
            
            response = await rag_chat_service.generate_response(
                message=enhanced_prompt,
                model=request.model,
                temperature=request.temperature,
                conversation_id=request.conversation_id
            )
            
            return {
                "success": True,
                "response": response.response,
                "conversation_id": response.conversation_id,
                "has_context": len(results) > 0,
                "strategies_used": list(set(result["strategy"] for result in strategy_results)),
                "results_count": len(results),
                "results": strategy_results,
                "enhanced_prompt": enhanced_prompt
            }
        else:
            # Fallback to basic RAG
            from ..services.rag.retriever import RAGRetriever
            basic_rag = RAGRetriever()
            enhanced_prompt = basic_rag.create_intelligent_rag_prompt(request.message, request.k)
            
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            rag_chat_service = ChatService(ollama_url=ollama_url, db=db)
            
            response = await rag_chat_service.generate_response(
                message=enhanced_prompt,
                model=request.model,
                temperature=request.temperature,
                conversation_id=request.conversation_id
            )
            
            return {
                "success": True,
                "response": response.response,
                "conversation_id": response.conversation_id,
                "has_context": True,
                "strategies_used": ["basic"],
                "results_count": 0,
                "results": [],
                "enhanced_prompt": enhanced_prompt
            }
        
    except Exception as e:
        logger.error(f"Advanced RAG chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def advanced_rag_stream_chat(request: AdvancedRAGStreamRequest, db: Session = Depends(get_db)):
    """
    Stream advanced RAG-enhanced chat response.
    
    Args:
        request: Advanced RAG stream request with message and parameters
        db: Database session
        
    Returns:
        StreamingResponse: Server-sent events with advanced RAG-enhanced response
    """
    try:
        if request.use_advanced_strategies:
            # Get advanced RAG context
            results = advanced_rag_retriever.retrieve_with_multiple_strategies(
                request.message, 
                request.conversation_history, 
                request.k
            )
            
            enhanced_prompt = advanced_rag_retriever.create_advanced_rag_prompt(
                request.message, 
                request.conversation_history, 
                request.k
            )
            
            # Get strategy information
            strategies_used = list(set(strategy for _, _, strategy in results))
            has_context = len(results) > 0
            
        else:
            # Fallback to basic RAG
            from ..services.rag.retriever import RAGRetriever
            basic_rag = RAGRetriever()
            enhanced_prompt = basic_rag.create_intelligent_rag_prompt(request.message, request.k)
            strategies_used = ["basic"]
            has_context = True
            results = []
        
        # Stream the response
        async def generate_stream():
            try:
                full_response = ""
                
                # Create chat service instance
                ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
                rag_chat_service = ChatService(ollama_url=ollama_url, db=db)
                
                # Use enhanced prompt for streaming
                simple_prompt = f"Answer this question: {request.message}"
                if has_context:
                    simple_prompt += f"\n\nUse this context: {enhanced_prompt}"
                
                async for chunk in rag_chat_service.generate_streaming_response(
                    message=simple_prompt,
                    model=request.model,
                    temperature=request.temperature,
                    conversation_id=request.conversation_id
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                
                # Send completion signal with advanced RAG context
                yield f"data: {json.dumps({
                    'content': '',
                    'strategies_used': strategies_used,
                    'has_context': has_context,
                    'results_count': len(results)
                })}\n\n"
                
            except Exception as e:
                error_chunk = {"error": str(e), "type": "error"}
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"Advanced RAG stream error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def advanced_search_documents(
    query: str = Form(...),
    conversation_history: Optional[List[Dict[str, Any]]] = Form(None),
    k: int = Form(10),
    use_advanced_strategies: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Search documents using advanced retrieval strategies.
    
    Args:
        query: Search query
        conversation_history: Optional conversation history for context
        k: Number of results to return
        use_advanced_strategies: Whether to use advanced strategies
        db: Database session
        
    Returns:
        dict: Advanced search results with strategy information
    """
    try:
        if use_advanced_strategies:
            results = advanced_rag_retriever.retrieve_with_multiple_strategies(
                query, conversation_history, k
            )
            
            formatted_results = []
            for doc, score, strategy in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": score,
                    "strategy": strategy,
                    "filename": doc.metadata.get('filename', 'Unknown'),
                    "source": doc.metadata.get('source', 'Unknown')
                })
            
            strategies_used = list(set(result["strategy"] for result in formatted_results))
            
        else:
            # Fallback to basic search
            from ..services.rag.retriever import RAGRetriever
            basic_rag = RAGRetriever()
            results = basic_rag.search_documents(query, k)
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    **result,
                    "strategy": "basic"
                })
            
            strategies_used = ["basic"]
        
        return {
            "success": True,
            "query": query,
            "strategies_used": strategies_used,
            "results_count": len(formatted_results),
            "results": formatted_results
        }
        
    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
async def get_available_strategies():
    """
    Get information about available retrieval strategies.
    
    Returns:
        dict: Available strategies and their descriptions
    """
    return {
        "success": True,
        "strategies": {
            "dense": {
                "name": "Dense Vector Similarity",
                "description": "Traditional embedding-based similarity search",
                "strengths": ["Semantic understanding", "Fast retrieval"],
                "weaknesses": ["May miss exact keyword matches", "Threshold sensitivity"]
            },
            "sparse": {
                "name": "Sparse TF-IDF Retrieval", 
                "description": "Keyword-based retrieval using TF-IDF",
                "strengths": ["Exact keyword matching", "Interpretable scores"],
                "weaknesses": ["No semantic understanding", "Vocabulary dependent"]
            },
            "expanded": {
                "name": "Query Expansion",
                "description": "Expands queries with related terms before retrieval",
                "strengths": ["Broader coverage", "Handles synonyms"],
                "weaknesses": ["May introduce noise", "Computational overhead"]
            },
            "contextual": {
                "name": "Conversational Context",
                "description": "Uses conversation history for context-aware retrieval",
                "strengths": ["Handles follow-up questions", "Maintains conversation flow"],
                "weaknesses": ["Requires conversation history", "Context window limits"]
            },
            "entity": {
                "name": "Entity-Based Retrieval",
                "description": "Retrieval based on named entities in queries",
                "strengths": ["Precise entity matching", "Good for specific queries"],
                "weaknesses": ["Requires entity recognition", "May miss conceptual queries"]
            },
            "multi_strategy": {
                "name": "Multi-Strategy Combination",
                "description": "Combines results from multiple strategies with intelligent reranking",
                "strengths": ["Best of all strategies", "Robust retrieval"],
                "weaknesses": ["Computational complexity", "More complex scoring"]
            }
        }
    }

@router.get("/health")
async def advanced_rag_health():
    """
    Health check for advanced RAG system.
    
    Returns:
        dict: System health status
    """
    try:
        # Check if spaCy is available
        spacy_available = False
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            spacy_available = True
        except:
            pass
        
        # Check if scikit-learn is available
        sklearn_available = False
        try:
            import sklearn
            sklearn_available = True
        except:
            pass
        
        return {
            "success": True,
            "status": "healthy",
            "components": {
                "advanced_retriever": True,
                "spacy_nlp": spacy_available,
                "scikit_learn": sklearn_available,
                "vector_store": True
            },
            "recommendations": [
                "Install spaCy model: python -m spacy download en_core_web_sm" if not spacy_available else None,
                "Install scikit-learn: pip install scikit-learn" if not sklearn_available else None
            ]
        }
        
    except Exception as e:
        logger.error(f"Advanced RAG health check error: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        } 