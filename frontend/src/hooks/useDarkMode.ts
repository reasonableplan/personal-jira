import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'theme-mode';
const DARK_CLASS = 'dark';

export interface DarkModeReturn {
  isDark: boolean;
  toggle: () => void;
  enable: () => void;
  disable: () => void;
}

function getInitialMode(): boolean {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === 'dark') return true;
  if (stored === 'light') return false;
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

export function useDarkMode(): DarkModeReturn {
  const [isDark, setIsDark] = useState<boolean>(getInitialMode);

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add(DARK_CLASS);
    } else {
      root.classList.remove(DARK_CLASS);
    }
    localStorage.setItem(STORAGE_KEY, isDark ? 'dark' : 'light');
  }, [isDark]);

  const toggle = useCallback(() => setIsDark((prev) => !prev), []);
  const enable = useCallback(() => setIsDark(true), []);
  const disable = useCallback(() => setIsDark(false), []);

  return { isDark, toggle, enable, disable };
}
