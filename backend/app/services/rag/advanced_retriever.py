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
        chunk_overlap: int = 200,
        max_history_messages: int = 20,  # Performance optimization
        max_entities: int = 30  # Performance optimization
    ):
        self.vector_store = vector_store or VectorStore()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_history_messages = max_history_messages
        self.max_entities = max_entities
        
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
            if conversation_history and len(conversation_history) > 0:
                # Check if this is a context-dependent query
                is_context_dependent = self._is_context_dependent_query(query, conversation_history)
                if is_context_dependent:
                    context_results = self._contextual_retrieval(query, conversation_history, k * 2)
                    logger.info(f"Using contextual retrieval for query: '{query}'")
                else:
                    logger.info(f"Skipping contextual retrieval for general knowledge query: '{query}'")
            
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
        """Retrieval based on conversation context with smart context detection"""
        try:
            # Check if this is a context-dependent question
            is_context_dependent = self._is_context_dependent_query(query, conversation_history)
            
            if not is_context_dependent:
                logger.info(f"Query '{query}' appears to be general knowledge, skipping contextual retrieval")
                return []
            
            # Extract key entities and concepts from conversation history
            context_entities = self._extract_context_entities(conversation_history)
            
            # Debug logging
            logger.info(f"Context entities extracted: {context_entities}")
            
            if not context_entities:
                return []
            
            # Create context-aware query with better formatting
            context_query = f"{query} context: {' '.join(context_entities)}"
            
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
        """Extract key entities from conversation history with performance optimization"""
        try:
            # Performance optimization: Limit processing for very long conversations
            if len(conversation_history) > self.max_history_messages:
                conversation_history = conversation_history[-self.max_history_messages:]
                logger.info(f"Performance optimization: Processing only last {self.max_history_messages} messages for entity extraction")
            
            entities = set()
            recent_entities = set()  # Entities from recent messages (higher priority)
            
            # Process messages with recency bias
            total_messages = len(conversation_history)
            for i, message in enumerate(conversation_history):
                content = message.get('content', '')
                is_recent = i >= total_messages - 5  # Last 5 messages are "recent"
                
                # Skip very short messages to improve performance
                if len(content) < 10:
                    continue
                
                if self.nlp:
                    doc = self.nlp(content)
                    # Extract named entities and noun phrases
                    for ent in doc.ents:
                        if is_recent:
                            recent_entities.add(ent.text)
                        else:
                            entities.add(ent.text)
                    for chunk in doc.noun_chunks:
                        if is_recent:
                            recent_entities.add(chunk.text)
                        else:
                            entities.add(chunk.text)
                else:
                    # Simple keyword extraction
                    words = content.lower().split()
                    # Add words that appear multiple times (likely important)
                    word_counts = defaultdict(int)
                    for word in words:
                        if len(word) > 3 and word not in ['this', 'that', 'with', 'from', 'they', 'have', 'been', 'will', 'would', 'could', 'should']:  # Skip short words and common words
                            word_counts[word] += 1
                    
                    for word, count in word_counts.items():
                        if count > 1:
                            if is_recent:
                                recent_entities.add(word)
                            else:
                                entities.add(word)
                    
                    # Also add important technical terms
                    technical_terms = ['attention', 'transformer', 'neural', 'network', 'model', 'architecture', 'mechanism', 'layer', 'embedding', 'token', 'sequence', 'context', 'query', 'key', 'value']
                    for term in technical_terms:
                        if term in content.lower():
                            if is_recent:
                                recent_entities.add(term)
                            else:
                                entities.add(term)
            
            # Combine entities with recent ones having priority
            all_entities = list(recent_entities) + list(entities - recent_entities)
            
            # Performance optimization: Limit total entities
            return all_entities[:self.max_entities]
            
        except Exception as e:
            logger.error(f"Error extracting context entities: {str(e)}")
            return []
    
    def _is_context_dependent_query(self, query: str, conversation_history: List[Dict]) -> bool:
        """Determine if a query is context-dependent using LLM reasoning."""
        try:
            # If no conversation history, definitely not context-dependent
            if not conversation_history or len(conversation_history) < 2:
                return False
            
            # Create a summary of the conversation context
            context_summary = self._create_conversation_summary(conversation_history)
            
            # Use LLM to determine if the query needs context
            context_detection_prompt = f"""You are an AI assistant that determines whether a user's question requires conversation context to answer properly.

CONVERSATION CONTEXT:
{context_summary}

CURRENT QUESTION: "{query}"

TASK: Determine if this question is context-dependent or general knowledge.

A question is CONTEXT-DEPENDENT if:
- It uses pronouns like "it", "this", "that", "they", "them"
- It refers to something mentioned in the conversation
- It's a follow-up question that builds on previous answers
- It asks for clarification or elaboration about previous topics
- It compares or contrasts with previously discussed concepts

A question is GENERAL KNOWLEDGE if:
- It asks for basic facts, definitions, or information
- It's a standalone question that doesn't reference the conversation
- It's about geography, history, science, or other general topics
- It doesn't use pronouns or references to previous discussion

RESPONSE FORMAT: Answer with exactly "CONTEXT" or "GENERAL" followed by a brief explanation.

Example:
Question: "What is the capital of France?"
Answer: "GENERAL - This is a basic geography question that doesn't reference the conversation."

Question: "How does it work?"
Answer: "CONTEXT - Uses pronoun 'it' and likely refers to something discussed previously."

Your analysis:"""

            # Try LLM-based detection first, fallback to heuristic
            try:
                return self._llm_context_detection(query, context_summary)
            except Exception as e:
                logger.warning(f"LLM context detection failed, using heuristic: {e}")
                return self._llm_context_detection_heuristic(query, conversation_history)
            
        except Exception as e:
            logger.error(f"Error in LLM context detection: {str(e)}")
            return False  # Default to general knowledge on error
    
    def _create_conversation_summary(self, conversation_history: List[Dict]) -> str:
        """Create a summary of the conversation for context analysis."""
        try:
            # Take last 5 messages for summary
            recent_messages = conversation_history[-5:]
            
            summary_parts = []
            for i, msg in enumerate(recent_messages):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:200]  # Limit length
                summary_parts.append(f"{role.upper()}: {content}")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error creating conversation summary: {str(e)}")
            return "Error creating summary"
    
    def _llm_context_detection(self, query: str, context_summary: str) -> bool:
        """Use LLM to determine if a query is context-dependent."""
        try:
            # Import here to avoid circular imports
            import os
            import httpx
            
            # Get Ollama URL from environment
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            
            # Create the prompt for context detection
            prompt = f"""You are an AI assistant that determines whether a user's question requires conversation context to answer properly.

CONVERSATION CONTEXT:
{context_summary}

CURRENT QUESTION: "{query}"

TASK: Determine if this question is context-dependent or general knowledge.

A question is CONTEXT-DEPENDENT if:
- It uses pronouns like "it", "this", "that", "they", "them"
- It refers to something mentioned in the conversation
- It's a follow-up question that builds on previous answers
- It asks for clarification or elaboration about previous topics
- It compares or contrasts with previously discussed concepts

A question is GENERAL KNOWLEDGE if:
- It asks for basic facts, definitions, or information
- It's a standalone question that doesn't reference the conversation
- It's about geography, history, science, or other general topics
- It doesn't use pronouns or references to previous discussion

IMPORTANT: Start your response with either "CONTEXT" or "GENERAL" followed by your explanation.

Examples:
Question: "What is the capital of France?"
Answer: "GENERAL - This is a basic geography question that doesn't reference the conversation."

Question: "How does it work?"
Answer: "CONTEXT - Uses pronoun 'it' and likely refers to something discussed previously."

Your analysis:"""

            # Call Ollama for context detection
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f"{ollama_url}/api/generate",
                    json={
                        "model": "llama3:latest",
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,  # Low temperature for consistent classification
                            "top_p": 0.9
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    llm_response = result.get("response", "").strip()
                    
                    # Parse the response - be more flexible with format
                    llm_response_lower = llm_response.lower()
                    
                    # Look for context indicators in the response
                    context_indicators = ["context", "context-dependent", "context dependent"]
                    general_indicators = ["general", "general knowledge", "standalone"]
                    
                    # Check if response contains context indicators
                    if any(indicator in llm_response_lower for indicator in context_indicators):
                        logger.info(f"LLM determined '{query}' is context-dependent: {llm_response[:100]}...")
                        return True
                    elif any(indicator in llm_response_lower for indicator in general_indicators):
                        logger.info(f"LLM determined '{query}' is general knowledge: {llm_response[:100]}...")
                        return False
                    else:
                        logger.warning(f"Unclear LLM response format: {llm_response[:100]}...")
                        # Fallback to heuristic
                        raise Exception("Unclear response format")
                else:
                    logger.error(f"Ollama API error: {response.status_code}")
                    raise Exception(f"API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error in LLM context detection: {str(e)}")
            raise  # Re-raise to trigger fallback to heuristic
    
    def _llm_context_detection_heuristic(self, query: str, conversation_history: List[Dict]) -> bool:
        """Heuristic-based context detection (fallback when LLM is not available)."""
        try:
            query_lower = query.lower().strip()
            
            # Quick checks for obvious context-dependent patterns
            context_indicators = [
                # Pronouns
                r"\b(it|this|that|these|those)\b",
                r"\b(he|she|they|them)\b",
                r"\b(his|her|their)\b",
                
                # Follow-up patterns
                r"what about",
                r"how about", 
                r"what else",
                r"can you explain",
                r"tell me more",
                r"go on",
                
                # References
                r"the first part",
                r"the second part",
                r"the previous",
                r"the next",
                
                # Very short questions (likely context-dependent)
                r"^what is it\?$",
                r"^how does it work\?$",
                r"^what about that\?$"
            ]
            
            # Check for context indicators
            for pattern in context_indicators:
                if re.search(pattern, query_lower):
                    return True
            
            # Check if query is very short (likely context-dependent)
            if len(query.split()) <= 3:
                return True
            
            # Check if query contains words from recent conversation
            recent_content = " ".join([
                msg.get('content', '').lower() 
                for msg in conversation_history[-3:]
            ])
            
            query_words = set(query_lower.split())
            context_words = set(recent_content.split())
            
            # If query shares significant words with recent context, it's likely context-dependent
            if len(query_words.intersection(context_words)) >= 2:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in heuristic context detection: {str(e)}")
            return False
    
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
            
            # Check if this is a general knowledge question
            is_context_dependent = self._is_context_dependent_query(query, conversation_history or [])
            
            if not is_context_dependent:
                # For general knowledge questions, use a simpler prompt
                return f"""You are a helpful AI assistant. Answer the following question using your general knowledge.

Question: {query}

Instructions:
- This appears to be a general knowledge question
- Use your knowledge to provide a complete and accurate answer
- If relevant documents were found, you may reference them, but don't limit yourself to them
- Provide a comprehensive answer based on your training

Answer:"""
            else:
                # For context-dependent questions, use the full RAG prompt
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