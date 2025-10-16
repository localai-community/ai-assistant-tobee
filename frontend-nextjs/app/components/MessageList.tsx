'use client';

import { useEffect, useRef } from 'react';
import { Message } from '../../lib/types';
import MessageItem from './MessageItem';
import styles from './MessageList.module.css';

interface MessageListProps {
  messages: Message[];
  currentMessage: string;
  isLoading: boolean;
  error: string | null;
}

export default function MessageList({ messages, currentMessage, isLoading, error }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentMessage]);

  if (messages.length === 0 && !isLoading && !error) {
    return (
      <div className={styles.emptyState}>
        <div className={styles.emptyIcon}>🤖</div>
        <h3 className={styles.emptyTitle}>Welcome to LocalAI Community</h3>
        <p className={styles.emptyDescription}>
          Start a conversation by typing a message below. You can ask questions, 
          upload documents, or explore the AI's capabilities.
        </p>
        <div className={styles.samplePrompts}>
          <h4>Try these sample prompts:</h4>
          <div className={styles.promptGrid}>
            <button className={styles.samplePrompt}>
              "Explain quantum computing in simple terms"
            </button>
            <button className={styles.samplePrompt}>
              "Help me write a Python function"
            </button>
            <button className={styles.samplePrompt}>
              "What are the latest trends in AI?"
            </button>
            <button className={styles.samplePrompt}>
              "Summarize this document" (after uploading)
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.messages}>
        {messages.map((message) => (
          <MessageItem key={message.id} message={message} />
        ))}
        
        {/* Show current streaming message */}
        {isLoading && currentMessage && (
          <MessageItem
            message={{
              id: 'streaming',
              conversation_id: 'current',
              role: 'assistant',
              content: currentMessage,
              created_at: new Date().toISOString()
            }}
            isStreaming={true}
          />
        )}
        
        {/* Show error message */}
        {error && (
          <div className={styles.errorMessage}>
            <div className={styles.errorIcon}>⚠️</div>
            <div className={styles.errorContent}>
              <h4>Error</h4>
              <p>{error}</p>
            </div>
          </div>
        )}
        
        {/* Auto-scroll anchor */}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
