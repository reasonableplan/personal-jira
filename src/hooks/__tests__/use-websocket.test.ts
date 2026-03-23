import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useWebSocket, WS_READY_STATE } from '../use-websocket';

const MOCK_URL = 'ws://localhost:8000/ws';

class MockWebSocket {
  static instances: MockWebSocket[] = [];
  url: string;
  readyState: number = WS_READY_STATE.CONNECTING;
  onopen: ((ev: Event) => void) | null = null;
  onclose: ((ev: CloseEvent) => void) | null = null;
  onmessage: ((ev: MessageEvent) => void) | null = null;
  onerror: ((ev: Event) => void) | null = null;
  close = vi.fn();
  send = vi.fn();

  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }

  simulateOpen() {
    this.readyState = WS_READY_STATE.OPEN;
    this.onopen?.(new Event('open'));
  }

  simulateMessage(data: unknown) {
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
  beforeEach(() => {
    MockWebSocket.instances = [];
    vi.stubGlobal('WebSocket', MockWebSocket);
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it('connects to the given URL', () => {
    renderHook(() => useWebSocket(MOCK_URL));
    expect(MockWebSocket.instances).toHaveLength(1);
    expect(MockWebSocket.instances[0].url).toBe(MOCK_URL);
  });

  it('reports connected status on open', () => {
    const { result } = renderHook(() => useWebSocket(MOCK_URL));
    expect(result.current.isConnected).toBe(false);
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });
    expect(result.current.isConnected).toBe(true);
  });

  it('parses incoming JSON messages', () => {
    const onMessage = vi.fn();
    renderHook(() => useWebSocket(MOCK_URL, { onMessage }));
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });
    const payload = { type: 'issue_updated', data: { id: '1' } };
    act(() => {
      MockWebSocket.instances[0].simulateMessage(payload);
    });
    expect(onMessage).toHaveBeenCalledWith(payload);
  });

  it('stores last message', () => {
    const { result } = renderHook(() => useWebSocket(MOCK_URL));
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
      MockWebSocket.instances[0].simulateMessage({ type: 'ping' });
    });
    expect(result.current.lastMessage).toEqual({ type: 'ping' });
  });

  it('reconnects on abnormal close', () => {
    renderHook(() => useWebSocket(MOCK_URL));
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
      MockWebSocket.instances[0].simulateClose(1006);
    });
    act(() => {
      vi.advanceTimersByTime(3000);
    });
    expect(MockWebSocket.instances.length).toBeGreaterThan(1);
  });

  it('does not reconnect on normal close', () => {
    renderHook(() => useWebSocket(MOCK_URL));
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
      MockWebSocket.instances[0].simulateClose(1000);
    });
    act(() => {
      vi.advanceTimersByTime(5000);
    });
    expect(MockWebSocket.instances).toHaveLength(1);
  });

  it('closes connection on unmount', () => {
    const { unmount } = renderHook(() => useWebSocket(MOCK_URL));
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });
    unmount();
    expect(MockWebSocket.instances[0].close).toHaveBeenCalled();
  });

  it('exposes sendMessage when connected', () => {
    const { result } = renderHook(() => useWebSocket(MOCK_URL));
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });
    act(() => {
      result.current.sendMessage({ type: 'subscribe', channel: 'issues' });
    });
    expect(MockWebSocket.instances[0].send).toHaveBeenCalledWith(
      JSON.stringify({ type: 'subscribe', channel: 'issues' })
    );
  });

  it('does not connect when enabled is false', () => {
    renderHook(() => useWebSocket(MOCK_URL, { enabled: false }));
    expect(MockWebSocket.instances).toHaveLength(0);
  });
});
