import { useState, useEffect, useCallback } from 'react';
import { UserSettings } from '../types';
import { getUserSettings, updateUserSettings } from '../api';

const DEFAULT_USER_ID = 'default-user';

const defaultSettings: UserSettings = {
  user_id: DEFAULT_USER_ID,
  enable_context_awareness: true,
  include_memory: true,
  context_strategy: 'auto',
  selected_model: 'llama3.2',
  use_streaming: true,
  use_rag: false,
  use_advanced_rag: false,
  use_phase2_reasoning: false,
  use_reasoning_chat: false,
  use_phase3_reasoning: false,
  selected_phase2_engine: 'ollama',
  selected_phase3_strategy: 'auto',
  temperature: 0.7,
  use_unified_reasoning: false,
  selected_reasoning_mode: 'auto'
};

export function useSettings(userId: string = DEFAULT_USER_ID) {
  const [settings, setSettings] = useState<UserSettings>(defaultSettings);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load settings from backend
  const loadSettings = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const userSettings = await getUserSettings(userId);
      setSettings({ ...defaultSettings, ...userSettings });
    } catch (err) {
      console.error('Error loading user settings:', err);
      // Use default settings if loading fails
      setSettings({ ...defaultSettings, user_id: userId });
      setError(err instanceof Error ? err.message : 'Failed to load settings');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // Save settings to backend
  const saveSettings = useCallback(async (newSettings: Partial<UserSettings>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const updatedSettings = await updateUserSettings(userId, newSettings);
      setSettings(prev => ({ ...prev, ...updatedSettings }));
    } catch (err) {
      console.error('Error saving user settings:', err);
      setError(err instanceof Error ? err.message : 'Failed to save settings');
    } finally {
      setIsLoading(false);
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

  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

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
