import { useState, useEffect, useCallback } from 'react';
import { Conversation } from '../types';
import { getConversations, deleteConversation } from '../api';

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

  const removeConversation = useCallback(async (conversationId: string) => {
    try {
      console.log('useConversations: Calling deleteConversation API for:', conversationId);
      await deleteConversation(conversationId);
      console.log('useConversations: API call successful, updating local state');
      // Remove the conversation from local state
      setConversations(prev => {
        const filtered = prev.filter(conv => conv.id !== conversationId);
        console.log('useConversations: Updated conversations count:', filtered.length);
        return filtered;
      });
      // Clear any error state after successful deletion
      setError(null);
    } catch (err) {
      console.error('useConversations: Error deleting conversation:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete conversation');
      throw err; // Re-throw so the UI can handle the error
    }
  }, []);

  // Fetch conversations on mount and when userId changes
  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  return {
    conversations,
    isLoading,
    error,
    refreshConversations,
    deleteConversation: removeConversation
  };
}
