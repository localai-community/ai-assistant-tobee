'use client';

import { useRef, useState } from 'react';
import styles from './FileUpload.module.css';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  acceptedTypes?: string[];
  maxSize?: number; // in MB
}

const DEFAULT_ACCEPTED_TYPES = ['.pdf', '.docx', '.txt', '.md'];
const DEFAULT_MAX_SIZE = 50; // 50MB

export default function FileUpload({ 
  onFileSelect, 
  disabled = false, 
  acceptedTypes = DEFAULT_ACCEPTED_TYPES,
  maxSize = DEFAULT_MAX_SIZE 
}: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileSelect = (file: File) => {
    // Validate file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedTypes.includes(fileExtension)) {
      alert(`File type ${fileExtension} is not supported. Accepted types: ${acceptedTypes.join(', ')}`);
      return;
    }

    // Validate file size
    if (file.size > maxSize * 1024 * 1024) {
      alert(`File size must be less than ${maxSize}MB`);
      return;
    }

    onFileSelect(file);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
    // Reset input value to allow selecting the same file again
    e.target.value = '';
  };

  const handleClick = () => {
    if (!disabled) {
      fileInputRef.current?.click();
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragOver(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (disabled) return;

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  return (
    <div className={styles.container}>
      <button
        type="button"
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        disabled={disabled}
        className={`${styles.uploadButton} ${isDragOver ? styles.dragOver : ''} ${disabled ? styles.disabled : ''}`}
        aria-label="Upload file"
      >
        <span className={styles.uploadIcon}>📎</span>
      </button>
      
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedTypes.join(',')}
        onChange={handleInputChange}
        className={styles.hiddenInput}
        disabled={disabled}
      />
      
      {isDragOver && (
        <div className={styles.dragOverlay}>
          <div className={styles.dragMessage}>
            <span className={styles.dragIcon}>📁</span>
            <p>Drop file here to upload</p>
            <small>Supported: {acceptedTypes.join(', ')}</small>
          </div>
        </div>
      )}
    </div>
  );
}
