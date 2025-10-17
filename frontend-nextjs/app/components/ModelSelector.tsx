'use client';

import { useState, useEffect, useCallback } from 'react';
import { getAvailableModels } from '../../lib/api';
import styles from './ModelSelector.module.css';

interface ModelSelectorProps {
  selectedModel: string;
  onModelChange: (model: string) => void;
}

export default function ModelSelector({ selectedModel, onModelChange }: ModelSelectorProps) {
  const [models, setModels] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  const loadModels = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const availableModels = await getAvailableModels();
      setModels(availableModels);
      setRetryCount(0); // Reset retry count on success
      
      // If selected model is not in the list, add it
      if (selectedModel && !availableModels.includes(selectedModel)) {
        setModels(prev => [selectedModel, ...prev]);
      }
    } catch (err) {
      console.error('Error loading models:', err);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to load models: ${errorMessage}. Make sure Ollama is running on localhost:11434`);
      // Fallback to common models
      setModels(['llama3:latest', 'llama2', 'codellama', 'mistral']);
    } finally {
      setIsLoading(false);
    }
  }, []); // Removed selectedModel dependency to prevent unnecessary reloads

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    loadModels();
  };

  useEffect(() => {
    loadModels();
  }, [loadModels]);

  // Add selected model to the list if it's not already there
  useEffect(() => {
    if (selectedModel && models.length > 0 && !models.includes(selectedModel)) {
      setModels(prev => [selectedModel, ...prev]);
    }
  }, [selectedModel, models]);

  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onModelChange(e.target.value);
  };

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <span className={styles.spinner}>⏳</span>
          <span>Loading models...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <span>⚠️</span>
          <div className={styles.errorContent}>
            <span>{error}</span>
            <button
              onClick={handleRetry}
              className={styles.retryButton}
              disabled={isLoading}
            >
              {isLoading ? 'Retrying...' : 'Retry'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <select
        value={selectedModel}
        onChange={handleModelChange}
        className={styles.select}
        disabled={models.length === 0}
      >
        {models.map((model) => (
          <option key={model} value={model}>
            {model}
          </option>
        ))}
      </select>
      
      {models.length > 0 && (
        <div className={styles.modelInfo}>
          <small>
            {models.length} model{models.length !== 1 ? 's' : ''} available
          </small>
        </div>
      )}
    </div>
  );
}
