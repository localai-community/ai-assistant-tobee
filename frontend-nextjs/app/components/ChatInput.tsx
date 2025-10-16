'use client';

import { useState, useRef, KeyboardEvent } from 'react';
import FileUpload from './FileUpload';
import { uploadDocument } from '../../lib/api';
import styles from './ChatInput.module.css';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  onFileUploaded?: (document: any) => void;
  conversationId?: string | null;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({ onSendMessage, onFileUploaded, conversationId, disabled = false, placeholder = "Type your message..." }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!message.trim() || disabled || isUploading) return;
    
    onSendMessage(message.trim());
    setMessage('');
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    
    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  };

  const handleFileUpload = async (file: File) => {
    if (!conversationId) {
      console.error('No conversation ID provided for file upload');
      return;
    }

    setIsUploading(true);
    
    try {
      console.log('Uploading file:', file.name);
      const result = await uploadDocument(file, conversationId);
      console.log('File upload successful:', result);
      
      // Notify parent component about successful upload
      if (onFileUploaded) {
        onFileUploaded(result);
      }
      
      // Send a message about the uploaded file
      onSendMessage(`📄 I just uploaded a document: ${file.name}`);
      
    } catch (error) {
      console.error('File upload failed:', error);
      // You might want to show an error message to the user here
      alert('File upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.inputWrapper}>
        <div className={styles.inputContainer}>
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || isUploading}
            className={styles.textarea}
            rows={1}
          />
          
          <div className={styles.actions}>
            <FileUpload
              onFileSelect={handleFileUpload}
              disabled={disabled || isUploading}
            />
            
            <button
              onClick={handleSubmit}
              disabled={!message.trim() || disabled || isUploading}
              className={styles.sendButton}
              aria-label="Send message"
            >
              {isUploading ? (
                <span className={styles.spinner}>⏳</span>
              ) : (
                <span>➤</span>
              )}
            </button>
          </div>
        </div>
        
        <div className={styles.hint}>
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
}
