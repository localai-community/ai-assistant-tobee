import React from 'react';
import styles from './DeleteConfirmationModal.module.css';

interface DeleteConfirmationModalProps {
  isOpen: boolean;
  conversationTitle: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function DeleteConfirmationModal({
  isOpen,
  conversationTitle,
  onConfirm,
  onCancel
}: DeleteConfirmationModalProps) {
  if (!isOpen) return null;

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onCancel();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onCancel();
    } else if (e.key === 'Enter') {
      onConfirm();
    }
  };

  return (
    <div 
      className={styles.overlay} 
      onClick={handleOverlayClick}
      onKeyDown={handleKeyDown}
      tabIndex={-1}
    >
      <div className={styles.modal}>
        <div className={styles.header}>
          <div className={styles.icon}>⚠️</div>
          <h3 className={styles.title}>Delete Conversation</h3>
        </div>
        
        <div className={styles.content}>
          <p className={styles.message}>
            Are you sure you want to delete <strong>"{conversationTitle}"</strong>?
          </p>
          <p className={styles.warning}>
            This action cannot be undone and will permanently remove all messages in this conversation.
          </p>
        </div>
        
        <div className={styles.actions}>
          <button 
            className={styles.cancelButton}
            onClick={onCancel}
            type="button"
          >
            Cancel
          </button>
          <button 
            className={styles.confirmButton}
            onClick={onConfirm}
            type="button"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
