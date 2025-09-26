"""
Document Manager Service
Comprehensive document lifecycle management for chat-scoped documents.
"""

import logging
import os
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.orm import Session

from ..models.database import ChatDocument, DocumentChunk
from ..services.repository import ChatDocumentRepository, DocumentChunkRepository

logger = logging.getLogger(__name__)

class DocumentManager:
    """Service for managing document lifecycle and sessions."""
    
    def __init__(self, db: Session, upload_dir: str = "storage/uploads"):
        self.db = db
        self.upload_dir = Path(upload_dir)
        self.document_repo = ChatDocumentRepository(db)
        self.chunk_repo = DocumentChunkRepository(db)
        
        # Ensure upload directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def create_document_session(
        self, 
        conversation_id: str, 
        user_id: str
    ) -> str:
        """Create a new document session for conversation."""
        try:
            session_id = f"session_{conversation_id}_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Created document session: {session_id}")
            return session_id
        except Exception as e:
            logger.error(f"Error creating document session: {e}")
            raise
    
    def cleanup_conversation_documents(self, conversation_id: str) -> Dict[str, Any]:
        """Clean up all documents for a conversation."""
        try:
            # Get all documents for the conversation
            documents = self.document_repo.get_conversation_documents(conversation_id)
            
            cleanup_stats = {
                "documents_deleted": 0,
                "chunks_deleted": 0,
                "files_deleted": 0,
                "total_size_freed": 0,
                "errors": []
            }
            
            for document in documents:
                try:
                    # Delete document chunks
                    chunks_deleted = self.chunk_repo.delete_document_chunks(document.id)
                    cleanup_stats["chunks_deleted"] += chunks_deleted
                    
                    # Delete physical file
                    file_path = Path(document.file_path)
                    if file_path.exists():
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        cleanup_stats["files_deleted"] += 1
                        cleanup_stats["total_size_freed"] += file_size
                    
                    # Delete document record
                    if self.document_repo.delete_document(document.id):
                        cleanup_stats["documents_deleted"] += 1
                    
                except Exception as e:
                    error_msg = f"Error cleaning up document {document.id}: {e}"
                    logger.error(error_msg)
                    cleanup_stats["errors"].append(error_msg)
            
            logger.info(f"Cleaned up conversation {conversation_id}: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Error cleaning up conversation documents: {e}")
            raise
    
    def get_document_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get document usage analytics for user."""
        try:
            # Get user documents
            documents = self.document_repo.get_user_documents(user_id, limit=1000)
            
            analytics = {
                "total_documents": len(documents),
                "total_size": sum(doc.file_size for doc in documents),
                "file_types": {},
                "conversations": set(),
                "upload_timeline": [],
                "processing_status": {},
                "recent_activity": []
            }
            
            for doc in documents:
                # File type distribution
                file_type = doc.file_type
                analytics["file_types"][file_type] = analytics["file_types"].get(file_type, 0) + 1
                
                # Conversation distribution
                analytics["conversations"].add(doc.conversation_id)
                
                # Upload timeline
                analytics["upload_timeline"].append({
                    "date": doc.upload_timestamp.isoformat(),
                    "filename": doc.filename,
                    "size": doc.file_size
                })
                
                # Processing status
                status = doc.processing_status
                analytics["processing_status"][status] = analytics["processing_status"].get(status, 0) + 1
                
                # Recent activity (last 30 days)
                if doc.updated_at > datetime.now() - timedelta(days=30):
                    analytics["recent_activity"].append({
                        "filename": doc.filename,
                        "action": "updated" if doc.updated_at > doc.upload_timestamp else "uploaded",
                        "timestamp": doc.updated_at.isoformat()
                    })
            
            # Convert sets to lists for JSON serialization
            analytics["conversations"] = list(analytics["conversations"])
            
            # Sort timeline by date
            analytics["upload_timeline"].sort(key=lambda x: x["date"], reverse=True)
            analytics["recent_activity"].sort(key=lambda x: x["timestamp"], reverse=True)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting document analytics: {e}")
            return {"error": str(e)}
    
    def archive_document(self, document_id: str) -> bool:
        """Archive document for long-term storage."""
        try:
            document = self.document_repo.get_document(document_id)
            if not document:
                return False
            
            # Update document status to archived
            self.document_repo.update_document(document_id, {
                "processing_status": "archived"
            })
            
            logger.info(f"Archived document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error archiving document: {e}")
            return False
    
    def restore_document(self, document_id: str) -> bool:
        """Restore archived document."""
        try:
            document = self.document_repo.get_document(document_id)
            if not document:
                return False
            
            # Update document status to processed
            self.document_repo.update_document(document_id, {
                "processing_status": "processed"
            })
            
            logger.info(f"Restored document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring document: {e}")
            return False
    
    def get_document_health(self) -> Dict[str, Any]:
        """Get document system health status."""
        try:
            # Get all documents
            all_documents = self.document_repo.get_user_documents("all", limit=10000)
            
            health_stats = {
                "total_documents": len(all_documents),
                "total_size": sum(doc.file_size for doc in all_documents),
                "processing_status": {},
                "file_types": {},
                "orphaned_files": 0,
                "missing_files": 0,
                "health_score": 100
            }
            
            for doc in all_documents:
                # Processing status distribution
                status = doc.processing_status
                health_stats["processing_status"][status] = health_stats["processing_status"].get(status, 0) + 1
                
                # File type distribution
                file_type = doc.file_type
                health_stats["file_types"][file_type] = health_stats["file_types"].get(file_type, 0) + 1
                
                # Check if physical file exists
                file_path = Path(doc.file_path)
                if not file_path.exists():
                    health_stats["missing_files"] += 1
                    health_stats["health_score"] -= 5  # Deduct points for missing files
            
            # Check for orphaned files (files without database records)
            try:
                for file_path in self.upload_dir.rglob("*"):
                    if file_path.is_file():
                        # Check if this file has a corresponding database record
                        has_record = any(
                            Path(doc.file_path) == file_path 
                            for doc in all_documents
                        )
                        if not has_record:
                            health_stats["orphaned_files"] += 1
                            health_stats["health_score"] -= 2  # Deduct points for orphaned files
            except Exception as e:
                logger.warning(f"Error checking for orphaned files: {e}")
            
            # Ensure health score doesn't go below 0
            health_stats["health_score"] = max(0, health_stats["health_score"])
            
            return health_stats
            
        except Exception as e:
            logger.error(f"Error getting document health: {e}")
            return {"error": str(e), "health_score": 0}
    
    def cleanup_old_documents(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up documents older than specified days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Get old documents
            all_documents = self.document_repo.get_user_documents("all", limit=10000)
            old_documents = [
                doc for doc in all_documents 
                if doc.upload_timestamp < cutoff_date
            ]
            
            cleanup_stats = {
                "documents_processed": len(old_documents),
                "documents_archived": 0,
                "documents_deleted": 0,
                "total_size_freed": 0,
                "errors": []
            }
            
            for doc in old_documents:
                try:
                    # Archive instead of delete for safety
                    if self.archive_document(doc.id):
                        cleanup_stats["documents_archived"] += 1
                        cleanup_stats["total_size_freed"] += doc.file_size
                    
                except Exception as e:
                    error_msg = f"Error processing old document {doc.id}: {e}"
                    logger.error(error_msg)
                    cleanup_stats["errors"].append(error_msg)
            
            logger.info(f"Cleaned up {len(old_documents)} old documents: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Error cleaning up old documents: {e}")
            return {"error": str(e)}
    
    def get_document_retention_policy(self) -> Dict[str, Any]:
        """Get current document retention policy."""
        return {
            "default_retention_days": 30,
            "archive_after_days": 30,
            "delete_after_days": 90,
            "max_documents_per_user": 100,
            "max_total_size_mb": 1000,
            "auto_cleanup_enabled": True
        }
    
    def update_document_retention_policy(self, policy: Dict[str, Any]) -> bool:
        """Update document retention policy."""
        try:
            # In a real implementation, this would be stored in a configuration table
            # For now, we'll just log the policy update
            logger.info(f"Document retention policy updated: {policy}")
            return True
        except Exception as e:
            logger.error(f"Error updating retention policy: {e}")
            return False
