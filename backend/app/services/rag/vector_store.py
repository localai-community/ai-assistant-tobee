import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import chromadb
from chromadb.config import Settings
from langchain.schema import Document as LangChainDocument
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np

logger = logging.getLogger(__name__)

class VectorStore:
    """Manages vector database operations for RAG system"""
    
    def __init__(self, persist_directory: str = "storage/vector_db", collection_name: str = "documents", conversation_id: str = None):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.base_collection_name = collection_name
        self.conversation_id = conversation_id
        
        # Create conversation-specific collection name
        if conversation_id:
            self.collection_name = f"{collection_name}_conv_{conversation_id}"
        else:
            self.collection_name = collection_name
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize LangChain vector store with conversation-specific collection
        self.vector_store = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_directory)
        )
        
        logger.info(f"Vector store initialized at {self.persist_directory} with collection: {self.collection_name}")
    
    def add_documents(self, documents: List[LangChainDocument]) -> bool:
        """Add documents to the vector store"""
        try:
            if not documents:
                logger.warning("No documents to add")
                return False
            
            # Add documents to vector store
            self.vector_store.add_documents(documents)
            
            # Persist changes
            self.vector_store.persist()
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            return False
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 4, 
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[LangChainDocument, float]]:
        """Search for similar documents"""
        try:
            results = self.vector_store.similarity_search_with_score(
                query, 
                k=k,
                filter=filter_dict
            )
            
            logger.info(f"Found {len(results)} similar documents for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    def similarity_search_by_metadata(
        self, 
        query: str, 
        metadata_filter: Dict[str, Any], 
        k: int = 4
    ) -> List[Tuple[LangChainDocument, float]]:
        """Search for similar documents with metadata filtering"""
        try:
            # Convert metadata filter to ChromaDB format
            chroma_filter = self._convert_metadata_filter(metadata_filter)
            
            results = self.vector_store.similarity_search_with_score(
                query, 
                k=k,
                filter=chroma_filter
            )
            
            logger.info(f"Found {len(results)} similar documents with metadata filter")
            return results
            
        except Exception as e:
            logger.error(f"Error in metadata-filtered search: {str(e)}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection"""
        try:
            collection = self.client.get_collection(self.collection_name)
            count = collection.count()
            
            # Calculate actual storage size
            storage_size_mb = self._calculate_storage_size()
            
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "persist_directory": str(self.persist_directory),
                "storage_size_mb": storage_size_mb
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {"error": str(e)}
    

    def _calculate_storage_size(self) -> float:
        """Calculate the actual storage size of the vector database"""
        try:
            import os
            total_size = 0
            
            # Walk through the persist directory
            for dirpath, dirnames, filenames in os.walk(self.persist_directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            
            # Convert to MB
            return round(total_size / (1024 * 1024), 2)
            
        except Exception as e:
            logger.error(f"Error calculating storage size: {str(e)}")
            return 0.0
    def delete_documents_by_metadata(self, metadata_filter: Dict[str, Any]) -> bool:
        """Delete documents based on metadata filter"""
        try:
            # Convert metadata filter to ChromaDB format
            chroma_filter = self._convert_metadata_filter(metadata_filter)
            
            # Get documents matching the filter
            results = self.vector_store.similarity_search_with_score(
                "",  # Empty query to get all documents
                k=10000,  # Large number to get all documents
                filter=chroma_filter
            )
            
            if not results:
                logger.info("No documents found matching the filter")
                return True
            
            # Extract document IDs (this is a simplified approach)
            # In a production system, you'd want to store document IDs properly
            logger.warning("Document deletion by metadata is not fully implemented")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            return False
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection(self.collection_name)
            self.client.create_collection(self.collection_name)
            
            # Reinitialize vector store
            self.vector_store = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_directory)
            )
            
            logger.info("Collection cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False
    
    def _convert_metadata_filter(self, metadata_filter: Dict[str, Any]) -> Dict[str, Any]:
        """Convert metadata filter to ChromaDB format"""
        chroma_filter = {}
        
        for key, value in metadata_filter.items():
            if isinstance(value, (str, int, float, bool)):
                chroma_filter[key] = {"$eq": value}
            elif isinstance(value, list):
                chroma_filter[key] = {"$in": value}
            else:
                logger.warning(f"Unsupported filter type for key {key}: {type(value)}")
        
        return chroma_filter
    
    def get_document_by_id(self, doc_id: str) -> Optional[LangChainDocument]:
        """Get a specific document by ID"""
        try:
            # This is a simplified implementation
            # In a production system, you'd want to store document IDs properly
            logger.warning("Document retrieval by ID is not fully implemented")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document by ID: {str(e)}")
            return None
    
    def update_document(self, doc_id: str, new_content: str, new_metadata: Dict[str, Any]) -> bool:
        """Update a document in the vector store"""
        try:
            # This is a simplified implementation
            # In a production system, you'd want to properly update documents
            logger.warning("Document update is not fully implemented")
            return False
            
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the vector store"""
        try:
            stats = self.get_collection_stats()
            embeddings_working = self._test_embeddings()
            
            return {
                "status": "healthy" if embeddings_working and "error" not in stats else "unhealthy",
                "collection_stats": stats,
                "embeddings_working": embeddings_working,
                "persist_directory_exists": self.persist_directory.exists()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _test_embeddings(self) -> bool:
        """Test if embeddings are working"""
        try:
            test_text = "This is a test"
            embedding = self.embeddings.embed_query(test_text)
            return len(embedding) > 0
        except Exception as e:
            logger.error(f"Embeddings test failed: {str(e)}")
            return False 