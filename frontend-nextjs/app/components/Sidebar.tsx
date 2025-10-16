'use client';

import { useState } from 'react';
import { UserSettings, Conversation } from '../../lib/types';
import { useConversations } from '../../lib/hooks/useConversations';
import ModelSelector from './ModelSelector';
import styles from './Sidebar.module.css';

interface SidebarProps {
  settings: UserSettings;
  onUpdateSetting: (key: keyof UserSettings, value: any) => void;
  onClearMessages: () => void;
  onToggleSidebar: () => void;
  onSelectConversation?: (conversationId: string) => void;
  currentConversationId?: string | null;
  isOpen: boolean;
}

export default function Sidebar({ 
  settings, 
  onUpdateSetting, 
  onClearMessages, 
  onToggleSidebar,
  onSelectConversation,
  currentConversationId,
  isOpen 
}: SidebarProps) {
  const [activeTab, setActiveTab] = useState<'settings' | 'conversations'>('settings');
  const { conversations, isLoading, error, refreshConversations } = useConversations();

  const handleSettingChange = (key: keyof UserSettings, value: any) => {
    onUpdateSetting(key, value);
  };

  const handleClearMessages = () => {
    if (confirm('Are you sure you want to clear all messages? This action cannot be undone.')) {
      onClearMessages();
    }
  };

  const handleConversationSelect = (conversationId: string) => {
    if (onSelectConversation) {
      onSelectConversation(conversationId);
    }
  };

  const formatConversationTitle = (conversation: Conversation) => {
    if (conversation.title) {
      return conversation.title;
    }
    // Use first message content as title if no title is set
    const firstMessage = conversation.messages?.[0];
    if (firstMessage?.content) {
      return firstMessage.content.length > 50 
        ? firstMessage.content.substring(0, 50) + '...'
        : firstMessage.content;
    }
    return 'Untitled Conversation';
  };

  return (
    <div className={styles.sidebar}>
      <div className={styles.header}>
        <h2 className={styles.title}>Settings</h2>
        <button
          className={styles.closeButton}
          onClick={onToggleSidebar}
          aria-label="Close sidebar"
        >
          ✕
        </button>
      </div>

      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === 'settings' ? styles.active : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'conversations' ? styles.active : ''}`}
          onClick={() => setActiveTab('conversations')}
        >
          💬 Conversations
        </button>
      </div>

      <div className={styles.content}>
        {activeTab === 'settings' && (
          <div className={styles.settingsTab}>
            {/* Model Selection */}
            <div className={styles.section}>
              <h3 className={styles.sectionTitle}>Model</h3>
              <ModelSelector
                selectedModel={settings.selected_model || 'llama3.2'}
                onModelChange={(model) => handleSettingChange('selected_model', model)}
              />
            </div>

            {/* Temperature */}
            <div className={styles.section}>
              <h3 className={styles.sectionTitle}>Temperature</h3>
              <div className={styles.rangeContainer}>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={settings.temperature || 0.7}
                  onChange={(e) => handleSettingChange('temperature', parseFloat(e.target.value))}
                  className={styles.range}
                />
                <span className={styles.rangeValue}>{settings.temperature || 0.7}</span>
              </div>
            </div>

            {/* RAG Settings */}
            <div className={styles.section}>
              <h3 className={styles.sectionTitle}>RAG & Context</h3>
              <div className={styles.checkboxGroup}>
                <label className={styles.checkbox}>
                  <input
                    type="checkbox"
                    checked={settings.use_rag || false}
                    onChange={(e) => handleSettingChange('use_rag', e.target.checked)}
                  />
                  <span>Enable RAG</span>
                </label>
                <label className={styles.checkbox}>
                  <input
                    type="checkbox"
                    checked={settings.use_advanced_rag || false}
                    onChange={(e) => handleSettingChange('use_advanced_rag', e.target.checked)}
                  />
                  <span>Advanced RAG</span>
                </label>
                <label className={styles.checkbox}>
                  <input
                    type="checkbox"
                    checked={settings.enable_context_awareness || false}
                    onChange={(e) => handleSettingChange('enable_context_awareness', e.target.checked)}
                  />
                  <span>Context Awareness</span>
                </label>
                <label className={styles.checkbox}>
                  <input
                    type="checkbox"
                    checked={settings.include_memory || false}
                    onChange={(e) => handleSettingChange('include_memory', e.target.checked)}
                  />
                  <span>Include Memory</span>
                </label>
              </div>
            </div>

            {/* Reasoning Settings */}
            <div className={styles.section}>
              <h3 className={styles.sectionTitle}>Reasoning</h3>
              <div className={styles.checkboxGroup}>
                <label className={styles.checkbox}>
                  <input
                    type="checkbox"
                    checked={settings.use_unified_reasoning || false}
                    onChange={(e) => handleSettingChange('use_unified_reasoning', e.target.checked)}
                  />
                  <span>Unified Reasoning</span>
                </label>
                <label className={styles.checkbox}>
                  <input
                    type="checkbox"
                    checked={settings.use_phase2_reasoning || false}
                    onChange={(e) => handleSettingChange('use_phase2_reasoning', e.target.checked)}
                  />
                  <span>Phase 2 Reasoning</span>
                </label>
                <label className={styles.checkbox}>
                  <input
                    type="checkbox"
                    checked={settings.use_phase3_reasoning || false}
                    onChange={(e) => handleSettingChange('use_phase3_reasoning', e.target.checked)}
                  />
                  <span>Phase 3 Reasoning</span>
                </label>
                <label className={styles.checkbox}>
                  <input
                    type="checkbox"
                    checked={settings.use_reasoning_chat || false}
                    onChange={(e) => handleSettingChange('use_reasoning_chat', e.target.checked)}
                  />
                  <span>Reasoning Chat</span>
                </label>
              </div>
            </div>

            {/* Actions */}
            <div className={styles.section}>
              <h3 className={styles.sectionTitle}>Actions</h3>
              <div className={styles.buttonGroup}>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={handleClearMessages}
                >
                  Clear Messages
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'conversations' && (
          <div className={styles.conversationsTab}>
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h3 className={styles.sectionTitle}>Recent Conversations</h3>
                <button
                  className={styles.refreshButton}
                  onClick={refreshConversations}
                  title="Refresh conversations"
                >
                  🔄
                </button>
              </div>
              
              {isLoading && (
                <div className={styles.loadingState}>
                  <p>Loading conversations...</p>
                </div>
              )}
              
              {error && (
                <div className={styles.errorState}>
                  <p>Error loading conversations: {error}</p>
                  <button
                    className="btn btn-sm"
                    onClick={refreshConversations}
                  >
                    Retry
                  </button>
                </div>
              )}
              
              {!isLoading && !error && conversations.length === 0 && (
                <div className={styles.emptyState}>
                  <div className={styles.emptyIcon}>💬</div>
                  <p>No conversations yet</p>
                  <small>Start a new conversation to see it here</small>
                </div>
              )}
              
              {!isLoading && !error && conversations.length > 0 && (
                <div className={styles.conversationList}>
                  {conversations.map((conversation) => {
                    const isCurrent = currentConversationId === conversation.id;
                    return (
                      <div
                        key={conversation.id}
                        className={`${styles.conversationItem} ${isCurrent ? styles.currentConversation : ''}`}
                        onClick={() => handleConversationSelect(conversation.id)}
                      >
                        <div className={styles.conversationTitle}>
                          {formatConversationTitle(conversation)}
                        </div>
                        <div className={styles.conversationMeta}>
                          <span className={styles.conversationModel}>
                            {conversation.model || 'llama3.2'}
                          </span>
                          <span className={styles.conversationDate}>
                            {new Date(conversation.updated_at).toLocaleDateString()}
                          </span>
                        </div>
                        {isCurrent && (
                          <div className={styles.currentIndicator}>👈</div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
