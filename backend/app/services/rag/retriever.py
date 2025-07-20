import logging
import re
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
        
        # Default prompt template for RAG - encourages use of both context and general knowledge
        self.default_prompt_template = """You are a helpful AI assistant. Use the following context from retrieved documents to enhance your answer, but also draw from your general knowledge to provide a comprehensive response.

Context from documents:
{context}

Question: {question}

Instructions:
- Use the provided context when it's relevant and helpful
- Supplement with your general knowledge to provide a complete answer
- If the context doesn't fully answer the question, use your knowledge to fill in gaps
- Always provide accurate, helpful information
- If you're unsure about something, acknowledge the uncertainty

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
        filter_dict: Optional[Dict[str, Any]] = None,
        relevance_threshold: Optional[float] = None
    ) -> List[Tuple[LangChainDocument, float]]:
        """Retrieve relevant documents for a query with intelligent relevance filtering"""
        try:
            # Get more results than needed for analysis
            search_k = max(k * 3, 10)  # Get more results for better analysis
            
            if filter_dict:
                results = self.vector_store.similarity_search_by_metadata(
                    query, filter_dict, k=search_k
                )
            else:
                results = self.vector_store.similarity_search(query, k=search_k)
            
            if not results:
                return []
            
            # Extract scores for analysis
            scores = [score for _, score in results]
            
            # Calculate dynamic threshold based on score distribution
            if relevance_threshold is None:
                relevance_threshold = self._calculate_dynamic_threshold(scores, query)
            
            # Filter by relevance threshold
            filtered_results = [
                (doc, score) for doc, score in results 
                if score >= relevance_threshold
            ]
            
            # Limit to k results
            filtered_results = filtered_results[:k]
            
            logger.info(f"Retrieved {len(filtered_results)} relevant documents for query (dynamic threshold: {relevance_threshold:.3f})")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def _calculate_dynamic_threshold(self, scores: List[float], query: str) -> float:
        """Calculate a dynamic relevance threshold based on score distribution and query characteristics"""
        try:
            if not scores:
                return 0.0
            
            # Basic statistics
            mean_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            score_range = max_score - min_score
            
            # Calculate standard deviation for score distribution
            variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
            std_dev = variance ** 0.5
            
            # Analyze query characteristics
            query_words = query.lower().split()
            query_length = len(query_words)
            
            # Adjust threshold based on query characteristics
            base_threshold = mean_score
            
            # For short queries (1-2 words), be more lenient
            if query_length <= 2:
                base_threshold = mean_score - (0.5 * std_dev)
            # For medium queries (3-5 words), use mean
            elif query_length <= 5:
                base_threshold = mean_score
            # For long queries (6+ words), be more strict
            else:
                base_threshold = mean_score + (0.3 * std_dev)
            
            # Ensure threshold is reasonable
            min_threshold = max_score * 0.3  # At least 30% of max score
            max_threshold = max_score * 0.9  # At most 90% of max score
            
            final_threshold = max(min_threshold, min(base_threshold, max_threshold))
            
            logger.debug(f"Dynamic threshold calculation: mean={mean_score:.3f}, std={std_dev:.3f}, "
                        f"query_length={query_length}, final_threshold={final_threshold:.3f}")
            
            return final_threshold
            
        except Exception as e:
            logger.error(f"Error calculating dynamic threshold: {str(e)}")
            # Fallback to a reasonable default
            return max(scores) * 0.5 if scores else 0.0
    
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
            
            # Format context from retrieved documents (very concise version)
            context_parts = []
            for i, (doc, score) in enumerate(results[:2]):  # Limit to top 2 documents
                # Get document filename from metadata
                filename = doc.metadata.get("filename", "Unknown Document")
                # Truncate content to keep it very manageable
                content = doc.page_content
                if len(content) > 100:  # Limit to 100 characters per document
                    content = content[:97] + "..."
                
                context_parts.append(f"Document {i+1}: {filename} - {content}")
            
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
    
    def create_intelligent_rag_prompt(
        self, 
        query: str, 
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create an intelligent RAG prompt that adapts based on available context"""
        try:
            # Check if this is likely a general knowledge question
            if self._is_general_knowledge_query(query):
                return f"""You are a helpful AI assistant. Answer the following question using your general knowledge and expertise.

Question: {query}

Instructions:
- Provide a comprehensive answer using your general knowledge
- If you're unsure about specific details, acknowledge the uncertainty
- Always be helpful and informative

Answer:"""
            
            # Get relevant documents first
            relevant_docs = self.retrieve_relevant_documents(query, k, filter_dict)
            
            if not relevant_docs:
                # No relevant documents found - use general knowledge prompt
                return f"""You are a helpful AI assistant. Answer the following question using your general knowledge and expertise.

Question: {query}

Instructions:
- Provide a comprehensive answer using your general knowledge
- If you're unsure about specific details, acknowledge the uncertainty
- Always be helpful and informative

Answer:"""
            
            # Relevant documents found - create context-enhanced prompt
            context = self.get_context_for_query(query, k, filter_dict)
            
            return f"""You are a helpful AI assistant. Answer the following question using both the provided context and your general knowledge.

Context: {context}

Question: {query}

Please provide a comprehensive answer:"""
            
        except Exception as e:
            logger.error(f"Error creating intelligent RAG prompt: {str(e)}")
            return f"Question: {query}\n\nContext: Error retrieving context."
    
    def _is_general_knowledge_query(self, query: str) -> bool:
        """Determine if a query is likely a general knowledge question that shouldn't rely heavily on documents"""
        try:
            query_lower = query.lower().strip()
            
            # Common general knowledge question patterns
            general_patterns = [
                # Weather and current events
                r'\bweather\b', r'\btemperature\b', r'\bforecast\b',
                r'\btoday\b', r'\bnow\b', r'\bcurrent\b',
                
                # Time and date
                r'\btime\b', r'\bdate\b', r'\bday\b', r'\bmonth\b', r'\byear\b',
                
                # Location and geography
                r'\bcapital\b', r'\bcountry\b', r'\bcity\b', r'\bwhere\b',
                r'\blocation\b', r'\bplace\b',
                
                # Personal and subjective
                r'\bhow are you\b', r'\bhow do you feel\b', r'\bwhat do you think\b',
                r'\bopinion\b', r'\bpreference\b',
                
            ]
            
            # Check for general knowledge patterns
            for pattern in general_patterns:
                if re.search(pattern, query_lower):
                    return True
            
            # Check for very short queries (likely general knowledge)
            if len(query_lower.split()) <= 2:
                return True
            
            # Check for question words that often indicate general knowledge
            question_words = ['what', 'where', 'when', 'who', 'why', 'how']
            if any(query_lower.startswith(word) for word in question_words):
                # But exclude technical/specific questions
                technical_terms = ['code', 'function', 'api', 'database', 'server', 
                                 'algorithm', 'model', 'neural', 'network', 'tensor',
                                 'framework', 'library', 'package', 'module', 'rnn',
                                 'cnn', 'lstm', 'transformer', 'bert', 'gpt', 'ml',
                                 'ai', 'nlp', 'cv', 'rl', 'gan', 'vae', 'svm', 'knn']
                if not any(term in query_lower for term in technical_terms):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking general knowledge query: {str(e)}")
            return False
    
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