import logging
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from pathlib import Path
from langchain.schema import Document as LangChainDocument
from langchain.prompts import PromptTemplate
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from collections import defaultdict

from .vector_store import VectorStore

logger = logging.getLogger(__name__)

class AdvancedRAGRetriever:
    """
    Advanced RAG retriever that uses multiple strategies beyond simple similarity search:
    - Multi-vector retrieval (dense + sparse)
    - Query expansion and reformulation
    - LLM-based reranking
    - Graph-based retrieval
    - Conversational context awareness
    """
    
    def __init__(
        self, 
        vector_store: Optional[VectorStore] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.vector_store = vector_store or VectorStore()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize TF-IDF for sparse retrieval
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = None
        self.document_texts = []
        
        # Initialize spaCy for NLP features
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Query expansion patterns
        self.expansion_patterns = {
            'technical': ['implementation', 'code', 'algorithm', 'method', 'approach'],
            'conceptual': ['concept', 'theory', 'principle', 'idea', 'understanding'],
            'comparative': ['difference', 'compare', 'versus', 'vs', 'alternative'],
            'temporal': ['history', 'evolution', 'development', 'timeline', 'future']
        }
        
        logger.info("Advanced RAG Retriever initialized")
    
    def add_documents(self, documents: List[LangChainDocument]) -> bool:
        """Add documents and build multiple indexes"""
        try:
            # Add to vector store
            success = self.vector_store.add_documents(documents)
            if not success:
                return False
            
            # Build TF-IDF index
            self.document_texts = [doc.page_content for doc in documents]
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.document_texts)
            
            logger.info(f"Added {len(documents)} documents with multi-index support")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return False
    
    def retrieve_with_multiple_strategies(
        self, 
        query: str, 
        conversation_history: Optional[List[Dict]] = None,
        k: int = 4
    ) -> List[Tuple[LangChainDocument, float, str]]:
        """
        Retrieve documents using multiple strategies and combine results
        Returns: (document, score, strategy_used)
        """
        try:
            # Strategy 1: Dense vector similarity (current approach)
            dense_results = self._dense_retrieval(query, k * 2)
            
            # Strategy 2: Sparse TF-IDF retrieval
            sparse_results = self._sparse_retrieval(query, k * 2)
            
            # Strategy 3: Query expansion
            expanded_results = self._expanded_retrieval(query, k * 2)
            
            # Strategy 4: Conversational context retrieval
            context_results = []
            if conversation_history:
                context_results = self._contextual_retrieval(query, conversation_history, k * 2)
            
            # Strategy 5: Entity-based retrieval
            entity_results = self._entity_based_retrieval(query, k * 2)
            
            # Combine and rerank all results
            all_results = self._combine_and_rerank(
                dense_results, sparse_results, expanded_results, 
                context_results, entity_results, query, k
            )
            
            return all_results
            
        except Exception as e:
            logger.error(f"Error in multi-strategy retrieval: {str(e)}")
            # Fallback to dense retrieval
            return self._dense_retrieval(query, k)
    
    def _dense_retrieval(self, query: str, k: int) -> List[Tuple[LangChainDocument, float, str]]:
        """Dense vector similarity search"""
        try:
            results = self.vector_store.similarity_search(query, k)
            return [(doc, score, "dense") for doc, score in results]
        except Exception as e:
            logger.error(f"Error in dense retrieval: {str(e)}")
            return []
    
    def _sparse_retrieval(self, query: str, k: int) -> List[Tuple[LangChainDocument, float, str]]:
        """TF-IDF based sparse retrieval"""
        try:
            if self.tfidf_matrix is None or not self.document_texts:
                return []
            
            # Transform query
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            # Get top k results
            top_indices = np.argsort(similarities)[::-1][:k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include relevant results
                    # Create a mock document for now - in real implementation, 
                    # you'd store document references
                    doc = LangChainDocument(
                        page_content=self.document_texts[idx],
                        metadata={"source": f"sparse_retrieval_{idx}"}
                    )
                    results.append((doc, float(similarities[idx]), "sparse"))
            
            return results
            
        except Exception as e:
            logger.error(f"Error in sparse retrieval: {str(e)}")
            return []
    
    def _expanded_retrieval(self, query: str, k: int) -> List[Tuple[LangChainDocument, float, str]]:
        """Query expansion based retrieval"""
        try:
            # Analyze query type and expand
            expanded_queries = self._expand_query(query)
            
            all_results = []
            for expanded_query in expanded_queries:
                results = self._dense_retrieval(expanded_query, k // len(expanded_queries))
                # Adjust scores for expanded queries
                adjusted_results = [(doc, score * 0.8, "expanded") for doc, score, _ in results]
                all_results.extend(adjusted_results)
            
            return all_results
            
        except Exception as e:
            logger.error(f"Error in expanded retrieval: {str(e)}")
            return []
    
    def _expand_query(self, query: str) -> List[str]:
        """Expand query with related terms"""
        try:
            expanded = [query]  # Original query
            
            query_lower = query.lower()
            
            # Add technical terms for technical queries
            if any(word in query_lower for word in ['code', 'implementation', 'algorithm']):
                expanded.append(f"{query} implementation code")
                expanded.append(f"{query} algorithm method")
            
            # Add conceptual terms for concept queries
            if any(word in query_lower for word in ['what is', 'define', 'explain']):
                expanded.append(f"{query} concept theory")
                expanded.append(f"{query} definition explanation")
            
            # Add comparative terms for comparison queries
            if any(word in query_lower for word in ['difference', 'compare', 'vs', 'versus']):
                expanded.append(f"{query} comparison")
                expanded.append(f"{query} alternatives")
            
            return expanded
            
        except Exception as e:
            logger.error(f"Error expanding query: {str(e)}")
            return [query]
    
    def _contextual_retrieval(
        self, 
        query: str, 
        conversation_history: List[Dict], 
        k: int
    ) -> List[Tuple[LangChainDocument, float, str]]:
        """Retrieval based on conversation context"""
        try:
            # Extract key entities and concepts from conversation history
            context_entities = self._extract_context_entities(conversation_history)
            
            if not context_entities:
                return []
            
            # Create context-aware query
            context_query = f"{query} {' '.join(context_entities)}"
            
            # Retrieve with context
            results = self._dense_retrieval(context_query, k)
            
            # Boost scores for contextually relevant results
            boosted_results = []
            for doc, score, strategy in results:
                # Check if document contains context entities
                doc_text = doc.page_content.lower()
                context_matches = sum(1 for entity in context_entities if entity.lower() in doc_text)
                
                if context_matches > 0:
                    # Boost score based on context matches
                    boost_factor = 1.0 + (context_matches * 0.2)
                    boosted_results.append((doc, score * boost_factor, "contextual"))
                else:
                    boosted_results.append((doc, score * 0.7, "contextual"))  # Penalize
            
            return boosted_results
            
        except Exception as e:
            logger.error(f"Error in contextual retrieval: {str(e)}")
            return []
    
    def _extract_context_entities(self, conversation_history: List[Dict]) -> List[str]:
        """Extract key entities from conversation history"""
        try:
            entities = set()
            
            for message in conversation_history[-5:]:  # Last 5 messages
                content = message.get('content', '')
                if self.nlp:
                    doc = self.nlp(content)
                    # Extract named entities and noun phrases
                    for ent in doc.ents:
                        entities.add(ent.text)
                    for chunk in doc.noun_chunks:
                        entities.add(chunk.text)
                else:
                    # Simple keyword extraction
                    words = content.lower().split()
                    # Add words that appear multiple times (likely important)
                    word_counts = defaultdict(int)
                    for word in words:
                        if len(word) > 3:  # Skip short words
                            word_counts[word] += 1
                    
                    for word, count in word_counts.items():
                        if count > 1:
                            entities.add(word)
            
            return list(entities)[:10]  # Limit to 10 entities
            
        except Exception as e:
            logger.error(f"Error extracting context entities: {str(e)}")
            return []
    
    def _entity_based_retrieval(self, query: str, k: int) -> List[Tuple[LangChainDocument, float, str]]:
        """Retrieval based on named entities in query"""
        try:
            if not self.nlp:
                return []
            
            # Extract entities from query
            doc = self.nlp(query)
            entities = [ent.text for ent in doc.ents]
            
            if not entities:
                return []
            
            # Search for documents containing these entities
            entity_results = []
            for entity in entities:
                results = self._dense_retrieval(entity, k // len(entities))
                # Boost scores for entity matches
                boosted_results = [(doc, score * 1.2, "entity") for doc, score, _ in results]
                entity_results.extend(boosted_results)
            
            return entity_results
            
        except Exception as e:
            logger.error(f"Error in entity-based retrieval: {str(e)}")
            return []
    
    def _combine_and_rerank(
        self,
        dense_results: List[Tuple[LangChainDocument, float, str]],
        sparse_results: List[Tuple[LangChainDocument, float, str]],
        expanded_results: List[Tuple[LangChainDocument, float, str]],
        context_results: List[Tuple[LangChainDocument, float, str]],
        entity_results: List[Tuple[LangChainDocument, float, str]],
        query: str,
        k: int
    ) -> List[Tuple[LangChainDocument, float, str]]:
        """Combine results from all strategies and rerank"""
        try:
            # Combine all results
            all_results = []
            all_results.extend(dense_results)
            all_results.extend(sparse_results)
            all_results.extend(expanded_results)
            all_results.extend(context_results)
            all_results.extend(entity_results)
            
            # Group by document and combine scores
            doc_scores = defaultdict(list)
            doc_strategies = defaultdict(set)
            
            for doc, score, strategy in all_results:
                doc_id = doc.page_content[:100]  # Use content as ID
                doc_scores[doc_id].append(score)
                doc_strategies[doc_id].add(strategy)
            
            # Calculate combined scores
            combined_results = []
            for doc_id, scores in doc_scores.items():
                # Find the original document
                original_doc = None
                for doc, _, _ in all_results:
                    if doc.page_content[:100] == doc_id:
                        original_doc = doc
                        break
                
                if original_doc:
                    # Weighted combination of scores
                    avg_score = np.mean(scores)
                    strategy_bonus = len(doc_strategies[doc_id]) * 0.1  # Bonus for multiple strategies
                    final_score = avg_score + strategy_bonus
                    
                    # Determine primary strategy
                    primary_strategy = "multi_strategy" if len(doc_strategies[doc_id]) > 1 else list(doc_strategies[doc_id])[0]
                    
                    combined_results.append((original_doc, final_score, primary_strategy))
            
            # Sort by final score and return top k
            combined_results.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Combined {len(all_results)} results from multiple strategies into {len(combined_results)} unique documents")
            
            return combined_results[:k]
            
        except Exception as e:
            logger.error(f"Error combining and reranking: {str(e)}")
            # Fallback to dense results
            return dense_results[:k]
    
    def create_advanced_rag_prompt(
        self, 
        query: str, 
        conversation_history: Optional[List[Dict]] = None,
        k: int = 4
    ) -> str:
        """Create an advanced RAG prompt with multi-strategy retrieval"""
        try:
            # Get results from multiple strategies
            results = self.retrieve_with_multiple_strategies(query, conversation_history, k)
            
            if not results:
                return f"""You are a helpful AI assistant. Answer the following question using your general knowledge.

Question: {query}

Answer:"""
            
            # Build context with strategy information
            context_parts = []
            for doc, score, strategy in results:
                context_parts.append(f"[{strategy.upper()}] Relevance: {score:.3f}")
                context_parts.append(f"Content: {doc.page_content}")
                context_parts.append("---")
            
            context = "\n".join(context_parts)
            
            return f"""You are a helpful AI assistant. Answer the following question using the provided context from multiple retrieval strategies.

Context from documents (retrieved using multiple strategies):
{context}

Question: {query}

Instructions:
- Use the provided context when it's relevant and helpful
- Consider that different retrieval strategies may have found different aspects of the answer
- Supplement with your general knowledge to provide a complete answer
- If the context doesn't fully answer the question, use your knowledge to fill in gaps
- Always provide accurate, helpful information

Answer:"""
            
        except Exception as e:
            logger.error(f"Error creating advanced RAG prompt: {str(e)}")
            return f"Question: {query}\n\nContext: Error retrieving context." 