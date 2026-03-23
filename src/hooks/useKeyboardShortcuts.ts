import { useEffect, useMemo } from 'react';
import type { ShortcutMap, ShortcutInfo } from '../types/shortcuts';

const IGNORED_TAGS = new Set(['INPUT', 'TEXTAREA', 'SELECT']);

interface UseKeyboardShortcutsOptions {
  enabled?: boolean;
}

function parseCombo(combo: string) {
  const parts = combo.toLowerCase().split('+');
  return {
    ctrl: parts.includes('ctrl'),
    shift: parts.includes('shift'),
    alt: parts.includes('alt'),
    meta: parts.includes('meta'),
    key: parts.filter((p) => !['ctrl', 'shift', 'alt', 'meta'].includes(p))[0],
  };
}

export function useKeyboardShortcuts(
  shortcuts: ShortcutMap,
  options: UseKeyboardShortcutsOptions = {}
) {
  const { enabled = true } = options;

  useEffect(() => {
    if (!enabled) return;

    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (
        IGNORED_TAGS.has(target.tagName) ||
        target.isContentEditable
      ) {
        return;
      }

      for (const [combo, entry] of Object.entries(shortcuts)) {
        const parsed = parseCombo(combo);
        if (
          e.key.toLowerCase() === parsed.key &&
          e.ctrlKey === parsed.ctrl &&
          e.shiftKey === parsed.shift &&
          e.altKey === parsed.alt &&
          e.metaKey === parsed.meta
        ) {
          e.preventDefault();
          entry.handler();
          return;
        }
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [shortcuts, enabled]);

  const shortcutList: ShortcutInfo[] = useMemo(
    () =>
      Object.entries(shortcuts).map(([keys, entry]) => ({
        keys,
        description: entry.description,
      })),
    [shortcuts]
  );

  return { shortcuts: shortcutList };
}
