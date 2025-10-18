'use client';

import { useState, useEffect } from 'react';
import { AIPrompt } from '../../lib/types';
import { getQuestionPrompt } from '../../lib/api';
import styles from './PromptViewer.module.css';

interface PromptViewerProps {
  questionId: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function PromptViewer({ questionId, isOpen, onClose }: PromptViewerProps) {
  const [prompt, setPrompt] = useState<AIPrompt | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && questionId) {
      fetchPrompt();
    }
  }, [isOpen, questionId]);

  const fetchPrompt = async () => {
    setLoading(true);
    setError(null);
    try {
      const promptData = await getQuestionPrompt(questionId);
      setPrompt(promptData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch prompt');
    } finally {
      setLoading(false);
    }
  };

  const formatPrompt = (promptText: string) => {
    try {
      // Try to parse as JSON first (structured prompt)
      const parsed = JSON.parse(promptText);
      return JSON.stringify(parsed, null, 2);
    } catch {
      // If not JSON, return as-is
      return promptText;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h3 className={styles.title}>AI Prompt Details</h3>
          <button className={styles.closeButton} onClick={onClose}>
            ×
          </button>
        </div>
        
        <div className={styles.content}>
          {loading && (
            <div className={styles.loading}>
              <div className={styles.spinner}></div>
              <p>Loading prompt...</p>
            </div>
          )}
          
          {error && (
            <div className={styles.error}>
              <p>Error: {error}</p>
              <button onClick={fetchPrompt} className={styles.retryButton}>
                Retry
              </button>
            </div>
          )}
          
          {prompt && !loading && !error && (
            <div className={styles.promptContent}>
              <div className={styles.metadata}>
                <div className={styles.metadataItem}>
                  <strong>Model:</strong> {prompt.model_used}
                </div>
                <div className={styles.metadataItem}>
                  <strong>Temperature:</strong> {prompt.temperature || 'Default'}
                </div>
                <div className={styles.metadataItem}>
                  <strong>Max Tokens:</strong> {prompt.max_tokens || 'Unlimited'}
                </div>
                <div className={styles.metadataItem}>
                  <strong>Timestamp:</strong> {formatTimestamp(prompt.prompt_timestamp)}
                </div>
              </div>
              
              <div className={styles.promptSection}>
                <h4 className={styles.sectionTitle}>Final Prompt Sent to AI Model</h4>
                <pre className={styles.promptText}>
                  {formatPrompt(prompt.final_prompt)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
