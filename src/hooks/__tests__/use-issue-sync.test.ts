import { renderHook } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useIssueSync } from '../use-issue-sync';
import * as useWebSocketModule from '../use-websocket';
import * as useToastModule from '../use-toast';
import { WsEventType } from '../../types/ws-events';

vi.mock('../use-websocket');
vi.mock('../use-toast');

describe('useIssueSync', () => {
  const mockAddToast = vi.fn();
  const mockOnMessage = vi.fn();
  let capturedOnMessage: ((msg: unknown) => void) | undefined;

  beforeEach(() => {
    vi.clearAllMocks();
    capturedOnMessage = undefined;

    vi.mocked(useToastModule.useToast).mockReturnValue({
      toasts: [],
      addToast: mockAddToast,
      removeToast: vi.fn(),
    });

    vi.mocked(useWebSocketModule.useWebSocket).mockImplementation(
      (_url: string, opts?: { onMessage?: (msg: unknown) => void }) => {
        capturedOnMessage = opts?.onMessage;
        return {
          isConnected: true,
          lastMessage: null,
          sendMessage: vi.fn(),
        };
      }
    );
  });

  it('connects to the issues WebSocket endpoint', () => {
    renderHook(() => useIssueSync({ onMessage: mockOnMessage }));
    expect(useWebSocketModule.useWebSocket).toHaveBeenCalledWith(
      expect.stringContaining('/ws/issues'),
      expect.any(Object)
    );
  });

  it('shows toast on issue_created event', () => {
    renderHook(() => useIssueSync({ onMessage: mockOnMessage }));
    capturedOnMessage?.({
      type: WsEventType.ISSUE_CREATED,
      data: { id: '1', title: 'New bug' },
    });
    expect(mockAddToast).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'info',
        message: expect.stringContaining('New bug'),
      })
    );
  });

  it('shows toast on issue_updated event', () => {
    renderHook(() => useIssueSync({ onMessage: mockOnMessage }));
    capturedOnMessage?.({
      type: WsEventType.ISSUE_UPDATED,
      data: { id: '2', title: 'Updated task' },
    });
    expect(mockAddToast).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'success',
        message: expect.stringContaining('Updated task'),
      })
    );
  });

  it('shows toast on issue_deleted event', () => {
    renderHook(() => useIssueSync({ onMessage: mockOnMessage }));
    capturedOnMessage?.({
      type: WsEventType.ISSUE_DELETED,
      data: { id: '3', title: 'Removed' },
    });
    expect(mockAddToast).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'warning',
        message: expect.stringContaining('Removed'),
      })
    );
  });

  it('shows error toast on issue_error event', () => {
    renderHook(() => useIssueSync({ onMessage: mockOnMessage }));
    capturedOnMessage?.({
      type: WsEventType.ISSUE_ERROR,
      data: { message: 'Something failed' },
    });
    expect(mockAddToast).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'error',
        message: expect.stringContaining('Something failed'),
      })
    );
  });

  it('forwards message to onMessage callback', () => {
    renderHook(() => useIssueSync({ onMessage: mockOnMessage }));
    const event = {
      type: WsEventType.ISSUE_UPDATED,
      data: { id: '2', title: 'Test' },
    };
    capturedOnMessage?.(event);
    expect(mockOnMessage).toHaveBeenCalledWith(event);
  });

  it('returns connection status', () => {
    const { result } = renderHook(() =>
      useIssueSync({ onMessage: mockOnMessage })
    );
    expect(result.current.isConnected).toBe(true);
  });
});
