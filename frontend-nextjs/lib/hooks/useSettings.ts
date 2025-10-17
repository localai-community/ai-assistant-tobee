import { useState, useEffect, useCallback } from 'react';
import { UserSettings } from '../types';
import { getUserSettings, updateUserSettings } from '../api';

const DEFAULT_USER_ID = 'default-user';

const defaultSettings: UserSettings = {
  user_id: DEFAULT_USER_ID,
  enable_context_awareness: true,
  include_memory: true,
  context_strategy: 'conversation_only',
  selected_model: 'llama3:latest',
  use_streaming: true,
  use_rag: false,
  use_advanced_rag: false,
  use_phase2_reasoning: false,
  use_reasoning_chat: false,
  use_phase3_reasoning: false,
  selected_phase2_engine: 'auto',
  selected_phase3_strategy: 'auto',
  temperature: 0.7,
  use_unified_reasoning: false,
  selected_reasoning_mode: 'auto'
};

export function useSettings(userId: string = DEFAULT_USER_ID) {
  const [settings, setSettings] = useState<UserSettings>({ ...defaultSettings, user_id: userId });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);

  // Load settings from backend
  const loadSettings = useCallback(async () => {
    // Don't reload settings if we're currently updating
    if (isUpdating) {
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const userSettings = await getUserSettings(userId);
      // Only update settings if we don't have any current settings or if this is a new user
      setSettings(prev => {
        // If this is the first load (no user_id set), use backend settings
        if (!prev.user_id || prev.user_id !== userId) {
          // If switching to guest user, always use default settings
          if (userId === DEFAULT_USER_ID) {
            return { ...defaultSettings, user_id: userId };
          }
          return { ...defaultSettings, ...userSettings };
        }
        // If switching to guest user from another user, always reset to default settings
        if (userId === DEFAULT_USER_ID && prev.user_id !== DEFAULT_USER_ID) {
          return { ...defaultSettings, user_id: userId };
        }
        
        // Otherwise, merge backend settings with current settings to preserve local changes
        const mergedSettings = { ...prev, ...userSettings };
        
        // CRITICAL: Don't override the selected_model if it's already set and different from backend
        // UNLESS we're switching to guest user - then always use default model
        if (userId === DEFAULT_USER_ID) {
          mergedSettings.selected_model = defaultSettings.selected_model;
        } else if (prev.selected_model && prev.selected_model !== userSettings.selected_model) {
          mergedSettings.selected_model = prev.selected_model;
        }
        
        return mergedSettings;
      });
    } catch (err) {
      console.error('Error loading user settings:', err);
      // Use default settings if loading fails
      setSettings({ ...defaultSettings, user_id: userId });
      setError(err instanceof Error ? err.message : 'Failed to load settings');
    } finally {
      setIsLoading(false);
    }
  }, [userId, isUpdating]);

  // Save settings to backend
  const saveSettings = useCallback(async (newSettings: Partial<UserSettings>) => {
    setIsUpdating(true);
    setIsLoading(true);
    setError(null);
    
    try {
      // Update local state immediately for better UX
      setSettings(prev => ({ ...prev, ...newSettings }));
      
      // Then save to backend (don't update local state with response)
      await updateUserSettings(userId, newSettings);
    } catch (err) {
      console.error('Error saving user settings:', err);
      setError(err instanceof Error ? err.message : 'Failed to save settings');
    } finally {
      setIsLoading(false);
      setIsUpdating(false);
    }
  }, [userId]);

  // Update a specific setting
  const updateSetting = useCallback(async (key: keyof UserSettings, value: any) => {
    const newSettings = { [key]: value };
    await saveSettings(newSettings);
  }, [saveSettings]);

  // Reset to default settings
  const resetSettings = useCallback(async () => {
    await saveSettings(defaultSettings);
  }, [saveSettings]);

  // Load settings on mount and when userId changes
  useEffect(() => {
    loadSettings();
  }, [userId, loadSettings]); // Include loadSettings in dependencies

  // Don't reload settings when settings change - this was causing the issue

  return {
    settings,
    isLoading,
    error,
    loadSettings,
    saveSettings,
    updateSetting,
    resetSettings
  };
}
