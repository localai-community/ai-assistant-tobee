'use client';

import { useState } from 'react';
import { DeepSeekParsed } from '../../lib/utils/deepseekParser';
import MarkdownRenderer from './MarkdownRenderer';
import styles from './DeepSeekReasoning.module.css';

interface DeepSeekReasoningProps {
  parsed: DeepSeekParsed;
  isStreaming?: boolean;
  currentThinking?: string; // For streaming thinking content
  currentAnswer?: string; // For streaming answer content
}

export default function DeepSeekReasoning({ 
  parsed, 
  isStreaming = false, 
  currentThinking,
  currentAnswer
}: DeepSeekReasoningProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!parsed.isDeepSeekFormat) {
    return null;
  }

  const thinkingContent = isStreaming && currentThinking ? currentThinking : parsed.thinking;
  const hasThinkingContent = thinkingContent.trim().length > 0;
  
  // During streaming, use currentAnswer if available, otherwise extract from currentThinking
  let answerContent = parsed.answer;
  let isInThinkingPhase = false;
  
  if (isStreaming) {
    if (currentAnswer) {
      answerContent = currentAnswer;
    } else if (currentThinking && currentThinking.includes('</think>')) {
      const thinkEndIndex = currentThinking.indexOf('</think>');
      answerContent = currentThinking.substring(thinkEndIndex + 8).trim();
    } else if (currentThinking && !currentThinking.includes('</think>')) {
      // We're in the thinking phase - <think> tag appeared but </think> hasn't yet
      isInThinkingPhase = true;
    }
  }

  // Debug logging
  console.log('DeepSeekReasoning Debug:', {
    isStreaming,
    isDeepSeekFormat: parsed.isDeepSeekFormat,
    currentThinking,
    currentAnswer,
    answerContent,
    isInThinkingPhase,
    hasThinkingContent
  });

  // If there's no answer content and no thinking content, don't render anything
  // This prevents showing empty DeepSeek components
  if (!answerContent.trim() && !hasThinkingContent) {
    return null;
  }

  return (
    <div className={styles.container}>
      {/* Reasoning Process Section - Always show button if there's thinking content */}
      {hasThinkingContent && (
        <div className={styles.reasoningSection}>
          <button
            className={`${styles.expandButton} ${isExpanded ? styles.expanded : ''} ${isStreaming ? styles.thinking : ''}`}
            onClick={() => setIsExpanded(!isExpanded)}
            type="button"
          >
            <span className={styles.icon}>🧠</span>
            <span className={styles.label}>
              {isStreaming ? 'Thinking...' : 'View Reasoning Process'}
            </span>
            <span className={`${styles.arrow} ${isExpanded ? styles.arrowUp : styles.arrowDown}`}>
              ▼
            </span>
          </button>
          
          {/* Only show thinking content when explicitly expanded and not streaming */}
          {isExpanded && !isStreaming && (
            <div className={styles.reasoningContent}>
              <div className={styles.thinkingText}>
                {thinkingContent}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Answer Section - Only show if there's actual answer content */}
      {answerContent.trim() && (
        <div className={styles.answerSection}>
          <MarkdownRenderer content={answerContent} className={styles.answerContent} />
          {isStreaming && !answerContent.includes('▌') && <span className={styles.cursor}>▌</span>}
        </div>
      )}

      {/* Show thinking loader when <think> tag appears but </think> hasn't yet */}
      {isStreaming && isInThinkingPhase && (
        <div className={styles.thinkingLoader}>
          <span className={styles.loaderIcon}>🧠</span>
          <span className={styles.loaderText}>DeepSeek is thinking...</span>
          <div className={styles.loaderDots}>
            <div className={styles.loaderDot}></div>
            <div className={styles.loaderDot}></div>
            <div className={styles.loaderDot}></div>
          </div>
        </div>
      )}

      {/* Fallback: If not streaming and no answer content, show a message indicating no answer */}
      {!isStreaming && !answerContent.trim() && hasThinkingContent && (
        <div className={styles.answerSection}>
          <div className={styles.answerContent}>
            <span className={styles.noAnswerMessage}>
              No answer content available. Click "View Reasoning Process" to see the thinking process.
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
