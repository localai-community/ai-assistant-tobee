'use client';

import { useState } from 'react';
import { useChat } from '../../lib/hooks/useChat';
import { useSettings } from '../../lib/hooks/useSettings';
import { useCurrentUser } from '../../lib/hooks/useCurrentUser';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import Sidebar from './Sidebar';
import NoUserWarningModal from './NoUserWarningModal';
import styles from './ChatInterface.module.css';

export default function ChatInterface() {
  const { currentUserId, saveCurrentUser, isLoading: userLoading } = useCurrentUser();
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
  } = useChat({ userSettings: settings, userId: currentUserId });

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showNoUserWarning, setShowNoUserWarning] = useState(false);
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;
    
    // Check if user is selected (not guest user)
    const GUEST_USER_ID = '00000000-0000-0000-0000-000000000001';
    const isGuestUser = currentUserId === GUEST_USER_ID;
    
    if (isGuestUser) {
      // Show warning modal for guest user
      setPendingMessage(message);
      setShowNoUserWarning(true);
      return;
    }
    
    // User is selected, proceed with sending message
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

  const handleNewConversation = () => {
    // Clear current conversation and messages to start fresh
    setConversationId(null);
    clearMessages();
  };

  const handleUserIdChange = async (newUserId: string) => {
    if (newUserId !== currentUserId) {
      try {
        console.log('Switching user from', currentUserId, 'to', newUserId);
        // Save the new user to the database
        await saveCurrentUser(newUserId);
        
        // Clear current conversation to start fresh with new user
        setConversationId(null);
        clearMessages();
        console.log('User switch completed successfully');
      } catch (error) {
        console.error('Error switching user:', error);
        throw error; // Re-throw to be caught by the calling function
      }
    }
  };

  const handleFileUploaded = (document: any) => {
    // If we don't have a conversation ID yet, set it from the uploaded document
    if (!conversationId && document.conversation_id) {
      setConversationId(document.conversation_id);
    }
  };

  const handleNoUserWarningClose = () => {
    setShowNoUserWarning(false);
    setPendingMessage(null);
  };

  const handleNoUserWarningContinue = async () => {
    setShowNoUserWarning(false);
    if (pendingMessage) {
      // Send message without saving to database (guest mode)
      await sendMessage(pendingMessage);
      setPendingMessage(null);
    }
  };

  // Show loading state while user is being loaded
  if (userLoading) {
    return (
      <div className={styles.container}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh',
          fontSize: '18px',
          color: '#666'
        }}>
          Loading user session...
        </div>
      </div>
    );
  }

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
          onNewConversation={handleNewConversation}
          onUserIdChange={handleUserIdChange}
          currentConversationId={conversationId}
          currentUserId={currentUserId}
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
          onSendMessage={handleSendMessage}
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

      {/* No User Warning Modal */}
      <NoUserWarningModal
        isOpen={showNoUserWarning}
        onClose={handleNoUserWarningClose}
        onContinue={handleNoUserWarningContinue}
      />
    </div>
  );
}
