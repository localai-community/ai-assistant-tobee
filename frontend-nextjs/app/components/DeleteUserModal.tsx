'use client';

import { useState } from 'react';
import { User } from '../../lib/types';
import styles from './DeleteUserModal.module.css';

interface DeleteUserModalProps {
  user: User | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (user: User) => Promise<void>;
  isDeleting?: boolean;
}

export default function DeleteUserModal({
  user,
  isOpen,
  onClose,
  onConfirm,
  isDeleting = false
}: DeleteUserModalProps) {
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen || !user) {
    return null;
  }

  const handleConfirm = async () => {
    setIsLoading(true);
    try {
      await onConfirm(user);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className={styles.overlay} onClick={handleOverlayClick}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <h2 className={styles.title}>⚠️ Delete User</h2>
          <button
            className={styles.closeButton}
            onClick={onClose}
            disabled={isLoading || isDeleting}
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        <div className={styles.content}>
          <div className={styles.warningIcon}>⚠️</div>
          <p className={styles.warningText}>
            Are you sure you want to delete the user <strong>"{user.username}"</strong>?
          </p>
          <p className={styles.detailText}>
            This action will permanently delete:
          </p>
          <ul className={styles.deleteList}>
            <li>User account and profile</li>
            <li>All conversations and chat history</li>
            <li>All uploaded documents and files</li>
            <li>All user settings and preferences</li>
          </ul>
          <p className={styles.finalWarning}>
            <strong>This action cannot be undone!</strong>
          </p>
        </div>

        <div className={styles.actions}>
          <button
            className={styles.cancelButton}
            onClick={onClose}
            disabled={isLoading || isDeleting}
          >
            Cancel
          </button>
          <button
            className={styles.deleteButton}
            onClick={handleConfirm}
            disabled={isLoading || isDeleting}
          >
            {isLoading || isDeleting ? '⏳ Deleting...' : '🗑️ Delete User'}
          </button>
        </div>
      </div>
    </div>
  );
}
