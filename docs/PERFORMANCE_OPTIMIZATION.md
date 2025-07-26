# Advanced RAG Performance Optimization Guide

## Overview

The Advanced RAG system can experience performance degradation with very long conversation histories. This guide explains the optimizations implemented and how to configure them.

## Performance Bottlenecks

### 1. **Entity Extraction Bottleneck**
- **Problem**: Processing all messages for entity extraction
- **Impact**: Linear time complexity with conversation length
- **Solution**: Limit to last 20 messages for entity extraction

### 2. **Context Query Bloat**
- **Problem**: Adding too many entities to queries
- **Impact**: Longer embedding generation and retrieval time
- **Solution**: Limit to 30 most relevant entities

### 3. **Database Retrieval**
- **Problem**: Loading 1000+ messages from database
- **Impact**: Memory usage and network overhead
- **Solution**: Limit to last 50 messages from database

## Current Optimizations

### **Entity Extraction Limits**
```python
# Only process last 20 messages for entity extraction
max_history_messages = 20

# Skip very short messages (< 10 characters)
if len(content) < 10:
    continue

# Limit total entities to 30
max_entities = 30
```

### **Database Retrieval Limits**
```python
# Limit database retrieval to last 50 messages
max_messages = 50
messages = message_repo.get_messages(conversation_id, limit=max_messages)
```

### **Smart Prioritization**
- **Recent messages** (last 5) get priority in entity extraction
- **Technical terms** automatically detected
- **Recency bias** ensures recent context is prioritized

## Performance Configuration

### **Current Settings**
```python
# Advanced RAG Retriever Configuration
max_history_messages = 20  # Messages processed for entities
max_entities = 30          # Maximum entities extracted
max_db_messages = 50       # Messages retrieved from database
```

### **Adjusting Performance Settings**

#### **For Better Performance (Faster, Less Context)**
```python
advanced_rag_retriever = AdvancedRAGRetriever(
    max_history_messages=10,  # Process fewer messages
    max_entities=15,          # Extract fewer entities
)
```

#### **For Better Context (Slower, More Context)**
```python
advanced_rag_retriever = AdvancedRAGRetriever(
    max_history_messages=50,  # Process more messages
    max_entities=50,          # Extract more entities
)
```

## Performance Monitoring

### **Log Messages to Watch**
```
Performance optimization: Processing only last 20 messages for entity extraction
Conversation history retrieval took 0.15s
Advanced RAG retrieval took 1.23s
Conversation 123 has 50+ messages. Performance may be affected.
```

### **Health Check Endpoint**
```bash
curl http://localhost:8000/api/v1/advanced-rag/health
```

Response includes performance configuration:
```json
{
  "performance_config": {
    "max_history_messages": 20,
    "max_entities": 30,
    "max_db_messages": 50
  }
}
```

## Performance vs Context Trade-offs

| **Setting** | **Performance** | **Context Quality** | **Use Case** |
|-------------|-----------------|-------------------|--------------|
| **Conservative** (10/15) | ⚡ Fast | ⚠️ Limited | Real-time chat |
| **Balanced** (20/30) | 🚀 Good | ✅ Good | General use |
| **Aggressive** (50/50) | 🐌 Slow | 🎯 Excellent | Deep analysis |

## Recommendations

### **For Short Conversations (< 20 messages)**
- Use default settings
- Full context available
- Optimal performance

### **For Medium Conversations (20-50 messages)**
- Default settings work well
- Some performance optimization applied
- Good context retention

### **For Long Conversations (50+ messages)**
- Performance optimizations active
- Recent context prioritized
- Consider conversation splitting for very long sessions

### **For Real-time Applications**
- Use conservative settings (10/15)
- Prioritize speed over context
- Consider streaming responses

## Troubleshooting Performance Issues

### **Slow Response Times**
1. Check conversation length in logs
2. Reduce `max_history_messages`
3. Reduce `max_entities`
4. Monitor database query performance

### **Memory Issues**
1. Reduce `max_db_messages`
2. Implement conversation archiving
3. Consider conversation splitting

### **Poor Context Quality**
1. Increase `max_history_messages`
2. Increase `max_entities`
3. Check if spaCy is available for better entity extraction

## Future Optimizations

### **Planned Improvements**
1. **Caching**: Cache entity extraction results
2. **Async Processing**: Parallel entity extraction
3. **Smart Sampling**: Intelligent message selection
4. **Conversation Summarization**: Summarize old messages
5. **Incremental Updates**: Only process new messages

### **Advanced Features**
1. **Conversation Chunking**: Split very long conversations
2. **Context Compression**: Compress old context
3. **Priority Queuing**: Process recent messages first
4. **Adaptive Limits**: Adjust limits based on conversation length

## Best Practices

1. **Monitor Performance**: Watch logs for performance warnings
2. **Adjust Settings**: Tune configuration based on use case
3. **Split Conversations**: Break very long conversations into sessions
4. **Use Streaming**: For real-time applications
5. **Archive Old Conversations**: Move old conversations to archive

## Conclusion

The Advanced RAG system balances performance and context quality through intelligent optimizations. The default settings work well for most use cases, but can be adjusted based on specific requirements.

For optimal performance:
- Use conservative settings for real-time applications
- Monitor conversation length and performance logs
- Consider conversation management strategies for very long sessions
- Leverage streaming responses for better user experience 