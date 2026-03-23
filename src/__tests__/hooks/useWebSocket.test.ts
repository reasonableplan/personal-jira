import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useWebSocket } from '../../hooks/useWebSocket';
import type { WSMessage } from '../../types/websocket';
import { WS_READY_STATE, WS_RECONNECT_INTERVAL_MS, WS_MAX_RETRIES } from '../../constants/websocket';

class MockWebSocket {
  static instances: MockWebSocket[] = [];
  url: string;
  readyState: number = WS_READY_STATE.CONNECTING;
  onopen: ((ev: Event) => void) | null = null;
  onclose: ((ev: CloseEvent) => void) | null = null;
  onmessage: ((ev: MessageEvent) => void) | null = null;
  onerror: ((ev: Event) => void) | null = null;
  send = vi.fn();
  close = vi.fn();

  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }

  simulateOpen() {
    this.readyState = WS_READY_STATE.OPEN;
    this.onopen?.(new Event('open'));
  }

  simulateMessage(data: WSMessage) {
    this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(data) }));
  }

  simulateClose(code = 1000) {
    this.readyState = WS_READY_STATE.CLOSED;
    this.onclose?.({ code } as CloseEvent);
  }

  simulateError() {
    this.onerror?.(new Event('error'));
  }
}

describe('useWebSocket', () => {
  const WS_URL = 'ws://localhost:8000/ws';

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    MockWebSocket.instances = [];
    vi.stubGlobal('WebSocket', MockWebSocket);
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it('connects to WebSocket URL on mount', () => {
    renderHook(() => useWebSocket(WS_URL));
    expect(MockWebSocket.instances).toHaveLength(1);
    expect(MockWebSocket.instances[0].url).toBe(WS_URL);
  });

  it('reports connected status after open', () => {
    const { result } = renderHook(() => useWebSocket(WS_URL));
    expect(result.current.status).toBe('connecting');

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    expect(result.current.status).toBe('connected');
  });

  it('receives and parses messages', () => {
    const onMessage = vi.fn();
    renderHook(() => useWebSocket(WS_URL, { onMessage }));

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    const msg: WSMessage = { type: 'issue_updated', payload: { id: '1', title: 'Updated' } };
    act(() => {
      MockWebSocket.instances[0].simulateMessage(msg);
    });

    expect(onMessage).toHaveBeenCalledWith(msg);
  });

  it('stores last message in state', () => {
    const { result } = renderHook(() => useWebSocket(WS_URL));

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    const msg: WSMessage = { type: 'issue_created', payload: { id: '2' } };
    act(() => {
      MockWebSocket.instances[0].simulateMessage(msg);
    });

    expect(result.current.lastMessage).toEqual(msg);
  });

  it('sends messages through WebSocket', () => {
    const { result } = renderHook(() => useWebSocket(WS_URL));

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    const msg: WSMessage = { type: 'subscribe', payload: { channel: 'issues' } };
    act(() => {
      result.current.sendMessage(msg);
    });

    expect(MockWebSocket.instances[0].send).toHaveBeenCalledWith(JSON.stringify(msg));
  });

  it('does not send when not connected', () => {
    const { result } = renderHook(() => useWebSocket(WS_URL));

    const msg: WSMessage = { type: 'subscribe', payload: { channel: 'issues' } };
    act(() => {
      result.current.sendMessage(msg);
    });

    expect(MockWebSocket.instances[0].send).not.toHaveBeenCalled();
  });

  it('reconnects on unexpected close', () => {
    renderHook(() => useWebSocket(WS_URL));

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    act(() => {
      MockWebSocket.instances[0].simulateClose(1006);
    });

    expect(MockWebSocket.instances).toHaveLength(1);

    act(() => {
      vi.advanceTimersByTime(WS_RECONNECT_INTERVAL_MS);
    });

    expect(MockWebSocket.instances).toHaveLength(2);
  });

  it('does not reconnect on normal close (1000)', () => {
    renderHook(() => useWebSocket(WS_URL));

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    act(() => {
      MockWebSocket.instances[0].simulateClose(1000);
    });

    act(() => {
      vi.advanceTimersByTime(WS_RECONNECT_INTERVAL_MS);
    });

    expect(MockWebSocket.instances).toHaveLength(1);
  });

  it('stops reconnecting after max retries', () => {
    renderHook(() => useWebSocket(WS_URL));

    for (let i = 0; i < WS_MAX_RETRIES; i++) {
      const ws = MockWebSocket.instances[MockWebSocket.instances.length - 1];
      act(() => {
        ws.simulateOpen();
      });
      act(() => {
        ws.simulateClose(1006);
      });
      act(() => {
        vi.advanceTimersByTime(WS_RECONNECT_INTERVAL_MS);
      });
    }

    const countAfterMaxRetries = MockWebSocket.instances.length;

    const lastWs = MockWebSocket.instances[MockWebSocket.instances.length - 1];
    act(() => {
      lastWs.simulateOpen();
    });
    act(() => {
      lastWs.simulateClose(1006);
    });
    act(() => {
      vi.advanceTimersByTime(WS_RECONNECT_INTERVAL_MS);
    });

    expect(MockWebSocket.instances).toHaveLength(countAfterMaxRetries);
  });

  it('resets retry count on successful connection', () => {
    const { result } = renderHook(() => useWebSocket(WS_URL));

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });
    act(() => {
      MockWebSocket.instances[0].simulateClose(1006);
    });
    act(() => {
      vi.advanceTimersByTime(WS_RECONNECT_INTERVAL_MS);
    });

    act(() => {
      MockWebSocket.instances[1].simulateOpen();
    });

    expect(result.current.status).toBe('connected');
  });

  it('closes connection on unmount', () => {
    const { unmount } = renderHook(() => useWebSocket(WS_URL));

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    unmount();

    expect(MockWebSocket.instances[0].close).toHaveBeenCalled();
  });

  it('sets error status on WebSocket error', () => {
    const { result } = renderHook(() => useWebSocket(WS_URL));

    act(() => {
      MockWebSocket.instances[0].simulateError();
    });

    expect(result.current.status).toBe('error');
  });

  it('provides disconnect function', () => {
    const { result } = renderHook(() => useWebSocket(WS_URL));

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    act(() => {
      result.current.disconnect();
    });

    expect(MockWebSocket.instances[0].close).toHaveBeenCalledWith(1000);
    expect(result.current.status).toBe('disconnected');
  });
});
