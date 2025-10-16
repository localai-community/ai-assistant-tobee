'use client';

import { useEffect, useState } from 'react';
import styles from './NoUserWarningModal.module.css';

interface NoUserWarningModalProps {
  isOpen: boolean;
  onClose: () => void;
  onContinue: () => void;
}

export default function NoUserWarningModal({ isOpen, onClose, onContinue }: NoUserWarningModalProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsVisible(true);
    } else {
      // Add delay for smooth exit animation
      const timer = setTimeout(() => setIsVisible(false), 200);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  if (!isVisible) return null;

  return (
    <div className={`${styles.overlay} ${isOpen ? styles.overlayOpen : styles.overlayClosed}`}>
      <div className={`${styles.modal} ${isOpen ? styles.modalOpen : styles.modalClosed}`}>
        <div className={styles.header}>
          <div className={styles.icon}>⚠️</div>
          <h2 className={styles.title}>No User Selected</h2>
        </div>
        
        <div className={styles.content}>
          <p className={styles.message}>
            You are currently in <strong>Guest Mode</strong>. Your questions and responses will <strong>not be saved</strong> to the database.
          </p>
          <p className={styles.subMessage}>
            To save your conversations, please select a user from the sidebar or create a new user.
          </p>
        </div>
        
        <div className={styles.actions}>
          <button
            type="button"
            onClick={onClose}
            className={styles.cancelButton}
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onContinue}
            className={styles.continueButton}
          >
            Continue as Guest
          </button>
        </div>
      </div>
    </div>
  );
}
