import { useState, useEffect, useCallback } from 'react';
import { getCurrentUser, setCurrentUser } from '../api';

const GUEST_USER_ID = '00000000-0000-0000-0000-000000000001'; // Guest user ID
const SESSION_KEY = 'default_session';

export function useCurrentUser() {
  const [currentUserId, setCurrentUserId] = useState<string>(GUEST_USER_ID);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load the current user from the database on mount
  const loadCurrentUser = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const savedUserId = await getCurrentUser(SESSION_KEY);
      if (savedUserId) {
        setCurrentUserId(savedUserId);
      } else {
        // No saved user, use guest as default
        setCurrentUserId(GUEST_USER_ID);
        // Save the guest user as the default
        await setCurrentUser(GUEST_USER_ID, SESSION_KEY);
      }
    } catch (err) {
      console.error('Error loading current user:', err);
      setError(err instanceof Error ? err.message : 'Failed to load current user');
      // Fallback to guest user on error
      setCurrentUserId(GUEST_USER_ID);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Save the current user to the database
  const saveCurrentUser = useCallback(async (userId: string) => {
    try {
      console.log('Saving current user in hook:', userId);
      await setCurrentUser(userId, SESSION_KEY);
      setCurrentUserId(userId);
      setError(null);
      console.log('User saved successfully in hook');
    } catch (err) {
      console.error('Error saving current user in hook:', err);
      setError(err instanceof Error ? err.message : 'Failed to save current user');
      throw err; // Re-throw to be caught by the calling function
    }
  }, []);

  // Load user on mount
  useEffect(() => {
    loadCurrentUser();
  }, [loadCurrentUser]);

  return {
    currentUserId,
    isLoading,
    error,
    saveCurrentUser,
    refreshCurrentUser: loadCurrentUser
  };
}
