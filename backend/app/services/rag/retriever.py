import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from langchain.schema import Document as LangChainDocument
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from .document_processor import DocumentProcessor
from .vector_store import VectorStore

logger = logging.getLogger(__name__)

class RAGRetriever:
    """Main RAG system that coordinates document processing and retrieval"""
    
    def __init__(
        self, 
        vector_store: Optional[VectorStore] = None,
        document_processor: Optional[DocumentProcessor] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.vector_store = vector_store or VectorStore()
        self.document_processor = document_processor or DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Default prompt template for RAG
        self.default_prompt_template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}

Answer:"""
        
        self.prompt = PromptTemplate(
            template=self.default_prompt_template,
            input_variables=["context", "question"]
        )
        
        logger.info("RAG Retriever initialized")
    
    def add_document(self, file_path: str) -> Dict[str, Any]:
        """Add a single document to the RAG system"""
        try:
            # Process the document
            documents = self.document_processor.process_file(file_path)
            
            if not documents:
                return {
                    "success": False,
                    "error": "No content extracted from document",
                    "file_path": file_path
                }
            
            # Add to vector store
            success = self.vector_store.add_documents(documents)
            
            if success:
                stats = self.document_processor.get_processing_stats(documents)
                return {
                    "success": True,
                    "file_path": file_path,
                    "chunks_created": len(documents),
                    "stats": stats
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to add documents to vector store",
                    "file_path": file_path
                }
                
        except Exception as e:
            logger.error(f"Error adding document {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def add_documents_from_directory(self, directory_path: str) -> Dict[str, Any]:
        """Add all supported documents from a directory"""
        try:
            # Process all documents in directory
            documents = self.document_processor.process_directory(directory_path)
            
            if not documents:
                return {
                    "success": False,
                    "error": "No documents found or processed",
                    "directory_path": directory_path
                }
            
            # Add to vector store
            success = self.vector_store.add_documents(documents)
            
            if success:
                stats = self.document_processor.get_processing_stats(documents)
                return {
                    "success": True,
                    "directory_path": directory_path,
                    "total_chunks": len(documents),
                    "stats": stats
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to add documents to vector store",
                    "directory_path": directory_path
                }
                
        except Exception as e:
            logger.error(f"Error adding documents from directory {directory_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "directory_path": directory_path
            }
    
    def retrieve_relevant_documents(
        self, 
        query: str, 
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[LangChainDocument, float]]:
        """Retrieve relevant documents for a query"""
        try:
            if filter_dict:
                results = self.vector_store.similarity_search_by_metadata(
                    query, filter_dict, k=k
                )
            else:
                results = self.vector_store.similarity_search(query, k=k)
            
            logger.info(f"Retrieved {len(results)} relevant documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def get_context_for_query(
        self, 
        query: str, 
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get formatted context string for a query"""
        try:
            results = self.retrieve_relevant_documents(query, k, filter_dict)
            
            if not results:
                return "No relevant documents found."
            
            # Format context from retrieved documents
            context_parts = []
            for doc, score in results:
                context_parts.append(f"Document: {doc.metadata.get('filename', 'Unknown')}")
                context_parts.append(f"Relevance Score: {score:.3f}")
                context_parts.append(f"Content: {doc.page_content}")
                context_parts.append("---")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error getting context: {str(e)}")
            return "Error retrieving context."
    
    def create_rag_prompt(
        self, 
        query: str, 
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None,
        custom_prompt_template: Optional[str] = None
    ) -> str:
        """Create a RAG prompt with context"""
        try:
            context = self.get_context_for_query(query, k, filter_dict)
            
            if custom_prompt_template:
                prompt = PromptTemplate(
                    template=custom_prompt_template,
                    input_variables=["context", "question"]
                )
            else:
                prompt = self.prompt
            
            return prompt.format(context=context, question=query)
            
        except Exception as e:
            logger.error(f"Error creating RAG prompt: {str(e)}")
            return f"Question: {query}\n\nContext: Error retrieving context."
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the RAG system"""
        try:
            vector_stats = self.vector_store.get_collection_stats()
            vector_health = self.vector_store.health_check()
            
            return {
                "vector_store": {
                    "stats": vector_stats,
                    "health": vector_health
                },
                "document_processor": {
                    "chunk_size": self.document_processor.chunk_size,
                    "chunk_overlap": self.document_processor.chunk_overlap
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
            return {"error": str(e)}
    
    def clear_all_documents(self) -> bool:
        """Clear all documents from the vector store"""
        try:
            success = self.vector_store.clear_collection()
            if success:
                logger.info("All documents cleared from RAG system")
            return success
            
        except Exception as e:
            logger.error(f"Error clearing documents: {str(e)}")
            return False
    
    def delete_documents_by_metadata(self, metadata_filter: Dict[str, Any]) -> bool:
        """Delete documents based on metadata filter"""
        try:
            success = self.vector_store.delete_documents_by_metadata(metadata_filter)
            if success:
                logger.info(f"Documents deleted with filter: {metadata_filter}")
            return success
            
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            return False
    
    def search_documents(
        self, 
        query: str, 
        k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search documents and return formatted results"""
        try:
            results = self.retrieve_relevant_documents(query, k, filter_dict)
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": score,
                    "filename": doc.metadata.get('filename', 'Unknown'),
                    "source": doc.metadata.get('source', 'Unknown')
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check of the RAG system"""
        try:
            vector_health = self.vector_store.health_check()
            
            # Test document processing
            test_doc = LangChainDocument(
                page_content="This is a test document for health check.",
                metadata={"test": True}
            )
            
            processing_working = True
            try:
                # Test if we can process a simple document
                test_chunks = self.document_processor.text_splitter.split_text(
                    test_doc.page_content
                )
                processing_working = len(test_chunks) > 0
            except Exception as e:
                processing_working = False
                logger.error(f"Document processing health check failed: {e}")
            
            return {
                "status": "healthy" if vector_health.get("status") == "healthy" and processing_working else "unhealthy",
                "vector_store": vector_health,
                "document_processing": {
                    "working": processing_working
                },
                "overall_status": "healthy" if vector_health.get("status") == "healthy" and processing_working else "unhealthy"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            } 