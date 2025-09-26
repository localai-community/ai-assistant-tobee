"""
Document Summary Service
AI-powered document summarization using Ollama LLM.
"""

import logging
import httpx
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from ..services.repository import ChatDocumentRepository
from ..models.schemas import ChatDocumentUpdate

logger = logging.getLogger(__name__)

class DocumentSummaryService:
    """Service for generating document summaries using AI."""
    
    def __init__(self, ollama_url: str, db: Session):
        self.ollama_url = ollama_url
        self.db = db
        self.document_repo = ChatDocumentRepository(db)
        self.summary_cache = {}
        
    async def generate_summary(
        self, 
        document_id: str,
        summary_type: str = "brief",
        conversation_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate document summary using Ollama LLM.
        
        Args:
            document_id: ID of the document to summarize
            summary_type: Type of summary (brief, detailed, key_points, executive)
            conversation_context: Optional conversation context for better summarization
            
        Returns:
            Dict containing summary results
        """
        try:
            # Get document from database
            document = self.document_repo.get_document(document_id)
            if not document:
                return {"success": False, "error": "Document not found"}
            
            # Check if summary already exists
            if document.summary_text and document.summary_type == summary_type:
                return {
                    "success": True,
                    "summary": document.summary_text,
                    "summary_type": summary_type,
                    "cached": True
                }
            
            # Read document content
            document_text = await self._read_document_content(document.file_path)
            if not document_text:
                return {"success": False, "error": "Could not read document content"}
            
            # Generate summary
            summary = await self._generate_ai_summary(
                document_text, 
                summary_type, 
                conversation_context,
                document.filename
            )
            
            if summary:
                # Update document with summary
                self.document_repo.update_document(document_id, {
                    "summary_text": summary,
                    "summary_type": summary_type,
                    "processing_status": "summarized"
                })
                
                return {
                    "success": True,
                    "summary": summary,
                    "summary_type": summary_type,
                    "cached": False
                }
            else:
                return {"success": False, "error": "Failed to generate summary"}
                
        except Exception as e:
            logger.error(f"Error generating summary for document {document_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_multi_level_summary(self, document_id: str) -> Dict[str, Any]:
        """
        Generate multiple types of summaries for a document.
        
        Args:
            document_id: ID of the document to summarize
            
        Returns:
            Dict containing all summary types
        """
        try:
            summaries = {}
            summary_types = ["brief", "detailed", "key_points"]
            
            for summary_type in summary_types:
                result = await self.generate_summary(document_id, summary_type)
                if result["success"]:
                    summaries[summary_type] = result["summary"]
                else:
                    summaries[summary_type] = f"Error: {result['error']}"
            
            return {
                "success": True,
                "summaries": summaries,
                "document_id": document_id
            }
            
        except Exception as e:
            logger.error(f"Error generating multi-level summary for document {document_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _read_document_content(self, file_path: str) -> Optional[str]:
        """Read content from document file."""
        try:
            from pathlib import Path
            from ..services.rag.document_processor import DocumentProcessor
            
            processor = DocumentProcessor()
            documents = processor.process_file(file_path)
            
            if documents:
                # Combine all chunks into single text
                content = "\n\n".join([doc.page_content for doc in documents])
                return content
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error reading document content from {file_path}: {e}")
            return None
    
    async def _generate_ai_summary(
        self, 
        text: str, 
        summary_type: str,
        conversation_context: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """Generate AI summary using Ollama."""
        try:
            # Create summary prompt
            prompt = self._create_summary_prompt(text, summary_type, conversation_context, filename)
            
            # Call Ollama API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": "llama3:latest",
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,  # Lower temperature for more focused summaries
                            "top_p": 0.9,
                            "max_tokens": 1000
                        }
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling Ollama API for summary: {e}")
            return None
    
    def _create_summary_prompt(
        self, 
        text: str, 
        summary_type: str,
        conversation_context: Optional[str] = None,
        filename: Optional[str] = None
    ) -> str:
        """Create optimized prompts for different summary types."""
        
        # Truncate text if too long (keep first 8000 characters for context)
        if len(text) > 8000:
            text = text[:8000] + "\n\n[Document truncated for summary generation]"
        
        base_prompt = f"""You are an expert document summarizer. Please create a {summary_type} summary of the following document."""
        
        if filename:
            base_prompt += f"\n\nDocument: {filename}"
        
        if conversation_context:
            base_prompt += f"\n\nConversation Context: {conversation_context}"
        
        base_prompt += f"\n\nDocument Content:\n{text}\n\n"
        
        if summary_type == "brief":
            return base_prompt + """Please provide a brief 2-3 sentence summary that captures the main topic and key points of this document."""
        
        elif summary_type == "detailed":
            return base_prompt + """Please provide a detailed summary that covers:
1. Main topic and purpose
2. Key points and arguments
3. Important details and examples
4. Conclusions or recommendations

Keep the summary comprehensive but concise (3-5 paragraphs)."""
        
        elif summary_type == "key_points":
            return base_prompt + """Please provide a bulleted list of the key points from this document. Focus on the most important information that someone would need to know."""
        
        elif summary_type == "executive":
            return base_prompt + """Please provide an executive summary suitable for decision-makers. Focus on:
1. What this document is about
2. Main findings or recommendations
3. Key implications or next steps

Keep it high-level and actionable (2-3 paragraphs)."""
        
        else:
            return base_prompt + f"Please provide a {summary_type} summary of this document."
    
    async def get_document_summary(self, document_id: str) -> Dict[str, Any]:
        """Get existing summary for a document."""
        try:
            document = self.document_repo.get_document(document_id)
            if not document:
                return {"success": False, "error": "Document not found"}
            
            if document.summary_text:
                return {
                    "success": True,
                    "summary": document.summary_text,
                    "summary_type": document.summary_type,
                    "created_at": document.updated_at
                }
            else:
                return {"success": False, "error": "No summary available"}
                
        except Exception as e:
            logger.error(f"Error getting document summary: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_document_summary(
        self, 
        document_id: str, 
        summary_text: str, 
        summary_type: str = "custom"
    ) -> Dict[str, Any]:
        """Update document with custom summary."""
        try:
            self.document_repo.update_document(document_id, {
                "summary_text": summary_text,
                "summary_type": summary_type,
                "processing_status": "summarized"
            })
            
            return {
                "success": True,
                "message": "Summary updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating document summary: {e}")
            return {"success": False, "error": str(e)}
