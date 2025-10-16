'use client';

import { Message } from '../../lib/types';
import styles from './MessageItem.module.css';

interface MessageItemProps {
  message: Message;
  isStreaming?: boolean;
}

export default function MessageItem({ message, isStreaming = false }: MessageItemProps) {
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
          <div 
            className={styles.content}
            dangerouslySetInnerHTML={{ 
              __html: formatContent(message.content) 
            }}
          />
          
          {isStreaming && (
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
