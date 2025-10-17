'use client';

import { Message } from '../../lib/types';
import { parseDeepSeekReasoning } from '../../lib/utils/deepseekParser';
import DeepSeekReasoning from './DeepSeekReasoning';
import styles from './MessageItem.module.css';

interface MessageItemProps {
  message: Message;
  isStreaming?: boolean;
  isDeepSeekReasoning?: boolean;
  currentThinking?: string;
  currentAnswer?: string;
}

export default function MessageItem({ message, isStreaming = false, isDeepSeekReasoning = false, currentThinking = '', currentAnswer = '' }: MessageItemProps) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';
  const isSystem = message.role === 'system';

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const formatContent = (content: string) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
  };

  // Parse DeepSeek reasoning format for assistant messages
  const parsedReasoning = isAssistant ? parseDeepSeekReasoning(message.content) : null;
  
  // Only show DeepSeek reasoning if there's actual answer content or we're streaming
  const shouldShowDeepSeek = parsedReasoning?.isDeepSeekFormat && 
    (parsedReasoning.answer.trim() || isStreaming);

  return (
    <div className={`${styles.message} ${isUser ? styles.userMessage : styles.assistantMessage} ${isSystem ? styles.systemMessage : ''}`}>
      <div className={styles.messageContent}>
        <div className={styles.messageHeader}>
          <div className={styles.avatar}>
            {isUser ? '👤' : isSystem ? '⚙️' : '🤖'}
          </div>
          <div className={styles.messageInfo}>
            <span className={styles.role}>
              {isUser ? 'You' : isSystem ? 'System' : 'Assistant'}
            </span>
            <span className={styles.timestamp}>
              {formatTime(message.created_at)}
            </span>
          </div>
        </div>
        
        <div className={styles.messageBody}>
          {/* Display DeepSeek reasoning format for assistant messages */}
          {isAssistant && (shouldShowDeepSeek || isDeepSeekReasoning) ? (
            <DeepSeekReasoning 
              parsed={parsedReasoning || parseDeepSeekReasoning(message.content)} 
              isStreaming={isStreaming}
              currentThinking={currentThinking}
              currentAnswer={currentAnswer}
            />
          ) : (
            <div 
              className={styles.content}
              dangerouslySetInnerHTML={{ 
                __html: formatContent(message.content) 
              }}
            />
          )}
          
          {isStreaming && !shouldShowDeepSeek && !isDeepSeekReasoning && (
            <div className={styles.streamingIndicator}>
              <span className={styles.typingDots}>
                <span></span>
                <span></span>
                <span></span>
              </span>
            </div>
          )}
        </div>

        {message.model_used && (
          <div className={styles.messageFooter}>
            <span className={styles.modelInfo}>
              Model: {message.model_used}
              {message.tokens_used && ` • ${message.tokens_used} tokens`}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
