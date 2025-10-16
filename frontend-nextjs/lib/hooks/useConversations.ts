import { useState, useEffect, useCallback } from 'react';
import { Conversation } from '../types';
import { getConversations } from '../api';

export function useConversations(userId?: string) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchConversations = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const fetchedConversations = await getConversations(userId);
      setConversations(fetchedConversations);
    } catch (err) {
      console.error('Error fetching conversations:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch conversations');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  const refreshConversations = useCallback(() => {
    fetchConversations();
  }, [fetchConversations]);

  // Fetch conversations on mount and when userId changes
  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  return {
    conversations,
    isLoading,
    error,
    refreshConversations
  };
}
