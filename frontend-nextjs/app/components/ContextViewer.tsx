'use client';

import { useState, useEffect } from 'react';
import { ContextAwarenessData } from '../../lib/types';
import { getQuestionContext } from '../../lib/api';
import styles from './ContextViewer.module.css';

interface ContextViewerProps {
  questionId: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function ContextViewer({ questionId, isOpen, onClose }: ContextViewerProps) {
  const [contextData, setContextData] = useState<ContextAwarenessData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && questionId) {
      fetchContext();
    }
  }, [isOpen, questionId]);

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

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const formatContextType = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const renderContextData = (data: any, type: string) => {
    if (Array.isArray(data)) {
      return (
        <div className={styles.contextList}>
          {data.map((item, index) => (
            <div key={index} className={styles.contextItem}>
              <pre className={styles.contextText}>
                {typeof item === 'string' ? item : JSON.stringify(item, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      );
    } else if (typeof data === 'object') {
      return (
        <pre className={styles.contextText}>
          {JSON.stringify(data, null, 2)}
        </pre>
      );
    } else {
      return (
        <div className={styles.contextText}>
          {String(data)}
        </div>
      );
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h3 className={styles.title}>Context Awareness Data</h3>
          <button className={styles.closeButton} onClick={onClose}>
            ×
          </button>
        </div>
        
        <div className={styles.content}>
          {loading && (
            <div className={styles.loading}>
              <div className={styles.spinner}></div>
              <p>Loading context data...</p>
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
          
          {contextData.length === 0 && !loading && !error && (
            <div className={styles.noData}>
              <p>No context data available for this question.</p>
            </div>
          )}
          
          {contextData.length > 0 && !loading && !error && (
            <div className={styles.contextContent}>
              {contextData.map((context, index) => (
                <div key={context.id} className={styles.contextSection}>
                  <div className={styles.contextHeader}>
                    <h4 className={styles.contextType}>
                      {formatContextType(context.context_type)}
                    </h4>
                    <div className={styles.contextMetadata}>
                      <span className={styles.timestamp}>
                        {formatTimestamp(context.context_timestamp)}
                      </span>
                      {context.context_metadata && (
                        <div className={styles.metadata}>
                          {Object.entries(context.context_metadata).map(([key, value]) => (
                            <span key={key} className={styles.metadataItem}>
                              <strong>{key}:</strong> {String(value)}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className={styles.contextBody}>
                    {renderContextData(context.context_data, context.context_type)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
