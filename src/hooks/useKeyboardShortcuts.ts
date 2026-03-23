import { useCallback, useEffect, useMemo } from 'react';
import type { KeyboardShortcutGroup, UseKeyboardShortcutsOptions } from '../types/keyboard';

const IGNORED_TAG_NAMES = new Set(['INPUT', 'TEXTAREA', 'SELECT']);

const isEditableTarget = (target: EventTarget | null): boolean => {
  if (!(target instanceof HTMLElement)) return false;
  if (IGNORED_TAG_NAMES.has(target.tagName)) return true;
  return target.isContentEditable;
};

const hasModifier = (e: KeyboardEvent): boolean =>
  e.ctrlKey || e.metaKey || e.altKey;

export const useKeyboardShortcuts = (options: UseKeyboardShortcutsOptions) => {
  const {
    onCreateIssue,
    onNavigateUp,
    onNavigateDown,
    onToggleHelp,
    enabled = true,
  } = options;

  const shortcutGroups: KeyboardShortcutGroup[] = useMemo(() => [
    {
      name: '이슈',
      shortcuts: [
        { key: 'C', description: '새 이슈 생성', handler: onCreateIssue },
        { key: 'J', description: '다음 이슈로 이동', handler: onNavigateDown },
        { key: 'K', description: '이전 이슈로 이동', handler: onNavigateUp },
      ],
    },
    {
      name: '일반',
      shortcuts: [
        { key: '?', description: '단축키 도움말', handler: onToggleHelp },
      ],
    },
  ], [onCreateIssue, onNavigateDown, onNavigateUp, onToggleHelp]);

  const keyMap = useMemo(() => {
    const map = new Map<string, () => void>();
    map.set('c', onCreateIssue);
    map.set('j', onNavigateDown);
    map.set('k', onNavigateUp);
    map.set('?', onToggleHelp);
    return map;
  }, [onCreateIssue, onNavigateDown, onNavigateUp, onToggleHelp]);

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (!enabled) return;
    if (isEditableTarget(e.target)) return;
    if (hasModifier(e)) return;

    const handler = keyMap.get(e.key.toLowerCase());
    if (handler) {
      handler();
    }
  }, [enabled, keyMap]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return { shortcutGroups };
};