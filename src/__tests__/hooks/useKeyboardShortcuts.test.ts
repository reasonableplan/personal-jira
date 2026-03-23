import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useKeyboardShortcuts } from '../../hooks/useKeyboardShortcuts';
import type { ShortcutMap } from '../../types/shortcuts';

describe('useKeyboardShortcuts', () => {
  const createIssue = vi.fn();
  const openSearch = vi.fn();
  const toggleSidebar = vi.fn();
  const goToBoard = vi.fn();

  const SHORTCUTS: ShortcutMap = {
    'ctrl+n': { handler: createIssue, description: 'Create new issue' },
    'ctrl+k': { handler: openSearch, description: 'Open search' },
    'ctrl+b': { handler: toggleSidebar, description: 'Toggle sidebar' },
    'ctrl+shift+b': { handler: goToBoard, description: 'Go to board' },
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('triggers handler on matching key combo', () => {
    renderHook(() => useKeyboardShortcuts(SHORTCUTS));

    act(() => {
      window.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'n', ctrlKey: true })
      );
    });

    expect(createIssue).toHaveBeenCalledOnce();
  });

  it('handles shift modifier correctly', () => {
    renderHook(() => useKeyboardShortcuts(SHORTCUTS));

    act(() => {
      window.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'b', ctrlKey: true, shiftKey: true })
      );
    });

    expect(goToBoard).toHaveBeenCalledOnce();
    expect(toggleSidebar).not.toHaveBeenCalled();
  });

  it('does not trigger when typing in input fields', () => {
    renderHook(() => useKeyboardShortcuts(SHORTCUTS));

    const input = document.createElement('input');
    document.body.appendChild(input);
    input.focus();

    act(() => {
      input.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'n', ctrlKey: true, bubbles: true })
      );
    });

    expect(createIssue).not.toHaveBeenCalled();
    document.body.removeChild(input);
  });

  it('does not trigger when typing in textarea', () => {
    renderHook(() => useKeyboardShortcuts(SHORTCUTS));

    const textarea = document.createElement('textarea');
    document.body.appendChild(textarea);
    textarea.focus();

    act(() => {
      textarea.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'k', ctrlKey: true, bubbles: true })
      );
    });

    expect(openSearch).not.toHaveBeenCalled();
    document.body.removeChild(textarea);
  });

  it('does not trigger when contenteditable is focused', () => {
    renderHook(() => useKeyboardShortcuts(SHORTCUTS));

    const div = document.createElement('div');
    div.setAttribute('contenteditable', 'true');
    document.body.appendChild(div);
    div.focus();

    act(() => {
      div.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'n', ctrlKey: true, bubbles: true })
      );
    });

    expect(createIssue).not.toHaveBeenCalled();
    document.body.removeChild(div);
  });

  it('cleans up event listeners on unmount', () => {
    const spy = vi.spyOn(window, 'removeEventListener');
    const { unmount } = renderHook(() => useKeyboardShortcuts(SHORTCUTS));

    unmount();

    expect(spy).toHaveBeenCalledWith('keydown', expect.any(Function));
    spy.mockRestore();
  });

  it('does not trigger on unregistered key combos', () => {
    renderHook(() => useKeyboardShortcuts(SHORTCUTS));

    act(() => {
      window.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'z', ctrlKey: true })
      );
    });

    expect(createIssue).not.toHaveBeenCalled();
    expect(openSearch).not.toHaveBeenCalled();
    expect(toggleSidebar).not.toHaveBeenCalled();
    expect(goToBoard).not.toHaveBeenCalled();
  });

  it('prevents default browser behavior for registered shortcuts', () => {
    renderHook(() => useKeyboardShortcuts(SHORTCUTS));

    const event = new KeyboardEvent('keydown', {
      key: 'k',
      ctrlKey: true,
      cancelable: true,
    });
    const preventSpy = vi.spyOn(event, 'preventDefault');

    act(() => {
      window.dispatchEvent(event);
    });

    expect(preventSpy).toHaveBeenCalled();
  });

  it('can be disabled', () => {
    renderHook(() => useKeyboardShortcuts(SHORTCUTS, { enabled: false }));

    act(() => {
      window.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'n', ctrlKey: true })
      );
    });

    expect(createIssue).not.toHaveBeenCalled();
  });

  it('returns list of registered shortcuts', () => {
    const { result } = renderHook(() => useKeyboardShortcuts(SHORTCUTS));

    expect(result.current.shortcuts).toEqual([
      { keys: 'ctrl+n', description: 'Create new issue' },
      { keys: 'ctrl+k', description: 'Open search' },
      { keys: 'ctrl+b', description: 'Toggle sidebar' },
      { keys: 'ctrl+shift+b', description: 'Go to board' },
    ]);
  });
});
