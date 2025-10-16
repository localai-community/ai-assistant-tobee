'use client';

import { useState } from 'react';
import { useChat } from '../../lib/hooks/useChat';
import { useSettings } from '../../lib/hooks/useSettings';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import Sidebar from './Sidebar';
import styles from './ChatInterface.module.css';

export default function ChatInterface() {
  const [currentUserId, setCurrentUserId] = useState('default-user');
  const { settings, updateSetting } = useSettings(currentUserId);
  const {
    messages,
    conversationId,
    isLoading,
    error,
    currentMessage,
    isSSEConnected,
    sendMessage,
    clearMessages,
    loadMessages,
    stopGeneration,
    setConversationId
  } = useChat({ userSettings: settings });

  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;
    await sendMessage(message);
  };

  const handleClearMessages = () => {
    clearMessages();
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleSelectConversation = async (conversationId: string) => {
    setConversationId(conversationId);
    await loadMessages(conversationId);
  };

  const handleUserIdChange = async (newUserId: string) => {
    if (newUserId !== currentUserId) {
      // Update the current user ID state
      setCurrentUserId(newUserId);
      
      // Clear current conversation to start fresh with new user
      setConversationId(null);
      clearMessages();
    }
  };

  const handleFileUploaded = (document: any) => {
    // If we don't have a conversation ID yet, set it from the uploaded document
    if (!conversationId && document.conversation_id) {
      setConversationId(document.conversation_id);
    }
  };

  return (
    <div className={styles.container}>
      {/* Sidebar */}
      <div className={`${styles.sidebar} ${sidebarOpen ? styles.sidebarOpen : styles.sidebarClosed}`}>
        <Sidebar
          settings={settings}
          onUpdateSetting={updateSetting}
          onClearMessages={handleClearMessages}
          onToggleSidebar={toggleSidebar}
          onSelectConversation={handleSelectConversation}
          onUserIdChange={handleUserIdChange}
          currentConversationId={conversationId}
          isOpen={sidebarOpen}
        />
      </div>

      {/* Main chat area */}
      <div className={styles.mainContent}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <button
              className={styles.sidebarToggle}
              onClick={toggleSidebar}
              aria-label="Toggle sidebar"
            >
              ☰
            </button>
            <h1 className={styles.title}>LocalAI Community</h1>
          </div>
          <div className={styles.headerRight}>
            <div className={styles.connectionStatus}>
              <span className={`${styles.statusDot} ${isSSEConnected ? styles.connected : styles.disconnected}`} />
              <span className={styles.statusText}>
                {isSSEConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            {isLoading && (
              <button
                className="btn btn-danger btn-sm"
                onClick={stopGeneration}
              >
                Stop
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className={styles.messagesContainer}>
          <MessageList
            messages={messages}
            currentMessage={currentMessage}
            isLoading={isLoading}
            error={error}
          />
        </div>

        {/* Input */}
        <div className={styles.inputContainer}>
          <ChatInput
            onSendMessage={handleSendMessage}
            onFileUploaded={handleFileUploaded}
            conversationId={conversationId}
            disabled={isLoading}
            placeholder="Type your message here..."
          />
        </div>
      </div>
    </div>
  );
}
