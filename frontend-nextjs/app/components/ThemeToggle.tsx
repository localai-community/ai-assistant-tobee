'use client';

import styles from './ThemeToggle.module.css';

type ThemeValue = 'light' | 'dark' | 'system';

interface ThemeToggleProps {
  theme: string;
  onThemeChange: (theme: ThemeValue) => void;
}

const options: { value: ThemeValue; label: string; icon: string }[] = [
  { value: 'light', label: 'Light', icon: '\u2600' },
  { value: 'dark', label: 'Dark', icon: '\u263E' },
  { value: 'system', label: 'System', icon: '\u2699' },
];

export default function ThemeToggle({ theme, onThemeChange }: ThemeToggleProps) {
  const current = (theme || 'system') as ThemeValue;

  return (
    <div className={styles.container}>
      {options.map((opt) => (
        <button
          key={opt.value}
          className={`${styles.option} ${current === opt.value ? styles.active : ''}`}
          onClick={() => onThemeChange(opt.value)}
          title={opt.label}
        >
          <span className={styles.icon}>{opt.icon}</span>
          <span className={styles.label}>{opt.label}</span>
        </button>
      ))}
    </div>
  );
}
