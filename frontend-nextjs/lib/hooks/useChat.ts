import { useState, useCallback, useRef } from 'react';
import { Message, ChatRequest, UserSettings } from '../types';
import { getMessages } from '../api';
import { isDeepSeekFormat, extractThinkingContent, extractAnswerContent } from '../utils/deepseekParser';

interface UseChatOptions {
  initialMessages?: Message[];
  conversationId?: string;
  userSettings?: UserSettings;
  userId?: string;
}

export function useChat(options: UseChatOptions = {}) {
  const { initialMessages = [], conversationId: initialConversationId, userSettings, userId } = options;
  
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [conversationId, setConversationId] = useState<string | null>(initialConversationId || null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentMessage, setCurrentMessage] = useState<string>('');
  const [isSSEConnected, setIsSSEConnected] = useState(false);
  const [isDeepSeekReasoning, setIsDeepSeekReasoning] = useState(false);
  const [currentThinking, setCurrentThinking] = useState<string>('');
  const [currentAnswer, setCurrentAnswer] = useState<string>('');
  
  const currentMessageRef = useRef<string>('');
  const abortControllerRef = useRef<AbortController | null>(null);
  const currentUserMessageIdRef = useRef<string | null>(null);

  const sendStreamingMessage = useCallback(async (chatRequest: ChatRequest) => {
    try {
      const abortController = new AbortController();
      abortControllerRef.current = abortController;
      setIsSSEConnected(true);

      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(chatRequest),
        signal: abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          // Stream is complete
          const assistantMessage: Message = {
            id: `msg-${Date.now()}`,
            conversation_id: chatRequest.conversation_id!,
            role: 'assistant',
            content: currentMessageRef.current,
            created_at: new Date().toISOString()
          };
          
          setMessages(prev => [...prev, assistantMessage]);
          setCurrentMessage('');
          currentMessageRef.current = '';
          setCurrentThinking('');
          setCurrentAnswer('');
          currentUserMessageIdRef.current = null;
          setIsLoading(false);
          setIsSSEConnected(false);
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'metadata') {
                // Store conversation ID if provided
                if (data.conversation_id) {
                  setConversationId(data.conversation_id);
                  // Update the user message with the correct conversation_id
                  if (currentUserMessageIdRef.current) {
                    setMessages(prev => prev.map(msg => 
                      msg.id === currentUserMessageIdRef.current && msg.conversation_id === 'temp'
                        ? { ...msg, conversation_id: data.conversation_id }
                        : msg
                    ));
                  }
                }
              } else if (data.type === 'content') {
                // Accumulate content
                const content = data.content || '';
                const newContent = currentMessageRef.current + content;
                setCurrentMessage(newContent);
                currentMessageRef.current = newContent;
                
                // Check for DeepSeek reasoning format
                if (!isDeepSeekReasoning && isDeepSeekFormat(newContent)) {
                  setIsDeepSeekReasoning(true);
                }
                
                // Extract thinking and answer content if in DeepSeek format
                if (isDeepSeekReasoning) {
                  const thinkingContent = extractThinkingContent(newContent);
                  setCurrentThinking(thinkingContent);
                  
                  const answerContent = extractAnswerContent(newContent);
                  setCurrentAnswer(answerContent);
                }
              } else if (data.type === 'error') {
                setError(data.error || 'An error occurred');
                setIsLoading(false);
                setIsSSEConnected(false);
                return;
              }
            } catch (err) {
              console.error('Failed to parse streaming data:', err);
            }
          }
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        console.log('Stream aborted');
      } else {
        console.error('Streaming error:', err);
        setError(err instanceof Error ? err.message : 'Streaming failed');
      }
      setIsLoading(false);
      setIsSSEConnected(false);
      setCurrentThinking('');
      setCurrentAnswer('');
      currentUserMessageIdRef.current = null;
    }
  }, []);

  const sendChatMessage = useCallback(async (message: string) => {
    if (!message.trim() || isLoading) return;

    setError(null);
    setIsLoading(true);
    setCurrentMessage('');
    currentMessageRef.current = '';
    setIsDeepSeekReasoning(false);
    setCurrentThinking('');
    setCurrentAnswer('');

    try {
      // Don't create conversation explicitly - let the streaming endpoint handle it
      let currentConversationId = conversationId;

      // Check if user is guest (don't save to database)
      const GUEST_USER_ID = '00000000-0000-0000-0000-000000000001';
      const isGuestUser = userId === GUEST_USER_ID;

      // Add user message to the list (conversation_id will be set when streaming starts)
      const userMessageId = `temp-${Date.now()}`;
      currentUserMessageIdRef.current = userMessageId;
      
      const userMessage: Message = {
        id: userMessageId,
        conversation_id: isGuestUser ? 'guest-temp' : (currentConversationId || 'temp'),
        role: 'user',
        content: message,
        created_at: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, userMessage]);

      // Prepare chat request
      const chatRequest: ChatRequest = {
        conversation_id: isGuestUser ? undefined : (currentConversationId || undefined), // Don't save conversation for guest
        message,
        model: userSettings?.selected_model || 'llama3:latest',
        temperature: userSettings?.temperature || 0.7,
        user_id: isGuestUser ? undefined : userId, // Don't save user_id for guest
        use_rag: userSettings?.use_rag || false,
        use_advanced_rag: userSettings?.use_advanced_rag || false,
        use_phase2_reasoning: userSettings?.use_phase2_reasoning || false,
        use_reasoning_chat: userSettings?.use_reasoning_chat || false,
        use_phase3_reasoning: userSettings?.use_phase3_reasoning || false,
        use_unified_reasoning: userSettings?.use_unified_reasoning || false,
        selected_reasoning_mode: userSettings?.selected_reasoning_mode || 'auto',
        selected_phase2_engine: userSettings?.selected_phase2_engine,
        selected_phase3_strategy: userSettings?.selected_phase3_strategy,
        enable_context_awareness: userSettings?.enable_context_awareness || false,
        include_memory: userSettings?.include_memory || false,
        context_strategy: userSettings?.context_strategy
      };

      // Send the message with streaming
      await sendStreamingMessage(chatRequest);

    } catch (err) {
      console.error('Error sending message:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message');
      setIsLoading(false);
    }
  }, [conversationId, isLoading, userSettings]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentMessage('');
    currentMessageRef.current = '';
    currentUserMessageIdRef.current = null;
    setError(null);
  }, []);

  const loadMessages = useCallback(async (convId: string) => {
    try {
      const loadedMessages = await getMessages(convId);
      setMessages(loadedMessages);
    } catch (err) {
      console.error('Error loading messages:', err);
      setError(err instanceof Error ? err.message : 'Failed to load messages');
    }
  }, []);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsLoading(false);
    setCurrentMessage('');
    currentMessageRef.current = '';
    currentUserMessageIdRef.current = null;
  }, []);

  return {
    messages,
    conversationId,
    isLoading,
    error,
    currentMessage,
    isSSEConnected,
    isDeepSeekReasoning,
    currentThinking,
    currentAnswer,
    sendMessage: sendChatMessage,
    clearMessages,
    loadMessages,
    stopGeneration,
    setConversationId
  };
}
