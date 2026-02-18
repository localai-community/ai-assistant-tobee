import { useEffect, useRef, useState } from 'react';

type ThemeSetting = 'light' | 'dark' | 'system';
type ResolvedTheme = 'light' | 'dark';

function resolve(setting: ThemeSetting): ResolvedTheme {
  if (setting === 'dark') return 'dark';
  if (setting === 'light') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function useTheme(theme?: string) {
  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>('light');
  const rootRef = useRef<HTMLElement | null>(null);

  // Grab the root element once on mount
  useEffect(() => {
    rootRef.current = document.documentElement;
  }, []);

  // Apply theme when it changes
  useEffect(() => {
    if (!theme || !rootRef.current) return;

    const setting = theme as ThemeSetting;
    const resolved = resolve(setting);

    rootRef.current.setAttribute('data-theme', resolved);
    rootRef.current.style.colorScheme = resolved;
    setResolvedTheme(resolved);

    // Listen for OS changes when set to "system"
    if (setting !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => {
      const r = e.matches ? 'dark' : 'light';
      rootRef.current?.setAttribute('data-theme', r);
      if (rootRef.current) rootRef.current.style.colorScheme = r;
      setResolvedTheme(r);
    };
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [theme]);

  return { resolvedTheme, isDark: resolvedTheme === 'dark' };
}
