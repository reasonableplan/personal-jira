import { renderHook, act } from '@testing-library/react';
import { useKeyboardShortcuts } from '../useKeyboardShortcuts';
import type { UseKeyboardShortcutsOptions } from '../../types/keyboard';

const createHandlers = (): UseKeyboardShortcutsOptions => ({
  onCreateIssue: jest.fn(),
  onNavigateUp: jest.fn(),
  onNavigateDown: jest.fn(),
  onToggleHelp: jest.fn(),
});

const fireKey = (key: string, options: Partial<KeyboardEventInit> = {}) => {
  const event = new KeyboardEvent('keydown', { key, bubbles: true, ...options });
  document.dispatchEvent(event);
  return event;
};

describe('useKeyboardShortcuts', () => {
  it('calls onCreateIssue when C is pressed', () => {
    const handlers = createHandlers();
    renderHook(() => useKeyboardShortcuts(handlers));

    act(() => { fireKey('c'); });

    expect(handlers.onCreateIssue).toHaveBeenCalledTimes(1);
  });

  it('calls onNavigateDown when J is pressed', () => {
    const handlers = createHandlers();
    renderHook(() => useKeyboardShortcuts(handlers));

    act(() => { fireKey('j'); });

    expect(handlers.onNavigateDown).toHaveBeenCalledTimes(1);
  });

  it('calls onNavigateUp when K is pressed', () => {
    const handlers = createHandlers();
    renderHook(() => useKeyboardShortcuts(handlers));

    act(() => { fireKey('k'); });

    expect(handlers.onNavigateUp).toHaveBeenCalledTimes(1);
  });

  it('calls onToggleHelp when ? is pressed', () => {
    const handlers = createHandlers();
    renderHook(() => useKeyboardShortcuts(handlers));

    act(() => { fireKey('?'); });

    expect(handlers.onToggleHelp).toHaveBeenCalledTimes(1);
  });

  it('ignores keys when typing in input elements', () => {
    const handlers = createHandlers();
    renderHook(() => useKeyboardShortcuts(handlers));

    const input = document.createElement('input');
    document.body.appendChild(input);
    input.focus();

    act(() => {
      const event = new KeyboardEvent('keydown', { key: 'c', bubbles: true });
      Object.defineProperty(event, 'target', { value: input });
      document.dispatchEvent(event);
    });

    expect(handlers.onCreateIssue).not.toHaveBeenCalled();
    document.body.removeChild(input);
  });

  it('ignores keys when typing in textarea elements', () => {
    const handlers = createHandlers();
    renderHook(() => useKeyboardShortcuts(handlers));

    const textarea = document.createElement('textarea');
    document.body.appendChild(textarea);
    textarea.focus();

    act(() => {
      const event = new KeyboardEvent('keydown', { key: 'j', bubbles: true });
      Object.defineProperty(event, 'target', { value: textarea });
      document.dispatchEvent(event);
    });

    expect(handlers.onNavigateDown).not.toHaveBeenCalled();
    document.body.removeChild(textarea);
  });

  it('ignores keys when contentEditable is active', () => {
    const handlers = createHandlers();
    renderHook(() => useKeyboardShortcuts(handlers));

    const div = document.createElement('div');
    div.contentEditable = 'true';
    document.body.appendChild(div);
    div.focus();

    act(() => {
      const event = new KeyboardEvent('keydown', { key: 'k', bubbles: true });
      Object.defineProperty(event, 'target', { value: div });
      document.dispatchEvent(event);
    });

    expect(handlers.onNavigateUp).not.toHaveBeenCalled();
    document.body.removeChild(div);
  });

  it('ignores keys with modifier keys pressed', () => {
    const handlers = createHandlers();
    renderHook(() => useKeyboardShortcuts(handlers));

    act(() => { fireKey('c', { ctrlKey: true }); });
    expect(handlers.onCreateIssue).not.toHaveBeenCalled();

    act(() => { fireKey('c', { metaKey: true }); });
    expect(handlers.onCreateIssue).not.toHaveBeenCalled();

    act(() => { fireKey('c', { altKey: true }); });
    expect(handlers.onCreateIssue).not.toHaveBeenCalled();
  });

  it('does not fire when enabled is false', () => {
    const handlers = createHandlers();
    renderHook(() => useKeyboardShortcuts({ ...handlers, enabled: false }));

    act(() => { fireKey('c'); });

    expect(handlers.onCreateIssue).not.toHaveBeenCalled();
  });

  it('cleans up event listener on unmount', () => {
    const handlers = createHandlers();
    const spy = jest.spyOn(document, 'removeEventListener');
    const { unmount } = renderHook(() => useKeyboardShortcuts(handlers));

    unmount();

    expect(spy).toHaveBeenCalledWith('keydown', expect.any(Function));
    spy.mockRestore();
  });

  it('returns shortcut groups for help display', () => {
    const handlers = createHandlers();
    const { result } = renderHook(() => useKeyboardShortcuts(handlers));

    expect(result.current.shortcutGroups).toHaveLength(2);
    expect(result.current.shortcutGroups[0].name).toBe('이슈');
    expect(result.current.shortcutGroups[1].name).toBe('일반');
  });

  it('handles uppercase keys the same as lowercase', () => {
    const handlers = createHandlers();
    renderHook(() => useKeyboardShortcuts(handlers));

    act(() => { fireKey('C'); });
    expect(handlers.onCreateIssue).toHaveBeenCalledTimes(1);

    act(() => { fireKey('J'); });
    expect(handlers.onNavigateDown).toHaveBeenCalledTimes(1);

    act(() => { fireKey('K'); });
    expect(handlers.onNavigateUp).toHaveBeenCalledTimes(1);
  });
});