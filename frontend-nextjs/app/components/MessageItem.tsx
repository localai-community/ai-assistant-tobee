'use client';

import { useState } from 'react';
import { Message } from '../../lib/types';
import { parseDeepSeekReasoning } from '../../lib/utils/deepseekParser';
import DeepSeekReasoning from './DeepSeekReasoning';
import MarkdownRenderer from './MarkdownRenderer';
import QuestionDetails from './QuestionDetails';
import { getConversationQuestions } from '../../lib/api';
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
  
  // State for question details
  const [showQuestionDetails, setShowQuestionDetails] = useState(false);
  const [questionId, setQuestionId] = useState<string | null>(null);
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false);

  // Function to find question ID for user messages
  const findQuestionId = async () => {
    if (!isUser || !message.conversation_id) {
      return;
    }
    
    setIsLoadingQuestion(true);
    try {
      const questions = await getConversationQuestions(message.conversation_id);
      
      // Find the question that matches this message content and timestamp
      const matchingQuestion = questions.find(q => {
        const contentMatch = q.question_text === message.content;
        const timeDiff = Math.abs(new Date(q.question_timestamp).getTime() - new Date(message.created_at).getTime());
        const timeMatch = timeDiff < 5000; // Within 5 seconds
        
        return contentMatch && timeMatch;
      });
      
      if (matchingQuestion) {
        setQuestionId(matchingQuestion.id);
      } else {
        // Fallback 1: Try to find by content match only (ignore time)
        const contentOnlyMatch = questions.find(q => q.question_text === message.content);
        if (contentOnlyMatch) {
          setQuestionId(contentOnlyMatch.id);
        } else {
          // Fallback 2: Try to find by conversation and approximate time (more generous)
          const fallbackQuestion = questions.find(q => {
            const timeDiff = Math.abs(new Date(q.question_timestamp).getTime() - new Date(message.created_at).getTime());
            return timeDiff < 3600000; // Within 1 hour
          });
          
          if (fallbackQuestion) {
            setQuestionId(fallbackQuestion.id);
          } else {
            // Fallback 3: Just take the first question from this conversation
            const firstQuestion = questions[0];
            if (firstQuestion) {
              setQuestionId(firstQuestion.id);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error finding question ID:', error);
    } finally {
      setIsLoadingQuestion(false);
    }
  };

  // Toggle question details
  const toggleQuestionDetails = () => {
    if (!questionId && !isLoadingQuestion) {
      findQuestionId();
    }
    setShowQuestionDetails(!showQuestionDetails);
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
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
            <MarkdownRenderer content={message.content} className={styles.content} />
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
        
        {/* Question details toggle for user messages */}
        {isUser && (
          <div className={styles.questionActions}>
            <button
              className={styles.toggleButton}
              onClick={toggleQuestionDetails}
              disabled={isLoadingQuestion}
            >
              {isLoadingQuestion ? (
                <span className={styles.loadingText}>Loading...</span>
              ) : (
                <span className={styles.toggleText}>
                  {showQuestionDetails ? 'Hide Details' : 'View Details'}
                </span>
              )}
            </button>
          </div>
        )}
      </div>
      
      {/* Question details component */}
      {isUser && showQuestionDetails && (
        <QuestionDetails
          questionId={questionId}
          questionText={message.content}
          isOpen={showQuestionDetails}
          onClose={() => setShowQuestionDetails(false)}
        />
      )}
    </div>
  );
}
