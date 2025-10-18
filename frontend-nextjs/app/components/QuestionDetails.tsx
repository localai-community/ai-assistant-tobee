'use client';

import { useState, useEffect } from 'react';
import { AIPrompt, ContextAwarenessData } from '../../lib/types';
import { getQuestionPrompt, getQuestionContext } from '../../lib/api';
import styles from './QuestionDetails.module.css';

interface QuestionDetailsProps {
  questionId: string | null;
  questionText: string;
  isOpen: boolean;
  onClose: () => void;
}

type TabType = 'prompt' | 'context';

export default function QuestionDetails({ questionId, questionText, isOpen, onClose }: QuestionDetailsProps) {
  const [activeTab, setActiveTab] = useState<TabType>('prompt');

  if (!isOpen) return null;

  // Show loading state if questionId is not available yet
  if (!questionId) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <div className={styles.questionInfo}>
            <h4 className={styles.questionTitle}>Question Details</h4>
            <p className={styles.questionText}>{questionText}</p>
          </div>
          <button className={styles.closeButton} onClick={onClose}>
            ×
          </button>
        </div>
        
        <div className={styles.content}>
          <div className={styles.loading}>
            <div className={styles.spinner}></div>
            <p>Loading question details...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.questionInfo}>
          <h4 className={styles.questionTitle}>Question Details</h4>
          <p className={styles.questionText}>{questionText}</p>
        </div>
        <button className={styles.closeButton} onClick={onClose}>
          ×
        </button>
      </div>
      
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === 'prompt' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('prompt')}
        >
          View Prompt
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'context' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('context')}
        >
          View Context
        </button>
      </div>
      
      <div className={styles.content}>
        {activeTab === 'prompt' && (
          <PromptViewerInline questionId={questionId} />
        )}
        
        {activeTab === 'context' && (
          <ContextViewerInline questionId={questionId} />
        )}
      </div>
    </div>
  );
}

// Inline Prompt Viewer Component
function PromptViewerInline({ questionId }: { questionId: string }) {
  const [prompt, setPrompt] = useState<AIPrompt | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (questionId) {
      fetchPrompt();
    }
  }, [questionId]);

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
      const parsed = JSON.parse(promptText);
      return JSON.stringify(parsed, null, 2);
    } catch {
      return promptText;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className={styles.tabContent}>
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
  );
}

// Inline Context Viewer Component
function ContextViewerInline({ questionId }: { questionId: string }) {
  const [contextData, setContextData] = useState<ContextAwarenessData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (questionId) {
      fetchContext();
    }
  }, [questionId]);

  const fetchContext = async () => {
    setLoading(true);
    setError(null);
    try {
      const context = await getQuestionContext(questionId);
      setContextData(context);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch context');
    } finally {
      setLoading(false);
    }
  };

  const formatContextData = (data: any) => {
    try {
      return JSON.stringify(data, null, 2);
    } catch {
      return String(data);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className={styles.tabContent}>
      {loading && (
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading context...</p>
        </div>
      )}
      
      {error && (
        <div className={styles.error}>
          <p>Error: {error}</p>
          <button onClick={fetchContext} className={styles.retryButton}>
            Retry
          </button>
        </div>
      )}
      
      {contextData.length > 0 && !loading && !error && (
        <div className={styles.contextContent}>
          {contextData.map((context, index) => (
            <div key={context.id} className={styles.contextItem}>
              <div className={styles.contextHeader}>
                <h4 className={styles.contextType}>
                  {context.context_type.replace(/_/g, ' ').toUpperCase()}
                </h4>
                <span className={styles.contextTimestamp}>
                  {formatTimestamp(context.context_timestamp)}
                </span>
              </div>
              
              <div className={styles.contextData}>
                <pre className={styles.contextText}>
                  {formatContextData(context.context_data)}
                </pre>
              </div>
              
              {context.context_metadata && (
                <div className={styles.contextMetadata}>
                  <h5>Metadata:</h5>
                  <pre className={styles.metadataText}>
                    {formatContextData(context.context_metadata)}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      
      {contextData.length === 0 && !loading && !error && (
        <div className={styles.noData}>
          <p>No context awareness data available for this question.</p>
        </div>
      )}
    </div>
  );
}
